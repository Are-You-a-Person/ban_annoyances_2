#!/usr/bin/env python3
from datetime import datetime
import random
import os
import encoding # snake encoding/decoding
import scratchattach as scratch3

# listen only (useful for debugging)
no_kick = False

# LOG-IN
if not no_kick:
    session = scratch3.login("CloudAntiCheat", os.environ["BOT_PASSWORD"])


# exact capitalization matters; I am 100% sure they hacked.
banned_users = {
    "-Plat-",
    "CoolBotABC123AWESOME",
    "shj_bot",
    "CorrectScratcher",
    "ns92",
    "betterconnection10",
    "superordi",
    "Vrai_nom",
    "SpartanDav",
    "WAYLIVES",
    "ahlashaool",
}

# a second ban list for testing
test_banned = {
    # "KentuckyFriedPlayer",
}

# data shared between projects such as scratcher status so that it is only fetched once
global_player_data = {}

# all but those in whitelisted users; dangerous/bad
ban_all = False


# prevents getting stuck in a loop setting cloud variables and lets the user bypass any anti-hack protections
whitelisted_users = {
    "CloudAntiCheat",
    "BLOCKING_HACCKS_BOT",
    "ThatMobileGames",
    "TheMobileGames",
    "Human_NOT_bot",
}

if not no_kick:
    whitelisted_users.add(session._username)



# override_value = "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
# override_value_for_fun = "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
# this value means username: "HACKER_DETECTED_STOP/@BLOCKING_HACCKS_BOT", score: "100000", top-left corner, fully red snake skin color in griffpatch's slither.io



class ProjectProtector:
    project = "Generic"
    def __init__(self, project_id):
        # setup vars
        self.project_id = project_id
        if not no_kick:
            self.conn = session.connect_cloud(project_id)
        self.events = events = scratch3.CloudEvents(project_id)
        events.event(self.on_ready)
        events.event(self.on_set)
        self.player_data = {}
    def start(self):
        self.events.start()
    def stop(self):
        self.events.stop()
    def get_override_value(self):
        return random.randrange(10**255, 10**256)
    def on_ready(self):
        print(f"Connected to {self.project_id}")
        
    def on_set(self, event):
        if event.user in whitelisted_users:
            return
        # get userinfo or create it if it doesn't exist
        try:
            userinfo = self.player_data[event.user]
        except KeyError:
            self.player_data[event.user] = userinfo = {}
            if event.user not in global_player_data:
                global_player_data[event.user] = {"new": True}
            userinfo["global"] = global_player_data[event.user]
            userinfo["new"] = True
            
        # skip if kicked in last 2 seconds
        if userinfo.get("lastkicked", 0) + 2000 > event.timestamp:
            return
        
        reason = self.check_hacks(event)
        userinfo["new"] = False
        userinfo["global"]["new"] = False
        if reason is not None:
            # logs kick reason and kicks hackers
            userinfo["lastkicked"] = event.timestamp
            print(f"{self.project} {self.project_id}: Kicking {event.user} for reason {reason!r} at {timestamp()}")
            self.disconnect_var(event.var)
            
    def disconnect_var(self, varname):
        override_value = self.get_override_value()
        print(f"Overriding {varname}")        
        if not no_kick:
            self.conn.set_var(varname, override_value)
            
    def check_hacks(self, event):
        global_userinfo = self.player_data[event.user]["global"]
        user = scratch3.User(username=event.user)
        # check ban lists
        if user.username in banned_users:
            return "on ban list"
        if user.username in test_banned:
            return "test banned"
        if ban_all:
            return "ban all"
        
        # only need to collect new scratcher status once
        if global_userinfo["new"]:
            global_userinfo["exists"] = exists = user.does_exist()
            global_userinfo["last_checked_exists"] = event.timestamp
            if exists:
                global_userinfo["new_scratcher"] = user.is_new_scratcher()
        
        # checks banned status once a minute
        if global_userinfo["last_checked_exists"] + 60 * 1000 < event.timestamp:
            global_userinfo["exists"] = exists = user.does_exist()
            global_userinfo["last_checked_exists"] = event.timestamp
        
        if not global_userinfo["exists"]:
            return "banned by scratch"
        if global_userinfo["new_scratcher"]:
            return "new scratcher"
        return None
        
class SlitherProtector(ProjectProtector):
    project = "Slither"
    def get_override_value(self):
        # return "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
        # change bot name here
        return encoding.encode_snake(" Hacker Detected!/@BLOCKING_HACCKS_BOT", length=100000, is_master=2)
    def check_hacks(self, event):
        # runs normal checks first
        reason = super().check_hacks(event)
        if reason is not None:
            return reason
        # attempts to decode, logs errors if it fails
        try:
            snake = encoding.decode_snake(event.value)
        except encoding.DecodingError as e:
            print(f"Error while decoding {event.value!r} set by {event.user}: {e}")
        else:
            if snake["name"].lower() != event.user.lower():
                return f"mismatched name ({snake['name']})"
            if "power" in snake and snake["power"] > 2.125:
                return "speed hacks"
        return None


def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# projects to protect
protect = [
    SlitherProtector("108566337"),
    SlitherProtector("544213416"),
    
    # untested and no in game username check (only basic scratcher checks)
    # ProjectProtector("12785898")
    # ProjectProtector("823872487")
]
# slither.io 1: "108566337"
# slither.io 2: "544213416"
# MMO Platformer: "612229554"
# Cloud fun 1: "12785898"
# Cloud fun 3: "823872487"
# Minecraft-ish: "843162693"

for protector in protect:
  protector.start()

# you can use any other method to wait too
input("Press enter to quit\n")

for protector in protect:
  protector.stop()