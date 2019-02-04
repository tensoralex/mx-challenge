"""
Utils to read messages from device
"""
import asyncio
import json
from eyedatagen.datagen import DataGen


class DeviceUtils:
    """
    Collection of utils to access messages from device
    """
    FREQ = 62  # Hz

    local_buffer = asyncio.Queue()

    def get_device_data(self):
        """
        Reads  message from a device
        :return: dict
        """
        return next(DataGen.get_message())

    async def push_data_to_buffer(self):
        """
        Push received message to local buffer

        :return:
        """
        freq = self.FREQ

        while True:
            await self.local_buffer.put(self.get_device_data())
            await asyncio.sleep(1 / freq)

    @staticmethod
    def reformat_message(message):
        """
        Transform message to JSON representation
        :param message: dict
        :return: str
        """
        return json.dumps(message)
