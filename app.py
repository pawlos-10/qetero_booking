from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager
from config import SECRET_KEY
from models.models import User
from models.database import init_db as init_database
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('profile.html')


def init_db():
    init_database()
    
    # Check if admin user exists
    admin_email = 'admin@qetero.com'
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        admin = User.create(
            email=admin_email,
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.save()

if __name__ == '__main__':
    init_db()    
    app.run(debug=True, host='0.0.0.0', port=1234)

