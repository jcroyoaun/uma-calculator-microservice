import os
from flask import Flask
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

from src.infrastructure.database import db
from src.interfaces.api import api
from src.interfaces.cli.commands import update_uma_command

docs = FlaskApiSpec()

def create_app():
    app = Flask(__name__)
    
    # Configure database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True
    }
    
    # Configure API documentation
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Food Voucher API',
            version='v1',
            plugins=[MarshmallowPlugin()],
            openapi_version='2.0',
            info={
                'description': 'API for calculating food voucher limits under ISR rules using current UMA values'
            }
        ),
        'APISPEC_SWAGGER_URL': '/swagger/',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
    })
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api/v1')
    
    # Initialize docs after registering blueprints
    docs.init_app(app)
    
    # Register CLI commands
    app.cli.add_command(update_uma_command)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Register API documentation
        from src.interfaces.api.routes import register_api_documentation
        register_api_documentation(docs)
    
    return app

app = create_app()
