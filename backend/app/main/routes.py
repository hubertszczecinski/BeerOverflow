from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
import requests
import jwt
from flask import current_app
from app.main import bp
from app.models import User
from app.services.risk import evaluate_transaction
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

    # Evaluate fraud/risk for senior users (or all users if desired)
    try:
        tx_payload = dict(tx_data)
        tx_payload['user_id'] = tx_payload.get('user_id') or current_user.id
        risk = evaluate_transaction(tx_payload)
    except Exception as e:
        risk = {'error': f'risk_evaluation_failed: {e}'}

    print(f"Processing transaction {tx_data.get('id')} for user {current_user.id}")

    return jsonify({
        'message': 'Transaction accepted for processing',
        'transactionId': tx_data.get('id'),
        'status': 'PROCESSING',
        'risk': risk
    }), 200


@bp.route('/api/submit-transaction', methods=['POST'])
@login_required
def submit_transaction_api_alias():
    return submit_transaction()
