from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)

def get_donation_keyboard(donation_url):
    """
    Create an inline keyboard with a donation button.
    Validates the URL to ensure it's a proper HTTP/HTTPS URL.
    """
    # Make sure the URL is valid (starts with http:// or https://)
    if donation_url and not (donation_url.startswith('http://') or donation_url.startswith('https://')):
        logger.warning(f"Invalid donation URL format: {donation_url}")
        # Use a safe default URL if the provided one is invalid
        donation_url = "https://telegram.me/start"
        
    logger.info(f"Creating donation keyboard with URL: {donation_url}")
    
    try:
        # InlineKeyboardButton can't have both url and callback_data
        # We need to split into two separate buttons or just use URL
        keyboard = [
            [InlineKeyboardButton("💖 Support Us", url=donation_url)]
        ]
        return InlineKeyboardMarkup(keyboard)
    except Exception as e:
        logger.error(f"Error creating donation keyboard: {str(e)}")
        # Return empty keyboard in case of error
        return None
