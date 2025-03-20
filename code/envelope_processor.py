import os
import cv2
import numpy as np
import pytesseract
import re
import sys
import subprocess
from tabulate import tabulate
from interpreter import extract_all_imb
import requests
import time
import datetime
import gc

# Configuration
OUTPUT_DIR = "./out"
DEBUG_DIR = "./debug"
BARCODE_DIR = "./barcodes"
MAX_IMAGE_DIM = 1600  # Maximum dimension for processed images
DEBUG = False

# Create necessary directories
for folder in [OUTPUT_DIR, DEBUG_DIR, BARCODE_DIR]:
    os.makedirs(folder, exist_ok=True)

def cleanup_image(image):
    """Helper to properly cleanup OpenCV images"""
    if image is not None:
        image.flags.writeable = False
        del image
        gc.collect()

def save_debug_image(filename, image, force=False):
    """Helper to save images into the debug folder with proper cleanup."""
    try:
        if (DEBUG or force):
            filepath = os.path.join(DEBUG_DIR, filename)
            cv2.imwrite(filepath, image)
            return filepath
        return None
    finally:
        cleanup_image(image)

def save_output_image(filename, image):
    """Helper to save images into the output folder with proper cleanup."""
    try:
        filepath = os.path.join(OUTPUT_DIR, filename)
        cv2.imwrite(filepath, image)
        return filepath
    finally:
        cleanup_image(image)

def get_normalized_image(original):
    """Normalize image with proper memory management"""
    try:
        if original is None:
            return None
            
        # Calculate new dimensions
        height, width = original.shape[:2]
        resized_height = 480
        scale = resized_height / height
        resized_width = int(width * scale)
        
        # Process image
        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (9, 9), 0)
        cv2.imwrite("blur.jpg", gray)
        
        gray = cv2.resize(gray, (resized_width, resized_height))
        cv2.imwrite("resized.jpg", gray)
        
        try:
            # Add border
            thickness = 10
            gray = cv2.copyMakeBorder(gray, thickness, thickness, thickness, thickness, 
                                    cv2.BORDER_CONSTANT, value=[255, 255, 255])
            cv2.imwrite("cropped.jpg", gray)
        except Exception as e:
            print(f"Failed to crop border: {e}")
        
        # Invert image
        gray = cv2.bitwise_not(gray)
        cv2.imwrite("inverted.jpg", gray)
        
        return gray
        
    except Exception as e:
        print(f"Error in get_normalized_image: {e}")
        return None
    finally:
        gc.collect()

def get_skew_angle(gray):
    """Calculate skew angle with proper memory management"""
    try:
        if gray is None:
            return 0
            
        # Create threshold
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        cv2.imwrite("thresh.jpg", thresh)
        
        # Dilate
        dilate = cv2.dilate(thresh, kernel)
        contours, _ = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process angles
        angles = []
        for contour in contours:
            rect = cv2.minAreaRect(contour)
            angle = rect[-1]
            if angle != 90.0 and angle != -0.0:
                angles.append(angle)
        
        # Calculate result
        if not angles:
            return 0
            
        angles.sort()
        mid_angle = angles[len(angles) // 2]
        
        cv2.imwrite("dilate.jpg", dilate)
        return mid_angle
        
    except Exception as e:
        print(f"Error in get_skew_angle: {e}")
        return 0
    finally:
        # Cleanup
        if 'thresh' in locals(): del thresh
        if 'dilate' in locals(): del dilate
        if 'contours' in locals(): del contours
        gc.collect()

def deskew(original, img):
    """Deskew image with proper memory management"""
    try:
        if original is None or img is None:
            return None
            
        angle = get_skew_angle(img)
        if angle > 45:  # anti-clockwise
            angle = -(90 - angle)
            
        height, width = original.shape[:2]
        m = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
        
        deskewed = cv2.warpAffine(original, m, (width, height), borderValue=(255,255,255))
        return deskewed
        
    except Exception as e:
        print(f"Error in deskew: {e}")
        return None
    finally:
        gc.collect()

def load_and_preprocess(image_path):
    """Load and preprocess image with proper memory management"""
    try:
        # Load image
        original = cv2.imread(image_path)
        if original is None:
            print(f"Error: Unable to load image at {image_path}")
            return None, None, None
            
        # Normalize and deskew
        img = get_normalized_image(original)
        if img is None:
            return None, None, None
            
        deskewed = deskew(original=original, img=img)
        if deskewed is None:
            return None, None, None
            
        # Resize if needed
        height, width = deskewed.shape[:2]
        if max(height, width) > MAX_IMAGE_DIM:
            scale = MAX_IMAGE_DIM / float(max(height, width))
            deskewed = cv2.resize(deskewed, (int(width * scale), int(height * scale)))
        
        # Process to grayscale
        image_gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
        equalized = cv2.equalizeHist(blurred)
        
        # Create thresholds
        thresh_adaptive = cv2.adaptiveThreshold(
            equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Save debug images
        save_debug_image("debug_gray.jpg", image_gray)
        save_debug_image("debug_blurred.jpg", blurred)
        save_debug_image("debug_equalized.jpg", equalized)
        save_debug_image("debug_thresh_adaptive.jpg", thresh_adaptive)
        
        return deskewed, equalized, thresh_adaptive
        
    except Exception as e:
        print(f"Error in load_and_preprocess: {e}")
        return None, None, None
    finally:
        # Cleanup intermediate images
        if 'img' in locals(): cleanup_image(img)
        if 'image_gray' in locals(): cleanup_image(image_gray)
        if 'blurred' in locals(): cleanup_image(blurred)
        gc.collect()

def detect_barcodes(image):
    """Detect barcodes with proper memory management"""
    try:
        from pyzbar import pyzbar
        if image is None:
            return []
            
        # Create a copy to avoid modifying original
        working_image = image.copy()
        barcodes = pyzbar.decode(working_image)
        
        results = []
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(working_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            results.append({
                "data": barcode.data.decode("utf-8"),
                "type": barcode.type,
                "rect": (x, y, w, h)
            })
            
        save_output_image("debug_barcodes.jpg", working_image)
        return results
        
    except Exception as e:
        print(f"Error in detect_barcodes: {e}")
        return []
    finally:
        if 'working_image' in locals(): cleanup_image(working_image)
        gc.collect()

def perform_ocr(image):
    """Perform OCR with proper memory management"""
    try:
        if image is None:
            return ""
            
        custom_config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(image, config=custom_config, lang='eng')
        
    except Exception as e:
        print(f"Error in perform_ocr: {e}")
        return ""
    finally:
        gc.collect()

def extract_pii(text):
    """Extract PII with proper memory management"""
    try:
        results = {}

        # 1) ZIP Codes
        zip_codes = re.findall(r'\b\d{5}(?:-\d{4})?\b', text)
        if zip_codes:
            results['ZIP Codes'] = zip_codes

        # 2) State Abbreviations (US)
        state_abbrs = re.findall(
            r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b',
            text,
            flags=re.IGNORECASE
        )
        if state_abbrs:
            results['State Abbreviations'] = state_abbrs

        # 3) Addresses
        address_pattern = r"\b\d{1,5}\s+(?:[NnSsEeWw]\.?\s+)?[A-Za-z0-9'\-]+(?:\s+[A-Za-z0-9'\-]+)*\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Way|Terrace|Ter\.?|Court|Ct\.?|Circle|Cir\.?)(?:\s+(?:Apt|Suite|Ste|#)\.?\s*\d+)?\b"
        matches = re.finditer(address_pattern, text, flags=re.IGNORECASE)
        addresses_found = [m.group(0) for m in matches]
        if addresses_found:
            results['Addresses'] = addresses_found

        return results
        
    except Exception as e:
        print(f"Error in extract_pii: {e}")
        return {}
    finally:
        gc.collect()

def run_barcode_extraction(image_path):
    """Run barcode extraction with proper error handling"""
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image path does not exist: {image_path}")
            return
            
        result = subprocess.run(
            ["python3", "barcode_extraction.py", image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print("Error during barcode extraction:")
            print(result.stderr)
            return
            
        print(result.stdout)
        
    except Exception as e:
        print(f"Error in run_barcode_extraction: {e}")
    finally:
        gc.collect()

def process_barcode_images():
    """Process barcode images with proper memory management"""
    results = []
    try:
        if not os.path.exists(BARCODE_DIR):
            print("No barcode directory found")
            return results
            
        barcode_files = sorted([
            f for f in os.listdir(BARCODE_DIR) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        
        if not barcode_files:
            print("No barcode images found")
            return results
            
        for file in barcode_files:
            try:
                file_path = os.path.join(BARCODE_DIR, file)
                barcode_img = cv2.imread(file_path)
                
                if barcode_img is None:
                    print(f"Warning: Unable to load barcode image {file}")
                    continue
                    
                imb_results = extract_all_imb(barcode_img)
                patterns = [
                    group.get("pattern", "") 
                    for group in imb_results
                ] if imb_results else []
                
                results.append({
                    "Barcode File": file,
                    "IMB Patterns": ", ".join(patterns) if patterns else "None"
                })
                
            except Exception as e:
                print(f"Error processing barcode file {file}: {e}")
            finally:
                if 'barcode_img' in locals(): cleanup_image(barcode_img)
                gc.collect()
                
        return results
        
    except Exception as e:
        print(f"Error in process_barcode_images: {e}")
        return results
    finally:
        gc.collect()

def envelopeProcessTrigger(image_path):
    """Main envelope processing function with proper memory management"""
    try:
        # Load and preprocess image
        deskew_original, equalized, thresh_adaptive = load_and_preprocess(image_path)
        if deskew_original is None:
            print("Failed to process image")
            return

        # Extract barcodes
        export_skew_path = save_debug_image("deskew_export.jpg", deskew_original, True)
        if export_skew_path:
            run_barcode_extraction(export_skew_path)
            barcode_report = process_barcode_images()
        else:
            print("Failed to save deskewed image")
            return

        # Perform OCR
        ocr_text = perform_ocr(deskew_original.copy())
        pii_results = extract_pii(ocr_text)

        # Generate report
        barcode_headers = ["Barcode File", "IMB Patterns"]
        barcode_table = [
            [entry["Barcode File"], entry["IMB Patterns"]] 
            for entry in barcode_report
        ]
        
        ocr_headers = ["PII/Address Data"]
        pii_summary = "; ".join([
            f"{k}: {', '.join(v)}" 
            for k, v in pii_results.items()
        ]) if pii_results else "None"
        ocr_table = [[pii_summary]]

        # Print report
        print("\n--- Report ---")
        print("\nBarcode / IMB Analysis:")
        print(tabulate(barcode_table, headers=barcode_headers, tablefmt="github"))
        print("\nEnvelope OCR and PII Extraction:")
        print(tabulate(ocr_table, headers=ocr_headers, tablefmt="github"))

        # Send data to server
        payload = {
            'IMB': barcode_report,
            'OCR': pii_results,
            'LOCATION': "Test Device",
            'TIME': time.strftime("%H:%M:%S", time.localtime()),
            'DATE': datetime.date.today().isoformat()
        }
        
        if barcode_report:
            try:
                response = requests.post(
                    'http://192.168.50.6:9100/envelopeData',
                    json=payload,
                    timeout=10
                )
                print("Data posted successfully!")
                print(response)
            except requests.exceptions.Timeout:
                print("Server request timed out")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data to server: {e}")

    except Exception as e:
        print(f"Error in envelopeProcessTrigger: {e}")
    finally:
        # Final cleanup
        if 'deskew_original' in locals(): cleanup_image(deskew_original)
        if 'equalized' in locals(): cleanup_image(equalized)
        if 'thresh_adaptive' in locals(): cleanup_image(thresh_adaptive)
        gc.collect()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python envelope_processor.py <path_to_image>")
        sys.exit(1)
    envelopeProcessTrigger(sys.argv[1])
