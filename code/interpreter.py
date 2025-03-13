import os
import cv2
import numpy as np
import pytesseract
import re
import sys

OUTPUT_DIR = "./out"
DEBUG_DIR = "./debug"

DEBUG = True

itter = 0

def save_debug_image(filename, image):
    """Helper to save images into the debug folder."""
    global itter
    global DEBUG
    if (DEBUG):
        cv2.imwrite(os.path.join(DEBUG_DIR, str(itter) + "_" + filename), image)

def save_output_image(filename, image):
    """Helper to save images into the output folder."""
    cv2.imwrite(os.path.join(OUTPUT_DIR, filename), image)

def extract_all_imb(image):
    """
    Attempts to detect multiple Intelligent Mail Barcodes (IMBs) in the entire image
    using open source methods.
    
    Steps:
      1. Convert the entire image to grayscale and apply a binary inverse threshold.
      2. Apply a modest morphological closing with a vertical kernel (1x3) to reconnect broken vertical segments.
      3. Use connectedComponentsWithStats to identify candidate bar regions.
      4. Filter out small or irrelevant components (including those with low vertical-to-horizontal ratios).
         (Thresholds have been lowered to allow small 'T' bars.)
      5. Group candidate bars into clusters based on their vertical proximity.
      6. For each group (candidate IMB), sort the bars by x-coordinate and classify each using four modalities:
           - F (Full): The candidate touches (within tolerance) both the group top and bottom.
           - A (Ascender): The candidate touches the group top (within tolerance) and extends downward past the middle.
           - D (Descender): The candidate touches the group bottom (within tolerance) and extends upward past the middle.
           - T (Tiny): If the candidate’s height is less than about 30% of the group height.
      7. Annotate each candidate bar on a debug image with its classification.
    
    Returns:
      A list of dictionaries, one per detected IMB group, with keys:
         'pattern': The string pattern (e.g., "FADT..."),
         'bbox': The bounding box of the group (x, y, w, h),
         'bars': List of candidate bar regions in the group.
    """
    global itter
    # Step 1: Grayscale and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    save_debug_image("debug_imb_binary_full.jpg", binary)
    
    # Step 2: Morphological closing with vertical kernel (1x3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    save_debug_image("debug_imb_closed_full.jpg", closed)
    
    # Step 3: Connected components analysis
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(closed, connectivity=8)
    
    # Step 4: Candidate extraction with lowered thresholds for small bars,
    # and increased vertical-to-horizontal ratio requirement to filter letters.
    candidates = []
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        # Require minimum area 20, minimum width 1, minimum height 3, and vertical ratio at least 2.5.
        if (h_box / float(w_box)) < 1.5:
            # print(itter, ": ", area, w_box, h_box, (h_box / float(w_box)))
            continue
        
        center_y = y + h_box / 2
        candidates.append((x, y, w_box, h_box, center_y))
    
    if not candidates:
        print("No candidate IMB bars detected.")
        return []
    
    # Step 5: Group candidates by vertical proximity.
    groups = []
    candidates.sort(key=lambda c: c[4])
    y_threshold = 40  # maximum difference in center_y (in pixels) for grouping
    for cand in candidates:
        assigned = False
        for group in groups:
            if abs(cand[4] - np.mean([c[4] for c in group])) < y_threshold:
                group.append(cand)
                assigned = True
                break
        if not assigned:
            groups.append([cand])
    
    # Only keep groups with a sufficient number of bars.
    groups = [g for g in groups if len(g) >= 30]

    for idx, group in enumerate(groups):
        group.sort(key=lambda c: c[0])
        xs = [c[0] for c in group]
        ys = [c[1] for c in group]
        ws = [c[2] for c in group]
        hs = [c[3] for c in group]
        group_bbox = (min(xs), min(ys), max([xs[i] + ws[i] for i in range(len(xs))]) - min(xs),
                      max([ys[i] + hs[i] for i in range(len(ys))]) - min(ys))

        x, y, w, h = group_bbox
        padding = 25
        x_new = max(0, x - padding)
        y_new = max(0, y - padding)
        x_end = min(closed.shape[1], x + w + padding)
        y_end = min(closed.shape[0], y + h + padding)
        cropped = closed[y_new:y_end, x_new:x_end]

        save_debug_image("debug_img_cropped.jpg", cropped)

    # Step 3.2: Connected components analysis
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cropped, connectivity=8)

    # Step 4.2: Candidate extraction with lowered thresholds for small bars,
    # and increased vertical-to-horizontal ratio requirement to filter letters.
    candidates = []
    for i in range(1, num_labels):
        x, y, w_box, h_box, area = stats[i]
        # Require minimum area 20, minimum width 1, minimum height 3, and vertical ratio at least 2.5.
        if (h_box / float(w_box)) < 1.5:
            # print(itter, ": ", area, w_box, h_box, (h_box / float(w_box)))
            continue
        
        center_y = y + h_box / 2
        candidates.append((x, y, w_box, h_box, center_y))
    
    if not candidates:
        print("No candidate IMB bars detected.")
        return []
    
    # Step 5: Group candidates by vertical proximity.
    groups = []
    candidates.sort(key=lambda c: c[4])
    y_threshold = 40  # maximum difference in center_y (in pixels) for grouping
    for cand in candidates:
        assigned = False
        for group in groups:
            if abs(cand[4] - np.mean([c[4] for c in group])) < y_threshold:
                group.append(cand)
                assigned = True
                break
        if not assigned:
            groups.append([cand])
    
    # Only keep groups with a sufficient number of bars.
    groups = [g for g in groups if len(g) >= 30]
    
    imb_results = []
    debug_full = image.copy()
    
    # Step 6: Process each group.
    for idx, group in enumerate(groups):
        group.sort(key=lambda c: c[0])
        xs = [c[0] for c in group]
        ys = [c[1] for c in group]
        ws = [c[2] for c in group]
        hs = [c[3] for c in group]
        group_bbox = (min(xs), min(ys), max([xs[i] + ws[i] for i in range(len(xs))]) - min(xs),
                      max([ys[i] + hs[i] for i in range(len(ys))]) - min(ys))
        group_y_min = group_bbox[1]
        group_y_max = group_bbox[1] + group_bbox[3]
        group_height = group_y_max - group_y_min
        mid = group_y_min + group_height / 2
        tolerance = 15  # pixels
        
        pattern = ""
        for (x, y, w_box, h_box, cy) in group:
            top = y
            bottom = y + h_box
            # If the candidate is very short relative to the group, classify as T.
            if h_box < 0.3 * group_height:
                label = "T"
            else:
                # F: candidate touches both top and bottom.
                if top <= group_y_min + tolerance and bottom >= group_y_max - tolerance:
                    label = "F"
                # A: candidate touches top and extends downward past the middle.
                elif top <= group_y_min + tolerance and bottom > mid:
                    label = "A"
                # D: candidate touches bottom and extends upward past the middle.
                elif bottom >= group_y_max - tolerance and top < mid:
                    label = "D"
                else:
                    label = "T"
            pattern += label
            cv2.rectangle(debug_full, (x, y), (x + w_box, y + h_box), (255, 0, 0), 1)
            cv2.putText(debug_full, label, (x, y + h_box // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        
        imb_results.append({
            "pattern": pattern,
            "bbox": group_bbox,
            "bars": group
        })
        cv2.rectangle(debug_full, (group_bbox[0], group_bbox[1]),
                      (group_bbox[0] + group_bbox[2], group_bbox[1] + group_bbox[3]),
                      (0, 255, 0), 2)
        cv2.putText(debug_full, f"IMB {idx+1}: {pattern[:900]}", 
                    (group_bbox[0], group_bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    itter += 1
    save_output_image("debug_imb_groups" + str(itter) + ".jpg", debug_full)
    return imb_results