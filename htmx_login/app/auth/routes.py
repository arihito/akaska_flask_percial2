from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('todo.index'))
    return render_template('login.j2')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))