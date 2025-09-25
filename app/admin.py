from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import db, Bet, UserBet
import json
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')


# --------------------------
# Admin Dashboard
# --------------------------
@admin.route('/', methods=['GET'])
@login_required
def dashboard():
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    bets = Bet.query.order_by(Bet.created_at.desc()).all()

    # Statistik vorbereiten
    bets_stats = {}
    for bet in bets:
        votes = UserBet.query.filter_by(bet_id=bet.id).all()
        options = bet.get_options()
        stats = {opt: 0 for opt in options}
        for vote in votes:
            if vote.choice in stats:
                stats[vote.choice] += 1
        bets_stats[bet.id] = stats

    return render_template('admin/dashboard.html', bets=bets, bets_stats=bets_stats)


# --------------------------
# Neue Wette hinzufügen
# --------------------------
@admin.route('/add', methods=['POST'])
@login_required
def add_bet():
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    title = request.form.get('title')
    description = request.form.get('description', '')
    options = [request.form.get(f'option{i}') for i in range(1, 5)]
    options = [opt.strip() for opt in options if opt and opt.strip()]

    if len(options) < 2:
        flash("Bitte mindestens 2 Antwortoptionen angeben!")
        return redirect(url_for('admin.dashboard'))

    # Deadline aus Formular
    deadline_str = request.form.get('deadline')
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Ungültiges Datumsformat, bitte YYYY-MM-DD HH:MM")

    new_bet = Bet(title=title, description=description, options=json.dumps(options), deadline=deadline)
    db.session.add(new_bet)
    db.session.commit()
    flash("Neue Wette erstellt!")
    return redirect(url_for('admin.dashboard'))


# --------------------------
# Wette bearbeiten / Detailseite
# --------------------------
@admin.route('/bet/<int:bet_id>', methods=['GET', 'POST'])
@login_required
def bet_detail(bet_id):
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    bet = Bet.query.get_or_404(bet_id)

    if request.method == 'POST':
        bet.title = request.form.get('title', bet.title)
        bet.description = request.form.get('description', bet.description)

        options = [request.form.get(f'option{i}') for i in range(1, 5)]
        options = [opt.strip() for opt in options if opt and opt.strip()]
        if len(options) < 2:
            flash("Bitte mindestens 2 Antwortoptionen angeben!")
            return redirect(url_for('admin.bet_detail', bet_id=bet.id))
        bet.options = json.dumps(options)

        # Deadline speichern
        deadline_str = request.form.get('deadline')
        if deadline_str:
            try:
                bet.deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Ungültiges Datumsformat, bitte YYYY-MM-DD HH:MM")
        else:
            bet.deadline = None

        db.session.commit()
        flash("Wette aktualisiert!")
        return redirect(url_for('admin.bet_detail', bet_id=bet.id))

    # Optionen auf 4 Felder auffüllen
    options = bet.get_options()
    while len(options) < 4:
        options.append("")

    # Statistik für Balken
    votes = UserBet.query.filter_by(bet_id=bet.id).all()
    stats = {opt: 0 for opt in options}
    for vote in votes:
        if vote.choice in stats:
            stats[vote.choice] += 1
    bets_stats = {bet.id: stats}

    return render_template('admin/bet_detail.html', bet=bet, options=options, bets_stats=bets_stats)


# --------------------------
# Wette schließen / öffnen
# --------------------------
@admin.route('/toggle/<int:bet_id>')
@login_required
def toggle_bet(bet_id):
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    bet = Bet.query.get_or_404(bet_id)
    bet.status = 'closed' if bet.status == 'active' else 'active'

    # Ergebnis berechnen, falls geschlossen
    if bet.status == 'closed':
        bet.calculate_result()

    db.session.commit()
    flash(f"Wette '{bet.title}' ist jetzt {bet.status}.")
    return redirect(url_for('admin.dashboard'))


# --------------------------
# Wette löschen
# --------------------------
@admin.route('/delete/<int:bet_id>')
@login_required
def delete_bet(bet_id):
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    bet = Bet.query.get_or_404(bet_id)
    db.session.delete(bet)
    db.session.commit()
    flash(f"Wette '{bet.title}' wurde gelöscht.")
    return redirect(url_for('admin.dashboard'))
