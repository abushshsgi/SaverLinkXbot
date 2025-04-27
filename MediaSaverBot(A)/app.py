import os
import logging
import threading
from flask import Flask, render_template_string, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import BOT_TOKEN, SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import init_db, User, Download, db
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import func
import telebot
import tempfile
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from url_validator import get_url_type
from downloaders import (
    download_youtube_video, 
    download_instagram_video, 
    download_twitter_video,
    download_facebook_video,
    DownloadError
)
from keyboards import get_donation_keyboard
from service import get_or_create_user, record_download, record_donation_click, get_user_stats
import gc
import re
import yt_dlp
import sys
from config import (
    WELCOME_MESSAGE, DOWNLOAD_SUCCESS_MESSAGE, 
    INVALID_URL_MESSAGE, PROCESSING_MESSAGE, ERROR_MESSAGE,
    DONATION_TEXT, DONATION_URL
)

logger = logging.getLogger(__name__)
app = Flask(__name__)

# Flask config
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
init_db(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin credentials (simple example)
ADMIN_USERNAME = "abdu"
ADMIN_PASSWORD = hashlib.sha256("ab".encode()).hexdigest()

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == "admin":
        return AdminUser(user_id)
    return None

@app.route('/')
def home():
    # Get bot info (simple fallback)
    bot_username = "your_bot_username"
    bot_name = "Media Downloader Bot"
    try:
        from telegram import Bot
        import asyncio
        async def get_bot_info():
            if not BOT_TOKEN:
                return {"username": "your_bot_username", "name": "Media Downloader Bot"}
            bot = Bot(token=BOT_TOKEN)
            bot_info = await bot.get_me()
            return {"username": bot_info.username, "name": bot_info.first_name}
        bot_info = asyncio.run(get_bot_info())
        bot_username = bot_info["username"]
        bot_name = bot_info["name"]
    except Exception as e:
        logger.error(f"Failed to get bot info: {str(e)}")
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ bot_name }} - Telegram Video Downloader</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>body {padding-top: 2rem;} .bot-icon {max-width: 150px;margin-bottom: 2rem;} .features-list {text-align: left;max-width: 600px;margin: 0 auto;}</style>
    </head>
    <body>
        <div class="container" data-bs-theme="dark">
            <div class="text-center mb-5">
                <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" alt="Bot Icon" class="bot-icon">
                <h1 class="display-4">{{ bot_name }}</h1>
                <p class="lead">A Telegram bot for downloading videos from Instagram and YouTube</p>
                <a href="https://t.me/{{ bot_username }}" class="btn btn-primary mt-3" target="_blank">Open in Telegram</a>
                <div class="mt-3">
                    <a href="/login" class="btn btn-outline-light me-2">Admin Login</a>
                    <a href="/dashboard" class="btn btn-outline-info me-2">Dashboard</a>
                </div>
            </div>
            
            <div class="row justify-content-center mb-5">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>Features</h3>
                        </div>
                        <div class="card-body features-list">
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">✅ Download videos from YouTube</li>
                                <li class="list-group-item">✅ Download videos from Instagram</li>
                                <li class="list-group-item">✅ Simple, user-friendly interface</li>
                                <li class="list-group-item">✅ Fast and reliable performance</li>
                                <li class="list-group-item">✅ Completely free to use</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row justify-content-center mb-5">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>How to Use</h3>
                        </div>
                        <div class="card-body">
                            <ol class="text-start">
                                <li class="mb-3">Search for <strong>@{{ bot_username }}</strong> on Telegram or click the button above</li>
                                <li class="mb-3">Start a chat with the bot by clicking on <strong>Start</strong></li>
                                <li class="mb-3">Copy a YouTube or Instagram video URL</li>
                                <li class="mb-3">Send the URL to the bot</li>
                                <li class="mb-3">Wait for the bot to process and download the video</li>
                                <li>Enjoy your downloaded video!</li>
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer class="text-center mt-5 mb-5">
            
                <p>© 2025 Media Downloader Bot. All rights reserved.</p>
                <p>
                    <a href="#" class="text-decoration-none me-3">Privacy Policy</a>
                    <a href="#" class="text-decoration-none me-3">Terms of Service</a>
                    <a href="#" class="text-decoration-none">Support</a>
                </p>
            </footer>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, bot_username=bot_username, bot_name=bot_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = AdminUser("admin")
            login_user(user)
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Noto'g'ri login yoki parol")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Statistika uchun misol (soddalashtirilgan)
    today = datetime.now().date()
    today_stats = db.session.query(
        func.count(User.id).label('new_users'),
        func.count(Download.id).label('downloads')
    ).select_from(User).outerjoin(Download).filter(
        func.date(User.created_at) == today
    ).first()
    total_users = User.query.count()
    total_downloads = Download.query.count()
    successful_downloads = Download.query.filter_by(status='success').count()
    stats = {
        'today_new_users': today_stats[0] or 0,
        'today_downloads': today_stats[1] or 0,
        'total_users': total_users,
        'total_downloads': total_downloads,
        'successful_downloads': successful_downloads
    }
    return render_template('dashboard.html', stats=stats, platform_data={})

# --- BOTNI ALOHIDA THREADDA ISHGA TUSHIRISH ---
bot = telebot.TeleBot(BOT_TOKEN)
active_downloads = {}

def detect_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'facebook.com' in url or 'fb.com' in url:
        return 'facebook'
    elif 'twitter.com' in url or 'x.com' in url:
        return 'twitter'
    return 'unknown'

def is_valid_url(url):
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return bool(url_pattern.match(url))

def run_bot():
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        with app.app_context():
            user_id = str(message.from_user.id)
            username = message.from_user.username
            first_name = message.from_user.first_name
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
                logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id}")
            bot.reply_to(message, WELCOME_MESSAGE)

    @bot.message_handler(func=lambda message: True)
    def handle_message(message):
        with app.app_context():
            url = message.text.strip()
            if not is_valid_url(url):
                bot.reply_to(message, INVALID_URL_MESSAGE)
                return
            platform = detect_platform(url)
            if platform == 'tiktok':
                bot.reply_to(message, "Bu linkni yuklab bo'lmaydi. TikTok qo'llab-quvvatlanmaydi.")
                return
            user = User.query.filter_by(user_id=str(message.from_user.id)).first()
            if user:
                download = Download(
                    user_id=user.id,
                    platform=platform,
                    url=url,
                    created_at=datetime.utcnow(),
                    status='processing'
                )
                db.session.add(download)
                db.session.commit()
                logger.info(f"Yangi yuklash qo'shildi: {url} from {platform}")
                if platform == 'unknown':
                    bot.reply_to(message, "Kechirasiz, bu saytdan yuklay olmayman. Quyidagi saytlardan foydalaning:\n- YouTube\n- Instagram\n- TikTok\n- Facebook\n- Twitter")
                    download.status = 'failed'
                    db.session.commit()
                    return
                status_message = bot.reply_to(message, PROCESSING_MESSAGE)
                try:
                    if platform == 'youtube':
                        video_path = download_youtube_video(url)
                    elif platform == 'instagram':
                        video_path = download_instagram_video(url)
                    elif platform == 'twitter':
                        video_path = download_twitter_video(url)
                    elif platform == 'facebook':
                        video_path = download_facebook_video(url)
                    else:
                        raise Exception("Platforma qo'llab-quvvatlanmaydi.")
                    with open(video_path, 'rb') as video_file:
                        bot.send_video(
                            message.chat.id,
                            video_file,
                            caption=f"✅ Video yuklab olindi via @{bot.get_me().username}"
                        )
                    download.status = 'success'
                    db.session.commit()
                    try:
                        os.remove(video_path)
                        os.rmdir(os.path.dirname(video_path))
                    except:
                        pass
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Xatolik yuz berdi: {error_msg}")
                    if "File is too large" in error_msg:
                        bot.edit_message_text(
                            "⚠️ Video hajmi juda katta (50MB dan oshib ketdi). Iltimos, kichikroq video tanlang.",
                            message.chat.id,
                            status_message.message_id
                        )
                    else:
                        bot.edit_message_text(
                            f"❌ Xatolik yuz berdi: {error_msg}",
                            message.chat.id,
                            status_message.message_id
                        )
                    download.status = 'failed'
                    db.session.commit()
            else:
                bot.reply_to(message, "Iltimos, avval /start buyrug'ini yuboring.")
    bot.polling(none_stop=True)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)