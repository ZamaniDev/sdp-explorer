"""Initialize the database with tables"""
from app import app, db, User, UserPreferences
import sys

def init_database():
    """Initialize database and optionally create a test user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")

        # Check if any users exist
        user_count = User.query.count()
        print(f"✓ Current user count: {user_count}")

        if user_count == 0:
            print("\nNo users found. Would you like to create an admin user? (y/n)")
            response = input().strip().lower()

            if response == 'y':
                print("\n--- Create Admin User ---")
                username = input("Username: ").strip()
                email = input("Email: ").strip()
                password = input("Password: ").strip()

                # Create user
                user = User(username=username, email=email)
                user.set_password(password)

                # Create default preferences
                preferences = UserPreferences(user=user)

                db.session.add(user)
                db.session.add(preferences)
                db.session.commit()

                print(f"\n✓ User '{username}' created successfully!")
                print("  You can now login at http://127.0.0.1:5000/login")

        print("\n✓ Database initialization complete!")

if __name__ == '__main__':
    init_database()
