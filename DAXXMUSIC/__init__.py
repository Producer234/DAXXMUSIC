from DAXXMUSIC.core.bot import DAXX
from DAXXMUSIC.core.dir import dirr
from DAXXMUSIC.core.git import git
from DAXXMUSIC.core.userbot import Userbot
from DAXXMUSIC.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

# Update directories
dirr()

# Only run git updater if .git exists (VPS/Local only)
import os
if os.path.exists(".git"):
    try:
        git()
    except Exception as e:
        LOGGER(__name__).warning(f"Git updater skipped: {e}")
else:
    LOGGER(__name__).info("Skipping git updater on Heroku (no .git folder).")

# Initialize databases / Heroku config
dbb()
heroku()

# Initialize clients
app = DAXX()
api = SafoneAPI()
userbot = Userbot()

# Platforms
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()