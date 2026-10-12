#!/usr/bin/env bash
set -euo pipefail
# Usage: bash scripts/benchmark.sh exploratory|confirmatory
mode=${1:-confirmatory}
case "$mode" in
  exploratory) levels=(1 2 4 8 16); repeats=1; sampling=() ;;
  confirmatory) levels=(1 2 4 8 16 32 64); repeats=3; sampling=(--temperature 0) ;;
  *) echo 'Expected exploratory or confirmatory' >&2; exit 2 ;;
esac
result_dir="results/$(date -u +%Y%m%dT%H%M%SZ)-${mode}"
mkdir -p "$result_dir"
nvidia-smi > "$result_dir/gpu.txt"
/opt/vllm-env/bin/python -m pip freeze > "$result_dir/packages.txt"
for ((repeat=1; repeat<=repeats; repeat++)); do
  # Reverse alternate sweeps to reduce a consistent order effect.
  order=("${levels[@]}")
  if (( repeat % 2 == 0 )); then
    order=(); for ((i=${#levels[@]}-1; i>=0; i--)); do order+=("${levels[i]}"); done
  fi
  for concurrency in "${order[@]}"; do
    /opt/vllm-env/bin/vllm bench serve \
      --backend openai --base-url http://127.0.0.1:8000 \
      --endpoint /v1/completions --model Qwen/Qwen2.5-1.5B-Instruct \
      --dataset-name random --random-input-len 512 --random-output-len 128 \
      --random-range-ratio 0 --ignore-eos --num-prompts 100 --num-warmups 5 \
      --request-rate inf --max-concurrency "$concurrency" --seed 42 \
      "${sampling[@]}" --save-result --result-dir "$result_dir" \
      --result-filename "concurrency-${concurrency}-repeat-${repeat}.json"
  done
done
echo "Saved results to $result_dir"
