import tkinter as tk
from tkinter import Menu, filedialog
from PIL import Image, ImageTk
import os
import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
from astropy.modeling import models, fitting
from specutils import Spectrum1D
from specutils.fitting import fit_lines
from astropy import units as u
import csv
import vision
import debayering

project_directory = os.getcwd()
placed_objects = []
reticle_tag = None
placement_mode = False

rotating_mode = False
rotating = False
initial_x, initial_y = 0, 0
current_reticle_tag = None

reticle_place = False

centerPoint = 0,0
final_angle = 0

new_width = 0 
new_height = 0

resized_image_csv = None
resized_image_green_csv = None
resized_image_blue_csv = None
resized_image_red_csv = None

img_x, img_y = 0, 0

imageScale = 0

def gaussian(x, amp, mu, sigma):
    return amp * np.exp(-(x - mu)**2 / (2 * sigma**2))

def save_profile_to_csv(profile, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Intensity'])
        for i, value in enumerate(profile):
            writer.writerow([i, value])
    print(f"Profile saved to {filename}")

# Adds File Explorer
def browseFiles():
    filename = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        title="Select a File",
        filetypes=(("Fits files", "*.fit;*.fits"), ("all files", "*.*"))
    )
    print(filename)
    
    if filename:
        # Read the image using OpenCV
        debayering.debayerFile(filename)
        image = cv2.imread('color_image_final.png')

        # Normalize the image to the range [0, 255]
        normalized_image = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        normalized_image = normalized_image.astype(np.uint8)

        image_blue = cv2.imread("blue_channel.png")
        normalized_blue_image = image_blue.astype(np.uint8)
        image_green = cv2.imread("green_channel.png")
        normalized_green_image = image_green.astype(np.uint8)
        image_red = cv2.imread("red_channel.png")
        normalized_red_image = image_red.astype(np.uint8)

        # Use PIL to open the image for resizing
        img = Image.open('color_image_final.png')

        #Do debayering things


        # Get original image dimensions
        original_height, original_width = normalized_image.shape[:2]

        # Calculate the scaling factors
        scale_width = screen_width / original_width
        scale_height = screen_height / original_height
        
        # Use the smaller scaling factor to maintain aspect ratio
        scale = min(scale_width, scale_height)
        global imageScale
        imageScale = scale

        # Calculate new dimensions
        global new_width
        global new_height
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)

        # Resize the image using OpenCV for further processing
        global resized_image_csv
        resized_image_csv = cv2.resize(normalized_image, (new_width, new_height))
        global resized_image_green_csv
        resized_image_green_csv = cv2.resize(normalized_green_image, (new_width, new_height))
        global resized_image_blue_csv
        resized_image_blue_csv = cv2.resize(normalized_blue_image, (new_width, new_height))
        global resized_image_red_csv
        resized_image_red_csv = cv2.resize(normalized_red_image, (new_width, new_height))

        # Resize the image using PIL for displaying
        resized_image = img.resize((new_width, new_height))

        # Convert the image to PhotoImage
        img_tk = ImageTk.PhotoImage(resized_image)

        # Clear the canvas
        canvas.delete("all")

        global img_x, img_y
        img_x = (screen_width - new_width) // 2
        img_y = (screen_height - new_height) // 2

        # Center the image on the canvas
        canvas.create_image(
            (screen_width - new_width) // 2, 
            (screen_height - new_height) // 2, 
            anchor=tk.NW, 
            image=img_tk
        )

        # Keep a reference to avoid garbage collection
        canvas.image = img_tk

        root.update()

def spectrumBounds():
    height, width = new_height, new_width
    
    # Calculate the endpoints of the line
    x_center, y_center = centerPoint
    half_length = int(np.hypot(width, height) // 2)
    x1 = int(x_center + half_length * np.cos(final_angle))
    y1 = int(y_center + half_length * np.sin(final_angle))
    x2 = int(x_center - half_length * np.cos(final_angle))
    y2 = int(y_center - half_length * np.sin(final_angle))

    # Generate linearly spaced coordinates between x1, y1 and x2, y2
    num_points = int(np.hypot(new_width, new_height))
    x_values = np.linspace(x1, x2, num_points)
    y_values = np.linspace(y1, y2, num_points)

    # Ensure the resized image is converted to grayscale
    grayscale_image = cv2.cvtColor(resized_image_csv, cv2.COLOR_BGR2GRAY)

    # Draw a red line on the image to indicate the profile line
    line_image = resized_image_csv.copy()
    for (x, y) in zip(x_values, y_values):
        if 0 <= int(y) < height and 0 <= int(x) < width:
            cv2.circle(line_image, (int(x), int(y)), 1, (0, 0, 255), -1)  # Draw small red circles along the line

    # Sample the image at the generated coordinates
    line_profile = []
    color_line_profile = []
    red_line_profile = []
    green_line_profile = []
    blue_line_profile = []

    for x, y in zip(x_values, y_values):
        if 0 <= int(y) < height and 0 <= int(x) < width:
            line_profile.append(grayscale_image[int(y), int(x)])
            color_line_profile.append(resized_image_csv[int(y), int(x)])
            red_line_profile.append(resized_image_red_csv[int(y), int(x)])
            green_line_profile.append(resized_image_green_csv[int(y), int(x)])
            blue_line_profile.append(resized_image_blue_csv[int(y), int(x)])

        
    line_profile = np.array(line_profile)
    color_line_profile = np.array(color_line_profile)
    red_line_profile = np.array(red_line_profile)
    green_line_profile = np.array(green_line_profile)
    blue_line_profile = np.array(blue_line_profile)
    

    middlePoint = centerPoint[0]


    print("This is the middle point:")
    print(middlePoint)

    half_spectrum_length = 1048 * imageScale

    print("Start pixel" + str(int(middlePoint-half_spectrum_length)))
    print("End pixel" + str(int(middlePoint+half_spectrum_length)))
    print(middlePoint)
    print(half_spectrum_length)

    preprocessed = []
    preprocessed_red = []
    preprocessed_green = []
    preprocessed_blue = []

    for i in range(int(middlePoint-half_spectrum_length),int(middlePoint+half_spectrum_length)):
        preprocessed.append(line_profile[i])
        preprocessed_red.append(red_line_profile[i])
        preprocessed_green.append(green_line_profile[i])
        preprocessed_blue.append(blue_line_profile[i])

    save_profile_to_csv(preprocessed, os.path.join(project_directory, 'grayscale_profile.csv'))
    save_profile_to_csv(preprocessed_red, os.path.join(project_directory, 'red_profile.csv'))
    save_profile_to_csv(preprocessed_green, os.path.join(project_directory, 'green_profile.csv'))
    save_profile_to_csv(preprocessed_blue, os.path.join(project_directory, 'blue_profile.csv'))

    
    colorTemp = vision.spectrumAnalysis()

    with open('temperature.txt', 'w') as f:
        f.write(str(colorTemp))

    # Close the Tkinter window
    root.destroy()

# Place reticle
def place_object(event): 
    if placement_mode:
        global reticle_tag
        global reticle_place
        global current_reticle_tag
        global centerPoint
        global final_angle
        final_angle = 0

        canvas.delete(reticle_tag)
        x, y = event.x, event.y

        relative_x = x - img_x
        relative_y = y - img_y
        # Place a dot (you can customize this to be a reticle or other shape)
        reticle_tag = f"reticle_{len(placed_objects)}"
        size = 200

        # Create a reticle using lines with a common tag
        line1_id = canvas.create_line(x-size, y, x+size, y, fill="red", width=2, tags=reticle_tag)
        line2_id = canvas.create_line(x, y-size, x, y+size, fill="white", width=2, tags=reticle_tag)
        
        centerPoint = relative_x,relative_y
        
        # Save the coordinates
        placed_objects.append((x, y, reticle_tag))
        reticle_place = True
        current_reticle_tag = reticle_tag

        print(f"Object placed at: ({relative_x}, {relative_y})")
    elif rotating_mode and reticle_place:
        print("Starting Rotation")
        global rotating, initial_x, initial_y
        rotating = True
        initial_x, initial_y = event.x, event.y

# Starts Window
root = tk.Tk()

# Defines Initial Sizes
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Sets Window Geometry
root.geometry(f"{screen_width}x{screen_height}")
root.title("Spectrum Analyzer")

# Adds Menubar
menubar = Menu(root)
root.config(menu=menubar)

# Creates menubar object
tools_menu = Menu(menubar, tearoff=False)
tools_menu.add_command(
    label='Select File',
    command=browseFiles
)

tools_menu.add_command(
    label='Analyze Spectrum',
    command=spectrumBounds
)

# Adds to the Menubar
menubar.add_cascade(
    label="Tools",
    menu=tools_menu
)

def stop_rotation(event):
    print("Stop Rotation")
    global rotating
    rotating = False

def rotate_reticle(event):
    if rotating and current_reticle_tag:
        
        global final_angle

        print("We be rotating")
        current_x, current_y = event.x, event.y
        angle = math.atan2(current_y - initial_y, current_x - initial_x)

        # Get the center of the reticle
        x, y, _ = placed_objects[-1]
        size = 200

        # Calculate new positions for the lines
        x1 = x + size * math.cos(angle)
        y1 = y + size * math.sin(angle)
        x2 = x - size * math.cos(angle)
        y2 = y - size * math.sin(angle)
        x3 = x + size * math.cos(angle + math.pi / 2)
        y3 = y + size * math.sin(angle + math.pi / 2)
        x4 = x - size * math.cos(angle + math.pi / 2)
        y4 = y - size * math.sin(angle + math.pi / 2)

        final_angle = math.atan2(y3 - y, x3 - x)

        print("This is the final angle:" + str(final_angle * (180/math.pi)))
        print("This is the center point:" + str(centerPoint))

        # Delete the old reticle and draw the new one
        canvas.delete(current_reticle_tag)
        reticle_tag = current_reticle_tag
        line1_id = canvas.create_line(x2, y2, x1, y1, fill="red", width=2, tags=reticle_tag)
        line2_id = canvas.create_line(x4, y4, x3, y3, fill="white", width=2, tags=reticle_tag)

canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack()

canvas.bind("<Button-1>", place_object)

def enable_placement_mode(event):
    global placement_mode
    global rotating_mode
    rotating_mode = False

    if placement_mode:
        placement_mode = False
    elif not placement_mode:
        placement_mode = True
    print("Placement mode enabled")

def enable_rotation_mode(event):
    global rotating_mode
    global placement_mode
    placement_mode = False

    if rotating_mode:
        rotating_mode = False
    elif not rotating_mode:
        rotating_mode = True
    print("Rotation mode enabled")

root.bind("<p>", enable_placement_mode)
root.bind("<r>", enable_rotation_mode)

canvas.bind("<B1-Motion>", rotate_reticle)
canvas.bind("<ButtonRelease-1>", stop_rotation)

root.mainloop()
