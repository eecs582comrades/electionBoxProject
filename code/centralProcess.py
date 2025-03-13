from processPictures import processPictures as process_pictures
from takePictures import capture_and_save as capture_and_save_image
from takePictures import start_continuous_capture
from envelope_processor import envelopeProcessTrigger as process_envelope

import os
import threading
import time
import psutil
import logging
import queue
import keyboard  # pip install keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import socketserver

class EventHandler(socketserver.BaseRequestHandler):
    def handle(self):
        capture_and_save_image()

# Configure logging
logging.basicConfig(filename='thread_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Queue for thread failure notifications (for watchdog purposes)
error_queue = queue.Queue()

class FolderBasedFileHandler(FileSystemEventHandler):
    """
    Monitors file creation events and executes a specific function based on the folder
    where the file appears. The folder_function_map should be a dictionary mapping
    absolute folder paths to the function that processes files in that folder.
    """
    def __init__(self, folder_function_map):
        super().__init__()
        # Convert folder keys to absolute paths for consistency.
        self.folder_function_map = {os.path.abspath(folder): func 
                                    for folder, func in folder_function_map.items()}

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        file_folder = os.path.abspath(os.path.dirname(file_path))
        logging.info(f"New file detected: {file_path} in folder: {file_folder}")

        # Retrieve the function for the folder if it exists.
        func = self.folder_function_map.get(file_folder)
        if func:
            logging.info(f"Calling function '{func.__name__}' for file: {file_path}")
            try:
                # Both process_pictures and process_envelope expect a file path.
                func(file_path)
            except Exception as e:
                logging.error(f"Error executing '{func.__name__}' on file '{file_path}': {e}")
        else:
            logging.info(f"No function mapping found for folder: {file_folder}")

def start_thread(target, name, priority=None, cpu_affinity=None):
    """
    Starts a worker thread with optional CPU affinity and priority settings.
    Use this for functions that run continuously and do not require an external argument.
    """
    def wrapped_target():
        tid = threading.get_ident()
        time.sleep(0.1)  # Allow thread initialization.
        try:
            p = psutil.Process(tid)
            if priority is not None:
                p.nice(priority)
            if cpu_affinity is not None:
                p.cpu_affinity(cpu_affinity)
        except psutil.NoSuchProcess:
            logging.warning(f"Could not set affinity/priority for {name}")
        target()  # Call the target function.
        
    thread = threading.Thread(target=wrapped_target, name=name, daemon=True)
    thread.start()
    return thread

def start_folder_monitor(folder_function_map):
    """
    Starts a dedicated thread that monitors multiple folders.
    When a new file is added to any of the monitored folders, the corresponding function
    (which takes the file path as an argument) is called.
    """
    event_handler = FolderBasedFileHandler(folder_function_map)
    observer = Observer()

    # Schedule the observer for each folder in the mapping.
    for folder in folder_function_map.keys():
        observer.schedule(event_handler, folder, recursive=False)
        logging.info(f"Started monitoring folder: {folder}")
    observer.start()

    def monitor_loop():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    monitor_thread = threading.Thread(target=monitor_loop, name="FolderMonitorThread", daemon=True)
    monitor_thread.start()
    return monitor_thread

def watchdog():
    """
    Monitors for crashed threads and restarts them when necessary.
    (For example, if a continuous worker thread fails.)
    """
    thread_map = {
        # In this example, the camera capture function is now triggered via hotkey,
        # so we don't start it as a continuous thread.
    }
    while True:
        crashed_thread = error_queue.get()  # Blocks until an error is reported.
        logging.info(f"Restarting {crashed_thread}...")
        if crashed_thread in thread_map:
            thread_map[crashed_thread]()
        else:
            logging.error(f"No restart mapping defined for thread: {crashed_thread}")

def main():
    logging.info("Starting main thread manager...")

    server = socketserver.UDPServer(("localhost", 9999), EventHandler)

    # Map each folder to the function that should process new files.
    folder_function_map = {
        os.path.abspath("./cache1"): process_pictures,   # Files here will be processed by process_pictures(file_path)
        os.path.abspath("./cache2"): process_envelope,     # Files here will be processed by process_envelope(file_path)
    }
    # Start monitoring the folders.
    start_folder_monitor(folder_function_map)

    start_continuous_capture()
    # Optionally start a watchdog thread to restart any crashed continuous threads.
    threading.Thread(target=watchdog, name="WatchdogThread", daemon=True).start()

    # Keep the main thread alive so that the hotkey and folder monitoring remain active.
    server.serve_forever()

if __name__ == "__main__":
    main()
