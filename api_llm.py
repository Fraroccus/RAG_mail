"""
API-based LLM for fast text generation using external services
"""

import requests
import config


class ApiLLM:
    """LLM using external API (Groq, OpenAI, etc.)"""
    
    def __init__(self):
        print(f"\nInitializing API LLM: {config.API_PROVIDER}")
        
        if config.API_PROVIDER == "groq":
            if not config.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in .env file. Get one free at https://console.groq.com")
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.api_key = config.GROQ_API_KEY
            self.model = config.GROQ_MODEL
            print(f"✓ Using Groq API with model: {self.model}")
        else:
            raise ValueError(f"API provider '{config.API_PROVIDER}' not supported yet")
    
    def generate(self, prompt: str, max_new_tokens: int = config.MAX_NEW_TOKENS) -> str:
        """
        Generate text using API
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_new_tokens,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            
            print(f"\n📏 Tokens usati: ~{result['usage']['total_tokens']} | Lunghezza risposta: {len(generated_text)} caratteri")
            
            return generated_text.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Errore API: {e}")
            # Print full error response for debugging
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"❌ Dettaglio errore: {error_detail}")
                except:
                    print(f"❌ Response text: {e.response.text}")
            return f"Errore nella generazione della risposta: {str(e)}"
    
    def generate_with_context(self, query: str, context_chunks: list) -> str:
        """
        Generate response using retrieved context
        
        Args:
            query: User query
            context_chunks: Retrieved relevant chunks
        
        Returns:
            Generated response
        """
        # Build context from chunks
        context = "\n\n".join([chunk['text'] for chunk in context_chunks])
        
        # Create prompt
        prompt = f"""Answer the following question based on the context provided.

Context:
{context}

Question: {query}

Answer:"""
        
        # Generate response
        response = self.generate(prompt)
        return response
