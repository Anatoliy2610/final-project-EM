run:
	uvicorn app.main:app --reload

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

test:
	pytest -v -s

linter:
	ruff check app


docker:
	docker build -t final_app .