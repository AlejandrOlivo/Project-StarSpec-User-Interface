import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from tkinter_webcam import webcam
import customtkinter as ctk
from PIL import ImageTk, Image
import cv2
import webview

#system appearance
ctk.set_appearance_mode("System")

#frame
root = ctk.CTk()
root.minsize(420, 360)
root.maxsize(840, 720)
root.geometry("840x720+440+55")
root.title("StarSpec UI")

#define background
image = Image.open("Space_Image.jpg")
bg = ImageTk.PhotoImage(image)

#create 1st frame (main controls)
frame1 = ctk.CTkFrame(root)
frame1.pack(fill="both", expand=1)
bg_image1 = ctk.CTkLabel(frame1, image=bg, text="")
bg_image1.pack(expand=1)
bg_image1.place(x=0, y=0)

#create 2nd frame (mount controls/live view)
frame2 = ctk.CTkFrame(root)
frame2.pack(fill="both", expand=1)
frame2.place(x=0, y=0)

webcam = webcam.Box(frame2, width=1100, height=900)
webcam.show_frames()

# bg_image2 = ctk.CTkLabel(frame2, image=bg, text="")
# bg_image2.pack(expand=1)


#buttons that will switch between pages
switch1 = ctk.CTkButton(frame1,
                        text="Mount Control", font=("Helvetica", 18), text_color="white",
                        command=lambda:frame2.tkraise(),
                        fg_color="black", bg_color="transparent", hover_color="dark grey",
                        width=50,
                        anchor="nw")
switch1.pack(expand=1)
switch1.place(x=10, y=10)

switch2 = ctk.CTkButton(frame2,
                        text="Main Control", font=("Helvetica", 18), text_color="white",
                        command=lambda:frame1.tkraise(),
                        fg_color="black", bg_color="transparent", hover_color="dark grey",
                        width=50,
                        anchor="nw")
switch2.pack(expand=1)
switch2.place(x=10, y=10)

#zoom in and out buttons
# def zoomIn():
#     print("in")
# def zoomOut():
#     print("out")

# zoomIn_image = ImageTk.PhotoImage(Image.open("Zoom-In.png").resize((30, 30)))
# zoomOut_image = ImageTk.PhotoImage(Image.open("Zoom-Out.png").resize((30, 30)))

# zoomIn_button = ctk.CTkButton(frame1, image=zoomIn_image,
#                 text="",
#                 command=zoomIn,
#                 height=30, width=30)
# zoomIn_button.pack(anchor="nw", expand=1)
# zoomIn_button.place(x=500, y=10)

# zoomOut_button = ctk.CTkButton(frame1, image=zoomOut_image,
#                 text="",
#                 command=zoomOut,
#                 height=30, width=30)
# zoomOut_button.pack(anchor="nw", expand=1)
# zoomOut_button.place(x=645, y=50)

#gain

#exposure time feature
exposure_time = ctk.CTkEntry(frame1,
                            font=("Helvetica", 18),
                            corner_radius=10,
                            width=65,
                            bg_color="transparent")
exposure_time.pack(padx=10, expand=1, anchor="w")
exposure_time.place(x=135, y=60)

exposure_time_label1 = ctk.CTkLabel(frame1,
                                    text="Exposure Time:",
                                    font=("Helvetica", 18),
                                    bg_color="transparent")
exposure_time_label1.pack(padx=5, pady=5,expand=1, anchor="w")
exposure_time_label1.place(x=10, y=60,)

exposure_time_label2 = ctk.CTkLabel(frame1,
                                    text="ms",
                                    font=("Helvetica", 18),
                                    bg_color="transparent")
exposure_time_label2.pack(padx=5, pady=5,expand=1, anchor="w")
exposure_time_label2.place(x=205, y=60)

#temperature feature
temperature = ctk.CTkEntry(frame1,
                            font=("Helvetica", 18),
                            corner_radius=10,
                            width=55)
temperature.pack(padx=10, expand=1, anchor="nw")
temperature.place(x=120, y=100)

temperature_label1 = ctk.CTkLabel(frame1,
                                    text="Temperature:",
                                    font=("Helvetica", 18),
                                    text_color_disabled="red")
temperature_label1.pack(padx=5, pady=5,expand=1)
temperature_label1.place(x=10, y=100)

temperature_label2 = ctk.CTkLabel(frame1, text="°C",
                                    font=("Helvetica", 18))
temperature_label2.pack(padx=5, pady=5,expand=1)
temperature_label2.place(x=177, y=100)


test_label1 = ctk.CTkLabel(frame1, text="", font=("Calibri", 14))
test_label1.pack()
test_label1.place(x=30, y=200)
test_label2 = ctk.CTkLabel(frame1, text="", font=("Calibri", 14))
test_label2.pack()
test_label2.place(x=30, y=220)

time=0
temp=0

#submit button
def submit():
    if exposure_time.get() == "":
        print("No exposure time was set.")
    else:
        test_label1.configure(text=f"Exposure time is set at {exposure_time.get()} ms")
        print(f"Exposure time is {exposure_time.get()} ms")
    if temperature.get() == "":
        print("No temperature was set.")
    else:
        test_label2.configure(text=f"Temperature is set at {temperature.get()} °C")
        print(f"Temperature is {temperature.get()} °C")
    # if len(exposure_time.get()) == 0:
    #     time = int(exposure_time.get())
    #     print(time)
    #     #exposure_time.get() == 0
    # if len(temperature.get()) == 0:
    #     temperature.get() == 0
    #     print(temperature.get())
    #     print("no temp receiveed")

submit = ctk.CTkButton(frame1,
                text="Submit", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=submit,
                height=30, width=50)
submit.pack(padx=10, pady=10, anchor="nw", expand=1)
submit.place(x=60, y=140)


#gain feature

#mount control feature
def moveNorth():
    print("Mount moved north")
def moveSouth():
    print("Mount moved south")
def moveWest():
    print("Mount moved west")
def moveEast():
    print("Mount moved east")

north = ctk.CTkButton(frame2,
                text="N", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=moveNorth,
                height=40, width=40)
north.pack(padx=10, pady=10, anchor="nw", expand=1)
north.place(x=700, y=80)

south = ctk.CTkButton(frame2,
                text="S", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=moveSouth,
                height=40, width=40)
south.pack(padx=10, pady=10, anchor="nw", expand=1)
south.place(x=700, y=180)

west = ctk.CTkButton(frame2,
                text="W", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=moveWest,
                height=40, width=40)
west.pack(padx=10, pady=10, anchor="nw", expand=1)
west.place(x=650, y=130)

east = ctk.CTkButton(frame2,
                text="E", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=moveEast,
                height=40, width=40)
east.pack(padx=10, pady=10, anchor="nw", expand=1)
east.place(x=750, y=130)

#image saving feature
def saveImage():
    print("Image saved")

save_image = ctk.CTkButton(frame2,
                text="Save Image", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=saveImage,
                height=30, width=80,
                anchor="ne")
save_image.pack(padx=10, pady=10, anchor="nw", expand=1)
save_image.place(x=720, y=10)

#live view feature
def liveView():
    print("Currently viewing the live feed")

live_view = ctk.CTkButton(frame2,
                text="Live View", font=("Helvetica", 18), text_color="white",
                fg_color="black", bg_color="transparent", hover_color="dark grey",
                command=liveView,
                height=30, width=80,
                anchor="ne")
live_view.pack(padx=10, pady=10, anchor="nw", expand=1)
live_view.place(x=620, y=10)

# def function(choice):
#     if choice == "Function 1":

#         print("Function 1 was selected")
#     elif choice == "Function 2":
#         print("Function 2 was selected")
#     elif choice == "Function 3":
#         print("Function 3 was selected")
#     elif choice == "Function 4":
#         print("Function 4 was selected")

# #dropdown menu 
# options = ["Function 1", "Function 2", "Function 3", "Function 4"]

# #dropdown menu
# dropMenu = ctk.CTkOptionMenu(frame2, values=options, command=function,
#                             anchor="nw",
#                             width=100, height=25,
#                             corner_radius=10,
#                             button_color="white",
#                             text_color="black", font=("Helvetica", 14), fg_color="white",
#                             dropdown_fg_color="white", dropdown_hover_color="light grey", dropdown_font=("Helvetica", 14))
# dropMenu.pack(padx=10, pady=10, expand=1, anchor="nw")

# def enter_pressed(event):
#     search.get()
#     print(search.get)

# #search bar
# search = ctk.CTkEntry(frame1, placeholder_text="Search...",
#                     font=("Helvetica", 14),
#                     corner_radius=10)
# search.pack(padx=150, pady=30, expand=1, anchor="nw")

#open a website
# webview.create_window("Stellarium", "https://spacetelescopelive.org/webb?obsId=01HZ086YP1Z8AY11WPCA54C349") 
# webview.start()



#Title
# title = ctk.CTkLabel(root, text = "Project StarSpec", font = ("Times New Roman", 40), fg_color = "#000000", bg_color= "#FFFFFF")
# title.grid(row = 0, column = 0,
#             padx = 250, pady = 5,
#             sticky = "ew")
# # title_frame = Frame(root, bg = "#000000")

# #Search Bar
# text = tkinter.StringVar()
# search = ctk.CTkEntry(root, width = 150, height = 15, placeholder_text = "Search", textvariable = text)
# search.grid(row = 0, column = 10,
#             padx = 575,
#             sticky = "ew")

frame1.tkraise()
#Run app
root.mainloop()