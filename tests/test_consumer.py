"""
Test componentB consumer module
"""

from componentB.consumer import *
import pytest
import json
from unittest import TestCase, mock
from tests.utils import run_async_task

DUMMY = {
    "timestamp": 1549230733144805256,
    "id": 0,
    "confidence": 0.6653831692629135,
    "normalizedX": 0.6841786683496842,
    "normalizedY": 0.45015501124320473,
    "pupildiameter": 60}


async def put_in_queue(msg):
    """
    Helper async function to populate queue
    """
    await message_buffer.put(msg)


def dummy_persist(messages):
    """
    Dummy mock function to persist messages
    :param messages: List[Dict]
    """


@mock.patch(
    'componentB.message_store.AvroPersist.persist_messages',
    side_effect=dummy_persist)
def test_consumer_flush_buffer(dummy_persist_funct):
    """
    Test flush buffer function
    """

    avro = AvroPersist()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_async_task(
            put_in_queue(DUMMY)
        ))
        loop.run_until_complete(run_async_task(
            flush_buffer(avro)
        ))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

        expected_result = [DUMMY]

    avro.persist_messages.assert_called_with(expected_result)
