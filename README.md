A Docker-based setup with two containers. One for capturing and streaming video frames from a PiCamera Module 3 Wide using Picamera2, and another for receiving and processing these frames.

use this to allow the display of frames by opencv 
```bash
xhost +local:docker
```

To run the code  

```bash
cd /picamera2-noetic
docker compose build
docker compose up
```
When you close the containers
```bash
docker compose down
```


