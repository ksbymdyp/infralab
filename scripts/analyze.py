"""Validate benchmark results, write a CSV summary, and plot measured values."""
import argparse
import csv
import json
import statistics
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
args = parser.parse_args()
rows = []
for path in args.directory.glob("concurrency-*.json"):
    d = json.loads(path.read_text())
    if d["completed"] != 100 or d["failed"] != 0:
        raise ValueError(f"Incomplete or failed run: {path}")
    if d["total_input_tokens"] != 51200 or d["total_output_tokens"] != 12800:
        raise ValueError(f"Unexpected token counts: {path}")
    rows.append(dict(file=path.name, concurrency=d["max_concurrency"],
                     output_tokens_per_second=d["output_throughput"],
                     mean_response_seconds=statistics.mean(d["latencies"]),
                     median_ttft_ms=d["median_ttft_ms"],
                     p99_ttft_ms=d["p99_ttft_ms"]))
rows.sort(key=lambda r: (r["concurrency"], r["file"]))
if not rows:
    raise ValueError("No benchmark files found")
with (args.directory / "summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
for ax, key, label in zip(axes,
        ["output_tokens_per_second", "mean_response_seconds"],
        ["Output throughput (tokens/s)", "Mean response time (s)"]):
    groups = {}
    for row in rows:
        groups.setdefault(row["concurrency"], []).append(row[key])
    x = sorted(groups)
    means = [statistics.mean(groups[c]) for c in x]
    ax.plot(x, means, marker="o")
    if any(len(groups[c]) > 1 for c in x):
        ax.errorbar(x, means, yerr=[statistics.stdev(groups[c]) if len(groups[c]) > 1 else 0 for c in x], fmt="none", capsize=4)
    ax.set_xscale("log", base=2)
    ax.set_xticks(x, labels=[str(c) for c in x])
    ax.set_xlabel("Maximum concurrent requests")
    ax.set_ylabel(label)
    ax.grid(alpha=0.2)
fig.suptitle("Qwen2.5-1.5B-Instruct · 512 input / 128 output tokens")
fig.savefig(args.directory / "concurrency.png", dpi=180)
plt.close(fig)
for row in rows:
    print(f"{row['concurrency']:>2}: {row['output_tokens_per_second']:.2f} tok/s, {row['mean_response_seconds']:.3f} s")
