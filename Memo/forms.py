from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, HiddenField, FileField, BooleanField, RadioField
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Optional
from models import Memo, User

class MemoForm(FlaskForm):
    id = HiddenField()
    title = StringField(
        "タイトル：",
        validators=[
            DataRequired("タイトルは必須入力です"),
            Length(max=30, message="30文字以下で入力してください"),
        ],
    )
    content = TextAreaField("",
        validators=[
            DataRequired("説明は必須入力です"),
        ],
    )
    image = FileField(
        "",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "gif"], "画像ファイルのみアップロードできます")
        ]
    )
    submit = SubmitField("投稿")

    def validate_title(self, title):
        query = Memo.query.filter_by(title=title.data, user_id=current_user.id)
        # 編集時のみ：自分自身を除外
        if self.id.data:
            query = query.filter(Memo.id != self.id.data)
        memo = query.first()
        if memo:
            raise ValidationError(f"タイトル「{title.data}」は既に存在します。別のタイトルを入力してください。")

class LoginForm(FlaskForm):
    username = StringField('ユーザ名：', validators=[DataRequired('ユーザ名は必須入力です。')])
    password = PasswordField('パスワード：', validators=[Length(8, 12, 'パスワードの長さは8文字以上12文字以内です')])
    remember = BooleanField('ログイン状態を1週間保持し自動でマイページに移動する')
    submit = SubmitField('ログイン')
	# カスタムバリデータとして英数記号が含まれていなければraiseで例外を明示的に発生させる
    def validate_password(self, password):
        if not (any(c.isalpha() for c in password.data) and \
        any(c.isdigit() for c in password.data) and \
        any(c in '!@#$%^&*()' for c in password.data)):
            raise ValidationError('パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります。')

class SignUpForm(LoginForm): # ログイン処理と同じなため機能を継承
	submit = SubmitField('登録') # ボタンラベルをオーバーライド
	# ユーザ名の重複判定のみ追加
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('そのユーザ名はすでに使用されれています')

class EditUserForm(FlaskForm):
    # ユーザ名更新
    username = StringField('ユーザー名', validators=[DataRequired()])
    # パスワード更新
    change_password = BooleanField('パスワードを変更する')
    password = PasswordField('新しいパスワード')
    confirm_password = PasswordField('パスワード確認再入力',
        validators=[
            Optional(),
            EqualTo('password', message='パスワードが一致しません')
    ])
    # 画像更新
    thumbnail = FileField('サムネイル画像（任意）')
    submit = SubmitField('更新')
    preset_thumbnail = RadioField(
        '既存画像',
        choices=[(f'{i:02}.png', f'{i:02}.png') for i in range(1, 11)]
    )
    submit = SubmitField('更新')
