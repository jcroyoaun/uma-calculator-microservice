from datetime import datetime
from decimal import Decimal
from flask import request, jsonify
from flask_apispec import use_kwargs, marshal_with, doc

from src.interfaces.api import api
from src.interfaces.api.schemas import (
    UMAResponseSchema, 
    VoucherAmountSchema, 
    LimitResponseSchema,
    RemainingLimitSchema
)
from src.domain.exceptions import VoucherError
from src.application.services import VoucherService
from src.infrastructure.repositories.uma_repository import UMARepository
from src.infrastructure.repositories.transaction_repository import TransactionRepository

# Initialize repositories and services
uma_repository = UMARepository()
transaction_repository = TransactionRepository()
voucher_service = VoucherService(uma_repository, transaction_repository)

@api.route('/uma', methods=['GET'])
@doc(
    tags=['UMA Values'],
    description='Get current UMA values and deposit limits'
)
@marshal_with(UMAResponseSchema)
def get_uma_values():
    """Get current UMA values and limits"""
    current_uma = uma_repository.get_current_value()
    if not current_uma:
        return jsonify({'error': 'No UMA value found'}), 404
        
    limits = VoucherLimits(current_uma.daily_value)
    return {
        'daily_value': float(current_uma.daily_value),
        'monthly_value': float(limits.monthly_uma),
        'max_monthly_deposit': float(limits.monthly_uma),
        'max_annual_deposit': float(limits.max_annual_amount),
        'annual_deposits_allowed': limits.annual_max_deposits
    }

@api.route('/vouchers/validate', methods=['POST'])
@doc(
    tags=['Vouchers'],
    description='Validate if voucher amount is within allowed limits'
)
@use_kwargs(VoucherAmountSchema)
@marshal_with(LimitResponseSchema)
def validate_voucher(**kwargs):
    """Validate if voucher amount is within limits"""
    try:
        amount = Decimal(str(kwargs.get('amount', 0)))
        response = voucher_service.validate_voucher(amount)
        if not response['is_valid']:
            return response, 400
        return response
    except (TypeError, ValueError) as e:
        return {
            'is_valid': False,
            'current_amount': kwargs.get('amount', 0),
            'limit': float(limits.max_annual_amount),
            'remaining': float(voucher_service.get_annual_remaining()),
            'message': str(e) or 'Invalid amount format'
        }, 400
    except VoucherError as e:
        return {
            'is_valid': False,
            'current_amount': kwargs.get('amount', 0),
            'limit': float(limits.max_annual_amount),
            'remaining': float(voucher_service.get_annual_remaining()),
            'message': str(e)
        }, 400

@api.route('/vouchers/remaining', methods=['GET'])
@doc(
    tags=['Vouchers'],
    description='Get remaining annual voucher limit'
)
@marshal_with(RemainingLimitSchema)
def get_remaining_limit():
    """Get remaining annual voucher limit"""
    year = request.args.get('year', datetime.now().year, type=int)
    current_uma = uma_repository.get_current_value()
    limits = VoucherLimits(current_uma.daily_value)
    remaining = voucher_service.get_annual_remaining(year)
    
    return {
        'year': year,
        'remaining_limit': float(remaining),
        'annual_limit': float(limits.max_annual_amount)
    }

def register_api_documentation(docs):
    """Register API documentation after app initialization"""
    docs.register(get_uma_values, blueprint='api')
    docs.register(validate_voucher, blueprint='api')
    docs.register(get_remaining_limit, blueprint='api')
