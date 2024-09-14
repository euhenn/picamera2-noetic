#!/usr/bin/env python3
import socket
import os

if __name__ == "__main__":
    socket_addr = "/var/run/docker.sock"
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    if os.path.exists(socket_addr):
        os.unlink(socket_addr)
    s.bind(socket_addr)
    s.listen(2)
    conn, _ = s.accept()
    #print("Connection accepted")

    # Write the received H264 stream to a file
    with open('/output/video.h264', 'wb') as f:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            f.write(data)

    conn.close()
    s.close()
