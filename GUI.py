from PIL import ImageGrab
import pytesseract
from textblob import TextBlob
from tkinter import *
import re
from subprocess import check_call
import ctypes
from IPU import Images_enhancing as Img
from tkinter import ttk
import os
import tkinter.filedialog
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


def click():
    # Get all the variables
    global optimal
    global keep_original
    global keep_exif
    global crop_and_resizing
    image_quality = image_quality_spinbox.get()
    extention = extention_combobox.get()
    mode = mode_combobox.get()

    remove_bg = True
    black_dots = True

    center = True
    rotate = True
    resize = True

    width = 900
    height = 900
    padding = 50

    # Get the address set and make sure the destiny folder exists, it it doesnt, create it.
    destiny_base = destiny_set
    os.makedirs(destiny_base, exist_ok=True)
    origin_base = origen_set

    # Search directory for image files
    for file in os.listdir(address):
        if file.find('.py') != -1 or file.find('.') == -1:
            continue

        origin = os.path.join(origin_base, file).lower()
        destiny = Img.correct(os.path.join(destiny_base, file), extention).lower()

        # Try opening files, in case they are not images the return an Error, or if there are any problems saving
        # images.
        try:
            foto = Img.ImageProcessor(origin, destiny)

            if remove_bg:
                if foto.image.mode == 'P' and foto.image.has_transparency_data:
                    foto.formatting('png', 'RGBA')
                foto.remove_background()
                foto.formatting("jpg", "RGB")

            if center:
                foto.centralize_image(width, height, resize, rotate)

            if padding:
                foto.pad_image(padding)

            foto.formatting(extention, mode)

            if black_dots:
                foto.np_image[0, 0] = [0, 0, 0]
                foto.np_image[self.height - 1, self.width - 1] = [0, 0, 0]

            foto.save_image(optimal, image_quality, keep_original, keep_exif, False)
        except IOError or Exception:
            print(origin + "\tError")


# Define switch variable Optimal
def switch_optimal():
    global optimal
    # Determine is on or off
    if optimal:
        optimal_switch.config(image=off)
        optimal = False
    else:
        optimal_switch.config(image=on)
        optimal = True


# Define switch variable keep_original
def switch_original():
    global keep_original
    # Determine is on or off
    if keep_original:
        original_switch.config(image=off)
        keep_original = False
    else:
        original_switch.config(image=on)
        keep_original = True


# Define switch variable crop_and_resize
def switch_crop_and_resize():
    global crop_and_resizing
    # Determine is on or off
    if crop_and_resizing:
        crop_and_resize_switch.config(image=off)
        crop_and_resizing = False
    else:
        crop_and_resize_switch.config(image=on)
        crop_and_resizing = True


def set_origen():
    global origen_set
    origen_set = tkinter.filedialog.askdirectory()
    origen_label.config(text=origen_set)


def set_destiny():
    global destiny_set
    destiny_set = tkinter.filedialog.askdirectory()
    destiny_label.config(text=destiny_set)


# Create Window
window = Tk()
window.title("Bulk Image Processing GUI")
window.geometry("750x400")

# Keep track of the buttons state on/off
optimal = True
keep_original = False
crop_and_resizing = True
keep_exif = True

# Get file location.
address = os.path.abspath(os.getcwd())
origen_set = address
destiny_set = address + '\\Ready Images'

# Define Switch Images
on = PhotoImage(file="IPU\\on.png")
off = PhotoImage(file="IPU\\off.png")

# Define Grid
Grid.rowconfigure(window, 0, weight=1)
Grid.rowconfigure(window, 1, weight=1)
Grid.rowconfigure(window, 2)
Grid.rowconfigure(window, 3, weight=1)
Grid.rowconfigure(window, 4, weight=1)
Grid.rowconfigure(window, 5, weight=1)
Grid.rowconfigure(window, 6, weight=1)
Grid.columnconfigure(window, 0, weight=1)
Grid.columnconfigure(window, 1, weight=1)
Grid.columnconfigure(window, 2, weight=1)
Grid.columnconfigure(window, 3, weight=1)

# Optimal
optimal_label = Label(window, text='Optimal')
optimal_label.grid(row=0, column=0, sticky="NSEW")
optimal_switch = Button(window, image=on, bd=0, command=switch_optimal)
optimal_switch.grid(row=1, column=0, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Keep_original
original_label = Label(window, text='Keep Original')
original_label.grid(row=0, column=1, sticky="NSEW")
original_switch = Button(window, image=off, bd=0, command=switch_original)
original_switch.grid(row=1, column=1, sticky="NSEW", pady=(10, 10), padx=(10, 10))


# Crop_and_resize
crop_and_resize_label = Label(window, text='Crop and Resize')
crop_and_resize_label.grid(row=0, column=2, sticky="NSEW")
crop_and_resize_switch = Button(window, image=on, bd=0, command=switch_crop_and_resize)
crop_and_resize_switch.grid(row=1, column=2, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Image_quality
image_quality_label = Label(window, text='Image Quality')
image_quality_label.grid(row=2, column=2, sticky="NSEW")
var = StringVar(window)
var.set("85")
image_quality_spinbox = Spinbox(window, from_=1, to=100, textvariable=var, state="readonly")
image_quality_spinbox.grid(row=3, column=2, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Extention
extention_label = Label(window, text='Extention')
extention_label.grid(row=2, column=0, sticky="NSEW")
extention_combobox = ttk.Combobox(window, state="readonly")
extention_combobox['values'] = ('png', 'jpg')
extention_combobox.current(1)
extention_combobox.grid(row=3, column=0, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Mode
mode_label = Label(window, text='Mode')
mode_label.grid(row=2, column=1, sticky="NSEW")
mode_combobox = ttk.Combobox(window, state="readonly")
mode_combobox['values'] = ('RGB', 'RBGA', 'P', '1', 'L', 'LAB', 'CMYK', 'LA', 'YCbCr', 'I')
mode_combobox.current(0)
mode_combobox.grid(row=3, column=1, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Set directories
origen_label = Label(window, text=origen_set)
origen_label.grid(row=4, column=1, sticky="NSEW")
origen_button = Button(window, command=set_origen, text="Set Origen")
origen_button.grid(row=4, column=0, sticky="NSEW", pady=(10, 10), padx=(10, 10))
destiny_label = Label(window, text=destiny_set)
destiny_label.grid(row=5, column=1, sticky="NSEW")
destiny_button = Button(window, command=set_destiny, text="Set Destination")
destiny_button.grid(row=5, column=0, sticky="NSEW", pady=(10, 10), padx=(10, 10))

# Process Images Button
Process_button = Button(window, command=click, text="Process Images")
Process_button.grid(row=6, column=1, sticky="NSEW", pady=(10, 10), padx=(10, 10))

window.call('wm', 'attributes', '.', '-topmost', '1')

window.mainloop()
