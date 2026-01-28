#!/usr/bin/env bash
set -euo pipefail

MODELS=("${@:-moondream}")

for model in "${MODELS[@]}"; do
  # Check if model already exists
  if ollama list | grep -q "^${model}"; then
    echo "Model '$model' already exists, skipping pull"
  else
    echo "Pulling $model"
    ollama pull "$model"
  fi
done
