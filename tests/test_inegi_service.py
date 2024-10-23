import pytest
from datetime import datetime
import requests
from unittest.mock import Mock

from inegi_service import INEGIService
from models import UMAValue
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
def inegi_service():
    return INEGIService()

def test_format_date(inegi_service):
    """Test date formatting from INEGI API response"""
    # Test YYYY/MM format
    date = inegi_service._format_date("2024/01")
    assert isinstance(date, datetime)
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 1

    # Test YYYY-MM-DD format
    date = inegi_service._format_date("2024-01-01")
    assert isinstance(date, datetime)
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 1

def test_get_latest_value_success(inegi_service, mocker):
    """Test successful API response parsing"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Series": [{
            "OBSERVATIONS": [{
                "TIME_PERIOD": "2024/01",
                "OBS_VALUE": "136.00"
            }]
        }]
    }
    
    mocker.patch.object(requests.Session, 'get', return_value=mock_response)
    result = inegi_service._get_latest_value()
    
    assert result is not None
    value, date = result
    assert value == 136.00
    assert isinstance(date, datetime)
    assert date.year == 2024
    assert date.month == 1

def test_get_latest_value_api_error(inegi_service, mocker):
    """Test handling of API errors"""
    mocker.patch.object(requests.Session, 'get', side_effect=requests.RequestException)
    result = inegi_service._get_latest_value()
    assert result is None

def test_update_uma_value_success(inegi_service, mocker, app):
    """Test successful UMA value update"""
    mock_value_data = (136.00, datetime(2024, 1, 1))
    mocker.patch.object(INEGIService, '_get_latest_value', return_value=mock_value_data)
    
    with app.app_context():
        result = inegi_service.update_uma_value()
        assert isinstance(result, UMAValue)
        assert float(result.daily_value) == 136.00
        assert result.valid_from == datetime(2024, 1, 1).date()

def test_update_uma_value_duplicate(inegi_service, mocker, app):
    """Test handling of duplicate UMA values"""
    mock_value_data = (136.00, datetime(2024, 1, 1))
    mocker.patch.object(INEGIService, '_get_latest_value', return_value=mock_value_data)
    
    with app.app_context():
        # First update
        first_result = inegi_service.update_uma_value()
        assert isinstance(first_result, UMAValue)
        
        # Second update with same value
        second_result = inegi_service.update_uma_value()
        assert second_result == first_result  # Should return existing record

def test_update_uma_value_api_error(inegi_service, mocker):
    """Test handling of API errors during update"""
    mocker.patch.object(INEGIService, '_get_latest_value', return_value=None)
    result = inegi_service.update_uma_value()
    assert result is None
