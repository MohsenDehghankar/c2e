from typing import List
from methods.base_method import BaseMethod
from helpers.llm import setup_ollama_client, call_ollama
from helpers.pubmed import set_api_key


class SimpleRAG(BaseMethod):
    def __init__(self, config):
        """
        Config should include:
        - model: str, the LLM model to use (default: "llama2")
        - llm_host: str, the host for the LLM server (default: "localhost")
        - llm_port: int, the port for the LLM server (default: 11434)
        """
        super().__init__(config)
        self.model = config.get("model", "llama2")  # use any of llama models
        self.llm_host = config.get("llm_host", "localhost")
        self.llm_port = config.get("llm_port", 11434)

    def setup(self):
        self.llm = setup_ollama_client(self.llm_host, self.llm_port)
        set_api_key()  # Ensure PubMed API key is set

    def validate_claims(self, claims: List[str]):
        for claim in claims:
            pass

    def evaluate_method(self, claims: List[str], ground_truth: List[str]):
        # Implement evaluation logic specific to SimpleRAG
        pass
