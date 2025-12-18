# SDP Explorer - Changelog

## Version 2.0 - December 18, 2025

### 🎉 Major Features

#### Authentication System
- **User Registration**: Secure account creation with email validation
- **User Login**: Session-based authentication with "remember me" functionality
- **Profile Management**: Users can update email and API credentials
- **Password Security**: Bcrypt-hashed passwords stored in database
- **Session Management**: Flask-Login handles secure user sessions

#### Database Integration
- **SQLite Database**: Lightweight persistent storage
- **Database Models**:
  - `User`: User accounts with credentials and API settings
  - `RequestHistory`: Persistent API request/response logs per user
  - `SavedQuery`: Save frequently used queries for quick access
  - `UserPreferences`: Personalized settings (theme, view mode, etc.)
- **Automatic Migration**: Database auto-creates on first run
- **Manual Setup**: `init_db.py` script for creating admin user

#### Saved Queries
- Save frequently used API calls
- Mark queries as favorites
- Quick access to saved queries
- Per-user query management
- CRUD operations via REST API

#### User Preferences
- Customizable theme settings
- Default view mode (smart/JSON)
- Configurable rows per page
- Auto-refresh settings
- Request history visibility toggle

#### Enhanced Security
- CSRF protection on all forms
- Password hashing with Werkzeug
- SQL injection protection via ORM
- Login required decorators
- Secure session cookies
- Per-user API credentials

### 📁 New Files

```
models.py              # SQLAlchemy database models
forms.py               # Flask-WTF form definitions
init_db.py             # Database initialization script
templates/login.html   # User login page
templates/register.html # User registration page
templates/profile.html  # User profile page
.gitignore             # Git ignore patterns
```

### 🔧 Modified Files

```
app.py                 # Complete refactor with auth & database
requirements.txt       # Added Flask-SQLAlchemy, Flask-Login, Flask-WTF
templates/layout.html  # Added navigation bar and flash messages
README.md              # Updated with features and quick start
claude.md              # Comprehensive documentation update
```

### 🔌 New API Endpoints

**Authentication**
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

**Profile Management**
- `GET /profile` - View profile
- `POST /profile` - Update profile

**Saved Queries**
- `GET /api/queries` - List all saved queries
- `POST /api/queries` - Save new query
- `DELETE /api/queries/<id>` - Delete query
- `POST /api/queries/<id>/favorite` - Toggle favorite status

**User Preferences**
- `GET /api/preferences` - Get user preferences
- `POST /api/preferences` - Update preferences

**Request History**
- `GET /api/history` - Get user's request history (now database-backed)

### 🔒 Security Enhancements

✅ **Implemented**
- Bcrypt password hashing
- CSRF protection
- SQL injection protection
- Session security
- Login-protected routes
- Per-user API credentials

⚠️ **Still Needed for Production**
- Set strong SECRET_KEY environment variable
- Enable SSL certificate verification
- Implement rate limiting
- Disable debug mode
- Add email verification
- Add password reset functionality

### 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database (optional)
python init_db.py

# Run application
python app.py

# Access at http://127.0.0.1:5000
```

**Default Test User**
- Username: `admin`
- Password: `admin123`
- Email: `admin@example.com`

### 📊 Database Schema

```sql
users
├── id (primary key)
├── username (unique, indexed)
├── email (unique, indexed)
├── password_hash
├── api_base_url (optional)
├── api_key (optional)
├── created_at
├── last_login
└── is_active

request_history
├── id (primary key)
├── user_id (foreign key → users.id, indexed)
├── timestamp (indexed)
├── method
├── url
├── params (JSON)
├── data (JSON)
├── status_code
├── response (JSON)
└── error

saved_queries
├── id (primary key)
├── user_id (foreign key → users.id, indexed)
├── name
├── description
├── category
├── endpoint
├── method
├── input_data (JSON)
├── placeholders (JSON)
├── created_at
├── updated_at
└── is_favorite

user_preferences
├── id (primary key)
├── user_id (foreign key → users.id, unique)
├── theme (light/dark)
├── default_view_mode (smart/json)
├── rows_per_page
├── show_request_history
├── auto_refresh
└── auto_refresh_interval
```

### 🎨 UX Improvements

- **Navigation Bar**: Easy access to profile and logout
- **Flash Messages**: User feedback for actions
- **Responsive Forms**: Clean, modern form design
- **Better Layout**: Improved visual hierarchy
- **User Context**: Show logged-in username
- **Error Handling**: Clear error messages for validation

### 📚 Documentation

- **README.md**: Quick start guide and features overview
- **claude.md**: Comprehensive technical documentation
- **CHANGELOG.md**: This file - detailed change log

### 🔄 Migration Notes

**Breaking Changes:**
- All routes now require authentication
- API credentials moved from config to per-user database
- Request history is now per-user (old in-memory history lost)

**Upgrade Path:**
1. Install new dependencies: `pip install -r requirements.txt`
2. Database auto-creates on first run
3. Register new user account or use `init_db.py`
4. Configure API credentials in user profile
5. Old request history will not be migrated (was in-memory only)

### 🎯 Future Enhancements

**Planned Features:**
- Dark mode theme
- Export saved queries to JSON
- Bulk query operations
- API call scheduling
- Email notifications
- Advanced search in request history
- Query sharing between users
- Role-based access control (admin/user)
- Audit logging
- API rate limiting
- Email verification
- Password reset via email

### 🐛 Known Issues

None at this time. Please report issues on GitHub.

### 👥 Contributors

- Claude (AI Assistant) - Complete implementation
- Project initiated via GitHub issue automation

---

**Full Commit**: `b6bd147`
**Branch**: `claude/init-claude-docs-4C4SE`
**Date**: December 18, 2025
