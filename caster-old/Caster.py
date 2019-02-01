import pygame
import pygame.freetype
import caster_tools

# Define a function to print the menu in game_state=0
def render_main_menu(screen, game_font, play_or_settings):
    game_font.render_to(screen, (295, 260), "Play", fgcolor=pygame.Color(107,117,255), size=90)
    if play_or_settings:
        game_font.render_to(screen, (297, 262), "Play", fgcolor=pygame.Color(65,47,219), style=4, size=90)
    else:
        game_font.render_to(screen, (297, 262), "Play", fgcolor=pygame.Color(78,83,156), size=90)
    # screen.blit(play, (350,250))

    game_font.render_to(screen, (200, 350), "Settings", fgcolor=pygame.Color(107,117,255), size=90)
    if play_or_settings:
        game_font.render_to(screen, (202, 352), "Settings", fgcolor=pygame.Color(78,83,156), size=90)
    else:
        game_font.render_to(screen, (202, 352), "Settings", fgcolor=pygame.Color(65,47,219), style=4, size=90)
    # screen.blit(gear, (0,520))

def render_settings_menu(screen, game_font, vol_value):
    game_font.render_to(screen, (230, 280), "Volume:", fgcolor=pygame.Color(109,112,155), size=90)
    game_font.render_to(screen, (232, 282), "Volume:", fgcolor=pygame.Color(78,83,156), size=90)

    for x in range (0, 10):
        offset = 115+(x*60)
        game_font.render_to(screen, (offset, 360), "¤", fgcolor=pygame.Color(109,112,155), size=90)

    for x in range (0, 10):
        offset = 117+(x*60)
        if (vol_value - 1) >= x:
            game_font.render_to(screen, (offset, 362), "¤", fgcolor=pygame.Color(65,47,219), size=90)
        else:
            game_font.render_to(screen, (offset, 362), "¤", fgcolor=pygame.Color(78,83,156), size=90)
# Define a main function
def main():

    # Initialize the pygame module
    pygame.init()

    # Load font
    game_font = pygame.freetype.Font("static/font/upheavtt.ttf")

    # Load a cursor
    pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    # Load and set the logo and window caption
    logo = pygame.image.load("static/img/logo_128.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("Caster 2D")

    # Set default window size
    default_window_size = (800,600)

    # Create default screen surface, 800x600, with no frame.
    # This is the base display surface, and is the canvas of the game.
    screen = pygame.display.set_mode(default_window_size, pygame.FULLSCREEN)

    # Create some visual assets to blit onto the screen
    """
    banner = pygame.image.load("static/img/logo_140x400.png")
    speaker = pygame.image.load("static/img/speaker.png")
    speaker_off = pygame.image.load("static/img/speaker_off.png")
    play = pygame.image.load("static/img/play.png")
    gear = pygame.image.load("static/img/gear.png")
    exit_img = pygame.image.load("static/img/exit.png")
    """
    background = pygame.image.load("static/img/background_800x600.png")

    # Generate list of songs based on music_list text file, for easy editing
    print("Reading Song List...") # Debug print
    song_list = []
    song_list_head = 0;
    with open("static/file/music_list.txt") as music_file:
        song_list = [line.rstrip('\n') for line in music_file]
    print("Song List loaded. Playing Music.") # Debug print
    # Begin playing the music at the head of the music list
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.load(song_list[song_list_head])
    pygame.mixer.music.play()
    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)


    # Define variables
    running = True # Runs the main loop
    mute = False # Music is muted
    play_or_settings = True # Toggle for selecting play or settings
    game_state = 0 # int to represent game state, 0=menu, 1=play, 2=settings
    vol_value = 10 # volume setting (default = 10, correlates to 1.0)
    draw_on = False;
    last_pos = (0,0)
    game_screen = caster_tools.GameScreen(screen)

    while running:
        for event in pygame.event.get():
            # Gets all Events in the EventQueue
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                # Change running to False to exit the main loop on window close, or
                # Escape menu by one level, setting running to False when escaping from main menu
                print("Menu escaped.") # Debug print
                if game_state == 1 or game_state == 2:
                    game_state = 0
                else:
                    running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                # Toggle fullscreen
                print("Fullscreen toggled.") # Debug print
                if screen.get_flags() & pygame.FULLSCREEN:
                    pygame.display.set_mode(default_window_size, pygame.NOFRAME)
                else:
                    pygame.display.set_mode(default_window_size, pygame.FULLSCREEN)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                # Toggle mute
                print("Mute toggled.") # Debug print
                mute = not mute
                if mute:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if event.type == (pygame.USEREVENT + 1):
                # Custom USEREVENT for when a song ends to either play next in list, or start over
                print("Song ended, ") # Debug print
                song_list_head += 1
                if (song_list_head < len(song_list)):
                    print("playing next song.") # Debug print
                    pygame.mixer.music.load(song_list[song_list_head])
                    pygame.mixer.music.play()
                else:
                    print("restarting queue.") # Debug print
                    song_list_head = 0
                    pygame.mixer.music.load(song_list[song_list_head])
                    pygame.mixer.music.play()
            if (
                # Switch between Play and Settings in the main menu
                    event.type == pygame.KEYDOWN and event.key == pygame.K_UP or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_w or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_s
                ):
                if game_state == 0:
                    print("Toggled Play/Settings.")
                    play_or_settings = not play_or_settings
            if (
                # Select a menu item
                    event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                ):
                if game_state == 0:
                    if play_or_settings:
                        print("Made menu selection: Play") # Debug print
                        game_state = 1
                        game_screen = caster_tools.GameScreen(screen)
                        game_screen.draw_canvas(game_screen.get_screen(), game_screen.get_canvas())
                    else:
                        print("Made menu selection: Settings") # Debug print
                        game_state = 2
            if (
                # Lower the volume using the vol_value, also changes graphic
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_a) and
                    game_state == 2 # Only want to consider this event when in settings
                ):
                print("Lowering Volume.") # Debug print
                if vol_value > 0:
                    vol_value -= 1
                pygame.mixer.music.set_volume(vol_value/10.0)
            if (
                # Raise the volume using the vol_value, also changes graphic
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT or
                    event.type == pygame.KEYDOWN and event.key == pygame.K_d) and
                    game_state == 2 # Only want to consider this event when in settings
                ):
                print("Raising Volume.") # Debug print
                if vol_value < 10:
                    vol_value += 1
                pygame.mixer.music.set_volume(vol_value/10.0)
            if (event.type == pygame.MOUSEBUTTONDOWN and game_state == 1):
                # Drawing in the game phase
                if (
                    (event.pos[0] >= 200 and event.pos[0] <= 600) and
                    (event.pos[1] >= 100 and event.pos[1] <= 500)
                ):
                    pygame.draw.circle(screen, pygame.Color(107,117,255), event.pos, 5)
                    draw_on = True
            if (event.type == pygame.MOUSEBUTTONUP and game_state == 1):
                draw_on = False
            if (
                (event.type == pygame.MOUSEMOTION and game_state == 1) and
                (event.pos[0] >= 200 and event.pos[0] <= 600) and
                (event.pos[1] >= 100 and event.pos[1] <= 500)
            ):
                if draw_on:
                    pygame.draw.circle(screen, pygame.Color(107,117,255), event.pos, 5)
                    caster_tools.GameScreen.roundline(screen, pygame.Color(107,117,255), event.pos, last_pos,  5)
                last_pos = event.pos
        # Blit assets
        """ Set background image for the screen. Background image is seamless, so
        we will blit the background onto the screen five times across and four times
        down, covering a maximum screen resolution of 4000x2400. This should account
        for approx. 98.62% of Steam users and 89.00% of web users. """
        """ for x in range (0, 5):
            for y in range (0, 4):
                blit_x = x*400
                blit_y = y*300
                screen.blit(background, (blit_x,blit_y)) """
        if (game_state == 0 or game_state == 2):
            screen.blit(background, (0,0))
            # screen.blit(banner, (200,60))
            game_font.render_to(screen, (95, 60), "Caster 2D", fgcolor=pygame.Color(107,117,255), size=(120,240))
            game_font.render_to(screen, (97, 62), "Caster 2D", fgcolor=pygame.Color(65,47,219), size=(120,240))
            # screen.blit(exit_img, (720,520))
        if game_state == 0:
            render_main_menu(screen, game_font, play_or_settings)
        elif game_state == 1:
            # game_screen = caster_tools.GameScreen(screen)
            screen = game_screen.get_screen()
        elif game_state == 2:
            render_settings_menu(screen, game_font, vol_value)
        else:
            print("Something is very, very wrong.") # Debug print

        # Control music and render pause/play header
        if mute:
            song_title = song_list[song_list_head].rstrip("ggo.")
            song_title = song_title.rstrip("3pm.")
            song_title = song_title.lstrip("static/audio/music/")
            text = ("Paused: " + song_title + " (press M to unpause)")
            if game_state == 1:
                game_font.render_to(game_screen.get_screen(), (5, 5), text, fgcolor=pygame.Color(60,63,94), size=30)
            else:
                game_font.render_to(screen, (5, 5), text, fgcolor=pygame.Color(60,63,94), size=30)
            # screen.blit(speaker_off, (0,0))
        else:
            song_title = song_list[song_list_head].rstrip("ggo.")
            song_title = song_title.rstrip("3pm.")
            song_title = song_title.lstrip("static/audio/music/")
            text = ("Playing: " + song_title + " (press M to pause)")
            if game_state == 1:
                game_font.render_to(game_screen.get_screen(), (5, 5), text, fgcolor=pygame.Color(60,63,94), size=30)
            else:
                game_font.render_to(screen, (5, 5), text, fgcolor=pygame.Color(60,63,94), size=30)
            # screen.blit(speaker, (0,0))
        game_font.render_to(screen, (90, 575), "(ESC to exit - F to toggle fullscreen)", fgcolor=pygame.Color(60,63,94), size=30)
        # Update the Screen
        pygame.display.flip()

if __name__=="__main__":
    # call the main function
    main()
