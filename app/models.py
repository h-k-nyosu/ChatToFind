from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from app.database import Base


class Item(BaseModel):
    name: str
    image: str


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    job_type = Column(String)
    job_summary = Column(String)
    job_details = Column(String)
    location = Column(String)
