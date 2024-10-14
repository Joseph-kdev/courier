from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from datetime import datetime

users = Blueprint("users", __name__, template_folder="templates", static_folder="static")

db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'client', 'driver', 'admin'
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    posted_jobs = db.relationship('Job', back_populates='client', foreign_keys='Job.client_id')
    applied_jobs = db.relationship('JobApplication', back_populates='driver')
    received_ratings = db.relationship('Rating', back_populates='driver', foreign_keys='Rating.driver_id')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_location = db.Column(db.String(100), nullable=False)
    end_location = db.Column(db.String(100), nullable=False)
    estimated_time = db.Column(db.Integer, nullable=False)
    payment = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'completed_by_driver', 'paid', 'rated'
    applications = db.relationship('JobApplication', back_populates='job', lazy='dynamic')
    client = db.relationship('User', back_populates='posted_jobs')
    rating = db.relationship('Rating', back_populates='job', uselist=False)

class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    proposed_fee = db.Column(db.Float, nullable=False)
    job = db.relationship('Job', back_populates='applications')
    driver = db.relationship('User', back_populates='applied_jobs')

    @property
    def applicant(self):
        return self.driver

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    job = db.relationship('Job', back_populates='rating')
    client = db.relationship('User', foreign_keys=[client_id])
    driver = db.relationship('User', foreign_keys=[driver_id], back_populates='received_ratings')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@users.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('landing_page.jobs'))
        else:
            flash('Invalid email or password')
    return render_template("login.html")

@users.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered')
        else:
            new_user = User(name=name, email=email, user_type='client')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('landing_page.jobs'))
    return render_template("landing_page.jobs")

@users.route("/post_job", methods=["GET", "POST"])
@login_required
def post_job():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        start_location = request.form.get("start_location")
        end_location = request.form.get("end_location")
        estimated_time = int(request.form.get("estimated_time"))
        payment = float(request.form.get("payment"))
        new_job = Job(
            title=title,
            description=description,
            start_location=start_location,
            end_location=end_location,
            estimated_time=estimated_time,
            payment=payment,
            client_id=current_user.id
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully')
        return redirect(url_for('landing_page.jobs'))
    return render_template("post_job.html")

@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing_page.home'))

@users.route("/profile")
@login_required
def profile():
    if current_user.user_type == 'client':
        posted_jobs = Job.query.filter_by(client_id=current_user.id).order_by(Job.created_at.desc()).all()
        for job in posted_jobs:
            job.applications = JobApplication.query.filter_by(job_id=job.id).order_by(JobApplication.proposed_fee.asc()).all()
    else:
        posted_jobs = None
    return render_template("profile.html", user=current_user, posted_jobs=posted_jobs)

@users.route("/apply_job/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    if current_user.user_type != 'driver':
        flash('Only drivers can apply for jobs.', 'error')
        return redirect(url_for('landing_page.jobs'))

    job = Job.query.get_or_404(job_id)
    if job.status != 'open':
        flash('This job is no longer open for bids.', 'error')
        return redirect(url_for('landing_page.jobs'))

    proposed_fee = float(request.form.get('proposed_fee'))
    existing_application = JobApplication.query.filter_by(job_id=job.id, driver_id=current_user.id).first()

    if existing_application:
        existing_application.proposed_fee = proposed_fee
        existing_application.status = 'pending'  # Reset status if updating bid
        flash('Your bid has been updated.', 'success')
    else:
        new_application = JobApplication(job_id=job.id, driver_id=current_user.id, status='pending', proposed_fee=proposed_fee)
        db.session.add(new_application)
        flash('Your bid has been submitted.', 'success')

    db.session.commit()
    return redirect(url_for('landing_page.jobs'))

@users.route("/accept_offer/<int:application_id>", methods=["POST"])
@login_required
def accept_offer(application_id):
    if current_user.user_type != 'client':
        flash('Only clients can accept offers.', 'error')
        return redirect(url_for('users.profile'))

    application = JobApplication.query.get_or_404(application_id)
    job = application.job

    if job.client_id != current_user.id:
        flash('You can only accept offers for your own jobs.', 'error')
        return redirect(url_for('users.profile'))

    if job.status != 'open':
        flash('This job is no longer open.', 'error')
        return redirect(url_for('users.profile'))

    # Update the accepted application
    application.status = 'accepted'
    job.status = 'in_progress'

    # Reject all other applications for this job
    for other_application in job.applications:
        if other_application.id != application.id:
            other_application.status = 'rejected'

    db.session.commit()
    flash('Offer accepted successfully. The job is now in progress.', 'success')
    return redirect(url_for('users.profile'))

@users.route("/delete_job/<int:job_id>", methods=["POST"])
@login_required
def delete_job(job_id):
    if current_user.user_type != 'client':
        flash('Only clients can delete jobs.', 'error')
        return redirect(url_for('users.profile'))

    job = Job.query.get_or_404(job_id)

    if job.client_id != current_user.id:
        flash('You can only delete your own jobs.', 'error')
        return redirect(url_for('users.profile'))

    # Delete associated applications first
    JobApplication.query.filter_by(job_id=job.id).delete()

    # Now delete the job
    db.session.delete(job)
    db.session.commit()

    flash('Job deleted successfully.', 'success')
    return redirect(url_for('users.profile'))

@users.route("/mark_job_completed/<int:job_id>", methods=["POST"])
@login_required
def mark_job_completed(job_id):
    if current_user.user_type != 'driver':
        flash('Only drivers can mark jobs as completed.', 'error')
        return redirect(url_for('users.profile'))

    job = Job.query.get_or_404(job_id)
    accepted_application = job.applications.filter_by(driver_id=current_user.id, status='accepted').first()

    if not accepted_application:
        flash('You can only mark jobs you have been accepted for as completed.', 'error')
        return redirect(url_for('users.profile'))

    job.status = 'completed_by_driver'
    db.session.commit()
    flash('Job marked as completed. Waiting for client to confirm payment.', 'success')
    return redirect(url_for('users.profile'))

@users.route("/mark_job_paid/<int:job_id>", methods=["POST"])
@login_required
def mark_job_paid(job_id):
    if current_user.user_type != 'client':
        flash('Only clients can mark jobs as paid.', 'error')
        return redirect(url_for('users.profile'))

    job = Job.query.get_or_404(job_id)
    if job.client_id != current_user.id:
        flash('You can only mark your own jobs as paid.', 'error')
        return redirect(url_for('users.profile'))

    if job.status != 'completed_by_driver':
        flash('You can only mark jobs that have been completed by the driver as paid.', 'error')
        return redirect(url_for('users.profile'))

    job.status = 'paid'
    db.session.commit()
    flash('Job marked as paid. Please rate the driver.', 'success')
    return redirect(url_for('users.profile'))

@users.route("/rate_driver/<int:job_id>", methods=["GET", "POST"])
@login_required
def rate_driver(job_id):
    job = Job.query.get_or_404(job_id)
    if job.client_id != current_user.id:
        flash('You can only rate drivers for your own jobs.', 'error')
        return redirect(url_for('users.profile'))

    if request.method == "POST":
        rating_value = int(request.form.get('rating'))
        comment = request.form.get('comment')
        driver = User.query.get(job.applications.filter_by(status='accepted').first().driver_id)

        new_rating = Rating(job_id=job.id, client_id=current_user.id, driver_id=driver.id, rating=rating_value, comment=comment)
        db.session.add(new_rating)

        # Update driver's overall rating
        driver.rating = (driver.rating * driver.rating_count + rating_value) / (driver.rating_count + 1)
        driver.rating_count += 1

        job.status = 'rated'
        db.session.commit()

        flash('Driver rated successfully.', 'success')
        return redirect(url_for('users.profile'))

    return render_template('rate_driver.html', job=job)