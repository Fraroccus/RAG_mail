"""
Add workspace_id to system_settings table
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')

print("\n🔄 Adding workspace support to system_settings...\n")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("✓ Connected to database")
    
    # Drop the unique constraint on key
    print("\n1️⃣ Removing unique constraint on key column...")
    cur.execute("""
        ALTER TABLE system_settings DROP CONSTRAINT IF EXISTS system_settings_key_key
    """)
    print("✓ Unique constraint removed")
    
    # Add workspace_id column
    print("\n2️⃣ Adding workspace_id column...")
    cur.execute("""
        ALTER TABLE system_settings 
        ADD COLUMN IF NOT EXISTS workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE
    """)
    print("✓ workspace_id column added")
    
    conn.commit()
    print("\n✅ Migration completed successfully!\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
