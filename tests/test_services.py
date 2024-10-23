import pytest
from decimal import Decimal
from datetime import datetime

from services import VoucherService
from exceptions import InvalidAmountError, LimitExceededError
from constants import MONTHLY_UMA, MAX_ANNUAL_AMOUNT
from models import VoucherTransaction
from app import create_app, db

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
def voucher_service(app):
    with app.app_context():
        return VoucherService()

def test_validate_amount_positive(voucher_service):
    """Test that positive amounts are validated correctly"""
    voucher_service.validate_amount(100.0)  # Should not raise exception

def test_validate_amount_negative(voucher_service):
    """Test that negative amounts raise InvalidAmountError"""
    with pytest.raises(InvalidAmountError):
        voucher_service.validate_amount(-100.0)

def test_validate_amount_zero(voucher_service):
    """Test that zero amount raises InvalidAmountError"""
    with pytest.raises(InvalidAmountError):
        voucher_service.validate_amount(0)

def test_check_monthly_limit_within(voucher_service):
    """Test amount within monthly limit"""
    voucher_service.check_monthly_limit(MONTHLY_UMA - 100)  # Should not raise exception

def test_check_monthly_limit_exceeded(voucher_service):
    """Test amount exceeding monthly limit"""
    with pytest.raises(LimitExceededError):
        voucher_service.check_monthly_limit(MONTHLY_UMA + 100)

def test_get_annual_remaining_no_transactions(voucher_service, mocker):
    """Test remaining calculation with no transactions"""
    mocker.patch.object(VoucherTransaction, 'get_annual_total', return_value=0)
    remaining = voucher_service.get_annual_remaining(2024)
    assert remaining == MAX_ANNUAL_AMOUNT

def test_get_annual_remaining_with_transactions(voucher_service, mocker):
    """Test remaining calculation with existing transactions"""
    used_amount = 1000.0
    mocker.patch.object(VoucherTransaction, 'get_annual_total', return_value=used_amount)
    remaining = voucher_service.get_annual_remaining(2024)
    assert remaining == MAX_ANNUAL_AMOUNT - used_amount

def test_validate_voucher_valid_amount(voucher_service, mocker):
    """Test voucher validation with valid amount"""
    mocker.patch.object(VoucherTransaction, 'get_annual_total', return_value=0)
    result = voucher_service.validate_voucher(1000.0)
    assert result['is_valid'] is True
    assert result['current_amount'] == 1000.0
    assert result['limit'] == MAX_ANNUAL_AMOUNT
    assert result['remaining'] == MAX_ANNUAL_AMOUNT

def test_validate_voucher_exceeds_monthly(voucher_service):
    """Test voucher validation with amount exceeding monthly limit"""
    result = voucher_service.validate_voucher(MONTHLY_UMA + 100)
    assert result['is_valid'] is False
    assert 'exceeds monthly UMA limit' in result['message']

def test_validate_voucher_exceeds_annual(voucher_service, mocker):
    """Test voucher validation with amount exceeding annual limit"""
    mocker.patch.object(VoucherTransaction, 'get_annual_total', 
                       return_value=MAX_ANNUAL_AMOUNT - 100)
    result = voucher_service.validate_voucher(200.0)
    assert result['is_valid'] is False
    assert 'exceed annual UMA limit' in result['message']
