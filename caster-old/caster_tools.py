import pygame
import pygame.freetype
import tensorflow as tf


class GameScreen:
    # Constructor, draws the game screen bg and the canvas to draw on
    def __init__(self, screen):
        self.screen = screen
        background = pygame.image.load("static/img/bg.png")
        """ Set background image for the screen. Background image is seamless, so
        we will blit the background onto the screen five times across and four times
        down, covering a maximum screen resolution of 4000x2400. This should account
        for approx. 98.62% of Steam users and 89.00% of web users. """
        for x in range (0, 5):
            for y in range (0, 4):
                blit_x = x*400
                blit_y = y*300
                screen.blit(background, (blit_x,blit_y))
        self.canvas = pygame.Surface((400,400))

    # Creates the surface to draw on
    def draw_canvas(this, screen, canvas):
        drawing_surface = canvas # Creates a 400x400 canvas
        drawing_surface.fill(pygame.Color(255,255,255)) # Canvas color, set to white
        this.screen.blit(drawing_surface, (200,100)) # Blits the canvas onto the surface

    def get_canvas(this): # Return the canvas
        return this.canvas

    def get_screen(this): # Return the game screen
        return this.screen

    def roundline(srf, color, start, end, radius=5):
            dx = end[0]-start[0]
            dy = end[1]-start[1]
            distance = max(abs(dx), abs(dy))
            for i in range(distance):
                x = int( start[0]+float(i)/distance*dx)
                y = int( start[1]+float(i)/distance*dy)
                pygame.draw.circle(srf, color, (x, y), radius)
