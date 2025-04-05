# Libraries to import
import cv2
import numpy as np
import os
import threading
import uuid
import picamera2
import time

class camThread(threading.Thread):
    def __init__(self, previewName, camID):
        threading.Thread.__init__(self)
        self.preiewName = previewName
        self.camID = camID
        self.uniqueIdent = uuid.uuid4()
    def run(self):
        print( "STARTING " + self.previewName)
        camPreview(self.previewName, self.camID)

def camPreview(previewName, array):
    image_list = list()
    sharpness_scores = list()
    camera = picamera2.Picamera2(camID)
    camera.start()
    for i in range(100):
        array = camera.capture_array()
        if not array:
            print(f"Error capturing image {i + 1} on camera {camID}")
        time.sleep(0.01)
        sharpness = calculate_sharpness(array)
        sharpness_scores.append(sharpness)
        image_list.append(array)
    camera.release()
    if image_list:
        best_index = np.argmax(sharpness_scores)
        best_image = image_list[best_index]
        cv2.imwrite("best_image_" + camID + ".jpg", best_image)
