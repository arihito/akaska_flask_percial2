import os 
from flask import Flask, render_template, redirect, request, url_for
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
    
@app.route('/')
def index():
    uncompleted_tasks = Task.query.filter_by(is_completed=False).all()
    completed_tasks = Task.query.filter_by(is_completed=True).all()
    return render_template('index.j2', uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks)

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
    uncompleted_tasks = Task.query.filter(Task.content.like(f'%{search}%')).filter_by(is_completed=False).all()
    completed_tasks = Task.query.filter(Task.content.like(f'%{search}%')).filter_by(is_completed=True).all()
    return render_template('index.j2', search=search, uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks)

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
    sort = request.args.get('sort', 'desc')
    order = Task.created_at.desc() if sort == 'desc' else Task.created_at.asc()
    uncompleted_tasks = Task.query.filter_by(is_completed=False).order_by(order).all()
    completed_tasks = Task.query.filter_by(is_completed=True).order_by(order).all()
    return render_template('index.j2', uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks)

if __name__ == '__main__':
    app.run(debug=True)