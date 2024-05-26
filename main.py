import time
from datetime import datetime, timedelta
import threading
import random
import os
try:
    import scratchattach as scratch3
except:
    os.system("pip install -U scratchattach")
    import scratchattach as scratch3

# LOG-IN
session = scratch3.login("BLOCKING_HACCKS_BOT", os.environ["BOT_PASSWORD"])

# Only one project works right now (will fix again very soon; don't worry)
projects_to_protect = ["108566337"]
# slither.io 1: "108566337"
# slither.io 2: "544213416"
# MMO Platformer: "612229554"
# Cloud fun 1: "12785898"
# Cloud fun 3: "823872487"
# Minecraft-ish: "843162693"

bad_users = ["-Plat-", "CoolBotABC123AWESOME", "shj_bot", "CorrectScratcher", "ns92", "betterconnection10", "superordi", "Vrai_nom", "SpartanDav", "WAYLIVES", "ahlashaool", ""]  # exact capitalization matters; I am 100% sure they hacked.

test_ban_for_fun = [""]
# a second ban list used to target specific hackers for specific reasons
# "*" means all but those in whitelisted users; dangerous/bad

whitelisted_users = ["BLOCKING_HACCKS_BOT", "ThatMobileGames", "TheMobileGames", "Human_NOT_bot"]  # prevents getting stuck in a loop setting cloud variables and lets the user bypass any anti-hack protections (WIP)

use_random_value = False
# override_value = ""
# override_value_for_fun = ""
# override_value = "-999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999"
override_value = "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
override_value_for_fun = "1412241413436443851643738533836533837645253484916333545483644424740644134363644526435485345128225104215930866100000313621610"
# this value means username: "HACKER_DETECTED_STOP/@BLOCKING_HACCKS_BOT", score: "100000", top-left corner, fully red snake skin color in griffpatch's slither.io


conns_to_disconnect = []
new_conns_to_use = []
for project in projects_to_protect:
    new_conns_to_use.append(session.connect_cloud(project))
    print("New conn to use:", project)


def create_new_conns():
    global conns_to_disconnect
    global new_conns_to_use
    while True:
        while len(conns_to_disconnect) > 0:
            conns_to_disconnect[0].disconnect()
            del conns_to_disconnect[0]
#            print("THREAD: disconnected 1")
        while "" in new_conns_to_use:
            index = new_conns_to_use.index("")
            new_conns_to_use[index] = session.connect_cloud(projects_to_protect[index])
            print("THREAD: Created new conn for project", projects_to_protect[index])


update_conns_thread = threading.Thread(target=create_new_conns)
update_conns_thread.daemon = True  # Thread to terminate when the program ends
update_conns_thread.start()


conns = []
for project in projects_to_protect:
    conns.append(session.connect_cloud(project))
    print("Main conn:", project)

events = []
for project in projects_to_protect:
    events.append(scratch3.CloudEvents(project))

print("SETUP - Conns:", conns)
print("SETUP - Events:", events)

attempted_event_count = [0 for _ in range(len(projects_to_protect))]
successes = [0 for _ in range(len(projects_to_protect))]
total_event_count = [0 for _ in range(len(projects_to_protect))]
total_success_count = [0 for _ in range(len(projects_to_protect))]
time_at_last_event = [0 for _ in range(len(projects_to_protect))]
time_at_last_success = [0 for _ in range(len(projects_to_protect))]
print(attempted_event_count, successes, total_event_count, total_success_count, time_at_last_event, time_at_last_success)
recent_veified_users_dict = {}

for i in events:
    @i.event  # Called when the event listener is ready
    def on_ready():
        print("Event listener ready:", i)
        print("Hacker detection is ready for", projects_to_protect[events.index(i)])


def get_PDT_time():
    return (datetime.utcnow() + timedelta(hours=-7)).strftime('%Y-%m-%d %H:%M:%S PDT')


for i in events:
    @i.event
    def on_set(event):  # Called when a cloud var is set
        global attempted_event_count
        global successes
        global total_event_count
        global total_success_count
        global time_at_last_event
        global time_at_last_success
        global new_conns_to_use
        global conns_to_disconnect
        global override_value
        global override_value_for_fun
        index = events.index(i)
        user = scratch3.get_user(event.user)
        if use_random_value == True:
            override_value = random.randint(10**(256-1), 10**256 - 1)
            override_value_for_fun = override_value
        if (event.user not in whitelisted_users) and ((event.user not in recent_veified_users_dict) or (int(time.time()) > recent_veified_users_dict[event.user] + 120)):
            if event.user in bad_users:
                conns[index].set_var(event.var, override_value)
                attempted_event_count[index] += 1
                time_at_last_event[index] = time.monotonic()
                print("Bad User detected:", event.user, "at", get_PDT_time())
            elif user.does_exist() == False:
                conns[index].set_var(event.var, override_value)
                attempted_event_count[index] += 1
                time_at_last_event[index] = time.monotonic()
                print("Banned User detected:", event.user, "at", get_PDT_time())
            elif user.is_new_scratcher():
                conns[index].set_var(event.var, override_value)
                attempted_event_count[index] += 1
                time_at_last_event[index] = time.monotonic()
                print("New Scratcher detected:", event.user, "at", get_PDT_time())
            else:
                recent_veified_users_dict.update({event.user: int(time.time())}) #prevents constantly making requests to Scratch to check users
            if (event.user in test_ban_for_fun) or ("*" in test_ban_for_fun):
                conns[index].set_var(event.var, override_value_for_fun)
                attempted_event_count[index] += 1
                time_at_last_event[index] = time.monotonic()
                print("Test ban for fun user detected:", event.user, "at", get_PDT_time())

        if (event.value == override_value) or (event.value == override_value_for_fun):
            successes[index] += 1
            time_at_last_success[index] = time.monotonic()
            print("Successes:", successes, "Events:", attempted_event_count)
        if ((time_at_last_event[index]) > (time_at_last_success[index] + 10)) and (new_conns_to_use[index] != ""):
            if len(conns) == len(new_conns_to_use):
                time_at_last_success[index] = 0
                time_at_last_event[index] = 0
                temporary_conn = conns[index]
                conns[index] = new_conns_to_use[index]
                new_conns_to_use[index] = ""
                conns_to_disconnect.append(temporary_conn)
                total_event_count[index] += attempted_event_count[index]
                attempted_event_count[index] = 0
                total_success_count[index] += successes[index]
                successes[index] = 0
                print("Used new conn")
                print("Total event count:", total_event_count, "Total success count:", total_success_count)
                print("Conns after change:", conns, "index", index)
            else:
                print("Why aren't the lists the same length. My code should work. >:(")

for i in events:
    i.start()
