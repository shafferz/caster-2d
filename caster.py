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
        # Boolean used to toggle fullscreen mode
        self.is_fullscreen = False
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
        self.player = Player()
        self.enemy = Player()
        self.spell_crafter = SpellCrafter()
        self.opponent_bot = SpellCrafter()
        self.tutorialized = False
        self.card_list = [
            pg.image.load("src/static/img/tutorial_card1.png"),
            pg.image.load("src/static/img/tutorial_card2.png"),
            pg.image.load("src/static/img/tutorial_card3.png"),
            pg.image.load("src/static/img/tutorial_card4.png"),
            pg.image.load("src/static/img/tutorial_card5.png")
        ]
        self.card = 0
        self.player_acted = False
        self.enemy_acted = False
        self.round = 1
        self.player_turn = True
        self.alive = True
        self.won = False

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
            elif self.game_state == 2:
                self.canvas.fill(WHITE)
                self.game_substate = 0
                self.game_state = 0
        # Handling pressing in the mouse, for clicking buttons or drawing
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
                                self.won = False
                                self.alive = True
                                self.round = 1
                                self.player_acted = False
                                self.enemy_acted = False
                                self.canvas.fill(WHITE)
                        # If the multiplayer rect exists
                        if self.multi_rect:
                            # If the click happened over the settings button area
                            if self.multi_rect.collidepoint(pg.mouse.get_pos()):
                                print("Clicked multiplayer")
                elif self.game_state == 1:
                    # Drawing point at coordinates, adjusted for offset of canvas
                    (adj_x, adj_y) = (event.pos[0]-200, event.pos[1]-100)
                    pg.draw.circle(self.canvas, BLACK, (adj_x, adj_y), 25)
                    # Variable to enable continuous drawing
                    self.draw_on = True
        # Handling letting go of mouse button, indicates stop drawing
        elif event.type == pg.MOUSEBUTTONUP:
            self.draw_on = False
        # Handling mouse moving events, used to smooth the drawing strokes
        elif event.type == pg.MOUSEMOTION:
            # Adjust coordinates of mouse event for canvas location
            (adj_x, adj_y) = (event.pos[0]-200, event.pos[1]-100)
            # If actively drawing, connect moving points with rounded line
            if self.draw_on:
                pg.draw.circle(self.canvas, BLACK, (adj_x, adj_y), 25)
                GameTools.roundline(self.canvas, BLACK, (adj_x, adj_y), self.last_pos,  25)
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
                prediction = GameTools.predict(self.canvas)
                self.spell_crafter.add_glyph(prediction)
                self.canvas.fill(WHITE)
        # Handling user pressing backspace, used to remove last added glyph
        elif event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE:
            if self.game_state == 1:
                if not self.spell_crafter.is_empty():
                    self.spell_crafter.remove_last_glyph()
        # Handling user pressing enter, used for a lot of actions
        elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
            # If in the game...
            if self.game_state == 1:
                # And if in tutorial mode...
                if self.game_substate == 0:
                    # If it is during the player's turn, cast the spell
                    if self.card < 4 and self.tutorialized == False:
                        self.card += 1
                    else:
                        self.tutorialized = True
                    if self.player_turn:
                        # If and only if the the spell is ready to cast
                        if self.spell_crafter.spell_ready(self.player.mana):
                            self.player_acted = True
                            if self.player_acted and self.enemy_acted:
                                self.calculate_result()
                                self.round += 1
                                self.player_acted = False
                                self.enemy_acted = False
                            self.player.eot()
                            self.opponent_bot.random_cast(min(self.enemy.max_mana, 4))
                    # If it is during the tutorial bot's turn, cast a random spell
                    else:
                        self.enemy_acted = True
                        if self.player_acted and self.enemy_acted:
                            self.calculate_result()
                            self.round += 1
                            self.player_acted = False
                            self.enemy_acted = False
                        self.enemy.eot()
                    # Logic to figure out who would go next
                    # If the round is odd, player gets first turn
                    if (self.round % 2) == 1:
                        # if player already went, enemy goes instead
                        if not self.player_acted:
                            self.player_turn = True
                        else:
                            self.player_turn = False
                    # If the round is even, enemy gets first turn
                    else:
                        # If enemy already went, player goes instead
                        if not self.enemy_acted:
                            self.player_turn = False
                        else:
                            self.player_turn = True
                    # If the player's hitpoints are reduced to 0, kill player
                    # and go to Game Over screen
                    if self.player.hitpoints <= 0:
                        self.game_state = 2
                        self.alive = False
                    # If the enemy's hitpoints are reduced to 0, give player a
                    # win and go to Game Over screen
                    if self.enemy.hitpoints <= 0:
                        self.game_state = 2
                        self.won = True
        # Handling pressing the F key, used to toggle Fullscreen mode
        elif event.type == pg.KEYDOWN and event.key == pg.K_f:
            if self.is_fullscreen:
                self.screen = pg.display.set_mode((WIDTH, HEIGHT))
            else:
                self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN)
            self.is_fullscreen = not self.is_fullscreen

    def calculate_result(self):
        self.spell_crafter.craft_spell()
        self.opponent_bot.craft_spell()
        # Defence is the strength of a shield spell, used to reduce incoming
        # spell attacks' damage. Booleans determine if advantage bonuses apply
        p1_defense = 0
        p2_defense = 0
        p1_has_adv = False
        p2_has_adv = False
        # If the spell glyph is mana, increase the player(s) max mana only
        if self.spell_crafter.spell_glyphs[0] == "mana":
            self.player.max_mana += 1
            self.player.mana = self.player.max_mana
        if self.opponent_bot.spell_glyphs[0] == "mana":
            self.enemy.max_mana += 1
            self.enemy.mana = self.enemy.max_mana
        # If the spell is a buff/debuff, find the buff index from dominant
        # element value. Player 1's spell first
        if self.spell_crafter.is_buff:
            buff_index = self.spell_crafter.dominant_element[0]-5
            # If on self, apply the buff and set the turn counter on the buff
            # to 3.
            if self.spell_crafter.on_self:
                self.spell_crafter.buff[buff_index] = self.spell_crafter.strength
                self.spell_crafter.buff_timer[buff_index] = 3
            # If on player 2, it is a curse, similar
            else:
                self.opponent_bot.debuff[buff_index] = self.spell_crafter.strength
                self.opponent_bot.debuff_timer[buff_index] = 3
        # Player 2's spell if it is a buff
        if self.opponent_bot.is_buff:
            buff_index = self.opponent_bot.dominant_element[0]-5
            # If on self, apply the buff and set the turn counter on the buff
            # to 3.
            if self.opponent_bot.on_self:
                self.opponent_bot.buff[buff_index] = self.opponent_bot.strength
                self.opponent_bot.buff_timer[buff_index] = 3
            # If on player 1, it is a curse, similar
            else:
                self.spell_crafter.debuff[buff_index] = self.opponent_bot.strength
                self.spell_crafter.debuff_timer[buff_index] = 3
        # Next we handle defensive spells. Player 1's shield spell first
        if not self.spell_crafter.is_buff and self.spell_crafter.on_self:
            p1_defense = self.spell_crafter.strength
        # Followed by Player 2's shield spell, if any
        if not self.opponent_bot.is_buff and self.opponent_bot.on_self:
            p2_defense = self.opponent_bot.strength
        # Before calculating attack damage, we need to know if either spell
        # has disadvantage. This means checking to see if any spell's element
        # is weak to the other's. Check to see if p1's spell is dominant first
        if (self.spell_crafter.dominant_element[0] == self.opponent_bot.dominant_element[0]-1 or (self.spell_crafter.dominant_element[0] == 5 and self.opponent_bot.dominant_element[0] == 1)):
            p1_has_adv = True
        # Then check if p2 has advantage
        if (self.opponent_bot.dominant_element[0] == self.spell_crafter.dominant_element[0]-1 or (self.opponent_bot.dominant_element[0] == 5 and self.spell_crafter.dominant_element[0] == 1)):
            p2_has_adv = True
        # Finally, if either has adv, the other has disadvantage. This doesn't
        # need calculated, as a modifier is applied to a spell with advantage.
        # The last step is to calculate projectiles and their damage, if any
        if not self.spell_crafter.is_buff and not self.spell_crafter.on_self:
            # Increase p1 damage 50% if p1 has advantage
            if p1_has_adv:
                damage = math.floor(self.spell_crafter.strength * 1.5)
            else:
                damage = self.spell_crafter.strength
            # Increase p2 shield strength 50% if p2 has advantage
            if p2_has_adv:
                damage -= math.floor(p2_defense * 1.5)
            else:
                damage -= p2_defense
            # If the shield reduces damage below 0, change damage to 0
            if damage < 0:
                damage = 0
            # Increase damage proportional to number of elemental glyphs of the
            # dominant type, and submit
            self.enemy.hit(damage*(1+self.spell_crafter.dominant_element[1]/4))
        if not self.opponent_bot.is_buff and not self.opponent_bot.on_self:
            # Increase p2 damage 50% if p1 has advantage
            if p2_has_adv:
                damage = math.floor(self.opponent_bot.strength * 1.5)
            else:
                damage = self.opponent_bot.strength
            # Increase p1 shield strength 50% if p1 has advantage
            if p1_has_adv:
                damage -= math.floor(p1_defense * 1.5)
            else:
                damage -= p1_defense
            # If the shield reduces damage below 0, change damage to 0
            if damage < 0:
                damage = 0
            # Increase damage proportional to number of elemental glyphs of the
            # dominant type, and submit
            self.player.hit(damage*(1+self.spell_crafter.dominant_element[1]/4))
        # Restore player's spell_crafter object to base values (except de/buffs)
        self.spell_crafter.restore_base_values()
        # Generate the opponent's next spell in advance
        self.opponent_bot.random_cast(min(self.enemy.max_mana, 4))

    def render_overlay(self):
        # Overlay for the music player at the top of the screen
        song_title = self.song_list[self.song_list_head].rstrip("ggo.")
        song_title = song_title.rstrip("3pm.")
        song_title = song_title.lstrip("static/audio/music/")
        text = song_title
        self.game_font.render_to(self.screen, (5, 5), text, fgcolor=BLUEGREY, size=30)
        if self.game_state == 0:
            self.game_font.render_to(self.screen, (165, 570), "Press F to toggle fullscreen", fgcolor=BLUEGREY, size=30)
        # Overlay specific to being in-game
        if self.game_state == 1:
            # Round number at the top
            round_str = "Round: " + str(self.round)
            self.game_font.render_to(self.screen, (330, 70), round_str, fgcolor=BLUEGREY, size=30)
            # Player's turn overlay
            if self.player_turn:
                if not self.spell_crafter.spell_ready(self.player.mana):
                    # Warn user that they need more glyphs (2 minimum)
                    if len(self.spell_crafter.spell_glyphs) < 2:
                        self.game_font.render_to(self.screen, (65, 570), "Need more glyphs!", fgcolor=RED, size=30)
                    # Warn user that they need a casting glyph
                    if not self.spell_crafter.has_casting():
                        self.game_font.render_to(self.screen, (375, 570), "Missing casting glyph!", fgcolor=RED, size=30)
                else:
                    self.game_font.render_to(self.screen, (225, 570), "Ready to Cast! (Enter)", fgcolor=GREEN, size=30)
                # Display the mana cost to the screen, turn red when too expensive, only on player's turn
                if self.spell_crafter.cost <= self.player.mana:
                    cost_str = ("Cost: " + str(self.spell_crafter.cost))
                    self.game_font.render_to(self.screen, (605, 230), cost_str, fgcolor=BLUEGREY, size=25)
                elif self.spell_crafter.cost > self.player.mana:
                    cost_str = ("Cost: " + str(self.spell_crafter.cost))
                    self.game_font.render_to(self.screen, (605, 230), cost_str, fgcolor=RED, size=25)
            mana_str = "Mana: " + str(self.player.mana-self.spell_crafter.cost) + "/" + str(self.player.max_mana)
            self.game_font.render_to(self.screen, (605, 255), mana_str, fgcolor=BLUE, size=25)
            hp_str = "HP: " + str(self.player.hitpoints) + "/100"
            self.game_font.render_to(self.screen, (605, 280), hp_str, fgcolor=RED, size=25)
            ems = "Mana: " + str(self.enemy.mana-self.opponent_bot.cost) + "/" + str(self.enemy.max_mana)
            self.game_font.render_to(self.screen, (605, 490), ems, fgcolor=BLUE, size=25)
            ehs = "HP: " + str(self.enemy.hitpoints) + "/100"
            self.game_font.render_to(self.screen, (605, 520), ehs, fgcolor=RED, size=25)
            if self.game_substate == 0:
                if not self.tutorialized:
                    self.screen.blit(self.card_list[self.card], (0,0))
        # Overlay specific to game over screen
        if self.game_state == 2:
            if self.alive == False:
                self.game_font.render_to(self.screen, (20, 50), "You lose", fgcolor=RED, size=165)
                self.game_font.render_to(self.screen, (220, 275), "Press ESC to continue", fgcolor=WHITE, size=30)
            if self.won == True:
                self.game_font.render_to(self.screen, (40, 50), "Victory!", fgcolor=BLUEGREY, size=165)
                self.game_font.render_to(self.screen, (220, 275), "Press Esc to continue", fgcolor=BLACK, size=30)

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

    def render_tutorial_game_screen(self):
        # Render the background first
        background = pg.image.load("src/static/img/bg.png")
        for _x in range (0, 5):
            for _y in range (0, 4):
                blit_x = _x*400
                blit_y = _y*300
                self.screen.blit(background, (blit_x,blit_y))
        # Render glyph guide
        glyph_img = pg.image.load("src/static/img/glyphs.png")
        self.screen.blit(glyph_img, (0, 100))

    def render_player_game_screen(self):
        self.screen.blit(self.canvas, (200, 100))
        self.game_font.render_to(self.screen, (275, 515), "Press Tab to Clear", fgcolor=BLUEGREY, size=25)
        self.game_font.render_to(self.screen, (195, 540), "Press Space to Submit Drawing", fgcolor=BLUEGREY, size=25)
        self.game_font.render_to(self.screen, (670, 70), "You", fgcolor=BLUEGREY, size=30)
        self.game_font.render_to(self.screen, (655, 460), "Enemy", fgcolor=BLUEGREY, size=30)
        if self.spell_crafter.spell_glyphs:
            glyph_list = []
            for glyph in self.spell_crafter.spell_glyphs:
                glyph_list.append(glyph)
            for spacing, glyph in enumerate(glyph_list):
                self.game_font.render_to(self.screen, (605, (100+(25*spacing))), glyph, fgcolor=BLUEGREY, size=25)

    def render_enemy_game_screen(self):
        self.game_font.render_to(self.screen, (265, 100), "This is the opponent's turn.", fgcolor=BLUEGREY, size=25)
        self.game_font.render_to(self.screen, (200, 125), "The opponent's spell has the glyphs:", fgcolor=BLUEGREY, size=25)
        if self.opponent_bot.spell_glyphs:
            glyph_list = []
            for glyph in self.opponent_bot.spell_glyphs:
                glyph_list.append(glyph)
            for spacing, glyph in enumerate(glyph_list):
                self.game_font.render_to(self.screen, (380, (150+(25*spacing))), glyph, fgcolor=BLUEGREY, size=25)

    def render_game_over(self):
        if self.alive == False:
            bad_bg = pg.image.load("src/static/img/stormy_background_800x600.png")
            self.screen.blit(bad_bg, self.bg_rect)
            self.game_font.render_to(self.screen, (200, 200), "GAME OVER", fgcolor=WHITE, size=75)
        if self.won == True:
            good_bg = pg.image.load("src/static/img/shining_background_800x600.png")
            self.screen.blit(good_bg, self.bg_rect)
            self.game_font.render_to(self.screen, (200, 200), "GAME OVER", fgcolor=BLACK, size=75)

    def run(self):
        while True:
            for event in pg.event.get():
                self.dispatch(event)
            if not self.screen.get_locked():
                if self.game_state == 0:
                        self.render_main_menu()
                        self.render_overlay()
                if self.game_state == 1:
                    if self.game_substate == 0:
                        # If the player is alive and has not won the game,
                        # we render the game screens and overlay.
                            self.render_tutorial_game_screen()
                            if self.player_turn:
                                self.render_player_game_screen()
                            else:
                                self.render_enemy_game_screen()
                            self.render_overlay()
                if self.game_state == 2:
                    self.render_game_over()
                    self.render_overlay()
            pg.display.flip()

if __name__ == '__main__':
    main = Core()
    main.run()
