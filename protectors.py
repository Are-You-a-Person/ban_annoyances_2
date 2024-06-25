#!/usr/bin/env python3
from datetime import datetime
import random
import encoding # snake encoding/decoding
import scratchattach as scratch3

# data shared between projects such as scratcher status so that it is only fetched once
global_player_data = {}

prev_flagged_users = {}
new_flags = []


def load_prev_flagged(filename = "prev_flagged.txt"):
    try:
        with open(filename) as file:
            for line in file:
                name, reason = line.split(": ", 1)
                name = name.lower()
                prev_flagged_users[name] = reason
    except FileNotFoundError:
        pass
            
def save_prev_flagged(filename = "prev_flagged.txt"):
    global new_flags
    if len(new_flags) > 0:
        flags = new_flags
        new_flags = []
        with open(filename, "a") as file:
            for line in flags:
                file.write(line + "\n")
            
            

class Flag(BaseException):
    reason = None
    comment = False
    save = False
    def __init__(self, protector, event):
        if self.reason is None:
            raise Exception(f"Flag '{self.__class__.__name__}' has no reason")
        self.event = event
        self.protector = protector
        self.timestamp = timestamp()
    @property
    def userinfo(self):
        return self.protector.player_data[self.event.user.lower()]
    def run_actions(self):
        if self.save and self.event.user.lower() not in prev_flagged_users:
            reason = f"{self.get_info()} at {self.timestamp}"
            prev_flagged_users[self.event.user.lower()] = reason
            new_flags.append(f"{self.event.user}: {reason}")
        if self.comment:
            # todo: add comenting
            msg = self.comment_msg()
            print(f"Comment {msg!r} on {self.event.user}'s profile")
        
    def get_info(self):
        return self.reason
    
    def __str__(self):
        return f"{self.event.user!r} was flagged for reason {self.get_info()!r} at {self.timestamp}"

class PrevFlag(Flag):
    reason = "previously flagged"
    def get_info(self):
        return f"previously flagged ({prev_flagged_users[self.event.user.lower()]})"
    def __str__(self):
        return f"{self.event.user!r} was previosly flagged for reason {prev_flagged_users[self.event.user.lower()]} (new flag at {self.timestamp})"

class BannedFlag(Flag):
    reason = "banned by scratch"
    save = True

class NewScratcherFlag(Flag):
    reason = "new scratcher"
    save = True
    comment = True
    def comment_msg(self):
        return (
            f"Hello {self.event.user}, you have been banned from griffpatch's "
            "slither.io because you played as a new scratcher."
            "You can appeal on @TheMobileGames’s profile."
        )

class BanListFlag(Flag):
    reason = "on ban list"
    
class TestBanFlag(Flag):
    reason = "test banned"
    
class SlitherFlag(Flag):
    comment = True
    save = True
    comment_reason = " because you were hacking"
    def __init__(self, protector, event, snake):
        super().__init__(protector, event)
        self.snake = snake
    def comment_msg(self):
        return (
            f"Hello {self.event.user}, you have been banned from griffpatch's "
            "slither.io because you were hacking."
            "You can appeal on @TheMobileGames’s profile."
        )
        
class SpeedFlag(SlitherFlag):
    reason = "speed hacks"
    def get_info(self):
        return f"speed hacks ({self.snake['power']} > 2.125)"
    
class FakeNameFlag(SlitherFlag):
    reason = "fake name"
    def get_info(self):
        return f"fake name ({self.snake['name']})"


def _lowercase_set(iterator):
    return {string.lower() for string in iterator}

class ProjectProtector:
    project = "Generic"
    def __init__(
            self,
            project_id,
            session=None,
            *,
            whitelist = (),
            banned = (),
            test_banned = (),
        ):
        # setup vars
        self.whitelist = _lowercase_set(whitelist)
        self.banned = _lowercase_set(banned)
        self.test_banned = _lowercase_set(test_banned)
        self.project_id = project_id
        self.session = session
        if session is None:
            self.conn = None
        else:
            self.conn = session.connect_cloud(project_id)
            # whitelist self
            self.whitelist.add(session._username.lower())
        self.events = events = scratch3.CloudEvents(project_id)
        events.event(self.on_ready)
        events.event(self.on_set)
        self.player_data = {}
        
    def print(self, *args, **kwargs):
        print(f"{self.project} {self.project_id}:", *args, **kwargs)
    def start(self):
        self.events.start()
    def stop(self):
        self.events.stop()
    def get_override_value(self, flag):
        return random.randrange(10**255, 10**256)
    def on_ready(self):
        self.print("listening" if self.conn is None else "connected")
        
    def on_set(self, event):
        lower_name = event.user.lower()
        if lower_name in self.whitelist:
            return
        # get userinfo or create it if it doesn't exist
        try:
            userinfo = self.player_data[lower_name]
        except KeyError:
            self.player_data[lower_name] = userinfo = {}
            if lower_name not in global_player_data:
                global_player_data[lower_name] = {"new": True}
            userinfo["global"] = global_player_data[lower_name]
            userinfo["new"] = True
            
        # skip if kicked in last 2 seconds
        if userinfo.get("lastkicked", 0) + userinfo.get("kick_after", 2000) > event.timestamp:
            return
        
        try:
            self.check_hacks(event)
        except Flag as flag:
            # logs kick reason and kicks hacker
            if flag.userinfo.get("no_log_until", 0) < event.timestamp:
                self.print(flag)
            flag.run_actions()
            if self.conn is None:
                self.print("No action taken, session is None")
            else:
                self.disconnect_var(event.var, flag)
            userinfo["lastkicked"] = event.timestamp
        
        userinfo["new"] = False
        userinfo["global"]["new"] = False
            
    def disconnect_var(self, varname, flag):
        override_value = self.get_override_value(flag)
        self.conn.set_var(varname, override_value)
            
    def check_hacks(self, event):
        lower_name = event.user.lower()
        
        if lower_name in prev_flagged_users:
            raise PrevFlag(self, event)
        
        # check ban lists (usernames stored as lowercase)
        if lower_name in self.banned:
            raise BanListFlag(self, event)
        if lower_name in self.test_banned:
            raise TestBanFlag(self, event)
        
        # creates user object without fetching any data
        user = scratch3.User(username=event.user)
        global_userinfo = self.player_data[lower_name]["global"]
        
        # only need to collect new scratcher status once
        if global_userinfo["new"]:
            global_userinfo["exists"] = exists = user.does_exist()
            global_userinfo["last_checked_exists"] = event.timestamp
            if exists:
                global_userinfo["new_scratcher"] = user.is_new_scratcher()
        
        # checks banned status once a minute
        if global_userinfo["last_checked_exists"] + 5 * 60 * 1000 < event.timestamp:
            global_userinfo["exists"] = user.does_exist()
            global_userinfo["last_checked_exists"] = event.timestamp
        
        # could be none if an error occured
        if global_userinfo["exists"] == False:
            raise BannedFlag(self, event)
        if global_userinfo["new_scratcher"]:
            raise NewScratcherFlag(self, event)
        return None
        
class SlitherProtector(ProjectProtector):
    project = "Slither"
    def __init__(
            self,
            project_id,
            session = None,
            *,
            overide_name = "HACKER DETECTED",
            **kwargs
        ):
        super().__init__(project_id, session, **kwargs)
        self.overide_name = overide_name
    def get_override_value(self, flag):
        # return "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
        # change bot size here
        userinfo = flag.userinfo
        flag.userinfo["no_log_until"] = flag.event.timestamp + 3000
        if userinfo.get("lastkicked", 0) + 3000 > flag.event.timestamp:
            flag.userinfo["kick_num"] += 1
            if (flag.userinfo["kick_num"] == 3):
                self.print(f"Anti kick detected, {flag.event.user} is being repeatedly disconected")
            elif (flag.userinfo["kick_num"] > 3 and flag.userinfo["kick_num"] % 100 == 0):
                    self.print(f"Anti kick detected, {flag.event.user} kicked {flag.userinfo['kick_num']} times")
            userinfo["kick_after"] = 1000
            return encoding.encode_snake(" ", length=0)
        else:
            flag.userinfo["kick_num"] = 0
            flag.userinfo["kick_after"] = 2000
            return encoding.encode_snake(" " + self.overide_name, length=999999)
    def check_hacks(self, event):
        # runs normal checks first
        super().check_hacks(event)
        
        # attempts to decode, logs errors if it fails
        try:
            snake = encoding.decode_snake(event.value)
        except encoding.DecodingError as e:
            self.print(f"Error while decoding {event.value!r} set by {event.user}: {e}")
        else:
            if snake["name"].lower() != event.user.lower():
                if snake["name"] == "":
                    self.print(f"{event.user} using empty name, skipping for now")
                else:
                    raise FakeNameFlag(self, event, snake)
            if "power" in snake and snake["power"] > 2.125:
                raise SpeedFlag(self, event, snake)


def timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')