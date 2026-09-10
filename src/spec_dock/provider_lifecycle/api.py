"""Public provider lifecycle adapter."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeAlias

from spec_dock.provider_lifecycle.contracts import LifecycleRequest, LifecycleResult
from spec_dock.provider_lifecycle.engine import ProviderLifecycleEngine

RuntimeInstallationAdmission: TypeAlias = Callable[..., LifecycleResult]


def execute_provider_lifecycle(
    request: LifecycleRequest,
    *,
    force: bool | None = None,
    cleanup_token: str | None = None,
) -> LifecycleResult:
    """Execute one normalized request through the provider lifecycle owner."""

    return ProviderLifecycleEngine().execute(request, force=force, cleanup_token=cleanup_token)


def invalid_provider_lifecycle_request(
    request: LifecycleRequest,
    *,
    code: str = "invalid-request",
) -> LifecycleResult:
    """Build the closed result for a parser-rejected lifecycle request."""

    return ProviderLifecycleEngine.invalid_request(request, code=code)
