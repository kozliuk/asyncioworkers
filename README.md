# asyncioworkers
easy way to create workers in asyncio
```python3
import asyncio
import random

import asyncioworkers


async def coro(index):
    for i in range(5):
        await asyncio.sleep(1)
        print("Task {}:".format(index), i)
    return 0


async def producer(w):
    tasks = []
    for i in range(1000):
        task = await w.run_coro(coro(i),
                                priority=random.randint(asyncioworkers.CRITICAL_PRIORITY, asyncioworkers.LOW_PRIORITY))
        tasks.append(task)
    for task in asyncio.as_completed(tasks):
        await task


async def _main():
    workers = asyncioworkers.Workers(100)
    await workers.start()
    await producer(workers)
    await workers.stop()
    del workers


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
```
