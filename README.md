# infralab

Small, hypothesis-driven experiments in model serving and ML infrastructure.

First experiment: serving Qwen2.5-1.5B-Instruct with vLLM on one rented NVIDIA L4. Increasing concurrency from 1 to 16 delivered 12.9× aggregate output throughput with about 12% longer mean response time in one exploratory sweep. See [the experiment notes](experiments/001-concurrency.md) for controls and limitations.

![Concurrency results](results/2026-10-12-l4/concurrency.png)

## Run on a GPU Pod

Use the Runpod PyTorch template with Python 3.12, SSH access, and enough container disk for packages and model weights. The initial run used 30 GB and no persistent volume.

```bash
bash scripts/setup-pod.sh
bash scripts/serve.sh
```

Leave the server running. In a second terminal:

```bash
bash scripts/benchmark.sh exploratory
# Next experiment: explicit temperature 0 and three repeats, up to concurrency 64
bash scripts/benchmark.sh confirmatory
```

Keep long-running processes in a terminal multiplexer such as tmux, if installed, to survive SSH disconnects. Export results before terminating a Pod with only container storage. GPU performance benchmarks run on the Pod; Codespaces can hold source code and analyze results.

## Analyze locally or in Codespaces

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
python scripts/analyze.py results/2026-10-12-l4
```

The analysis validates request/token counts and writes `summary.csv` and `concurrency.png`. For repeated runs, plot markers show means and error bars show sample standard deviations. The original JSON files are retained without editing their measured values.
