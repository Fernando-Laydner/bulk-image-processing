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
mode = 'RGB'
destinys = address + '\\Ready Images\\'
os.makedirs(destinys, exist_ok=True)
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
        Img.enhance(origin, destiny, extention, optimal, image_quality, keep_original, mode)
        Img.beautifying(destiny, 500, 500)
    except:
        print(origin + "\tError")
