import datetime
import json
import traceback
import os
import threading
import time
#suppress pygame startup message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import users
import chatroom
import twitch
import player
import srl
import settings
import draw
import sort
from bot import fetchIRC

def threadSpawner(chat_pool):
    print("Joining Twitch channels...")
    for c in chat_pool:
        c.reconnect()
        t = threading.Thread(target=fetchIRC, args=(c,playerLookup))
        t.daemon = True
        t.start()
        time.sleep(1)
    print("Done joining Twitch channels.")

#---------loading & processing settings-------------
with open('settings.json', 'r') as f:
    j = json.load(f)
    NICK = j['bot-twitch-username']
    PASSWORD = j['bot-twitch-auth']
    debug = j['debug']
    settings.startTime = datetime.datetime.fromisoformat(j['start-time'])
    use_backups = j['use-player-backups']
    mode = j['mode']
    extra_chats = j['extra-chat-rooms']

#---------------player object assignments--------------
playerLookup = {}
j = {}
# create the backup file if it doesn't exist
if not os.path.isfile("backup.json"):
    with open('backup.json', 'w+') as f:
        json.dump(j, f, indent=4)
with open('backup.json', 'r') as f:
    j = json.load(f)

if use_backups and j != {}:
    for racer in users.racersCS:
        state_data = {}
        if racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, state_data)
else:
    for racer in users.racersCS:
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, {})

#------------set up chat rooms------------
chat_pool = []
for e in extra_chats:
    e = e.lower()
    if e not in users.racersL:
        chat_pool.append(chatroom.ChatRoom(e, NICK, PASSWORD))
    else:
        print("skipping extra channel "+e+" which is already a racer")
for player in playerLookup.keys():
    chat_pool.append(playerLookup[player].chat)

#join Twitch channels
t = threading.Thread(target=threadSpawner, args=(chat_pool,))
t.daemon = True
t.start()

#SRL = threading.Thread(target=srl.srlThread, args=("#speedrunslive", mainChat, playerLookup,))
#SRL.start()

#---------------------pygame setup----------------------
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats Program")
pygame.display.flip()

done = False
count = 0
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    if settings.doQuit == True:
        done = True

    if settings.redraw == True:
        sortedRacers = sort.sort(playerLookup)
    
    if count <= 120:
        #draw page 1: 12 seconds
        if count == 0 or settings.redraw == True:
            screen = draw.draw(screen, mode, playerLookup, sortedRacers, 1)
            settings.redraw = False
    else:
        #draw page 2: 8 seconds
        if count == 121 or settings.redraw == True:
            screen = draw.draw(screen, mode, playerLookup, sortedRacers, 2)
            settings.redraw = False
    count += 1
    if count > 200:
        count = 0
    draw.drawTimer(screen)
    time.sleep(0.1)

pygame.quit()
