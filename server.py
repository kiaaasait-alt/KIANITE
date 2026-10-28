import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST = "127.0.0.1"
PORT = 8000

DATA_DIR = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ADMINS_FILE = os.path.join(DATA_DIR, 'admins.json')
KEYS_FILE = os.path.join(DATA_DIR, 'keys.json')

def ensure_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'w') as f:
            json.dump([], f)
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'w') as f:
            json.dump([], f)

ensure_data()

first_names = ["alex","jordan","tyler","ryan","josh","chris","mike","jason","kyle","brandon","justin","andrew","matt","matthew","david","james","john","daniel","nathan","ethan"]
first_female = ["emily","sarah","ashley","jessica","amanda","lauren","megan","hannah","olivia","emma"]
last_names = ["smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez"]
words = ["shadow","ghost","dark","night","blood","frost","blaze","storm","thunder","venom"]
aesthetic = ["x", "z", "v", "ex", "yn", "ix"]

MODES = {"og", "lastnames", "swag", "killer", "short", "aesthetic"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.roblox.com",
    "Referer": "https://www.roblox.com/",
}

def num():
    choices = ["123","1234","111","222","333","444","555","666","777","888","999","420","69","1337"]
    return random.choice(choices)

def make_name(mode):
    first = random.choice(first_names + first_female)
    if mode == "lastnames":
        return first + random.choice(last_names) + num()
    if mode == "swag":
        return first + "swag" + num()
    if mode == "killer":
        return first + "killer" + num()
    if mode == "short":
        return first[:3] + num()[:3]
    if mode == "aesthetic":
        return first + random.choice(aesthetic) + num()[:2]
    return first + random.choice(words) + num()

def http_json(url, payload=None, timeout=10):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            raise
        raise
    except Exception as e:
        raise

def account_year(created):
    if not created:
        return None
    try:
        return datetime.fromisoformat(str(created).replace("Z", "+00:00")).year
    except:
        try:
            return int(str(created)[:4])
        except:
            return None

def check_batch(names, min_year, max_year):
    try:
        data = http_json("https://users.roblox.com/v1/usernames/users", {"usernames": names, "excludeBannedUsers": False}, timeout=10)
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return None
        return []
    except:
        return []
    
    found = []
    for user in data.get("data", []) or []:
        uid = user.get("id")
        if not uid:
            continue
        try:
            info = http_json("https://users.roblox.com/v1/users/%s" % uid, timeout=8)
        except:
            continue
        created = info.get("created")
        year = account_year(created)
        if year is None or not (min_year <= year <= max_year):
            continue
        found.append({
            "username": info.get("name") or info.get("displayName") or user.get("name") or "",
            "displayName": info.get("displayName") or "",
            "description": info.get("description") or "",
            "isBanned": bool(info.get("isBanned")),
            "hasVerifiedBadge": bool(info.get("hasVerifiedBadge")),
            "hasDetails": True,
            "id": uid,
            "created": str(created)[:10],
            "year": year,
        })
    return found

def run_scan(mode, min_year, max_year, batches=6):
    name_batches = [[make_name(mode) for _ in range(12)] for _ in range(batches)]
    checked = batches * 12
    results = []
    limited = False
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(check_batch, names, min_year, max_year) for names in name_batches]
        for future in as_completed(futures):
            try:
                batch_result = future.result(timeout=20)
            except:
                continue
            if batch_result is None:
                limited = True
            elif isinstance(batch_result, list):
                results.extend(batch_result)
    unique = {}
    for record in results:
        uid = str(record["id"])
        if uid not in unique:
            unique[uid] = record
    return checked, list(unique.values()), limited

STATIC_FILES = {
    "/index.html": "text/html; charset=utf-8",
    "/style.css": "text/css; charset=utf-8",
    "/app.js": "application/javascript; charset=utf-8",
    "/admin.html": "text/html; charset=utf-8",
}

IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}
AUDIO_TYPES = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg"}

def read_json_file(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

def write_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

class Handler(BaseHTTPRequestHandler):
    server_version = "Kianite/1.0"
    
    def log_message(self, fmt, *args):
        pass
    
    def _send(self, status, body, content_type):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
    
    def _json(self, status, payload):
        self._send(status, json.dumps(payload), "application/json; charset=utf-8")
    
    def _serve_static_file(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        content_type = IMAGE_TYPES.get(ext) or AUDIO_TYPES.get(ext)
        if not content_type and filename in STATIC_FILES:
            content_type = STATIC_FILES[filename]
        if not content_type:
            self._send(404, "Not found", "text/plain")
            return
        path = os.path.join(BASE_DIR, filename.lstrip('/'))
        if not os.path.isfile(path):
            self._send(404, "Not found", "text/plain")
            return
        try:
            with open(path, 'rb') as f:
                body = f.read()
            self._send(200, body, content_type)
        except:
            self._send(500, "Error", "text/plain")
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/media':
            images = []
            tracks = []
            for name in os.listdir(BASE_DIR):
                full = os.path.join(BASE_DIR, name)
                if not os.path.isfile(full):
                    continue
                ext = os.path.splitext(name)[1].lower()
                if ext in IMAGE_TYPES:
                    images.append({'name': name, 'url': '/' + name})
                elif ext in AUDIO_TYPES:
                    tracks.append({'name': name, 'url': '/' + name})
            images.sort(key=lambda x: 0 if x['name'] == 'kia.png' else 1)
            tracks.sort(key=lambda x: (0 if 'wiv' in x['name'].lower() else (1 if 'angel' in x['name'].lower() else 2)))
            return self._json(200, {'background': images[0] if images else None, 'tracks': tracks, 'track': tracks[0] if tracks else None})
        
        if path == '/api/avatar':
            qs = parse_qs(parsed.query)
            uid = qs.get('id', [''])[0]
            if not uid.isdigit():
                return self._json(400, {'error': 'bad'})
            try:
                thumb = http_json(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={uid}&size=150x150&format=Png&isCircular=false", timeout=6)
                data = thumb.get('data') or []
                return self._json(200, {'avatar': data[0].get('imageUrl') if data else None})
            except:
                return self._json(200, {'avatar': None})
        
        if path == '/api/profile':
            qs = parse_qs(parsed.query)
            uid = qs.get('id', [''])[0]
            if not uid.isdigit():
                return self._json(400, {'error': 'bad'})
            try:
                info = http_json(f"https://users.roblox.com/v1/users/{uid}", timeout=8)
                return self._json(200, {
                    'id': info.get('id'), 'username': info.get('name'), 'displayName': info.get('displayName'),
                    'description': info.get('description') or '', 'created': info.get('created'),
                    'isBanned': bool(info.get('isBanned')), 'hasVerifiedBadge': bool(info.get('hasVerifiedBadge'))
                })
            except:
                return self._json(404, {'error': 'not found'})
        
        if path == '/api/lookup':
            qs = parse_qs(parsed.query)
            query = qs.get('query', [''])[0]
            if not query:
                return self._json(400, {'error': 'missing'})
            try:
                user = None
                if query.isdigit():
                    user = http_json(f"https://users.roblox.com/v1/users/{query}", timeout=8)
                else:
                    lookup = http_json("https://users.roblox.com/v1/usernames/users", {"usernames": [query], "excludeBannedUsers": False}, timeout=8)
                    if lookup.get('data'):
                        user = http_json(f"https://users.roblox.com/v1/users/{lookup['data'][0]['id']}", timeout=8)
                if not user or not user.get('id'):
                    return self._json(404, {'error': 'not found'})
                thumb = http_json(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user['id']}&size=150x150&format=Png&isCircular=false", timeout=6)
                thumb_data = thumb.get('data') or []
                return self._json(200, {
                    'success': True,
                    'user': {'id': user['id'], 'username': user['name'], 'displayName': user['displayName'], 'created': user['created'], 'description': user.get('description') or '', 'isBanned': bool(user.get('isBanned')), 'hasVerifiedBadge': bool(user.get('hasVerifiedBadge'))},
                    'avatar': thumb_data[0].get('imageUrl') if thumb_data else None,
                    'verified': bool(user.get('hasVerifiedBadge')),
                    'inventoryPublic': random.choice(['public', 'private']),
                    'lastSeen': random.choice(['Recently', 'Online/Recently', 'Unknown'])
                })
            except:
                return self._json(404, {'error': 'not found'})
        
        if path == '/':
            path = '/index.html'
        filename = path.lstrip('/')
        if filename.lower() == 'admin.html' or filename in os.listdir(BASE_DIR):
            self._serve_static_file(filename)
            return
        if path in STATIC_FILES:
            self._serve_static_file(path)
            return
        self._send(404, "Not found", "text/plain")
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length) if length else b'{}'
            payload = json.loads(raw.decode('utf-8') or '{}')
        except:
            payload = {}
        
        if path == '/api/scan':
            try:
                mode = str(payload.get('mode', 'og')).lower()
                if mode not in MODES:
                    mode = 'og'
                min_year = int(payload.get('minYear', 2015))
                max_year = int(payload.get('maxYear', 2017))
                batches = int(payload.get('batches', 6))
                checked, found, limited = run_scan(mode, min_year, max_year, batches)
                return self._json(200, {'checked': checked, 'found': found, 'limited': limited})
            except Exception as e:
                return self._json(500, {'error': str(e)})
        
        if path == '/api/auth':
            try:
                action = payload.get('action')
                username = str(payload.get('username', '')).strip()
                password = str(payload.get('password', '')).strip()
                users = read_json_file(USERS_FILE, [])
                if action == 'signup':
                    if not username or not password:
                        return self._json(200, {'error': 'Missing credentials'})
                    if any(u.get('username','').lower() == username.lower() for u in users):
                        return self._json(200, {'error': 'Username taken'})
                    user = {'id': str(int(time.time()*1000)) + str(random.randint(1000,9999)), 'username': username, 'password': password, 'createdAt': datetime.now().isoformat(), 'banned': False, 'hits': []}
                    users.append(user)
                    write_json_file(USERS_FILE, users)
                    return self._json(200, {'success': True, 'user': {'id': user['id'], 'username': user['username']}})
                if action == 'login':
                    if not username or not password:
                        return self._json(200, {'error': 'Missing credentials'})
                    user = next((u for u in users if u.get('username','').lower() == username.lower() and u.get('password') == password), None)
                    if not user:
                        return self._json(200, {'error': 'Invalid credentials'})
                    if user.get('banned'):
                        return self._json(200, {'error': 'Account banned'})
                    return self._json(200, {'success': True, 'user': {'id': user['id'], 'username': user['username']}})
                return self._json(200, {'error': 'Invalid action'})
            except Exception as e:
                return self._json(200, {'error': 'Server error'})
        
        if path == '/api/hits':
            try:
                action = payload.get('action')
                userId = payload.get('userId')
                users = read_json_file(USERS_FILE, [])
                if action == 'get':
                    user = next((u for u in users if u.get('id') == userId), None)
                    if not user:
                        return self._json(404, {'error': 'not found'})
                    return self._json(200, {'hits': user.get('hits', [])})
                if action == 'add':
                    hit = payload.get('hit')
                    idx = next((i for i,u in enumerate(users) if u.get('id') == userId), -1)
                    if idx == -1:
                        return self._json(404, {'error': 'not found'})
                    if not users[idx].get('hits'):
                        users[idx]['hits'] = []
                    hit_copy = dict(hit)
                    hit_copy['addedAt'] = datetime.now().isoformat()
                    users[idx]['hits'].insert(0, hit_copy)
                    write_json_file(USERS_FILE, users)
                    return self._json(200, {'success': True, 'hits': users[idx]['hits']})
                return self._json(400, {'error': 'bad'})
            except Exception as e:
                return self._json(500, {'error': str(e)})
        
        if path == '/api/admin':
            try:
                action = payload.get('action')
                key = payload.get('key')
                keys = read_json_file(KEYS_FILE, [])
                admins = read_json_file(ADMINS_FILE, [])
                users = read_json_file(USERS_FILE, [])
                if action == 'verify_key':
                    k = next((x for x in keys if x.get('key') == key and not x.get('used')), None)
                    if not k:
                        return self._json(401, {'error': 'invalid'})
                    k['used'] = True
                    k['usedAt'] = datetime.now().isoformat()
                    write_json_file(KEYS_FILE, keys)
                    if not any(a.get('key') == key for a in admins):
                        admins.append({'key': key, 'addedAt': datetime.now().isoformat()})
                        write_json_file(ADMINS_FILE, admins)
                    return self._json(200, {'success': True})
                if action == 'get_data':
                    if not any(a.get('key') == key for a in admins):
                        return self._json(401, {'error': 'unauthorized'})
                    return self._json(200, {'users': users})
                if action == 'ban_user':
                    if not any(a.get('key') == key for a in admins):
                        return self._json(401, {'error': 'unauthorized'})
                    uid = payload.get('userId')
                    ban = payload.get('ban') == True
                    for u in users:
                        if u.get('id') == uid:
                            u['banned'] = ban
                            break
                    write_json_file(USERS_FILE, users)
                    return self._json(200, {'success': True})
                return self._json(400, {'error': 'bad'})
            except Exception as e:
                return self._json(500, {'error': str(e)})
        
        self._send(404, "Not found", "text/plain")

def main():
    port = PORT
    server = None
    for candidate in range(PORT, PORT + 10):
        try:
            server = ThreadingHTTPServer((HOST, candidate), Handler)
            port = candidate
            break
        except OSError:
            continue
    if not server:
        print("No port available")
        return
    url = f"http://{HOST}:{port}/"
    print(f"Kianite running at {url}")
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
