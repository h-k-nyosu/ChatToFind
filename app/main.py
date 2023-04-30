from jsonfinder import jsonfinder
from sqlalchemy.orm import Session

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from app.database.database import SessionLocal
from app.dependencies import get_db
from app.llm.chat import generate_chat_response
from app.llm.generate_search_query import generate_search_query
from app.llm.queries import PostgresQueries


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


def parse_json(text):
    res_jsonfinder = jsonfinder(text)
    res_json = []
    for res in res_jsonfinder:
        if res[2]:
            res_json.append(res[2])
    return res_json


@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    jobs = PostgresQueries.get_jobs(db)
    jobs_per_row = 30
    job_rows = [jobs[i : i + jobs_per_row] for i in range(0, len(jobs), jobs_per_row)]

    return templates.TemplateResponse(
        "index.html", {"request": request, "job_rows": job_rows}
    )


@app.get("/jobs/{job_id}")
async def job_detail(job_id: int, request: Request):
    db = SessionLocal()
    job = PostgresQueries.get_job(db, job_id)
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
async def get_search_items(message: str, db: Session = Depends(get_db)):
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
        search_results = PostgresQueries.get_custom_jobs(
            query_params=search_query["search_query"], db=db
        )
        response.append(
            {"title": search_query["title"], "search_results": search_results}
        )
    print(f"response: {response}")
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
