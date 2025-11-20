"""
Flask API backend per sistema email RAG
Interfaccia in italiano
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from database import db, Email, EmailDraft, HistoricalEmail, EnrollmentDocument, SystemSettings, Correction, Workspace, User
from email_connector import EmailConnector
from dual_rag_system import DualRAGSystem
from language_detector import LanguageDetector
import config
import os
from datetime import datetime
import json
from functools import wraps


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, supports_credentials=True)
db.init_app(app)

# Simple input sanitization
import re

def sanitize_text(text, max_len=None):
    if not isinstance(text, str):
        return ''
    cleaned = re.sub(r'<[^>]*>', '', text)
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', cleaned)
    cleaned = cleaned.strip()
    if max_len and isinstance(max_len, int):
        cleaned = cleaned[:max_len]
    return cleaned

# Initialize components
email_connector = None
rag_systems = {}  # Cache of workspace-specific RAG systems
language_detector = LanguageDetector()


def cleanup_workspace_vector_stores(workspace_id):
    """Delete FAISS index files for a workspace"""
    import glob
    
    # Get all collection names for this workspace
    collection_patterns = [
        f"{config.COLLECTION_HISTORICAL_EMAILS}_ws{workspace_id}",
        f"{config.COLLECTION_ENROLLMENT_DOCS}_ws{workspace_id}",
        f"{config.COLLECTION_CORRECTIONS}_ws{workspace_id}"
    ]
    
    deleted_count = 0
    for pattern in collection_patterns:
        # Delete .index and .pkl files
        index_path = os.path.join(config.CHROMA_DB_DIR, f"{pattern}.index")
        metadata_path = os.path.join(config.CHROMA_DB_DIR, f"{pattern}.pkl")
        
        if os.path.exists(index_path):
            os.remove(index_path)
            deleted_count += 1
            print(f"  ✓ Rimosso: {pattern}.index")
        
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            deleted_count += 1
            print(f"  ✓ Rimosso: {pattern}.pkl")
    
    return deleted_count


def duplicate_workspace_vector_stores(source_id, target_id):
    """Copy FAISS index files from source workspace to target workspace"""
    import shutil
    
    collection_types = [
        config.COLLECTION_HISTORICAL_EMAILS,
        config.COLLECTION_ENROLLMENT_DOCS,
        config.COLLECTION_CORRECTIONS
    ]
    
    copied_count = 0
    for collection_type in collection_types:
        source_pattern = f"{collection_type}_ws{source_id}"
        target_pattern = f"{collection_type}_ws{target_id}"
        
        # Copy .index file
        source_index = os.path.join(config.CHROMA_DB_DIR, f"{source_pattern}.index")
        target_index = os.path.join(config.CHROMA_DB_DIR, f"{target_pattern}.index")
        
        if os.path.exists(source_index):
            shutil.copy2(source_index, target_index)
            copied_count += 1
            print(f"  ✓ Copiato: {source_pattern}.index -> {target_pattern}.index")
        
        # Copy .pkl file
        source_pkl = os.path.join(config.CHROMA_DB_DIR, f"{source_pattern}.pkl")
        target_pkl = os.path.join(config.CHROMA_DB_DIR, f"{target_pattern}.pkl")
        
        if os.path.exists(source_pkl):
            shutil.copy2(source_pkl, target_pkl)
            copied_count += 1
            print(f"  ✓ Copiato: {source_pattern}.pkl -> {target_pattern}.pkl")
    
    return copied_count


def get_rag_system(workspace_id):
    """Get or create RAG system for workspace"""
    # Validate workspace exists
    workspace = Workspace.query.get(workspace_id)
    if not workspace:
        raise ValueError(f"Workspace {workspace_id} does not exist")
    
    if workspace_id not in rag_systems:
        print(f"🔄 Inizializzazione RAG system per workspace {workspace_id}...")
        try:
            rag_systems[workspace_id] = DualRAGSystem(workspace_id=workspace_id)
        except Exception as e:
            # If RAG initialization fails (corrupted indexes), try to recover
            print(f"⚠️ Errore inizializzazione RAG system: {e}")
            print(f"🔧 Tentativo di recupero eliminando vector stores corrotti...")
            
            # Delete corrupted vector store files
            cleanup_workspace_vector_stores(workspace_id)
            
            # Try again with fresh indexes
            try:
                rag_systems[workspace_id] = DualRAGSystem(workspace_id=workspace_id)
                print(f"✓ RAG system ricreato con successo")
            except Exception as retry_error:
                print(f"❌ Impossibile inizializzare RAG system: {retry_error}")
                raise ValueError(f"Cannot initialize RAG system for workspace {workspace_id}: {retry_error}")
    
    return rag_systems[workspace_id]


def init_components():
    """Initialize email connector"""
    global email_connector
    
    try:
        if config.MS_CLIENT_ID and config.MS_CLIENT_SECRET:
            email_connector = EmailConnector()
            print("✓ Email connector inizializzato")
        else:
            print("⚠ Configurazione Microsoft Graph mancante")
        
        print("✓ RAG system manager inizializzato")
    except Exception as e:
        print(f"⚠ Errore inizializzazione: {e}")


# ============== AUTHENTICATION ==============

def login_required(f):
    """Decorator to require login for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'errore': 'Authentication required'}), 401
        
        # Check if user still exists and is active
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return jsonify({'errore': 'User not found or inactive'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'errore': 'Authentication required'}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_active or not user.is_admin:
            return jsonify({'errore': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'errore': 'Username e password richiesti'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({'errore': 'Username o password errati'}), 401
        
        if not user.is_active:
            return jsonify({'errore': 'Account disattivato'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        
        return jsonify({
            'successo': True,
            'user': user.to_dict(),
            'must_change_password': user.must_change_password
        })
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'errore': str(e)}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'successo': True})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info"""
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict())


@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.json
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'errore': 'Password attuale e nuova richieste'}), 400
        
        if len(new_password) < 4:
            return jsonify({'errore': 'La password deve essere almeno 4 caratteri'}), 400
        
        user = User.query.get(session['user_id'])
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({'errore': 'Password attuale errata'}), 401
        
        # Set new password
        user.set_password(new_password)
        user.must_change_password = False
        db.session.commit()
        
        return jsonify({'successo': True, 'messaggio': 'Password aggiornata'})
    
    except Exception as e:
        print(f"Password change error: {e}")
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== ADMIN: USER MANAGEMENT ==============

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            'users': [u.to_dict() for u in users]
        })
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        full_name = data.get('full_name', '').strip()
        temp_password = data.get('temp_password', '')
        is_admin = data.get('is_admin', False)
        
        if not username or not temp_password:
            return jsonify({'errore': 'Username e password temporanea richiesti'}), 400
        
        if len(temp_password) < 4:
            return jsonify({'errore': 'La password deve essere almeno 4 caratteri'}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'errore': 'Username già in uso'}), 400
        
        # Create user
        user = User(
            username=username,
            full_name=full_name,
            is_admin=is_admin,
            is_active=True,
            must_change_password=True
        )
        user.set_password(temp_password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'user': user.to_dict(),
            'messaggio': f'Utente creato. Password temporanea: {temp_password}'
        }), 201
    
    except Exception as e:
        print(f"Create user error: {e}")
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['PATCH'])
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        # Prevent self-deactivation or removing own admin rights
        current_user_id = session.get('user_id')
        if user_id == current_user_id:
            if 'is_active' in data and not data['is_active']:
                return jsonify({'errore': 'Non puoi disattivare il tuo account'}), 400
            if 'is_admin' in data and not data['is_admin']:
                return jsonify({'errore': 'Non puoi rimuovere i tuoi privilegi admin'}), 400
        
        # Update fields
        if 'full_name' in data:
            user.full_name = data['full_name'].strip()
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'user': user.to_dict()
        })
    
    except Exception as e:
        print(f"Update user error: {e}")
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        new_password = data.get('new_password', '')
        
        if not new_password or len(new_password) < 4:
            return jsonify({'errore': 'La password deve essere almeno 4 caratteri'}), 400
        
        user.set_password(new_password)
        user.must_change_password = True
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'messaggio': f'Password reimpostata per {user.username}'
        })
    
    except Exception as e:
        print(f"Reset password error: {e}")
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        current_user_id = session.get('user_id')
        
        # Can't delete yourself
        if user_id == current_user_id:
            return jsonify({'errore': 'Non puoi eliminare il tuo account'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Delete user's workspaces and their vector stores
        for workspace in user.workspaces:
            # Clean up vector stores
            if workspace.id in rag_systems:
                del rag_systems[workspace.id]
            cleanup_workspace_vector_stores(workspace.id)
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'messaggio': f'Utente {user.username} eliminato'
        })
    
    except Exception as e:
        print(f"Delete user error: {e}")
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/')
def serve_frontend():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')


# ============== ENDPOINTS EMAIL ==============

@app.route('/api/emails/fetch', methods=['POST'])
def fetch_emails():
    """Recupera nuove email da Outlook"""
    try:
        if not email_connector:
            return jsonify({'errore': 'Email connector non configurato'}), 500
        
        emails = email_connector.fetch_unread_emails()
        
        nuove_email = []
        for email_data in emails:
            # Controlla se già esiste
            exists = Email.query.filter_by(message_id=email_data['message_id']).first()
            if exists:
                continue
            
            # Rileva lingua ed estrai info
            body_clean = sanitize_text(email_data.get('body', ''), max_len=20000)
            subject_clean = sanitize_text(email_data.get('subject', ''), max_len=500)
            detected_lang = language_detector.detect_language(body_clean)
            student_info = language_detector.extract_student_info(body_clean)
            
            # Crea record email
            email = Email(
                message_id=sanitize_text(email_data.get('message_id', ''), max_len=500),
                sender_email=sanitize_text(email_data.get('sender_email', ''), max_len=255),
                sender_name=sanitize_text(email_data.get('sender_name', ''), max_len=255),
                subject=subject_clean,
                body=body_clean,
                detected_language=detected_lang,
                received_date=datetime.fromisoformat(email_data['received_date'].replace('Z', '+00:00')),
                query_type=','.join(student_info['query_type'])
            )
            
            db.session.add(email)
            nuove_email.append(email)
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'nuove_email': len(nuove_email),
            'email': [e.to_dict() for e in nuove_email]
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Ottieni lista email"""
    try:
        status = request.args.get('status', 'all')
        
        query = Email.query
        
        if status == 'no_draft':
            query = query.filter(~Email.draft.has())
        elif status == 'pending':
            query = query.join(EmailDraft).filter(EmailDraft.status == 'pending')
        elif status == 'sent':
            query = query.join(EmailDraft).filter(EmailDraft.status == 'sent')
        
        emails = query.order_by(Email.received_date.desc()).all()
        
        return jsonify({
            'successo': True,
            'email': [e.to_dict() for e in emails]
        })
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/emails/<int:email_id>', methods=['GET'])
def get_email(email_id):
    """Ottieni dettagli email singola"""
    try:
        email = Email.query.get_or_404(email_id)
        
        result = email.to_dict()
        if email.draft:
            result['bozza'] = email.draft.to_dict()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/emails/generate-manual', methods=['POST'])
def generate_manual_response():
    """Genera risposta da email incollata manualmente"""
    try:
        data = request.json
        workspace_id = data.get('workspace_id')
        
        if not workspace_id:
            return jsonify({'errore': 'workspace_id richiesto'}), 400
        
        rag_system = get_rag_system(workspace_id)
        
        # Prepara dati email
        incoming_email = {
            'subject': sanitize_text(data.get('oggetto', ''), max_len=500),
            'body': sanitize_text(data.get('corpo', ''), max_len=20000),
            'sender_email': sanitize_text(data.get('mittente', 'manuale@esempio.com'), max_len=255),
            'sender_name': sanitize_text(data.get('mittente', 'Manuale'), max_len=255)
        }
        
        # Genera risposta
        result = rag_system.generate_email_response(incoming_email)
        
        return jsonify({
            'successo': True,
            'risposta': result['response'],
            'lingua_rilevata': result['detected_language'],
            'confidenza': result['confidence_score']
        })
    
    except Exception as e:
        print(f"❌ Errore generazione manuale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS BOZZE EMAIL ==============

@app.route('/api/drafts/generate/<int:email_id>', methods=['POST'])
def generate_draft(email_id):
    """Genera bozza risposta per una email"""
    try:
        email = Email.query.get_or_404(email_id)
        data = request.json or {}
        workspace_id = data.get('workspace_id', 1)  # Default to workspace 1
        
        # Controlla se bozza già esiste
        if email.draft:
            return jsonify({'errore': 'Bozza già esistente'}), 400
        
        # Get workspace-specific RAG system
        rag_system = get_rag_system(workspace_id)
        
        # Prepara dati email per RAG
        incoming_email = {
            'subject': email.subject,
            'body': email.body,
            'sender_email': email.sender_email,
            'sender_name': email.sender_name
        }
        
        # Genera risposta
        result = rag_system.generate_email_response(incoming_email)
        
        # Crea bozza
        draft = EmailDraft(
            email_id=email.id,
            generated_response=result['response'],
            response_language=result['detected_language'],
            retrieved_contexts=json.dumps(result['retrieved_contexts']),
            confidence_score=result['confidence_score'],
            status='pending'
        )
        
        db.session.add(draft)
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'bozza': draft.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>', methods=['GET'])
def get_draft(draft_id):
    """Ottieni bozza"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        return jsonify(draft.to_dict())
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>', methods=['PUT'])
def update_draft(draft_id):
    """Aggiorna bozza (modifica testo)"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        data = request.json
        
        if 'testo_modificato' in data:
            draft.edited_response = sanitize_text(data['testo_modificato'], max_len=20000)
        
        if 'note_admin' in data:
            draft.admin_notes = sanitize_text(data['note_admin'], max_len=500)
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'bozza': draft.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>/approve', methods=['POST'])
def approve_draft(draft_id):
    """Approva bozza"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        data = request.json
        
        draft.status = 'approved'
        draft.reviewed_at = datetime.utcnow()
        draft.reviewed_by = data.get('revisore', 'admin')
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'bozza': draft.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>/reject', methods=['POST'])
def reject_draft(draft_id):
    """Rifiuta bozza"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        data = request.json
        
        draft.status = 'rejected'
        draft.reviewed_at = datetime.utcnow()
        draft.reviewed_by = data.get('revisore', 'admin')
        draft.admin_notes = data.get('motivo', '')
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'bozza': draft.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>/send', methods=['POST'])
def send_draft(draft_id):
    """Invia email approvata"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        email = draft.email
        
        if not email_connector:
            return jsonify({'errore': 'Email connector non configurato'}), 500
        
        if draft.status != 'approved':
            return jsonify({'errore': 'Bozza non approvata'}), 400
        
        # Usa testo modificato se disponibile, altrimenti originale
        response_text = draft.edited_response or draft.generated_response
        
        # Aggiungi firma se configurata
        if config.EMAIL_SIGNATURE:
            response_text += f"\n\n{config.EMAIL_SIGNATURE}"
        
        # Invia email
        success = email_connector.send_email(
            to_email=email.sender_email,
            subject=f"Re: {email.subject}",
            body=response_text,
            reply_to_message_id=email.message_id
        )
        
        if success:
            draft.status = 'sent'
            draft.sent_at = datetime.utcnow()
            
            # Marca email originale come letta
            email_connector.mark_as_read(email.message_id)
            
            db.session.commit()
            
            return jsonify({
                'successo': True,
                'messaggio': 'Email inviata con successo'
            })
        else:
            return jsonify({'errore': 'Invio fallito'}), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/drafts/<int:draft_id>/feedback', methods=['POST'])
def submit_feedback(draft_id):
    """Invia feedback sulla bozza generata"""
    try:
        draft = EmailDraft.query.get_or_404(draft_id)
        data = request.json
        
        # Update feedback
        draft.feedback_rating = data.get('rating')
        draft.feedback_comment = data.get('comment')
        draft.feedback_categories = ','.join(data.get('categories', []))
        draft.feedback_submitted_at = datetime.utcnow()
        
        db.session.commit()
        
        # Se il feedback è positivo e l'email è stata inviata, aggiungi a email storiche
        if draft.feedback_rating >= 4 and draft.status == 'sent':
            email = draft.email
            
            # Controlla se già esiste
            existing = HistoricalEmail.query.filter_by(
                student_query=email.body,
                response=draft.edited_response or draft.generated_response
            ).first()
            
            if not existing:
                historical = HistoricalEmail(
                    workspace_id=1,  # Default workspace for now - TODO: associate emails with workspaces
                    subject=email.subject,
                    student_query=email.body,
                    response=draft.edited_response or draft.generated_response,
                    language=draft.response_language,
                    tags=email.query_type,
                    date_sent=draft.sent_at,
                    indexed=False
                )
                db.session.add(historical)
                db.session.commit()
                
                # TODO: Index in workspace-specific RAG when emails have workspace_id
        
        return jsonify({
            'successo': True,
            'bozza': draft.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS EMAIL STORICHE ==============

@app.route('/api/historical-emails', methods=['GET'])
def get_historical_emails():
    """Ottieni lista email storiche"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        query = HistoricalEmail.query
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        emails = query.order_by(HistoricalEmail.created_at.desc()).all()
        
        return jsonify({
            'successo': True,
            'email_storiche': [e.to_dict() for e in emails]
        })
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/historical-emails', methods=['POST'])
def add_historical_email():
    """Aggiungi email storica"""
    try:
        data = request.json
        workspace_id = data.get('workspace_id', 1)  # Default to workspace 1
        
        email = HistoricalEmail(
            workspace_id=workspace_id,
            subject=sanitize_text(data.get('oggetto', ''), max_len=500),
            student_query=sanitize_text(data['domanda_studente'], max_len=20000),
            response=sanitize_text(data['risposta'], max_len=20000),
            language=sanitize_text(data.get('lingua', 'it'), max_len=10),
            tags=sanitize_text(data.get('tags', ''), max_len=500),
            country=sanitize_text(data.get('paese', ''), max_len=100),
            program=sanitize_text(data.get('programma', ''), max_len=255),
            date_sent=datetime.fromisoformat(data['data_invio']) if 'data_invio' in data else None
        )
        
        db.session.add(email)
        db.session.commit()
        
        # Indicizza nel RAG
        rag_system = get_rag_system(workspace_id)
        rag_system.index_historical_email({
            'query': email.student_query,
            'response': email.response,
            'language': email.language,
            'country': email.country,
            'program': email.program,
            'tags': email.tags
        })
        
        email.indexed = True
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'email_storica': email.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/historical-emails/<int:email_id>', methods=['DELETE'])
def delete_historical_email(email_id):
    """Elimina email storica"""
    try:
        email = HistoricalEmail.query.get_or_404(email_id)
        db.session.delete(email)
        db.session.commit()
        
        return jsonify({'successo': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS DOCUMENTI ISCRIZIONE ==============

@app.route('/api/enrollment-docs', methods=['GET'])
def get_enrollment_docs():
    """Ottieni lista documenti iscrizione"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        query = EnrollmentDocument.query
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        docs = query.order_by(EnrollmentDocument.last_updated.desc()).all()
        
        return jsonify({
            'successo': True,
            'documenti': [d.to_dict() for d in docs]
        })
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs', methods=['POST'])
def add_enrollment_doc():
    """Aggiungi documento iscrizione"""
    try:
        data = request.json
        workspace_id = data.get('workspace_id', 1)  # Default to workspace 1
        
        doc = EnrollmentDocument(
            workspace_id=workspace_id,
            title=sanitize_text(data['titolo'], max_len=255),
            filename=sanitize_text(data.get('nome_file', ''), max_len=255),
            content=sanitize_text(data['contenuto'], max_len=200000),
            document_type=sanitize_text(data.get('tipo_documento', 'general'), max_len=100),
            country=sanitize_text(data.get('paese', 'ALL'), max_len=100),
            program=sanitize_text(data.get('programma', 'ALL'), max_len=255),
            language=sanitize_text(data.get('lingua', 'it'), max_len=10),
            priority=sanitize_text(data.get('priorita', 'medium'), max_len=20)
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # Indicizza nel RAG
        print(f"📝 Indicizzazione documento: {doc.title}")
        print(f"📄 Lunghezza contenuto: {len(doc.content)} caratteri")
        try:
            rag_system = get_rag_system(workspace_id)
            rag_system.index_enrollment_document({
                'content': doc.content,
                'title': doc.title,
                'document_type': doc.document_type,
                'country': doc.country,
                'program': doc.program,
                'language': doc.language,
                'priority': doc.priority
            })
            doc.indexed = True
            db.session.commit()
            print(f"✓ Documento indicizzato con successo")
        except Exception as e:
            print(f"❌ Errore indicizzazione: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'successo': True,
            'documento': doc.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs/<int:doc_id>', methods=['GET'])
def get_enrollment_doc_detail(doc_id):
    """Ottieni dettagli completi documento iscrizione"""
    try:
        doc = EnrollmentDocument.query.get_or_404(doc_id)
        return jsonify({
            'successo': True,
            'documento': doc.to_dict(include_full_content=True)
        })
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs/<int:doc_id>', methods=['PUT'])
def update_enrollment_doc(doc_id):
    """Aggiorna documento iscrizione"""
    try:
        doc = EnrollmentDocument.query.get_or_404(doc_id)
        data = request.json
        
        if 'titolo' in data:
            doc.title = sanitize_text(data['titolo'], max_len=255)
        if 'contenuto' in data:
            doc.content = sanitize_text(data['contenuto'], max_len=200000)
        if 'tipo_documento' in data:
            doc.document_type = sanitize_text(data['tipo_documento'], max_len=100)
        if 'paese' in data:
            doc.country = sanitize_text(data['paese'], max_len=100)
        if 'programma' in data:
            doc.program = sanitize_text(data['programma'], max_len=255)
        if 'priorita' in data:
            doc.priority = sanitize_text(data['priorita'], max_len=20)
        
        doc.last_updated = datetime.utcnow()
        doc.indexed = False  # Richiede re-indicizzazione
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'documento': doc.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs/<int:doc_id>', methods=['DELETE'])
def delete_enrollment_doc(doc_id):
    """Elimina documento iscrizione"""
    try:
        doc = EnrollmentDocument.query.get_or_404(doc_id)
        db.session.delete(doc)
        db.session.commit()
        
        return jsonify({'successo': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs/reindex-all', methods=['POST'])
def reindex_all_enrollment_docs():
    """Re-indicizza tutti i documenti iscrizione"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        
        if not workspace_id:
            return jsonify({'errore': 'workspace_id richiesto'}), 400
        
        rag_system = get_rag_system(workspace_id)
        docs = EnrollmentDocument.query.filter_by(workspace_id=workspace_id).all()
        print(f"\n🔄 Re-indicizzazione {len(docs)} documenti per workspace {workspace_id}...")
        
        success_count = 0
        for doc in docs:
            try:
                print(f"📝 Indicizzazione: {doc.title}")
                print(f"   📄 Lunghezza: {len(doc.content)} caratteri")
                
                rag_system.index_enrollment_document({
                    'content': doc.content,
                    'title': doc.title,
                    'document_type': doc.document_type,
                    'country': doc.country,
                    'program': doc.program,
                    'language': doc.language,
                    'priority': doc.priority
                })
                
                doc.indexed = True
                success_count += 1
                print(f"   ✓ Successo")
            except Exception as e:
                print(f"   ❌ Errore: {e}")
                import traceback
                traceback.print_exc()
        
        db.session.commit()
        print(f"\n✓ Re-indicizzati {success_count}/{len(docs)} documenti")
        
        return jsonify({
            'successo': True,
            'documenti_processati': len(docs),
            'documenti_indicizzati': success_count
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Errore re-indicizzazione: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS STATISTICHE ==============

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Ottieni statistiche sistema"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        
        stats = {
            'email_totali': Email.query.count(),
            'bozze_pending': EmailDraft.query.filter_by(status='pending').count(),
            'bozze_approvate': EmailDraft.query.filter_by(status='approved').count(),
            'email_inviate': EmailDraft.query.filter_by(status='sent').count()
        }
        
        # Filter by workspace
        if workspace_id:
            stats['email_storiche'] = HistoricalEmail.query.filter_by(workspace_id=workspace_id).count()
            stats['documenti_iscrizione'] = EnrollmentDocument.query.filter_by(workspace_id=workspace_id).count()
        else:
            stats['email_storiche'] = HistoricalEmail.query.count()
            stats['documenti_iscrizione'] = EnrollmentDocument.query.count()
        
        # RAG stats are workspace-specific if workspace_id provided
        if workspace_id:
            try:
                rag_system = get_rag_system(workspace_id)
                rag_stats = rag_system.get_stats()
                stats.update(rag_stats)
            except Exception as e:
                print(f"⚠ Errore caricamento stats RAG: {e}")
        
        return jsonify(stats)
    
    except Exception as e:
        print(f"❌ Errore in /api/stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS IMPOSTAZIONI SISTEMA ==============

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Ottieni tutte le impostazioni di sistema"""
    try:
        settings = SystemSettings.query.all()
        return jsonify({
            'successo': True,
            'impostazioni': [s.to_dict() for s in settings]
        })
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/settings/<key>', methods=['GET'])
def get_setting(key):
    """Ottieni singola impostazione"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        
        if workspace_id:
            setting = SystemSettings.query.filter_by(key=key, workspace_id=workspace_id).first()
        else:
            setting = SystemSettings.query.filter_by(key=key, workspace_id=None).first()
        
        if not setting:
            return jsonify({'errore': 'Impostazione non trovata'}), 404
        
        return jsonify(setting.to_dict())
    
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/settings/<key>', methods=['PUT'])
def update_setting(key):
    """Aggiorna impostazione"""
    try:
        data = request.json
        workspace_id = data.get('workspace_id')
        
        if workspace_id:
            setting = SystemSettings.query.filter_by(key=key, workspace_id=workspace_id).first()
        else:
            setting = SystemSettings.query.filter_by(key=key, workspace_id=None).first()
        
        if not setting:
            # Crea nuova impostazione
            setting = SystemSettings(
                key=key,
                workspace_id=workspace_id,
                value=data.get('value', ''),
                description=data.get('description', '')
            )
            db.session.add(setting)
        else:
            # Aggiorna esistente
            if 'value' in data:
                setting.value = data['value']
            if 'description' in data:
                setting.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'impostazione': setting.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS CORRECTIONS ==============

@app.route('/api/corrections', methods=['GET'])
def get_corrections():
    """Ottieni tutte le correzioni"""
    try:
        workspace_id = request.args.get('workspace_id', type=int)
        query = Correction.query
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        corrections = query.order_by(Correction.priority.desc(), Correction.created_at.desc()).all()
        return jsonify({
            'successo': True,
            'correzioni': [c.to_dict() for c in corrections]
        })
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/corrections', methods=['POST'])
def add_correction():
    """Aggiungi correzione"""
    try:
        data = request.json
        workspace_id = data.get('workspace_id', 1)  # Default to workspace 1
        
        correction = Correction(
            workspace_id=workspace_id,
            title=sanitize_text(data['titolo'], max_len=255),
            wrong_info=sanitize_text(data['info_errata'], max_len=2000),
            correct_info=sanitize_text(data['info_corretta'], max_len=2000),
            context=sanitize_text(data.get('contesto', ''), max_len=2000),
            category=data.get('categoria', 'general'),
            priority=data.get('priorita', 'medium')
        )
        
        db.session.add(correction)
        db.session.commit()
        
        # Index in RAG system
        print(f"🔧 Indicizzazione correzione: {correction.title}")
        try:
            rag_system = get_rag_system(workspace_id)
            rag_system.index_correction({
                'title': correction.title,
                'wrong_info': correction.wrong_info,
                'correct_info': correction.correct_info,
                'context': correction.context,
                'category': correction.category,
                'priority': correction.priority
            })
            correction.indexed = True
            db.session.commit()
            print(f"✓ Correzione indicizzata con successo")
        except Exception as e:
            print(f"❌ Errore indicizzazione: {e}")
        
        return jsonify({
            'successo': True,
            'correzione': correction.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/corrections/<int:correction_id>', methods=['DELETE'])
def delete_correction(correction_id):
    """Elimina correzione"""
    try:
        correction = Correction.query.get_or_404(correction_id)
        db.session.delete(correction)
        db.session.commit()
        
        return jsonify({'successo': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== ENDPOINTS WORKSPACES ==============

@app.route('/api/workspaces', methods=['GET'])
@login_required
def get_workspaces():
    """Ottieni tutti i workspaces dell'utente corrente"""
    try:
        user_id = session.get('user_id')
        workspaces = Workspace.query.filter_by(user_id=user_id).order_by(Workspace.last_modified.desc()).all()
        return jsonify({
            'successo': True,
            'workspaces': [w.to_dict() for w in workspaces]
        })
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/workspaces', methods=['POST'])
@login_required
def create_workspace():
    """Crea nuovo workspace"""
    try:
        data = request.json
        user_id = session.get('user_id')
        
        workspace = Workspace(
            user_id=user_id,
            title=sanitize_text(data['titolo'], max_len=60),
            emoji=sanitize_text(data.get('emoji', '📧'), max_len=10),
            color=sanitize_text(data.get('colore', '#1976d2'), max_len=7),
            is_active=True
        )
        
        db.session.add(workspace)
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'workspace': workspace.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/workspaces/<int:workspace_id>', methods=['GET'])
@login_required
def get_workspace(workspace_id):
    """Ottieni dettagli workspace"""
    try:
        user_id = session.get('user_id')
        workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first_or_404()
        return jsonify(workspace.to_dict())
    except Exception as e:
        return jsonify({'errore': str(e)}), 500


@app.route('/api/workspaces/<int:workspace_id>', methods=['PUT'])
@login_required
def update_workspace(workspace_id):
    """Aggiorna workspace"""
    try:
        user_id = session.get('user_id')
        workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first_or_404()
        data = request.json
        
        if 'titolo' in data:
            workspace.title = sanitize_text(data['titolo'], max_len=60)
        if 'emoji' in data:
            workspace.emoji = sanitize_text(data['emoji'], max_len=10)
        if 'colore' in data:
            workspace.color = sanitize_text(data['colore'], max_len=7)
        if 'is_active' in data:
            workspace.is_active = data['is_active']
        
        workspace.last_modified = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'workspace': workspace.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/workspaces/<int:workspace_id>', methods=['DELETE'])
@login_required
def delete_workspace(workspace_id):
    """Elimina workspace (con tutti i dati associati)"""
    try:
        user_id = session.get('user_id')
        workspace = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first_or_404()
        
        # 1. Clean up RAG system from memory cache
        if workspace_id in rag_systems:
            del rag_systems[workspace_id]
            print(f"🗑️ RAG system per workspace {workspace_id} rimosso dalla cache")
        
        # 2. Delete FAISS vector store files from disk
        print(f"🗑️ Pulizia vector stores per workspace {workspace_id}...")
        deleted_files = cleanup_workspace_vector_stores(workspace_id)
        print(f"✓ Rimossi {deleted_files} file vector store")
        
        # 3. Delete database records (cascade will handle related data)
        db.session.delete(workspace)
        db.session.commit()
        
        return jsonify({
            'successo': True,
            'file_rimossi': deleted_files
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/workspaces/<int:workspace_id>/duplicate', methods=['POST'])
@login_required
def duplicate_workspace(workspace_id):
    """Duplica un workspace con tutti i suoi dati"""
    try:
        user_id = session.get('user_id')
        original = Workspace.query.filter_by(id=workspace_id, user_id=user_id).first_or_404()
        
        # Crea nuovo workspace
        duplicate = Workspace(
            user_id=user_id,
            title=f"{original.title} (Copia)",
            emoji=original.emoji,
            color=original.color,
            is_active=True
        )
        db.session.add(duplicate)
        db.session.flush()  # Get ID before copying related data
        
        # Copia historical emails
        for email in original.historical_emails:
            new_email = HistoricalEmail(
                workspace_id=duplicate.id,
                subject=email.subject,
                student_query=email.student_query,
                response=email.response,
                language=email.language,
                tags=email.tags,
                country=email.country,
                program=email.program,
                date_sent=email.date_sent
            )
            db.session.add(new_email)
        
        # Copia enrollment documents
        for doc in original.enrollment_documents:
            new_doc = EnrollmentDocument(
                workspace_id=duplicate.id,
                title=doc.title,
                filename=doc.filename,
                content=doc.content,
                document_type=doc.document_type,
                country=doc.country,
                program=doc.program,
                language=doc.language,
                priority=doc.priority
            )
            db.session.add(new_doc)
        
        # Copia corrections
        for corr in original.corrections:
            new_corr = Correction(
                workspace_id=duplicate.id,
                title=corr.title,
                wrong_info=corr.wrong_info,
                correct_info=corr.correct_info,
                context=corr.context,
                category=corr.category,
                priority=corr.priority
            )
            db.session.add(new_corr)
        
        # Copia system settings (system prompt)
        original_settings = SystemSettings.query.filter_by(
            key='system_prompt',
            workspace_id=workspace_id
        ).first()
        
        if original_settings:
            new_settings = SystemSettings(
                key='system_prompt',
                workspace_id=duplicate.id,
                value=original_settings.value,
                description=original_settings.description
            )
            db.session.add(new_settings)
        
        db.session.commit()
        
        # Copy FAISS vector stores
        print(f"📋 Copia vector stores da workspace {workspace_id} a {duplicate.id}...")
        copied_files = duplicate_workspace_vector_stores(workspace_id, duplicate.id)
        print(f"✓ Copiati {copied_files} file vector store")
        
        return jsonify({
            'successo': True,
            'workspace': duplicate.to_dict(),
            'file_copiati': copied_files
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


# ============== INIZIALIZZAZIONE ==============

with app.app_context():
    db.create_all()
    init_components()
    print("✓ Database inizializzato")


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
