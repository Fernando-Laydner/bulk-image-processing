import os
from IPU import Images_enhancing as Img

# Idea: A more user-end .exe file with tkinter (Logs, Options), cmd launch option for batch and automated uses.

# Get file location.
address = os.path.abspath(os.getcwd())

# Global variables for easier customizability.
optimal = True
image_quality = 90
extention = 'jpg'
keep_original = True
destinys = address + '\\Ready Images\\'
origins = address + '\\'

# Search directory for image files
for file_in_address in os.listdir(address):
    if file_in_address.find('.py') != -1 or file_in_address.find('.') == -1:
        continue

    # Adjust path to file.
    origin = origins + file_in_address
    destiny = destinys + file_in_address

    # Set destiny of the file with proper format.
    destiny = Img.correct(destiny, extention)

    # Set entire file location to lowercase, to avoid having to deal with uppercase letters in the extension.
    origin = origin.lower()

    # Try opening files, in case they are not images the return an Error, or if there are any problems saving images.
    try:
        if Img.enhance(origin, destiny, extention, optimal, image_quality) != 0 and not keep_original:
            os.remove(origin)
    except:
        print(origin + "\tError")
