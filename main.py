import os
from IPU import Images_enhancing as Img

# Idea: A more user-end .exe file with tkinter (Logs, Options), cmd launch option for batch and automated uses.
# Loss mode: enables for continious compression until file size is at or below desired or mininal image_quality
# is reached.


# Get file location.
address = os.path.abspath(os.getcwd())

# Global variables for easier customizability.
optimal = True
image_quality = 85
extention = 'jpg'
keep_original = False
keep_exif = True
crop_and_resizing = True
mode = 'RGB'
destiny_base = address + '\\Ready Images\\'
os.makedirs(destiny_base, exist_ok=True)
origin_base = address + '\\'

# Search directory for image files
for file_in_address in os.listdir(address):
    if file_in_address.find('.py') != -1 or file_in_address.find('.') == -1 or file_in_address.find('.idea') != -1:
        continue

    # Adjust path to file.
    origin = origin_base + file_in_address
    destiny = destiny_base + file_in_address

    # Set destiny of the file with proper format.
    destiny = Img.correct(destiny, extention).lower()

    # Set entire file location to lowercase, to avoid having to deal with uppercase letters in the extension.
    origin = origin.lower()

    # Try opening files, in case they are not images the return an Error, or if there are any problems saving images.
    try:
        # Img.denoiser(origin)
        Img.enhance(origin, destiny, extention, optimal, image_quality, keep_original, mode, keep_exif)
        if crop_and_resizing:
            Img.crop_and_resize(destiny, 1000, 1000, 0.2, True)
    except IOError or Exception:
        print(origin + "\tError")
