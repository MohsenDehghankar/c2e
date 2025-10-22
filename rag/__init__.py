"""
RAG (Retrieval-Augmented Generation) Package

This package provides a flexible architecture for implementing different retrieval strategies.

Base Classes:
- BaseRAG: Abstract base class for all RAG implementations
- RAGContext: Data class for retrieved context

Implementations:
- SimpleRAG: Simple URL-based RAG with keyword search
"""

from rag.base_rag import BaseRAG, RAGContext
from rag.simple_rag import SimpleRAG

__all__ = [
    "BaseRAG",
    "RAGContext", 
    "SimpleRAG",
]
