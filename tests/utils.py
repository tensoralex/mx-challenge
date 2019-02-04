"""
Helper functions
"""
import asyncio
from contextlib import suppress
from unittest import mock
from time import sleep

async def run_async_task(async_task):
    """
    Helper function to run infinite async tasks for small amount of time
    :param async_task: task which we want to run for 1 second and then cancel it
    """
    task = asyncio.Task(async_task)

    await asyncio.sleep(1)

    task.cancel()
    with suppress(asyncio.CancelledError):
        # await for task cancellation
        await task

def AsyncMock(*args, **kwargs):
    """
    Mocking async coroutine
    :param args:
    :param kwargs:
    :return: coroutine
    """
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro

async def AsyncSleep(*args, **kwargs):
     await asyncio.sleep(0.001)
     return kwargs.get('return_value')

def nop():
    """
    Do nothing just wait 1 second
    """
    sleep(1)