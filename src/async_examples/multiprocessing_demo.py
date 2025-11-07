import math,time, statistics, argparse, os
from concurrent.futures import ProcessPoolExecutor, as_completed

def pct(arr, q: float) -> float:
    if not arr:
        return 0.0
    a = sorted(arr)
    idx = max(0, min(len(a) -1, int(q*len(a))-1))
    return a[idx]

def cpu_work(iters:int) -> float:
    s=0.0
    for i in range(1, iters +1):
        s += math.sqrt(i)
    return s

def run_parallel(n_task: int , workers: int, iters_per_task: int):
    lantencies = []
    t0= time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures =[]
        for _ in range(n_task):
            start = time.perf_counter()
            f = pool.submit(cpu_work, iters_per_task)
            f._t0 = start
            futures.append(f)
        results=[]
        for f in as_completed(futures):
            results.append(f.result())
            lantencies.append(time.perf_counter() - f._t0)
    elapsed = time.perf_counter() - t0
    thr = n_task / elapsed if elapsed >0 else float('inf')
    mean_ms = (statistics.fmean(lantencies) * 1000) if lantencies else 0.0
    return {
        "elapsed": elapsed,
        "throughput": thr,
        "mean_ms": mean_ms,
        "p95_ms": pct([l*1000 for l in lantencies], 0.95),
        "p99_ms": pct([l*1000 for l in lantencies], 0.99),
        "results_len": len(results),
    }

def run_sequential(n_task: int, work :int):
    latencies = []
    t0 = time.perf_counter()
    results = []
    for _ in range(n_task):
        t_task = time.perf_counter()
        results.append(cpu_work(work))
        latencies.append(time.perf_counter() - t_task)
    elapsed = time.perf_counter() - t0
    thr = n_task / elapsed if elapsed >0 else float('inf')
    mean_ms = (statistics.fmean(latencies) * 1000) if latencies else 0.0
    return {
        "elapsed": elapsed,
        "throughput": thr,
        "mean_ms": mean_ms,
        "p95_ms": pct([l*1000 for l in latencies], 0.95),
        "p99_ms": pct([l*1000 for l in latencies], 0.99),
        "results_len": len(results),
}

def pretty_print(title: str, stats: dict):
    print(f"\n[{title}  ]")
    print(f" elapsed={stats['elapsed']:.4f}s | throughput={stats['throughput']:.2f}/s | mean={stats['mean_ms']:.2f} ms | p95={stats['p95_ms']:.2f} ms | p99={stats['p99_ms']:.2f} ms | results={stats['results_len']}")     


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multiprocessing CPU-bound tasks demo") 
    parser.add_argument("--tasks", type=int, default=200, help="Number of tasks to run")
    parser.add_argument("--workers", type=int, default=os.cpu_count(), help="Number of worker processes")
    parser.add_argument("--work", type=int, default=100000, help="Number of iterations per task")
    parser.add_argument("--baseline", action="store_true",
                    help="Also run sequential baseline for comparison")
    args = parser.parse_args()  
    print(f"CPU cores: {os.cpu_count()} | workers={args.workers} | tasks={args.tasks} | work={args.work}")
    par = run_parallel(args.tasks, args.workers, args.work)
    pretty_print("ProcessPool (song song)", par)

    if args.baseline:
        seq = run_sequential(args.tasks, args.work)
        pretty_print("Baseline (tuần tự, 1 tiến trình)", seq)
        speedup = seq["elapsed"] / par["elapsed"] if par["elapsed"] > 0 else float("inf")
        print(f"\n≈ Speedup ~ {speedup:.2f}x (song song so với tuần tự)")