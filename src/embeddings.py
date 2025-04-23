"""
Embedding and Retrieval System for CodeBridge AI

This module handles the creation of text embeddings and
vector database storage/retrieval.
"""

import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

class EmbeddingEngine:
    def __init__(self, docs_dir="../data/docs", db_dir="../data/vectordb"):
        """
        Initialize the embedding engine.
        
        Args:
            docs_dir (str): Directory containing documentation text files
            db_dir (str): Directory to store the vector database
        """
        # Create directories if they don't exist
        os.makedirs(docs_dir, exist_ok=True)
        os.makedirs(db_dir, exist_ok=True)
        
        self.docs_dir = docs_dir
        self.db_dir = db_dir
        
        # Initialize the embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=db_dir)
        
        # Check if collection exists, if not create it
        try:
            self.collection = self.client.get_collection("code_docs")
            print("Loaded existing vector database.")
        except:
            self.collection = self.client.create_collection("code_docs")
            print("Created new vector database.")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into chunks for embedding.
        
        Args:
            text (str): The text to split
            chunk_size (int): The approximate chunk size in characters
            overlap (int): The overlap between chunks in characters
            
        Returns:
            List[str]: List of text chunks
        """
        chunks = []
        
        # Simple chunking strategy based on paragraphs
        paragraphs = text.split('\n\n')
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            if current_size + paragraph_size > chunk_size:
                # Join the current chunk and add it to chunks
                chunks.append('\n\n'.join(current_chunk))
                
                # Start a new chunk with overlap
                if overlap > 0 and len(current_chunk) > 0:
                    # Keep the last paragraph for overlap
                    current_chunk = [current_chunk[-1]]
                    current_size = len(current_chunk[-1])
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(paragraph)
            current_size += paragraph_size
        
        # Add the last chunk if there is one
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def process_documents(self):
        """
        Process all documents in the docs directory, 
        create embeddings and store in the vector database.
        """
        doc_files = [f for f in os.listdir(self.docs_dir) if f.endswith('.txt')]
        
        if not doc_files:
            print("No documentation files found. Please run the scraper first.")
            return
        
        print(f"Processing {len(doc_files)} documentation files...")
        
        all_ids = []
        all_texts = []
        all_metadatas = []
        
        for filename in tqdm(doc_files):
            file_path = os.path.join(self.docs_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Chunk the text
            chunks = self.chunk_text(text)
            
            # Create IDs, texts and metadata for each chunk
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename.replace('.txt', '')}_{i}"
                all_ids.append(chunk_id)
                all_texts.append(chunk)
                all_metadatas.append({"source": filename, "chunk": i})
        
        # Generate embeddings in batches
        print("Generating embeddings...")
        embeddings = self.model.encode(all_texts, show_progress_bar=True)
        
        # Add to collection
        print("Adding to vector database...")
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings.tolist(),
            metadatas=all_metadatas,
            documents=all_texts
        )
        
        print(f"Successfully added {len(all_ids)} chunks to the vector database.")
    
    def query(self, question: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector database for relevant chunks.
        
        Args:
            question (str): The query question
            n_results (int): Number of results to return
            
        Returns:
            List[Dict]: List of relevant chunks with metadata
        """
        # Generate embedding for the question
        question_embedding = self.model.encode(question).tolist()
        
        # Query the collection
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results


if __name__ == "__main__":
    # Example usage
    engine = EmbeddingEngine()
    engine.process_documents()
    
    # Test query
    results = engine.query("How do I use useState in React?")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Source: {result['metadata']['source']}):")
        print(f"Relevance: {result['distance']}")
        print(f"Text: {result['text'][:200]}...")
