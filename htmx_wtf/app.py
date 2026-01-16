from flask import Flask, render_template, request
from forms import NameForm

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if request.method == 'POST':
        form.validate()
        if not form.errors:
            return f'<div id="form-area"><p>こんにちは {form.name.data}さん</p></div>'
    return render_template('_form.j2', form=form)