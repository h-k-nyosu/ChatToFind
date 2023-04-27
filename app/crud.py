from typing import List
from .models import Job
from sqlalchemy.orm import Session


def get_job(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def get_jobs(db: Session):
    return db.query(Job).all()
