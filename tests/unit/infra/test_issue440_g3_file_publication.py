"""One-file creation through `file_publication.publish_file` never overwrites (iss-00440).

Moved from tests/integration/test_direct_json_publication.py, whose other tests covered the retired metadata JSON
replacement.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from spec_dock.runtime.infra.file_publication import publish_file

if TYPE_CHECKING:
    from pathlib import Path


def test_file_create_only_has_one_link_and_preserves_an_existing_destination(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    payload = b'{"created":true}\n'
    publish_file(path, payload, stage_name=".candidate", verify=lambda: None)
    assert path.stat().st_nlink == 1
    assert path.read_bytes() == payload
    assert not (tmp_path / ".candidate").exists()
    with pytest.raises(ValueError, match="already exists"):
        publish_file(path, b'{"replacement":true}\n', stage_name=".candidate", verify=lambda: None)
    assert path.read_bytes() == payload
    assert not (tmp_path / ".candidate").exists()
