import queue
import threading
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import openai
from jsonfinder import jsonfinder

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage


from app.models import Job
from app.database import SessionLocal
from app.dependencies import get_db

import app.crud as crud

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(f"data: {token}\n\n")


def chat_response_thread(g, prompt):
    try:
        chat = ChatOpenAI(
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager([ChainStreamHandler(g)]),
            temperature=0.7,
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
        )
        print("chat_response start")
        chat(
            [
                SystemMessage(
                    content="あなたは転職エージェントAIとしてユーザーの転職相談に乗ります。必要に応じてヒアリングをするなど、ユーザーニーズに合った提案をしてください。"
                ),
                HumanMessage(content=prompt),
            ]
        )
        print("chat_response end")

    finally:
        g.send(f"data: END\n\n")
        g.close()


def generate_chat_response(prompt):
    g = ThreadedGenerator()
    threading.Thread(target=chat_response_thread, args=(g, prompt)).start()
    return g


@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db)
    jobs_per_row = 30
    job_rows = [jobs[i : i + jobs_per_row] for i in range(0, len(jobs), jobs_per_row)]

    return templates.TemplateResponse(
        "index.html", {"request": request, "job_rows": job_rows}
    )


@app.get("/jobs/{job_id}")
async def job_detail(job_id: int, request: Request):
    db = SessionLocal()
    job = crud.get_job(db, job_id)
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


openai.api_key = os.environ.get("OPENAI_API_KEY")

GENERATE_SEARCH_QUERY_PROMPT = """
あなたは検索クエリジェネレータです。
与えられた文章から、関連する求人データを検索するための検索クエリを生成してください。ただし以下の制約条件に従うこと。

## 制約条件
・出力結果例の形式に従ってJSON形式で回答します
・search_queryはスキーマに従うこと
・2~5件の検索クエリを生成すること
・titleには検索を一言で表す言葉を生成すること。最終的に`[title]の求人`として出力されます
・不足している検索条件があれば勝手に補ってください

## スキーマ
class JobQueryParams:
    keyword: Optional[str] = None
    job_type: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    sort_by: Optional[str] = None
    order: Optional[str] = None

## 出力結果例
1件目
{
    "title": "ソフトウェアエンジニア",
    "search_query": {
        "keyword": "Software Engineer",
        "job_type": "Full Time",
        "location": "Tokyo",
        "min_salary": 300000,
        "max_salary": 600000,
        "sort_by": "monthly_salary",
        "order": "desc"
    }
}

2件目
{
    "title": "データサイエンティスト",
    "search_query": {
        "keyword": "Data Scientist"
    }
}
"""


async def generate_search_query(text):
    print("generate_search_query start")
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"{GENERATE_SEARCH_QUERY_PROMPT}"},
            {"role": "user", "content": f"{text}"},
        ],
        max_tokens=2000,
    )
    print("generate_search_query finish")

    sql_response = response["choices"][0]["message"]["content"]
    return sql_response


def parse_json(text):
    res_jsonfinder = jsonfinder(text)
    res_json = []
    for res in res_jsonfinder:
        if res[2]:
            res_json.append(res[2])
    return res_json


@app.get("/search-items")
async def get_search_items(message: str, db: Session = Depends(get_db)):
    print(f"message: {message}")
    search_query_str = await generate_search_query(message)
    print(f"search_query_str: {search_query_str}")
    search_query_list = parse_json(search_query_str)
    print(f"search_query_list: {search_query_list}")
    response = []
    for search_query in search_query_list:
        search_results = crud.get_custom_jobs(
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
