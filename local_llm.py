"""
Local LLM for text generation
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import config


class LocalLLM:
    """Local language model for generating responses"""
    
    def __init__(self):
        print(f"\nLoading LLM: {config.LLM_MODEL}")
        print("This may take a few minutes on first run (downloading model)...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            config.LLM_MODEL,
            torch_dtype=torch.float16 if config.DEVICE == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        
        # Move model to device
        self.model.to(config.DEVICE)
        self.model.eval()
        
        print(f"✓ LLM loaded on {config.DEVICE}")
    
    def generate(self, prompt: str, max_length: int = config.MAX_NEW_TOKENS) -> str:
        """
        Generate text based on prompt
        
        Args:
            prompt: Input prompt
            max_length: Maximum length of generated text
        
        Returns:
            Generated text
        """
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512
        ).to(config.DEVICE)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=config.TEMPERATURE,
                do_sample=True if config.TEMPERATURE > 0 else False,
                top_p=0.9,
                num_beams=2
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
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
