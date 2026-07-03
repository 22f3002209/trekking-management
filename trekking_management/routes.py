from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

from . import db
from .models import Admin, TrekStaff, Trekker, Trek, Booking, TrekHistory

routes = Blueprint('routes', __name__)


# ===================================
# HOME PAGE
# ===================================

@routes.route('/')
def home():
    return render_template("home.html")


# ===================================
# ADMIN ROUTES
# ===================================
@routes.route('/admin_dashboard')
@login_required
def admin_dashboard():
    
    total_treks = Trek.query.count()
    total_staff = TrekStaff.query.count()
    total_trekkers = Trekker.query.count()
    total_bookings = Booking.query.count()
    
    return render_template(
        "admin_dashboard.html",
        total_treks=total_treks,
        total_staff=total_staff,
        total_trekkers=total_trekkers,
        total_bookings=total_bookings
    )

# Admin Search
@routes.route('/admin_search')
@login_required
def admin_search():

    search_text = request.args.get('search_text', '')

    treks = []
    staff_members = []
    trekkers = []

    if search_text:

        treks = Trek.query.filter(
            (Trek.name.ilike(f"%{search_text}%")) |
            (Trek.id == search_text)
        ).all()

        staff_members = TrekStaff.query.filter(
            (TrekStaff.name.ilike(f"%{search_text}%")) |
            (TrekStaff.id == search_text)
        ).all()

        trekkers = Trekker.query.filter(
            (Trekker.name.ilike(f"%{search_text}%")) |
            (Trekker.id == search_text)
        ).all()

    return render_template(
        "admin_search.html",
        search_text=search_text,
        treks=treks,
        staff_members=staff_members,
        trekkers=trekkers
    )

# View History
@routes.route('/view_history')
@login_required
def view_history():

    completed_treks = Trek.query.filter_by(status="Completed").all()

    return render_template(
        "view_history.html",
        completed_treks=completed_treks
    )

# _________About Staff_________

# Manage staff
@routes.route('/manage_staff')
@login_required
def manage_staff():    
    staff_members = TrekStaff.query.filter(TrekStaff.approval_status != 'Pending').all()

    return render_template(
        "manage_staff.html",
        staff_members=staff_members
    )


# requests for registration
@routes.route('/staff_requests')
@login_required
def staff_requests():
    pending_staff = TrekStaff.query.filter_by(approval_status='Pending').all()

    return render_template(
        'staff_requests.html',
        pending_staff=pending_staff
        )

# Staff details
@routes.route('/staff_details/<int:id>')
@login_required
def staff_details(id):

    staff = TrekStaff.query.get_or_404(id)
    history = TrekHistory.query.filter_by(staff_id=id).all()

    return render_template(
        "staff_details.html",
        staff=staff,
        history=history
    )

# Approve staff registration requests
@routes.route('/approve_staff/<int:id>')
@login_required
def approve_staff(id):
    staff = TrekStaff.query.get_or_404(id)

    if staff.approval_status == 'Pending':
        staff.approval_status = 'Approved'

        db.session.commit()

        flash("Staff Approved successfully", "success")

        return redirect(url_for("routes.staff_requests"))

# Reject staff registration requests
@routes.route('/reject_staff/<int:id>')
@login_required
def reject_staff(id):
    staff = TrekStaff.query.get_or_404(id)

    if staff.approval_status == 'Pending':
        staff.approval_status = 'Rejected'
        staff.is_active = False

        db.session.commit()

        flash("Staff request Rejected", "warning")

        return redirect(url_for("routes.staff_requests"))


# Blacklist or Activate staff
@routes.route('/toggle_staff_status/<int:id>', methods=['POST'])
@login_required
def toggle_staff_status(id):
    staff = TrekStaff.query.get_or_404(id)

    staff.is_active = not staff.is_active

    db.session.commit()

    flash("Staff status updated", "success")

    return redirect(url_for("routes.manage_staff"))


# _________About Treks_________

# Manage Treks
@routes.route('/manage_treks')
@login_required
def manage_treks():
    treks = Trek.query.all()

    return render_template("manage_treks.html", treks=treks)


# Add trek
@routes.route('/add_trek', methods=['GET', 'POST'])
@login_required
def add_trek():
    approved_staff = TrekStaff.query.filter_by(approval_status='Approved', is_active=True).all()

    if request.method == 'POST':

        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        total_slots = int(request.form.get('total_slots'))
        description = request.form.get('description')

        start_date = datetime.strptime(request.form.get('start_date'),'%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'),'%Y-%m-%d').date()

        assigned_staff_id = request.form.get('assigned_staff_id')

        conflicting_trek = Trek.query.filter(
            Trek.assigned_staff_id == assigned_staff_id,
            Trek.start_date <= end_date,
            Trek.end_date >= start_date
        ).first()

        if conflicting_trek:
            flash(f"Staff is already assigned to '{conflicting_trek.name}' during these dates", "danger")
            return redirect(url_for("routes.add_trek"))

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            total_slots=total_slots,
            available_slots=total_slots,
            description=description,
            start_date=start_date,
            end_date=end_date,
            assigned_staff_id=assigned_staff_id,
            status='Pending'
        )

        db.session.add(new_trek)
        db.session.commit()

        flash("Trek created successfully", "success")
        return redirect(url_for("routes.manage_treks"))
    
    return render_template("add_trek.html", approved_staff=approved_staff)

# View Trek
@routes.route('/admin_view_trek/<int:id>')
@login_required
def admin_view_trek(id):
    trek = Trek.query.get_or_404(id)

    return render_template("admin_view_trek.html", trek=trek)

# Edit trek
@routes.route('/edit_trek/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trek(id):
    trek = Trek.query.get_or_404(id)

    approved_staff = TrekStaff.query.filter_by(approval_status='Approved', is_active=True).all()

    if request.method == 'POST':

        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        total_slots = int(request.form.get('total_slots'))
        description = request.form.get('description')

        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        status = request.form.get('status')

        assigned_staff_id = request.form.get('assigned_staff_id')

        # Validation 1: Date check
        if start_date > end_date:
            flash("Start date cannot be after end date.", "danger")
            return redirect(url_for('routes.edit_trek', id=trek.id))
        
        # Validation 2: Staff overlap check
        conflicting_trek = Trek.query.filter(
            Trek.assigned_staff_id == assigned_staff_id,
            Trek.id != trek.id,
            Trek.start_date <= end_date,
            Trek.end_date >= start_date
        ).first()

        if conflicting_trek:
            flash(f"Selected staff is already assigned to '{conflicting_trek.name}' during these dates.", "danger")
            return redirect(url_for('routes.edit_trek', id=trek.id))
        
        booked_count = Booking.query.filter_by(
            trek_id=trek.id,
            status='Booked'
        ).count()

        if total_slots < booked_count:
            flash(
                f"Total slots cannot be less than the {booked_count} booked participant(s).",
                "danger"
            )
            return redirect(url_for('routes.edit_trek', id=trek.id))
                
        # Update trek
        trek.name = name
        trek.location = location
        trek.difficulty = difficulty
        trek.duration = duration

        trek.total_slots = total_slots
        trek.available_slots = total_slots - booked_count

        trek.description = description

        trek.start_date = start_date
        trek.end_date = end_date

        trek.status = status

        trek.assigned_staff_id = assigned_staff_id

        db.session.commit()

        flash("Trek updated successfully.", "success")
        return redirect(url_for("routes.manage_treks"))

    return render_template("edit_trek.html", trek=trek, approved_staff=approved_staff)

# Delete Trek
@routes.route('/delete_trek/<int:id>', methods=['POST'])
@login_required
def delete_trek(id):
    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)
    db.session.commit()

    flash("Trek deleted successfully.", "success")

    return redirect(url_for("routes.manage_treks"))


# _________About Trekkers_________

# View Trekkers
@routes.route('/view_trekkers')
@login_required
def view_trekkers():

    trekkers = Trekker.query.all()

    return render_template(
        "view_trekkers.html",
        trekkers=trekkers
    )

# View Trekker details
@routes.route('/admin_trekker_details/<int:id>')
@login_required
def admin_trekker_details(id):

    trekker = Trekker.query.get_or_404(id)
    history = TrekHistory.query.filter_by(trekker_id=id).all()

    return render_template(
        "admin_trekker_details.html",
        trekker=trekker,
        history=history
    )

# Toggle status
@routes.route('/toggle_trekker_status/<int:id>', methods=['POST'])
@login_required
def toggle_trekker_status(id):
    trekker = Trekker.query.get_or_404(id)

    trekker.is_active = not trekker.is_active

    db.session.commit()

    flash("Trekker status updated.", "success")

    return redirect(
        url_for("routes.view_trekkers")
    )


# _________About Bookings_________

# View Bookings
@routes.route('/view_bookings')
@login_required
def view_bookings():

    booked_bookings = Booking.query.filter_by(status='Booked').all()
    cancelled_bookings = Booking.query.filter_by(status='Cancelled').all()

    return render_template(
        "view_bookings.html",
        booked_bookings=booked_bookings,
        cancelled_bookings=cancelled_bookings
    )

# ==========================================
# STAFF ROUTES
# ==========================================

# Staff Dashboard
@routes.route('/staff_dashboard')
@login_required
def staff_dashboard():

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id,
        Trek.status != "Pending"
        ).all()

    total_assigned = len(assigned_treks)
    total_registered = 0
    trek_counts = {}

    for trek in assigned_treks:
        count = Booking.query.filter_by(
            trek_id=trek.id,
            status="Booked"
        ).count()

        trek_counts[trek.id] = count
        total_registered += count

    return render_template("staff_dashboard.html",
                           assigned_treks=assigned_treks,
                           total_assigned=total_assigned,
                           total_registered=total_registered,
                           trek_counts=trek_counts
                           )

# Edit profile
@routes.route('/staff_edit_profile', methods=['GET', 'POST'])
@login_required
def staff_edit_profile():

    staff = TrekStaff.query.get_or_404(current_user.id)

    if request.method == "POST":
        staff.name = request.form.get('name')
        staff.age = request.form.get('age')
        staff.gender = request.form.get('gender')
        staff.contact = request.form.get('contact')
        staff.experience = request.form.get('experience')

        password = request.form.get('password')

        if password:
            staff.password = password

        db.session.commit()

        flash("Profile updated successfully.", "success")

        return redirect(url_for("routes.staff_dashboard"))
    
    return render_template("staff_edit_profile.html",
                           staff=staff
                           )

# Trek update
@routes.route('/staff_update_trek/<int:trek_id>', methods=['GET', 'POST'])
@login_required
def staff_update_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    # Only assigned staff can manage

    if trek.assigned_staff_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routes.staff_dashboard"))

    if request.method == 'POST':
        
        new_status = request.form.get('status')
        
        # Create Trek History when trek becomes completed
        if (trek.status != 'Completed' and new_status == 'Completed'):

            bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()

            for booking in bookings:
                booking.status = 'Completed'

                existing_history = TrekHistory.query.filter_by(
                    booking_id=booking.id
                ).first()

                if not existing_history:
                    history = TrekHistory(
                        booking_id=booking.id,
                        trekker_id=booking.trekker_id,
                        trek_id=trek.id,
                        staff_id=trek.assigned_staff_id
                    )
                db.session.add(history)

        trek.status = new_status

        db.session.commit()

        flash("Trek updated successfully.", "success")
        return redirect(url_for("routes.staff_dashboard"))

    return render_template("staff_update_trek.html", trek=trek)

# View participants
@routes.route('/staff_view_participants/<int:trek_id>')
@login_required
def staff_view_participants(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routes.staff_dashboard"))

    booked_participants = Booking.query.filter_by(
        trek_id=trek.id,
        status="Booked"
        ).all()
    
    cancelled_participants = Booking.query.filter_by(
        trek_id=trek.id,
        status="Cancelled"
        ).all()

    return render_template(
        "staff_view_participants.html",
        trek=trek,
        booked_participants=booked_participants,
        cancelled_participants=cancelled_participants)

# View Trekker details
@routes.route('/staff_trekker_details/<int:trekker_id>/<int:trek_id>')
@login_required
def staff_trekker_details(trekker_id, trek_id):

    trekker = Trekker.query.get_or_404(trekker_id)
    history = TrekHistory.query.filter_by(trekker_id=trekker_id).all()

    return render_template(
        "staff_trekker_details.html",
        trekker=trekker,
        trek_id=trek_id,
        history=history
    )

# ==========================================
# TREKKER ROUTES
# ==========================================

@routes.route('/trekker_dashboard')
@login_required
def trekker_dashboard():

    location = request.args.get('location', '')
    difficulty = request.args.get('difficulty', '')

    query = Trek.query.filter(
        Trek.status == 'Open',
        Trek.available_slots > 0
    )

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    available_treks = query.all()

    return render_template("trekker_dashboard.html",
                           available_treks=available_treks,
                           location=location,
                           difficulty=difficulty
                           )

# Edit profile
@routes.route('/trekker_edit_profile', methods=['GET', 'POST'])
@login_required
def trekker_edit_profile():

    trekker = Trekker.query.get_or_404(current_user.id)

    if request.method == 'POST':

        trekker.name = request.form.get('name')

        trekker.age = request.form.get('age')

        trekker.gender = request.form.get('gender')

        trekker.contact = request.form.get('contact')

        trekker.emergency_contact = request.form.get('emergency_contact')

        trekker.emergency_contact_relation = request.form.get('emergency_contact_relation')

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("routes.trekker_dashboard"))

    return render_template("trekker_edit_profile.html",trekker=trekker)

# My bookings
@routes.route('/my_bookings')
@login_required
def my_bookings():

    booked_bookings = Booking.query.filter_by(
        trekker_id=current_user.id,
        status='Booked'
    ).all()

    cancelled_bookings = Booking.query.filter_by(
        trekker_id=current_user.id,
        status='Cancelled'
    ).all()

    return render_template(
        "my_bookings.html",
        booked_bookings=booked_bookings,
        cancelled_bookings=cancelled_bookings
    )

# Trek details
@routes.route('/trek_details/<int:trek_id>')
@login_required
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    existing_booking = Booking.query.filter_by(
        trekker_id=current_user.id,
        trek_id=trek.id,
        status="Booked"
    ).first()

    return render_template(
        "trek_details.html",
        trek=trek,
        existing_booking=existing_booking
    )

# Book Trek
@routes.route('/book_trek/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != 'Open':
        flash("This trek is not open for booking.", "danger")
        return redirect(url_for("routes.trek_details", trek_id=trek.id))

    if trek.available_slots <= 0:
        flash("No slots available.", "danger")
        return redirect(url_for("routes.trek_details", trek_id=trek.id))

    existing_booking = Booking.query.filter_by(
        trekker_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
        ).first()

    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("routes.trek_details", trek_id=trek.id))

    booking = Booking(
        trekker_id=current_user.id,
        trek_id=trek.id,
        status='Booked'
    )

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()
    flash("Trek booked successfully.", "success")

    return redirect(url_for("routes.my_bookings"))

# cancel
@routes.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    if booking.trekker_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("routes.my_bookings"))

    if booking.status != 'Booked':
        flash("This booking cannot be cancelled.", "warning")
        return redirect(url_for("routes.my_bookings"))

    booking.status = 'Cancelled'
    booking.trek.available_slots += 1

    db.session.commit()
    flash("Booking cancelled successfully.", "success")

    return redirect(url_for("routes.my_bookings"))

# Trekker History
@routes.route('/trekker_history')
@login_required
def trekker_history():

    histories = TrekHistory.query.filter_by(
        trekker_id=current_user.id
    ).all()

    return render_template("trekker_history.html", histories=histories)