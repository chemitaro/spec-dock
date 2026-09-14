from __future__ import annotations

import spec_dock.provider_lifecycle as provider_lifecycle


def test_public_facade_exposes_only_the_closed_lifecycle_entrypoints() -> None:
    assert provider_lifecycle.__all__ == ["RuntimeInstallationAdmission", "execute_provider_lifecycle"]
    assert hasattr(provider_lifecycle, "RuntimeInstallationAdmission")
    assert hasattr(provider_lifecycle, "execute_provider_lifecycle")
    assert not hasattr(provider_lifecycle, "FaultInjector")
    assert not hasattr(provider_lifecycle, "ProviderLifecycleEngine")
