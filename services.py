from datetime import datetime
from decimal import Decimal
from typing import Optional

from constants import MONTHLY_UMA, MAX_ANNUAL_AMOUNT, ERRORS
from exceptions import VoucherError, LimitExceededError, InvalidAmountError
from models import VoucherTransaction

class VoucherService:
    @staticmethod
    def validate_amount(amount: float) -> None:
        """Validate if amount is positive"""
        if amount <= 0:
            raise InvalidAmountError(ERRORS['INVALID_AMOUNT'])

    @staticmethod
    def check_monthly_limit(amount: float) -> None:
        """Check if amount exceeds monthly UMA limit"""
        if amount > MONTHLY_UMA:
            raise LimitExceededError(
                ERRORS['EXCEED_MONTHLY'].format(MONTHLY_UMA)
            )

    @staticmethod
    def get_annual_remaining(year: Optional[int] = None) -> float:
        """Calculate remaining annual limit"""
        year = year or datetime.now().year
        used = VoucherTransaction.get_annual_total(year)
        return float(Decimal(str(MAX_ANNUAL_AMOUNT)) - Decimal(str(used)))

    def validate_voucher(self, amount: float) -> dict:
        """Validate if voucher amount is within limits"""
        try:
            self.validate_amount(amount)
            self.check_monthly_limit(amount)
            
            remaining = self.get_annual_remaining()
            if amount > remaining:
                raise LimitExceededError(
                    ERRORS['EXCEED_ANNUAL'].format(MAX_ANNUAL_AMOUNT)
                )

            return {
                'is_valid': True,
                'current_amount': amount,
                'limit': MAX_ANNUAL_AMOUNT,
                'remaining': remaining
            }

        except VoucherError as e:
            return {
                'is_valid': False,
                'current_amount': amount,
                'limit': MAX_ANNUAL_AMOUNT,
                'remaining': self.get_annual_remaining(),
                'message': str(e)
            }
