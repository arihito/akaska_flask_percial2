from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class NameForm(FlaskForm):
    name = StringField('名前', validators=[
        DataRequired(message='名前は必須です。'),
        Length(max=4, message='4文字以内で入力してください。')
    ], render_kw={'autofocus': True, 'maxlength': None})