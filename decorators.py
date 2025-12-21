"""
Decorators for permission checking and access control
"""
from functools import wraps
from flask import abort
from flask_login import current_user
from models import APICredential


def requires_permission(resource, action, scope='own'):
    """
    Decorator to check if user has permission for an action

    Usage:
        @requires_permission('tickets', 'delete', 'all')
        def delete_ticket(ticket_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            # For now, all authenticated users have access
            # TODO: Implement proper RBAC when roles are added

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_appropriate_credential(user, required_level):
    """
    Get the appropriate API credential based on required access level

    Args:
        user: Current user
        required_level: 'admin', 'technician', or 'requester'

    Returns:
        APICredential object or None
    """
    # Try to get credential of exact level first
    credential = APICredential.query.filter_by(
        user_id=user.id,
        role_type=required_level,
        is_active=True
    ).first()

    if credential:
        return credential

    # Fallback: if admin is requested but not found, try technician
    if required_level == 'admin':
        credential = APICredential.query.filter_by(
            user_id=user.id,
            role_type='technician',
            is_active=True
        ).first()

        if credential:
            return credential

    # Last resort: use user's default credentials from profile
    if user.api_key and user.api_base_url:
        # Create a temporary credential object
        class TempCredential:
            def __init__(self, api_key, api_base_url):
                self.api_key = api_key
                self.api_base_url = api_base_url

        return TempCredential(user.api_key, user.api_base_url)

    return None
