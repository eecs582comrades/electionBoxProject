import threading
import uuid
import picamera2
import time
import json

def camPreview(camID):
    image_list = list()
    camera = picamera2.Picamera2(camID)
    camera.start()
    for i in range(100):
        array = camera.capture_array()
        if not array.any():
            print(f"Error capturing image {i + 1} on camera {camID}")
        time.sleep(0.01)
        image_list.append(array)
    print("REACHED END")
    return image_list