import asyncio, time, random, statistics, argparse

async def fake_io(min_lat, max_lat):
    await asyncio.sleep(random.uniform(min_lat, max_lat))

async def run(n, concurrency, min_lat, max_lat):
    sem = asyncio.Semaphore(concurrency)
    lats = []

    async def one():
        t0 = time.perf_counter()
        async with sem:
            await fake_io(min_lat, max_lat)
        lats.append(time.perf_counter() - t0)

    t0 = time.perf_counter()
    await asyncio.gather(*(one() for _ in range(n)))
    elapsed = time.perf_counter() - t0
    thr = n / elapsed if elapsed > 0 else float('inf')
    mean_ms = (statistics.fmean(lats) * 1000) if lats else 0.0

    print(f"tasks={n} | elapsed={elapsed:.4f}s | throughput={thr:.2f}/s | mean={mean_ms:.2f} ms")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=2000)
    ap.add_argument("--concurrency", type=int, default=100)
    ap.add_argument("--min-latency", type=float, default=0.0005, help="Minimum latency (s)")
    ap.add_argument("--max-latency", type=float, default=0.02, help="Maximum latency (s)")
    args = ap.parse_args()
    asyncio.run(run(args.tasks, args.concurrency, args.min_latency, args.max_latency))

