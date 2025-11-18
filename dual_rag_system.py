"""
Dual RAG system for email response generation
Uses two separate knowledge bases:
1. Historical emails (writing style)
2. Enrollment documents (factual information)
"""

from vector_store import VectorStore
from local_llm import LocalLLM
from api_llm import ApiLLM
from language_detector import LanguageDetector
import config


class DualRAGSystem:
    """RAG system with dual knowledge bases"""
    
    def __init__(self, workspace_id=None):
        print("=" * 60)
        print(f"Inizializzazione Dual RAG System (Workspace: {workspace_id or 'Global'})")
        print("=" * 60)
        
        self.workspace_id = workspace_id
        
        # Create workspace-specific collection names
        if workspace_id:
            historical_collection = f"{config.COLLECTION_HISTORICAL_EMAILS}_ws{workspace_id}"
            enrollment_collection = f"{config.COLLECTION_ENROLLMENT_DOCS}_ws{workspace_id}"
            corrections_collection = f"{config.COLLECTION_CORRECTIONS}_ws{workspace_id}"
        else:
            historical_collection = config.COLLECTION_HISTORICAL_EMAILS
            enrollment_collection = config.COLLECTION_ENROLLMENT_DOCS
            corrections_collection = config.COLLECTION_CORRECTIONS
        
        # Initialize three separate vector stores
        self.historical_emails_store = VectorStore(
            collection_name=historical_collection
        )
        self.enrollment_docs_store = VectorStore(
            collection_name=enrollment_collection
        )
        self.corrections_store = VectorStore(
            collection_name=corrections_collection
        )
        
        # Initialize LLM (API or local)
        if config.USE_API_LLM:
            self.llm = ApiLLM()
        else:
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
            'content': doc_data['content'],  # Changed from 'text' to 'content'
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
    
    def index_correction(self, correction_data):
        """
        Index a correction to prevent repeated mistakes
        
        Args:
            correction_data: Dict with 'wrong_info', 'correct_info', 'context'
        """
        # Create a searchable text combining wrong and correct info
        combined_text = f"WRONG: {correction_data['wrong_info']}\n\nCORRECT: {correction_data['correct_info']}"
        if correction_data.get('context'):
            combined_text += f"\n\nCONTEXT: {correction_data['context']}"
        
        chunks = [{
            'text': combined_text,
            'metadata': {
                'type': 'correction',
                'title': correction_data.get('title', 'Correction'),
                'category': correction_data.get('category', 'general'),
                'priority': correction_data.get('priority', 'medium')
            }
        }]
        
        self.corrections_store.add_documents(chunks)
    
    def generate_email_response(self, incoming_email, top_k_style=2, top_k_facts=3, top_k_corrections=2):
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
        print(f"   → Trovate {len(historical_contexts)} email")
        
        # Retrieve from enrollment documents (for facts)
        print(f"📚 Ricerca documenti iscrizione...")
        print(f"   → Vector store contiene: {self.enrollment_docs_store.get_collection_count()} chunks")
        factual_contexts = self.enrollment_docs_store.search(
            email_body,
            top_k=top_k_facts
        )
        print(f"   → Trovati {len(factual_contexts)} documenti")
        if factual_contexts:
            for i, ctx in enumerate(factual_contexts[:2], 1):  # Show first 2
                print(f"   → Doc {i}: distanza={ctx.get('distance', 'N/A'):.3f}, titolo={ctx['metadata'].get('title', 'N/A')}")
        else:
            print(f"   ⚠ Nessun documento trovato - possibile problema di ricerca")
        
        # Retrieve from corrections (to prevent mistakes)
        print(f"🔧 Ricerca correzioni...")
        print(f"   → Vector store contiene: {self.corrections_store.get_collection_count()} chunks")
        correction_contexts = self.corrections_store.search(
            email_body,
            top_k=top_k_corrections
        )
        print(f"   → Trovate {len(correction_contexts)} correzioni")
        
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
            lang_instruction,
            correction_contexts  # Pass corrections to prompt builder
        )
        
        print(f"\n🤖 Generazione risposta in {self.language_detector.get_language_name(detected_lang)}...")
        print(f"📏 Lunghezza prompt: {len(prompt)} caratteri")
        print(f"📝 Contesti recuperati: {len(historical_contexts)} storici, {len(factual_contexts)} documenti")
        response = self.llm.generate(prompt)
        
        # DEBUG: Show prompt details
        print(f"\n{'='*60}")
        print("DEBUG - PROMPT SENT TO MODEL:")
        print(f"{'='*60}")
        print(prompt[:2000] + "...\n[TRUNCATED]" if len(prompt) > 2000 else prompt)
        print(f"{'='*60}\n")
        
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
        """Format historical email contexts - simplified"""
        if not contexts:
            return "No previous examples available."
        
        # Only use the BEST match to avoid confusion
        ctx = contexts[0]
        return f"Example response style:\n{ctx['text'][:400]}...\n"
    
    def _format_factual_context(self, contexts):
        """Format enrollment document contexts - provide more detail"""
        if not contexts:
            return "No specific information available."
        
        # Combine top 2 chunks with REDUCED size to fit in prompt
        formatted = ""
        for ctx in contexts[:2]:  # Reduced from 3 to 2
            formatted += f"{ctx['text'][:300]}\n\n"  # Reduced from 500 to 300
        return formatted.strip()
    
    def _format_corrections_context(self, contexts):
        """Format corrections to highlight common mistakes"""
        if not contexts:
            return ""
        
        formatted = ""
        for ctx in contexts:
            formatted += f"- {ctx['text'][:400]}\n"
        return formatted.strip()
    
    def _build_generation_prompt(self, email_body, subject, style_ctx, factual_ctx, lang_instruction, correction_contexts=None):
        """Build the complete prompt for LLM"""
        # Get custom system prompt from database if available
        from database import SystemSettings, db
        custom_prompt = None
        try:
            if self.workspace_id:
                setting = SystemSettings.query.filter_by(key='system_prompt', workspace_id=self.workspace_id).first()
            else:
                setting = SystemSettings.query.filter_by(key='system_prompt', workspace_id=None).first()
            
            if setting and setting.value:
                custom_prompt = setting.value
        except:
            pass  # Database might not be ready yet
        
        # Use custom prompt if available, otherwise use default
        if custom_prompt:
            base_instruction = custom_prompt
        else:
            base_instruction = "Sei un assistente email per ITS MAKER ACADEMY FOUNDATION."
        
        # Build prompt with corrections to prevent mistakes
        corrections_text = ""
        if correction_contexts:
            corrections_text = "\n\nIMPORTANT CORRECTIONS:\n" + self._format_corrections_context(correction_contexts)
        
        # Simplified, more compact prompt
        prompt = f"""{base_instruction}

{lang_instruction}

INFORMATION:
{factual_ctx}{corrections_text}

STUDENT EMAIL:
{email_body}

RESPONSE:"""
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
