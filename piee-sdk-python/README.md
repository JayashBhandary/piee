# PIEE SDK — Python SDK README

Unified SDK for the PIEE AI Infrastructure Platform.
Works with both local (`http://localhost:8000`) and cloud (`https://api.piee.app`) backends.

## Installation

```bash
pip install piee
```

## Usage

```python
from piee import PIEE

# Cloud (default)
client = PIEE(api_key="pk-...")

# Local
client = PIEE(base_url="http://localhost:8000", api_key="pk-...")

# Chat completion
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```
