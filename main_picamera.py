#!/usr/bin/env python3
import socket
import time
import logging
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FileOutput

# Function to initialize the camera with retries
def initialize_camera(max_retries=5, retry_delay=2):
    """Initialize Picamera2 with retry logic."""
    picam2 = None
    for attempt in range(max_retries):
        try:
            picam2 = Picamera2()
            video_config = picam2.create_video_configuration(raw=picam2.sensor_modes[0])
            picam2.configure(video_config)
            logging.info("Camera successfully initialized.")
            return picam2  # Return the camera instance if successful
        except Exception as e:
            logging.error(f"Camera initialization failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Exiting.")
                raise SystemExit("Camera not detected. Exiting.")  # Exit if retries are exhausted
    return picam2

if __name__ == "__main__":
    # Logging setup for better error reporting
    logging.basicConfig(level=logging.INFO)

    socket_addr = "/var/run/docker.sock"
    
    # Unix socket setup
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(socket_addr)
    except Exception as e:
        logging.error(f"Failed to connect to socket at {socket_addr}: {e}")
        raise SystemExit("Socket connection failed. Exiting.")
    
    # Camera initialization with retry logic
    picam2 = initialize_camera()

    # H264 encoder and stream setup
    encoder = H264Encoder(1000000)
    stream = s.makefile('wb')
    encoder.output = FileOutput(stream)

    try:
        # Start the camera and encoder
        picam2.start_encoder(encoder, quality=Quality.LOW)
        picam2.start()
        logging.info("Recording started. Capturing video for 20 seconds.")
        time.sleep(20)  # Capture video for 20 seconds
        logging.info("Recording completed. Stopping camera.")
        picam2.stop()
        picam2.stop_encoder()
    except Exception as e:
        logging.error(f"Error during video capture: {e}")
    finally:
        # Ensure resources are cleaned up
        logging.info("Closing socket and cleaning up.")
        s.close()

