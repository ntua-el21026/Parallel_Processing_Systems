#!/usr/bin/env python3
"""
Generate execution-time diagrams for every results_*.txt table.

Usage:
    python diagrams.py [--metric {total,per_loop}]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List, Tuple

import matplotlib

matplotlib.use("Agg")  # Always render off-screen
import matplotlib.pyplot as plt  # noqa: E402


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
IMAGES_DIR = BASE_DIR / "images"
TAG_RE = re.compile(r"S\d+_N\d+_C\d+_L\d+_T\d+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create one image per results_*.txt file.",
    )
    parser.add_argument(
        "--metric",
        choices=("total", "per_loop"),
        default="total",
        help="Which time column to visualize (default: total).",
    )
    return parser.parse_args()


def parse_results_table(path: Path) -> List[Tuple[int, float, float]]:
    """Return list of (thread_count, total_time, per_loop_time)."""
    rows: List[Tuple[int, float, float]] = []
    with path.open() as file:
        for line in file:
            stripped = line.strip()
            if not stripped or stripped.startswith("KIND") or stripped.startswith("-"):
                continue
            tag_match = TAG_RE.search(line)
            if not tag_match:
                continue
            run_tag = tag_match.group(0)
            tokens = stripped.split()
            if len(tokens) < 2:
                continue
            try:
                total = float(tokens[-2])
                per_loop = float(tokens[-1])
            except ValueError:
                continue
            threads = int(run_tag.rsplit("_T", 1)[-1])
            rows.append((threads, total, per_loop))
    rows.sort(key=lambda entry: entry[0])
    return rows


def series_from_rows(
    rows: Iterable[Tuple[int, float, float]], metric: str
) -> Tuple[List[int], List[float]]:
    xs: List[int] = []
    ys: List[float] = []
    for threads, total, per_loop in rows:
        xs.append(threads)
        ys.append(total if metric == "total" else per_loop)
    return xs, ys


def format_lock_label(path: Path) -> str:
    return path.stem.replace("results_", "").replace("_", " ")


def add_bar_labels(ax: plt.Axes, bars: Iterable[plt.Rectangle], fmt: str = "{:.4f}") -> None:
    for rect in bars:
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            height,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=8,
        )


def plot_results(path: Path, metric: str) -> Path | None:
    rows = parse_results_table(path)
    if not rows:
        return None
    threads, values = series_from_rows(rows, metric)
    lock_name = format_lock_label(path)
    metric_label = "Total time (s)" if metric == "total" else "Per-loop time (s)"
    positions = list(range(len(threads)))
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(positions, values, width=0.6, color="#4472c4")
    ax.set_xticks(positions)
    ax.set_xticklabels([str(t) for t in threads])
    ax.set_title(f"{lock_name} - {metric_label}")
    ax.set_xlabel("Threads")
    ax.set_ylabel(metric_label)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    add_bar_labels(ax, bars)
    output_path = IMAGES_DIR / f"{path.stem}_{metric}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def collect_all_results(metric: str) -> Tuple[List[int], List[str], List[List[float]]]:
    lock_files = sorted(RESULTS_DIR.glob("results_*.txt"))
    lock_labels = [format_lock_label(path) for path in lock_files]
    data_by_thread: dict[int, dict[str, float]] = {}
    for path, label in zip(lock_files, lock_labels):
        rows = parse_results_table(path)
        for threads, total, per_loop in rows:
            value = total if metric == "total" else per_loop
            data_by_thread.setdefault(threads, {})[label] = value
    threads = sorted(data_by_thread.keys())
    matrix: List[List[float]] = []
    for thread in threads:
        per_lock = []
        for label in lock_labels:
            if label not in data_by_thread[thread]:
                raise ValueError(f"Missing data for {label} @ T={thread}")
            per_lock.append(data_by_thread[thread][label])
        matrix.append(per_lock)
    return threads, lock_labels, matrix


def plot_combined(metric: str) -> Path | None:
    threads, lock_labels, matrix = collect_all_results(metric)
    if not threads or not lock_labels:
        return None
    metric_label = "Total time (s)" if metric == "total" else "Per-loop time (s)"
    indices = list(range(len(threads)))
    group_width = 0.8
    num_locks = len(lock_labels)
    bar_width = group_width / num_locks
    fig, ax = plt.subplots(figsize=(10, 6))
    for idx, label in enumerate(lock_labels):
        values = [row[idx] for row in matrix]
        offsets = [
            i - group_width / 2 + idx * bar_width + bar_width / 2 for i in indices
        ]
        ax.bar(offsets, values, width=bar_width, label=label.title())
    ax.set_xticks(indices)
    ax.set_xticklabels([str(t) for t in threads])
    ax.set_xlabel("Threads")
    ax.set_ylabel(metric_label)
    ax.set_title(f"All locks - {metric_label}")
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.legend(ncol=2, fontsize=8)
    output_path = IMAGES_DIR / f"results_all_{metric}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    args = parse_args()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    generated = []
    for txt_file in sorted(RESULTS_DIR.glob("results_*.txt")):
        image_path = plot_results(txt_file, args.metric)
        if image_path:
            generated.append(image_path)
    combined = plot_combined(args.metric)
    if combined:
        generated.append(combined)
    if not generated:
        raise SystemExit("No diagrams produced (no results files?).")
    print(f"Generated {len(generated)} diagram(s):")
    for path in generated:
        print(f" - {path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
