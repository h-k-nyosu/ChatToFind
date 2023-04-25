.PHONY: install run

install:
	pip -r requirements.txt

run:
	uvicorn app.main:app --reload
