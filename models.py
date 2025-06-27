from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
try:
    from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
except ImportError:
    # Fallback if flask-dance is not available
    class OAuthConsumerMixin:
        pass

# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    trust_score = db.Column(db.Float, default=5.0)
    
    # Location data
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    location_updated_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    exchange_requests = db.relationship('ExchangeRequest', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_matches = db.relationship('ExchangeMatch', foreign_keys='ExchangeMatch.requester_id', backref='requester', lazy=True)
    received_matches = db.relationship('ExchangeMatch', foreign_keys='ExchangeMatch.provider_id', backref='provider', lazy=True)

# OAuth model for Replit authentication
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

# Exchange Request model
class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # What they have vs what they want
    have_amount = db.Column(db.Float, nullable=False)
    have_denomination = db.Column(db.String, nullable=False)  # '1000', '500', '100', '50', '20', '10', '5', '1', 'coins'
    
    want_amount = db.Column(db.Float, nullable=False)  
    want_denomination = db.Column(db.String, nullable=False)
    
    # Location where exchange should happen
    exchange_latitude = db.Column(db.Float, nullable=False)
    exchange_longitude = db.Column(db.Float, nullable=False)
    exchange_location_name = db.Column(db.String, nullable=True)  # "SM Mall", "Ayala Terminal", etc.
    
    # Status and timing
    status = db.Column(db.String, default='active')  # active, matched, completed, cancelled
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Notes and preferences
    notes = db.Column(db.Text, nullable=True)
    preferred_safe_zones = db.Column(db.Text, nullable=True)  # JSON string of preferred meeting spots
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    matches = db.relationship('ExchangeMatch', backref='request', lazy=True, cascade='all, delete-orphan')

# Exchange Match model
class ExchangeMatch(db.Model):
    __tablename__ = 'exchange_matches'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), nullable=False)
    requester_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Match details
    status = db.Column(db.String, default='pending')  # pending, confirmed, completed, cancelled
    distance_km = db.Column(db.Float, nullable=False)
    
    # Timing
    matched_at = db.Column(db.DateTime, default=datetime.now)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Chat and feedback
    chat_active = db.Column(db.Boolean, default=False)
    requester_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    provider_rating = db.Column(db.Integer, nullable=True)
    requester_feedback = db.Column(db.Text, nullable=True)
    provider_feedback = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Notification model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, nullable=False)  # 'match_found', 'exchange_confirmed', 'exchange_completed', 'rating_received'
    
    # Related data
    related_request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), nullable=True)
    related_match_id = db.Column(db.Integer, db.ForeignKey('exchange_matches.id'), nullable=True)
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    related_request = db.relationship('ExchangeRequest', backref='notifications')
    related_match = db.relationship('ExchangeMatch', backref='notifications')

# Chat Message model
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('exchange_matches.id'), nullable=False)
    sender_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String, default='text')  # text, location, image
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    match = db.relationship('ExchangeMatch', backref='chat_messages')
    sender = db.relationship('User', backref='sent_messages')