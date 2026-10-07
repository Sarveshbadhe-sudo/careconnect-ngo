"""Admin controls: live donation stats, CSV export, and event manager."""
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from models import db, User, Donation, Event

admin_bp = Blueprint('admin', __name__)

def admin_required(func):
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Restricted: Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@admin_bp.route('/admin')
@admin_required
def dashboard():
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    events = Event.query.order_by(Event.created_at.desc()).all()

    total_funds = sum(d.amount for d in donations)
    total_donors = User.query.filter_by(role='user').count()
    total_meals = sum(d.meals_funded for d in donations)

    # Category Breakdown for Chart.js
    categories = ['Bal Shiksha Ahara', 'Swasthya Ahara', 'Winter Blanket Drive', 'Emergency Medical Aid']
    category_totals = {cat: 0.0 for cat in categories}
    for d in donations:
        if d.category in category_totals:
            category_totals[d.category] += d.amount
        else:
            category_totals['Emergency Medical Aid'] += d.amount

    return render_template(
        'admin_dashboard.html',
        donations=donations,
        events=events,
        total_funds=total_funds,
        total_donors=total_donors,
        total_meals=total_meals,
        chart_labels=list(category_totals.keys()),
        chart_values=list(category_totals.values())
    )

@admin_bp.route('/admin/event/add', methods=['POST'])
@admin_required
def add_event():
    title = request.form.get('title')
    category = request.form.get('category')
    venue = request.form.get('venue')
    date = request.form.get('date')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    status = request.form.get('status', 'upcoming')

    new_event = Event(
        title=title, category=category, venue=venue,
        date=date, description=description,
        image_url=image_url, status=status
    )
    db.session.add(new_event)
    db.session.commit()
    flash('New event added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/event/delete/<int:event_id>', methods=['POST'])
@admin_required
def delete_event(event_id):
    ev = Event.query.get_or_404(event_id)
    db.session.delete(ev)
    db.session.commit()
    flash('Event removed.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/export-csv')
@admin_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Receipt ID', 'Donor Name', 'Category', 'Amount (INR)', 'Meals Funded', 'Payment Method', 'Transaction Ref', 'Date'])

    donations = Donation.query.all()
    for d in donations:
        writer.writerow([d.receipt_id, d.donor_name, d.category, d.amount, d.meals_funded, d.payment_method, d.transaction_ref, d.created_at.strftime('%Y-%m-%d %H:%M')])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=aashray_seva_donations.csv"}
    )