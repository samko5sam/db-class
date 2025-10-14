from flask import Flask
from flask_cors import CORS
from config import Config
from .extensions import db, bcrypt, jwt, migrate
from .routes import main

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    origins = [
        "*"
    ]

    # Enable CORS for React frontend
    CORS(
        app, 
        resources={r"/api/*": {"origins": origins}},
        allow_headers=["Authorization", "Content-Type"],
        supports_credentials=True
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprint
    app.register_blueprint(main, url_prefix='/api')

    return app