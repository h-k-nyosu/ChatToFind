from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models import Job
from app.database import SessionLocal, engine
from app.dependencies import get_db

import app.crud as crud
import app.models as models
import app.crud as crud
import app.schemas as schemas


app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db)
    jobs_per_row = 3
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
