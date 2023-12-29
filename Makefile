init: install-deps

install-deps:
	@pip install --upgrade pip setuptools wheel
	@pip install --upgrade poetry
	@poetry install --no-root
	@pre-commit install --hook-type commit-msg
	@pre-commit run --all-files
