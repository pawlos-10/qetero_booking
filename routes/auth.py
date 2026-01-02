"""
Authentication routes (login, register, logout)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('patient.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validate inputs
        if not email or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('patient.home'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Patient registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('patient.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate inputs
        errors = []
        if not email or not password or not first_name or not last_name:
            errors.append('Please fill in all required fields.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User.create(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role='patient'
        )
        
        try:
            user.save()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

