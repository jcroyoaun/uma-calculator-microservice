from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_apispec import use_kwargs, marshal_with, doc

from constants import DAILY_UMA, MONTHLY_UMA, MAX_ANNUAL_AMOUNT, ANNUAL_MAX_DEPOSITS
from exceptions import VoucherError
from schemas import (
    UMAResponseSchema, 
    VoucherAmountSchema, 
    LimitResponseSchema,
    RemainingLimitSchema
)
from services import VoucherService

api = Blueprint('api', __name__)
voucher_service = VoucherService()

@api.route('/uma', methods=['GET'])
@doc(
    tags=['UMA Values'],
    description='Get current UMA values and deposit limits'
)
@marshal_with(UMAResponseSchema)
def get_uma_values():
    """Get current UMA values and limits"""
    return {
        'daily_value': DAILY_UMA,
        'monthly_value': MONTHLY_UMA,
        'max_monthly_deposit': MONTHLY_UMA,
        'max_annual_deposit': MAX_ANNUAL_AMOUNT,
        'annual_deposits_allowed': ANNUAL_MAX_DEPOSITS
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
        amount = kwargs.get('amount', 0)
        response = voucher_service.validate_voucher(amount)
        return response
    except (TypeError, ValueError):
        return {
            'is_valid': False,
            'current_amount': 0,
            'limit': MAX_ANNUAL_AMOUNT,
            'remaining': MAX_ANNUAL_AMOUNT,
            'message': 'Invalid amount format'
        }, 400
    except VoucherError as e:
        return {
            'is_valid': False,
            'current_amount': amount,
            'limit': MAX_ANNUAL_AMOUNT,
            'remaining': voucher_service.get_annual_remaining(),
            'message': str(e)
        }, e.code

@api.route('/vouchers/remaining', methods=['GET'])
@doc(
    tags=['Vouchers'],
    description='Get remaining annual voucher limit'
)
@marshal_with(RemainingLimitSchema)
def get_remaining_limit():
    """Get remaining annual voucher limit"""
    year = request.args.get('year', datetime.now().year, type=int)
    remaining = voucher_service.get_annual_remaining(year)
    return {
        'year': year,
        'remaining_limit': remaining,
        'annual_limit': MAX_ANNUAL_AMOUNT
    }

def register_api_documentation(docs):
    """Register API documentation after app initialization"""
    docs.register(get_uma_values, blueprint='api')
    docs.register(validate_voucher, blueprint='api')
    docs.register(get_remaining_limit, blueprint='api')
