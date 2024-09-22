#!/usr/bin/env python3
import socket
import numpy as np
import time
import sys
from picamera2 import Picamera2

class UnixSocketClient:
    def __init__(self, socket_addr, config, retry_interval=1):
        self.socket_addr = socket_addr
        self.retry_interval = retry_interval
        self.camera = self.initialize_camera(config)
        self.sock = None

    def initialize_camera(self, config):
        camera = Picamera2()
        config = camera.create_preview_configuration(config)
        camera.align_configuration(config) # in case of use of bad format
        camera.configure(config)
        camera.start()
        return camera

    def wait_for_server(self):
        # Continuously attempt to connect to the server
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(self.socket_addr)
                print("Connected to server.")
                break
            except socket.error:
                print(f"Server not available. Retrying in {self.retry_interval} second(s)...")
                time.sleep(self.retry_interval)

    def reconnect_on_broken_pipe(self):
        # Reconnect to the server in case of a broken pipe
        print("Broken pipe detected, attempting to reconnect...")
        if self.sock:
            self.sock.close()  # Close the old socket
        self.wait_for_server()

    def send_frames(self):
        try:
            while True:
                # Capture image as numpy array
                array = self.camera.capture_array("main")
                arr2_pack = array.tobytes()

                try:
                    self.sock.sendall(arr2_pack)
                except BrokenPipeError:
                    self.reconnect_on_broken_pipe()
                    
        except KeyboardInterrupt:
            print("\nInterrupted! Closing the client...")
        finally:
            self.close_socket()

    def close_socket(self):
        # Close the socket if is open
        if self.sock:
            self.sock.close()
            print("Socket closed.")

if __name__ == "__main__":

    socket_addr = "/tmp/bfmc_socket.sock"

    config = {
        "size": (320, 240),  
        "format": "RGB888"
    }

    client = UnixSocketClient(socket_addr, config, retry_interval = 2)

    try:
        client.wait_for_server()
        client.send_frames()
    except KeyboardInterrupt:
        print("\n Exiting ...")
        client.close_socket()
        sys.exit(0)
