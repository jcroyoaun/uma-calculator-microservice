import click
from flask.cli import with_appcontext
from inegi_service import INEGIService

@click.command('update-uma')
@with_appcontext
def update_uma_command():
    """Update UMA value from INEGI"""
    service = INEGIService()
    result = service.update_uma_value()
    if result:
        click.echo(f"Successfully updated UMA value to {result.daily_value}")
    else:
        click.echo("Failed to update UMA value")
