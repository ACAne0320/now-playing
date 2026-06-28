"""Shared media-state store.

In public (serverless) mode the "now playing" state must be shared across all
function instances, otherwise an update that lands on one instance is invisible
to the instance serving a different template request — which is why some README
cards render a track while others show "No music playing".

This module provides a small store abstraction with two backends:

* ``InMemoryStore`` — a process-local dict. Correct for local mode / a single
  long-lived server, but NOT shared across serverless instances.
* ``RedisStore``    — Upstash / Vercel KV over their HTTP REST API (stateless,
  so it works from short-lived serverless functions). Used automatically when
  the KV environment variables are present.

``create_store()`` picks the Redis backend when configured and otherwise falls
back to in-memory, so nothing breaks locally or without a KV store.
"""

import json
import os
from typing import Any, Optional

import requests


class MediaStore:
    """Abstract store for per-user media state."""

    backend = "unknown"

    def get(self, key: str) -> Optional[dict]:
        raise NotImplementedError

    def set(self, key: str, value: Optional[dict]) -> None:
        raise NotImplementedError

    def keys(self) -> list[str]:
        raise NotImplementedError


class InMemoryStore(MediaStore):
    """Process-local store. Not shared across serverless instances."""

    backend = "memory"

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Optional[dict]:
        return self._data.get(key)

    def set(self, key: str, value: Optional[dict]) -> None:
        self._data[key] = value

    def keys(self) -> list[str]:
        return list(self._data.keys())


class RedisStore(MediaStore):
    """Shared store backed by the Upstash / Vercel KV REST API.

    Commands are issued as JSON arrays (e.g. ``["SET", key, value]``) to the
    REST endpoint, which is stateless and therefore safe to call from any
    serverless instance.
    """

    backend = "redis"
    PREFIX = "nowplaying:"

    def __init__(self, url: str, token: str, timeout: float = 5.0) -> None:
        self._url = url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}
        self._timeout = timeout

    def _command(self, *args: str) -> Any:
        resp = requests.post(
            self._url,
            json=list(args),
            headers=self._headers,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("result")

    def get(self, key: str) -> Optional[dict]:
        raw = self._command("GET", self.PREFIX + key)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (TypeError, ValueError):
            return None

    def set(self, key: str, value: Optional[dict]) -> None:
        self._command("SET", self.PREFIX + key, json.dumps(value))

    def keys(self) -> list[str]:
        result = self._command("KEYS", self.PREFIX + "*") or []
        return [k[len(self.PREFIX):] for k in result if k.startswith(self.PREFIX)]


def _kv_credentials() -> tuple[Optional[str], Optional[str]]:
    """Find the KV REST URL + read-write token from the environment.

    Tries well-known names first (Vercel KV / standalone Upstash), then
    discovers by suffix because the Upstash Vercel Marketplace integration
    may inject prefixed names like ``UPSTASH_REDIS_<name>_REST_API_URL``.
    Only HTTP(S) REST endpoints are accepted (the ``redis://`` TCP URLs that
    Upstash also injects cannot be used by the REST client).
    """
    env = os.environ

    for url_key, tok_key in (
        ("KV_REST_API_URL", "KV_REST_API_TOKEN"),
        ("UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN"),
    ):
        if env.get(url_key) and env.get(tok_key):
            return env[url_key], env[tok_key]

    url: Optional[str] = None
    for key, val in env.items():
        if val and val.startswith("http") and key.upper().endswith(
            ("REST_API_URL", "REST_URL")
        ):
            url = val
            break

    tokens: list[tuple[int, str]] = []
    for key, val in env.items():
        upper = key.upper()
        if val and upper.endswith(("REST_API_TOKEN", "REST_TOKEN")):
            read_only = 1 if ("READ_ONLY" in upper or "READONLY" in upper) else 0
            tokens.append((read_only, val))
    tokens.sort(key=lambda item: item[0])  # prefer the read-write token
    token = tokens[0][1] if tokens else None

    return url, token


def create_store() -> MediaStore:
    """Return a Redis-backed store when KV env vars are present, else in-memory."""
    url, token = _kv_credentials()
    if url and token:
        try:
            return RedisStore(url, token)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[store] Redis init failed ({exc}); falling back to in-memory")
    return InMemoryStore()
