"""
Starts componentA processes to capture and transport data
from simulated Eye Tracking Device
"""
from componentA.workers import launch_workers

if __name__ == "__main__":
    launch_workers()
