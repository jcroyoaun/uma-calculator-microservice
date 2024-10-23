from datetime import datetime
from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP

def round_amount(amount: Union[int, float, Decimal], decimals: int = 2) -> float:
    """Round amount to specified decimals"""
    if not isinstance(amount, (int, float, Decimal)):
        raise ValueError("Amount must be a number")
    return float(
        Decimal(str(amount)).quantize(
            Decimal(f'0.{"0" * decimals}'),
            rounding=ROUND_HALF_UP
        )
    )

def get_current_year() -> int:
    """Get current year"""
    return datetime.now().year

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None
