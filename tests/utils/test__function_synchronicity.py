import asyncio

import pytest

from pyscope.utils import _force_async, _force_sync


def test__forceaync():
    @_force_async
    def t():
        import time

        time.sleep(1)
        return True

    @_force_sync
    async def main():
        import asyncio

        # if it were to execute sequentially, it would take 10 seconds, in this case we expect to see only 1 second
        futures = list(map(lambda x: t(), range(10)))
        return await asyncio.gather(*futures)

    assert main() == [True] * 10


def test__forcesync():
    @_force_sync
    async def fn():
        return 1

    assert fn() == 1
