import asyncio


class Workers:

    class Task:

        def __init__(self, coro, loop=None):
            super().__init__()
            self.coro = coro
            self.__event = asyncio.Event(loop=loop)
            self.__task = None
            self._result = None
            self._exception = None
            self.__in_cancel = None

        async def do(self):
            self.__event.clear()
            try:
                if self.__in_cancel is not None:
                    raise asyncio.CancelledError()
                self.__task = asyncio.get_event_loop().create_task(self.coro)
                self._result = await self.__task
            except asyncio.CancelledError as err:
                if self.__in_cancel is None:
                    raise err
                self._exception = err
            finally:
                self.__event.set()

        async def _wait(self):
            await self.__event.wait()

        async def _result(self):
            await self._wait()
            if self._exception is not None:
                raise self._exception
            return self._result

        async def cancel(self):
            self.__in_cancel = True
            if self.__task:
                self.__task.cancel()

        def __await__(self):
            return self._result().__await__()

    def __init__(self, number=3):
        self.__number = number
        self.__q = asyncio.Queue()
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
            _task = await self.__q.get()
            await _task.do()

    async def run_coro(self, coro):
        _task = Workers.Task(coro)
        await self.__q.put(_task)
        return _task



