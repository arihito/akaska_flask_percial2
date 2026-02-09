from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SubmitField,
    EmailField,
    PasswordField,
    HiddenField,
    FileField,
    BooleanField,
    RadioField,
)
from flask_wtf.file import FileAllowed
from flask_login import current_user
from wtforms.validators import (
    DataRequired,
    Length,
    ValidationError,
    EqualTo,
    Optional,
    Email,
)
from models import Memo, User

# ========================================
# 共通バリデーション関数
# ========================================

def validate_password_strength(password):
    """
    パスワード強度チェック（共通関数）
    英数字と記号(!@#$%^&*())を含む必要がある
    """
    if not (
        any(c.isalpha() for c in password)
        and any(c.isdigit() for c in password)
        and any(c in "!@#$%^&*()" for c in password)
    ):
        raise ValidationError(
            "パスワードには【英数字と記号：!@#$%^&*()】を含める必要があります。"
        )


# ========================================
# フォームクラス
# ========================================

class MemoForm(FlaskForm):
    id = HiddenField()
    title = StringField(
        "タイトル：",
        validators=[
            DataRequired("タイトルは必須入力です"),
            Length(max=30, message="30文字以下で入力してください"),
        ],
    )
    content = TextAreaField(
        "",
        validators=[
            DataRequired("説明は必須入力です"),
        ],
    )
    image = FileField(
        "",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "gif"], "画像ファイルのみアップロードできます"
            )
        ],
    )
    submit = SubmitField("投稿")

    def validate_title(self, title):
        query = Memo.query.filter_by(title=title.data, user_id=current_user.id)
        # 編集時のみ：自分自身を除外
        if self.id.data:
            query = query.filter(Memo.id != self.id.data)
        memo = query.first()
        if memo:
            raise ValidationError(
                f"タイトル「{title.data}」は既に存在します。別のタイトルを入力してください。"
            )

class LoginForm(FlaskForm):
    email = StringField(
        "メールアドレス：", validators=[DataRequired("メールアドレスは必須入力です。")]
    )
    password = PasswordField(
        "パスワード：", validators=[DataRequired("パスワードは必須入力です。")]
    )
    remember = BooleanField("ログイン状態を1週間保持し自動でマイページに移動する")
    submit = SubmitField("ログイン")


class SignUpForm(LoginForm):  # ログイン処理と同じなため機能を継承
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名を入力してください"),
            Length(max=50),
        ],
    )
    email = EmailField(
        "メールアドレス",
        validators=[
            DataRequired(message="メールアドレスを入力してください"),
            Email(message="メールアドレスの形式が正しくありません"),
        ],
    )
    password = PasswordField(
        "パスワード：",
        validators=[Length(8, 12, "パスワードの長さは8文字以上12文字以内です")],
    )
    submit = SubmitField("登録")  # ボタンラベルをオーバーライド

    # ユーザ名の重複判定
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("そのユーザ名はすでに使用されています")

    # メールアドレスの重複確認
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError("このメールアドレスはすでに登録されています")

    # パスワード強度チェック（共通関数を使用）
    def validate_password(self, password):
        validate_password_strength(password.data)


class EditUserForm(FlaskForm):
    # ユーザー名更新
    username = StringField("ユーザー名", validators=[Optional()])

    # パスワード更新
    change_password = BooleanField("パスワードを変更する (任意)")
    password = PasswordField("新しいパスワード", validators=[Optional()])
    confirm_password = PasswordField(
        "パスワード確認再入力",
        validators=[
            Optional(),
            EqualTo("password", message="パスワードが一致しません"),
        ],
    )

    # サムネイル更新
    thumbnail = FileField(
        "サムネイル画像",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png"], "画像ファイルのみ"),
        ],
    )
    preset_thumbnail = RadioField(
        "既存画像",
        choices=[(f"{i:02}.png", f"{i:02}.png") for i in range(1, 11)],
        validators=[Optional()],
    )

    delete_user = BooleanField("このユーザーを削除する")
    submit = SubmitField("更新")

    # パスワード入力の空判定
    def validate_password(self, field):
        if self.change_password.data:
            if not field.data:
                raise ValidationError("パスワードを入力してください")
            # 強度チェック（共通関数を使用）
            validate_password_strength(field.data)

    # 確認用パスワード入力の空判定
    def validate_confirm_password(self, field):
        if self.change_password.data:
            if not field.data:
                raise ValidationError("確認用パスワードを入力してください")
