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

load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import (
    HumanMessage,
    SystemMessage
)


from app.models import Job
from app.database import SessionLocal, engine
from app.dependencies import get_db

import app.crud as crud
import app.models as models
import app.crud as crud


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
        print(f"token: {token}")
        self.gen.send(f"data: {token}\n\n")

def chat_response_thread(g, prompt):
    try:
        chat = ChatOpenAI(
            verbose=True,
            streaming=True,
            callback_manager=CallbackManager([ChainStreamHandler(g)]),
            temperature=0.7,
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        chat([SystemMessage(content="あなたは転職エージェントAIとしてユーザーの転職相談に乗ります。必要に応じてヒアリングをするなど、ユーザーニーズに合った提案をしてください。"), HumanMessage(content=prompt)])

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
    print(f"message: {message}")
    if not message:
        return
    return StreamingResponse(
        generate_chat_response(message),
        media_type='text/event-stream'
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
