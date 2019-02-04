from componentB.message_store import *
import pytest
import json
import io
from unittest import TestCase, mock
from tests.utils import run_async_task

DUMMY_MESSAGE = [{
    "timestamp": 1549230733144805256,
    "id": 0,
    "confidence": 0.6653831692629135,
    "normalizedX": 0.6841786683496842,
    "normalizedY": 0.45015501124320473,
    "pupildiameter": 60}]

DUMMY_SCHEMA = {
    'type': 'record', 'name': 'output.avro.eyegaze', 'fields': [
        {
            'name': 'timestamp', 'type': 'long'}, {
                'default': 0, 'name': 'id', 'type': 'int'}, {
                    'default': 0, 'name': 'confidence', 'type': 'float'}, {
                        'default': 0, 'name': 'normalizedX', 'type': 'float'}, {
                            'default': 0, 'name': 'normalizedY', 'type': 'float'}, {
                                'default': 0, 'name': 'pupildiameter', 'type': 'int'}], '__fastavro_parsed': True}


def open_mock(*args, **kwargs):
    if args[0] == "config.yaml":
        return open(*args, **kwargs)
    else:
        handle = open("unittest.avro", 'w')
        return handle


@mock.patch('componentB.message_store.open', side_effect=open_mock)
@mock.patch('componentB.message_store.fastavro.writer')
def test_avropersist_persist_messages(open_func, writer_func):

    avro = AvroPersist()

    avro.persist_messages(DUMMY_MESSAGE)

    fastavro.writer.assert_called_with(mock.ANY, DUMMY_SCHEMA, DUMMY_MESSAGE)
