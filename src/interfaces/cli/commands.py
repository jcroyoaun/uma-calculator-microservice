import click
from flask.cli import with_appcontext

from src.infrastructure.services.inegi_service import INEGIService
from src.infrastructure.repositories.uma_repository import UMARepository

@click.command('update-uma')
@with_appcontext
def update_uma_command():
    """Update UMA value from INEGI"""
    uma_repository = UMARepository()
    service = INEGIService(uma_repository)
    result = service.update_uma_value()
    
    if result:
        click.echo(f"Successfully updated UMA value to {result.daily_value}")
    else:
        click.echo("Failed to update UMA value")
