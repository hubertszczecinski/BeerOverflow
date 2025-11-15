"""
MFA (Multi-Factor Authentication) utility functions.
Provides token generation and validation for secured operations.
"""
from flask import request, jsonify, current_app
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from functools import wraps


def generate_mfa_token(user_id, scope='mfa_commit', duration_minutes=60):
    """
    Generate a JWT token for MFA operations.

    Args:
        user_id: The user ID to associate with the token
        scope: The scope of the token (default: 'mfa_commit')
        duration_minutes: Token validity duration in minutes (default: 60)

    Returns:
        tuple: (token_string, expiry_datetime)
    """
    expiry = datetime.utcnow() + timedelta(minutes=duration_minutes)
    payload = {
        'sub': user_id,
        'scope': scope,
        'iat': datetime.utcnow(),
        'exp': expiry
    }
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    return token, expiry


def verify_mfa_token(token, required_scope='mfa_commit'):
    """
    Verify and decode an MFA token.

    Args:
        token: The JWT token string to verify
        required_scope: The expected scope for the token (default: 'mfa_commit')

    Returns:
        dict: Decoded payload if valid

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
        ValueError: If scope doesn't match or user doesn't match current user
    """
    payload = jwt.decode(
        token,
        current_app.config['SECRET_KEY'],
        algorithms=["HS256"]
    )

    # Verify scope
    if payload.get('scope') != required_scope:
        raise ValueError(f"Invalid token scope. Expected '{required_scope}', got '{payload.get('scope')}'")

    # Verify user (if current_user is available)
    if current_user and current_user.is_authenticated:
        if payload.get('sub') != current_user.id:
            raise ValueError("Token user does not match current user")

    return payload


def require_mfa_token(scope='mfa_commit'):
    """
    Decorator to require a valid MFA token for an endpoint.
    Token should be provided in the Authorization header as 'Bearer <token>'.

    Args:
        scope: The required scope for the token (default: 'mfa_commit')

    Usage:
        @bp.route('/protected-endpoint', methods=['POST'])
        @login_required
        @require_mfa_token()
        def protected_endpoint():
            # Your endpoint logic here
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the MFA token from the header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'message': 'MFA token is missing or invalid'}), 401

            mfa_token = auth_header.split(' ')[1]

            # Validate the MFA token
            try:
                payload = verify_mfa_token(mfa_token, required_scope=scope)
                # Add payload to request context for use in endpoint
                request.mfa_payload = payload
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'MFA token has expired'}), 401
            except (jwt.InvalidTokenError, ValueError) as e:
                return jsonify({'message': f'MFA token is invalid: {str(e)}'}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

