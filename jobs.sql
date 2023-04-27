CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    job_type VARCHAR(255) NOT NULL,
    job_summary TEXT NOT NULL,
    job_details TEXT NOT NULL,
    monthly_salary INT NOT NULL,
    location VARCHAR(255) NOT NULL
);