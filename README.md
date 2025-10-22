# C2E - Context-to-Evidence System

A Python-based RAG (Retrieval-Augmented Generation) system with PubMed integration for biomedical literature search.

## Features

- **LLM Integration**: Call local Ollama models for text generation
- **RAG Architecture**: Extensible base class for implementing different RAG strategies
- **PubMed API**: Search and retrieve biomedical papers from NCBI databases
- **PMC Full-Text**: Access open-access full-text papers from PubMed Central
- **Environment Configuration**: Secure API key management via `.env` files

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

### Setting Up NCBI API Key

To get better rate limits (10 requests/second vs 3 requests/second), get a free API key from:
https://www.ncbi.nlm.nih.gov/account/settings/

#### Option 1: Using .env file (Recommended)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   NCBI_API_KEY=your_actual_api_key_here
   NCBI_EMAIL=your.email@example.com
   ```

3. The API key will be automatically loaded when you use the PubMed module:
   ```python
   from helpers.pubmed import set_api_key, get_papers
   
   # Automatically loads from .env
   set_api_key()
   
   # Now search papers
   papers = get_papers("machine learning healthcare", top_k=5)
   ```

#### Option 2: Manual Configuration

```python
from helpers.pubmed import set_api_key

set_api_key("your_api_key", "your.email@example.com", load_from_env=False)
```

## Usage Examples

### PubMed Search

```bash
python examples/example_pubmed.py
```

### Ollama LLM

```bash
python examples/example_use_ollama.py
```

## Project Structure

```
c2e/
├── helpers/
│   ├── llm.py           # Ollama LLM wrapper
│   └── pubmed.py        # PubMed API integration
├── rag/
│   ├── base_rag.py      # Abstract RAG base class
│   └── simple_rag.py    # Simple RAG implementation
├── examples/
│   ├── example_pubmed.py      # PubMed usage examples
│   └── example_use_ollama.py  # LLM usage examples
├── .env.example         # Environment template
└── requirements.txt
```

## Self RAG
## FLARE