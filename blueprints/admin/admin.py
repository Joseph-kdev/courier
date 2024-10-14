from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from blueprints.user_page.users import User, Job, JobApplication, db

admin = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

@admin.route("/dashboard")
@login_required
def dashboard():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    users_count = User.query.count()
    jobs_count = Job.query.count()
    applications_count = JobApplication.query.count()
    
    return render_template("dashboard.html", 
                           users_count=users_count, 
                           jobs_count=jobs_count, 
                           applications_count=applications_count)

@admin.route("/users")
@login_required
def users_list():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    users = User.query.all()
    return render_template("users_list.html", users=users)

@admin.route("/jobs")
@login_required
def jobs_list():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    jobs = Job.query.all()
    return render_template("admin/jobs_list.html", jobs=jobs)

@admin.route("/applications")
@login_required
def applications_list():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    applications = JobApplication.query.all()
    return render_template("admin/applications_list.html", applications=applications)

@admin.route("/create_driver", methods=["GET", "POST"])
@login_required
def create_driver():
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
        else:
            new_driver = User(name=name, email=email, user_type='driver')
            new_driver.set_password(password)
            db.session.add(new_driver)
            db.session.commit()
            flash('Driver account created successfully', 'success')
            return redirect(url_for('admin.users_list'))
    
    return render_template("create_driver.html")

@admin.route("/user/<int:user_id>")
@login_required
def user_details(user_id):
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    user = User.query.get_or_404(user_id)
    return render_template("user_details.html", user=user)

@admin.route("/user/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('landing_page.home'))
    
    user = User.query.get_or_404(user_id)
    if user.user_type == 'admin':
        flash('Cannot delete admin users', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users_list'))
