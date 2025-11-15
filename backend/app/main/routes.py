from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
import requests
from flask import current_app
from app.main import bp
from app.models import User, Account, AccountType, TransactionEvent
from app.services.risk import evaluate_transaction
from app.models import db
from app.auth.mfa_utils import require_mfa_token
from datetime import datetime
import random
import string


def generate_account_number():
    """Generate a random unique account number"""
    while True:
        # Generate a 16-digit account number
        account_number = ''.join(random.choices(string.digits, k=16))
        # Check if it already exists
        if not Account.query.filter_by(account_number=account_number).first():
            return account_number


@bp.route('/submit-transaction', methods=['POST'])
@login_required
@require_mfa_token()
def submit_transaction():
    """
    API endpoint to submit a single transaction.
    Requires a valid MFA token in the Authorization header.
    """
    # Get the transaction data from the client
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


# ==================== ACCOUNT MANAGEMENT ENDPOINTS ====================

@bp.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get all accounts for the current user"""
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'accounts': [account.to_dict() for account in accounts]
    }), 200


@bp.route('/accounts/<int:account_id>', methods=['GET'])
@login_required
def get_account(account_id):
    """Get a specific account for the current user"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    return jsonify({'account': account.to_dict()}), 200


@bp.route('/accounts', methods=['POST'])
@login_required
@require_mfa_token()
def create_account():
    """
    Create a new account for the current user.
    Requires MFA authentication.

    Request body:
    {
        "account_type": "checking" | "savings" | "business" | "investment",
        "currency": "USD" (optional, defaults to USD),
        "initial_balance": 0.00 (optional, defaults to 0)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validate account type
    account_type_str = data.get('account_type', '').lower()
    try:
        account_type = AccountType(account_type_str)
    except ValueError:
        valid_types = [t.value for t in AccountType]
        return jsonify({
            'message': f'Invalid account type. Must be one of: {", ".join(valid_types)}'
        }), 400

    # Generate unique account number
    account_number = generate_account_number()

    # Get optional parameters
    currency = data.get('currency', 'USD').upper()
    initial_balance = data.get('initial_balance', 0.00)

    # Validate currency (simple validation)
    if len(currency) != 3 or not currency.isalpha():
        return jsonify({'message': 'Invalid currency code. Must be 3-letter code (e.g., USD, EUR)'}), 400

    # Validate initial balance
    try:
        initial_balance = float(initial_balance)
        if initial_balance < 0:
            return jsonify({'message': 'Initial balance cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid initial balance'}), 400

    # Create the account
    account = Account(
        user_id=current_user.id,
        account_type=account_type,
        account_number=account_number,
        balance=initial_balance,
        currency=currency
    )

    try:
        db.session.add(account)
        db.session.commit()

        return jsonify({
            'message': 'Account created successfully',
            'account': account.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create account: {str(e)}'}), 500


@bp.route('/accounts/<int:account_id>', methods=['PUT'])
@login_required
@require_mfa_token()
def update_account(account_id):
    """
    Update account status (activate/deactivate).
    Requires MFA authentication.

    Request body:
    {
        "is_active": true/false
    }
    """
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    if 'is_active' in data:
        account.is_active = bool(data['is_active'])

    try:
        db.session.commit()
        return jsonify({
            'message': 'Account updated successfully',
            'account': account.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to update account: {str(e)}'}), 500


@bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@login_required
@require_mfa_token()
def delete_account(account_id):
    """
    Delete an account (only if balance is 0).
    Requires MFA authentication.
    """
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    # Check if account has zero balance
    if account.balance != 0:
        return jsonify({
            'message': 'Cannot delete account with non-zero balance. Please withdraw or transfer all funds first.'
        }), 400

    try:
        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to delete account: {str(e)}'}), 500


# ==================== PENDING TRANSACTION ENDPOINTS ====================

@bp.route('/accounts/<int:account_id>/transactions', methods=['POST'])
@login_required
@require_mfa_token()
def create_pending_transaction(account_id):
    """
    Create a pending transaction for an account.
    Requires MFA authentication.

    Request body:
    {
        "amount": 100.00,
        "transaction_type": "debit" | "credit",
        "description": "Payment description",
        "channel": "web" (optional, defaults to "web"),
        "recipient_id": "recipient_account" (optional),
        "location": "City, Country" (optional)
    }
    """
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    if not account.is_active:
        return jsonify({'message': 'Account is not active'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validate required fields
    amount = data.get('amount')
    transaction_type = data.get('transaction_type', '').lower()
    description = data.get('description', '')
    channel = data.get('channel', 'web')
    recipient_id = data.get('recipient_id')
    location = data.get('location')

    if not amount:
        return jsonify({'message': 'Amount is required'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'message': 'Amount must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid amount'}), 400

    if transaction_type not in ['debit', 'credit']:
        return jsonify({'message': 'Transaction type must be either "debit" or "credit"'}), 400

    # Check if account has sufficient balance for debit transactions
    if transaction_type == 'debit' and account.balance < amount:
        return jsonify({'message': 'Insufficient balance'}), 400

    # Create pending transaction using TransactionEvent
    pending_tx = TransactionEvent(
        account_id=account.id,
        user_id=current_user.id,
        amount=amount,
        currency=account.currency,
        timestamp=datetime.utcnow(),
        type=transaction_type,
        channel=channel,
        recipient_id=recipient_id,
        location=location,
        description=description,
        status='PENDING',
        balance_before=float(account.balance)
    )

    try:
        db.session.add(pending_tx)
        db.session.commit()

        return jsonify({
            'message': 'Transaction created and queued for processing',
            'transaction': pending_tx.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Failed to create transaction: {str(e)}'}), 500


@bp.route('/accounts/<int:account_id>/transactions', methods=['GET'])
@login_required
def get_pending_transactions(account_id):
    """Get all pending transactions for an account"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    transactions = TransactionEvent.query.filter_by(account_id=account.id).order_by(
        TransactionEvent.created_at.desc()
    ).all()

    return jsonify({
        'transactions': [tx.to_dict() for tx in transactions]
    }), 200


@bp.route('/process-pending-transactions', methods=['POST'])
@login_required
@require_mfa_token()
def process_pending_transactions():
    """
    Process all pending transactions and update account balances.
    This can be called manually or scheduled as a periodic task.
    Requires MFA authentication.
    """
    # Get all pending transactions
    pending_txs = TransactionEvent.query.filter_by(status='PENDING').all()

    processed_count = 0
    failed_count = 0
    results = []

    for tx in pending_txs:
        try:
            # Update status to processing
            tx.status = 'PROCESSING'
            db.session.commit()

            # Get the account
            account = Account.query.get(tx.account_id)
            if not account:
                tx.status = 'FAILED'
                tx.processed_at = datetime.utcnow()
                results.append({
                    'transaction_id': tx.id,
                    'status': 'FAILED',
                    'reason': 'Account not found'
                })
                failed_count += 1
                db.session.commit()
                continue

            # Process the transaction based on type
            if tx.type == 'debit':
                if account.balance >= tx.amount:
                    account.balance -= tx.amount
                else:
                    tx.status = 'FAILED'
                    tx.processed_at = datetime.utcnow()
                    results.append({
                        'transaction_id': tx.id,
                        'status': 'FAILED',
                        'reason': 'Insufficient balance'
                    })
                    failed_count += 1
                    db.session.commit()
                    continue
            elif tx.type == 'credit':
                account.balance += tx.amount
            else:
                # Unknown transaction type, fail it
                tx.status = 'FAILED'
                tx.processed_at = datetime.utcnow()
                results.append({
                    'transaction_id': tx.id,
                    'status': 'FAILED',
                    'reason': f'Unknown transaction type: {tx.type}'
                })
                failed_count += 1
                db.session.commit()
                continue

            # Update balance_after
            tx.balance_after = float(account.balance)

            # Mark as completed
            tx.status = 'COMPLETED'
            tx.processed_at = datetime.utcnow()
            account.updated_at = datetime.utcnow()

            db.session.commit()
            processed_count += 1
            results.append({
                'transaction_id': tx.id,
                'status': 'COMPLETED',
                'new_balance': float(account.balance)
            })

        except Exception as e:
            db.session.rollback()
            tx.status = 'FAILED'
            tx.processed_at = datetime.utcnow()
            db.session.commit()
            failed_count += 1
            results.append({
                'transaction_id': tx.id,
                'status': 'FAILED',
                'reason': str(e)
            })

    return jsonify({
        'message': 'Transaction processing completed',
        'processed': processed_count,
        'failed': failed_count,
        'results': results
    }), 200


@bp.route('/auto-process-transactions', methods=['POST'])
def auto_process_transactions():
    """
    Auto-process pending transactions without authentication.
    This endpoint can be called by a cron job or scheduled task.
    In production, this should be protected by IP whitelist or internal network only.
    """
    # Get all pending transactions older than 5 seconds
    import datetime as dt
    cutoff_time = dt.datetime.utcnow() - dt.timedelta(seconds=5)
    pending_txs = TransactionEvent.query.filter(
        TransactionEvent.status == 'PENDING',
        TransactionEvent.created_at <= cutoff_time
    ).all()

    processed_count = 0
    failed_count = 0

    for tx in pending_txs:
        try:
            tx.status = 'PROCESSING'
            db.session.commit()

            account = Account.query.get(tx.account_id)
            if not account:
                tx.status = 'FAILED'
                tx.processed_at = datetime.utcnow()
                failed_count += 1
                db.session.commit()
                continue

            # Process the transaction based on type
            if tx.type == 'debit':
                if account.balance >= tx.amount:
                    account.balance -= tx.amount
                else:
                    tx.status = 'FAILED'
                    tx.processed_at = datetime.utcnow()
                    failed_count += 1
                    db.session.commit()
                    continue
            elif tx.type == 'credit':
                account.balance += tx.amount
            else:
                # Unknown transaction type
                tx.status = 'FAILED'
                tx.processed_at = datetime.utcnow()
                failed_count += 1
                db.session.commit()
                continue

            # Update balance_after
            tx.balance_after = float(account.balance)

            tx.status = 'COMPLETED'
            tx.processed_at = datetime.utcnow()
            account.updated_at = datetime.utcnow()

            db.session.commit()
            processed_count += 1

        except Exception as e:
            db.session.rollback()
            tx.status = 'FAILED'
            tx.processed_at = datetime.utcnow()
            db.session.commit()
            failed_count += 1

    return jsonify({
        'message': 'Auto-processing completed',
        'processed': processed_count,
        'failed': failed_count
    }), 200

