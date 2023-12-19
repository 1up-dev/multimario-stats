# Bot commands
## Commands for Anyone
#### !roles [twitch_username]
+ List the roles of `[twitch_username]`.
+ If `[twitch_username]` is not specified, list the roles of the user that sent the command.
#### !place [number]
+ Show who is in place #`[number]` and their current status.
+ If the requested place number does not currently exist, the bot will display the info for the next highest existing place (This may happen if there are ties).
#### !place [twitch_username]
+ If `[twitch_username]` is a racer, show their current status.
#### !mmhelp
+ Post the link to this command list. (https://bit.ly/44P3Y46)

## Commands for Counters  
*To get permission to count, ask a racer or an admin.*  
*Note: VIPs and Mods can count without being explicitly given permission.*  
#### !add [twitch_username] [number]  
+ Add `[number]` to the total score for `[twitch_username]`.  
+ Positive and negative numbers are accepted.  
#### !set [twitch_username] [number]  
+ Set the total score for `[twitch_username]` to `[number]`.  
+ Inline addition is allowed. (`!set Odme_ 70+120+120+32`)  
   
## Commands for Racers  
#### !add [number]  
+ Add `[number]` to your total score.  
+ Positive and negative numbers are accepted.  
#### !set [number]  
+ Set your total score to `[number]`.  
+ Inline addition is allowed. (`!set 70+120+120+32`)  
#### !place  
+ Check what place you are currently in and show your current score.  
#### !quit  
+ Quit the race.  
#### !unquit/!rejoin  
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
*Note: ⚠️ indicates a destructive command that is not easily undone.*
#### !forcequit/!noshow/!dq [twitch_username]  
+ Set the status of `[twitch_username]` to "Quit", "No-Show", or "Disqualified".  
#### !revive [twitch_username]  
+ Undo a quit, dq, noshow, or finish and set the racer to "Live" status.  
#### !settime [twitch_username] [duration]  
+ Set a racer's run duration on the "done" or "quit" card.  
+ Must be in this format: `32:59:59`  
#### !fetchracers  
+ Re-fetch the racer list from Google Sheets to add or remove racers.  
#### !start [date & time]  
+ If date & time are *not* given, set the start time of the race to the current time.  
+ When specifying the date & time, it must be in this format: `2018-12-29T14:59:59` `(YYYY-MM-DDTHH:MM:SS)`  
#### !togglestream  
+ Turn the Twitch stream on or off.  
#### !autostream  
+ Enable or disable automatic stream events (Stream automatically turns on before the race begins, and turns off after all racers stop or the time limit is reached.)
#### !addcounter/!removecounter [twitch_username]  
+ Add or remove `[twitch_username]` as a counter.  
#### !block/!unblock [twitch_username]  
+ Add or remove `[twitch_username]` to the blocklist, preventing them from counting.  
#### !admin [twitch_username]  
+ Add `[twitch_username]` as a new admin.  
#### !mmleave/!mmjoin [twitch_username]  
+ Ask the bot to leave or join the chat of `[twitch_username]`.  
#### !extrachannels
+ View the list of extra channels where the bot is currently active.  
#### !clearstats
+ ⚠️ Set the score of all racers to 0 and the status of all racers to "live".  
#### !removeracer [twitch_username]  
+ Remove `[twitch_username]` from the stats stream manually without changing the Google sheet (Useful if there is a nearly-blank last page with only no-shows on it, and you want to remove those racers from the stream but not from the Google sheet). If `!fetchracers` is run after doing this, it will add the racer back onto the stream.
#### !mmkill  
+ ⚠️ Close the stats program and bot permanently. If the program is unable to stop the stream, the stream will be stuck live with a blank screen until the host restarts the program or stops the stream.  
