#!/usr/bin/env python3
# diagrams.py
#
# Usage:
#   python diagrams.py
#   python diagrams.py --benchmarks ../benchmarks
#
# Generates:
#   time_N64.png, speedup_N64.png
#   time_N1024.png, speedup_N1024.png
#   time_N4096.png, speedup_N4096.png
#   results_full.txt  (tab-separated, with Speedup column)

from pathlib import Path
import argparse
import sys
import re
import matplotlib.pyplot as plt

RE_TIME = re.compile(r"Time\s+([0-9]*\.?[0-9]+)")

EXPECTED_N = [64, 1024, 4096]
EXPECTED_THREADS = [1, 2, 4, 6, 8]

def parse_args():
    default_bench = Path(__file__).resolve().parents[1] / "benchmarks"
    p = argparse.ArgumentParser(description="Plot time & speedup from Game of Life benchmarks and write results_full.txt")
    p.add_argument("--benchmarks", type=Path, default=default_bench,
                   help="Path to the 'benchmarks' directory (default: ../benchmarks)")
    return p.parse_args()

def fail_if_errs(bench_root: Path):
    offending = []
    for n in EXPECTED_N:
        for t in EXPECTED_THREADS:
            d = bench_root / f"N{n}_T{t}"
            err = d / f"life_{t}_{n}.err"
            if not err.exists():
                continue
            try:
                content = err.read_text().strip()
            except Exception as e:
                offending.append((err, f"Could not read: {e}"))
                continue
            if content:
                offending.append((err, content))
    if offending:
        print("ERROR: Found non-empty .err files. Aborting.\n", file=sys.stderr)
        for path, content in offending:
            print(f"--- {path} ---", file=sys.stderr)
            print(content, file=sys.stderr)
            print(file=sys.stderr)
        sys.exit(1)

def read_time_from_out(out_path: Path) -> float:
    if not out_path.exists():
        raise FileNotFoundError(f"Missing .out file: {out_path}")
    text = out_path.read_text(errors="ignore")
    if not text.strip():
        raise ValueError(f".out file is empty: {out_path}")
    first_line = text.splitlines()[0]
    m = RE_TIME.search(first_line)
    if not m:
        raise ValueError(f"Could not parse Time from first line of {out_path!s}:\n{first_line}")
    return float(m.group(1))

def collect_times(bench_root: Path):
    results = {n: {} for n in EXPECTED_N}
    issues = []
    for n in EXPECTED_N:
        for t in EXPECTED_THREADS:
            d = bench_root / f"N{n}_T{t}"
            outp = d / f"life_{t}_{n}.out"
            try:
                tm = read_time_from_out(outp)
                results[n][t] = tm
            except Exception as e:
                issues.append(str(e))
    if issues:
        print("ERROR: Issues with required .out files:\n", file=sys.stderr)
        for m in issues:
            print(f"- {m}", file=sys.stderr)
        sys.exit(1)
    for n in EXPECTED_N:
        have = sorted(results[n].keys())
        if have != EXPECTED_THREADS:
            print(f"ERROR: For N={n} expected threads {EXPECTED_THREADS} but found {have}", file=sys.stderr)
            sys.exit(1)
    return results

def plot_time(n: int, times_by_threads: dict, out_dir: Path):
    threads = sorted(times_by_threads.keys())
    times = [times_by_threads[t] for t in threads]
    plt.figure()
    plt.title(f"Time vs Threads (N={n})")
    plt.xlabel("Threads")
    plt.ylabel("Time (s)")
    plt.plot(threads, times, marker="o")
    plt.xticks(threads)
    plt.grid(True, linestyle="--", linewidth=0.5)
    out_path = out_dir / f"time_N{n}.png"
    plt.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Wrote {out_path}")

def plot_speedup(n: int, times_by_threads: dict, out_dir: Path):
    threads = sorted(times_by_threads.keys())
    t1 = times_by_threads.get(1)
    if t1 is None or t1 <= 0:
        print(f"ERROR: Missing or invalid T1 time for N={n}", file=sys.stderr)
        sys.exit(1)
    speedup = [t1 / times_by_threads[t] for t in threads]
    plt.figure()
    plt.title(f"Speedup vs Threads (N={n})")
    plt.xlabel("Threads")
    plt.ylabel("Speedup (T1 / Tthreads)")
    plt.plot(threads, speedup, marker="o")
    plt.xticks(threads)
    plt.grid(True, linestyle="--", linewidth=0.5)
    out_path = out_dir / f"speedup_N{n}.png"
    plt.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close()
    print(f"Wrote {out_path}")

def write_results_table(results: dict, out_dir: Path):
    """
    Writes results_full.txt with columns:
    N\tThreads\tTime (s)\tSpeedup
    """
    out_path = out_dir / "results_full.txt"
    lines = ["N\tThreads\tTime (s)\tSpeedup"]
    for n in sorted(results.keys()):
        t1 = results[n][1]
        for t in sorted(results[n].keys()):
            time = results[n][t]
            speedup = t1 / time if time > 0 else float("inf")
            lines.append(f"{n}\t{t}\t{time:.6f}\t{speedup:.6f}")
    out_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_path}")

def main():
    args = parse_args()
    bench_root = args.benchmarks
    if not bench_root.exists():
        print(f"ERROR: Benchmarks directory not found: {bench_root}", file=sys.stderr)
        sys.exit(1)

    # 1) Stop if any .err has content
    fail_if_errs(bench_root)

    # 2) Parse .out files
    results = collect_times(bench_root)

    # 3) Plots
    out_dir = Path(__file__).resolve().parent
    for n in EXPECTED_N:
        plot_time(n, results[n], out_dir)
        plot_speedup(n, results[n], out_dir)

    # 4) Table with speedup
    write_results_table(results, out_dir)

if __name__ == "__main__":
    main()
