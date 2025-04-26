"""
Language Model Integration for CodeBridge AI

This module handles interactions with local language models via LM Studio and Ollama.
"""

import requests
import json
from typing import List, Dict, Any
import os
import re

class LLMEngine:
    def __init__(self, model_name="GLM-4-0414", 
                 provider="lmstudio",  # Options: "lmstudio" or "ollama"
                 lmstudio_base_url="http://localhost:1234",
                 ollama_base_url="http://localhost:11434"):
        """
        Initialize the LLM engine.
        
        Args:
            model_name (str): Name of the model to use
            provider (str): "lmstudio" or "ollama"
            lmstudio_base_url (str): Base URL for LM Studio API
            ollama_base_url (str): Base URL for Ollama API
        """
        self.model_name = model_name
        self.provider = provider.lower()
        self.lmstudio_base_url = lmstudio_base_url
        self.ollama_base_url = ollama_base_url
        
        # Set API endpoints based on provider
        if self.provider == "lmstudio":
            self.api_endpoint = f"{lmstudio_base_url}/v1/chat/completions"
        else:  # ollama
            self.api_endpoint = f"{ollama_base_url}/api/generate"
    
    def check_connection(self):
        """
        Check if the LLM provider is running and the model is available.
        
        Returns:
            bool: True if provider is running and model is available
        """
        try:
            if self.provider == "lmstudio":
                response = requests.get(f"{self.lmstudio_base_url}/v1/models")
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    available_models = [model.get("id") for model in models]
                    if not models:
                        print("No models found in LM Studio.")
                        print("Make sure you have started a model in LM Studio.")
                        return False
                    
                    print(f"Available models in LM Studio: {', '.join(available_models)}")
                    return True
                else:
                    print(f"Failed to connect to LM Studio API. Status code: {response.status_code}")
                    return False
            else:  # ollama
                response = requests.get(f"{self.ollama_base_url}/api/tags")
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
            if self.provider == "lmstudio":
                print("Could not connect to LM Studio. Make sure it's running and the API is enabled.")
                print("To enable the API in LM Studio:")
                print("1. Open LM Studio")
                print("2. Go to Settings")
                print("3. Enable the 'Local Server' option and note the port (default is 1234)")
            else:
                print("Could not connect to Ollama. Make sure it's installed and running.")
                print("Install from: https://ollama.ai/")
            return False
    
    def detect_query_type(self, query: str) -> str:
        """
        Detect the type of query to optimize the system prompt.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The type of query detected ("swift_error", "swift_code", "general")
        """
        # Check for Swift error patterns
        swift_error_patterns = [
            r"error:",
            r"warning:",
            r"cannot find",
            r"value of type .* has no member",
            r"undeclared type",
            r"unexpectedly found nil",
            r"Thread \d+: .* error",
            r"fatal error",
            r"unresolved identifier",
            r"expression was too complex",
            r"failed to build"
        ]
        
        # Check for Swift/iOS development patterns
        swift_code_patterns = [
            r"swift",
            r"xcode",
            r"ios",
            r"swiftui",
            r"uikit",
            r"cocoa",
            r"appkit",
            r"foundation",
            r"core data",
            r"watchkit",
            r"app clip",
            r"@state",
            r"@binding",
            r"@published",
            r"@environment",
            r"struct.*:.*view",
            r"func.*some view"
        ]
        
        # Check for Swift error patterns
        for pattern in swift_error_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "swift_error"
        
        # Check for Swift code patterns
        for pattern in swift_code_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "swift_code"
        
        # Default to general query
        return "general"
    
    def get_system_prompt(self, query_type: str) -> str:
        """
        Get the appropriate system prompt based on query type.
        
        Args:
            query_type (str): The type of query ("swift_error", "swift_code", "general")
            
        Returns:
            str: The system prompt
        """
        if query_type == "swift_error":
            return """You are CodeBridge AI, an expert Swift and iOS development assistant specializing in debugging and error resolution.

You help developers understand and fix errors in their Swift code. When analyzing an error:
1. Clearly identify the error type and root cause
2. Provide a step-by-step solution with clear explanations
3. Include example code that solves the problem
4. Suggest ways to avoid similar issues in the future

Use the provided context to provide accurate solutions specific to Swift, SwiftUI, and UIKit development.
If you're not completely sure of a solution, mention alternatives and explain the tradeoffs.
Always format Swift code properly using Swift syntax conventions."""

        elif query_type == "swift_code":
            return """You are CodeBridge AI, an expert Swift and iOS development assistant.

You help developers write clean, efficient, and modern Swift code. When providing code:
1. Follow Swift best practices and conventions
2. Write code that's easy to maintain and debug
3. Provide explanations for non-obvious parts
4. Consider performance and memory implications
5. Use modern Swift features and APIs when appropriate

Use the provided context to provide accurate and effective Swift code solutions.
Include helpful comments to explain the code's functionality.
Format Swift code properly using Swift syntax conventions."""

        else:
            return """You are CodeBridge AI, a helpful coding assistant specializing in software development.

Answer the following question using the provided context. 
If the context doesn't contain relevant information, say so and provide general guidance.
Always include example code when appropriate."""
    
    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Generate a response using the language model.
        
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
        
        # Detect query type and get appropriate system prompt
        query_type = self.detect_query_type(query)
        system_prompt = self.get_system_prompt(query_type)

        try:
            if self.provider == "lmstudio":
                # LM Studio uses OpenAI-compatible API
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the relevant context:\n{context_text}\n\nQuestion: {query}"}
                ]
                
                response = requests.post(
                    self.api_endpoint,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data["choices"][0]["message"]["content"]
                else:
                    return f"Error: API returned status code {response.status_code}. Response: {response.text}"
            
            else:  # ollama
                # Create the prompt for Ollama
                prompt = f"{system_prompt}\n\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
                
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
    
    def generate_response_for_xcode_error(self, error_message: str, code_context: str = None) -> str:
        """
        Generate a response specifically for Xcode compilation errors.
        
        Args:
            error_message (str): The error message from Xcode
            code_context (str, optional): The code surrounding the error
            
        Returns:
            str: The generated response
        """
        # Prepare the prompt
        system_prompt = """You are CodeBridge AI, an expert Swift and iOS development assistant specializing in debugging Xcode errors.

Analyze the provided Xcode error message and code context to:
1. Identify the exact error and its root cause
2. Explain why this error is occurring
3. Provide a complete, working solution with code examples
4. Suggest how to avoid this error in the future

Be specific and precise in your analysis and solution."""

        # Format user content
        user_content = f"Xcode Error Message:\n{error_message}\n\n"
        if code_context:
            user_content += f"Code Context:\n```swift\n{code_context}\n```\n\n"
        
        user_content += "Please help me fix this error. Provide a complete solution with code examples."

        try:
            if self.provider == "lmstudio":
                # LM Studio uses OpenAI-compatible API
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]
                
                response = requests.post(
                    self.api_endpoint,
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "stream": False
                    }
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    return response_data["choices"][0]["message"]["content"]
                else:
                    return f"Error: API returned status code {response.status_code}. Response: {response.text}"
            
            else:  # ollama
                # Create the prompt for Ollama
                prompt = f"{system_prompt}\n\n{user_content}\n\nAnswer:"
                
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
    
    # Use LM Studio
    llm_engine = LLMEngine(model_name="GLM-4-0414", provider="lmstudio")
    
    # Check if LM Studio is running
    if not llm_engine.check_connection():
        print("Please start LM Studio and make sure the API is enabled.")
        exit(1)
    
    # Test query
    query = "How do I use SwiftUI's NavigationView?"
    context = embedding_engine.query(query)
    
    print(f"\nGenerating response for: '{query}'")
    response = llm_engine.generate_response(query, context)
    
    print("\nResponse:")
    print(response)
    
    # Test Xcode error handling
    xcode_error = "Cannot find 'ContentView' in scope"
    code_context = """import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}"""
    
    print("\nTesting Xcode error handling:")
    error_response = llm_engine.generate_response_for_xcode_error(xcode_error, code_context)
    
    print("\nError Response:")
    print(error_response)
