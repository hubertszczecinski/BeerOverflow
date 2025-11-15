from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
import requests
import jwt
from flask import current_app
from app.main import bp
from app.models import User
from app.models import db

@bp.route('/submit-transaction', methods=['POST'])
@login_required
def submit_transaction():
    """
    API endpoint to submit a single transaction.
    Requires a valid MFA token in the Authorization header.
    """
    # 1. Get the MFA token from the header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'MFA token is missing or invalid'}), 401

    mfa_token = auth_header.split(' ')[1]

    # 2. Validate the MFA token
    try:
        payload = jwt.decode(
            mfa_token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
        # Check if token is for the correct user and scope
        if payload.get('sub') != current_user.id or payload.get('scope') != 'mfa_commit':
            raise jwt.InvalidTokenError
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({'message': 'MFA token is expired or invalid'}), 401

    # 3. Get the transaction data from the client
    tx_data = request.get_json()
    if not tx_data:
        return jsonify({'message': 'No transaction data provided'}), 400

    # --- TODO: Process the transaction ---
    # E.g., add it to a real processing queue, update balances, etc.
    # For the hackathon, we just "accept" it.
    print(f"Processing transaction {tx_data.get('id')} for user {current_user.id}")
    # ... your real processing logic ...

    # Return success
    return jsonify({
        'message': 'Transaction accepted for processing',
        'transactionId': tx_data.get('id'),
        'status': 'PROCESSING'
    }), 200