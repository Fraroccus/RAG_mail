"""
Add user authentication system and link workspaces to users
"""

import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')

print("\n🔄 Adding user authentication system...\n")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("✓ Connected to database")
    
    # 1. Create users table
    print("\n1️⃣ Creating users table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),
            is_admin BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            must_change_password BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    print("✓ Users table created")
    
    # 2. Create default admin user
    print("\n2️⃣ Creating default admin user...")
    admin_email = "admin@itsmaker.academy"
    admin_password = "Admin123!"  # Change this after first login!
    admin_password_hash = generate_password_hash(admin_password)
    
    cur.execute("""
        INSERT INTO users (email, password_hash, full_name, is_admin, is_active, must_change_password)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        RETURNING id
    """, (admin_email, admin_password_hash, "Administrator", True, True, True))
    
    result = cur.fetchone()
    if result:
        admin_id = result[0]
        print(f"✓ Admin user created with ID: {admin_id}")
        print(f"  📧 Email: {admin_email}")
        print(f"  🔑 Password: {admin_password}")
        print(f"  ⚠️  IMPORTANT: Change this password after first login!")
    else:
        print("  ℹ️  Admin user already exists")
        cur.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
        admin_id = cur.fetchone()[0]
    
    # 3. Add user_id column to workspaces
    print("\n3️⃣ Adding user_id to workspaces table...")
    cur.execute("""
        ALTER TABLE workspaces 
        ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) DEFAULT %s
    """, (admin_id,))
    print("✓ user_id column added")
    
    # 4. Update existing workspaces to belong to admin
    print("\n4️⃣ Assigning existing workspaces to admin...")
    cur.execute("""
        UPDATE workspaces 
        SET user_id = %s 
        WHERE user_id IS NULL
    """, (admin_id,))
    affected = cur.rowcount
    print(f"✓ Assigned {affected} existing workspace(s) to admin")
    
    conn.commit()
    print("\n✅ Migration completed successfully!\n")
    print("=" * 60)
    print("ADMIN LOGIN CREDENTIALS:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print("=" * 60)
    print("\n⚠️  Remember to change the admin password after first login!\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
