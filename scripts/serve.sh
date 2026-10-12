#!/usr/bin/env bash
set -euo pipefail
exec /opt/vllm-env/bin/vllm serve Qwen/Qwen2.5-1.5B-Instruct \
  --host 127.0.0.1 --port 8000 --max-model-len 4096 \
  --gpu-memory-utilization 0.8
