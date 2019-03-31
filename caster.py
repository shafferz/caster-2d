"""
Author: Zachary Shaffer
GitHub: @shafferz

This is the main game source code for the Caster 2D project while in
development. The following project is the implementation portion of my Senior
Thesis at Allegheny College.

Special thanks to Tyler Lyle (@lylet-AC on GitHub) and GitHub user iKlsR for
helping me re-format my game source code in a more Pythonic way. Without their
expertises in pygame, this project could have been much more unweildy.
"""
import pygame as pg
import os, sys

from settings import *
from pygame import freetype
from src.util import *

class Core(object):
    def __init__(self):
        pg.init()
        # Display game in fullscreen
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        # Set game caption and game icon
        pg.display.set_caption(TITLE)
        pg.display.set_icon(pg.image.load(ICON))
        # Create game clock
        self.clock = pg.time.Clock()
        # Load background and give it a rectangle
        self.bg_img = pg.image.load("src/static/img/background_800x600.png")
        self.bg_rect = self.bg_img.get_rect()
        # Load custom Font
        self.game_font = pg.freetype.Font(os.path.join(FONT_DIR, "upheavtt.ttf"))
        # Set custom cursor
        pg.mouse.set_cursor(*pg.cursors.broken_x)
        # Generate a list of songs from a text file
        self.song_list = []
        self.song_list_head = 0;
        with open(os.path.join(FILE_DIR, "music_list.txt")) as music_file:
            self.song_list = [line.rstrip('\n') for line in music_file]
        # Variables for volume and playback control
        self.mute = False
        self.volume = 1.0
        # Play songs from song list
        pg.mixer.music.set_volume(self.volume)
        pg.mixer.music.load(os.path.join(MUSIC_DIR, self.song_list[self.song_list_head]))
        pg.mixer.music.play()
        pg.mixer.music.set_endevent(pg.USEREVENT + 1) # USEREVENT+1 is a custom event
        # Set game variables
        self.game_state = 0
        self.game_substate = 0
        self.pause = False
        self.canvas = pg.Surface((400,400))
        self.canvas.fill(WHITE)
        self.draw_on = False
        self.last_pos = (0,0)

    def dispatch(self, event):
        # If the game is quit via closing
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        # Handling pressing escape
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            # If the user is in the main menu and uses escape
            if self.game_state == 0:
                # If the substate is 0, meaning base of main menu, exit game
                if self.game_substate == 0:
                    pg.quit()
                    sys.exit()
                # If in any of the submenus of the main menu, return to base
                else:
                    self.game_substate = 0
            elif self.game_state == 1:
                self.canvas.fill(WHITE)
                self.game_state = 0
        # Handling pressing in
        elif event.type == pg.MOUSEBUTTONDOWN:
            if not self.pause:
                # Clicking in the main menu
                if self.game_state == 0:
                    # Base of main menu (Play or Options)
                    if self.game_substate == 0:
                        # If the play rect exists
                        if self.play_rect:
                            # If the click happened over the play button area
                            if self.play_rect.collidepoint(pg.mouse.get_pos()):
                                self.game_substate = 2
                        # If the setting rect exists
                        if self.set_rect:
                            # If the click happened over the settings button area
                            if self.set_rect.collidepoint(pg.mouse.get_pos()):
                                self.game_substate = 1
                    # Play submenu of main menu
                    elif self.game_substate == 2:
                        # If the tutorial rect exists
                        if self.tut_rect:
                            # If the click happened over the tutorial button area
                            if self.tut_rect.collidepoint(pg.mouse.get_pos()):
                                self.game_state = 1
                                self.game_substate = 0
                        # If the multiplayer rect exists
                        if self.multi_rect:
                            # If the click happened over the settings button area
                            if self.multi_rect.collidepoint(pg.mouse.get_pos()):
                                print("Clicked multiplayer")
                elif self.game_state == 1:
                    # Drawing point at coordinates, adjusted for offset of canvas
                    (adj_x, adj_y) = (event.pos[0]-200, event.pos[1]-100)
                    pg.draw.circle(self.canvas, BLACK, (adj_x, adj_y), 10)
                    # Variable to enable continuous drawing
                    self.draw_on = True
        # Handling letting go of mouse button
        elif event.type == pg.MOUSEBUTTONUP:
            self.draw_on = False
        # Handling mouse moving events
        elif event.type == pg.MOUSEMOTION:
            # Adjust coordinates of mouse event for canvas location
            (adj_x, adj_y) = (event.pos[0]-200, event.pos[1]-100)
            # If actively drawing, connect moving points with rounded line
            if self.draw_on:
                pg.draw.circle(self.canvas, BLACK, (adj_x, adj_y), 10)
                GameTools.roundline(self.canvas, BLACK, (adj_x, adj_y), self.last_pos,  10)
            self.last_pos = (adj_x, adj_y)
        # USEREVENT+1 is a custom event for when the music ends
        elif event.type == (pg.USEREVENT + 1):
            # Go to the next song
            self.song_list_head += 1
            # If we are still within our music list, load and play
            if (self.song_list_head < len(self.song_list)):
                pg.mixer.music.load(os.path.join(MUSIC_DIR, self.song_list[self.song_list_head]))
                pg.mixer.music.play()
            # If we go over the end of the music list, wrap to beginning
            else:
                self.song_list_head = 0
                pg.mixer.music.load(os.path.join(MUSIC_DIR, self.song_list[self.song_list_head]))
                pg.mixer.music.play()
        # Handling user pressing the M key, for muting music
        elif event.type == pg.KEYDOWN and event.key == pg.K_m:
            # Set mute bool to true or false depending on new state
            self.mute = not self.mute
            if self.mute:
                # Set volume to 0
                pg.mixer.music.set_volume(0.0)
            else:
                # Set volume to whatever was last set
                pg.mixer.music.set_volume(self.volume)
        # Handling user pressing the P key, for pausing game
        elif event.type == pg.KEYDOWN and event.key == pg.K_p:
            # Set pause bool to true or false depending on new state
            self.pause = not self.pause
            # Load an overlaying graphic for pausing
            pause_bg = pg.image.load("src/static/img/pause_graphic.png")
            options_popup = pg.image.load("src/static/img/options.png")
            if self.pause:
                # Pause music and display graphic
                pg.mixer.music.pause()
                self.screen.blit(pause_bg, self.bg_rect)
                self.screen.blit(options_popup, self.bg_rect)
                # Lock the screen surface to prevent any changes to it
                self.screen.lock()
            else:
                # Unpause music and unlock the screen surface
                pg.mixer.music.unpause()
                self.screen.unlock()
        # Handling user pressing the comma (,) key, for going to previous song
        elif event.type == pg.KEYDOWN and event.key == pg.K_COMMA:
            # Move head of the song list backward
            self.song_list_head -= 1
            # Wrap to end of song list if going backwards over the end of the song list
            if self.song_list_head < 0:
                self.song_list_head = (len(self.song_list))-1
            # Load and play new song
            pg.mixer.music.load(os.path.join(MUSIC_DIR, self.song_list[self.song_list_head]))
            pg.mixer.music.play()
        # Handling user pressing the period (.) key, for going to next song
        elif event.type == pg.KEYDOWN and event.key == pg.K_PERIOD:
            # Move head of the song list forward
            self.song_list_head += 1
            # Wrap to beginning of song list if going over the end of the song list
            if self.song_list_head >= len(self.song_list):
                self.song_list_head = 0
            # Load and play new song
            pg.mixer.music.load(os.path.join(MUSIC_DIR, self.song_list[self.song_list_head]))
            pg.mixer.music.play()
        # Handling user pressing the open bracket ([) key, used to lower volume
        elif event.type == pg.KEYDOWN and event.key == pg.K_LEFTBRACKET:
            # If the volume is greater than 0, decrease volume by 10%
            if self.volume > 0.0:
                self.volume -= 0.1
                pg.mixer.music.set_volume(self.volume)
        # Handling user pressing the close bracket (]) key, used to raise volume
        elif event.type == pg.KEYDOWN and event.key == pg.K_RIGHTBRACKET:
            # If the volume is less than 1, increase volume by 10%
            if self.volume < 1.0:
                self.volume += 0.1
                pg.mixer.music.set_volume(self.volume)
        # Handling user pressing the tab key, used to clear drawing canvas
        elif event.type == pg.KEYDOWN and event.key == pg.K_TAB:
            # If in the game
            if self.game_state == 1:
                self.canvas.fill(WHITE)
        # Handling user pressing the space key, used to submit canvas drawings
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            if self.game_state == 1:
                # Send the canvas to the GameTools from util for prediction
                GameTools.predict(self.canvas)
                self.canvas.fill(WHITE)

    def render_overlay(self):
        song_title = self.song_list[self.song_list_head].rstrip("ggo.")
        song_title = song_title.rstrip("3pm.")
        song_title = song_title.lstrip("static/audio/music/")
        text = song_title
        if not self.mute:
            text += " (press M to mute)"
        else:
            text += " (press M to unmute)"
        self.game_font.render_to(self.screen, (5, 5), text, fgcolor=BLUEGREY, size=30)

    def render_main_menu(self):
        # Display game background
        self.screen.blit(self.bg_img, self.bg_rect)
        # Substate 0 is base main menu
        if self.game_substate == 0:
            self.game_font.render_to(self.screen, (95, 60), TITLE, fgcolor=BLUEGREY, size=(120,240))
            self.game_font.render_to(self.screen, (97, 62), TITLE, fgcolor=BLUE, size=(120,240))
            # Display game options with rectangles associated for event handling
            self.game_font.render_to(self.screen, (293, 258), "Play", fgcolor=BLUEGREY, size=90)
            self.game_font.render_to(self.screen, (295, 260), "Play", fgcolor=BLUE, size=90)
            self.play_rect = pg.Rect(295, 260, 215, 90)
            self.game_font.render_to(self.screen, (213, 348), "Options", fgcolor=BLUEGREY, size=90)
            self.game_font.render_to(self.screen, (215, 350), "Options", fgcolor=BLUE, size=90)
            self.set_rect = pg.Rect(215, 350, 415, 90)
        # Substate 1 is main menu options submenu
        elif self.game_substate == 1:
            options_popup = pg.image.load("src/static/img/options.png")
            self.screen.blit(options_popup, self.bg_rect)
        # Substate 2 is main menu play submenu
        elif self.game_substate == 2:
            self.game_font.render_to(self.screen, (95, 60), TITLE, fgcolor=BLUEGREY, size=(120,240))
            self.game_font.render_to(self.screen, (97, 62), TITLE, fgcolor=BLUE, size=(120,240))
            # Display play options with rectangles associated for event handling
            self.game_font.render_to(self.screen, (203, 258), "Tutorial", fgcolor=BLUEGREY, size=90)
            self.game_font.render_to(self.screen, (205, 260), "Tutorial", fgcolor=BLUE, size=90)
            self.tut_rect = pg.Rect(105, 230, 485, 90)
            self.game_font.render_to(self.screen, (113, 348), "Multiplayer", fgcolor=BLUEGREY, size=90)
            self.game_font.render_to(self.screen, (115, 350), "Multiplayer", fgcolor=GREY, size=90)
            self.multi_rect = pg.Rect(115, 350, 550, 90)

    def render_game_screen(self):
        background = pg.image.load("src/static/img/bg.png")
        for _x in range (0, 5):
            for _y in range (0, 4):
                blit_x = _x*400
                blit_y = _y*300
                self.screen.blit(background, (blit_x,blit_y))
        self.screen.blit(self.canvas, (200, 100))
        self.game_font.render_to(self.screen, (275, 515), "Press Tab to Clear", fgcolor=BLUEGREY, size=25)
        self.game_font.render_to(self.screen, (195, 540), "Press Space to Submit Drawing", fgcolor=BLUEGREY, size=25)

    def run(self):
        while True:
            for event in pg.event.get():
                self.dispatch(event)
            if self.game_state == 0:
                if not self.screen.get_locked():
                    self.render_main_menu()
                    self.render_overlay()
            if self.game_state == 1:
                if not self.screen.get_locked():
                    self.render_game_screen()
                    self.render_overlay()
            pg.display.flip()

if __name__ == '__main__':
    main = Core()
    main.run()
