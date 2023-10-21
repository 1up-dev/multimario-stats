# multimario-stats
This is the program that runs the scoreboard and Twitch chat bot for **[The 602 Race](https://docs.google.com/spreadsheets/d/1ludkWzuN0ZzMh9Bv1gq9oQxMypttiXkg6AEFvxy_gZk/)** and other Multi-Mario endurance races.  
See **[this video archive](https://www.twitch.tv/videos/1856764496)** for an example of it in use.  
![Example](https://i.imgur.com/bHeYEUO.jpg)

## What is the 602 Race?  
>The 602 Race is an endurance race to 100% completion of four 3D Super Mario games, with a total of 602 Stars to be collected.  
>The four games in order are: Super Mario 64: 120 Stars, Super Mario Galaxy: 120 Stars, Super Mario Sunshine: 120 Shines, and Super Mario Galaxy 2: 242 Stars.

## Running
- Rename `settings-template.json` to `settings.json` and fill out the fields.
- Running the program will make the bot active in the Twitch chats of all the racers and the extra chat rooms specified in `settings.json`.
- The bot gets its login info and makes API requests using a Twitch developer application. Register an application here: https://dev.twitch.tv/console. Add `http://localhost:3000` as an OAuth Redirect URL, then copy the `Client ID` and `Client Secret` into `settings.json`. After you start the program, it will open a browser window and prompt you to grant access using your desired account for the bot. The `token` and `refresh-token` fields will then be filled out automatically.
- The Google API Key is used to get the list of racers from the race spreadsheet. You will need to create a new project that has access to the Google Sheets API. https://console.developers.google.com/apis/dashboard
- For the OBS start- and stop-stream functionality to work, open your desired streaming profile on OBS, go to the Tools menu at the top of the window, and select `WebSocket Server Settings`. Check `Enable WebSocket server`, set `Server Port` to `4455`, and **un**check `Enable Authentication`.
- Setting `"testing-gsheet"` in `settings.json` will enable testing mode:
    - The provided testing Google Sheet will be used to get the list of racers instead of the official race sheet.
    - Each racer will be given random stats.
    - Racer status updates (done, quit, etc) will not be mirror-posted in the main channel, to avoid spam while testing.
