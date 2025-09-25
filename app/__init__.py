from flask import Flask
from .models import db, User
from flask_login import LoginManager
import time
from sqlalchemy.exc import OperationalError

# ---- Login Manager ----
login_manager = LoginManager()
login_manager.login_view = "main.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    # ---- Grundkonfiguration ----
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@db:3306/betting'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ---- Extensions ----
    db.init_app(app)
    login_manager.init_app(app)

    # ---- Blueprints ----
    from .routes import main
    from .admin import admin
    app.register_blueprint(main)
    app.register_blueprint(admin)

    # ---- DB-Setup & Admin-User ----
    with app.app_context():
        for i in range(20):  # 20 Versuche à 5 Sekunden
            try:
                db.create_all()
                print("✅ DB verbunden und Tabellen erstellt.")

                # --- Admin-User anlegen ---
                if not User.query.filter_by(username="admin").first():
                    admin_user = User(username="admin")
                    admin_user.set_password("starten01")
                    db.session.add(admin_user)
                    db.session.commit()
                    print("✅ Admin-User erstellt (admin / starten01).")

                break  # Erfolgreich -> Schleife verlassen

            except OperationalError:
                print(f"⏳ DB noch nicht bereit (Versuch {i+1}/20)...")
                time.sleep(5)
        else:
            raise RuntimeError("❌ Datenbank nach 20 Versuchen nicht erreichbar.")

    return app
