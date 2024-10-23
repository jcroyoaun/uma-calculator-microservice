import pytest
from unittest.mock import Mock
from click.testing import CliRunner
from datetime import datetime

from commands import update_uma_command
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
def cli_runner():
    return CliRunner()

def test_update_uma_command_success(cli_runner, mocker, app):
    """Test successful UMA value update command"""
    # Mock INEGIService.update_uma_value to return a successful result
    mock_value = UMAValue()
    mock_value.daily_value = 136.00
    mock_value.valid_from = datetime(2024, 1, 1).date()
    mocker.patch.object(INEGIService, 'update_uma_value', return_value=mock_value)

    with app.app_context():
        result = cli_runner.invoke(update_uma_command)
        assert result.exit_code == 0
        assert "Successfully updated UMA value to 136.00" in result.output

def test_update_uma_command_failure(cli_runner, mocker, app):
    """Test UMA value update command failure"""
    # Mock INEGIService.update_uma_value to return None (failure)
    mocker.patch.object(INEGIService, 'update_uma_value', return_value=None)

    with app.app_context():
        result = cli_runner.invoke(update_uma_command)
        assert result.exit_code == 0  # Commands should not fail the application
        assert "Failed to update UMA value" in result.output
