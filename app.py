from flask import Flask, render_template
from config import Config
from models.db_models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.document_routes import document_bp
    from routes.chat_routes import chat_bp
    from routes.admin_routes import admin_bp
    app.register_blueprint(document_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)