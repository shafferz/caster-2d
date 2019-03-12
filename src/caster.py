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

class Core(object):
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
        pg.display.set_caption(TITLE)
        pg.display.set_icon(pg.image.load(ICON))
        self.clock = pg.time.Clock()
        # TODO: Figure out why PNG isn't loading
        # self.bg_img = pg.image.load(os.path.join(IMG_DIR), "background_800x600.jpg")
        # self.bg_rect = self.bg_image.get_rect()
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

    def dispatch(self, event):
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass
        elif event.type == (pg.USEREVENT + 1):
            # Custom USEREVENT for when a song ends to either play next in list, or start over
            self.song_list_head += 1
            if (self.song_list_head < len(self.song_list)):
                pg.mixer.music.load(self.song_list[self.song_list_head])
                pg.mixer.music.play()
            else:
                self.song_list_head = 0
                pg.mixer.music.load(self.song_list[self.song_list_head])
                pg.mixer.music.play()
        elif event.type == pg.KEYDOWN and event.key == pg.K_m:
            self.mute = not self.mute
            if self.mute:
                pg.mixer.music.pause()
            else:
                pg.mixer.music.unpause()

    def run(self):
        while True:
            for event in pg.event.get():
                self.dispatch(event)

            self.screen.fill([0xFF, 0xFF, 0xFF])
            pg.display.flip()

if __name__ == '__main__':
    main = Core()
    main.run()
