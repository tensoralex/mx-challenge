"""
Starts componentB processes to receive and persist messages from
Eye Tracking simulated device
"""
from componentB.consumer import launch_consumer


if __name__ == "__main__":
    launch_consumer()
