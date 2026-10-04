"""Write editable schema-three metadata inside an unpublished, held scaffold."""

from __future__ import annotations

import json
import os

from spec_dock.runtime.domain.lifecycle import decode_scope_metadata
from spec_dock.runtime.domain.writer_admission import require_scope_structure


def write_new_scope_metadata_at(directory_fd: int, payload: dict[str, object]) -> None:
    require_scope_structure(payload)
    decode_scope_metadata(payload)
    descriptor = os.open(".meta.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o666, dir_fd=directory_fd)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write((json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
