"""
Language detection and multilingual response generation
"""

from langdetect import detect, LangDetectException
import re


class LanguageDetector:
    """Detect and handle multiple languages"""
    
    # Language code mapping
    LANGUAGE_NAMES = {
        'it': 'Italian',
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'ar': 'Arabic',
        'ur': 'Urdu',
        'hi': 'Hindi',
        'bn': 'Bengali'
    }
    
    def __init__(self):
        pass
    
    def detect_language(self, text):
        """
        Detect the language of a text
        
        Args:
            text: Input text to analyze
        
        Returns:
            Language code (e.g., 'it', 'en', 'ar') or 'unknown'
        """
        # Clean text for better detection
        cleaned_text = self._clean_text(text)
        
        if not cleaned_text or len(cleaned_text) < 10:
            return 'unknown'
        
        try:
            lang_code = detect(cleaned_text)
            return lang_code if lang_code in self.LANGUAGE_NAMES else lang_code
        except LangDetectException:
            return 'unknown'
    
    def _clean_text(self, text):
        """Remove HTML tags and excessive whitespace"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove email signatures markers
        text = re.sub(r'(--|_____|Sent from|Inviato da).*', '', text, flags=re.DOTALL)
        return text.strip()
    
    def get_language_name(self, lang_code):
        """Get human-readable language name"""
        return self.LANGUAGE_NAMES.get(lang_code, lang_code.upper())
    
    def get_system_prompt_for_language(self, lang_code):
        """
        Generate system prompt instructing the LLM to respond in detected language
        
        Args:
            lang_code: Language code
        
        Returns:
            System prompt string
        """
        language_instructions = {
            'it': "Rispondi in italiano. Mantieni un tono professionale e cortese.",
            'en': "Respond in English. Maintain a professional and courteous tone.",
            'fr': "Répondez en français. Maintenez un ton professionnel et courtois.",
            'es': "Responde en español. Mantén un tono profesional y cortés.",
            'ar': "الرد باللغة العربية. حافظ على نبرة مهنية ومهذبة.",
            'ur': "اردو میں جواب دیں۔ پیشہ ورانہ اور شائستہ لہجہ برقرار رکھیں۔",
            'hi': "हिंदी में उत्तर दें। पेशेवर और विनम्र स्वर बनाए रखें।",
            'bn': "বাংলায় উত্তর দিন। একটি পেশাদার এবং বিনয়ী স্বর বজায় রাখুন।"
        }
        
        return language_instructions.get(
            lang_code,
            f"Respond in {self.get_language_name(lang_code)}. Maintain a professional and courteous tone."
        )
    
    def extract_student_info(self, email_text):
        """
        Extract useful information from email text
        
        Args:
            email_text: Email body text
        
        Returns:
            Dictionary with extracted information
        """
        info = {
            'has_questions': False,
            'mentions_deadline': False,
            'mentions_visa': False,
            'mentions_documents': False,
            'mentions_fees': False,
            'query_type': []
        }
        
        text_lower = email_text.lower()
        
        # Check for questions
        question_markers = ['?', 'come', 'quando', 'dove', 'perché', 'cosa', 'quale',
                           'how', 'when', 'where', 'why', 'what', 'which',
                           'كيف', 'متى', 'أين', 'لماذا', 'ما']
        info['has_questions'] = any(marker in text_lower for marker in question_markers)
        
        # Detect topics (multilingual keywords)
        if any(word in text_lower for word in ['deadline', 'scadenza', 'termine', 'موعد', 'آخر تاريخ']):
            info['mentions_deadline'] = True
            info['query_type'].append('deadline')
        
        if any(word in text_lower for word in ['visa', 'visto', 'تأشيرة', 'वीज़ा']):
            info['mentions_visa'] = True
            info['query_type'].append('visa')
        
        if any(word in text_lower for word in ['document', 'documento', 'certificat', 'وثيقة', 'दस्तावेज़']):
            info['mentions_documents'] = True
            info['query_type'].append('documents')
        
        if any(word in text_lower for word in ['fee', 'cost', 'price', 'tuition', 'tassa', 'costo', 'prezzo', 'retta',
                                                'تكلفة', 'رسوم', 'शुल्क']):
            info['mentions_fees'] = True
            info['query_type'].append('fees')
        
        if any(word in text_lower for word in ['application', 'apply', 'enroll', 'admission', 'iscrizione', 'domanda',
                                                'candidatura', 'ammission', 'تطبيق', 'تسجيل', 'आवेदन']):
            info['query_type'].append('application')
        
        return info
