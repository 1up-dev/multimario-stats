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
import scoreboard
import player
import twitch

# pygame setup
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats")
scoreboard.draw(screen, {}, 0)

# Validate Twitch API token. This also retrieves the bot username.
twitch.validate_token()

# load twitch user lists
users.load_users()

# load racers, construct player objects
playerLookup = player.init_players()

# start bot thread
t = threading.Thread(target=bot.init, args=(playerLookup,))
t.daemon = True
t.start()

# main display loop
count = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            settings.doQuit = True
    if settings.doQuit == True:
        settings.chat_ref.connection.close()
        pygame.quit()
        break

    if settings.redraw == True:
        settings.save_state(playerLookup)
        sort.sort(playerLookup)
    
    # redraw every 10 seconds or if redraw is requested
    # draw page 0 from 0-99, page 1 from 100-199, etc.
    if count%100 == 0 or settings.redraw == True:
        scoreboard.draw(screen, playerLookup, count//100)
        settings.redraw = False
    count += 1

    if count > settings.max_count:
        count = 0
    timer.draw(screen, playerLookup)
    time.sleep(0.1)
