import json
from pathlib import Path
import sys
import tempfile


def _runtime_modules():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.infra import active_store, contracts as infra_contracts
    finally:
        sys.path.pop(0)
    return active_store, infra_contracts


class TestActiveStoreInfra:
    def _manifest(self, infra_contracts):
        return infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-00001",
                path="spec-dock/initiatives/init-00001-platform",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-00002",
                path="spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery",
            ),
            issue=infra_contracts.ActiveManifestEntry(
                id="iss-00003",
                path="spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-target",
            ),
        )

    def _make_placeholder_dirs(self, specdock_dir: Path) -> None:
        for layer in ("initiative", "epic", "issue"):
            placeholder = specdock_dir / "system" / "active-none" / layer
            placeholder.mkdir(parents=True, exist_ok=True)
            (placeholder / "README.md").write_text(f"Active {layer}: none\n", encoding="utf-8")

    def test_write_manifest_prefers_agent_active_and_prunes_legacy_work_files(self) -> None:
        active_store, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            legacy_dir = specdock_dir / ".work"
            legacy_dir.mkdir(parents=True)
            (legacy_dir / "active.json").write_text("{}\n", encoding="utf-8")
            (legacy_dir / "current.json").write_text("{}\n", encoding="utf-8")

            active_store.write_active_manifest(specdock_dir, self._manifest(infra_contracts))

            loaded = active_store.load_active_manifest(specdock_dir)
            assert loaded.source == "agent.active"
            assert loaded.manifest.issue.id == "iss-00003"
            assert not (legacy_dir / "active.json").exists()
            assert not (legacy_dir / "current.json").exists()

    def test_apply_active_pointers_uses_repo_relative_paths_and_placeholders_without_cli(self) -> None:
        active_store, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            specdock_dir = repo_root / "spec-dock"
            self._make_placeholder_dirs(specdock_dir)
            issue_dir = (
                specdock_dir
                / "initiatives"
                / "init-00001-platform"
                / "epics"
                / "epic-00002-delivery"
                / "issues"
                / "iss-00003-target"
            )
            issue_dir.mkdir(parents=True)
            (issue_dir / "requirement.md").write_text("# req\n", encoding="utf-8")
            (issue_dir.parents[1]).mkdir(parents=True, exist_ok=True)

            active_store.apply_active_pointers(
                specdock_dir,
                infra_contracts.ActiveManifest(
                    initiative=None,
                    epic=None,
                    issue=infra_contracts.ActiveManifestEntry(
                        id="iss-00003",
                        path="spec-dock/initiatives/init-00001-platform/epics/epic-00002-delivery/issues/iss-00003-target",
                    ),
                ),
                "# context\n",
            )

            active_dir = specdock_dir / "active"
            assert (active_dir / "issue").exists()
            assert "active-none/initiative" in (active_dir / "initiative").resolve().as_posix()
            assert "active-none/epic" in (active_dir / "epic").resolve().as_posix()
            assert (active_dir / "context-pack.md").read_text(encoding="utf-8") == "# context\n"

    def test_patch_agent_state_updates_cached_active_fields_without_rebuilding_indexes(self) -> None:
        active_store, infra_contracts = _runtime_modules()
        with tempfile.TemporaryDirectory() as tmp:
            specdock_dir = Path(tmp) / "spec-dock"
            agent_dir = specdock_dir / ".agent"
            agent_dir.mkdir(parents=True)
            for name in ("index-all.json", "tree-all.json", "index.json", "tree.json"):
                (agent_dir / name).write_text(
                    json.dumps({"active": None, "nodes": {"iss-00003": {"status": "done"}}}) + "\n",
                    encoding="utf-8",
                )

            active_store.patch_agent_state_active_fields(specdock_dir, self._manifest(infra_contracts))

            for name in ("index-all.json", "tree-all.json", "index.json", "tree.json"):
                payload = json.loads((agent_dir / name).read_text(encoding="utf-8"))
                assert payload["active"]["issue"]["id"] == "iss-00003"
                assert payload["nodes"]["iss-00003"]["status"] == "done"
