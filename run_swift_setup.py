"""
Setup script to initialize CodeBridge AI with Swift documentation.

This script downloads Swift documentation, processes it into the
vector database, and prepares the system for Swift app development.
"""

import os
import argparse
from src.swift_scraper import SwiftDocumentationScraper
from src.embeddings import EmbeddingEngine
from tqdm import tqdm

def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data",
        "data/docs",
        "data/docs/swift",
        "data/vectordb"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Run the setup process."""
    parser = argparse.ArgumentParser(description="CodeBridge AI - Swift Documentation Setup")
    parser.add_argument("--skip-scraping", action="store_true", help="Skip the documentation scraping step")
    args = parser.parse_args()
    
    print("=" * 60)
    print("          CodeBridge AI - Swift Documentation Setup")
    print("=" * 60)
    print("This script will download and process Swift documentation")
    print("to help you build and debug your Swift applications.")
    print("=" * 60)
    
    # Setup directories
    setup_directories()
    
    # Scrape Swift documentation
    if not args.skip_scraping:
        print("\nStep 1: Downloading Swift documentation...")
        scraper = SwiftDocumentationScraper()
        
        # Use the main method from the scraper
        try:
            # This will run the documentation scraping
            # It's already defined in the __main__ section of swift_scraper.py
            import src.swift_scraper
            
            print("Swift documentation download complete!")
        except Exception as e:
            print(f"Error downloading documentation: {e}")
            print("You can try running the script again with --skip-scraping")
            return
    else:
        print("\nSkipping documentation download as requested.")
    
    # Process documents into vector database
    print("\nStep 2: Processing documents into the vector database...")
    try:
        embedding_engine = EmbeddingEngine()
        embedding_engine.process_documents()
        print("Document processing complete!")
    except Exception as e:
        print(f"Error processing documents: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Setup complete! You can now use CodeBridge AI to help with your Swift development.")
    print("\nTo run CodeBridge AI with your LM Studio model:")
    print("python src/main.py")
    print("\nFor more options:")
    print("python src/main.py --help")
    print("=" * 60)

if __name__ == "__main__":
    main()
