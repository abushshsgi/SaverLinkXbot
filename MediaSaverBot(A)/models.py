import os
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, Float
from typing import Optional, List
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Base model class
class Base(DeclarativeBase):
    pass


# Create a single SQLAlchemy instance for the whole application
db = SQLAlchemy(model_class=Base)

def init_db(app):
    """Initialize database with the Flask app - use this to avoid duplicate initializations"""
    db.init_app(app)
    
    # Create all tables
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        # Create new tables
        db.create_all()
        print("Database tables created successfully!")


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class User(db.Model):
    """User model to track bot users."""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # This is the telegram_id
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    username: Mapped[Optional[str]] = mapped_column(String(80))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    platform: Mapped[Optional[str]] = mapped_column(String(50))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Add relationship to downloads
    downloads = relationship("Download", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.user_id}: {self.username}>"


class Download(db.Model):
    """Download model to track user downloads."""
    __tablename__ = 'downloads'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    media_type: Mapped[Optional[str]] = mapped_column(String(20))  # video, photo, etc.
    platform: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[Optional[str]] = mapped_column(String(20), default='success')
    
    # Define the relationship properly
    user = relationship("User", back_populates="downloads")
    
    def __repr__(self):
        return f"<Download {self.id}: {self.media_type} - {self.platform}>"


class Donation(db.Model):
    """Donation model to track when users click on donation links."""
    __tablename__ = 'donations'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    clicked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    context: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., 'after_download', 'donate_command'
    
    def __repr__(self):
        return f"<Donation {self.id}: User {self.user_id}>"