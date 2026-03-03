# PIEE TypeScript SDK Test Project

This folder contains a simple script to test the PIEE TypeScript SDK against a local or remote API server.

## Setup

1. Make sure you have Node.js installed.
2. Ensure the SDK at `../sdk` is built (it should have a `dist` folder). If not, build it first:
   ```bash
   cd ../sdk && npm install && npm run build
   ```
3. Install dependencies in this test project:
   ```bash
   cd ../test-sdk-typescript
   npm install
   ```

## Running the Test

Run the test script to verify that the SDK can successfully communicate with the PIEE API server:

```bash
# Defaults to http://localhost:8000
npm run test
```

To test against a different environment, use environment variables:

```bash
PIEE_BASE_URL="https://api.piee.app" PIEE_API_KEY="pk-my-key" npm run test
```
