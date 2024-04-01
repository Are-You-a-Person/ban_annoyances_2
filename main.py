import time
import datetime
import threading
import os
try:
    import scratchattach as scratch3
except:
    os.system("pip install -U scratchattach")
    import scratchattach as scratch3

session = scratch3.login("BLOCKING_HACCKS_BOT", os.environ["PASSWORD"])
projects_to_protect = ["108566337"]  # only one project works right now

conns_to_disconnect = []
new_conns_to_use = []
for project in projects_to_protect:
    new_conns_to_use.append(session.connect_cloud(project))
    print("new conn to use:", project)


def create_new_conns():
    global conns_to_disconnect
    global new_conns_to_use
    while True:
        while len(conns_to_disconnect) > 0:
            conns_to_disconnect[0].disconnect()
            del conns_to_disconnect[0]
            #print("THREAD: disconnected 1")
        while "" in new_conns_to_use:
            index = new_conns_to_use.index("")
            new_conns_to_use[index] = session.connect_cloud(projects_to_protect[index])
            print("THREAD: Created new conn for project", projects_to_protect[index])


update_conns_thread = threading.Thread(target=create_new_conns)
update_conns_thread.daemon = True  # Thread to terminate when the program ends
update_conns_thread.start()


bad_users = ["CorrectScratcher", "ahlashaool", "ns92", "betterconnection10", "superordi", "Vrai_nom",]  # exact capitalization matters

test_ban_for_fun = ["", ""]  # does not change the hacker's username to "("
whitelisted_users = ["ThatMobileGames", "TheMobileGames", "Human_NOT_bot", ""]  # prevents getting stuck in a loop setting cloud variables and lets the user bypass any anti-hack protections (WIP)

override_value = "-999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999"
#override_value_for_fun = ""
override_value_for_fun = "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"

conns = []
for project in projects_to_protect:
    conns.append(session.connect_cloud(project))
    print("main conn:", project)

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

for i in events:
    @i.event  # Called when the event listener is ready
    def on_ready():
        print("Event listener ready:", i)
        print("Hacker detection is ready for", projects_to_protect[events.index(i)])

for i in events:
    print("why is this working before but not after", events.index(i))
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
        index = events.index(i)
        #print("new", projects_to_protect[events.index(i)])
        iso_date = session.connect_user(event.user).join_date
        if (time.time() - (datetime.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())) < 1209600:  # if the user was made less than 2 weeks ago, their cloud vars will be overidden
            conns[index].set_var(event.var, override_value)
            attempted_event_count[index] += 1
            time_at_last_event[index] = time.monotonic()
            print("New Scratcher detected:", event.user)
        elif (event.user in bad_users) and (event.user not in whitelisted_users):
            conns[index].set_var(event.var, override_value)
            attempted_event_count[index] += 1
            time_at_last_event[index] = time.monotonic()
            print("Bad user detected:", event.user)
        elif (event.user in test_ban_for_fun) and (event.user not in whitelisted_users):
            conns[index].set_var(event.var, override_value_for_fun)
            attempted_event_count[index] += 1
            time_at_last_event[index] = time.monotonic()
            print("Test ban for fun user detected in", projects_to_protect[index], ":", event.user)

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
