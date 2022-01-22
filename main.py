import cv2
import urllib.request
import numpy as np
import requests
import threading


def executeCommand(addr: str, cmd: str = "stop"):
    try:
        requests.get(f"http://{addr}/{cmd}")
        print(cmd)
    except requests.exceptions.Timeout or requests.exceptions.ConnectionError:
        print(f"command for {cmd} timed out")


host = "192.168.1.24"

while True:
    try:
        response = requests.get(f"http://{host}/cam-lo.jpg", timeout=0.5)
        jpg = response.content
        image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        try:
            cv2.imshow('ESP32 camera', image)
        except Exception as e:
            print(e)
    except requests.exceptions.Timeout or requests.exceptions.ConnectionError:
        print("Video Frame Timed out")
    except Exception as e:
        print(e)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        exit(0)
    elif key == ord('w'):
        threading.Thread(target=executeCommand, args=(host, "forward")).start()
    elif key == ord('s'):
        threading.Thread(target=executeCommand, args=(host, "backward")).start()
    elif key == ord('a'):
        threading.Thread(target=executeCommand, args=(host, "turnLeft")).start()
    elif key == ord('d'):
        threading.Thread(target=executeCommand, args=(host, "turnRight")).start()
    elif key == 32:
        threading.Thread(target=executeCommand, args=(host, "stop")).start()
