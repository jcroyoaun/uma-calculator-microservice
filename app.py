import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True
    }
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes import api
    app.register_blueprint(api, url_prefix='/api/v1')
    
    # Register CLI commands
    from commands import update_uma_command
    app.cli.add_command(update_uma_command)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()
