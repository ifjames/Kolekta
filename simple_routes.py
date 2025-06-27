from flask import render_template, request, jsonify, flash, redirect, url_for, session
from app import app

# Simple authentication helpers
def is_authenticated():
    return 'user_id' in session

def get_current_user():
    if 'user_id' in session:
        return {
            'id': 'demo-user',
            'first_name': 'Demo',
            'last_name': 'User',
            'email': 'demo@kolekta.com',
            'trust_score': 4.8,
            'profile_image_url': None
        }
    return None

# Demo login
@app.route('/demo-login')
def demo_login():
    session['user_id'] = 'demo-user'
    flash('Logged in as demo user!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/')
def index():
    current_user = get_current_user()
    if current_user:
        # Mock data for demo
        from datetime import datetime
        active_requests = [
            {
                'id': 1,
                'have_amount': 1000,
                'have_denomination': '1000',
                'want_amount': 1000,
                'want_denomination': '20',
                'status': 'active',
                'exchange_location_name': 'SM Mall',
                'created_at': datetime.now(),
                'notes': 'Need coins for jeepney fare'
            }
        ]
        
        recent_matches = [
            {
                'id': 1,
                'status': 'pending',
                'distance_km': 2.5,
                'matched_at': datetime.now(),
                'requester_id': 'demo-user',
                'provider': {
                    'first_name': 'Juan',
                    'profile_image_url': None
                }
            }
        ]
        
        notifications = [
            {
                'id': 1,
                'title': 'New Match Found!',
                'message': 'Someone nearby can exchange your ₱1000 for ₱20 coins',
                'type': 'match_found',
                'is_read': False,
                'created_at': datetime.now()
            }
        ]
        
        return render_template('simple_dashboard.html', 
                             current_user=current_user,
                             active_requests=active_requests,
                             recent_matches=recent_matches,
                             notifications=notifications)
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

# Add context processor to make current_user available in all templates
@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}