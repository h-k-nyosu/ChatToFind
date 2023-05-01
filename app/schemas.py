from pydantic import BaseModel


class JobBase(BaseModel):
    title: str
    job_type: str
    job_summary: str
    job_details: str
    monthly_salary: int
    location: str


class Job(JobBase):
    id: str

    class Config:
        orm_mode = True
