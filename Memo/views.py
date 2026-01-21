from flask import render_template
from app import app
from werkzeug.exceptions import NotFound

@app.errorhandler(NotFound)
def show_404_page(error):
    msg = error.description
    print('エラー内容:', msg)
    return render_template('errors/404.j2', msg=msg), 404
