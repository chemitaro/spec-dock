from __future__ import annotations

import json
from pathlib import Path
import sys


def _runtime_modules():
    runtime_scripts_dir = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import context_packet_store
    finally:
        sys.path.pop(0)
    return context_packet_store


def test_context_packet_store_writes_ignored_projection_refs_with_hashes(tmp_path: Path) -> None:
    context_packet_store = _runtime_modules()
    store = context_packet_store.ContextPacketStore(tmp_path)

    result = store.write_current({
        "schema_version": "context-packet-projection-v1",
        "packets": [{"role": "dev-coder", "context_mode": "bounded_packet"}],
        "invocation_events": [],
    })

    assert result.written is True
    assert result.errors == ()
    assert [ref["path"] for ref in result.refs] == [
        "spec-dock/.agent/context-packets/current-context-packets.json",
        "spec-dock/.agent/context-packets/dev-coder-packet.json",
    ]
    assert all(ref["sha256"] for ref in result.refs)
    payload = json.loads((tmp_path / result.refs[0]["path"]).read_text(encoding="utf-8"))
    assert payload["schema_version"] == "context-packet-projection-v1"


def test_context_packet_store_rejects_symlinked_projection_path(tmp_path: Path) -> None:
    context_packet_store = _runtime_modules()
    target = tmp_path / "spec-dock/.agent/context-packets/current-context-packets.json"
    target.parent.mkdir(parents=True)
    target.symlink_to(tmp_path / "outside.json")
    store = context_packet_store.ContextPacketStore(tmp_path)

    result = store.write_current({"packets": [], "invocation_events": []})

    assert result.written is False
    assert result.refs == ()
    assert result.errors


def test_context_packet_store_replace_failure_preserves_existing_projection_set(tmp_path: Path, monkeypatch) -> None:
    context_packet_store = _runtime_modules()
    store = context_packet_store.ContextPacketStore(tmp_path)
    initial = store.write_current({
        "schema_version": "context-packet-projection-v1",
        "packets": [{"role": "dev-coder", "context_mode": "bounded_packet"}],
        "invocation_events": [],
    })
    assert initial.written is True
    existing = {ref["path"]: (tmp_path / ref["path"]).read_text(encoding="utf-8") for ref in initial.refs}
    replace_calls = 0

    def fail_second_replace(src: Path, dst: Path) -> None:
        nonlocal replace_calls
        replace_calls += 1
        if replace_calls == 2:
            raise OSError("replace failed after first packet")
        src.replace(dst)

    monkeypatch.setattr(context_packet_store, "_replace_path", fail_second_replace)

    result = store.write_current({
        "schema_version": "context-packet-projection-v1",
        "packets": [{"role": "dev-coder", "context_mode": "recent_fork"}],
        "invocation_events": [],
    })

    assert result.written is False
    assert result.refs == ()
    assert result.errors
    for rel_path, text in existing.items():
        assert (tmp_path / rel_path).read_text(encoding="utf-8") == text
    assert not list((tmp_path / "spec-dock/.agent/context-packets").glob("*.tmp"))


def test_context_packet_store_removes_stale_role_packets_on_rewrite(tmp_path: Path) -> None:
    context_packet_store = _runtime_modules()
    store = context_packet_store.ContextPacketStore(tmp_path)
    first = store.write_current({
        "schema_version": "context-packet-projection-v1",
        "packets": [
            {"role": "dev-coder", "context_mode": "recent_fork"},
            {"role": "code-reviewer", "context_mode": "clean_room"},
        ],
        "invocation_events": [],
    })
    assert first.written is True
    reviewer_packet = tmp_path / "spec-dock/.agent/context-packets/code-reviewer-packet.json"
    assert reviewer_packet.exists()

    second = store.write_current({
        "schema_version": "context-packet-projection-v1",
        "packets": [{"role": "dev-coder", "context_mode": "bounded_packet"}],
        "invocation_events": [],
    })

    assert second.written is True
    assert not reviewer_packet.exists()
