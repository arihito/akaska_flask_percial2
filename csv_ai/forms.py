from flask_wtf import FlaskForm
from models import  User, Product
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import (StringField, PasswordField, BooleanField, IntegerField, DateField, SubmitField)
from wtforms.validators import DataRequired, Email, Length, NumberRange

# -----------------
# ログインフォーム
# -----------------
class LoginForm(FlaskForm):
    user_name = StringField(
        "ユーザー名",
        validators=[DataRequired('ユーザー名が入力されていません'),
                    Length(max=20, message='20文字以内で入力してください')]
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired('パスワードが入力されていません'), Length(min=5)]  # 5文字以上
    )
    submit = SubmitField("認証")

# -----------------
# ユーザー登録フォーム
# -----------------
class UserForm(FlaskForm):
    user_name = StringField(
        "ユーザー名",
        validators=[DataRequired('ユーザー名は必須です'),
                    Length(max=20, message='20文字以内で入力してください')]
    )
    email = StringField(
        "メールアドレス",
        validators=[DataRequired('メールアドレスは必須です'), Email()]
    )
    password = PasswordField(
        "パスワード",
        validators=[DataRequired('パスワードは必須です'),
                    Length(4, 10, 'パスワードの長さは4文字以上10文字以内です')]  # 5文字以上
    )
    is_admin = BooleanField("管理者権限")
    is_active = BooleanField("有効ユーザー")
    submit = SubmitField("登録")

    # カスタムバリデータ
    def validate_user_name(self, user_name):
        # StringFieldオブジェクトではなく、その中のデータ(文字列)をクエリに渡す必要があるため
        # 以下のようにuser_name.dataを使用して、StringFieldから実際の文字列データを取得する
        user = User.query.filter_by(user_name=user_name.data).first()
        if user:
            raise ValidationError(f"ユーザー名「'{user_name.data}'」は既に存在します。\
                別のユーザー名を入力してください。")

    # カスタムバリデータ
    def validate_email(self, email):
        # StringFieldオブジェクトではなく、その中のデータ(文字列)をクエリに渡す必要があるため
        # 以下のようにemail.dataを使用して、StringFieldから実際の文字列データを取得する
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(f"メールアドレス「'{email.data}'」は既に存在します。\
                別のメールアドレスを入力してください。")

# -----------------
# 製品登録フォーム(追加用)
# -----------------
class ProductCreateForm(FlaskForm):
    product_id = IntegerField(
        "製品番号",
        validators=[DataRequired('製品番号は必須です'),
                    NumberRange(min=1, message='製品番号は1以上の値を設定してください')]
    )
    product_name = StringField(
        "製品名",
        validators=[DataRequired('製品名は必須です'),
                    Length(max=30, message='製品名は30文字以内で入力してください')]
    )
    price = IntegerField(
        "価格",
        validators=[DataRequired('価格は必須です'),
                    NumberRange(min=0, message='価格は0円以上で設定してください')]  # 0以上の整数
    )
    released_date = DateField(
        "発売日",
        validators=[DataRequired()],
        format="%Y-%m-%d"  # 入力フォーマット例: 2025-09-30
    )
    submit = SubmitField("登録")

    # カスタムバリデータ
    def validate_product_id(self, product_id):
        # StringFieldオブジェクトではなく、その中のデータ(文字列)をクエリに渡す必要があるため
        # 以下のようにproduct_id.dataを使用して、IntegerFieldから実際の文字列データを取得する
        product = Product.query.filter_by(product_id=product_id.data).first()
        if product:
            raise ValidationError(f"製品番号「'{product_id.data}'」は既に存在します。\
                別の製品番号を設定してください。")

# -----------------
# 製品フォーム(更新用)
# -----------------
class ProductUpdateForm(FlaskForm):
    product_id = IntegerField("製品番号(変更不可)")
    product_name = StringField(
        "製品名",
        validators=[DataRequired('製品名は必須です'),
                    Length(max=30, message='製品名は30文字以内で入力してください')]
    )
    price = IntegerField(
        "価格",
        validators=[DataRequired('価格は必須です'),
                    NumberRange(min=0, message='価格は0円以上で設定してください')]  # 0以上の整数
    )
    released_date = DateField(
        "発売日",
        validators=[DataRequired()],
        format="%Y-%m-%d"  # 入力フォーマット例: 2025-09-30
    )
    submit = SubmitField("変更")
