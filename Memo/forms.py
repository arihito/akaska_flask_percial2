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
    SelectField,
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
    Regexp
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
    summary = TextAreaField(
        "要約文（省略可・一覧表示に優先使用）：",
        validators=[
            Optional(),
            Length(max=300, message="300文字以下で入力してください"),
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
            Length(min=3, max=12),
            Regexp(
                r'^[ぁ-んァ-ヶー一-龯a-zA-Z0-9_\-\.]+$',
                message="使用できない文字が含まれています"
            )
        ],
        render_kw={
            "autocomplete": "new-password",
            "spellcheck": "false",
            "autocapitalize": "none",
            "inputmode": "latin",
            "lang": "ja"
        }
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
    confirm_password = PasswordField(
        "パスワード（確認）：",
        validators=[
            DataRequired(message="確認用パスワードを入力してください"),
            EqualTo("password", message="パスワードが一致しません"),
        ],
    )
    gender = SelectField(
        "",
        choices=[
            ("", "「性別」 を選択してください"),
            ("男性", "男性"),
            ("女性", "女性"),
            ("その他", "その他"),
        ],
        validators=[DataRequired(message="性別を選択してください")],
    )
    age_range = SelectField(
        "",
        choices=[
            ("", "「年代」 を選択してください"),
            ("0〜10", "0〜10歳"),
            ("10〜20", "10〜20歳"),
            ("20〜30", "20〜30歳"),
            ("30〜40", "30〜40歳"),
            ("40〜50", "40〜50歳"),
            ("50〜60", "50〜60歳"),
            ("60以上", "60歳以上"),
        ],
        validators=[DataRequired(message="年代を選択してください")],
    )
    address = SelectField(
        "",
        choices=[
            ("", "「居住地域」 を選択してください"),
            ("東京都", "東京都"),
            ("神奈川県", "神奈川県"),
            ("埼玉県", "埼玉県"),
            ("千葉県", "千葉県"),
            ("その他", "その他の地域"),
        ],
        validators=[DataRequired(message="居住地域を選択してください")],
    )
    occupation = SelectField(
        "",
        choices=[
            ("", "「ご職業」 を選択してください"),
            ("学生", "学生"),
            ("会社員", "会社員"),
            ("自営業", "自営業"),
            ("主婦・主夫", "主婦・主夫"),
            ("その他", "その他"),
        ],
        validators=[DataRequired(message="ご職業を選択してください")],
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


class AdminLoginForm(FlaskForm):
    admin_password = PasswordField(
        "管理者パスワード：",
        validators=[DataRequired("管理者パスワードは必須入力です。")]
    )
    submit = SubmitField("管理者ログイン")
