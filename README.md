# C2E - Claim to Evidence System

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

### Health Fact-Checking Datasets

```bash
# Quick demo of all three datasets
python examples/demo_datasets.py

# Comprehensive examples
python examples/example_load_datasets.py
```

The project includes loaders for three health-related fact-checking datasets:
- **HEALTHVER**: Health claim verification dataset
- **PUBHEALTH**: Public health fact-checking dataset  
- **SCIFACT**: Scientific fact verification dataset

See [datasets/README.md](datasets/README.md) for detailed information.

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
├── datasets/
│   ├── load_datasets.py       # Dataset loaders
│   └── README.md              # Dataset documentation
├── helpers/
│   ├── llm.py                 # Ollama LLM wrapper
│   └── pubmed.py              # PubMed API integration
├── rag/
│   └── base_rag.py            # Abstract RAG base class
├── examples/
│   ├── demo_datasets.py       # Quick dataset demo
│   ├── example_load_datasets.py  # Dataset usage examples
│   ├── example_pubmed.py      # PubMed usage examples
│   └── example_use_ollama.py  # LLM usage examples
├── .env.example               # Environment template
└── requirements.txt
```
