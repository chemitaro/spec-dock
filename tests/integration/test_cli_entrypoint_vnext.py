"""The future supported entrypoint pins an external engine distribution."""

from pathlib import Path

import pytest

from spec_dock.runtime_loader import EnginePin, digest_distribution, verify_engine_pin


def _fixture_engine(tmp_path: Path) -> tuple[Path, Path, Path]:
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    installed = tmp_path / "installed"
    package = installed / "spec_dock"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("VERSION = 'fixed'\n", encoding="utf-8")
    executable = installed / "bin" / "spec-dock"
    executable.parent.mkdir()
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)
    return checkout, installed, executable


def test_external_engine_pin_uses_absolute_package_and_digest(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    pin = EnginePin(executable, distribution, digest_distribution(distribution))
    verified = verify_engine_pin(pin, checkout_root=checkout)
    assert verified.executable == executable
    (distribution / "spec_dock" / "__init__.py").write_text("VERSION = 'changed'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_engine_pin(pin, checkout_root=checkout)


def test_checkout_runtime_and_symlinked_engine_are_rejected(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    local_package = checkout / "spec_dock"
    local_package.mkdir()
    (local_package / "__init__.py").write_text("local\n", encoding="utf-8")
    local_executable = checkout / "spec-dock"
    local_executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    local_executable.chmod(0o755)
    with pytest.raises(ValueError, match="checkout"):
        verify_engine_pin(EnginePin(local_executable, checkout, digest_distribution(checkout)), checkout_root=checkout)
    alias = tmp_path / "engine-link"
    alias.symlink_to(executable)
    with pytest.raises(ValueError, match="symlink"):
        verify_engine_pin(EnginePin(alias, distribution, digest_distribution(distribution)), checkout_root=checkout)


def test_executable_tamper_and_relative_pin_are_rejected(tmp_path: Path) -> None:
    checkout, distribution, executable = _fixture_engine(tmp_path)
    pin = EnginePin(executable, distribution, digest_distribution(distribution))
    executable.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="digest"):
        verify_engine_pin(pin, checkout_root=checkout)
    with pytest.raises(ValueError, match="absolute"):
        verify_engine_pin(EnginePin(Path("spec-dock"), distribution, pin.distribution_digest), checkout_root=checkout)
