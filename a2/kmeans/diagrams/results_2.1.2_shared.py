# results_2.1.2_shared.py
#
# Reads results/results_2.1.2_shared.txt (seq + naive, default affinity)
# and generates three bar plots for 2.1.2 (shared clusters):
#   - images/2.1.2_shared_time.png          (Time vs Threads)
#   - images/2.1.2_shared_speedup.png       (Speedup vs seq)
#   - images/2.1.2_shared_speedup_par1.png  (Speedup vs 1-thread parallel)
#
# x-axis:  ["seq", "1", "2", "4", "8", "16", "32", "64"]
# time:    total runtime for each configuration
# speedup: seq_time / time   (original diagram)
# speedup_par1: T_1 / time   (new diagram, baseline: 1-thread parallel)
#
# Times / speedups are printed as labels above each bar.

import os
import math
import matplotlib.pyplot as plt


def parse_results(path):
    runs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if set(line) <= {"-", " "}:
                continue

            parts = line.split()
            if len(parts) < 12:
                continue

            # Skip header row
            if parts[0].upper() == "KIND":
                continue

            kind = parts[0]
            run_tag = parts[1]
            bin_name = parts[2]
            threads = int(parts[3])
            aff = parts[4]
            size = int(parts[5])
            coords = int(parts[6])
            clusters = int(parts[7])
            loops = int(parts[8])
            nloops = int(parts[9])
            total_s = float(parts[10])
            per_loop_s = float(parts[11])

            runs.append(
                {
                    "KIND": kind,
                    "RUN_TAG": run_tag,
                    "BIN": bin_name,
                    "THREADS": threads,
                    "AFF": aff,
                    "SIZE": size,
                    "COORDS": coords,
                    "CLUSTERS": clusters,
                    "LOOPS": loops,
                    "NLOOPS": nloops,
                    "TOTAL": total_s,
                    "PER_LOOP": per_loop_s,
                }
            )
    return runs


def build_data_for_plots(runs):
    configs = sorted(
        set(
            (r["SIZE"], r["COORDS"], r["CLUSTERS"], r["LOOPS"])
            for r in runs
        )
    )
    if not configs:
        raise RuntimeError("No data rows found in results file.")
    size, coords, clusters, loops = configs[0]

    runs = [
        r for r in runs
        if (r["SIZE"], r["COORDS"], r["CLUSTERS"], r["LOOPS"]) == (size, coords, clusters, loops)
    ]

    seq_runs = [r for r in runs if r["KIND"] == "serial"]
    if not seq_runs:
        raise RuntimeError("No serial (seq_kmeans) run found.")
    seq_time = seq_runs[0]["TOTAL"]

    naive_runs = [r for r in runs if r["KIND"] == "naive"]
    naive_runs.sort(key=lambda r: r["THREADS"])

    labels = ["seq"] + [str(r["THREADS"]) for r in naive_runs]
    times = [seq_time] + [r["TOTAL"] for r in naive_runs]
    speedups = [seq_time / t if t > 0 else math.nan for t in times]

    return labels, times, speedups, (size, coords, clusters, loops)


def add_bar_labels(ax, bars, fmt="{:.4f}", fontsize=8):
    for rect in bars:
        height = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            height,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # If your .txt is in the same directory, remove "results" below
    results_path = os.path.join(base_dir, "results", "results_2.1.2_shared.txt")
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    runs = parse_results(results_path)
    labels, times, speedups, cfg = build_data_for_plots(runs)
    size, coords, clusters, loops = cfg

    x = list(range(len(labels)))

    # 1) Time bar plot (unchanged)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x, times)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Configuration (seq and number of threads)")
    ax.set_ylabel("Time (s)")
    ax.set_title(
        f"K-means (shared clusters, naive) — Time vs Threads (default affinity)\n"
        f"Size={size}, Coords={coords}, Clusters={clusters}, Loops={loops}"
    )
    add_bar_labels(ax, bars, fmt="{:.4f}")

    fig.tight_layout()
    out_path_time = os.path.join(images_dir, "2.1.2_shared_time.png")
    fig.savefig(out_path_time, dpi=150)
    plt.close(fig)

    # 2) Speedup bar plot w.r.t. seq (unchanged)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x, speedups)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Configuration (seq and number of threads)")
    ax.set_ylabel("Speedup (seq_time / time)")
    ax.set_title(
        f"K-means (shared clusters, naive) — Speedup vs Threads (default affinity)\n"
        f"Size={size}, Coords={coords}, Clusters={clusters}, Loops={loops}"
    )
    add_bar_labels(ax, bars, fmt="{:.2f}")

    fig.tight_layout()
    out_path_speed = os.path.join(images_dir, "2.1.2_shared_speedup.png")
    fig.savefig(out_path_speed, dpi=150)
    plt.close(fig)

    # 3) New: Speedup bar plot w.r.t. 1-thread parallel
    if "1" not in labels:
        raise RuntimeError("No 1-thread parallel run found in labels.")
    idx_1 = labels.index("1")
    t1 = times[idx_1]

    speedups_par1 = [t1 / t if t > 0 else math.nan for t in times]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(x, speedups_par1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Configuration (seq and number of threads)")
    ax.set_ylabel("Speedup (T_1 / time)")
    ax.set_title(
        f"K-means (shared clusters, naive) — Speedup vs Threads\n"
        f"(baseline: 1-thread parallel, default affinity)\n"
        f"Size={size}, Coords={coords}, Clusters={clusters}, Loops={loops}"
    )
    add_bar_labels(ax, bars, fmt="{:.2f}")

    fig.tight_layout()
    out_path_speed_par1 = os.path.join(images_dir, "2.1.2_shared_speedup_par1.png")
    fig.savefig(out_path_speed_par1, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
