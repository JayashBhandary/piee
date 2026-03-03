# PIEE Python SDK Test Project

This folder contains a simple script to test the PIEE Python SDK against a local or remote API server.

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install the local SDK:
   ```bash
   pip install -e ../piee-sdk-python
   ```

## Running the Test

Run the test script to verify that the SDK can successfully communicate with the PIEE API server:

```bash
# Defaults to http://localhost:8000
python test_piee.py
```

To test against a different environment, use environment variables:

```bash
PIEE_BASE_URL="https://api.piee.app" PIEE_API_KEY="pk-my-key" python test_piee.py
```
