# Health Fact-Checking Datasets

This directory contains loaders for three health-related fact-checking datasets commonly used for claim verification research.

## Datasets

### 1. HEALTHVER
**Source:** https://github.com/sarrouti/HealthVer

A dataset for health claim verification containing claims annotated with their veracity.

**Format:** CSV files (train, dev, test)

**Usage:**
```python
from datasets.load_datasets import load_healthver

# Load a specific split
train_df = load_healthver('train')

# Load all splits
all_data = load_healthver('all')
```

### 2. PUBHEALTH
**Source:** https://github.com/neemakot/Health-Fact-Checking

A large-scale public health fact-checking dataset with explainable evidence.

**Format:** TSV files (train, dev, test)

**Features:**
- Claim text
- Evidence sources
- Explanations
- Fact-checker information
- Publication dates
- Labels (true, false, mixture, unproven)

**Manual Download Required:**
Download from: https://drive.google.com/file/d/1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj/view

**Usage:**
```python
from datasets.load_datasets import load_pubhealth

# Load a specific split
train_df = load_pubhealth('train')

# Load all splits
all_data = load_pubhealth('all')
```

### 3. SCIFACT
**Source:** https://github.com/allenai/scifact

Scientific fact verification dataset based on scientific abstracts and claims.

**Format:** JSONL files

**Components:**
- Claims (train, dev, test)
- Corpus of scientific abstracts
- Evidence annotations
- Rationale selections

**Usage:**
```python
from datasets.load_datasets import load_scifact

# Load claims only
data = load_scifact('train')

# Load claims with corpus
data = load_scifact('train', include_corpus=True)

# Access claims and corpus
claims = data['claims']
corpus = data['corpus']  # if include_corpus=True
```

## Installation

Install required dependencies:

```bash
pip install -r ../requirements.txt
```

## Quick Start

### Load a Single Dataset

```python
from datasets.load_datasets import load_healthver, load_pubhealth, load_scifact

# HEALTHVER
healthver_train = load_healthver('train', data_dir='./data')
print(f"Loaded {len(healthver_train)} HEALTHVER examples")

# PUBHEALTH (requires manual download)
pubhealth_train = load_pubhealth('train', data_dir='./data')
print(f"Loaded {len(pubhealth_train)} PUBHEALTH examples")

# SCIFACT
scifact_data = load_scifact('train', data_dir='./data', include_corpus=True)
print(f"Loaded {len(scifact_data['claims'])} SCIFACT claims")
print(f"Loaded {len(scifact_data['corpus'])} corpus documents")
```

### Get Dataset Statistics

```python
from datasets.load_datasets import get_dataset_stats

stats = get_dataset_stats(data_dir='./data')
print(stats)
```

### Using Class-Based Loaders

```python
from datasets.load_datasets import HealthVerLoader, PubHealthLoader, SciFactLoader

# Create loader instances
healthver = HealthVerLoader(data_dir='./data')
pubhealth = PubHealthLoader(data_dir='./data')
scifact = SciFactLoader(data_dir='./data')

# Download datasets
healthver.download()
scifact.download()
# pubhealth.download()  # Shows manual download instructions

# Load data
train_df = healthver.load('train')
claims = scifact.load_claims('train')
corpus = scifact.load_corpus()
```

## Examples

See `../examples/example_load_datasets.py` for comprehensive usage examples:

```bash
cd examples
python example_load_datasets.py
```

## Data Directory Structure

After downloading all datasets, your data directory will look like:

```
data/
├── healthver/
│   ├── healthver_train.csv
│   ├── healthver_dev.csv
│   └── healthver_test.csv
├── pubhealth/
│   ├── train.tsv
│   ├── dev.tsv
│   ├── test.tsv
│   └── lexicon.txt
└── scifact/
    ├── data.tar.gz
    └── data/
        ├── corpus.jsonl
        ├── claims_train.jsonl
        ├── claims_dev.jsonl
        └── claims_test.jsonl
```

## Dataset Specifications

| Dataset | Train | Dev | Test | Total | Format |
|---------|-------|-----|------|-------|--------|
| HEALTHVER | ~8,500 | ~1,000 | ~1,000 | ~10,500 | CSV |
| PUBHEALTH | 9,817 | 1,227 | 1,235 | 12,279 | TSV |
| SCIFACT Claims | 809 | 300 | 300 | 1,409 | JSONL |
| SCIFACT Corpus | - | - | - | 5,183 | JSONL |

## Labels

### HEALTHVER
- Support
- Refute
- Neutral

### PUBHEALTH
- true
- false
- mixture
- unproven

### SCIFACT
- SUPPORTS
- REFUTES
- NOT_ENOUGH_INFO

## Citation

If you use these datasets, please cite the original papers:

### HEALTHVER
```bibtex
@inproceedings{sarrouti2021healthver,
  title={Evidence-based Fact-Checking of Health-related Claims},
  author={Sarrouti, Mourad and Ben Abacha, Asma and Mrabet, Yassine and Demner-Fushman, Dina},
  booktitle={Findings of EMNLP 2021},
  year={2021}
}
```

### PUBHEALTH
```bibtex
@inproceedings{kotonya2020explainable,
  title={Explainable Automated Fact-Checking for Public Health Claims},
  author={Kotonya, Neema and Toni, Francesca},
  booktitle={EMNLP 2020},
  year={2020}
}
```

### SCIFACT
```bibtex
@inproceedings{wadden2020fact,
  title={Fact or Fiction: Verifying Scientific Claims},
  author={Wadden, David and Lin, Shanchuan and Lo, Kyle and Wang, Lucy Lu and van Zuylen, Madeleine and Cohan, Arman and Hajishirzi, Hannaneh},
  booktitle={EMNLP 2020},
  year={2020}
}
```

## Troubleshooting

### PUBHEALTH Manual Download

If automatic download fails, manually download the dataset:

1. Visit: https://drive.google.com/file/d/1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj/view
2. Download the ZIP file
3. Extract to `data/pubhealth/`

Alternatively, use `gdown`:

```bash
pip install gdown
gdown 1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj -O data/pubhealth/pubhealth.zip
unzip data/pubhealth/pubhealth.zip -d data/pubhealth/
```

### Import Errors

If you get import errors, make sure to:
- Install all requirements: `pip install -r requirements.txt`
- Run scripts from the project root or adjust the Python path

### File Not Found Errors

The loaders will automatically download datasets (except PUBHEALTH). If you encounter errors:
- Check your internet connection
- Verify the data directory path is correct
- For PUBHEALTH, follow manual download instructions above

## License

Each dataset has its own license. Please refer to the original repositories for license information.
