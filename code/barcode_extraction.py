import os
import cv2
import numpy as np
import argparse
import gc

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Barcode detection script")
parser.add_argument("image_path", type=str, help="Path to the input image")
args = parser.parse_args()

DEBUG = False

# Configuration
MAX_BAR_SPACING = 0.3  # Maximum allowed spacing between bars (as fraction of ROI width)
MIN_BAR_COUNT = 35
MAX_BAR_COUNT = 66
MIN_BAR_HEIGHT_RATIO = 3.0  # Minimum height/width ratio for a bar

# Validate image path
if not os.path.exists(args.image_path):
    print(f"Error: The file '{args.image_path}' does not exist.")
    exit(1)

# Define output directories
output_dir = "./barcode_extraction_debug"
barcode_dir = "./barcodes"

# Ensure the preprocessing folder is clean before each run
for directory in [output_dir, barcode_dir]:
    if os.path.exists(directory):
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))
    else:
        os.makedirs(directory)

def cleanup_image(image):
    """Helper to properly cleanup OpenCV images"""
    if image is not None:
        image.flags.writeable = False
        del image
        gc.collect()

def scale(roi):
    """Scale up the extracted barcode to be 200px tall while preserving the aspect ratio"""
    try:
        current_height = roi.shape[0]
        scale_factor = 200 / current_height
        new_width = int(roi.shape[1] * scale_factor)
        resized_roi = cv2.resize(roi, (new_width, 200), interpolation=cv2.INTER_LINEAR)
        return resized_roi
    except Exception as e:
        print(f"Error in scale: {e}")
        return None
    finally:
        gc.collect()

def detect_vertical_lines(roi):
    """
    Detects thin, barcode-like vertical lines in a given ROI.
    Checks for proper spacing between bars to avoid false positives from text.
    
    Parameters:
        roi (np.array): Input region-of-interest image in BGR format.
        
    Returns:
        int: Count of detected vertical bars, or 0 if spacing is invalid.
    """
    try:
        if roi is None:
            return 0
            
        # Convert to grayscale and scale the ROI
        roi = scale(roi)
        if roi is None:
            return 0
            
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Apply a slight blur to reduce noise
        blurred = cv2.medianBlur(roi_gray, 3)
        
        # Apply Otsu's thresholding with binary inversion
        _, binary_roi = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Save the binary debug image
        if DEBUG:
            debug_bin_path = os.path.join(output_dir, f"bin_debug_{barcode_counter_final + 1}.png")
            cv2.imwrite(debug_bin_path, binary_roi)
        
        # Enhance the thin vertical lines using morphological closing
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
        morph = cv2.morphologyEx(binary_roi, cv2.MORPH_CLOSE, vertical_kernel)
        
        # Save the morphological debug image
        if DEBUG:
            debug_morph_path = os.path.join(output_dir, f"morph_debug_{barcode_counter_final + 1}.png")
            cv2.imwrite(debug_morph_path, morph)
        
        # Use connected components to identify candidate regions
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(morph, connectivity=8)
        
        # Store valid bars with their x-coordinates
        valid_bars = []
        debug_roi = roi.copy()
        
        # Loop over each detected component (skip background at index 0)
        for i in range(1, num_labels):
            x, y, w, h, area = stats[i]
            # Define criteria for a thin vertical line
            if h / w > MIN_BAR_HEIGHT_RATIO:
                valid_bars.append((x, y, w, h))
                cv2.rectangle(debug_roi, (x, y), (x + w, y + h), (0, 255, 0), 1)
            else:
                cv2.rectangle(debug_roi, (x, y), (x + w, y + h), (0, 0, 255), 1)
        
        # Check spacing between bars
        if len(valid_bars) > 1:
            # Sort bars by x-coordinate
            valid_bars.sort(key=lambda b: b[0])
            
            # Calculate average spacing between bars
            total_spacing = 0
            for i in range(len(valid_bars) - 1):
                current_bar_end = valid_bars[i][0] + valid_bars[i][2]
                next_bar_start = valid_bars[i + 1][0]
                spacing = next_bar_start - current_bar_end
                total_spacing += spacing
            
            avg_spacing = total_spacing / (len(valid_bars) - 1)
            roi_width = roi.shape[1]
            spacing_ratio = avg_spacing / roi_width
            
            # If spacing is too large, reject the candidate
            if spacing_ratio > MAX_BAR_SPACING:
                if DEBUG:
                    print(f"Rejected candidate: spacing ratio {spacing_ratio:.3f} exceeds maximum {MAX_BAR_SPACING}")
                return 0
        
        # Save the final debug image with detected bars outlined
        if DEBUG:
            debug_roi_path = os.path.join(output_dir, f"debug_bbox_{barcode_counter_final + 1}.png")
            cv2.imwrite(debug_roi_path, debug_roi)
        
        return len(valid_bars)
        
    except Exception as e:
        print(f"Error in detect_vertical_lines: {e}")
        return 0
    finally:
        # Cleanup
        if 'roi_gray' in locals(): cleanup_image(roi_gray)
        if 'blurred' in locals(): cleanup_image(blurred)
        if 'binary_roi' in locals(): cleanup_image(binary_roi)
        if 'morph' in locals(): cleanup_image(morph)
        if 'debug_roi' in locals(): cleanup_image(debug_roi)
        gc.collect()

def extract_roi_with_empty_padding(x, y, w, h, image, padding=PADDING):
    """
    Extracts a region of interest (ROI) from the image with a fixed amount of padding.
    If the padded area falls outside the image boundaries, those areas are filled with zeros.
    """
    try:
        img_h, img_w = image.shape[:2]
        
        # Coordinates for the padded ROI (these may be negative)
        x1 = x - padding
        y1 = y - padding
        x2 = x + w + padding
        y2 = y + h + padding
        
        out_w = w + 2 * padding
        out_h = h + 2 * padding
        
        # Create an empty (zero-filled) canvas for the ROI
        if image.ndim == 3:
            roi = np.zeros((out_h, out_w, image.shape[2]), dtype=image.dtype)
        else:
            roi = np.zeros((out_h, out_w), dtype=image.dtype)
        
        # Calculate the intersection between the padded ROI and the image boundaries
        src_x1 = max(x1, 0)
        src_y1 = max(y1, 0)
        src_x2 = min(x2, img_w)
        src_y2 = min(y2, img_h)
        
        # Determine destination coordinates in the ROI where the image data should be placed
        dst_x1 = src_x1 - x1
        dst_y1 = src_y1 - y1
        dst_x2 = dst_x1 + (src_x2 - src_x1)
        dst_y2 = dst_y1 + (src_y2 - src_y1)
        
        roi[dst_y1:dst_y2, dst_x1:dst_x2] = image[src_y1:src_y2, src_x1:src_x2]
        return roi
        
    except Exception as e:
        print(f"Error in extract_roi_with_empty_padding: {e}")
        return None
    finally:
        gc.collect()

# Load the image
image = cv2.imread(args.image_path)
if image is None:
    print(f"Error: Unable to load image at {args.image_path}")
    exit(1)

try:
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Step 1: Reduce noise and enhance barcode structure
    blurred_refined = cv2.GaussianBlur(gray, (7, 7), 0)
    cv2.imwrite(os.path.join(output_dir, "0_blurred.png"), blurred_refined)
    
    # Apply adaptive thresholding for better barcode contrast
    thresh_refined = cv2.adaptiveThreshold(
        blurred_refined, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 17, 5
    )
    cv2.imwrite(os.path.join(output_dir, "1_adaptive_threshold.png"), thresh_refined)
    
    # Step 2: Use two-stage morphological operations
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 6))
    morph_closed = cv2.morphologyEx(thresh_refined, cv2.MORPH_CLOSE, kernel_close)
    cv2.imwrite(os.path.join(output_dir, "2_morphological_closing.png"), morph_closed)
    
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph_refined = cv2.morphologyEx(morph_closed, cv2.MORPH_OPEN, kernel_open)
    cv2.imwrite(os.path.join(output_dir, "3_morphological_opening.png"), morph_refined)
    
    # Step 3: Find contours (Initial barcode candidates)
    contours_final, _ = cv2.findContours(morph_refined, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on the image for visualization
    contour_visualization_final = image.copy()
    cv2.drawContours(contour_visualization_final, contours_final, -1, (0, 255, 0), 2)
    cv2.imwrite(os.path.join(output_dir, "4_contour_detection.png"), contour_visualization_final)
    
    # Step 4: Filter candidates using size, aspect ratio, and additional barcode detection methods
    barcode_counter_final = 0
    filtered_visualization_final = image.copy()
    real_barcodes = []  # Store final valid barcodes
    
    # Define padding amount (in pixels)
    PADDING = 10  # Adjust as needed
    
    for contour in contours_final:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        
        # Initial barcode-like shape filter
        if w > 60 and h > 15 and 1.5 < aspect_ratio < 20.0:
            # Extract padded ROI using the new function that leaves the padding empty (zeros)
            roi = extract_roi_with_empty_padding(x, y, w, h, image, padding=PADDING)
            if roi is None:
                continue
                
            # Compute padded bounding box coordinates (without clipping)
            x_pad = x - PADDING
            y_pad = y - PADDING
            w_pad = w + 2 * PADDING
            h_pad = h + 2 * PADDING
            
            # Ensure ROI has 3 channels before conversion
            if len(roi.shape) == 2:
                roi_gray = roi
            else:
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Detect vertical bars in ROI
            vertical_bar_count = detect_vertical_lines(roi)
            
            # Save debug image of the current candidate ROI
            if DEBUG:
                candidate_debug_path = os.path.join(output_dir, f"candidate_debug_{barcode_counter_final + 1}.png")
                cv2.imwrite(candidate_debug_path, roi)
            
            barcode_counter_final += 1
            
            # Accept the candidate if it has enough vertical bars
            if MIN_BAR_COUNT <= vertical_bar_count <= MAX_BAR_COUNT:
                real_barcodes.append((x_pad, y_pad, w_pad, h_pad))
                cv2.rectangle(filtered_visualization_final, (x_pad, y_pad), 
                            (x_pad + w_pad, y_pad + h_pad), (0, 0, 255), 2)
                
                # Scale up the extracted barcode to be 200px tall while preserving aspect ratio
                resized_barcode = scale(roi)
                if resized_barcode is not None:
                    # Save extracted barcode as an individual image
                    barcode_path = os.path.join(barcode_dir, f"barcode_{barcode_counter_final}.png")
                    cv2.imwrite(barcode_path, resized_barcode)
            
            # Cleanup ROI
            cleanup_image(roi)
            if 'roi_gray' in locals(): cleanup_image(roi_gray)
            if 'resized_barcode' in locals(): cleanup_image(resized_barcode)
    
    # Save final validated barcode detections
    cv2.imwrite(os.path.join(output_dir, "5_candidates.png"), filtered_visualization_final)
    
except Exception as e:
    print(f"Error in main processing: {e}")
finally:
    # Cleanup
    if 'image' in locals(): cleanup_image(image)
    if 'gray' in locals(): cleanup_image(gray)
    if 'blurred_refined' in locals(): cleanup_image(blurred_refined)
    if 'thresh_refined' in locals(): cleanup_image(thresh_refined)
    if 'morph_closed' in locals(): cleanup_image(morph_closed)
    if 'morph_refined' in locals(): cleanup_image(morph_refined)
    if 'contour_visualization_final' in locals(): cleanup_image(contour_visualization_final)
    if 'filtered_visualization_final' in locals(): cleanup_image(filtered_visualization_final)
    gc.collect()

