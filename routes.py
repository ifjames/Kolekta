import json
import os
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from sqlalchemy import func, and_
from math import radians, cos, sin, asin, sqrt

from app import app, db
from models import User, ExchangeRequest, ExchangeMatch, Notification, ChatMessage

# Simple session-based authentication for demo
@app.before_request
def make_session_permanent():
    session.permanent = True

def is_authenticated():
    return 'user_id' in session

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# Create a demo user for testing
@app.route('/demo-login')
def demo_login():
    # Create or get demo user
    demo_user = User.query.filter_by(email='demo@kolekta.com').first()
    if not demo_user:
        demo_user = User(
            id='demo-user-123',
            email='demo@kolekta.com',
            first_name='Demo',
            last_name='User',
            is_verified=True,
            trust_score=4.8
        )
        db.session.add(demo_user)
        db.session.commit()
    
    session['user_id'] = demo_user.id
    flash('Logged in as demo user!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth (in km)"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

@app.route('/')
def index():
    current_user = get_current_user()
    if current_user:
        # Get user's active requests
        active_requests = ExchangeRequest.query.filter_by(
            user_id=current_user.id, 
            status='active'
        ).filter(ExchangeRequest.expires_at > datetime.now()).all()
        
        # Get recent matches
        recent_matches = ExchangeMatch.query.filter(
            (ExchangeMatch.requester_id == current_user.id) | 
            (ExchangeMatch.provider_id == current_user.id)
        ).order_by(ExchangeMatch.created_at.desc()).limit(5).all()
        
        # Get unread notifications
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).order_by(Notification.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html', 
                             current_user=current_user,
                             active_requests=active_requests,
                             recent_matches=recent_matches,
                             notifications=unread_notifications)
    else:
        return render_template('landing.html')

@app.route('/request-exchange')
@require_login
def request_exchange():
    return render_template('request_exchange.html')

@app.route('/create-request', methods=['POST'])
@require_login
def create_request():
    data = request.get_json()
    
    # Create new exchange request
    new_request = ExchangeRequest(
        user_id=current_user.id,
        have_amount=float(data['have_amount']),
        have_denomination=data['have_denomination'],
        want_amount=float(data['want_amount']),
        want_denomination=data['want_denomination'],
        exchange_latitude=float(data['latitude']),
        exchange_longitude=float(data['longitude']),
        exchange_location_name=data.get('location_name', ''),
        notes=data.get('notes', ''),
        expires_at=datetime.now() + timedelta(hours=24)  # Default 24 hour expiry
    )
    
    db.session.add(new_request)
    db.session.commit()
    
    # Find potential matches
    find_matches_for_request(new_request)
    
    return jsonify({'success': True, 'request_id': new_request.id})

def find_matches_for_request(exchange_request):
    """Find potential matches for a new exchange request"""
    # Find requests that complement this one
    potential_matches = ExchangeRequest.query.filter(
        and_(
            ExchangeRequest.user_id != exchange_request.user_id,
            ExchangeRequest.status == 'active',
            ExchangeRequest.expires_at > datetime.now(),
            ExchangeRequest.have_denomination == exchange_request.want_denomination,
            ExchangeRequest.want_denomination == exchange_request.have_denomination,
            ExchangeRequest.have_amount >= exchange_request.want_amount,
            ExchangeRequest.want_amount <= exchange_request.have_amount
        )
    ).all()
    
    for match_request in potential_matches:
        # Calculate distance
        distance = calculate_distance(
            exchange_request.exchange_latitude,
            exchange_request.exchange_longitude,
            match_request.exchange_latitude,
            match_request.exchange_longitude
        )
        
        # Only match if within 5km
        if distance <= 5:
            # Create match
            new_match = ExchangeMatch(
                request_id=exchange_request.id,
                requester_id=exchange_request.user_id,
                provider_id=match_request.user_id,
                distance_km=distance
            )
            db.session.add(new_match)
            
            # Create notifications
            requester_notification = Notification(
                user_id=exchange_request.user_id,
                title="Match Found!",
                message=f"Found someone nearby who can exchange {match_request.have_denomination} for {exchange_request.want_denomination}",
                type="match_found",
                related_request_id=exchange_request.id,
                related_match_id=new_match.id
            )
            
            provider_notification = Notification(
                user_id=match_request.user_id,
                title="Exchange Request Match",
                message=f"Someone nearby wants to exchange {exchange_request.have_denomination} for {match_request.want_denomination}",
                type="match_found",
                related_request_id=match_request.id,
                related_match_id=new_match.id
            )
            
            db.session.add(requester_notification)
            db.session.add(provider_notification)
    
    db.session.commit()

@app.route('/find-exchanges')
@require_login
def find_exchanges():
    # Get user's location from query params or session
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    if lat and lng:
        # Update user's current location
        current_user.current_latitude = lat
        current_user.current_longitude = lng
        current_user.location_updated_at = datetime.now()
        db.session.commit()
    
    # Get all active requests within 10km
    nearby_requests = []
    if current_user.current_latitude and current_user.current_longitude:
        all_requests = ExchangeRequest.query.filter(
            and_(
                ExchangeRequest.user_id != current_user.id,
                ExchangeRequest.status == 'active',
                ExchangeRequest.expires_at > datetime.now()
            )
        ).all()
        
        for req in all_requests:
            distance = calculate_distance(
                current_user.current_latitude,
                current_user.current_longitude,
                req.exchange_latitude,
                req.exchange_longitude
            )
            if distance <= 10:  # Within 10km
                req.distance = round(distance, 2)
                nearby_requests.append(req)
        
        # Sort by distance
        nearby_requests.sort(key=lambda x: x.distance)
    
    return render_template('find_exchanges.html', requests=nearby_requests)

@app.route('/my-requests')
@require_login
def my_requests():
    requests = ExchangeRequest.query.filter_by(user_id=current_user.id).order_by(
        ExchangeRequest.created_at.desc()
    ).all()
    return render_template('my_requests.html', requests=requests)

@app.route('/matches')
@require_login
def matches():
    user_matches = ExchangeMatch.query.filter(
        (ExchangeMatch.requester_id == current_user.id) | 
        (ExchangeMatch.provider_id == current_user.id)
    ).order_by(ExchangeMatch.created_at.desc()).all()
    
    return render_template('matches.html', matches=user_matches)

@app.route('/match/<int:match_id>')
@require_login
def match_detail(match_id):
    match = ExchangeMatch.query.get_or_404(match_id)
    
    # Check if user is part of this match
    if match.requester_id != current_user.id and match.provider_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('matches'))
    
    # Get chat messages
    messages = ChatMessage.query.filter_by(match_id=match_id).order_by(
        ChatMessage.created_at.asc()
    ).all()
    
    return render_template('match_detail.html', match=match, messages=messages)

@app.route('/confirm-match/<int:match_id>', methods=['POST'])
@require_login
def confirm_match(match_id):
    match = ExchangeMatch.query.get_or_404(match_id)
    
    # Check if user can confirm this match
    if match.provider_id == current_user.id and match.status == 'pending':
        match.status = 'confirmed'
        match.confirmed_at = datetime.now()
        match.chat_active = True
        
        # Create notification for requester
        notification = Notification(
            user_id=match.requester_id,
            title="Exchange Confirmed!",
            message="Your exchange request has been confirmed. You can now chat with your exchange partner.",
            type="exchange_confirmed",
            related_match_id=match_id
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Exchange confirmed! You can now chat with your exchange partner.', 'success')
    
    return redirect(url_for('match_detail', match_id=match_id))

@app.route('/send-message/<int:match_id>', methods=['POST'])
@require_login
def send_message(match_id):
    match = ExchangeMatch.query.get_or_404(match_id)
    
    # Check if user is part of this match and chat is active
    if ((match.requester_id != current_user.id and match.provider_id != current_user.id) or 
        not match.chat_active):
        return jsonify({'error': 'Access denied'}), 403
    
    message_text = request.json.get('message', '').strip()
    if not message_text:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Create message
    message = ChatMessage(
        match_id=match_id,
        sender_id=current_user.id,
        message=message_text
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message.id,
            'sender_name': current_user.first_name or 'User',
            'message': message.message,
            'created_at': message.created_at.strftime('%H:%M')
        }
    })

@app.route('/notifications')
@require_login
def notifications():
    user_notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark as read
    for notification in user_notifications:
        notification.is_read = True
    db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/profile')
@require_login
def profile():
    return render_template('profile.html')

@app.route('/update-location', methods=['POST'])
@require_login
def update_location():
    data = request.get_json()
    current_user.current_latitude = float(data['latitude'])
    current_user.current_longitude = float(data['longitude'])
    current_user.location_updated_at = datetime.now()
    db.session.commit()
    return jsonify({'success': True})

# API endpoint for getting nearby requests (for map view)
@app.route('/api/nearby-requests')
@require_login
def api_nearby_requests():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 5, type=float)  # Default 5km radius
    
    if not lat or not lng:
        return jsonify({'error': 'Location required'}), 400
    
    # Get all active requests within radius
    all_requests = ExchangeRequest.query.filter(
        and_(
            ExchangeRequest.user_id != current_user.id,
            ExchangeRequest.status == 'active',
            ExchangeRequest.expires_at > datetime.now()
        )
    ).all()
    
    nearby_requests = []
    for req in all_requests:
        distance = calculate_distance(lat, lng, req.exchange_latitude, req.exchange_longitude)
        if distance <= radius:
            nearby_requests.append({
                'id': req.id,
                'have_amount': req.have_amount,
                'have_denomination': req.have_denomination,
                'want_amount': req.want_amount,  
                'want_denomination': req.want_denomination,
                'latitude': req.exchange_latitude,
                'longitude': req.exchange_longitude,
                'location_name': req.exchange_location_name,
                'distance': round(distance, 2),
                'user_name': req.user.first_name or 'User',
                'created_at': req.created_at.isoformat()
            })
    
    return jsonify(nearby_requests)