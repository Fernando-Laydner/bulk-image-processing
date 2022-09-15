# bulk-image-processing
Python Pillow based image processing for products

Simples to use bulk image processing made in python by user: @Fernando-Laydner

Part of the code was found on the internet and some I wrote myself.

Intended use was to process images for ecommerce purposes.

How to use:
*******************************************************************************************************
The program should work out of the box if you have the module Pillow installed already: pip install Pillow
*******************************************************************************************************

I recommend using the whole program in a same folder, and moving the pictures inside the folder for processing. 
There is a settings part on the top of the main.py file. In there you may change the input (origins) and the output (destiny) folders as well as the desired extension for the output and a few other saving options requested by  the module Pillow.

Feel free to give ideas on how to improve and make the code better to understand and to use. 
A more user-end program is something I have in mind but I find myself with little time and too much testing is needed to refine images conversion, to a more broad use of the program. 
I have tried using as little as possible modules and there are no ghostscripts, even tho PIL might provide more formats I found it too much work for a more user-end approach and decided to keep it more simples. The only not native modules that are required being installed is PIL, Numpy, Shutil and OpenCV2.

Now a lot of the stuff should work, code should be cleaner and added a few more functions to play a bit with background removal.
