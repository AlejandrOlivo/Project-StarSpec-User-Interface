import subprocess
import time

#Initialize KSTARS server
KSTARS_init_path = "./KSTARS_init.sh"
KSTARS_init_command = f"gnome-terminal -- bash -c '{KSTARS_init_path}; exec bash'"
KSTARS_init_process = subprocess.Popen(KSTARS_init_command, shell=True)
print("Initializing KSTARS...")
time.sleep(6)

#initizlize INDI server
INDI_init_path = "./INDI_init.sh"
INDI_init_command = f"gnome-terminal -- bash -c '{INDI_init_path}; exec bash'"
INDI_init_process = subprocess.Popen(INDI_init_command, shell=True)
print("Initializing INDI Server...")
time.sleep(6)

import os
from datetime import datetime
from gi.repository import GObject as gobject
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
import dbus
from dbus import glib
import threading

def ZWOLiveThreadFunc():
    while True:
        if ZWOLiveActive:
            global Z_Expose_t

            #Get Exposure Time
            try:
                exptime = float(ZWOexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1
            
            #Take Image
            takeZWOPicture(Z_Expose_t, "/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO", "ZLIVE")
    
            #Display ZWO Image
            image1 = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/ZWO/ZLIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=image1, size=(470, 315))
            label = ctk.CTkLabel(live_view_frame, text="", image=Z_live_test)
            label.place(x=100, y=60) 
        time.sleep(1)

def PILiveThreadFunc():
    while True:
        if PILiveActive:
            global PI_Expose_t

            #Get Exposure Time
            try:
                exptime = float(PIexposure_time_text.get("1.0", "end-1c"))
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid exposure time, using exposure time = 1")
                exptime = 1

            takePIPicture(PI_Expose_t, "/home/starspec/STSC/STSCvenv/UI/LIVE/PI", "PILIVE") #take image
    
            #Display PI Image
            image2 = Image.open("/home/starspec/STSC/STSCvenv/UI/LIVE/PI/PILIVE.fits")
            Z_live_test = ctk.CTkImage(dark_image=image2, size=(470, 315))
            label = ctk.CTkLabel(live_view_frame, text="", image=Z_live_test)
            label.place(x=100, y=380)
        time.sleep(1)

def stopLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 0
    print("\nMain Camera image capture disabled")

def startLiveZImage():
    global ZWOLiveActive
    ZWOLiveActive = 1
    print("\nMain Camera image capture enabled")
  
def stopLivePIImage():
    global PILiveActive
    PILiveActive = 0
    print("\nGuide Camera image capture disabled")

def startLivePIImage():
    global PILiveActive
    PILiveActive = 1
    print("\nGuide Camera image capture enabled")

#Open PHD2
def open_phd2():
    print("Disconnecting Guide Camera")
    iface.setSwitch(PIcam, "CONNECTION", "DISCONNECT", "On")
    iface.sendProperty(PIcam, "CONNECTION")
    result = subprocess.Popen(['phd2'], stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = TRUE)
    print("\nOpening PHD2...")

#Open Spectrum Analysis
def open_analysis():
    spectrum_path = "spectrumUI.py"
    result = subprocess.Popen(["python", spectrum_path], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    print("\nOpening spectrum analysis")
    
    with open("temperature.txt", "r") as file:
        content = file.read()
    temp = content.strip("[]") + "°K"
    
    spectrum_temp = ctk.CTkLabel(live_view_frame,
                                text=f"Star temperature = {temp}", font=("Helvetica", 14), text_color="white",
                                fg_color="black",  bg_color="#091421",
                                corner_radius=10)
    spectrum_temp.pack(anchor="nw", expand=1)
    spectrum_temp.place(x=580, y=70)

#Captures and saves image from ZWO camera
def takeZWOPicture(exp_time, save_location, upload_prefix):
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", save_location)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
    iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", upload_prefix)
    iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
    iface.setNumber(ZWOcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", float(exp_time))
    iface.sendProperty(ZWOcam, "CCD_EXPOSURE")

    #Wait until exposure is complete
    ccdState = "Busy"
    while iface.getPropertyState(ZWOcam, "CCD_EXPOSURE") == "Busy":
        time.sleep(1)
    
#Captures and saves image from PI camera
def takePIPicture(exp_time, save_location, upload_prefix):
    iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", save_location)
    iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
    iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", upload_prefix)
    iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
    iface.setNumber(PIcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", float(exp_time))
    iface.sendProperty(PIcam, "CCD_EXPOSURE")
    
    #Wait until exposure is complete
    ccdState = "Busy"
    while iface.getPropertyState(PIcam, "CCD_EXPOSURE") == "Busy":
        time.sleep(1)

def Z_RAW():
    if check_RAW_Z.get() == "on":
        check_RGB_Z.deselect()
        iface.setSwitch(ZWOcam, "CCD_CAPTURE_FORMAT", "ASI_IMG_RAW16", "On")
        iface.sendProperty(ZWOcam, "CCD_CAPTURE_FORMAT")
    
def Z_RGB():
    if check_RGB_Z.get() == "on":
        check_RAW_Z.deselect()
        iface.setSwitch(ZWOcam, "CCD_CAPTURE_FORMAT", "ASI_IMG_RGB24", "On")
        iface.sendProperty(ZWOcam, "CCD_CAPTURE_FORMAT")

def PI_RAW():
    if check_RAW_PI.get() == "on":
        check_RGB_PI.deselect()
        iface.setSwitch(PIcam, "CCD_CAPTURE_FORMAT", "INDI_RAW", "On")
        iface.sendProperty(PIcam, "CCD_CAPTURE_FORMAT")
    
def PI_RGB():
    if check_RGB_PI.get() == "on":
        check_RAW_PI.deselect()
        iface.setSwitch(PIcam, "CCD_CAPTURE_FORMAT", "INDI_RGB", "On")
        iface.sendProperty(PIcam, "CCD_CAPTURE_FORMAT")
        
def Mount_Fast():
    if check_FAST_Mount.get() == "on":
        check_SLOW_Mount.deselect()
        iface.setSwitch(Mount, "TELESCOPE_SLEW_RATE", "9x", "On")
        iface.sendProperty(Mount, "TELESCOPE_SLEW_RATE")
        
def Mount_Slow():
    if check_SLOW_Mount.get() == "on":
        check_FAST_Mount.deselect()
        iface.setSwitch(Mount, "TELESCOPE_SLEW_RATE", "7x", "On")
        iface.sendProperty(Mount, "TELESCOPE_SLEW_RATE")

#Submit ZWO settings to the INDI server
def submitZWOsettings():
    global Z_expose_t
    gain = ZWOgain_text.get("1.0", "end-1c")
    exposure_time = float(ZWOexposure_time_text.get("1.0", "end-1c"))
    temperature = ZWOtemperature_text.get("1.0", "end-1c")

    if gain == "":
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
            #Set Gain
            iface.setNumber(ZWOcam, "CCD_CONTROLS", "Gain", gain_value)
            iface.sendProperty(ZWOcam, "CCD_CONTROLS")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"\nZWO gain is set at {gain_value}")

    if ZWOexposure_time_text.get("1.0", "end-1c") == "":
        Z_Expose_t = 1
    else:
        try:
            Z_Expose_t = float(exposure_time)
            #Set Exposure Time
            iface.setNumber(ZWOcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", Z_Expose_t)
            iface.sendProperty(ZWOcam, "CCD_EXPOSURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return
    print(f"ZWO exposure time is set at {exposure_time} seconds")

    if temperature == "":
        temperature_value = 21
    else:
        try:
            temperature_value = int(temperature)
            #Set Temperature
            iface.setNumber(ZWOcam, "CCD_TEMPERATURE", "CCD_TEMPERATURE_VALUE", temperature_value)
            iface.sendProperty(ZWOcam, "CCD_TEMPERATURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid temperature")
            return
    print(f"Temperature is set at {temperature_value} °C")

#Submit PI settings to the INDI server
def submitPIsettings():
    gain = PIgain_text.get("1.0", "end-1c")
    exposure_time = float(PIexposure_time_text.get("1.0", "end-1c"))

    if gain == "":
        gain_value = 0
    else:
        try:
            gain_value = int(gain)
            #set gain
            iface.setNumber(PIcam, "CCD_GAIN", "GAIN", gain_value)
            iface.sendProperty(PIcam, "CCD_GAIN")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid gain")
            return
    print(f"\nPI gain is set at {gain_value}")

    if PIexposure_time_text.get("1.0", "end-1c") == "":
        PI_Expose_t = 1
    else:
        try:
            PI_Expose_t = float(exposure_time)
            iface.setNumber(PIcam, "CCD_EXPOSURE", "CCD_EXPOSURE_VALUE", PI_Expose_t)
            iface.sendProperty(PIcam, "CCD_EXPOSURE")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid exposure time")
            return

    print(f"PI exposure time is set at {exposure_time} seconds")

#Move the Mount North
def moveNorth():
    north_active = iface.getSwitch(Mount, "TELESCOPE_MOTION_NS","MOTION_NORTH")
    if north_active == "Off":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_NS", "MOTION_NORTH", "On")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_NS")
        print("Starting North Motion...")
    if north_active == "On":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_NS", "MOTION_NORTH", "Off")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_NS")
        print("Stopping North Motion")

#Move the Mount South
def moveSouth():
    south_active = iface.getSwitch(Mount, "TELESCOPE_MOTION_NS","MOTION_SOUTH")
    if south_active == "Off":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_NS", "MOTION_SOUTH", "On")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_NS")
        print("Starting South Motion...")
    if south_active == "On":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_NS", "MOTION_SOUTH", "Off")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_NS")
        print("Stopping South Motion")

#Move the Mount East
def moveEast():
    east_active = iface.getSwitch(Mount, "TELESCOPE_MOTION_WE","MOTION_EAST")
    if east_active == "Off":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_WE", "MOTION_EAST", "On")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_WE")
        print("Starting East Motion...")
    if east_active == "On":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_WE", "MOTION_EAST", "Off")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_WE")
        print("Stopping East Motion")

#Move the Mount West
def moveWest():
    west_active = iface.getSwitch(Mount, "TELESCOPE_MOTION_WE","MOTION_WEST")
    if west_active == "Off":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_WE", "MOTION_WEST", "On")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_WE")
        print("Starting West Motion...")
    if west_active == "On":
        iface.setSwitch(Mount, "TELESCOPE_MOTION_WE", "MOTION_WEST", "Off")
        iface.sendProperty(Mount, "TELESCOPE_MOTION_WE")
        print("Stopping West Motion")

#Close User Interface
def close():
    root.destroy()

#----- START INITIALIZE DEVICES -----
ZWOcam = "ZWO CCD ASI294MC Pro"
PIcam = "indi_pylibcamera"
Mount = "Celestron GPS"

Z_Expose_t = 1
PI_Expose_t = 1

#Starts daemon ZWO and PI livestream threads for live capture
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

gobject.threads_init()
glib.init_threads()

#Create a Session Bus
bus = dbus.SessionBus()

#Create an object that will proxy for a particular remote object
remote_object = bus.get_object("org.kde.kstars", "/KStars/INDI")

#Get INDI Interface
iface = dbus.Interface(remote_object, 'org.kde.kstars.INDI')

#Initiate INDI Devices
while not iface.connect("localhost", 7624):
    time.sleep(1)

print("\nWaiting for INDI devices...")

#Array for received devices
devices = []

while True:
    devices = iface.getDevices()
    if (len(devices) < 3):
        time.sleep(1)
    else:
        break

print("We received the following devices:")
for device in devices:
    print(device)

#Connect User Interface to Device Drivers
iface.setSwitch(ZWOcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(ZWOcam, "CONNECTION")
iface.setSwitch(PIcam, "CONNECTION", "CONNECT", "On")
iface.sendProperty(PIcam, "CONNECTION")
iface.setSwitch(Mount, "CONNECTION", "CONNECT", "On")
iface.sendProperty(Mount, "CONNECTION")
ccdState = "Busy"

while True:
    ccdState = iface.getPropertyState(ZWOcam, "CONNECTION")
    if (ccdState != "Ok"):
        time.sleep(1)
    else:
        break

print("\nConnection to Main Camera, Mount, and Guide Camera is established.")

#Prints all properties of each device
'''
ZWOProps = iface.getProperties(ZWOcam)
PIProps = iface.getProperties(PIcam)
MOUNTProps = iface.getProperties(Mount)

print(f"\n---ZWO PROPERTIES---")
for ZWOProp in ZWOProps:
    print(ZWOProp)
    
print(f"\n---PI PROPERTIES---")
for PIProp in PIProps:
    print(PIProp)
    
print(f"\n---MOUNT PROPERTIES---")
for MountProp in MOUNTProps:
    print(MountProp)
'''

#Set cooling & temperature in ZWO camera
iface.setSwitch(ZWOcam, "CCD_COOLER", "COOLER_ON", "On")
iface.sendProperty(ZWOcam, "CCD_COOLER")

iface.setText(ZWOcam, "CCD_TEMPERATURE", "CCD_TEMPERATURE_VALUE", "13.00")
iface.sendProperty(ZWOcam, "CCD_TEMPERATURE")

#Set up images for local storage
iface.setSwitch(ZWOcam, "UPLOAD_MODE", "UPLOAD_LOCAL", "On")
iface.sendProperty(ZWOcam, "UPLOAD_MODE")
iface.setSwitch(PIcam, "UPLOAD_MODE", "UPLOAD_LOCAL", "On")
iface.sendProperty(PIcam, "UPLOAD_MODE")

#Set Image Format
iface.setSwitch(ZWOcam, "CCD_CAPTURE_FORMAT", "ASI_IMG_RAW16", "On")
iface.sendProperty(ZWOcam, "CCD_CAPTURE_FORMAT")
iface.setSwitch(PIcam, "CCD_CAPTURE_FORMAT", "INDI_RGB", "On")
iface.sendProperty(PIcam, "CCD_CAPTURE_FORMAT")

#Invert Mount Controls
iface.setSwitch(Mount, "TELESCOPE_REVERSE_MOTION", "REVERSE_NS", "On")
iface.sendProperty(Mount, "TELESCOPE_REVERSE_MOTION")
iface.setSwitch(Mount, "TELESCOPE_REVERSE_MOTION", "REVERSE_WE", "On")
iface.sendProperty(Mount, "TELESCOPE_REVERSE_MOTION")
 
#Set Image Location
iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures")
iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_DIR", "/home/starspec/STSC/STSCvenv/UI/PICaptures")
iface.sendProperty(PIcam, "UPLOAD_SETTINGS")

#Set Image Name
iface.setText(ZWOcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", "ZWO_IMAGE_XXX")
iface.sendProperty(ZWOcam, "UPLOAD_SETTINGS")
iface.setText(PIcam, "UPLOAD_SETTINGS", "UPLOAD_PREFIX", "PI_IMAGE_XXX")
iface.sendProperty(PIcam, "UPLOAD_SETTINGS")
#----- END INITIALIZE DEVICES -----

#----- START INITIALIZE GUI -----
ctk.set_appearance_mode("System")

root = ctk.CTk()
root.minsize(420, 360)
root.maxsize(840, 720)
root.geometry("840x720+440+55")
root.title("StarSpec")

#Define Background Image
image = Image.open("Space_Image.jpeg")
bg = ctk.CTkImage(dark_image=image, size=(840, 720))

#Create 1st Frame (Settings)
settings_frame = ctk.CTkFrame(root)
settings_frame.pack(fill="both", expand=1)
bg_image1 = ctk.CTkLabel(settings_frame, image=bg, text="")
bg_image1.pack(expand=1)
bg_image1.place(x=0, y=0)

#Create 2nd Frame (Live View)
live_view_frame = ctk.CTkFrame(root)
live_view_frame.pack(fill="both", expand=1)
live_view_frame.place(x=0, y=0)
bg_image2 = ctk.CTkLabel(live_view_frame, image=bg, text="")
bg_image2.pack(expand=1)
#----- END INITIALIZE GUI -----

#----- START SETTINGS BUTTONS -----
settings = ctk.CTkButton(settings_frame,
                        text="Settings", font=("Helvetica", 18), text_color="white",
                        command=lambda:settings_frame.tkraise(),
                        fg_color="black", bg_color="#091421", hover_color="dark grey",
                        width=50,
                        anchor="nw",
                        corner_radius=10,
                        border_color="white", border_width=2)
settings.pack(expand=1)
settings.place(x=10, y=10)

live_view = ctk.CTkButton(settings_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_view_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=106, y=10)

#ZWO Camera Settings
ZWOtitle_label = ctk.CTkLabel(settings_frame,
                                text="MAIN SETTINGS", font=("Helvetica", 30), text_color="white",
                                fg_color="black",  bg_color="#091421",
                                corner_radius=10)
ZWOtitle_label.pack(anchor="nw", expand=1)
ZWOtitle_label.place(x=100, y=100)

#Set ZWO Gain
ZWOgain_label = ctk.CTkLabel(settings_frame,
                            text="Gain:", font=("Helvetica", 30), text_color="white",
                            fg_color="black",  bg_color="#091421",
                            corner_radius=10)
ZWOgain_label.pack(anchor="nw", expand=1)
ZWOgain_label.place(x=50, y=165)

ZWOgain_text = ctk.CTkTextbox(settings_frame,
                                font=("Helvetica", 20),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False" )
ZWOgain_text.pack(anchor="nw", expand=1)
ZWOgain_text.place(x=330, y=160)

#Set ZWO Exposure Time
ZWOexposure_time_label = ctk.CTkLabel(settings_frame,
                                        text="Exposure Time (s):", font=("Helvetica", 30), text_color="white",
                                        fg_color="black",  bg_color="#091421",
                                        corner_radius=10)
ZWOexposure_time_label.pack(anchor="nw", expand=1)
ZWOexposure_time_label.place(x=50, y=245)

ZWOexposure_time_text = ctk.CTkTextbox(settings_frame,
                                        font=("Helvetica", 20),
                                        fg_color="white", bg_color="black", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
ZWOexposure_time_text.pack(anchor="nw", expand=1)
ZWOexposure_time_text.place(x=330, y=240)

#Set ZWO Temperature
ZWOtemperature_label = ctk.CTkLabel(settings_frame,
                                    text="Temperature (°C):", font=("Helvetica", 30), text_color="white",
                                    fg_color="black",  bg_color="#091421",
                                    corner_radius=10)
ZWOtemperature_label.pack(anchor="nw", expand=1)
ZWOtemperature_label.place(x=50, y=325)

ZWOtemperature_text = ctk.CTkTextbox(settings_frame,
                                    font=("Helvetica", 20),
                                    fg_color="white", bg_color="black", text_color="black",
                                    height=20, width=70,
                                    activate_scrollbars="False")
ZWOtemperature_text.pack(anchor="nw", expand=1)
ZWOtemperature_text.place(x=330, y=320)

#PI Camera Settings
PItitle_label = ctk.CTkLabel(settings_frame,
                            text="GUIDE SETTINGS", font=("Helvetica", 30), text_color="white",
                            fg_color="black",  bg_color="#091421",
                            corner_radius=10)
PItitle_label.pack(anchor="nw", expand=1)
PItitle_label.place(x=450, y=100)

#Set PI Gain
PIgain_label = ctk.CTkLabel(settings_frame,
                            text="Gain:", font=("Helvetica", 30), text_color="white",
                            fg_color="black",  bg_color="#091421",
                            corner_radius=10)
PIgain_label.pack(anchor="nw", expand=1)
PIgain_label.place(x=430, y=165)

PIgain_text = ctk.CTkTextbox(settings_frame,
                                font=("Helvetica", 20),
                                fg_color="white", bg_color="black", text_color="black",
                                height=20, width=70,
                                activate_scrollbars="False")
PIgain_text.pack(anchor="nw", expand=1)
PIgain_text.place(x=720, y=160)

#Set PI Exposure Time
PIexposure_time_label = ctk.CTkLabel(settings_frame,
                                    text="Exposure Time (s):", font=("Helvetica", 30), text_color="white",
                                    fg_color="black",  bg_color="#091421",
                                    corner_radius=10)
PIexposure_time_label.pack(anchor="nw", expand=1)
PIexposure_time_label.place(x=430, y=245)

PIexposure_time_text = ctk.CTkTextbox(settings_frame,
                                        font=("Helvetica", 20),
                                        fg_color="white", bg_color="#091421", text_color="black",
                                        height=20, width=70,
                                        activate_scrollbars="False")
PIexposure_time_text.pack(anchor="nw", expand=1)
PIexposure_time_text.place(x=720, y=240)

ZWOsubmit_button = ctk.CTkButton(settings_frame,
                                text="Submit", font=("Helvetica", 26), text_color="white",
                                command=submitZWOsettings,
                                fg_color="black", bg_color="#091421", hover_color="dark grey",
                                height=30, width=90,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
ZWOsubmit_button.pack(anchor="nw", expand=1)
ZWOsubmit_button.place(x=200, y=410)

PIsubmit_button = ctk.CTkButton(settings_frame,
                                text="Submit", font=("Helvetica", 26), text_color="white",
                                command=submitPIsettings,
                                fg_color="black", bg_color="#091421", hover_color="dark grey",
                                height=30, width=90,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("#504348", "#82646c", "black", "#705559"))
PIsubmit_button.pack(anchor="nw", expand=1)
PIsubmit_button.place(x=540, y=410)

Zcheck_on = ctk.StringVar(value="on")
Zcheck_off = ctk.StringVar(value="off")

PIcheck_on = ctk.StringVar(value="on")
PIcheck_off = ctk.StringVar(value="off")

Mountcheck_on = ctk.StringVar(value="on")
Mountcheck_off = ctk.StringVar(value="off")

#Image Format Settings
image_format = ctk.CTkLabel(settings_frame,
                                    text="IMAGE FORMAT", font=("Helvetica", 30), text_color="white",
                                    fg_color="black",  bg_color="#091421",
                                    corner_radius=10)
image_format.pack(anchor="nw", expand=1)
image_format.place(x=290, y=480)

check_RAW_Z = ctk.CTkCheckBox(settings_frame,
                                text="RAW 16", font=("Helvetica", 24), text_color="white",
                                command=Z_RAW,
                                bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                height= 30, width=120,
                                corner_radius=10,
                                onvalue="on", offvalue="off", variable=Zcheck_on,)
check_RAW_Z.pack()
check_RAW_Z.place(x=180, y=540)

check_RGB_Z = ctk.CTkCheckBox(settings_frame,
                                text="RGB 24", font=("Helvetica", 24), text_color="white",
                                command=Z_RGB,
                                bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                height= 30, width=120,
                                corner_radius=10,
                                onvalue="on", offvalue="off", variable=Zcheck_off)
check_RGB_Z.pack()
check_RGB_Z.place(x=180, y=590)

check_RAW_PI = ctk.CTkCheckBox(settings_frame,
                                text="RAW", font=("Helvetica", 24), text_color="white",
                                command=PI_RAW,
                                bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                height= 30, width=90,
                                corner_radius=10,
                                onvalue="on", offvalue="off", variable=PIcheck_off)
check_RAW_PI.pack()
check_RAW_PI.place(x=550, y=540)

check_RGB_PI = ctk.CTkCheckBox(settings_frame,
                                text="RGB",font=("Helvetica", 24), text_color="white",
                                command=PI_RGB,
                                bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                height= 30, width=90,
                                corner_radius=10,
                                onvalue="on", offvalue="off",variable=PIcheck_on)
check_RGB_PI.pack()
check_RGB_PI.place(x=550, y=590)

#Mount Speed Settings
mount_speed = ctk.CTkLabel(settings_frame,
                                    text="MOUNT SPEED", font=("Helvetica", 30), text_color="white",
                                    fg_color="black",  bg_color="#091421",
                                    corner_radius=10)
mount_speed.pack(anchor="nw", expand=1)
mount_speed.place(x=80, y=655)

check_SLOW_Mount = ctk.CTkCheckBox(settings_frame,
                                    text="7x", font=("Helvetica", 28), text_color="white",
                                    command=Mount_Slow,
                                    bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                    height= 30, width=65,
                                    corner_radius=10,
                                    onvalue="on", offvalue="off",variable=Mountcheck_on)
check_SLOW_Mount.pack()
check_SLOW_Mount.place(x=350, y=660)

check_FAST_Mount = ctk.CTkCheckBox(settings_frame,
                                    text="9x", font=("Helvetica", 28), text_color="white",
                                    command=Mount_Fast,
                                    bg_color="black", fg_color="white", hover_color="white", checkmark_color="black",
                                    height= 30, width=65,
                                    corner_radius=10,
                                    onvalue="on", offvalue="off",variable=Mountcheck_off)
check_FAST_Mount.pack()
check_FAST_Mount.place(x=430, y=660)

close_button1 = ctk.CTkButton(settings_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="#091421", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button1.pack(anchor="nw", expand=1)
close_button1.place(x=760, y=680)
#----- END SETTINGS BUTTONS -----

#----- START LIVE VIEW BUTTONS -----
label_bg = ctk.CTkImage(dark_image=image, size=(75, 30))
Z_cam_label = ctk.CTkLabel(live_view_frame,
                            text="ZWO Cam", font=("Helvetica", 16), text_color="white",
                            image=label_bg)
Z_cam_label.pack()
Z_cam_label.place(x=15, y=200)

Pi_cam_label = ctk.CTkLabel(live_view_frame,
                            text="PI Cam", font=("Helvetica", 16), text_color="white",
                            image=label_bg)
Pi_cam_label.pack()
Pi_cam_label.place(x=15, y=530)

settings = ctk.CTkButton(live_view_frame,
                            text="Settings", font=("Helvetica", 18), text_color="white",
                            command=lambda:settings_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2)
settings.pack(expand=1)
settings.place(x=10, y=10)

live_view = ctk.CTkButton(live_view_frame,
                            text="Live View", font=("Helvetica", 18), text_color="white",
                            command=lambda:live_view_frame.tkraise(),
                            fg_color="black", bg_color="black", hover_color="dark grey",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
live_view.pack(expand=1)
live_view.place(x=106, y=10)

north = ctk.CTkButton(live_view_frame,
                        text="N", font=("Helvetica", 16), text_color="white",
                        command=moveNorth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#6b414c", "#292e3d", "black", "#563243"))
north.pack(anchor="nw", expand=1)
north.place(x=680, y=294)

south = ctk.CTkButton(live_view_frame,
                        text="S", font=("Helvetica", 16), text_color="white",
                        command=moveSouth,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#715b4c", "black", "black", "#5d4458"))
south.pack(anchor="nw", expand=1)
south.place(x=680, y=394)

east = ctk.CTkButton(live_view_frame,
                        text="E", font=("Helvetica", 16), text_color="white",
                        command=moveEast,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#5a3633", "black", "black", "#10070d"))
east.pack(anchor="nw", expand=1)
east.place(x=730, y=344)

west = ctk.CTkButton(live_view_frame,
                        text="W", font=("Helvetica", 16), text_color="white",
                        command=moveWest,
                        fg_color="black", bg_color="black", hover_color="dark grey",
                        height=32, width=32,
                        corner_radius=10,
                        border_color="white", border_width=2, background_corner_colors=("#c9a799", "black", "black", "#b39fa5"))
west.pack(anchor="nw", expand=1)
west.place(x=630, y=344)

start_Z_liveloop = ctk.CTkButton(live_view_frame,
                                text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:startLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_Z_liveloop.pack(anchor="nw", expand=1)
start_Z_liveloop.place(x=610, y=130)

stop_Z_liveloop = ctk.CTkButton(live_view_frame,
                                text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                command=lambda:stopLiveZImage(),
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_Z_liveloop.pack(anchor="nw", expand=1)
stop_Z_liveloop.place(x=610, y=170)

capture_ZWO_image = ctk.CTkButton(live_view_frame,
                                    text="Capture ZWO Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takeZWOPicture(float(ZWOexposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/ZWOCaptures", "ZWO_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_ZWO_image.pack(anchor="nw", expand=1)
capture_ZWO_image.place(x=610, y=210)

start_PI_liveloop = ctk.CTkButton(live_view_frame,
                                    text="Start Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:startLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
start_PI_liveloop.pack(anchor="nw", expand=1)
start_PI_liveloop.place(x=610, y=470)

stop_PI_liveloop = ctk.CTkButton(live_view_frame,
                                    text="Stop Live Loop", font=("Helvetica", 18), text_color="white",
                                    command=lambda:stopLivePIImage(),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
stop_PI_liveloop.pack(anchor="nw", expand=1)
stop_PI_liveloop.place(x=610, y=510)

capture_PI_image = ctk.CTkButton(live_view_frame,
                                    text="Capture PI Image", font=("Helvetica", 18), text_color="white",
                                    command=lambda:takePIPicture(float(PIexposure_time_text.get("1.0", "end-1c")), "/home/starspec/STSC/STSCvenv/UI/PICaptures", "PI_IMAGE_XXX"),
                                    fg_color="black", bg_color="black", hover_color="dark grey",
                                    corner_radius=10,
                                    border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
capture_PI_image.pack(anchor="nw", expand=1)
capture_PI_image.place(x=610, y=550)

phd2_button = ctk.CTkButton(live_view_frame,
                            text="PHD2", font=("Helvetica", 18), text_color="white",
                            command=open_phd2,
                            fg_color="black", bg_color="black", hover_color="dark grey", text_color_disabled="red",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
phd2_button.pack(expand=1)
phd2_button.place(x=582, y=10)

spectrum_analysis_button = ctk.CTkButton(live_view_frame,
                            text="Spectrum Analysis", font=("Helvetica", 18), text_color="white",
                            command=open_analysis,
                            fg_color="black", bg_color="black", hover_color="dark grey", text_color_disabled="red",
                            width=50,
                            anchor="nw",
                            corner_radius=10,
                            border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
spectrum_analysis_button.pack(expand=1)
spectrum_analysis_button.place(x=660, y=10)

close_button2 = ctk.CTkButton(live_view_frame,
                                text="Close", font=("Helvetica", 18), text_color="white",
                                command=close,
                                fg_color="black", bg_color="black", hover_color="dark grey",
                                height=30, width=60,
                                corner_radius=10,
                                border_color="white", border_width=2, background_corner_colors=("black", "black", "black", "black"))
close_button2.pack(anchor="nw", expand=1)
close_button2.place(x=760, y=680)
#----- END LIVE VIEW BUTTONS -----

#Initiate User Interface on Settings
settings_frame.tkraise()

#Run UI
root.mainloop()
