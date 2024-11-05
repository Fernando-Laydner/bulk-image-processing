import os
from IPU import Images_enhancing as Img
import threading
from queue import Queue

# Idea: A more user-end .exe file with tkinter (Logs, Options), cmd launch option for batch and automated uses.
# Loss mode: enables for continuous compression until file size is at or below desired or minimal image_quality
# is reached.

# Get file location.
address = os.path.abspath(os.getcwd())

# Global variables for easier customizability.
optimal = True
image_quality = 85
extension = 'jpg'
keep_original = False
keep_exif = False
crop_and_resizing = True
mode = 'RGB'
destiny_base = os.path.join(address, 'Ready Images')
os.makedirs(destiny_base, exist_ok=True)
origin_base = address + '\\'
thread_number = 1
# Actual size
size = 1000
pad = 50
size = size - 2 * pad


# Function to process images
def process_image(file):
    # Only doing like this because those are the only files in my current folder that should not be images
    if (file.find('.py') != -1 or file.find('.') == -1 or file.find('.idea') != -1 or file.find('.git') != -1 or
            file.find('.md') != -1):
        return

    # Adjust path to file.
    origin = os.path.join(origin_base, file).lower()
    destiny = Img.correct(os.path.join(destiny_base, file), extension).lower()

    # Try opening files, in case they are not images the return an Error, or if there are any problems saving images.
    try:
        foto = Img.ImageProcessor(origin, destiny)
        foto.process_image(extension, mode, size, size, pad, model=-1)
        foto.save_image(optimal, image_quality, keep_original, keep_exif, choose_smaller=False)
    except IOError or Exception:
        print(origin + "\tError")


# Worker function for threads
def worker():
    while True:
        file = q.get()
        if file is None:
            break
        process_image(file)
        q.task_done()


if __name__ == '__main__':
    # Create a queue and add files to it
    q = Queue()
    for file_in_address in os.listdir(address):
        q.put(file_in_address)

    # Create and start threads
    threads = []
    for i in range(thread_number):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    # Block until all tasks are done
    q.join()

    # Stop workers
    for i in range(thread_number):
        q.put(None)
    for t in threads:
        t.join()
