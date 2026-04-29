import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models import db, Employer, Applicant, Job, Contact, Application

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ---------- ADMIN CREDENTIALS ----------
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics'), exist_ok=True)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('index.html', jobs=jobs)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_msg = Contact(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()

        flash("Message sent successfully!")
        return redirect(url_for('contactus'))

    return render_template('contactus.html')


@app.route('/register/user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        pwd = generate_password_hash(request.form['password'])

        resume_file = request.files.get('resume')
        resume_path = None
        if resume_file and resume_file.filename:
            filename = secure_filename(resume_file.filename)
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', filename))
            resume_path = f'static/uploads/resumes/{filename}'

        photo_file = request.files.get('photo')
        photo_path = None
        if photo_file and photo_file.filename:
            filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', filename))
            photo_path = f'static/uploads/profile_pics/{filename}'

        a = Applicant(name=name, email=email, password=pwd, resume=resume_path, photo=photo_path)
        db.session.add(a)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for('login'))

    return render_template('register_user.html')


@app.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    if request.method == 'POST':
        name = request.form['name'].strip()
        company = request.form['company'].strip()
        email = request.form['email'].strip()
        pwd = generate_password_hash(request.form['password'])

        logo_file = request.files.get('logo')
        logo_path = None
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', filename))
            logo_path = f'static/uploads/profile_pics/{filename}'

        e = Employer(name=name, company=company, email=email, password=pwd, logo=logo_path)
        db.session.add(e)
        db.session.commit()
        flash("Company Registered!")
        return redirect(url_for('login'))

    return render_template('register_employer.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = Applicant.query.filter_by(email=email).first()
        role = 'applicant'

        if not user:
            user = Employer.query.filter_by(email=email).first()
            role = 'employer'

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = role
            return redirect(url_for('dashboard'))

        flash("Invalid Email or Password")

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session.get('role') == 'employer':
        jobs = Job.query.filter_by(employer_id=session['user_id']).all()
        return render_template('dashboard_employer.html', jobs=jobs)

    elif session.get('role') == 'applicant':
        jobs = Job.query.order_by(Job.id.desc()).all()
        return render_template('dashboard_user.html', jobs=jobs)

    return redirect(url_for('login'))


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'employer':
        return redirect(url_for('login'))

    if request.method == 'POST':

        logo_file = request.files.get('logo')
        logo_path = None
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'profile_pics', filename))
            logo_path = f"static/uploads/profile_pics/{filename}"

        job = Job(
            employer_id=session['user_id'],
            title=request.form['title'],
            company=request.form['company'],
            location=request.form['location'],
            description=request.form['description'],
            salary=request.form['salary'],
            job_type=request.form['job_type'],
            experience=request.form['experience'],
            deadline=request.form['deadline'],
            posted_on=str(date.today()),
            logo=logo_path
        )

        db.session.add(job)
        db.session.commit()
        flash("Job Posted Successfully!")
        return redirect(url_for('dashboard'))

    return render_template('post_job.html')



@app.route('/jobs')
def jobs():
    jobs = Job.query.order_by(Job.id.desc()).all()
    return render_template('jobs.html', jobs=jobs)


@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    if session.get('role') != 'applicant':
        return redirect(url_for('login'))

    job = Job.query.get(job_id)
    user = Applicant.query.get(session['user_id'])

    if request.method == 'POST':
        new_application = Application(
            applicant_name=user.name,
            applicant_email=user.email,
            job_title=job.title,
            company=job.company
        )
        db.session.add(new_application)
        db.session.commit()

        flash("Application Submitted Successfully!")
        return redirect(url_for('jobs'))

    return render_template('apply.html', job=job)



# ---------------- ADMIN PANEL ----------------

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Admin Credentials")

    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    messages = Contact.query.order_by(Contact.id.desc()).all()
    return render_template('admin_dashboard.html', messages=messages)

@app.route('/admin/messages')
def admin_messages():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    messages = Contact.query.order_by(Contact.id.desc()).all()
    return render_template('admin_messages.html', messages=messages)

# ---------- ADMIN VIEW USERS ----------
@app.route('/admin/users')
def admin_users():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    users = Applicant.query.all()
    return render_template('admin_users.html', users=users)


# ---------- ADMIN VIEW EMPLOYERS ----------
@app.route('/admin/employers')
def admin_employers():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    employers = Employer.query.all()
    return render_template('admin_employers.html', employers=employers)


# ---------- ADMIN VIEW JOBS ----------
@app.route('/admin/jobs')
def admin_jobs():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    jobs = Job.query.all()
    return render_template('admin_jobs.html', jobs=jobs)


# ---------- ADMIN DELETE JOB ----------
@app.route('/admin/delete_job/<int:id>')
def admin_delete_job(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    job = Job.query.get(id)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully")
    return redirect(url_for('admin_jobs'))


@app.route('/admin/delete/<int:id>')
def delete_message(id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    msg = Contact.query.get(id)
    db.session.delete(msg)
    db.session.commit()
    flash("Message Deleted!")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/applications')
def admin_applications():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    applications = Application.query.order_by(Application.id.desc()).all()
    return render_template('admin_applications.html', applications=applications)


if __name__ == '__main__':
    app.run(debug=True)
