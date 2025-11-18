"""
SQL Migration: Add workspace support to existing tables
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL', '')
# Format: postgresql://user:password@host:port/database

print("\n🔄 Starting database migration for workspaces...\n")

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("✓ Connected to database")
    
    # 1. Create workspaces table
    print("\n1️⃣ Creating workspaces table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workspaces (
            id SERIAL PRIMARY KEY,
            title VARCHAR(60) NOT NULL,
            emoji VARCHAR(10) DEFAULT '📧',
            color VARCHAR(7) DEFAULT '#1976d2',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)
    print("✓ Workspaces table created")
    
    # 2. Insert default workspace if not exists
    print("\n2️⃣ Creating default workspace...")
    cur.execute("""
        INSERT INTO workspaces (id, title, emoji, color, is_active)
        VALUES (1, 'ITS Maker Academy', '🎓', '#1976d2', TRUE)
        ON CONFLICT (id) DO NOTHING
    """)
    print("✓ Default workspace created")
    
    # 3. Add workspace_id to historical_emails
    print("\n3️⃣ Adding workspace_id to historical_emails...")
    cur.execute("""
        ALTER TABLE historical_emails 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER DEFAULT 1 NOT NULL
        REFERENCES workspaces(id) ON DELETE CASCADE
    """)
    print("✓ Added workspace_id to historical_emails")
    
    # 4. Add workspace_id to enrollment_documents
    print("\n4️⃣ Adding workspace_id to enrollment_documents...")
    cur.execute("""
        ALTER TABLE enrollment_documents 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER DEFAULT 1 NOT NULL
        REFERENCES workspaces(id) ON DELETE CASCADE
    """)
    print("✓ Added workspace_id to enrollment_documents")
    
    # 5. Add workspace_id to corrections
    print("\n5️⃣ Adding workspace_id to corrections...")
    cur.execute("""
        ALTER TABLE corrections 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER DEFAULT 1 NOT NULL
        REFERENCES workspaces(id) ON DELETE CASCADE
    """)
    print("✓ Added workspace_id to corrections")
    
    # Commit all changes
    conn.commit()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) FROM historical_emails WHERE workspace_id = 1")
    emails_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM enrollment_documents WHERE workspace_id = 1")
    docs_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM corrections WHERE workspace_id = 1")
    corrections_count = cur.fetchone()[0]
    
    print(f"\n📊 Default workspace (ITS Maker Academy 🎓):")
    print(f"   - Historical Emails: {emails_count}")
    print(f"   - Enrollment Documents: {docs_count}")
    print(f"   - Corrections: {corrections_count}")
    
    print("\n✅ Migration completed successfully!")
    print("   You can now start Flask and access the workspace dashboard.\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
