from PIL import Image
from shutil import copyfile
import os

#######################################################################################


#######################################################################################


# Convert and tries to enhance the image.
def enhance(origin, destiny, formating, optimal, image_quality):
    # Verify if Image can be openned by PIL. If not, returns 0.
    try:
        process = Image.open(origin)
    except IOError:
        return 0

    # Check image mode in case it needs a change
    right_mode = check_mode(process.mode, formating)
    if process.mode != right_mode:
        if process.mode == 'P':
            process = process.convert("RGBA")
            process2 = Image.new('RGBA', process.size, (255, 255, 255))
            process = Image.alpha_composite(process2, process)
            if right_mode != 'RGBA':
                process = process.convert(right_mode)
        else:
            process = process.convert(right_mode)

    process.save(destiny, optimize=optimal, quality=image_quality)

    # Get original file's extention for reporting and checking if enhancing was worth it.
    extention = origin.rpartition('.')[2]
    if extention != destiny.rpartition('.')[2]:
        print(origin, "\tConverted from " + extention + " to " + formating + " and enhanced!")
        return 1
    else:
        check_size(origin, destiny)
        return 2


# Set proper extention to the end result.
def correct(string, extention):
    return string.rpartition('.')[0] + '.' + extention


# Check if compression was worth it.
def check_size(origin, destiny):
    if os.stat(origin).st_size < os.stat(destiny).st_size:
        os.remove(destiny)
        copyfile(origin, destiny)
        print(origin, "\tOriginal file had better compression settings!")
    else:
        print(origin, "\tWas enhanced!")


# Check image mode to see if conversion is needed
def check_mode(mode, formating):
    formating = formating.upper()
    if mode == '1':
        mode = 'One'
    # Lists of extentions allowed by each mode.
    RGB = ['JFIF', 'JP2', 'WEBP', 'SGI', 'ICO', 'JPE', 'PCX', 'PGM', 'PNG', 'PNM', 'PPM', 'TGA', 'TIFF', 'GIF',
           'JPEG', 'JPG', 'PBM']
    RGBA = ['JP2', 'WEBP', 'SGI', 'ICO', 'PGM', 'PNG', 'PNM', 'PPM', 'TGA', 'TIFF', 'GIF', 'PBM']
    P = ['WEBP', 'ICO', 'PCX', 'PNG', 'TGA', 'TIFF']
    One = ['JFIF', 'WEBP', 'ICO', 'JPE', 'PCX', 'PGM', 'PNG', 'PNM', 'PPM', 'TGA', 'TIFF', 'GIF', 'JPEG', 'JPG',
           'PBM', 'XBM']
    L = ['JFIF', 'JP2', 'WEBP', 'SGI', 'ICO', 'JPE', 'PCX', 'PGM', 'PNG', 'PNM', 'PPM', 'TGA', 'TIFF', 'GIF',
         'JPEG', 'JPG', 'PBM']
    LAB = []
    CMYK = ['JFIF', 'WEBP', 'JPE', 'TIFF', 'JPEG', 'JPG']
    LA = ['JP2', 'WEBP', 'ICO', 'PNG', 'TGA', 'TIFF', 'GIF']
    YCbCr = ['JFIF', 'JP2', 'WEBP', 'JPE', 'TIFF', 'JPEG', 'JPG']
    I = ['WEBP', 'ICO', 'PGM', 'PNG', 'PNM', 'PPM', 'TIFF', 'GIF', 'PBM']

    # Check if format is compatible with current image mode.
    if formating in locals()[mode]:
        if mode == 'One':
            mode = '1'
        return mode

    # Follows a hierarchy to find easier mode (in the future this could be an option).
    if formating in RGB:
        return 'RGB'
    if formating in RGBA:
        return 'RGBA'
    if formating in P:
        return 'P'
    if formating in One:
        return '1'
    if formating in L:
        return 'L'
    if formating in LAB:
        return 'LAB'
    if formating in CMYK:
        return 'CMYK'
    if formating in LA:
        return 'LA'
    if formating in YCbCr:
        return 'YCbCr'
    if formating in I:
        return 'I'
    return 0
