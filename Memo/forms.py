from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from models import Memo, User, Favorite

class MemoForm(FlaskForm):
    title = StringField(
        "タイトル：",
        validators=[
            DataRequired("タイトルは必須入力です"),
            Length(max=10, message="10文字以下で入力してください"),
        ],
    )
    content = TextAreaField("内容：")
    submit = SubmitField("返信")

    def validate_title(self, title):
		# filter_byにオリジナルの判定条件を指定
        memo = Memo.query.filter_by(title=title.data).first()
        if memo:
            raise ValidationError(
                f"タイトル「{title.data}」は既に存在します。別のタイトルを入力してください。"
            )
            
class LoginForm(FlaskForm):
	username = StringField('ユーザ名：', validators=[DataRequired('ユーザ名は必須入力です。')])
	password = PasswordField('パスワード：', validators=[Length(4, 10, 'パスワードの長さは4文字以上10文字以内です')])
	submit = SubmitField('ログイン')
	# カスタムバリデータとして英数記号が含まれていなければraiseで例外を明示的に発生させる
	def validate_password(self, password):
		if not (any(c.isalpha() for c in password.data) and \
		any(c.isdigit() for c in password.data) and \
		any(c in '!@#$%^&*()' for c in password.data)):
			raise ValidationError('パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります。')

class SignUpForm(LoginForm): # ログイン処理と同じなため機能を継承
	submit = SubmitField('サインアップ') # ボタンラベルをオーバーライド
	# ユーザ名の重複判定のみ追加
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('そのユーザ名はすでに使用されれています')