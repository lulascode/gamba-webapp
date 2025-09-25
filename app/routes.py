from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import db, User, Bet, UserBet
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

# Auto-Redirect: Wenn nicht eingeloggt -> /login
@main.route('/')
@login_required
def index():
    # Alle aktiven Wetten aus der DB abrufen
    active_bets = Bet.query.filter_by(status="active").all()

    # Statistik pro Wette vorbereiten
    bets_stats = {}
    for bet in active_bets:
        votes = UserBet.query.filter_by(bet_id=bet.id).all()
        # Dynamische Keys aus den Optionen der Wette
        options = bet.get_options()
        stats = {opt: 0 for opt in options}
        for vote in votes:
            if vote.choice in stats:
                stats[vote.choice] += 1
        bets_stats[bet.id] = stats

    # Eigene Wahl pro Wette abrufen
    user_choices = {ub.bet_id: ub.choice for ub in UserBet.query.filter_by(user_id=current_user.id).all()}

    return render_template('index.html', bets=active_bets, bets_stats=bets_stats, user_choices=user_choices)


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
    bet = Bet.query.get_or_404(bet_id)
    choice = request.form.get('choice')

    if choice not in bet.get_options():
        flash("Ungültige Auswahl!")
        return redirect(url_for('main.index'))

    existing = UserBet.query.filter_by(user_id=current_user.id, bet_id=bet.id).first()
    if existing:
        existing.choice = choice
        flash("Deine Wahl wurde aktualisiert!")
    else:
        new_vote = UserBet(user_id=current_user.id, bet_id=bet.id, choice=choice)
        db.session.add(new_vote)
        flash("Abstimmung erfolgreich!")

    # Ergebnis neu berechnen, falls Deadline vorbei oder geschlossen
    if bet.is_closed():
        bet.calculate_result()

    db.session.commit()
    return redirect(url_for('main.index'))