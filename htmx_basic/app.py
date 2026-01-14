from flask import Flask, render_template, request
app = Flask(__name__)

todos = []
next_id = 1

@app.route('/')
def index():
    return render_template('index.j2')

@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name', 'World')
    return f'<p>Hello, {name}!</p>'

@app.route('/todo')
def todo():
    return render_template('todo.j2', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    global next_id
    title = request.form['title']
    todo = {'id': next_id, 'title': title}
		# 追加した一覧を保持
    todos.append(todo)
    next_id += 1
    # 追加データのみを削除ページに渡す
    return render_template('_todo.j2', todo=todo)

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    global todos
    # 取得IDと等しくない要素だけをリストに再追加
    todos = [t for t in todos if t['id'] != todo_id]
    return ''

if __name__ == '__main__':
    app.run(debug=True)