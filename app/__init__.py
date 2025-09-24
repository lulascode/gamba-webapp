from flask import Flask
from .models import db, User, Bet
from flask_login import LoginManager
import time
from sqlalchemy.exc import OperationalError

login_manager = LoginManager()
login_manager.login_view = "main.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@db:3306/betting'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        for i in range(20):  # 20 Versuche à 5 Sekunden
            try:
                db.create_all()
                print("✅ DB verbunden und Tabellen erstellt.")

                # --- Standard-Daten einfügen ---
                # Admin-User anlegen, falls nicht vorhanden
                if not User.query.filter_by(username="admin").first():
                    admin = User(username="admin")
                    admin.set_password("starten01")
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Admin-User erstellt.")

                # Test-Wetten anlegen (hartcodiert)
                test_bets = [
                    {"title": "Test-Wette", "description": "Wenn diese Wette zu sehen ist funktioniert alles!", "status": "active"},
                    {"title": "Wette 1: Fußballspiel", "description": "Wer gewinnt das heutige Fußballspiel?", "status": "active"},
                    {"title": "Wette 2: Wettervorhersage", "description": "Wird es morgen regnen?", "status": "active"},
                    {"title": "Wette 3: Aktienkurs", "description": "Steigt der Aktienkurs von Company X diese Woche?", "status": "active"},
                    {"title": "Wette 4: Filmstart", "description": "Wird der neue Blockbuster mehr als 1 Mio Zuschauer im ersten Wochenende haben?", "status": "active"},
                    {"title": "Wette 5: Quizfrage", "description": "Werden mehr als 50% der Leute die heutige Quizfrage richtig beantworten?", "status": "active"},
                    {"title": "Wette 6: Politik", "description": "Wird die neue Gesetzesänderung diese Woche verabschiedet?", "status": "active"},
                    {"title": "Wette 7: Technologie", "description": "Kommt das neue Smartphone-Modell pünktlich auf den Markt?", "status": "active"}
                ]

                for b in test_bets:
                    if not Bet.query.filter_by(title=b["title"]).first():
                        bet = Bet(title=b["title"], description=b["description"], status=b["status"])
                        db.session.add(bet)
                        db.session.commit()
                        print(f"✅ Beispiel-Wette '{b['title']}' erstellt.")

                break
            except OperationalError:
                print(f"⏳ DB noch nicht bereit (Versuch {i+1}/20)...")
                time.sleep(5)
        else:
            raise RuntimeError("❌ DB nicht erreichbar.")

    return app
