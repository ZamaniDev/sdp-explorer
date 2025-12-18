"""Database models for SDP Explorer"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    api_base_url = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    request_history = db.relationship('RequestHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    saved_queries = db.relationship('SavedQuery', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class RequestHistory(db.Model):
    """API request history"""
    __tablename__ = 'request_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    method = db.Column(db.String(10), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    params = db.Column(db.Text, nullable=True)  # JSON string
    data = db.Column(db.Text, nullable=True)  # JSON string
    status_code = db.Column(db.Integer, nullable=True)
    response = db.Column(db.Text, nullable=True)  # JSON string
    error = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<RequestHistory {self.method} {self.url}>'


class SavedQuery(db.Model):
    """Saved API queries for quick access"""
    __tablename__ = 'saved_queries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    input_data = db.Column(db.Text, nullable=True)  # JSON string
    placeholders = db.Column(db.Text, nullable=True)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_favorite = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<SavedQuery {self.name}>'


class UserPreferences(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    theme = db.Column(db.String(20), default='light')  # light, dark
    default_view_mode = db.Column(db.String(20), default='smart')  # smart, json
    rows_per_page = db.Column(db.Integer, default=20)
    show_request_history = db.Column(db.Boolean, default=True)
    auto_refresh = db.Column(db.Boolean, default=False)
    auto_refresh_interval = db.Column(db.Integer, default=30)  # seconds

    def __repr__(self):
        return f'<UserPreferences user_id={self.user_id}>'
