from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import db, Bet

admin = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.username != "admin":
            flash("🚫 Zugriff verweigert.")
            return redirect(url_for("main.index"))
        return func(*args, **kwargs)
    return wrapper

@admin.route("/")
@login_required
@admin_required
def dashboard():
    bets = Bet.query.order_by(Bet.created_at.desc()).all()
    return render_template("admin/dashboard.html", bets=bets)

@admin.route("/add", methods=["POST"])
@login_required
@admin_required
def add_bet():
    title = request.form.get("title")
    description = request.form.get("description")
    if not title:
        flash("❗ Titel darf nicht leer sein.")
    else:
        bet = Bet(title=title, description=description, status="active")
        db.session.add(bet)
        db.session.commit()
        flash("✅ Wette hinzugefügt.")
    return redirect(url_for("admin.dashboard"))

@admin.route("/toggle/<int:bet_id>")
@login_required
@admin_required
def toggle_bet(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    bet.status = "closed" if bet.status == "active" else "active"
    db.session.commit()
    flash("🔁 Status geändert.")
    return redirect(url_for("admin.dashboard"))

@admin.route("/delete/<int:bet_id>")
@login_required
@admin_required
def delete_bet(bet_id):
    bet = Bet.query.get_or_404(bet_id)
    
    # Zuerst alle zugehörigen Votes löschen
    from .models import UserBet
    UserBet.query.filter_by(bet_id=bet.id).delete()
    
    # Danach die Wette selbst löschen
    db.session.delete(bet)
    db.session.commit()
    flash("🗑️ Wette und zugehörige Stimmen gelöscht.")
    return redirect(url_for("admin.dashboard"))

