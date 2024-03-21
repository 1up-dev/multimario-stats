import requests
import threading
import time
import http.server
import socketserver
import webbrowser
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
    if response.status_code == 401:
        if retry:
            print(f"{settings.now()} [API] 401 after refreshing token. Giving up.")
            return
        # print(f"{settings.now()} [API] 401. Refreshing token. {response.json()}")
        if refresh_token():
            headers["Authorization"] = f'Bearer {settings.twitch_token}'
            return req(method, url, headers, params, retry=True)
        # Token refresh failed.
        return
    return response

def create_clip(broadcaster_id, username):
    # Wait 15 seconds before clipping in order to capture more of the reaction in the clip
    time.sleep(15)
    headers = {"Client-Id":settings.twitch_clientid, "Authorization":f'Bearer {settings.twitch_token}'}
    params = {"broadcaster_id": broadcaster_id}
    response = req("POST", "https://api.twitch.tv/helix/clips", headers, params)

    error_message = ""
    if response == None:
        error_message = "API request failed (Empty response).\n"
    elif response.status_code == 400:
        error_message = "Broadcaster ID {broadcaster_id} not found.\n"
    elif response.status_code == 403:
        error_message = "Clip creation is restricted on this channel.\n"
    elif response.status_code == 404:
        error_message = "This channel is offline.\n"
    elif response.status_code not in range(200,300):
        error_message = "Clip request failed (unknown error): {response.status_code} {response.json()}\n"
    elif response.json() == None or len(response.json()['data']) == 0 or 'edit_url' not in response.json()['data'][0]:
        error_message = "Successful API response has no clip link. {response.status_code} {response.json()}\n"
    
    start_time = settings.startTime.isoformat().split("T")[0]
    logfile = settings.path(f"log/{start_time}-clips.log")
    if error_message != "":
        with open(logfile, 'a+') as f:
            f.write(f"{settings.now()} {username} {error_message}")
        return
    
    clip_link = response.json()['data'][0]['edit_url']
    with open(logfile, 'a+') as f:
        f.write(f"{settings.now()} {username} {clip_link}\n")

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
            return []
        if response.status_code not in range(200,300):
            print(f"{settings.now()} [API] Userinfo request failed: {response.status_code} {response.json()}")
            return []
        response_json = response.json()
        if response_json == None:
            return []
        all_infos = all_infos + response_json['data']
        j += 100
        if users[j:j+100] == []:
            break
    return all_infos

def validate_token(nested=False):
    # Validate token
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {settings.twitch_token}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if response.status_code in range(200,300):
        if data != None:
            # Token is valid.
            settings.twitch_nick = data['login']
            return True
    if nested:
        # Avoid infinite loops on misbehaving API requests
        return False
    # print(f"{settings.now()} [API] Token is invalid. Refreshing. {response.status_code} {data}")
    refresh_token()

def refresh_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id": settings.twitch_clientid, "client_secret": settings.twitch_secret, "grant_type": "refresh_token", "refresh_token": settings.twitch_refresh_token}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code not in range(200,300) or data == None:
        print(f"{settings.now()} [API] Token refresh failed. Requesting authorization from user. {response.status_code} {data}")
        return new_token()
    # Token refreshed.
    settings.twitch_token = data['access_token']
    settings.twitch_refresh_token = data['refresh_token']
    settings.save_api_tokens_to_file()

    # Validate the new token in order to retrieve the bot's username
    if not validate_token(nested=True):
        print(f"{settings.now()} [API] Refreshed token is invalid. Giving up.")
        return False
    # print(f"{settings.now()} [API] Token refreshed.")
    return True

def new_token():
    # Request authorization from user
    global twitch_auth_code
    twitch_auth_code = ""
    port = 3000
    webbrowser.open(f"https://id.twitch.tv/oauth2/authorize?client_id={settings.twitch_clientid}&redirect_uri=http://localhost:{port}&response_type=code&scope=clips:edit+chat:edit+chat:read+whispers:edit+whispers:read")
    with socketserver.TCPServer(("localhost", port), HTTPHandler) as server:
        print(f"{settings.now()} [API] HTTP server waiting for Twitch authorization at localhost:{port}")
        server.handle_request()
    if twitch_auth_code == "":
        print(f"{settings.now()} [API] Authorization request failed.")
        return False

    # Request new token
    url = "https://id.twitch.tv/oauth2/token"
    params = {"client_id":settings.twitch_clientid, "client_secret":settings.twitch_secret, "code":twitch_auth_code, "grant_type":"authorization_code", "redirect_uri":f"http://localhost:{port}"}
    response = requests.post(url, params=params)
    data = response.json()
    if response.status_code not in range(200,300):
        print(f"{settings.now()} [API] New token request failed. {response.status_code} {data}")
        return False
    if data == None:
        print(f"{settings.now()} [API] New token request failed. {response.status_code} {data}")
        return False
    settings.twitch_token = data["access_token"]
    settings.twitch_refresh_token = data["refresh_token"]
    settings.save_api_tokens_to_file()

    # Validate the new token in order to retrieve the bot's username
    if not validate_token(nested=True):
        print(f"{settings.now()} [API] New token is invalid. Giving up.")
        return False

    print(f"{settings.now()} [API] New token received.")
    return True
