import os
import anthropic

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set in this environment. "
        "Set it with: setx ANTHROPIC_API_KEY \"your-key-here\" (then restart your terminal), "
        "or pass api_key=... directly to anthropic.Anthropic()."
    )

client = anthropic.Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=20,
    messages=[{"role": "user", "content": "say hello in 3 words"}],
)

print(response.content[0].text)