import json
import httpx
from typing import Optional, Dict, Any, Generator, Iterator
from .exceptions import PIEEAPIError
from .types import (
    PIEEConfig, ChatCompletionRequest, ChatCompletionResponse,
    ChatCompletionChunk, EmbeddingRequest, EmbeddingResponse,
    ModelListResponse, TokenResponse, WalletBalance, UsageStats
)

class HTTPClient:
    def __init__(self, config: PIEEConfig):
        base_url = config.base_url or "https://api.piee.app"
        self.base_url = base_url.rstrip("/")
        self.timeout = config.timeout or 120.0
        
        self.headers = {
            "Content-Type": "application/json",
        }
        if config.default_headers:
            self.headers.update(config.default_headers)
            
        if config.api_key:
            if config.api_key.startswith("pk-"):
                self.headers["X-API-Key"] = config.api_key
            else:
                self.headers["Authorization"] = f"Bearer {config.api_key}"
                
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )

    def _handle_error(self, response: httpx.Response) -> None:
        if not response.is_success:
            try:
                error_data = response.json()
                msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                err_type = error_data.get("error", {}).get("type", "api_error")
                code = error_data.get("error", {}).get("code")
                param = error_data.get("error", {}).get("param")
                raise PIEEAPIError(message=msg, status=response.status_code, type_=err_type, code=code, param=param)
            except ValueError:
                raise PIEEAPIError(
                    message=f"HTTP {response.status_code}: {response.text}",
                    status=response.status_code,
                    type_="api_error"
                )

    def request(self, method: str, path: str, **kwargs) -> Any:
        response = self.client.request(method, path, **kwargs)
        self._handle_error(response)
        return response.json()

    def stream(self, method: str, path: str, **kwargs) -> Iterator[ChatCompletionChunk]:
        with self.client.stream(method, path, **kwargs) as response:
            self._handle_error(response)
            for line in response.iter_lines():
                if line:
                    line = line.strip()
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk_dict = json.loads(data)
                        yield ChatCompletionChunk(**chunk_dict)
                    except json.JSONDecodeError:
                        continue

    def close(self):
        self.client.close()


class Completions:
    def __init__(self, client: HTTPClient):
        self.client = client

    def create(self, **kwargs) -> ChatCompletionResponse:
        stream = kwargs.get("stream", False)
        if stream:
            raise ValueError("Use .stream() for streaming completion")
            
        response = self.client.request("POST", "/v1/chat/completions", json={**kwargs, "stream": False})
        return ChatCompletionResponse(**response)

    def stream(self, **kwargs) -> Iterator[ChatCompletionChunk]:
        return self.client.stream("POST", "/v1/chat/completions", json={**kwargs, "stream": True})

class Chat:
    def __init__(self, client: HTTPClient):
        self.completions = Completions(client)

class Embeddings:
    def __init__(self, client: HTTPClient):
        self.client = client

    def create(self, **kwargs) -> EmbeddingResponse:
        response = self.client.request("POST", "/v1/embeddings", json=kwargs)
        return EmbeddingResponse(**response)

class Models:
    def __init__(self, client: HTTPClient):
        self.client = client

    def list(self) -> ModelListResponse:
        response = self.client.request("GET", "/v1/models")
        return ModelListResponse(**response)

class Auth:
    def __init__(self, client: HTTPClient):
        self.client = client

    def login(self, email: str, password: str) -> TokenResponse:
        response = self.client.request("POST", "/auth/login", json={"email": email, "password": password})
        return TokenResponse(**response)

class Billing:
    def __init__(self, client: HTTPClient):
        self.client = client

    def balance(self) -> WalletBalance:
        response = self.client.request("GET", "/billing/balance")
        return WalletBalance(**response)

class Usage:
    def __init__(self, client: HTTPClient):
        self.client = client

    def stats(self) -> UsageStats:
        response = self.client.request("GET", "/audit/usage")
        return UsageStats(**response)


class PIEE:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = 120.0,
        default_headers: Optional[Dict[str, str]] = None,
    ):
        config = PIEEConfig(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            default_headers=default_headers
        )
        self._http_client = HTTPClient(config)
        self.chat = Chat(self._http_client)
        self.embeddings = Embeddings(self._http_client)
        self.models = Models(self._http_client)
        self.auth = Auth(self._http_client)
        self.billing = Billing(self._http_client)
        self.usage = Usage(self._http_client)

    def close(self):
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
