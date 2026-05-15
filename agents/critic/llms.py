"""
Concrete LLM client implementations.

We provide a Groq client (recommended for development — fast, free tier).
Add other clients (Together, OpenAI, local) by following the same pattern.

To use Groq:
    pip install groq
    export GROQ_API_KEY=your_key_here
"""

import os


class GroqLLMClient:
    """
    Groq client for Llama 3.3 70B.
    Fast inference, generous free tier, ideal for development.
    """

    model_name = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "groq package not installed. Run: pip install groq"
            )

        api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Set it as an environment variable or pass api_key=..."
            )

        self.client = Groq(api_key=api_key)
        if model:
            self.model_name = model

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        """Returns (response_text, total_tokens_used)."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,  # Low temp = consistent evaluation, not creative
            max_tokens=1500,  # Critic output is structured + bounded
            response_format={"type": "json_object"},  # Forces valid JSON
        )
        text = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        return text, tokens


class MockLLMClient:
    """
    Mock client for unit tests.
    Returns canned responses without hitting any API.
    Lets you test the agent's logic without spending tokens.
    """

    model_name = "mock-llm-v1"

    def __init__(self, canned_response: str):
        self.canned_response = canned_response
        self.call_count = 0

    def complete(self, system_prompt: str, user_prompt: str) -> tuple[str, int]:
        self.call_count += 1
        return self.canned_response, 0
