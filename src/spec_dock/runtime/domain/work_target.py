"""Immutable direct selection; Scope identifiers remain GitHub-number based."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Literal

_SCOPE_ID = re.compile(
    r"^(?:init|epic|iss)-(?:local-)?(?:0{4}[1-9]|0{3}[1-9][0-9]|0{2}[1-9][0-9]{2}|0[1-9][0-9]{3}|[1-9][0-9]{4,})$"
)
_GITHUB_REF = re.compile(r"^gh:[a-z0-9][a-z0-9-]*/[a-z0-9_.-]+#[1-9][0-9]*$")


@dataclass(frozen=True)
class PhysicalIdentity:
    platform: Literal["posix"]
    device: str
    file_id: str

    def __post_init__(self) -> None:
        if self.platform != "posix" or not re.fullmatch(r"[0-9]+", self.device):
            raise ValueError("invalid physical identity")
        if not re.fullmatch(r"[0-9]+", self.file_id):
            raise ValueError("invalid physical file identity")

    @classmethod
    def from_payload(cls, payload: object) -> PhysicalIdentity:
        if not isinstance(payload, dict) or set(payload) != {"platform", "device", "file_id"}:
            raise ValueError("invalid physical identity fields")
        platform, device, file_id = payload["platform"], payload["device"], payload["file_id"]
        if platform != "posix" or not isinstance(device, str) or not isinstance(file_id, str):
            raise ValueError("invalid physical identity types")
        return cls(platform, device, file_id)


@dataclass(frozen=True)
class WorkTarget:
    schema_version: str
    scope_id: str
    github_ref: str | None
    selected_branch: str
    selected_at: str
    clone_identity: PhysicalIdentity
    worktree_identity: PhysicalIdentity

    def __post_init__(self) -> None:
        if self.schema_version != "specdock.work-target/v1" or not _SCOPE_ID.fullmatch(self.scope_id):
            raise ValueError("invalid work target schema or Scope ID")
        if self.github_ref is not None and not _GITHUB_REF.fullmatch(self.github_ref):
            raise ValueError("invalid canonical GitHub linkage")
        if not self.selected_branch or any(ord(c) < 32 for c in self.selected_branch):
            raise ValueError("invalid selected branch")
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z", self.selected_at):
            raise ValueError("selection time must be UTC RFC3339")
        datetime.fromisoformat(self.selected_at[:-1] + "+00:00")

    @classmethod
    def from_payload(cls, payload: object) -> WorkTarget:
        fields = {
            "schema_version",
            "scope_id",
            "github_ref",
            "selected_branch",
            "selected_at",
            "clone_identity",
            "worktree_identity",
        }
        if not isinstance(payload, dict) or set(payload) != fields:
            raise ValueError("invalid work target fields")
        strings: list[str] = []
        for key in ("schema_version", "scope_id", "selected_branch", "selected_at"):
            value = payload[key]
            if not isinstance(value, str):
                raise ValueError("invalid work target field type")
            strings.append(value)
        linkage = payload["github_ref"]
        if linkage is not None and not isinstance(linkage, str):
            raise ValueError("invalid work target linkage type")
        return cls(
            strings[0],
            strings[1],
            linkage,
            strings[2],
            strings[3],
            PhysicalIdentity.from_payload(payload["clone_identity"]),
            PhysicalIdentity.from_payload(payload["worktree_identity"]),
        )
