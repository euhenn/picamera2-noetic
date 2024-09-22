#!/usr/bin/env python3
import socket
import numpy as np
import cv2
import os
import sys
import signal

class UnixSocketServer:
    def __init__(self, socket_addr="/tmp/bfmc_socket.sock", frame_size=(320, 240)):
        self.socket_addr = socket_addr
        self.frame_size = frame_size
        self.msg_size = frame_size[0] * frame_size[1] * 3  # 230400 bytes for 320x240 RGB frames
        self.server_socket = None
        self.conn = None
        self.data = b''

    def setup_socket(self):
        # Remove socket if it already exists
        if os.path.exists(self.socket_addr):
            os.remove(self.socket_addr)

        # Create and bind the Unix socket
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_addr)
        self.server_socket.listen(1)
        print("Server setup complete. Waiting for connection...")

    def accept_connection(self):
        try:
            self.conn, _ = self.server_socket.accept()
            print("Client connected.")
        except socket.error:
            print("Error accepting client connection.")

    def receive_frame(self):
        try:
            while len(self.data) < self.msg_size:
                packet = self.conn.recv(4096)
                if not packet:
                    raise ConnectionError("Client disconnected.")
                self.data += packet

            # Get full frame and save remainder
            frame_data = self.data[:self.msg_size]
            self.data = self.data[self.msg_size:]
            frame = np.frombuffer(frame_data, dtype=np.uint8).reshape(self.frame_size[1], self.frame_size[0], 3)
            return True, frame
        except (ConnectionError, socket.error):
            print("Connection lost. Waiting for reconnection...")
            self.conn.close()
            self.accept_connection()
            return False, None

    def close(self):
        if self.conn:
            self.conn.close()
        if self.server_socket:
            self.server_socket.close()
        cv2.destroyAllWindows()

def signal_handler(sig, frame):
    print("\nShutting down the server...")
    server.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    server = UnixSocketServer()
    server.setup_socket()
    server.accept_connection()

    try:
        while True:
            ret, frame = server.receive_frame()
            if ret:
                cv2.imshow('Received Frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        server.close()
        
# remove the warning using: chmod 0700  /run/user/1000/
