.PHONY: setup lint test ingest serve eval download

setup:
	uv sync --all-groups
	uv run pre-commit install

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest || [ $$? -eq 5 ]

ingest:
	uv run python -m ingest.pipeline

serve:
	uv run uvicorn api.main:app --reload

eval:
	uv run python -m eval.run

download:
	uv run python -m ingest.download
