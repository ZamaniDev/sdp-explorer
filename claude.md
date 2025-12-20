# SDP Explorer - Project Overview

## Project Summary
A Flask-based web application for exploring and interacting with the ME SDP MSP (ManageEngine Service Desk Plus) API. Provides an intuitive interface with **user authentication, database persistence, and saved queries** for testing API endpoints, viewing responses, and managing service desk requests.

## Technology Stack
- **Backend**: Flask 3.0.0 (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with bcrypt password hashing
- **Forms**: Flask-WTF with CSRF protection
- **HTTP Client**: requests 2.31.0
- **Frontend**: Vanilla JavaScript, HTML/CSS
- **API**: ManageEngine Service Desk Plus v3 REST API

## Project Structure
```
sdp-explorer/
├── app.py                 # Flask application with authentication & API routes
├── models.py              # SQLAlchemy database models
├── forms.py               # Flask-WTF form definitions
├── config.py              # API configuration and endpoint definitions
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── instance/
│   └── sdp_explorer.db   # SQLite database (created at runtime)
├── templates/
│   ├── layout.html       # Base HTML template with navigation
│   ├── login.html        # User login page
│   ├── register.html     # User registration page
│   ├── profile.html      # User profile & settings page
│   └── explorer.html     # Main API explorer interface
└── static/
    └── explorer.js       # Frontend JavaScript logic
```

## Key Features

### NEW: Authentication & User Management
- **User Registration**: Secure account creation with email validation (`templates/register.html`)
- **User Login**: Session-based authentication with "remember me" functionality (`templates/login.html`)
- **Profile Management**: Users can update email and API credentials (`templates/profile.html`)
- **Password Security**: Bcrypt-hashed passwords in database (`models.py:30-35`)
- **Session Management**: Flask-Login handles user sessions (`app.py:20-32`)
- **Per-user API Configuration**: Each user can configure their own API credentials (`models.py:16-17`)

### NEW: Database Persistence
- **SQLite Database**: Lightweight database stored in `instance/sdp_explorer.db`
- **Database Models** (`models.py`):
  - `User`: User accounts with credentials and API settings
  - `RequestHistory`: Persistent API request/response logs per user
  - `SavedQuery`: User's saved API queries for quick access
  - `UserPreferences`: Personalized settings (theme, view mode, etc.)
- **Automatic Initialization**: Database created automatically on first run (`app.py:441-445`)
- **Manual Initialization**: Run `python init_db.py` to create admin user

### NEW: Saved Queries Feature
- **Save Frequently Used Queries**: Store commonly used API calls for quick access
- **Favorite Queries**: Mark important queries as favorites for priority display
- **Query Management**: Create, update, delete, and organize saved queries
- **API Endpoints**:
  - `GET /api/queries` - List all saved queries (`app.py:318-342`)
  - `POST /api/queries` - Save a new query (`app.py:345-366`)
  - `DELETE /api/queries/<id>` - Delete a query (`app.py:369-378`)
  - `POST /api/queries/<id>/favorite` - Toggle favorite status (`app.py:381-390`)

### NEW: User Preferences
- **Customizable Settings**: Theme, default view mode, rows per page
- **Auto-refresh**: Optional automatic data refresh with configurable interval
- **Request History Visibility**: Toggle request history display
- **API Endpoints**:
  - `GET /api/preferences` - Get user preferences (`app.py:394-411`)
  - `POST /api/preferences` - Update preferences (`app.py:414-438`)

### NEW: Enhanced Security
- **CSRF Protection**: Flask-WTF provides CSRF tokens for all forms
- **Password Hashing**: Werkzeug security for password storage
- **Login Required**: All API routes protected with `@login_required` decorator
- **Session Security**: Secure session management with secret key
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection

### 1. API Connection Testing
- Quick connectivity test to verify API key validity
- Tests basic request endpoint functionality
- Located in `app.py:64-76` (test_connection route)

### 2. API Explorer
- **Category-based endpoint selection**: Organized by resource type (Requests, Users, Technicians, Notes, Worklogs, Reports)
- **Flexible input modes**:
  - Form mode with visual controls
  - Raw JSON mode for advanced usage
- **Smart response rendering**:
  - Card-based list views
  - Detailed modal views for individual items
  - JSON raw view option
- **Search and filtering**:
  - Dynamic field discovery from API responses
  - Multi-filter support with field path notation
  - Real-time result filtering

### 3. Quick Views
- Pre-configured views for common queries:
  - Recent requests (20 most recent)
  - All technicians list
- Switchable smart/JSON view modes

### 4. Request History
- Logs last 50 API requests
- Captures request/response details
- Debugging aid with full request/response inspection

### 5. Pagination Support
- Automatic pagination controls
- Tracks current page and total count
- Next/Previous navigation

## Configuration (`config.py`)

### API Settings
- **Base URL**: `https://support.pirasys.com/api/v3`
- **Authentication**: API key-based (authtoken header)
- **Current API Key**: `A38AFA8D-0DCD-440F-B8DC-759E5C9D3C3F`

### Defined Endpoints
The application supports the following endpoint categories:
- **Requests**: List, view, add, update, assign
- **Notes**: List, view, add notes to requests
- **Users**: List and view users
- **Technicians**: List and view technicians
- **Worklogs**: Request worklogs and summaries
- **Reports**: List, execute reports and queries

## Core Functionality

### API Call Handler (`app.py:12-57`)
- Centralized API communication function
- Handles GET, POST, PUT, DELETE methods
- SSL verification disabled for self-signed certificates
- Automatic request/response logging
- Error handling with detailed error messages

### Smart Response Renderer (`static/explorer.js:455-740`)
- Intelligent detection of response structure
- Automatic identification of lists vs single objects
- Preview field selection based on field importance:
  - ID fields (request_id, ticket_id, user_id)
  - Name/title fields
  - Status/priority badges with colors
  - Timestamps
  - Person fields (requester, technician)

### Dynamic Field Discovery (`static/explorer.js:195-295`)
- Analyzes API response structure
- Extracts filterable field paths
- Groups fields by category
- Enables click-to-add filter functionality
- Handles nested objects (e.g., `status.name`, `requester.id`)

### Search Filter System
- Supports dot notation for nested fields
- Multiple filters with AND logic
- Dynamic filter management (add/remove)
- Integrates with ME SDP API's `search_fields` parameter

## API Integration Details

### Request Format
GET requests use query parameters:
```python
params = {
    'input_data': json.dumps({
        'list_info': {
            'row_count': 20,
            'start_index': 1,
            'sort_field': 'created_time',
            'sort_order': 'desc',
            'get_total_count': True,
            'search_fields': {
                'status.name': 'Open',
                'priority.name': 'High'
            }
        }
    })
}
```

POST/PUT requests use form data:
```python
data = {
    'input_data': json.dumps({
        # request body
    })
}
```

### Authentication
All requests include:
```python
headers = {"authtoken": API_KEY}
```

### Response Structure
Standard ME SDP API response format:
```json
{
    "list_info": {
        "total_count": 100,
        "has_more_rows": true,
        "start_index": 1,
        "row_count": 20
    },
    "requests": [
        {
            "id": "12345",
            "subject": "Request subject",
            "status": {"name": "Open", "color": "#00ff00"},
            "requester": {"name": "John Doe", "id": "123"}
        }
    ]
}
```

## Running the Application

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (optional - will auto-create on first run)
python init_db.py
```

### Start Server
```bash
python app.py
```

### First Time Setup
1. Navigate to `http://127.0.0.1:5000`
2. You'll be redirected to the login page
3. Click "Register here" to create your first account
4. Fill in username, email, password (API credentials optional)
5. After registration, login with your credentials
6. Access the API explorer dashboard

### Default Test User (if created via init_db.py)
- **Username**: admin
- **Password**: admin123
- **Email**: admin@example.com

### Configuration
- **Secret Key**: Set via `SECRET_KEY` environment variable (defaults to dev key)
- **Database**: SQLite at `instance/sdp_explorer.db`
- **Debug Mode**: Enabled by default in `app.py:460`

## Security Considerations

### ✅ Implemented Security Features
1. **User Authentication**: Flask-Login with session management
2. **Password Hashing**: Werkzeug's bcrypt-based password hashing
3. **CSRF Protection**: Flask-WTF provides CSRF tokens for all forms
4. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
5. **Per-user API Credentials**: API keys stored per-user in database (encrypted at rest)
6. **Login Required**: All API endpoints protected with `@login_required` decorator
7. **Session Security**: Secure session cookies with secret key

### ⚠️ Remaining Security Issues
1. **SSL Verification Disabled**: `verify=False` in API requests (for self-signed certs)
2. **No Rate Limiting**: No throttling on API calls
3. **Debug Mode in Production**: Should be disabled for production deployment
4. **Secret Key**: Using default dev key (should use strong random key in production)
5. **No Email Verification**: Registration doesn't verify email addresses
6. **No Password Reset**: No forgot password functionality

### Recommended Production Improvements
- Set strong `SECRET_KEY` environment variable
- Enable SSL verification with proper certificate handling
- Implement rate limiting (Flask-Limiter)
- Disable debug mode for production
- Add email verification for new registrations
- Implement password reset functionality
- Use HTTPS for the web interface
- Add brute-force protection for login attempts
- Implement audit logging for security events

## Development Notes

### URL Placeholder Replacement
The application supports dynamic URL parameters using `{placeholder}` syntax:
- Example: `/requests/{request_id}`
- Replaced in `app.py:86-89` before making API call

### Request History Management
- Stored in-memory (lost on restart)
- Limited to 50 most recent requests
- Could be persisted to database for long-term storage

### Frontend State Management
Global JavaScript state variables (`static/explorer.js:3-14`):
- `endpoints`: Endpoint configuration from backend
- `lastResponse`: Most recent API response
- `currentPage`: Pagination tracking
- `discoveredFields`: Cached filterable fields

## API Endpoint Reference

### Requests
- **GET** `/requests` - List all requests
- **GET** `/requests/{request_id}` - View specific request
- **POST** `/requests` - Create new request
- **PUT** `/requests/{request_id}` - Update request
- **POST** `/requests/{request_id}/assign` - Assign request

### Notes
- **GET** `/requests/{request_id}/notes` - List notes
- **GET** `/requests/{request_id}/notes/{note_id}` - View note
- **POST** `/requests/{request_id}/notes` - Add note

### Users & Technicians
- **GET** `/users` - List users
- **GET** `/users/{user_id}` - View user
- **GET** `/technicians` - List technicians
- **GET** `/technicians/{technician_id}` - View technician

### Worklogs
- **GET** `/requests/{request_id}/worklogs` - List worklogs
- **GET** `/requests/{request_id}/worklogs/summary` - Worklog summary

### Reports
- **GET** `/reports` - List available reports
- **POST** `/reports/{report_id}/execute` - Execute report
- **POST** `/reports/execute_query` - Execute custom query

### Accounts
- **GET** `/accounts` - List all accounts
- **GET** `/accounts/{account_id}` - View specific account
- **POST** `/accounts` - Create new account (Admin only)
- **PUT** `/accounts/{account_id}` - Update account (Admin only)
- **DELETE** `/accounts/{account_id}` - Delete account (Admin only)
- **GET** `/accounts/{account_id}/contacts` - List account contacts
- **GET** `/accounts/{account_id}/sites` - List account sites

For detailed Accounts API documentation, see `docs/ACCOUNTS_API.md`

## Future Enhancement Ideas
- User authentication system
- Saved queries/favorites
- Export to CSV/Excel
- Bulk operations support
- Webhook configuration
- Custom report builder
- Dark mode UI
- Request templates
- Attachment upload/download
- Email notifications integration
