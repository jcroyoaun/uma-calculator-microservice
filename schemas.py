from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class VoucherAmount:
    amount: float
    transaction_date: Optional[date] = None

@dataclass
class LimitResponse:
    is_valid: bool
    current_amount: float
    limit: float
    remaining: float
    message: Optional[str] = None

@dataclass
class UMAResponse:
    daily_value: float
    monthly_value: float
    max_monthly_deposit: float
    max_annual_deposit: float
    annual_deposits_allowed: int
