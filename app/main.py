import asyncio
import traceback
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from app.llm.chat import generate_chat_response
from app.llm.generate_search_query import generate_search_query
from app.database.queries import OpensearchQueries
from app.utils.parse_json import parse_json
from app.utils.conversation_history import ConversationHistory

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

opensearch_queries = OpensearchQueries()
conversation_history = ConversationHistory()


@app.get("/")
async def index(request: Request):
    session_id = str(uuid.uuid4())
    jobs = opensearch_queries.get_jobs()
    jobs_per_row = 30
    job_rows = [jobs[i : i + jobs_per_row] for i in range(0, len(jobs), jobs_per_row)]

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "job_rows": job_rows, "session_id": session_id},
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
async def stream_chat_response(message: str, session_id: str):
    if not message:
        return
    return StreamingResponse(
        generate_chat_response(message, session_id, conversation_history),
        media_type="text/event-stream",
    )


@app.get("/search-items")
async def get_search_items(message: str):
    try:
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
    except BaseException as e:
        print(f"[ERROR] {e}")
        traceback.print_exc()
        return


# 非同期でremove_expired_sessionsを実行する関数
async def remove_expired_sessions_async():
    while True:
        await asyncio.sleep(60 * 60 * 24)  # 1日（24時間）待機
        conversation_history.remove_expired_sessions()


# バックグラウンドタスクを開始する関数
def start_remove_expired_sessions_task():
    loop = asyncio.get_event_loop()
    loop.create_task(remove_expired_sessions_async())


# タスクを開始
start_remove_expired_sessions_task()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
