import subprocess
import time

import os
from datetime import datetime
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
from PIL import ImageTk, Image
import cv2
from cv2 import *
import threading

def ZWOLiveThreadFunc():
    while True:
        if ZWOLiveActive:
            #get exposure time for image capture
            try:
                exptime = float(ZWOexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1
            takeZWOPicture(exptime, "/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO", "ZLIVE") #take image
    
            #display image
            image1 = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO/ZLIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=image1, size=(470, 315))
            label = ctk.CTkLabel(live_loop_frame, text="", image=Z_live_test)
            label.place(x=100, y=60)
        time.sleep(1)
    
def PILiveThreadFunc():
    while True:
        if PILiveActive:
            #get exposure time for image capture
            try:
                exptime = float(PIexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1
            takePIPicture(exptime, "/home/starspec/STSC/STSCvenv/UI/LIVE/PI", "PILIVE") #take image
    
            #display image
            image2 = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/PI/PILIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=image2, size=(470, 315))
            label = ctk.CTkLabel(live_loop_frame, text="", image=Z_live_test)
            label.place(x=100, y=380) 
        time.sleep(1)

def stopLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 0
    print("ZWO Live image capture has stopped.")

def startLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 1
    print("Main Camera Looping Exposure Enabled")
  
def stopLivePIImage():
    global PILiveActive
    PILiveActive = 0
    print("PI Live image capture has stopped.")

def startLivePIImage():
    global PILiveActive
    PILiveActive = 1
    print("Guide Camera Looping Exposure Enabled")

#open phd2 [UPDATE TO CLOSE PI CONNECTION PRIOR TO OPENING]
def open_phd2():
    print("Disconnecting Guide Camera")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("Opening PHD2...")

#open spectrum analysis
def open_analysis():
    print("Displaying spectrum analysis")

#takes and saves a picture on the ZWO camera
def takeZWOPicture(exp_time, save_location, upload_prefix):
    print("ZWO picture taken")
    
#takes and saves a picture on the ZWO camera
def takePIPicture(exp_time, save_location, upload_prefix):
    print("PI picture taken")

#submit the ZWO settings to the INDI server
def submitZWOsettings():
    gain = ZWOgain_text.get("1.0", "end-1c")
    exposure_time = float(ZWOexposure_time_text.get("1.0", "end-1c"))
    temperature = ZWOtemperature_text.get("1.0", "end-1c")

    if gain == "":
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"ZWO gain is set at {gain_value}")

    if ZWOexposure_time_text.get("1.0", "end-1c") == "":
        exposure_time_value = 1
    else:
        try:
            exposure_time_value = float(exposure_time)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"ZWO exposure time is set at {exposure_time} seconds")
        
    if temperature == "":
        temperature_value = 21
    else:
        try:
            temperature_value = int(temperature)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid temperature")
            return
    print(f"Temperature is set at {temperature_value} °C")

#submit the PI settings to the INDI server
def submitPIsettings():
    gain = PIgain_text.get("1.0", "end-1c")
    exposure_time = float(PIexposure_time_text.get("1.0", "end-1c"))

    if gain == "":
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"PI gain is set at {gain_value}")

    if PIexposure_time_text.get("1.0", "end-1c") == "":
        exposure_time_value = 1
    else:
        try:
            exposure_time_value = float(exposure_time)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return

    print(f"PI exposure time is set at {exposure_time} seconds")

#move the mount north
def moveNorth():
    print("Mount moved north")

#move the mount south
def moveSouth():
    print("Mount moved south")

#move the mount east
def moveEast():
    print("Mount moved east")

#move the mount west
def moveWest():
    print("Mount moved west")

#terminate UI
def close():
    root.destroy()

#----- START INITIALIZE DEVICES -----
ZWOcam = "ZWO CCD ASI294MC Pro"
PIcam = "indi_pylibcamera"
Mount = "Celestron GPS"

#starts daemon ZWO and PI livestream threads for live capture
ZWOLiveActive = 0
ZWOLiveThread = threading.Thread(target=ZWOLiveThreadFunc)
ZWOLiveThread.daemon = True #kills on program exit
PILiveActive = 0
PILiveThread = threading.Thread(target=PILiveThreadFunc)
PILiveThread.daemon = True #kills on program exit

ZWOLiveThread.start()
print("ZWOLiveThread has started")
PILiveThread.start()
print("PILiveThread has started")

# Introspection returns an XML document containing information
# about the methods supported by an interface.
# print("Introspection data:\n")
# print(remote_object.Introspect())

print("Waiting for INDI devices...")

print("Connection to Telescope and CCD is established.")
#----- END INITIALIZE DEVICES -----

#----- START INITIALIZE GUI -----
#system appearance
ctk.set_appearance_mode("System")

#frame
root = ctk.CTk()
root.minsize(420, 360)
root.maxsize(840, 720)
root.geometry("840x720+440+55")
root.title("StarSpec UI")

#define background
image = Image.open("Space_Image.jpeg")
bg = ctk.CTkImage(dark_image=image, size=(840, 720))

#create 1st frame (live view)
live_loop_frame = ctk.CTkFrame(root)
live_loop_frame.pack(fill="both", expand=1)
bg_image1 = ctk.CTkLabel(live_loop_frame, image=bg, text="")
bg_image1.pack(expand=1)
bg_image1.place(x=0, y=0)

#create 2nd frame (loop settings)
settings_frame = ctk.CTkFrame(root)
settings_frame.pack(fill="both", expand=1)
settings_frame.place(x=0, y=0)
bg_image3 = ctk.CTkLabel(settings_frame, image=bg, text="")
bg_image3.pack(expand=1)
#----- END INITIALIZE GUI -----

#----- START LIVE VIEW BUTTONS -----
label_bg = ctk.CTkImage(dark_image=image, size=(75, 30))
Z_cam_label = ctk.CTkLabel(live_loop_frame,
                            text="ZWO Cam", font=("Helvetica", 16), text_color="white",
                            image=label_bg)
Z_cam_label.pack()
Z_cam_label.place(x=15, y=200)

Pi_cam_label = ctk.CTkLabel(live_loop_frame,
                            text="PI Cam", font=("Helvetica", 16), text_color="white",
                            image=label_bg)
Pi_cam_label.pack()
Pi_cam_label.place(x=15, y=530)

live_view = ctk.CTkButton(live_loop_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_loop_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=10, y=10)

loop_settings = ctk.CTkButton(live_loop_frame,
                                text="Settings", font=("Helvetica", 18), text_color="white",
                                command=lambda:settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=116, y=10)

north = ctk.CTkButton(live_loop_frame,
                        text="N", font=("Helvetica", 16), text_color="white",
                        command=moveNorth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=680, y=294)

south = ctk.CTkButton(live_loop_frame,
                        text="S", font=("Helvetica", 16), text_color="white",
                        command=moveSouth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=680, y=394)

east = ctk.CTkButton(live_loop_frame,
                        text="E", font=("Helvetica", 16), text_color="white",
                        command=moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=730, y=344)

west = ctk.CTkButton(live_loop_frame,
                        text="W", font=("Helvetica", 16), text_color="white",
                        command=moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=630, y=344)

start_Z_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:startLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_Z_liveloop.pack(anchor="nw", expand=1)
start_Z_liveloop.place(x=610, y=130)

stop_Z_liveloop = ctk.CTkButton(live_loop_frame,
                                text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:stopLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_Z_liveloop.pack(anchor="nw", expand=1)
stop_Z_liveloop.place(x=610, y=170)

capture_ZWO_image = ctk.CTkButton(live_loop_frame,
                                    text="Capture ZWO Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takeZWOPicture(float(ZWOexposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures", "ZWO_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_ZWO_image.pack(anchor="nw", expand=1)
capture_ZWO_image.place(x=610, y=210)

start_PI_liveloop = ctk.CTkButton(live_loop_frame,
                                    text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:startLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_PI_liveloop.pack(anchor="nw", expand=1)
start_PI_liveloop.place(x=610, y=470)

stop_PI_liveloop = ctk.CTkButton(live_loop_frame,
                                    text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:stopLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_PI_liveloop.pack(anchor="nw", expand=1)
stop_PI_liveloop.place(x=610, y=510)

capture_PI_image = ctk.CTkButton(live_loop_frame,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(float(PIexposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/PICaptures", "PI_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_PI_image.pack(anchor="nw", expand=1)
capture_PI_image.place(x=610, y=550)

phd2_button = ctk.CTkButton(live_loop_frame,
                            text="PHD2", font=("Helvetica", 18), text_color="white",
                            command=open_phd2,
                            fg_color="black", bg_color="black", hover_color="dark grey", text_color_disabled="red",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
phd2_button.pack(expand=1)
phd2_button.place(x=582, y=10)

spectrum_analysis_button = ctk.CTkButton(live_loop_frame,
                            text="Spectrum Analysis", font=("Helvetica", 18), text_color="white",
                            command=open_analysis,
                            fg_color="black", bg_color="black", hover_color="dark grey", text_color_disabled="red",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
spectrum_analysis_button.pack(expand=1)
spectrum_analysis_button.place(x=660, y=10)

close_button1 = ctk.CTkButton(live_loop_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button1.pack(anchor="nw", expand=1)
close_button1.place(x=760, y=680)
#----- END LIVE VIEW BUTTONS -----

#----- START SETTINGS BUTTONS -----
live_view = ctk.CTkButton(settings_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_loop_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=10, y=10)

loop_settings = ctk.CTkButton(settings_frame,
                                text="Settings", font=("Helvetica", 18), text_color="white",
                                command=lambda:settings_frame.tkraise(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                width=50,
                                anchor="nw",
                                corner_radius=10,
                                border_color="white", border_width=2)
loop_settings.pack(expand=1)
loop_settings.place(x=116, y=10)

ZWOsubmit_button = ctk.CTkButton(settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitZWOsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
ZWOsubmit_button.pack(anchor="nw", expand=1)
ZWOsubmit_button.place(x=100, y=260)

PIsubmit_button = ctk.CTkButton(settings_frame,
                                text="Submit", font=("Helvetica", 18), text_color="white",
                                command=submitPIsettings,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
PIsubmit_button.pack(padx=10, pady=10, anchor="nw", expand=1)
PIsubmit_button.place(x=350, y=260)

close_button2 = ctk.CTkButton(settings_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button2.pack(anchor="nw", expand=1)
close_button2.place(x=760, y=680)

#ZWO Camera Settings
ZWOtitle_label = ctk.CTkLabel(settings_frame,
                                text="MAIN SETTINGS", font=("Helvetica", 18), text_color="white",
                                fg_color="black",  bg_color="black",
                                corner_radius=10)
ZWOtitle_label.pack(anchor="nw", expand=1)
ZWOtitle_label.place(x=50, y=60)

#set ZWO gain
ZWOgain_label = ctk.CTkLabel(settings_frame,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
ZWOgain_label.pack(anchor="nw", expand=1)
ZWOgain_label.place(x=10, y=105)

ZWOgain_text = ctk.CTkTextbox(settings_frame,
                                font=("Helvetica", 18),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False" )
ZWOgain_text.pack(anchor="nw", expand=1)
ZWOgain_text.place(x=180, y=100)

#set ZWO exposure time
ZWOexposure_time_label = ctk.CTkLabel(settings_frame,
                                        text="Exposure Time(s):", font=("Helvetica", 18), text_color="white",
                                        fg_color="black",  bg_color="black",
                                        corner_radius=10)
ZWOexposure_time_label.pack(anchor="nw", expand=1)
ZWOexposure_time_label.place(x=10, y=155)

ZWOexposure_time_text = ctk.CTkTextbox(settings_frame,
                                        font=("Helvetica", 18),
                                        fg_color="white", bg_color="black", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
ZWOexposure_time_text.pack(anchor="nw", expand=1)
ZWOexposure_time_text.place(x=180, y=150)

#set ZWO temperature
ZWOtemperature_label = ctk.CTkLabel(settings_frame,
                                    text="Temperature(°C):", font=("Helvetica", 18), text_color="white",
                                    fg_color="black",  bg_color="black",
                                    corner_radius=10)
ZWOtemperature_label.pack(anchor="nw", expand=1)
ZWOtemperature_label.place(x=10, y=205)

ZWOtemperature_text = ctk.CTkTextbox(settings_frame,
                                    font=("Helvetica", 18),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=70,
                                    activate_scrollbars="False")
ZWOtemperature_text.pack(anchor="nw", expand=1)
ZWOtemperature_text.place(x=180, y=200)

PItitle_label = ctk.CTkLabel(settings_frame,
                            text="GUIDE SETTINGS", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
PItitle_label.pack(anchor="nw", expand=1)
PItitle_label.place(x=300, y=60)

#set PI gain
PIgain_label = ctk.CTkLabel(settings_frame,
                            text="Gain:", font=("Helvetica", 18), text_color="white",
                            fg_color="black",  bg_color="black",
                            corner_radius=10)
PIgain_label.pack(anchor="nw", expand=1)
PIgain_label.place(x=270, y=105)

PIgain_text = ctk.CTkTextbox(settings_frame,
                                font=("Helvetica", 18),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False")
PIgain_text.pack(anchor="nw", expand=1)
PIgain_text.place(x=440, y=100)

#set PI exposure time
PIexposure_time_label = ctk.CTkLabel(settings_frame,
                                        text="Exposure Time(s):", font=("Helvetica", 18), text_color="white",
                                        fg_color="black",  bg_color="black",
                                        corner_radius=10)
PIexposure_time_label.pack(anchor="nw", expand=1)
PIexposure_time_label.place(x=270, y=155)

PIexposure_time_text = ctk.CTkTextbox(settings_frame,
                                        font=("Helvetica", 18),
                                        fg_color="white", bg_color="black", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
PIexposure_time_text.pack(anchor="nw", expand=1)
PIexposure_time_text.place(x=440, y=150)
#----- END SETTINGS BUTTONS -----

live_loop_frame.tkraise() #start the UI on the live view frame

#Run UI
root.mainloop()