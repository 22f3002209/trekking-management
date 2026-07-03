from flask_login import UserMixin
from datetime import datetime
from . import db

# Admin Model
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


# Trek Staff Model
class TrekStaff(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    experience = db.Column(db.Integer, default=0)
    password = db.Column(db.String(150), nullable=False)
    approval_status = db.Column(db.String(20), default='Pending') # Pending / Approved / Rejected
    is_active = db.Column(db.Boolean, default=True)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    # One to many relationship with Trek
    treks = db.relationship('Trek', backref='staff')

    # One to many relationship with TrekHistory
    histories = db.relationship('TrekHistory', backref='staff', cascade='all, delete-orphan', passive_deletes=True)


# Trekker Model
class Trekker(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    emergency_contact = db.Column(db.String(15), nullable=False)
    emergency_contact_relation = db.Column(db.String(150))
    password = db.Column(db.String(150), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    # One to many relationship with Booking
    bookings = db.relationship('Booking', backref='trekker', cascade='all, delete-orphan', passive_deletes=True)

    # One to many relationship with TrekHistory
    histories = db.relationship('TrekHistory', backref='trekker', cascade='all, delete-orphan', passive_deletes=True)


# Trek Model
class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy / Moderate / Hard
    duration = db.Column(db.Integer, nullable=False) # in days
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending / Approved / Open / Closed / Completed 
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("trek_staff.id", ondelete='SET NULL'), nullable=False)

    # One to many relationship with TrekHistory
    histories = db.relationship('TrekHistory', backref='trek', cascade='all, delete-orphan', passive_deletes=True)

    # One to many relationship with Booking
    bookings = db.relationship('Booking', backref='trek', cascade='all, delete-orphan', passive_deletes=True)
    

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Booked') # Booked / Cancelled / Completed

    # Foreign keys
    trekker_id = db.Column(db.Integer, db.ForeignKey('trekker.id', ondelete='CASCADE'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id', ondelete='CASCADE'), nullable=False)

    # One to one relationship with TrekHistory
    history = db.relationship('TrekHistory', backref='booking', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    
    # later add the feature to register for 1+ person from simgle account


# Trek History Model
class TrekHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    completed_on = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Text)
    rating = db.Column(db.Integer)

    # Foreign keys
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id', ondelete='CASCADE'), nullable=False, unique=True)
    trekker_id = db.Column(db.Integer, db.ForeignKey('trekker.id', ondelete='CASCADE'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id', ondelete='CASCADE'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('trek_staff.id', ondelete='CASCADE'), nullable=False)