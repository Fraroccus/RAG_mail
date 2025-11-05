"""
Dual RAG system for email response generation
Uses two separate knowledge bases:
1. Historical emails (writing style)
2. Enrollment documents (factual information)
"""

from vector_store import VectorStore
from local_llm import LocalLLM
from language_detector import LanguageDetector
import config


class DualRAGSystem:
    """RAG system with dual knowledge bases"""
    
    def __init__(self):
        print("=" * 60)
        print("Inizializzazione Dual RAG System")
        print("=" * 60)
        
        # Initialize two separate vector stores
        self.historical_emails_store = VectorStore(
            collection_name=config.COLLECTION_HISTORICAL_EMAILS
        )
        self.enrollment_docs_store = VectorStore(
            collection_name=config.COLLECTION_ENROLLMENT_DOCS
        )
        
        self.llm = LocalLLM()
        self.language_detector = LanguageDetector()
        
        print("\n" + "=" * 60)
        print("✓ Dual RAG System Pronto!")
        print("=" * 60)
    
    def index_historical_email(self, email_data):
        """
        Index a historical email for style learning
        
        Args:
            email_data: Dict with 'query', 'response', 'metadata'
        """
        # Combine query and response for context
        combined_text = f"DOMANDA STUDENTE: {email_data['query']}\n\nRISPOSTA: {email_data['response']}"
        
        chunks = [{
            'text': combined_text,
            'metadata': {
                'type': 'historical_email',
                'language': email_data.get('language', 'unknown'),
                'country': email_data.get('country', 'unknown'),
                'program': email_data.get('program', 'unknown'),
                'tags': email_data.get('tags', '')
            }
        }]
        
        self.historical_emails_store.add_documents(chunks)
    
    def index_enrollment_document(self, doc_data):
        """
        Index an enrollment document
        
        Args:
            doc_data: Dict with 'content', 'metadata'
        """
        # Chunk large documents
        from text_chunker import TextChunker
        chunker = TextChunker()
        
        documents = [{
            'text': doc_data['content'],
            'metadata': {
                'type': 'enrollment_doc',
                'title': doc_data.get('title', 'Untitled'),
                'document_type': doc_data.get('document_type', 'general'),
                'country': doc_data.get('country', 'ALL'),
                'program': doc_data.get('program', 'ALL'),
                'language': doc_data.get('language', 'it'),
                'priority': doc_data.get('priority', 'medium')
            }
        }]
        
        chunks = chunker.chunk_documents(documents)
        self.enrollment_docs_store.add_documents(chunks)
    
    def generate_email_response(self, incoming_email, top_k_style=2, top_k_facts=3):
        """
        Generate response to incoming email using dual RAG
        
        Args:
            incoming_email: Dict with email details
            top_k_style: Number of historical emails to retrieve
            top_k_facts: Number of enrollment docs to retrieve
        
        Returns:
            Dict with response and metadata
        """
        email_body = incoming_email['body']
        email_subject = incoming_email.get('subject', '')
        
        # Detect language
        detected_lang = self.language_detector.detect_language(email_body)
        student_info = self.language_detector.extract_student_info(email_body)
        
        print(f"\n🌐 Lingua rilevata: {self.language_detector.get_language_name(detected_lang)}")
        print(f"📋 Tipo query: {', '.join(student_info['query_type']) if student_info['query_type'] else 'generale'}")
        
        # Retrieve from historical emails (for style)
        print(f"\n🔍 Ricerca email storiche...")
        historical_contexts = self.historical_emails_store.search(
            email_body,
            top_k=top_k_style
        )
        
        # Retrieve from enrollment documents (for facts)
        print(f"📚 Ricerca documenti iscrizione...")
        factual_contexts = self.enrollment_docs_store.search(
            email_body,
            top_k=top_k_facts
        )
        
        # Build prompts
        style_context = self._format_style_context(historical_contexts)
        factual_context = self._format_factual_context(factual_contexts)
        
        # Generate response with language instruction
        lang_instruction = self.language_detector.get_system_prompt_for_language(detected_lang)
        
        prompt = self._build_generation_prompt(
            email_body,
            email_subject,
            style_context,
            factual_context,
            lang_instruction
        )
        
        print(f"\n🤖 Generazione risposta in {self.language_detector.get_language_name(detected_lang)}...")
        response = self.llm.generate(prompt)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(historical_contexts, factual_contexts)
        
        return {
            'response': response,
            'detected_language': detected_lang,
            'confidence_score': confidence,
            'query_type': student_info['query_type'],
            'retrieved_contexts': {
                'historical': [ctx['text'] for ctx in historical_contexts],
                'factual': [ctx['text'] for ctx in factual_contexts]
            }
        }
    
    def _format_style_context(self, contexts):
        """Format historical email contexts"""
        if not contexts:
            return "Nessun esempio di stile disponibile."
        
        formatted = "ESEMPI DI EMAIL PRECEDENTI:\n\n"
        for i, ctx in enumerate(contexts, 1):
            formatted += f"Esempio {i}:\n{ctx['text']}\n\n"
        return formatted
    
    def _format_factual_context(self, contexts):
        """Format enrollment document contexts"""
        if not contexts:
            return "Nessuna informazione specifica disponibile."
        
        formatted = "INFORMAZIONI UFFICIALI SULL'ISCRIZIONE:\n\n"
        for i, ctx in enumerate(contexts, 1):
            title = ctx['metadata'].get('title', 'Documento')
            formatted += f"{title}:\n{ctx['text']}\n\n"
        return formatted
    
    def _build_generation_prompt(self, email_body, subject, style_ctx, factual_ctx, lang_instruction):
        """Build the complete prompt for LLM"""
        # Get custom system prompt from database if available
        from database import SystemSettings, db
        custom_prompt = None
        try:
            setting = SystemSettings.query.filter_by(key='system_prompt').first()
            if setting and setting.value:
                custom_prompt = setting.value
        except:
            pass  # Database might not be ready yet
        
        # Use custom prompt if available, otherwise use default
        if custom_prompt:
            base_instruction = custom_prompt
        else:
            base_instruction = "Sei un assistente email per ITS MAKER ACADEMY FOUNDATION."
        
        prompt = f"""{base_instruction}

{lang_instruction}

Devi rispondere all'email di uno studente internazionale interessato all'iscrizione.

{style_ctx}

{factual_ctx}

EMAIL DELLO STUDENTE:
Oggetto: {subject}
Messaggio: {email_body}

ISTRUZIONI:
1. Rispondi nella stessa lingua dell'email dello studente
2. Usa uno stile simile agli esempi forniti
3. Includi tutte le informazioni rilevanti dalle procedure di iscrizione
4. Sii professionale, cortese e completo
5. Se non hai informazioni specifiche, indica allo studente di contattare l'ufficio

RISPOSTA:
"""
        return prompt
    
    def _calculate_confidence(self, historical_contexts, factual_contexts):
        """
        Calculate confidence score based on retrieval quality
        
        Returns:
            Float between 0 and 1
        """
        if not factual_contexts:
            return 0.3  # Low confidence without factual info
        
        # Average distance scores (lower is better)
        hist_score = sum(ctx.get('distance', 1.0) for ctx in historical_contexts) / max(len(historical_contexts), 1)
        fact_score = sum(ctx.get('distance', 1.0) for ctx in factual_contexts) / max(len(factual_contexts), 1)
        
        # Convert to confidence (invert and normalize)
        # Distance typically ranges 0-2, with 0 being perfect match
        confidence = 1.0 - ((hist_score * 0.3 + fact_score * 0.7) / 2.0)
        
        return max(0.0, min(1.0, confidence))
    
    def get_stats(self):
        """Get statistics for both knowledge bases"""
        return {
            'historical_emails_count': self.historical_emails_store.get_collection_count(),
            'enrollment_docs_count': self.enrollment_docs_store.get_collection_count(),
            'llm_model': config.LLM_MODEL,
            'embedding_model': config.EMBEDDING_MODEL
        }
    
    def clear_all(self):
        """Clear both knowledge bases"""
        self.historical_emails_store.clear_collection()
        self.enrollment_docs_store.clear_collection()
