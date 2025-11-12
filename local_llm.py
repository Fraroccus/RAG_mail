"""
Local LLM for text generation
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, pipeline
import torch
import config


class LocalLLM:
    """Local language model for generating responses"""
    
    def __init__(self):
        print(f"\nLoading LLM: {config.LLM_MODEL}")
        print("This may take a few minutes on first run (downloading model)...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL, trust_remote_code=True)
        
        # Detect model type and load appropriately
        if "t5" in config.LLM_MODEL.lower():
            # Seq2Seq model (T5)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                config.LLM_MODEL,
                torch_dtype=torch.float16 if config.DEVICE == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            )
            self.is_causal = False
        else:
            # Causal LM (Phi, Llama, Mistral, etc.)
            self.model = AutoModelForCausalLM.from_pretrained(
                config.LLM_MODEL,
                torch_dtype=torch.float16 if config.DEVICE == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            self.is_causal = True
        
        # Move model to device
        self.model.to(config.DEVICE)
        self.model.eval()
        
        # Set pad token if needed
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"✓ LLM loaded on {config.DEVICE}")
    
    def generate(self, prompt: str, max_new_tokens: int = config.MAX_NEW_TOKENS) -> str:
        """
        Generate text based on prompt
        
        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of new tokens to generate
        
        Returns:
            Generated text
        """
        # Tokenize input
        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=2048
        ).to(config.DEVICE)
        
        # Generate based on model type
        with torch.no_grad():
            if self.is_causal:
                # Causal LM generation (Phi, Llama, etc.)
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=False  # Disable cache to avoid compatibility issues
                )
                # Decode and remove input prompt
                full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = full_text[len(prompt):].strip()
            else:
                # Seq2Seq generation (T5)
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    min_length=100,
                    temperature=0.3,
                    do_sample=False,
                    num_beams=4,
                    repetition_penalty=1.2,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"\n📏 Tokens generati: {len(outputs[0])} | Lunghezza risposta: {len(response)} caratteri")
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
