import pygame as pg

class GameTools:
    def roundline(srf, color, start, end, radius=5):
            dx = end[0]-start[0]
            dy = end[1]-start[1]
            distance = max(abs(dx), abs(dy))
            for i in range(distance):
                x = int( start[0]+float(i)/distance*dx)
                y = int( start[1]+float(i)/distance*dy)
                pg.draw.circle(srf, color, (x, y), radius)
