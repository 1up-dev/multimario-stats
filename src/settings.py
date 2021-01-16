import datetime
import pygame

startTime = datetime.datetime.now()
doQuit = False
redraw = True

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)
