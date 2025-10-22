"""
Example usage of the llm.py module for calling Ollama models.

This demonstrates how to use the setup_ollama_client and call_ollama functions.
"""

from helpers.llm import setup_ollama_client, call_ollama


def simple_example():
    """Simple single-query example."""
    print("=" * 60)
    print("Simple Example: Single Query")
    print("=" * 60 + "\n")

    # Setup client
    client = setup_ollama_client(host="localhost", port=11434)

    # Make a simple query
    response = call_ollama(
        prompt="What is Python programming language?",
        model="llama2",
        temperature=0.7,
        client=client,
    )

    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Question: What is Python programming language?")
        print(f"\nAnswer: {response.get('response', 'No response')}")


def system_prompt_example():
    """Example using a system prompt."""
    print("\n" + "=" * 60)
    print("Example with System Prompt")
    print("=" * 60 + "\n")

    client = setup_ollama_client(host="localhost", port=11434)

    # Use a system prompt to set the assistant's behavior
    response = call_ollama(
        prompt="Explain recursion",
        model="llama2",
        temperature=0.7,
        system_prompt="You are a helpful programming tutor. Explain concepts clearly and concisely.",
        client=client,
    )

    if "error" in response:
        print(f"Error: {response['error']}")
    else:
        print("System: You are a helpful programming tutor.")
        print(f"Question: Explain recursion")
        print(f"\nAnswer: {response.get('response', 'No response')}")


def interactive_mode():
    """Interactive question-answering mode."""
    print("\n" + "=" * 60)
    print("Interactive Mode")
    print("=" * 60)

    # Get configuration from user
    host = input("Enter Ollama host (default: localhost): ").strip() or "localhost"
    port_input = input("Enter Ollama port (default: 11434): ").strip()
    port = int(port_input) if port_input else 11434
    model = input("Enter model name (default: llama2): ").strip() or "llama2"

    # Setup the client
    print(f"\nConnecting to Ollama at {host}:{port}...")
    client = setup_ollama_client(host=host, port=port)

    # Get optional system prompt
    system_msg = input("\nEnter system prompt (press Enter to skip): ").strip()
    system_prompt = system_msg if system_msg else None

    # Interactive loop
    print("\n" + "=" * 60)
    print("Ask questions (type 'quit' or 'exit' to stop)")
    print("=" * 60 + "\n")

    while True:
        prompt = input("You: ").strip()

        if prompt.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if not prompt:
            continue

        print("\nAssistant: ", end="", flush=True)
        response = call_ollama(
            prompt=prompt,
            model=model,
            temperature=0.7,
            client=client,
            system_prompt=system_prompt,
        )

        if "error" in response:
            print(f"Error: {response['error']}")
        else:
            print(response.get("response", "No response"))

        print()


def main():
    """Main function to run examples."""
    print("\n" + "=" * 60)
    print("Ollama LLM Usage Examples")
    print("=" * 60 + "\n")

    print("Select example to run:")
    print("1. Simple single query")
    print("2. Query with system prompt")
    print("3. Interactive mode")
    print("4. Run all non-interactive examples")

    choice = input("\nEnter choice (1-4, default: 4): ").strip() or "4"

    if choice == "1":
        simple_example()
    elif choice == "2":
        system_prompt_example()
    elif choice == "3":
        interactive_mode()
    elif choice == "4":
        simple_example()
        system_prompt_example()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
