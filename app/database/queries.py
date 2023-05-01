from typing import List
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session
from opensearch_dsl import Search

from abc import ABC, abstractmethod

from app.models import Job as JobModel
from app.schemas import Job as JobSchema
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
        return db.query(JobModel).filter(JobModel.id == job_id).first()

    def get_jobs(db: Session):
        return db.query(JobModel).all()

    def get_custom_jobs(db: Session, query_params: dict):
        query = db.query(JobModel)

        # Filter
        if "keyword" in query_params:
            keyword = query_params["keyword"]
            query = query.filter(
                or_(
                    JobModel.title.ilike(f"%{keyword}%"),
                    JobModel.job_type.ilike(f"%{keyword}%"),
                    JobModel.job_summary.ilike(f"%{keyword}%"),
                    JobModel.job_details.ilike(f"%{keyword}%"),
                    JobModel.location.ilike(f"%{keyword}%"),
                )
            )

        if "job_type" in query_params:
            query = query.filter(
                JobModel.job_type.ilike(f"%{query_params['job_type']}%")
            )

        if "location" in query_params:
            query = query.filter(
                JobModel.location.ilike(f"%{query_params['location']}%")
            )

        if "min_salary" in query_params:
            query = query.filter(JobModel.monthly_salary >= query_params["min_salary"])

        if "max_salary" in query_params:
            query = query.filter(JobModel.monthly_salary <= query_params["max_salary"])

        return query.all()


class OpensearchQueries(BaseQueries):
    def __init__(self):
        self.client = os_client

    def _transform_hit_to_job(self, res):
        job_data = res.__dict__["_d_"]
        job_data["id"] = res.meta["id"]
        return JobSchema(**job_data)

    def get_job(self, job_id: str):
        search = Search(using=self.client, index="jobs").filter("term", _id=job_id)
        response = search.execute()
        return self._transform_hit_to_job(response.hits[0]) if response.hits else None

    def get_jobs(self):
        search = Search(using=self.client, index="jobs").params(size=90)
        response = search.execute()
        return [self._transform_hit_to_job(hit) for hit in response.hits]

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
        return [self._transform_hit_to_job(hit) for hit in response.hits]
