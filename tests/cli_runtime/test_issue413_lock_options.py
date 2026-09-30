"""Start lock wait is separate from ordinary subprocess timeouts."""

from __future__ import annotations

import pytest

from spec_dock.runtime.cli.options import parse_vnext_output


def test_start_lock_defaults_to_five_seconds() -> None:
    result = parse_vnext_output(["work", "start", "iss-00413", "--base", "HEAD"], public_v2=True)
    assert result.namespace is not None
    assert result.namespace.lock_timeout == 5


@pytest.mark.parametrize(
    "arguments",
    [
        ["scope", "list", "--lock-timeout", "0"],
        ["work", "start", "iss-00413", "--lock-timeout", "301"],
        ["work", "start", "iss-00413", "--timeout", "301"],
    ],
)
def test_out_of_contract_timeouts_stop_before_context(arguments: list[str]) -> None:
    result = parse_vnext_output(arguments, public_v2=True)
    assert result.namespace is None
    assert result.exit_code == 2
