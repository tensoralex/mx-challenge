"""
Reads messages from local buffer and transports them to componentB
"""
import asyncio
import time
import yaml
from .deviceutils import DeviceUtils


class ClientProtocol(asyncio.Protocol):
    """
    Implements handlers of async events for client
    """

    def connection_made(self, transport):
        """
        Invoked when TCP connection is established
        :param transport:
        :return: None
        """
        self.transport = transport
        print(f"Connection to componentB estbalished..,")

    def data_received(self, data):
        """
        Dummy. When data received from componentB
        :param data:
        :return: None
        """
        pass

    def connection_lost(self, exc):
        """
        Invoked when connection to componentB is lost
        :param exc: Exception
        :return: None
        """
        print("Lost connection with the server")
        self.transport_message().close()


async def transport_message(util_cls, workers, connection, transport):
    """
    Async method to prepare and send message to componentB
    when messages are present in local buffer
    :param util_cls: class DeviceUtils
    :return: None
    """

    # Setting variables to calculate metrics
    interval = 10  # seconds
    period = time.time() + interval
    counter, rate, qsize = (0, 0, 0)

    # Main loop
    while True:
        # Display metrics when 10 seconds passed
        if time.time() > period:
            period = time.time() + interval
            rate = counter // interval
            avg_qsize = qsize / counter
            qsize = 0
            counter = 0
            print(
                f"ComponentA: Average message rate is {rate} per sec and average queue size {avg_qsize}")

        qsize += util_cls.local_buffer.qsize()
        counter += 1


        # Receive message from local buffer
        message = await util_cls.local_buffer.get()
        # Convert message to JSON
        network_message = util_cls.reformat_message(message)

        # Push message to componentB
        transport.write(network_message.encode() + b"\n")


def launch_workers():
    """
    Method launches asyncio loop to message simulation and transport them
    to componentB
    :return: None
    """
    # Reading configuration from config.yaml
    with open("config.yaml", 'r') as yml_file:
        try:
            config = yaml.load(yml_file)
            # IP addresses from which we would like to receive messages
            connect_to = config["componentA"]["connect_to"]
            on_port = config["componentA"]["port"]
            connection = (connect_to, on_port)
            # Number of devices to simulate
            num_of_devices = config["componentA"]["num_of_devices"]
        except yaml.YAMLError as ex:
            print(f"Exception during reading configuration {ex}")
            raise

    # Get asyncio loop
    workers = asyncio.get_event_loop()
    # Instantiate message class
    device = DeviceUtils()

    # Establish connection to componentB
    coro = workers.create_connection(ClientProtocol, *connection)

    # We need transport to write stream of messages
    transport, protocol = workers.run_until_complete(coro)

    # Create as many async tasks as we simulate devices
    for i in range(num_of_devices):
        workers.create_task(device.push_data_to_buffer())

    # Setting up reader from local bufferS
    workers.run_until_complete(
        transport_message(
            device,
            workers,
            connection,
            transport))

    # Run the loop
    try:
        workers.run_forever()
    finally:
        workers.run_until_complete(workers.shutdown_asyncgens())
        workers.close()
