"""
Tests for data generation module
"""
from eyedatagen.datagen import DataGen
import pytest


def test_datagen_get_message_type():
    """
    verify that returned type of message is dict
    """
    msg = next(DataGen.get_message())
    assert isinstance(msg, dict)


def test_datagen__get_message_schema():
    """
    verify schema of the message
    """
    msg = next(DataGen.get_message())

    try:
        for v in [
            "timestamp",
            "id",
            "confidence",
            "normalizedX",
            "normalizedY",
                "pupildiameter"]:
            _ = msg[v]
    except KeyError:
        print(f"Item {v} was not found in schema")
        raise


def test_datagen__get_message_format():
    """
    check that values conforms to message format
    """
    msg = next(DataGen.get_message())

    fmt = {
        "timestamp": int,
        "id": int,
        "confidence": float,
        "normalizedX": float,
        "normalizedY": float,
        "pupildiameter": int}

    for k, v in fmt.items():
        value = msg[k]
        value_type = v
        assert isinstance(value, value_type)


def test_datagen__get_message_rate():
    """
    will test that message producing rate is fast enough
    """
    import time
    msg_gen = DataGen.get_message()
    inc = 0
    # run for 2 seconds
    t_end = time.time() + 2
    while time.time() < t_end:
        _ = next(msg_gen)
        inc += 1

    # rate messages per second
    rate = inc // 2
    print(f"\n Message generation rate is {rate} per sec \n")
    assert rate > 60
