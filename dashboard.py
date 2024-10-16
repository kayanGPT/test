from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_socketio import SocketIO
from flask_mail import Mail, Message
from config import load_config
from database_manager import DatabaseManager
import json
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import stripe
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['STRIPE_PUBLIC_KEY'] = os.environ.get('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')

socketio = SocketIO(app)
config = load_config()
db = DatabaseManager(config['DATABASE_URL'])
mail = Mail(app)
stripe.api_key = app.config['STRIPE_SECRET_KEY']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.get_user_by_username(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = db.get_user_by_username(username)
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        db.create_user(username, email, hashed_password)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    projects = db.get_user_projects(user_id)
    return render_template('dashboard.html', projects=projects)

@app.route('/content_calendar')
@login_required
def content_calendar():
    user_id = session['user_id']
    events = db.get_calendar_events(user_id)
    videos = db.get_user_videos(user_id)
    return render_template('content_calendar.html', events=events, videos=videos)

@app.route('/add_calendar_event', methods=['POST'])
@login_required
def add_calendar_event():
    user_id = session['user_id']
    video_id = request.form['video_id']
    platform = request.form['platform']
    scheduled_time = request.form['scheduled_time']
    
    db.add_calendar_event(user_id, video_id, platform, scheduled_time)
    flash('Calendar event added successfully', 'success')
    return redirect(url_for('content_calendar'))

@app.route('/update_calendar_event/<int:event_id>', methods=['POST'])
@login_required
def update_calendar_event(event_id):
    platform = request.form['platform']
    scheduled_time = request.form['scheduled_time']
    status = request.form['status']
    
    db.update_calendar_event(event_id, platform, scheduled_time, status)
    flash('Calendar event updated successfully', 'success')
    return redirect(url_for('content_calendar'))

@app.route('/delete_calendar_event/<int:event_id>', methods=['POST'])
@login_required
def delete_calendar_event(event_id):
    db.delete_calendar_event(event_id)
    flash('Calendar event deleted successfully', 'success')
    return redirect(url_for('content_calendar'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    db.create_tables()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
