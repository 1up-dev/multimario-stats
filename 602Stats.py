import socket
import math
import pygame
import datetime as dt
import random
import time

#twitch API stuff:
HOST = "irc.twitch.tv"
PORT = 6667
PASSWORD = "oauth:jv8w6oc6n44674ve078311bl1m6r6r" #From http://twitchapps.com/tmi/
CHANNEL = "#602race" #"#rareware301"
NICK = "602race" #"rareware301"

class playerObject:
    def __init__(self, name, corner):
        self.name = name
        self.corner = corner
        self.collects = 0 #random.choice(range(0,602))
        if name in ["bird650",]:
            self.status = "forfeit"
        else:
            self.status = "live"
        self.completionTime = "HH:MM:SS"
        self.place = 1

def message(msg): #posts messages to twitch chat
    try:
        TwitchIRC.send(bytes("PRIVMSG " + CHANNEL + " :" + msg + "\r\n", "UTF-8"))
    except socket.error:
        pass

def assignPlaces(playerLookup): #place assigner
    scores = {}
    place = 1
    
    for key in playerLookup:
        if playerLookup[key].status != "forfeit" and playerLookup[key].status != "disqualified":
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
            if playerLookup[player].status == "live":
                playerLookup[player].place = place
        place += 1

def draw(screen, playerLookup): #draw code
    for key in playerLookup:
        pygame.draw.rect(screen, (25,25,25), [55+playerLookup[key].corner[0], 32+playerLookup[key].corner[1], 198, 23])
        
        if playerLookup[key].status == "live":    #checks if the player is live
            screen.blit(ScoreCard, (1+playerLookup[key].corner[0], 55+playerLookup[key].corner[1]))
            score = playerLookup[key].collects
            
            if playerLookup[key].place <=3:
                label = BigFont.render(str("Completion: {0}%    Place: {1}".format(math.floor(((score)/602)*100), playerLookup[key].place)), 1, (239,195,0))
            else:
                label = BigFont.render(str("Completion: {0}%    Place: {1}".format(math.floor(((score)/602)*100), playerLookup[key].place)), 1, (140,140,156))
            screen.blit(label, (62+playerLookup[key].corner[0], 32+playerLookup[key].corner[1]))
            
            if score == 0:    #draws for 0
                screen.blit(SM64Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))
                
            elif score <= 120:    #draws scores while playing SM64
                if score == 120:
                    screen.blit(SMGLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                else:
                    screen.blit(SM64Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                length = math.floor((score/120)*93)
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], length, 7])
                
                label = SmallFont.render(str(score), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))
                
            elif score <= 240:    #draws scores while playing SMG
                if score == 240:
                    screen.blit(SMSLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                else:
                    screen.blit(SMGLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-120)/120)*93)
                pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], length, 7])
                
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str(score-120), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))
                
            elif score <= 360:    #draws scores while playing SMS
                if score == 360:
                    screen.blit(SMG2Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                else:
                    screen.blit(SMSLogo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-240)/120)*93)
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 101+playerLookup[key].corner[1], length, 7])
                
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str(score-240), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = SmallFont.render(str("0"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))
                
            elif score < 602:    #draws scores while playing SMG2
                screen.blit(SMG2Logo, (148+playerLookup[key].corner[0], 90+playerLookup[key].corner[1]))
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [130+playerLookup[key].corner[0], 74+playerLookup[key].corner[1], 93, 7])
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 101+playerLookup[key].corner[1], 93, 7])
                length = math.floor(((score-360)/242)*218)
                pygame.draw.rect(screen, (0,148,255), [5+playerLookup[key].corner[0], 129+playerLookup[key].corner[1], length, 7])
                
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 70+playerLookup[key].corner[1]))
                label = SmallFont.render(str("120"), 1, (140,140,156))
                screen.blit(label, (104+playerLookup[key].corner[0], 97+playerLookup[key].corner[1]))
                label = SmallFont.render(str(score-360), 1, (140,140,156))
                screen.blit(label, (229+playerLookup[key].corner[0], 125+playerLookup[key].corner[1]))
            
                
        elif playerLookup[key].status == "forfeit":    #shows forfeit tag
            screen.blit(Forfeit, (1+playerLookup[key].corner[0], 55+playerLookup[key].corner[1]))
            
        elif playerLookup[key].status == "done":    #shows done tag
            screen.blit(Done, (1+playerLookup[key].corner[0], 55+playerLookup[key].corner[1]))
            if playerLookup[key].place <= 3:
                label = BigFont.render(str("{0}    Place: {1}".format(playerLookup[key].completionTime, playerLookup[key].place)), 1, (239,195,0))
            else:
                label = BigFont.render(str("{0}    Place: {1}".format(playerLookup[key].completionTime, playerLookup[key].place)), 1, (140,140,156))
            screen.blit(label, (59+playerLookup[key].corner[0], 32+playerLookup[key].corner[1]))
                
        elif playerLookup[key].status == "disqualified":    #shows disqualified tag
            screen.blit(Disqualified, (1+playerLookup[key].corner[0], 55+playerLookup[key].corner[1]))
            
    pygame.display.flip()
    return screen
    

#--------------------player object assignments--------------------
p1 = ("360chrism",(3,3)) #
p2 = ("javoxxib",(3,146)) #
p3 = ("themilkman47",(3,289)) #
p4 = ("lord_frish",(3,432)) #
p5 = ("p4ntz",(3,575)) #

p6 = ("icupletsplay",(258,3)) #
p7 = ("mclightofday",(258,146)) #
#p8 = ("Player H",(258,289)) #
p9 = ("monadopurge",(258,432))
p10 = ("silentjay630",(258,575))

p11 = ("coolmath10",(513,3))
p12 = ("marioman847",(513,146))
#slot for timer
p13 = ("silverness48200",(513,432))
p14 = ("cosmoing",(513,575))

p15 = ("flygonman",(768,3))
p16 = ("werewolfshadowgaming",(768,146))
#p17 = ("Player Q",(768,289))
p18 = ("zoob1324",(768,432))
p19 = ("zodastone",(768,575))

p20 = ("n0cturne_",(1023,3))
p21 = ("teensies_king",(1023,146))
p22 = ("bird650",(1023,289))
p23 = ("odmewhirter123",(1023,432))
p24 = ("kayareya",(1023,575))

mods = ["enkaybee", "1upsforlife", "360chrism", "3quinox_", "airball12", "angellolion", "chrisoofy", "coolmath10", "cosmoing", \
    "drastnikov", "elxer", "fir3turtle", "flygonman", "gabgab2222", "glfan99", "icupletsplay", "imdutch21", "imthe666st", \
    "javoxxib", "kayareya", "ladaur", "lord_frish", "marioman847", "matthewpipie", "mclightofday", "miror_a", "mlstrm", "monadopurge", \
    "n0cturne_", "nkiller", "odmewhirter123", "olib40", "p4ntz", "pengoothepenguin", "quoteconut", "raysfire", "rivdog02", "shadowlugia", \
    "shield48", "silentjay630", "sirstendec", "slowkingspants", "snarfybobo", "teensies_king", "theepicflame", "theesizzler", "themilkman47", \
    "twitchmasta123", "tww2", "vallu111", "werewolfshadowgaming", "xen0va", "xenoda", "xzrockin", "zodastone", "zoob1324"]
playerLookup = {p1[0]:p1, p2[0]:p2, p3[0]:p3, p4[0]:p4, p5[0]:p5,
    p6[0]:p6, p7[0]:p7, p9[0]:p9, p10[0]:p10,
    p11[0]:p11, p12[0]:p12, p13[0]:p13, p14[0]:p14,
    p15[0]:p15, p16[0]:p16, p18[0]:p18, p19[0]:p19,
    p20[0]:p20, p21[0]:p21, p22[0]:p22, p23[0]:p23, p24[0]:p24}
finishers = []
for player in playerLookup.keys():
    playerLookup[player] = playerObject(playerLookup[player][0],playerLookup[player][1])
assignPlaces(playerLookup)
currentTime = dt.datetime.now()

#--------------------pygame settings--------------------
pygame.init()
size=[1280,720]
screen = pygame.display.set_mode(size)
pygame.display.set_caption("The 602")
screen.fill((16,16,16))
ScoreCard = pygame.image.load('ScoreCard602.bmp')
Forfeit = pygame.image.load('Forfeit.bmp')
Done = pygame.image.load('Done.bmp')
Disqualified = pygame.image.load('Disqualified.bmp')
SM64Logo = pygame.image.load('SM64.bmp')
SMSLogo = pygame.image.load('SMS.bmp')
SMGLogo = pygame.image.load('SMG.bmp')
SMG2Logo = pygame.image.load('SMG2.bmp')
SmallFont = pygame.font.SysFont("Lobster 1.4", 12)
BigFont = pygame.font.SysFont("Lobster 1.4", 16)
screen = draw(screen, playerLookup)
pygame.display.flip()
redraw = False


#--------------------connect to Twitch IRC--------------------
TwitchIRC = socket.socket()
TwitchIRC.connect((HOST, PORT))
TwitchIRC.send(bytes("PASS %s\r\n" %PASSWORD, "UTF-8"))
TwitchIRC.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
TwitchIRC.send(bytes("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK), "UTF-8"))
TwitchIRC.send(bytes("JOIN %s\r\n" % CHANNEL, "UTF-8"))


#--------------------main loop--------------------
while True:
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done=True

        try:
            readbuffer = TwitchIRC.recv(1024).decode("UTF-8", errors = "ignore")
        except socket.error:
            pass
        temp = str.split(readbuffer, "\n")
        readbuffer = temp.pop( )
            
        for line in temp:
            x = 0
            out = ""
            line = str.rstrip(line)
            line = str.split(line)
            for index, i in enumerate(line):
                if x == 0:
                    user = line[index]
                    user = user.split('!')[0]
                    user = user[0:24] + ": "
                if x == 3:
                    out += line[index]
                    out = out[1:]
                if x >= 4:
                    out += " " + line[index]
                x = x + 1

            if user == "PING: ":
                TwitchIRC.send(bytes("PONG tmi.twitch.tv\r\n", "UTF-8"))
            elif user == ":tmi.twitch.tv: ":
                pass
            elif user == ":tmi.twitch.: ":
                pass
            elif user == ":%s.tmi.twitch.tv: " % NICK:
                pass
            elif user == ":jtv: ":
                pass
            elif len(out) > 0:
                try:
                    user = user.lower()
                    user = user[1:-2]
                    out = out.lower()
                    
                    #----------------------------------------actions for players----------------------------------------
                    if user in playerLookup.keys():
                        if playerLookup[user].status == "live":
                            if out == "!star":
                                playerLookup[user].collects += 1
                                if playerLookup[user].collects == 602:
                                    cycleTime = dt.datetime.now()
                                    finishTime = str(dt.timedelta(seconds=(math.floor((cycleTime - currentTime).total_seconds()))))
                                    finishers.append(user)
                                    message("Congrats on finishing, " + user.title() + "!")
                                    playerLookup[user].completionTime = finishTime
                                    playerLookup[user].status = "done"
                                redraw = True
                            elif out.split(" ")[0] == "!star" and len(out.split(" ")) == 2:
                                try:
                                    number = int(out.split(" ")[1])
                                    if playerLookup[user].collects + number >= 0 and playerLookup[user].collects + number <= 602:
                                        playerLookup[user].collects += number
                                        if playerLookup[user].collects == 602:
                                            cycleTime = dt.datetime.now()
                                            finishTime = str(dt.timedelta(seconds=(math.floor((cycleTime - currentTime).total_seconds()))))
                                            finishers.append(user)
                                            message("Congrats on finishing, " + user.title() + "!")
                                            playerLookup[user].completionTime = finishTime
                                            playerLookup[user].status = "done"
                                        redraw = True
                                except:
                                    pass
                            elif out == "!quit":
                                playerLookup[user].status = "forfeit"
                                redraw = True
                                
                    #----------------------------------------actions for mods----------------------------------------
                    
                    if user in mods:
                        if out.split(" ")[0] == "!add":
                            if out.split(" ")[1] in playerLookup.keys():
                                player = out.split(" ")[1]
                                if len(out.split(" ")) == 3 and playerLookup[player].status == "live":
                                    try:
                                        number = int(out.split(" ")[2])
                                        if playerLookup[player].collects + number >= 0 and playerLookup[player].collects + number <= 602:
                                            playerLookup[player].collects += number
                                            if playerLookup[player].collects == 602:
                                                cycleTime = dt.datetime.now()
                                                finishTime = str(dt.timedelta(seconds=(math.floor((cycleTime - currentTime).total_seconds()))))
                                                finishers.append(player)
                                                message("Congrats on finishing, " + player.title() + "!")
                                                playerLookup[player].completionTime = finishTime
                                                playerLookup[player].status = "done"
                                            redraw = True
                                    except:
                                        pass
                    
                        elif out.split(" ")[0] == "!dq":
                            if len(out.split(" ")) == 2 and out.split(" ")[1] in playerLookup.keys():
                                player = out.split(" ")[1]
                                if playerLookup[player].status == "live" or playerLookup[player].status == "done":
                                    if playerLookup[player].status == "done":
                                        finishers.remove(player)
                                    playerLookup[player].status = "disqualified"
                                    redraw = True
                    
                    #----------------------------------------actions for owner----------------------------------------            
                    if user == "enkaybee" or user == "1upsforlife":
                        if out.split(" ")[0] == "!undq":
                            if len(out.split(" ")) == 2 and out.split(" ")[1] in playerLookup.keys():
                                player = out.split(" ")[1]
                                playerLookup[player].status = "live"
                                playerLookup[player].collects = 0
                                redraw = True
                        elif out.split(" ")[0] == "!addmod" and len(out.split(" ")) == 2:
                            if out.split(" ")[1] not in mods:
                                mods.append(out.split(" ")[1])
                        elif out.split(" ")[0] == "!removemod" and len(out.split(" ")) == 2:
                            if out.split(" ")[1] in mods:
                                mods.remove(out.split(" ")[1])
                        elif out.split(" ")[0] == "!start":
                            currentTime = dt.datetime.now()
                            message("The race has started!")
                                
                except UnicodeEncodeError:
                    pass
                    
        if redraw:
            assignPlaces(playerLookup)
            screen = draw(screen, playerLookup)
            pygame.display.flip()
            redraw = False
            
    except:
        print("Something is wrong. Reconnecting to Twitch chat....")
        TwitchIRC = socket.socket()
        TwitchIRC.connect((HOST, PORT))
        TwitchIRC.send(bytes("PASS %s\r\n" %PASSWORD, "UTF-8"))
        TwitchIRC.send(bytes("NICK %s\r\n" % NICK, "UTF-8"))
        TwitchIRC.send(bytes("USER %s %s bla :%s\r\n" % (NICK, HOST, NICK), "UTF-8"))
        TwitchIRC.send(bytes("JOIN %s\r\n" % CHANNEL, "UTF-8"))
        
input("HOLDING FINAL")
pygame.quit()