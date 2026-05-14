"""
Publishing Agent — the main class.

Public interface:
    agent = PublishingAgent()
    output: PublishingOutput = agent.publish(publishing_input)

Design principles (same as Critic):
- Stateless: each publish() call is independent
- Pluggable adapters: pass a custom adapter map to swap mocks → real
- Never raises on platform errors; always returns structured result
- Logs everything needed for MLflow tracking
"""

from datetime import datetime, timezone

from schemas.models import (
    PublishingInput,
    PublishingOutput,
    PlatformResult,
    PublishStatus,
    Platform,
)
from adapters.base import PublishingAdapter
from adapters.mock_adapters import ALL_ADAPTERS


class PublishingAgent:
    """Routes approved assets to platform adapters and aggregates results."""

    def __init__(self, adapters: dict[Platform, PublishingAdapter] | None = None):
        # Default to mock adapters. To swap in real adapters in production,
        # pass a custom mapping: PublishingAgent(adapters={Platform.LINKEDIN: RealLinkedInAdapter(), ...})
        self.adapters = adapters if adapters is not None else ALL_ADAPTERS

    def publish(self, inp: PublishingInput) -> PublishingOutput:
        """Publish to all targeted platforms; aggregate per-platform results."""
        results: list[PlatformResult] = []

        for platform in inp.target_platforms:
            adapter = self.adapters.get(platform)

            if adapter is None:
                # Should not happen given the Platform enum, but defensive
                results.append(PlatformResult(
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error_message=f"No adapter registered for {platform.value}",
                    latency_ms=0,
                ))
                continue

            # Skip platforms the user hasn't connected
            if not adapter.is_connected(inp.user.user_id):
                results.append(PlatformResult(
                    platform=platform,
                    status=PublishStatus.SKIPPED_NOT_CONNECTED,
                    error_message=(
                        f"User has not linked their {platform.value} account. "
                        f"Direct them to the account-linking flow."
                    ),
                    latency_ms=0,
                ))
                continue

            # Dispatch to the adapter. Adapter is contractually required
            # to never raise — but we wrap defensively just in case.
            try:
                result = adapter.publish(inp.assets, inp.user.user_id)
            except Exception as e:
                result = PlatformResult(
                    platform=platform,
                    status=PublishStatus.FAILED,
                    error_message=f"Adapter raised: {type(e).__name__}: {e}",
                    latency_ms=0,
                )
            results.append(result)

        # Aggregate
        succeeded = sum(1 for r in results if r.status == PublishStatus.SUCCESS)
        failed = sum(1 for r in results if r.status == PublishStatus.FAILED)
        skipped = sum(1 for r in results if r.status == PublishStatus.SKIPPED_NOT_CONNECTED)

        # Overall status: SUCCESS only if every targeted platform succeeded
        if failed == 0 and skipped == 0:
            overall = PublishStatus.SUCCESS
        else:
            overall = PublishStatus.FAILED

        return PublishingOutput(
            script_id=inp.assets.script_id,
            overall_status=overall,
            total_succeeded=succeeded,
            total_failed=failed,
            total_skipped=skipped,
            results=results,
            timestamp=datetime.now(timezone.utc),
        )
