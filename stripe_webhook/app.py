from flask import Flask, render_template
from checkout.routes import checkout_bp
from checkout.webhook import webhook_bp
from extensions import init_stripe

def create_app():
    app = Flask(__name__)

    init_stripe(app)

    app.register_blueprint(checkout_bp)
    app.register_blueprint(webhook_bp)

    @app.route('/')
    def index():
        return render_template('index.j2')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
