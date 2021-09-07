import requests, re, json, websocket, time


class AuthenticationError(Exception):
    pass


class CredentialsError(Exception):
    pass


class CharacterError(Exception):
    pass


def login(username, password):
    headers = {
        "x-csrftoken": "a",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
        "referer": "https://scratch.mit.edu",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
    data = json.dumps({"username": username, "password": password})
    request = requests.post("https://scratch.mit.edu/login/", data = data, headers = headers)
    try:
        session_id = re.search('"(.*)"', request.headers["Set-Cookie"]).group()
    except AttributeError:
        raise CredentialsError("Incorrect username or password")
    token = request.json()[0]["token"]
    csrf_token = re.search("scratchcsrftoken=(.*?);", request.headers["Set-Cookie"]).group(1)
    return [session_id, token, csrf_token, username]


def post_comment(username, content, parent_id = "", commentee_id = ""):
    try:
        headers = {
        "x-csrftoken": session[2],
        "X-Token": session[1],
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "scratchcsrftoken=" + session[2] + ";scratchlanguage=en;scratchsessionsid=" + session[0] + ";",
        "referer": f"https://scratch.mit.edu/users/{username}/"
        }
    except NameError:
    	raise AuthenticationError("You need to log in to post comments")
    data = json.dumps({
        "commentee_id": commentee_id,
        "content": content,
        "parent_id": parent_id})
    requests.post(f"https://scratch.mit.edu/site-api/comments/user/{username}/add/", headers = headers, data = data)
    
    
def follow(user):
	try:
		headers = {
		"x-csrftoken": session[2],
		"X-Token": session[1],
		"x-requested-with": "XMLHttpRequest",
		"Cookie": "scratchcsrftoken=" + session[2] + ";scratchlanguage=en;scratchsessionsid=" + session[0] + ";",
		"referer": f"https://scratch.mit.edu/users/" + session[3] + "/"
		}
	except NameError:
		raise AuthenticationError("You need to log in to follow a user")
	requests.put("https://scratch.mit.edu/site-api/users/followers/" + user + "/add/?usernames=" + session[3], headers = headers).json()


def unfollow(user):
    try:
        headers = {
        "x-csrftoken": session[2],
        "X-Token": session[1],
        "x-requested-with": "XMLHttpRequest",
        "Cookie": "scratchcsrftoken=" + session[2] + ";scratchlanguage=en;scratchsessionsid=" + session[0] + ";",
        "referer": f"https://scratch.mit.edu/users/" + session[3] + "/"
        }
    except NameError:
        raise AuthenticationError("You need to log in to unfollow a user")
    requests.put("https://scratch.mit.edu/site-api/users/followers/" + user + "/remove/?usernames=" + session[3], headers = headers).json()


def message_count(user):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/messages/count", headers = headers).json()["count"]


def user_id(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["id"]


def get_case(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["username"]


def location(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["profile"]["country"]


def join_date(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["history"]["joined"][:10]
    

def join_time(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["history"]["joined"][11:19]


def about_me(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["profile"]["bio"]


def wiwo(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["profile"]["status"]


def is_existing(user):
    return requests.get(f"https://scratch.mit.edu/users/{user}/").status_code == 200


def ever_existed(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").text != '{"code":"NotFound","message":""}'


def is_available(username):
    return requests.get(f"https://api.scratch.mit.edu/accounts/checkusername/{username}/").text == '{"username":"' + username + '","msg":"valid username"}'


def is_scratchteam(user):
    return requests.get(f"https://api.scratch.mit.edu/users/{user}/").json()["scratchteam"]


def followers(user):
    return requests.get(f"https://scratchdb.lefty.one/v3/user/info/{user}").json()["statistics"]["followers"]


def following(user):
    return requests.get(f"https://scratchdb.lefty.one/v3/user/info/{user}").json()["statistics"]["following"]
    

def followers_list(user):
	done = False
	offset = 0
	page = 1
	followers = list()
	while done == False:
	   with requests.get(f"https://api.scratch.mit.edu/users/{user}/followers?offset={offset}") as request:
	   	followers.extend(request.json())
	   	if (len(request.json()) != 20):
	   		done = True
	   	else:
	   	 offset += 20
	   	 page += 1
	my_list = list()
	for user in followers:
		my_list.append(user["username"])
	return my_list
	
	
def following_list(user):
	done = False
	offset = 0
	page = 1
	following = list()
	while done == False:
	   with requests.get(f"https://api.scratch.mit.edu/users/{user}/following?offset={offset}") as request:
	   	following.extend(request.json())
	   	if (len(request.json()) != 20):
	   		done = True
	   	else:
	   	 offset += 20
	   	 page += 1
	my_list = list()
	for user in following:
		my_list.append(user["username"])
	return my_list


def total_loves(user):
    return requests.get(f"https://scratchdb.lefty.one/v3/user/info/{user}").json()["statistics"]["loves"]


def total_favorites(user):
    return requests.get(f"https://scratchdb.lefty.one/v3/user/info/{user}").json()["statistics"]["favorites"]


def total_views(user):
    return requests.get(f"https://scratchdb.lefty.one/v3/user/info/{user}").json()["statistics"]["views"]


def set_cloud_var(name, value, project_id):
    ws = websocket.WebSocket()
    def sendPacket(packet):
        ws.send(json.dumps(packet) + '\n')
    def connect():
        global ws
        ws.connect("wss://clouddata.scratch.mit.edu", cookie = "scratchsessionsid=" + session[0] + ";", origin = "https://scratch.mit.edu", enable_multithread = True)
        sendPacket({
            "method": "handshake",
            "user": session[3],
            "project_id": str(project_id)
            })
    try:
        sendPacket({
      "method": "set",
      "name": "☁ " + name,
      "value": str(value),
      "user": session[3],
      "project_id": str(project_id)
    })
    except BrokenPipeError:
        connect()
        time.sleep(0.1)
        set_cloud_var(name, value)



def encode(val):
    chars = ['', '', '', '', '', '', '', '', '', 
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    '!', '@', '#', '$', '%', '^', '*', '(', ')', '-', '_', '+', '=', '<', '>', ',', '\\', '/', '{', '}', '[', ']', ';', '.', "'", '"', ':', ' ']
    val = str(val)
    encoded = ""
    for i in range (1, len(val) + 1):
        try:
            encoded = str(encoded) + str(chars.index(val[i - 1]) + 1)
        except ValueError:
            raise CharacterError("Your string contains an unsupported character. The supported characters are: abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^*()-_+=<>,\/{}[];.'\": and Space")
    return int(encoded + "00")


def decode(val):
    chars = ['', '', '', '', '', '', '', '', '', 
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    '!', '@', '#', '$', '%', '^', '*', '(', ')', '-', '_', '+', '=', '<', '>', ',', '\\', '/', '{', '}', '[', ']', ';', '.', "'", '"', ':', ' ']
    value = ""
    idx = None
    i = 1
    val = str(val)
    while True:
        idx = val[i - 1] + val[i]
        i += 2
        if idx < 1:
            break
        value += chars[int(idx) - 1]
    return value
