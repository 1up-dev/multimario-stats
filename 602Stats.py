import socket
import math
import pygame
import datetime
import pickle
import random
import json
import requests
import urllib
import os
import time

#-----------------object definitions-------------------
class playerObject:
    def __init__(self, name):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.collects = random.choice(range(0,602))
        self.status = "live"
        self.completionTime = "HH:MM:SS"
        self.failTime = "HH:MM:SS"
        self.place = 1
        try:
            self.profile = pygame.transform.scale(pygame.image.load("./profiles/{0}.png".format(name)), (60,60))
        except pygame.error:
            self.profile = pygame.transform.scale(pygame.image.load("./602files/error.png"), (60,60))
        #time.sleep(1)
        #self.chat = ChatRoom("#"+name, NICK, PASSWORD)

    def finish(self):
        cycleTime = datetime.datetime.now()

        tmp1 = datetime.timedelta(seconds=math.floor((cycleTime - startTime).total_seconds()))
        delta = str(tmp1).split(" days,")

        extraHours = 0
        if len(delta)==1:
            delta = delta[0]
            pass
        elif len(delta)==2:
            days = delta[0]
            days = int(days)
            extraHours = days * 24
            delta = delta[1]

        finalTime = delta.split(":")
        preHours = int(finalTime[0])
        finalHours = preHours + extraHours
        finishTime = str(finalHours)+":"+finalTime[1]+":"+finalTime[2]

        finishers.append(self.name)
        mainChat.message(self.nameCaseSensitive + " has finished!")
        self.completionTime = finishTime
        self.status = "done"

    def unfinish(self):
        finishers.remove(self.name)
        self.collects = 601

    def fail(self, status):
        cycleTime = datetime.datetime.now()
        failTime = str(datetime.timedelta(seconds=(math.floor((cycleTime - startTime).total_seconds()))))
        self.failTime = failTime
        self.status = status

    def hasCollected(self):
        tempStars = self.collects
        game=""
        buffer=""
        noun="Star"
        if tempStars <= 120:
            game="Super Mario 64"
        elif tempStars <= 240:
            game="Super Mario Galaxy"
            tempStars -= 120
        elif tempStars <= 360:
            game="Super Mario Sunshine"
            tempStars -= 240
            noun="Shine"
        elif tempStars <= 602:
            game="Super Mario Galaxy 2"
            tempStars -= 360
        if tempStars is not 1:
            buffer = "s"
        mainChat.message(self.nameCaseSensitive + " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + ".")

class ChatRoom:
    def __init__(self, channel, nick, password):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.NICK = nick
        self.PASSWORD = password
        self.channel = channel
        self.currentSocket = socket.socket()
        self.inputBuffer = ""
        self.reconnect()
    def message(self, msg):
        try:
            self.currentSocket.send(bytes("PRIVMSG "+self.channel+" :"+msg+"\n", "UTF-8"))
        except socket.error:
            print("Socket error.")
    def reconnect(self):
        self.currentSocket = socket.socket()
        self.currentSocket.connect((self.HOST,self.PORT))
        self.currentSocket.send(bytes("PASS "+self.PASSWORD+"\n", "UTF-8"))
        self.currentSocket.send(bytes("NICK "+self.NICK+"\n", "UTF-8"))
        self.currentSocket.send(bytes("JOIN "+self.channel+"\n", "UTF-8"))
        self.currentSocket.send(bytes("CAP REQ :twitch.tv/tags twitch.tv/commands\n", "UTF-8"))
        timeNow = datetime.datetime.now().isoformat()
        timeNow = timeNow.split("T")
        timeNow = timeNow[0] + "@" + timeNow[1].split(".")[0]
        self.currentSocket.send(bytes("PRIVMSG "+self.channel+" :"+"602 Stats Bot joined "+self.channel+" on "+timeNow+"\n", "UTF-8"))
        print("[IRC] "+ timeNow + ": Joined Twitch channel "+self.channel+".")
    def pong(self):
        try:
            self.currentSocket.send(bytes("PONG tmi.twitch.tv\r\n", "UTF-8"))
            timeNow = datetime.datetime.now().isoformat()
            timeNow = timeNow.split("T")
            timeNow = timeNow[0] + "@" + timeNow[1].split(".")[0]
            print("[IRC] "+ timeNow +": Pong attempted.")
        except socket.error:
            print("Socket error.")

#----------------function definitions------------------
def assignPlaces(playerLookup):
    scores = {}
    place = 1

    for finisher in finishers:
        playerLookup[finisher].place = place
        place += 1

    for key in playerLookup:
        if playerLookup[key].status != "done":
            totalScore =  playerLookup[key].collects
            if totalScore in scores.keys():
                scores[totalScore].append(playerLookup[key].name)
            else:
                scores[totalScore] = [playerLookup[key].name]
    array = sorted(scores.keys(), reverse = True)

    for score in array:
        count = 0
        for player in scores[score]:
            count+=1
            playerLookup[player].place = place
        place += count

#todo info on scorecard after dq/forfeit (how long they played, how many stars they had)
#todo scorecard/profile borders
def draw(screen, playerLookup):
    screen.blit(pygame.transform.scale(background, (1600,900)), (0,0))

    #------sorting runners for display------
    sortedRacers = []
    for key in playerLookup:
        if len(sortedRacers) == 0:
            sortedRacers.append(key)
        else:
            added = False
            for index, racer in enumerate(sortedRacers):
                if added:
                    pass
                elif playerLookup[key].place < playerLookup[racer].place:
                    sortedRacers.insert(index, key)
                    added = True
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    added = True

    #------------slot assignments-----------
    racerIndex=0
    for s in range(0,len(racers)):
        if s==-1: #leaving empty slots for spacing
            pass
        else:
            if racerIndex >= len(sortedRacers):
                pass
            else:
                playerLookup[sortedRacers[racerIndex]].corner = slots[s]
                racerIndex+=1

    #-----------scorecard drawing------------
    for key in playerLookup:
        currentPlayer = playerLookup[key]
        corner = currentPlayer.corner
        pygame.draw.rect(screen, (25, 25, 25), [corner[0]-3, corner[1]-3, 393, 181])

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
                screen.blit(sm64BG, (corner[0], corner[1]))
                sm64count = score
            elif score < 240:
                screen.blit(smgBG, (corner[0], corner[1]))
                sm64count = 120
                smgcount = score-120
            elif score < 360:
                screen.blit(smsBG, (corner[0], corner[1]))
                sm64count = 120
                smgcount = 120
                smscount = score-240
            elif score < 602:
                screen.blit(smg2BG, (corner[0], corner[1]))
                sm64count = 120
                smgcount = 120
                smscount = 120
                smg2count = score-360

            smallBar = 136
            largeBar = 322
            barHeight = 20
            sm64length = math.floor((sm64count/120)*smallBar)
            smglength = math.floor((smgcount/120)*largeBar)
            smslength = math.floor((smscount/120)*smallBar)
            smg2length = math.floor((smg2count/242)*largeBar)

            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 110+corner[1], largeBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [225+corner[0], 80+corner[1], smallBar+4, barHeight])
            pygame.draw.rect(screen, (40,40,40), [40+corner[0], 140+corner[1], largeBar+4, barHeight])
            if score > 0:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 80+corner[1]+2, sm64length, barHeight-4])
            if score > 120:
                pygame.draw.rect(screen, (150,150,150,254), [40+corner[0]+2, 110+corner[1]+2, smglength, barHeight-4])
            if score > 240:
                pygame.draw.rect(screen, (150,150,150,254), [225+corner[0]+2, 80+corner[1]+2, smslength, barHeight-4])
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
            screen.blit(SM64, (6+corner[0], 75+corner[1]) )
            label = getFont(18).render(str(sm64count), 1, sm64color)
            screen.blit(label, (45+corner[0], 79+corner[1]))

            screen.blit(SMG, (6+corner[0], 103+corner[1]) )
            label = getFont(18).render(str(smgcount), 1, smgcolor)
            screen.blit(label, (45+corner[0], 109+corner[1]))

            screen.blit(SMS, (188+corner[0], 70+corner[1]) )
            label = getFont(18).render(str(smscount), 1, smscolor)
            screen.blit(label, (230+corner[0], 79+corner[1]))

            screen.blit(SMG2, (6+corner[0], 137+corner[1]) )
            label = getFont(18).render(str(smg2count), 1, smg2color)
            screen.blit(label, (45+corner[0], 139+corner[1]))

        elif currentPlayer.status == "done":    #shows done tag
            screen.blit(finishBG, (playerLookup[key].corner[0], playerLookup[key].corner[1]))
            doneTag = getFont(70).render("Done!", 1, (220,220,220))
            screen.blit(doneTag, (120+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            label = getFont(24).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "quit":    #shows quit tag
            quitTag = getFont(70).render("Quit", 1, (255, 0, 0))
            screen.blit(quitTag, (130+currentPlayer.corner[0], 55+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "disqualified":    #shows disqualified tag
            forfeitTag = getFont(50).render("Disqualified", 1, (255, 0, 0))
            screen.blit(forfeitTag, (80+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

        elif currentPlayer.status == "noshow":    #shows no-show tag
            forfeitTag = getFont(50).render("No-Show", 1, (255, 0, 0))
            screen.blit(forfeitTag, (110+currentPlayer.corner[0], 70+currentPlayer.corner[1]))

            label = getFont(24).render("Completion: "+str(score)+"/602", 1, (220,220,220))
            screen.blit(label, (100+currentPlayer.corner[0], 140+currentPlayer.corner[1]))


        #-------scorecard header-------
        screen.blit(currentPlayer.profile, (10+currentPlayer.corner[0], 10+currentPlayer.corner[1])) #profile picture

        if currentPlayer.place <=3:
            nameRender = getFont(28).render(str(currentPlayer.nameCaseSensitive), 1, (239,195,0))
            placeRender = getFont(45).render(str(currentPlayer.place), 1, (239,195,0))
        else:
            nameRender = getFont(28).render(str(currentPlayer.nameCaseSensitive), 1, (220,220,220))
            placeRender = getFont(45).render(str(currentPlayer.place), 1, (200,200,200))

        screen.blit(nameRender, (80+currentPlayer.corner[0], 20+currentPlayer.corner[1])) #name

        if currentPlayer.place > 9:
            screen.blit(placeRender, (335+currentPlayer.corner[0], 8+currentPlayer.corner[1]))
        else:
            screen.blit(placeRender, (350+currentPlayer.corner[0], 8+currentPlayer.corner[1]))


    pygame.display.flip()
    return screen

def pushUpdaters():
    with open("updaters.txt", "w") as updaterFile:
        for updater in updaters:
            if updater.index == len(updaters)-1:
                updaterFile.write(updater)
            else:
                updaterFile.write(updater+"\n")

def fetchProfiles(users):
    with open ('settings.txt') as f:
        settingsFile = f.read()
        CLIENT_ID = settingsFile.split("Twitch developer app Client-ID: ")[1].split()[0]
    for user in users:
        if not os.path.isfile("./profiles/"+user+".png"):
            url = "https://api.twitch.tv/helix/users?login="+user
            headers = {"Client-ID":CLIENT_ID}
            response = requests.get(url, headers=headers)
            #data={}

            if response.status_code in range(200,300):
                responseData = json.loads(response.content.decode("UTF-8"))['data']
                if len(responseData)==0:
                    print("[API] Twitch user "+user+" does not exist. Using default image.")
                    #playerLookup[user].validTwitchAccount = False
                    #todo if twitch account does not exist, don't try to join its chat
                else:
                    data = responseData[0]
                    profileLocation = data['profile_image_url']
                    urllib.request.urlretrieve(profileLocation, "."+"/profiles/"+user+".png")
                    print("[API] Fetched profile of Twitch user "+user+".")
            else:
                print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
                return None
    return

def fetchIRC(thisChat):
    while True:
        readbuffer = thisChat.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
        thisChat.inputBuffer += readbuffer

#---------loading & processing external data-------------
with open('racers.txt') as f:
    racersCaseSensitive = f.read().split("\n")
    racers = []
    for r in racersCaseSensitive:
        r.rstrip()
        if r=="" or r==" ":
            racersCaseSensitive.remove(r)
    for r in racersCaseSensitive:
        racers.append(r.lower())
with open('updaters.txt') as f:
    updaters = f.read().lower().split("\n")
    for u in updaters:
        u.rstrip()
        if u=="" or u==" ":
            updaters.remove(u)
with open('admins.txt') as f:
    admins = f.read().lower().split("\n")
    for a in admins:
        a.rstrip()
        if a=="" or a==" ":
            admins.remove(a)
with open ('settings.txt') as f:
    file = f.read()
    NICK = file.split("Twitch Username for Bot: ")[1].split()[0]
    PASSWORD = file.split("Twitch Chat Authentication Token: ")[1].split()[0]
    CHANNEL = file.split("Main Twitch Chat for Bot: ")[1].split()[0]

for racer in racers:
    if racer not in updaters:
        updaters.append(racer)
        pushUpdaters()

with open("./602files/startingTime.obj", 'rb') as objIn:
    startTime = pickle.load(objIn)

fetchProfiles(racers)

#----------player object & slot assignments-------------
slots = [
    (10,160),(407,160),(804,160),(1201,160),
    (10,345),(407,345),(804,345),(1201,345),
    (10,530),(407,530),(804,530),(1201,530),
    (10,715),(407,715),(804,715),(1201,715), (1600,900)
]
playerLookup = {}
finishers = []
for racer in racersCaseSensitive:
    playerLookup[racer.lower()] = playerObject(racer)
assignPlaces(playerLookup)

#--------------------pygame settings--------------------
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("602 Stats Program")
screen.fill((16,16,16))

SM64= pygame.image.load('./602files/star.png')
SMS = pygame.image.load('./602files/shine.png')
SMG = pygame.image.load('./602files/luma.png')
SMG2 = pygame.image.load('./602files/yoshi.png')

background = pygame.image.load('./602files/bgtest.png')

sm64BG = pygame.image.load('./602files/sm64bg.png')
smgBG = pygame.image.load('./602files/smgbg.png')
smsBG = pygame.image.load('./602files/smsbg.png')
smg2BG = pygame.image.load('./602files/smg2bg.png')
finishBG = pygame.image.load('./602files/602bg.png')

def getFont(size):
    return pygame.font.SysFont("Lobster 1.4", size)

screen = draw(screen, playerLookup)
pygame.display.flip()
redraw = False

#todo join srl chat with a thread and set start time
#--------------------main bot loop--------------------
mainChat = ChatRoom(CHANNEL, NICK, PASSWORD)
done = False
while not done:
    for i in range(0, len(racers)+1):
        '''
        if i == len(racers):
            currentChat = mainChat
            currentChannel = "602race"
        else:
            currentChat = playerLookup[racers[i]].chat
            currentChannel = racers[i]
        '''
        #todo remove these two lines to check the other chats
        currentChat = mainChat
        currentChannel = "602race"

        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done=True
            #--------------------reading from twitch chat--------------------
            lines=""
            try: #todo move this into chatroom object in order to stop it from halting the loop
                readbuffer = currentChat.currentSocket.recv(1024).decode("UTF-8", errors = "ignore")
                lines = readbuffer.split("\n")
            except socket.error as e:
                print("[!] Socket Error:", e)
                pass

            print(lines)
            for line in lines:
                out = ""
                user = ""
                line = line.rstrip().split()

                ismod = False
                if len(line) > 0:
                    if line[0][0] == "@":
                        tags = line[0]
                        del line[0]
                        modstatus = tags.split("mod=")[1][0]
                        if (modstatus == "1") or (user == currentChannel):
                            ismod = True

                for index, word in enumerate(line):
                    if index == 0:
                        user = word.split('!')[0]
                        user = user[0:24]
                    if index == 3:
                        out += word
                        out = out[1:]
                    if index >= 4:
                        out += " " + word

                if user == "PING":
                    currentChat.pong()
                elif len(out) > 0:
                    user = user.lower()[1:]
                    out = out.lower()
                    command = out.split(" ")

                    #todo allow add command to work if racer is finished, so anyone can undo a finish
                    #todo maybe instead: allow racers to unfinish themselves

                    #----------------------racer commands----------------------
                    if user in racers:
                        if playerLookup[user].status == "live":
                            if command[0] == "!add" and len(command) == 2: #and user == player.name
                                number = int(command[1])
                                if 0 <= playerLookup[user].collects + number <= 602:
                                    playerLookup[user].collects += number
                                    if playerLookup[user].collects == 602:
                                        playerLookup[user].finish()
                                    else:
                                        playerLookup[user].hasCollected()
                                    redraw = True
                            elif command[0] == "!quit":
                                playerLookup[user].fail("quit")
                                redraw = True
                                currentChat.message(playerLookup[user].nameCaseSensitive + "has quit.")
                        if user not in admins:
                            if command[0] == "!mod" and len(command) == 2:
                                if command[1] not in updaters:
                                    updaters.append(command[1])
                                    pushUpdaters()
                                    currentChat.message(command[1] + " is now an updater.")
                                else:
                                    currentChat.message(command[1] + " is already an updater.")
                            elif command[0] == "!unmod" and len(command) == 2:
                                if command[1] in updaters:
                                    updaters.remove(command[1])
                                    pushUpdaters()
                                    currentChat.message(command[1] + " is no longer an updater.")
                                else:
                                    currentChat.message(command[1] + " is already not an updater.")

                    #--------------------updater commands----------------------
                    if (user in updaters) or ismod:
                        if command[0] == "!add" and len(command) == 3:
                            if command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live":
                                    number = int(command[2])
                                    if 0 <= playerLookup[player].collects + number <= 602:
                                        playerLookup[player].collects += number
                                        if playerLookup[player].collects == 602:
                                            playerLookup[player].finish()
                                        else:
                                            playerLookup[player].hasCollected()
                                        redraw = True
                        elif command[0] == "!add" and len(command) == 2 and user not in racers:
                            currentChat.message(user+", you're not a racer! Please specify whose star count you would like to update. (!add odme_ 2)")
                            #placeholder to allow me to collapse this line of code

                    #----------------------admin commands----------------------
                    if user in admins:
                        if command[0] == "!start":
                            #todo allow admin to set start time to a specific date & time (2018-12-29 09:00)

                            startTime = datetime.datetime.now()
                            with open("./602files/startingTime.obj", 'wb') as output:
                                pickle.dump(startTime, output, pickle.HIGHEST_PROTOCOL)
                            now = datetime.datetime.now().isoformat().split("T")
                            now = now[0] + " @ " + now[1].split(".")[0]
                            currentChat.message("The race has started, on " + now)
                        elif command[0] == "!mod" and len(command) == 2:
                            if command[1] not in updaters:
                                updaters.append(command[1])
                                pushUpdaters()
                                currentChat.message(command[1] + " is now an updater.")
                            else:
                                currentChat.message(command[1] + " is already an updater.")
                        elif command[0] == "!unmod" and len(command) == 2:
                            if command[1] in updaters:
                                updaters.remove(command[1])
                                pushUpdaters()
                                currentChat.message(command[1] + " is no longer an updater.")
                            else:
                                currentChat.message(command[1] + " is already not an updater.")
                        elif command[0] == "!forcequit":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                    if playerLookup[player].status == "done":
                                        finishers.remove(player)
                                    playerLookup[player].fail("quit")
                                    redraw = True
                                    currentChat.message(command[1] + " has been forcequit.")
                        elif command[0] == "!noshow":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "done":
                                    finishers.remove(player)
                                playerLookup[player].fail("noshow")
                                redraw = True
                                currentChat.message(command[1] + " set to No-show.")
                        elif command[0] == "!dq":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                    if playerLookup[player].status == "done":
                                        finishers.remove(player)
                                    playerLookup[player].fail("disqualified")
                                    redraw = True
                                    currentChat.message(command[1] + " has been disqualified.")
                        elif command[0] == "!revive":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                playerLookup[player].status = "live"
                                if playerLookup[player].collects == 602:
                                    playerLookup[player].unfinish()
                                redraw = True
                                currentChat.message(command[1] + " has been revived.")

            if redraw:
                assignPlaces(playerLookup)
                screen = draw(screen, playerLookup)
                pygame.display.flip()
                redraw = False

        except Exception as e:
            print("[!] Exception:", e)
            pass

pygame.quit()
