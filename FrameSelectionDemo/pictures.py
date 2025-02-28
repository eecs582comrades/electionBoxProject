'''
Name of code artifact: Basic camera action script
Description: USes camera on device connected and captures a bunch of photos; Calculates laplacian variance of each photo 
and saves the best one(The hsarpest and least blurry image)
Name(s): Chase Curtis
Date Created: 11-10-24
'''

# Libraries to import
import cv2
import numpy as np
import os

# Possibly turn all of this into a function

# Function to calculate the sharpness of an image using Laplacian variance(Helps decide what is blurry and what is sharp)
def calculate_sharpness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert the image to grayscale
    return cv2.Laplacian(gray, cv2.CV_64F).var() # Calculate the laplacian variance

# Initialize the camera
camera = cv2.VideoCapture(0)  # 0 for default camera
if not camera.isOpened(): 
    print("Error: Could not open the camera.")
    exit() 

image_list = []
sharpness_scores = []

# Capture Images
for i in range(100):
    ret, frame = camera.read()
    if not ret:
        print(f"Error capturing image {i + 1}")
        continue

    # Display the image (Testing)
    cv2.imshow(f"Captured Image {i + 1}", frame)
    cv2.waitKey(1) # Wait 10ms between captures

    # Calculate sharpness
    sharpness = calculate_sharpness(frame)
    sharpness_scores.append(sharpness)
    image_list.append(frame)

# Release the camera
camera.release()
# Close windows (Testing)
cv2.destroyAllWindows()

# Takes Best Image based on sharpness(Laplacian Variance)
if image_list:
    best_index = np.argmax(sharpness_scores)
    best_image = image_list[best_index]

    # Display the best image(Testing)
    cv2.imshow("Best Image", best_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save the best image
    cv2.imwrite("best_image.jpg", best_image)
    
    # Here input code to send to Wil's code for decoding the barcodes

    print(f"Image saved! Sharpness score(For Testing): {sharpness_scores[best_index]}")
else:
    print("No images were captured.")
