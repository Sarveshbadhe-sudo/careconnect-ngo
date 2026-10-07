"""User and Admin authentication routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        pan = request.form.get('pan_number', '').strip().upper()
        password = request.form.get('password', '')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please sign in.', 'danger')
            return redirect(url_for('auth.login'))

        hashed_pw = generate_password_hash(password)
        new_user = User(full_name=full_name, email=email, phone=phone, pan_number=pan, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration complete! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['role'] = user.role
            flash(f'Welcome back, {user.full_name}!', 'success')
            return redirect(url_for('admin.dashboard') if user.role == 'admin' else url_for('donor.dashboard'))
        
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('public_index'))