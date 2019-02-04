from multiprocessing import Value, Lock
import asyncio
import time
import json
import yaml
from .message_store import AvroPersist


# We use message buffer to accumulate incoming messages and flush the into
# disk every 10 seconds
message_buffer = asyncio.Queue()


class Metrics:
    """
    Thread safe variables to capture metrics
    """

    def __init__(self, initval=0):
        self.cnt = Value("i", initval)
        self.prev = Value("i", initval)
        self.latency = Value("i", initval)
        self.lock = Lock()

    def inc_cnt(self):
        """
        Increment counter
        :return: None
        """
        with self.lock:
            self.cnt.value += 1

    def reset_cnt(self):
        """
        Reset counter
        :return: None
        """
        with self.lock:
            self.cnt.value = 0

    @property
    def counter_value(self):
        """
        Get value from counter
        :return: int
        """
        with self.lock:
            return self.cnt.value

    @property
    def previous_value(self):
        """
        Get previously save value of counter
        :return: int
        """
        with self.lock:
            return self.prev.value

    @previous_value.setter
    def previous_value(self, value):
        """
        Save additional value of the message counter
        :param value: int
        :return: None
        """
        with self.lock:
            self.prev.value = value

    @property
    def msg_latency(self):
        """
        Get saved latency value in nanoseconds
        :return: int
        """
        with self.lock:
            return self.latency.value

    @msg_latency.setter
    def msg_latency(self, latency):
        """
        Save latency value in nanoseconds
        :param latency: int
        :return: None
        """
        with self.lock:
            self.latency.value = latency


async def flush_buffer(avro):
    """
    Save accumulated messages into disk
    :param avro: class AvroPersist
    :return: None
    """
    qsize = message_buffer.qsize()
    messages = []
    for i in range(qsize):
        messages.append(await message_buffer.get())
    avro.persist_messages(messages)
    messages = None


async def flusher(metrics, avro):
    """
    Coroutine runs every 10 seconds to flush data into disk and update metrics

    :param metrics: class Metrics
    :param avro: class AvroPersist
    :return: None
    """
    while True:
        await asyncio.sleep(10)
        cnt = metrics.counter_value
        rate = cnt - metrics.previous_value

        # Adjust latency to milliseconds
        latency = round(metrics.msg_latency / 10e+6, 3)

        print(
            f"ComponentB: Received so far {cnt} messages. Average rate is {rate // 10}",
            f" per second. Message transport latency {latency} ms")

        metrics.previous_value = cnt

        # Initiate flush data to disk
        await flush_buffer(avro)


async def message_handler(reader, writer, metrics, whitelisted):
    """
    Async coroutine which triggered every time message received from ComponentA

    :param reader: Reader stream
    :param writer: Writer stream (not used)
    :param whitelisted: List of IPs from which messages will be accepted
    :type whitelisted: List
    :return: None
    """

    # get an IP address of message sender
    client_ip, port = writer.get_extra_info('peername')

    # If client not whitelisted discard the message
    if client_ip not in whitelisted:
        return

    while True:

        # Increment message counter
        metrics.inc_cnt()

        # Reading a message (assuming one message is not larger 1024 Bytes)
        data = await reader.readline()

        if not data:
            continue

        data_str = data.decode()

        # Convert message to JSON
        message = json.loads(data_str)

        # Calculating latency from timestamp in message and current timestmap
        msg_latency = time.time_ns() - message["timestamp"]
        metrics.msg_latency = msg_latency

        # Put message into flush queue
        await message_buffer.put(message)


def launch_consumer():
    """
    Launch TCP server and listen for messages
    :return: None
    """

    with open("config.yaml", 'r') as yml_file:
        try:
            config = yaml.load(yml_file)
            # IP addresses from which we would like to receive messages
            ip_whitelist = config["componentB"]["ip_whitelist"]
            listen_on = config["componentB"]["listen_on"]
            on_port = config["componentB"]["port"]
        except yaml.YAMLError as ex:
            print(ex)
            raise

    tsmetrics = Metrics()

    # Instantiating class to work with Avro format
    avro = AvroPersist()

    # Getting AsyncIO loop and creating tasks
    loop = asyncio.get_event_loop()
    loop.create_task(flusher(tsmetrics, avro))
    coro = asyncio.start_server(
        lambda r, w: message_handler(
            r,
            w,
            tsmetrics,
            ip_whitelist),
        listen_on,
        on_port,
        loop=loop)
    server = loop.run_until_complete(coro)

    # Listen for messages until Ctrl+C is pressed
    print(f'ComponentB: Listening on {server.sockets[0].getsockname()}')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server loop
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
