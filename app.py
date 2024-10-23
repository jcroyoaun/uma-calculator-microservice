import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
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
    from routes import api
    app.register_blueprint(api, url_prefix='/api/v1')
    
    # Initialize docs after registering blueprints
    docs.init_app(app)
    
    # Register CLI commands
    from commands import update_uma_command
    app.cli.add_command(update_uma_command)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Register API documentation after all routes are set up
        from routes import register_api_documentation
        register_api_documentation(docs)
    
    return app

app = create_app()
