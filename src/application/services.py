from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict

from src.domain.exceptions import InvalidAmountError, LimitExceededError
from src.domain.models import VoucherLimits

class VoucherService:
    def __init__(self, uma_repository, transaction_repository):
        self.uma_repository = uma_repository
        self.transaction_repository = transaction_repository

    def validate_amount(self, amount: Decimal) -> None:
        """Validate if amount is positive"""
        if amount <= 0:
            raise InvalidAmountError("Invalid amount")

    def check_monthly_limit(self, amount: Decimal) -> None:
        """Check if amount exceeds monthly UMA limit"""
        current_uma = self.uma_repository.get_current_value()
        limits = VoucherLimits(current_uma.daily_value)
        
        if amount > limits.monthly_uma:
            raise LimitExceededError(
                f"Amount exceeds monthly UMA limit of {limits.monthly_uma:.2f} MXN"
            )

    def get_annual_remaining(self, year: Optional[int] = None) -> Decimal:
        """Calculate remaining annual limit"""
        year = year or datetime.now().year
        current_uma = self.uma_repository.get_current_value()
        limits = VoucherLimits(current_uma.daily_value)
        
        used = self.transaction_repository.get_annual_total(year)
        return limits.max_annual_amount - used

    def validate_voucher(self, amount: Decimal) -> Dict:
        """Validate if voucher amount is within limits"""
        try:
            self.validate_amount(amount)
            self.check_monthly_limit(amount)
            
            remaining = self.get_annual_remaining()
            current_uma = self.uma_repository.get_current_value()
            limits = VoucherLimits(current_uma.daily_value)
            
            if amount > remaining:
                raise LimitExceededError(
                    f"Amount would exceed annual UMA limit of {limits.max_annual_amount:.2f} MXN"
                )

            return {
                'is_valid': True,
                'current_amount': amount,
                'limit': limits.max_annual_amount,
                'remaining': remaining
            }

        except LimitExceededError as e:
            current_uma = self.uma_repository.get_current_value()
            limits = VoucherLimits(current_uma.daily_value)
            return {
                'is_valid': False,
                'current_amount': amount,
                'limit': limits.max_annual_amount,
                'remaining': self.get_annual_remaining(),
                'message': str(e)
            }
