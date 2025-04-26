"""
Xcode Helper for CodeBridge AI

This module provides tools to work with Xcode and Swift projects.
It helps with error processing, code suggestions, and debugging.
"""

import os
import re
import sys
from llm import LLMEngine
from embeddings import EmbeddingEngine

class XcodeHelper:
    def __init__(self, llm_engine, embedding_engine):
        """
        Initialize the Xcode Helper.
        
        Args:
            llm_engine (LLMEngine): The language model engine
            embedding_engine (EmbeddingEngine): The embedding engine for retrieval
        """
        self.llm_engine = llm_engine
        self.embedding_engine = embedding_engine
    
    def clean_xcode_error(self, error_text):
        """
        Clean and format Xcode error messages for better processing.
        
        Args:
            error_text (str): Raw error text from Xcode
            
        Returns:
            dict: Cleaned error with file, line, and message
        """
        # Common error pattern in Xcode: filename:line:column: error: message
        error_pattern = r'([\w/\.\-]+):(\d+):(\d+): (error|warning): (.*)'
        
        # Extract basic error info
        match = re.search(error_pattern, error_text)
        if match:
            file_path = match.group(1)
            line_num = match.group(2)
            column = match.group(3)
            error_type = match.group(4)
            message = match.group(5)
            
            return {
                'file': os.path.basename(file_path),
                'path': file_path,
                'line': line_num,
                'column': column,
                'type': error_type,
                'message': message,
                'full_error': error_text
            }
        
        # If no match, return the whole error
        return {
            'file': 'unknown',
            'path': 'unknown',
            'line': 'unknown',
            'column': 'unknown',
            'type': 'error',
            'message': error_text,
            'full_error': error_text
        }
    
    def extract_code_context(self, file_path, line_num, context_lines=5):
        """
        Extract code context around the error.
        
        Args:
            file_path (str): Path to the file with the error
            line_num (str or int): Line number where the error occurred
            context_lines (int): Number of lines to include before and after
            
        Returns:
            str: Code context or None if file cannot be read
        """
        try:
            line_num = int(line_num)
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            # Calculate context range
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            
            # Extract relevant lines
            context = ''.join(lines[start:end])
            return context
        except Exception as e:
            print(f"Could not read file: {e}")
            return None
    
    def process_xcode_error(self, error_text, include_code=True):
        """
        Process an Xcode error and generate a solution.
        
        Args:
            error_text (str): The error text from Xcode
            include_code (bool): Whether to include code context
            
        Returns:
            str: The generated solution
        """
        # Clean the error
        error_info = self.clean_xcode_error(error_text)
        
        # Get code context if requested and possible
        code_context = None
        if include_code and error_info['path'] != 'unknown' and os.path.exists(error_info['path']):
            code_context = self.extract_code_context(error_info['path'], error_info['line'])
        
        # Get relevant documentation from vector database
        context = self.embedding_engine.query(error_info['message'], n_results=3)
        
        # Generate solution
        if code_context:
            # Use dedicated error handler with code context
            solution = self.llm_engine.generate_response_for_xcode_error(
                error_info['full_error'], 
                code_context
            )
        else:
            # Use regular response generation with context from the vector database
            query = f"Xcode error: {error_info['full_error']}"
            solution = self.llm_engine.generate_response(query, context)
        
        return solution
    
    def suggest_swift_implementation(self, feature_description):
        """
        Suggest a Swift implementation based on a feature description.
        
        Args:
            feature_description (str): Description of the feature to implement
            
        Returns:
            str: Suggested implementation
        """
        # Get relevant documentation
        context = self.embedding_engine.query(feature_description, n_results=3)
        
        # Generate implementation
        query = f"Implement in Swift: {feature_description}"
        implementation = self.llm_engine.generate_response(query, context)
        
        return implementation


def main():
    """CLI interface for Xcode Helper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Xcode Helper for CodeBridge AI")
    parser.add_argument("--error", help="Process an Xcode error")
    parser.add_argument("--error-file", help="Process Xcode errors from a file")
    parser.add_argument("--implement", help="Suggest a Swift implementation for a feature")
    args = parser.parse_args()
    
    # Initialize engines
    llm_engine = LLMEngine(model_name="GLM-4-0414", provider="lmstudio")
    embedding_engine = EmbeddingEngine()
    
    # Check if LM Studio is running
    if not llm_engine.check_connection():
        print("Please start LM Studio and make sure the API is enabled.")
        return
    
    # Initialize helper
    helper = XcodeHelper(llm_engine, embedding_engine)
    
    # Process based on arguments
    if args.error:
        print("Processing Xcode error...")
        solution = helper.process_xcode_error(args.error)
        print("\nSolution:")
        print("=" * 60)
        print(solution)
        print("=" * 60)
    
    elif args.error_file:
        print(f"Processing errors from file: {args.error_file}")
        try:
            with open(args.error_file, 'r') as f:
                error_text = f.read()
            solution = helper.process_xcode_error(error_text)
            print("\nSolution:")
            print("=" * 60)
            print(solution)
            print("=" * 60)
        except Exception as e:
            print(f"Error reading file: {e}")
    
    elif args.implement:
        print(f"Generating Swift implementation for: {args.implement}")
        implementation = helper.suggest_swift_implementation(args.implement)
        print("\nSuggested Implementation:")
        print("=" * 60)
        print(implementation)
        print("=" * 60)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
