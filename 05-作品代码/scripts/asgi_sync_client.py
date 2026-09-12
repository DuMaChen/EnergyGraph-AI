"""Small synchronous facade for httpx AsyncClient + ASGITransport.

The project uses FastAPI/Starlette 0.46 with httpx 0.28.  Starlette's
TestClient can hang during portal startup in this environment, while an
AsyncClient against ASGITransport is deterministic.  Existing synchronous
fixture scripts use this facade so their assertions remain readable without
reintroducing the hanging client.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx


class SyncASGIClient:
    def __init__(self, app: Any, base_url: str = "http://test") -> None:
        self._app = app
        self._base_url = base_url

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def execute() -> httpx.Response:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self._app), base_url=self._base_url) as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(execute())

    def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        return None

    def __enter__(self) -> "SyncASGIClient":
        return self

    def __exit__(self, *_args: Any) -> None:
        self.close()
