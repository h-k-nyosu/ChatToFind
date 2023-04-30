from typing import List
from .models import Job
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session


def get_job(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()


def get_jobs(db: Session):
    return db.query(Job).all()


def get_custom_jobs(db: Session, query_params: dict):
    query = db.query(Job)

    # Filter
    if "keyword" in query_params:
        keyword = query_params["keyword"]
        print(f"keyword: {keyword}")
        query = query.filter(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.job_type.ilike(f"%{keyword}%"),
                Job.job_summary.ilike(f"%{keyword}%"),
                Job.job_details.ilike(f"%{keyword}%"),
                Job.location.ilike(f"%{keyword}%"),
            )
        )

    if "job_type" in query_params:
        query = query.filter(Job.job_type.ilike(f"%{query_params['job_type']}%"))

    if "location" in query_params:
        query = query.filter(Job.location.ilike(f"%{query_params['location']}%"))

    if "min_salary" in query_params:
        query = query.filter(Job.monthly_salary >= query_params["min_salary"])

    if "max_salary" in query_params:
        query = query.filter(Job.monthly_salary <= query_params["max_salary"])

    # # Sort
    # if "sort_by" in query_params:
    #     order = query_params.get("order", "asc")
    #     if order == "asc":
    #         query = query.order_by(asc(getattr(Job, query_params["sort_by"])))
    #     elif order == "desc":
    #         query = query.order_by(desc(getattr(Job, query_params["sort_by"])))

    return query.all()
