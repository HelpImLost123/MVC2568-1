# app.py
from datetime import datetime
from flask import Flask, jsonify, request, render_template, session, redirect, url_for, flash
from model import (load_data, save_data, load_users, save_users, load_jobs, save_jobs, 
                   load_candidates, save_candidates, load_applications, save_applications,
                   load_companies, save_companies, get_company_by_id,
                   authenticate_user, get_applicants, get_applicant_by_id, get_candidate_by_id,
                   get_job_by_id, get_candidate_by_user_id, generate_id)
from functools import wraps
import os
import re

def is_job_open(job):
    """Check if a job is currently open for applications."""
    try:
        current_date = datetime.now().date()
        deadline = datetime.strptime(job['application_deadline'], '%Y-%m-%d').date()
        return current_date <= deadline
    except (ValueError, KeyError):
        return False

def get_application_count(job_id):
    """Get the number of applications for a specific job."""
    applications = load_applications()
    return len([app for app in applications if app['job_id'] == job_id])

def validate_email(email):
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def username_exists(username):
    """Check if username already exists."""
    users = load_users()
    return any(user['username'].lower() == username.lower() for user in users)

def email_exists(email):
    """Check if email already exists in candidates."""
    candidates = load_candidates()
    return any(candidate['email'].lower() == email.lower() for candidate in candidates)

data_store = load_data()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('user_type') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_type'] = user['user_type']
            
            # Get full name based on user type
            if user['user_type'] == 'admin':
                session['full_name'] = 'System Administrator'
            else:
                # Get candidate information using the candidate_id from user
                candidate_id = user.get('candidate_id')
                if candidate_id:
                    candidate = get_candidate_by_id(candidate_id)
                    if candidate:
                        session['full_name'] = f"{candidate['first_name']} {candidate['last_name']}"
                        session['candidate_id'] = candidate['id']
                    else:
                        session['full_name'] = user['username']
                else:
                    session['full_name'] = user['username']
            
            flash(f'Welcome, {session["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        major = request.form.get('major', '').strip()
        phone = request.form.get('phone', '').strip()
        gpa = request.form.get('gpa', '').strip()
        
        # Validation
        errors = []
        
        # Required field validation
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif username_exists(username):
            errors.append('Username already exists. Please choose a different one.')
            
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
            
        if password != confirm_password:
            errors.append('Passwords do not match.')
            
        if not first_name:
            errors.append('First name is required.')
            
        if not last_name:
            errors.append('Last name is required.')
            
        if not email:
            errors.append('Email is required.')
        elif not validate_email(email):
            errors.append('Please enter a valid email address.')
        elif email_exists(email):
            errors.append('Email already registered. Please use a different email.')
            
        if not major:
            errors.append('Major is required.')
            
        if not phone:
            errors.append('Phone number is required.')
            
        if not gpa:
            errors.append('GPA is required.')
        else:
            try:
                gpa_float = float(gpa)
                if gpa_float < 0.0 or gpa_float > 4.0:
                    errors.append('GPA must be between 0.0 and 4.0.')
            except ValueError:
                errors.append('Please enter a valid GPA (e.g., 3.5).')
        
        # If validation fails, return with errors
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user and candidate records
        try:
            # Generate IDs
            user_id = generate_id(1)  # User ID starts with 1
            candidate_id = generate_id(2)  # Candidate ID starts with 2
            
            # Create user record
            new_user = {
                'id': user_id,
                'username': username,
                'password': password,  # In production, this should be hashed
                'user_type': 'candidate',
                'candidate_id': candidate_id
            }
            
            # Create candidate record
            new_candidate = {
                'id': candidate_id,
                'user_id': user_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'major': major,
                'phone': phone,
                'gpa': gpa
            }
            
            # Save to database
            users = load_users()
            candidates = load_candidates()
            
            users.append(new_user)
            candidates.append(new_candidate)
            
            save_users(users)
            save_candidates(candidates)
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('applicant_dashboard'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    applicants = get_applicants()
    return render_template('applicant_list.html', applicants=applicants)

@app.route('/admin/jobs')
@admin_required
def admin_jobs():
    """Admin view of all job listings with application counts."""
    jobs = load_jobs()
    companies = load_companies()
    
    # Create company lookup dictionary
    company_dict = {company['id']: company for company in companies}
    
    jobs_with_counts = []
    for job in jobs:
        job_with_count = job.copy()
        job_with_count['application_count'] = get_application_count(job['id'])
        job_with_count['is_open'] = is_job_open(job)
        # Add company information
        company = company_dict.get(job['company_id'])
        if company:
            job_with_count['company_name'] = company['name']
            job_with_count['company_location'] = company['location']
        jobs_with_counts.append(job_with_count)
    
    return render_template('admin_jobs.html', jobs=jobs_with_counts)

@app.route('/admin/applicant/<int:applicant_id>')
@admin_required
def applicant_details(applicant_id):
    """Show detailed information for a specific applicant."""
    applicant = get_applicant_by_id(applicant_id)
    if not applicant:
        flash('Applicant not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    return render_template('applicant_details.html', applicant=applicant)

@app.route('/jobs')
@login_required
def applicant_dashboard():
    """Applicant dashboard showing job listings."""
    jobs = load_jobs()
    companies = load_companies()
    
    # Create company lookup dictionary
    company_dict = {company['id']: company for company in companies}
    
    # Filter jobs based on user type
    if session.get('user_type') == 'admin':
        # Admin sees all jobs with application counts
        filtered_jobs = []
        for job in jobs:
            job_with_details = job.copy()
            job_with_details['application_count'] = get_application_count(job['id'])
            job_with_details['is_open'] = is_job_open(job)
            # Add company information
            company = company_dict.get(job['company_id'])
            if company:
                job_with_details['company_name'] = company['name']
                job_with_details['company_location'] = company['location']
            filtered_jobs.append(job_with_details)
    else:
        # Candidates only see jobs that are currently open for applications
        filtered_jobs = []
        for job in jobs:
            if is_job_open(job) and job.get('application_status') == 'open':
                job_with_details = job.copy()
                # Add company information
                company = company_dict.get(job['company_id'])
                if company:
                    job_with_details['company_name'] = company['name']
                    job_with_details['company_location'] = company['location']
                filtered_jobs.append(job_with_details)
    
    return render_template('jobs.html', jobs=filtered_jobs)

@app.route('/job/<int:job_id>')
@login_required
def job_details(job_id):
    """Show detailed information for a specific job."""
    job = get_job_by_id(job_id)
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('applicant_dashboard'))
    
    # Check if user has already applied (for candidates only)
    has_applied = False
    job_is_open = is_job_open(job)
    
    if session.get('user_type') == 'candidate':
        user_id = session.get('user_id')
        candidate = get_candidate_by_user_id(user_id)
        if candidate:
            applications = load_applications()
            has_applied = any(app['candidate_id'] == candidate['id'] and app['job_id'] == job_id 
                            for app in applications)
    
    return render_template('job_details.html', job=job, has_applied=has_applied, job_is_open=job_is_open)

@app.route('/apply/<int:job_id>', methods=['POST'])
@login_required
def apply_to_job(job_id):
    """Apply to a specific job (candidates only)."""
    if session.get('user_type') != 'candidate':
        flash('Only candidates can apply to jobs.', 'error')
        return redirect(url_for('job_details', job_id=job_id))
    
    # Get the job and validate it exists
    job = get_job_by_id(job_id)
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('applicant_dashboard'))
    
    # Check if the application deadline has passed
    if not is_job_open(job):
        flash('Sorry, the application deadline for this position has passed.', 'error')
        return redirect(url_for('job_details', job_id=job_id))
    
    user_id = session.get('user_id')
    candidate = get_candidate_by_user_id(user_id)
    
    if not candidate:
        flash('Candidate profile not found.', 'error')
        return redirect(url_for('applicant_dashboard'))
    
    # Check if already applied
    applications = load_applications()
    if any(app['candidate_id'] == candidate['id'] and app['job_id'] == job_id 
           for app in applications):
        flash('You have already applied to this job.', 'warning')
        return redirect(url_for('job_details', job_id=job_id))
    
    # Create new application
    new_application = {
        'id': generate_id(4),  # Application ID starts with 4
        'candidate_id': candidate['id'],
        'job_id': job_id,
        'application_date': datetime.now().strftime('%Y-%m-%d'),  # Store as string
        'status': 'pending'
    }
    
    applications.append(new_application)
    save_applications(applications)
    
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('job_details', job_id=job_id))

# API route to get all data from the data_store.
# This is a Controller function that retrieves data from the Model and returns it.
@app.route('/api/data', methods=['GET'])
def get_data():
    data_store = load_data()
    return jsonify(data_store)

# API route to add new data to the data_store.
# This is a Controller function that receives new data from the client,
# updates the Model, and saves it.
@app.route('/api/add-data', methods=['POST'])
def add_data():
    new_item = request.json
    # Assign a new ID to the item based on the current data_store
    new_item['id'] = len(data_store) + 1
    data_store.append(new_item)
    
    # Save the updated data_store to the file using the imported function
    save_data(data_store)
    
    return jsonify({"message": "Item added successfully!", "item": new_item})

# API routes for jobs
@app.route('/api/jobs', methods=['GET'])
@login_required
def get_jobs():
    """API endpoint to get all job listings."""
    jobs = load_jobs()
    return jsonify(jobs)

@app.route('/api/applicants', methods=['GET'])
@admin_required
def get_applicants_api():
    """API endpoint to get all applicants (admin only)."""
    applicants = get_applicants()
    return jsonify(applicants)

if __name__ == '__main__':
    # You can change the port and debug settings as needed
    app.run(debug=True, port=5000)
