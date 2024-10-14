from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from blueprints.landing_page.landing import landing_page
from blueprints.user_page.users import users, db, login_manager, User
from blueprints.admin.admin import admin
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courier_ke.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'users.login'

app.register_blueprint(landing_page, url_prefix="/")
app.register_blueprint(users, url_prefix="/users")
app.register_blueprint(admin, url_prefix="/admin")

migrate = Migrate(app, db)

def create_default_admin():
    admin_user = User.query.filter_by(email='admin@mail.com').first()
    if not admin_user:
        admin_user = User(name='admin', email='admin@mail.com', user_type='admin')
        admin_user.set_password('admin')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created.")
    else:
        print("Admin user already exists.")

with app.app_context():
    db.create_all()
    create_default_admin()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)