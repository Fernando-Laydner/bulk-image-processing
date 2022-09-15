from PIL import Image, ImageFilter
import cv2
from shutil import copyfile
import os
import numpy as np

# Known extensions not supported: exr, pfm, sfw, x3f, fts, hdr, mng, pam, picon, pict, wpg, xcf, xpm, xwd, svg, wbmp,
# cr2, erf, heic, nrw, orf, pef, pes, ref, rw2


# Convert and tries to enhance the image.
def enhance(origin, destiny, formating, optimal, image_quality, keep_original, mode='', keep_exif=False):
    # Opens the image.
    process = Image.open(origin)

    # Check if image metadata is needed.
    if keep_exif:
        process.load()
        exif = process.getexif()
    else:
        exif = None

    # Check if mode that was passed exists
    if mode not in ['RGB', 'RGBA', 'L', 'P', '1', 'LAB', 'CMYK', 'LA', 'YCbCr', 'I', '']:
        raise Exception("Sorry, mode did not exist")

    # Check image mode in case it needs a change.
    best_mode = check_mode(process.mode, formating)
    couldbe_mode = check_mode(mode, formating)
    if couldbe_mode != 0:
        if couldbe_mode != best_mode:
            best_mode = couldbe_mode

    # Probably more changes will be necessary here.
    if process.mode != best_mode:
        if process.mode == 'P':
            process = process.convert("RGBA")

        if best_mode != 'RGBA' and process.mode == 'RGBA':
            new_image = Image.new("RGBA", process.size, "WHITE")
            new_image.paste(process, (0, 0), process)
            process = new_image

        process = process.convert(best_mode)

    # Save image.
    if keep_exif:
        process.save(destiny, optimize=optimal, quality=image_quality, exif=exif)
    else:
        process.save(destiny, optimize=optimal, quality=image_quality)
    process.close()

    # Get original file's extention for reporting and checking if enhancing was worth it.
    if origin.split('.')[-1] != destiny.split('.')[-1]:
        print(origin, "\tConverted from " + extention + " to " + formating + " and enhanced!")
    else:
        if os.stat(origin).st_size < os.stat(destiny).st_size:
            os.remove(destiny)
            copyfile(origin, destiny)
            print(origin, "\tOriginal file had better compression settings!")
        else:
            print(origin, "\tWas enhanced!")

    # Deletes original image
    if not keep_original:
        os.remove(origin)


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # If both the width and height are None, then return the original image
    if width is None and height is None:
        return image

    # Initialize the dimensions of the image to be resized and grab the image size
    h, w = image.shape[:2]

    # Calculate the ratio of the width and construct the dimensions
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    # Resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # Return the resized image
    return resized


# Crop and resizes image
def crop_and_resize(destiny, width_min, height_min, border_ratio):
    # Opens the file
    img = cv_open_image(destiny)

    # Convert the into gray scale
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Get the height and width of the image.
    h, w = img.shape[:2]

    # Invert the image to be white on black for compatibility with findContours function.
    imgray = 255 - img

    # Binarize the image and call it thresh.
    ret, thresh = cv2.threshold(imgray, 10, 255, cv2.THRESH_BINARY)

    # Find all the contours in thresh. In your case the 3 and the additional strike
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Calculate bounding rectangles for each contour.
    rects = [cv2.boundingRect(cnt) for cnt in contours]

    # Calculate the combined bounding rectangle points.
    top_x = min([x for (x, y, w, h) in rects])
    top_y = min([y for (x, y, w, h) in rects])
    bottom_x = max([x + w for (x, y, w, h) in rects])
    bottom_y = max([y + h for (x, y, w, h) in rects])

    # Get image actual proportions
    height_actual, width_actual = bottom_y - top_y, bottom_x - top_x

    # Defines what the border could be
    height_border = int(height_actual * border_ratio)
    width_border = int(width_actual * border_ratio)

    # Defines what the border will be
    if height_border > width_border:
        border = height_border
    else:
        border = width_border

    # Check if image needs to be cropped
    if top_x > 10 and top_y > 10 and w - bottom_x > 10 and h - bottom_y > 10:
        # Crop image
        cropped_image = img[top_y:bottom_y, top_x:bottom_x]

        # Adds the border to the image size
        top_y -= border
        bottom_y += border
        top_x -= border
        bottom_x += border

        # Make image sharper if it was too small
        sharpen = False
        if sharpen:
            if height_cropped < height_min/2 or width_cropped < width_min/2:
                sharp = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
                cropped_image = cv2.filter2D(cropped_image, -1, sharp)

                cropped_image = cv2.bilateralFilter(cropped_image, 6, 21, 7)
                cropped_image = cv2.GaussianBlur(cropped_image, (5, 5), 1)

                print(destiny + " Tried to sharpen and blur image because it was too small, "
                                "check if it is properly done")

        # Creates blank image
        img = np.zeros((bottom_y - top_y, bottom_x - top_x), np.uint8)
        img = (255 - img)

        # Get the cropped image into the blank image
        img[border:height_cropped + border, border:width_cropped + border] = cropped_image

        # Message
        print(destiny + " Image was cropped successfully")

    # Check if the image needs to resized
    if height_actual < height_min or width_actual < width_min:
        if height_min > width_min:
            min_size = height_min + 2*border
        else:
            min_size = width_min + 2 * border
        img = image_resize(img, min_size)
        print(destiny + " Image was resized to: " + str(min_size))

    # Save it
    cv_save_image(destiny, img)


# Removes pixels inside the trashhold of a gray scale
def background_off(src, background_threshold_start=250, background_threshold_finish=255):
    # load image
    img = cv_open_image(src)

    # convert to graky
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # threshold input image as mask
    mask = cv2.threshold(gray, background_threshold_start, background_threshold_finish, cv2.THRESH_BINARY)[1]

    # negate mask
    mask = 255 - mask

    # apply morphology to remove isolated extraneous noise
    # use borderconstant of black since foreground touches the edges
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # anti-alias the mask -- blur then stretch
    # blur alpha channel
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=2, sigmaY=2, borderType=cv2.BORDER_DEFAULT)

    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2 * (mask.astype(np.float32)) - 255.0).clip(0, 255).astype(np.uint8)

    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask

    # save resulting masked image
    cv_save_image(src, result)


# Set proper extention to the end result.
def correct(string, extention):
    return string.rpartition('.')[0] + '.' + extention


# Open image to CV because it doesnt like to work
def cv_open_image(path):
    process = Image.open(path)
    img = np.array(process, np.uint8)
    return img[:, :, ::-1].copy()


# Save image to CV because it doesnt like to work
def cv_save_image(path, img):
    im_pil = Image.fromarray(img)
    im_pil.save(path)


# Check image mode to see if conversion is needed.
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
