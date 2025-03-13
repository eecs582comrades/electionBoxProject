import threading
import uuid
import picamera2
import time
import pickle
import cv2
import numpy as np
import os
import shutil

_DEBUG = True

def _processPicturesHelper(array):
    allEdgeIntensity = []
    for i in range(len(array)):
        blurred = cv2.GaussianBlur(array[i], (3, 3), 0)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian_abs = np.uint8(np.absolute(laplacian))
        allEdgeIntensity.append([i, np.mean(laplacian_abs)])
    ranged_images = sorted(allEdgeIntensity, key=lambda x: x[1], reverse=True)
    return array[ranged_images[0][0]]
def processPictures(pickleFile):
    start_time_all = time.perf_counter()

    if _DEBUG:
        print(f"[DEBUG][{time.perf_counter():.3f}] Starting processPictures")
    
    #1. Retrieve Data
    with open(pickleFile, "rb") as curFile:
        data = pickle.load(curFile)

    #2. Various set-up functions for placement of data, importing uuid, etc.
    curUuid = data["uuid"]

    os.makedirs("./cache2", exist_ok=True)
    os.makedirs("./tmp2", exist_ok=True)

    cache_picture_path0 = os.path.join("./cache2", curUuid + "DEBUG0.jpg")
    tmp_picture_path0 = os.path.join("./tmp", curUuid + "DEBUG0.jpg")
    cache_picture_path1 = os.path.join("./cache2", curUuid + "DEBUG1.jpg")
    tmp_picture_path1 = os.path.join("./tmp", curUuid + "DEBUG1.jpg")


    if _DEBUG:
        start_time = time.perf_counter()
        print(f"[DEBUG][{time.perf_counter():.3f}] Starting _processPicturesHelper")
        # print(f"[DEBUG][{time.perf_counter():.3f}] Camera Verification: {data}")

    #3. Here we go - the big processing!
    camera0Image = _processPicturesHelper(data['camera0'])
    camera1Image = _processPicturesHelper(data['camera1'])

    if _DEBUG:
        elapsed = time.perf_counter() - start_time
        print(f"[DEBUG][{time.perf_counter():.3f}] Process Picture Helper took {elapsed:.3f} sec")

    #4. Prep for export and export to temp in ./tmp2
    newData = {
        "camera0": camera0Image,
        "camera1": camera1Image,
        "uuid": data["uuid"]
    }
    
    if _DEBUG:
        start_time = time.perf_counter()

    cv2.imwrite(tmp_picture_path0, camera0Image)
    cv2.imwrite(tmp_picture_path1, camera1Image)
    
    if _DEBUG:
        elapsed = time.perf_counter() - start_time
        print(f"[DEBUG][{time.perf_counter():.3f}] PKL dump took took {elapsed:.3f} sec")

    #5. Move from ./tmp2 to ./cache2

    shutil.move(tmp_picture_path0, cache_picture_path0)
    shutil.move(tmp_picture_path1, cache_picture_path1)

    if _DEBUG:
        
        total_elapsed_all = time.perf_counter() - start_time_all
        print(f"[DEBUG][{time.perf_counter():.3f}] Finished processing => {cache_picture_path0}, total {total_elapsed_all:.3f} sec")

if __name__ == "__main__":
    print("THIS IS DEBUG ONLY - CALL processPictures() DIRECTLY WITH PICKLE FILE FOR PRODUCTION")
    processPictures("./cache1/e74e8404-8fdb-497a-83b2-59109e63c364_preprocessing.pkl")