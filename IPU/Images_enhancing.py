import os
import cv2
import numpy as np
from shutil import copyfile
from PIL import Image
from rembg import remove, new_session

# Known extensions not supported: exr, pfm, sfw, x3f, fts, hdr, mng, pam, picon, pict, wpg, xcf, xpm, xwd, svg, wbmp,
# cr2, erf, heic, nrw, orf, pef, pes, ref, rw2


# Set proper extension to the end result.
def correct(string, extension):
    return string.rpartition('.')[0] + '.' + extension


# Check image mode to see if conversion is needed.
def check_mode(mode, formating):
    formating = formating.upper()
    if mode == '1':
        mode = 'One'
    # Lists of extensions allowed by each mode.
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


class ImageProcessor:
    model = 0
    image = None
    np_image = None
    gray = None
    original_image = None
    height, width = None, None
    true_height, true_width = None, None
    image_path = None
    destiny = None
    debug = False

    def __init__(self, image_path, destiny):
        self.image_path = image_path
        self.destiny = destiny
        self.open_image()
        self.exif = self.image.getexif()
        if self.np_image is None:
            raise ValueError("Image not found or unable to open")

        self.original_image = self.np_image.copy()
        self.height, self.width = self.np_image.shape[:2]

    # Open image to CV because it doesn't like to work
    def open_image(self):
        self.image = Image.open(self.image_path)
        self.update_np_image()

    def update_np_image(self):
        self.image.load()
        self.np_image = np.array(self.image, np.uint8).copy()

    def print_and_debug(self, where):
        if self.debug:
            from matplotlib import pyplot as plt
            plt.imshow(self.np_image, interpolation='nearest')
            plt.title(where)
            plt.show()

    def formatting(self, formating, mode=''):
        # Check if mode that was passed exists
        if mode not in ['RGB', 'RGBA', 'L', 'P', '1', 'LAB', 'CMYK', 'LA', 'YCbCr', 'I', '']:
            raise Exception("Sorry, mode did not exist")

        # Check image mode in case it needs a change.
        best_mode = check_mode(self.image.mode, formating)
        couldbe_mode = check_mode(mode, formating)
        if couldbe_mode != 0:
            if couldbe_mode != best_mode:
                best_mode = couldbe_mode

        # Probably more changes will be necessary here.
        if self.image.mode != best_mode:
            if self.image.mode == 'P':
                self.image = self.image.convert("RGBA")

            if best_mode != 'RGBA' and self.image.mode == 'RGBA':
                new_image = Image.new("RGBA", self.image.size, "WHITE")
                new_image.paste(self.image, (0, 0), self.image)
                self.image = new_image

            self.image = self.image.convert(best_mode)
            self.update_np_image()

    def image_resize_exact(self, width, height, inter=cv2.INTER_AREA):
        aspect_ratio = self.true_width / self.true_height
        if width / height > aspect_ratio:
            new_width = int(height * aspect_ratio)
            new_height = height
        else:
            new_width = width
            new_height = int(width / aspect_ratio)
        self.np_image = cv2.resize(self.np_image, (new_width, new_height), interpolation=inter)
        self.height, self.width = self.np_image.shape[:2]

    def pad_image(self, border_ratio):
        self.np_image = cv2.copyMakeBorder(self.np_image, border_ratio, border_ratio, border_ratio, border_ratio,
                                           cv2.BORDER_CONSTANT, value=[255, 255, 255])
        self.height, self.width = self.np_image.shape[:2]
        self.print_and_debug("Padding added")

    def centralize_image(self, width, height, resize=True, rotate=True):
        if self.gray is None:
            self.gray = cv2.cvtColor(self.np_image, cv2.COLOR_BGR2GRAY)
        rows = np.any(self.gray < 255, axis=1)
        cols = np.any(self.gray < 255, axis=0)

        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]

        # Crop the image to these bounds
        self.np_image = self.np_image[y_min:y_max + 1, x_min:x_max + 1]
        self.true_height, self.true_width = self.np_image.shape[:2]

        # Rotate if necessary
        if rotate:
            if self.true_height < self.true_width / 2:
                self.rotate_image(45)
                self.print_and_debug("Rotated")

        # Resize if necessary
        if resize:
            h, w, _ = self.np_image.shape
            if w != width or h != height:
                self.image_resize_exact(width, height)
                self.print_and_debug("Resized")

        # Create a centered image
        h, w, _ = self.np_image.shape
        centered_image = np.zeros((height, width, 3), np.uint8)
        centered_image.fill(255)

        top_left_y = (height - h) // 2
        top_left_x = (width - w) // 2
        centered_image[top_left_y:top_left_y + h, top_left_x:top_left_x + w] = self.np_image
        self.np_image = centered_image
        self.height, self.width = self.np_image.shape[:2]
        self.print_and_debug("Centered")

    def rotate_image(self, angle):
        height, width = self.np_image.shape[:2]
        center = (width // 2, height // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        M[0, 2] += (new_width / 2) - center[0]
        M[1, 2] += (new_height / 2) - center[1]
        self.np_image = cv2.warpAffine(self.np_image, M, (new_width, new_height), borderMode=cv2.BORDER_CONSTANT,
                                       borderValue=(255, 255, 255))
        self.height, self.width = self.np_image.shape[:2]
        self.true_height, self.true_width = self.np_image.shape[:2]

    def remove_background(self):
        modelos = ["birefnet-general-lite", "silueta"]  # A lot faster the second option, but not as good...
        my_session = new_session(modelos[self.model])
        print("Removing Background, may take a few seconds...")
        self.image = remove(self.image, session=my_session)
        self.update_np_image()
        self.print_and_debug("Background Removed")

    def save_image(self, optimal, image_quality, keep_original=True, keep_exif=False, choose_smaller=True):
        self.image = Image.fromarray(self.np_image)

        # Save image.
        if keep_exif:
            self.image.save(self.destiny, optimize=optimal, quality=image_quality, exif=self.exif)
        else:
            self.image.save(self.destiny, optimize=optimal, quality=image_quality)
        self.image.close()

        # Get original file's extension for reporting and checking if enhancing was worth it.
        if self.image_path.split('.')[-1] != self.destiny.split('.')[-1]:
            print(self.image_path, "\tConverted from " +
                  self.image_path.split('.')[-1] + " to " + self.destiny.split('.')[-1] + " and enhanced!")
        else:
            if choose_smaller and os.stat(self.image_path).st_size < os.stat(self.destiny).st_size:
                os.remove(self.destiny)
                copyfile(self.image_path, self.destiny)
                print(self.image_path, "\tOriginal file had better compression settings!")
            else:
                print(self.image_path, "\tWas enhanced!")

        if not keep_original:
            self.delete_original()

    def delete_original(self):
        os.remove(self.image_path)

    def process_image(self, width, height, border_ratio, black_dots=False):
        if self.image.mode == 'P' and self.image.has_transparency_data:
            self.formatting('png', 'RGBA')
        self.remove_background()
        self.formatting("jpg", "RGB")
        self.centralize_image(width, height)
        self.pad_image(border_ratio)

        if black_dots:
            self.np_image[0, 0] = [0, 0, 0]
            self.np_image[self.height - 1, self.width - 1] = [0, 0, 0]
