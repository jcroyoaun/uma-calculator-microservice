from datetime import datetime
from decimal import Decimal
from typing import Optional

class UMAValue:
    """Value object representing UMA values"""
    def __init__(self, daily_value: Decimal, valid_from: datetime):
        self.daily_value = daily_value
        self.valid_from = valid_from
        self.created_at = datetime.utcnow()

class VoucherTransaction:
    """Value object representing voucher transactions"""
    def __init__(self, amount: Decimal, transaction_date: datetime):
        self.amount = amount
        self.transaction_date = transaction_date
        self.created_at = datetime.utcnow()

class VoucherLimits:
    """Value object for voucher limits calculation"""
    def __init__(self, daily_uma: Decimal):
        self.daily_uma = daily_uma
        self.monthly_uma = daily_uma * Decimal('30.4')
        self.annual_max_deposits = 7
        self.max_monthly_amount = self.monthly_uma
        self.max_annual_amount = self.monthly_uma * Decimal(str(self.annual_max_deposits))
