"""
Migration script to add workspace support
Creates default workspace and migrates existing data
"""

from flask import Flask
from database import db, Workspace, HistoricalEmail, EnrollmentDocument, Correction
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("\n🔄 Starting workspace migration...")
    
    # Create all tables (including new Workspace table)
    db.create_all()
    print("✓ Database tables created/updated")
    
    # Check if default workspace exists
    default_workspace = Workspace.query.filter_by(id=1).first()
    
    if not default_workspace:
        # Create default workspace
        default_workspace = Workspace(
            id=1,
            title="ITS Maker Academy",
            emoji="🎓",
            color="#1976d2",
            is_active=True
        )
        db.session.add(default_workspace)
        db.session.commit()
        print("✓ Created default workspace: ITS Maker Academy 🎓")
    else:
        print(f"✓ Default workspace already exists: {default_workspace.title}")
    
    # Update existing records to link to default workspace
    # (The default=1 in the schema handles this, but we ensure it explicitly)
    
    historical_count = HistoricalEmail.query.filter_by(workspace_id=1).count()
    documents_count = EnrollmentDocument.query.filter_by(workspace_id=1).count()
    corrections_count = Correction.query.filter_by(workspace_id=1).count()
    
    print(f"\n📊 Default workspace contents:")
    print(f"   - Historical Emails: {historical_count}")
    print(f"   - Enrollment Documents: {documents_count}")
    print(f"   - Corrections: {corrections_count}")
    
    print("\n✅ Migration completed successfully!")
    print("   You can now create additional workspaces from the dashboard.\n")
