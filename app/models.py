from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.mysql import TEXT
import json
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bets = db.relationship('UserBet', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'closed'), default='active')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Ablaufdatum
    deadline = db.Column(db.DateTime, nullable=True)
    
    # Eigene Antwortoptionen, als JSON-String gespeichert
    options = db.Column(db.Text, nullable=False, default=json.dumps(["JA","NEIN","VIELLEICHT"]))
    
    # Mehrfachauswahl erlauben
    allow_multiple = db.Column(db.Boolean, default=False)
    
    # Ergebnis: Option mit den meisten Stimmen
    result = db.Column(db.String(255), nullable=True)
    
    user_bets = db.relationship('UserBet', backref='bet', lazy=True)

    def get_options(self):
        try:
            return json.loads(self.options)
        except:
            return ["JA","NEIN","VIELLEICHT"]

    def is_closed(self):
        if self.status == "closed":
            return True
        if self.deadline and datetime.utcnow() > self.deadline:
            return True
        return False

    def calculate_result(self):
        stats = {}
        for opt in self.get_options():
            stats[opt] = UserBet.query.filter_by(bet_id=self.id, choice=opt).count()
        if stats:
            self.result = max(stats, key=stats.get)
        db.session.commit()
        return self.result


class UserBet(db.Model):
    __tablename__ = 'user_bets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=False)
    choice = db.Column(db.String(255), nullable=False)  # flexible Option
    created_at = db.Column(db.DateTime, server_default=db.func.now())
