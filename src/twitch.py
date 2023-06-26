import requests
import json
import urllib
import os
import threading
import time
import http.server
import socketserver
import webbrowser
import pygame
import settings

class HTTPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global twitch_auth_code
        if 'code=' in self.path:
            twitch_auth_code = self.path.split('code=')[1].split('&')[0]
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b"multimario-stats: Received Twitch authorization.<br>You may close this page.")
        return

def req(method, url, headers={}, params={}, retry=False):
    if method == "GET":
        response = requests.get(url, params=params, headers=headers)
    elif method == "POST":
        response = requests.post(url, params=params, headers=headers)
    else:
        return
    data = response.json()
    if response.status_code == 401:
        if retry:
            print(f"[API] 401 Invalid token after retrying. Giving up.")
            return
        print(f"[API] 401 Invalid token. Attempting to refresh token. {data}")
        if validate_token():
            headers["Authorization"] = f'Bearer {settings.twitch_token}'
            return req(method, url, headers, params, True)
        print("[API] Token refresh failed. Giving up on request.")
        return
    if response.status_code not in range(200,300):
        print(f"[API] Bad request. Giving up. ({response.status_code}): {data}")
        return
    return data

def get_player_infos(logins, playerLookup):
    user_infos = get_user_infos(logins)
    if user_infos == None:
        return
    for info in user_infos:
        login = info['login']
        racer = playerLookup[login]
        path = settings.path(f"profiles/{racer.name}.png")
        if not os.path.isfile(path):
            urllib.request.urlretrieve(info['profile_image_url'], path)
        racer.profile = pygame.image.load(path)
        racer.twitch_id = info['id']
        racer.display_name = info['display_name']
        settings.redraw = True

def get_player_infos_async(logins, playerLookup):
    t = threading.Thread(target=get_player_infos, args=(logins, playerLookup,))
    t.daemon = True
    t.start()

def create_clip(broadcaster_id, username):
    time.sleep(20)
    headers = {"Client-Id":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
    params = {"broadcaster_id": broadcaster_id}
    response = req("POST", "https://api.twitch.tv/helix/clips", headers, params)
    if response == None:
        return
    responseData = response['data']
    if len(responseData) == 0 or 'edit_url' not in responseData[0]:
        print(f"Clip request failed. {response}")
        return
    link = responseData[0]['edit_url']
    with open(settings.path(f"clip-links.txt"), 'a+') as f:
        f.write(f"{settings.now()} {username}: {link}\n")

def create_clip_async(broadcaster_id, username):
    t = threading.Thread(target=create_clip, args=(broadcaster_id, username,))
    t.daemon = True
    t.start()

def get_user_infos(users):
    all_infos = []
    j = 0
    while True:
        url = "https://api.twitch.tv/helix/users" + "?login=" + "&login=".join(users[j:j+100])
        headers = {"Client-ID":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
        response = req("GET", url, headers)
        if response == None:
            return
        all_infos = all_infos + response['data']
        j += 100
        if users[j:j+100] == []:
            break
    return all_infos

def validate_token():
    print("[API] Validating token...")

    # Validate token
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {settings.twitch_token}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            settings.twitch_nick = data['login']
            print("[API] Token is valid.")
            return True
    print("[API] Token is invalid. Refreshing.", response.status_code, data)

    # Refresh token
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": settings.twitch_clientid, "client_secret": settings.twitch_secret, "grant_type": "refresh_token", "refresh_token": settings.twitch_refresh_token}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            settings.twitch_token = data['access_token']
            settings.twitch_refresh_token = data['refresh_token']
            settings.save_api_tokens_to_file()
            if not validate_token():
                print("[API] Refreshed token is invalid. Giving up.")
                return False
            print("[API] Token refreshed.")
            return True
    print("[API] Token refresh failed. Requesting authorization from user.", response.status_code, data)

    # Request authorization from user
    global twitch_auth_code
    twitch_auth_code = ""
    port = 3000
    webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?client_id={settings.twitch_clientid}&redirect_uri=http://localhost:{port}&response_type=code&scope=clips:edit+chat:edit+chat:read+whispers:edit+whispers:read")
    with socketserver.TCPServer(("localhost", port), HTTPHandler) as server:
        print(f"[API] HTTP server waiting for Twitch authorization at localhost:{port}")
        server.handle_request()
    if twitch_auth_code == "":
        print("[API] Authorization request failed.")
        return False

    # Request new token
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id":settings.twitch_clientid, "client_secret":settings.twitch_secret, "code":twitch_auth_code, "grant_type":"authorization_code", "redirect_uri":f"http://localhost:{port}"}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code not in range(200,300):
        print("[API] New token request failed.", response.status_code, data)
        return False
    if data == None:
        print("[API] New token request failed.", response.status_code, data)
        return False
    settings.twitch_token = data["access_token"]
    settings.twitch_refresh_token = data["refresh_token"]
    settings.save_api_tokens_to_file()
    print("[API] New token received. Validating...")
    
    # Validate token
    if validate_token():
        return True
    print("[API] New token is invalid. Giving up.")
    return False
