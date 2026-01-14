from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Todo

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/')
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('todo.j2', todos=todos)

@todo_bp.route('/add', methods=['POST'])
@login_required
def add():
    todo = Todo(
        title=request.form['title'],
        user_id=current_user.id
    )
    db.session.add(todo)
    db.session.commit()
    return render_template('_todo_item.j2', todo=todo)

@todo_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    Todo.query.filter_by(id=id, user_id=current_user.id).delete()
    db.session.commit()
    return ''