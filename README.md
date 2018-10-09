# asyncioworkers
easy way to create workers in asyncio
```python3
import asyncio
import asyncioworkers


async def coro(index):
    for i in range(5):
        await asyncio.sleep(1)
        print("Task {}:".format(index), i)
    return 0


async def producer(w):
    for i in range(30):
        await w.run_coro(coro(i))
    await asyncio.sleep(3)


async def _main():
    workers = asyncioworkers.Workers()
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
