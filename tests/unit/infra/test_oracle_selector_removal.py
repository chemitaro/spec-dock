from pathlib import Path

from spec_dock.cli import main

_SELECTOR_TOKENS = ("--oracle", "oracle_implementation", "OracleImplementation")
_INSTALLED_SELECTOR_SURFACES = (
    "spec-dock/scripts/spec_dock_runtime/commands/authoring.py",
    "spec-dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py",
    "spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py",
    "spec-dock/scripts/authoring-pack/invoke_chatgpt_backend.py",
    ".agents/skills/spec-dock-chatgpt-authoring/SKILL.md",
    "spec-dock/docs/reference_authoring_pack_backend.md",
)


def test_init_installs_authoring_backend_without_oracle_implementation_selector(tmp_path: Path) -> None:
    target = tmp_path / "consumer"
    target.mkdir()

    assert main(["init", str(target)]) == 0

    installed = {
        relative_path: (target / relative_path).read_text(encoding="utf-8")
        for relative_path in _INSTALLED_SELECTOR_SURFACES
    }
    for relative_path, text in installed.items():
        for token in _SELECTOR_TOKENS:
            assert token not in text, f"{relative_path} retained retired selector token {token}"

    contract = installed["spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py"]
    assert 'PRIMARY_BACKEND_ENV = "SPECDOCK_CHATGPT_COMMAND"' in contract
    assert 'FALLBACK_BACKEND_ENV = "ORACLE_CHATGPT_COMMAND"' in contract

    reference = installed["spec-dock/docs/reference_authoring_pack_backend.md"]
    assert "`--backend-command`" in reference
    assert "`SPECDOCK_CHATGPT_COMMAND`" in reference
    assert "`ORACLE_CHATGPT_COMMAND`" in reference
