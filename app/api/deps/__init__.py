"""API dependencies; submodules group deps by integration (e.g. Zalo)."""

from app.api.deps.webhooks.zalo_webhook_deps import (
    build_zalo_webhook_signature_content,
    verify_zalo_webhook_signature,
)

__all__ = [
    "build_zalo_webhook_signature_content",
    "settings",
    "verify_zalo_webhook_signature",
]
