import pytest
from datetime import datetime
from decimal import Decimal

from utils import round_amount, get_current_year, parse_date

def test_round_amount_decimal():
    """Test rounding decimal numbers"""
    assert round_amount(10.256) == 10.26
    assert round_amount(10.254) == 10.25
    assert round_amount(10.0) == 10.00

def test_round_amount_integer():
    """Test rounding integer numbers"""
    assert round_amount(10) == 10.00
    assert round_amount(0) == 0.00

def test_round_amount_decimal_object():
    """Test rounding Decimal objects"""
    assert round_amount(Decimal('10.256')) == 10.26
    assert round_amount(Decimal('10.254')) == 10.25

def test_round_amount_invalid():
    """Test rounding invalid inputs"""
    with pytest.raises(ValueError):
        round_amount("10.25")
    with pytest.raises(ValueError):
        round_amount(None)

def test_get_current_year():
    """Test getting current year"""
    current_year = datetime.now().year
    assert get_current_year() == current_year

def test_parse_date_valid():
    """Test parsing valid date strings"""
    date = parse_date("2024-01-01")
    assert isinstance(date, datetime)
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 1

def test_parse_date_invalid():
    """Test parsing invalid date strings"""
    assert parse_date("invalid-date") is None
    assert parse_date("2024/01/01") is None
    assert parse_date("") is None
    assert parse_date(None) is None
