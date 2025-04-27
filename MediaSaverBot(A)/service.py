import logging
from datetime import datetime
from models import db, User, Download, Donation
from telegram import Update

logger = logging.getLogger(__name__)


def get_or_create_user(update: Update):
    """
    Get existing user or create a new one.
    """
    user = update.effective_user
    
    if not user:
        return None
        
    db_user = User.query.filter_by(user_id=user.id).first()
    
    if not db_user:
        # Create new user
        db_user = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_premium=getattr(user, 'is_premium', False)
        )
        
        try:
            db.session.add(db_user)
            db.session.commit()
            logger.info(f"Created new user: {db_user}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}")
            return None
    else:
        # Update last activity
        try:
            db_user.last_activity = datetime.utcnow()
            
            # Update user info if changed
            if db_user.username != user.username:
                db_user.username = user.username
            if db_user.first_name != user.first_name:
                db_user.first_name = user.first_name
            if db_user.last_name != user.last_name:
                db_user.last_name = user.last_name
                
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user activity: {e}")
    
    return db_user


def record_download(user_id, url, source_type, file_size=None, status='success', error_message=None):
    """
    Record a download attempt.
    """
    try:
        download = Download(
            user_id=user_id,
            url=url,
            source_type=source_type,
            file_size=file_size,
            status=status,
            error_message=error_message
        )
        
        db.session.add(download)
        db.session.commit()
        logger.info(f"Recorded download: {download}")
        return download
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording download: {e}")
        return None


def record_donation_click(user_id, context='after_download'):
    """
    Record when a user clicks on a donation link.
    """
    try:
        donation = Donation(
            user_id=user_id,
            context=context
        )
        
        db.session.add(donation)
        db.session.commit()
        logger.info(f"Recorded donation click: {donation}")
        return donation
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording donation click: {e}")
        return None


def get_user_stats(user_id):
    """
    Get stats for a specific user.
    """
    try:
        downloads_count = Download.query.filter_by(user_id=user_id).count()
        successful_downloads = Download.query.filter_by(user_id=user_id, status='success').count()
        
        youtube_downloads = Download.query.filter_by(user_id=user_id, source_type='youtube').count()
        instagram_downloads = Download.query.filter_by(user_id=user_id, source_type='instagram').count()
        
        donation_clicks = Donation.query.filter_by(user_id=user_id).count()
        
        return {
            'downloads_count': downloads_count,
            'successful_downloads': successful_downloads,
            'youtube_downloads': youtube_downloads,
            'instagram_downloads': instagram_downloads,
            'donation_clicks': donation_clicks
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return None


def get_total_stats():
    """
    Get overall bot stats.
    """
    try:
        total_users = User.query.count()
        total_downloads = Download.query.count()
        successful_downloads = Download.query.filter_by(status='success').count()
        
        youtube_downloads = Download.query.filter_by(source_type='youtube').count()
        instagram_downloads = Download.query.filter_by(source_type='instagram').count()
        
        donation_clicks = Donation.query.count()
        
        active_users_24h = User.query.filter(
            User.last_activity >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        return {
            'total_users': total_users,
            'total_downloads': total_downloads,
            'successful_downloads': successful_downloads,
            'youtube_downloads': youtube_downloads,
            'instagram_downloads': instagram_downloads,
            'donation_clicks': donation_clicks,
            'active_users_24h': active_users_24h
        }
    except Exception as e:
        logger.error(f"Error getting total stats: {e}")
        return None