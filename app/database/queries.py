import openai
import json
import numpy as np
from opensearch_dsl import Search, Q
from typing import Dict, Any

from abc import ABC, abstractmethod

from app.schemas import Job as JobSchema
from app.schemas import JobBase
from app.database.opensearch import os_client
from app.database.pinecone import index


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
                    "title",
                    "job_type",
                    "job_summary",
                    "job_details",
                    "location",
                ],
                type="most_fields",
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


import random
from typing import List


class PineconeQueries(BaseQueries):
    def __init__(self):
        self.index = index

    def _transform_hit_to_job(self, hit: Dict[str, Any]) -> JobSchema:
        metadata = hit["metadata"]
        job_data = json.loads(metadata["content"])
        job_data["id"] = hit["id"]
        return JobSchema(**job_data)

    def get_job(self, job_id: str) -> JobSchema:
        response = self.index.fetch(ids=[job_id])

        return self._transform_hit_to_job(response["vectors"][job_id])

    def get_jobs(self, num_jobs: int = 120) -> List[JobSchema]:
        dimension = self.index.describe_index_stats()["dimension"]
        sample_vector = np.random.rand(dimension).tolist()
        response = self.index.query(
            vector=sample_vector, top_k=num_jobs, include_metadata=True
        )
        matches = response["matches"]
        jobs = []
        for match in matches:
            try:
                job = self._transform_hit_to_job(match)
                jobs.append(job)
            except Exception:
                pass
        print(len(jobs))
        return jobs

    def get_custom_jobs(self, generated_jobs: str) -> List[JobSchema]:
        # generated_jobs の処理

        res = openai.Embedding.create(
            input=generated_jobs, engine="text-embedding-ada-002"
        )
        embed = res["data"][0]["embedding"]

        result = self.index.query(vector=embed, top_k=20, include_metadata=True)
        matches = result["matches"]
        return [self._transform_hit_to_job(hit) for hit in matches]
