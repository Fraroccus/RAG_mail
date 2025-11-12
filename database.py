"""
Database models for email RAG system
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Email(db.Model):
    """Incoming emails"""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(500), unique=True, nullable=False)
    sender_email = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255))
    subject = db.Column(db.String(500))
    body = db.Column(db.Text, nullable=False)
    detected_language = db.Column(db.String(10))
    received_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Extracted information
    student_country = db.Column(db.String(100))
    program_interest = db.Column(db.String(255))
    query_type = db.Column(db.String(100))
    is_urgent = db.Column(db.Boolean, default=False)
    
    # Relationships
    draft = db.relationship('EmailDraft', backref='email', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'subject': self.subject,
            'body': self.body,
            'detected_language': self.detected_language,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'student_country': self.student_country,
            'program_interest': self.program_interest,
            'query_type': self.query_type,
            'is_urgent': self.is_urgent
        }


class EmailDraft(db.Model):
    """Generated email drafts pending approval"""
    __tablename__ = 'email_drafts'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False)
    
    # Draft content
    generated_response = db.Column(db.Text, nullable=False)
    edited_response = db.Column(db.Text)  # User-edited version
    response_language = db.Column(db.String(10))
    
    # RAG context
    retrieved_contexts = db.Column(db.Text)  # JSON string of retrieved chunks
    confidence_score = db.Column(db.Float)
    
    # Status tracking
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, sent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.String(100))
    
    # Notes
    admin_notes = db.Column(db.Text)
    
    # Feedback
    feedback_rating = db.Column(db.Integer)  # 1-5 stars
    feedback_comment = db.Column(db.Text)
    feedback_categories = db.Column(db.String(255))  # tone, accuracy, completeness, etc.
    feedback_submitted_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email_id': self.email_id,
            'generated_response': self.generated_response,
            'edited_response': self.edited_response,
            'response_language': self.response_language,
            'retrieved_contexts': json.loads(self.retrieved_contexts) if self.retrieved_contexts else [],
            'confidence_score': self.confidence_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'reviewed_by': self.reviewed_by,
            'admin_notes': self.admin_notes,
            'feedback_rating': self.feedback_rating,
            'feedback_comment': self.feedback_comment,
            'feedback_categories': self.feedback_categories.split(',') if self.feedback_categories else [],
            'feedback_submitted_at': self.feedback_submitted_at.isoformat() if self.feedback_submitted_at else None
        }


class HistoricalEmail(db.Model):
    """Historical email responses for learning writing style"""
    __tablename__ = 'historical_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(500))
    student_query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10))
    tags = db.Column(db.String(500))  # Comma-separated tags
    country = db.Column(db.String(100))
    program = db.Column(db.String(255))
    date_sent = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    indexed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'student_query': self.student_query,
            'response': self.response,
            'language': self.language,
            'tags': self.tags.split(',') if self.tags else [],
            'country': self.country,
            'program': self.program,
            'date_sent': self.date_sent.isoformat() if self.date_sent else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'indexed': self.indexed
        }


class EnrollmentDocument(db.Model):
    """Enrollment procedures and requirements documents"""
    __tablename__ = 'enrollment_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    document_type = db.Column(db.String(100))  # procedure, requirement, FAQ, deadline, etc.
    country = db.Column(db.String(100))  # Specific country or 'ALL'
    program = db.Column(db.String(255))  # Specific program or 'ALL'
    language = db.Column(db.String(10))
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    indexed = db.Column(db.Boolean, default=False)
    
    def to_dict(self, include_full_content=False):
        content_display = self.content
        if not include_full_content and len(self.content) > 500:
            content_display = self.content[:500] + '...'
        
        return {
            'id': self.id,
            'title': self.title,
            'filename': self.filename,
            'content': content_display,
            'full_content_length': len(self.content),
            'document_type': self.document_type,
            'country': self.country,
            'program': self.program,
            'language': self.language,
            'priority': self.priority,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'indexed': self.indexed
        }


class SystemSettings(db.Model):
    """System configuration and settings"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Correction(db.Model):
    """Feedback-based corrections to prevent repeated mistakes"""
    __tablename__ = 'corrections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # Short description
    wrong_info = db.Column(db.Text, nullable=False)  # What was wrong
    correct_info = db.Column(db.Text, nullable=False)  # What's correct
    context = db.Column(db.Text)  # When/where this applies
    category = db.Column(db.String(100))  # e.g., 'pricing', 'deadlines', 'requirements'
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    indexed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'wrong_info': self.wrong_info,
            'correct_info': self.correct_info,
            'context': self.context,
            'category': self.category,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'indexed': self.indexed
        }
