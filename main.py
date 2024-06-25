import os
from protectors import SlitherProtector
import protectors
import scratchattach as scratch3
from time import sleep

# login
session = scratch3.login("BLOCKING_HACCKS_BOT", os.environ["BOT_PASSWORD"])
# session = scratch3.login(os.environ["BOT_USERNAME"], os.environ["BOT_PASSWORD"])

# listen only
# session = None


# exact capitalization doesn't matter; I am 100% sure they hacked.
banned_users = [
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
]

# a second ban list for testing
test_banned = [
    # "KentUckyFriEdPlaYer",
]


# prevents getting stuck in a loop setting cloud variables and lets the user bypass any anti-hack protections
whitelisted_users = [
    "BLOCKING_HACCKS_BOT",
    "ThatMobileGames",
    "TheMobileGames",
    "Human_NOT_bot",
    "CloudAntiCheat",
]

# no need to prefix with a space it is done automatically
overide_name = "HACKER DETECTED / @BLOCKING_HACCKS_BOT"

# puting options into dict so it is only needed once
options = {
    "session": session,
    "whitelist": whitelisted_users,
    "banned": banned_users,
    "test_banned": test_banned,
}

sliter_options = options | {
    "overide_name": overide_name,
}

# projects to protect
protect = [
    SlitherProtector("108566337", **sliter_options),
    SlitherProtector("544213416", **sliter_options),
    SlitherProtector("702543294", **sliter_options),
    # SlitherProtector("1041333138", **sliter_options),
]
# slither.io 1: "108566337"
# slither.io 2: "544213416"
# slither.io 3: "702543294"
# MMO Platformer: "612229554"
# Cloud fun 1: "12785898"
# Cloud fun 3: "823872487"
# Minecraft-ish: "843162693"

protectors.load_prev_flagged()

for protector in protect:
  protector.start()

# you can use any other method to wait too
while True:
    try:
        sleep(30)
    except KeyboardInterrupt:
        protectors.save_prev_flagged()
        break
    protectors.save_prev_flagged()

for protector in protect:
  protector.stop()