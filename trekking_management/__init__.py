from flask import Flask, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Initialize flask app
def create_app():
    app =  Flask(__name__)

    app.config['DEBUG'] = True

    # Configuration settings
    app.config['SECRET_KEY'] = "keep_it_secret!"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///trekking.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Import and register blueprints
    from .auth import auth
    from .routes import routes

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(routes, url_prefix='/')

    # Import models
    from .models import Admin, TrekStaff, Trekker

    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database connected and tables created")

        # Create default Admin
        admin = Admin.query.filter_by(email = "admin@gmail.com").first()

        if not admin:
            admin = Admin(
                email = "admin@gmail.com",
                password = "1234"
            )
            db.session.add(admin)
            db.session.commit()
            print("Default Admin created")

    # Flask-login setup
    login_manager = LoginManager()

    login_manager.init_app(app)

    login_manager.login_view = "auth.admin_login"

    @login_manager.user_loader
    def load_user(user_id):
        user_type  = session.get('user_type')

        if user_type == "admin":
            return Admin.query.get(int(user_id))
        
        elif user_type == "staff":
            return TrekStaff.query.get(int(user_id))
        
        elif user_type == "trekker":
            return Trekker.query.get(int(user_id))
        
        return None
    
    return app