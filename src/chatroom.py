import socket
import datetime
import time

class ChatRoom:
    def __init__(self, channels, nick, password):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.NICK = nick
        self.PASSWORD = password
        self.channels = channels
        self.currentSocket = socket.socket()
    def message(self, channel, msg):
        try:
            self.currentSocket.send(bytes("PRIVMSG "+channel+" :"+msg+"\n", "UTF-8"))
        except socket.error:
            print("[Twitch IRC] Socket error.")
    def reconnect(self):
        self.currentSocket.close()
        self.currentSocket = socket.socket()
        self.currentSocket.connect((self.HOST,self.PORT))
        self.currentSocket.send(bytes("PASS "+self.PASSWORD+"\n", "UTF-8"))
        self.currentSocket.send(bytes("NICK "+self.NICK+"\n", "UTF-8"))

        channel_list = ""
        for c in self.channels:
            channel_list += "#"+c+","
        channel_list = channel_list[0:-1]
        self.currentSocket.send(bytes("JOIN "+channel_list+"\n", "UTF-8"))

        self.currentSocket.send(bytes("CAP REQ :twitch.tv/tags twitch.tv/commands\n", "UTF-8"))
    def pong(self):
        try:
            self.currentSocket.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))
            with open(f"irc/0-main.log", 'a') as f:
                f.write(datetime.datetime.now().isoformat().split(".")[0] + " Pong sent." + "\n")
            # print(datetime.datetime.now().isoformat().split(".")[0], "Pong sent")
        except socket.error:
            print("[Twitch IRC] Socket error when attempting pong.")
