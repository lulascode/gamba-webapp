from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import db, Bet
from datetime import datetime
import json

admin = Blueprint('admin', __name__, template_folder='templates/admin')

# Admin Dashboard
@admin.route('/')
@login_required
def dashboard():
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    bets = Bet.query.order_by(Bet.created_at.desc()).all()

    # --- Stimmen pro Option zählen ---
    from .models import UserBet
    bets_stats = {}
    for bet in bets:
        options = bet.get_options()  # dynamisch aus JSON
        votes = UserBet.query.filter_by(bet_id=bet.id).all()
        stats = {opt: 0 for opt in options}
        for v in votes:
            if v.choice in stats:
                stats[v.choice] += 1
        bets_stats[bet.id] = stats

    return render_template('dashboard.html', bets=bets, bets_stats=bets_stats)


# Neue Wette hinzufügen
@admin.route('/add', methods=['POST'])
@login_required
def add_bet():
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))

    title = request.form.get('title')
    description = request.form.get('description', '')
    
    # Optionen aus Formular: mindestens 2, max. 4
    options = [request.form.get(f'option{i}') for i in range(1, 5)]
    options = [opt.strip() for opt in options if opt and opt.strip()]
    
    if len(options) < 2:
        flash("Bitte mindestens 2 Antwortoptionen angeben!")
        return redirect(url_for('admin.dashboard'))
    
    new_bet = Bet(title=title, description=description, options=json.dumps(options))
    db.session.add(new_bet)
    db.session.commit()
    flash("Neue Wette erstellt!")
    return redirect(url_for('admin.dashboard'))

# Wette löschen
@admin.route('/delete/<int:bet_id>')
@login_required
def delete_bet(bet_id):
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))
    bet = Bet.query.get_or_404(bet_id)
    db.session.delete(bet)
    db.session.commit()
    flash("Wette gelöscht!")
    return redirect(url_for('admin.dashboard'))

# Wette schließen / öffnen
@admin.route('/toggle/<int:bet_id>')
@login_required
def toggle_bet(bet_id):
    if current_user.username != "admin":
        flash("Zugriff verweigert!")
        return redirect(url_for('main.index'))
    bet = Bet.query.get_or_404(bet_id)
    bet.status = 'closed' if bet.status == 'active' else 'active'
    db.session.commit()
    flash(f"Wette {bet.title} ist nun {bet.status}")
    return redirect(url_for('admin.dashboard'))

# Wette bearbeiten / Detailseite
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
        
        # Optionen bearbeiten
        options = [request.form.get(f'option{i}') for i in range(1, 5)]
        options = [opt.strip() for opt in options if opt and opt.strip()]
        if len(options) < 2:
            flash("Bitte mindestens 2 Antwortoptionen angeben!")
            return redirect(url_for('admin.bet_detail', bet_id=bet.id))
        bet.options = json.dumps(options)
        
        # Deadline
        deadline = request.form.get('deadline', None)
        if deadline:
            try:
                bet.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            except:
                flash("Ungültiges Datumsformat, bitte YYYY-MM-DD HH:MM")
        
        db.session.commit()
        flash("Wette aktualisiert!")
        return redirect(url_for('admin.bet_detail', bet_id=bet.id))
    
    # Optionen für das Formular vorbereiten (max 4 Felder)
    options = bet.get_options()
    while len(options) < 4:
        options.append("")
    
    return render_template('bet_detail.html', bet=bet, options=options)
