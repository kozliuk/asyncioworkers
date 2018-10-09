import asyncio

LOW_PRIORITY = 3
MEDIUM_PRIORITY = 2
HIGH_PRIORITY = 1
CRITICAL_PRIORITY = 0


class Workers:

    class Task:

        def __init__(self, coro, loop=None):
            super().__init__()
            self.coro = coro
            self.__event = asyncio.Event(loop=loop)
            self.__task = None
            self.__result = None
            self.__exception = None
            self.__in_cancel = None

        async def do(self):
            self.__event.clear()
            try:
                if self.__in_cancel is not None:
                    raise asyncio.CancelledError()
                self.__task = asyncio.get_event_loop().create_task(self.coro)
                self.__result = await self.__task
            except asyncio.CancelledError as err:
                if self.__in_cancel is None:
                    raise err
                self.__exception = err
            except Exception as err:
                self.__exception = err
            finally:
                self.__event.set()

        async def _wait(self):
            await self.__event.wait()

        async def _result(self):
            await self._wait()
            if self.__exception is not None:
                raise self.__exception
            return self.__result

        async def cancel(self):
            self.__in_cancel = True
            if self.__task:
                self.__task.cancel()

        def __lt__(self, other):
            return False

        def __await__(self):
            return self._result().__await__()

    def __init__(self, number=3):
        self.__number = number
        self.__q = asyncio.PriorityQueue()
        self.__workers = []

    async def start(self):
        for num in range(self.__number):
            self.__workers.append(asyncio.get_event_loop().create_task(self.worker(num)))

    async def stop(self):
        for w in self.__workers:
            w.cancel()
        await asyncio.wait(self.__workers)

    async def worker(self, index):
        while True:
            _, _task = await self.__q.get()
            await _task.do()

    async def run_coro(self, coro, *, priority=MEDIUM_PRIORITY):
        _task = Workers.Task(coro)
        await self.__q.put((priority, _task))
        return _task



