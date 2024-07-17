# Makefile for Python project setup and initial steps using poetry

# Define variables
POETRY := poetry
PRE_COMMIT := pre-commit

# Targets
.PHONY: all check-poetry install-poetry install-tools setup-pre-commit lint check-format check-types format clean check help

# Default target
all: check-poetry install-tools setup-pre-commit lint check-format check-types

# Check if poetry is installed
check-poetry:
	@which $(POETRY) > /dev/null 2>&1 || $(MAKE) install-poetry

# Install poetry if not installed
install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -
	export PATH="$$HOME/.poetry/bin:$$PATH"

# Install necessary tools using poetry
install-tools: check-poetry
	$(POETRY) install

# Setup pre-commit hooks
setup-pre-commit:
	$(POETRY) run $(PRE_COMMIT) install

# Run all linters
lint:
	$(POETRY) run flake8 --config=.flake8 .
	$(POETRY) run pylint --rcfile=.pylintrc **/*.py

# Check code formatting
check-format:
	$(POETRY) run black --check .
	$(POETRY) run isort --check-only .

# Check types with mypy
check-types:
	$(POETRY) run mypy .

# Format code
format:
	$(POETRY) run black .
	$(POETRY) run isort .

# Clean up
clean:
	rm -rf __pycache__
	find . -name "*.pyc" -exec rm -f {} \;

# Run all checks (lint, format, types)
check: lint check-format check-types

# Help message
help:
	@echo "Usage:"
	@echo "  make all              Install tools, setup pre-commit, run lint, format, and type checks"
	@echo "  make check-poetry     Check if poetry is installed"
	@echo "  make install-poetry   Install poetry"
	@echo "  make install-tools    Install necessary tools using poetry"
	@echo "  make setup-pre-commit Setup pre-commit hooks"
	@echo "  make lint             Run all linters (flake8, pylint)"
	@echo "  make check-format     Check code formatting (black, isort)"
	@echo "  make check-types      Check types with mypy"
	@echo "  make format           Format code with black and isort"
	@echo "  make clean            Clean up temporary files"
	@echo "  make check            Run all checks (lint, format, types)"
	@echo "  make help             Show this help message"
