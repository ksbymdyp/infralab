#!/usr/bin/env bash
set -euo pipefail
python3 -m venv /opt/vllm-env
/opt/vllm-env/bin/python -m pip install --upgrade pip
/opt/vllm-env/bin/python -m pip install --no-cache-dir 'vllm==0.31.0'
/opt/vllm-env/bin/python -m pip freeze > pod-packages.txt
nvidia-smi
