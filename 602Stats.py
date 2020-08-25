import socket
import math
import sys
import pygame
import datetime
import pickle
import random
import json
import traceback
import requests
import urllib
import os
import time
import threading
import chatroom
import srl
import twitch
import player
import google_sheets
import users

#----------------function definitions------------------
def draw(screen, playerLookup):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))

    #------sorting runners for display------
    sortedRacers = []
    for key in playerLookup:
        if len(sortedRacers) == 0:
            sortedRacers.append(key)
        elif playerLookup[key].collects == 602:
            added = False
            for index, racer in enumerate(sortedRacers):
                if added:
                    pass
                elif playerLookup[racer].collects < 602:
                    sortedRacers.insert(index, key)
                    added = True
                elif playerLookup[key].duration < playerLookup[racer].duration:
                    sortedRacers.insert(index, key)
                    added = True
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    added = True
        else:
            added = False
            for index, racer in enumerate(sortedRacers):
                if added:
                    pass
                elif playerLookup[key].collects >= playerLookup[racer].collects:
                    sortedRacers.insert(index, key)
                    added = True
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    added = True

    #---------place number assignments--------
    for index, racer in enumerate(sortedRacers):
        if index == 0:
            playerLookup[racer].place = 1
        else:
            current = playerLookup[racer]
            previous = playerLookup[sortedRacers[index-1]]
            if current.collects != 602:
                if current.collects == previous.collects:
                    current.place = previous.place
                else:
                    playerLookup[racer].place = index+1
            else:
                playerLookup[racer].place = index+1

    #------------slot assignments-----------
    for index, p in enumerate(sortedRacers):
        if index+2 < 25:
            playerLookup[p].corner = slots[index+2]
        else:
            playerLookup[p].corner = slots[25]

    # racerIndex=0
    # for s in range(0,25):
    #     if s <= 2: #leaving empty slots for spacing
    #         pass
    #     elif racerIndex < 25:
    #         playerLookup[sortedRacers[racerIndex]].corner = slots[s]
    #         racerIndex+=1
    #     else:
    #         playerLookup[sortedRacers[racerIndex]].corner = [1600, 900]
    #         racerIndex+=1

    #-----------scorecard drawing------------
    for key in playerLookup:
        currentPlayer = playerLookup[key]
        corner = currentPlayer.corner
        #pygame.draw.rect(screen, (25, 25, 25), [corner[0]-3, corner[1]-3, 393, 181])
        pygame.draw.rect(screen, (25, 25, 25), [corner[0], corner[1], 314, 174])

        score = currentPlayer.collects
        if currentPlayer.status == "live":
            # if currentPlayer.place <=3:
            #     completion = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (239,195,0))
            # else:
            #     completion = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))
            # screen.blit(completion, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

            sm64count = 0
            smgcount = 0
            smscount = 0
            smg2count = 0
            if score < 120:
                test = pygame.transform.scale(sm64BG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = score
            elif score < 240:
                test = pygame.transform.scale(smgBG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = score-120
            elif score < 360:
                test = pygame.transform.scale(smsBG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = 120
                smscount = score-240
            elif score < 602:
                test = pygame.transform.scale(smg2BG,(306,166))
                screen.blit(test, (corner[0]+4, corner[1]+4))
                sm64count = 120
                smgcount = 120
                smscount = 120
                smg2count = score-360

            smallBar = 110 #136
            largeBar = 260 #322
            barHeight = 20
            sm64length = math.floor((sm64count/120)*smallBar)
            smglength = math.floor((smgcount/120)*largeBar)
            smslength = math.floor((smscount/120)*smallBar)
            smg2length = math.floor((smg2count/242)*largeBar)

            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 110+corner[1], largeBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [190+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 140+corner[1], largeBar+4, barHeight])
            if score > 0:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 80+corner[1]+2, sm64length, barHeight-4])
            if score > 120:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 110+corner[1]+2, smglength, barHeight-4])
            if score > 240:
                pygame.draw.rect(screen, (150,150,150,254), [190+corner[0]+2, 80+corner[1]+2, smslength, barHeight-4])
            if score > 360:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 140+corner[1]+2, smg2length, barHeight-4])

            sm64color = (220,220,220)
            smscolor = (220,220,220)
            smgcolor = (220,220,220)
            smg2color = (220,220,220)
            if sm64count > 9:
                sm64color = (60,60,60)
            if smgcount > 9:
                smgcolor = (60,60,60)
            if smscount > 9:
                smscolor = (60,60,60)
            if smg2count > 9:
                smg2color = (60,60,60)

            #------------individual game scores & icons--------------
            screen.blit(star, (6+corner[0], 75+corner[1]) )
            label = getFont(18).render(str(sm64count), 1, sm64color)
            screen.blit(label, (45+corner[0], 79+corner[1]))

            screen.blit(luma, (6+corner[0], 103+corner[1]) )
            label = getFont(18).render(str(smgcount), 1, smgcolor)
            screen.blit(label, (45+corner[0], 109+corner[1]))

            screen.blit(shine, (157+corner[0], 70+corner[1]) )
            label = getFont(18).render(str(smscount), 1, smscolor)
            screen.blit(label, (195+corner[0], 79+corner[1]))

            screen.blit(yoshi, (6+corner[0], 137+corner[1]) )
            label = getFont(18).render(str(smg2count), 1, smg2color)
            screen.blit(label, (45+corner[0], 139+corner[1]))

        elif currentPlayer.status == "done":    #shows done tag

            test = pygame.transform.scale(finishBG,(306,166))
            screen.blit(test, (corner[0]+4, corner[1]+4))

            # screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(70).render("Done!", 1, (220,220,220))
            screen.blit(doneTag, (90+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            label = getFont(24).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (220,220,220))
            screen.blit(label, (70+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "quit":    #shows quit tag

            quitTag = getFont(70).render("Quit", 1, (255, 0, 0))
            screen.blit(quitTag, (100+currentPlayer.corner[0], 55+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602 in "+currentPlayer.completionTime, 1, (220,220,220))
            screen.blit(label, (5+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "disqualified":    #shows disqualified tag
            forfeitTag = getFont(50).render("Disqualified", 1, (255, 0, 0))
            screen.blit(forfeitTag, (40+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (65+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "noshow":    #shows no-show tag
            forfeitTag = getFont(50).render("No-Show", 1, (255, 0, 0))
            screen.blit(forfeitTag, (75+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (65+currentPlayer.corner[0], 140+currentPlayer.corner[1]))


        #-------scorecard header-------
        screen.blit(currentPlayer.profile, (10+currentPlayer.corner[0], 10+currentPlayer.corner[1])) #profile picture

        color = (220,220,220)
        if currentPlayer.place <=3:
            color = (239,195,0)
        nameRender = getFont(24).render(str(currentPlayer.nameCaseSensitive), 1, color)
        placeRender = getFont(45).render(str(currentPlayer.place), 1, color)

        screen.blit(nameRender, (75+currentPlayer.corner[0], 22+currentPlayer.corner[1])) #name

        if currentPlayer.place > 9:
            screen.blit(placeRender, (260+currentPlayer.corner[0], 8+currentPlayer.corner[1]))
        else:
            screen.blit(placeRender, (280+currentPlayer.corner[0], 8+currentPlayer.corner[1]))


    pygame.display.flip()
    return screen

def status(user):
    returnString = user + ": "
    if user in users.racersL:
        returnString += "Racer ("+playerLookup[user].status +"), "
    if user in users.admins:
        returnString += "Admin, "
    if user in users.updaters:
        returnString += "Updater, "
    if user in users.blacklist:
        returnString += "Blacklist, "
    if returnString == (user + ": "):
        returnString += "None, "
    return returnString[0:-2]

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
        CHANNEL = "#" + j['test-chat']
    else:
        CHANNEL = "#" + j['main-chat']
    debug = json.loads(j['debug'].lower())
    startTime = datetime.datetime.fromisoformat(j['start-time'])
    use_backups = json.loads(j['use-player-backups'].lower())

twitch.fetchProfiles(users.racersL)

#----------player object & slot assignments-------------
#387 x 175 scorecards
# slots = [
#     (10,160),(407,160),(804,160),(1201,160),
#     (10,345),(407,345),(804,345),(1201,345),
#     (10,530),(407,530),(804,530),(1201,530),
#     (10,715),(407,715),(804,715),(1201,715), (1600,900)
# ]
#314 x 174 scorecards
slots = [
    (5,5),  (324,5),  (643,5),  (962,5),  (1281,5),
    (5,184),(324,184),(643,184),(962,184),(1281,184),
    (5,363),(324,363),(643,363),(962,363),(1281,363),
    (5,542),(324,542),(643,542),(962,542),(1281,542),
    (5,721),(324,721),(643,721),(962,721),(1281,721),
    (1600,900)
]

playerLookup = {}
if use_backups:
    for racer in users.racersL:
        pass
        # with open("./backup/"+racer+".obj", 'rb') as f:
        #     playerLookup[racer] = pickle.load(f)
else:
    print("Joining Twitch channels...", end="", flush=True)
    for racer in users.racersCS:
        playerLookup[racer.lower()] = player.Player(racer, NICK, PASSWORD, debug)
    print(" Done.")

#---------------------pygame setup----------------------
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("Multi-Mario Stats Program")
star  = pygame.image.load('./resources/star.png')
shine = pygame.image.load('./resources/shine.png')
luma  = pygame.image.load('./resources/luma.png')
yoshi = pygame.image.load('./resources/yoshi.png')
background = pygame.image.load('./resources/background.png')
sm64BG = pygame.image.load('./resources/sm64.png')
smgBG = pygame.image.load('./resources/smg.png')
smsBG = pygame.image.load('./resources/sms.png')
smg2BG = pygame.image.load('./resources/smg2.png')
finishBG = pygame.image.load('./resources/finish.png')

def getFont(size):
    return pygame.font.Font("./resources/Lobster 1.4.otf", size)

screen = draw(screen, playerLookup)
pygame.display.flip()
redraw = False

#------------create and start irc threads------------
for player in playerLookup.keys():
    room = playerLookup[player].chat
    t = threading.Thread(target=fetchIRC, args=(room,))
    t.start()

mainChat = chatroom.ChatRoom(CHANNEL, NICK, PASSWORD)
t = threading.Thread(target=fetchIRC, args=(mainChat,))
t.start()
#SRL = threading.Thread(target=srl.srlThread, args=("#speedrunslive", mainChat,))
#SRL.start()
#--------------------main bot loop--------------------
done = False
while not done:
    for i in range(0, len(users.racersL)+1):

        if i == len(users.racersL):
            currentChat = mainChat
        else:
            currentChat = playerLookup[users.racersL[i]].chat

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
                            statusMsg = status(user)
                        else:
                            statusMsg = status(command[1])
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
                                playerLookup[user].collects = 601
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
                                playerLookup[player].status = "live"
                                if playerLookup[player].collects == 602:
                                    playerLookup[player].collects = 601
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
                screen = draw(screen, playerLookup)
                pygame.display.flip()
                redraw = False

        except Exception as e:
            print(traceback.format_exc())

pygame.quit()
