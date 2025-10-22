from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from helpers.llm import setup_ollama_client, call_ollama


@dataclass
class RAGContext:
    """Container for retrieved context information."""

    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
    source: Optional[str] = None


class BaseRAG(ABC):
    """
    Base class for Retrieval systems.

    This abstract class defines the interface that all RAG implementations must follow.
    Subclasses should implement the retrieve() method according to their specific strategy.
    """

    def __init__(
        self, ollama_client=None, host: str = "localhost", port: int = 11434, **kwargs
    ):
        """
        Initialize the RAG system.

        Args:
            ollama_client: Pre-configured Ollama client. If not provided, one will be created.
            host: Ollama host (used if ollama_client is not provided)
            port: Ollama port (used if ollama_client is not provided)
            **kwargs: Additional configuration parameters
        """
        self.config = kwargs

        # Setup Ollama client
        if ollama_client is not None:
            self.ollama_client = ollama_client
        else:
            self.ollama_client = setup_ollama_client(host, port)

        self._setup()

    @abstractmethod
    def _setup(self):
        """
        Setup method called during initialization.
        Subclasses should implement this to initialize their specific components.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RAGContext]:
        """
        Retrieve relevant contexts for the given query.

        Args:
            query: The user's query
            top_k: Number of top contexts to retrieve

        Returns:
            List of RAGContext objects containing retrieved information
        """
        pass

    def _format_contexts(self, contexts: List[RAGContext]) -> str:
        """
        Format retrieved contexts into a string for the prompt.

        Args:
            contexts: List of RAGContext objects

        Returns:
            Formatted string containing all contexts
        """
        formatted = []
        for i, ctx in enumerate(contexts, 1):
            source_info = f" (Source: {ctx.source})" if ctx.source else ""
            formatted.append(f"Context {i}{source_info}:\n{ctx.content}")

        return "\n\n".join(formatted)

    def _build_prompt(self, query: str, contexts: List[RAGContext]) -> str:
        """
        Build the augmented prompt for the LLM with retrieved contexts.

        Args:
            query: The user's query
            contexts: Retrieved contexts

        Returns:
            Augmented prompt string
        """
        contexts_str = self._format_contexts(contexts)

        prompt = f"""Based on the following contexts, please answer the question.

Contexts:
{contexts_str}

Question: {query}

Answer:"""

        return prompt

    def generate(
        self,
        query: str,
        top_k: int = 5,
        model: str = "llama2",
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate an answer by retrieving relevant contexts and querying the LLM.

        This method:
        1. Retrieves relevant contexts using the retrieve() method
        2. Augments the query with the retrieved contexts
        3. Calls the LLM to generate an answer

        Args:
            query: The user's query
            top_k: Number of contexts to retrieve
            model: The LLM model to use
            temperature: LLM temperature for generation

        Returns:
            Dictionary containing:
                - answer: The generated answer
                - contexts: List of retrieved contexts
                - query: The original query
        """
        # Retrieve relevant contexts
        contexts = self.retrieve(query, top_k)

        # Build augmented prompt
        if contexts:
            prompt = self._build_prompt(query, contexts)
        else:
            # No contexts found, ask directly
            prompt = f"Question: {query}\n\nAnswer:"

        # Generate answer using the pre-configured client
        response = call_ollama(
            prompt=prompt,
            model=model,
            temperature=temperature,
            client=self.ollama_client,
        )

        if "error" in response:
            raise Exception(f"Error generating answer: {response['error']}")

        return {
            "answer": response.get("response", "No response generated"),
            "contexts": contexts,
            "query": query,
            "num_contexts": len(contexts),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
