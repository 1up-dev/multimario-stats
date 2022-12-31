import os
import threading
import time
#suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import users
import chatroom
import settings
import sort
import timer
import mode

# load users and racers, construct player objects
playerLookup = users.init_users()

# start bot thread
t = threading.Thread(target=chatroom.bot_init, args=(playerLookup,))
t.daemon = True
t.start()

# pygame setup
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats")

# determine number of pages
max_count = 99
num_players = len(playerLookup.keys())
i1 = 28
while True:
    if num_players <= i1:
        break
    max_count += 100
    i1 += 25
count = 0

# main display loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            settings.doQuit = True
    if settings.doQuit == True:
        pygame.quit()
        break

    if settings.redraw == True:
        for key in playerLookup:
            playerLookup[key].backup()
        sortedRacers = sort.sort(playerLookup)
    
    # redraw every 10 seconds or if redraw is requested
    # draw page 0 from 0-99, page 1 from 100-199, etc.
    if count%100 == 0 or settings.redraw == True:
        screen = mode.draw(screen, playerLookup, sortedRacers, count//100)
        settings.redraw = False
    count += 1

    if count > max_count:
        count = 0
    timer.drawTimer(screen)
    time.sleep(0.1)
