import datetime
import json
import os
import threading
import time
#suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import users
import chatroom
import player
import srl
import settings
import sort
import bot
import timer
import mode

def chat_init(playerLookup):
    print("Joining Twitch channels...")
    channels = []
    for c in settings.extra_chats:
        if c not in users.racersL:
            channels.append(c)
        else:
            print("skipping extra channel", c, "which is already a racer")
    for c in users.racersL:
        channels.append(c)

    c = chatroom.ChatRoom(channels)
    attempts = 0
    while(c.reconnect() == False):
        attempts += 1
        time.sleep(1)
        if attempts > 5:
            print("Failed to connect to Twitch IRC successfully.")
            return
    time.sleep(1)
    
    t = threading.Thread(target=bot.fetchIRC, args=(c, playerLookup))
    t.daemon = True
    t.start()
    print("Done joining Twitch channels.")

# create the backup file if it doesn't exist
j = {}
backupFile = os.path.join(settings.baseDir,"backup.json")
if not os.path.isfile(backupFile):
    with open(backupFile, 'w+') as f:
        json.dump(j, f, indent=4)
with open(backupFile, 'r') as f:
    j = json.load(f)

# player object instantiation
playerLookup = {}
if settings.use_backups and j != {}:
    for racer in users.racersCS:
        state_data = {}
        if racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, state_data)
else:
    for racer in users.racersCS:
        playerLookup[racer.lower()] = player.Player(racer, {})

# join Twitch channels
t = threading.Thread(target=chat_init, args=(playerLookup,))
t.daemon = True
t.start()

#SRL = threading.Thread(target=srl.srlThread, args=("#speedrunslive", mainChat, playerLookup,))
#SRL.start()

# pygame setup
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats")
pygame.mixer.stop()

# determine number of pages
max_count = 100
num_players = len(users.racersL)
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
        sortedRacers = sort.sort(playerLookup)
    
    if max_count == 100:
        # if there is only one page, never redraw it on a timer
        if settings.redraw == True:
            screen = mode.draw(screen, playerLookup, sortedRacers, 1)
            settings.redraw = False
    elif count <= 100:
        if count == 0 or settings.redraw == True:
            screen = mode.draw(screen, playerLookup, sortedRacers, 1)
            settings.redraw = False
    elif count <= 200:
        if count == 101 or settings.redraw == True:
            screen = mode.draw(screen, playerLookup, sortedRacers, 2)
            settings.redraw = False
    else:
        if count == 201 or settings.redraw == True:
            screen = mode.draw(screen, playerLookup, sortedRacers, 3)
            settings.redraw = False
    count += 1

    if count >= max_count:
        count = 0
    timer.drawTimer(screen)
    time.sleep(0.1)
