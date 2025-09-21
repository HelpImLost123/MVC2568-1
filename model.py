# data_manager.py
import json
import os
# Define the file paths for our JSON "databases"
USERS_FILE = 'users.json'
JOBS_FILE = 'jobs.json'
CANDIDATES_FILE = 'candidates.json'
APPLICATIONS_FILE = 'applications.json'
COMPANIES_FILE = 'companies.json'

def load_users():
    """Loads users data from the JSON file."""
    if not os.path.exists(USERS_FILE):
        print(f"Warning: {USERS_FILE} not found. Creating empty users file.")
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print(f"Error: Could not read or decode {USERS_FILE}. Returning an empty list.")
        return []

def save_users(users):
    """Saves users data to the JSON file."""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError:
        print(f"Error: Could not save users to {USERS_FILE}.")

def load_jobs():
    """Loads jobs data from the JSON file."""
    if not os.path.exists(JOBS_FILE):
        print(f"Warning: {JOBS_FILE} not found. Creating empty jobs file.")
        with open(JOBS_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print(f"Error: Could not read or decode {JOBS_FILE}. Returning an empty list.")
        return []

def save_jobs(jobs):
    """Saves jobs data to the JSON file."""
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=4)
    except IOError:
        print(f"Error: Could not save jobs to {JOBS_FILE}.")

def authenticate_user(username, password):
    """Authenticate user credentials and return user data if valid."""
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def load_candidates():
    """Loads candidates data from the JSON file."""
    if not os.path.exists(CANDIDATES_FILE):
        print(f"Warning: {CANDIDATES_FILE} not found. Creating empty candidates file.")
        with open(CANDIDATES_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(CANDIDATES_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print(f"Error: Could not read or decode {CANDIDATES_FILE}. Returning an empty list.")
        return []

def save_candidates(candidates):
    """Saves candidates data to the JSON file."""
    try:
        with open(CANDIDATES_FILE, 'w') as f:
            json.dump(candidates, f, indent=4)
    except IOError:
        print(f"Error: Could not save candidates to {CANDIDATES_FILE}.")

def load_applications():
    """Loads applications data from the JSON file."""
    if not os.path.exists(APPLICATIONS_FILE):
        print(f"Warning: {APPLICATIONS_FILE} not found. Creating empty applications file.")
        with open(APPLICATIONS_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(APPLICATIONS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print(f"Error: Could not read or decode {APPLICATIONS_FILE}. Returning an empty list.")
        return []

def save_applications(applications):
    """Saves applications data to the JSON file."""
    try:
        with open(APPLICATIONS_FILE, 'w') as f:
            json.dump(applications, f, indent=4)
    except IOError:
        print(f"Error: Could not save applications to {APPLICATIONS_FILE}.")

def load_companies():
    """Loads companies data from the JSON file."""
    if not os.path.exists(COMPANIES_FILE):
        print(f"Warning: {COMPANIES_FILE} not found. Creating empty companies file.")
        with open(COMPANIES_FILE, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(COMPANIES_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        print(f"Error: Could not read or decode {COMPANIES_FILE}. Returning an empty list.")
        return []

def save_companies(companies):
    """Saves companies data to the JSON file."""
    try:
        with open(COMPANIES_FILE, 'w') as f:
            json.dump(companies, f, indent=4)
    except IOError:
        print(f"Error: Could not save companies to {COMPANIES_FILE}.")

def get_company_by_id(company_id):
    """Get a specific company by ID."""
    companies = load_companies()
    for company in companies:
        if company['id'] == company_id:
            return company
    return None

def get_candidate_by_id(candidate_id):
    """Get a specific candidate by ID."""
    candidates = load_candidates()
    for candidate in candidates:
        if candidate['id'] == candidate_id:
            return candidate
    return None

def get_user_by_candidate_id(candidate_id):
    """Get user information by candidate ID."""
    users = load_users()
    for user in users:
        if user.get('candidate_id') == candidate_id:
            return user
    return None

def get_applications_with_details():
    """Get all applications with candidate and job details."""
    applications = load_applications()
    candidates = load_candidates()
    jobs = load_jobs()
    
    # Create lookup dictionaries
    candidate_dict = {c['id']: c for c in candidates}
    job_dict = {j['id']: j for j in jobs}
    
    # Combine application data with candidate and job details
    detailed_applications = []
    for app in applications:
        candidate = candidate_dict.get(app['candidate_id'])
        job = job_dict.get(app['job_id'])
        
        if candidate and job:
            detailed_app = {
                'application': app,
                'candidate': candidate,
                'job': job
            }
            detailed_applications.append(detailed_app)
    
    return detailed_applications

def get_applicants():
    """Get all candidates who have made applications."""
    applications = load_applications()
    candidates = load_candidates()
    
    # Get unique candidate IDs from applications
    candidate_ids = list(set(app['candidate_id'] for app in applications))
    
    # Get candidate details for those who have applied
    applicants = []
    for candidate in candidates:
        if candidate['id'] in candidate_ids:
            # Get the most recent application date for this candidate
            candidate_applications = [app for app in applications if app['candidate_id'] == candidate['id']]
            most_recent_app = max(candidate_applications, key=lambda x: x['application_date'])
            
            # Combine candidate info with application info
            applicant = {
                'id': candidate['id'],
                'full_name': f"{candidate['first_name']} {candidate['last_name']}",
                'first_name': candidate['first_name'],
                'last_name': candidate['last_name'],
                'email': candidate['email'],
                'major': candidate['major'],
                'phone': candidate.get('phone', ''),
                'gpa': candidate.get('gpa', ''),
                'application_date': most_recent_app['application_date']
            }
            applicants.append(applicant)
    
    return applicants

def get_applicant_by_id(applicant_id):
    """Get a specific applicant (candidate) by ID with application details."""
    candidate = get_candidate_by_id(applicant_id)
    if not candidate:
        return None
    
    applications = load_applications()
    jobs = load_jobs()
    
    # Get all applications for this candidate
    candidate_applications = [app for app in applications if app['candidate_id'] == applicant_id]
    
    # Get job details for each application
    application_details = []
    for app in candidate_applications:
        job = next((j for j in jobs if j['id'] == app['job_id']), None)
        if job:
            application_details.append({
                'application': app,
                'job': job
            })
    
    # Combine candidate info with application details
    applicant = {
        'id': candidate['id'],
        'full_name': f"{candidate['first_name']} {candidate['last_name']}",
        'first_name': candidate['first_name'],
        'last_name': candidate['last_name'],
        'email': candidate['email'],
        'major': candidate['major'],
        'phone': candidate.get('phone', ''),
        'gpa': candidate.get('gpa', ''),
        'applications': application_details
    }
    
    return applicant

def get_job_by_id(job_id):
    """Get a specific job by ID with company information."""
    jobs = load_jobs()
    companies = load_companies()
    
    # Create company lookup dictionary
    company_dict = {company['id']: company for company in companies}
    
    for job in jobs:
        if job['id'] == job_id:
            # Add company information to job
            job_with_company = job.copy()
            company = company_dict.get(job['company_id'])
            if company:
                job_with_company['company_name'] = company['name']
                job_with_company['company_location'] = company['location']
                job_with_company['company_contact_email'] = company['contact_email']
            return job_with_company
    return None

def get_candidate_by_user_id(user_id):
    """Get candidate information by user ID."""
    users = load_users()
    candidates = load_candidates()
    
    # First find the user
    user = next((u for u in users if u['id'] == user_id), None)
    if not user or user.get('user_type') != 'candidate':
        return None
    
    # Then find the candidate with matching user_id
    candidate = next((c for c in candidates if c.get('user_id') == user_id), None)
    return candidate

def generate_id(prefix):
    """Generate a new 8-digit ID with the specified prefix."""
    import random
    
    # Get all existing IDs based on prefix
    all_ids = []
    
    if prefix == 1:  # Users
        users = load_users()
        all_ids = [user['id'] for user in users]
    elif prefix == 2:  # Candidates
        candidates = load_candidates()
        all_ids = [candidate['id'] for candidate in candidates]
    elif prefix == 3:  # Jobs
        jobs = load_jobs()
        all_ids = [job['id'] for job in jobs]
    elif prefix == 4:  # Applications
        applications = load_applications()
        all_ids = [app['id'] for app in applications]
        
    # Find the maximum existing ID with the given prefix
    max_id = prefix * 10**7 - 1  # Start at prefix0000000
    for existing_id in all_ids:
        if str(existing_id).startswith(str(prefix)):
            if existing_id > max_id:
                max_id = existing_id
    new_id = max_id + 1
    return new_id