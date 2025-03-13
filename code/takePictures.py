import threading
import uuid
import time
import pickle
import os
import sys
import shutil
import numpy as np
from picamera2 import Picamera2
from PIL import Image
from collections import deque

_DEBUG = True

# Holds *only the most recent* frame from each camera
latest_frames = {"camera0": None, "camera1": None}

# A single lock to protect read/write access to latest_frames
lock = threading.Lock()

# Initialize both cameras (only done once)
camera0 = Picamera2(0)
time.sleep(1)
camera1 = Picamera2(1)
time.sleep(1)
for cam, cam_id in zip([camera0, camera1], [0, 1]):
    cam.configure(
        cam.create_video_configuration(
            main={
                "format": "YUV420",
                "size": (2028, 1080),
            },
            controls={
                "FrameRate": 20,
                "NoiseReductionMode": 0,
                "Sharpness": 0,
            },
            buffer_count=1,
            queue=False,
        )
    )
    cam.start()
    if _DEBUG:
        print(f"[DEBUG] Camera {cam_id} started.")


def capture_continuous(cam, key):
    """
    Continuously grab frames from the camera and update `latest_frames[key]` with
    the newest frame (numpy array). Only store a single frame in memory at any time.
    """
    global latest_frames
    while True:
        frame = cam.capture_array("main")
        # Hold the lock just long enough to update the dictionary reference
        with lock:
            latest_frames[key] = frame
        # Short sleep to reduce CPU usage
        time.sleep(0.005)


def start_continuous_capture():
    """
    Start background threads that continuously update the global `latest_frames`
    for each camera.
    """
    for cam, key in [(camera0, "camera0"), (camera1, "camera1")]:
        t = threading.Thread(
            target=capture_continuous,
            args=(cam, key),
            daemon=True
        )
        t.start()

    if _DEBUG:
        print("[DEBUG] Continuous capturing threads started.")


def capture_for_duration(duration=2.0):
    """
    Collect frames from each camera for `duration` seconds.
    Only save them if they are actually new references.
    Returns a dict with up to the most recent 200 numpy arrays for each camera.
    """
    # Use deque(maxlen=200) to keep only the last 200 frames for each camera
    captured_sequence = {
        "camera0": deque(maxlen=200),
        "camera1": deque(maxlen=200)
    }
    last_seen = {"camera0": None, "camera1": None}

    end_time = time.perf_counter() + duration
    while time.perf_counter() < end_time:
        # Grab a snapshot of the frame references outside the lock
        print(latest_frames)
        with lock:
            frames_snapshot = {
                key: latest_frames[key] for key in latest_frames
            }

        # Now process outside the lock
        for key, frame_ref in frames_snapshot.items():
            if frame_ref is not None and frame_ref is not last_seen[key]:
                # We have a new frame reference -> copy the data
                captured_sequence[key].append(np.copy(frame_ref))
                last_seen[key] = frame_ref

    # Convert each deque to a list before returning/pickling
    return {
        k: list(v) for k, v in captured_sequence.items()
    }


def capture_and_save():
    """
    Capture for 2 seconds on both cameras (simultaneously), then
    pickle + write frames in a background thread. Each call spawns
    its own worker so multiple calls can overlap.
    """

    def _worker():
        # 1) Capture frames
        start_time_all = time.perf_counter()
        if _DEBUG:
            print(f"[DEBUG][{time.perf_counter():.3f}] Starting capture_for_duration")

        start_time = time.perf_counter()
        captured_frames = capture_for_duration(2.0)
        if _DEBUG:
            print(captured_frames)
            elapsed = time.perf_counter() - start_time
            print(f"[DEBUG][{time.perf_counter():.3f}] capture_for_duration took {elapsed:.3f} sec")

        # 2) Ensure directories exist
        os.makedirs("./tmp", exist_ok=True)
        os.makedirs("./cache1", exist_ok=True)

        # Generate a UUID for this capture and add file to data being transferred
        file_uuid = str(uuid.uuid4())
        captured_frames["uuid"] = file_uuid

        # Build the paths for the pickle file
        tmp_pkl_path = os.path.join("./tmp", file_uuid + "_preprocessing.pkl")
        final_pkl_path = os.path.join("./cache1", file_uuid + "_preprocessing.pkl")

        # 3) Dump to PKL in ./tmp
        if _DEBUG:
            print(f"[DEBUG][{time.perf_counter():.3f}] Writing PKL to temp => {tmp_pkl_path}")
        start_time = time.perf_counter()
        with open(tmp_pkl_path, "wb") as f:
            pickle.dump(captured_frames, f)
        if _DEBUG:
            elapsed = time.perf_counter() - start_time
            print(f"[DEBUG][{time.perf_counter():.3f}] Writing PKL took {elapsed:.3f} sec")

        # 4) Move PKL to ./cache1
        start_time = time.perf_counter()
        shutil.move(tmp_pkl_path, final_pkl_path)
        if _DEBUG:
            elapsed = time.perf_counter() - start_time
            print(f"[DEBUG][{time.perf_counter():.3f}] Moved PKL to => {final_pkl_path} (move took {elapsed:.3f} sec)")

        # Optional: Free memory right away
        del captured_frames

        # Log summary
        if _DEBUG:
            total_elapsed_all = time.perf_counter() - start_time_all
            print(f"[DEBUG][{time.perf_counter():.3f}] Finished capture => {final_pkl_path}, total {total_elapsed_all:.3f} sec")

    # Fire off the capture thread so multiple calls can happen concurrently
    threading.Thread(target=_worker, daemon=True).start()
    return


if __name__ == "__main__":
    start_continuous_capture()

    # REPLACE WITH REAL TRIGGER LOGIC, OR USE capture_and_save FROM EXTERNAL MODULE
    print("Press Enter to capture frames (or type 'q' to quit).")

    while True:
        key = input()
        if key.lower() == "q":
            print("Exiting.")
            break
        capture_and_save()
