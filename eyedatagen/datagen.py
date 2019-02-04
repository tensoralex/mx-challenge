"""
Simulates Eye Tracking Device
"""
import time
import random


class DataGen:

    @staticmethod
    def get_message():
        """
        Simulate generation of message by Eye Tracking Device
        Message format:
            timestamp - nanoseconds
            ID - 0 - left eye, 1 - right eye
            confidence - 0 no confidence, 1 - perfect confidence
            normalizedX - Normalized x coordinate of pupil location 0 - left, 1 - right
            normalizedY - Normalized y coordinate of pupil location 0 - bottom, 1 - up
            pupildiameter - diameter of pupil in image pixels

        :return: dict
        """

        while True:
            timestamp = time.time_ns()
            id = random.randint(0, 1)
            confidence = random.uniform(0, 1)
            normalizedX = random.betavariate(3, 3)
            normalizedY = random.betavariate(5, 5)
            pupildiameter = random.randint(1, 100)

            yield {"timestamp": timestamp,
                   "id": id,
                   "confidence": confidence,
                   "normalizedX": normalizedX,
                   "normalizedY": normalizedY,
                   "pupildiameter": pupildiameter}
