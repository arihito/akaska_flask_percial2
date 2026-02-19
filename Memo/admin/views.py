from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from forms import AdminLoginForm
from flask_wtf import FlaskForm
import stripe

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """管理者セッション認証デコレータ"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin_authenticated'):
            flash('管理者としてログインしてください', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
@login_required
def login():
    # 既に管理者認証済みなら管理画面へ
    if session.get('is_admin_authenticated'):
        return redirect(url_for('admin.index'))

    # 管理者権限チェック
    if not current_user.is_admin:
        flash('管理者権限がありません', 'danger')
        return redirect(url_for('memo.index'))

    form = AdminLoginForm()

    if form.validate_on_submit():
        if current_user.check_admin_password(form.admin_password.data):
            session['is_admin_authenticated'] = True
            flash('管理者としてログインしました', 'secondary')
            return redirect(url_for('admin.index'))
        else:
            flash('管理者パスワードが正しくありません', 'danger')

    return render_template('admin/login.j2', form=form)


@admin_bp.route('/')
@admin_required
def index():
    return render_template('admin/index.j2')


@admin_bp.route('/payment')
@login_required
def payment():
    form = FlaskForm()
    return render_template('admin/payment.j2', form=form)


@admin_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    price = current_app.config['ADMIN_PLAN_PRICE']
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'jpy',
                    'product_data': {
                        'name': '管理者アクセスプラン（10日間）',
                    },
                    'unit_amount': price,
                },
                'quantity': 1,
            }
        ],
        mode='payment',
        metadata={'user_id': str(current_user.id)},
        success_url=url_for('admin.payment_success', _external=True),
        cancel_url=url_for('admin.payment_cancel', _external=True),
    )
    return redirect(checkout_session.url, code=303)


@admin_bp.route('/payment/success')
@login_required
def payment_success():
    flash('決済が完了しました。管理者用のログインパスワードをご登録のメールアドレスにお送りしますので、しばらくお待ちください。', 'secondary')
    return redirect(url_for('admin.login'))


@admin_bp.route('/payment/cancel')
@login_required
def payment_cancel():
    flash('決済がキャンセルされました', 'danger')
    return redirect(url_for('admin.payment'))


@admin_bp.route('/logout')
@login_required
def logout():
    session.pop('is_admin_authenticated', None)
    flash('管理者からログアウトしました', 'secondary')
    return redirect(url_for('memo.index'))
