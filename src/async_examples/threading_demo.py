import time, random, statistics, argparse, os
from concurrent.futures import ThreadPoolExecutor, as_completed

def pct(arr, q: float) -> float:
    """Phân vị q (0..1) đơn giản, không cần numpy."""
    if not arr:
        return 0.0
    a = sorted(arr)
    idx = max(0, min(len(a) - 1, int(q * len(a)) - 1))
    return a[idx]

def fake_blocking_io(min_lat: float, max_lat: float) -> None:
    """Mô phỏng I/O blocking bằng sleep đồng bộ."""
    time.sleep(random.uniform(min_lat, max_lat))

def run_threaded(n_tasks: int, workers: int, min_lat: float, max_lat: float):
    latencies = []
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = []
        for _ in range(n_tasks):
            start = time.perf_counter()
            f = pool.submit(fake_blocking_io, min_lat, max_lat)
            f._t0 = start  # đánh dấu thời điểm bắt đầu task
            futures.append(f)

        for f in as_completed(futures):
            _ = f.result()
            latencies.append(time.perf_counter() - f._t0)

    elapsed = time.perf_counter() - t0
    thr = n_tasks / elapsed if elapsed > 0 else float("inf")
    mean_ms = statistics.fmean(latencies) * 1000 if latencies else 0.0
    return {
        "elapsed": elapsed,
        "throughput": thr,
        "mean_ms": mean_ms,
        "p95_ms": pct([l * 1000 for l in latencies], 0.95),
        "p99_ms": pct([l * 1000 for l in latencies], 0.99),
        "results_len": len(latencies),
    }

def run_sequential(n_tasks: int, min_lat: float, max_lat: float):
    latencies = []
    t0 = time.perf_counter()
    for _ in range(n_tasks):
        t_task = time.perf_counter()
        fake_blocking_io(min_lat, max_lat)
        latencies.append(time.perf_counter() - t_task)

    elapsed = time.perf_counter() - t0
    thr = n_tasks / elapsed if elapsed > 0 else float("inf")
    mean_ms = statistics.fmean(latencies) * 1000 if latencies else 0.0
    return {
        "elapsed": elapsed,
        "throughput": thr,
        "mean_ms": mean_ms,
        "p95_ms": pct([l * 1000 for l in latencies], 0.95),
        "p99_ms": pct([l * 1000 for l in latencies], 0.99),
        "results_len": len(latencies),
    }

def pretty_print(title: str, stats: dict):
    print(f"\n[{title}]")
    print(
        f"elapsed={stats['elapsed']:.4f}s | throughput={stats['throughput']:.2f}/s | "
        f"mean={stats['mean_ms']:.2f} ms | p95={stats['p95_ms']:.2f} ms | "
        f"p99={stats['p99_ms']:.2f} ms | results={stats['results_len']}"
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Threading demo for blocking I/O")
    ap.add_argument("--tasks", type=int, default=200, help="Số task")
    ap.add_argument("--workers", type=int, default=min(64, (os.cpu_count() or 8) * 4),
                    help="Số thread trong pool")
    ap.add_argument("--min-latency", type=float, default=0.005, help="Độ trễ tối thiểu (s)")
    ap.add_argument("--max-latency", type=float, default=0.02,  help="Độ trễ tối đa (s)")
    ap.add_argument("--baseline", action="store_true", help="Chạy tuần tự để so sánh")
    args = ap.parse_args()

    print(f"workers={args.workers} | tasks={args.tasks} | lat=[{args.min_latency},{args.max_latency}]s")

    th = run_threaded(args.tasks, args.workers, args.min_latency, args.max_latency)
    pretty_print("ThreadPool (I/O blocking)", th)

    if args.baseline:
        seq = run_sequential(args.tasks, args.min_latency, args.max_latency)
        pretty_print("Baseline (tuần tự, 1 thread)", seq)
        speedup = seq["elapsed"] / th["elapsed"] if th["elapsed"] > 0 else float("inf")
        print(f"\n≈ Speedup ~ {speedup:.2f}x (thread pool so với tuần tự)")
