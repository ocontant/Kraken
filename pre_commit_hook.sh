#!/bin/bash

# Get the commit message from the staged commit
COMMIT_MSG=$(git log -1 --pretty=%B)

# Check if there are any changes in model files
CHANGED_MODELS=$(git diff --cached --name-only | grep 'krakenfx/repository/models/')

if [ -n "$CHANGED_MODELS" ]; then
  echo "Detected changes in models. Generating new Alembic migration with message: $COMMIT_MSG"
  poetry run alembic revision --autogenerate -m "$COMMIT_MSG"

  # Add the new migration file to the commit
  git add alembic/versions/*
else
  echo "No changes in models detected."
fi
