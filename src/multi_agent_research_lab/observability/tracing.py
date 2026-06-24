"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any
from dotenv import load_dotenv

load_dotenv(override=True)

# Try to initialize Langfuse if available
_langfuse_client = None
_langfuse_initialized = False

def get_langfuse_client():
    global _langfuse_client, _langfuse_initialized
    if not _langfuse_initialized:
        _langfuse_initialized = True
        try:
            from langfuse import Langfuse
            sk = os.getenv("LANGFUSE_SECRET_KEY", "").strip('"\'')
            pk = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip('"\'')
            host = os.getenv("LANGFUSE_HOST", os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")).strip('"\'')
            
            if sk and pk:
                _langfuse_client = Langfuse(secret_key=sk, public_key=pk, host=host)
                print(f"✅ Langfuse Client connected to {host}!")
        except ImportError:
            pass
    return _langfuse_client

@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context using Langfuse or default."""
    started = perf_counter()
    span_data: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    lf_client = get_langfuse_client()
    
    if lf_client:
        try:
            with lf_client.start_as_current_observation(name=name, metadata=attributes):
                yield span_data
        finally:
            span_data["duration_seconds"] = perf_counter() - started
            lf_client.flush()
    else:
        try:
            yield span_data
        finally:
            span_data["duration_seconds"] = perf_counter() - started
