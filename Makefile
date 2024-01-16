init: install-deps

install-deps:
	@pip install --upgrade pip setuptools wheel
	@pip install --upgrade poetry
	@poetry install --no-root
	@pre-commit install --hook-type commit-msg
	@pre-commit run --all-files


run:
	@poetry run uvicorn src.entrypoint:app --reload

seed:
	@poetry run python -m src.database.seeds

create-tables:
	@poetry run python -m src.database.tables
