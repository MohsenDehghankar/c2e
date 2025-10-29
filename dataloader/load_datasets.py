"""
Dataset loaders for health-related fact-checking datasets.

This module provides functions to download and load three datasets:
1. HEALTHVER: Health claim verification dataset
2. PUBHEALTH: Public health fact-checking dataset
3. SCIFACT: Scientific fact verification dataset
"""

import os
import json
import pandas as pd
import requests
from typing import Dict, List, Optional, Tuple
import tarfile
import zipfile
from pathlib import Path


# Dataset URLs
HEALTHVER_URLS = {
    "train": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_train.csv",
    "dev": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_dev.csv",
    "test": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_test.csv",
}

PUBHEALTH_URL = (
    "https://drive.google.com/uc?id=1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj&export=download"
)

SCIFACT_URL = "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"


class DatasetLoader:
    """Base class for dataset loading with common utilities."""

    def __init__(self, data_dir: str = "./data"):
        """
        Initialize the dataset loader.

        Args:
            data_dir: Directory to store downloaded datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_file(
        self, url: str, output_path: Path, chunk_size: int = 8192
    ) -> None:
        """
        Download a file from URL to output path.

        Args:
            url: URL to download from
            output_path: Path to save the file
            chunk_size: Size of chunks to download
        """
        if output_path.exists():
            print(f"File already exists: {output_path}")
            return

        print(f"Downloading {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

        print(f"Downloaded to {output_path}")

    def extract_tar_gz(self, tar_path: Path, extract_dir: Path) -> None:
        """
        Extract a tar.gz file.

        Args:
            tar_path: Path to the tar.gz file
            extract_dir: Directory to extract to
        """
        print(f"Extracting {tar_path}...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(extract_dir)
        print(f"Extracted to {extract_dir}")


class HealthVerLoader(DatasetLoader):
    """Loader for HEALTHVER dataset."""

    def __init__(self, data_dir: str = "./data"):
        super().__init__(data_dir)
        self.healthver_dir = self.data_dir / "healthver"
        self.healthver_dir.mkdir(parents=True, exist_ok=True)

    def download(self) -> None:
        """Download all HEALTHVER dataset splits."""
        for split, url in HEALTHVER_URLS.items():
            output_path = self.healthver_dir / f"healthver_{split}.csv"
            self.download_file(url, output_path)

    def load(self, split: str = "train") -> pd.DataFrame:
        """
        Load a specific split of the HEALTHVER dataset.

        Args:
            split: Dataset split ('train', 'dev', or 'test')

        Returns:
            DataFrame containing the dataset
        """
        if split not in ["train", "dev", "test"]:
            raise ValueError(
                f"Invalid split: {split}. Must be 'train', 'dev', or 'test'"
            )

        file_path = self.healthver_dir / f"healthver_{split}.csv"

        if not file_path.exists():
            print(f"Dataset file not found. Downloading...")
            self.download()

        df = pd.read_csv(file_path)
        print(f"Loaded HEALTHVER {split} set: {len(df)} examples")
        return df

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Load all splits of the HEALTHVER dataset.

        Returns:
            Dictionary with 'train', 'dev', and 'test' DataFrames
        """
        return {
            "train": self.load("train"),
            "dev": self.load("dev"),
            "test": self.load("test"),
        }


class PubHealthLoader(DatasetLoader):
    """Loader for PUBHEALTH dataset."""

    def __init__(self, data_dir: str = "./data"):
        super().__init__(data_dir)
        self.pubhealth_dir = self.data_dir / "pubhealth"
        self.pubhealth_dir.mkdir(parents=True, exist_ok=True)

    def download(self) -> None:
        """Download PUBHEALTH dataset."""
        # Note: Google Drive downloads can be tricky with direct links
        # Users may need to download manually from:
        # https://drive.google.com/file/d/1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj/view

        print("=" * 80)
        print("PUBHEALTH Dataset Download Instructions:")
        print("=" * 80)
        print(
            "The PUBHEALTH dataset needs to be downloaded manually from Google Drive."
        )
        print("\nSteps:")
        print(
            "1. Visit: https://drive.google.com/file/d/1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj/view"
        )
        print("2. Download the file")
        print(f"3. Extract the contents to: {self.pubhealth_dir}")
        print("\nAlternatively, you can use gdown:")
        print(f"  pip install gdown")
        print(
            f"  gdown 1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj -O {self.pubhealth_dir}/pubhealth.zip"
        )
        print("=" * 80)

        # Try using gdown if available
        try:
            import gdown

            output_zip = self.pubhealth_dir / "pubhealth.zip"
            if not output_zip.exists():
                gdown.download(
                    id="1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj",
                    output=str(output_zip),
                    quiet=False,
                )

                # Extract zip
                print(f"Extracting {output_zip}...")
                with zipfile.ZipFile(output_zip, "r") as zip_ref:
                    zip_ref.extractall(self.pubhealth_dir)
                print(f"Extracted to {self.pubhealth_dir}")
        except ImportError:
            print("\nNote: Install 'gdown' for automatic download: pip install gdown")

    def load(self, split: str = "train") -> pd.DataFrame:
        """
        Load a specific split of the PUBHEALTH dataset.

        Args:
            split: Dataset split ('train', 'dev', or 'test')

        Returns:
            DataFrame containing the dataset
        """
        if split not in ["train", "dev", "test"]:
            raise ValueError(
                f"Invalid split: {split}. Must be 'train', 'dev', or 'test'"
            )

        # Try different possible file locations
        possible_paths = [
            self.pubhealth_dir / f"{split}.tsv",
            self.pubhealth_dir / "public_health_fact" / f"{split}.tsv",
            self.pubhealth_dir / "PUBHEALTH" / f"{split}.tsv",
        ]

        file_path = None
        for path in possible_paths:
            if path.exists():
                file_path = path
                break

        if file_path is None:
            print(f"Dataset file not found. Please download manually.")
            self.download()
            raise FileNotFoundError(
                f"PUBHEALTH {split}.tsv not found in {self.pubhealth_dir}"
            )

        # Load TSV file
        df = pd.read_csv(file_path, sep="\t")
        print(f"Loaded PUBHEALTH {split} set: {len(df)} examples")
        return df

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """
        Load all splits of the PUBHEALTH dataset.

        Returns:
            Dictionary with 'train', 'dev', and 'test' DataFrames
        """
        return {
            "train": self.load("train"),
            "dev": self.load("dev"),
            "test": self.load("test"),
        }


class SciFactLoader(DatasetLoader):
    """Loader for SCIFACT dataset."""

    def __init__(self, data_dir: str = "./data"):
        super().__init__(data_dir)
        self.scifact_dir = self.data_dir / "scifact"
        self.scifact_dir.mkdir(parents=True, exist_ok=True)

    def download(self) -> None:
        """Download SCIFACT dataset."""
        tar_path = self.scifact_dir / "data.tar.gz"

        if not tar_path.exists():
            self.download_file(SCIFACT_URL, tar_path)

        # Extract if not already extracted
        if not (self.scifact_dir / "data" / "corpus.jsonl").exists():
            self.extract_tar_gz(tar_path, self.scifact_dir)

    def load_corpus(self) -> List[Dict]:
        """
        Load the SCIFACT corpus (evidence documents).

        Returns:
            List of corpus documents
        """
        corpus_path = self.scifact_dir / "data" / "corpus.jsonl"

        if not corpus_path.exists():
            print("Corpus not found. Downloading...")
            self.download()

        corpus = []
        with open(corpus_path, "r") as f:
            for line in f:
                corpus.append(json.loads(line))

        print(f"Loaded SCIFACT corpus: {len(corpus)} documents")
        return corpus

    def load_claims(self, split: str = "train") -> List[Dict]:
        """
        Load claims from a specific split.

        Args:
            split: Dataset split ('train', 'dev', or 'test')

        Returns:
            List of claims
        """
        if split not in ["train", "dev", "test"]:
            raise ValueError(
                f"Invalid split: {split}. Must be 'train', 'dev', or 'test'"
            )

        claims_path = self.scifact_dir / "data" / f"claims_{split}.jsonl"

        if not claims_path.exists():
            print("Claims not found. Downloading...")
            self.download()

        claims = []
        with open(claims_path, "r") as f:
            for line in f:
                claims.append(json.loads(line))

        print(f"Loaded SCIFACT {split} claims: {len(claims)} examples")
        return claims

    def load(self, split: str = "train", include_corpus: bool = False) -> Dict:
        """
        Load SCIFACT dataset.

        Args:
            split: Dataset split ('train', 'dev', or 'test')
            include_corpus: Whether to include the full corpus

        Returns:
            Dictionary with 'claims' and optionally 'corpus'
        """
        result = {"claims": self.load_claims(split)}

        if include_corpus:
            result["corpus"] = self.load_corpus()

        return result

    def load_all(self, include_corpus: bool = True) -> Dict[str, Dict]:
        """
        Load all splits of the SCIFACT dataset.

        Args:
            include_corpus: Whether to include the corpus (shared across splits)

        Returns:
            Dictionary with 'train', 'dev', and 'test' data
        """
        corpus = self.load_corpus() if include_corpus else None

        result = {}
        for split in ["train", "dev", "test"]:
            result[split] = {"claims": self.load_claims(split)}
            if corpus is not None:
                result[split]["corpus"] = corpus

        return result


# Convenience functions
def load_healthver(split: str = "train", data_dir: str = "./data") -> pd.DataFrame:
    """
    Load HEALTHVER dataset.

    Args:
        split: Dataset split ('train', 'dev', or 'test', or 'all')
        data_dir: Directory to store/load data

    Returns:
        DataFrame or dict of DataFrames
    """
    loader = HealthVerLoader(data_dir)
    if split == "all":
        return loader.load_all()
    return loader.load(split)


def load_pubhealth(split: str = "train", data_dir: str = "./data") -> pd.DataFrame:
    """
    Load PUBHEALTH dataset.

    Args:
        split: Dataset split ('train', 'dev', or 'test', or 'all')
        data_dir: Directory to store/load data

    Returns:
        DataFrame or dict of DataFrames
    """
    loader = PubHealthLoader(data_dir)
    if split == "all":
        return loader.load_all()
    return loader.load(split)


def load_scifact(
    split: str = "train", data_dir: str = "./data", include_corpus: bool = False
) -> Dict:
    """
    Load SCIFACT dataset.

    Args:
        split: Dataset split ('train', 'dev', or 'test', or 'all')
        data_dir: Directory to store/load data
        include_corpus: Whether to include the evidence corpus

    Returns:
        Dictionary with claims and optionally corpus
    """
    loader = SciFactLoader(data_dir)
    if split == "all":
        return loader.load_all(include_corpus)
    return loader.load(split, include_corpus)


def get_dataset_stats(data_dir: str = "./data") -> Dict[str, Dict]:
    """
    Get statistics for all available datasets.

    Args:
        data_dir: Directory containing the datasets

    Returns:
        Dictionary with statistics for each dataset
    """
    stats = {}

    # HEALTHVER stats
    try:
        healthver = load_healthver("all", data_dir)
        stats["healthver"] = {
            "train": len(healthver["train"]),
            "dev": len(healthver["dev"]),
            "test": len(healthver["test"]),
            "total": sum(len(df) for df in healthver.values()),
        }
    except Exception as e:
        stats["healthver"] = {"error": str(e)}

    # PUBHEALTH stats
    try:
        pubhealth = load_pubhealth("all", data_dir)
        stats["pubhealth"] = {
            "train": len(pubhealth["train"]),
            "dev": len(pubhealth["dev"]),
            "test": len(pubhealth["test"]),
            "total": sum(len(df) for df in pubhealth.values()),
        }
    except Exception as e:
        stats["pubhealth"] = {"error": str(e)}

    # SCIFACT stats
    try:
        scifact = load_scifact("all", data_dir, include_corpus=True)
        stats["scifact"] = {
            "train_claims": len(scifact["train"]["claims"]),
            "dev_claims": len(scifact["dev"]["claims"]),
            "test_claims": len(scifact["test"]["claims"]),
            "corpus_docs": len(scifact["train"]["corpus"]),
            "total_claims": sum(len(split["claims"]) for split in scifact.values()),
        }
    except Exception as e:
        stats["scifact"] = {"error": str(e)}

    return stats


if __name__ == "__main__":
    """Example usage and testing."""

    print("=" * 80)
    print("Health Fact-Checking Datasets Loader")
    print("=" * 80)

    # Test HEALTHVER
    print("\n" + "=" * 80)
    print("1. HEALTHVER Dataset")
    print("=" * 80)
    try:
        healthver_train = load_healthver("train")
        print(f"Train set shape: {healthver_train.shape}")
        print(f"Columns: {list(healthver_train.columns)}")
        print(f"\nSample row:\n{healthver_train.iloc[0]}")
    except Exception as e:
        print(f"Error loading HEALTHVER: {e}")

    # Test PUBHEALTH
    print("\n" + "=" * 80)
    print("2. PUBHEALTH Dataset")
    print("=" * 80)
    try:
        pubhealth_train = load_pubhealth("train")
        print(f"Train set shape: {pubhealth_train.shape}")
        print(f"Columns: {list(pubhealth_train.columns)}")
        print(f"\nSample row:\n{pubhealth_train.iloc[0]}")
    except Exception as e:
        print(f"Error loading PUBHEALTH: {e}")

    # Test SCIFACT
    print("\n" + "=" * 80)
    print("3. SCIFACT Dataset")
    print("=" * 80)
    try:
        scifact_data = load_scifact("train", include_corpus=True)
        print(f"Number of claims: {len(scifact_data['claims'])}")
        print(f"Number of corpus documents: {len(scifact_data['corpus'])}")
        print(f"\nSample claim:\n{json.dumps(scifact_data['claims'][0], indent=2)}")
    except Exception as e:
        print(f"Error loading SCIFACT: {e}")

    # Show dataset statistics
    print("\n" + "=" * 80)
    print("Dataset Statistics")
    print("=" * 80)
    try:
        stats = get_dataset_stats()
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error getting stats: {e}")
