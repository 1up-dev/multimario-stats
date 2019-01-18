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
#reference: https://www.twitch.tv/videos/74943470

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
        self.validTwitchAccount = True
        try:
            self.profile = pygame.transform.scale(pygame.image.load("./profiles/{0}.bmp".format(name)), (50,50))
        except pygame.error:
            self.profile = pygame.transform.scale(pygame.image.load("./602files/error.bmp"), (50,50))

        if self.validTwitchAccount:
            print("",end="")
            #self.chat = ChatRoom(name, NICK, PASSWORD)
            #ABOVE WILL JOIN EACH PLAYER'S CHAT ON CREATION OF PLAYEROBJECT

    def finish(self):
        cycleTime = datetime.datetime.now()
        finishTime = str(datetime.timedelta(seconds=(math.floor((cycleTime - startTime).total_seconds()))))
        finishers.append(self.name)
        mainChat.message(self.nameCaseSensitive + " has finished!")
        self.completionTime = finishTime
        self.status = "done"

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

    for key in playerLookup:
        #if playerLookup[key].status != "forfeit" and playerLookup[key].status != "disqualified":
            totalScore =  playerLookup[key].collects
            if totalScore in scores.keys():
                scores[totalScore].append(playerLookup[key].name)
            else:
                scores[totalScore] = [playerLookup[key].name]

    array = sorted(scores.keys(), reverse = True)

    if array[0] == 602:
        array = array[1:]

    for finisher in finishers:
        playerLookup[finisher].place = place
        place += 1

    for score in array:
        for player in scores[score]:
            playerLookup[player].place = place
        place += 1

#todo show info on player slot after dq/forfeit (how long they played, how many stars they had)
#todo transparency with current game picture behind
#todo slot outlines, profile picture outlines
#todo redo scoreboard layout, all on left side with place number on right side instead of on top
def draw(screen, playerLookup):

    sortedRacers = []
    for key in playerLookup:
        if len(sortedRacers) == 0:
            sortedRacers.append(key)
        else:
            added = False
            for index, racer in enumerate(sortedRacers):
                if added:
                    pass
                elif playerLookup[key].collects > playerLookup[racer].collects:
                    sortedRacers.insert(index, key)
                    added = True
                elif index == len(sortedRacers)-1:
                    sortedRacers.append(key)
                    added = True

    racerIndex=0
    for index in range(0,25):
        if index==11 or index==12 or index==13: #leaving empty slots for timer and spacing
            pass
        else:
            if racerIndex >= len(sortedRacers):
                pass
            else:
                playerLookup[sortedRacers[racerIndex]].corner = slots[index]
                racerIndex+=1

    for key in playerLookup:
        currentPlayer = playerLookup[key]

        pygame.draw.rect(screen, (25,25,25), [currentPlayer.corner[0], currentPlayer.corner[1], 253, 55]) #upper background
        placeRender = getFont(40).render(str(currentPlayer.place), 1, (200,200,200))

        if currentPlayer.place > 9:
            screen.blit(placeRender, (205+currentPlayer.corner[0], 4+currentPlayer.corner[1]))
        else:
            screen.blit(placeRender, (220+currentPlayer.corner[0], 4+currentPlayer.corner[1]))

        screen.blit(currentPlayer.profile, (3+currentPlayer.corner[0], 3+currentPlayer.corner[1])) #profile picture

        nameRender = getFont(20).render(str(currentPlayer.nameCaseSensitive), 1, (200,200,200)) #name
        screen.blit(nameRender, (60+currentPlayer.corner[0], 5+currentPlayer.corner[1])) #name

        lowerRect = pygame.Rect([currentPlayer.corner[0], 55+currentPlayer.corner[1], 253, 86])

        if currentPlayer.status == "live":
            screen.blit(ScoreCard, (1+currentPlayer.corner[0], 55+currentPlayer.corner[1])) #scorecard
            score = currentPlayer.collects

            if currentPlayer.place <=3:
                label = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (239,195,0))
            else:
                label = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))

            screen.blit(label, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

            if score < 120:    #draws scores while playing SM64
                screen.blit(SM64Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                length = math.floor((score/120)*93)
                if score != 0:
                    pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], length, 7])

                label = getFont(12).render(str(score), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))

            elif score < 240:    #draws scores while playing SMG
                screen.blit(SMGLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-120)/120)*93)
                if score != 120:
                    pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], length, 7])

                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str(score-120), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))

            elif score < 360:    #draws scores while playing SMS
                screen.blit(SMSLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-240)/120)*93)
                if score != 240:
                    pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 101+playerLookup[key].corner[1], length, 7])

                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str(score-240), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = getFont(12).render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))

            elif score < 602:    #draws scores while playing SMG2
                screen.blit(SMG2Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 101+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-360)/242)*218)
                if score != 360:
                    pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 129+playerLookup[key].corner[1], length, 7])

                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = getFont(12).render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = getFont(12).render(str(score-360), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))

        elif currentPlayer.status == "done":    #shows done tag
            pygame.draw.rect(screen, (25,25,25), lowerRect)
            forfeitTag = getFont(70).render("Done!", 1, (0, 127, 255))
            screen.blit(forfeitTag, (50+currentPlayer.corner[0], 55+currentPlayer.corner[1]))

            label = getFont(16).render(str("Final Time: {0}".format(currentPlayer.completionTime)), 1, (140,140,156))
            screen.blit(label, (59+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

        elif currentPlayer.status == "quit":    #shows quit tag
            pygame.draw.rect(screen, (25,25,25), lowerRect)
            quitTag = getFont(70).render("Quit", 1, (255, 0, 0))
            screen.blit(quitTag, (65+currentPlayer.corner[0], 55+currentPlayer.corner[1]))


            score = currentPlayer.collects
            label = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))
            screen.blit(label, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

        elif currentPlayer.status == "disqualified":    #shows disqualified tag
            pygame.draw.rect(screen, (25,25,25), lowerRect)
            forfeitTag = getFont(50).render("Disqualified", 1, (255, 0, 0))
            screen.blit(forfeitTag, (7+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            score = currentPlayer.collects
            label = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))
            screen.blit(label, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

        elif currentPlayer.status == "noshow":    #shows no-show tag
            pygame.draw.rect(screen, (25,25,25), lowerRect)
            forfeitTag = getFont(50).render("No-Show", 1, (255, 0, 0))
            screen.blit(forfeitTag, (40+currentPlayer.corner[0], 65+currentPlayer.corner[1]))

            score = currentPlayer.collects
            label = getFont(16).render(str("Completion: {0}%".format(math.floor((score/602)*100))), 1, (140,140,156))
            screen.blit(label, (62+currentPlayer.corner[0], 32+currentPlayer.corner[1]))

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
        if not os.path.isfile("./profiles/"+user+".bmp"):
            url = "https://api.twitch.tv/helix/users?login="+user
            headers = {"Client-ID":CLIENT_ID}
            response = requests.get(url, headers=headers)
            #data={}

            if response.status_code in range(200,300):
                responseData = json.loads(response.content.decode("UTF-8"))['data']
                if len(responseData)==0:
                    print("[API] Twitch user "+user+" does not exist. Using default image.")
                    #playerLookup[user].validTwitchAccount = False
                else:
                    data = responseData[0]
                    profileLocation = data['profile_image_url']
                    urllib.request.urlretrieve(profileLocation, "."+"/profiles/"+user+".bmp")
                    print("[API] Fetched profile of Twitch user "+user+".")
            else:
                print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
                return None
    return

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
    (3,3),   (258,3),   (513,3),   (768,3),   (1023,3),
    (3,146), (258,146), (513,146), (768,146), (1023,146),
    (3,289), (258,289), (513,289), (768,289), (1023,289),
    (3,432), (258,432), (513,432), (768,432), (1023,432),
    (3,575), (258,575), (513,575), (768,575), (1023,575)
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

ScoreCard = pygame.image.load('./602files/ScoreCard602.bmp')
SM64Logo = pygame.image.load('./602files/SM64.bmp')
SMSLogo = pygame.image.load('./602files/SMS.bmp')
SMGLogo = pygame.image.load('./602files/SMG.bmp')
SMG2Logo = pygame.image.load('./602files/SMG2.bmp')

def getFont(size):
    return pygame.font.SysFont("Lobster 1.4", size)

screen = draw(screen, playerLookup)
pygame.display.flip()
redraw = False

#--------------------main bot loop--------------------
mainChat = ChatRoom(CHANNEL, NICK, PASSWORD)
done = False
while not done:
    #todo for player in players, conduct this entire loop, replace mainChat with player.chat
    #for i in range(0, len(racers)+1):

    # if i == len(racers):
    #     currentChat = mainChat
    #     currentChannel = "602race"
    # else:
    #     currentChat = playerLookup[racers[i]].chat
    #     currentChannel = racers[i]

    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

        #--------------------reading from twitch chat--------------------
        lines=""
        try:
            readbuffer = mainChat.currentSocket.recv(1024).decode("UTF-8", errors = "ignore")
            lines = readbuffer.split("\n")
        except socket.error as e:
            print("[!] Socket Error:", e)
            pass

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
                    if (modstatus == "1"): #or (user == currentChannel):
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
                mainChat.pong()
            elif len(out) > 0:
                user = user.lower()[1:]
                out = out.lower()
                command = out.split(" ")

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
                            mainChat.message(playerLookup[user].nameCaseSensitive + "has quit.")
                    if user not in admins:
                        if command[0] == "!mod" and len(command) == 2:
                            if command[1] not in updaters:
                                updaters.append(command[1])
                                pushUpdaters()
                                mainChat.message(command[1] + " is now an updater.")
                            else:
                                mainChat.message(command[1] + " is already an updater.")
                        elif command[0] == "!unmod" and len(command) == 2:
                            if command[1] in updaters:
                                updaters.remove(command[1])
                                pushUpdaters()
                                mainChat.message(command[1] + " is no longer an updater.")
                            else:
                                mainChat.message(command[1] + " is already not an updater.")

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
                    elif command[0] == "!add" and len(command) == 2:
                        mainChat.message(user+", you're not a racer! Please specify whose star count you would like to update. (!add odme_ 2)")
                        #placeholder to allow me to collapse this line of code

                #----------------------admin commands----------------------
                if user in admins:
                    if command[0] == "!start":
                        startTime = datetime.datetime.now()
                        with open("./602files/startingTime.obj", 'wb') as output:
                            pickle.dump(startTime, output, pickle.HIGHEST_PROTOCOL)
                        now = datetime.datetime.now().isoformat().split("T")
                        now = now[0] + " @ " + now[1].split(".")[0]
                        mainChat.message("The race has started, on " + now)
                    elif command[0] == "!mod" and len(command) == 2:
                        if command[1] not in updaters:
                            updaters.append(command[1])
                            pushUpdaters()
                            mainChat.message(command[1] + " is now an updater.")
                        else:
                            mainChat.message(command[1] + " is already an updater.")
                    elif command[0] == "!unmod" and len(command) == 2:
                        if command[1] in updaters:
                            updaters.remove(command[1])
                            pushUpdaters()
                            mainChat.message(command[1] + " is no longer an updater.")
                        else:
                            mainChat.message(command[1] + " is already not an updater.")
                    elif command[0] == "!forcequit":
                        if len(command) == 2 and command[1] in playerLookup.keys():
                            player = command[1]
                            if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                if playerLookup[player].status == "done":
                                    finishers.remove(player)
                                playerLookup[player].fail("quit")
                                redraw = True
                                mainChat.message(command[1] + " has been forcequit.")
                    elif command[0] == "!noshow":
                        if len(command) == 2 and command[1] in playerLookup.keys():
                            player = command[1]
                            if playerLookup[player].status == "done":
                                finishers.remove(player)
                            playerLookup[player].fail("noshow")
                            redraw = True
                            mainChat.message(command[1] + " set to No-show.")
                    elif command[0] == "!dq":
                        if len(command) == 2 and command[1] in playerLookup.keys():
                            player = command[1]
                            if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                if playerLookup[player].status == "done":
                                    finishers.remove(player)
                                playerLookup[player].fail("disqualified")
                                redraw = True
                                mainChat.message(command[1] + " has been disqualified.")
                    elif command[0] == "!revive":
                        if len(command) == 2 and command[1] in playerLookup.keys():
                            player = command[1]
                            playerLookup[player].status = "live"
                            redraw = True
                            mainChat.message(command[1] + " has been revived.")
                    
        if redraw:
            assignPlaces(playerLookup)
            screen = draw(screen, playerLookup)
            pygame.display.flip()
            redraw = False
    except Exception as e:
        print("[!] Exception:", e)
        pass

pygame.quit()
