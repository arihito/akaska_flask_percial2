from flask import Flask
from .extensions import db, login_manager
from .models import User
from .auth.routes import auth_bp
from .todo.routes import todo_bp

def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY='secret',
        SQLALCHEMY_DATABASE_URI='sqlite:///app.db'
    )

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(todo_bp)

    return app