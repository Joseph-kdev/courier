from flask import Blueprint, render_template, url_for, redirect
from flask_login import current_user
from blueprints.user_page.users import Job, JobApplication
from sqlalchemy.orm import joinedload

landing_page = Blueprint("landing_page", __name__, template_folder="templates", static_folder="static")

@landing_page.route("/")
def home():
    return render_template("index.html")

@landing_page.route("/jobs")
def jobs():
    all_jobs = Job.query.filter_by(status='open').all()

    if current_user.is_authenticated and current_user.user_type == 'driver':
        # Fetch all applications for this driver
        driver_applications = JobApplication.query.filter_by(driver_id=current_user.id).all()
        
        # Create a dictionary of job_id: application for quick lookup
        application_dict = {app.job_id: app for app in driver_applications}
        
        for job in all_jobs:
            job.user_application = application_dict.get(job.id)
    else:
        for job in all_jobs:
            job.user_application = None

    return render_template("jobs.html", jobs=all_jobs)
