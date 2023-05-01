from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from app.database.postgresql import SessionLocal
from app.dependencies import get_db
from app.llm.chat import generate_chat_response
from app.llm.generate_search_query import generate_search_query
from app.database.queries import OpensearchQueries
from app.utils import parse_json
from app.schemas import Job

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

opensearch_queries = OpensearchQueries()


@app.get("/")
async def index(request: Request):
    jobs = opensearch_queries.get_jobs()
    jobs_per_row = 30
    job_rows = [jobs[i : i + jobs_per_row] for i in range(0, len(jobs), jobs_per_row)]

    return templates.TemplateResponse(
        "index.html", {"request": request, "job_rows": job_rows}
    )


@app.get("/jobs/{job_id}")
async def job_detail(job_id: str, request: Request):
    job = opensearch_queries.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return templates.TemplateResponse(
        "job_detail.html", {"request": request, "job": job}
    )


@app.get("/question-stream")
async def stream_chat_response(message: str):
    if not message:
        return
    return StreamingResponse(
        generate_chat_response(message), media_type="text/event-stream"
    )


@app.get("/search-items")
async def get_search_items(message: str):
    print(f"message: {message}")
    search_query_str = await generate_search_query(message)

    print(f"search_query_str: {search_query_str}")
    search_query_list = parse_json(search_query_str)

    print(f"search_query_list: {search_query_list}")
    if not search_query_list:
        return

    response = []
    for search_query in search_query_list:
        print(f"search_query: {search_query['search_query']}")
        search_results = opensearch_queries.get_custom_jobs(
            query_params=search_query["search_query"]
        )
        response.append(
            {"title": search_query["title"], "search_results": search_results}
        )
    print(f"response: {response}")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
