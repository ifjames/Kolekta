import os
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from app import app
from firestore_models import User, ExchangeRequest, ExchangeMatch, Notification

# Authentication helpers
def is_authenticated():
    return 'user_id' in session

def get_current_user():
    if 'user_id' in session:
        user = User.get(session['user_id'])
        if user:
            return {
                'id': user.id,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'email': getattr(user, 'email', ''),
                'trust_score': getattr(user, 'trust_score', 5.0),
                'profile_image_url': getattr(user, 'profile_image_url', None)
            }
        else:
            # User session exists but user not found in Firestore, clear session
            session.pop('user_id', None)
    return None

# Firebase authentication
@app.route('/firebase-auth', methods=['POST'])
def firebase_auth():
    data = request.get_json()
    
    if not data or 'uid' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    # Check if user exists
    user = User.get(data['uid'])
    
    if not user:
        # Create new user
        name_parts = (data.get('displayName') or '').split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user_data = {
            'id': data['uid'],
            'email': data.get('email'),
            'first_name': first_name,
            'last_name': last_name,
            'profile_image_url': data.get('photoURL'),
            'is_verified': True  # Firebase users are considered verified
        }
        
        user = User.create(user_data)
    
    # Log in user
    session['user_id'] = user.id
    return jsonify({'success': True})

@app.route('/login')
def login():
    if is_authenticated():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/clear-session')
def clear_session():
    """Clear session data if there are authentication issues"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/')
def index():
    current_user = get_current_user()
    if current_user:
        # Get real data from Firestore
        from datetime import datetime
        
        # Get user's exchange requests
        user_requests = ExchangeRequest.query([
            {"field": "user_id", "operator": "==", "value": current_user['id']}
        ])
        
        # Get user's matches
        matches_as_requester = ExchangeMatch.query([
            {"field": "requester_id", "operator": "==", "value": current_user['id']}
        ])
        matches_as_provider = ExchangeMatch.query([
            {"field": "provider_id", "operator": "==", "value": current_user['id']}
        ])
        
        recent_matches = matches_as_requester + matches_as_provider
        recent_matches = sorted(recent_matches, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
        
        # Get user's notifications
        user_notifications = Notification.query([
            {"field": "user_id", "operator": "==", "value": current_user['id']}
        ])
        notifications = sorted(user_notifications, key=lambda x: x.created_at or datetime.min, reverse=True)[:5]
        
        # Convert to dicts for template
        active_requests = [req.to_dict() for req in user_requests if req.status == 'active']
        recent_matches_data = []
        for match in recent_matches:
            match_dict = match.to_dict()
            # Get provider info if user is requester
            if match.requester_id == current_user['id'] and match.provider_id:
                provider = User.get(match.provider_id)
                if provider:
                    match_dict['provider'] = provider.to_dict()
            recent_matches_data.append(match_dict)
        
        notifications_data = [notif.to_dict() for notif in notifications]
        
        return render_template('simple_dashboard.html', 
                             current_user=current_user,
                             active_requests=active_requests,
                             recent_matches=recent_matches_data,
                             notifications=notifications_data)
    else:
        return render_template('landing.html')

@app.route('/request-exchange')
def request_exchange():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    return render_template('request_exchange.html', current_user=current_user)

@app.route('/find-exchanges')
def find_exchanges():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    
    # Mock nearby requests
    requests = [
        {
            'id': 1,
            'have_amount': 500,
            'have_denomination': '500',
            'want_amount': 500,
            'want_denomination': '20',
            'distance': 1.2,
            'user_name': 'Maria',
            'location_name': 'Ayala Terminal',
            'created_at': '2025-01-27T10:30:00Z',
            'latitude': 14.5547,
            'longitude': 121.0244
        },
        {
            'id': 2,
            'have_amount': 100,
            'have_denomination': '100',
            'want_amount': 100,
            'want_denomination': '5',
            'distance': 0.8,
            'user_name': 'Roberto',
            'location_name': 'LRT Station',
            'created_at': '2025-01-27T11:15:00Z',
            'latitude': 14.5995,
            'longitude': 120.9842
        }
    ]
    
    return render_template('find_exchanges.html', 
                         current_user=current_user,
                         requests=requests)

@app.route('/create-request', methods=['POST'])
def create_request():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    # In a real app, this would save to database
    # For demo, just return success
    return jsonify({
        'success': True, 
        'request_id': 123,
        'message': 'Exchange request created successfully!'
    })

@app.route('/update-location', methods=['POST'])
def update_location():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    # In a real app, this would update user location in database
    return jsonify({'success': True})

@app.route('/api/nearby-requests')
def api_nearby_requests():
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Mock data for API
    nearby_requests = [
        {
            'id': 1,
            'have_amount': 500,
            'have_denomination': '500',
            'want_amount': 500,
            'want_denomination': '20',
            'latitude': 14.5547,
            'longitude': 121.0244,
            'location_name': 'Ayala Terminal',
            'distance': 1.2,
            'user_name': 'Maria',
            'created_at': '2025-01-27T10:30:00Z'
        }
    ]
    
    return jsonify(nearby_requests)

@app.route('/matches')
def matches():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    
    return render_template('matches.html')

@app.route('/notifications')
def notifications():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    
    return render_template('notifications.html')

@app.route('/profile')
def profile():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    
    return render_template('profile.html')

@app.route('/my-requests')
def my_requests():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('demo_login'))
    
    return render_template('my_requests.html')

# API endpoints for real-time features
@app.route('/api/check-new-matches')
def api_check_new_matches():
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'has_new_matches': False,
        'count': 0,
        'matches': []
    })

@app.route('/api/check-notifications')
def api_check_notifications():
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'has_new_notifications': False,
        'count': 0,
        'notifications': []
    })

# Add context processor to make current_user and Firebase config available in all templates
@app.context_processor
def inject_user():
    return {
        'current_user': get_current_user(),
        'firebase_api_key': os.environ.get('FIREBASE_API_KEY'),
        'firebase_project_id': os.environ.get('FIREBASE_PROJECT_ID'),
        'firebase_app_id': os.environ.get('FIREBASE_APP_ID')
    }