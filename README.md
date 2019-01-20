# 602Stats
This is the program that runs the scoreboard and Twitch chat bot for [The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/).  
See [this video archive](https://www.twitch.tv/videos/356727983) from December 2018 for an example of it in use.  
  
## Stats stream bot commands:
**Note: Moderators of the Twitch channel the bot is in are automatically allowed to update. They do not have to be whitelisted manually.**
### **Commands for Updaters:**
#### !add [twitchname] [number]
- This adds to the total number of stars for [twitchname]. 
- It will update game completion as appropriate. 
- Positive and negative numbers are accepted.
   
### **Commands for Racers:**
#### !add [number]
- Positive and negative numbers are accepted.
#### !quit
- Quit the race. An admin can undo this if necessary.
#### !mod [twitchname]
- Adds [twitchname] as a star count updater.
#### !unmod [twitchname]
- Removes [twitchname] as a star count updater.
  
### **Commands for Admins:**
#### !start
- Sets the start time of the race to the current time. 
#### !start [date & time]
- Sets the start time of the race to the specified time.
- Must be in this format: 2018-12-29@09:00
  
#### !mod [twitchname]
#### !unmod [twitchname]
#### !forcequit [twitchname]
#### !noshow [twitchname]
#### !dq [twitchname]
#### !revive [twitchname]
- Undo a quit, dq, or noshow.
  
## Before you attempt to run the program
- WARNING: Running the program will join all the Twitch chats specified in racers.txt and make the bot active. Make sure racers.txt has the correct names in it before starting.  
- The program pulls the username and password (authentication token) for the bot from settings.txt. Get the authentication token from http://twitchapps.com/tmi/.  
- The Twitch developer app Client-ID is for API requests, get it from https://dev.twitch.tv/dashboard/apps.  
- admins.txt, racers.txt, and updaters.txt must contain only Twitch usernames separated by newlines.  
