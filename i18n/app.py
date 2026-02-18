from flask import Flask, request, session
from flask_babel import Babel, gettext as _

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret-key"
app.config["BABEL_DEFAULT_LOCALE"] = "ja"
app.config["BABEL_SUPPORTED_LOCALES"] = [
    "ja",
    "ja_JP",
    "en",
    "en_US",
    "kr",
    "cz",
    "es",
]

def get_locale():
    if "lang" in request.args:
        return request.args.get("lang")
    if "lang" in session:
        return session["lang"]
    return request.accept_languages.best_match(
        app.config["BABEL_SUPPORTED_LOCALES"]
    )

# ★ Flask-Babel 4.x の正しい指定
babel = Babel(app, locale_selector=get_locale)


@app.route("/")
def index():
    greeting = _("Hello, world!")
    return (
        f"<p>{greeting}</p>"
        f"<p><a href='/?lang=ja'>日本語</a> | "
        f"<a href='/?lang=en'>English</a></p>"
    )
