"""
Example script demonstrating how to load and use the three health fact-checking datasets.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets.load_datasets import (
    load_healthver,
    load_pubhealth,
    load_scifact,
    get_dataset_stats,
)
import json


def example_healthver():
    """Example: Load and explore HEALTHVER dataset."""
    print("\n" + "=" * 80)
    print("HEALTHVER Dataset Example")
    print("=" * 80)

    # Load training data
    train_df = load_healthver("train", data_dir="../data")

    print(f"\nDataset shape: {train_df.shape}")
    print(f"Columns: {list(train_df.columns)}")

    # Show first few examples
    print(f"\nFirst 3 claims:")
    for idx, row in train_df.head(3).iterrows():
        print(f"\n--- Example {idx+1} ---")
        for col in train_df.columns:
            print(f"{col}: {row[col]}")

    # Show label distribution
    if "label" in train_df.columns:
        print(f"\nLabel distribution:")
        print(train_df["label"].value_counts())


def example_pubhealth():
    """Example: Load and explore PUBHEALTH dataset."""
    print("\n" + "=" * 80)
    print("PUBHEALTH Dataset Example")
    print("=" * 80)

    try:
        # Load training data
        train_df = load_pubhealth("train", data_dir="../data")

        print(f"\nDataset shape: {train_df.shape}")
        print(f"Columns: {list(train_df.columns)}")

        # Show first example
        print(f"\nFirst example:")
        for col in train_df.columns:
            print(f"{col}: {train_df.iloc[0][col]}")

        # Show label distribution
        if "label" in train_df.columns:
            print(f"\nLabel distribution:")
            print(train_df["label"].value_counts())

    except FileNotFoundError as e:
        print(f"\nNote: {e}")
        print("Please download the PUBHEALTH dataset manually from:")
        print("https://drive.google.com/file/d/1eTtRs5cUlBP5dXsx-FTAlmXuB6JQi2qj/view")


def example_scifact():
    """Example: Load and explore SCIFACT dataset."""
    print("\n" + "=" * 80)
    print("SCIFACT Dataset Example")
    print("=" * 80)

    # Load training data with corpus
    data = load_scifact("train", data_dir="../data", include_corpus=True)

    claims = data["claims"]
    corpus = data["corpus"]

    print(f"\nNumber of claims: {len(claims)}")
    print(f"Number of corpus documents: {len(corpus)}")

    # Show first claim
    print(f"\nFirst claim:")
    print(json.dumps(claims[0], indent=2))

    # Show first corpus document
    print(f"\nFirst corpus document:")
    print(json.dumps(corpus[0], indent=2))

    # Analyze claim labels
    labels = {}
    for claim in claims:
        if "labels" in claim:
            for doc_id, label_info in claim["labels"].items():
                label = label_info.get("label", "UNKNOWN")
                labels[label] = labels.get(label, 0) + 1

    print(f"\nLabel distribution:")
    for label, count in sorted(labels.items()):
        print(f"  {label}: {count}")


def example_combined_stats():
    """Example: Get statistics for all datasets."""
    print("\n" + "=" * 80)
    print("Combined Dataset Statistics")
    print("=" * 80)

    try:
        stats = get_dataset_stats(data_dir="../data")
        print(json.dumps(stats, indent=2))
    except Exception as e:
        print(f"Error: {e}")


def example_load_all_splits():
    """Example: Load all splits of a dataset at once."""
    print("\n" + "=" * 80)
    print("Loading All Splits Example (HEALTHVER)")
    print("=" * 80)

    # Load all splits at once
    all_data = load_healthver("all", data_dir="../data")

    for split, df in all_data.items():
        print(f"\n{split.upper()} set: {len(df)} examples")
        if "label" in df.columns:
            print(f"  Labels: {df['label'].value_counts().to_dict()}")


def example_iterate_claims():
    """Example: Iterate through claims and process them."""
    print("\n" + "=" * 80)
    print("Iterating Through Claims Example")
    print("=" * 80)

    # Load SCIFACT claims
    data = load_scifact("train", data_dir="../data", include_corpus=False)
    claims = data["claims"]

    print(f"\nProcessing {len(claims)} claims...")

    # Process first 3 claims
    for i, claim in enumerate(claims[:3]):
        claim_id = claim.get("id")
        claim_text = claim.get("claim")

        print(f"\n--- Claim {i+1} (ID: {claim_id}) ---")
        print(f"Text: {claim_text}")

        # Check if evidence is available
        if "evidence" in claim:
            print(f"Evidence available: Yes")
            print(f"Number of evidence docs: {len(claim['evidence'])}")
        else:
            print(f"Evidence available: No (test set)")


if __name__ == "__main__":
    """Run all examples."""

    print("=" * 80)
    print("Health Fact-Checking Datasets - Usage Examples")
    print("=" * 80)

    # Run examples
    try:
        example_healthver()
    except Exception as e:
        print(f"Error in HEALTHVER example: {e}")

    try:
        example_pubhealth()
    except Exception as e:
        print(f"Error in PUBHEALTH example: {e}")

    try:
        example_scifact()
    except Exception as e:
        print(f"Error in SCIFACT example: {e}")

    try:
        example_combined_stats()
    except Exception as e:
        print(f"Error in combined stats: {e}")

    try:
        example_load_all_splits()
    except Exception as e:
        print(f"Error in load all splits: {e}")

    try:
        example_iterate_claims()
    except Exception as e:
        print(f"Error in iterate claims: {e}")

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)
