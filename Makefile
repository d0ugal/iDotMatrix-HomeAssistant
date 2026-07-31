RUFF_VERSION ?= 0.15.8
RUFF = docker run --rm -v "$(PWD)":/src -w /src ghcr.io/astral-sh/ruff:$(RUFF_VERSION)

.PHONY: lint format test

lint:
	$(RUFF) check .
	$(RUFF) format --check .

format:
	$(RUFF) format .

test:
	uvx --with pillow --with pytest --from pytest pytest -q
