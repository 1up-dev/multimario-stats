# Bot commands
## Commands for Anyone
#### !roles/!mmstatus [twitch_username]
+ List the roles of `[twitch_username]`. (Both commands are identical)
+ If `[twitch_username]` is not specificed, list the roles of the user that sent the command.
+ If the user is a racer, also show their status in the race.
#### !place [number]
+ Show who is in place #`[number]` in the race, what game they're up to, and how many collectibles they have in that game.
#### !mmcommands
+ Post the link to this command list: https://bit.ly/44P3Y46

## Commands for Counters  
*To get permission to count, ask a racer or an admin.*  
*Note: VIPs and Mods can count without being explicitly given permission.*  
#### !add [twitch_username] [number]  
+ Add `[number]` to the total amount of collectibles for `[twitch_username]`.  
+ Positive and negative numbers are accepted.  
+ Addition is allowed. (`!add Odme_ 70+120+120+32`)  
#### !set [twitch_username] [number]  
+ Set the total number of collectibles for `[twitch_username]` to `[number]`.  
   
## Commands for Racers  
#### !add [number]  
+ Add `[number]` to the total amount of collectibles for the racer that sent the command.  
+ Positive and negative numbers are accepted.  
+ Addition is allowed. (`!add 70+120+120+32`)  
#### !set [number]  
+ Set the total number of collectibles for the racer that sent the command to `[number]`.  
#### !quit  
+ Quit the race.  
#### !rejoin/!unquit   
+ Re-enter the race after quitting. (Both commands are identical)  
+ To rejoin after finishing, just use `!set` or `!add` to your desired score.  
#### !addcounter/!removecounter [twitch_username]  
+ Add or remove `[twitch_username]` as a counter.  
#### !mmjoin  
+ Ask the bot to join your channel if it is not already active there.   
+ Must be sent by a racer in a chat where the bot is active (like twitch.tv/MultiMarioEvents).  
+ Remember that if the bot is not responding, it may be delaying its responses to avoid getting globally muted by Twitch. Wait a couple minutes to be sure before attempting to !add/!set multiple times.  
   
## Commands for channel owner  
#### !mmleave  
+ Ask the bot to leave your channel. Must be sent by the channel owner in their own chat.  
   
## Commands for Admins  
#### !forcequit/!noshow/!dq [twitch_username]  
+ Set the status of `[twitch_username]` to "Quit", "No-Show", or "Disqualified".  
#### !revive [twitch_username]  
+ Undo a quit, dq, noshow, or finish and set the racer to "Live" status.  
#### !settime [twitch_username] [duration]  
+ Set a racer's run duration on the "done" or "quit" card.  
+ Must be in this format: `32:59:59`  
#### !fetchracers  
+ Re-fetch the racer list from the Google spreadsheet to add or remove racers.  
#### !start [date & time]  
+ If date & time are *not* given, set the start time of the race to the current time.  
+ When specifying the date & time, it must be in this format: `2018-12-29T14:59:59` `(YYYY-MM-DDTHH:MM:SS)`  
#### !togglestream  
+ Turn the Twitch stream on or off.  
#### !addcounter/!removecounter [twitch_username]  
+ Add or remove `[twitch_username]` as a counter.  
#### !block/!unblock [twitch_username]  
+ Add or remove `[twitch_username]` to the blocklist, preventing them from counting.  
#### !admin [twitch_username]  
+ Add `[twitch_username]` as a new admin.  
#### !mmleave/!mmjoin [twitch_username]  
+ Ask the bot to leave or join the chat of `[twitch_username]`.  
#### !clearstats
+ Set the score of all racers to 0 and the status of all racers to "live".  
#### !mmkill  
+ Close the stats program and bot. Warning: it will not turn back on automatically.  
