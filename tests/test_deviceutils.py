"""
Tests for device utils module
"""
import asyncio
from componentA.deviceutils import DeviceUtils
import pytest
from tests.utils import run_async_task

def test_deviceutils_get_device_data():
    """
    Verify schema of received message
    """

    deviceutils = DeviceUtils()

    message = deviceutils.get_device_data()

    try:
        for v in [
            "timestamp",
            "id",
            "confidence",
            "normalizedX",
            "normalizedY",
                "pupildiameter"]:
            _ = message[v]
    except KeyError:
        print(f"Item {v} was not found in schema")
        raise


def test_deviceutils_reformat_message():
    """
    Verify message converted to JSON
    """
    import json
    deviceutils = DeviceUtils()

    message = deviceutils.get_device_data()

    json_msg = DeviceUtils.reformat_message(message)

    assert json.loads(json_msg) == message


def test_deviceutils_push_data_to_buffer():
    """
    Verify message are being accumalted in buffer
    """
    device = DeviceUtils()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_async_task(device.push_data_to_buffer()))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    queue_size = device.local_buffer.qsize()

    assert queue_size > 0
