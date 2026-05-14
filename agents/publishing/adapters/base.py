"""
Adapter base interface for the Publishing Agent.

Every platform (Buzzsprout, LinkedIn, Twitter, Instagram) is a separate
adapter implementing this interface. The agent orchestrates them; it
doesn't know which platform is which.

This is the same hub-and-spoke pattern from the Orchestrator — applied
internally inside the Publishing Agent.
"""

from typing import Protocol

from schemas.models import PublishableAssets, PlatformResult, Platform


class PublishingAdapter(Protocol):
    """Any platform adapter must implement this interface."""

    platform: Platform

    def publish(self, assets: PublishableAssets, user_id: str) -> PlatformResult:
        """
        Publish the assets to this platform on behalf of the user.

        Must:
          - Return a PlatformResult with status, URL (if success), latency
          - Never raise — wrap errors in PlatformResult.status=FAILED
          - Be idempotent if possible (same input → same output)
        """
        ...

    def is_connected(self, user_id: str) -> bool:
        """Whether the user has linked this platform.

        For mock adapters: read from MOCK_CONNECTIONS dict.
        For real adapters: check OAuth token validity in credential vault.
        """
        ...
