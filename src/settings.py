"""
Author: Zachary Shaffer
GitHub: @shafferz

This is the settings module for caster.py. Important global variables and other
information used in caster.py will be found here.

Inspired by work done by Tyler Lyle, friend and Pygame consultant. See their
work on GitHub: @lylet-AC.
"""
import os
import encoder

# Greyscale
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
# Default blue scale
BLUE = (65, 47, 219)
FADEDBLUE = (83, 110, 230)
BLUEGREY = (111, 104, 169)

# Important paths
ROOT_DIR = os.path.dirname(__file__) # Root Directory
STATIC_DIR = os.path.join(ROOT_DIR, "static") # Static Directory
USR_DIR = os.path.join(ROOT_DIR, "usr") # User Directory

# Specific paths:
MUSIC_DIR = os.path.join(STATIC_DIR, "audio/music")
FILE_DIR = os.path.join(STATIC_DIR, "file")
FONT_DIR = os.path.join(STATIC_DIR, "font")
IMG_DIR = os.path.join(STATIC_DIR, "img")
DATA_DIR = os.path.join(IMG_DIR, "data")

# TODO: General Game settings
TITLE = "Caster 2D" # Window title
FPS = 30 # 30, 45, or 60
ICON = os.path.join(IMG_DIR, "logo_128.png") # Window Icon
# Potentially deprecated, game default is fullscreen.
WIDTH = 800
HEIGHT = 600


# TODO: Neural-Network settings
DATA_FILENAME = (encoder.string_gen(29) + "d.png")
