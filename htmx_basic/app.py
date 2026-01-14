from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.j2')

@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name', 'World')
    return f'<p>Hello, {name}!</p>'

if __name__ == '__main__':
    app.run(debug=True)