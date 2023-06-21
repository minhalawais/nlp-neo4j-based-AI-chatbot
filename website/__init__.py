from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db=SQLAlchemy()
DB_NAME = "users.db"

def creat_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "adsfjwuenvcjWEOPoiajfjsndsiuhwe"
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    



    return app

