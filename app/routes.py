from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import db, User, Bet, UserBet
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

# Auto-Redirect: Wenn nicht eingeloggt -> /login
@main.route('/')
@login_required
def index():
    active_bets = Bet.query.filter_by(status="active").all()
    bet_data = []

    for bet in active_bets:
        votes = {'JA': 0, 'NEIN': 0, 'VIELLEICHT': 0}
        user_choice = None
        for ub in bet.user_bets:
            votes[ub.choice] += 1
            if ub.user_id == current_user.id:
                user_choice = ub.choice

        bet_data.append({
            'id': bet.id,
            'title': bet.title,
            'description': bet.description,
            'status': bet.status,
            'votes': votes,
            'user_choice': user_choice
        })

    return render_template('index.html', bets=bet_data)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash("Falscher Benutzername oder Passwort")
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Benutzername existiert schon")
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash("Registrierung erfolgreich!")
            return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/vote/<int:bet_id>', methods=['POST'])
@login_required
def vote(bet_id):
    choice = request.form.get('choice')
    if choice not in ['JA','NEIN','VIELLEICHT']:
        flash("Ungültige Auswahl!")
        return redirect(url_for('main.index'))

    existing = UserBet.query.filter_by(user_id=current_user.id, bet_id=bet_id).first()
    if existing:
        existing.choice = choice
        flash("Deine Wahl wurde aktualisiert!")
    else:
        new_vote = UserBet(user_id=current_user.id, bet_id=bet_id, choice=choice)
        db.session.add(new_vote)
        flash("Abstimmung erfolgreich!")

    db.session.commit()
    return redirect(url_for('main.index'))
