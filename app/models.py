from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bets = db.relationship('UserBet', backref='user', lazy=True)  # Verbindung zu UserBet

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
    user_bets = db.relationship('UserBet', backref='bet', lazy=True)  # Verbindung zu UserBet


class UserBet(db.Model):
    __tablename__ = 'user_bets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # FK zu User
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=False)    # FK zu Bet
    choice = db.Column(db.Enum('JA','NEIN','VIELLEICHT'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
