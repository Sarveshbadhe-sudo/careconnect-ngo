"""
Aashray Seva - NGO Management & Donation Portal
Department of Information Technology | SIES GST (Autonomous)
Tech Stack: Python 3, Flask, SQLite (SQLAlchemy), ReportLab
"""

import csv
import io
import uuid
from datetime import datetime

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import Donation, Event, User, db
from utils import generate_pdf_receipt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aashray-seva-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aashray_seva.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ----------------- 1. PUBLIC HOMEPAGE ----------------- #
@app.route('/', endpoint='public_index')
def public_index():
    upcoming_events = Event.query.filter_by(status='upcoming').limit(3).all()
    completed_events = Event.query.filter_by(status='completed').limit(6).all()
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()

    all_donations = Donation.query.all()
    total_funds = sum(d.amount for d in all_donations)
    total_meals = sum(d.meals_funded for d in all_donations)
    total_donors = User.query.filter_by(role='user').count()

    return render_template(
        'index.html',
        upcoming_events=upcoming_events,
        completed_events=completed_events,
        recent_donations=recent_donations,
        total_funds=total_funds,
        total_meals=total_meals,
        total_donors=total_donors,
    )


# ----------------- 2. AUTHENTICATION (USER & ADMIN) ----------------- #
@app.route('/login', methods=['GET', 'POST'], endpoint='login')
@app.route('/login', methods=['GET', 'POST'], endpoint='auth.login')
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        selected_role = request.form.get('login_role', 'user')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if user.role != selected_role:
                flash(
                    f'Unauthorized: This account is registered as a {user.role.title()}, not {selected_role.title()}. Please switch tabs.',
                    'danger',
                )
                return render_template('login.html')

            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['role'] = user.role

            if user.role == 'admin':
                flash('Logged in to Admin Central Console.', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('user_dashboard'))

        flash('Invalid credentials. Please verify your email and password.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'], endpoint='register')
@app.route('/register', methods=['GET', 'POST'], endpoint='auth.register')
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        pan = request.form.get('pan_number', '').strip().upper()
        password = request.form.get('password', '')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please sign in.', 'danger')
            return redirect(url_for('login'))

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            pan_number=pan,
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', endpoint='logout')
@app.route('/logout', endpoint='auth.logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('public_index'))


# ----------------- 3. DONATION SYSTEM & RECEIPTS ----------------- #
@app.route('/donate', methods=['GET', 'POST'], endpoint='donate')
@app.route('/donate', methods=['GET', 'POST'], endpoint='donor.donate')
def donate():
    if request.method == 'POST':
        donor_name = request.form.get('donor_name', '').strip()
        category = request.form.get('category', 'Bal Shiksha Ahara')
        amount = float(request.form.get('amount', 0))
        payment_method = request.form.get('payment_method', 'UPI')
        pan_number = request.form.get('pan_number', '').strip().upper()

        if amount <= 0:
            flash('Please enter a valid donation amount.', 'danger')
            return redirect(url_for('donate'))

        meals_funded = int(amount // 25)
        receipt_id = f"AS-{uuid.uuid4().hex[:8].upper()}"
        tx_ref = f"TXN-{uuid.uuid4().hex[:10].upper()}"

        user_id = session.get('user_id')
        if not user_id:
            guest_email = f"guest_{uuid.uuid4().hex[:6]}@aashray.ngo"
            guest = User(
                full_name=donor_name,
                email=guest_email,
                pan_number=pan_number,
                password_hash=generate_password_hash("guestpass123"),
            )
            db.session.add(guest)
            db.session.commit()
            user_id = guest.id

        new_donation = Donation(
            receipt_id=receipt_id,
            user_id=user_id,
            donor_name=donor_name,
            category=category,
            amount=amount,
            meals_funded=meals_funded,
            payment_method=payment_method,
            transaction_ref=tx_ref,
            pan_number=pan_number,
        )
        db.session.add(new_donation)
        db.session.commit()
        return redirect(url_for('receipt', receipt_id=receipt_id))
    return render_template('donate.html')


@app.route('/receipt/<receipt_id>', endpoint='receipt')
@app.route('/receipt/<receipt_id>', endpoint='donor.receipt')
def receipt(receipt_id):
    donation = Donation.query.filter_by(receipt_id=receipt_id).first_or_404()
    return render_template('receipt.html', donation=donation)


@app.route('/receipt/<receipt_id>/pdf', endpoint='download_pdf')
@app.route('/receipt/<receipt_id>/pdf', endpoint='donor.download_pdf')
def download_pdf(receipt_id):
    donation = Donation.query.filter_by(receipt_id=receipt_id).first_or_404()
    pdf_buffer = generate_pdf_receipt(donation)
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Aashray_Receipt_{receipt_id}.pdf",
        mimetype='application/pdf',
    )


# ----------------- 4. USER DASHBOARD ----------------- #
@app.route('/user/dashboard', endpoint='user_dashboard')
@app.route('/user/dashboard', endpoint='donor.dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please login to access your donor dashboard.', 'warning')
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    donations = (
        Donation.query.filter_by(user_id=user.id)
        .order_by(Donation.created_at.desc())
        .all()
    )
    total_donated = sum(d.amount for d in donations)
    total_meals = sum(d.meals_funded for d in donations)
    return render_template(
        'user_dashboard.html',
        user=user,
        donations=donations,
        total_donated=total_donated,
        total_meals=total_meals,
    )


# ----------------- 5. ADMIN DASHBOARD & CONTROLS ----------------- #
@app.route('/admin', endpoint='admin_dashboard')
@app.route('/admin', endpoint='admin.dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        flash('Admin login required.', 'danger')
        return redirect(url_for('login'))

    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    events = Event.query.order_by(Event.created_at.desc()).all()
    total_funds = sum(d.amount for d in donations)
    total_donors = User.query.filter_by(role='user').count()
    total_meals = sum(d.meals_funded for d in donations)

    categories = [
        'Bal Shiksha Ahara',
        'Swasthya Ahara',
        'Winter Blanket Drive',
        'General Corpus',
    ]
    category_totals = {cat: 0.0 for cat in categories}
    for d in donations:
        if d.category in category_totals:
            category_totals[d.category] += d.amount
        else:
            category_totals['General Corpus'] += d.amount

    return render_template(
        'admin_dashboard.html',
        donations=donations,
        events=events,
        total_funds=total_funds,
        total_donors=total_donors,
        total_meals=total_meals,
        chart_labels=list(category_totals.keys()),
        chart_values=list(category_totals.values()),
    )


@app.route('/admin/event/add', methods=['POST'], endpoint='add_event')
@app.route('/admin/event/add', methods=['POST'], endpoint='admin.add_event')
def add_event():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    title = request.form.get('title')
    category = request.form.get('category')
    venue = request.form.get('venue')
    date = request.form.get('date')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    status = request.form.get('status', 'upcoming')

    new_event = Event(
        title=title,
        category=category,
        venue=venue,
        date=date,
        description=description,
        image_url=image_url,
        status=status,
    )
    db.session.add(new_event)
    db.session.commit()
    flash('Campaign added successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/event/delete/<int:event_id>', methods=['POST'], endpoint='delete_event')
@app.route('/admin/event/delete/<int:event_id>', methods=['POST'], endpoint='admin.delete_event')
def delete_event(event_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    ev = Event.query.get_or_404(event_id)
    db.session.delete(ev)
    db.session.commit()
    flash('Campaign removed.', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/export-csv', endpoint='export_csv')
@app.route('/admin/export-csv', endpoint='admin.export_csv')
def export_csv():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Receipt ID',
        'Donor Name',
        'Category',
        'Amount (INR)',
        'Meals Funded',
        'Payment Method',
        'Transaction Ref',
        'Date',
    ])
    for d in Donation.query.all():
        writer.writerow([
            d.receipt_id,
            d.donor_name,
            d.category,
            d.amount,
            d.meals_funded,
            d.payment_method,
            d.transaction_ref,
            d.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=donations.csv"},
    )


# ----------------- 6. DATABASE INITIALIZATION & MOCK SEEDING ----------------- #
def seed_database():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@aashray.ngo').first():
            admin = User(
                full_name='System Admin',
                email='admin@aashray.ngo',
                phone='9876543210',
                role='admin',
                password_hash=generate_password_hash('admin123'),
            )
            donor = User(
                full_name='Sahil Manohar Desale',
                email='sahil@gmail.com',
                phone='9820123456',
                pan_number='ABCDE1234F',
                role='user',
                password_hash=generate_password_hash('sahil123'),
            )
            db.session.add_all([admin, donor])
            db.session.commit()

            events = [
                Event(
                    title="Bal Shiksha Ahara - Municipal School Food Drive",
                    category="Nutrition",
                    venue="Municipal School 102, Nerul, Navi Mumbai",
                    date="2026-10-18",
                    description="Distributing fresh hot nutritious breakfast and fruit kits to 450 municipal primary school kids.",
                    status="upcoming",
                    image_url="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=600",
                ),
                Event(
                    title="Winter Warmth: Blanket & Woolen Clothes Drive",
                    category="Relief",
                    venue="Navi Mumbai Slum Settlements",
                    date="2026-11-05",
                    description="Distributing thermal blankets and jackets to elderly residents and migrant families.",
                    status="upcoming",
                    image_url="https://images.unsplash.com/photo-1593113598332-cd288d649433?w=600",
                ),
                Event(
                    title="Swasthya Ahara - Civil Hospital Distribution",
                    category="Healthcare",
                    venue="Govt Hospital Shelter, Vashi",
                    date="2026-09-12",
                    description="Served warm khichdi and fresh fruit to over 1,200 relatives of hospitalized patients.",
                    status="completed",
                    image_url="https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=600",
                ),
                Event(
                    title="Education Kit Distribution - Mission Vidya",
                    category="Education",
                    venue="Turbhe Colony Learning Center",
                    date="2026-08-20",
                    description="Provided stationery kits, notebooks, and school bags to 300 underprivileged children.",
                    status="completed",
                    image_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600",
                ),
            ]
            donations = [
                Donation(
                    receipt_id="AS-8941AB12",
                    user_id=donor.id,
                    donor_name="Sahil Manohar Desale",
                    category="Bal Shiksha Ahara",
                    amount=5000.0,
                    meals_funded=200,
                    payment_method="UPI",
                    transaction_ref="TXN-UPI9918231",
                    pan_number="ABCDE1234F",
                ),
                Donation(
                    receipt_id="AS-3321FA77",
                    user_id=donor.id,
                    donor_name="Dharamkumar Bhatia",
                    category="Swasthya Ahara",
                    amount=2500.0,
                    meals_funded=100,
                    payment_method="Card",
                    transaction_ref="TXN-CRD4928172",
                    pan_number="BKJPA9012K",
                ),
                Donation(
                    receipt_id="AS-1092FF98",
                    user_id=donor.id,
                    donor_name="Pratap Merchant",
                    category="Winter Blanket Drive",
                    amount=12000.0,
                    meals_funded=480,
                    payment_method="NetBanking",
                    transaction_ref="TXN-NB0029182",
                    pan_number="PMMPA4412R",
                ),
            ]
            db.session.add_all(events + donations)
            db.session.commit()


if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5000)