import ollama
from typing import Optional, Dict, Any


def setup_ollama_client(host: str = "localhost", port: int = 11434) -> ollama.Client:
    """
    Setup and return an Ollama client with specified host and port.

    Args:
        host: The hostname where Ollama is running (default: "localhost")
        port: The port number where Ollama is running (default: 11434)

    Returns:
        An initialized Ollama client

    Example:
        >>> client = setup_ollama_client("localhost", 11434)
    """
    base_url = f"http://{host}:{port}"
    return ollama.Client(host=base_url)


def call_ollama(
    prompt: str,
    model: str = "llama2",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    system_prompt: Optional[str] = None,
    client: Optional[ollama.Client] = None,
    host: str = "localhost",
    port: int = 11434,
) -> Dict[str, Any]:
    """
    Call Ollama models with a prompt.

    Args:
        prompt: The user prompt/question to send to the model
        model: The name of the Ollama model to use (default: "llama2")
        temperature: Controls randomness in generation (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        stream: Whether to stream the response
        system_prompt: Optional system prompt to set context
        client: Optional pre-configured Ollama client. If not provided, one will be created.
        host: Ollama server host (default: "localhost")
        port: Ollama server port (default: 11434)

    Returns:
        Dictionary containing the model's response and metadata

    Example:
        >>> client = setup_ollama_client("localhost", 11434)
        >>> response = call_ollama("What is Python?", model="llama2", client=client)
        >>> print(response['response'])
    """
    try:
        # Setup client if not provided
        if client is None:
            client = setup_ollama_client(host, port)

        # Prepare options
        options = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens

        # Call the generate API
        response = client.generate(
            model=model,
            prompt=prompt,
            system=system_prompt,
            stream=stream,
            options=options,
        )

        if stream:
            return {"stream": response, "status": "streaming"}
        else:
            return response

    except Exception as e:
        return {"error": f"Ollama error: {str(e)}", "status": "error"}
