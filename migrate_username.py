"""
Migrate from email to username and update admin credentials
"""

import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')

print("\n🔄 Migrating to username-based authentication...\n")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("✓ Connected to database")
    
    # 1. Check if column already exists
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='username'
    """)
    
    if cur.fetchone():
        print("\n✓ Username column already exists")
    else:
        # Add username column
        print("\n1️⃣ Adding username column...")
        cur.execute("ALTER TABLE users ADD COLUMN username VARCHAR(50)")
        print("✓ Username column added")
        
        # Copy email to username for existing users
        print("\n2️⃣ Migrating existing data...")
        cur.execute("""
            UPDATE users 
            SET username = SPLIT_PART(email, '@', 1)
            WHERE username IS NULL
        """)
        print("✓ Data migrated")
        
        # Make username NOT NULL and UNIQUE
        print("\n3️⃣ Adding constraints...")
        cur.execute("ALTER TABLE users ALTER COLUMN username SET NOT NULL")
        cur.execute("ALTER TABLE users ADD CONSTRAINT users_username_key UNIQUE (username)")
        print("✓ Constraints added")
        
        # Drop email column
        print("\n4️⃣ Removing email column...")
        cur.execute("ALTER TABLE users DROP COLUMN email")
        print("✓ Email column removed")
    
    # Update admin credentials
    print("\n5️⃣ Updating admin credentials...")
    admin_password_hash = generate_password_hash('MAKER')
    
    cur.execute("""
        UPDATE users 
        SET username = 'ADMIN',
            password_hash = %s,
            must_change_password = FALSE
        WHERE is_admin = TRUE
    """, (admin_password_hash,))
    
    if cur.rowcount > 0:
        print("✓ Admin credentials updated")
    else:
        print("⚠️  No admin user found to update")
    
    conn.commit()
    
    print("\n✅ Migration completed successfully!")
    print("\n" + "="*50)
    print("ADMIN LOGIN CREDENTIALS:")
    print("  Username: ADMIN")
    print("  Password: MAKER")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    if conn:
        conn.rollback()
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
