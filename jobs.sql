-- jobs.sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    job_type VARCHAR(255) NOT NULL,
    job_summary TEXT NOT NULL,
    job_details TEXT NOT NULL,
    location VARCHAR(255) NOT NULL
);
