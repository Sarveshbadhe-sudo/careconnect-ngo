"""Donor workflows: dynamic donation calculation, storage, and 80G receipt download."""
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from models import db, User, Donation
from utils import generate_pdf_receipt

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donor_name = request.form.get('donor_name', '').strip()
        category = request.form.get('category', 'Nutrition')
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'UPI')
        pan_number = request.form.get('pan_number', '').strip().upper()

        if amount <= 0:
            flash('Please enter a valid donation amount.', 'danger')
            return redirect(url_for('donor.donate'))

        # Automatic calculation: Rs. 25 per meal
        meals_funded = int(amount // 25)
        receipt_id = f"AS-{uuid.uuid4().hex[:8].upper()}"
        tx_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        user_id = session.get('user_id')
        if not user_id:
            # Check or create guest user
            guest_email = request.form.get('email', f"guest_{uuid.uuid4().hex[:6]}@aashray.ngo")
            user = User.query.filter_by(email=guest_email).first()
            if not user:
                from werkzeug.security import generate_password_hash
                user = User(
                    full_name=donor_name,
                    email=guest_email,
                    pan_number=pan_number,
                    password_hash=generate_password_hash("guestpass123")
                )
                db.session.add(user)
                db.session.commit()
            user_id = user.id

        new_donation = Donation(
            receipt_id=receipt_id,
            user_id=user_id,
            donor_name=donor_name,
            category=category,
            amount=amount,
            meals_funded=meals_funded,
            payment_method=payment_method,
            transaction_ref=tx_ref,
            pan_number=pan_number
        )
        db.session.add(new_donation)
        db.session.commit()

        flash(f'Thank you! Your donation of INR {amount:,.0f} has funded {meals_funded} meals.', 'success')
        return redirect(url_for('donor.receipt', receipt_id=receipt_id))

    return render_template('donate.html')

@donor_bp.route('/receipt/<receipt_id>')
def receipt(receipt_id):
    donation = Donation.query.filter_by(receipt_id=receipt_id).first_or_404()
    return render_template('receipt.html', donation=donation)

@donor_bp.route('/receipt/<receipt_id>/pdf')
def download_pdf(receipt_id):
    donation = Donation.query.filter_by(receipt_id=receipt_id).first_or_404()
    pdf_buffer = generate_pdf_receipt(donation)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Aashray_Seva_{receipt_id}.pdf",
        mimetype='application/pdf'
    )

@donor_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access your donor dashboard.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    donations = Donation.query.filter_by(user_id=user.id).order_by(Donation.created_at.desc()).all()
    total_donated = sum(d.amount for d in donations)
    total_meals = sum(d.meals_funded for d in donations)

    return render_template('user_dashboard.html', user=user, donations=donations, total_donated=total_donated, total_meals=total_meals)