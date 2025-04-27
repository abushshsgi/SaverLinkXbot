import os
import tempfile
import logging
import yt_dlp
import instaloader
import requests
from config import MAX_FILE_SIZE

# TikTok, Twitter, Facebook and other social media download functions

logger = logging.getLogger(__name__)

class DownloadError(Exception):
    """Custom exception for download errors"""
    pass

def download_youtube_video(url):
    """
    Download a video from YouTube using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "video.%(ext)s")
        
        # Set up yt-dlp options
        ydl_opts = {
            'format': 'best[filesize<50M]/bestvideo[filesize<50M]+bestaudio[filesize<30M]/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
            'verbose': True,
            'geo_bypass': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        # Try downloading with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading YouTube video: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                raise DownloadError("Could not retrieve video information.")
                
            logger.info(f"Downloaded video: {info.get('title', 'Unknown title')}")
            
            # Find the downloaded file
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    logger.info(f"Found downloaded file: {file_path}")
                    
                    # Verify file size
                    file_size = os.path.getsize(file_path)
                    logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
                    
                    if file_size > MAX_FILE_SIZE:
                        os.remove(file_path)
                        raise DownloadError(f"Video is too large to send via Telegram (size: {file_size / (1024*1024):.2f} MB)")
                    
                    return file_path
            
            raise DownloadError("Could not find the downloaded video file.")
        
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp download error: {str(e)}")
        # More user-friendly error message
        error_msg = str(e).lower()
        if "copyright" in error_msg or "unavailable" in error_msg:
            raise DownloadError("This video is unavailable due to copyright restrictions or regional limitations.")
        elif "private" in error_msg:
            raise DownloadError("This video is private or requires login.")
        elif "not found" in error_msg or "does not exist" in error_msg:
            raise DownloadError("The video does not exist or has been removed.")
        else:
            raise DownloadError(f"Failed to download YouTube video: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {str(e)}")
        raise DownloadError(f"Failed to download YouTube video: {str(e)}")

def download_twitter_video(url):
    """
    Download a video from Twitter/X using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "twitter_video.%(ext)s")
        
        # Set up yt-dlp options for Twitter/X
        ydl_opts = {
            'format': 'best[filesize<50M]/bestvideo[filesize<50M]+bestaudio[filesize<30M]/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
            'verbose': True,
            'geo_bypass': True,
            'extractor_args': {
                'twitter': {
                    'legacy_api': True,
                    'api_gql': False,
                    'force_https': True
                }
            },
            'cookiesfrombrowser': ('chrome', 'firefox', 'opera', 'edge', 'safari'),
            'socket_timeout': 30
        }
        
        # Try downloading with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading Twitter/X video: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                raise DownloadError("Could not retrieve video information.")
                
            logger.info(f"Downloaded video: {info.get('title', 'Unknown title')}")
            
            # Find the downloaded file
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    logger.info(f"Found downloaded file: {file_path}")
                    
                    # Verify file size
                    file_size = os.path.getsize(file_path)
                    logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
                    
                    if file_size > MAX_FILE_SIZE:
                        os.remove(file_path)
                        raise DownloadError(f"Video is too large to send via Telegram (size: {file_size / (1024*1024):.2f} MB)")
                    
                    return file_path
            
            raise DownloadError("Could not find the downloaded video file.")
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp Twitter/X download error: {str(e)}")
        error_msg = str(e).lower()
        if "private" in error_msg or "protected" in error_msg:
            raise DownloadError("This Twitter/X account is private or the tweet is protected. You can only download public content.")
        elif "not found" in error_msg or "does not exist" in error_msg:
            raise DownloadError("The tweet does not exist or has been removed.")
        else:
            raise DownloadError(f"Failed to download Twitter/X video: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading Twitter/X video: {str(e)}")
        raise DownloadError(f"Failed to download Twitter/X video: {str(e)}")

def download_facebook_video(url):
    """
    Download a video from Facebook using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        output_template = os.path.join(temp_dir, "facebook_video.%(ext)s")
        
        # Set up yt-dlp options for Facebook
        ydl_opts = {
            'format': 'best[filesize<50M]/bestvideo[filesize<50M]+bestaudio[filesize<30M]/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
            'verbose': True,
            'geo_bypass': True,
            'cookiesfrombrowser': ('chrome', 'firefox', 'opera', 'edge', 'safari'),
            'socket_timeout': 30,
            'extractor_args': {
                'facebook': {
                    'want_video': '1',
                    'download_video': True,
                    'prefer_public': True,
                    'prefer_mobile': True,
                    'maxrate': '8M'
                }
            },
        }
        
        # Try downloading with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading Facebook video: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                raise DownloadError("Could not retrieve video information.")
                
            logger.info(f"Downloaded video: {info.get('title', 'Unknown title')}")
            
            # Find the downloaded file
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    logger.info(f"Found downloaded file: {file_path}")
                    
                    # Verify file size
                    file_size = os.path.getsize(file_path)
                    logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
                    
                    if file_size > MAX_FILE_SIZE:
                        os.remove(file_path)
                        raise DownloadError(f"Video is too large to send via Telegram (size: {file_size / (1024*1024):.2f} MB)")
                    
                    return file_path
            
            raise DownloadError("Could not find the downloaded video file.")
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp Facebook download error: {str(e)}")
        error_msg = str(e).lower()
        if "private" in error_msg:
            raise DownloadError("This Facebook content is private. You can only download public content.")
        elif "not found" in error_msg or "does not exist" in error_msg:
            raise DownloadError("The Facebook video does not exist or has been removed.")
        else:
            raise DownloadError(f"Failed to download Facebook video: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading Facebook video: {str(e)}")
        raise DownloadError(f"Failed to download Facebook video: {str(e)}")

def download_instagram_video(url):
    """
    Download a video from Instagram using yt-dlp.
    Returns the path to the downloaded file.
    """
    try:
        # First try to use yt-dlp for Instagram
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            output_template = os.path.join(temp_dir, "instagram_video.%(ext)s")
            
            # Set up yt-dlp options for Instagram
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_template,
                'noplaylist': True,
                'quiet': False,
                'no_warnings': False,
                'ignoreerrors': False,
                'verbose': True,
                'geo_bypass': True,
            }
            
            # Try downloading with yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading Instagram video with yt-dlp: {url}")
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise DownloadError("Could not retrieve video information.")
                    
                logger.info(f"Downloaded video: {info.get('title', 'Unknown title')}")
                
                # Find the downloaded file
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    if os.path.isfile(file_path):
                        logger.info(f"Found downloaded file: {file_path}")
                        
                        # Verify file size
                        file_size = os.path.getsize(file_path)
                        logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
                        
                        if file_size > MAX_FILE_SIZE:
                            os.remove(file_path)
                            raise DownloadError(f"Video is too large to send via Telegram (size: {file_size / (1024*1024):.2f} MB)")
                        
                        return file_path
                
                raise DownloadError("Could not find the downloaded video file.")
                
        except yt_dlp.utils.DownloadError as e:
            # If yt-dlp fails, fall back to instaloader
            logger.warning(f"yt-dlp failed for Instagram, trying instaloader: {str(e)}")
            
            # Fall back to instaloader method
            temp_dir = tempfile.mkdtemp()
            
            # Initialize Instaloader
            L = instaloader.Instaloader(dirname_pattern=temp_dir, filename_pattern="{profile}_{mediaid}")
            
            # Extract the shortcode from URL
            if '/p/' in url:
                shortcode = url.split('/p/')[1].split('/')[0]
            elif '/reel/' in url:
                shortcode = url.split('/reel/')[1].split('/')[0]
            else:
                raise DownloadError("Could not extract post ID from URL.")
            
            # Download the post
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            # Check if it's a video
            if not post.is_video:
                raise DownloadError("This Instagram post does not contain a video. It might be a photo post.")
                
            # Download the video
            L.download_post(post, target=temp_dir)
            
            # Find the downloaded video file
            for file in os.listdir(temp_dir):
                if file.endswith('.mp4'):
                    video_path = os.path.join(temp_dir, file)
                    
                    # Check if the file is too large for Telegram
                    file_size = os.path.getsize(video_path)
                    if file_size > MAX_FILE_SIZE:
                        raise DownloadError(f"Video is too large to send via Telegram (size: {file_size / (1024*1024):.2f} MB)")
                        
                    return video_path
                    
            raise DownloadError("Could not find downloaded video file.")
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp Instagram download error: {str(e)}")
        error_msg = str(e).lower()
        if "private" in error_msg:
            raise DownloadError("This Instagram account is private. You can only download public content.")
        elif "not found" in error_msg or "does not exist" in error_msg:
            raise DownloadError("The Instagram post does not exist or has been removed.")
        else:
            raise DownloadError(f"Failed to download Instagram video: {str(e)}")
    
    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Instaloader error: {str(e)}")
        error_msg = str(e).lower()
        if "is private" in error_msg:
            raise DownloadError("This Instagram account is private. You can only download public content.")
        else:
            raise DownloadError(f"Failed to download Instagram video: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading Instagram video: {str(e)}")
        raise DownloadError(f"Failed to download Instagram video: {str(e)}")
