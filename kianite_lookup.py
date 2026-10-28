import base64
import random
import time
import threading
import queue
import webbrowser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter import ttk, messagebox
import string
import re

first_names = [
    "alex","jordan","tyler","ryan","josh","chris","mike","jason","kyle","brandon",
    "justin","andrew","matt","matthew","david","james","john","daniel","nathan","ethan",
    "noah","liam","lucas","mason","logan","jacob","william","ben","benjamin","elijah",
    "oliver","aiden","jack","owen","henry","michael","sam","samuel","joe","joseph",
    "tom","thomas","tim","timothy","nick","nicholas","eric","steve","steven","kevin",
    "brian","adam","austin","blake","chase","cole","dylan","hunter","parker","carter",
    "cameron","luke","jake","zach","zachary","sean","shawn","trevor","travis","bradley",
    "connor","caleb","cody","derek","garrett","grant","ian","isaac","jared","jeremy",
    "jonathan","kaden","kayden","landon","marcus","max","nolan","preston","riley","robert",
    "scott","seth","tanner","taylor","trent","tristan","victor","wesley","wyatt","xavier","zane","devin",
    "dominic","elliot","finn","grayson","hudson","kai","levi","miles","roman","silas",
    "spencer","theo","walker","weston","colton","jaxon","bryson","easton","gavin","hayden",
    "jace","jayden","lincoln","sawyer","sebastian"
]

first_female = [
    "emily","sarah","ashley","jessica","amanda","lauren","megan","hannah","olivia","emma","ava","sophia",
    "mia","chloe","grace","lily","zoey","rachel","rebecca","kayla","kaitlyn","madison","morgan","brittany",
    "brooke","chelsea","danielle","elizabeth","ella","hailey","isabella","jade","jasmine","jennifer","julia",
    "katie","kaylee","kimberly","lillian","mary","maya","michelle","natalie","paige","samantha","savannah",
    "skylar","victoria","zoe","abby","alyssa","amber","anna","ariana","autumn","bella","brianna","caitlin",
    "caroline","charlotte","claire","daisy","destiny","faith","gianna","jocelyn","kendall","leah","lucy",
    "maria","marissa","melissa","molly","naomi","nora","peyton","reagan","rose","ruby","sabrina","sierra",
    "stella","summer","valerie","vanessa","violet"
]

last_names = [
    "smith","johnson","williams","brown","jones","garcia","miller","davis","rodriguez","martinez",
    "hernandez","lopez","wilson","anderson","thomas","taylor","moore","jackson","martin","lee",
    "perez","thompson","white","harris","sanchez","clark","ramirez","lewis","robinson","walker",
    "young","allen","king","wright","scott","torres","nguyen","hill","flores","green",
    "adams","nelson","baker","hall","rivera","campbell","mitchell","carter","roberts","gomez",
    "phillips","evans","turner","diaz","parker","cruz","edwards","collins","reyes","stewart",
    "morris","murphy","cook","rogers","morgan","cooper","peterson","bailey","reed","kelly",
    "howard","ramos","kim","cox","ward","richardson","watson","brooks","wood","bennett",
    "gray","hughes","price","sanders","patel","myers","long","ross","foster","powell",
    "jenkins","perry","russell","sullivan","bell","coleman","butler","henderson","barnes","fisher"
]

words = [
    "shadow","ghost","dark","night","blood","frost","blaze","storm","thunder","venom","reaper","demon","angel",
    "wolf","tiger","dragon","phoenix","raven","snake","viper","blade","chaos","void","nova","pixel","cyber","neon",
    "toxic","lethal","savage","brutal","wicked","silent","hidden","secret","masked","anon","zero","null","glitch",
    "alpha","omega","sigma","prime","ultra","hyper","king","queen","lord","boss","ninja","samurai","assassin",
    "hunter","slayer","sniper","gunner","pro","gamer","player","xenon","flux","aura","zen","arc","rift","nova"
]

aesthetic = ["x","z","v","ex","yn","ix","ae","ly","en","el","on","ir","aeon","flux","byte","net","core"]

running = False
found = set()
q = queue.Queue()
mode = "og"
year_range = (2015, 2017)
checked = 0

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.roblox.com",
    "Referer": "https://www.roblox.com/"
})

def num():
    choices = [
        "123","1234","111","222","333","444","555","666","777","888","999","101","202","303","404","505",
        "606","707","808","909","121","131","141","151","161","171","181","191","212","232","242","252",
        "262","272","282","292","321","420","456","789","000","001","007","69","1337","9999","1111","0000"
    ]
    choices += [str(random.randint(100, 9999)) for _ in range(15)]
    return random.choice(choices)

def make_name():
    end = num()
    first = random.choice(first_names + first_female)
    
    if mode == "lastnames":
        return first + random.choice(last_names) + end
    
    if mode == "swag":
        return random.choice([
            first + "swag" + end,
            first + "swagg" + end,
            "swag" + first + end,
            "x" + first + "swag" + end[-3:],
            first + random.choice(aesthetic) + "swag" + end[-2:],
        ])
    
    if mode == "killer":
        return random.choice([
            first + "killer" + end,
            "killer" + first + end,
            first + "kill" + end,
            first + "reaper" + end[-3:],
            random.choice(words) + "kill" + end,
        ])
    
    if mode == "short":
        return random.choice([
            first[:3] + end[:3],
            first[:4] + end[:2],
            random.choice(words)[:3] + end[:3],
            first + end[:3],
        ])
    
    if mode == "aesthetic":
        return random.choice([
            first + random.choice(aesthetic) + end[-2:],
            random.choice(words) + random.choice(aesthetic) + end[-3:],
            first[:4] + random.choice(aesthetic) + random.choice(words)[:2],
            random.choice(aesthetic) + first + random.choice(aesthetic) + end[-2:],
            first + random.choice(words)[:3] + random.choice(aesthetic),
        ])
    
    # og / anything - high hit rate
    return random.choice([
        first + random.choice(words) + end,
        random.choice(words) + first + end,
        first + random.choice(last_names) + end,
        first + str(random.randint(10, 99)) + end,
        first + random.choice(["x","z","q","xx","zz","v"]) + end[-2:],
        random.choice(words) + str(random.randint(10, 99)) + end,
        first + random.choice(words)[:4] + end,
        first + first[-2:] + end,
        random.choice(words) + random.choice(words)[:3] + end,
        first + random.choice(aesthetic) + end[-3:],
        random.choice(words) + random.choice(aesthetic) + end,
        first[:5] + random.choice(words)[:3] + end[:3],
    ])

def check_batch(names):
    try:
        r = session.post("https://users.roblox.com/v1/usernames/users",
                         json={"usernames": names, "excludeBannedUsers": False}, timeout=10)
        if r.status_code != 200:
            return []
        out = []
        min_y, max_y = year_range
        data = r.json().get("data", [])
        for u in data:
            try:
                r2 = session.get(f"https://users.roblox.com/v1/users/{u['id']}", timeout=8)
                if r2.status_code != 200:
                    continue
                info = r2.json()
                created = info.get("created")
                if not created:
                    continue
                try:
                    year = datetime.fromisoformat(created.replace("Z", "+00:00")).year
                except:
                    year = int(created[:4])
                if min_y <= year <= max_y:
                    out.append({
                        "username": info.get("name") or info.get("displayName") or u.get("name"),
                        "id": u["id"],
                        "created": created[:10],
                        "year": year
                    })
            except:
                continue
        return out
    except Exception as e:
        return []

def scanner():
    global running, checked
    with ThreadPoolExecutor(max_workers=16) as ex:
        while running:
            try:
                batch_list = []
                for _ in range(6):
                    batch_list.append([make_name() for _ in range(20)])
                futs = [ex.submit(check_batch, b) for b in batch_list]
                checked += 120
                for f in as_completed(futs):
                    if not running:
                        break
                    try:
                        for res in f.result(timeout=15):
                            q.put(res)
                    except:
                        pass
                time.sleep(0.04)
            except:
                time.sleep(0.1)

def process_queue():
    count = 0
    while not q.empty() and count < 50:
        try:
            res = q.get_nowait()
        except queue.Empty:
            break
        uname = res["username"]
        if not uname or uname.lower() in found:
            continue
        found.add(uname.lower())
        listbox.insert(tk.END, f"{uname}  │  {res['id']}  │  {res['created']}  │  {res['year']}")
        count_var.set(f"FOUND: {len(found)}")
        count += 1
    if running:
        status_var.set(f"⚡ SCANNING [{mode.upper()}] | {year_range[0]}-{year_range[1]} | CHECKED: {checked:,}")
    else:
        status_var.set("READY")
    root.after(80, process_queue)

def start():
    global running, checked
    if running: 
        return
    running = True
    checked = 0
    start_btn.config(state="disabled", bg="#1a4d1a")
    stop_btn.config(state="normal", bg="#4d1a1a")
    status_var.set(f"⚡ INITIALIZING SCAN...")
    threading.Thread(target=scanner, daemon=True).start()

def stop():
    global running
    running = False
    start_btn.config(state="normal", bg="#1f1f1f")
    stop_btn.config(state="disabled", bg="#1f1f1f")
    status_var.set("■ STOPPED")

def set_mode(m):
    global mode
    mode = m
    mode_label.config(text=m.upper())
    status_var.set(f"MODE CHANGED → {m.upper()}")

def set_years(y1, y2):
    global year_range
    year_range = (y1, y2)
    year_label.config(text=f"{y1} - {y2}")
    status_var.set(f"YEAR FILTER → {y1} - {y2}")

def clear():
    found.clear()
    listbox.delete(0, tk.END)
    count_var.set("FOUND: 0")
    status_var.set("✓ CLEARED")

def copy_selected():
    sel = listbox.curselection()
    if not sel:
        status_var.set("⚠ SELECT A USERNAME")
        return
    try:
        username = listbox.get(sel[0]).split("  │  ")[0].strip()
        root.clipboard_clear()
        root.clipboard_append(username)
        root.update()
        status_var.set(f"✓ COPIED: {username}")
    except:
        status_var.set("⚠ COPY FAILED")

def on_select(e):
    copy_selected()

def copy_all():
    if not found:
        status_var.set("⚠ NOTHING TO COPY")
        return
    try:
        root.clipboard_clear()
        root.clipboard_append("\n".join(sorted(found)))
        root.update()
        status_var.set(f"✓ COPIED {len(found)} USERNAMES")
    except:
        status_var.set("⚠ COPY FAILED")

def open_selected():
    sel = listbox.curselection()
    if not sel: 
        status_var.set("⚠ SELECT A USER")
        return
    try:
        uid = listbox.get(sel[0]).split("  │  ")[1].strip()
        webbrowser.open(f"https://www.roblox.com/users/{uid}/profile")
        status_var.set("🌐 OPENING PROFILE")
    except:
        status_var.set("⚠ FAILED TO OPEN")

# Standard Windows-style light theme with a green-on-black console
BG = "#f0f0f0"
PANEL = "#e9e9e9"
FIELD = "#ffffff"
TEXT = "#111111"
SUBTEXT = "#555555"
BTN_BG = "#f5f5f5"
BTN_ACTIVE = "#e5e5e5"
CONSOLE_BG = "#050505"
CONSOLE_FG = "#00ff66"
CONSOLE_DIM = "#0a6b32"
CONSOLE_SEL = "#003b1a"
CONSOLE_SEL_FG = "#7dffb0"

current_profile = None
current_avatar_bytes = None
avatar_photo = None

root = tk.Tk()
root.title("NVJN PROPRIETARY PGER")
root.geometry("1040x700")
root.minsize(940, 660)
root.configure(bg=BG)
root.option_add("*Font", "Segoe UI 9")


def log(msg):
    log_text.config(state="normal")
    log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    total = int(log_text.index("end-1c").split(".")[0])
    if total > 400:
        log_text.delete("1.0", f"{total - 350}.0")
    log_text.see(tk.END)
    log_text.config(state="disabled")


def draw_noob():
    avatar_canvas.delete("all")
    avatar_canvas.create_rectangle(0, 0, 96, 96, fill="#d9d9d9", outline="")
    avatar_canvas.create_rectangle(8, 62, 88, 96, fill="#c0392b", outline="")
    avatar_canvas.create_rectangle(8, 62, 88, 70, fill="#922b21", outline="")
    avatar_canvas.create_oval(28, 12, 68, 58, fill="#f1c40f", outline="#b7950b", width=1)
    avatar_canvas.create_oval(37, 29, 45, 37, fill="black", outline="")
    avatar_canvas.create_oval(51, 29, 59, 37, fill="black", outline="")
    avatar_canvas.create_arc(36, 36, 60, 52, start=200, extent=140, style="arc", outline="black", width=2)


def set_avatar(img_bytes):
    global avatar_photo
    if not img_bytes:
        return
    try:
        photo = tk.PhotoImage(data=base64.b64encode(img_bytes).decode("ascii"))
        factor = max(1, (max(photo.width(), photo.height()) + 95) // 96)
        if factor > 1:
            photo = photo.subsample(factor, factor)
        avatar_canvas.delete("all")
        avatar_canvas.create_image(48, 48, image=photo)
        avatar_photo = photo
    except Exception:
        draw_noob()


def apply_profile(info, img_bytes):
    global current_profile, current_avatar_bytes
    current_profile = info
    current_avatar_bytes = img_bytes
    created = (info.get("created") or "")[:10]
    uid_var.set(str(info.get("id", "")))
    username_var.set(info.get("name", ""))
    display_var.set(info.get("displayName", ""))
    created_var.set(created)
    profile_hint_var.set(f"ID {info.get('id', '?')}")
    found_var.set(True)
    avatar_var.set(bool(img_bytes))
    loaded_var.set(True)
    selected_var.set(True)
    try:
        old_var.set(int(created[:4]) <= 2017)
    except Exception:
        old_var.set(False)
    set_avatar(img_bytes)
    status_var.set("PROFILE LOADED")
    log(f"Loaded {info.get('name', '?')} ({info.get('displayName', '')}) | ID {info.get('id', '?')} | Created {created or 'unknown'}")


def lookup_failed(err):
    loaded_var.set(False)
    selected_var.set(False)
    profile_hint_var.set("Not found")
    status_var.set("LOOKUP FAILED")
    log(f"ERROR: {err}")


def lookup_worker(identifier):
    try:
        if identifier.isdigit():
            r = session.get(f"https://users.roblox.com/v1/users/{identifier}", timeout=10)
            if r.status_code != 200:
                raise RuntimeError(f"User not found ({r.status_code})")
            info = r.json()
        else:
            r = session.post(
                "https://users.roblox.com/v1/usernames/users",
                json={"usernames": [identifier], "excludeBannedUsers": False},
                timeout=10,
            )
            if r.status_code != 200:
                raise RuntimeError(f"Lookup failed ({r.status_code})")
            data = r.json().get("data", [])
            if not data:
                raise RuntimeError("Username not found")
            uid = data[0]["id"]
            r2 = session.get(f"https://users.roblox.com/v1/users/{uid}", timeout=10)
            if r2.status_code != 200:
                raise RuntimeError(f"User details failed ({r2.status_code})")
            info = r2.json()

        uid = info.get("id")
        img_bytes = None
        if uid:
            tr = session.get(
                "https://thumbnails.roblox.com/v1/users/avatar-headshot",
                params={"userIds": uid, "size": "150x150", "format": "Png", "isCircular": "false"},
                timeout=10,
            )
            if tr.status_code == 200:
                thumbs = tr.json().get("data", [])
                if thumbs and thumbs[0].get("imageUrl"):
                    ir = session.get(thumbs[0]["imageUrl"], timeout=10)
                    if ir.status_code == 200:
                        img_bytes = ir.content

        root.after(0, lambda: apply_profile(info, img_bytes))
    except Exception as e:
        err = str(e)
        root.after(0, lambda err=err: lookup_failed(err))


def start_lookup(identifier):
    identifier = str(identifier).strip()
    if not identifier:
        log("Enter a username or User ID.")
        return
    status_var.set("LOOKING UP...")
    profile_hint_var.set("Loading...")
    loaded_var.set(False)
    selected_var.set(False)
    log(f"Preparing to load profile: {identifier}...")
    threading.Thread(target=lookup_worker, args=(identifier,), daemon=True).start()


def on_search():
    start_lookup(search_entry.get())


def parse_selected():
    sel = listbox.curselection()
    if not sel:
        return None
    parts = listbox.get(sel[0]).split("  │  ")
    if len(parts) < 2:
        return None
    return parts[0].strip(), parts[1].strip()


def on_select(event=None):
    parsed = parse_selected()
    if not parsed:
        return
    username, uid = parsed
    selected_var.set(True)
    log(f"Selected {username}...")
    start_lookup(uid)


def view_on_web():
    url = None
    if current_profile and current_profile.get("id"):
        url = f"https://www.roblox.com/users/{current_profile['id']}/profile"
    else:
        parsed = parse_selected()
        if parsed:
            url = f"https://www.roblox.com/users/{parsed[1]}/profile"
    if url:
        webbrowser.open(url)
        log(f"Opening {url}")
    else:
        log("No profile selected.")


def start():
    global running, checked
    if running:
        return
    running = True
    checked = 0
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    status_var.set("SCANNING...")
    log("Preparing To Generate User...")
    log(f"Mode: {mode.upper()} | Year range: {year_range[0]}-{year_range[1]}")
    threading.Thread(target=scanner, daemon=True).start()


def stop():
    global running
    running = False
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    status_var.set("STOPPED")
    log("Scanner stopped.")


def set_mode(m):
    global mode
    mode = m
    mode_label.config(text=m.upper())
    for key, btn in mode_buttons.items():
        btn.config(relief="sunken" if key == m else "raised", bg="#dcdcdc" if key == m else BTN_BG)
    status_var.set(f"MODE: {m.upper()}")
    log(f"Mode changed to {m.upper()}")


def set_years(y1, y2):
    global year_range
    year_range = (y1, y2)
    year_label.config(text=f"{y1} - {y2}")
    status_var.set(f"YEARS: {y1}-{y2}")
    log(f"Year filter set to {y1}-{y2}")


def clear():
    found.clear()
    listbox.delete(0, tk.END)
    count_var.set("FOUND: 0")
    status_var.set("CLEARED")
    log("Results cleared.")


def copy_selected():
    parsed = parse_selected()
    username = parsed[0] if parsed else (current_profile.get("name") if current_profile else None)
    if not username:
        log("Select a username first.")
        return
    root.clipboard_clear()
    root.clipboard_append(username)
    root.update()
    status_var.set(f"COPIED: {username}")
    log(f"Copied {username}")


def copy_all():
    names = []
    for i in range(listbox.size()):
        names.append(listbox.get(i).split("  │  ")[0].strip())
    if not names:
        log("Nothing to copy.")
        return
    root.clipboard_clear()
    root.clipboard_append("\n".join(names))
    root.update()
    status_var.set(f"COPIED {len(names)} USERNAMES")
    log(f"Copied {len(names)} usernames.")


def open_selected():
    parsed = parse_selected()
    if parsed:
        webbrowser.open(f"https://www.roblox.com/users/{parsed[1]}/profile")
        log(f"Opening profile for {parsed[0]}")
    else:
        view_on_web()


def process_queue():
    count = 0
    while not q.empty() and count < 50:
        try:
            res = q.get_nowait()
        except queue.Empty:
            break
        uname = res["username"]
        if not uname or uname.lower() in found:
            continue
        found.add(uname.lower())
        listbox.insert(tk.END, f"{uname}  │  {res['id']}  │  {res['created']}  │  {res['year']}")
        count_var.set(f"FOUND: {len(found)}")
        if len(found) <= 50 or len(found) % 10 == 0:
            log(f"FOUND {len(found)}: {uname} | {res['created']}")
        count += 1
    if running:
        status_var.set(f"SCANNING [{mode.upper()}] | {year_range[0]}-{year_range[1]} | CHECKED: {checked:,}")
    elif status_var.get().startswith("SCANNING"):
        status_var.set("READY")
    root.after(80, process_queue)


def make_button(parent, text, command, width=14):
    return tk.Button(
        parent, text=text, command=command, width=width,
        relief="raised", bd=1, bg=BTN_BG, activebackground=BTN_ACTIVE,
        fg=TEXT, font=("Segoe UI", 8), cursor="hand2",
    )


# Top search row
top = tk.Frame(root, bg=BG)
top.pack(fill="x", padx=8, pady=(8, 4))

tk.Label(top, text="User ID", bg=BG, fg=TEXT).pack(side="left")
search_entry = tk.Entry(top, bg=FIELD, fg=TEXT, relief="sunken", bd=1, insertbackground=TEXT)
search_entry.pack(side="left", fill="x", expand=True, padx=(6, 6), ipady=3)
search_entry.bind("<Return>", lambda event: on_search())
make_button(top, "Search", on_search, width=10).pack(side="left")

main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=8, pady=(0, 4))

left = tk.Frame(main, bg=BG, width=350)
left.pack(side="left", fill="y")
left.pack_propagate(False)

user_panel = tk.LabelFrame(
    left, text="User Panel", bg=BG, fg=TEXT, bd=1,
    relief="groove", font=("Segoe UI", 9, "bold"),
)
user_panel.pack(fill="x")

avatar_row = tk.Frame(user_panel, bg=BG)
avatar_row.pack(fill="x", padx=8, pady=6)

avatar_canvas = tk.Canvas(
    avatar_row, width=96, height=96, bg="#d9d9d9",
    highlightthickness=1, highlightbackground="#777777", bd=0,
)
avatar_canvas.pack(side="left")

avatar_right = tk.Frame(avatar_row, bg=BG)
avatar_right.pack(side="left", fill="both", expand=True, padx=(8, 0))
make_button(avatar_right, "View On Web", view_on_web, width=16).pack(anchor="w")
profile_hint_var = tk.StringVar(value="No user selected")
tk.Label(avatar_right, textvariable=profile_hint_var, bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(anchor="w", pady=(6, 0))

fields = tk.Frame(user_panel, bg=BG)
fields.pack(fill="x", padx=8)
fields.columnconfigure(1, weight=1)

uid_var = tk.StringVar()
username_var = tk.StringVar()
display_var = tk.StringVar()
created_var = tk.StringVar()
for row, (label, var) in enumerate([
    ("User ID", uid_var),
    ("Username", username_var),
    ("Display Name", display_var),
    ("Created", created_var),
]):
    tk.Label(fields, text=label, bg=BG, fg=TEXT, anchor="w").grid(row=row, column=0, sticky="w", pady=1)
    tk.Entry(
        fields, textvariable=var, state="readonly", readonlybackground=FIELD,
        fg=TEXT, relief="sunken", bd=1,
    ).grid(row=row, column=1, sticky="ew", padx=(6, 0), pady=1)

check_frame = tk.Frame(user_panel, bg=BG)
check_frame.pack(fill="x", padx=8, pady=(6, 4))

found_var = tk.BooleanVar()
old_var = tk.BooleanVar()
avatar_var = tk.BooleanVar()
loaded_var = tk.BooleanVar()
selected_var = tk.BooleanVar()
for i, (label, var) in enumerate([
    ("Found", found_var),
    ("Old Account", old_var),
    ("Has Avatar", avatar_var),
    ("Profile Loaded", loaded_var),
    ("Selected", selected_var),
]):
    tk.Checkbutton(
        check_frame, text=label, variable=var, bg=BG, activebackground=BG,
        anchor="w", state="disabled", disabledforeground=TEXT,
        selectcolor=FIELD, font=("Segoe UI", 8),
    ).grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 8), pady=0)

actions = tk.Frame(user_panel, bg=BG)
actions.pack(fill="x", padx=6, pady=(0, 8))

start_btn = make_button(actions, "Start", start)
stop_btn = make_button(actions, "Stop", stop)
stop_btn.config(state="disabled")
copy_btn = make_button(actions, "Copy Name", copy_selected)
open_btn = make_button(actions, "Open Profile", open_selected)
clear_btn = make_button(actions, "Clear List", clear)
copyall_btn = make_button(actions, "Copy All", copy_all)

for i, btn in enumerate([start_btn, stop_btn, copy_btn, open_btn, clear_btn, copyall_btn]):
    btn.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")
for c in range(2):
    actions.columnconfigure(c, weight=1)

generator = tk.LabelFrame(
    left, text="Generation", bg=BG, fg=TEXT, bd=1,
    relief="groove", font=("Segoe UI", 9, "bold"),
)
generator.pack(fill="x", pady=(8, 0))

mode_row = tk.Frame(generator, bg=BG)
mode_row.pack(fill="x", padx=6, pady=(4, 2))
tk.Label(mode_row, text="Mode", bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(side="left")
mode_label = tk.Label(mode_row, text="OG", bg=BG, fg=TEXT, font=("Segoe UI", 8, "bold"))
mode_label.pack(side="right")

mode_buttons = {}
mode_grid = tk.Frame(generator, bg=BG)
mode_grid.pack(fill="x", padx=4, pady=(0, 4))
for i, m in enumerate(["og", "lastnames", "swag", "killer", "short", "aesthetic"]):
    b = tk.Button(
        mode_grid, text=m.upper(), command=lambda m=m: set_mode(m), width=10,
        relief="raised", bd=1, bg=BTN_BG, activebackground=BTN_ACTIVE,
        font=("Segoe UI", 7), cursor="hand2",
    )
    b.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="ew")
    mode_buttons[m] = b
for c in range(3):
    mode_grid.columnconfigure(c, weight=1)

year_row = tk.Frame(generator, bg=BG)
year_row.pack(fill="x", padx=6, pady=(2, 2))
tk.Label(year_row, text="Year Range", bg=BG, fg=SUBTEXT, font=("Segoe UI", 8)).pack(side="left")
year_label = tk.Label(year_row, text="2015 - 2017", bg=BG, fg=TEXT, font=("Segoe UI", 8, "bold"))
year_label.pack(side="right")

year_grid = tk.Frame(generator, bg=BG)
year_grid.pack(fill="x", padx=4, pady=(0, 6))
for i, (label, y1, y2) in enumerate([
    ("2013-14", 2013, 2014),
    ("2015-17", 2015, 2017),
    ("2016-18", 2016, 2018),
    ("2014-16", 2014, 2016),
]):
    b = tk.Button(
        year_grid, text=label, command=lambda y1=y1, y2=y2: set_years(y1, y2), width=12,
        relief="raised", bd=1, bg=BTN_BG, activebackground=BTN_ACTIVE,
        font=("Segoe UI", 8), cursor="hand2",
    )
    b.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")
for c in range(2):
    year_grid.columnconfigure(c, weight=1)

right = tk.LabelFrame(
    main, text="Output", bg=BG, fg=TEXT, bd=1,
    relief="groove", font=("Segoe UI", 9, "bold"),
)
right.pack(side="left", fill="both", expand=True, padx=(8, 0))

console = tk.Frame(right, bg=CONSOLE_BG)
console.pack(fill="both", expand=True, padx=4, pady=4)
console.grid_rowconfigure(1, weight=3)
console.grid_rowconfigure(3, weight=1)
console.grid_columnconfigure(0, weight=1)

console_head = tk.Frame(console, bg=CONSOLE_BG)
console_head.grid(row=0, column=0, sticky="ew", padx=6, pady=(4, 2))
count_var = tk.StringVar(value="FOUND: 0")
tk.Label(
    console_head, text="NVJN // OUTPUT CONSOLE", bg=CONSOLE_BG,
    fg=CONSOLE_FG, font=("Consolas", 9, "bold"),
).pack(side="left")
tk.Label(
    console_head, textvariable=count_var, bg=CONSOLE_BG,
    fg=CONSOLE_FG, font=("Consolas", 9, "bold"),
).pack(side="right")

list_frame = tk.Frame(console, bg=CONSOLE_BG)
list_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=2)
list_frame.grid_rowconfigure(1, weight=1)
list_frame.grid_columnconfigure(0, weight=1)

tk.Label(
    list_frame, text="USERNAME                     ID          CREATED      YEAR",
    bg=CONSOLE_BG, fg=CONSOLE_DIM, font=("Consolas", 8, "bold"), anchor="w",
).grid(row=0, column=0, columnspan=2, sticky="ew")

list_scroll = tk.Scrollbar(
    list_frame, bg=CONSOLE_BG, troughcolor=CONSOLE_BG,
    activebackground=CONSOLE_FG, bd=0,
)
list_scroll.grid(row=1, column=1, sticky="ns")

listbox = tk.Listbox(
    list_frame, bg=CONSOLE_BG, fg=CONSOLE_FG, selectbackground=CONSOLE_SEL,
    selectforeground=CONSOLE_SEL_FG, font=("Consolas", 9), relief="flat",
    highlightthickness=0, yscrollcommand=list_scroll.set, activestyle="none",
    bd=0, selectmode=tk.SINGLE, exportselection=False,
)
listbox.grid(row=1, column=0, sticky="nsew")
list_scroll.config(command=listbox.yview)
listbox.bind("<<ListboxSelect>>", on_select)

tk.Label(
    console, text=" LOG", bg=CONSOLE_BG, fg=CONSOLE_DIM,
    font=("Consolas", 8, "bold"), anchor="w",
).grid(row=2, column=0, sticky="ew", padx=6)

log_frame = tk.Frame(console, bg=CONSOLE_BG)
log_frame.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 4))
log_frame.grid_rowconfigure(0, weight=1)
log_frame.grid_columnconfigure(0, weight=1)

log_scroll = tk.Scrollbar(
    log_frame, bg=CONSOLE_BG, troughcolor=CONSOLE_BG,
    activebackground=CONSOLE_FG, bd=0,
)
log_scroll.grid(row=0, column=1, sticky="ns")

log_text = tk.Text(
    log_frame, bg=CONSOLE_BG, fg=CONSOLE_FG, insertbackground=CONSOLE_FG,
    font=("Consolas", 8), relief="flat", highlightthickness=0, wrap="word",
    state="disabled", bd=0, yscrollcommand=log_scroll.set,
)
log_text.grid(row=0, column=0, sticky="nsew")
log_scroll.config(command=log_text.yview)

status_bar = tk.Frame(root, bg=PANEL, bd=1, relief="sunken")
status_bar.pack(fill="x", side="bottom")
status_var = tk.StringVar(value="READY")
tk.Label(
    status_bar, textvariable=status_var, bg=PANEL, fg=SUBTEXT,
    font=("Segoe UI", 8), anchor="w",
).pack(side="left", padx=8, pady=2)
tk.Label(
    status_bar, text="KIANITE CORE", bg=PANEL, fg=SUBTEXT, font=("Segoe UI", 8),
).pack(side="right", padx=8)

draw_noob()
log("NVJN PROPRIETARY PGER initialized.")
log("Preparing To Generate User...")
log("Select a generation mode and press START.")
root.after(80, process_queue)
root.mainloop()
