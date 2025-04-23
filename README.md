# CodeBridge AI

## Overview
CodeBridge AI is a local AI coding assistant that specializes in full-stack development, initially focused on the MERN stack (MongoDB, Express, React, Node.js). It uses Retrieval-Augmented Generation (RAG) to enhance AI responses with specific programming resources.

## Features
- Knowledge base of documentation, code examples, and tutorials
- Local vector database for efficient retrieval
- Open-source language models for code generation
- Simple developer interface to describe coding tasks

## Technology Stack
- **Embedding**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB
- **Language Model**: Local models via Ollama (CodeLlama, Phi-2)
- **Web Scraping**: BeautifulSoup
- **Interface**: Command-line (initial version)

## Getting Started

### Prerequisites
- Python 3.8+
- Ollama (for running local LLMs)
- 16GB RAM recommended

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/codebridge-ai.git
cd codebridge-ai

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install Ollama and pull models
# Follow instructions at https://ollama.ai/
# then: ollama pull codellama:7b
```

## Project Structure
- `src/`: Source code
- `data/`: Knowledge base storage
- `docs/`: Documentation

## Roadmap
- [x] Initial project setup
- [ ] Knowledge base creation for React
- [ ] Embedding and vector storage implementation
- [ ] Basic retrieval system
- [ ] Local LLM integration
- [ ] Command-line interface
- [ ] Expand to full MERN stack
- [ ] Web interface

## License
MIT

## Contributing
This is a personal project but suggestions and feedback are welcome.
