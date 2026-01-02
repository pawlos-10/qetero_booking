from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.models import User, Doctor, Appointment, Schedule
from utils.decorators import admin_required
from datetime import datetime, date, time
from models.database import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Statistics
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = User.query.filter_by(role='patient').count()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM appointments')
    total_appointments = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status='pending'")
    pending_appointments = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM appointments WHERE status='approved'")
    approved_appointments = cursor.fetchone()['count']
    
    # Recent appointments
    cursor.execute('SELECT * FROM appointments ORDER BY created_at DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    
    recent_appointments = []
    for row in rows:
        appt = Appointment(
            id=row['id'],
            patient_id=row['patient_id'],
            doctor_id=row['doctor_id'],
            appointment_date=date.fromisoformat(row['appointment_date']),
            appointment_time=time.fromisoformat(row['appointment_time'][:8]) if row['appointment_time'] else None,
            status=row['status'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        appt.patient = User.query.get(row['patient_id'])
        appt.doctor = Doctor.query.get(row['doctor_id'])
        recent_appointments.append(appt)
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments,
                         approved_appointments=approved_appointments,
                         recent_appointments=recent_appointments)



@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    doctors_list = Doctor.query.filter_by().all()
    return render_template('admin/doctors.html', doctors=doctors_list)


@admin_bp.route('/doctor/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        specialty = request.form.get('specialty', '').strip()
        bio = request.form.get('bio', '').strip()
        is_active = request.form.get('is_active') == 'on'
        
        # Validate inputs
        if not first_name or not last_name or not email or not specialty:
            flash('Please fill in all required fields.', 'error')
            return render_template('admin/doctor_form.html', action='Add')
        
        # Check if email already exists
        if Doctor.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/doctor_form.html', action='Add')
        
        doctor = Doctor(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            specialty=specialty,
            bio=bio,
            is_active=is_active
        )
        
        try:
            doctor.save()
            flash('Doctor added successfully!', 'success')
            return redirect(url_for('admin.doctors'))
        except Exception as e:
            flash('Failed to add doctor. Please try again.', 'error')
    
    return render_template('admin/doctor_form.html', action='Add', doctor=None)


@admin_bp.route('/doctor/<int:doctor_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.first_name = request.form.get('first_name', '').strip()
        doctor.last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        doctor.phone = request.form.get('phone', '').strip()
        doctor.specialty = request.form.get('specialty', '').strip()
        doctor.bio = request.form.get('bio', '').strip()
        doctor.is_active = request.form.get('is_active') == 'on'
        
        # Validate inputs
        if not doctor.first_name or not doctor.last_name or not email or not doctor.specialty:
            flash('Please fill in all required fields.', 'error')
            return render_template('admin/doctor_form.html', action='Edit', doctor=doctor)
        
        # Check email uniqueness if changed
        if email != doctor.email:
            if Doctor.query.filter_by(email=email).first():
                flash('Email already exists.', 'error')
                return render_template('admin/doctor_form.html', action='Edit', doctor=doctor)
            doctor.email = email
        
        try:
            doctor.save()
            flash('Doctor updated successfully!', 'success')
            return redirect(url_for('admin.doctors'))
        except Exception as e:
            flash('Failed to update doctor. Please try again.', 'error')
    
    return render_template('admin/doctor_form.html', action='Edit', doctor=doctor)


@admin_bp.route('/doctor/<int:doctor_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    try:
        doctor.delete()
        flash('Doctor deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete doctor. Please try again.', 'error')
    
    return redirect(url_for('admin.doctors'))


# ==================== SCHEDULE MANAGEMENT ====================

@admin_bp.route('/doctor/<int:doctor_id>/schedules')
@login_required
@admin_required
def doctor_schedules(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    schedules = Schedule.query.filter_by(doctor_id=doctor_id).all()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    return render_template('admin/schedules.html', doctor=doctor, schedules=schedules, days=days)


@admin_bp.route('/doctor/<int:doctor_id>/schedule/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_schedule(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week', type=int)
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        is_available = request.form.get('is_available') == 'on'
        
        if day_of_week is None or not start_time_str or not end_time_str:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('admin.doctor_schedules', doctor_id=doctor_id))
        
        try:
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid time format.', 'error')
            return redirect(url_for('admin.doctor_schedules', doctor_id=doctor_id))
        
        if start_time >= end_time:
            flash('Start time must be before end time.', 'error')
            return redirect(url_for('admin.doctor_schedules', doctor_id=doctor_id))
        
        # Check if schedule already exists
        existing = Schedule.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_of_week
        ).first()
        
        if existing:
            existing.start_time = start_time
            existing.end_time = end_time
            existing.is_available = is_available
            existing.save()
        else:
            schedule = Schedule(
                doctor_id=doctor_id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                is_available=is_available
            )
            schedule.save()
        
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('admin.doctor_schedules', doctor_id=doctor_id))
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return render_template('admin/schedule_form.html', doctor=doctor, days=days)


# ==================== PATIENT MANAGEMENT ====================
@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    """View all patients"""
    patients_list = User.query.filter_by(role='patient').all()
    return render_template('admin/patients.html', patients=patients_list)


@admin_bp.route('/patient/<int:patient_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_patient(patient_id):
    """Delete patient"""
    patient = User.query.get_or_404(patient_id)
    
    if patient.is_admin():
        flash('Cannot delete admin user.', 'error')
        return redirect(url_for('admin.patients'))
    
    try:
        patient.delete()
        flash('Patient deleted successfully!', 'success')
    except Exception as e:
        flash('Failed to delete patient. Please try again.', 'error')
    
    return redirect(url_for('admin.patients'))


# ==================== APPOINTMENT MANAGEMENT ====================

@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    """View all appointments"""
    status_filter = request.args.get('status', 'all')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if status_filter != 'all':
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE status=?
            ORDER BY appointment_date DESC, appointment_time DESC
        ''', (status_filter,))
    else:
        cursor.execute('''
            SELECT * FROM appointments 
            ORDER BY appointment_date DESC, appointment_time DESC
        ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    appointments_list = []
    for row in rows:
        appt = Appointment(
            id=row['id'],
            patient_id=row['patient_id'],
            doctor_id=row['doctor_id'],
            appointment_date=date.fromisoformat(row['appointment_date']),
            appointment_time=time.fromisoformat(row['appointment_time'][:8]) if row['appointment_time'] else None,
            status=row['status'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        appt.patient = User.query.get(row['patient_id'])
        appt.doctor = Doctor.query.get(row['doctor_id'])
        appointments_list.append(appt)
    
    return render_template('admin/appointments.html', 
                         appointments=appointments_list, 
                         status_filter=status_filter)


@admin_bp.route('/appointment/<int:appointment_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_appointment(appointment_id):
    """Approve appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check for conflicts using raw SQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE id != ? AND doctor_id = ? AND appointment_date = ? 
        AND appointment_time = ? AND status = 'approved'
    ''', (appointment_id, appointment.doctor_id, 
          appointment.appointment_date.strftime('%Y-%m-%d'),
          appointment.appointment_time.strftime('%H:%M:%S')))
    conflicting = cursor.fetchone()
    conn.close()
    
    if conflicting:
        flash('Cannot approve. Time slot already booked.', 'error')
        return redirect(url_for('admin.appointments'))
    
    appointment.status = 'approved'
    
    try:
        appointment.save()
        flash('Appointment approved successfully!', 'success')
    except Exception as e:
        flash('Failed to approve appointment.', 'error')
    
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/appointment/<int:appointment_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_appointment(appointment_id):
    """Reject appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    appointment.status = 'rejected'
    
    try:
        appointment.save()
        flash('Appointment rejected.', 'success')
    except Exception as e:
        flash('Failed to reject appointment.', 'error')
    
    return redirect(url_for('admin.appointments'))


@admin_bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_appointment(appointment_id):
    """Cancel appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    appointment.status = 'cancelled'
    
    try:
        appointment.save()
        flash('Appointment cancelled.', 'success')
    except Exception as e:
        flash('Failed to cancel appointment.', 'error')
    
    return redirect(url_for('admin.appointments'))

