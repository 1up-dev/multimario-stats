import socket
import datetime
import time
import pickle
import json
import os
import settings

def srlThread(channel, twitchChat, playerLookup):
    NICK = settings.srl_nick
    PASS = settings.srl_pw
    HOST = "irc.speedrunslive.com"
    PORT = 6667
    joinedRoom = False
    roomCode = ""
    stopLoop = False
    srlGame = "Multiple Game Race"
    currentSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    currentSocket.connect((HOST,PORT))
    currentSocket.send(bytes("USER "+NICK+" "+NICK+" "+NICK+" :test"+"\n", "UTF-8"))
    currentSocket.send(bytes("NICK "+NICK+"\n", "UTF-8"))
    time.sleep(2)

    while not stopLoop:
        readbuffer = currentSocket.recv(4096).decode("UTF-8", errors = "ignore")

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

                tmp3 = tmp.split("\n")[1]
                if tmp3.find(":RaceBot!RaceBot") != -1:
                    tmp3 = tmp3.split(":RaceBot!RaceBot")
                    if tmp3.find("PRIVMSG " + roomCode) != -1:
                        tmp3 = tmp3.split("PRIVMSG " +roomCode)[1].split("\n")[0][2:].replace("4", "")
                        twitchChat.message("[SRL] RaceBot: "+tmp3)

                if tmp.find("GO!") != -1:
                    startTime = datetime.datetime.now()
                    redraw = True
                    with open(os.path.join(settings.baseDir,'settings.json'), 'r+') as f:
                        j = json.load(f)
                        j['start-time'] = startTime.isoformat().split(".")[0]
                        f.seek(0)
                        json.dump(j, f, indent=4)
                        f.truncate()
                    for racer in playerLookup.keys():
                        playerLookup[racer].calculateCompletionTime()
                    twitchChat.message("[SRL] Race start time set to "+startTime.isoformat().split(".")[0])
                    stopLoop = True
