"""
Flask API backend per sistema email RAG
Interfaccia in italiano
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import db, Email, EmailDraft, HistoricalEmail, EnrollmentDocument, SystemSettings
from email_connector import EmailConnector
from dual_rag_system import DualRAGSystem
from language_detector import LanguageDetector
import config
import os
from datetime import datetime
import json


app = Flask(__name__, static_folder='frontend/build', static_url_path='')
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

# Initialize components
email_connector = None
rag_system = None
language_detector = LanguageDetector()


def init_components():
    """Initialize email connector and RAG system"""
    global email_connector, rag_system
    
    try:
        if config.MS_CLIENT_ID and config.MS_CLIENT_SECRET:
            email_connector = EmailConnector()
            print("✓ Email connector inizializzato")
        else:
            print("⚠ Configurazione Microsoft Graph mancante")
        
        rag_system = DualRAGSystem()
        print("✓ RAG system inizializzato")
    except Exception as e:
        print(f"⚠ Errore inizializzazione: {e}")


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
            detected_lang = language_detector.detect_language(email_data['body'])
            student_info = language_detector.extract_student_info(email_data['body'])
            
            # Crea record email
            email = Email(
                message_id=email_data['message_id'],
                sender_email=email_data['sender_email'],
                sender_name=email_data['sender_name'],
                subject=email_data['subject'],
                body=email_data['body'],
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


# ============== ENDPOINTS BOZZE EMAIL ==============

@app.route('/api/drafts/generate/<int:email_id>', methods=['POST'])
def generate_draft(email_id):
    """Genera bozza risposta per una email"""
    try:
        email = Email.query.get_or_404(email_id)
        
        if not rag_system:
            return jsonify({'errore': 'RAG system non inizializzato'}), 500
        
        # Controlla se bozza già esiste
        if email.draft:
            return jsonify({'errore': 'Bozza già esistente'}), 400
        
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
            draft.edited_response = data['testo_modificato']
        
        if 'note_admin' in data:
            draft.admin_notes = data['note_admin']
        
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
                
                # Indicizza automaticamente
                if rag_system:
                    rag_system.index_historical_email({
                        'query': historical.student_query,
                        'response': historical.response,
                        'language': historical.language,
                        'tags': historical.tags
                    })
                    historical.indexed = True
                    db.session.commit()
        
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
        emails = HistoricalEmail.query.order_by(HistoricalEmail.created_at.desc()).all()
        
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
        
        email = HistoricalEmail(
            subject=data.get('oggetto', ''),
            student_query=data['domanda_studente'],
            response=data['risposta'],
            language=data.get('lingua', 'it'),
            tags=data.get('tags', ''),
            country=data.get('paese', ''),
            program=data.get('programma', ''),
            date_sent=datetime.fromisoformat(data['data_invio']) if 'data_invio' in data else None
        )
        
        db.session.add(email)
        db.session.commit()
        
        # Indicizza nel RAG
        if rag_system:
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
        docs = EnrollmentDocument.query.order_by(EnrollmentDocument.last_updated.desc()).all()
        
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
        
        doc = EnrollmentDocument(
            title=data['titolo'],
            filename=data.get('nome_file', ''),
            content=data['contenuto'],
            document_type=data.get('tipo_documento', 'general'),
            country=data.get('paese', 'ALL'),
            program=data.get('programma', 'ALL'),
            language=data.get('lingua', 'it'),
            priority=data.get('priorita', 'medium')
        )
        
        db.session.add(doc)
        db.session.commit()
        
        # Indicizza nel RAG
        if rag_system:
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
        
        return jsonify({
            'successo': True,
            'documento': doc.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'errore': str(e)}), 500


@app.route('/api/enrollment-docs/<int:doc_id>', methods=['PUT'])
def update_enrollment_doc(doc_id):
    """Aggiorna documento iscrizione"""
    try:
        doc = EnrollmentDocument.query.get_or_404(doc_id)
        data = request.json
        
        if 'titolo' in data:
            doc.title = data['titolo']
        if 'contenuto' in data:
            doc.content = data['contenuto']
        if 'tipo_documento' in data:
            doc.document_type = data['tipo_documento']
        if 'paese' in data:
            doc.country = data['paese']
        if 'programma' in data:
            doc.program = data['programma']
        if 'priorita' in data:
            doc.priority = data['priorita']
        
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


# ============== ENDPOINTS STATISTICHE ==============

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Ottieni statistiche sistema"""
    try:
        stats = {
            'email_totali': Email.query.count(),
            'bozze_pending': EmailDraft.query.filter_by(status='pending').count(),
            'bozze_approvate': EmailDraft.query.filter_by(status='approved').count(),
            'email_inviate': EmailDraft.query.filter_by(status='sent').count(),
            'email_storiche': HistoricalEmail.query.count(),
            'documenti_iscrizione': EnrollmentDocument.query.count()
        }
        
        if rag_system:
            try:
                rag_stats = rag_system.get_stats()
                stats.update(rag_stats)
            except Exception as e:
                print(f"⚠ Errore caricamento stats RAG: {e}")
                # Continue without RAG stats
        
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
        setting = SystemSettings.query.filter_by(key=key).first()
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
        
        setting = SystemSettings.query.filter_by(key=key).first()
        if not setting:
            # Crea nuova impostazione
            setting = SystemSettings(
                key=key,
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
