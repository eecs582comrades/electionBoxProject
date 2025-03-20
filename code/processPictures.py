import threading
import uuid
import time
import pickle
import cv2
import numpy as np
import os
import shutil
import gc

_DEBUG = True
_CHUNK_SIZE = 10  # Process images in chunks to manage memory

def cleanup_image(image):
    """Helper to properly cleanup OpenCV images"""
    if image is not None:
        image.flags.writeable = False
        del image
        gc.collect()

def _processPicturesHelper(array):
    """Process images in chunks to manage memory better"""
    if not array:
        return None
        
    try:
        best_image = None
        best_edge_intensity = -1
        
        # Process in chunks to avoid memory overload
        for i in range(0, len(array), _CHUNK_SIZE):
            chunk = array[i:i + _CHUNK_SIZE]
            for img in chunk:
                try:
                    # Process one image
                    blurred = cv2.GaussianBlur(img, (3, 3), 0)
                    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
                    laplacian_abs = np.uint8(np.absolute(laplacian))
                    current_intensity = np.mean(laplacian_abs)
                    
                    # Update best if needed
                    if current_intensity > best_edge_intensity:
                        if best_image is not None:
                            cleanup_image(best_image)  # Cleanup old best image
                        best_image = img.copy()
                        best_edge_intensity = current_intensity
                    
                    # Cleanup intermediate arrays
                    del blurred, laplacian, laplacian_abs
                    
                except Exception as e:
                    print(f"Error processing image: {e}")
                    continue
                    
            # Force cleanup after each chunk
            gc.collect()
            
        return best_image
        
    except Exception as e:
        print(f"Error in _processPicturesHelper: {e}")
        return None
    finally:
        # Ensure cleanup
        gc.collect()

def processPictures(pickleFile):
    """Process pictures with proper resource management"""
    start_time_all = time.perf_counter()
    data = None
    
    try:
        if _DEBUG:
            print(f"[DEBUG][{time.perf_counter():.3f}] Starting processPictures")
        
        # 1. Retrieve Data
        try:
            with open(pickleFile, "rb") as curFile:
                data = pickle.load(curFile)
        except Exception as e:
            print(f"Error loading pickle file: {e}")
            return
            
        if not data or "uuid" not in data:
            print("Invalid data format in pickle file")
            return
            
        # 2. Setup directories
        curUuid = data["uuid"]
        for directory in ["./cache2", "./tmp2"]:
            os.makedirs(directory, exist_ok=True)

        cache_picture_path0 = os.path.join("./cache2", curUuid + "DEBUG0.jpg")
        tmp_picture_path0 = os.path.join("./tmp2", curUuid + "DEBUG0.jpg")
        cache_picture_path1 = os.path.join("./cache2", curUuid + "DEBUG1.jpg")
        tmp_picture_path1 = os.path.join("./tmp2", curUuid + "DEBUG1.jpg")

        if _DEBUG:
            start_time = time.perf_counter()
            print(f"[DEBUG][{time.perf_counter():.3f}] Starting _processPicturesHelper")

        # 3. Process images
        camera0Image = _processPicturesHelper(data.get('camera0', []))
        camera1Image = _processPicturesHelper(data.get('camera1', []))

        if _DEBUG:
            elapsed = time.perf_counter() - start_time
            print(f"[DEBUG][{time.perf_counter():.3f}] Process Picture Helper took {elapsed:.3f} sec")

        # Clear original data to free memory
        data.clear()
        gc.collect()

        # 4. Save processed images
        if camera0Image is not None:
            cv2.imwrite(tmp_picture_path0, camera0Image)
            shutil.move(tmp_picture_path0, cache_picture_path0)
            cleanup_image(camera0Image)
            
        if camera1Image is not None:
            cv2.imwrite(tmp_picture_path1, camera1Image)
            shutil.move(tmp_picture_path1, cache_picture_path1)
            cleanup_image(camera1Image)

        if _DEBUG:
            total_elapsed_all = time.perf_counter() - start_time_all
            print(f"[DEBUG][{time.perf_counter():.3f}] Finished processing => {cache_picture_path0}, total {total_elapsed_all:.3f} sec")
            
    except Exception as e:
        print(f"Error in processPictures: {e}")
    finally:
        # Cleanup
        if data:
            data.clear()
        gc.collect()

if __name__ == "__main__":
    print("THIS IS DEBUG ONLY - CALL processPictures() DIRECTLY WITH PICKLE FILE FOR PRODUCTION")
    processPictures("./cache1/e74e8404-8fdb-497a-83b2-59109e63c364_preprocessing.pkl")