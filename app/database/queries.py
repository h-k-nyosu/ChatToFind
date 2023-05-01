from typing import List
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session
from opensearch_dsl import Search

from abc import ABC, abstractmethod

from app.models import Job
from app.database.opensearch import os_client


class BaseQueries(ABC):
    @abstractmethod
    def get_job(self, db: Session, job_id: int):
        pass

    @abstractmethod
    def get_jobs(self, db: Session):
        pass

    @abstractmethod
    def get_custom_jobs(self, db: Session, query_params: dict):
        pass


class PostgresQueries(BaseQueries):
    def get_job(db: Session, job_id: int):
        return db.query(Job).filter(Job.id == job_id).first()

    def get_jobs(db: Session):
        return db.query(Job).all()

    def get_custom_jobs(db: Session, query_params: dict):
        query = db.query(Job)

        # Filter
        if "keyword" in query_params:
            keyword = query_params["keyword"]
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

        return query.all()


class OpensearchQueries(BaseQueries):
    def __init__(self):
        self.client = os_client

    def get_job(self, job_id: str):
        search = Search(using=self.client, index="jobs").filter("term", _id=job_id)
        response = search.execute()
        return response.hits[0] if response.hits else None

    def get_jobs(self):
        search = Search(using=self.client, index="jobs").params(size=90)
        response = search.execute()
        return response.hits

    def get_custom_jobs(self, query_params: dict):
        search = Search(using=self.client, index="jobs")

        if "keyword" in query_params:
            keyword = query_params["keyword"]
            search = search.query(
                "multi_match",
                query=keyword,
                fields=[
                    "title^3",
                    "job_type",
                    "job_summary",
                    "job_details",
                    "location",
                ],
                type="best_fields",
                tie_breaker=0.3,
            )

        if "min_salary" in query_params:
            search = search.filter(
                "range", monthly_salary={"gte": query_params["min_salary"]}
            )

        response = search.execute()
        return response.hits
