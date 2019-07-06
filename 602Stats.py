import socket
import math
import sys
import pygame
import datetime
import pickle
import random
import json
import requests
import urllib
import os
import time
import threading

#-----------------object definitions-------------------
class playerObject:
    def __init__(self, name):
        self.name = name.lower()
        self.nameCaseSensitive = name
        self.corner = (0,0)
        self.collects = random.choice(range(0,602))
        self.status = "live"
        self.place = 1
        self.duration = -1
        self.completionTime = "HH:MM:SS"
        self.finishTimeAbsolute = None
        try:
            self.profile = pygame.transform.scale(pygame.image.load("./profiles/{0}.png".format(name)), (60,60))
        except pygame.error:
            self.profile = pygame.transform.scale(pygame.image.load("./resources/error.png"), (60,60))
        time.sleep(1)
        self.chat = ChatRoom("#"+self.name, NICK, PASSWORD)

    def manualDuration(self):               #add startTime + duration to calculate new finish time
        self.finishTimeAbsolute = startTime + datetime.timedelta(seconds=self.duration)

    def calculateCompletionTime(self):
        if type(self.finishTimeAbsolute) != datetime.datetime:
            return
        self.duration = (self.finishTimeAbsolute - startTime).total_seconds()

        tmp1 = datetime.timedelta(seconds=math.floor(self.duration))
        delta = str(tmp1).split(" day")

        initialHours = 0
        extraHours=""
        if len(delta)==1:
            extraHours = delta[0]
            pass
        elif len(delta)==2:
            days = delta[0]
            days = int(days)
            initialHours = days * 24
            if delta[1][0]=="s":
                extraHours = delta[1][3:]
            elif delta[1][0]==",":
                extraHours = delta[1][2:]

        finalTime = extraHours.split(":")
        finalHours = int(finalTime[0]) + initialHours
        finishTime = str(finalHours)+":"+finalTime[1]+":"+finalTime[2]
        self.completionTime = finishTime

    def finish(self):
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime()
        self.chat.message(self.nameCaseSensitive + " has finished!")
        self.status = "done"

    def unfinish(self):
        self.collects = 601
        self.status = "live"

    def fail(self, status):
        self.status = status
        self.finishTimeAbsolute = datetime.datetime.now()
        self.calculateCompletionTime()

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

        return self.nameCaseSensitive + " now has " + str(tempStars) + " "+ noun+buffer + " in " + game + "."

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
        #self.message("602 Stats Bot joined "+self.channel+" on "+timeNow)
        print("[Twitch] "+ "Joined Twitch channel "+self.channel+".")
    def pong(self):
        try:
            self.currentSocket.send(bytes("PONG tmi.twitch.tv\r\n", "UTF-8"))
            timeNow = datetime.datetime.now().isoformat()
            timeNow = timeNow.split("T")
            timeNow = timeNow[0] + "@" + timeNow[1].split(".")[0]
            print("[Twitch] "+ timeNow +": Pong attempted.")
        except socket.error:
            print("Socket error.")

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
    racerIndex=0
    for s in range(0,len(sortedRacers)):
        if s==-1: #leaving empty slots for spacing
            pass
        elif racerIndex < 16:
            playerLookup[sortedRacers[racerIndex]].corner = slots[s]
            racerIndex+=1
        else:
            playerLookup[sortedRacers[racerIndex]].corner = [1600, 900]
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
            screen.blit(star, (6+corner[0], 75+corner[1]) )
            label = getFont(18).render(str(sm64count), 1, sm64color)
            screen.blit(label, (45+corner[0], 79+corner[1]))

            screen.blit(luma, (6+corner[0], 103+corner[1]) )
            label = getFont(18).render(str(smgcount), 1, smgcolor)
            screen.blit(label, (45+corner[0], 109+corner[1]))

            screen.blit(shine, (188+corner[0], 70+corner[1]) )
            label = getFont(18).render(str(smscount), 1, smscolor)
            screen.blit(label, (230+corner[0], 79+corner[1]))

            screen.blit(yoshi, (6+corner[0], 137+corner[1]) )
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

            label = getFont(24).render("Completion: "+str(score)+"/602 in "+currentPlayer.completionTime, 1, (220,220,220))
            screen.blit(label, (50+currentPlayer.corner[0], 140+currentPlayer.corner[1]))

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

def pushAdmins():
    with open("admins.txt", "w") as adminFile:
        for admin in admins:
            if admin.index == len(admins)-1:
                adminFile.write(admin)
            else:
                adminFile.write(admin+"\n")

def pushBlacklist():
    with open("blacklist.txt", "w") as blacklistFile:
        for b in blacklist:
            if b.index == len(blacklist)-1:
                blacklistFile.write(b)
            else:
                blacklistFile.write(b+"\n")

def status(user):
    returnString = user + ": "
    if user in racers:
        returnString += "Racer ("+playerLookup[user].status +"), "
    if user in admins:
        returnString += "Admin, "
    if user in updaters:
        returnString += "Updater, "
    if user in blacklist:
        returnString += "Blacklist, "
    if returnString == (user + ": "):
        returnString += "None, "
    return returnString[0:-2]

def fetchProfiles(users, CLIENT_ID):
    for user in users:
        if not os.path.isfile("./profiles/"+user+".png"):
            url = "https://api.twitch.tv/helix/users?login="+user
            headers = {"Client-ID":CLIENT_ID}
            response = requests.get(url, headers=headers)
            if response.status_code in range(200,300):
                responseData = json.loads(response.content.decode("UTF-8"))['data']
                if len(responseData)==0:
                    print("[API] Twitch user "+user+" does not exist. Using default image.")
                    #playerLookup[user].validTwitchAccount = False
                else:
                    data = responseData[0]
                    profileLocation = data['profile_image_url']
                    urllib.request.urlretrieve(profileLocation, "."+"/profiles/"+user+".png")
                    print("[API] Fetched profile of Twitch user "+user+".")
            else:
                print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
                return None
    return

def fetchRacers(APIkey):
    success=False
    tries = 0
    sheetRacers = []
    while not success:
        url = "https://sheets.googleapis.com/v4/spreadsheets/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/values/A6:A?key="+APIkey
        response = requests.get(url, headers={})
        tries+=1
        if response.status_code in range(200,300):
            nResponse = json.loads(response.content.decode("UTF-8"))["values"]
            for e in nResponse:
                if e == []:
                    pass
                elif e[0] == "Theoretical WR":
                    pass
                else:
                    sheetRacers.append(e[0])
            success=True
        else:
            nResponse = json.loads(response.content.decode("UTF-8"))["error"]
            print('[!] (Try '+str(tries)+') Google Sheets API request failed. ' + str(nResponse["code"]) +': '+nResponse["message"])
            if tries==5:
                print("[!] Can't request from Google Sheets API. Giving up.")
                success=True
    return sheetRacers

def fetchIRC(thisChat):
    while True:
        try:
            readbuffer = thisChat.currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
            thisChat.inputBuffer += readbuffer
        except Exception as e:
            print("[!] Exception on line", sys.exc_info()[-1].tb_lineno, ":", e)
            return #returns from method and ends thread if there is an error

def srlThread(NICK, PASS, channel, twitchChat):
    HOST = "irc.speedrunslive.com"
    PORT = 6667
    joinedRoom = False
    roomCode = ""
    stopLoop = False
    srlGame = "Super Monkey Ball 2" #replace with "Multiple Game Race"
    currentSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    currentSocket.connect((HOST,PORT))
    currentSocket.send(bytes("USER "+NICK+" "+NICK+" "+NICK+" :test"+"\n", "UTF-8"))
    currentSocket.send(bytes("NICK "+NICK+"\n", "UTF-8"))
    time.sleep(2)

    while not stopLoop:
        readbuffer = currentSocket.recv(4096).decode("UTF-8", errors = "ignore")
        #print(readbuffer, end="")

        if readbuffer.find('PING :') != -1:
            pong = readbuffer.split("PING :")[1]
            pong = pong.split("\r")[0]
            #print("[SRL] PONG :"+pong)
            currentSocket.send(bytes("PONG :"+pong+"\n", "UTF-8"))

        if readbuffer.find("If you do not change within 20 seconds") != -1:
            currentSocket.send(bytes("nickserv identify "+PASS+"\n", "UTF-8"))
            time.sleep(1)
            currentSocket.send(bytes("JOIN "+channel+"\n", "UTF-8"))

        if readbuffer.find("Password accepted") != -1:
            print("[SRL] Joined SpeedRunsLive IRC.")

        if readbuffer.find("You have not registered") != -1:
            stopLoop = True

        if (not joinedRoom) and (readbuffer.find(srlGame) != -1):
            roomCode = readbuffer.split(srlGame)[1].split("#srl")[1][0:6]
            roomCode = "#srl"+roomCode
            currentSocket.send(bytes("JOIN "+roomCode+"\n", "UTF-8"))
            print("[SRL] Joined " + srlGame + " - "+ roomCode)
            joinedRoom = True

        if joinedRoom and (readbuffer.find(":RaceBot!RaceBot") != -1):
            global startTime
            global redraw
            tmp = readbuffer.split(":RaceBot!RaceBot")[1]
            if tmp.find("PRIVMSG "+roomCode) != -1:
                tmp = tmp.split("PRIVMSG "+roomCode)[1]

                racebotMessage = tmp.split("\n")[0][2:].replace("4", "")
                twitchChat.message("[SRL] RaceBot: "+racebotMessage)

                #TODO check for an eaten message, this doesn't work right now
                tmp3 = tmp.split("\n")[1]
                if tmp3.find(":RaceBot!RaceBot") != -1:
                    tmp3 = tmp3.split(":RaceBot!RaceBot")
                    if tmp3.find("PRIVMSG " + roomCode) != -1:
                        tmp3 = tmp3.split("PRIVMSG " +roomCode)[1].split("\n")[0][2:].replace("4", "")
                        twitchChat.message("[SRL] RaceBot: "+tmp3)

                if tmp.find("GO!") != -1:
                    startTime = datetime.datetime.now()
                    redraw = True
                    with open("./resources/startingTime.obj", 'wb') as output:
                        pickle.dump(startTime, output, pickle.HIGHEST_PROTOCOL)
                    for racer in racers:
                        playerLookup[racer].calculateCompletionTime()
                    now = datetime.datetime.now().isoformat().split("T")
                    now = now[0] + " @ " + now[1].split(".")[0]
                    twitchChat.message("[SRL] Race start time set to "+now)
                    stopLoop = True

#---------loading & processing external data-------------
'''
with open('racers.txt') as f:
    racersCaseSensitive = f.read().split("\n")
    racersCaseSensitive = list(filter(None, racersCaseSensitive))
    racers = []
    for r in racersCaseSensitive:
        racers.append(r.lower())
'''
with open('updaters.txt') as f:
    updaters = f.read().lower().split("\n")
    updaters = list(filter(None, updaters))
with open('admins.txt') as f:
    admins = f.read().lower().split("\n")
    admins = list(filter(None, admins))
with open('blacklist.txt') as f:
    blacklist = f.read().lower().split("\n")
    blacklist = list(filter(None, blacklist))
with open('settings.txt') as f:
    file = f.read()
    NICK = file.split("Twitch Username for Bot: ")[1].split()[0].lower()
    PASSWORD = file.split("Twitch Chat Authentication Token: ")[1].split()[0]
    CHANNEL = "#" + file.split("Main Twitch Chat for Bot: ")[1].split()[0].lower()
    SRLusername = file.split("SpeedRunsLive Username: ")[1].split()[0]
    SRLpassword = file.split("SpeedRunsLive Password: ")[1].split()[0]
    Twitch_clientId = file.split("Twitch developer app Client-ID: ")[1].split()[0]
    GoogleAPIKey = file.split("Google API Key: ")[1].split()[0]

racersCaseSensitive = fetchRacers(GoogleAPIKey)
racers = []
for racer in racersCaseSensitive:
    racers.append(racer.lower())
#todo: remove fetched from both names to use official sheet racers
#      then get rid of reference to racers.txt file
print(racersCaseSensitive)

for racer in racers:
    if (racer not in updaters) and (racer not in blacklist):
        updaters.append(racer)
        pushUpdaters()

with open("./resources/startingTime.obj", 'rb') as objIn:
    startTime = pickle.load(objIn)

fetchProfiles(racers, Twitch_clientId)

#----------player object & slot assignments-------------
slots = [
    (10,160),(407,160),(804,160),(1201,160),
    (10,345),(407,345),(804,345),(1201,345),
    (10,530),(407,530),(804,530),(1201,530),
    (10,715),(407,715),(804,715),(1201,715), (1600,900)
] #387 x 175 scorecards
playerLookup = {}
for racer in racersCaseSensitive:
    playerLookup[racer.lower()] = playerObject(racer)

#--------------------pygame settings--------------------
pygame.init()
screen = pygame.display.set_mode([1600,900])
pygame.display.set_caption("602 Stats Program")

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
    return pygame.font.SysFont("Lobster 1.4", size)

screen = draw(screen, playerLookup)
pygame.display.flip()
redraw = False

#------------create and start chat threads------------
for racer in racers:
    room = playerLookup[racer].chat
    t = threading.Thread(target=fetchIRC, args=(room,))
    t.start()

mainChat = ChatRoom(CHANNEL, NICK, PASSWORD)
t = threading.Thread(target=fetchIRC, args=(mainChat,))
t.start()
SRL = threading.Thread(target=srlThread, args=(SRLusername,SRLpassword,"#speedrunslive", mainChat,))
SRL.start()
#--------------------main bot loop--------------------
done = False
while not done:
    for i in range(0, len(racers)+1):

        if i == len(racers):
            currentChat = mainChat
            currentChannel = CHANNEL[1:]
        else:
            currentChat = playerLookup[racers[i]].chat
            currentChannel = racers[i]

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
                if user == currentChannel:
                    ismod = True
                elif len(line) > 0:
                    if line[0][0] == "@":
                        tags = line[0]
                        del line[0]
                        modstatus = tags.split("mod=")
                        if len(modstatus) > 1:
                            modstatus = modstatus[1][0]
                            if modstatus == "1":
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
                    print("[Command] "+user+":"+str(command))

                    #----------------------global commands---------------------
                    if command[0] == "!ping":
                        currentChat.message("Hi. Bot is alive.")
                    if command[0] == "!status":
                        if len(command) == 1:
                            statusMsg = status(user)
                        else:
                            statusMsg = status(command[1])
                        if statusMsg is not None:
                            currentChat.message(statusMsg)

                    #----------------------racer commands----------------------
                    if user in racers: #todo more intuitive unfinish command?
                        if playerLookup[user].status == "live":
                            if command[0] == "!add" and len(command) == 2:
                                number = int(command[1])
                                if 0 <= playerLookup[user].collects + number <= 602:
                                    playerLookup[user].collects += number
                                    if playerLookup[user].collects == 602:
                                        playerLookup[user].finish()
                                        currentChat.message(playerLookup[user].nameCaseSensitive + " has finished!")
                                    else:
                                        currentChat.message(playerLookup[user].hasCollected())
                                    redraw = True
                            elif command[0] == "!quit":
                                playerLookup[user].fail("quit")
                                redraw = True
                                currentChat.message(playerLookup[user].nameCaseSensitive + " has quit.")
                        elif playerLookup[user].status == "done":
                            if command[0] == "!unfinish":
                                playerLookup[user].unfinish()
                                redraw = True
                                currentChat.message(user+" has been unfinished.")
                        if user not in admins:
                            if command[0] == "!mod" and len(command) == 2:
                                if command[1] in blacklist:
                                    currentChat.message("Sorry, " + command[1] + " is on the blacklist.")
                                elif command[1] not in updaters:
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
                        if command[0] == "!add":
                            if len(command) == 3:
                                if command[1] in playerLookup.keys():
                                    player = command[1]
                                    if playerLookup[player].status == "live":
                                        number = int(command[2])
                                        if 0 <= playerLookup[player].collects + number <= 602:
                                            playerLookup[player].collects += number
                                            if playerLookup[player].collects == 602:
                                                playerLookup[player].finish()
                                                currentChat.message(playerLookup[player].nameCaseSensitive + " has finished!")
                                            else:
                                                currentChat.message(playerLookup[player].hasCollected())
                                            redraw = True
                            elif len(command) == 2:
                                if user not in racers:
                                    pass
                                    #currentChat.message(user+", you're not a racer! Please specify whose star count you would like to update. (!add odme_ 2)")

                    #----------------------admin commands----------------------
                    if user in admins:
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
                                with open("./resources/startingTime.obj", 'wb') as output:
                                    pickle.dump(newTime, output, pickle.HIGHEST_PROTOCOL)
                                startTime = newTime
                                now = newTime.isoformat().split("T")
                                now = now[0] + "@" + now[1].split(".")[0]
                                currentChat.message("The race start time has been set to " + now)
                                for racer in racers:
                                    playerLookup[racer].calculateCompletionTime()
                                redraw = True
                        elif command[0] == "!mod" and len(command) == 2:
                            if command[1] in blacklist:
                                currentChat.message("Sorry, " + command[1] + " is on the blacklist.")
                            elif command[1] not in updaters:
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
                                    playerLookup[player].fail("quit")
                                    redraw = True
                                    currentChat.message(command[1] + " has been forcequit.")
                        elif command[0] == "!noshow":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                playerLookup[player].fail("noshow")
                                redraw = True
                                currentChat.message(command[1] + " set to No-show.")
                        elif command[0] == "!dq":
                            if len(command) == 2 and command[1] in playerLookup.keys():
                                player = command[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
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
                                        playerLookup[player].manualDuration()
                                        redraw = True
                                        currentChat.message(command[1]+"'s time has been updated.")
                        elif command[0] == "!blacklist" and len(command) == 2:
                            if command[1] not in blacklist:
                                blacklist.append(command[1])
                                pushBlacklist()
                                if command[1] in updaters:
                                    updaters.remove(command[1])
                                    pushUpdaters()
                                currentChat.message(command[1] + " has been blacklisted.")
                            else:
                                currentChat.message(command[1] + " is already blacklisted.")
                        elif command[0] == "!unblacklist" and len(command) == 2:
                            if command[1] in blacklist:
                                blacklist.remove(command[1])
                                pushBlacklist()
                                currentChat.message(command[1] + " is no longer blacklisted.")
                            else:
                                currentChat.message(command[1] + " is already not blacklisted.")
                        elif command[0] == "!admin" and len(command) == 2:
                            if command[1] not in admins:
                                admins.append(command[1])
                                pushAdmins()
                                currentChat.message(command[1] + " is now an admin.")
                            else:
                                currentChat.message(command[1] + " is already an admin.")

            if redraw:
                screen = draw(screen, playerLookup)
                pygame.display.flip()
                redraw = False

        except Exception as e:
            print("[!] Exception on line", sys.exc_info()[-1].tb_lineno, ":", e)
            pass

pygame.quit()
