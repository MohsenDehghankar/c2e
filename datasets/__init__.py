"""
Health Fact-Checking Datasets Package

This package provides easy access to three health-related fact-checking datasets:
- HEALTHVER: Health claim verification
- PUBHEALTH: Public health fact-checking
- SCIFACT: Scientific fact verification
"""

from .load_datasets import (
    # Loaders
    DatasetLoader,
    HealthVerLoader,
    PubHealthLoader,
    SciFactLoader,
    
    # Convenience functions
    load_healthver,
    load_pubhealth,
    load_scifact,
    get_dataset_stats,
)

__version__ = '1.0.0'

__all__ = [
    # Loaders
    'DatasetLoader',
    'HealthVerLoader',
    'PubHealthLoader',
    'SciFactLoader',
    
    # Functions
    'load_healthver',
    'load_pubhealth',
    'load_scifact',
    'get_dataset_stats',
]
