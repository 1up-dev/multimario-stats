import socket
import os
import datetime
import time
import traceback
import settings
import bot

class ChatRoom:
    def __init__(self, channels):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.NICK = settings.twitch_nick
        self.PASSWORD = settings.twitch_pw
        self.channels = channels
        self.currentSocket = socket.socket()
    def message(self, channel, msg):
        try:
            self.currentSocket.send(bytes("PRIVMSG "+channel+" :"+msg+"\n", "UTF-8"))
        except socket.error:
            print("[Twitch IRC] Socket error.")
    def part(self, channel):
        try:
            self.currentSocket.send(bytes(f"PART #{channel}\n", "UTF-8"))
            self.channels.remove(channel)
        except socket.error:
            print("[Twitch IRC] Socket error.")
    def join(self, channel):
        try:
            self.currentSocket.send(bytes(f"JOIN #{channel}\n", "UTF-8"))
            self.channels.append(channel)
        except socket.error:
            print("[Twitch IRC] Socket error.")
    def reconnect(self):
        self.currentSocket.close()
        self.currentSocket = socket.socket()
        self.currentSocket.connect((self.HOST,self.PORT))
        self.currentSocket.send(bytes("PASS "+self.PASSWORD+"\n", "UTF-8"))
        self.currentSocket.send(bytes("NICK "+self.NICK+"\n", "UTF-8"))

        # Join Twitch channels in batches of 20 or less, to comply with rate limiting.
        # https://dev.twitch.tv/docs/irc/guide#rate-limits
        j = 0
        while True:
            channel_list = "#"+",#".join(self.channels[j:j+20])
            if j != 0:
                print("Sleeping 11 seconds before joining next batch of channels...")
                time.sleep(11)
            try:
                # Errors produced by this line:
                # ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
                # BrokenPipeError: [Errno 32] Broken pipe
                self.currentSocket.send(bytes("JOIN "+channel_list+"\n", "UTF-8"))
            except:
                print("Exception while connecting:")
                print(traceback.format_exc())
                return False
            print("Joined",channel_list)
            j += 20
            if self.channels[j:j+20] == []:
                break

        self.currentSocket.send(bytes("CAP REQ :twitch.tv/tags twitch.tv/commands\n", "UTF-8"))
    def pong(self):
        try:
            self.currentSocket.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))
            with open(os.path.join(settings.baseDir,"irc/0-main.log"), 'a') as f:
                f.write(datetime.datetime.now().isoformat().split(".")[0] + " Pong sent." + "\n")
            # print(datetime.datetime.now().isoformat().split(".")[0], "Pong sent")
        except socket.error:
            print("[Twitch IRC] Socket error when attempting pong.")

def bot_init(playerLookup):
    channels = []
    for c in settings.extra_chats:
        if c.lower() not in playerLookup.keys():
            channels.append(c.lower())
    for c in playerLookup.keys():
        channels.append(c)
    c = ChatRoom(channels)
    attempts = 0
    while(c.reconnect() == False):
        attempts += 1
        time.sleep(1)
        if attempts > 5:
            print("Failed to connect to Twitch IRC successfully.")
            return
    bot.fetchIRC(c,playerLookup)