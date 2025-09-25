import json
from datetime import datetime
from . import db  # Importiere db einmalig global aus __init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# --------------------------
# User-Model
# --------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    bets = db.relationship('UserBet', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --------------------------
# Bet-Model
# --------------------------
class Bet(db.Model):
    __tablename__ = 'bets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum('active', 'closed'), default='active')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    deadline = db.Column(db.DateTime, nullable=True)
    options = db.Column(db.Text, nullable=False, default=json.dumps(["JA","NEIN","VIELLEICHT"]))
    allow_multiple = db.Column(db.Boolean, default=False)
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

    def time_left(self):
        """Gibt die verbleibende Zeit bis zur Deadline zurück"""
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        if delta.total_seconds() < 0:
            return "abgelaufen"
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = remainder // 60
        return f"{days}d {hours}h {minutes}m"

    def calculate_result(self):
        stats = {}
        for opt in self.get_options():
            stats[opt] = UserBet.query.filter_by(bet_id=self.id, choice=opt).count()
        if stats:
            self.result = max(stats, key=stats.get)
        db.session.commit()
        return self.result

# --------------------------
# UserBet-Model
# --------------------------
class UserBet(db.Model):
    __tablename__ = 'user_bets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=False)
    choice = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
