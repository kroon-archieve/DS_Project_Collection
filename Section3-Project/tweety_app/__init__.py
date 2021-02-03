import os
from flask import Flask
from tweety_app.routes import basic_routes, func_routes
from tweety_app.models import db, migrate
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URI = os.getenv('DB_URI')
# DATABASE_URI = os.getenv('HEROKU_DB_URI')
DATABASE_URI = "sqlite:///tweety.sqlite3"

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes=False

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(basic_routes.basic_routes)
    app.register_blueprint(func_routes.func_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
