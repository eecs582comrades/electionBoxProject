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
# This should be in a debug libray but I'm lazy
OUTPUT_DIR = "./out"
DEBUG_DIR = "./debug"
BARCODE_DIR = "./barcodes"
for folder in [OUTPUT_DIR, DEBUG_DIR, BARCODE_DIR]:
    os.makedirs(folder, exist_ok=True)

DEBUG = False

def save_debug_image(filename, image, force=False):
    """Helper to save images into the debug folder."""
    global DEBUG
    if (DEBUG or force):
        cv2.imwrite(os.path.join(DEBUG_DIR, filename), image)

    return os.path.join(DEBUG_DIR, filename)

def save_output_image(filename, image):
    """Helper to save images into the output folder."""
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), image)

# End of what should be in the debug library :)

def get_normalized_image(original):
    resized_height = 480
    percent = resized_height / len(original)
    resized_width = int(percent * len(original[0]))
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
    cv2.imwrite("blur.jpg",gray)
    gray = cv2.resize(gray,(resized_width,resized_height))
    cv2.imwrite("resized.jpg",gray)
    try:
        start_point = (0, 0) 
        end_point = (gray.shape[0], gray.shape[1]) 
        color = (255, 255, 255) 
        thickness = 10
        gray = cv2.rectangle(gray, start_point, end_point, color, thickness) 
        cv2.imwrite("cropped.jpg",gray)
    except:
        print("Failed to crop border")
    gray = cv2.bitwise_not(gray)
    cv2.imwrite("inverted.jpg",gray)
    
    return gray
    
def get_skew_angle(gray):
    thresh = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    cv2.imwrite("thresh.jpg",thresh)
    dilate = cv2.dilate(thresh, kernel)
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    angles = []
    for contour in contours:
        minAreaRect = cv2.minAreaRect(contour)
        angle = minAreaRect[-1]
        if angle != 90.0 and angle != -0.0:
            angles.append(angle)
        
    angles.sort()
    mid_angle = angles[int(len(angles)/2)]
    print(angles)
    print(mid_angle)
    #cv2.namedWindow('dilate',cv2.WINDOW_NORMAL)
    #cv2.imshow("dilate", dilate)
    cv2.imwrite("dilate.jpg",dilate)
    return mid_angle

def deskew(original, img):
    angle = get_skew_angle(img)
    #angle = np.rad2deg(angle)
    print(angle)
    if angle > 45: #anti-clockwise
        angle = -(90 - angle)
    height = original.shape[0]
    width = original.shape[1]
    m = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
    
    #deskewed = cv2.warpAffine(original, m, (width, height), borderMode=cv2.BORDER_REPLICATE)
    deskewed = cv2.warpAffine(original, m, (width, height), borderValue=(255,255,255))
    #cv2.namedWindow('deskewed',cv2.WINDOW_NORMAL)
    #cv2.imshow("deskewed", deskewed)
    #cv2.namedWindow('original',cv2.WINDOW_NORMAL)
    #cv2.imshow("original", original)
    #cv2.waitKey(0)
    return deskewed

def load_and_preprocess(image_path):
    """
    Loads the image and applies several pre‑processing steps:
      - Converts to grayscale.
      - Applies Gaussian blur to reduce noise.
      - Uses histogram equalization to boost contrast.
      - Applies both Otsu thresholding (simple) and adaptive thresholding.
    Saves intermediate images for debugging.
    
    Returns:
      image_color: Original/resized color image (for barcode detection and OCR).
      equalized: Blurred and equalized grayscale image.
      thresh_adaptive: Adaptive thresholded image.
    """
    original = cv2.imread(image_path)
    img = get_normalized_image(original)
    deskewed = deskew(original=original, img=img)
    if deskewed is None:
        print(f"Error: Unable to load image at {image_path}")
        sys.exit(1)

    height, width = deskewed.shape[:2]
    max_dim = 1600
    if max(height, width) > max_dim:
        scale = max_dim / float(max(height, width))
        deskewed = cv2.resize(deskewed, (int(width * scale), int(height * scale)))
    
    image_gray = cv2.cvtColor(deskewed, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(image_gray, (5, 5), 0)
    equalized = cv2.equalizeHist(blurred)
    
    _, thresh_simple = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh_adaptive = cv2.adaptiveThreshold(equalized, 255,
                                            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)
    
    save_debug_image("debug_gray.jpg", image_gray)
    save_debug_image("debug_blurred.jpg", blurred)
    save_debug_image("debug_equalized.jpg", equalized)
    save_debug_image("debug_thresh_simple.jpg", thresh_simple)
    save_debug_image("debug_thresh_adaptive.jpg", thresh_adaptive)
    
    return deskewed, equalized, thresh_adaptive

def detect_barcodes(image):
    """
    Detects standard barcodes in the provided image using pyzbar.
    (Note: pyzbar does not support IMB decoding.)
    Returns a list of dictionaries with barcode data.
    """
    from pyzbar import pyzbar
    barcodes = pyzbar.decode(image)
    results = []
    for barcode in barcodes:
        (x, y, w, h) = barcode.rect
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        results.append({
            "data": barcode_data,
            "type": barcode_type,
            "rect": (x, y, w, h)
        })
    save_output_image("debug_barcodes.jpg", image)
    return results

def perform_ocr(image):
    """
    Uses Tesseract OCR to extract text from the image.
    Uses a custom configuration to improve layout detection.
    """
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config, lang='eng')
    return text

def extract_pii(text):
    """
    Uses regular expressions to extract likely PII such as ZIP codes,
    state abbreviations, and addresses from the OCR output.
    """
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
    # Explanation of the single-line pattern:
    # \b\d{1,5}\s+          => house number up to 5 digits, then whitespace
    # (?:[NnSsEeWw]\.?\s+)? => optional compass direction (e.g., "N." or "W")
    # [A-Za-z0-9'-]+(?:\s+[A-Za-z0-9'-]+)* => street name words (letters, digits, apostrophes, hyphens)
    # \s+ => whitespace between the street name and suffix
    # (?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Way|Terrace|Ter\.?|Court|Ct\.?|Circle|Cir\.?) 
    #     => common street suffixes
    # (?:\s+(?:Apt|Suite|Ste|#)\.?\s*\d+)? => optional apartment/suite (e.g., "Suite 101" or "#12")
    # \b => word boundary
    address_pattern = r"\b\d{1,5}\s+(?:[NnSsEeWw]\.?\s+)?[A-Za-z0-9'\-]+(?:\s+[A-Za-z0-9'\-]+)*\s+(?:Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Drive|Dr\.?|Way|Terrace|Ter\.?|Court|Ct\.?|Circle|Cir\.?)(?:\s+(?:Apt|Suite|Ste|#)\.?\s*\d+)?\b"

    matches = re.finditer(address_pattern, text, flags=re.IGNORECASE)
    addresses_found = [m.group(0) for m in matches]
    if addresses_found:
        results['Addresses'] = addresses_found

    return results

def run_barcode_extraction(image_path):
    """
    Calls the barcode_extraction.py script as a subprocess.
    """
    print("Running barcode extraction...")
    result = subprocess.run(["python3", "barcode_extraction.py", image_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True)
    if result.returncode != 0:
        print("Error during barcode extraction:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(result.stdout)

def process_barcode_images():
    """
    For each image in the BARCODE_DIR, run interpreter's extraction.
    Returns a list of dictionaries with filename and interpreter results.
    """
    results = []
    if not os.path.exists(BARCODE_DIR):
        print("No barcode directory found. Skipping interpreter processing.")
        return results

    barcode_files = sorted([f for f in os.listdir(BARCODE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
    if not barcode_files:
        print("No barcode images found in the barcode directory.")
        return results

    for file in barcode_files:
        file_path = os.path.join(BARCODE_DIR, file)
        barcode_img = cv2.imread(file_path)
        if barcode_img is None:
            print(f"Warning: Unable to load barcode image {file}")
            continue
        imb_results = extract_all_imb(barcode_img)
        # For reporting, we can simply join any detected IMB patterns
        patterns = [group.get("pattern", "") for group in imb_results] if imb_results else []
        results.append({
            "Barcode File": file,
            "IMB Patterns": ", ".join(patterns) if patterns else "None"
        })
    return results

def envelopeProcessTrigger(image_path):

    ### BARCODE EXTRACTION ###
    deskew_original, equalized, thresh_adaptive = load_and_preprocess(image_path)

    # Step 1: Run barcode extraction on the envelope image
    export_skew_path = save_debug_image("deskew_export.jpg", deskew_original, True)
    print(export_skew_path)
    run_barcode_extraction(export_skew_path)
    # Step 2: Process each barcode image with interpreter extraction
    barcode_report = process_barcode_images()

    ### OCR AND EXTEMPORARY DATA EXTRACTION ###
    # Step 3: Load envelope image for OCR and PII extraction
    ocr_text = perform_ocr(deskew_original.copy())
    pii_results = extract_pii(ocr_text)
    
    ### REPORT AND EXPORT ###
    # Build the report as two sections:
    # Section 1: Barcode / IMB Analysis
    barcode_headers = ["Barcode File", "IMB Patterns"]
    barcode_table = [ [entry["Barcode File"], entry["IMB Patterns"]] for entry in barcode_report ]
    # Section 2: OCR / PII Extraction
    ocr_headers = ["PII/Address Data"]
    # For display purposes, truncate OCR text if needed
    pii_summary = "; ".join([f"{k}: {', '.join(v)}" for k, v in pii_results.items()]) if pii_results else "None"
    ocr_table = [[pii_summary]]
    

    print("\n--- Report ---")
    print("\nBarcode / IMB Analysis:")
    print(tabulate(barcode_table, headers=barcode_headers, tablefmt="github"))
    
    print("\nEnvelope OCR and PII Extraction:")
    print(tabulate(ocr_table, headers=ocr_headers, tablefmt="github"))

    payload = {
        'IMB': barcode_report, 
        'OCR': pii_results, 
        'LOCATION': "Test Device", 
        'TIME': time.strftime("%H:%M:%S", time.localtime()), 
        'DATE': datetime.date.today().isoformat()
    }
    if barcode_report:
        try:
            print("Attempting to post!")
            response = requests.post('http://192.168.50.6:9100/envelopeData', json = payload, timeout = 10)
            print("posted!")
            print(response)
        except requests.exceptions.Timeout:
            print("TIMEOUT")
            return
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
if __name__ == '__main__':  
    if len(sys.argv) != 2:
        print("Usage: python envelope_processor.py <path_to_image>")
        sys.exit(1)
    image_path = sys.argv[1]
    envelopeProcessTrigger(image_path)
