"""SDP Explorer - Flask application with authentication and database"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import requests
import json
from datetime import datetime
import os
from models import db, User, RequestHistory, SavedQuery, UserPreferences
from forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm, SaveQueryForm

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sdp_explorer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Import config for default values (fallback)
from config import API_BASE_URL as DEFAULT_API_BASE_URL, API_KEY as DEFAULT_API_KEY, ENDPOINTS


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def get_user_api_config():
    """Get API configuration for current user"""
    if current_user.is_authenticated:
        api_base_url = current_user.api_base_url or DEFAULT_API_BASE_URL
        api_key = current_user.api_key or DEFAULT_API_KEY
    else:
        api_base_url = DEFAULT_API_BASE_URL
        api_key = DEFAULT_API_KEY
    return api_base_url, api_key


def api_call(method, endpoint, params=None, data=None):
    """Make API call to ME SDP MSP"""
    api_base_url, api_key = get_user_api_config()
    url = f"{api_base_url}{endpoint}"
    headers = {"authtoken": api_key}

    # Prepare log entry
    log_entry = {
        "timestamp": datetime.utcnow(),
        "method": method.upper(),
        "url": url,
        "params": json.dumps(params) if params else None,
        "data": json.dumps(data) if data else None,
    }

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, verify=False)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=data, verify=False)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, data=data, verify=False)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)

        # Log response
        log_entry["status_code"] = response.status_code
        log_entry["response"] = response.text

        # Save to database if user is authenticated
        if current_user.is_authenticated:
            history = RequestHistory(
                user_id=current_user.id,
                timestamp=log_entry["timestamp"],
                method=log_entry["method"],
                url=log_entry["url"],
                params=log_entry["params"],
                data=log_entry["data"],
                status_code=log_entry["status_code"],
                response=log_entry["response"]
            )
            db.session.add(history)
            db.session.commit()

        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json() if response.text else {},
            "raw": response.text
        }
    except Exception as e:
        log_entry["error"] = str(e)

        # Save error to database
        if current_user.is_authenticated:
            history = RequestHistory(
                user_id=current_user.id,
                timestamp=log_entry["timestamp"],
                method=log_entry["method"],
                url=log_entry["url"],
                params=log_entry["params"],
                data=log_entry["data"],
                error=str(e)
            )
            db.session.add(history)
            db.session.commit()

        return {
            "success": False,
            "error": str(e)
        }


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            api_base_url=form.api_base_url.data or None,
            api_key=form.api_key.data or None
        )
        user.set_password(form.password.data)

        # Create default preferences
        preferences = UserPreferences(user=user)

        db.session.add(user)
        db.session.add(preferences)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.api_base_url = form.api_base_url.data or None
        current_user.api_key = form.api_key.data or None
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form)


# Main application routes
@app.route('/')
@login_required
def index():
    """Main explorer page"""
    # Get user's saved queries
    saved_queries = SavedQuery.query.filter_by(user_id=current_user.id).order_by(
        SavedQuery.is_favorite.desc(),
        SavedQuery.updated_at.desc()
    ).all()

    return render_template('explorer.html',
                         endpoints=ENDPOINTS,
                         saved_queries=saved_queries)


@app.route('/api/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Test API connectivity"""
    result = api_call("GET", "/requests", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 1,
                "start_index": 1,
                "get_total_count": True
            }
        })
    })
    return jsonify(result)


@app.route('/api/call', methods=['POST'])
@login_required
def make_api_call():
    """Generic API call endpoint"""
    data = request.json
    method = data.get('method', 'GET')
    endpoint = data.get('endpoint', '')
    input_data = data.get('input_data', {})

    # Replace placeholders in endpoint
    placeholders = data.get('placeholders', {})
    for key, value in placeholders.items():
        endpoint = endpoint.replace(f"{{{key}}}", str(value))

    # Prepare request
    if method.upper() == "GET":
        params = {'input_data': json.dumps(input_data)} if input_data else None
        result = api_call(method, endpoint, params=params)
    else:
        data_param = {'input_data': json.dumps(input_data)} if input_data else None
        result = api_call(method, endpoint, data=data_param)

    return jsonify(result)


@app.route('/api/quick/requests', methods=['GET'])
@login_required
def quick_requests():
    """Quick view: List recent requests"""
    result = api_call("GET", "/requests", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 20,
                "start_index": 1,
                "sort_field": "created_time",
                "sort_order": "desc",
                "get_total_count": True
            }
        })
    })
    return jsonify(result)


@app.route('/api/quick/technicians', methods=['GET'])
@login_required
def quick_technicians():
    """Quick view: List all technicians"""
    result = api_call("GET", "/technicians", params={
        'input_data': json.dumps({
            "list_info": {
                "row_count": 100,
                "start_index": 1,
                "get_total_count": True
            }
        })
    })
    return jsonify(result)


@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """Get request history for current user"""
    limit = request.args.get('limit', 50, type=int)
    history = RequestHistory.query.filter_by(user_id=current_user.id)\
        .order_by(RequestHistory.timestamp.desc())\
        .limit(limit)\
        .all()

    result = []
    for h in history:
        result.append({
            'id': h.id,
            'timestamp': h.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'method': h.method,
            'url': h.url,
            'params': h.params,
            'data': h.data,
            'status_code': h.status_code,
            'response': h.response,
            'error': h.error
        })

    return jsonify(result)


# Saved Queries routes
@app.route('/api/queries', methods=['GET'])
@login_required
def get_saved_queries():
    """Get all saved queries for current user"""
    queries = SavedQuery.query.filter_by(user_id=current_user.id)\
        .order_by(SavedQuery.is_favorite.desc(), SavedQuery.updated_at.desc())\
        .all()

    result = []
    for q in queries:
        result.append({
            'id': q.id,
            'name': q.name,
            'description': q.description,
            'category': q.category,
            'endpoint': q.endpoint,
            'method': q.method,
            'input_data': json.loads(q.input_data) if q.input_data else {},
            'placeholders': json.loads(q.placeholders) if q.placeholders else {},
            'is_favorite': q.is_favorite,
            'created_at': q.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': q.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result)


@app.route('/api/queries', methods=['POST'])
@login_required
def save_query():
    """Save a new query"""
    data = request.json

    query = SavedQuery(
        user_id=current_user.id,
        name=data.get('name'),
        description=data.get('description'),
        category=data.get('category'),
        endpoint=data.get('endpoint'),
        method=data.get('method'),
        input_data=json.dumps(data.get('input_data', {})),
        placeholders=json.dumps(data.get('placeholders', {})),
        is_favorite=data.get('is_favorite', False)
    )

    db.session.add(query)
    db.session.commit()

    return jsonify({'success': True, 'id': query.id})


@app.route('/api/queries/<int:query_id>', methods=['DELETE'])
@login_required
def delete_query(query_id):
    """Delete a saved query"""
    query = SavedQuery.query.filter_by(id=query_id, user_id=current_user.id).first()
    if query:
        db.session.delete(query)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Query not found'}), 404


@app.route('/api/queries/<int:query_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(query_id):
    """Toggle favorite status of a query"""
    query = SavedQuery.query.filter_by(id=query_id, user_id=current_user.id).first()
    if query:
        query.is_favorite = not query.is_favorite
        db.session.commit()
        return jsonify({'success': True, 'is_favorite': query.is_favorite})
    return jsonify({'success': False, 'error': 'Query not found'}), 404


# User preferences routes
@app.route('/api/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get user preferences"""
    prefs = current_user.preferences
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.session.add(prefs)
        db.session.commit()

    return jsonify({
        'theme': prefs.theme,
        'default_view_mode': prefs.default_view_mode,
        'rows_per_page': prefs.rows_per_page,
        'show_request_history': prefs.show_request_history,
        'auto_refresh': prefs.auto_refresh,
        'auto_refresh_interval': prefs.auto_refresh_interval
    })


@app.route('/api/preferences', methods=['POST'])
@login_required
def update_preferences():
    """Update user preferences"""
    prefs = current_user.preferences
    if not prefs:
        prefs = UserPreferences(user_id=current_user.id)
        db.session.add(prefs)

    data = request.json
    if 'theme' in data:
        prefs.theme = data['theme']
    if 'default_view_mode' in data:
        prefs.default_view_mode = data['default_view_mode']
    if 'rows_per_page' in data:
        prefs.rows_per_page = data['rows_per_page']
    if 'show_request_history' in data:
        prefs.show_request_history = data['show_request_history']
    if 'auto_refresh' in data:
        prefs.auto_refresh = data['auto_refresh']
    if 'auto_refresh_interval' in data:
        prefs.auto_refresh_interval = data['auto_refresh_interval']

    db.session.commit()
    return jsonify({'success': True})


# Import site matrix routes
import site_matrix_routes


def init_db():
    """Initialize database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == '__main__':
    # Disable SSL warnings for self-signed certificates
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Initialize database if it doesn't exist
    db_path = os.path.join(app.instance_path, 'sdp_explorer.db')
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        os.makedirs(app.instance_path, exist_ok=True)
        init_db()

    app.run(debug=True, host='172.14.200.12', port=5000)
