"""Tracing hooks.

This file intentionally avoids binding to one provider. Students can plug in LangSmith,
Langfuse, OpenTelemetry, or simple JSON traces.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

# Try to initialize Langfuse if available
try:
    from langfuse import Langfuse
    if os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_PUBLIC_KEY"):
        langfuse_client = Langfuse()
    else:
        langfuse_client = None
except ImportError:
    langfuse_client = None


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Minimal span context using Langfuse or default."""
    started = perf_counter()
    span_data: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    
    lf_span = None
    if langfuse_client:
        lf_span = langfuse_client.span(name=name, metadata=attributes)

    try:
        yield span_data
    finally:
        span_data["duration_seconds"] = perf_counter() - started
        if lf_span:
            lf_span.end()
            langfuse_client.flush()
