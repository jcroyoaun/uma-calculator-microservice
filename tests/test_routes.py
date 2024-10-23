import pytest
from flask import json
from datetime import datetime

from app import create_app, db
from models import UMAValue, VoucherTransaction
from constants import DAILY_UMA, MONTHLY_UMA, MAX_ANNUAL_AMOUNT

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for the application."""
    return app.test_client()

def test_get_uma_values(client):
    """Test getting UMA values endpoint"""
    response = client.get('/api/v1/uma')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['daily_value'] == DAILY_UMA
    assert data['monthly_value'] == MONTHLY_UMA
    assert data['max_annual_deposit'] == MAX_ANNUAL_AMOUNT

def test_validate_voucher_valid(client):
    """Test voucher validation with valid amount"""
    response = client.post('/api/v1/vouchers/validate',
                         json={'amount': 1000.0})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['is_valid'] is True
    assert data['current_amount'] == 1000.0

def test_validate_voucher_invalid_amount(client):
    """Test voucher validation with invalid amount"""
    response = client.post('/api/v1/vouchers/validate',
                         json={'amount': -100.0})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['is_valid'] is False
    assert 'Invalid amount' in data['message']

def test_validate_voucher_exceeds_monthly(client):
    """Test voucher validation with amount exceeding monthly limit"""
    response = client.post('/api/v1/vouchers/validate',
                         json={'amount': MONTHLY_UMA + 100})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['is_valid'] is False
    assert 'exceeds monthly UMA limit' in data['message']

def test_get_remaining_limit(client):
    """Test getting remaining limit"""
    current_year = datetime.now().year
    response = client.get(f'/api/v1/vouchers/remaining?year={current_year}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['year'] == current_year
    assert data['annual_limit'] == MAX_ANNUAL_AMOUNT
    assert 'remaining_limit' in data

def test_get_remaining_limit_with_transactions(client, app):
    """Test getting remaining limit with existing transactions"""
    with app.app_context():
        transaction = VoucherTransaction(
            amount=1000.0,
            transaction_date=datetime.now().date()
        )
        db.session.add(transaction)
        db.session.commit()

    current_year = datetime.now().year
    response = client.get(f'/api/v1/vouchers/remaining?year={current_year}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['remaining_limit'] == MAX_ANNUAL_AMOUNT - 1000.0
