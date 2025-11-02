import asyncio
import time

async def task(name, delay):
    print(f"🔹 {name} bắt đầu (delay {delay}s)...")
    await asyncio.sleep(delay)
    print(f"✅ {name} hoàn thành sau {delay}s")

async def main():
    start = time.time()
    await asyncio.gather(
        task("Tác vụ 1", 2),
        task("Tác vụ 2", 3),
        task("Tác vụ 3", 1),
    )
    print(f"⏱ Tổng thời gian: {time.time() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
