from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kumbh-mela-secret-key' # Change for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kumbh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Login Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10)) # 'lost' or 'found'
    name = db.Column(db.String(100), nullable=False) # Item Name OR Person Name
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # --- New Fields for Humans ---
    is_person = db.Column(db.Boolean, default=False)
    age = db.Column(db.String(10), nullable=True) # Changed to string to allow ranges "10-12"
    gender = db.Column(db.String(20), nullable=True)
    height = db.Column(db.String(50), nullable=True)

# Create DB
with app.app_context():
    db.create_all()

# --- Routes ---

@app.route('/')
def index():
    recent_lost = Item.query.filter_by(type='lost').order_by(Item.date_reported.desc()).limit(3).all()
    recent_found = Item.query.filter_by(type='found').order_by(Item.date_reported.desc()).limit(3).all()
    return render_template('index.html', lost_items=recent_lost, found_items=recent_found)

@app.route('/dashboard')
@login_required
def dashboard():
    my_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.date_reported.desc()).all()
    all_items = Item.query.order_by(Item.date_reported.desc()).all()
    return render_template('dashboard.html', my_items=my_items, all_items=all_items)

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- Reporting Routes ---
@app.route('/report/lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        return submit_item('lost')
    return render_template('report_lost.html')

@app.route('/report/found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        return submit_item('found')
    return render_template('report_found.html')

def submit_item(item_type):
    # Determine if it's a person report
    cat = request.form.get('category')
    is_person_report = (cat == 'Missing Person' or cat == 'Found Person')
    
    new_item = Item(
        type=item_type,
        name=request.form['name'],
        category=cat,
        location=request.form['location'],
        description=request.form['description'],
        contact_name=request.form['contact_name'],
        contact_phone=request.form['contact_phone'],
        user_id=current_user.id,
        
        # Human Fields
        is_person=is_person_report,
        age=request.form.get('age') if is_person_report else None,
        gender=request.form.get('gender') if is_person_report else None,
        height=request.form.get('height') if is_person_report else None
    )
    db.session.add(new_item)
    db.session.commit()
    flash(f'{cat} reported successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)