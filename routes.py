from flask import Blueprint, jsonify, request
from datetime import datetime

from constants import DAILY_UMA, MONTHLY_UMA, MAX_ANNUAL_AMOUNT, ANNUAL_MAX_DEPOSITS
from exceptions import VoucherError
from schemas import UMAResponse
from services import VoucherService

api = Blueprint('api', __name__)
voucher_service = VoucherService()

@api.route('/uma', methods=['GET'])
def get_uma_values():
    """Get current UMA values and limits"""
    response = UMAResponse(
        daily_value=DAILY_UMA,
        monthly_value=MONTHLY_UMA,
        max_monthly_deposit=MONTHLY_UMA,
        max_annual_deposit=MAX_ANNUAL_AMOUNT,
        annual_deposits_allowed=ANNUAL_MAX_DEPOSITS
    )
    return jsonify(response.__dict__)

@api.route('/vouchers/validate', methods=['POST'])
def validate_voucher():
    """Validate if voucher amount is within limits"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        response = voucher_service.validate_voucher(amount)
        return jsonify(response.__dict__)
    except (TypeError, ValueError):
        return jsonify({
            'error': 'Invalid amount format'
        }), 400
    except VoucherError as e:
        return jsonify({'error': str(e)}), e.code

@api.route('/vouchers/remaining', methods=['GET'])
def get_remaining_limit():
    """Get remaining annual voucher limit"""
    year = request.args.get('year', datetime.now().year, type=int)
    remaining = voucher_service.get_annual_remaining(year)
    return jsonify({
        'year': year,
        'remaining_limit': remaining,
        'annual_limit': MAX_ANNUAL_AMOUNT
    })
