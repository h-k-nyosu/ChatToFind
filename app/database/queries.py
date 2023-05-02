from opensearch_dsl import Search, Q

from abc import ABC, abstractmethod

from app.schemas import Job as JobSchema
from app.database.opensearch import os_client


class BaseQueries(ABC):
    @abstractmethod
    def get_job(self, job_id: str):
        pass

    @abstractmethod
    def get_jobs(self):
        pass

    @abstractmethod
    def get_custom_jobs(self, query_params: dict):
        pass


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

        if "keyword" in query_params and query_params["keyword"]:
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
                fuzziness="AUTO",
            )

        if "location" in query_params and query_params["location"]:
            if isinstance(query_params["location"], list):
                location_queries = [
                    Q("match_phrase_prefix", location=loc)
                    for loc in query_params["location"]
                ]
                search = search.query(
                    "bool", should=location_queries, minimum_should_match=1
                )
            else:
                search = search.query(
                    "match_phrase_prefix", location=query_params["location"]
                )

        if "min_salary" in query_params and query_params["min_salary"]:
            search = search.filter(
                "range", monthly_salary={"gte": query_params["min_salary"]}
            )

        print("Final Opensearch query: ", search.to_dict())

        response = search.execute()
        return [self._transform_hit_to_job(hit) for hit in response.hits]
