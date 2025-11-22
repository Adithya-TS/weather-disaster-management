"""
FastAPI surface for the Weather Disaster Management system.

The FastAPI app is defined in `fastapi_app.py` and exposes HTTP endpoints
that trigger the underlying Google ADK workflow.
"""

from .fastapi_app import app  # noqa: F401

