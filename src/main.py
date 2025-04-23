"""
Main CLI interface for CodeBridge AI

This module provides a command-line interface for interacting with the AI coding assistant.
"""

import os
import sys
import argparse
from embeddings import EmbeddingEngine
from llm import LLMEngine

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the CodeBridge AI header."""
    clear_screen()
    print("=" * 60)
    print("                      CodeBridge AI")
    print("     Your local AI assistant for code and development")
    print("=" * 60)
    print("Type 'exit', 'quit', or press Ctrl+C to exit.")
    print("Type 'clear' to clear the screen.")
    print("=" * 60)

def main():
    """Main function to run the CLI interface."""
    parser = argparse.ArgumentParser(description="CodeBridge AI - Local Coding Assistant")
    parser.add_argument("--model", default="codellama:7b", help="Ollama model to use")
    parser.add_argument("--setup", action="store_true", help="Run initial setup (process documents)")
    args = parser.parse_args()
    
    # Initialize engines
    embedding_engine = EmbeddingEngine()
    llm_engine = LLMEngine(model_name=args.model)
    
    # Run setup if requested
    if args.setup:
        print("Running initial setup...")
        embedding_engine.process_documents()
        print("Setup complete!")
        return
    
    # Check if Ollama is running
    if not llm_engine.check_ollama():
        print("Please start Ollama and make sure the model is available.")
        return
    
    # Check if vector database has documents
    try:
        collection_info = embedding_engine.collection.count()
        if collection_info == 0:
            print("No documents found in the vector database.")
            print("Please run the setup first with: python main.py --setup")
            return
    except Exception as e:
        print(f"Error checking vector database: {e}")
        print("Please run the setup first with: python main.py --setup")
        return
    
    # Main interaction loop
    try:
        print_header()
        
        history = []
        
        while True:
            # Get user query
            user_query = input("\n> ")
            
            # Handle special commands
            if user_query.lower() in ['exit', 'quit']:
                print("Thank you for using CodeBridge AI!")
                break
            elif user_query.lower() == 'clear':
                print_header()
                continue
            elif not user_query.strip():
                continue
            
            # Get relevant context from vector database
            print("Searching documentation...")
            context = embedding_engine.query(user_query, n_results=3)
            
            # Generate response
            print("Generating response...")
            response = llm_engine.generate_response(user_query, context)
            
            # Display response
            print("\n" + "=" * 60)
            print(response)
            print("=" * 60)
            
            # Add to history
            history.append({"query": user_query, "response": response})
            
    except KeyboardInterrupt:
        print("\nThank you for using CodeBridge AI!")

if __name__ == "__main__":
    main()
