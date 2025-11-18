"""
Check and fix system prompts after migration
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL', '')

print("\n🔍 Checking system_settings...\n")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Check existing system_prompt entries
    cur.execute("""
        SELECT id, key, workspace_id, LENGTH(value) as value_length, description
        FROM system_settings 
        WHERE key = 'system_prompt'
        ORDER BY id
    """)
    
    rows = cur.fetchall()
    print(f"Found {len(rows)} system_prompt entry(ies):\n")
    
    for row in rows:
        print(f"  ID: {row[0]}")
        print(f"  Key: {row[1]}")
        print(f"  Workspace ID: {row[2]}")
        print(f"  Value Length: {row[3]} characters")
        print(f"  Description: {row[4]}")
        print()
    
    # If we have a system_prompt with NULL workspace_id, ask to assign it to workspace 1
    if rows:
        null_workspace_prompts = [r for r in rows if r[2] is None]
        if null_workspace_prompts:
            print(f"⚠️  Found {len(null_workspace_prompts)} system_prompt(s) with NULL workspace_id")
            print("   These won't be visible in workspace views!")
            print("\n🔧 Assigning to workspace 1 (default)...\n")
            
            for row in null_workspace_prompts:
                cur.execute("""
                    UPDATE system_settings 
                    SET workspace_id = 1 
                    WHERE id = %s
                """, (row[0],))
                print(f"  ✓ Updated system_prompt ID {row[0]} -> workspace_id = 1")
            
            conn.commit()
            print("\n✅ Migration fix completed!\n")
        else:
            print("✅ All system_prompts have workspace_id assigned.\n")
    else:
        print("ℹ️  No system_prompt found in database.\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
