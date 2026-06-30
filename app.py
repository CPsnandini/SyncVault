from flask import Flask
from config import Config
from extensions import db, jwt
from auth_routes import auth_bp
from file_routes import file_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)

    with app.app_context():
        db.create_all()
        import os
        os.makedirs(app.config["STORAGE_DIR"], exist_ok=True)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)