# import requests
#
# host = "192.168.1.31"
# response = requests.get(f"http://{host}/stop")
# print(response.content)

import cv2
import urllib.request
import numpy as np

stream = urllib.request.urlopen('http://192.168.1.31/cam.mjpeg')
bytes = bytes()
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        i = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('ESP32 camera', i)
        if cv2.waitKey(1) == 27:
            exit(0)
