import socket
import datetime
import time
import traceback
import threading
import settings

class ChatRoom:
    def __init__(self, channels):
        self.HOST = "irc.chat.twitch.tv"
        self.PORT = 6667
        self.channels = channels
        self.connection = socket.socket()
        self.readbuffer = ""
        self.authenticated = False

        # variables for outbound rate limit compliance 
        self.last_join_time = datetime.datetime.now() - datetime.timedelta(0,11)
        self.last_connect_time = datetime.datetime.now() - datetime.timedelta(0,30)
        self.msgCount = 0
        self.msgPeriod = datetime.datetime.now()
        self.sendbuffer = []
        t = threading.Thread(target=self.send_thread, args=())
        t.daemon = True
        t.start()

        self.reconnect()

    def send_thread(self):
        while True:
            if len(self.sendbuffer) == 0:
                time.sleep(0.5)
                continue
            if not self.authenticated:
                time.sleep(0.5)
                continue

            # Twitch JOIN rate limiting: >10 seconds between JOINs
            if self.sendbuffer[0][0:4] == "JOIN":
                seconds_since_last_join = (datetime.datetime.now() - self.last_join_time).total_seconds()
                if seconds_since_last_join < 11:
                    if len(self.sendbuffer) == 1:
                        # Wait 0.5, then check for new messages instead of blocking just for this JOIN message
                        time.sleep(0.5)
                        continue
                    # Move this JOIN message to the back of the queue
                    msg_to_move = self.sendbuffer.pop(0)
                    self.sendbuffer.append(msg_to_move)
                    continue
                self.last_join_time = datetime.datetime.now()

            # Twitch rate limiting: Using 31-sec and 19-msg thresholds just in case
            timer = (datetime.datetime.now() - self.msgPeriod).total_seconds()
            if timer > 31:
                self.msgPeriod = datetime.datetime.now()
                self.msgCount = 0
            elif self.msgCount >= 19:
                time.sleep(31-timer)
                self.msgPeriod = datetime.datetime.now()
                self.msgCount = 0
            self.msgCount += 1

            try:
                self.connection.send(bytes(f"{self.sendbuffer[0]}\r\n", "UTF-8"))
                self.sendbuffer.pop(0)
            except OSError:
                print(f"{settings.now()} Socket send: {traceback.format_exc()}")
                # Wait for the main bot thread to reconnect() on a failed recv() call.
                time.sleep(5)
            time.sleep(1.1)

    def send_instant(self, msg):
        self.msgCount += 1
        try:
            self.connection.send(bytes(f"{msg}\r\n", "UTF-8"))
        except OSError:
            print(f"{settings.now()} Socket instant send: {traceback.format_exc()}")

    def send(self, msg):
        self.sendbuffer.append(msg)

    def recv(self):
        try:
            self.readbuffer = self.readbuffer + self.connection.recv(4096).decode("UTF-8", errors = "ignore")
            if self.readbuffer == "":
                print(f"{settings.now()} Socket recv: empty readbuffer")
        except OSError:
            if settings.doQuit:
                return []
            print(f"{settings.now()} Socket recv: {traceback.format_exc()}")
            self.readbuffer = ""
        if self.readbuffer == "":
            self.reconnect()
            return []
        lines = self.readbuffer.split('\n')
        self.readbuffer = lines.pop()
        return lines

    def message(self, channel, msg, reply_id=None):
        if len(msg) > 300:
            msg = msg[:300] + "... (Message cut due to length)"
        
        # Log the outgoing message to the log file for readability
        path = f"irc/{channel[1:]}.log"
        with open(settings.path(path), 'a+') as f:
            f.write(f"{settings.now()} (Bot outgoing) {settings.twitch_nick}: {msg} \n")
        
        if channel == "#0-whispers":
            return
        
        if reply_id == None:
            self.send(f"PRIVMSG {channel} :{msg}")
        else:
            self.send(f"@reply-parent-msg-id={reply_id} PRIVMSG {channel} :{msg}")

    def part(self, channels, announce=False):
        for channel in channels:
            self.channels.remove(channel)
            if announce:
                self.message(f"#{channel}", f"Now leaving #{channel}.")
        channel_string = "#"+",#".join(channels)
        self.send(f"PART {channel_string}")

    def join(self, channels=[], announce=False, skip_queue=True):
        # Empty list: join all channels. Non-empty list: join specified channels and add them to the channels list
        self.channels += channels
        if channels == []:
            channels = self.channels
        # Twitch JOIN rate limiting: batches of 20 channels or less
        join_messages = []
        j = 0
        while True:
            channel_string = "#"+",#".join(channels[j:j+20])
            join_messages.append(f"JOIN {channel_string}")
            j += 20
            if channels[j:j+20] == []:
                break

        if skip_queue:
            # Insert the JOIN messages at the beginning of sendbuffer, so the joins are attempted first.
            self.sendbuffer = join_messages + self.sendbuffer
        else:
            self.sendbuffer = self.sendbuffer + join_messages

        # Warning: if there are many channels to join, the JOIN messages may be slowed down to comply with rate limiting. Some of these announcement messages will then be sent before the bot has actually joined the channel.
        # The code currently only calls for joins to be announced in situations where only one channel is being joined, so this case *should* not usually occur.
        # TODO: Join announcements should instead only be sent once the bot receives a confirmation that it has joined the channel successfully (Twitch IRC message 366?).
        for channel in channels:
            if announce:
                self.message(f"#{channel}", f"Now joined #{channel}.")

    def reconnect(self):
        self.authenticated = False # Pause all message sending
        seconds_since_last_connect = (datetime.datetime.now() - self.last_connect_time).total_seconds()
        if seconds_since_last_connect < 30:
            print(f"{settings.now()} [IRC] Last connection attempt was {seconds_since_last_connect}s ago. Waiting {2 * seconds_since_last_connect}s.")
            time.sleep(2 * seconds_since_last_connect)
        self.last_connect_time = datetime.datetime.now()
        print(f"{settings.now()} [IRC] Connecting to Twitch IRC.")

        # Remove all JOIN messages from the sendbuffer, because reconnect() will send a new JOIN for all channels.
        new_sendbuffer = []
        for msg in self.sendbuffer:
            if msg[0:4] != "JOIN":
                new_sendbuffer.append(msg)
        self.sendbuffer = new_sendbuffer

        self.connection.close()
        self.connection = socket.socket()
        self.connection.settimeout(480) # 8 minutes
        self.readbuffer = ""
        try:
            self.connection.connect((self.HOST,self.PORT))
        except Exception:
            time.sleep(10)
            return
        self.send_instant("CAP REQ :twitch.tv/tags twitch.tv/commands")
        self.send_instant(f"PASS oauth:{settings.twitch_token}")
        self.send_instant(f"NICK {settings.twitch_nick}")

        # Queue JOIN messages for all channels. Add bot's own channel to the beginning of the channel list
        if settings.twitch_nick != "" and settings.twitch_nick not in self.channels:
            self.channels = [settings.twitch_nick] + self.channels
        self.join()
        # time.sleep(1)
