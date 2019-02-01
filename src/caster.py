"""
Author: Zachary Shaffer
GitHub: @shafferz

This is the main game source code for the Caster 2D project while in
development. The following project is the implementation portion of my Senior
Thesis at Allegheny College.

Special thanks to Tyler Lyle (@lylet-AC on GitHub) for helping me re-format my
game source code in a more Pythonic way. Without their expertise in pygame, this
project could have been much more unweildy.
"""
import pygame as pg
from settings import *

# The Game class
class Game:
    def __init__(self):
        pg.init()
        # Set up screen with title and logo
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pygame.display.set_icon(pg.image.load(ICON))
        pygame.display.set_caption(TITLE)
        # Initialize clock
        self.clock = pg.time.Clock()
        # Load background
        self.bg_img = pg.image.load(os.path.join(IMG_DIR), "background_1920x1080.png")
        # Load a cursor
        pg.mouse.set_cursor(*pg.cursors.broken_x)
        # Load font
        self.game_font = pg.freetype.Font(os.path.join(FONT_DIR, "upheavtt.ttf")

    def events(self):
        # Capture key pressed
        key_press = pg.key.get_pressed()

        for event in pg.event.get():
            if event == pg.QUIT:
                self.quit()

# Running the game
g = Game()
