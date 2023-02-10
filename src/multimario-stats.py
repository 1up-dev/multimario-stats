import os
import threading
import time
#suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import users
import bot
import settings
import sort
import timer
import mode
import player

# load users and racers, construct player objects
playerLookup = users.init_users()

# start bot thread
t = threading.Thread(target=bot.init, args=(playerLookup,))
t.daemon = True
t.start()

# pygame setup
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats")

# determine number of pages
settings.set_max_count(len(playerLookup))

# main display loop
count = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            settings.doQuit = True
    if settings.doQuit == True:
        pygame.quit()
        break

    if settings.redraw == True:
        player.backup_all(playerLookup)
        sortedRacers = sort.sort(playerLookup)
    
    # redraw every 10 seconds or if redraw is requested
    # draw page 0 from 0-99, page 1 from 100-199, etc.
    if count%100 == 0 or settings.redraw == True:
        screen = mode.draw(screen, playerLookup, sortedRacers, count//100)
        settings.redraw = False
    count += 1

    if count > settings.max_count:
        count = 0
    timer.drawTimer(screen, playerLookup)
    time.sleep(0.1)
