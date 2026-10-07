"""App initialization, blueprint registration, and default mock seed data."""
from flask import Flask, render_template
from werkzeug.security import generate_password_hash
from models import db, User, Donation, Event
from routes_auth import auth_bp
from routes_donor import donor_bp
from routes_admin import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aashray-seva-key-sies-gst-mini-project-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aashray_seva.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(donor_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def public_index():
    upcoming_events = Event.query.filter_by(status='upcoming').limit(3).all()
    completed_events = Event.query.filter_by(status='completed').limit(6).all()
    recent_donations = Donation.query.order_by(Donation.created_at.desc()).limit(5).all()
    
    total_funds = sum(d.amount for d in Donation.query.all())
    total_meals = sum(d.meals_funded for d in Donation.query.all())
    total_donors = User.query.filter_by(role='user').count()

    return render_template(
        'index.html',
        upcoming_events=upcoming_events,
        completed_events=completed_events,
        recent_donations=recent_donations,
        total_funds=total_funds,
        total_meals=total_meals,
        total_donors=total_donors
    )

def seed_database():
    with app.app_context():
        db.create_all()
        # Seed Admin
        if not User.query.filter_by(email='admin@aashray.ngo').first():
            admin = User(
                full_name='System Administrator',
                email='admin@aashray.ngo',
                phone='9876543210',
                role='admin',
                password_hash=generate_password_hash('admin123')
            )
            donor = User(
                full_name='Sahil Manohar Desale',
                email='sahil@gmail.com',
                phone='9820123456',
                pan_number='ABCDE1234F',
                role='user',
                password_hash=generate_password_hash('sahil123')
            )
            db.session.add_all([admin, donor])
            db.session.commit()

            # Seed Initial Events
            events = [
                Event(
                    title="Bal Shiksha Ahara - ZP School Food Distribution",
                    category="Nutrition",
                    venue="Municipal School 102, Nerul, Navi Mumbai",
                    date="2026-10-18",
                    description="Distributing fresh hot nutritious breakfast and fruit kits to 450 municipal primary school kids.",
                    status="upcoming",
                    image_url="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=600&auto=format&fit=crop&q=80"
                ),
                Event(
                    title="Winter Warmth: Blanket & Woolen Clothes Drive",
                    category="Relief",
                    venue="Navi Mumbai Slum Settlements",
                    date="2026-11-05",
                    description="Distributing thermal blankets and jackets to elderly residents and migrant families.",
                    status="upcoming",
                    image_url="https://images.unsplash.com/photo-1593113598332-cd288d649433?w=600&auto=format&fit=crop&q=80"
                ),
                Event(
                    title="Swasthya Ahara: Community Kitchen Drive",
                    category="Healthcare",
                    venue="Govt Hospital Shelter, Vashi",
                    date="2026-09-12",
                    description="Served warm khichdi and fresh fruit to over 1,200 relatives of hospitalized patients.",
                    status="completed",
                    image_url="https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=600&auto=format&fit=crop&q=80"
                ),
                Event(
                    title="Education Kit Distribution - Mission Vidya",
                    category="Education",
                    venue="Turbhe Colony Learning Center",
                    date="2026-08-20",
                    description="Provided stationery kits, notebooks, and school bags to 300 underprivileged children.",
                    status="completed",
                    image_url="https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&auto=format&fit=crop&q=80"
                )
            ]
            db.session.add_all(events)
            db.session.commit()

            # Seed Real-time Donations
            donations = [
                Donation(
                    receipt_id="AS-8941AB12", user_id=donor.id, donor_name="Sahil Manohar Desale",
                    category="Bal Shiksha Ahara", amount=5000.0, meals_funded=200,
                    payment_method="UPI", transaction_ref="TXN-UPI9918231", pan_number="ABCDE1234F"
                ),
                Donation(
                    receipt_id="AS-3321FA77", user_id=donor.id, donor_name="Dharamkumar Bhatia",
                    category="Swasthya Ahara", amount=2500.0, meals_funded=100,
                    payment_method="Card", transaction_ref="TXN-CRD4928172", pan_number="BKJPA9012K"
                ),
                Donation(
                    receipt_id="AS-1092FF98", user_id=donor.id, donor_name="Pratap Merchant",
                    category="Winter Blanket Drive", amount=12000.0, meals_funded=480,
                    payment_method="NetBanking", transaction_ref="TXN-NB0029182", pan_number="PMMPA4412R"
                )
            ]
            db.session.add_all(donations)
            db.session.commit()

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5000)