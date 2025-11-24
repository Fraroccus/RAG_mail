"""
Database initialization script for Supabase
Run this once to create tables and admin user
"""
import os
from flask_app import app, db
from database import User, Workspace, Email, EmailDraft, EnrollmentDocument

def init_database():
    """Initialize database with tables and admin user"""
    with app.app_context():
        print("=" * 60)
        print("DATABASE INITIALIZATION")
        print("=" * 60)
        
        # Drop all tables (BE CAREFUL - this deletes all data!)
        # Uncomment only if you want to reset everything
        # print("\nDropping all tables...")
        # db.drop_all()
        # print("✓ All tables dropped")
        
        # Create all tables
        print("\nCreating tables...")
        db.create_all()
        print("✓ Tables created")
        
        # List all tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nTables in database: {tables}")
        
        # Check if admin exists
        print("\nChecking for admin user...")
        admin = User.query.filter_by(username='ADMIN').first()
        
        if admin:
            print(f"✓ Admin user already exists (ID: {admin.id})")
            print(f"  Username: {admin.username}")
            print(f"  Full Name: {admin.full_name}")
            print(f"  Is Admin: {admin.is_admin}")
            print(f"  Is Active: {admin.is_active}")
        else:
            print("Creating admin user...")
            admin = User(
                username='ADMIN',
                full_name='Administrator',
                is_admin=True,
                is_active=True,
                must_change_password=False
            )
            admin.set_password('MAKER')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created")
            print("  Username: ADMIN")
            print("  Password: MAKER")
        
        # Verify creation
        print("\nVerifying users in database...")
        all_users = User.query.all()
        print(f"Total users: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.username} (ID: {user.id}, Admin: {user.is_admin})")
        
        print("\n" + "=" * 60)
        print("INITIALIZATION COMPLETE")
        print("=" * 60)
        print("\nYou can now log in with:")
        print("  Username: ADMIN")
        print("  Password: MAKER")
        print("=" * 60)

if __name__ == '__main__':
    # Check if DATABASE_URL is set
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nPlease set it first:")
        print("  export DATABASE_URL='your_supabase_connection_string'")
        exit(1)
    
    print(f"Using database: {db_url[:30]}...")
    
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
