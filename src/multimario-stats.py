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
import draw
import sort
import bot
import draw_t

def chat_init(playerLookup):
    print("Joining Twitch channels...")
    channels = []
    for c in extra_chats:
        if c not in users.racersL:
            channels.append(c)
        else:
            print("skipping extra channel", c, "which is already a racer")
    for c in users.racersL:
        channels.append(c)

    c = chatroom.ChatRoom(channels, NICK, PASSWORD)
    c.reconnect()
    time.sleep(1)
    
    t = threading.Thread(target=bot.fetchIRC, args=(c, playerLookup))
    t.daemon = True
    t.start()
    print("Done joining Twitch channels.")

# loading & processing settings
with open('settings.json', 'r') as f:
    j = json.load(f)
    NICK = j['bot-twitch-username']
    PASSWORD = j['bot-twitch-auth']
    debug = j['debug']
    settings.startTime = datetime.datetime.fromisoformat(j['start-time'])
    use_backups = j['use-player-backups']
    mode = j['mode']
    extra_chats = j['extra-chat-rooms']

# create the backup file if it doesn't exist
j = {}
if not os.path.isfile("backup.json"):
    with open('backup.json', 'w+') as f:
        json.dump(j, f, indent=4)
with open('backup.json', 'r') as f:
    j = json.load(f)

# player object instantiation
playerLookup = {}
if use_backups and j != {}:
    for racer in users.racersCS:
        state_data = {}
        if racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, state_data)
else:
    for racer in users.racersCS:
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, {})

# join Twitch channels
t = threading.Thread(target=chat_init, args=(playerLookup,))
t.daemon = True
t.start()

#SRL = threading.Thread(target=srl.srlThread, args=("#speedrunslive", mainChat, playerLookup,))
#SRL.start()

# pygame setup
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats Program")
pygame.mixer.stop()

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
    draw_t.drawTimer(screen)
    time.sleep(0.1)
