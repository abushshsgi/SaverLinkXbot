import os

# Telegram Bot Token from environment variable
BOT_TOKEN = "8100639428:AAH9OGoY4r7OqSIpUh-ksod-EV-_uQ2YLL4"  # O'z bot tokeningizni shu yerga qo'ying

# Database configuration
# NeonTech database connection
SQLALCHEMY_DATABASE_URI = "sqlite:///mediasaver.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Xavfsizlik kaliti
SECRET_KEY = "your-secret-key-here"

# Debug rejimi
DEBUG = True

# Donation Details
# Make sure the URL has the correct HTTP/HTTPS prefix
donation_url_env = os.getenv("DONATION_URL", "https://example.com/donate")
# Validate donation URL
if donation_url_env and not (donation_url_env.startswith('http://') or donation_url_env.startswith('https://')):
    # Add https:// prefix if missing
    DONATION_URL = "https://" + donation_url_env
else:
    DONATION_URL = donation_url_env

DONATION_TEXT = """
Thank you for considering a donation! 🙏
Here's how you can support us:
💳 {donation_url}
"""

# Bot Messages
WELCOME_MESSAGE = """
👋 Hi there! I'm your media saver bot.
Just send me a YouTube or Instagram link, and I'll help you download the video!
"""

DOWNLOAD_SUCCESS_MESSAGE = """
✅ Your video is ready! Tap the button below to download.
🙏 Like the bot? Consider supporting us with a small donation!
"""

INVALID_URL_MESSAGE = """
⚠️ Oops! That doesn't look like a valid Instagram or YouTube link. 
Please try again with a correct URL.
"""

PROCESSING_MESSAGE = "🔄 Processing your link... Just a moment!"

ERROR_MESSAGE = """
😔 Sorry, I ran into an error while trying to download your video. 

This could be due to:
- The content might be a photo, not a video
- The account might be private
- The video might be too large (over 50MB)
- There might be temporary issues with the platform

Please try again with a different link.
"""

# File size limit for Telegram (50MB in bytes)
MAX_FILE_SIZE = 50 * 1024 * 1024
