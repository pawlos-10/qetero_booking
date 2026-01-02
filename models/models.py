from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time
from models.database import get_db_connection


def parse_datetime(value):
    """Parse various timestamp formats into a datetime object, or return None/unchanged value."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        # Handles 'YYYY-MM-DD HH:MM:SS' and ISO formats
        return datetime.fromisoformat(str(value))
    except Exception:
        try:
            return datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
        except Exception:
            return value


class QueryProperty:
    """Descriptor to make query accessible as a property"""
    def __init__(self, query_class):
        self.query_class = query_class
    
    def __get__(self, instance, owner):
        return self.query_class()


class User:
    """User model"""
    
    def __init__(self, id=None, email=None, password_hash=None, first_name=None, 
                 last_name=None, phone=None, role='patient', created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.role = role
        self.created_at = parse_datetime(created_at)
        self._is_authenticated = True
        self._is_active = True
        self._is_anonymous = False
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def get_id(self):
        """Get user ID for Flask-Login"""
        return str(self.id) if self.id else None
    
    def is_authenticated(self):
        return self._is_authenticated
    
    def is_active(self):
        return self._is_active
    
    def is_anonymous(self):
        return self._is_anonymous
    
    query = QueryProperty(lambda: UserQuery())
    
    @staticmethod
    def create(email, password, first_name, last_name, phone=None, role='patient'):
        """Create new user"""
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )
        user.set_password(password)
        return user
    
    def save(self):
        """Save user to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if self.id:
            # Update
            cursor.execute('''
                UPDATE users 
                SET email=?, password_hash=?, first_name=?, last_name=?, phone=?, role=?
                WHERE id=?
            ''', (self.email, self.password_hash, self.first_name, 
                  self.last_name, self.phone, self.role, self.id))
        else:
            # Insert
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, role)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.email, self.password_hash, self.first_name, 
                  self.last_name, self.phone, self.role))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """Delete user from database"""
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id=?', (self.id,))
            conn.commit()
            conn.close()


class UserQuery:
    """User query helper"""
    
    def filter_by(self, **kwargs):
        self._filters = kwargs
        return self
    
    def first(self):
        """Get first matching user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT * FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " LIMIT 1"
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None
    
    def get(self, user_id):
        """Get user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                phone=row['phone'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None
    
    def all(self):
        """Get all matching users"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT * FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY first_name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [User(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            phone=row['phone'],
            role=row['role'],
            created_at=row['created_at']
        ) for row in rows]
    
    def count(self):
        """Count matching users"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT COUNT(*) as count FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result['count']


class Doctor:
    """Doctor model"""
    
    def __init__(self, id=None, first_name=None, last_name=None, email=None,
                 phone=None, specialty=None, bio=None, is_active=True, created_at=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.specialty = specialty
        self.bio = bio
        self.is_active = bool(is_active) if isinstance(is_active, int) else is_active
        self.created_at = parse_datetime(created_at)
    
    @property
    def full_name(self):
        """Get doctor's full name"""
        return f"{self.first_name} {self.last_name}"
    
    query = QueryProperty(lambda: DoctorQuery())
    
    def save(self):
        """Save doctor to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        is_active_int = 1 if self.is_active else 0
        
        if self.id:
            cursor.execute('''
                UPDATE doctors 
                SET first_name=?, last_name=?, email=?, phone=?, specialty=?, bio=?, is_active=?
                WHERE id=?
            ''', (self.first_name, self.last_name, self.email, self.phone,
                  self.specialty, self.bio, is_active_int, self.id))
        else:
            cursor.execute('''
                INSERT INTO doctors (first_name, last_name, email, phone, specialty, bio, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.first_name, self.last_name, self.email, self.phone,
                  self.specialty, self.bio, is_active_int))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """Delete doctor from database"""
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM doctors WHERE id=?', (self.id,))
            conn.commit()
            conn.close()


class DoctorQuery:
    """Doctor query helper"""
    
    def filter_by(self, **kwargs):
        self._filters = kwargs
        return self
    
    def get_or_404(self, doctor_id):
        """Get doctor by ID or return 404"""
        doctor = self.get(doctor_id)
        if not doctor:
            from flask import abort
            abort(404)
        return doctor
    
    def get(self, doctor_id):
        """Get doctor by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM doctors WHERE id=?', (doctor_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Doctor(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                specialty=row['specialty'],
                bio=row['bio'],
                is_active=row['is_active'],
                created_at=row['created_at']
            )
        return None
    
    def first(self):
        """Get first matching doctor"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            if key == 'is_active':
                value = 1 if value else 0
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT * FROM doctors"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " LIMIT 1"
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Doctor(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                email=row['email'],
                phone=row['phone'],
                specialty=row['specialty'],
                bio=row['bio'],
                is_active=row['is_active'],
                created_at=row['created_at']
            )
        return None
    
    def all(self):
        """Get all matching doctors"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            if key == 'is_active':
                value = 1 if value else 0
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT * FROM doctors"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY first_name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [Doctor(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            email=row['email'],
            phone=row['phone'],
            specialty=row['specialty'],
            bio=row['bio'],
            is_active=row['is_active'],
            created_at=row['created_at']
        ) for row in rows]
    
    def count(self):
        """Count matching doctors"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            if key == 'is_active':
                value = 1 if value else 0
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT COUNT(*) as count FROM doctors"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result['count']


class Schedule:
    """Schedule model"""
    
    def __init__(self, id=None, doctor_id=None, day_of_week=None,
                 start_time=None, end_time=None, is_available=True, created_at=None):
        self.id = id
        self.doctor_id = doctor_id
        self.day_of_week = day_of_week
        self.start_time = start_time if isinstance(start_time, time) or start_time is None else time.fromisoformat(str(start_time))
        self.end_time = end_time if isinstance(end_time, time) or end_time is None else time.fromisoformat(str(end_time))
        self.is_available = bool(is_available) if isinstance(is_available, int) else is_available
        self.created_at = parse_datetime(created_at)
        self.doctor = None  # For relationship
    
    query = QueryProperty(lambda: ScheduleQuery())
    
    def save(self):
        """Save schedule to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_time_str = self.start_time.strftime('%H:%M:%S') if isinstance(self.start_time, time) else str(self.start_time)
        end_time_str = self.end_time.strftime('%H:%M:%S') if isinstance(self.end_time, time) else str(self.end_time)
        is_available_int = 1 if self.is_available else 0
        
        if self.id:
            cursor.execute('''
                UPDATE schedules 
                SET doctor_id=?, day_of_week=?, start_time=?, end_time=?, is_available=?
                WHERE id=?
            ''', (self.doctor_id, self.day_of_week, start_time_str, end_time_str, is_available_int, self.id))
        else:
            cursor.execute('''
                INSERT INTO schedules (doctor_id, day_of_week, start_time, end_time, is_available)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.doctor_id, self.day_of_week, start_time_str, end_time_str, is_available_int))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self


class ScheduleQuery:
    """Schedule query helper"""
    
    def filter_by(self, **kwargs):
        self._filters = kwargs
        return self
    
    def all(self):
        """Get all matching schedules"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        for key, value in self._filters.items():
            if key == 'is_available':
                value = 1 if value else 0
            conditions.append(f"{key}=?")
            params.append(value)
        
        query = "SELECT * FROM schedules"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY day_of_week"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        schedules = []
        for row in rows:
            start_time = time.fromisoformat(row['start_time']) if ':' in str(row['start_time']) else time.fromisoformat(str(row['start_time'])[:8])
            end_time = time.fromisoformat(row['end_time']) if ':' in str(row['end_time']) else time.fromisoformat(str(row['end_time'])[:8])
            schedule = Schedule(
                id=row['id'],
                doctor_id=row['doctor_id'],
                day_of_week=row['day_of_week'],
                start_time=start_time,
                end_time=end_time,
                is_available=row['is_available'],
                created_at=row['created_at']
            )
            # Load doctor relationship if needed
            schedule.doctor = Doctor.query.get(row['doctor_id'])
            schedules.append(schedule)
        
        return schedules
    
    def first(self):
        """Get first matching schedule"""
        schedules = self.all()
        return schedules[0] if schedules else None


class Appointment:
    """Appointment model"""
    
    def __init__(self, id=None, patient_id=None, doctor_id=None,
                 appointment_date=None, appointment_time=None, status='pending',
                 notes=None, created_at=None, updated_at=None):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date if isinstance(appointment_date, date) or appointment_date is None else date.fromisoformat(str(appointment_date))
        self.appointment_time = appointment_time if isinstance(appointment_time, time) or appointment_time is None else time.fromisoformat(str(appointment_time))
        self.status = status
        self.notes = notes
        self.created_at = parse_datetime(created_at)
        self.updated_at = parse_datetime(updated_at)
        self.patient = None  # For relationship
        self.doctor = None  # For relationship
    
    query = QueryProperty(lambda: AppointmentQuery())
    
    def save(self):
        """Save appointment to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        date_str = self.appointment_date.strftime('%Y-%m-%d') if isinstance(self.appointment_date, date) else str(self.appointment_date)
        time_str = self.appointment_time.strftime('%H:%M:%S') if isinstance(self.appointment_time, time) else str(self.appointment_time)
        
        if self.id:
            cursor.execute('''
                UPDATE appointments 
                SET patient_id=?, doctor_id=?, appointment_date=?, appointment_time=?, 
                    status=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (self.patient_id, self.doctor_id, date_str, time_str,
                  self.status, self.notes, self.id))
        else:
            cursor.execute('''
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.patient_id, self.doctor_id, date_str, time_str,
                  self.status, self.notes))
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self
    
    def delete(self):
        """Delete appointment from database"""
        if self.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM appointments WHERE id=?', (self.id,))
            conn.commit()
            conn.close()


class AppointmentQuery:
    """Appointment query helper"""
    
    def filter(self, *conditions):
        """Complex filter conditions"""
        self._filter_conditions = conditions
        return self
    
    def filter_by(self, **kwargs):
        self._filters = kwargs
        return self
    
    def get_or_404(self, appointment_id):
        """Get appointment by ID or return 404"""
        appointment = self.get(appointment_id)
        if not appointment:
            from flask import abort
            abort(404)
        return appointment
    
    def get(self, appointment_id):
        """Get appointment by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE id=?', (appointment_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            appointment = self._row_to_appointment(row)
            self._load_relationships(appointment)
            return appointment
        return None
    
    def first(self):
        """Get first matching appointment"""
        appointments = self.all()
        return appointments[0] if appointments else None
    
    def all(self):
        """Get all matching appointments"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        # Handle filter_by
        if hasattr(self, '_filters'):
            for key, value in self._filters.items():
                if key == 'status' and hasattr(value, '__iter__') and not isinstance(value, str):
                    # Handle .in_() case
                    placeholders = ','.join(['?' for _ in value])
                    conditions.append(f"{key} IN ({placeholders})")
                    params.extend(value)
                else:
                    conditions.append(f"{key}=?")
                    params.append(value)
        
        # Handle filter conditions (like >=)
        if hasattr(self, '_filter_conditions'):
            for condition in self._filter_conditions:
                # Simple condition parsing
                if hasattr(condition, 'left') and hasattr(condition, 'right'):
                    # SQLAlchemy-like condition
                    left = condition.left.key if hasattr(condition.left, 'key') else condition.left
                    op = '>=' if 'ge' in str(type(condition)) else '='  # Simplified
                    right = condition.right
                    conditions.append(f"{left} {op} ?")
                    params.append(right)
        
        query = "SELECT * FROM appointments"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Handle order_by
        if hasattr(self, '_order_by'):
            query += " ORDER BY " + self._order_by
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        appointments = [self._row_to_appointment(row) for row in rows]
        for appointment in appointments:
            self._load_relationships(appointment)
        
        return appointments
    
    def order_by(self, *args):
        """Order results"""
        order_parts = []
        for arg in args:
            if hasattr(arg, 'key'):
                order_parts.append(f"{arg.key} {arg.direction if hasattr(arg, 'direction') else 'ASC'}")
            else:
                order_parts.append(str(arg))
        self._order_by = ", ".join(order_parts)
        return self
    
    def limit(self, num):
        """Limit results"""
        self._limit = num
        return self
    
    def count(self):
        """Count matching appointments"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        if hasattr(self, '_filters'):
            for key, value in self._filters.items():
                conditions.append(f"{key}=?")
                params.append(value)
        
        query = "SELECT COUNT(*) as count FROM appointments"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result['count']
    
    def _row_to_appointment(self, row):
        """Convert database row to Appointment object"""
        appointment_date = date.fromisoformat(row['appointment_date']) if row['appointment_date'] else None
        appointment_time = time.fromisoformat(row['appointment_time'][:8]) if row['appointment_time'] and ':' in str(row['appointment_time']) else None
        
        return Appointment(
            id=row['id'],
            patient_id=row['patient_id'],
            doctor_id=row['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=row['status'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _load_relationships(self, appointment):
        """Load related patient and doctor"""
        appointment.patient = User.query.get(appointment.patient_id)
        appointment.doctor = Doctor.query.get(appointment.doctor_id)
