# Qetero Booking System

A complete, production-ready clinic appointment booking system built with Python Flask.

## Features

### Patient Features
- Patient registration and authentication
- Browse available doctors and their specialties
- Book appointments with date and time selection
- View appointment status (pending, approved, rejected, cancelled)
- Cancel pending/approved appointments
- View upcoming appointments on dashboard

### Admin Features
- Secure admin authentication
- Admin dashboard with statistics
- Manage doctors (add, edit, delete, activate/deactivate)
- Manage doctor schedules (set working hours per day)
- View and manage all patients
- Approve/reject/cancel appointments
- Role-based access control

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (easily migratable to PostgreSQL)
- **ORM**: Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6)
- **Templates**: Jinja2

## Project Structure

```
qetero-booking/
│
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
│
├── models/
│   └── models.py          # Database models (User, Doctor, Appointment, Schedule)
│
├── routes/
│   ├── auth.py           # Authentication routes (login, register, logout)
│   ├── patient.py        # Patient routes
│   └── admin.py          # Admin routes
│
├── templates/
│   ├── base.html         # Base template
│   ├── auth/             # Authentication templates
│   ├── patient/          # Patient templates
│   └── admin/            # Admin templates
│
├── static/
│   ├── css/
│   │   └── main.css      # Main stylesheet with color system
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   └── assets/           # Static assets
│
└── utils/
    └── decorators.py     # Custom decorators (admin_required, patient_required)
```

## Color System

The system uses CSS variables for consistent theming:

- **Primary Color**: `#0A1A2F` (dark navy)
- **Secondary Color**: `#00D4AA` (teal accent)
- **Light Background**: `#F8FAFC`
- **Gray Background**: `#F1F5F9`
- **Dark Text**: `#0F172A`
- **Alert/Error**: `#FF4D94`

All colors are defined in `:root` CSS variables in `static/css/main.css`.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. **Clone or download the project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:5000`
   - The database will be automatically initialized on first run

## Default Credentials

### Admin Account
- **Email**: `admin@qetero.com`
- **Password**: `admin123`

**Important**: Change the admin password after first login for production use!

## Database

The system uses SQLite by default (`qetero_booking.db`). The database file is automatically created on first run.


## Usage Guide

### For Patients

1. **Register an account**
   - Click "Register" on the login page
   - Fill in your details and create a password

2. **Login**
   - Use your registered email and password

3. **Browse doctors**
   - Click "Doctors" to view all available doctors
   - Click "View Details & Book" to see doctor information and schedule

4. **Book an appointment**
   - Select a date and time
   - Add optional notes
   - Submit the booking request
   - Wait for admin approval

5. **View appointments**
   - Go to "My Appointments" to see all your appointments
   - Check the status of each appointment
   - Cancel appointments if needed

### For Admins

1. **Login**
   - Use the admin credentials (default: admin@qetero.com / admin123)

2. **Dashboard**
   - View statistics about doctors, patients, and appointments
   - See recent appointments

3. **Manage Doctors**
   - Add new doctors with their specialties and contact information
   - Edit doctor details
   - Set doctor schedules (working hours per day)
   - Activate/deactivate doctors

4. **Manage Appointments**
   - View all appointments with status filter
   - Approve or reject pending appointments
   - Cancel appointments if needed

5. **Manage Patients**
   - View all registered patients
   - Delete patient accounts if needed

## Security Features

- Password hashing using Werkzeug
- Role-based access control
- Protected routes using decorators
- Session management with Flask-Login
- CSRF protection (can be added with Flask-WTF)

## Development

### Running in Development Mode

The app runs in debug mode by default when using `python app.py`. For production:

1. Set `debug=False` in `app.py`
2. Use a production WSGI server (e.g., Gunicorn, uWSGI)
3. Set proper `SECRET_KEY` in environment variables
4. Use a production database (PostgreSQL recommended)

### Code Structure

- **Models**: Define database schema and relationships
- **Routes**: Handle HTTP requests and business logic
- **Templates**: Jinja2 templates for HTML rendering
- **Static**: CSS, JavaScript, and other static files
- **Utils**: Reusable utilities and decorators

## API Endpoints

### Patient API
- `GET /patient/api/available-times/<doctor_id>?date=YYYY-MM-DD` - Get available appointment times for a doctor on a specific date

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is open source and available for educational and commercial use.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Qetero Booking** - Making healthcare appointment management simple and efficient.

