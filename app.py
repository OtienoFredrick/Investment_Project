from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_migrate import Migrate  # Import Flask-Migrate
import os
import binascii

app = Flask(__name__)

# Configuration
app.secret_key = 'your_secret_key'  # Replace with a strong random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Database URI (SQLite in this case)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy event system to save memory

# Mail Configuration (replace with your actual email credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'fredrickotieno768@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'mbbh rfmf exnk ogtn'  # Replace with your email password
mail = Mail(app)

# Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# User Model (represents a user in the database)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)

# Create the database (Only if not already created)
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    """Redirect to the login page by default."""
    return render_template('layout.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        # Process form data here (you can access it using request.form)
        # For example:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Do something with the data, e.g., send an email or save to the database
        return redirect(url_for('home'))  # Redirect after submission
    return render_template('layout.html')  # If it's a GET request, render layout.html


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists and if the password matches
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))

        # Hash the password and save the new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests."""
    if request.method == 'POST':
        email = request.form['email']

        # Check if the user exists
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a reset token (using a secure random hex string)
            reset_token = binascii.hexlify(os.urandom(16)).decode()
            user.reset_token = reset_token
            db.session.commit()

            # Send reset email with the reset URL
            reset_url = url_for('reset_password', token=reset_token, _external=True)
            msg = Message('Password Reset Request', sender='your_email@gmail.com', recipients=[email])
            msg.body = f'Click the following link to reset your password: {reset_url}'
            mail.send(msg)

            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found. Please check again.', 'danger')

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset form submission."""
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('Invalid or expired token.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate the new passwords match
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('reset_password', token=token))

        # Hash the new password and update the user's password
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        user.reset_token = None  # Clear the reset token once password is updated
        db.session.commit()

        flash('Your password has been updated.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/dashboard')
def dashboard():
    """Dashboard route, only accessible if logged in."""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    """Logout the user and redirect to login page."""
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
