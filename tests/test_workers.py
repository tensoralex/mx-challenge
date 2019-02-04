"""
Tests for workers module
"""
from componentA.workers import *
import pytest
import json
from unittest import TestCase, mock
from tests.utils import run_async_task
from componentA.deviceutils import DeviceUtils

DUMMY={
        "timestamp": 1549230733144805256,
        "id": 0,
        "confidence": 0.6653831692629135,
        "normalizedX": 0.6841786683496842,
        "normalizedY": 0.45015501124320473,
        "pupildiameter": 60}

async def dummy_buffer(*args, **kwargs):
    await asyncio.sleep(0.001)

    return DUMMY


@mock.patch('componentA.deviceutils.DeviceUtils.local_buffer.get', side_effect=dummy_buffer)
def test_workers_transport_message(buffer_get_func):
    """
    Test transport message function
    """

    util_cls = DeviceUtils()

    dummy_message = DUMMY

    connection = mock.Mock()

    transport = mock.Mock()
    transport.write = mock.MagicMock(return_value=None)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_async_task(
            transport_message(util_cls, loop, connection, transport)
        ))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    expected_result = json.dumps(dummy_message).encode() + b"\n"

    transport.write.assert_called_with(expected_result)
