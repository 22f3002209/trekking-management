from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required

from .models import Admin, TrekStaff, Trekker
from . import db

auth = Blueprint('auth', __name__)


# ________Admin auth routes________

# Admin login
@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = Admin.query.filter_by(email=email).first()

        if admin and admin.password == password:
            login_user(admin)
            session['user_type']  = "admin"
            flash("Admin successfully logged in!", "success")
            return redirect(url_for("routes.admin_dashboard"))
        flash("Invalid email or password", "danger")

    return render_template("admin_login.html")

# Admin logout
@auth.route('/admin_logout')
@login_required
def admin_logout():
    
    logout_user()
    session.pop('user_type', None)
    flash("Admin logged out!", "success")

    return redirect(url_for("routes.home"))


# ________Staff auth routes________

# Trek Staff Register
@auth.route('/staff_register', methods=['GET', 'POST'])
def staff_register():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        experience = request.form.get('experience')

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.staff_register"))
        
        existing_staff = TrekStaff.query.filter_by(email=email).first()
        if existing_staff:
            flash("Email alreday registered", "warning")
            return redirect(url_for('auth.staff_login'))
        
        new_staff = TrekStaff(
            name=name,
            email=email,
            age=age,
            gender=gender,
            contact=contact,
            experience=experience,
            password=password
        )

        db.session.add(new_staff)
        db.session.commit()

        flash("Registration Submitted, Wait for Admin approval", "success")
        return redirect(url_for('auth.staff_login'))
    
    return render_template("staff_register.html")


# Trek staff login
@auth.route('/staff_login', methods=['GET', 'POST'])
def staff_login():

    if request.method == "POST":

        email = request.form.get('email')
        password = request.form.get('password')

        staff = TrekStaff.query.filter_by(email=email).first()

        if not staff or staff.password != password:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.staff_login"))
        
        if not staff.is_active:
            flash("Your account has been deactivated!", "warning")
            return redirect(url_for("auth.staff_login"))
        
        if staff.approval_status == 'Pending':
            flash("Your registration request is awaiting admin approval...", "warning")
            return redirect(url_for("auth.staff_login"))
        
        if staff.approval_status == 'Rejected':
            flash("Your registration request has been rejected. You may submit a new request.", "warning")
            return redirect(url_for("auth.staff_register"))
                
        login_user(staff)
        session['user_type'] = "staff"
        flash("Logged in successfully!", "success")

        return redirect(url_for("routes.staff_dashboard"))
    
    return render_template("staff_login.html")


# Trek staff logout
@auth.route('/staff_logout')
@login_required
def staff_logout():

    logout_user()
    session.pop('user_type', None)
    flash("Logged out successfully!", "success")

    return redirect(url_for("routes.home"))


# ________Trekker auth routes________

# Trekker registration
@auth.route('/trekker_register', methods=['GET', 'POST'])
def trekker_register():

    if request.method == "POST":

        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        emergency_contact = request.form.get('emergency_contact')
        emergency_contact_relation = request.form.get('emergency_contact_relation')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("auth.trekker_register"))
        
        existing_trekker = Trekker.query.filter_by(email=email).first()

        if existing_trekker:
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.trekker_login"))
        
        new_trekker = Trekker(
            name=name,
            email=email,
            age=age,
            gender=gender,
            contact=contact,
            emergency_contact=emergency_contact,
            emergency_contact_relation=emergency_contact_relation,
            password=password
        )

        db.session.add(new_trekker)
        db.session.commit()

        flash("Registration successful! Please login", "success")
        return redirect(url_for("auth.trekker_login"))
    
    return render_template("trekker_register.html")


# Trekker login
@auth.route('/trekker_login', methods=['GET', 'POST'])
def trekker_login():
    
    if request.method == "POST":

        email = request.form.get('email')
        password = request.form.get('password')

        trekker = Trekker.query.filter_by(email=email).first()

        if not trekker or trekker.password != password:
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.trekker_login"))
        
        if not trekker.is_active:
            flash("Your account has been deactivated", "warning")
            return redirect(url_for("auth.trekker_login"))
        
        login_user(trekker)
        session['user_type'] = "trekker"
        flash("Logged in successfully!", "success")
        return redirect(url_for("routes.trekker_dashboard"))
    
    return render_template("trekker_login.html")


# Trekker logout
@auth.route('/trekker_logout')
@login_required
def trekker_logout():
    
    logout_user()
    session.pop('user_type', None)
    flash("Logged out successfully!", "success")

    return redirect(url_for('routes.home'))