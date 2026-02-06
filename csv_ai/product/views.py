from flask import Blueprint,render_template, request, redirect, url_for, flash
from models import db, Product
from forms import ProductCreateForm, ProductUpdateForm
from flask_login import login_required

# authのBlueprint
product_bp = Blueprint('product', __name__, url_prefix='/product')

# ルーティング

# トップ画面へ遷移
@product_bp.route("/top", methods=["GET"])
@login_required
def top():
    # 商品情報全件取得
    products = Product.query.all()
    # 画面遷移
    return render_template("product/top.html", products=products)

# 製品登録(Form使用)
@product_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    # Formインスタンス生成
    form = ProductCreateForm()
    if form.validate_on_submit():
        # データ入力取得
        product_id = form.product_id.data
        product_name = form.product_name.data
        price = form.price.data
        released_date = form.released_date.data
        # 登録処理
        product = Product(product_id = product_id, product_name = product_name, price = price, released_date = released_date)
        db.session.add(product)
        db.session.commit()
        # 画面遷移
        flash("登録しました")
        return redirect(url_for("product.top"))
    # GET時
    # 画面遷移
    return render_template("product/create_form.html", form=form)

# 更新(Form使用)
@product_bp.route("/update/<int:product_id>", methods=["GET", "POST"])
@login_required
def update(product_id):
    # データベースからmemo_idに一致するメモを取得し、見つからない場合は404エラーを表示
    target_data = Product.query.get_or_404(product_id)
    # Formに入れ替え
    form = ProductUpdateForm(obj=target_data)
    if request.method == 'POST' and form.validate():
        # 変更処理
        target_data.product_name = form.product_name.data
        target_data.price = form.price.data
        target_data.released_date = form.released_date.data
        db.session.commit()
        # フラッシュメッセージ
        flash("変更しました")
        # 画面遷移
        return redirect(url_for("product.top"))
    # GET時
    # 画面遷移
    return render_template("product/update_form.html", form=form, edit_id=target_data.product_id)

# 削除
@product_bp.route("/delete/<int:product_id>")
@login_required
def delete(product_id):
    # データべースからmemo_idに一致するメモを取得し、見つからない場合は404エラーを表示
    product = Product.query.get_or_404(product_id)
    # 削除処理
    db.session.delete(product)
    db.session.commit()
    # 画面遷移
    return redirect(url_for("product.top"))

