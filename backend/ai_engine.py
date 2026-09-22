import ollama
import time


MODEL_NAME = "qwen2.5:7b"


def ask_ai(prompt: str):
    """
    Send a prompt to the local Qwen AI model through Ollama.

    Optimized for:
    - Faster repeated requests
    - Deterministic QA results
    - Structured JSON responses
    - Local execution
    - Clear error handling
    """

    start_time = time.time()

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json",
            options={
                "temperature": 0,
            },
            keep_alive="10m"
        )

        elapsed_time = time.time() - start_time

        print(f"AI Response Time: {elapsed_time:.2f} seconds")

        return response["message"]["content"]

    except Exception as e:
        elapsed_time = time.time() - start_time

        print(f"AI Error after {elapsed_time:.2f} seconds: {e}")

        raise RuntimeError(
            f"Ollama AI request failed: {str(e)}"
        )