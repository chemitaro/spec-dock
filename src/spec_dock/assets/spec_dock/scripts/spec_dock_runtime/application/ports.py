from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..infra.contracts import StoredMetaRecord


class ValidateNodeReader(Protocol):
    def load_node_records(self) -> list[StoredMetaRecord]:
        ...


@dataclass(frozen=True)
class Ports:
    node_reader: ValidateNodeReader
    repo_root: Path | None
