from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Employer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    company = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    logo = db.Column(db.String(255))

class Applicant(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    resume = db.Column(db.String(255))
    photo = db.Column(db.String(255))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))

    title = db.Column(db.String(200))
    company = db.Column(db.String(150))
    location = db.Column(db.String(150))
    description = db.Column(db.Text)

    salary = db.Column(db.String(100))
    job_type = db.Column(db.String(50))
    experience = db.Column(db.String(50))
    deadline = db.Column(db.String(50))
    posted_on = db.Column(db.String(50))

    logo = db.Column(db.String(255))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    message = db.Column(db.Text)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(150))
    applicant_email = db.Column(db.String(150))
    job_title = db.Column(db.String(150))
    company = db.Column(db.String(150))
