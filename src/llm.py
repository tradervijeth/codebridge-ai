"""
Language Model Integration for CodeBridge AI

This module handles interactions with local language models via Ollama.
"""

import requests
import json
from typing import List, Dict, Any

class LLMEngine:
    def __init__(self, model_name="codellama:7b", base_url="http://localhost:11434"):
        """
        Initialize the LLM engine.
        
        Args:
            model_name (str): Name of the Ollama model to use
            base_url (str): Base URL for Ollama API
        """
        self.model_name = model_name
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/generate"
    
    def check_ollama(self):
        """
        Check if Ollama is running and the model is available.
        
        Returns:
            bool: True if Ollama is running and model is available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            
            if response.status_code == 200:
                if any(model["name"] == self.model_name for model in models):
                    return True
                else:
                    print(f"Model {self.model_name} not found in Ollama. Available models:")
                    for model in models:
                        print(f" - {model['name']}")
                    print(f"\nTry installing with: ollama pull {self.model_name}")
                    return False
            else:
                print("Failed to connect to Ollama API.")
                return False
                
        except requests.exceptions.ConnectionError:
            print("Could not connect to Ollama. Make sure it's installed and running.")
            print("Install from: https://ollama.ai/")
            return False
    
    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Generate a response using the local language model.
        
        Args:
            query (str): The user's query
            context (List[Dict]): Relevant context chunks from the retrieval system
            
        Returns:
            str: The generated response
        """
        # Format context for the prompt
        context_text = ""
        for i, item in enumerate(context):
            source = item["metadata"]["source"].replace('.txt', '')
            context_text += f"\n--- Context {i+1} (Source: {source}) ---\n{item['text']}\n"
        
        # Create the prompt
        prompt = f"""You are CodeBridge AI, a helpful coding assistant specializing in full-stack development.
Answer the following question using the provided context. 
If the context doesn't contain relevant information, say so and provide general guidance.
Always include example code when appropriate.

{context_text}

Question: {query}

Answer:"""
        
        try:
            # Call local Ollama instance
            response = requests.post(
                self.api_endpoint,
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'stream': False
                }
            )
            
            response_data = response.json()
            return response_data.get('response', "Error: No response from model")
            
        except Exception as e:
            return f"Error generating response: {str(e)}"


if __name__ == "__main__":
    # Example usage
    from embeddings import EmbeddingEngine
    
    # Initialize engines
    embedding_engine = EmbeddingEngine()
    llm_engine = LLMEngine()
    
    # Check if Ollama is running
    if not llm_engine.check_ollama():
        print("Please start Ollama and make sure the model is available.")
        exit(1)
    
    # Test query
    query = "How do I use useState in React?"
    context = embedding_engine.query(query)
    
    print(f"\nGenerating response for: '{query}'")
    response = llm_engine.generate_response(query, context)
    
    print("\nResponse:")
    print(response)
