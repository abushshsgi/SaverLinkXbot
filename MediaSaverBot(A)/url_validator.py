import re
import logging

logger = logging.getLogger(__name__)

def is_youtube_url(url):
    """
    Check if the URL is a valid YouTube URL.
    Supports various YouTube URL formats including shorts, mobile links, 
    and links with additional parameters.
    """
    # More comprehensive regex for YouTube URLs
    youtube_patterns = [
        # Standard youtube.com URLs
        r'(https?://)?(www\.)?(youtube\.com/watch\?(.*&)?v=|youtube\.com/v/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})(&.*)?$',
        # Short youtu.be URLs
        r'(https?://)?youtu\.be/([a-zA-Z0-9_-]{11})(\?.*)?$',
        # YouTube shorts
        r'(https?://)?(www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})(\?.*)?$',
        # YouTube mobile app URLs
        r'(https?://)?(m\.)?youtube\.com/watch\?(.*&)?v=([a-zA-Z0-9_-]{11})(&.*)?$'
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid YouTube URL detected: {url}")
            return True
            
    logger.info(f"Not a valid YouTube URL: {url}")
    return False

def is_instagram_url(url):
    """
    Check if the URL is a valid Instagram URL.
    Supports posts, reels, stories, and other Instagram content.
    """
    # Updated regex to match more Instagram URL patterns
    instagram_patterns = [
        # Standard posts
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/p/([a-zA-Z0-9_-]+)/?(\?.*)?$',
        # Reels
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/(reel|reels)/([a-zA-Z0-9_-]+)/?(\?.*)?$',
        # Stories
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/stories/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_-]+)/?(\?.*)?$',
        # IGTV
        r'(https?://)?(www\.)?(instagram\.com|instagr\.am)/tv/([a-zA-Z0-9_-]+)/?(\?.*)?$',
        # Mobile links
        r'(https?://)?(m\.)?(instagram\.com|instagr\.am)/(p|reel|reels|tv|stories)/([a-zA-Z0-9_-]+)/?(\?.*)?$'
    ]
    
    for pattern in instagram_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid Instagram URL detected: {url}")
            return True
            
    logger.info(f"Not a valid Instagram URL: {url}")
    return False

def is_facebook_url(url):
    """
    Check if the URL is a valid Facebook video URL.
    Supports various Facebook video URL formats.
    """
    facebook_patterns = [
        # Standard video URLs
        r'(https?://)?(www\.|m\.|web\.)?facebook\.com/watch\?v=([0-9]+).*?$',
        # Shared videos on profiles/pages
        r'(https?://)?(www\.|m\.)?facebook\.com/.+?/videos/([0-9]+).*?$',
        # Shared videos on groups
        r'(https?://)?(www\.|m\.)?facebook\.com/groups/.+?/videos/([0-9]+).*?$',
        # Watch URLs with story
        r'(https?://)?(www\.|m\.)?facebook\.com/story\.php\?story_fbid=([0-9]+).*?$',
        # Short fb.watch URLs
        r'(https?://)?fb\.watch/([a-zA-Z0-9_-]+).*?$',
        # Reel URLs
        r'(https?://)?(www\.|m\.)?facebook\.com/reel/([0-9]+).*?$'
    ]
    
    for pattern in facebook_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid Facebook URL detected: {url}")
            return True
    
    logger.info(f"Not a valid Facebook URL: {url}")
    return False

def is_twitter_url(url):
    """
    Check if the URL is a valid Twitter/X video URL.
    Supports various Twitter/X video URL formats.
    """
    twitter_patterns = [
        # Twitter status URLs
        r'(https?://)?(www\.|mobile\.)?twitter\.com/([a-zA-Z0-9_]+)/status/(\d+)(\?.*)?$',
        # X.com status URLs
        r'(https?://)?(www\.)?x\.com/([a-zA-Z0-9_]+)/status/(\d+)(\?.*)?$'
    ]
    
    for pattern in twitter_patterns:
        if re.match(pattern, url):
            logger.info(f"Valid Twitter/X URL detected: {url}")
            return True
    
    logger.info(f"Not a valid Twitter/X URL: {url}")
    return False

def get_url_type(url):
    """
    Determine the type of URL (YouTube, Instagram, Facebook, Twitter or invalid).
    Returns 'youtube', 'instagram', 'facebook', 'twitter', or None.
    """
    if is_youtube_url(url):
        return 'youtube'
    elif is_instagram_url(url):
        return 'instagram'
    elif is_facebook_url(url):
        return 'facebook'  
    elif is_twitter_url(url):
        return 'twitter'
    return None
