.PHONY: install run

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload
