"""API dependencies; submodules group deps by integration (e.g. Zalo)."""

from app.core.config import settings

from app.api.deps.zalo_webhook_deps import (
    build_zalo_webhook_signature_content,
    verify_zalo_webhook_signature,
)

__all__ = [
    "build_zalo_webhook_signature_content",
    "settings",
    "verify_zalo_webhook_signature",
]
