import os
from flask import Flask, render_template, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime # 日付クラス
import pytz # タイムゾーンパッケージ
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Migrate(app, db)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')))
    
    def __str__(self):
        return f'課題ID:{ self.id } 内容：{ self.content }'
    
PER_PAGE = 3

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Task.query.filter_by(is_completed=False).paginate(page=page, per_page=PER_PAGE)
    uncompleted_tasks = pagination.items
    total_pages = pagination.pages
    completed_tasks = Task.query.filter_by(is_completed=True).all()
    editing_task_id = request.args.get('editing_task_id', type=int)
    return render_template('index.j2', uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks, total_pages=total_pages, page=page, editing_task_id=editing_task_id)

@app.route('/new', methods=['POST'])
def new_task():
    content = request.form['content']
    task = Task(content=content)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search_task():
    search = request.form['search']
    page = request.args.get('page', 1, type=int)
    pagination = Task.query.filter(Task.content.like(f'%{search}%')).filter_by(is_completed=False).paginate(page=page, per_page=PER_PAGE)
    uncompleted_tasks = pagination.items
    total_pages = pagination.pages
    completed_tasks = Task.query.filter(Task.content.like(f'%{search}%')).filter_by(is_completed=True).all()
    return render_template('index.j2', search=search, uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks, total_pages=total_pages, page=page)

@app.route('/tasks/<int:task_id>/edit', methods=['POST'])
def edit_task(task_id):
    return redirect(url_for('index', editing_task_id=task_id))

@app.route('/tasks/edit_cancel', methods=['POST'])
def edit_cancel():
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.content = request.form['update']
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    if request.method == 'POST':
        task = Task.query.get_or_404(task_id)
        task.is_completed = True
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/uncomplete', methods=['POST'])
def uncomplete_task(task_id):
    if request.method == 'POST':
        task = Task.query.get_or_404(task_id)
        task.is_completed = False
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/tasks/all_complete', methods=['POST'])
def all_complete():
    Task.query.update({Task.is_completed: True})
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/all_uncomplete', methods=['POST'])
def all_uncomplete():
    Task.query.update({Task.is_completed: False})
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/all_complete', methods=['POST'])
def all_complete_task():
    Task.query.update({Task.is_completed: True})
    db.session.commit()
    return redirect(url_for('index'))
    
@app.route('/tasks/remove_checks', methods=['POST'])
def remove_checks():
    if request.method == 'POST':
        del_checks = request.form.getlist('del_checks')
        if not del_checks:
            return redirect(url_for('index'))
        for check_id in del_checks:
            task = Task.query.get(int(check_id))
            if task:
                db.session.delete(task)
        db.session.commit()
        return redirect(url_for("index"))

@app.route('/tasks/<int:task_id>/remove', methods=['POST'])
def remove_task(task_id):
    if request.method == 'POST':
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('index'))
    
@app.route('/tasks/clear', methods=['POST'])
def clear_tasks():
    Task.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/sort')
def sort():
    if 'sort' in session:
        sort = session['sort']
    elif request.args.get('sort'):     
        sort = request.args.get('sort', 'desc')
    else:
        sort = 'desc'
    page = request.args.get('page', 1, type=int)
    order = Task.created_at.desc() if sort == 'desc' else Task.created_at.asc()
    pagination = Task.query.filter_by(is_completed=False).order_by(order).paginate(page=page, per_page=PER_PAGE)
    uncompleted_tasks = pagination.items
    total_pages = pagination.pages
    completed_tasks = Task.query.filter_by(is_completed=True).order_by(order).all()
    return render_template('index.j2', uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks, total_pages=total_pages, page=page)

if __name__ == '__main__':
    app.run(debug=True)