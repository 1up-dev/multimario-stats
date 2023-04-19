import json
import requests
import settings

def getRacers():
    sheetRacers = []
    race_num = 0
    if 'race-num' in settings.modeInfo:
        race_num = settings.modeInfo['race-num']

    url = settings.gsheet + settings.google_api_key
    response = requests.get(url, headers={})
    if response.status_code not in range(200,300):
        response = json.loads(response.content.decode("UTF-8"))["error"]
        print('[!] Google Sheets API request failed. ' + str(response["code"]) +': '+response["message"])
        return []

    response = json.loads(response.content.decode("UTF-8"))
    for row in response["values"]:
        if row == [] or row[0] == "Theoretical WR":
            break
        if race_num <= 0:
            sheetRacers.append(row[0].strip())
            continue
        if len(row) < race_num+1:
            # not racing
            continue
        if(row[race_num] != ''):
            # racing
            sheetRacers.append(row[0].strip())
    
    return sheetRacers
