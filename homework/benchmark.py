"""Reproducible paired inputs; timing, counting and memory runs are separate."""
import argparse
import csv
import json
import platform
import random
import statistics
import time
import tracemalloc
from pathlib import Path
from sorting import ALGORITHMS, Stats

PATTERNS = ['Random', 'Sorted', 'Reverse', 'Duplicates']
def make_input(pattern, n, seed):
    rng = random.Random(seed)
    if pattern == 'Random':
        return [rng.randrange(10 * n) for _ in range(n)]
    if pattern == 'Sorted':
        return list(range(n))
    if pattern == 'Reverse':
        return list(range(n - 1, -1, -1))
    return [rng.randrange(10) for _ in range(n)]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sizes', nargs='+', type=int, default=[100, 250, 500, 1000, 2000])
    p.add_argument('--repeats', type=int, default=5)
    args = p.parse_args()
    if min(args.sizes) < 2 or args.repeats < 1:
        p.error('sizes must be >= 2 and repeats >= 1')
    Path('results').mkdir(exist_ok=True)
    seed = 20260930
    order_rng = random.Random(seed)
    raw = []
    for fn in ALGORITHMS.values():
        fn([3, 1, 2])  # Untimed warm-up.
    for n in args.sizes:
        for pi, pattern in enumerate(PATTERNS):
            for trial in range(args.repeats):
                source = make_input(pattern, n, seed + n * 100 + pi * 10 + trial)
                expected = sorted(source)
                order = list(ALGORITHMS)
                order_rng.shuffle(order)
                for name in order:
                    a = source.copy()  # Excluded from timing.
                    start = time.perf_counter_ns()
                    ALGORITHMS[name](a)
                    elapsed = (time.perf_counter_ns() - start) / 1e6
                    assert a == expected
                    a = source.copy()
                    s = Stats()
                    ALGORITHMS[name](a, stats=s)  # Untimed counting run.
                    assert a == expected
                    raw.append(dict(n=n, pattern=pattern, trial=trial, algorithm=name,
                                    time_ms=elapsed, comparisons=s.comparisons, writes=s.writes))
            print('completed', pattern, n, flush=True)
    with open('results/raw.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(raw[0])); w.writeheader(); w.writerows(raw)
    summary = []
    for n in args.sizes:
        for pattern in PATTERNS:
            for name in ALGORITHMS:
                group = [r for r in raw if r['n'] == n and r['pattern'] == pattern and r['algorithm'] == name]
                summary.append(dict(n=n, pattern=pattern, algorithm=name,
                    median_ms=statistics.median(r['time_ms'] for r in group),
                    min_ms=min(r['time_ms'] for r in group), max_ms=max(r['time_ms'] for r in group),
                    mean_comparisons=statistics.mean(r['comparisons'] for r in group),
                    mean_writes=statistics.mean(r['writes'] for r in group)))
    with open('results/summary.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0])); w.writeheader(); w.writerows(summary)
    memory = []
    for pattern in PATTERNS:
        source = make_input(pattern, max(args.sizes), seed)
        for name, fn in ALGORITHMS.items():
            a = source.copy()  # Input copy and source are not traced.
            tracemalloc.start()
            fn(a)
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            assert a == sorted(source)
            memory.append(dict(pattern=pattern, algorithm=name, n=len(a), peak_traced_bytes=peak))
    metadata = dict(seed=seed, sizes=args.sizes, repeats=args.repeats,
        python=platform.python_version(), platform=platform.platform(), processor=platform.processor(),
        timer='perf_counter_ns', memory=memory,
        note='Executed by Codex in its Linux execution environment, not on the student laptop.')
    Path('results/environment.json').write_text(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
