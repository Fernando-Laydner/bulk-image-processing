from PIL import Image
from shutil import copyfile
import os

# Known extensions not supported: exr, pfm, sfw, x3f, fts, hdr, mng, pam, picon, pict, wpg, xcf, xpm, xwd, svg, wbmp,
# cr2, erf, heic, nrw, orf, pef, pes, ref, rw2


# Convert and tries to enhance the image.
def enhance(origin, destiny, formating, optimal, image_quality, keep_original, mode=''):
    # Verify if Image can be openned by PIL. If not, returns 0.
    try:
        process = Image.open(origin)
    except IOError:
        return 0

    if mode in ['RGB', 'RGBA', 'L', 'P', '1', 'LAB', 'CMYK', 'LA', 'YCbCr', 'I', '']:

        # Check image mode in case it needs a change
        right_mode = check_mode(process.mode, formating)
        couldbe_mode = check_mode(mode, formating)

        if couldbe_mode != 0 and couldbe_mode != right_mode:
            print("Chosen mode not supported by extension, choosing an alternative")

        if process.mode != right_mode:
            if process.mode == 'P' or process.mode == 'RGBA':
                process = process.convert("RGBA")

                new_image = Image.new("RGBA", process.size, "WHITE")
                new_image.paste(process, (0, 0), process)
                process = new_image

                if right_mode != 'RGBA':
                    process = process.convert(right_mode)
            else:
                process = process.convert(right_mode)
    elif mode != '':
        print('Mode did not exist')
        return 0

    process.save(destiny, optimize=optimal, quality=image_quality)

    # Get original file's extention for reporting and checking if enhancing was worth it.
    extention = origin.rpartition('.')[2]
    if extention != destiny.rpartition('.')[2]:
        print(origin, "\tConverted from " + extention + " to " + formating + " and enhanced!")
    else:
        check_size(origin, destiny)

    if not keep_original:
        os.remove(origin)
    return 1


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
    elif formating in RGBA:
        return 'RGBA'
    elif formating in P:
        return 'P'
    elif formating in One:
        return '1'
    elif formating in L:
        return 'L'
    elif formating in LAB:
        return 'LAB'
    elif formating in CMYK:
        return 'CMYK'
    elif formating in LA:
        return 'LA'
    elif formating in YCbCr:
        return 'YCbCr'
    elif formating in I:
        return 'I'
    return 0


# Image resizer
def beautifying(origin, width_min, height_min):
    # Verify if Image can be openned by PIL. If not, returns 0.
    try:
        process = Image.open(origin)
    except IOError:
        return 0

    # Get pixel data and image size
    pixdata = process.load()
    width, height = process.size
    width -= 1
    height -= 1

    up, down, left, right = (0, 0), (0, 0), (0, 0), (0, 0)

    # Color of the first pixel
    first = pixdata[0, 0]
    last = pixdata[width, height]

    # up
    for y in range(0, height):
        if up[0] != 0 or up[1] != 0:
            break
        for x in range(0, width):
            if pixdata[x, y] != first:
                up = (x, y)
                break
    # down
    for y in range(height, 0, -1):
        if down[0] != 0 or down[1] != 0:
            break
        for x in range(width, 0, -1):
            if pixdata[x, y] != last:
                down = (x, y)
                break
    # left
    for x in range(0, width):
        if left[0] != 0 or left[1] != 0:
            break
        for y in range(0, height):
            if pixdata[x, y] != first:
                left = (x, y)
                break
    # right
    for x in range(width, 0, -1):
        if right[0] != 0 or right[1] != 0:
            break
        for y in range(height, 0, -1):
            if pixdata[x, y] != last:
                right = (x, y)
                break

    # Get actual proportions of the image disregarding background
    actual_height = down[1] - up[1]
    actual_width = right[0] - left[0]

    # Check if image is centered, crop borders based on a ratio with actual_proportions, resize it if less than desired.
    off_up = up[1]
    off_down = height - down[1]
    off_left = left[0]
    off_right = width - right[0]

    height_border = int(actual_height*0.1)
    width_border = int(actual_width*0.1)

    if off_up > height_border and off_down > height_border:
        up = up[1] - height_border
        down = down[1] + height_border
    else:
        up = 0
        down = height
    if off_left > width_border and off_right > width_border:
        left = left[0] - width_border
        right = right[0] + width_border
    else:
        left = 0
        right = width

    if (up != 0 and down != height) or (left != 0 and right != width):
        process = process.crop((left, up, right, down))
        print(origin + " was cropped!")

    actual_ratio = 1
    if actual_width < width_min or actual_height < height_min:
        ratio_1 = width_min/actual_width
        ratio_2 = height_min/actual_height
        if ratio_1 > ratio_2:
            actual_ratio = ratio_1
        else:
            actual_ratio = ratio_2

    width, height = process.size

    if actual_ratio > 1:
        process = process.resize((int(width*actual_ratio), int(height*actual_ratio)), Image.ANTIALIAS)
        print(origin + " was resized!")
    process.save(origin)
