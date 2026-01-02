"""
Patient routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.models import Doctor, Appointment, Schedule
from utils.decorators import patient_required
from datetime import datetime, date, time, timedelta
from models.database import get_db_connection

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


@patient_bp.route('/')
@patient_bp.route('/home')
@login_required
@patient_required
def home():
    """Patient home page"""
    # Get upcoming appointments using raw SQL for complex query
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = date.today().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE patient_id=? AND status IN ('pending', 'approved') 
        AND appointment_date >= ?
        ORDER BY appointment_date, appointment_time
        LIMIT 5
    ''', (current_user.id, today_str))
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to Appointment objects
    upcoming_appointments = []
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
        appt.patient = current_user
        appt.doctor = Doctor.query.get(row['doctor_id'])
        upcoming_appointments.append(appt)
    
    # Get all active doctors count
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    
    return render_template('patient/home.html', 
                         upcoming_appointments=upcoming_appointments,
                         total_doctors=total_doctors)


@patient_bp.route('/doctors')
@login_required
@patient_required
def doctors():
    """View all doctors"""
    doctors_list = Doctor.query.filter_by(is_active=True).all()
    return render_template('patient/doctors.html', doctors=doctors_list)


@patient_bp.route('/doctor/<int:doctor_id>')
@login_required
@patient_required
def doctor_detail(doctor_id):
    """View doctor details and book appointment"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if not doctor.is_active:
        flash('Doctor is not available.', 'error')
        return redirect(url_for('patient.doctors'))
    
    # Get doctor's schedule
    schedules = Schedule.query.filter_by(doctor_id=doctor_id, is_available=True).all()
    
    # Pass today's date for the date input min attribute
    today = date.today().strftime('%Y-%m-%d')
    
    return render_template('patient/doctor_detail.html', doctor=doctor, schedules=schedules, today=today)


@patient_bp.route('/appointment/book', methods=['POST'])
@login_required
@patient_required
def book_appointment():
    """Book an appointment"""
    doctor_id = request.form.get('doctor_id', type=int)
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    notes = request.form.get('notes', '').strip()
    
    # Validate inputs
    if not doctor_id or not appointment_date or not appointment_time:
        flash('Please fill in all required fields.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Check doctor exists and is active
    doctor = Doctor.query.get(doctor_id)
    if not doctor or not doctor.is_active:
        flash('Doctor not found or not available.', 'error')
        return redirect(url_for('patient.doctors'))
    
    try:
        # Parse date and time
        appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        appt_time = datetime.strptime(appointment_time, '%H:%M').time()
    except ValueError:
        flash('Invalid date or time format.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Check if date is in the future
    if appt_date < date.today():
        flash('Cannot book appointment for past dates.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Check if doctor has schedule for this day
    day_of_week = appt_date.weekday()
    schedule = Schedule.query.filter_by(
        doctor_id=doctor_id,
        day_of_week=day_of_week,
        is_available=True
    ).first()
    
    if not schedule:
        flash('Doctor is not available on this day.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Check if time is within schedule
    if appt_time < schedule.start_time or appt_time >= schedule.end_time:
        flash('Selected time is outside doctor\'s working hours.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Check if appointment already exists at this time using raw SQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE doctor_id=? AND appointment_date=? AND appointment_time=? AND status='approved'
    ''', (doctor_id, appt_date.strftime('%Y-%m-%d'), appt_time.strftime('%H:%M:%S')))
    existing_row = cursor.fetchone()
    conn.close()
    
    if existing_row:
        flash('This time slot is already booked.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))
    
    # Create appointment
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        notes=notes,
        status='pending'
    )
    
    try:
        appointment.save()
        flash('Appointment booked successfully! Waiting for approval.', 'success')
        return redirect(url_for('patient.appointments'))
    except Exception as e:
        flash('Failed to book appointment. Please try again.', 'error')
        return redirect(request.referrer or url_for('patient.doctors'))


@patient_bp.route('/appointments')
@login_required
@patient_required
def appointments():
    """View all patient appointments"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE patient_id=?
        ORDER BY appointment_date DESC, appointment_time DESC
    ''', (current_user.id,))
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
        appt.patient = current_user
        appt.doctor = Doctor.query.get(row['doctor_id'])
        appointments_list.append(appt)
    
    return render_template('patient/appointments.html', appointments=appointments_list)


@patient_bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@login_required
@patient_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify appointment belongs to current user
    if appointment.patient_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('patient.appointments'))
    
    # Only allow cancellation of pending or approved appointments
    if appointment.status not in ['pending', 'approved']:
        flash('Cannot cancel this appointment.', 'error')
        return redirect(url_for('patient.appointments'))
    
    appointment.status = 'cancelled'
    
    try:
        appointment.save()
        flash('Appointment cancelled successfully.', 'success')
    except Exception as e:
        flash('Failed to cancel appointment.', 'error')
    
    return redirect(url_for('patient.appointments'))


@patient_bp.route('/api/available-times/<int:doctor_id>')
@login_required
@patient_required
def get_available_times(doctor_id):
    """Get available appointment times for a doctor on a specific date"""
    appointment_date_str = request.args.get('date')
    
    if not appointment_date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        appt_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get doctor's schedule for this day
    day_of_week = appt_date.weekday()
    schedule = Schedule.query.filter_by(
        doctor_id=doctor_id,
        day_of_week=day_of_week,
        is_available=True
    ).first()
    
    if not schedule:
        return jsonify({'available_times': []})
    
    # Get booked appointments for this date using raw SQL
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT appointment_time FROM appointments 
        WHERE doctor_id=? AND appointment_date=? AND status='approved'
    ''', (doctor_id, appt_date.strftime('%Y-%m-%d')))
    booked_rows = cursor.fetchall()
    conn.close()
    
    booked_times = {time.fromisoformat(row['appointment_time'][:8]) for row in booked_rows if row['appointment_time']}
    
    # Generate available time slots (30-minute intervals)
    available_times = []
    current_time = schedule.start_time
    end_time = schedule.end_time
    
    while current_time < end_time:
        if current_time not in booked_times:
            available_times.append(current_time.strftime('%H:%M'))
        
        # Add 30 minutes
        current_dt = datetime.combine(date.today(), current_time)
        current_dt += timedelta(minutes=30)
        current_time = current_dt.time()
    
    return jsonify({'available_times': available_times})

