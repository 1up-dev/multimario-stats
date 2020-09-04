import datetime
import json
import traceback
import os
import threading
import pygame
import users
import chatroom
import twitch
import player
import srl
import mode_602
import mode_1120

def fetchIRC(thisChat):
    while True:
        try:
            readbuffer = thisChat.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            if readbuffer == "": #reconnect on server disconnect
                thisChat.reconnect()
            thisChat.inputBuffer += readbuffer
        except Exception as e:
            print("[!] Error in irc recv thread:", thisChat.channel, e)
            thisChat.reconnect() #reconnect if there is an error

#---------loading & processing external data-------------
with open('settings.json', 'r') as f:
    j = json.load(f)
    debug = json.loads(j['debug'].lower())
    NICK = j['bot-twitch-username']
    PASSWORD = j['bot-twitch-auth']
    if debug:
        CHANNEL = j['test-chat']
    else:
        CHANNEL = j['main-chat']
    debug = json.loads(j['debug'].lower())
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    use_backups = json.loads(j['use-player-backups'].lower())
    mode = j['mode']
    extra_chats = j['extra-chat-rooms']

#---------------player object assignments--------------
playerLookup = {}
print("Joining Twitch channels, please wait... ", end="", flush=True)

j = {}
if not os.path.isfile("backup.json"):
    with open('backup.json', 'w+') as f:
        json.dump(j, f, indent=4)
try:
    with open('backup.json', 'r') as f:
        j = json.load(f)
except Exception as e:
    print(traceback.format_exc())

if use_backups and j != {}:
    for racer in users.racersCS:
        state_data = {}
        if racer.lower() in j.keys():
            state_data = j[racer.lower()]
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, state_data)
else:
    for racer in users.racersCS:
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug, mode, {})

#------------create and start irc threads------------
chat_pool = []
for player in playerLookup.keys():
    chat_pool.append(playerLookup[player].chat)
for e in extra_chats:
    e = e.lower()
    if e not in users.racersL:
        chat_pool.append(chatroom.ChatRoom(e, NICK, PASSWORD))
    else:
        print("skipping extra channel "+e+" which is already a racer")
for c in chat_pool:
    t = threading.Thread(target=fetchIRC, args=(c,))
    t.daemon = True
    t.start()
#SRL = threading.Thread(target=srl.srlThread, args=("#speedrunslive", mainChat, playerLookup,))
#SRL.start()
print("Done.")

#---------------------pygame setup----------------------
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats Program")
pygame.display.flip()
redraw = True

#--------------------main bot loop--------------------
done = False
while not done:
    for currentChat in chat_pool:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done=True
            #--------------------reading from twitch chat--------------------
            lines = currentChat.inputBuffer.split("\n")
            currentChat.inputBuffer = ""

            for line in lines:
                out = ""
                user = ""
                line = line.rstrip().split()

                ismod = False
                userId = -1
                if len(line) > 0:
                    if line[0][0] == "@":
                        tags = line.pop(0)

                        tmp8 = tags.split("mod=")
                        if len(tmp8) > 1:
                            if tmp8[1][0] == "1":
                                ismod = True
                        
                        tmp9 = tags.split("user-id=")
                        if len(tmp9) > 1:
                            userId = tmp9[1].split(";")[0]

                for index, word in enumerate(line):
                    if index == 0:
                        user = word.split('!')[0]
                        user = user[0:24]
                    if index == 3:
                        out += word
                        out = out[1:]
                    if index >= 4:
                        out += " " + word

                command = out.lower().split(" ")

                if command[0] == '':
                    pass
                elif user == "PING":
                    currentChat.pong()
                elif user.__contains__("."):
                    pass
                elif command[0][0] != "!":
                    pass
                else:
                    user = user.lower()[1:]
                    print("[In chat "+currentChat.channel+"] "+user+":"+str(command))

                    #----------------------global commands---------------------
                    if command[0] == "!ping":
                        currentChat.message("Hi. Bot is alive.")
                    if command[0] == "!602commands":
                        currentChat.message("Command list: https://pastebin.com/d7mPZd13")
                    if command[0] == "!roles":
                        if len(command) == 1:
                            statusMsg = users.status(user, playerLookup)
                        else:
                            statusMsg = users.status(command[1], playerLookup)
                        if statusMsg is not None:
                            currentChat.message(statusMsg)

                    #----------------------shared commands---------------------
                    if (user in users.admins) or (user in users.racersL):
                        if command[0] == "!whitelist" and len(command) == 2:
                            if command[1] in users.blacklist:
                                currentChat.message("Sorry, " + command[1] + " is on the blacklist.")
                            elif command[1] not in users.updaters:
                                users.add(command[1],users.Role.UPDATER)
                                currentChat.message(command[1] + " is now an updater.")
                            else:
                                currentChat.message(command[1] + " is already an updater.")
                        elif command[0] == "!unwhitelist" and len(command) == 2:
                            if command[1] in users.updaters:
                                users.remove(command[1],users.Role.UPDATER)
                                currentChat.message(command[1] + " is no longer an updater.")
                            else:
                                currentChat.message(command[1] + " is already not an updater.")

                    #----------------------racer commands----------------------
                    if user in users.racersL:
                        if (command[0] == "!add" or command[0] == "!set") and len(command) == 2:
                            try:
                                number = int(command[1])
                                if user in playerLookup.keys():
                                    response = ""
                                    if command[0] == "!add":
                                        response = playerLookup[user].update(playerLookup[user].collects + number)
                                    elif command[0] == "!set":
                                        response = playerLookup[user].update(number)
                                    if response != "":
                                        currentChat.message(response)
                                    redraw = True
                            except ValueError:
                                pass
                        
                        if command[0] == "!quit" and playerLookup[user].status == "live":
                            playerLookup[user].fail("quit", startTime)
                            redraw = True
                            currentChat.message(playerLookup[user].nameCaseSensitive + " has quit.")
                        if command[0] == "!rejoin" and playerLookup[user].status != "live":
                            if playerLookup[user].status == "done":
                                playerLookup[user].collects -= 1
                            playerLookup[user].status = "live"
                            redraw = True
                            currentChat.message(playerLookup[user].nameCaseSensitive +" has rejoined the race.")          

                    #--------------------updater commands----------------------
                    if ((user in users.updaters) or (ismod==True)) and (user not in users.blacklist):
                        if (command[0] == "!add" or command[0] == "!set") and len(command) == 3:
                            player = command[1]
                            try:
                                number = int(command[2])
                                if player in playerLookup.keys():
                                    response = ""
                                    if command[0] == "!add":
                                        response = playerLookup[player].update(playerLookup[player].collects + number)
                                    elif command[0] == "!set":
                                        response = playerLookup[player].update(number)
                                    if response != "":
                                        currentChat.message(response)
                                    redraw = True
                            except ValueError:
                                pass

                    #----------------------admin commands----------------------
                    if user in users.admins:
                        if command[0] == "!start":
                            newTime = -1
                            if len(command)==1:
                                newTime = datetime.datetime.now()
                            elif len(command)==2:
                                newTime = command[1]
                                try:
                                    newTime = datetime.datetime.fromisoformat(newTime)
                                except ValueError:
                                    currentChat.message("Invalid date format. Must be of this format: 2018-12-29@09:00")
                            else:
                                currentChat.message("Invalid date format. Must be of this format: 2018-12-29@09:00")
                            if type(newTime) == datetime.datetime:
                                startTime = newTime
                                with open('settings.json', 'r+') as f:
                                    j = json.load(f)
                                    j['start-time'] = startTime.isoformat().split(".")[0]
                                    f.seek(0)
                                    json.dump(j, f, indent=4)
                                    f.truncate()
                                currentChat.message("The race start time has been set to " + startTime.isoformat().split(".")[0])
                                for player in playerLookup.keys():
                                    playerLookup[player].calculateCompletionTime(startTime)
                                redraw = True
                        elif command[0] == "!forcequit":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                    playerLookup[player].fail("quit", startTime)
                                    redraw = True
                                    currentChat.message(command[1] + " has been forcequit.")
                        elif command[0] == "!noshow":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                playerLookup[player].fail("noshow", startTime)
                                redraw = True
                                currentChat.message(command[1] + " set to No-show.")
                        elif command[0] == "!dq":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                    playerLookup[player].fail("disqualified", startTime)
                                    redraw = True
                                    currentChat.message(command[1] + " has been disqualified.")
                        elif command[0] == "!revive":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "done":
                                    playerLookup[player].collects -= 1
                                playerLookup[player].status = "live"
                                redraw = True
                                currentChat.message(command[1] + " has been revived.")
                        elif command[0] == "!settime":
                            if len(command) == 3 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "done" or playerLookup[player].status == "quit":
                                    newTime = command[2]
                                    stringTime = command[2]
                                    newTime = newTime.split(":")
                                    if len(newTime) == 3:
                                        duration = int(newTime[2]) + 60*int(newTime[1]) + 3600*int(newTime[0])
                                        playerLookup[player].duration = duration
                                        playerLookup[player].completionTime = stringTime
                                        playerLookup[player].manualDuration(startTime)
                                        redraw = True
                                        currentChat.message(command[1]+"'s time has been updated.")
                        elif command[0] == "!blacklist" and len(command) == 2:
                            if command[1] not in users.blacklist:
                                users.add(command[1],users.Role.BLACKLIST)
                                if command[1] in users.updaters:
                                    users.remove(command[1],users.Role.UPDATER)
                                currentChat.message(command[1] + " has been blacklisted.")
                            else:
                                currentChat.message(command[1] + " is already blacklisted.")
                        elif command[0] == "!unblacklist" and len(command) == 2:
                            if command[1] in users.blacklist:
                                users.remove(command[1],users.Role.BLACKLIST)
                                currentChat.message(command[1] + " is no longer blacklisted.")
                            else:
                                currentChat.message(command[1] + " is already not blacklisted.")
                        elif command[0] == "!admin" and len(command) == 2:
                            if command[1] not in users.admins:
                                users.add(command[1],users.Role.ADMIN)
                                currentChat.message(command[1] + " is now an admin.")
                            else:
                                currentChat.message(command[1] + " is already an admin.")

            if redraw:
                if mode == "602":
                    screen = mode_602.draw(screen, playerLookup)
                elif mode == "1120":
                    screen = mode_1120.draw(screen, playerLookup)
                pygame.display.flip()
                redraw = False

        except Exception as e:
            print(traceback.format_exc())

pygame.quit()
