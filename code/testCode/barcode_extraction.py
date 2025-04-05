import os
import cv2
import numpy as np
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Barcode detection script")
parser.add_argument("image_path", type=str, help="Path to the input image")
args = parser.parse_args()

DEBUG = False

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

# Load the image
image = cv2.imread(args.image_path)

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

# First: Closing to connect barcode gaps
kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 6))
morph_closed = cv2.morphologyEx(thresh_refined, cv2.MORPH_CLOSE, kernel_close)
cv2.imwrite(os.path.join(output_dir, "2_morphological_closing.png"), morph_closed)

# Second: Opening to remove small noise
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

def scale(roi):
    # Scale up the extracted barcode to be 500px tall while preserving the aspect ratio
    current_height = roi.shape[0]
    scale_factor = 200 / current_height
    new_width = int(roi.shape[1] * scale_factor)
    resized_roi = cv2.resize(roi, (new_width, 200), interpolation=cv2.INTER_LINEAR)
    return resized_roi

def detect_vertical_lines(roi):
    """
    Detects thin, barcode-like vertical lines in a given ROI.
    
    Parameters:
        roi (np.array): Input region-of-interest image in BGR format.
        
    Returns:
        int: Count of detected vertical bars.
    """
    # Convert to grayscale and scale the ROI
    roi = scale(roi)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply a slight blur to reduce noise
    blurred = cv2.medianBlur(roi_gray, 3)
    
    # Apply Otsu's thresholding with binary inversion
    _, binary_roi = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Save the binary debug image
    debug_bin_path = os.path.join(output_dir, f"bin_debug_{barcode_counter_final + 1}.png")
    if DEBUG:
        cv2.imwrite(debug_bin_path, binary_roi)
    
    # Enhance the thin vertical lines using morphological closing
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    morph = cv2.morphologyEx(binary_roi, cv2.MORPH_CLOSE, vertical_kernel)
    
    # Save the morphological debug image
    debug_morph_path = os.path.join(output_dir, f"morph_debug_{barcode_counter_final + 1}.png")
    if DEBUG:
        cv2.imwrite(debug_morph_path, morph)
    
    # Use connected components to identify candidate regions
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(morph, connectivity=8)
    
    bar_count = 0
    debug_roi = roi.copy()
    
    # Loop over each detected component (skip background at index 0)
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        # Define criteria for a thin vertical line
        if h / w > 3:
            bar_count += 1
            cv2.rectangle(debug_roi, (x, y), (x + w, y + h), (0, 255, 0), 1)
        else:
            cv2.rectangle(debug_roi, (x, y), (x + w, y + h), (0, 0, 255), 1)
    
    # Save the final debug image with detected bars outlined
    debug_roi_path = os.path.join(output_dir, f"debug_bbox_{barcode_counter_final + 1}.png")
    if DEBUG:
        cv2.imwrite(debug_roi_path, debug_roi)

    """
    DEVNOTE: We should update this function so that, if the vertical lines are spaced to far apart (net), we reject the candidate.
    Specifically, barcodes will be close together like ||||||. Sometimes, text will include i's and l's, and those are often detected as
    vertical lines. So if we detect a lot of i's and l's, that can lead to a false positive on barcode detection. To prevent this, we need
    to make sure that the vertical lines that ARE detected aren't too spread out. This is doable, I just got too lazy to code it :)
    """
    
    return bar_count

def extract_roi_with_empty_padding(x, y, w, h, image, padding=PADDING):
    """
    Extracts a region of interest (ROI) from the image with a fixed amount of padding.
    If the padded area falls outside the image boundaries, those areas are filled with zeros.
    """
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

for contour in contours_final:
    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = w / float(h)

    # Initial barcode-like shape filter
    if w > 60 and h > 15 and 1.5 < aspect_ratio < 20.0:
        # Extract padded ROI using the new function that leaves the padding empty (zeros)
        roi = extract_roi_with_empty_padding(x, y, w, h, image, padding=PADDING)
        
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
        candidate_debug_path = os.path.join(output_dir, f"candidate_debug_{barcode_counter_final + 1}.png")
        if DEBUG:
            cv2.imwrite(candidate_debug_path, roi)
        
        barcode_counter_final += 1

        # Accept the candidate if it has enough vertical bars
        if vertical_bar_count >= 35 and vertical_bar_count <= 66:
            real_barcodes.append((x_pad, y_pad, w_pad, h_pad))
            cv2.rectangle(filtered_visualization_final, (x_pad, y_pad), (x_pad + w_pad, y_pad + h_pad), (0, 0, 255), 2)

            # Scale up the extracted barcode to be 500px tall while preserving aspect ratio
            resized_barcode = scale(roi)

            # Save extracted barcode as an individual image
            barcode_path = os.path.join(barcode_dir, f"barcode_{barcode_counter_final}.png")
            cv2.imwrite(barcode_path, resized_barcode)

# Save final validated barcode detections
cv2.imwrite(os.path.join(output_dir, "5_candidates.png"), filtered_visualization_final)

