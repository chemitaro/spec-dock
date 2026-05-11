import ast
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from contextlib import contextmanager, redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests.cli_runtime.harness import (
    CliRuntimeHarness,
    _EXPECTED_MANAGED_SKILL_NAMES,
    _expected_spec_dock_version,
    main,
)

_ISS_00031_STALE_WHEEL_PATHS = (
    "spec_dock/assets/spec_dock/templates/adr.md",
    "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
    "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
    "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
    "spec_dock/assets/spec_dock/templates/initiative/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/epic/discussions/rules.md",
    "spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
)

_ISS_00031_EXCLUDE_PATTERNS = (
    "assets/spec_dock/templates/adr.md",
    "assets/spec_dock/templates/**/discussions/rules.md",
    "assets/spec_dock/templates/issue/discussions/_template.md",
    "assets/spec_dock/templates/initiative/epics/new-epic",
    "assets/spec_dock/templates/epic/issues/new-issue",
)


class TestInitUpdate(CliRuntimeHarness):
    _CANONICAL_RULES_PROVIDER_ASSET_MAP = {
        "spec-dock/docs/rules/initiative/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md"
        ),
        "spec-dock/docs/rules/initiative/epics.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md"
        ),
        "spec-dock/docs/rules/epic/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md"
        ),
        "spec-dock/docs/rules/epic/issues.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md"
        ),
        "spec-dock/docs/rules/issue/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"
        ),
    }
    _DOGFOODING_MIRROR_PROVIDER_ASSET_MAP = {
        "spec-dock/.gitignore": "src/spec_dock/assets/spec_dock/.gitignore",
        "spec-dock/templates/README.md": "src/spec_dock/assets/spec_dock/templates/README.md",
        "spec-dock/scripts/README.md": "src/spec_dock/assets/spec_dock/scripts/README.md",
        "spec-dock/docs/guide.md": "src/spec_dock/assets/spec_dock/docs/guide.md",
        "spec-dock/docs/phase_requirement.md": (
            "src/spec_dock/assets/spec_dock/docs/phase_requirement.md"
        ),
        "spec-dock/docs/phase_design.md": "src/spec_dock/assets/spec_dock/docs/phase_design.md",
        "spec-dock/docs/phase_plan.md": "src/spec_dock/assets/spec_dock/docs/phase_plan.md",
        "spec-dock/docs/phase_plan_initiative.md": (
            "src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md"
        ),
        "spec-dock/docs/phase_plan_epic.md": (
            "src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md"
        ),
        "spec-dock/docs/phase_plan_issue.md": (
            "src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md"
        ),
        "spec-dock/docs/workflow_initiative.md": (
            "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md"
        ),
        "spec-dock/docs/workflow_epic.md": "src/spec_dock/assets/spec_dock/docs/workflow_epic.md",
        "spec-dock/docs/workflow_issue.md": "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
        "spec-dock/docs/workflow-tree.md": "src/spec_dock/assets/spec_dock/docs/workflow-tree.md",
        "spec-dock/docs/reference_github.md": (
            "src/spec_dock/assets/spec_dock/docs/reference_github.md"
        ),
        "spec-dock/docs/rules/initiative/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md"
        ),
        "spec-dock/docs/rules/initiative/epics.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md"
        ),
        "spec-dock/docs/rules/epic/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md"
        ),
        "spec-dock/docs/rules/epic/issues.md": "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md",
        "spec-dock/docs/rules/issue/discussions.md": (
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md"
        ),
        ".agents/skills/spec-driven-tdd-workflow/SKILL.md": (
            "src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md"
        ),
        ".agents/skills/spec-dock-issue-execution/SKILL.md": (
            "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md"
        ),
        ".agents/skills/spec-dock-codex-adapter/SKILL.md": (
            "src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md"
        ),
        ".agents/skills/spec-dock-copilot-adapter/SKILL.md": (
            "src/spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md"
        ),
        ".agents/host-adapters/meta.json": "src/spec_dock/assets/install_root/.agents/host-adapters/meta.json",
        ".codex/AGENTS.md": "src/spec_dock/assets/install_root/.codex/AGENTS.md",
        ".codex/config.toml": "src/spec_dock/assets/install_root/.codex/config.toml",
        ".codex/agents/spec-manager.toml": "src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml",
        ".github/agents/orchestrator.agent.md": (
            "src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md"
        ),
        ".github/agents/spec-manager.agent.md": (
            "src/spec_dock/assets/install_root/.github/agents/spec-manager.agent.md"
        ),
    }
    _DOGFOODING_RUNTIME_MIRROR_PROVIDER_ASSET_MAP = {
        "spec-dock/scripts/spec_dock_runtime/application/contracts.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/create_node.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/doctor.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/repo_context.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/sync_state.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/application/import_node.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/cli/parser.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/cli/registry.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/commands/issue.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/commands/new.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/commands/import_cmd.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/domain/validation.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/infra/git_cli.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py"
        ),
        "spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py": (
            "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py"
        ),
    }

    _CANONICAL_RULES_EXPECTATIONS = {
        "docs/rules/initiative/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには initiative に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --initiative <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --initiative <id> --title",
            ),
            "absent": (
                "--epic <id>",
                "--issue <id>",
            ),
        },
        "docs/rules/initiative/epics.md": {
            "contains": (
                "# epics/rules.md",
                "このディレクトリには initiative 配下の epic を作成します。",
                "Epic workflow: `spec-dock/docs/workflow_epic.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new epic --initiative <id> --title",
            ),
            "absent": (
                "--no-github",
                "new issue --epic",
                "new doc adr",
            ),
        },
        "docs/rules/epic/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには epic に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --epic <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --epic <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "--issue <id>",
            ),
        },
        "docs/rules/epic/issues.md": {
            "contains": (
                "# issues/rules.md",
                "このディレクトリには epic 配下の issue を作成します。",
                "Issue workflow: `spec-dock/docs/workflow_issue.md`",
                "GitHub linkage: `spec-dock/docs/reference_github.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new issue --epic <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "new doc adr",
            ),
        },
        "docs/rules/issue/discussions.md": {
            "contains": (
                "# discussions/rules.md",
                "このディレクトリには issue に紐づく議論資料を置きます。",
                "Discussion workflow: `spec-dock/docs/workflow_adr.md`",
                "リポジトリ root から実行してください",
                "./spec-dock/scripts/spec-dock new doc adr --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc disc --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc research --issue <id> --title",
                "./spec-dock/scripts/spec-dock new doc note --issue <id> --title",
            ),
            "absent": (
                "--initiative <id>",
                "--epic <id>",
            ),
        },
    }
    _WORKFLOW_TREE_REQUIRED_FRAGMENTS = (
        "`guide.md`",
        "`reference_sync.md`",
        "`workflow_issue.md`",
        "`workflow_adr.md`",
        "`spec-dock/adrs/`",
        "generated ADR mirror",
    )
    _GUIDE_REQUIRED_FRAGMENTS = (
        "`spec-dock/adrs/`",
        "generated ADR mirror",
        "`sync` で rebuild / gitignore 対象",
    )
    _GUIDE_REFERENCE_NAME_REQUIRED_FRAGMENTS = (
        "[workflow_initiative.md](workflow_initiative.md)",
        "[workflow_epic.md](workflow_epic.md)",
        "[workflow_issue.md](workflow_issue.md)",
        "[workflow_adr.md](workflow_adr.md)",
        "[reference_github.md](reference_github.md)",
        "[reference_naming.md](reference_naming.md)",
        "[reference_deps.md](reference_deps.md)",
        "[reference_sync.md](reference_sync.md)",
    )
    _EXPECTED_HOST_ADAPTER_META = {
        "schema_version": 1,
        "owner": "spec-dock",
        "targets": {
            "codex": {
                "enabled": True,
                "entry_file": ".agents/skills/spec-dock-codex-adapter/SKILL.md",
                "native_shim": {
                    "managed": True,
                    "owner": "spec-dock",
                    "target_file": ".codex/agents/spec-manager.toml",
                    "source_of_truth_asset": "install_root/.codex/agents/spec-manager.toml",
                    "delegates_to": ".agents/skills/spec-dock-codex-adapter/SKILL.md",
                },
            },
            "copilot": {
                "enabled": True,
                "entry_file": ".agents/skills/spec-dock-copilot-adapter/SKILL.md",
                "native_shim": {
                    "managed": True,
                    "owner": "spec-dock",
                    "target_file": ".github/agents/orchestrator.agent.md",
                    "source_of_truth_asset": "install_root/.github/agents/orchestrator.agent.md",
                    "delegates_to": ".agents/skills/spec-dock-copilot-adapter/SKILL.md",
                },
            },
        },
        "managed_assets": {
            "bootstrap_only_exact_file_paths": [
                ".codex/config.toml",
            ],
            "obsolete_exact_file_paths": [
                ".codex/agents/spec-dock.toml",
                ".github/agents/spec-dock.agent.md",
                ".codex/agents/spec-dock-codex-adapter.toml",
                ".github/agents/spec-dock-copilot-adapter.agent.md",
                ".codex/agents/code_reviewer.toml",
                ".codex/agents/dev_coder.toml",
                ".codex/agents/doc_writer.toml",
                ".codex/agents/pr_monitor.toml",
                ".codex/agents/qa_reviewer.toml",
                ".codex/agents/repo_analyst.toml",
                ".codex/agents/spark_worker.toml",
                ".codex/agents/spec_reviewer.toml",
                ".codex/agents/utility_worker.toml",
                ".github/agents/code_reviewer.agent.md",
                ".github/agents/dev_coder.agent.md",
                ".github/agents/doc_writer.agent.md",
                ".github/agents/pr_monitor.agent.md",
                ".github/agents/qa_reviewer.agent.md",
                ".github/agents/repo_analyst.agent.md",
                ".github/agents/spec_reviewer.agent.md",
                ".github/agents/utility_worker.agent.md",
            ]
        },
        "generated_by": "spec-dock update",
        "updated_at": "2026-04-06T00:00:00Z",
    }
    _ISSUE_68_INSTALL_ROOT = Path("src/spec_dock/assets/install_root")
    _ISSUE_68_AUTHORITATIVE_RELATIVE_PATHS = (
        ".agents/host-adapters/meta.json",
        ".agents/skills/git-commit-conventional-ja/SKILL.md",
        ".agents/skills/git-commit-conventional-ja/agents/openai.yaml",
        ".agents/skills/git-commit-conventional-ja/references/conventional-commits-v1.0.0.md",
        ".agents/skills/github-codex-pr-review-comments/SKILL.md",
        ".agents/skills/github-codex-pr-review-comments/agents/openai.yaml",
        ".agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh",
        ".agents/skills/github-pr-creator/SKILL.md",
        ".agents/skills/github-pr-creator/agents/openai.yaml",
        ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
        ".agents/skills/spec-dock-adr-facilitation/SKILL.md",
        ".agents/skills/spec-dock-epic-planning/SKILL.md",
        ".agents/skills/spec-dock-initiative-planning/SKILL.md",
        ".agents/skills/spec-dock-issue-execution/SKILL.md",
        ".agents/skills/spec-dock-codex-adapter/SKILL.md",
        ".agents/skills/spec-dock-copilot-adapter/SKILL.md",
        ".codex/AGENTS.md",
        ".codex/config.toml",
        ".codex/agents/code-reviewer.toml",
        ".codex/agents/consultant.toml",
        ".codex/agents/deep-consultant.toml",
        ".codex/agents/default.toml",
        ".codex/agents/dev-coder.toml",
        ".codex/agents/doc-writer.toml",
        ".codex/agents/explorer.toml",
        ".codex/agents/pr-monitor.toml",
        ".codex/agents/qa-reviewer.toml",
        ".codex/agents/repo-analyst.toml",
        ".codex/agents/researcher.toml",
        ".codex/agents/spark-worker.toml",
        ".codex/agents/spec-manager.toml",
        ".codex/agents/spec-reviewer.toml",
        ".codex/agents/utility-worker.toml",
        ".codex/agents/worker.toml",
        ".github/agents/code-reviewer.agent.md",
        ".github/agents/consultant.agent.md",
        ".github/agents/dev-coder.agent.md",
        ".github/agents/doc-writer.agent.md",
        ".github/agents/orchestrator.agent.md",
        ".github/agents/pr-monitor.agent.md",
        ".github/agents/qa-reviewer.agent.md",
        ".github/agents/repo-analyst.agent.md",
        ".github/agents/researcher.agent.md",
        ".github/agents/spec-manager.agent.md",
        ".github/agents/spec-reviewer.agent.md",
        ".github/agents/utility-worker.agent.md",
        ".github/workflows/ci.yml",
    )
    _ISSUE_68_CLASSIFICATION_PREFIX_TO_RELATIVE_PATHS = {
        ".agents/skills/": (
            ".agents/skills/git-commit-conventional-ja/SKILL.md",
            ".agents/skills/git-commit-conventional-ja/agents/openai.yaml",
            ".agents/skills/git-commit-conventional-ja/references/conventional-commits-v1.0.0.md",
            ".agents/skills/github-codex-pr-review-comments/SKILL.md",
            ".agents/skills/github-codex-pr-review-comments/agents/openai.yaml",
            ".agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh",
            ".agents/skills/github-pr-creator/SKILL.md",
            ".agents/skills/github-pr-creator/agents/openai.yaml",
            ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ".agents/skills/spec-dock-adr-facilitation/SKILL.md",
            ".agents/skills/spec-dock-epic-planning/SKILL.md",
            ".agents/skills/spec-dock-initiative-planning/SKILL.md",
            ".agents/skills/spec-dock-issue-execution/SKILL.md",
            ".agents/skills/spec-dock-codex-adapter/SKILL.md",
            ".agents/skills/spec-dock-copilot-adapter/SKILL.md",
        ),
        ".agents/host-adapters/": (
            ".agents/host-adapters/meta.json",
        ),
        ".codex/agents/": (
            ".codex/agents/code-reviewer.toml",
            ".codex/agents/consultant.toml",
            ".codex/agents/deep-consultant.toml",
            ".codex/agents/default.toml",
            ".codex/agents/dev-coder.toml",
            ".codex/agents/doc-writer.toml",
            ".codex/agents/explorer.toml",
            ".codex/agents/pr-monitor.toml",
            ".codex/agents/qa-reviewer.toml",
            ".codex/agents/repo-analyst.toml",
            ".codex/agents/researcher.toml",
            ".codex/agents/spark-worker.toml",
            ".codex/agents/spec-manager.toml",
            ".codex/agents/spec-reviewer.toml",
            ".codex/agents/utility-worker.toml",
            ".codex/agents/worker.toml",
        ),
        ".github/agents/": (
            ".github/agents/code-reviewer.agent.md",
            ".github/agents/consultant.agent.md",
            ".github/agents/dev-coder.agent.md",
            ".github/agents/doc-writer.agent.md",
            ".github/agents/orchestrator.agent.md",
            ".github/agents/pr-monitor.agent.md",
            ".github/agents/qa-reviewer.agent.md",
            ".github/agents/repo-analyst.agent.md",
            ".github/agents/researcher.agent.md",
            ".github/agents/spec-manager.agent.md",
            ".github/agents/spec-reviewer.agent.md",
            ".github/agents/utility-worker.agent.md",
        ),
        ".codex/": (
            ".codex/AGENTS.md",
            ".codex/config.toml",
        ),
        ".github/workflows/": (
            ".github/workflows/ci.yml",
        ),
    }
    _ISSUE_68_RETIRED_LEGACY_ROOT = (
        Path(__file__).resolve().parents[1] / "src" / "spec_dock" / "assets" / "codex_skills"
    )
    _ISSUE_68_PROVIDER_DUPLICATE_BOUNDARY = {
        "spec-driven-tdd-workflow skill": {
            "search_globs": (
                "**/spec-driven-tdd-workflow/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ),
        },
        "spec-dock-adr-facilitation skill": {
            "search_globs": (
                "**/spec-dock-adr-facilitation/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-adr-facilitation/SKILL.md",
            ),
        },
        "spec-dock-epic-planning skill": {
            "search_globs": (
                "**/spec-dock-epic-planning/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md",
            ),
        },
        "spec-dock-initiative-planning skill": {
            "search_globs": (
                "**/spec-dock-initiative-planning/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md",
            ),
        },
        "spec-dock-issue-execution skill": {
            "search_globs": (
                "**/spec-dock-issue-execution/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md",
            ),
        },
        "spec-dock-codex-adapter skill": {
            "search_globs": (
                "**/spec-dock-codex-adapter/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md",
            ),
        },
        "spec-dock-copilot-adapter skill": {
            "search_globs": (
                "**/spec-dock-copilot-adapter/SKILL.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md",
            ),
        },
        "host adapter metadata": {
            "search_globs": (
                "**/host-adapters/meta.json",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.agents/host-adapters/meta.json",
            ),
        },
        "codex native shim": {
            "search_globs": (
                "**/spec-manager.toml",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml",
            ),
        },
        "github agent file": {
            "search_globs": (
                "**/orchestrator.agent.md",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md",
            ),
        },
        "github workflow asset": {
            "search_globs": (
                "**/.github/workflows/ci.yml",
            ),
            "allowed_provider_paths": (
                "src/spec_dock/assets/install_root/.github/workflows/ci.yml",
            ),
        },
    }
    _ISSUE_69_REPRESENTATIVE_ARTIFACT_RELATIVE_PATHS = (
        "spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md",
        "spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md",
        "spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md",
        "spec_dock/assets/install_root/.agents/host-adapters/meta.json",
        "spec_dock/assets/install_root/.codex/AGENTS.md",
        "spec_dock/assets/install_root/.codex/config.toml",
        "spec_dock/assets/install_root/.codex/agents/spec-manager.toml",
        "spec_dock/assets/install_root/.github/agents/orchestrator.agent.md",
        "spec_dock/assets/install_root/.github/agents/spec-manager.agent.md",
        "spec_dock/assets/install_root/.github/workflows/ci.yml",
    )
    _ISSUE_69_HANDOFF_SURFACE_ARTIFACT_RELATIVE_PATHS = (
        "spec_dock/assets/install_root/.agents/host-adapters/meta.json",
        "spec_dock/assets/install_root/.codex/agents/code-reviewer.toml",
        "spec_dock/assets/install_root/.codex/agents/consultant.toml",
        "spec_dock/assets/install_root/.codex/agents/deep-consultant.toml",
        "spec_dock/assets/install_root/.codex/agents/default.toml",
        "spec_dock/assets/install_root/.codex/agents/dev-coder.toml",
        "spec_dock/assets/install_root/.codex/agents/doc-writer.toml",
        "spec_dock/assets/install_root/.codex/agents/explorer.toml",
        "spec_dock/assets/install_root/.codex/agents/pr-monitor.toml",
        "spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml",
        "spec_dock/assets/install_root/.codex/agents/repo-analyst.toml",
        "spec_dock/assets/install_root/.codex/agents/researcher.toml",
        "spec_dock/assets/install_root/.codex/agents/spark-worker.toml",
        "spec_dock/assets/install_root/.codex/agents/spec-manager.toml",
        "spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml",
        "spec_dock/assets/install_root/.codex/agents/utility-worker.toml",
        "spec_dock/assets/install_root/.codex/agents/worker.toml",
        "spec_dock/assets/install_root/.github/agents/code-reviewer.agent.md",
        "spec_dock/assets/install_root/.github/agents/consultant.agent.md",
        "spec_dock/assets/install_root/.github/agents/dev-coder.agent.md",
        "spec_dock/assets/install_root/.github/agents/doc-writer.agent.md",
        "spec_dock/assets/install_root/.github/agents/orchestrator.agent.md",
        "spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md",
        "spec_dock/assets/install_root/.github/agents/qa-reviewer.agent.md",
        "spec_dock/assets/install_root/.github/agents/repo-analyst.agent.md",
        "spec_dock/assets/install_root/.github/agents/researcher.agent.md",
        "spec_dock/assets/install_root/.github/agents/spec-manager.agent.md",
        "spec_dock/assets/install_root/.github/agents/spec-reviewer.agent.md",
        "spec_dock/assets/install_root/.github/agents/utility-worker.agent.md",
    )
    _ISSUE_69_INSTALL_ROOT_PACKAGE_DATA_PATTERNS = (
        "assets/install_root/.agents/**",
        "assets/install_root/.codex/**",
        "assets/install_root/.github/**",
    )
    _ISSUE_69_WHEELHOUSE_RELATIVE = Path("tests/fixtures/wheelhouse")
    _ISSUE_69_BUILD_BACKEND_REQUIREMENTS = (
        "build==1.2.2",
        "packaging==24.2",
        "pyproject_hooks==1.2.0",
        "setuptools==75.8.0",
        "tomli==2.2.1",
        "wheel==0.45.1",
    )
    _ISSUE_69_WHEELHOUSE_FILENAMES = (
        "build-1.2.2-py3-none-any.whl",
        "packaging-24.2-py3-none-any.whl",
        "pyproject_hooks-1.2.0-py3-none-any.whl",
        "setuptools-75.8.0-py3-none-any.whl",
        "tomli-2.2.1-py3-none-any.whl",
        "wheel-0.45.1-py3-none-any.whl",
    )
    _ISSUE_69_STALE_EXCLUSION_ARTIFACT_RELATIVE_PATTERNS = (
        "spec_dock/assets/spec_dock/scripts/spec-dock-close*.sh",
        "spec_dock/assets/github/workflows/spec-dock-close.yml",
        "spec_dock/assets/spec_dock/templates/**/current/**",
        "spec_dock/assets/spec_dock/templates/**/completed/**",
        "spec_dock/assets/spec_dock/templates/adr.md",
        "spec_dock/assets/spec_dock/templates/**/discussions/rules.md",
        "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
        "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
        "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
        "spec_dock/assets/spec_dock/templates/*/**/README.md",
        "spec_dock/assets/spec_dock/templates/design.md",
        "spec_dock/assets/spec_dock/templates/plan.md",
        "spec_dock/assets/spec_dock/templates/report.md",
        "spec_dock/assets/spec_dock/templates/requirement.md",
    )
    _ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS = (
        "spec_dock/assets/spec_dock/scripts/spec-dock-close-smoke.sh",
        "spec_dock/assets/github/workflows/spec-dock-close.yml",
        "spec_dock/assets/spec_dock/templates/initiative/current/stale.md",
        "spec_dock/assets/spec_dock/templates/initiative/completed/stale.md",
        "spec_dock/assets/spec_dock/templates/adr.md",
        "spec_dock/assets/spec_dock/templates/issue/discussions/rules.md",
        "spec_dock/assets/spec_dock/templates/issue/discussions/_template.md",
        "spec_dock/assets/spec_dock/templates/initiative/epics/new-epic",
        "spec_dock/assets/spec_dock/templates/epic/issues/new-issue",
        "spec_dock/assets/spec_dock/templates/issue/legacy/README.md",
        "spec_dock/assets/spec_dock/templates/design.md",
        "spec_dock/assets/spec_dock/templates/plan.md",
        "spec_dock/assets/spec_dock/templates/report.md",
        "spec_dock/assets/spec_dock/templates/requirement.md",
    )
    _ISSUE_69_SETUP_SEED_STALE_FIXTURES_ENV = "SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES"
    _ISSUE_69_SETUP_PRE_PRUNE_SNAPSHOT_ENV = "SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT"
    _CHECKED_IN_DOGFOODING_META_JSON_PATHS = (
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/.meta.json",
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/.meta.json",
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00049-protocol-contract-and-runtime-alignment/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00050-host-adapter-scaffold-and-final-parity/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00051-host-native-shim-deployment-and-validation-closure/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00052-reject-non-canonical-git-issue-targets/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00055-close-linked-github-issues-from-specdock-command/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00056-delete-local-spec-nodes-with-safeguards-and-epic-final-closeout/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00088-issue-lifecycle-start-and-finish-commands/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/.meta.json",
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00035-sync-adr-symlink-mirror/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00037-migration-guardrails-and-validation-hardening/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00060-meta-json-dependency-schema-and-reader-alignment/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00064-update-user-facing-docs-help/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00068-install-root-tree-and-asset-classification/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00069-package-data-and-installed-artifact-parity/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00070-installer-source-discovery-and-managed-ownership/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00071-verification-dogfooding-and-update-parity/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00072-legacy-authority-retirement-and-final-spec-close/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/issues/iss-00078-installer-coexistence-contract-and-migration-flow/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00090-github-default-sync-contract/.meta.json",
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00090-github-default-sync-contract/issues/iss-00091-default-github-state-commands/.meta.json",
    )
    _CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH = {
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/.meta.json": [],
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/.meta.json": [],
        "spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00082-fail-fast-on-malformed-node-metadata/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00049-protocol-contract-and-runtime-alignment/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00050-host-adapter-scaffold-and-final-parity/.meta.json": [
            "iss-00049"
        ],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00051-host-native-shim-deployment-and-validation-closure/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00052-reject-non-canonical-git-issue-targets/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00055-close-linked-github-issues-from-specdock-command/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00056-delete-local-spec-nodes-with-safeguards-and-epic-final-closeout/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00088-issue-lifecycle-start-and-finish-commands/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/.meta.json": [],
        "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00034-github-mandatory-node-creation-contract/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00035-sync-adr-symlink-mirror/.meta.json": [
            "iss-00036"
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/.meta.json": [
            "iss-00034"
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00037-migration-guardrails-and-validation-hardening/.meta.json": [
            "iss-00034",
            "iss-00036",
            "iss-00035",
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/.meta.json": [
            "iss-00034",
            "iss-00036",
            "iss-00035",
            "iss-00037",
            "iss-00040",
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00060-meta-json-dependency-schema-and-reader-alignment/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00063-final-regression-parity-and-cutover-closure/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00064-update-user-facing-docs-help/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00068-install-root-tree-and-asset-classification/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00069-package-data-and-installed-artifact-parity/.meta.json": [
            "iss-00068"
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00070-installer-source-discovery-and-managed-ownership/.meta.json": [
            "iss-00068",
            "iss-00069",
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00071-verification-dogfooding-and-update-parity/.meta.json": [
            "iss-00069",
            "iss-00070",
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00072-legacy-authority-retirement-and-final-spec-close/.meta.json": [
            "iss-00071"
        ],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00077-legacy-hidden-workspace-coexistence-and-migration/issues/iss-00078-installer-coexistence-contract-and-migration-flow/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00090-github-default-sync-contract/.meta.json": [],
        "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00090-github-default-sync-contract/issues/iss-00091-default-github-state-commands/.meta.json": [],
    }
    _CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP = {
        "iss-00035": ["iss-00036"],
        "iss-00036": ["iss-00034"],
        "iss-00037": ["iss-00034", "iss-00035", "iss-00036"],
        "iss-00038": ["iss-00034", "iss-00035", "iss-00036", "iss-00037", "iss-00040"],
        "iss-00050": ["iss-00049"],
        "iss-00069": ["iss-00068"],
        "iss-00070": ["iss-00068", "iss-00069"],
        "iss-00071": ["iss-00069", "iss-00070"],
        "iss-00072": ["iss-00071"],
    }
    _NATIVE_SHIM_STATE_PAYLOAD_PATTERN = (
        r'(?m)"(schema_version|projection|nodes|issues|deps|source|updated_at)"\s*:'
        r"|^\s*(schema_version|projection|nodes|issues|deps|source|updated_at)\s*="
    )
    _NATIVE_SHIM_CONTEXT_INLINE_PATTERN = r"\.agent/.*\.json|context-pack\.md"
    _NATIVE_SHIM_DIRECT_PROTOCOL_PATTERN = r"active\.json|index\.json|deps-issues\.json|index-all\.json"
    _CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN = r"(?m)^\s*developer_instructions\s*="
    _CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN = r"(?m)^\s*instructions\s*="

    def _assert_canonical_rules_files_contract(self, text_map: dict[str, str]) -> None:
        for rel_suffix, expected in self._CANONICAL_RULES_EXPECTATIONS.items():
            matching_paths = [path for path in text_map if path.endswith(rel_suffix)]
            self.assertEqual(
                len(matching_paths),
                1,
                f"expected exactly one canonical rules document for {rel_suffix}: {matching_paths}",
            )
            rel_path = matching_paths[0]
            text = text_map[rel_path]
            for fragment in expected["contains"]:
                self.assertIn(
                    fragment,
                    text,
                    f"expected canonical rules fragment missing from {rel_path}: {fragment}",
                )
            for fragment in expected["absent"]:
                self.assertNotIn(
                    fragment,
                    text,
                    f"unexpected canonical rules fragment present in {rel_path}: {fragment}",
                )

    def _assert_canonical_rules_files_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[1]
        for installed_rel_path, asset_rel_path in self._CANONICAL_RULES_PROVIDER_ASSET_MAP.items():
            installed_path = installed_base / installed_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(installed_path.is_file(), f"missing canonical rules file: {installed_path}")
            self.assertTrue(asset_path.is_file(), f"missing canonical rules asset: {asset_path}")
            self.assertEqual(
                installed_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"canonical rules file diverged from provider asset: {installed_rel_path}",
            )

    def _assert_workflow_tree_docs_contract(self, workflow_tree_text: str) -> None:
        for fragment in self._WORKFLOW_TREE_REQUIRED_FRAGMENTS:
            self.assertIn(
                fragment,
                workflow_tree_text,
                f"workflow-tree contract fragment missing: {fragment}",
            )
        for legacy_token in (
            "spec-dock-guide.md",
            "sync.md",
            "workflow-issue.md",
            "workflow-adr.md",
        ):
            self.assertNotIn(
                f"`{legacy_token}`",
                workflow_tree_text,
                f"workflow-tree contains legacy link token: {legacy_token}",
            )

    def _assert_guide_docs_contract(self, guide_text: str) -> None:
        for fragment in self._GUIDE_REQUIRED_FRAGMENTS:
            self.assertIn(
                fragment,
                guide_text,
                f"guide contract fragment missing: {fragment}",
            )
        for fragment in self._GUIDE_REFERENCE_NAME_REQUIRED_FRAGMENTS:
            self.assertIn(
                fragment,
                guide_text,
                f"guide reference-name contract fragment missing: {fragment}",
            )
        for legacy_token in (
            "workflow-initiative.md",
            "workflow-epic.md",
            "workflow-issue.md",
            "workflow-adr.md",
            "reference-github.md",
            "reference-naming.md",
            "reference-deps.md",
            "reference-sync.md",
        ):
            self.assertNotIn(
                legacy_token,
                guide_text,
                f"guide contains legacy link token: {legacy_token}",
            )

    def _assert_checked_in_dogfooding_mirror_docs_match_provider_assets(self, repo_root: Path) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_MIRROR_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(mirror_path.is_file(), f"missing checked-in dogfooding mirror file: {mirror_path}")
            self.assertTrue(asset_path.is_file(), f"missing provider asset file: {asset_path}")
            self.assertEqual(
                mirror_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"checked-in dogfooding mirror file diverged from provider asset: {mirror_rel_path}",
            )

    def _assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(self, repo_root: Path) -> None:
        for mirror_rel_path, asset_rel_path in self._DOGFOODING_RUNTIME_MIRROR_PROVIDER_ASSET_MAP.items():
            mirror_path = repo_root / mirror_rel_path
            asset_path = repo_root / asset_rel_path
            self.assertTrue(mirror_path.is_file(), f"missing checked-in dogfooding runtime mirror file: {mirror_path}")
            self.assertTrue(asset_path.is_file(), f"missing provider runtime asset file: {asset_path}")
            self.assertEqual(
                mirror_path.read_text(encoding="utf-8"),
                asset_path.read_text(encoding="utf-8"),
                f"checked-in dogfooding runtime mirror file diverged from provider asset: {mirror_rel_path}",
            )

    def _assert_installed_templates_match_provider_assets(
        self,
        installed_base: Path,
        repo_root: Path | None = None,
    ) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[1]
        mirror_root = installed_base / "spec-dock" / "templates"
        asset_root = repo_root / "src/spec_dock/assets/spec_dock/templates"

        mirror_entries = sorted(path.relative_to(mirror_root).as_posix() for path in mirror_root.rglob("*"))
        asset_entries = sorted(path.relative_to(asset_root).as_posix() for path in asset_root.rglob("*"))
        self.assertEqual(
            mirror_entries,
            asset_entries,
            "installed templates tree diverged from provider assets",
        )

        for rel_path in asset_entries:
            mirror_path = mirror_root / rel_path
            asset_path = asset_root / rel_path
            self.assertEqual(
                mirror_path.is_dir(),
                asset_path.is_dir(),
                f"installed templates entry kind diverged from provider asset: {rel_path}",
            )
            self.assertEqual(
                mirror_path.is_file(),
                asset_path.is_file(),
                f"installed templates entry kind diverged from provider asset: {rel_path}",
            )
            if asset_path.is_file():
                self.assertEqual(
                    mirror_path.read_text(encoding="utf-8"),
                    asset_path.read_text(encoding="utf-8"),
                    f"installed template diverged from provider asset: {rel_path}",
                )

    def _run_command_with_host_adapter_manifest_override(
        self,
        command: str,
        target: Path,
        manifest_override: dict[str, object],
    ) -> tuple[int, str]:
        def _mutate_assets(patched_assets_root: Path) -> None:
            patched_meta = (
                patched_assets_root / "install_root" / ".agents" / "host-adapters" / "meta.json"
            )
            patched_meta.write_text(
                json.dumps(manifest_override, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

        return self._run_command_with_assets_override(
            command,
            target,
            _mutate_assets,
        )

    def _run_command_with_assets_override(
        self,
        command: str,
        target: Path,
        mutate_assets: object,
    ) -> tuple[int, str]:
        repo_root = Path(__file__).resolve().parents[1]
        source_assets_root = repo_root / "src" / "spec_dock" / "assets"

        with tempfile.TemporaryDirectory() as tmp_assets:
            patched_assets_root = Path(tmp_assets) / "assets"
            shutil.copytree(source_assets_root, patched_assets_root)
            if callable(mutate_assets):
                mutate_assets(patched_assets_root)

            @contextmanager
            def _patched_assets_dir():
                yield patched_assets_root

            err = io.StringIO()
            with patch("spec_dock.cli._assets_dir", _patched_assets_dir), redirect_stderr(err):
                code = main([command, str(target)])
        return code, err.getvalue()

    def _run_update_with_host_adapter_manifest_override(
        self,
        target: Path,
        manifest_override: dict[str, object],
    ) -> tuple[int, str]:
        return self._run_command_with_host_adapter_manifest_override(
            "update",
            target,
            manifest_override,
        )

    def _run_init_with_host_adapter_manifest_override(
        self,
        target: Path,
        manifest_override: dict[str, object],
    ) -> tuple[int, str]:
        return self._run_command_with_host_adapter_manifest_override(
            "init",
            target,
            manifest_override,
        )

    def _managed_contract_guard_paths(self) -> tuple[str, ...]:
        managed_skill_paths = tuple(
            f".agents/skills/{skill_name}/SKILL.md" for skill_name in _EXPECTED_MANAGED_SKILL_NAMES
        )
        return (
            *managed_skill_paths,
            ".agents/host-adapters/meta.json",
            ".codex/agents/spec-manager.toml",
            ".github/agents/orchestrator.agent.md",
            ".codex/agents/spec-dock-codex-adapter.toml",
            ".github/agents/spec-dock-copilot-adapter.agent.md",
            "spec-dock/docs/guide.md",
            "spec-dock/docs/workflow_issue.md",
            "spec-dock/scripts/spec-dock",
        )

    def _seed_managed_contract_guard_snapshot(self, target: Path) -> dict[str, bytes | None]:
        rel_paths = self._managed_contract_guard_paths()
        for index, rel_path in enumerate(rel_paths):
            self._write_text_force(
                target / rel_path,
                f"contract-failure-guard::{index}::{rel_path}\n",
            )
        return {
            rel_path: (target / rel_path).read_bytes() if (target / rel_path).is_file() else None
            for rel_path in rel_paths
        }

    def _assert_managed_contract_guard_unchanged(
        self,
        target: Path,
        expected_snapshot: dict[str, bytes | None],
    ) -> None:
        for rel_path, expected_bytes in expected_snapshot.items():
            path = target / rel_path
            observed_bytes = path.read_bytes() if path.is_file() else None
            self.assertEqual(
                observed_bytes,
                expected_bytes,
                f"managed file changed despite manifest contract failure: {rel_path}",
            )

    def _build_managed_skill_install_plan_from_assets_root(self, assets_root: Path):
        import spec_dock.cli as cli

        return cli._build_managed_skill_install_plan(assets_root)

    def _issue_70_missing_transition_coverage(
        self,
        *,
        previous_plan: object,
        current_plan: object,
    ) -> set[str]:
        previous_targets = {
            mapping.target_rel.as_posix()
            for mapping in previous_plan.current_file_mappings
        }
        current_targets = {
            mapping.target_rel.as_posix()
            for mapping in current_plan.current_file_mappings
        }
        current_obsolete = {
            rel_path.as_posix() for rel_path in current_plan.obsolete_exact_rel_paths
        }
        removed_targets = previous_targets.difference(current_targets)
        return removed_targets.difference(current_obsolete)

    def _issue_71_extract_markdown_section_by_heading_prefix(
        self,
        *,
        markdown_text: str,
        heading_prefix: str,
        source_label: str,
    ) -> str:
        lines = markdown_text.splitlines()
        start_index = None
        heading_marker = f"## {heading_prefix}"
        for index, line in enumerate(lines):
            if line.startswith(heading_marker):
                start_index = index
                break
        self.assertIsNotNone(
            start_index,
            f"issue-71 expected heading prefix missing in {source_label}: {heading_prefix}",
        )

        assert start_index is not None
        end_index = len(lines)
        for index in range(start_index + 1, len(lines)):
            if lines[index].startswith("## "):
                end_index = index
                break
        return "\n".join(lines[start_index:end_index]) + "\n"

    def _assert_spec_manager_contract(
        self,
        *,
        text: str,
        delegation_expected: str,
        shim_label: str,
    ) -> None:
        self.assertIn(
            delegation_expected,
            text,
            f"spec-manager missing delegation reference ({shim_label}): {delegation_expected}",
        )
        for fragment in (
            "command operator",
            "./spec-dock/scripts/spec-dock active {set,show,clear}",
            "./spec-dock/scripts/spec-dock validate",
            "requirement/design/plan/report",
            "manual",
            "Read order",
        ):
            self.assertIn(
                fragment,
                text,
                f"spec-manager missing command-operator fragment ({shim_label}): {fragment}",
            )
        self.assertRegex(
            text,
            r"(?i)(must not manually edit|manual file edit|manual file editing)",
            f"spec-manager missing manual-edit prohibition ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_STATE_PAYLOAD_PATTERN,
            f"spec-manager includes structured state payload keys ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_CONTEXT_INLINE_PATTERN,
            f"spec-manager includes .agent/*.json or context-pack inline reference ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_DIRECT_PROTOCOL_PATTERN,
            f"spec-manager includes direct protocol read reference ({shim_label})",
        )

    def _assert_codex_native_shim_loader_contract(self, *, text: str, shim_label: str) -> None:
        self.assertRegex(
            text,
            self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN,
            f"codex native shim missing developer_instructions key ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN,
            f"codex native shim still uses legacy instructions key ({shim_label})",
        )
        self.assertIn('model = "gpt-5.4-mini"', text, f"codex spec-manager missing model ({shim_label})")
        self.assertIn(
            'model_reasoning_effort = "high"',
            text,
            f"codex spec-manager missing reasoning effort ({shim_label})",
        )
        self.assertIn('approval_policy = "never"', text, f"codex spec-manager missing approval policy ({shim_label})")
        self.assertIn('sandbox_mode = "workspace-write"', text, f"codex spec-manager missing sandbox mode ({shim_label})")
        self.assertIn("notify = []", text, f"codex spec-manager missing notify disable ({shim_label})")
        self.assertIn("[features]", text, f"codex spec-manager missing features table ({shim_label})")
        self.assertIn("shell_tool = true", text, f"codex spec-manager missing shell tool enable ({shim_label})")

    def _assert_copilot_spec_manager_contract(self, *, text: str, shim_label: str) -> None:
        self.assertIn("name: spec-manager", text, f"copilot spec-manager name missing ({shim_label})")
        self.assertIn("model: gpt-5.4-mini", text, f"copilot spec-manager model missing ({shim_label})")
        self.assertIn("tools: ['read', 'search', 'execute', 'todo']", text, f"copilot spec-manager tools mismatch ({shim_label})")
        self.assertIn("user-invocable: false", text, f"copilot spec-manager must be subagent-only ({shim_label})")
        self.assertNotIn("mcp-servers:", text, f"copilot spec-manager must not add mcp-servers ({shim_label})")
        self.assertNotIn("'edit'", text, f"copilot spec-manager must not allow edit tool ({shim_label})")
        self.assertNotIn("'agent'", text, f"copilot spec-manager must not allow agent tool ({shim_label})")
        self.assertNotIn("'web'", text, f"copilot spec-manager must not allow web tool ({shim_label})")
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_STATE_PAYLOAD_PATTERN,
            f"copilot spec-manager includes structured state payload keys ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_CONTEXT_INLINE_PATTERN,
            f"copilot spec-manager includes .agent/*.json or context-pack inline reference ({shim_label})",
        )

    def _assert_copilot_orchestrator_contract(self, *, text: str, shim_label: str) -> None:
        self.assertIn("name: orchestrator", text, f"copilot orchestrator name missing ({shim_label})")
        self.assertIn("user-invocable: true", text, f"copilot orchestrator must be user-invocable ({shim_label})")
        self.assertIn(
            "delegate bounded `./spec-dock/scripts/spec-dock ...` command operations to `spec-manager` by default",
            text,
            f"copilot orchestrator missing spec-manager routing guidance ({shim_label})",
        )
        self.assertIn(
            "Keep requirement/design/plan/report authoring, context synthesis, and user-facing judgment in the main orchestrator.",
            text,
            f"copilot orchestrator missing docs-owner boundary ({shim_label})",
        )
        self.assertNotIn(
            "disable-model-invocation: true",
            text,
            f"copilot orchestrator must keep model invocation enabled ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_STATE_PAYLOAD_PATTERN,
            f"copilot orchestrator includes structured state payload keys ({shim_label})",
        )
        self.assertNotRegex(
            text,
            self._NATIVE_SHIM_CONTEXT_INLINE_PATTERN,
            f"copilot orchestrator includes .agent/*.json or context-pack inline reference ({shim_label})",
        )

    def _assert_codex_bootstrap_routing_contract(self, *, text: str, shim_label: str) -> None:
        self.assertIn("Treat `spec-manager` as the default specialist for SpecDock operations.", text)
        self.assertIn(
            "Use `spec-manager` by default for SpecDock command workflows instead of operating the tool ad hoc.",
            text,
            f"codex bootstrap missing command routing guidance ({shim_label})",
        )
        self.assertIn(
            "Keep requirement/design/plan/report authoring with the main orchestrator.",
            text,
            f"codex bootstrap missing docs-owner boundary ({shim_label})",
        )
        self.assertIn(
            "delegate only the command portion to `spec-manager`",
            text,
            f"codex bootstrap missing mixed-task delegation guidance ({shim_label})",
        )

    def _assert_codex_main_config_routing_contract(self, *, text: str, shim_label: str) -> None:
        self.assertIn(
            "SpecDock のコマンド操作は原則として `spec-manager` へ委任する。",
            text,
            f"codex main config missing spec-manager routing guidance ({shim_label})",
        )

    def _issue_69_run_subprocess(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        result = subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            "issue-69 command failed:\n"
            f"command: {' '.join(args)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}",
        )

    def _issue_69_run_subprocess_capture(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        result = subprocess.run(
            args,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            "issue-69 command failed:\n"
            f"command: {' '.join(args)}\n"
            f"cwd: {cwd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}",
        )
        return result

    def _issue_69_resolve_wheelhouse(self, repo_root: Path) -> Path:
        wheelhouse = repo_root / self._ISSUE_69_WHEELHOUSE_RELATIVE
        self.assertTrue(
            wheelhouse.is_dir(),
            f"issue-69 local wheelhouse is missing: {wheelhouse}",
        )
        missing_wheels = [
            wheel_name
            for wheel_name in self._ISSUE_69_WHEELHOUSE_FILENAMES
            if not (wheelhouse / wheel_name).is_file()
        ]
        self.assertEqual(
            missing_wheels,
            [],
            f"issue-69 local wheelhouse is missing pinned backend wheels: {missing_wheels}",
        )
        return wheelhouse

    def _issue_69_venv_python(self, venv_dir: Path) -> Path:
        if os.name == "nt":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"

    def _issue_69_venv_spec_dock(self, venv_python: Path) -> Path:
        if os.name == "nt":
            spec_dock_exe = venv_python.parent / "spec-dock.exe"
            if spec_dock_exe.is_file():
                return spec_dock_exe
            spec_dock_cmd = venv_python.parent / "spec-dock.cmd"
            if spec_dock_cmd.is_file():
                return spec_dock_cmd
            return spec_dock_cmd
        return venv_python.parent / "spec-dock"

    def _issue_69_env_root(self, venv_python: Path) -> Path:
        return venv_python.parent.parent

    def _issue_69_site_packages_dir(self, env_root: Path) -> Path:
        if os.name == "nt":
            return env_root / "Lib" / "site-packages"
        return env_root / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"

    def _issue_69_runtime_env_without_checkout_fallback(self) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        return env

    def _issue_69_install_target_packages(
        self,
        *,
        target_dir: Path,
        requirements: list[str],
        wheelhouse: Path | None = None,
    ) -> None:
        target_dir.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--target",
            str(target_dir),
        ]
        if wheelhouse is not None:
            command.extend(
                [
                    "--no-index",
                    "--find-links",
                    str(wheelhouse),
                ]
            )
        command.extend(requirements)
        self._issue_69_run_subprocess(command)

    def _issue_69_create_fallback_runtime_env(self, env_root: Path) -> Path:
        self.assertNotEqual(os.name, "nt", "issue-69 fallback runtime env is only implemented for POSIX")
        bin_dir = env_root / "bin"
        site_packages_dir = self._issue_69_site_packages_dir(env_root)
        bin_dir.mkdir(parents=True, exist_ok=True)
        site_packages_dir.mkdir(parents=True, exist_ok=True)

        python_wrapper = self._issue_69_venv_python(env_root)
        python_wrapper.write_text(
            "#!/bin/sh\n"
            f"PYTHONPATH={shlex.quote(str(site_packages_dir))}${{PYTHONPATH:+:${{PYTHONPATH}}}} "
            f"exec {shlex.quote(sys.executable)} \"$@\"\n",
            encoding="utf-8",
        )
        python_wrapper.chmod(0o755)

        spec_dock_wrapper = self._issue_69_venv_spec_dock(python_wrapper)
        spec_dock_wrapper.write_text(
            "#!/bin/sh\n"
            f"exec {shlex.quote(str(python_wrapper))} -m spec_dock.cli \"$@\"\n",
            encoding="utf-8",
        )
        spec_dock_wrapper.chmod(0o755)
        return python_wrapper

    def _issue_69_ensure_spec_dock_wrapper(self, venv_python: Path) -> Path:
        spec_dock_wrapper = self._issue_69_venv_spec_dock(venv_python)
        if spec_dock_wrapper.is_file():
            return spec_dock_wrapper
        if os.name == "nt":
            spec_dock_wrapper.write_text(
                "@echo off\r\n"
                f"\"{venv_python}\" -m spec_dock.cli %*\r\n",
                encoding="utf-8",
            )
        else:
            spec_dock_wrapper.write_text(
                "#!/bin/sh\n"
                f"exec {shlex.quote(str(venv_python))} -m spec_dock.cli \"$@\"\n",
                encoding="utf-8",
            )
            spec_dock_wrapper.chmod(0o755)
        return spec_dock_wrapper

    def _issue_69_build_artifacts_with_local_wheelhouse(
        self,
        *,
        repo_root: Path,
        build_context: Path,
        wheel_dir: Path,
        sdist_dir: Path,
        build_env: dict[str, str] | None = None,
    ) -> tuple[Path, Path, Path]:
        wheelhouse = self._issue_69_resolve_wheelhouse(repo_root)
        venv_dir = build_context.parent / "build-venv"
        fallback_env_dir = build_context.parent / "build-wrapper-env"
        dist_dir = build_context.parent / "dist"
        venv_result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        if venv_result.returncode == 0:
            venv_python = self._issue_69_venv_python(venv_dir)
            self.assertTrue(
                venv_python.is_file(),
                f"issue-69 expected venv python executable at: {venv_python}",
            )
        else:
            venv_python = self._issue_69_create_fallback_runtime_env(fallback_env_dir)

        self._issue_69_install_target_packages(
            target_dir=self._issue_69_site_packages_dir(self._issue_69_env_root(venv_python)),
            requirements=list(self._ISSUE_69_BUILD_BACKEND_REQUIREMENTS),
            wheelhouse=wheelhouse,
        )

        self._issue_69_run_subprocess(
            [
                str(venv_python),
                "-m",
                "build",
                "--wheel",
                "--sdist",
                "--no-isolation",
                "--outdir",
                str(dist_dir),
            ],
            cwd=build_context,
            env=build_env,
        )

        wheel_paths = sorted(dist_dir.glob("*.whl"))
        sdist_paths = sorted(dist_dir.glob("*.tar.gz"))
        self.assertEqual(len(wheel_paths), 1, f"issue-69 expected one wheel artifact, got: {wheel_paths}")
        self.assertEqual(len(sdist_paths), 1, f"issue-69 expected one sdist artifact, got: {sdist_paths}")

        wheel_dir.mkdir(parents=True, exist_ok=True)
        sdist_dir.mkdir(parents=True, exist_ok=True)
        wheel_path = wheel_dir / wheel_paths[0].name
        sdist_path = sdist_dir / sdist_paths[0].name
        shutil.copy2(wheel_paths[0], wheel_path)
        shutil.copy2(sdist_paths[0], sdist_path)
        return wheel_path, sdist_path, venv_python

    def _issue_69_prepare_isolated_installed_wheel_runtime(
        self,
        *,
        repo_root: Path,
        temp_root: Path,
    ) -> Path:
        build_context = temp_root / "build-context"
        wheel_dir = temp_root / "wheelhouse"
        sdist_dir = temp_root / "sdist"
        self._issue_69_prepare_build_context(repo_root, build_context)
        wheel_path, _, venv_python = self._issue_69_build_artifacts_with_local_wheelhouse(
            repo_root=repo_root,
            build_context=build_context,
            wheel_dir=wheel_dir,
            sdist_dir=sdist_dir,
        )
        self._issue_69_install_target_packages(
            target_dir=self._issue_69_site_packages_dir(self._issue_69_env_root(venv_python)),
            requirements=[str(wheel_path)],
        )
        self._issue_69_ensure_spec_dock_wrapper(venv_python)
        return venv_python

    def _issue_69_path_is_within(self, path: Path, root: Path) -> bool:
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return False
        return True

    def _issue_69_collect_isolated_installed_runtime_snapshot(
        self,
        *,
        venv_python: Path,
        repo_root: Path,
        cwd: Path,
    ) -> dict[str, object]:
        repo_root_literal = json.dumps(str(repo_root.resolve()))
        script = (
            "import json\n"
            "import sys\n"
            "from pathlib import Path\n"
            "import spec_dock\n"
            "import spec_dock.cli as cli\n"
            f"repo_root = Path({repo_root_literal})\n"
            "def _is_under_repo(path_text: str) -> bool:\n"
            "    if not path_text:\n"
            "        return False\n"
            "    try:\n"
            "        Path(path_text).resolve().relative_to(repo_root)\n"
            "        return True\n"
            "    except Exception:\n"
            "        return False\n"
            "with cli._assets_dir() as assets_dir:\n"
            "    resolved_assets_dir = Path(assets_dir).resolve()\n"
            "    install_root = resolved_assets_dir / 'install_root'\n"
            "    inventory = sorted(\n"
            "        f\"spec_dock/assets/{candidate.relative_to(resolved_assets_dir).as_posix()}\"\n"
            "        for candidate in install_root.rglob('*')\n"
            "        if candidate.is_file()\n"
            "    )\n"
            "payload = {\n"
            "    'spec_dock_file': str(Path(spec_dock.__file__).resolve()),\n"
            "    'assets_dir': str(resolved_assets_dir),\n"
            "    'sys_path_has_repo_root': any(_is_under_repo(path_text) for path_text in sys.path if path_text),\n"
            "    'inventory': inventory,\n"
            "}\n"
            "print(json.dumps(payload))\n"
        )
        result = self._issue_69_run_subprocess_capture(
            [str(venv_python), "-c", script],
            cwd=cwd,
            env=self._issue_69_runtime_env_without_checkout_fallback(),
        )
        output_lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(output_lines, "issue-69 runtime snapshot command produced no JSON output")
        payload = json.loads(output_lines[-1])
        self.assertIsInstance(payload, dict, "issue-69 runtime snapshot must be a JSON object")
        return payload

    def _issue_70_collect_isolated_installed_plan_snapshot(
        self,
        *,
        venv_python: Path,
        cwd: Path,
    ) -> dict[str, object]:
        script = (
            "import json\n"
            "from pathlib import Path\n"
            "import spec_dock.cli as cli\n"
            "with cli._assets_dir() as assets_dir:\n"
            "    resolved_assets_dir = Path(assets_dir).resolve()\n"
            "    plan = cli._build_managed_skill_install_plan(resolved_assets_dir)\n"
            "payload = {\n"
            "    'assets_dir': str(resolved_assets_dir),\n"
            "    'current_targets': sorted(mapping.target_rel.as_posix() for mapping in plan.current_file_mappings),\n"
            "    'current_sources': sorted(mapping.source_asset_rel.as_posix() for mapping in plan.current_file_mappings),\n"
            "    'obsolete_targets': sorted(path.as_posix() for path in plan.obsolete_exact_rel_paths),\n"
            "}\n"
            "print(json.dumps(payload))\n"
        )
        result = self._issue_69_run_subprocess_capture(
            [str(venv_python), "-c", script],
            cwd=cwd,
            env=self._issue_69_runtime_env_without_checkout_fallback(),
        )
        output_lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertTrue(output_lines, "issue-70 plan snapshot command produced no JSON output")
        payload = json.loads(output_lines[-1])
        self.assertIsInstance(payload, dict, "issue-70 plan snapshot must be a JSON object")
        return payload

    def _issue_69_assert_runtime_snapshot_uses_installed_package(
        self,
        *,
        snapshot: dict[str, object],
        repo_root: Path,
    ) -> None:
        spec_dock_file = Path(str(snapshot.get("spec_dock_file", ""))).resolve()
        assets_dir = Path(str(snapshot.get("assets_dir", ""))).resolve()
        self.assertIn(
            "site-packages",
            spec_dock_file.as_posix(),
            f"issue-69 expected installed package module path, got: {spec_dock_file}",
        )
        self.assertIn(
            "site-packages",
            assets_dir.as_posix(),
            f"issue-69 expected installed package assets path, got: {assets_dir}",
        )
        self.assertFalse(
            self._issue_69_path_is_within(spec_dock_file, repo_root),
            f"issue-69 runtime imported spec_dock from checkout path: {spec_dock_file}",
        )
        self.assertFalse(
            self._issue_69_path_is_within(assets_dir, repo_root),
            f"issue-69 runtime loaded assets from checkout path: {assets_dir}",
        )
        self.assertFalse(
            bool(snapshot.get("sys_path_has_repo_root")),
            "issue-69 runtime sys.path unexpectedly includes repository checkout path",
        )

    def _issue_69_seed_stale_fixtures_in_sdist_source_context(self, build_context: Path) -> set[str]:
        source_root = build_context / "src"
        present_seeded_fixtures: set[str] = set()
        for fixture_artifact_path in self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS:
            fixture_source_path = source_root / fixture_artifact_path
            fixture_source_path.parent.mkdir(parents=True, exist_ok=True)
            fixture_source_path.write_text("issue-69 stale fixture in source context\n", encoding="utf-8")
            if fixture_source_path.is_file():
                present_seeded_fixtures.add(fixture_artifact_path)
        return present_seeded_fixtures

    def _issue_69_collect_wheel_file_inventory(self, wheel_path: Path) -> set[str]:
        with zipfile.ZipFile(wheel_path) as wheel_zip:
            return {member for member in wheel_zip.namelist() if not member.endswith("/")}

    def _issue_69_collect_sdist_source_file_inventory(self, sdist_path: Path) -> set[str]:
        inventory: set[str] = set()
        with tarfile.open(sdist_path, "r:gz") as sdist_tar:
            for member in sdist_tar.getmembers():
                if not member.isfile():
                    continue
                _, sep, relative_member = member.name.partition("/")
                if not sep or not relative_member.startswith("src/"):
                    continue
                inventory.add(relative_member.removeprefix("src/"))
        return inventory

    def _issue_69_extract_pyproject_stale_exclusion_patterns(self, pyproject_text: str) -> tuple[str, ...]:
        section_header = "[tool.setuptools.exclude-package-data]"
        self.assertIn(section_header, pyproject_text, "missing setuptools exclude-package-data section")
        exclude_section = pyproject_text.split(section_header, 1)[1]
        list_header = "spec_dock = ["
        self.assertIn(list_header, exclude_section, "missing spec_dock exclude-package-data list")
        list_block = exclude_section.split(list_header, 1)[1].split("]", 1)[0]
        patterns: list[str] = []
        for line in list_block.splitlines():
            if '"' not in line:
                continue
            _, _, remainder = line.partition('"')
            pattern, _, _ = remainder.partition('"')
            if pattern:
                patterns.append(pattern)
        return tuple(patterns)

    def _issue_69_extract_setup_stale_exclusion_patterns(self, setup_text: str) -> tuple[str, ...]:
        parsed_module = ast.parse(setup_text, filename="setup.py")
        for statement in parsed_module.body:
            if not isinstance(statement, ast.Assign):
                continue
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id == "_STALE_BUILD_OUTPUT_PATTERNS":
                    extracted = ast.literal_eval(statement.value)
                    self.assertIsInstance(extracted, tuple)
                    return tuple(str(item) for item in extracted)
        self.fail("setup.py is missing _STALE_BUILD_OUTPUT_PATTERNS")

    def _issue_69_prepare_build_context(self, repo_root: Path, build_context: Path) -> None:
        build_context.mkdir(parents=True, exist_ok=True)
        for filename in ("pyproject.toml", "README.md", "setup.py"):
            shutil.copy2(repo_root / filename, build_context / filename)
        shutil.copytree(
            repo_root / "src",
            build_context / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    def _issue_69_collect_source_install_root_inventory(self, repo_root: Path) -> set[str]:
        source_root = repo_root / "src"
        install_root = source_root / "spec_dock" / "assets" / "install_root"
        return {
            candidate.relative_to(source_root).as_posix()
            for candidate in install_root.rglob("*")
            if candidate.is_file()
        }

    def _issue_69_collect_wheel_install_root_inventory(self, wheel_path: Path) -> set[str]:
        with zipfile.ZipFile(wheel_path) as wheel_zip:
            return {
                member
                for member in wheel_zip.namelist()
                if member.startswith("spec_dock/assets/install_root/") and not member.endswith("/")
            }

    def _issue_69_collect_sdist_install_root_inventory(self, sdist_path: Path) -> set[str]:
        sdist_inventory: set[str] = set()
        with tarfile.open(sdist_path, "r:gz") as sdist_tar:
            for member in sdist_tar.getmembers():
                if not member.isfile():
                    continue
                _, sep, relative_member = member.name.partition("/")
                if not sep:
                    continue
                if not relative_member.startswith("src/"):
                    continue
                artifact_relative = relative_member.removeprefix("src/")
                if artifact_relative.startswith("spec_dock/assets/install_root/"):
                    sdist_inventory.add(artifact_relative)
        return sdist_inventory

    def _issue_69_collect_installed_install_root_inventory(self, installed_root: Path) -> set[str]:
        package_root = installed_root / "spec_dock"
        install_root = package_root / "assets" / "install_root"
        self.assertTrue(
            install_root.is_dir(),
            f"issue-69 installed package is missing install_root assets: {install_root}",
        )
        return {
            f"spec_dock/{candidate.relative_to(package_root).as_posix()}"
            for candidate in install_root.rglob("*")
            if candidate.is_file()
        }

    def _issue_69_collect_install_root_artifact_surfaces(self) -> dict[str, set[str]]:
        repo_root = Path(__file__).resolve().parents[1]
        source_inventory = self._issue_69_collect_source_install_root_inventory(repo_root)

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            installed_dir = temp_root / "installed-package"
            wheelhouse = self._issue_69_resolve_wheelhouse(repo_root)

            self._issue_69_prepare_build_context(repo_root, build_context)
            installed_dir.mkdir(parents=True, exist_ok=True)

            wheel_path, sdist_path, venv_python = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )
            wheel_name_part, wheel_version_part, _ = wheel_path.name.split("-", 2)
            wheel_requirement = f"{wheel_name_part.replace('_', '-')}=={wheel_version_part}"

            self._issue_69_run_subprocess(
                [
                    str(venv_python),
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--no-cache-dir",
                    "--no-deps",
                    "--find-links",
                    str(wheel_dir),
                    "--find-links",
                    str(wheelhouse),
                    "--target",
                    str(installed_dir),
                    wheel_requirement,
                ]
            )

            wheel_inventory = self._issue_69_collect_wheel_install_root_inventory(wheel_path)
            sdist_inventory = self._issue_69_collect_sdist_install_root_inventory(sdist_path)
            installed_inventory = self._issue_69_collect_installed_install_root_inventory(installed_dir)

        return {
            "source": source_inventory,
            "wheel": wheel_inventory,
            "sdist": sdist_inventory,
            "installed": installed_inventory,
        }

    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            exit_code = main(["init", str(target)])
            self.assertEqual(exit_code, 0)

            self._assert_version_file(target)

            # Repo-root shortcut (best-effort; only assert when symlinks are supported).
            if self._can_create_symlink(target):
                self.assertTrue((target / "spec").is_symlink(), "repo-root shortcut missing: spec")

            self.assertTrue((target / "spec-dock" / "docs").is_dir())
            self.assertTrue((target / "spec-dock" / "templates").is_dir())
            self.assertTrue((target / "spec-dock" / "scripts").is_dir())
            self.assertTrue((target / "spec-dock" / "system").is_dir())
            self.assertTrue((target / "spec-dock" / "initiatives").is_dir())
            self.assertTrue((target / "spec-dock" / "active").is_dir())
            self.assertTrue((target / "spec-dock" / ".agent").is_dir())
            self.assertTrue((target / "spec-dock" / ".gitignore").is_file())
            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".agent/", gitignore)
            self.assertIn("active/", gitignore)
            self.assertIn("/adrs/", gitignore)

            docs_dir = target / "spec-dock" / "docs"
            self.assertTrue((docs_dir / "README.md").is_file())
            self.assertTrue((docs_dir / "guide.md").is_file())
            self.assertTrue((docs_dir / "workflow_initiative.md").is_file())
            self.assertTrue((docs_dir / "workflow_epic.md").is_file())
            self.assertTrue((docs_dir / "workflow_issue.md").is_file())
            self.assertTrue((docs_dir / "workflow_adr.md").is_file())
            self.assertTrue((docs_dir / "workflow-tree.md").is_file())
            self.assertTrue((docs_dir / "phase_requirement.md").is_file())
            self.assertTrue((docs_dir / "phase_design.md").is_file())
            self.assertTrue((docs_dir / "phase_plan.md").is_file())
            self.assertTrue((docs_dir / "reference_github.md").is_file())
            self.assertTrue((docs_dir / "reference_naming.md").is_file())
            self.assertTrue((docs_dir / "reference_sync.md").is_file())

            docs_readme = (docs_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("spec-driven-tdd-workflow", docs_readme)
            self.assertIn("spec-dock-initiative-planning", docs_readme)
            self.assertIn("spec-dock-epic-planning", docs_readme)
            self.assertIn("spec-dock-issue-execution", docs_readme)
            self.assertIn("spec-dock-adr-facilitation", docs_readme)
            self.assertIn("reference レイヤ", docs_readme)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", docs_readme)
            self.assertIn("[phase_design.md](phase_design.md)", docs_readme)
            self.assertIn("[phase_plan.md](phase_plan.md)", docs_readme)

            guide_text = (docs_dir / "guide.md").read_text(encoding="utf-8")
            self.assertIn("phase playbook（共通の作り方）", guide_text)
            self.assertIn("[phase_requirement.md](phase_requirement.md)", guide_text)
            self.assertIn("[phase_design.md](phase_design.md)", guide_text)
            self.assertIn("[phase_plan.md](phase_plan.md)", guide_text)
            self._assert_guide_docs_contract(guide_text)
            workflow_tree = (docs_dir / "workflow-tree.md").read_text(encoding="utf-8")
            self._assert_workflow_tree_docs_contract(workflow_tree)

            workflow_initiative = (docs_dir / "workflow_initiative.md").read_text(encoding="utf-8")
            workflow_epic = (docs_dir / "workflow_epic.md").read_text(encoding="utf-8")
            workflow_issue = (docs_dir / "workflow_issue.md").read_text(encoding="utf-8")
            workflow_adr = (docs_dir / "workflow_adr.md").read_text(encoding="utf-8")
            self.assertIn("spec-dock-initiative-planning", workflow_initiative)
            self.assertIn("spec-dock-epic-planning", workflow_epic)
            self.assertIn("spec-dock-issue-execution", workflow_issue)
            self.assertIn("spec-dock-adr-facilitation", workflow_adr)
            self.assertIn("plan upfront approval", workflow_issue)
            self.assertIn("step result approval", workflow_issue)
            self.assertIn("docs impact", workflow_issue)
            self.assertIn("final diff review quality gate", workflow_issue)
            self.assertIn("reviewer approval", workflow_issue)
            for command in (
                "./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title",
                "./spec-dock/scripts/spec-dock import issue <num|#num|canonical-url> --title",
                "./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url>",
                "./spec-dock/scripts/spec-dock active set --id <issue-id>",
                "./spec-dock/scripts/spec-dock active set --github-issue <n>",
                "./spec-dock/scripts/spec-dock active show",
                "./spec-dock/scripts/spec-dock deps check <target>",
                "./spec-dock/scripts/spec-dock active set <target> --force",
                "./spec-dock/scripts/spec-dock validate",
                "./spec-dock/scripts/spec-dock sync",
            ):
                self.assertIn(command, workflow_issue)
            self.assertNotIn("./spec ", workflow_issue)

            # v2 does not ship legacy docs/old/ (keep the published docs minimal).
            self.assertFalse((docs_dir / "old").exists())

            # Runtime script exists; legacy close scripts must not be present.
            scripts_dir = target / "spec-dock" / "scripts"
            self.assertTrue((scripts_dir / "spec-dock").is_file())
            self.assertEqual(list(scripts_dir.glob("spec-dock-close*.sh")), [])

            # Placeholders exist (active pointers must never be broken).
            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertTrue((placeholder_root / "initiative" / "README.md").is_file())
            self.assertTrue((placeholder_root / "epic" / "README.md").is_file())
            self.assertTrue((placeholder_root / "issue" / "README.md").is_file())
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (target / "spec-dock" / "active" / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- state (github default): `./spec-dock/scripts/spec-dock sync`", context_pack_text)
            self.assertIn(
                "- state (cache/local opt-out): `./spec-dock/scripts/spec-dock sync --no-github`",
                context_pack_text,
            )
            self.assertNotIn("- state (local): `./spec-dock/scripts/spec-dock sync`", context_pack_text)
            self.assertNotIn("- state (github): `./spec-dock/scripts/spec-dock sync --github`", context_pack_text)

            # Legacy (v1) templates should not be installed.
            templates_dir = target / "spec-dock" / "templates"
            self._assert_installed_templates_match_provider_assets(target)
            for legacy in ("requirement.md", "design.md", "plan.md", "report.md"):
                self.assertFalse((templates_dir / legacy).exists(), f"legacy template leaked: {legacy}")
            self.assertEqual(list(templates_dir.rglob("current")), [])
            self.assertEqual(list(templates_dir.rglob("completed")), [])

            # Issue templates should be sufficiently detailed (regression guard).
            initiative_templates_dir = templates_dir / "initiative"
            epic_templates_dir = templates_dir / "epic"
            issue_templates_dir = templates_dir / "issue"

            req_text = (issue_templates_dir / "requirement.md").read_text(encoding="utf-8")
            self.assertIn("## 対象ユーザー / 利用シナリオ", req_text)
            self.assertIn("## 用語（ドメイン語彙）", req_text)
            for scope_templates in (
                initiative_templates_dir,
                epic_templates_dir,
                issue_templates_dir,
            ):
                self.assertFalse((scope_templates / "discussions" / "rules.md").exists())
                self.assertFalse((scope_templates / "adrs").exists())
                self.assertFalse((scope_templates / "artifacts").exists())
                self.assertEqual(list((scope_templates / "discussions").glob("new-*")), [])
            self.assertFalse((initiative_templates_dir / "epics" / "new-epic").exists())
            self.assertFalse((epic_templates_dir / "issues" / "new-issue").exists())
            self.assertFalse((initiative_templates_dir / "discussions" / "rules.md").exists())
            self.assertFalse((epic_templates_dir / "discussions" / "rules.md").exists())
            self.assertFalse((issue_templates_dir / "discussions" / "rules.md").exists())

            rules_dir = target / "spec-dock" / "docs" / "rules"
            self.assertTrue((rules_dir / "initiative" / "discussions.md").is_file())
            self.assertTrue((rules_dir / "initiative" / "epics.md").is_file())
            self.assertTrue((rules_dir / "epic" / "discussions.md").is_file())
            self.assertTrue((rules_dir / "epic" / "issues.md").is_file())
            self.assertTrue((rules_dir / "issue" / "discussions.md").is_file())

            discussions_templates_dir = templates_dir / "discussions"
            self.assertTrue((discussions_templates_dir / "adr.md").is_file())
            self.assertTrue((discussions_templates_dir / "note.md").is_file())
            self.assertTrue((discussions_templates_dir / "disc.md").is_file())
            self.assertTrue((discussions_templates_dir / "research.md").is_file())
            self.assertEqual(list(initiative_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(epic_templates_dir.rglob("README.md")), [])
            self.assertEqual(list(issue_templates_dir.rglob("README.md")), [])

            design_text = (issue_templates_dir / "design.md").read_text(encoding="utf-8")
            # UML is embedded as small subsections (not a single block at the end).
            self.assertIn("```plantuml", design_text)
            self.assertIn("### UML（", design_text)

            plan_text = (issue_templates_dir / "plan.md").read_text(encoding="utf-8")
            self.assertNotIn("update_plan", plan_text)
            self.assertIn("このテンプレートは最小 scaffold", plan_text)
            self.assertIn("## 実行ルール（全ステップ共通）", plan_text)
            self.assertIn("workflow_issue.md", plan_text)
            self.assertIn("phase_plan_issue.md", plan_text)
            self.assertIn("S90 — docs impact resolution / docs refresh", plan_text)
            self.assertIn("S99 — final diff review quality gate", plan_text)
            self.assertIn("target files:", plan_text)

            report_text = (issue_templates_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## 遭遇した問題と解決", report_text)
            self.assertIn("#### Step Contract Closure", report_text)
            self.assertIn("#### Test Contract Closure", report_text)
            self.assertIn("#### Closure Coverage", report_text)
            self.assertIn("#### Closure Delta", report_text)
            self.assertIn("| step | closure ids | close condition | evidence | result | notes |", report_text)
            self.assertIn("| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |", report_text)
            self.assertIn("| change | closure id | test id alias | resolves to closure id | reason | re-review required |", report_text)
            self.assertIn("`closure id / test id` は Central index の `id` を指す", report_text)
            self.assertIn("pass / approved no-op / fail / blocked", report_text)
            self.assertIn("|---|---|---|---|---|", report_text)

            skills_root = target / ".agents" / "skills"
            self._assert_managed_skills_installed(target)
            self.assertTrue((target / ".codex" / "agents" / "spec-manager.toml").is_file())
            self.assertTrue((target / ".github" / "agents" / "orchestrator.agent.md").is_file())

            skill_text = (skills_root / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("`discussions/`", skill_text)
            self.assertIn("./spec-dock/scripts/spec-dock new doc adr --issue", skill_text)
            self.assertIn("`spec-dock/docs/reference_deps.md`", skill_text)
            self.assertIn("`spec-dock/docs/reference_sync.md`", skill_text)
            self.assertIn("./spec-dock/scripts/spec-dock ...", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock deps check <target>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock validate", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock sync", skill_text)
            self.assertNotIn("./spec ", skill_text)
            self.assertNotIn("adrs/new-adr", skill_text)
            self.assertFalse(
                (target / ".github" / "workflows" / "spec-dock-close.yml").exists()
            )

    def test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            legacy_dir = target / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            marker_path = legacy_dir / "legacy-marker.txt"
            marker_path.write_text("legacy data\n", encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["init", str(target)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((target / "spec-dock").is_dir())
            self.assertTrue(legacy_dir.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"), "legacy data\n")
            self.assertNotIn("Please rename it before installing", stderr.getvalue())

    def test_issue_78_update_reports_manual_migration_guidance_without_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".spec-dock").mkdir(parents=True, exist_ok=True)

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["update", str(target)])

            self.assertEqual(exit_code, 1)
            error_text = stderr.getvalue()
            self.assertIn("'spec-dock' not found.", error_text)
            self.assertIn("Legacy '.spec-dock' exists with an incompatible format.", error_text)
            self.assertIn("Run 'spec-dock init'", error_text)
            self.assertIn("migrate manually", error_text)
            self.assertNotIn("Please rename it", error_text)
            self.assertNotIn("mv .spec-dock spec-dock", error_text)

    def test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            current_dir = target / "spec-dock"
            legacy_dir = target / ".spec-dock"
            legacy_dir.mkdir(parents=True, exist_ok=True)
            marker_path = legacy_dir / "legacy-marker.txt"
            marker_path.write_text("legacy data\n", encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                exit_code = main(["update", str(target)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(current_dir.is_dir())
            self.assertTrue(legacy_dir.is_dir())
            self.assertEqual(marker_path.read_text(encoding="utf-8"), "legacy data\n")
            self.assertNotIn("Please rename it", stderr.getvalue())
            self.assertNotIn("mv .spec-dock spec-dock", stderr.getvalue())

    def test_init_does_not_seed_legacy_node_deps_json_templates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            templates_dir = target / "spec-dock" / "templates"
            self.assertFalse((templates_dir / "initiative" / "deps.json").exists())
            self.assertFalse((templates_dir / "epic" / "deps.json").exists())
            self.assertFalse((templates_dir / "issue" / "deps.json").exists())

    def test_init_prunes_legacy_node_deps_json_templates_from_stale_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            def _mutate_assets(patched_assets_root: Path) -> None:
                for scope in ("initiative", "epic", "issue"):
                    deps_path = patched_assets_root / "spec_dock" / "templates" / scope / "deps.json"
                    deps_path.parent.mkdir(parents=True, exist_ok=True)
                    deps_path.write_text("legacy deps fixture\n", encoding="utf-8")

            exit_code, _stderr = self._run_command_with_assets_override("init", target, _mutate_assets)
            self.assertEqual(exit_code, 0)

            templates_dir = target / "spec-dock" / "templates"
            self.assertFalse((templates_dir / "initiative" / "deps.json").exists())
            self.assertFalse((templates_dir / "epic" / "deps.json").exists())
            self.assertFalse((templates_dir / "issue" / "deps.json").exists())

    def test_update_prunes_legacy_node_deps_json_templates_from_stale_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            def _mutate_assets(patched_assets_root: Path) -> None:
                for scope in ("initiative", "epic", "issue"):
                    deps_path = patched_assets_root / "spec_dock" / "templates" / scope / "deps.json"
                    deps_path.parent.mkdir(parents=True, exist_ok=True)
                    deps_path.write_text("legacy deps fixture\n", encoding="utf-8")

            exit_code, _stderr = self._run_command_with_assets_override("update", target, _mutate_assets)
            self.assertEqual(exit_code, 0)

            templates_dir = target / "spec-dock" / "templates"
            self.assertFalse((templates_dir / "initiative" / "deps.json").exists())
            self.assertFalse((templates_dir / "epic" / "deps.json").exists())
            self.assertFalse((templates_dir / "issue" / "deps.json").exists())

    def test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._assert_canonical_rules_files_match_provider_assets(target)

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/docs/rules/initiative/discussions.md",
                "spec-dock/docs/rules/initiative/epics.md",
                "spec-dock/docs/rules/epic/discussions.md",
                "spec-dock/docs/rules/epic/issues.md",
                "spec-dock/docs/rules/issue/discussions.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_canonical_rules_files_contract(text_map)
            self._assert_discussion_guidance_contract(text_map)

    def test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            corrupted_rules_text_map = {
                installed_rel_path: f"corrupted canonical rules guidance for {installed_rel_path}\n"
                for installed_rel_path in self._CANONICAL_RULES_PROVIDER_ASSET_MAP
            }
            for installed_rel_path, corrupted_rules_text in corrupted_rules_text_map.items():
                canonical_rules_path = target / installed_rel_path
                self._write_text_force(canonical_rules_path, corrupted_rules_text)
                self.assertEqual(
                    canonical_rules_path.read_text(encoding="utf-8"),
                    corrupted_rules_text,
                )

            self._write_text_force(
                target / "spec-dock" / "docs" / "workflow_adr.md",
                "./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title \"...\"\n",
            )
            legacy_template_text_map = {
                "spec-dock/templates/adr.md": "# legacy adr template\n",
                "spec-dock/templates/initiative/discussions/rules.md": (
                    "legacy naming: <type>-00001-<slug>.md\n"
                ),
                "spec-dock/templates/epic/discussions/rules.md": (
                    "legacy epic discussion rules\n"
                ),
                "spec-dock/templates/issue/discussions/rules.md": (
                    "legacy issue discussion rules\n"
                ),
                "spec-dock/templates/issue/discussions/_template.md": (
                    "# legacy discussion scaffold\n"
                ),
                "spec-dock/templates/initiative/epics/new-epic": "#!/bin/sh\n",
                "spec-dock/templates/epic/issues/new-issue": "#!/bin/sh\n",
            }
            for legacy_rel_path, legacy_text in legacy_template_text_map.items():
                legacy_path = target / legacy_rel_path
                legacy_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(legacy_path, legacy_text)
                self.assertTrue(legacy_path.is_file(), f"expected legacy template fixture: {legacy_rel_path}")
            self._write_text_force(
                target / "spec-dock" / "scripts" / "README.md",
                "legacy example: new adr --issue ...\n",
            )
            self._write_text_force(
                target / ".agents" / "skills" / "spec-driven-tdd-workflow" / "SKILL.md",
                "legacy skill example: new adr --issue ...\n",
            )
            legacy_gitignore_path = target / "spec-dock" / ".gitignore"
            self._write_text_force(
                legacy_gitignore_path,
                ".agent/\n"
                "active/\n"
                "tree-all.puml\n"
                "tree.puml\n"
                "deps-issues.puml\n"
                "dashboard.md\n",
            )
            self.assertNotIn(
                "/adrs/",
                legacy_gitignore_path.read_text(encoding="utf-8"),
                "legacy fixture must omit /adrs/ before update",
            )

            self.assertEqual(main(["update", str(target)]), 0)
            gitignore = (target / "spec-dock" / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("/adrs/", gitignore)
            self._assert_canonical_rules_files_match_provider_assets(target)
            self._assert_installed_templates_match_provider_assets(target)
            self._assert_workflow_tree_docs_contract(
                (target / "spec-dock" / "docs" / "workflow-tree.md").read_text(encoding="utf-8")
            )
            self._assert_guide_docs_contract(
                (target / "spec-dock" / "docs" / "guide.md").read_text(encoding="utf-8")
            )
            for installed_rel_path, corrupted_rules_text in corrupted_rules_text_map.items():
                self.assertNotEqual(
                    (target / installed_rel_path).read_text(encoding="utf-8"),
                    corrupted_rules_text,
                    f"canonical rules file was not refreshed: {installed_rel_path}",
                )
            for legacy_rel_path in legacy_template_text_map:
                self.assertFalse((target / legacy_rel_path).exists(), f"legacy template survived update: {legacy_rel_path}")

            guidance_paths = [
                "spec-dock/templates/README.md",
                "spec-dock/docs/rules/initiative/discussions.md",
                "spec-dock/docs/rules/initiative/epics.md",
                "spec-dock/docs/rules/epic/discussions.md",
                "spec-dock/docs/rules/epic/issues.md",
                "spec-dock/docs/rules/issue/discussions.md",
                "spec-dock/docs/reference_naming.md",
                "spec-dock/docs/workflow_adr.md",
                "spec-dock/docs/workflow_issue.md",
                "spec-dock/docs/workflow_epic.md",
                "spec-dock/docs/workflow_initiative.md",
                "spec-dock/docs/phase_requirement.md",
                "spec-dock/docs/phase_design.md",
                "spec-dock/docs/phase_plan.md",
                "spec-dock/docs/README.md",
                "spec-dock/docs/guide.md",
                "spec-dock/scripts/README.md",
                ".agents/skills/spec-driven-tdd-workflow/SKILL.md",
            ]
            text_map = self._read_text_map(target, guidance_paths)
            self._assert_canonical_rules_files_contract(text_map)
            self._assert_discussion_guidance_contract(text_map)

    def test_update_preserves_legacy_artifacts_inside_existing_node_trees(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            self._write_text_force(
                target / "spec-dock" / "docs" / "rules" / "initiative" / "epics.md",
                "corrupted managed rules\n",
            )
            managed_legacy_artifacts = {
                target / "spec-dock" / "templates" / "initiative" / "epics" / "new-epic": "#!/bin/sh\n",
                target / "spec-dock" / "templates" / "epic" / "issues" / "new-issue": "#!/bin/sh\n",
                target / "spec-dock" / "templates" / "issue" / "discussions" / "rules.md": (
                    "managed legacy rules\n"
                ),
            }
            for artifact_path, artifact_text in managed_legacy_artifacts.items():
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(artifact_path, artifact_text)

            node_root = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
            node_legacy_artifacts = {
                node_root / "epics" / "new-epic": "node legacy wrapper\n",
                node_root / "epics" / "rules.md": "node legacy rules copy\n",
                node_root / "epics" / "epic-local-00001-jwt-auth" / "issues" / "new-issue": (
                    "node issue wrapper\n"
                ),
                node_root
                / "epics"
                / "epic-local-00001-jwt-auth"
                / "issues"
                / "iss-local-00001-refresh-token"
                / "discussions"
                / "rules.md": "node issue discussion rules copy\n",
            }
            for artifact_path, artifact_text in node_legacy_artifacts.items():
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(artifact_path, artifact_text)
                self.assertEqual(artifact_path.read_text(encoding="utf-8"), artifact_text)

            self.assertEqual(main(["update", str(target)]), 0)

            self._assert_canonical_rules_files_match_provider_assets(target)
            self._assert_installed_templates_match_provider_assets(target)
            for artifact_path in managed_legacy_artifacts:
                self.assertFalse(artifact_path.exists(), f"managed legacy artifact survived update: {artifact_path}")
            for artifact_path, artifact_text in node_legacy_artifacts.items():
                self.assertTrue(artifact_path.is_file(), f"node-tree artifact should be preserved: {artifact_path}")
                self.assertEqual(artifact_path.read_text(encoding="utf-8"), artifact_text)

    def test_current_guidance_documents_match_discussion_numbering_contract(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        guidance_paths = [
            "src/spec_dock/assets/spec_dock/templates/README.md",
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md",
            "src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/rules/epic/issues.md",
            "src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md",
            "src/spec_dock/assets/spec_dock/docs/reference_naming.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_adr.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_issue.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_epic.md",
            "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md",
            "src/spec_dock/assets/spec_dock/docs/phase_requirement.md",
            "src/spec_dock/assets/spec_dock/docs/phase_design.md",
            "src/spec_dock/assets/spec_dock/docs/phase_plan.md",
            "src/spec_dock/assets/spec_dock/docs/README.md",
            "src/spec_dock/assets/spec_dock/docs/guide.md",
            "src/spec_dock/assets/spec_dock/scripts/README.md",
            "src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md",
        ]
        text_map = self._read_text_map(repo_root, guidance_paths)
        self._assert_canonical_rules_files_contract(text_map)
        self._assert_discussion_guidance_contract(text_map)

    def test_pyproject_excludes_deleted_wrapper_era_assets_from_package_data(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

        for package_data_pattern in _ISS_00031_EXCLUDE_PATTERNS:
            self.assertIn(
                f'"{package_data_pattern}"',
                pyproject_text,
                f"missing exclude-package-data guard for stale build artifact: {package_data_pattern}",
            )

    def test_built_wheel_excludes_deleted_wrapper_era_assets_from_stale_build_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"

            build_context.mkdir()
            shutil.copy2(repo_root / "pyproject.toml", build_context / "pyproject.toml")
            shutil.copy2(repo_root / "README.md", build_context / "README.md")
            shutil.copy2(repo_root / "setup.py", build_context / "setup.py")
            shutil.copytree(
                repo_root / "src",
                build_context / "src",
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            wheel_dir.mkdir()

            for stale_rel_path in _ISS_00031_STALE_WHEEL_PATHS:
                stale_path = build_context / "build" / "lib" / stale_rel_path
                stale_path.parent.mkdir(parents=True, exist_ok=True)
                stale_path.write_text("stale wrapper-era artifact\n", encoding="utf-8")

            wheel_path, _, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )

            with zipfile.ZipFile(wheel_path) as wheel_zip:
                wheel_entries = set(wheel_zip.namelist())

            self.assertIn(
                "spec_dock/assets/spec_dock/templates/README.md",
                wheel_entries,
                "sanity check failed: built wheel did not include expected live template asset",
            )
            for stale_rel_path in _ISS_00031_STALE_WHEEL_PATHS:
                self.assertNotIn(
                    stale_rel_path,
                    wheel_entries,
                    f"built wheel unexpectedly shipped stale build artifact: {stale_rel_path}",
                )

    def test_issue_69_package_data_includes_hidden_install_root_subtrees(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
        section_header = "[tool.setuptools.package-data]"
        next_section_header = "[tool.setuptools.exclude-package-data]"
        self.assertIn(section_header, pyproject_text, "missing setuptools package-data section")
        self.assertIn(next_section_header, pyproject_text, "missing setuptools exclude-package-data section")

        package_data_section = pyproject_text.split(section_header, 1)[1].split(next_section_header, 1)[0]
        for pattern in self._ISSUE_69_INSTALL_ROOT_PACKAGE_DATA_PATTERNS:
            self.assertIn(
                f'"{pattern}"',
                package_data_section,
                f"missing issue-69 hidden install_root package-data inclusion: {pattern}",
            )

    def test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces(self) -> None:
        surfaces = self._issue_69_collect_install_root_artifact_surfaces()
        for surface_name in ("source", "wheel", "sdist", "installed"):
            self.assertTrue(
                surfaces[surface_name],
                f"issue-69 expected non-empty install_root inventory for artifact surface: {surface_name}",
            )
            for artifact_relative_path in self._ISSUE_69_REPRESENTATIVE_ARTIFACT_RELATIVE_PATHS:
                self.assertIn(
                    artifact_relative_path,
                    surfaces[surface_name],
                    (
                        f"missing issue-69 representative install_root asset in {surface_name}: "
                        f"{artifact_relative_path}"
                    ),
                )

    def test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources(self) -> None:
        surfaces = self._issue_69_collect_install_root_artifact_surfaces()
        source_inventory = surfaces["source"]
        self.assertTrue(source_inventory, "issue-69 source install_root inventory must be non-empty")

        for surface_name in ("wheel", "sdist", "installed"):
            observed_inventory = surfaces[surface_name]
            missing = sorted(source_inventory - observed_inventory)
            unexpected = sorted(observed_inventory - source_inventory)
            self.assertEqual(
                observed_inventory,
                source_inventory,
                (
                    f"issue-69 full install_root inventory parity failed for {surface_name}; "
                    f"missing={missing[:10]} unexpected={unexpected[:10]}"
                ),
            )

    def test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir(parents=True, exist_ok=True)
            venv_python = self._issue_69_prepare_isolated_installed_wheel_runtime(
                repo_root=repo_root,
                temp_root=temp_root,
            )
            snapshot = self._issue_69_collect_isolated_installed_runtime_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=snapshot,
                repo_root=repo_root,
            )
            installed_inventory = {str(path) for path in snapshot.get("inventory", [])}
            expected_handoff_surface = set(self._ISSUE_69_HANDOFF_SURFACE_ARTIFACT_RELATIVE_PATHS)
            scope_prefixes = (
                "spec_dock/assets/install_root/.agents/host-adapters/",
                "spec_dock/assets/install_root/.codex/agents/",
                "spec_dock/assets/install_root/.github/agents/",
            )
            discovered_handoff_scope = {
                artifact_relative_path
                for artifact_relative_path in installed_inventory
                if any(artifact_relative_path.startswith(prefix) for prefix in scope_prefixes)
            }
            self.assertEqual(
                discovered_handoff_scope,
                expected_handoff_surface,
                (
                    "issue-69 isolated installed package handoff surface mismatch; "
                    f"expected={sorted(expected_handoff_surface)} observed={sorted(discovered_handoff_scope)}"
                ),
            )

    def test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir(parents=True, exist_ok=True)
            target_repo = temp_root / "consumer-repo"
            target_repo.mkdir(parents=True, exist_ok=True)
            venv_python = self._issue_69_prepare_isolated_installed_wheel_runtime(
                repo_root=repo_root,
                temp_root=temp_root,
            )
            spec_dock_command = self._issue_69_venv_spec_dock(venv_python)
            self.assertTrue(
                spec_dock_command.is_file(),
                f"issue-69 expected installed spec-dock command in isolated venv: {spec_dock_command}",
            )
            runtime_env = self._issue_69_runtime_env_without_checkout_fallback()
            init_result = self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "init", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )
            update_result = self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "update", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )

            self.assertTrue(
                (target_repo / "spec-dock").is_dir(),
                "issue-69 isolated installed package smoke should create target spec-dock directory",
            )
            combined_output = (
                f"{init_result.stdout}\n{init_result.stderr}\n{update_result.stdout}\n{update_result.stderr}"
            ).lower()
            for error_fragment in ("missing asset", "missing install_root", "missing bundled"):
                self.assertNotIn(
                    error_fragment,
                    combined_output,
                    (
                        "issue-69 isolated installed package smoke emitted missing-asset diagnostics: "
                        f"{error_fragment}"
                    ),
                )

            snapshot = self._issue_69_collect_isolated_installed_runtime_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=snapshot,
                repo_root=repo_root,
            )

    def test_issue_69_windows_helper_prefers_existing_exe_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp)
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            venv_python = scripts_dir / "python.exe"
            venv_python.write_text("", encoding="utf-8")
            spec_dock_exe = scripts_dir / "spec-dock.exe"
            spec_dock_exe.write_text("", encoding="utf-8")
            spec_dock_cmd = scripts_dir / "spec-dock.cmd"
            spec_dock_cmd.write_text("@echo off\r\n", encoding="utf-8")

            with patch("tests.test_init_update.os.name", "nt"):
                resolved = self._issue_69_venv_spec_dock(venv_python)
                ensured = self._issue_69_ensure_spec_dock_wrapper(venv_python)

            self.assertEqual(resolved, spec_dock_exe)
            self.assertEqual(ensured, spec_dock_exe)
            self.assertEqual(spec_dock_exe.read_text(encoding="utf-8"), "")

    def test_issue_69_windows_helper_prefers_existing_cmd_launcher_when_exe_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp)
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            venv_python = scripts_dir / "python.exe"
            venv_python.write_text("", encoding="utf-8")
            spec_dock_cmd = scripts_dir / "spec-dock.cmd"
            spec_dock_cmd.write_text("@echo off\r\nrem existing\r\n", encoding="utf-8")

            with patch("tests.test_init_update.os.name", "nt"):
                resolved = self._issue_69_venv_spec_dock(venv_python)
                ensured = self._issue_69_ensure_spec_dock_wrapper(venv_python)

            self.assertEqual(resolved, spec_dock_cmd)
            self.assertEqual(ensured, spec_dock_cmd)
            self.assertEqual(
                spec_dock_cmd.read_text(encoding="utf-8").splitlines(),
                ["@echo off", "rem existing"],
            )
            self.assertFalse((scripts_dir / "spec-dock.exe").exists())

    def test_issue_69_windows_helper_synthesizes_cmd_wrapper_when_launcher_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            venv_dir = Path(tmp)
            scripts_dir = venv_dir / "Scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            venv_python = scripts_dir / "python.exe"
            venv_python.write_text("", encoding="utf-8")
            expected_wrapper = scripts_dir / "spec-dock.cmd"

            with patch("tests.test_init_update.os.name", "nt"):
                resolved = self._issue_69_venv_spec_dock(venv_python)
                ensured = self._issue_69_ensure_spec_dock_wrapper(venv_python)

            self.assertEqual(resolved, expected_wrapper)
            self.assertEqual(ensured, expected_wrapper)
            self.assertTrue(expected_wrapper.is_file())
            self.assertEqual(
                expected_wrapper.read_text(encoding="utf-8").splitlines(),
                ["@echo off", f"\"{venv_python}\" -m spec_dock.cli %*"],
            )
            self.assertFalse((scripts_dir / "spec-dock.exe").exists())

    def test_issue_69_local_and_installed_handoff_surface_inventories_match(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        source_inventory = self._issue_69_collect_source_install_root_inventory(repo_root)
        expected_handoff_surface = set(self._ISSUE_69_HANDOFF_SURFACE_ARTIFACT_RELATIVE_PATHS)
        source_handoff_surface = source_inventory & expected_handoff_surface
        self.assertEqual(
            source_handoff_surface,
            expected_handoff_surface,
            (
                "issue-69 source handoff surface mismatch; "
                f"expected={sorted(expected_handoff_surface)} observed={sorted(source_handoff_surface)}"
            ),
        )

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir(parents=True, exist_ok=True)
            venv_python = self._issue_69_prepare_isolated_installed_wheel_runtime(
                repo_root=repo_root,
                temp_root=temp_root,
            )
            snapshot = self._issue_69_collect_isolated_installed_runtime_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=snapshot,
                repo_root=repo_root,
            )
            installed_inventory = {str(path) for path in snapshot.get("inventory", [])}
            installed_handoff_surface = installed_inventory & expected_handoff_surface
            missing = sorted(source_handoff_surface - installed_handoff_surface)
            unexpected = sorted(installed_handoff_surface - source_handoff_surface)
            self.assertEqual(
                installed_handoff_surface,
                source_handoff_surface,
                (
                    "issue-69 local and isolated installed handoff surface inventory mismatch; "
                    f"missing={missing[:10]} unexpected={unexpected[:10]}"
                ),
            )

    def test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"
            pre_prune_snapshot = temp_root / "wheel-pre-prune-snapshot.json"

            self._issue_69_prepare_build_context(repo_root, build_context)
            build_env = os.environ.copy()
            build_env[self._ISSUE_69_SETUP_SEED_STALE_FIXTURES_ENV] = "1"
            build_env[self._ISSUE_69_SETUP_PRE_PRUNE_SNAPSHOT_ENV] = str(pre_prune_snapshot)

            wheel_path, _, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
                build_env=build_env,
            )

            self.assertTrue(
                pre_prune_snapshot.is_file(),
                f"issue-69 expected pre-prune snapshot to exist: {pre_prune_snapshot}",
            )
            snapshot_payload = json.loads(pre_prune_snapshot.read_text(encoding="utf-8"))
            expected_seeded_fixtures = set(self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS)
            self.assertEqual(
                set(snapshot_payload.get("expected_seeded_stale_fixture_paths", [])),
                expected_seeded_fixtures,
                "issue-69 setup.py snapshot did not report the approved seeded fixture set",
            )
            self.assertEqual(
                set(snapshot_payload.get("present_before_prune", [])),
                expected_seeded_fixtures,
                "issue-69 seeded stale fixture set must exist in wheel build staging before prune",
            )

            wheel_inventory = self._issue_69_collect_wheel_file_inventory(wheel_path)
            for stale_artifact_path in self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS:
                self.assertNotIn(
                    stale_artifact_path,
                    wheel_inventory,
                    (
                        "issue-69 wheel build unexpectedly shipped seeded stale wrapper-era output: "
                        f"{stale_artifact_path}"
                    ),
                )

    def test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            build_context = temp_root / "build-context"
            wheel_dir = temp_root / "wheelhouse"
            sdist_dir = temp_root / "sdist"

            self._issue_69_prepare_build_context(repo_root, build_context)
            present_before_build = self._issue_69_seed_stale_fixtures_in_sdist_source_context(build_context)
            expected_seeded_fixtures = set(self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS)
            self.assertEqual(
                present_before_build,
                expected_seeded_fixtures,
                "issue-69 seeded stale fixture set must exist in sdist source context before build",
            )

            _, sdist_path, _ = self._issue_69_build_artifacts_with_local_wheelhouse(
                repo_root=repo_root,
                build_context=build_context,
                wheel_dir=wheel_dir,
                sdist_dir=sdist_dir,
            )

            sdist_inventory = self._issue_69_collect_sdist_source_file_inventory(sdist_path)
            for stale_artifact_path in self._ISSUE_69_SEEDED_STALE_FIXTURE_ARTIFACT_RELATIVE_PATHS:
                self.assertNotIn(
                    stale_artifact_path,
                    sdist_inventory,
                    (
                        "issue-69 sdist build unexpectedly shipped seeded stale wrapper-era output: "
                        f"{stale_artifact_path}"
                    ),
                )

    def test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        pyproject_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
        setup_text = (repo_root / "setup.py").read_text(encoding="utf-8")

        pyproject_patterns = self._issue_69_extract_pyproject_stale_exclusion_patterns(pyproject_text)
        setup_patterns = self._issue_69_extract_setup_stale_exclusion_patterns(setup_text)

        pyproject_normalized_patterns = {f"spec_dock/{pattern}" for pattern in pyproject_patterns}
        setup_pattern_set = set(setup_patterns)
        expected_pattern_set = set(self._ISSUE_69_STALE_EXCLUSION_ARTIFACT_RELATIVE_PATTERNS)

        self.assertEqual(
            pyproject_normalized_patterns,
            setup_pattern_set,
            "issue-69 stale exclusion patterns diverged between pyproject.toml and setup.py",
        )
        self.assertEqual(
            setup_pattern_set,
            expected_pattern_set,
            "issue-69 stale exclusion patterns must stay aligned to the approved exact pattern set",
        )

    def test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_script = repo_root / "spec-dock" / "scripts" / "spec-dock"
        self.assertTrue(runtime_script.is_file(), f"dogfooding runtime script missing: {runtime_script}")

        doctor_help = subprocess.run(
            [sys.executable, str(runtime_script), "doctor", "--help"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            doctor_help.returncode,
            0,
            msg=(
                "checked-in dogfooding runtime must expose 'doctor'\n"
                f"stdout:\n{doctor_help.stdout}\n"
                f"stderr:\n{doctor_help.stderr}\n"
            ),
        )
        self.assertIn("usage: spec-dock/scripts/spec-dock doctor", doctor_help.stdout)

        legacy_active = subprocess.run(
            [sys.executable, str(runtime_script), "active", "set", "--initiative", "1"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(legacy_active.returncode, 2)
        self.assertIn("'active set' supports explicit targets:", legacy_active.stderr)
        self.assertIn("active set --id <node-id>", legacy_active.stderr)

    def test_checked_in_dogfooding_mirror_docs_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_checked_in_dogfooding_mirror_docs_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_mirror_templates_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_installed_templates_match_provider_assets(repo_root, repo_root=repo_root)

    def test_spec_document_templates_keep_policy_out_of_scaffold(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        template_root = repo_root / "src/spec_dock/assets/spec_dock/templates"

        for scope in ("initiative", "epic", "issue"):
            for filename in ("requirement.md", "design.md", "plan.md"):
                text = (template_root / scope / filename).read_text(encoding="utf-8")
                self.assertNotIn("## 文書契約", text)
                self.assertNotIn("この文書が答える問い", text)
                self.assertNotIn("この文書に書かないこと", text)
                self.assertNotIn("trace policy", text)
                self.assertNotIn("## 図表方針", text)
                self.assertNotIn("## 図表ポートフォリオ", text)
                self.assertNotIn("## Traceability matrix", text)

        phase_docs = [
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_requirement.md",
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_design.md",
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_plan.md",
        ]
        for path in phase_docs:
            text = path.read_text(encoding="utf-8")
            self.assertIn("## scope ownership", text)
            self.assertIn("## diagram guidance", text)

        plan_scope_docs = [
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md",
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md",
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md",
        ]
        for path in plan_scope_docs:
            text = path.read_text(encoding="utf-8")
            self.assertIn("## diagram / trace guidance", text)

        initiative_design = (template_root / "initiative" / "design.md").read_text(encoding="utf-8")
        epic_design = (template_root / "epic" / "design.md").read_text(encoding="utf-8")
        issue_design = (template_root / "issue" / "design.md").read_text(encoding="utf-8")
        issue_plan = (template_root / "issue" / "plan.md").read_text(encoding="utf-8")
        self.assertIn("UML（推奨: system context / target-state overview）", initiative_design)
        self.assertIn("```plantuml", initiative_design)
        self.assertIn("!include C4_Context.puml", initiative_design)
        self.assertIn("LAYOUT_WITH_LEGEND()", initiative_design)
        self.assertIn("Person(user", initiative_design)
        self.assertIn("System(system", initiative_design)
        self.assertIn("System_Ext(external", initiative_design)
        self.assertIn("Rel(user, system", initiative_design)
        self.assertIn("## System Context", initiative_design)
        self.assertIn("- Title:\n  - System context / target-state overview", initiative_design)
        self.assertIn("## ドメイン境界 / ユビキタス言語（必要時）", initiative_design)
        self.assertIn("## Container Overview（必要時）", initiative_design)
        container_overview_section = initiative_design.split("## Container Overview（必要時）", 1)[1].split(
            "## 対象境界 / 依存", 1
        )[0]
        self.assertIn("N/A: reason", container_overview_section)
        self.assertNotIn("```plantuml", container_overview_section)
        self.assertIn("## Component / Module View", epic_design)
        self.assertIn("## Package Dependency", epic_design)
        self.assertIn("UML（推奨: package dependency / package dependency delta）", epic_design)
        self.assertIn("diagram metadata:", epic_design)
        self.assertIn("## Domain Model（DDD 必要時）", epic_design)
        self.assertIn("UML（推奨: component / module）", epic_design)
        self.assertIn("UML（推奨: main sequence）", epic_design)
        domain_model_section = epic_design.split("## Domain Model（DDD 必要時）", 1)[1].split(
            "## 契約", 1
        )[0]
        data_model_section = epic_design.split("## データモデル", 1)[1].split(
            "## 主要フロー", 1
        )[0]
        self.assertNotIn("```plantuml", domain_model_section)
        self.assertNotIn("```plantuml", data_model_section)
        self.assertIn("N/A: reason", domain_model_section)
        self.assertIn("N/A: reason", data_model_section)
        self.assertIn("## State / Activity（必要時）", epic_design)
        state_activity_section = epic_design.split("## State / Activity（必要時）", 1)[1].split(
            "## 失敗設計", 1
        )[0]
        self.assertIn("N/A: reason", state_activity_section)
        self.assertNotIn("```plantuml", state_activity_section)
        for section in (
            epic_design.split("## Component / Module View", 1)[1].split("## Package Dependency", 1)[0],
            epic_design.split("## Package Dependency", 1)[1].split("## Domain Model", 1)[0],
            domain_model_section,
            data_model_section,
            epic_design.split("## 主要フロー", 1)[1].split("## State / Activity", 1)[0],
            state_activity_section,
        ):
            for metadata_field in (
                "Title:",
                "Question answered:",
                "Scope:",
                "Excluded details:",
                "Update trigger:",
            ):
                self.assertIn(metadata_field, section)
        self.assertIn("このテンプレートは最小 scaffold", issue_design)
        self.assertIn("項目は追加・削除・統合・並べ替えてよい", issue_design)
        self.assertIn("## Parent Diagram References", issue_design)
        self.assertIn("module dependency:", issue_design)
        self.assertIn("class dependency（必要時）:", issue_design)
        self.assertIn("function dependency（必要時）:", issue_design)
        self.assertIn("file dependency:", issue_design)
        self.assertIn("## Module Dependency Diagram", issue_design)
        self.assertIn("- Title:", issue_design)
        self.assertIn("UML（原則: module dependency / package dependency delta）", issue_design)
        module_dependency_section = issue_design.split("## Module Dependency Diagram", 1)[1].split(
            "## Local Diagram Delta（必要時）", 1
        )[0]
        self.assertIn("```plantuml", module_dependency_section)
        self.assertNotIn("N/A: reason", module_dependency_section)
        self.assertIn("## Local Diagram Delta（必要時）", issue_design)
        self.assertIn("## Sequence Delta（必要時）", issue_design)
        self.assertIn("## Domain Model Delta（必要時）", issue_design)
        for optional_issue_section in (
            issue_design.split("## Sequence Delta（必要時）", 1)[1].split(
                "## Domain Model Delta（必要時）", 1
            )[0],
            issue_design.split("## Domain Model Delta（必要時）", 1)[1].split(
                "## クラス / インターフェース詳細設計（必要時）", 1
            )[0],
            issue_design.split("## クラス / インターフェース詳細設計（必要時）", 1)[1].split(
                "## ディレクトリ / ファイル変更計画", 1
            )[0],
        ):
            self.assertIn("N/A: reason", optional_issue_section)
            self.assertNotIn("```plantuml", optional_issue_section)
        self.assertEqual(
            1,
            issue_design.count("```plantuml"),
            "issue design scaffold should only ship the standard module dependency UML placeholder",
        )
        self.assertNotIn("必要な場合だけ追加する", issue_design)
        self.assertIn("## ディレクトリ / ファイル変更計画", issue_design)
        self.assertRegex(issue_design, r"```text\n\.\n\|-- src/\n\|   \|-- package/")
        for operation in ("Add", "Modify", "Move/Rename", "Read only", "Delete"):
            self.assertRegex(issue_design, rf"# .*{re.escape(operation)}")
        self.assertIn("depends on:", issue_design)
        self.assertNotIn("\n- Add:\n", issue_design)
        self.assertNotIn("\n- Modify:\n", issue_design)
        self.assertNotIn("\n- Delete:\n", issue_design)
        self.assertNotIn("\n- Move/Rename:\n", issue_design)
        self.assertNotIn("\n- Read only:\n", issue_design)
        self.assertNotIn("unknown path handling", issue_design)
        self.assertNotIn("user confirmation points", issue_design)
        self.assertIn("## 要件 → 設計マッピング", issue_design)
        self.assertIn("## 要件 / 例外 -> verification mapping", issue_design)
        self.assertIn("このテンプレートは最小 scaffold", issue_plan)
        self.assertIn("workflow_issue.md", issue_plan)
        self.assertIn("phase_plan_issue.md", issue_plan)
        self.assertIn("## 依存関係から導く実装順序", issue_plan)
        self.assertIn("`Module Dependency Diagram`", issue_plan)
        self.assertIn("`ディレクトリ / ファイル変更計画`", issue_plan)
        self.assertIn("depends on:", issue_plan)
        self.assertIn("unblocks:", issue_plan)
        self.assertIn("target files:", issue_plan)
        self.assertIn("## Spec-Locked Closure Index（仕様固定クロージャ索引）", issue_plan)
        self.assertIn("Issue 全体のテストケース一覧ではなく", issue_plan)
        self.assertIn("エージェントが仕様を縮小解釈・後付けテスト・過剰実装しない", issue_plan)
        self.assertIn("| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |", issue_plan)
        self.assertIn("fixture notes:", issue_plan)
        self.assertIn("golden output:", issue_plan)
        self.assertIn("manual verification:", issue_plan)
        self.assertIn("property domain:", issue_plan)
        self.assertIn("non-goals:", issue_plan)
        self.assertIn("evidence level values:", issue_plan)
        self.assertIn("red-required:", issue_plan)
        self.assertIn("covered-existing:", issue_plan)
        self.assertIn("inspect-only:", issue_plan)
        self.assertIn("manual-required:", issue_plan)
        self.assertIn("通常 Issue は step / behavior slice ごとに 1〜3 件程度の検証契約を書く", issue_plan)
        self.assertIn("中央 index は重複するテストケース表にせず", issue_plan)
        self.assertIn("test bundle:", issue_plan)
        self.assertIn("closure ids:", issue_plan)
        self.assertIn("test ids:", issue_plan)
        self.assertIn("same as closure ids unless a project explicitly documents separate aliases", issue_plan)
        self.assertIn("evidence level:", issue_plan)
        self.assertIn("acceptance:", issue_plan)
        self.assertIn("characterization:", issue_plan)
        self.assertIn("property / invariant:", issue_plan)
        self.assertIn("regression:", issue_plan)
        self.assertIn("negative:", issue_plan)
        self.assertIn("pre-implementation evidence:", issue_plan)
        self.assertIn("expected red / characterization pass / test sensitivity evidence", issue_plan)
        self.assertIn("#### step closure contract", issue_plan)
        self.assertIn("closure ids:", issue_plan)
        self.assertIn("close when:", issue_plan)
        self.assertIn("verification evidence:", issue_plan)
        self.assertIn("Step Contract Closure:", issue_plan)
        self.assertIn("Closure Coverage:", issue_plan)
        self.assertIn("#### behavior slice execution", issue_plan)
        self.assertIn("implementation batch:", issue_plan)
        self.assertIn("allowed scope:", issue_plan)
        self.assertIn("forbidden scope:", issue_plan)
        self.assertIn("related / full command:", issue_plan)
        self.assertIn("refactor / tidy:", issue_plan)
        self.assertNotIn("TDD iterations", issue_plan)
        self.assertNotIn("update_plan", issue_plan)
        self.assertNotIn("commit gate", issue_plan)
        self.assertNotIn("commit expectation", issue_plan)
        self.assertIn("## 要件 ↔ ステップ対応", issue_plan)

        phase_design = (repo_root / "src/spec_dock/assets/spec_dock/docs/phase_design.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Markdown preview compatibility", phase_design)
        self.assertIn("`c4plantuml` fence は VS Code Markdown preview 互換性のため使わない", phase_design)
        self.assertIn("`!include C4_Context.puml`", phase_design)
        self.assertIn("## PlantUML / UML usage policy", phase_design)
        self.assertIn("人間が構造・境界・責務・流れ・状態・依存を短時間で理解できる設計書", phase_design)
        self.assertIn("視覚的・構造的に把握しやすくするために使う", phase_design)
        self.assertIn("目的は「図を増やすこと」ではなく", phase_design)
        self.assertIn("templates は完成形や準拠規格ではなく", phase_design)
        self.assertIn("項目を追加・削除・統合・並べ替えてよい", phase_design)
        self.assertIn("## diagram selection rules", phase_design)
        self.assertIn("## optional diagram catalog", phase_design)
        self.assertIn("テンプレートから削った図表は「不要になった情報」ではなく", phase_design)
        self.assertIn("必要ならここにない図表も追加してよい", phase_design)
        for diagram_name in (
            "Use Case",
            "C4 System Context",
            "C4 Container",
            "Component / Module View",
            "Package Dependency / Package Dependency Delta",
            "Module Dependency Diagram",
            "Sequence",
            "Activity",
            "State",
            "Domain Model / Aggregate",
            "Bounded Context Map",
            "Object",
            "Class / Interface",
            "ER / DB Schema",
            "Deployment",
            "Step Dependency Graph / Test Matrix / Rollback Map",
        ):
            self.assertIn(diagram_name, phase_design)
        self.assertIn("## DDD diagram guidance", phase_design)
        self.assertIn("## UML review gate", phase_design)
        self.assertIn("Title", phase_design)
        self.assertIn("Question answered", phase_design)
        self.assertIn("Excluded details", phase_design)
        self.assertIn("Update trigger", phase_design)
        self.assertIn("N/A: reason", phase_design)
        self.assertIn("対応する `plantuml` block は削除する", phase_design)
        self.assertIn("図を書く場合は `N/A: reason` を残さない", phase_design)
        self.assertIn("Domain Model Delta", phase_design)
        self.assertIn("PlantUML / C4 / DDD 図は Markdown 内では `plantuml` fence を使う", phase_design)
        self.assertIn("## Issue dependency and file-change planning", phase_design)
        self.assertIn("Module Dependency Diagram", phase_design)
        self.assertIn("ディレクトリ / ファイル変更計画", phase_design)
        self.assertIn("Linux `tree` style", phase_design)
        self.assertIn("tree の下に同じ path 一覧を重複して置かない", phase_design)
        self.assertIn("この節は後方互換の入口です", phase_design)

        phase_plan_issue = (
            repo_root / "src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md"
        ).read_text(encoding="utf-8")
        self.assertIn("`Module Dependency Diagram`", phase_plan_issue)
        self.assertIn("`ディレクトリ / ファイル変更計画`", phase_plan_issue)
        self.assertIn("`depends on`", phase_plan_issue)
        self.assertIn("`unblocks`", phase_plan_issue)
        self.assertIn("`target files`", phase_plan_issue)
        self.assertIn("canonical path inventory", phase_plan_issue)
        self.assertIn("templates は最小 scaffold", phase_plan_issue)
        self.assertIn("`behavior slice` は 1 つの観測可能な振る舞い", phase_plan_issue)
        self.assertIn("`test bundle`", phase_plan_issue)
        self.assertIn("`pre-implementation evidence`", phase_plan_issue)
        self.assertIn("`bounded implementation batch`", phase_plan_issue)
        self.assertIn("`test sensitivity evidence`", phase_plan_issue)
        self.assertIn("`Spec-Locked Closure Index`（仕様固定クロージャ索引）", phase_plan_issue)
        self.assertIn("Issue 全体のテストケース一覧ではなく", phase_plan_issue)
        self.assertIn("`id`、`phase / step`、`slice`、`type`、`spec link`、`locked expectation`、`observable input/state`、`bug class guarded`、`required`、`evidence level`、`closure evidence`", phase_plan_issue)
        self.assertIn("`red-required`、`covered-existing`、`inspect-only`、`manual-required`", phase_plan_issue)
        self.assertIn("すべての row に failing test を要求しない", phase_plan_issue)
        self.assertIn("Central index は仕様由来の `spec link`", phase_plan_issue)
        self.assertIn("`step closure contract` はその step で満たす closure `id`", phase_plan_issue)
        self.assertIn("`test ids` と書く場合も Central index の closure `id` の alias", phase_plan_issue)
        self.assertIn("`test id alias` と `resolves to closure id`", phase_plan_issue)
        self.assertIn("`test bundle` は Central index の `locked expectation` / `observable input/state` を再記述しない", phase_plan_issue)
        self.assertIn("各 step の close 判定は Issue 全体の一覧表ではなく", phase_plan_issue)
        self.assertIn("plan amendment と re-review を必須", phase_plan_issue)
        self.assertIn("every `required=yes` closure row", phase_plan_issue)
        self.assertIn("every bundle `closure id` が Central index に存在", phase_plan_issue)
        self.assertIn("private method、実装アルゴリズム、mock 構造、assert 細部を原則固定しない", phase_plan_issue)
        self.assertIn("public CLI behavior、shipped scaffold / runtime contract", phase_plan_issue)
        self.assertNotIn("failing test は iteration ごとに 1 本ずつ進める", phase_plan_issue)
        self.assertIn("commit/no-op は `workflow_issue.md` の実行 contract が所有", phase_plan_issue)
        self.assertIn("Issue 固有の判断が必要な場合だけ明記する", phase_plan_issue)
        self.assertIn("report-before-commit/no-op の実行順は `workflow_issue.md`", phase_plan_issue)

        workflow_issue = (
            repo_root / "src/spec_dock/assets/spec_dock/docs/workflow_issue.md"
        ).read_text(encoding="utf-8")
        self.assertIn("templates は完成形ではなく、書き始めるための最小 scaffold", workflow_issue)
        self.assertIn("項目を追加・削除・統合・並べ替えてよい", workflow_issue)
        self.assertIn("正確性、検証可能性、人間の理解、エージェントの実行", workflow_issue)
        self.assertIn("`optional diagram catalog` から必要なものを選んで追加してよい", workflow_issue)
        self.assertIn("カタログ外でも、構造・境界・責務・流れ・状態・依存", workflow_issue)
        self.assertIn("Linux `tree` style の `ディレクトリ / ファイル変更計画`", workflow_issue)
        self.assertIn("仕様固定マイクロバッチTDD", workflow_issue)
        self.assertIn("Spec-Locked Micro-Batch TDD", workflow_issue)
        self.assertIn("Spec-Locked Closure Index", workflow_issue)
        self.assertIn("Issue 全体のテストケース一覧や詳細なテスト実装指示ではなく", workflow_issue)
        self.assertIn("closure index の `id` を参照", workflow_issue)
        self.assertIn("required closure id が behavior slice", workflow_issue)
        self.assertIn("plan amendment と re-review", workflow_issue)
        self.assertIn("Step Contract Closure", workflow_issue)
        self.assertIn("Test Contract Closure", workflow_issue)
        self.assertIn("Closure Coverage", workflow_issue)
        self.assertIn("required closure id が `Step Contract Closure` / `Test Contract Closure` / `Closure Coverage` で pass または approved no-op", workflow_issue)
        self.assertIn("Closure Delta", workflow_issue)
        self.assertIn("step closure contract / test bundle / pre-implementation evidence", workflow_issue)
        self.assertIn("bounded implementation batch", workflow_issue)
        self.assertIn("test sensitivity evidence", workflow_issue)
        self.assertNotIn("Red → Green → Refactor → review", workflow_issue)

        issue_execution_skill = (
            repo_root
            / "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("spec-dock/docs/phase_plan_issue.md", issue_execution_skill)
        self.assertIn("Keep templates as scaffolds", issue_execution_skill)
        self.assertIn("Spec authoring mode", issue_execution_skill)
        self.assertIn("Execution mode", issue_execution_skill)
        self.assertIn("optional diagram catalog", issue_execution_skill)
        self.assertIn("authoritative source for diagram choices", issue_execution_skill)
        self.assertIn("catalog-listed or project-specific sections", issue_execution_skill)
        self.assertIn("Spec-Locked Closure Index", issue_execution_skill)
        self.assertIn("required closure id", issue_execution_skill)
        self.assertIn("behavior slice `closure ids` / `test ids`", issue_execution_skill)
        self.assertIn("verification command, or evidence path", issue_execution_skill)
        self.assertIn("Step Contract Closure", issue_execution_skill)
        self.assertIn("Test Contract Closure", issue_execution_skill)
        self.assertIn("Closure Coverage", issue_execution_skill)
        self.assertIn("Closure Delta", issue_execution_skill)
        self.assertNotIn("Add Use Case, Sequence", issue_execution_skill)

        workflow_skill = (
            repo_root
            / "src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("minimum authoring scaffolds", workflow_skill)
        self.assertIn("add, remove, merge, reorder, or rewrite", workflow_skill)
        self.assertIn("optional diagram choices", workflow_skill)
        self.assertIn("project-specific sections outside the catalog", workflow_skill)

        for root in (
            repo_root / "src/spec_dock/assets/spec_dock/templates",
            repo_root / "src/spec_dock/assets/spec_dock/docs",
            repo_root / "spec-dock/templates",
            repo_root / "spec-dock/docs",
        ):
            for path in root.rglob("*.md"):
                self.assertNotIn(
                    "```c4plantuml",
                    path.read_text(encoding="utf-8"),
                    f"Markdown preview does not render c4plantuml fences: {path}",
                )

    def test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        initiatives_root = repo_root / "spec-dock" / "initiatives"
        self.assertTrue(
            initiatives_root.is_dir(),
            f"checked-in dogfooding initiatives tree missing: {initiatives_root}",
        )
        meta_paths = sorted(initiatives_root.rglob(".meta.json"))
        self.assertGreater(
            len(meta_paths),
            0,
            f"checked-in dogfooding initiatives tree is empty of .meta.json: {initiatives_root}",
        )
        observed_meta_paths = [meta_path.relative_to(repo_root).as_posix() for meta_path in meta_paths]
        self.assertEqual(
            observed_meta_paths,
            list(self._CHECKED_IN_DOGFOODING_META_JSON_PATHS),
            "checked-in dogfooding .meta.json path set diverged from cutover snapshot",
        )

        legacy_deps_paths = sorted(
            path.relative_to(repo_root).as_posix() for path in initiatives_root.rglob("deps.json")
        )
        self.assertEqual(
            legacy_deps_paths,
            [],
            f"checked-in dogfooding initiatives still contain legacy deps.json: {legacy_deps_paths}",
        )

        non_list_depends_on_paths: list[str] = []
        observed_depends_on_by_meta_path: dict[str, list[object]] = {}
        for meta_path in meta_paths:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            rel_meta_path = meta_path.relative_to(repo_root).as_posix()
            depends_on = payload.get("depends_on", [])
            if not isinstance(depends_on, list):
                non_list_depends_on_paths.append(rel_meta_path)
                continue
            observed_depends_on_by_meta_path[rel_meta_path] = depends_on
        self.assertEqual(
            non_list_depends_on_paths,
            [],
            "checked-in dogfooding .meta.json has non-list depends_on values: "
            f"{non_list_depends_on_paths}",
        )
        self.assertEqual(
            observed_depends_on_by_meta_path,
            self._CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH,
            "checked-in dogfooding depends_on values diverged from cutover baseline",
        )

    def test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        checked_in_initiatives_root = repo_root / "spec-dock" / "initiatives"
        self.assertTrue(
            checked_in_initiatives_root.is_dir(),
            f"checked-in dogfooding initiatives tree missing: {checked_in_initiatives_root}",
        )
        self.assertGreater(
            len(list(checked_in_initiatives_root.rglob(".meta.json"))),
            0,
            "checked-in dogfooding initiatives tree must contain .meta.json before runtime cutover checks",
        )

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)

            target_initiatives_root = target / "spec-dock" / "initiatives"
            shutil.rmtree(target_initiatives_root)
            shutil.copytree(checked_in_initiatives_root, target_initiatives_root)

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

            sync_result = self._run_runtime_capture(target, ["sync"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            runtime_map_check_code = f"""
import json
import sys
from pathlib import Path

runtime_scripts_dir = Path({str(target / "spec-dock" / "scripts")!r})
specdock_dir = Path({str(target / "spec-dock")!r})
sys.path.insert(0, str(runtime_scripts_dir))
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.cli import bootstrap as runtime_bootstrap
finally:
    sys.path.pop(0)

runtime = runtime_bootstrap.build_runtime(specdock_dir)
result = runtime.use_cases.sync(
    app_contracts.SyncRequest(
        force=False,
        github_enabled=False,
        issue_limit=200,
        update_active_from_branch=False,
    )
)
if result.artifact_failure is not None:
    raise AssertionError(f"runtime sync artifact failure: {{result.artifact_failure}}")

expected_non_empty = {json.dumps(self._CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP, ensure_ascii=False)}
observed_full = result.state.issue_depends_on_map
observed_non_empty = {{issue_id: deps for issue_id, deps in observed_full.items() if deps}}
assert observed_non_empty == expected_non_empty, json.dumps(
    {{
        "expected_non_empty": expected_non_empty,
        "observed_non_empty": observed_non_empty,
        "observed_full": observed_full,
    }},
    ensure_ascii=False,
    indent=2,
)
"""
            runtime_map_result = subprocess.run(
                [sys.executable, "-c", runtime_map_check_code],
                cwd=str(target),
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                runtime_map_result.returncode,
                0,
                msg=(
                    "runtime issue_depends_on_map mismatch on cutover snapshot\n"
                    f"stdout:\n{runtime_map_result.stdout}\n"
                    f"stderr:\n{runtime_map_result.stderr}"
                ),
            )

    def test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        checked_in_initiatives_root = repo_root / "spec-dock" / "initiatives"
        self.assertTrue(
            checked_in_initiatives_root.is_dir(),
            f"checked-in dogfooding initiatives tree missing: {checked_in_initiatives_root}",
        )

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)

            target_initiatives_root = target / "spec-dock" / "initiatives"
            shutil.rmtree(target_initiatives_root)
            shutil.copytree(checked_in_initiatives_root, target_initiatives_root)

            def _find_issue_meta_path(issue_id: str) -> Path:
                matches: list[Path] = []
                for meta_path in target_initiatives_root.rglob(".meta.json"):
                    payload = json.loads(meta_path.read_text(encoding="utf-8"))
                    if payload.get("type") == "issue" and payload.get("id") == issue_id:
                        matches.append(meta_path)
                self.assertEqual(
                    len(matches),
                    1,
                    f"cutover snapshot must have exactly one issue meta for {issue_id}: {matches}",
                )
                return matches[0]

            from_issue_id = "iss-00063"
            to_issue_id = "iss-00062"
            from_meta_path = _find_issue_meta_path(from_issue_id)
            self.assertEqual(
                json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on"),
                [],
                f"expected empty depends_on before deps add on {from_issue_id}",
            )

            add_result = self._run_runtime_capture(
                target,
                ["deps", "add", "--from", from_issue_id, "--to", to_issue_id],
            )
            self.assertEqual(
                add_result.returncode,
                0,
                msg=f"deps add stdout:\n{add_result.stdout}\ndeps add stderr:\n{add_result.stderr}",
            )
            self.assertIn(
                f"spec-dock: ok (deps add) from={from_issue_id} to={to_issue_id} result=updated",
                add_result.stdout,
            )
            self.assertEqual(
                json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on"),
                [to_issue_id],
                "deps add did not persist expected depends_on edge into .meta.json",
            )

            remove_result = self._run_runtime_capture(
                target,
                ["deps", "remove", "--from", from_issue_id, "--to", to_issue_id],
            )
            self.assertEqual(
                remove_result.returncode,
                0,
                msg=(
                    f"deps remove stdout:\n{remove_result.stdout}\n"
                    f"deps remove stderr:\n{remove_result.stderr}"
                ),
            )
            self.assertIn(
                f"spec-dock: ok (deps remove) from={from_issue_id} to={to_issue_id} result=updated",
                remove_result.stdout,
            )
            self.assertEqual(
                json.loads(from_meta_path.read_text(encoding="utf-8")).get("depends_on"),
                [],
                "deps remove did not clear depends_on edge from .meta.json",
            )

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

            sync_result = self._run_runtime_capture(target, ["sync"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

    def test_checked_in_dogfooding_runtime_mirror_match_provider_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        self._assert_checked_in_dogfooding_runtime_mirror_match_provider_assets(repo_root)

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_import_uniqueness_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self.records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), str(repo_slug)))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Foreign #123",
            labels=[],
            updated_at="2026-03-19T00:00:00Z",
            url="https://github.com/other/repo/issues/123",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-00123",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        ),
    ]
    _materialize_required_artifacts(records)

    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    request = app_contracts.ImportNodeRequest(
        issue_number=123,
        title="Foreign Issue",
        slug=None,
        parent_id="epic-local-00001",
        target_repo_owner="other",
        target_repo_name="repo",
        allow_foreign_url=True,
    )
    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(request, ports)
        except RuntimeError as exc:
            message = str(exc)
        else:
            raise AssertionError("expected foreign import to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert "single-repo" in message, message
    assert "GitHub-backed identity" in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_release_lock_backward_compat_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import import_node as app_import_node
finally:
    sys.path.pop(0)

with tempfile.TemporaryDirectory() as td:
    specdock_dir = Path(td) / "spec-dock"
    lock_path = specdock_dir / "system" / ".runtime" / "create.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_payload = (
        "token=holder\\n"
        "pid=222\\n"
        "user=lock-holder\\n"
        "created_unix=9999999999\\n"
        "created_iso=2099-01-01T00:00:00Z\\n"
    )
    lock_path.write_text(lock_payload, encoding="utf-8")

    try:
        app_import_node._release_create_lock(lock_path, "other")
        raise AssertionError("expected ownership mismatch")
    except RuntimeError as exc:
        message = str(exc)

    runtime_cmd = str((specdock_dir / "scripts" / "spec-dock").resolve())
    assert "reason=ownership_mismatch" in message, message
    assert f"{{runtime_cmd}} doctor" in message, message
    assert lock_path.exists(), "lock unexpectedly removed on ownership mismatch"

    lock_path.write_text(lock_payload, encoding="utf-8")
    app_import_node._release_create_lock(lock_path, "holder")
    assert not lock_path.exists(), "lock was not removed"
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_import_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/example/repo/issues/{{issue_number}}",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00555",
        title="Race winner import",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00555-race-winner-import",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=555,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=555,
                    title="Imported issue",
                    slug=None,
                    parent_id="epic-local-00001",
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "already linked" in message, message
        else:
            raise AssertionError("expected import/import race to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert injected["done"], injected
    assert events == [], events
    assert issue_gateway.calls == [(str(repo_root), 555, "example/repo")], issue_gateway.calls
    assert sum(1 for record in node_repo.records if record.id == "iss-00555") == 1, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_import_new_race_revalidation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
        self.on_view = None
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        if self.on_view is not None:
            self.on_view()
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Race",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://github.com/other/repo/issues/{{issue_number}}",
            repo_owner="other",
            repo_name="repo",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    node_repo = _StubNodeRepo(records, events)
    issue_gateway = _StubIssueGateway()
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    raced_record = _record(
        kind="issue",
        node_id="iss-00123",
        title="Race winner new issue",
        path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-00123-race-winner-new-issue",
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
    )
    injected = {{"done": False}}
    def _inject_race_winner():
        if injected["done"]:
            return
        _materialize_required_artifacts([raced_record])
        node_repo.records.append(raced_record)
        injected["done"] = True

    issue_gateway.on_view = _inject_race_winner

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=123,
                    title="Imported foreign issue",
                    slug=None,
                    parent_id="epic-local-00001",
                    target_repo_owner="other",
                    target_repo_name="repo",
                    allow_foreign_url=True,
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
        else:
            raise AssertionError("expected foreign import to be rejected")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert not injected["done"], injected
    assert "single-repo" in message, message
    assert "GitHub-backed identity" in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
    assert events == [], events
    assert sum(1 for record in node_repo.records if record.id == "iss-00123") == 0, node_repo.records
    assert sum(1 for record in node_repo.records if record.id == "iss-local-00001") == 0, node_repo.records
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_no_write_preflight_collision_with_active_parent_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        dest_dir.mkdir(parents=True, exist_ok=True)
        payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Issue",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://example.invalid/issues/{{issue_number}}",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"

class _StubActiveStateStore:
    def __init__(self, manifest):
        self._manifest = manifest
        self.calls = []
    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )
    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    (issue_template_dir / "README.md").write_text("issue=<ISS_ID>\\n", encoding="utf-8")
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00001-jwt-auth",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    events = []
    issue_gateway = _StubIssueGateway()
    active_state_store = _StubActiveStateStore(
        infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/path/init-local-00001",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/path/epic-local-00001",
            ),
            issue=None,
        )
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records, events),
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        active_state_store=active_state_store,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    collision = (
        Path(records[1].path)
        / "issues"
        / "iss-00124-add-refresh-token"
        / "README.md"
    )
    collision.parent.mkdir(parents=True, exist_ok=True)
    collision.write_text("existing", encoding="utf-8")

    original_sync_after_import = app_import_node.sync_after_import
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        try:
            app_import_node.import_issue(
                app_contracts.ImportNodeRequest(
                    issue_number=124,
                    title="Add refresh token",
                    slug=None,
                    parent_id=None,
                ),
                ports,
            )
        except RuntimeError as exc:
            message = str(exc)
            assert "Destination already exists" in message, message
        else:
            raise AssertionError("expected preflight collision to fail")
    finally:
        app_import_node.sync_after_import = original_sync_after_import

    assert events == [], events
    assert issue_gateway.calls == [], issue_gateway.calls
    assert [name for name, _path in active_state_store.calls] == ["load_active_manifest_no_migrate"], active_state_store.calls
    assert not (collision.parent / ".meta.json").exists()
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_parent_fallback_reresolve_inside_lock_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import import_node as app_import_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self.records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        dest_dir.mkdir(parents=True, exist_ok=True)
        payload = {{
            "schema_version": 1,
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
            "parent_id": record.parent_id,
            "initiative_id": record.initiative_id,
            "epic_id": record.epic_id,
        }}
        if record.github_issue_number is not None:
            payload["github"] = {{"issue_number": int(record.github_issue_number)}}
        (Path(dest_dir) / ".meta.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(str(key), str(value))
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if src_path.is_dir():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self):
        self.calls = []
    def issue_view_minimal(self, repo_root, issue_number, *, repo_slug=None):
        self.calls.append((str(repo_root), int(issue_number), repo_slug))
        return domain_models.IssueSnapshot(
            issue_number=int(issue_number),
            state="OPEN",
            title="Issue",
            labels=[],
            updated_at="2026-03-20T00:00:00Z",
            url=f"https://example.invalid/issues/{{issue_number}}",
        )

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "example/repo"

class _StubActiveStateStore:
    def __init__(self, manifest):
        self._manifest = manifest
        self.calls = []
    def load_active_manifest(self, specdock_dir):
        self.calls.append(("load_active_manifest", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )
    def load_active_manifest_no_migrate(self, specdock_dir):
        self.calls.append(("load_active_manifest_no_migrate", str(specdock_dir)))
        return infra_contracts.ActiveManifestLoadResult(
            manifest=self._manifest,
            source="agent.active",
            warnings=[],
        )

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    issue_template_dir = specdock_dir / "templates" / "issue"
    issue_template_dir.mkdir(parents=True, exist_ok=True)
    (issue_template_dir / "README.md").write_text("issue=<ISS_ID>\\n", encoding="utf-8")
    for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
        (issue_template_dir / filename).write_text(f"template:{{filename}}\\n", encoding="utf-8")
    rules_dir = specdock_dir / "docs" / "rules" / "issue"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "discussions.md").write_text("# issue discussions\\n", encoding="utf-8")

    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00001-jwt-auth",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00002",
            title="Session rotation",
            path=specdock_dir / "initiatives" / "init-local-00001-auth-platform" / "epics" / "epic-local-00002-session-rotation",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)

    issue_gateway = _StubIssueGateway()
    active_state_store = _StubActiveStateStore(
        infra_contracts.ActiveManifest(
            initiative=infra_contracts.ActiveManifestEntry(
                id="init-local-00001",
                path="spec-dock/path/init-local-00001",
            ),
            epic=infra_contracts.ActiveManifestEntry(
                id="epic-local-00001",
                path="spec-dock/path/epic-local-00001",
            ),
            issue=None,
        )
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        active_state_store=active_state_store,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    captured = {{"resolve_calls": 0}}
    original_resolve_parent_from_active = app_import_node.resolve_parent_from_active
    original_sync_after_import = app_import_node.sync_after_import
    def _drifting_resolve_parent_from_active(graph, child_kind, active):
        del graph, active
        assert child_kind == "issue", child_kind
        captured["resolve_calls"] += 1
        if captured["resolve_calls"] == 1:
            return "epic-local-00001"
        return "epic-local-00002"
    app_import_node.resolve_parent_from_active = _drifting_resolve_parent_from_active
    app_import_node.sync_after_import = lambda _ports: object()
    try:
        result = app_import_node.import_issue(
            app_contracts.ImportNodeRequest(
                issue_number=777,
                title="Parent drift import",
                slug=None,
                parent_id=None,
            ),
            ports,
        )
    finally:
        app_import_node.resolve_parent_from_active = original_resolve_parent_from_active
        app_import_node.sync_after_import = original_sync_after_import

    assert captured["resolve_calls"] == 2, captured
    assert result.node.parent_id == "epic-local-00002", result.node.parent_id
    assert "/epic-local-00002-session-rotation/" in result.node.path.as_posix(), result.node.path
    assert issue_gateway.calls == [(str(repo_root), 777, "example/repo")], issue_gateway.calls
    assert [name for name, _path in active_state_store.calls] == [
        "load_active_manifest_no_migrate",
        "load_active_manifest_no_migrate",
    ], active_state_store.calls
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_sync_snapshot_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
    from spec_dock_runtime.presentation import json_state as presentation_json_state
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "main"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / ".meta.json").write_text("{{}}", encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=301,
                state="OPEN",
                title="Current repo #301",
                labels=[],
                updated_at="2026-03-18T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        ],
        foreign_snapshots={{
            ("other/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Foreign #301",
                labels=["bugfix"],
                updated_at="2026-03-18T02:00:00Z",
                url="https://github.com/other/repo/issues/301",
                repo_owner="other",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )
    result = app_sync_state.collect_sync_state(
        app_contracts.SyncRequest(
            force=False,
            github_enabled=True,
            issue_limit=10000,
            update_active_from_branch=False,
        ),
        ports,
    )
    current_status = result.issue_statuses["iss-local-00001"]
    foreign_status = result.issue_statuses["iss-local-00002"]
    assert current_status.effective_status == "open"
    assert foreign_status.effective_status == "done"
    index_all = json.loads(presentation_json_state.render_index_artifact(result).all_json_text)
    current_payload = index_all["nodes"]["iss-local-00001"]["github"]
    foreign_payload = index_all["nodes"]["iss-local-00002"]["github"]
    assert current_payload["url"] == "https://github.com/current/repo/issues/301"
    assert current_payload["state"] == "OPEN"
    assert foreign_payload["url"] == "https://github.com/other/repo/issues/301"
    assert foreign_payload["state"] == "CLOSED"
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_active_deps_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=301,
                state="OPEN",
                title="Current repo #301",
                labels=[],
                updated_at="2026-03-18T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        ],
        foreign_snapshots={{
            ("other/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Foreign #301",
                labels=["bugfix"],
                updated_at="2026-03-18T02:00:00Z",
                url="https://github.com/other/repo/issues/301",
                repo_owner="other",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    current_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert current_status.effective_status == "open"
    assert deps_result.inspection.evaluation.ready is True
    assert deps_result.inspection.evaluation.guard_reason == "ready"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "other/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_non_issue_deps_target_status_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
    from spec_dock_runtime.presentation import json_state as presentation_json_state
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(issue_depends_on_map={{}}, warnings=[])

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots):
        self._snapshots = list(snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        raise RuntimeError("unexpected repo-scoped issue view")

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-00101",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-00101-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        _record(
            kind="epic",
            node_id="epic-00201",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-00101-platform" / "epics" / "epic-00201-delivery",
            parent_id="init-00101",
            initiative_id="init-00101",
            epic_id=None,
            github_issue_number=201,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[
            domain_models.IssueSnapshot(
                issue_number=101,
                state="OPEN",
                title="Initiative #101",
                labels=[],
                updated_at="2026-03-20T10:00:00Z",
                url="https://github.com/current/repo/issues/101",
                repo_owner="current",
                repo_name="repo",
            ),
            domain_models.IssueSnapshot(
                issue_number=201,
                state="OPEN",
                title="Epic #201",
                labels=[],
                updated_at="2026-03-20T11:00:00Z",
                url="https://github.com/current/repo/issues/201",
                repo_owner="current",
                repo_name="repo",
            ),
        ],
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
    )

    for target_id, expected_last_sync_at in (
        ("init-00101", "2026-03-20T10:00:00Z"),
        ("epic-00201", "2026-03-20T11:00:00Z"),
    ):
        deps_result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id=target_id, github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )
        payload = json.loads(presentation_json_state.render_deps_check_json(deps_result))
        target_status = payload["target_status"]
        assert target_status["authority"] == "github"
        assert target_status["effective_status"] == "open"
        assert target_status["source"] == "github"
        assert target_status["stale"] is False
        assert target_status["last_sync_at"] == expected_last_sync_at

    assert issue_gateway.view_calls == []
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_issue_create_lock_scope_narrowing_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, %r)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

def _runtime_cmd(specdock_dir):
    return shlex.quote(str((specdock_dir / "scripts" / "spec-dock").resolve()))

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records, events):
        self.records = list(records)
        self.events = events
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self.records)
    def write_meta(self, dest_dir, record):
        self.events.append("write_meta")
        Path(dest_dir).mkdir(parents=True, exist_ok=True)
        (Path(dest_dir) / ".meta.json").write_text(f"id={record.id}\\n", encoding="utf-8")
        self.records.append(record)

class _StubTemplateScaffolder:
    def __init__(self, events):
        self.events = events
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        self.events.append("copy_scaffolded_tree")
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            rendered = self.render_text(src_path.read_text(encoding="utf-8"), replacements)
            dst.write_text(rendered, encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _FailingTemplateScaffolder(_StubTemplateScaffolder):
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise RuntimeError("simulated write seam failure")

class _BlockingIssueGateway:
    def __init__(self, numbers, started_event, release_event):
        self.numbers = list(numbers)
        self.calls = []
        self.started_event = started_event
        self.release_event = release_event
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        self.started_event.set()
        if not self.release_event.wait(timeout=5.0):
            raise RuntimeError("timed out waiting for release_event")
        if not self.numbers:
            raise RuntimeError("no issue numbers configured")
        return self.numbers.pop(0)

class _StubClock:
    def today(self):
        return "2026-03-20"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([811], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    issue_result = {}
    issue_errors = []
    def _run_issue():
        try:
            issue_result["value"] = app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            issue_errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    try:
        local_result = app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Payments",
                slug=None,
                parent_id=None,
                requested_node_id=None,
                github_mode="link_existing",
                github_issue_number=702,
            ),
            ports,
        )
    finally:
        release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert issue_errors == [], issue_errors
    assert local_result.node.id == "init-00702", local_result
    assert issue_result["value"].node.id == "iss-00811", issue_result
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    body = issue_gateway.calls[0][2]
    assert "Type: issue" in body, body
    assert "Epic:" not in body, body
    assert "Initiative:" not in body, body

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([812], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    errors = []
    def _run_issue():
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    node_repo.records = [record for record in node_repo.records if record.id != "epic-local-00001"]
    release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert len(errors) == 1, errors
    message = str(errors[0])
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "Epic not found: epic-local-00001" in message, message
    assert "GitHub issue was created: #812" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 812" in message, message
    assert events == [], events

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([813], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        "token=holder\\npid=222\\nuser=lock-holder\\ncreated_unix=9999999999\\ncreated_iso=2099-01-01\\n",
        encoding="utf-8",
    )

    try:
        app_create_node.create_issue(
            app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                requested_node_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected lock failure after github create")
    except RuntimeError as exc:
        message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_remote_only_fail" in message, message
    assert "create lock acquisition failed" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert "GitHub issue was created: #813" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 813" in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    issue_gateway = _BlockingIssueGateway([814], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    errors = []
    def _run_issue():
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
        except Exception as exc:
            errors.append(exc)

    thread = threading.Thread(target=_run_issue)
    thread.start()
    assert started.wait(timeout=1.0), "issue_create was not called"
    node_repo.records.append(
        _record(
            kind="issue",
            node_id="iss-local-00042",
            title="Competing link",
            path=epic_dir / "issues" / "iss-local-00042-competing-link",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=814,
        )
    )
    release.set()
    thread.join(timeout=5.0)
    assert not thread.is_alive(), "github create thread did not finish"
    assert len(errors) == 1, errors
    message = str(errors[0])
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "github linkage is already linked" in message, message
    assert "github.issue_number=814" in message, message
    assert "GitHub issue was created: #814" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" in message, message
    assert "--epic epic-local-00001" in message, message
    assert "--github-issue 814" in message, message
    assert events == [], events
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert not (epic_dir / "issues" / "iss-00814-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([815], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_FailingTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    try:
        app_create_node.create_issue(
            app_contracts.CreateNodeRequest(
                title="Refresh token",
                slug=None,
                parent_id="epic-local-00001",
                requested_node_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected write seam failure after github create")
    except RuntimeError as exc:
        message = str(exc)
    assert started.is_set(), "issue_create was not called"
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "simulated write seam failure" in message, message
    assert "GitHub issue was created: #815" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00815`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues" / "iss-00815-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([819], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    with patch.object(
        app_create_node,
        "_post_write_duplicate_guard",
        side_effect=RuntimeError("simulated post-write duplicate guard failure"),
    ):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected post-write guard failure after local write commit")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "simulated post-write duplicate guard failure" in message, message
    assert "GitHub issue was created: #819" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00819`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00819-refresh-token" / ".meta.json").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([816], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected cleanup failure after local write success")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_success_cleanup_fail" in message, message
    assert "create lock release failed" in message, message
    assert "GitHub issue was created: #816" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00816`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00816-refresh-token" / ".meta.json").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([817], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_FailingTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
        try:
            app_create_node.create_issue(
                app_contracts.CreateNodeRequest(
                    title="Refresh token",
                    slug=None,
                    parent_id="epic-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected combined body and cleanup failure")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_body_and_cleanup_fail" in message, message
    assert "Primary local failure: simulated write seam failure" in message, message
    assert "Cleanup failure: create lock release failed" in message, message
    assert "GitHub issue was created: #817" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00817`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert "close/cleanup" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert events == [], events
    assert not (epic_dir / "issues" / "iss-00817-refresh-token").exists()

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    events = []
    started = threading.Event()
    release = threading.Event()
    release.set()
    issue_gateway = _BlockingIssueGateway([818], started, release)
    node_repo = _StubNodeRepo(records, events)
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=node_repo,
        template_scaffolder=_StubTemplateScaffolder(events),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=_StubClock(),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )

    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    original_unlink = app_create_node.Path.unlink

    def _unlink_with_failure(path_self, *args, **kwargs):
        if path_self == lock_path:
            raise OSError("permission denied")
        return original_unlink(path_self, *args, **kwargs)

    with patch.object(
        app_create_node,
        "_post_write_duplicate_guard",
        side_effect=RuntimeError("simulated post-write duplicate guard failure"),
    ):
        with patch.object(app_create_node.Path, "unlink", new=_unlink_with_failure):
            try:
                app_create_node.create_issue(
                    app_contracts.CreateNodeRequest(
                        title="Refresh token",
                        slug=None,
                        parent_id="epic-local-00001",
                        requested_node_id=None,
                        github_mode="create",
                        github_issue_number=None,
                    ),
                    ports,
                )
                raise AssertionError("expected post-write guard and cleanup failure")
            except RuntimeError as exc:
                message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_body_and_cleanup_fail" in message, message
    assert "Primary local failure: simulated post-write duplicate guard failure" in message, message
    assert "Cleanup failure: create lock release failed" in message, message
    assert "GitHub issue was created: #818" in message, message
    assert "Create may already have succeeded" in message, message
    assert "Do not rerun blindly" in message, message
    assert "local node `iss-00818`" in message, message
    assert f"{runtime_cmd} doctor" in message, message
    assert f"{runtime_cmd} new issue --title 'Refresh token'" not in message, message
    assert len(issue_gateway.calls) == 1, issue_gateway.calls
    assert (epic_dir / "issues" / "iss-00818-refresh-token" / ".meta.json").exists()
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_issue_create_pre_github_validation_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, %r)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        del dest_dir, record
        raise AssertionError("write_meta should not be called for pure validation failures")

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        del replacements
        return text
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise AssertionError("copy_scaffolded_tree should not be called for pure validation failures")
    def write_text(self, dest_path, text):
        del dest_path, text
        raise AssertionError("write_text should not be called for pure validation failures")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    epic_dir = init_dir / "epics" / "epic-local-00001-jwt-auth"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="JWT auth",
            path=epic_dir,
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    cases = [
        (
            "requested-id-with-github-mode",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-00001",
                "requested_node_id": "iss-local-00100",
            },
            "Cannot combine '--id' with GitHub-backed node creation",
        ),
        (
            "missing-epic",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": None,
                "requested_node_id": None,
            },
            "--epic is required",
        ),
        (
            "partial-repo-identity",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-00001",
                "requested_node_id": None,
                "github_repo_owner": "chemitaro",
                "github_repo_name": None,
            },
            "github_repo_owner and github_repo_name must be provided together",
        ),
        (
            "missing-initiative-node",
            "create_epic",
            {
                "title": "JWT auth",
                "parent_id": "init-local-99999",
                "requested_node_id": None,
            },
            "Initiative not found: init-local-99999",
        ),
        (
            "missing-epic-node",
            "create_issue",
            {
                "title": "Refresh token",
                "parent_id": "epic-local-99999",
                "requested_node_id": None,
            },
            "Epic not found: epic-local-99999",
        ),
    ]
    for case_name, create_attr, overrides, expected_error in cases:
        issue_gateway = _StubIssueGateway([950])
        ports = app_ports.Ports(
            node_reader=_DummyNodeReader(),
            node_repo=_StubNodeRepo(records),
            template_scaffolder=_StubTemplateScaffolder(),
            issue_gateway=issue_gateway,
            git_gateway=_StubGitGateway(),
            clock=None,
            repo_root=repo_root,
            specdock_dir=specdock_dir,
        )
        request_kwargs = {
            "title": "Refresh token",
            "slug": None,
            "parent_id": "epic-local-00001",
            "requested_node_id": None,
            "github_mode": "create",
            "github_issue_number": None,
            "github_repo_owner": None,
            "github_repo_name": None,
        }
        request_kwargs.update(overrides)
        try:
            getattr(app_create_node, create_attr)(app_contracts.CreateNodeRequest(**request_kwargs), ports)
            raise AssertionError(f"expected failure for {case_name}")
        except RuntimeError as exc:
            message = str(exc)
        assert expected_error in message, (case_name, message)
        assert "Outcome: pre_github_fail" in message, (case_name, message)
        assert "GitHub issue was created:" not in message, (case_name, message)
        assert issue_gateway.calls == [], (case_name, issue_gateway.calls)
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_non_issue_create_guidance_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import os
import shlex
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, %r)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")
    rules_root = specdock_dir / "docs" / "rules"
    for scope, filename in (
        ("initiative", "epics.md"),
        ("initiative", "discussions.md"),
        ("epic", "issues.md"),
        ("epic", "discussions.md"),
        ("issue", "discussions.md"),
    ):
        rules_path = rules_root / scope / filename
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(f"# {scope} {filename}\\n", encoding="utf-8")

def _runtime_cmd(specdock_dir):
    return shlex.quote(str((specdock_dir / "scripts" / "spec-dock").resolve()))

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        path = Path(dest_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / ".meta.json").write_text(f"id={record.id}\\n", encoding="utf-8")
        self._records.append(record)

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        created = []
        for src_path in sorted(Path(src_dir).rglob("*"), key=lambda p: p.as_posix()):
            if not src_path.is_file():
                continue
            rel = src_path.relative_to(src_dir)
            dst = Path(dest_dir) / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(self.render_text(src_path.read_text(encoding="utf-8"), replacements), encoding="utf-8")
            created.append(dst)
        return created
    def write_text(self, dest_path, text):
        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    issue_gateway = _StubIssueGateway([960])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo([]),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    lock_path = app_create_node._resolve_create_lock_path(specdock_dir)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(
        "token=holder\\npid=222\\nuser=lock-holder\\ncreated_unix=9999999999\\ncreated_iso=2099-01-01\\n",
        encoding="utf-8",
    )
    os.environ[app_create_node._ENV_CREATE_LOCK_WAIT_SECONDS] = "0.02"
    os.environ[app_create_node._ENV_CREATE_LOCK_POLL_SECONDS] = "0.005"
    os.environ[app_create_node._ENV_CREATE_LOCK_STALE_SECONDS] = "3600"
    try:
        app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Auth platform",
                slug=None,
                parent_id=None,
                requested_node_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected initiative failure")
    except RuntimeError as exc:
        message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_remote_only_fail" in message, message
    assert "GitHub issue was created: #960" in message, message
    assert f"{runtime_cmd} new initiative --title 'Auth platform'" in message, message
    assert "--github-issue 960" in message, message

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)
    init_dir = specdock_dir / "initiatives" / "init-local-00001-auth-platform"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform",
            path=init_dir,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway([961])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo(records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    with patch.object(app_create_node, "execute_create_plan", side_effect=RuntimeError("simulated epic write failure")):
        try:
            app_create_node.create_epic(
                app_contracts.CreateNodeRequest(
                    title="JWT auth",
                    slug=None,
                    parent_id="init-local-00001",
                    requested_node_id=None,
                    github_mode="create",
                    github_issue_number=None,
                ),
                ports,
            )
            raise AssertionError("expected epic failure")
        except RuntimeError as exc:
            message = str(exc)
    runtime_cmd = _runtime_cmd(specdock_dir)
    assert "Outcome: post_github_local_write_fail" in message, message
    assert "GitHub issue was created: #961" in message, message
    assert f"{runtime_cmd} new epic --title 'JWT auth'" in message, message
    assert "--initiative init-local-00001" in message, message
    assert "--github-issue 961" in message, message
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_create_mode_graph_preflight_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = """
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, %r)
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
    )

def _prepare_templates(specdock_dir):
    for kind in ("initiative", "epic", "issue"):
        template_root = specdock_dir / "templates" / kind
        (template_root / "docs").mkdir(parents=True, exist_ok=True)
        (template_root / "README.md").write_text(f"{kind} <INIT_ID> <EPIC_ID> <ISS_ID>\\n", encoding="utf-8")
        (template_root / "docs" / "checklist.md").write_text("owner=<YOUR_NAME> YYYY-MM-DD\\n", encoding="utf-8")

class _DummyNodeReader:
    def load_node_records(self):
        return []

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)
    def write_meta(self, dest_dir, record):
        del dest_dir, record
        raise AssertionError("write_meta should not be called when graph preflight fails")

class _StubTemplateScaffolder:
    def render_text(self, text, replacements):
        del replacements
        return text
    def load_template_text(self, src_path):
        return Path(src_path).read_text(encoding="utf-8")
    def copy_scaffolded_tree(self, src_dir, dest_dir, replacements):
        del src_dir, dest_dir, replacements
        raise AssertionError("copy_scaffolded_tree should not be called when graph preflight fails")
    def write_text(self, dest_path, text):
        del dest_path, text
        raise AssertionError("write_text should not be called when graph preflight fails")

class _StubIssueGateway:
    def __init__(self, numbers):
        self._numbers = list(numbers)
        self.calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return []
    def issue_create(self, repo_root, title, body):
        self.calls.append((str(repo_root), title, body))
        if not self._numbers:
            raise RuntimeError("no issue numbers configured")
        return self._numbers.pop(0)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    _prepare_templates(specdock_dir)

    init_a = specdock_dir / "initiatives" / "init-local-00001-auth-platform-a"
    init_b = specdock_dir / "initiatives" / "init-local-00001-auth-platform-b"
    duplicate_records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform A",
            path=init_a,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Auth platform B",
            path=init_b,
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
    ]

    issue_gateway = _StubIssueGateway([960])
    ports = app_ports.Ports(
        node_reader=_DummyNodeReader(),
        node_repo=_StubNodeRepo(duplicate_records),
        template_scaffolder=_StubTemplateScaffolder(),
        issue_gateway=issue_gateway,
        git_gateway=_StubGitGateway(),
        clock=None,
        repo_root=repo_root,
        specdock_dir=specdock_dir,
    )
    try:
        app_create_node.create_initiative(
            app_contracts.CreateNodeRequest(
                title="Payments",
                slug=None,
                parent_id=None,
                requested_node_id=None,
                github_mode="create",
                github_issue_number=None,
            ),
            ports,
        )
        raise AssertionError("expected graph preflight failure before github create")
    except RuntimeError as exc:
        message = str(exc)
    assert "duplicate id" in message.lower(), message
    assert "Outcome: pre_github_fail" in message, message
    assert "GitHub issue was created:" not in message, message
    assert issue_gateway.calls == [], issue_gateway.calls
""" % str(runtime_scripts_dir)
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_same_repo_index_missing_view_fallback_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": [], "iss-local-00002": ["iss-local-00001"]}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open", "iss-local-00002": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo Scoped",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo-scoped",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Target",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-target",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 301): domain_models.IssueSnapshot(
                issue_number=301,
                state="CLOSED",
                title="Current repo #301",
                labels=["done"],
                updated_at="2026-03-19T00:00:00Z",
                url="https://github.com/current/repo/issues/301",
                repo_owner="current",
                repo_name="repo",
            )
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"

    deps_result = app_check_deps.check_deps(
        app_contracts.CheckDepsRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00002", github_issue_number=None),
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert deps_result.inspection.evaluation.ready is True
    dep_status = deps_result.inspection.issue_statuses["iss-local-00001"]
    assert dep_status.source == "github"
    assert dep_status.effective_status == "done"
    assert len(issue_gateway.view_calls) == 2
    assert all(call[2] == "current/repo" for call in issue_gateway.view_calls)
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_sync_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_manifest_no_migrate(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "main"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        (node_dir / ".meta.json").write_text("{{}}", encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Local issue",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-local",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    _materialize_required_artifacts(records)
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 101): domain_models.IssueSnapshot(
                issue_number=101,
                state="OPEN",
                title="Current #101",
                labels=[],
                updated_at="2026-03-23T00:00:00Z",
                url="https://github.com/current/repo/issues/101",
                repo_owner="current",
                repo_name="repo",
            ),
            ("current/repo", 201): domain_models.IssueSnapshot(
                issue_number=201,
                state="CLOSED",
                title="Current #201",
                labels=["done"],
                updated_at="2026-03-23T00:01:00Z",
                url="https://github.com/current/repo/issues/201",
                repo_owner="current",
                repo_name="repo",
            ),
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    result = app_sync_state.collect_sync_state(
        app_contracts.SyncRequest(
            force=False,
            github_enabled=True,
            issue_limit=10000,
            update_active_from_branch=False,
        ),
        ports,
    )
    init_status = result.issue_statuses["init-local-00001"]
    epic_status = result.issue_statuses["epic-local-00001"]
    assert init_status.source == "github"
    assert init_status.effective_status == "open"
    assert epic_status.source == "github"
    assert epic_status.effective_status == "done"
    assert issue_gateway.view_calls == [
        (str(repo_root), 101, "current/repo"),
        (str(repo_root), 201, "current/repo"),
    ]
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_unscoped_current_repo_fallback_active_deps_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import check_deps as app_check_deps
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import set_active as app_set_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubDepsTopologyReader:
    def load_issue_depends_on_map(self, specdock_dir, graph):
        del specdock_dir, graph
        return infra_contracts.DepsTopologyLoadResult(
            issue_depends_on_map={{"iss-local-00001": []}},
            warnings=[],
        )

class _StubDerivedStateReader:
    def load_cached_issue_status_by_id(self, specdock_dir):
        del specdock_dir
        return {{"iss-local-00001": "open"}}
    def load_cached_issue_last_sync_at_by_id(self, specdock_dir):
        del specdock_dir
        return {{}}

class _StubIssueGateway:
    def __init__(self, snapshots, foreign_snapshots):
        self._snapshots = list(snapshots)
        self._foreign_snapshots = dict(foreign_snapshots)
        self.view_calls = []
    def issue_index(self, repo_root, *, limit):
        del repo_root, limit
        return list(self._snapshots)
    def issue_view_snapshot(self, repo_root, issue_number, *, repo_slug=None):
        self.view_calls.append((str(repo_root), int(issue_number), repo_slug))
        key = (str(repo_slug or ""), int(issue_number))
        return self._foreign_snapshots[key]

class _StubActiveStateStore:
    def load_active_manifest(self, specdock_dir):
        del specdock_dir
        return infra_contracts.ActiveManifestLoadResult(manifest=None, source="none", warnings=[])
    def load_active_issue_id(self, specdock_dir):
        del specdock_dir
        return None
    def snapshot_current_state(self, specdock_dir):
        del specdock_dir
        return {{}}
    def write_active_manifest(self, specdock_dir, manifest):
        del specdock_dir
        return manifest
    def apply_active_pointers(self, specdock_dir, manifest, context_pack_text):
        del specdock_dir, manifest, context_pack_text
    def patch_agent_state_active_fields(self, specdock_dir, manifest):
        del specdock_dir, manifest
    def rollback_to_snapshot(self, specdock_dir, snapshot):
        del specdock_dir, snapshot

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=201,
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Local issue",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-local",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=None,
        ),
    ]
    issue_gateway = _StubIssueGateway(
        snapshots=[],
        foreign_snapshots={{
            ("current/repo", 101): domain_models.IssueSnapshot(
                issue_number=101,
                state="OPEN",
                title="Current #101",
                labels=[],
                updated_at="2026-03-23T00:00:00Z",
                url="https://github.com/current/repo/issues/101",
                repo_owner="current",
                repo_name="repo",
            ),
            ("current/repo", 201): domain_models.IssueSnapshot(
                issue_number=201,
                state="CLOSED",
                title="Current #201",
                labels=["done"],
                updated_at="2026-03-23T00:01:00Z",
                url="https://github.com/current/repo/issues/201",
                repo_owner="current",
                repo_name="repo",
            ),
        }},
    )
    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        deps_topology_reader=_StubDepsTopologyReader(),
        derived_state_reader=_StubDerivedStateReader(),
        issue_gateway=issue_gateway,
        active_state_store=_StubActiveStateStore(),
        git_gateway=_StubGitGateway(),
    )

    set_result = app_set_active.set_active(
        app_contracts.SetActiveRequest(
            target=app_contracts.TargetRef(kind="node_id", node_id="iss-local-00001", github_issue_number=None),
            force=False,
            checkout=False,
            use_github=True,
            issue_limit=10000,
        ),
        ports,
    )
    assert set_result.selection.issue_id == "iss-local-00001"
    assert issue_gateway.view_calls == [
        (str(repo_root), 101, "current/repo"),
        (str(repo_root), 201, "current/repo"),
    ]

    for target_id, expected_status in (
        ("init-local-00001", "open"),
        ("epic-local-00001", "done"),
    ):
        issue_gateway.view_calls.clear()
        deps_result = app_check_deps.check_deps(
            app_contracts.CheckDepsRequest(
                target=app_contracts.TargetRef(kind="node_id", node_id=target_id, github_issue_number=None),
                use_github=True,
                issue_limit=10000,
            ),
            ports,
        )
        target_status = deps_result.inspection.issue_statuses[target_id]
        assert target_status.source == "github"
        assert target_status.effective_status == expected_status
        assert issue_gateway.view_calls == [
            (str(repo_root), 101, "current/repo"),
            (str(repo_root), 201, "current/repo"),
        ]
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_repo_scoped_validation_doctor_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import doctor as app_doctor
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import validate_tree as app_validate_tree
    from spec_dock_runtime.infra import contracts as infra_contracts
finally:
    sys.path.pop(0)

def _record(*, kind, node_id, title, path, parent_id, initiative_id, epic_id, github_issue_number, github_repo_owner=None, github_repo_name=None):
    return infra_contracts.StoredMetaRecord(
        kind=kind,
        id=node_id,
        title=title,
        slug=title.lower().replace(" ", "-"),
        path=path.as_posix(),
        parent_id=parent_id,
        initiative_id=initiative_id,
        epic_id=epic_id,
        github_issue_number=github_issue_number,
        meta_path=(path / ".meta.json").as_posix(),
        github_repo_owner=github_repo_owner,
        github_repo_name=github_repo_name,
    )

class _StubNodeReader:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self):
        return list(self._records)

class _StubNodeRepo:
    def __init__(self, records):
        self._records = list(records)
    def load_node_records(self, specdock_dir):
        del specdock_dir
        return list(self._records)

class _StubGitGateway:
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

def _materialize_required_artifacts(records):
    for record in records:
        node_dir = Path(record.path)
        node_dir.mkdir(parents=True, exist_ok=True)
        meta_payload = {{
            "type": record.kind,
            "id": record.id,
            "title": record.title,
            "slug": record.slug,
        }}
        if record.parent_id is not None:
            meta_payload["parent_id"] = record.parent_id
        if record.initiative_id is not None:
            meta_payload["initiative_id"] = record.initiative_id
        if record.epic_id is not None:
            meta_payload["epic_id"] = record.epic_id
        if record.github_issue_number is not None:
            meta_payload["github"] = {{"issue_number": int(record.github_issue_number)}}
            if record.github_repo_owner is not None and record.github_repo_name is not None:
                meta_payload["github"]["repo_owner"] = record.github_repo_owner
                meta_payload["github"]["repo_name"] = record.github_repo_name
        (node_dir / ".meta.json").write_text(json.dumps(meta_payload, ensure_ascii=False), encoding="utf-8")
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            (node_dir / filename).write_text(f"{{record.id}}:{{filename}}\\n", encoding="utf-8")

with tempfile.TemporaryDirectory() as td:
    repo_root = Path(td)
    specdock_dir = repo_root / "spec-dock"
    specdock_dir.mkdir(parents=True, exist_ok=True)
    records = [
        _record(
            kind="initiative",
            node_id="init-local-00001",
            title="Platform",
            path=specdock_dir / "initiatives" / "init-local-00001-platform",
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=101,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="epic",
            node_id="epic-local-00001",
            title="Delivery",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery",
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=102,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00001",
            title="Current Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00001-current-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        _record(
            kind="issue",
            node_id="iss-local-00002",
            title="Foreign Repo",
            path=specdock_dir / "initiatives" / "init-local-00001-platform" / "epics" / "epic-local-00001-delivery" / "issues" / "iss-local-00002-foreign-repo",
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=301,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
    _materialize_required_artifacts(records)

    ports = app_ports.Ports(
        node_reader=_StubNodeReader(records),
        node_repo=_StubNodeRepo(records),
        repo_root=repo_root,
        specdock_dir=specdock_dir,
        git_gateway=_StubGitGateway(),
    )
    validation = app_validate_tree.validate_tree(app_contracts.ValidateTreeRequest(), ports)
    assert not validation.report.errors, validation.report.errors

    doctor_result = app_doctor.doctor(app_contracts.DoctorRequest(), ports)
    assert doctor_result.ok, doctor_result.findings

    loaded_graph = app_create_node.load_graph(ports, validate=True)
    assert "iss-local-00001" in loaded_graph.nodes_by_id
    assert "iss-local-00002" in loaded_graph.nodes_by_id
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_keeps_numeric_branch_current_repo_overlap_parity(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        runtime_scripts_dir = repo_root / "spec-dock" / "scripts"
        check_code = f"""
import sys
from pathlib import Path

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime.application import contracts as app_contracts
    from spec_dock_runtime.application import ports as app_ports
    from spec_dock_runtime.application import sync_state as app_sync_state
    from spec_dock_runtime.domain import active as domain_active
    from spec_dock_runtime.domain import models as domain_models
    from spec_dock_runtime.domain import tree as domain_tree
finally:
    sys.path.pop(0)

seeds = [
    domain_models.SpecNodeSeed(
        kind="initiative",
        id="init-local-00001",
        title="Platform",
        slug="platform",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
        parent_id=None,
        initiative_id=None,
        epic_id=None,
        github_issue_number=None,
    ),
    domain_models.SpecNodeSeed(
        kind="epic",
        id="epic-local-00001",
        title="Delivery",
        slug="delivery",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
        parent_id="init-local-00001",
        initiative_id="init-local-00001",
        epic_id=None,
        github_issue_number=None,
    ),
    domain_models.SpecNodeSeed(
        kind="issue",
        id="iss-local-00001",
        title="Current issue",
        slug="current-issue",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue/.meta.json"),
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
    ),
    domain_models.SpecNodeSeed(
        kind="issue",
        id="iss-local-00002",
        title="Foreign issue",
        slug="foreign-issue",
        path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue"),
        meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-foreign-issue/.meta.json"),
        parent_id="epic-local-00001",
        initiative_id="init-local-00001",
        epic_id="epic-local-00001",
        github_issue_number=123,
        github_repo_owner="other",
        github_repo_name="repo",
    ),
]
graph = domain_tree.build_graph(seeds)

matched, reason = domain_active.infer_active_node_from_branch(
    graph,
    branch="123-fix-login",
    current_repo_slug="current/repo",
)
assert matched is not None
assert matched.id == "iss-local-00001", matched
assert reason == "matched github.issue_number=123 from branch", reason

unknown_matched, unknown_reason = domain_active.infer_active_node_from_branch(
    graph,
    branch="issue-123",
    current_repo_slug=None,
)
assert unknown_matched is None
assert unknown_reason == "ambiguous github issue numbers [123]: issue:iss-local-00001, issue:iss-local-00002", unknown_reason

foreign_only_graph = domain_tree.build_graph(
    [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Platform",
            slug="platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="Delivery",
            slug="delivery",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Foreign issue",
            slug="foreign-issue",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-foreign-issue/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
)
foreign_only_matched, foreign_only_reason = domain_active.infer_active_node_from_branch(
    foreign_only_graph,
    branch="123-fix-login",
    current_repo_slug="current/repo",
)
assert foreign_only_matched is None
assert (
    foreign_only_reason
    == "no current-repo matches for github issue numbers [123] in scope (current/repo); refusing foreign fallback: issue:iss-local-00001"
), foreign_only_reason

scoped_ambiguity_graph = domain_tree.build_graph(
    [
        domain_models.SpecNodeSeed(
            kind="initiative",
            id="init-local-00001",
            title="Platform",
            slug="platform",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/.meta.json"),
            parent_id=None,
            initiative_id=None,
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="epic",
            id="epic-local-00001",
            title="Delivery",
            slug="delivery",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/.meta.json"),
            parent_id="init-local-00001",
            initiative_id="init-local-00001",
            epic_id=None,
            github_issue_number=None,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00001",
            title="Current issue a",
            slug="current-issue-a",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00001-current-issue-a/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00002",
            title="Current issue b",
            slug="current-issue-b",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00002-current-issue-b/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="current",
            github_repo_name="repo",
        ),
        domain_models.SpecNodeSeed(
            kind="issue",
            id="iss-local-00003",
            title="Foreign issue",
            slug="foreign-issue",
            path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue"),
            meta_path=Path("/repo/spec-dock/initiatives/init-local-00001-platform/epics/epic-local-00001-delivery/issues/iss-local-00003-foreign-issue/.meta.json"),
            parent_id="epic-local-00001",
            initiative_id="init-local-00001",
            epic_id="epic-local-00001",
            github_issue_number=123,
            github_repo_owner="other",
            github_repo_name="repo",
        ),
    ]
)
scoped_ambiguity_matched, scoped_ambiguity_reason = domain_active.infer_active_node_from_branch(
    scoped_ambiguity_graph,
    branch="issue-123",
    current_repo_slug="current/repo",
)
assert scoped_ambiguity_matched is None
assert (
    scoped_ambiguity_reason
    == "ambiguous github issue numbers [123] in current repo scope (current/repo): issue:iss-local-00001, issue:iss-local-00002"
), scoped_ambiguity_reason

class _StubNodeReader:
    def load_node_records(self):
        return []

class _StubGitGateway:
    def current_branch_or_none(self, repo_root):
        del repo_root
        return "123-fix-login"
    def origin_github_repo_slug(self, repo_root):
        del repo_root
        return "current/repo"

ports = app_ports.Ports(
    node_reader=_StubNodeReader(),
    repo_root=Path("/repo"),
    git_gateway=_StubGitGateway(),
    active_state_store=object(),
)
state = app_contracts.SyncStateResult(
    graph=domain_models.SpecGraph(nodes_by_id={{}}),
    active=None,
    issue_statuses={{}},
    progress=domain_models.ProgressMap(by_node_id={{}}, counts={{"total": 0, "done": 0, "open": 0, "unknown": 0}}),
    deps_state=domain_models.DepsState(nodes=[], warnings=[]),
    deps_eval_by_id={{}},
    generated_at="2026-03-23T00:00:00+00:00",
    warnings=[],
    deps_preflight_error=None,
    repo_root=Path("/repo"),
)
observed = {{}}
original_infer = app_sync_state.infer_active_node_from_branch

def _fake_infer(graph, *, branch, current_repo_slug=None):
    del graph
    observed["branch"] = branch
    observed["current_repo_slug"] = current_repo_slug
    return (None, "no branch match")

app_sync_state.infer_active_node_from_branch = _fake_infer
try:
    next_state, outcome = app_sync_state.maybe_auto_update_from_branch(state, ports)
finally:
    app_sync_state.infer_active_node_from_branch = original_infer

assert next_state is state
assert outcome is not None
assert outcome.applied is False
assert outcome.reason == "no branch match"
assert observed == {{"branch": "123-fix-login", "current_repo_slug": "current/repo"}}
"""
        result = subprocess.run(
            [sys.executable, "-c", check_code],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_tool_version_fallback_reads_pyproject(self) -> None:
        import spec_dock.cli as cli

        expected = _expected_spec_dock_version()
        old_version = getattr(cli, "__version__", None)
        old_file = getattr(cli, "__file__", None)
        try:
            cli.__version__ = "0.0.0+unknown"
            repo_root = Path(__file__).resolve().parents[1]
            cli.__file__ = str(repo_root / "src" / "spec_dock" / "cli.py")
            self.assertEqual(cli._tool_version(), expected)
        finally:
            if old_version is not None:
                cli.__version__ = old_version
            if old_file is not None:
                cli.__file__ = old_file

    def test_no_skill_option_is_rejected(self) -> None:
        import spec_dock.cli as cli

        with self.assertRaises(SystemExit) as cm:
            cli._parse_args(["init", "--no-skill", "."])
        self.assertEqual(cm.exception.code, 2)

    def test_update_migrates_legacy_single_skill_and_preserves_custom_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            skills_root = target / ".agents" / "skills"
            meta_path = target / ".agents" / "host-adapters" / "meta.json"
            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                if skill_name == "spec-driven-tdd-workflow":
                    continue
                shutil.rmtree(skills_root / skill_name)
            self._write_text_force(meta_path, '{"schema_version": 99}\n')

            custom_dir = skills_root / "my-custom-skill"
            custom_dir.mkdir(parents=True, exist_ok=True)
            (custom_dir / "SKILL.md").write_text("# custom\n", encoding="utf-8")
            (custom_dir / "notes.txt").write_text("keep\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)
            self.assertEqual(
                json.loads(meta_path.read_text(encoding="utf-8")),
                self._EXPECTED_HOST_ADAPTER_META,
            )
            self.assertTrue((custom_dir / "SKILL.md").is_file())
            self.assertTrue((custom_dir / "notes.txt").is_file())

    def test_update_installs_full_skill_set_for_legacy_no_skill_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            skills_root = target / ".agents" / "skills"

            self.assertEqual(main(["init", str(target)]), 0)
            shutil.rmtree(skills_root)
            self.assertFalse(skills_root.exists())
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

            for skill_name in _EXPECTED_MANAGED_SKILL_NAMES:
                shutil.rmtree(skills_root / skill_name)
            self.assertEqual(list(skills_root.glob("*")), [])
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_update_skill_sync_converges_after_interrupted_run(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            original_copy_file = cli._copy_file
            failed_once = False

            def interrupted_copy(src: Path, dest: Path) -> None:
                nonlocal failed_once
                if (
                    not failed_once
                    and dest.as_posix().endswith("/.agents/skills/spec-dock-epic-planning/SKILL.md")
                ):
                    failed_once = True
                    raise RuntimeError("simulated skill sync interruption")
                original_copy_file(src, dest)

            cli._copy_file = interrupted_copy
            try:
                self.assertEqual(main(["update", str(target)]), 1)
            finally:
                cli._copy_file = original_copy_file

            self.assertTrue(failed_once)
            self.assertEqual(main(["update", str(target)]), 0)
            self._assert_managed_skills_installed(target)

    def test_issue_68_install_root_tree_exists(self) -> None:
        install_root = self._ISSUE_68_INSTALL_ROOT
        self.assertTrue(install_root.is_dir(), f"missing install_root: {install_root}")
        for subtree in (".agents", ".codex", ".github"):
            subtree_path = install_root / subtree
            self.assertTrue(subtree_path.is_dir(), f"missing install_root subtree: {subtree_path}")
        for relative_path in self._ISSUE_68_AUTHORITATIVE_RELATIVE_PATHS:
            asset_path = install_root / relative_path
            self.assertTrue(asset_path.is_file(), f"missing issue-68 authoritative asset: {asset_path}")

    def test_issue_68_authoritative_inventory_paths_are_classified_under_install_root(self) -> None:
        install_root = self._ISSUE_68_INSTALL_ROOT
        classified_paths: set[str] = set()

        for prefix, relative_paths in self._ISSUE_68_CLASSIFICATION_PREFIX_TO_RELATIVE_PATHS.items():
            for relative_path in relative_paths:
                self.assertTrue(
                    relative_path.startswith(prefix),
                    f"issue-68 classification mismatch for {relative_path}; expected prefix {prefix}",
                )
                self.assertTrue(
                    (install_root / relative_path).is_file(),
                    f"missing issue-68 classified authoritative asset: {install_root / relative_path}",
                )
                classified_paths.add(relative_path)

        self.assertEqual(
            classified_paths,
            set(self._ISSUE_68_AUTHORITATIVE_RELATIVE_PATHS),
            "issue-68 authoritative inventory should be fully classified under install_root",
        )

    def test_issue_68_workflow_seed_matches_repo_root_ci_workflow(self) -> None:
        install_root_workflow = self._ISSUE_68_INSTALL_ROOT / ".github/workflows/ci.yml"
        repo_root_workflow = Path(".github/workflows/ci.yml")

        self.assertTrue(
            repo_root_workflow.is_file(),
            f"missing repo-root workflow seed source: {repo_root_workflow}",
        )
        self.assertTrue(
            install_root_workflow.is_file(),
            f"missing issue-68 install_root workflow seed: {install_root_workflow}",
        )
        self.assertEqual(
            install_root_workflow.read_bytes(),
            repo_root_workflow.read_bytes(),
            "install_root workflow seed must be byte-equivalent to repo-root .github/workflows/ci.yml",
        )
        workflow_text = install_root_workflow.read_text(encoding="utf-8")
        self.assertIn("test -f ./spec-dock/scripts/spec-dock", workflow_text)
        self.assertNotIn("test -x ./spec-dock/scripts/spec-dock", workflow_text)
        self.assertIn("python3 ./spec-dock/scripts/spec-dock sync", workflow_text)
        self.assertIn("python3 ./spec-dock/scripts/spec-dock validate", workflow_text)

    def test_issue_68_provider_only_workflow_is_not_shipped_via_install_root(self) -> None:
        repo_root_provider_workflow = Path(".github/workflows/provider-ci.yml")
        install_root_provider_workflow = self._ISSUE_68_INSTALL_ROOT / ".github/workflows/provider-ci.yml"

        self.assertTrue(
            repo_root_provider_workflow.is_file(),
            f"missing repo-root provider-only workflow: {repo_root_provider_workflow}",
        )
        self.assertFalse(
            install_root_provider_workflow.exists(),
            (
                "provider-only workflow must not be shipped in install_root managed assets: "
                f"{install_root_provider_workflow}"
            ),
        )
        workflow_text = repo_root_provider_workflow.read_text(encoding="utf-8")
        self.assertIn("python -m pip install -e .", workflow_text)
        self.assertIn("python -m unittest discover -v", workflow_text)

    def test_issue_68_legacy_codex_skills_tree_is_retired(self) -> None:
        legacy_root = self._ISSUE_68_RETIRED_LEGACY_ROOT
        self.assertFalse(
            legacy_root.exists(),
            f"issue-68 legacy provider tree must be retired from current repo: {legacy_root}",
        )

    def test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        provider_assets_root = repo_root / "src/spec_dock/assets"

        for asset_label, duplicate_boundary in self._ISSUE_68_PROVIDER_DUPLICATE_BOUNDARY.items():
            observed_provider_paths: set[str] = set()
            for search_glob in duplicate_boundary["search_globs"]:
                observed_provider_paths.update(
                    candidate.relative_to(repo_root).as_posix()
                    for candidate in provider_assets_root.rglob(search_glob)
                    if candidate.is_file()
                )
            self.assertEqual(
                sorted(observed_provider_paths),
                sorted(duplicate_boundary["allowed_provider_paths"]),
                f"issue-68 authority inventory boundary mismatch for {asset_label}",
            )

    def test_bundled_skill_assets_cover_managed_manifest(self) -> None:
        import spec_dock.cli as cli

        self.assertEqual(cli._managed_skill_names(), _EXPECTED_MANAGED_SKILL_NAMES)
        with cli._assets_dir() as assets_dir:
            for skill_name in cli._managed_skill_names():
                skill_path = assets_dir / "install_root" / ".agents" / "skills" / skill_name / "SKILL.md"
                self.assertTrue(skill_path.is_file(), f"missing bundled skill asset: {skill_path}")
            self.assertTrue(
                (assets_dir / "install_root" / ".agents" / "host-adapters" / "meta.json").is_file(),
                "missing bundled host adapter metadata asset",
            )
            self.assertTrue(
                (assets_dir / "install_root" / ".codex" / "agents" / "spec-manager.toml").is_file(),
                "missing bundled codex native shim asset",
            )
            self.assertTrue(
                (assets_dir / "install_root" / ".github" / "agents" / "orchestrator.agent.md").is_file(),
                "missing bundled copilot native shim asset",
            )

    def test_bundled_native_shim_assets_satisfy_static_delegation_only_contract(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            codex_path = assets_dir / "install_root" / ".codex" / "agents" / "spec-manager.toml"
            codex_bootstrap_path = assets_dir / "install_root" / ".codex" / "AGENTS.md"
            codex_config_path = assets_dir / "install_root" / ".codex" / "config.toml"
            copilot_spec_manager_path = assets_dir / "install_root" / ".github" / "agents" / "spec-manager.agent.md"
            copilot_path = assets_dir / "install_root" / ".github" / "agents" / "orchestrator.agent.md"
            self.assertTrue(codex_path.is_file(), f"missing bundled codex native shim: {codex_path}")
            self.assertTrue(codex_bootstrap_path.is_file(), f"missing bundled codex bootstrap guide: {codex_bootstrap_path}")
            self.assertTrue(codex_config_path.is_file(), f"missing bundled codex main config: {codex_config_path}")
            self.assertTrue(
                copilot_spec_manager_path.is_file(),
                f"missing bundled copilot spec-manager: {copilot_spec_manager_path}",
            )
            self.assertTrue(copilot_path.is_file(), f"missing bundled copilot native shim: {copilot_path}")
            codex_text = codex_path.read_text(encoding="utf-8")
            codex_bootstrap_text = codex_bootstrap_path.read_text(encoding="utf-8")
            codex_config_text = codex_config_path.read_text(encoding="utf-8")
            copilot_spec_manager_text = copilot_spec_manager_path.read_text(encoding="utf-8")
            copilot_text = copilot_path.read_text(encoding="utf-8")

        self._assert_spec_manager_contract(
            text=codex_text,
            delegation_expected=".agents/skills/spec-dock-codex-adapter/SKILL.md",
            shim_label="bundled codex native shim",
        )
        self._assert_codex_native_shim_loader_contract(
            text=codex_text,
            shim_label="bundled codex native shim",
        )
        self._assert_codex_bootstrap_routing_contract(
            text=codex_bootstrap_text,
            shim_label="bundled codex bootstrap guide",
        )
        self._assert_codex_main_config_routing_contract(
            text=codex_config_text,
            shim_label="bundled codex main config",
        )
        self._assert_spec_manager_contract(
            text=copilot_spec_manager_text,
            delegation_expected=".agents/skills/spec-dock-copilot-adapter/SKILL.md",
            shim_label="bundled copilot spec-manager",
        )
        self._assert_copilot_spec_manager_contract(
            text=copilot_spec_manager_text,
            shim_label="bundled copilot spec-manager",
        )
        self._assert_copilot_orchestrator_contract(
            text=copilot_text,
            shim_label="bundled copilot orchestrator",
        )

    def test_bundled_skill_routing_contract(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            skills_dir = assets_dir / "install_root" / ".agents" / "skills"
            hub_text = (skills_dir / "spec-driven-tdd-workflow" / "SKILL.md").read_text(encoding="utf-8")
            initiative_text = (skills_dir / "spec-dock-initiative-planning" / "SKILL.md").read_text(encoding="utf-8")
            epic_text = (skills_dir / "spec-dock-epic-planning" / "SKILL.md").read_text(encoding="utf-8")
            issue_text = (skills_dir / "spec-dock-issue-execution" / "SKILL.md").read_text(encoding="utf-8")
            adr_text = (skills_dir / "spec-dock-adr-facilitation" / "SKILL.md").read_text(encoding="utf-8")
            codex_adapter_text = (skills_dir / "spec-dock-codex-adapter" / "SKILL.md").read_text(
                encoding="utf-8"
            )
            copilot_adapter_text = (skills_dir / "spec-dock-copilot-adapter" / "SKILL.md").read_text(
                encoding="utf-8"
            )

        self.assertIn(
            "`spec-dock-initiative-planning`: initiative-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-epic-planning`: epic-level requirement/design/plan planning.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-issue-execution`: issue-level TDD execution and report updates.",
            hub_text,
        )
        self.assertIn(
            "`spec-dock-adr-facilitation`: ADR drafting/decision facilitation linked to the current workflow.",
            hub_text,
        )
        self.assertIn("`spec-dock/docs/reference_github.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", hub_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", hub_text)
        self.assertIn("`spec-dock/active/context-pack.md`", hub_text)
        self.assertIn("issue-00049", codex_adapter_text)
        self.assertIn("spec-dock/docs/workflow_issue.md", codex_adapter_text)
        self.assertIn("thin", codex_adapter_text.lower())
        self.assertIn("issue-00049", copilot_adapter_text)
        self.assertIn("spec-dock/docs/workflow_issue.md", copilot_adapter_text)
        self.assertIn("thin", copilot_adapter_text.lower())

        for skill_text in (hub_text, issue_text, codex_adapter_text, copilot_adapter_text):
            self.assertIn("./spec-dock/scripts/spec-dock", skill_text)
            self.assertNotIn("./spec ", skill_text)

        self.assertIn("./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>", issue_text)
        self.assertIn("./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>", issue_text)
        self.assertIn("./spec-dock/scripts/spec-dock deps check <target>", issue_text)
        self.assertIn("./spec-dock/scripts/spec-dock validate", issue_text)
        self.assertIn("./spec-dock/scripts/spec-dock sync", issue_text)
        self.assertIn("--no-github", issue_text)

        for skill_text in (hub_text, codex_adapter_text, copilot_adapter_text):
            self.assertNotIn("./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock deps check <target>", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock validate", skill_text)
            self.assertNotIn("./spec-dock/scripts/spec-dock sync", skill_text)

        self.assertIn("`spec-dock/docs/reference_deps.md`", codex_adapter_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", codex_adapter_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", copilot_adapter_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", copilot_adapter_text)

        self.assertIn("`spec-dock/docs/workflow_initiative.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", initiative_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", initiative_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", initiative_text)
        self.assertIn("create/import an initiative", initiative_text)
        self.assertIn("scope-specific constraints and decisions", initiative_text)

        self.assertIn("`spec-dock/docs/workflow_epic.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", epic_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", epic_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", epic_text)
        self.assertIn("create/import an epic", epic_text)
        self.assertIn("scope-specific constraints and decisions", epic_text)
        self.assertIn("`spec-dock/docs/workflow_issue.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_deps.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_sync.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_github.md`", issue_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_requirement.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_design.md`", issue_text)
        self.assertIn("`spec-dock/docs/phase_plan.md`", issue_text)
        self.assertIn("`spec-dock/active/context-pack.md`", issue_text)
        self.assertIn("approved behavior-slice execution", issue_text)
        self.assertIn("source of truth", issue_text)
        self.assertIn("docs impact resolution step", issue_text)
        self.assertIn("final diff review quality gate", issue_text)

        self.assertIn("`spec-dock/docs/workflow_adr.md`", adr_text)
        self.assertIn("`spec-dock/docs/reference_naming.md`", adr_text)
        self.assertIn("Return to the current parent workflow", adr_text)
        self.assertIn("create/update an ADR", adr_text)

        for skill_text in (hub_text, initiative_text, epic_text, issue_text, adr_text):
            self.assertNotIn("runtime-operations", skill_text)

    def test_init_installs_host_adapter_metadata_with_fixed_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            meta_path = target / ".agents" / "host-adapters" / "meta.json"
            self.assertTrue(meta_path.is_file(), f"missing host adapter metadata: {meta_path}")
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertEqual(meta, self._EXPECTED_HOST_ADAPTER_META)

    def test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            plan = cli._build_managed_skill_install_plan(Path(assets_dir))
            install_root = Path(assets_dir) / "install_root"
            expected_inventory = {
                candidate.relative_to(install_root).as_posix()
                for candidate in install_root.rglob("*")
                if candidate.is_file()
            }

        managed_targets = {
            mapping.target_rel.as_posix() for mapping in plan.current_file_mappings
        }
        self.assertEqual(managed_targets, expected_inventory)
        self.assertIn(".github/workflows/ci.yml", managed_targets)
        self.assertEqual(
            {
                mapping.source_asset_rel.as_posix()
                for mapping in plan.current_file_mappings
            },
            {f"install_root/{rel_path}" for rel_path in expected_inventory},
        )

    def test_issue_70_update_rejects_missing_or_invalid_managed_assets_obsolete_manifest(self) -> None:
        cases = (
            ("missing_managed_assets", "invalid managed_assets contract"),
            ("null_managed_assets", "invalid managed_assets contract"),
            ("missing_obsolete_exact_file_paths", "invalid managed_assets.obsolete_exact_file_paths"),
            ("null_obsolete_exact_file_paths", "invalid managed_assets.obsolete_exact_file_paths"),
            ("non_list_obsolete_exact_file_paths", "invalid managed_assets.obsolete_exact_file_paths"),
        )
        for case_name, expected_error in cases:
            with self.subTest(case_name=case_name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))

                    if case_name == "missing_managed_assets":
                        malformed_manifest.pop("managed_assets")
                    elif case_name == "null_managed_assets":
                        malformed_manifest["managed_assets"] = None
                    elif case_name == "missing_obsolete_exact_file_paths":
                        malformed_manifest["managed_assets"].pop("obsolete_exact_file_paths")
                    elif case_name == "null_obsolete_exact_file_paths":
                        malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = None
                    elif case_name == "non_list_obsolete_exact_file_paths":
                        malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = (
                            ".codex/agents/spec-dock-codex-adapter.toml"
                        )
                    else:
                        raise AssertionError(f"unknown case_name: {case_name}")

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn(expected_error, stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_70_update_rejects_current_obsolete_overlap_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                ".agents/host-adapters/meta.json"
            ]

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "managed_assets.obsolete_exact_file_paths overlaps current managed path "
                "'.agents/host-adapters/meta.json'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_70_init_rejects_current_managed_directory_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "README.md").write_text("preflight-marker\n", encoding="utf-8")
            conflicting_path = target / ".github" / "workflows" / "ci.yml"
            conflicting_path.mkdir(parents=True, exist_ok=True)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")
            self.assertEqual(
                (target / "README.md").read_text(encoding="utf-8"),
                "preflight-marker\n",
            )

    def test_issue_70_init_rejects_current_managed_container_file_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / ".github").write_text("container-file-conflict\n", encoding="utf-8")

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/agents/",
                stderr,
            )
            self.assertIn("non-directory container: '.github'", stderr)
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")

    def test_issue_70_init_rejects_current_managed_symlink_parent_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            (target / "README.md").write_text("preflight-marker\n", encoding="utf-8")
            workflows_parent = target / ".github" / "workflows"
            workflows_parent.parent.mkdir(parents=True, exist_ok=True)
            (target / "symlink-workflows-container").mkdir(parents=True, exist_ok=True)
            os.symlink("../symlink-workflows-container", workflows_parent)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self.assertIn("symlink container: '.github/workflows'", stderr)
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "preflight-marker\n")

    def test_issue_70_init_rejects_current_managed_symlink_exact_file_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            (target / "README.md").write_text("preflight-marker\n", encoding="utf-8")
            managed_workflow_path = target / ".github" / "workflows" / "ci.yml"
            managed_workflow_path.parent.mkdir(parents=True, exist_ok=True)

            symlink_target = target / "symlink-ci-target.yml"
            symlink_target.write_text("managed-workflow-symlink-target\n", encoding="utf-8")
            os.symlink("../../symlink-ci-target.yml", managed_workflow_path)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self.assertIn("symlink at exact file path", stderr)
            self.assertTrue(managed_workflow_path.is_symlink())
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "preflight-marker\n")
            self.assertEqual(symlink_target.read_text(encoding="utf-8"), "managed-workflow-symlink-target\n")

    def test_issue_70_update_rejects_current_managed_directory_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            managed_workflow_path = target / ".github" / "workflows" / "ci.yml"
            managed_workflow_path.unlink(missing_ok=True)
            managed_workflow_path.mkdir(parents=True, exist_ok=True)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_70_update_rejects_current_managed_symlink_parent_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)

            workflows_parent = target / ".github" / "workflows"
            if workflows_parent.is_symlink() or workflows_parent.is_file():
                workflows_parent.unlink(missing_ok=True)
            elif workflows_parent.exists():
                shutil.rmtree(workflows_parent)
            (target / "symlink-workflows-container").mkdir(parents=True, exist_ok=True)
            os.symlink("../symlink-workflows-container", workflows_parent)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self.assertIn("symlink container: '.github/workflows'", stderr)
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_70_update_rejects_current_managed_symlink_exact_file_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)

            managed_workflow_path = target / ".github" / "workflows" / "ci.yml"
            managed_workflow_path.unlink(missing_ok=True)
            symlink_target = target / "symlink-ci-target.yml"
            symlink_target.write_text("managed-workflow-symlink-target\n", encoding="utf-8")
            os.symlink("../../symlink-ci-target.yml", managed_workflow_path)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.github/workflows/ci.yml'",
                stderr,
            )
            self.assertIn("symlink at exact file path", stderr)
            self.assertTrue(managed_workflow_path.is_symlink())
            self.assertEqual(symlink_target.read_text(encoding="utf-8"), "managed-workflow-symlink-target\n")
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_75_init_allows_bootstrap_only_exact_file_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            bootstrap_path = target / ".codex" / "config.toml"
            bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
            symlink_target = target / "bootstrap-config-target.toml"
            symlink_target.write_text("# bootstrap symlink target\n", encoding="utf-8")
            os.symlink("../bootstrap-config-target.toml", bootstrap_path)

            exit_code = main(["init", str(target)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((target / "spec-dock").is_dir(), "init should complete when bootstrap-only symlink points to file")
            self.assertTrue(bootstrap_path.is_symlink(), "bootstrap-only path should remain a symlink")
            self.assertEqual(
                symlink_target.read_text(encoding="utf-8"),
                "# bootstrap symlink target\n",
                "init must preserve existing bootstrap-only symlink target content",
            )

    def test_issue_75_update_allows_bootstrap_only_exact_file_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            bootstrap_path = target / ".codex" / "config.toml"
            bootstrap_path.unlink(missing_ok=True)
            symlink_target = target / "bootstrap-config-update-target.toml"
            symlink_target.write_text("# bootstrap update symlink target\n", encoding="utf-8")
            os.symlink("../bootstrap-config-update-target.toml", bootstrap_path)

            exit_code = main(["update", str(target)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(bootstrap_path.is_symlink(), "update should keep bootstrap-only path as symlink")
            self.assertEqual(
                symlink_target.read_text(encoding="utf-8"),
                "# bootstrap update symlink target\n",
                "update must preserve existing bootstrap-only symlink target content",
            )

    def test_issue_75_init_rejects_bootstrap_only_broken_symlink_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            (target / "README.md").write_text("preflight-marker\n", encoding="utf-8")
            bootstrap_path = target / ".codex" / "config.toml"
            bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
            os.symlink("../missing-bootstrap-config.toml", bootstrap_path)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.codex/config.toml'",
                stderr,
            )
            self.assertIn("symlink at exact file path", stderr)
            self.assertTrue(bootstrap_path.is_symlink())
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "preflight-marker\n")

    def test_issue_75_init_rejects_bootstrap_only_non_file_symlink_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            (target / "README.md").write_text("preflight-marker\n", encoding="utf-8")
            bootstrap_path = target / ".codex" / "config.toml"
            bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
            symlink_target_dir = target / "bootstrap-config-dir"
            symlink_target_dir.mkdir(parents=True, exist_ok=True)
            os.symlink("../bootstrap-config-dir", bootstrap_path)

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["init", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for current managed path '.codex/config.toml'",
                stderr,
            )
            self.assertIn("symlink at exact file path", stderr)
            self.assertTrue(bootstrap_path.is_symlink())
            self.assertFalse((target / "spec-dock").exists(), "conflict preflight must fail before scaffold writes")
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "preflight-marker\n")

    def test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)

            obsolete_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            obsolete_workflow.mkdir(parents=True, exist_ok=True)

            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                *malformed_manifest["managed_assets"]["obsolete_exact_file_paths"],
                ".github/workflows/spec-dock-close.yml",
            ]
            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "target directory/container conflict for obsolete managed path '.github/workflows/spec-dock-close.yml'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_issue_70_update_prunes_obsolete_managed_symlink_exact_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)

            obsolete_target = target / ".codex" / "agents" / "spec-dock-codex-adapter.toml"
            obsolete_target.parent.mkdir(parents=True, exist_ok=True)
            symlink_target = target / "obsolete-managed-symlink-target.toml"
            symlink_target.write_text("obsolete symlink target\n", encoding="utf-8")
            os.symlink("../../obsolete-managed-symlink-target.toml", obsolete_target)
            self.assertTrue(obsolete_target.is_symlink())

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 0, stderr)
            self.assertFalse(obsolete_target.exists())
            self.assertFalse(obsolete_target.is_symlink())
            self.assertEqual(
                symlink_target.read_text(encoding="utf-8"),
                "obsolete symlink target\n",
            )

    def test_issue_70_update_prunes_obsolete_managed_symlink_to_directory_exact_file_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)

            obsolete_target = target / ".codex" / "agents" / "spec-dock-codex-adapter.toml"
            obsolete_target.parent.mkdir(parents=True, exist_ok=True)
            symlink_target_dir = target / "obsolete-managed-symlink-dir"
            symlink_target_dir.mkdir(parents=True, exist_ok=True)
            symlink_target_file = symlink_target_dir / "keep.txt"
            symlink_target_file.write_text("keep me\n", encoding="utf-8")
            os.symlink("../../obsolete-managed-symlink-dir", obsolete_target)
            self.assertTrue(obsolete_target.is_symlink())

            err = io.StringIO()
            with redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 0, stderr)
            self.assertFalse(obsolete_target.exists())
            self.assertFalse(obsolete_target.is_symlink())
            self.assertEqual(
                symlink_target_file.read_text(encoding="utf-8"),
                "keep me\n",
            )

    def test_issue_70_update_syncs_workflow_and_prunes_obsolete_exact_workflow_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            expected_workflow = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".github"
                / "workflows"
                / "ci.yml"
            ).read_bytes()
            managed_workflow = target / ".github" / "workflows" / "ci.yml"
            obsolete_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            custom_workflow = target / ".github" / "workflows" / "custom-review.yml"

            stale_workflow = b"name: stale managed workflow\n"
            custom_workflow_text = "name: custom workflow\n"
            self._write_text_force(managed_workflow, stale_workflow.decode("utf-8"))
            self._write_text_force(obsolete_workflow, "name: obsolete workflow\n")
            self._write_text_force(custom_workflow, custom_workflow_text)

            manifest_override = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            manifest_override["managed_assets"]["obsolete_exact_file_paths"] = [
                *manifest_override["managed_assets"]["obsolete_exact_file_paths"],
                ".github/workflows/spec-dock-close.yml",
            ]
            exit_code, _stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                manifest_override,
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(managed_workflow.is_file(), f"missing managed workflow after update: {managed_workflow}")
            self.assertEqual(managed_workflow.read_bytes(), expected_workflow)
            self.assertNotEqual(managed_workflow.read_bytes(), stale_workflow)
            self.assertFalse(obsolete_workflow.exists(), "obsolete exact workflow path must be pruned")
            self.assertTrue(custom_workflow.is_file(), f"missing custom workflow after update: {custom_workflow}")
            self.assertEqual(custom_workflow.read_text(encoding="utf-8"), custom_workflow_text)

    def test_issue_70_update_skips_obsolete_cleanup_when_post_sync_verify_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            workflow_path = target / ".github" / "workflows" / "ci.yml"
            workflow_path.unlink(missing_ok=True)
            obsolete_codex_path = target / ".codex" / "agents" / "spec-dock-codex-adapter.toml"
            self._write_text_force(obsolete_codex_path, "obsolete should survive verify failure\n")

            original_copy_file = cli._copy_file

            def _copy_file_without_workflow(src: Path, dest: Path) -> None:
                if src.as_posix().endswith("install_root/.github/workflows/ci.yml"):
                    return
                original_copy_file(src, dest)

            err = io.StringIO()
            with patch("spec_dock.cli._copy_file", side_effect=_copy_file_without_workflow), redirect_stderr(err):
                exit_code = main(["update", str(target)])
            stderr = err.getvalue()

            self.assertEqual(exit_code, 1)
            self.assertIn("managed current sync incomplete (missing target): .github/workflows/ci.yml", stderr)
            self.assertTrue(
                obsolete_codex_path.is_file(),
                "obsolete cleanup must be skipped when current sync verification fails",
            )

    def test_issue_70_update_reflection_ignores_legacy_codex_skills_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            expected_adapter_skill = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".agents"
                / "skills"
                / "spec-dock-codex-adapter"
                / "SKILL.md"
            ).read_bytes()
            expected_codex_shim = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".codex"
                / "agents"
                / "spec-manager.toml"
            ).read_bytes()

            def _mutate_assets(patched_assets_root: Path) -> None:
                legacy_skill = patched_assets_root / "codex_skills" / "spec-dock-codex-adapter" / "SKILL.md"
                legacy_shim = patched_assets_root / "codex_skills" / "native-shims" / "spec-dock.toml"
                legacy_meta = patched_assets_root / "codex_skills" / "host-adapters" / "meta.json"
                legacy_skill.parent.mkdir(parents=True, exist_ok=True)
                legacy_shim.parent.mkdir(parents=True, exist_ok=True)
                legacy_meta.parent.mkdir(parents=True, exist_ok=True)

                legacy_skill.write_text(
                    "# legacy stale adapter duplicate\n",
                    encoding="utf-8",
                )
                legacy_shim.write_text(
                    "name = \"legacy-stale-codex\"\n",
                    encoding="utf-8",
                )
                legacy_meta.write_text(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "owner": "legacy-owner",
                            "targets": {},
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )

            exit_code, _stderr = self._run_command_with_assets_override(
                "update",
                target,
                _mutate_assets,
            )
            self.assertEqual(exit_code, 0)
            self.assertEqual(
                (target / ".agents" / "skills" / "spec-dock-codex-adapter" / "SKILL.md").read_bytes(),
                expected_adapter_skill,
            )
            self.assertEqual(
                (target / ".codex" / "agents" / "spec-manager.toml").read_bytes(),
                expected_codex_shim,
            )
            self.assertEqual(
                json.loads((target / ".agents" / "host-adapters" / "meta.json").read_text(encoding="utf-8")),
                self._EXPECTED_HOST_ADAPTER_META,
            )

    def test_issue_70_provider_transition_detects_removed_current_paths_without_obsolete_coverage(self) -> None:
        repo_assets_root = Path(__file__).resolve().parents[1] / "src" / "spec_dock" / "assets"
        previous_plan = self._build_managed_skill_install_plan_from_assets_root(repo_assets_root)

        with tempfile.TemporaryDirectory() as tmp_assets:
            patched_assets_root = Path(tmp_assets) / "assets"
            shutil.copytree(repo_assets_root, patched_assets_root)
            removed_workflow_rel = Path(".github") / "workflows" / "ci.yml"
            (patched_assets_root / "install_root" / removed_workflow_rel).unlink()

            current_plan = self._build_managed_skill_install_plan_from_assets_root(patched_assets_root)

        missing_coverage = self._issue_70_missing_transition_coverage(
            previous_plan=previous_plan,
            current_plan=current_plan,
        )
        self.assertEqual(
            missing_coverage,
            {removed_workflow_rel.as_posix()},
            "removed current managed paths must be covered by obsolete manifest or ownership transfer",
        )

    def test_issue_70_provider_transition_accepts_removed_current_paths_with_obsolete_coverage(self) -> None:
        repo_assets_root = Path(__file__).resolve().parents[1] / "src" / "spec_dock" / "assets"
        previous_plan = self._build_managed_skill_install_plan_from_assets_root(repo_assets_root)

        with tempfile.TemporaryDirectory() as tmp_assets:
            patched_assets_root = Path(tmp_assets) / "assets"
            shutil.copytree(repo_assets_root, patched_assets_root)
            removed_workflow_rel = Path(".github") / "workflows" / "ci.yml"
            (patched_assets_root / "install_root" / removed_workflow_rel).unlink()
            patched_manifest_path = (
                patched_assets_root / "install_root" / ".agents" / "host-adapters" / "meta.json"
            )
            patched_manifest = json.loads(patched_manifest_path.read_text(encoding="utf-8"))
            patched_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                *patched_manifest["managed_assets"]["obsolete_exact_file_paths"],
                removed_workflow_rel.as_posix(),
            ]
            patched_manifest_path.write_text(
                json.dumps(patched_manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            current_plan = self._build_managed_skill_install_plan_from_assets_root(patched_assets_root)

        missing_coverage = self._issue_70_missing_transition_coverage(
            previous_plan=previous_plan,
            current_plan=current_plan,
        )
        self.assertEqual(missing_coverage, set())

    def test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir(parents=True, exist_ok=True)
            target_repo = temp_root / "consumer-repo"
            target_repo.mkdir(parents=True, exist_ok=True)

            venv_python = self._issue_69_prepare_isolated_installed_wheel_runtime(
                repo_root=repo_root,
                temp_root=temp_root,
            )
            spec_dock_command = self._issue_69_venv_spec_dock(venv_python)
            self.assertTrue(
                spec_dock_command.is_file(),
                f"issue-70 expected installed spec-dock command in isolated venv: {spec_dock_command}",
            )

            runtime_snapshot = self._issue_69_collect_isolated_installed_runtime_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=runtime_snapshot,
                repo_root=repo_root,
            )
            plan_snapshot = self._issue_70_collect_isolated_installed_plan_snapshot(
                venv_python=venv_python,
                cwd=isolated_cwd,
            )

            installed_assets_dir = Path(str(runtime_snapshot.get("assets_dir", ""))).resolve()
            self.assertEqual(
                Path(str(plan_snapshot.get("assets_dir", ""))).resolve(),
                installed_assets_dir,
                "issue-70 installed plan snapshot should resolve from the same installed assets root",
            )

            current_targets = {str(path) for path in plan_snapshot.get("current_targets", [])}
            current_sources = {str(path) for path in plan_snapshot.get("current_sources", [])}
            obsolete_targets = {str(path) for path in plan_snapshot.get("obsolete_targets", [])}
            self.assertTrue(current_sources, "issue-70 installed plan must expose current managed sources")
            self.assertTrue(
                all(source.startswith("install_root/") for source in current_sources),
                "issue-70 installed plan should source current managed files from install_root only",
            )
            self.assertFalse(
                any("codex_skills" in source for source in current_sources),
                "issue-70 installed plan should not source current managed files from legacy codex_skills",
            )
            for required_target in (
                ".agents/skills/spec-dock-codex-adapter/SKILL.md",
                ".agents/host-adapters/meta.json",
                ".codex/config.toml",
                ".codex/agents/spec-manager.toml",
                ".github/agents/orchestrator.agent.md",
                ".github/workflows/ci.yml",
            ):
                self.assertIn(
                    required_target,
                    current_targets,
                    f"issue-70 installed plan is missing required managed target: {required_target}",
                )
            self.assertNotIn(
                ".codex/agents/orchestrator.toml",
                current_targets,
                "issue-70 installed plan should not generate codex direct orchestrator target",
            )
            self.assertIn(
                ".codex/agents/spec-dock-codex-adapter.toml",
                obsolete_targets,
                "issue-70 installed plan missing obsolete managed codex shim target",
            )
            self.assertIn(
                ".github/agents/spec-dock-copilot-adapter.agent.md",
                obsolete_targets,
                "issue-70 installed plan missing obsolete managed copilot shim target",
            )

            install_root = installed_assets_dir / "install_root"
            managed_rel_paths = (
                ".agents/skills/spec-dock-codex-adapter/SKILL.md",
                ".agents/host-adapters/meta.json",
                ".codex/agents/spec-manager.toml",
                ".github/agents/orchestrator.agent.md",
                ".github/workflows/ci.yml",
            )
            bootstrap_only_rel_path = ".codex/config.toml"
            expected_managed_bytes = {
                rel_path: (install_root / rel_path).read_bytes() for rel_path in managed_rel_paths
            }
            expected_bootstrap_only_bytes = (install_root / bootstrap_only_rel_path).read_bytes()

            legacy_skill_duplicate = (
                installed_assets_dir / "codex_skills" / "spec-dock-codex-adapter" / "SKILL.md"
            )
            legacy_native_shim_duplicate = (
                installed_assets_dir / "codex_skills" / "native-shims" / "spec-dock.toml"
            )
            legacy_meta_duplicate = installed_assets_dir / "codex_skills" / "host-adapters" / "meta.json"
            legacy_skill_duplicate.parent.mkdir(parents=True, exist_ok=True)
            legacy_native_shim_duplicate.parent.mkdir(parents=True, exist_ok=True)
            legacy_meta_duplicate.parent.mkdir(parents=True, exist_ok=True)
            legacy_skill_duplicate.write_text("# issue-70 stale legacy skill duplicate\n", encoding="utf-8")
            legacy_native_shim_duplicate.write_text("name = \"issue-70-legacy-stale\"\n", encoding="utf-8")
            legacy_meta_duplicate.write_text("{ invalid legacy duplicate json\n", encoding="utf-8")

            runtime_env = self._issue_69_runtime_env_without_checkout_fallback()
            self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "init", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )

            for rel_path, expected_bytes in expected_managed_bytes.items():
                target_path = target_repo / rel_path
                self.assertTrue(target_path.is_file(), f"missing managed file after isolated init: {target_path}")
                self.assertEqual(
                    target_path.read_bytes(),
                    expected_bytes,
                    f"isolated init did not reflect installed install_root asset for: {rel_path}",
                )
            bootstrap_only_target = target_repo / bootstrap_only_rel_path
            self.assertTrue(
                bootstrap_only_target.is_file(),
                f"missing bootstrap-only file after isolated init: {bootstrap_only_target}",
            )
            self.assertEqual(
                bootstrap_only_target.read_bytes(),
                expected_bootstrap_only_bytes,
                "isolated init did not copy bootstrap-only codex config from install_root",
            )

            for rel_path in managed_rel_paths:
                self._write_text_force(target_repo / rel_path, f"issue-70 stale managed payload: {rel_path}\n")
            bootstrap_only_custom_text = "# issue-70 user edited codex config must survive update\n"
            self._write_text_force(bootstrap_only_target, bootstrap_only_custom_text)

            obsolete_paths = (
                ".codex/agents/spec-dock.toml",
                ".github/agents/spec-dock.agent.md",
                ".codex/agents/spec-dock-codex-adapter.toml",
                ".github/agents/spec-dock-copilot-adapter.agent.md",
            )
            for rel_path in obsolete_paths:
                obsolete_path = target_repo / rel_path
                obsolete_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(obsolete_path, f"issue-70 obsolete payload: {rel_path}\n")

            custom_paths = {
                ".agents/skills/custom-reviewer/SKILL.md": "# custom skill must survive update\n",
                ".codex/agents/custom-reviewer.toml": "name = \"custom-reviewer\"\n",
                ".github/workflows/custom-review.yml": "name: custom workflow must survive update\n",
            }
            for rel_path, text in custom_paths.items():
                custom_path = target_repo / rel_path
                custom_path.parent.mkdir(parents=True, exist_ok=True)
                self._write_text_force(custom_path, text)

            self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "update", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )

            for rel_path, expected_bytes in expected_managed_bytes.items():
                target_path = target_repo / rel_path
                self.assertTrue(target_path.is_file(), f"missing managed file after isolated update: {target_path}")
                self.assertEqual(
                    target_path.read_bytes(),
                    expected_bytes,
                    f"isolated update did not reflect installed install_root asset for: {rel_path}",
                )
            self.assertEqual(
                bootstrap_only_target.read_text(encoding="utf-8"),
                bootstrap_only_custom_text,
                "isolated update should preserve user-edited bootstrap-only codex config",
            )
            self.assertFalse(
                (target_repo / ".codex/agents/orchestrator.toml").exists(),
                "isolated update should not generate codex direct orchestrator",
            )

            for rel_path in obsolete_paths:
                self.assertFalse(
                    (target_repo / rel_path).exists(),
                    f"isolated update should prune obsolete managed path: {rel_path}",
                )

            for rel_path, expected_text in custom_paths.items():
                custom_path = target_repo / rel_path
                self.assertTrue(
                    custom_path.is_file(),
                    f"isolated update removed custom managed-outside file: {rel_path}",
                )
                self.assertEqual(
                    custom_path.read_text(encoding="utf-8"),
                    expected_text,
                    f"isolated update mutated custom managed-outside file: {rel_path}",
                )

    def test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        install_root = repo_root / "src" / "spec_dock" / "assets" / "install_root"
        mirrored_prefixes = (
            Path(".agents/host-adapters/meta.json"),
            Path(".agents/skills"),
            Path(".codex"),
            Path(".github/agents"),
            Path(".github/workflows/ci.yml"),
        )
        provider_rel_paths: set[str] = set()
        checked_in_rel_paths: set[str] = set()

        for rel_prefix in mirrored_prefixes:
            provider_prefix_path = install_root / rel_prefix
            checked_in_prefix_path = repo_root / rel_prefix

            if provider_prefix_path.is_file():
                provider_rel_paths.add(rel_prefix.as_posix())
            else:
                self.assertTrue(
                    provider_prefix_path.is_dir(),
                    f"issue-71 missing provider parity directory: {provider_prefix_path}",
                )
                provider_rel_paths.update(
                    path.relative_to(install_root).as_posix()
                    for path in provider_prefix_path.rglob("*")
                    if path.is_file()
                )

            if checked_in_prefix_path.is_file():
                checked_in_rel_paths.add(rel_prefix.as_posix())
            else:
                self.assertTrue(
                    checked_in_prefix_path.is_dir(),
                    f"issue-71 missing checked-in parity directory: {checked_in_prefix_path}",
                )
                checked_in_rel_paths.update(
                    path.relative_to(repo_root).as_posix()
                    for path in checked_in_prefix_path.rglob("*")
                    if path.is_file()
                )

        self.assertEqual(
            checked_in_rel_paths,
            provider_rel_paths,
            "issue-71 checked-in host-pack parity file inventory diverged from install_root",
        )

        for rel_path in sorted(provider_rel_paths):
            with self.subTest(rel_path=rel_path):
                checked_in_path = repo_root / rel_path
                provider_asset_path = install_root / rel_path
                self.assertEqual(
                    checked_in_path.read_bytes(),
                    provider_asset_path.read_bytes(),
                    (
                        "issue-71 checked-in agent-tooling parity diverged from install_root asset: "
                        f"{rel_path}"
                    ),
                )

    def test_issue_75_pr_monitor_guidance_uses_repo_relative_helper_path(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expected_helper_path = (
            "./.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh"
        )
        legacy_helper_path = (
            "/srv/mount/.codex/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh"
        )
        guidance_files = (
            "src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml",
            "src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md",
            ".codex/agents/pr-monitor.toml",
            ".github/agents/pr-monitor.agent.md",
        )

        for rel_path in guidance_files:
            with self.subTest(rel_path=rel_path):
                content = (repo_root / rel_path).read_text(encoding="utf-8")
                self.assertIn(
                    expected_helper_path,
                    content,
                    f"issue-75 guidance missing repo-relative helper path in: {rel_path}",
                )
                self.assertNotIn(
                    legacy_helper_path,
                    content,
                    f"issue-75 guidance still contains legacy absolute helper path in: {rel_path}",
                )

    def test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        issue_69_report = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00003-architecture-maintenance-and-hardening"
            / "epics"
            / "epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling"
            / "issues"
            / "iss-00069-package-data-and-installed-artifact-parity"
            / "report.md"
        )
        issue_70_report = (
            repo_root
            / "spec-dock"
            / "initiatives"
            / "init-local-00003-architecture-maintenance-and-hardening"
            / "epics"
            / "epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling"
            / "issues"
            / "iss-00070-installer-source-discovery-and-managed-ownership"
            / "report.md"
        )
        self.assertTrue(issue_69_report.is_file(), f"issue-71 missing issue-69 report: {issue_69_report}")
        self.assertTrue(issue_70_report.is_file(), f"issue-71 missing issue-70 report: {issue_70_report}")

        issue_69_text = issue_69_report.read_text(encoding="utf-8")
        issue_70_text = issue_70_report.read_text(encoding="utf-8")

        package_parity_section = self._issue_71_extract_markdown_section_by_heading_prefix(
            markdown_text=issue_69_text,
            heading_prefix="package-parity-evidence",
            source_label="issue-69 report",
        )
        for required_phrase in (
            "full inventory parity:",
            "representative asset set:",
            "stale exclusion guard:",
            "isolated install smoke:",
        ):
            self.assertIn(
                required_phrase,
                package_parity_section,
                f"issue-71 missing package parity subcheck phrase: {required_phrase}",
            )
        self.assertGreaterEqual(
            package_parity_section.count("- result:"),
            4,
            "issue-71 package parity evidence should include result lines for required subchecks",
        )
        self.assertGreaterEqual(
            package_parity_section.count("- pass"),
            4,
            "issue-71 package parity evidence should include pass results for required subchecks",
        )
        self.assertNotIn(
            "pending",
            package_parity_section.lower(),
            "issue-71 package parity evidence should not be pending-only",
        )
        self.assertNotIn(
            "placeholder",
            package_parity_section.lower(),
            "issue-71 package parity evidence should not be placeholder-only",
        )

        handoff_section = self._issue_71_extract_markdown_section_by_heading_prefix(
            markdown_text=issue_70_text,
            heading_prefix="handoff-validation-evidence",
            source_label="issue-70 report",
        )
        for required_phrase in (
            "source inventory / manifest assertions:",
            "invalid manifest negative test coverage:",
            "current managed / obsolete managed boundary assertions:",
            "installed-package cutover evidence:",
        ):
            self.assertIn(
                required_phrase,
                handoff_section,
                f"issue-71 missing issue-70 handoff subcheck phrase: {required_phrase}",
            )
        self.assertGreaterEqual(
            handoff_section.count("- result:"),
            4,
            "issue-71 handoff evidence should include result lines for required subchecks",
        )
        self.assertGreaterEqual(
            handoff_section.count("- pass"),
            4,
            "issue-71 handoff evidence should include pass results for required subchecks",
        )
        self.assertNotIn(
            "pending",
            handoff_section.lower(),
            "issue-71 handoff evidence should not be pending-only",
        )
        self.assertNotIn(
            "placeholder",
            handoff_section.lower(),
            "issue-71 handoff evidence should not be placeholder-only",
        )

    def test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            isolated_cwd = temp_root / "isolated-cwd"
            isolated_cwd.mkdir(parents=True, exist_ok=True)
            target_repo = temp_root / "consumer-repo"
            target_repo.mkdir(parents=True, exist_ok=True)

            venv_python = self._issue_69_prepare_isolated_installed_wheel_runtime(
                repo_root=repo_root,
                temp_root=temp_root,
            )
            spec_dock_command = self._issue_69_venv_spec_dock(venv_python)
            self.assertTrue(
                spec_dock_command.is_file(),
                f"issue-71 expected installed spec-dock command in isolated venv: {spec_dock_command}",
            )

            runtime_env = self._issue_69_runtime_env_without_checkout_fallback()
            self.assertNotIn("PYTHONPATH", runtime_env, "issue-71 runtime env must not rely on PYTHONPATH fallback")
            self.assertNotIn("PYTHONHOME", runtime_env, "issue-71 runtime env must not rely on PYTHONHOME fallback")

            runtime_snapshot = self._issue_69_collect_isolated_installed_runtime_snapshot(
                venv_python=venv_python,
                repo_root=repo_root,
                cwd=isolated_cwd,
            )
            self._issue_69_assert_runtime_snapshot_uses_installed_package(
                snapshot=runtime_snapshot,
                repo_root=repo_root,
            )
            self.assertFalse(
                bool(runtime_snapshot.get("sys_path_has_repo_root")),
                "issue-71 isolated installed runtime unexpectedly resolved repo-root fallback in sys.path",
            )

            plan_snapshot = self._issue_70_collect_isolated_installed_plan_snapshot(
                venv_python=venv_python,
                cwd=isolated_cwd,
            )
            current_sources = {str(path) for path in plan_snapshot.get("current_sources", [])}
            self.assertTrue(current_sources, "issue-71 installed plan must expose current managed sources")
            self.assertTrue(
                all(source.startswith("install_root/") for source in current_sources),
                "issue-71 installed plan should source current managed files from install_root only",
            )
            self.assertFalse(
                any(source.startswith("codex_skills/") for source in current_sources),
                "issue-71 installed plan must not source current managed files from legacy codex_skills",
            )

            installed_assets_dir = Path(str(runtime_snapshot.get("assets_dir", ""))).resolve()
            managed_rel_path = ".codex/agents/spec-manager.toml"
            expected_managed_bytes = (installed_assets_dir / "install_root" / managed_rel_path).read_bytes()

            self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "init", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )

            managed_target = target_repo / managed_rel_path
            self.assertTrue(managed_target.is_file(), f"issue-71 missing managed file after isolated init: {managed_target}")
            self.assertEqual(
                managed_target.read_bytes(),
                expected_managed_bytes,
                "issue-71 isolated init did not reflect install_root managed asset bytes",
            )

            obsolete_rel_path = ".codex/agents/spec-dock-codex-adapter.toml"
            obsolete_target = target_repo / obsolete_rel_path
            obsolete_target.parent.mkdir(parents=True, exist_ok=True)
            self._write_text_force(obsolete_target, "issue-71 obsolete managed payload\n")

            custom_rel_path = ".github/workflows/custom-review.yml"
            custom_target = target_repo / custom_rel_path
            custom_target.parent.mkdir(parents=True, exist_ok=True)
            custom_text = "name: issue-71 custom unmanaged workflow\n"
            self._write_text_force(custom_target, custom_text)

            self._write_text_force(managed_target, "issue-71 stale managed payload\n")
            self._issue_69_run_subprocess_capture(
                [str(spec_dock_command), "update", str(target_repo)],
                cwd=isolated_cwd,
                env=runtime_env,
            )

            self.assertEqual(
                managed_target.read_bytes(),
                expected_managed_bytes,
                "issue-71 isolated update did not restore managed file from install_root",
            )
            self.assertFalse(
                obsolete_target.exists(),
                f"issue-71 isolated update should prune obsolete managed path: {obsolete_rel_path}",
            )
            self.assertTrue(
                custom_target.is_file(),
                f"issue-71 isolated update removed custom unmanaged file: {custom_rel_path}",
            )
            self.assertEqual(
                custom_target.read_text(encoding="utf-8"),
                custom_text,
                f"issue-71 isolated update mutated custom unmanaged file: {custom_rel_path}",
            )

    def test_init_generated_native_shims_satisfy_static_delegation_only_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            expected_codex_bytes = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".codex"
                / "agents"
                / "spec-manager.toml"
            ).read_bytes()
            expected_copilot_bytes = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".github"
                / "agents"
                / "orchestrator.agent.md"
            ).read_bytes()
            expected_copilot_spec_manager_bytes = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".github"
                / "agents"
                / "spec-manager.agent.md"
            ).read_bytes()

            codex_path = target / ".codex" / "agents" / "spec-manager.toml"
            codex_bootstrap_path = target / ".codex" / "AGENTS.md"
            codex_config_path = target / ".codex" / "config.toml"
            copilot_spec_manager_path = target / ".github" / "agents" / "spec-manager.agent.md"
            copilot_path = target / ".github" / "agents" / "orchestrator.agent.md"
            codex_orchestrator_path = target / ".codex" / "agents" / "orchestrator.toml"
            self.assertTrue(codex_path.is_file(), f"missing generated codex native shim: {codex_path}")
            self.assertTrue(codex_bootstrap_path.is_file(), f"missing generated codex bootstrap guide: {codex_bootstrap_path}")
            self.assertTrue(codex_config_path.is_file(), f"missing generated codex main config: {codex_config_path}")
            self.assertTrue(
                copilot_spec_manager_path.is_file(),
                f"missing generated copilot spec-manager: {copilot_spec_manager_path}",
            )
            self.assertTrue(copilot_path.is_file(), f"missing generated copilot native shim: {copilot_path}")
            self.assertFalse(
                codex_orchestrator_path.exists(),
                f"codex direct orchestrator should not be generated: {codex_orchestrator_path}",
            )
            self.assertEqual(
                codex_path.read_bytes(),
                expected_codex_bytes,
                "generated codex native shim diverged from provider asset bytes",
            )
            self.assertEqual(
                copilot_path.read_bytes(),
                expected_copilot_bytes,
                "generated copilot native shim diverged from provider asset bytes",
            )
            self.assertEqual(
                copilot_spec_manager_path.read_bytes(),
                expected_copilot_spec_manager_bytes,
                "generated copilot spec-manager diverged from provider asset bytes",
            )
            codex_text = codex_path.read_text(encoding="utf-8")
            codex_bootstrap_text = codex_bootstrap_path.read_text(encoding="utf-8")
            codex_config_text = codex_config_path.read_text(encoding="utf-8")
            copilot_spec_manager_text = copilot_spec_manager_path.read_text(encoding="utf-8")
            copilot_text = copilot_path.read_text(encoding="utf-8")

            self._assert_spec_manager_contract(
                text=codex_text,
                delegation_expected=".agents/skills/spec-dock-codex-adapter/SKILL.md",
                shim_label="generated codex native shim",
            )
            self._assert_codex_native_shim_loader_contract(
                text=codex_text,
                shim_label="generated codex native shim",
            )
            self._assert_codex_bootstrap_routing_contract(
                text=codex_bootstrap_text,
                shim_label="generated codex bootstrap guide",
            )
            self._assert_codex_main_config_routing_contract(
                text=codex_config_text,
                shim_label="generated codex main config",
            )
            self._assert_spec_manager_contract(
                text=copilot_spec_manager_text,
                delegation_expected=".agents/skills/spec-dock-copilot-adapter/SKILL.md",
                shim_label="generated copilot spec-manager",
            )
            self._assert_copilot_spec_manager_contract(
                text=copilot_spec_manager_text,
                shim_label="generated copilot spec-manager",
            )
            self._assert_copilot_orchestrator_contract(
                text=copilot_text,
                shim_label="generated copilot orchestrator",
            )

    def test_update_copies_legacy_codex_native_shim_instructions_key_as_is(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            source_assets_root = repo_root / "src" / "spec_dock" / "assets"

            with tempfile.TemporaryDirectory() as tmp_assets:
                patched_assets_root = Path(tmp_assets) / "assets"
                shutil.copytree(source_assets_root, patched_assets_root)

                codex_shim_path = patched_assets_root / "install_root" / ".codex" / "agents" / "spec-manager.toml"
                codex_text = codex_shim_path.read_text(encoding="utf-8")
                self.assertRegex(codex_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                patched_text = codex_text.replace("developer_instructions =", "instructions =", 1)
                self.assertRegex(patched_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)
                self.assertNotRegex(patched_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                codex_shim_path.write_text(patched_text, encoding="utf-8")
                expected_bytes = codex_shim_path.read_bytes()

                @contextmanager
                def _patched_assets_dir():
                    yield patched_assets_root

                with patch("spec_dock.cli._assets_dir", _patched_assets_dir):
                    self.assertEqual(main(["update", str(target)]), 0)

            generated_path = target / ".codex" / "agents" / "spec-manager.toml"
            generated_text = generated_path.read_text(encoding="utf-8")
            self.assertEqual(
                generated_path.read_bytes(),
                expected_bytes,
                "update should copy legacy codex shim asset bytes without normalization",
            )
            self.assertRegex(generated_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)
            self.assertNotRegex(generated_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)

    def test_init_copies_legacy_codex_native_shim_instructions_key_as_is(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "repo"
            target.mkdir(parents=True, exist_ok=True)

            repo_root = Path(__file__).resolve().parents[1]
            source_assets_root = repo_root / "src" / "spec_dock" / "assets"

            with tempfile.TemporaryDirectory() as tmp_assets:
                patched_assets_root = Path(tmp_assets) / "assets"
                shutil.copytree(source_assets_root, patched_assets_root)

                codex_shim_path = patched_assets_root / "install_root" / ".codex" / "agents" / "spec-manager.toml"
                codex_text = codex_shim_path.read_text(encoding="utf-8")
                self.assertRegex(codex_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                patched_text = codex_text.replace("developer_instructions =", "instructions =", 1)
                self.assertRegex(patched_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)
                self.assertNotRegex(patched_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                codex_shim_path.write_text(patched_text, encoding="utf-8")
                expected_bytes = codex_shim_path.read_bytes()

                @contextmanager
                def _patched_assets_dir():
                    yield patched_assets_root

                with patch("spec_dock.cli._assets_dir", _patched_assets_dir):
                    self.assertEqual(main(["init", str(target)]), 0)

            generated_path = target / ".codex" / "agents" / "spec-manager.toml"
            generated_text = generated_path.read_text(encoding="utf-8")
            self.assertEqual(
                generated_path.read_bytes(),
                expected_bytes,
                "init should copy legacy codex shim asset bytes without normalization",
            )
            self.assertRegex(generated_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)
            self.assertNotRegex(generated_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)

    def test_update_copies_codex_native_shim_without_instruction_keys_as_is(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            source_assets_root = repo_root / "src" / "spec_dock" / "assets"

            with tempfile.TemporaryDirectory() as tmp_assets:
                patched_assets_root = Path(tmp_assets) / "assets"
                shutil.copytree(source_assets_root, patched_assets_root)

                codex_shim_path = patched_assets_root / "install_root" / ".codex" / "agents" / "spec-manager.toml"
                codex_text = codex_shim_path.read_text(encoding="utf-8")
                self.assertRegex(codex_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                self.assertNotRegex(codex_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)

                lines = codex_text.splitlines(keepends=True)
                normalized_lines: list[str] = []
                skipping_block = False
                for line in lines:
                    if not skipping_block and line.lstrip().startswith("developer_instructions"):
                        skipping_block = True
                        continue
                    if skipping_block:
                        if '"""' in line:
                            skipping_block = False
                        continue
                    normalized_lines.append(line)

                patched_text = "".join(normalized_lines)
                self.assertNotRegex(patched_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
                self.assertNotRegex(patched_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)
                codex_shim_path.write_text(patched_text, encoding="utf-8")
                expected_bytes = codex_shim_path.read_bytes()

                @contextmanager
                def _patched_assets_dir():
                    yield patched_assets_root

                with patch("spec_dock.cli._assets_dir", _patched_assets_dir):
                    self.assertEqual(main(["update", str(target)]), 0)

            generated_path = target / ".codex" / "agents" / "spec-manager.toml"
            generated_text = generated_path.read_text(encoding="utf-8")
            self.assertEqual(
                generated_path.read_bytes(),
                expected_bytes,
                "update should copy codex shim asset bytes without instruction key validation",
            )
            self.assertNotRegex(generated_text, self._CODEX_NATIVE_SHIM_DEVELOPER_INSTRUCTIONS_PATTERN)
            self.assertNotRegex(generated_text, self._CODEX_NATIVE_SHIM_LEGACY_INSTRUCTIONS_PATTERN)

    def test_update_manages_native_shims_with_gate_2_five_subchecks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            repo_root = Path(__file__).resolve().parents[1]
            codex_shim_asset = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".codex"
                / "agents"
                / "spec-manager.toml"
            )
            copilot_shim_asset = (
                repo_root
                / "src"
                / "spec_dock"
                / "assets"
                / "install_root"
                / ".github"
                / "agents"
                / "orchestrator.agent.md"
            )
            expected_codex_shim = codex_shim_asset.read_bytes()
            expected_copilot_shim = copilot_shim_asset.read_bytes()

            managed_codex_path = target / ".codex" / "agents" / "spec-manager.toml"
            managed_copilot_path = target / ".github" / "agents" / "orchestrator.agent.md"
            managed_codex_config_path = target / ".codex" / "config.toml"
            expected_codex_config = (
                repo_root / "src" / "spec_dock" / "assets" / "install_root" / ".codex" / "config.toml"
            ).read_bytes()
            obsolete_codex_path = target / ".codex" / "agents" / "spec-dock-codex-adapter.toml"
            obsolete_copilot_path = target / ".github" / "agents" / "spec-dock-copilot-adapter.agent.md"
            obsolete_old_codex_path = target / ".codex" / "agents" / "spec-dock.toml"
            obsolete_old_copilot_path = target / ".github" / "agents" / "spec-dock.agent.md"
            custom_codex_path = target / ".codex" / "agents" / "custom-reviewer.toml"
            custom_copilot_path = target / ".github" / "agents" / "custom-reviewer.agent.md"
            custom_skill_path = target / ".agents" / "skills" / "custom-reviewer" / "SKILL.md"
            meta_path = target / ".agents" / "host-adapters" / "meta.json"

            stale_managed_codex = b"name = \"stale-managed\"\n"
            stale_managed_copilot = b"# stale managed copilot shim\n"
            bootstrap_only_codex_config = "# user custom codex config should survive update\n"
            custom_codex_content = "name = \"custom-reviewer\"\n"
            custom_copilot_content = "# custom reviewer copilot agent\n"
            custom_skill_content = "# custom skill that must be preserved\n"

            self._write_text_force(managed_codex_path, stale_managed_codex.decode("utf-8"))
            self._write_text_force(managed_copilot_path, stale_managed_copilot.decode("utf-8"))
            self._write_text_force(managed_codex_config_path, bootstrap_only_codex_config)
            self._write_text_force(obsolete_codex_path, "obsolete managed codex shim\n")
            self._write_text_force(obsolete_copilot_path, "obsolete managed copilot shim\n")
            self._write_text_force(obsolete_old_codex_path, "obsolete old canonical codex shim\n")
            self._write_text_force(obsolete_old_copilot_path, "obsolete old canonical copilot shim\n")
            self._write_text_force(custom_codex_path, custom_codex_content)
            self._write_text_force(custom_copilot_path, custom_copilot_content)
            custom_skill_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_text_force(custom_skill_path, custom_skill_content)

            self.assertEqual(main(["update", str(target)]), 0)

            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            managed_codex_bytes = (
                managed_codex_path.read_bytes() if managed_codex_path.is_file() else None
            )
            managed_copilot_bytes = (
                managed_copilot_path.read_bytes() if managed_copilot_path.is_file() else None
            )
            gate_2_sync_prune_evidence: dict[str, dict[str, object]] = {
                "managed_codex_shim_generated_or_updated": {
                    "expected": "managed codex shim exists and matches provider asset",
                    "observed": (
                        f"exists={managed_codex_path.is_file()}, "
                        f"matches_asset={managed_codex_bytes == expected_codex_shim}"
                    ),
                    "pass": managed_codex_path.is_file()
                    and managed_codex_bytes == expected_codex_shim
                    and managed_codex_bytes != stale_managed_codex,
                },
                "managed_copilot_shim_generated_or_updated": {
                    "expected": "managed copilot shim exists and matches provider asset",
                    "observed": (
                        f"exists={managed_copilot_path.is_file()}, "
                        f"matches_asset={managed_copilot_bytes == expected_copilot_shim}"
                    ),
                    "pass": managed_copilot_path.is_file()
                    and managed_copilot_bytes == expected_copilot_shim
                    and managed_copilot_bytes != stale_managed_copilot,
                },
                "obsolete_managed_fixture_pruned": {
                    "expected": "obsolete managed fixtures are removed",
                    "observed": (
                        f"codex_exists={obsolete_codex_path.exists()}, "
                        f"copilot_exists={obsolete_copilot_path.exists()}, "
                        f"old_codex_exists={obsolete_old_codex_path.exists()}, "
                        f"old_copilot_exists={obsolete_old_copilot_path.exists()}"
                    ),
                    "pass": (not obsolete_codex_path.exists())
                    and (not obsolete_copilot_path.exists())
                    and (not obsolete_old_codex_path.exists())
                    and (not obsolete_old_copilot_path.exists()),
                },
                "bootstrap_only_codex_config_preserved": {
                    "expected": "bootstrap-only codex config should keep user-edited content",
                    "observed": (
                        managed_codex_config_path.read_text(encoding="utf-8")
                        if managed_codex_config_path.is_file()
                        else None
                    ),
                    "pass": managed_codex_config_path.is_file()
                    and managed_codex_config_path.read_text(encoding="utf-8") == bootstrap_only_codex_config
                    and managed_codex_config_path.read_bytes() != expected_codex_config,
                },
                "unknown_custom_fixture_preserved": {
                    "expected": "unknown custom native shims and custom skill are preserved",
                    "observed": (
                        f"codex_custom={custom_codex_path.read_text(encoding='utf-8') if custom_codex_path.is_file() else None}, "
                        f"copilot_custom={custom_copilot_path.read_text(encoding='utf-8') if custom_copilot_path.is_file() else None}, "
                        f"custom_skill_exists={custom_skill_path.is_file()}"
                    ),
                    "pass": custom_codex_path.is_file()
                    and custom_codex_path.read_text(encoding="utf-8") == custom_codex_content
                    and custom_copilot_path.is_file()
                    and custom_copilot_path.read_text(encoding="utf-8") == custom_copilot_content
                    and custom_skill_path.is_file()
                    and custom_skill_path.read_text(encoding="utf-8") == custom_skill_content,
                },
                "baseline_skill_and_metadata_untouched": {
                    "expected": "baseline adapter skills and entry_file contracts remain intact",
                    "observed": (
                        "codex_skill_exists="
                        f"{(target / '.agents' / 'skills' / 'spec-dock-codex-adapter' / 'SKILL.md').is_file()}, "
                        "copilot_skill_exists="
                        f"{(target / '.agents' / 'skills' / 'spec-dock-copilot-adapter' / 'SKILL.md').is_file()}, "
                        f"meta_entry_codex={meta.get('targets', {}).get('codex', {}).get('entry_file')}, "
                        f"meta_entry_copilot={meta.get('targets', {}).get('copilot', {}).get('entry_file')}"
                    ),
                    "pass": (target / ".agents" / "skills" / "spec-dock-codex-adapter" / "SKILL.md").is_file()
                    and (target / ".agents" / "skills" / "spec-dock-copilot-adapter" / "SKILL.md").is_file()
                    and meta == self._EXPECTED_HOST_ADAPTER_META,
                },
            }
            gate_2_sync_prune_pass = all(
                bool(gate_2_sync_prune_evidence[subcheck]["pass"])
                for subcheck in (
                    "managed_codex_shim_generated_or_updated",
                    "managed_copilot_shim_generated_or_updated",
                    "obsolete_managed_fixture_pruned",
                    "bootstrap_only_codex_config_preserved",
                    "unknown_custom_fixture_preserved",
                    "baseline_skill_and_metadata_untouched",
                )
            )

            for subcheck, evidence in gate_2_sync_prune_evidence.items():
                self.assertTrue(bool(evidence["pass"]), f"{subcheck} failed: {evidence}")
            self.assertTrue(gate_2_sync_prune_pass, gate_2_sync_prune_evidence)

    def test_update_rejects_non_boolean_native_shim_managed_values(self) -> None:
        for invalid_managed in ("true", 1):
            with self.subTest(invalid_managed=invalid_managed):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    malformed_manifest["targets"]["codex"]["native_shim"]["managed"] = invalid_managed

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn("invalid native_shim.managed for host 'codex'", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_manifest_missing_required_native_shim_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"].pop("copilot")

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn("missing required managed native shim hosts: copilot", stderr)
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_missing_or_null_required_host_native_shim_contract(self) -> None:
        for mode in ("missing", "null"):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    if mode == "missing":
                        malformed_manifest["targets"]["codex"].pop("native_shim")
                    else:
                        malformed_manifest["targets"]["codex"]["native_shim"] = None

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn("missing required native_shim contract for host 'codex'", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_required_host_native_shim_managed_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["codex"]["native_shim"]["managed"] = False

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn("required host 'codex' must define native_shim.managed=true", stderr)
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_required_host_native_shim_target_file_swaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["codex"]["native_shim"]["target_file"] = (
                ".github/agents/orchestrator.agent.md"
            )
            malformed_manifest["targets"]["copilot"]["native_shim"]["target_file"] = (
                ".codex/agents/spec-manager.toml"
            )

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "required host 'codex' must use canonical native_shim.target_file '.codex/agents/spec-manager.toml'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_duplicate_required_host_native_shim_target_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["copilot"]["native_shim"]["target_file"] = (
                ".codex/agents/spec-manager.toml"
            )

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "duplicate native_shim.target_file '.codex/agents/spec-manager.toml'",
                stderr,
            )
            self.assertIn("for hosts 'codex' and 'copilot'", stderr)
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_init_preflight_rejects_invalid_host_manifest_before_scaffold_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "repo"
            target.mkdir(parents=True, exist_ok=True)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["codex"]["native_shim"]["target_file"] = (
                ".github/agents/orchestrator.agent.md"
            )

            exit_code, stderr = self._run_init_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "required host 'codex' must use canonical native_shim.target_file '.codex/agents/spec-manager.toml'",
                stderr,
            )
            self.assertEqual(list(target.iterdir()), [], "preflight failure should not write managed scaffold files")

    def test_update_preflight_rejects_missing_or_non_directory_later_managed_asset_before_mutation(self) -> None:
        for mode in ("missing", "non_directory"):
            with self.subTest(mode=mode):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)

                    def _mutate_assets(patched_assets_root: Path) -> None:
                        scripts_dir = patched_assets_root / "spec_dock" / "scripts"
                        shutil.rmtree(scripts_dir)
                        if mode == "non_directory":
                            scripts_dir.write_text("invalid scaffold asset directory replacement\n", encoding="utf-8")

                    exit_code, stderr = self._run_command_with_assets_override(
                        "update",
                        target,
                        _mutate_assets,
                    )

                    self.assertEqual(exit_code, 1)
                    if mode == "missing":
                        self.assertIn("Missing asset directory", stderr)
                    else:
                        self.assertIn("Invalid asset directory", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_required_host_entry_file_drift_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["codex"]["entry_file"] = ".agents/skills/spec-dock-copilot-adapter/SKILL.md"

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "required host 'codex' must use canonical entry_file '.agents/skills/spec-dock-codex-adapter/SKILL.md'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_missing_or_malformed_required_native_shim_owner_and_delegates_to_before_writes(
        self,
    ) -> None:
        cases = (
            ("owner_missing", "invalid native_shim.owner for host 'codex'"),
            ("owner_non_string", "invalid native_shim.owner for host 'codex'"),
            ("owner_drift", "required host 'codex' must use native_shim.owner 'spec-dock'"),
            ("delegates_missing", "invalid native_shim.delegates_to for host 'codex'"),
            ("delegates_non_string", "invalid native_shim.delegates_to for host 'codex'"),
            (
                "delegates_drift",
                "required host 'codex' must use canonical native_shim.delegates_to "
                "'.agents/skills/spec-dock-codex-adapter/SKILL.md'",
            ),
        )
        for case_name, expected_error in cases:
            with self.subTest(case_name=case_name):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    native_shim = malformed_manifest["targets"]["codex"]["native_shim"]

                    if case_name == "owner_missing":
                        native_shim.pop("owner")
                    elif case_name == "owner_non_string":
                        native_shim["owner"] = 1
                    elif case_name == "owner_drift":
                        native_shim["owner"] = "external-owner"
                    elif case_name == "delegates_missing":
                        native_shim.pop("delegates_to")
                    elif case_name == "delegates_non_string":
                        native_shim["delegates_to"] = 1
                    elif case_name == "delegates_drift":
                        native_shim["delegates_to"] = ".agents/skills/spec-dock-copilot-adapter/SKILL.md"
                    else:
                        raise AssertionError(f"unknown case_name: {case_name}")

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn(expected_error, stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_non_mapping_host_target_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["targets"]["codex"] = "not-a-map"

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn("invalid host adapter target contract for host 'codex'", stderr)
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_current_dir_obsolete_exact_file_paths(self) -> None:
        for invalid_obsolete_path in (".", "./"):
            with self.subTest(invalid_obsolete_path=invalid_obsolete_path):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                        invalid_obsolete_path,
                    ]

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn("invalid managed_assets.obsolete_exact_file_paths item", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_directory_like_obsolete_exact_file_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            before = self._seed_managed_contract_guard_snapshot(target)
            malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
            malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                ".codex/agents/legacy",
            ]

            exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                target,
                malformed_manifest,
            )

            self.assertEqual(exit_code, 1)
            self.assertIn(
                "invalid managed_assets.obsolete_exact_file_paths item (must be exact file path): "
                "'.codex/agents/legacy'",
                stderr,
            )
            self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_parent_traversal_native_shim_paths(self) -> None:
        cases: tuple[tuple[str, str, str], ...] = (
            (
                "source_of_truth_asset",
                "../codex_skills/native-shims/spec-dock.toml",
                "invalid native_shim.source_of_truth_asset path for host 'codex'",
            ),
            (
                "target_file",
                "../.codex/agents/spec-manager.toml",
                "invalid native_shim.target_file path for host 'codex'",
            ),
            (
                "obsolete_exact_file_paths",
                "../.codex/agents/spec-dock-codex-adapter.toml",
                "invalid managed_assets.obsolete_exact_file_paths item",
            ),
        )
        for field, invalid_path, expected_error in cases:
            with self.subTest(field=field, invalid_path=invalid_path):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    if field == "obsolete_exact_file_paths":
                        malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [invalid_path]
                    else:
                        malformed_manifest["targets"]["codex"]["native_shim"][field] = invalid_path

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn(expected_error, stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_windows_drive_relative_native_shim_paths(self) -> None:
        cases: tuple[tuple[str, str], ...] = (
            ("source_of_truth_asset", "invalid native_shim.source_of_truth_asset path for host 'codex'"),
            ("target_file", "invalid native_shim.target_file path for host 'codex'"),
            ("obsolete_exact_file_paths", "invalid managed_assets.obsolete_exact_file_paths item"),
        )
        invalid_paths = ("C:foo", "/foo", "\\foo")
        for field, expected_error in cases:
            for invalid_path in invalid_paths:
                with self.subTest(field=field, invalid_path=invalid_path):
                    with tempfile.TemporaryDirectory() as tmp:
                        target = Path(tmp)
                        self.assertEqual(main(["init", str(target)]), 0)
                        before = self._seed_managed_contract_guard_snapshot(target)
                        malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                        if field == "obsolete_exact_file_paths":
                            malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [invalid_path]
                        else:
                            malformed_manifest["targets"]["codex"]["native_shim"][field] = invalid_path

                        exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                            target,
                            malformed_manifest,
                        )

                        self.assertEqual(exit_code, 1)
                        self.assertIn(expected_error, stderr)
                        self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_native_shim_target_file_outside_managed_prefixes(self) -> None:
        for invalid_target in ("README.md", ".agents/skills/spec-dock-codex-adapter/SKILL.md"):
            with self.subTest(invalid_target=invalid_target):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    malformed_manifest["targets"]["codex"]["native_shim"]["target_file"] = invalid_target

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn("invalid native_shim.target_file path for host 'codex'", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_update_rejects_obsolete_exact_file_paths_outside_managed_prefixes(self) -> None:
        for invalid_obsolete in ("README.md", ".agents/spec-dock-codex-adapter/SKILL.md"):
            with self.subTest(invalid_obsolete=invalid_obsolete):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp)
                    self.assertEqual(main(["init", str(target)]), 0)
                    before = self._seed_managed_contract_guard_snapshot(target)
                    malformed_manifest = json.loads(json.dumps(self._EXPECTED_HOST_ADAPTER_META))
                    malformed_manifest["managed_assets"]["obsolete_exact_file_paths"] = [
                        invalid_obsolete
                    ]

                    exit_code, stderr = self._run_update_with_host_adapter_manifest_override(
                        target,
                        malformed_manifest,
                    )

                    self.assertEqual(exit_code, 1)
                    self.assertIn("invalid managed_assets.obsolete_exact_file_paths item", stderr)
                    self._assert_managed_contract_guard_unchanged(target, before)

    def test_reference_sync_doc_matches_bundled_asset(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            bundled = (assets_dir / "spec_dock" / "docs" / "reference_sync.md").read_text(encoding="utf-8")

        repo_copy = (
            Path(__file__).resolve().parents[1] / "spec-dock" / "docs" / "reference_sync.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(repo_copy, bundled)

    def test_reference_deps_doc_matches_bundled_asset(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            bundled = (assets_dir / "spec_dock" / "docs" / "reference_deps.md").read_text(encoding="utf-8")

        repo_copy = (
            Path(__file__).resolve().parents[1] / "spec-dock" / "docs" / "reference_deps.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(repo_copy, bundled)

    def test_workflow_issue_doc_matches_bundled_asset(self) -> None:
        import spec_dock.cli as cli

        with cli._assets_dir() as assets_dir:
            bundled = (assets_dir / "spec_dock" / "docs" / "workflow_issue.md").read_text(encoding="utf-8")

        repo_copy = (
            Path(__file__).resolve().parents[1] / "spec-dock" / "docs" / "workflow_issue.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(repo_copy, bundled)

    def test_init_fails_without_force_when_spec_dock_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            # Second init without --force should fail.
            self.assertNotEqual(main(["init", str(target)]), 0)

    def test_update_keeps_initiatives_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            marker = target / "spec-dock" / "initiatives" / "marker.txt"
            marker.write_text("keep\n", encoding="utf-8")

            # Simulate legacy (v1) leftovers that v2 should prune on update.
            legacy_workflow = target / ".github" / "workflows" / "spec-dock-close.yml"
            legacy_workflow.parent.mkdir(parents=True, exist_ok=True)
            legacy_workflow.write_text("legacy\n", encoding="utf-8")

            legacy_symlink = target / "spec-dock" / "current-initiative"
            created_symlink = False
            try:
                # v1 style link target (so v2 can safely prune without deleting v2-generated shortcuts).
                os.symlink("initiative/current", legacy_symlink)
                created_symlink = True
            except OSError:
                # Some environments may restrict symlinks; workflow pruning is still validated.
                created_symlink = False

            self.assertEqual(main(["update", str(target)]), 0)
            self.assertTrue(marker.is_file())
            self._assert_version_file(target)
            self.assertFalse(legacy_workflow.exists())
            if created_symlink:
                self.assertFalse(legacy_symlink.is_symlink())

    def _clear_active_entrypoints(self, target: Path) -> Path:
        active_dir = target / "spec-dock" / "active"
        for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
            p = active_dir / name
            if p.is_symlink() or p.is_file():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                shutil.rmtree(p)
        self.assertEqual(list(active_dir.iterdir()), [])
        return active_dir

    def _overlay_checked_in_dogfooding_runtime(self, target: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        checked_in_scripts_dir = repo_root / "spec-dock" / "scripts"
        target_scripts_dir = target / "spec-dock" / "scripts"
        self.assertTrue(checked_in_scripts_dir.is_dir(), f"checked-in scripts dir missing: {checked_in_scripts_dir}")
        self.assertTrue(target_scripts_dir.is_dir(), f"target scripts dir missing: {target_scripts_dir}")

        target_runtime_dir = target_scripts_dir / "spec_dock_runtime"
        if target_runtime_dir.exists():
            shutil.rmtree(target_runtime_dir)
        shutil.copytree(checked_in_scripts_dir / "spec_dock_runtime", target_runtime_dir)
        shutil.copy2(checked_in_scripts_dir / "spec-dock", target_scripts_dir / "spec-dock")

    def _create_minimal_local_tree(self, target: Path) -> tuple[Path, Path, Path]:
        initiative_dir = target / "spec-dock" / "initiatives" / "init-local-00001-auth-platform"
        epic_dir = initiative_dir / "epics" / "epic-local-00001-jwt-auth"
        issue_dir = epic_dir / "issues" / "iss-local-00001-add-refresh-token"

        def _materialize_node(node_dir: Path, meta: dict[str, object]) -> None:
            node_dir.mkdir(parents=True, exist_ok=True)
            (node_dir / "discussions").mkdir(parents=True, exist_ok=True)
            self._write_json_force(node_dir / ".meta.json", meta)
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                self._write_text_force(node_dir / filename, f"{meta['id']}:{filename}\n")

        _materialize_node(
            initiative_dir,
            {
                "schema_version": 1,
                "type": "initiative",
                "id": "init-local-00001",
                "title": "Auth platform",
                "slug": "auth-platform",
                "github": {
                    "issue_number": 101,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        _materialize_node(
            epic_dir,
            {
                "schema_version": 1,
                "type": "epic",
                "id": "epic-local-00001",
                "title": "JWT auth",
                "slug": "jwt-auth",
                "parent_id": "init-local-00001",
                "initiative_id": "init-local-00001",
                "github": {
                    "issue_number": 102,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        _materialize_node(
            issue_dir,
            {
                "schema_version": 1,
                "type": "issue",
                "id": "iss-local-00001",
                "title": "Add refresh token",
                "slug": "add-refresh-token",
                "parent_id": "epic-local-00001",
                "initiative_id": "init-local-00001",
                "epic_id": "epic-local-00001",
                "github": {
                    "issue_number": 103,
                    "repo_owner": "example",
                    "repo_name": "repo",
                },
            },
        )
        self.assertTrue((initiative_dir / ".meta.json").is_file())
        self.assertTrue((epic_dir / ".meta.json").is_file())
        self.assertTrue((issue_dir / ".meta.json").is_file())
        return initiative_dir, epic_dir, issue_dir

    def _materialize_local_issue_under_epic(
        self,
        epic_dir: Path,
        *,
        local_num: int,
        title: str,
        github_issue_number: int | None = None,
        github_repo_owner: str = "example",
        github_repo_name: str = "repo",
    ) -> Path:
        epic_meta = json.loads((epic_dir / ".meta.json").read_text(encoding="utf-8"))
        slug = title.lower().replace(" ", "-")
        issue_dir = epic_dir / "issues" / f"iss-local-{local_num:05d}-{slug}"
        issue_meta: dict[str, object] = {
            "schema_version": 1,
            "type": "issue",
            "id": f"iss-local-{local_num:05d}",
            "title": title,
            "slug": slug,
            "parent_id": str(epic_meta["id"]),
            "initiative_id": str(epic_meta["initiative_id"]),
            "epic_id": str(epic_meta["id"]),
        }
        if github_issue_number is not None:
            issue_meta["github"] = {
                "issue_number": github_issue_number,
                "repo_owner": github_repo_owner,
                "repo_name": github_repo_name,
            }

        issue_dir.mkdir(parents=True, exist_ok=True)
        (issue_dir / "discussions").mkdir(parents=True, exist_ok=True)
        self._write_json_force(issue_dir / ".meta.json", issue_meta)
        for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
            self._write_text_force(issue_dir / filename, f"{issue_meta['id']}:{filename}\n")
        return issue_dir

    def test_checked_in_dogfooding_runtime_subprocess_import_post_sync_no_crash_parity(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            import_result = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(
                import_result.returncode,
                0,
                msg=f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}",
            )
            self.assertIn("spec-dock: ok (import issue)", import_result.stdout)
            self.assertNotIn("import_post_sync_failed", import_result.stderr)
            self.assertTrue((target / "spec-dock" / ".agent" / "index.json").is_file())
            self.assertTrue((target / "spec-dock" / ".agent" / "tree.json").is_file())

    def test_checked_in_dogfooding_runtime_subprocess_issue_create_gateway_failure_pre_github_parity(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, _current_issue_dir = self._create_minimal_local_tree(target)

            issues_dir = epic_dir / "issues"
            before_issue_dirs = sorted(p.name for p in issues_dir.iterdir() if p.is_dir())
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            gh_path = bin_dir / "gh"
            gh_path.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                f'echo "$1 $2" >> "{log_path.as_posix()}"\n'
                'if [[ "$1" == "issue" && "$2" == "create" ]]; then\n'
                '  echo "simulated issue_create failure" >&2\n'
                "  exit 1\n"
                "fi\n"
                'if [[ "$1" == "issue" && "$2" == "list" ]]; then\n'
                "  echo '[]'\n"
                "  exit 0\n"
                "fi\n"
                'echo "unexpected gh args: $@" >&2\n'
                "exit 99\n",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            create_result = self._run_runtime_capture(
                target,
                ["new", "issue", "--epic", "epic-local-00001", "--title", "Gateway failure issue"],
                env=test_env,
            )
            self.assertEqual(
                create_result.returncode,
                1,
                msg=f"new issue stdout:\n{create_result.stdout}\nnew issue stderr:\n{create_result.stderr}",
            )
            self.assertIn("Outcome: pre_github_fail", create_result.stderr)
            self.assertNotIn("GitHub issue was created:", create_result.stderr)

            after_issue_dirs = sorted(p.name for p in issues_dir.iterdir() if p.is_dir())
            self.assertEqual(after_issue_dirs, before_issue_dirs)
            self.assertFalse(any(name.endswith("-gateway-failure-issue") for name in after_issue_dirs))

            gh_calls = [line for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(gh_calls), 1, msg=f"unexpected gh calls: {gh_calls}")
            self.assertEqual(gh_calls[0], "issue create", msg=f"unexpected gh calls: {gh_calls}")

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)
            depends_meta_path = depends_issue_dir / ".meta.json"
            depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
            depends_meta["depends_on"] = [123]
            self._write_json_force(depends_meta_path, depends_meta)

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003", "--json"],
            )
            self.assertEqual(
                deps_result.returncode,
                3,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            payload = json.loads(deps_result.stdout)
            self.assertEqual(payload.get("effective_depends_on"), ["iss-local-00001"])
            self.assertEqual(payload.get("blockers"), ["iss-local-00001"])
            self.assertNotIn("Ambiguous github.issue_number=123", deps_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_repo_scoped_url_target_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123, "repo_owner": "current", "repo_name": "repo"}
            self._write_json_force(current_meta_path, current_meta)

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            ambiguous_active = self._run_runtime_capture(target, ["active", "set", "123", "--force"])
            self.assertEqual(
                ambiguous_active.returncode,
                1,
                msg=f"active(ambiguous) stdout:\n{ambiguous_active.stdout}\nactive(ambiguous) stderr:\n{ambiguous_active.stderr}",
            )
            self.assertIn("Ambiguous github.issue_number=123", ambiguous_active.stderr)

            scoped_active = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/other/repo/issues/123", "--force"],
            )
            self.assertEqual(
                scoped_active.returncode,
                0,
                msg=f"active(scoped) stdout:\n{scoped_active.stdout}\nactive(scoped) stderr:\n{scoped_active.stderr}",
            )
            self.assertIn("spec-dock: ok (active set)", scoped_active.stdout)

            active_manifest = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_manifest["issue"]["id"], "iss-local-00002")

            scoped_deps = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/other/repo/issues/123", "--json"],
            )
            self.assertIn(
                scoped_deps.returncode,
                (0, 3),
                msg=f"deps(scoped) stdout:\n{scoped_deps.stdout}\ndeps(scoped) stderr:\n{scoped_deps.stderr}",
            )
            self.assertIn('"target": "iss-local-00002"', scoped_deps.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_current_repo_url_target_resolves_unscoped_current_parity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            active_current = self._run_runtime_capture(
                target,
                ["active", "set", "https://github.com/current/repo/issues/123", "--force"],
            )
            self.assertEqual(
                active_current.returncode,
                0,
                msg=f"active(current) stdout:\n{active_current.stdout}\nactive(current) stderr:\n{active_current.stderr}",
            )
            active_manifest = json.loads((target / "spec-dock" / ".agent" / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(active_manifest["issue"]["id"], "iss-local-00001")

            deps_current = self._run_runtime_capture(
                target,
                ["deps", "check", "https://github.com/current/repo/issues/123", "--json"],
            )
            self.assertIn(
                deps_current.returncode,
                (0, 3),
                msg=f"deps(current) stdout:\n{deps_current.stdout}\ndeps(current) stderr:\n{deps_current.stderr}",
            )
            self.assertIn('"target": "iss-local-00001"', deps_current.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"
            expected_by_ref = {
                "other/repo#123": "iss-local-00002",
                "https://github.com/other/repo/issues/123": "iss-local-00002",
                "current/repo#123": "iss-local-00001",
                "https://github.com/current/repo/issues/123": "iss-local-00001",
            }
            for dep_ref, expected_dep in expected_by_ref.items():
                with self.subTest(dep_ref=dep_ref):
                    depends_meta_path = depends_issue_dir / ".meta.json"
                    depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
                    depends_meta["depends_on"] = [dep_ref]
                    self._write_json_force(depends_meta_path, depends_meta)
                    deps_result = self._run_runtime_capture(
                        target,
                        ["deps", "check", "--id", "iss-local-00003", "--json"],
                    )
                    self.assertEqual(
                        deps_result.returncode,
                        3,
                        msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
                    )
                    payload = json.loads(deps_result.stdout)
                    self.assertEqual(payload.get("effective_depends_on"), [expected_dep])
                    self.assertEqual(payload.get("blockers"), [expected_dep])

    def test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, _current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)
            self._materialize_local_issue_under_epic(epic_dir, local_num=3, title="Depends issue", github_issue_number=203)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            foreign_issue_dir = epic_dir / "issues" / "iss-local-00002-foreign-issue"
            foreign_meta_path = foreign_issue_dir / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {
                "issue_number": 123,
                "repo_owner": "other",
                "repo_name": "repo",
            }
            self._write_json_force(foreign_meta_path, foreign_meta)

            depends_issue_dir = epic_dir / "issues" / "iss-local-00003-depends-issue"
            depends_meta_path = depends_issue_dir / ".meta.json"
            depends_meta = json.loads(depends_meta_path.read_text(encoding="utf-8"))
            depends_meta["depends_on"] = [123]
            self._write_json_force(depends_meta_path, depends_meta)

            deps_result = self._run_runtime_capture(
                target,
                ["deps", "check", "--id", "iss-local-00003"],
            )
            self.assertEqual(
                deps_result.returncode,
                1,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            self.assertIn(
                "No node found for github.issue_number=123 in current repo scope (current/repo)",
                deps_result.stderr,
            )
            self.assertIn("Create/link the node first.", deps_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_keeps_sync_deps_active_validate_doctor_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            deps_result = self._run_runtime_capture(target, ["deps", "check", "--id", "iss-local-00001"])
            self.assertIn(
                deps_result.returncode,
                (0, 3),
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )
            self.assertTrue(
                "spec-dock: ok (deps check)" in deps_result.stdout
                or "spec-dock: blocked (deps check)" in deps_result.stderr,
                msg=f"deps stdout:\n{deps_result.stdout}\ndeps stderr:\n{deps_result.stderr}",
            )

            active_result = self._run_runtime_capture(target, ["active", "set", "--id", "iss-local-00001", "--force"])
            self.assertEqual(
                active_result.returncode,
                0,
                msg=f"active stdout:\n{active_result.stdout}\nactive stderr:\n{active_result.stderr}",
            )
            self.assertIn("spec-dock: ok (active set)", active_result.stdout)

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                0,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("spec-dock: ok (validate)", validate_result.stdout)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                0,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("spec-dock: ok (doctor) findings=0", doctor_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_keeps_lone_unscoped_legacy_without_backfill_parity(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)

            foreign_meta_path = epic_dir / "issues" / "iss-local-00002-foreign-issue" / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_meta_path, foreign_meta)

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])

    def test_checked_in_dogfooding_runtime_subprocess_keeps_readonly_lone_unscoped_without_backfill_parity(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("git not available")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, epic_dir, current_issue_dir = self._create_minimal_local_tree(target)
            self._materialize_local_issue_under_epic(epic_dir, local_num=2, title="Foreign issue", github_issue_number=202)

            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/current/repo.git"])

            current_meta_path = current_issue_dir / ".meta.json"
            current_meta = json.loads(current_meta_path.read_text(encoding="utf-8"))
            current_meta["github"] = {"issue_number": 123}
            self._write_json_force(current_meta_path, current_meta)
            current_meta_path.chmod(current_meta_path.stat().st_mode & ~0o222)

            foreign_meta_path = epic_dir / "issues" / "iss-local-00002-foreign-issue" / ".meta.json"
            foreign_meta = json.loads(foreign_meta_path.read_text(encoding="utf-8"))
            foreign_meta["github"] = {"issue_number": 123, "repo_owner": "other", "repo_name": "repo"}
            self._write_json_force(foreign_meta_path, foreign_meta)

            runtime_fs_repo = target / "spec-dock" / "scripts" / "spec_dock_runtime" / "infra" / "fs_repo.py"
            runtime_fs_repo.write_text(
                runtime_fs_repo.read_text(encoding="utf-8")
                + "\n\n"
                + "def _runtime_os_name() -> str:\n"
                + '    return "nt"\n',
                encoding="utf-8",
            )

            sync_result = self._run_runtime_capture(target, ["sync", "--github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )

            current_meta_after = json.loads(current_meta_path.read_text(encoding="utf-8"))
            self.assertEqual(current_meta_after["github"]["issue_number"], 123)
            self.assertNotIn("repo_owner", current_meta_after["github"])
            self.assertNotIn("repo_name", current_meta_after["github"])
            self.assertEqual(current_meta_path.stat().st_mode & 0o222, 0)

    def test_checked_in_dogfooding_runtime_subprocess_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("epic missing parent_id", validate_result.stderr)
            self.assertNotIn("Missing required artifact", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("epic missing parent_id", doctor_result.stderr)
            self.assertNotIn("Missing required artifact", doctor_result.stderr)

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_sync_fails_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed: Missing required artifact", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertNotIn("spec-dock: ok (sync)", sync_result.stdout)

    def test_checked_in_dogfooding_runtime_subprocess_import_fails_fast_when_required_artifact_missing(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            log_path = target / ".gh.log"
            self._make_gh_issue_view_stub(bin_dir, log_path=log_path)
            test_env = {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            import_result = self._run_runtime_capture(
                target,
                ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"],
                env=test_env,
            )
            self.assertEqual(
                import_result.returncode,
                1,
                msg=f"import stdout:\n{import_result.stdout}\nimport stderr:\n{import_result.stderr}",
            )
            self.assertIn("preflight validate failed", import_result.stderr)
            self.assertIn("Missing required artifact", import_result.stderr)
            self.assertIn("report.md", import_result.stderr)
            self.assertFalse(
                (
                    target
                    / "spec-dock"
                    / "initiatives"
                    / "init-local-00001-auth-platform"
                    / "epics"
                    / "epic-local-00001-jwt-auth"
                    / "issues"
                    / "iss-00123-imported-issue"
                ).exists()
            )
            if log_path.exists():
                self.assertEqual(log_path.read_text(encoding="utf-8").strip(), "")

    def test_checked_in_dogfooding_runtime_subprocess_import_partial_write_doctor_first_parity(self) -> None:
        if os.name == "nt":
            self.skipTest("This test uses a bash stub for gh; skip on Windows.")

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            self._create_minimal_local_tree(target)
            self._run_git(target, ["init"])
            self._run_git(target, ["remote", "add", "origin", "https://github.com/example/repo.git"])

            bin_dir = target / ".bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            self._make_gh_issue_view_stub(bin_dir)
            test_env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}

            runtime_scripts_dir = target / "spec-dock" / "scripts"
            check_code = f"""
import io
import os
import sys
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, {str(runtime_scripts_dir)!r})
try:
    from spec_dock_runtime import app as runtime_app
    from spec_dock_runtime.application import create_node as app_create_node
    from spec_dock_runtime.application import import_node as app_import_node
finally:
    sys.path.pop(0)

os.chdir({str(target)!r})
stderr_buffer = io.StringIO()
with patch.object(
    app_import_node,
    "execute_create_plan",
    side_effect=app_create_node.CreatePlanExecutionError(
        phase="scaffold_copied",
        message="simulated import partial write",
    ),
):
    with redirect_stderr(stderr_buffer):
        exit_code = runtime_app.main(
            ["import", "issue", "123", "--title", "Imported issue", "--epic", "epic-local-00001"]
        )

stderr_text = stderr_buffer.getvalue()
runtime_cmd = str((Path({str(target)!r}) / "spec-dock" / "scripts" / "spec-dock").resolve())
assert exit_code == 1, exit_code
assert "Outcome: import_local_write_fail." in stderr_text, stderr_text
assert "simulated import partial write" in stderr_text, stderr_text
assert "Import may have partially written local files. Do not rerun blindly." in stderr_text, stderr_text
assert f"{{runtime_cmd}} doctor" in stderr_text, stderr_text
assert "Recovery: rerun" not in stderr_text, stderr_text
"""
            result = subprocess.run(
                [sys.executable, "-c", check_code],
                cwd=str(target),
                capture_output=True,
                text=True,
                env=test_env,
            )
            self.assertEqual(result.returncode, 0, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")

    def test_checked_in_dogfooding_runtime_subprocess_sync_force_degrades_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)
            agent_dir = target / "spec-dock" / ".agent"

            (issue_dir / "report.md").chmod((issue_dir / "report.md").stat().st_mode | 0o200)
            (issue_dir / "report.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active", "--force"])
            self.assertEqual(
                sync_result.returncode,
                0,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("preflight validate failed", sync_result.stderr)
            self.assertIn("report.md", sync_result.stderr)
            self.assertTrue(
                "deps_preflight_failed" in sync_result.stderr or "DEPS_DISABLED" in sync_result.stderr,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("spec-dock: ok (sync)", sync_result.stdout)

            index = json.loads((agent_dir / "index.json").read_text(encoding="utf-8"))
            self.assertFalse(index["deps"]["valid"])
            self.assertIn("preflight validate failed", str(index["deps"]["error"]))

            tree = json.loads((agent_dir / "tree.json").read_text(encoding="utf-8"))
            self.assertFalse(tree["deps"]["valid"])
            self.assertIn("preflight validate failed", str(tree["deps"]["error"]))

    def test_checked_in_dogfooding_runtime_subprocess_sync_validation_boundary_prefers_structure_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)

            broken_epic_meta_path = epic_dir / ".meta.json"
            broken_epic_meta = json.loads(broken_epic_meta_path.read_text(encoding="utf-8"))
            broken_epic_meta.pop("parent_id", None)
            self._write_json_force(broken_epic_meta_path, broken_epic_meta)
            (initiative_dir / "report.md").chmod((initiative_dir / "report.md").stat().st_mode | 0o200)
            (initiative_dir / "report.md").unlink()
            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            sync_result = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_result.returncode,
                1,
                msg=f"sync stdout:\n{sync_result.stdout}\nsync stderr:\n{sync_result.stderr}",
            )
            self.assertIn("epic missing parent_id", sync_result.stderr)
            self.assertNotIn("Missing required artifact", sync_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_validate_doctor_fail_when_required_artifact_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _, _, issue_dir = self._create_minimal_local_tree(target)

            (issue_dir / "design.md").chmod((issue_dir / "design.md").stat().st_mode | 0o200)
            (issue_dir / "design.md").unlink()

            validate_result = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_result.returncode,
                1,
                msg=f"validate stdout:\n{validate_result.stdout}\nvalidate stderr:\n{validate_result.stderr}",
            )
            self.assertIn("Missing required artifact", validate_result.stderr)
            self.assertIn("design.md", validate_result.stderr)

            doctor_result = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_result.returncode,
                1,
                msg=f"doctor stdout:\n{doctor_result.stdout}\ndoctor stderr:\n{doctor_result.stderr}",
            )
            self.assertIn("[missing_artifact] Missing required artifact", doctor_result.stderr)
            self.assertIn("design.md", doctor_result.stderr)

    def test_checked_in_dogfooding_runtime_subprocess_create_lock_missing_meta_diagnosis_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._overlay_checked_in_dogfooding_runtime(target)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)

            meta_path = issue_dir / ".meta.json"
            meta_path.chmod(meta_path.stat().st_mode | 0o200)
            meta_path.unlink()

            lock_path = target / "spec-dock" / "system" / ".runtime" / "create.lock"
            lock_path.parent.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(
                "\n".join(
                    [
                        "token=active",
                        "pid=1234",
                        "user=tester",
                        "created_unix=9999999999",
                        "created_iso=2286-11-20T17:46:39Z",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            validate_in_progress = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_in_progress.returncode,
                1,
                msg=f"validate(in_progress) stdout:\n{validate_in_progress.stdout}\nvalidate(in_progress) stderr:\n{validate_in_progress.stderr}",
            )
            self.assertIn("Create in-progress state detected", validate_in_progress.stderr)
            self.assertNotIn("Missing required artifact", validate_in_progress.stderr)

            sync_in_progress = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_in_progress.returncode,
                1,
                msg=f"sync(in_progress) stdout:\n{sync_in_progress.stdout}\nsync(in_progress) stderr:\n{sync_in_progress.stderr}",
            )
            self.assertIn("Create in-progress state detected", sync_in_progress.stderr)

            doctor_in_progress = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_in_progress.returncode,
                1,
                msg=f"doctor(in_progress) stdout:\n{doctor_in_progress.stdout}\ndoctor(in_progress) stderr:\n{doctor_in_progress.stderr}",
            )
            self.assertIn("[stale_create_lock]", doctor_in_progress.stderr)
            self.assertIn("Create in-progress state detected", doctor_in_progress.stderr)
            self.assertNotIn("[missing_artifact]", doctor_in_progress.stderr)

            lock_path.write_text(
                "\n".join(
                    [
                        "token=stale",
                        "pid=4321",
                        "user=tester",
                        "created_unix=0",
                        "created_iso=1970-01-01T00:00:00Z",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            validate_stale = self._run_runtime_capture(target, ["validate"])
            self.assertEqual(
                validate_stale.returncode,
                1,
                msg=f"validate(stale) stdout:\n{validate_stale.stdout}\nvalidate(stale) stderr:\n{validate_stale.stderr}",
            )
            self.assertIn("Stale create-lock state detected", validate_stale.stderr)
            self.assertNotIn("Missing required artifact", validate_stale.stderr)

            sync_stale = self._run_runtime_capture(target, ["sync", "--no-github", "--no-update-active"])
            self.assertEqual(
                sync_stale.returncode,
                1,
                msg=f"sync(stale) stdout:\n{sync_stale.stdout}\nsync(stale) stderr:\n{sync_stale.stderr}",
            )
            self.assertIn("Stale create-lock state detected", sync_stale.stderr)

            doctor_stale = self._run_runtime_capture(target, ["doctor"])
            self.assertEqual(
                doctor_stale.returncode,
                1,
                msg=f"doctor(stale) stdout:\n{doctor_stale.stdout}\ndoctor(stale) stderr:\n{doctor_stale.stderr}",
            )
            self.assertIn("[stale_create_lock]", doctor_stale.stderr)
            self.assertIn("Stale create-lock state detected", doctor_stale.stderr)
            self.assertNotIn("[missing_artifact]", doctor_stale.stderr)

    def test_update_rebuilds_active_entrypoints_from_persisted_manifest_when_valid_and_active_dir_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)
            self.assertIn("- state (github default): `./spec-dock/scripts/spec-dock sync`", context_pack_text)
            self.assertIn(
                "- state (cache/local opt-out): `./spec-dock/scripts/spec-dock sync --no-github`",
                context_pack_text,
            )
            self.assertNotIn("- state (local): `./spec-dock/scripts/spec-dock sync`", context_pack_text)
            self.assertNotIn("- state (github): `./spec-dock/scripts/spec-dock sync --github`", context_pack_text)

    def test_update_rebuilds_placeholder_symlink_entrypoints_from_persisted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                pathfile = active_dir / f"{layer}.path"
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                pathfile.unlink(missing_ok=True)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                os.symlink(rel_placeholder, link)
                self.assertTrue(link.is_symlink())

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    self.assertTrue(link.exists())
                    self.assertEqual(link.resolve(), expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_rebuilds_placeholder_pathfile_entrypoints_from_persisted_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_placeholder + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    if link.exists():
                        self.assertEqual(link.resolve(), expected.resolve())
                    else:
                        self.assertTrue(pathfile.is_file())
                        resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                        self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_mixed_entrypoints_keep_healthy_real_and_rebuild_placeholder_layers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)

            (active_dir / "initiative.path").write_text(
                os.path.relpath(initiative_dir, start=active_dir) + "\n",
                encoding="utf-8",
            )
            (active_dir / "epic.path").write_text(
                os.path.relpath(placeholder_root / "epic", start=active_dir) + "\n",
                encoding="utf-8",
            )
            (active_dir / "issue.path").write_text(
                os.path.relpath(placeholder_root / "issue", start=active_dir) + "\n",
                encoding="utf-8",
            )

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)

    def test_update_keeps_placeholder_and_none_context_pack_when_persisted_manifest_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"
            placeholder_root = target / "spec-dock" / "system" / "active-none"

            for layer in ("initiative", "epic", "issue"):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_placeholder + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- entry: `spec-dock/.agent/active.json`", context_pack_text)
            self.assertIn("- default working set: `spec-dock/.agent/index.json`", context_pack_text)
            self.assertIn("- default dependency view: `spec-dock/.agent/deps-issues.json`", context_pack_text)
            self.assertIn("- escalation only: `spec-dock/.agent/index-all.json`", context_pack_text)
            self.assertIn("- Start with `spec-dock/.agent/active.json`.", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/README.md`", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_rewrites_stale_context_pack_when_rebuilding_active_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            # Simulate partial deletion: entrypoints disappeared but stale context-pack remains.
            for name in ("initiative", "epic", "issue", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.write_text(
                "# Context Pack (stale)\n\n## Active\n- initiative: (none)\n- epic: (none)\n- issue: (none)\n",
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_entrypoints_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            active_dir = target / "spec-dock" / "active"
            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_skips_persisted_target_resolution_when_active_entrypoints_are_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            with patch(
                "spec_dock.cli._resolve_manifest_target_dir",
                side_effect=AssertionError("healthy active entrypoint should skip persisted target resolution"),
            ):
                self.assertEqual(main(["update", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)

    def test_update_regenerates_context_pack_from_existing_active_entrypoints_when_manifest_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            self._create_minimal_local_tree(target)
            self._run_runtime(target, ["active", "set", "--id", "iss-local-00001", "--force"])

            active_dir = target / "spec-dock" / "active"
            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_keeps_context_pack_aligned_with_existing_active_pathfiles_when_persisted_manifest_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing",
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            for layer, node_dir in (
                ("initiative", initiative_dir),
                ("epic", epic_dir),
                ("issue", issue_dir),
            ):
                link = active_dir / layer
                if link.is_symlink() or link.is_file():
                    link.unlink(missing_ok=True)
                elif link.is_dir():
                    shutil.rmtree(link)
                rel_target = os.path.relpath(node_dir, start=active_dir)
                (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "report.md"))

    def test_update_recovers_active_entrypoints_from_id_when_persisted_paths_are_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, _issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-00001", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-00001",
                        "path": "spec-dock/initiatives/init-local-00001-auth-platform/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": (
                            "spec-dock/initiatives/init-local-00001-auth-platform/epics/"
                            "epic-local-00001-jwt-auth/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertIn("init-local-00001", self._read_active_pointer_text(target, "initiative", "requirement.md"))
            self.assertIn("epic-local-00001", self._read_active_pointer_text(target, "epic", "requirement.md"))
            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "requirement.md"))

    def test_update_falls_back_to_placeholder_when_persisted_active_manifest_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/README.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_falls_back_to_placeholder_when_persisted_path_points_to_same_layer_wrong_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            wrong_issue_dir = issue_dir.parent / "iss-local-00002-other-issue"
            wrong_issue_dir.mkdir(parents=True, exist_ok=True)
            self._write_json_force(
                wrong_issue_dir / ".meta.json",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00002",
                    "title": "Other issue",
                    "slug": "other-issue",
                    "parent_id": "epic-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": "epic-local-00001",
                },
            )
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                (wrong_issue_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": wrong_issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: (none)", context_pack_text)
            self.assertNotIn("iss-local-00002", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_prefers_id_based_recovery_when_same_layer_wrong_id_path_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            wrong_issue_dir = issue_dir.parent / "iss-local-00002-other-issue"
            wrong_issue_dir.mkdir(parents=True, exist_ok=True)
            self._write_json_force(
                wrong_issue_dir / ".meta.json",
                {
                    "schema_version": 1,
                    "type": "issue",
                    "id": "iss-local-00002",
                    "title": "Other issue",
                    "slug": "other-issue",
                    "parent_id": "epic-local-00001",
                    "initiative_id": "init-local-00001",
                    "epic_id": "epic-local-00001",
                },
            )
            for filename in ("requirement.md", "design.md", "plan.md", "report.md"):
                (wrong_issue_dir / filename).write_text(f"{filename}\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": wrong_issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertIn("iss-local-00001", self._read_active_pointer_text(target, "issue", "requirement.md"))
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-00002", context_pack_text)

    def test_update_bootstraps_active_fallback_entrypoints_when_active_dir_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])
            self.assertEqual(main(["update", str(target)]), 0)

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                (placeholder_root / "initiative" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "README.md"),
                (placeholder_root / "epic" / "README.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "README.md"),
                (placeholder_root / "issue" / "README.md").read_text(encoding="utf-8"),
            )
            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: (none)", context_pack_text)
            self.assertIn("- epic: (none)", context_pack_text)
            self.assertIn("- issue: (none)", context_pack_text)

    def test_update_regenerates_context_pack_from_persisted_active_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            context_pack_path = active_dir / "context-pack.md"
            context_pack_path.unlink(missing_ok=True)
            self.assertFalse(context_pack_path.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            context_pack_text = context_pack_path.read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertIn("- `spec-dock/active/initiative/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/epic/requirement.md`", context_pack_text)
            self.assertIn("- `spec-dock/active/issue/report.md`", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertNotIn("- `spec-dock/active/issue/README.md`", context_pack_text)

    def test_update_bootstraps_active_path_files_when_active_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            for name in ("initiative", "epic", "issue", "context-pack.md", "initiative.path", "epic.path", "issue.path"):
                p = active_dir / name
                if p.is_symlink() or p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p)

            self.assertEqual(list(active_dir.iterdir()), [])

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent.resolve() == active_dir.resolve() and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_rebuilds_active_path_files_from_persisted_manifest_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent.resolve() == active_dir.resolve() and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    pathfile = active_dir / f"{layer}.path"
                    self.assertFalse(link.exists())
                    self.assertFalse(link.is_symlink())
                    self.assertTrue(pathfile.is_file())
                    resolved = (active_dir / pathfile.read_text(encoding="utf-8").strip()).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)

    def test_update_repairs_stale_active_path_files_to_persisted_targets_when_symlink_creation_fails(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-00001",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-00001",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent.resolve() == active_dir.resolve() and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            expected_paths = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, expected in expected_paths.items():
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, expected.resolve())

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

    def test_update_repairs_stale_active_path_files_to_placeholder_when_persisted_manifest_broken_and_symlink_creation_fails(
        self,
    ) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = self._clear_active_entrypoints(target)

            stale_rel = "../system/active-none/missing-node"
            for layer in ("initiative", "epic", "issue"):
                (active_dir / f"{layer}.path").write_text(stale_rel + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {
                        "id": "init-local-99999",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                    "epic": {
                        "id": "epic-local-99999",
                        "path": initiative_dir.relative_to(target).as_posix(),
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": epic_dir.relative_to(target).as_posix(),
                    },
                },
            )

            original_symlink = cli.os.symlink

            def _fail_active_symlink(src: str | bytes, dst: str | bytes, *args, **kwargs) -> None:
                dst_path = Path(dst)
                if dst_path.parent.resolve() == active_dir.resolve() and dst_path.name in {"initiative", "epic", "issue"}:
                    raise OSError("simulated active symlink failure")
                original_symlink(src, dst, *args, **kwargs)

            cli.os.symlink = _fail_active_symlink
            try:
                self.assertEqual(main(["update", str(target)]), 0)
            finally:
                cli.os.symlink = original_symlink

            placeholder_root = target / "spec-dock" / "system" / "active-none"
            for layer in ("initiative", "epic", "issue"):
                with self.subTest(layer=layer):
                    pathfile = active_dir / f"{layer}.path"
                    self.assertTrue(pathfile.is_file())
                    rel_target = pathfile.read_text(encoding="utf-8").strip()
                    self.assertNotEqual(rel_target, stale_rel)
                    resolved = (active_dir / rel_target).resolve()
                    self.assertEqual(resolved, (placeholder_root / layer).resolve())
                    self.assertEqual(
                        self._read_active_pointer_text(target, layer, "README.md"),
                        (placeholder_root / layer / "README.md").read_text(encoding="utf-8"),
                    )

    def test_update_prefers_existing_active_entrypoints_over_stale_persisted_manifest_for_context_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            active_dir = target / "spec-dock" / "active"

            # Keep healthy entrypoints via pathfiles, then inject stale persisted ids.
            entry_targets = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, target_dir in entry_targets.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    if link.is_symlink() or link.is_file():
                        link.unlink(missing_ok=True)
                    elif link.is_dir():
                        shutil.rmtree(link)
                    rel_target = os.path.relpath(target_dir, start=active_dir)
                    (active_dir / f"{layer}.path").write_text(rel_target + "\n", encoding="utf-8")

            self._write_json_force(
                target / "spec-dock" / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_prefers_real_pathfile_entrypoint_over_placeholder_symlink_when_manifest_is_stale(self) -> None:
        import spec_dock.cli as cli

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)
            initiative_dir, epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            placeholder_root = specdock_dir / "system" / "active-none"

            entry_targets = {
                "initiative": initiative_dir,
                "epic": epic_dir,
                "issue": issue_dir,
            }
            for layer, target_dir in entry_targets.items():
                with self.subTest(layer=layer):
                    link = active_dir / layer
                    if link.is_symlink() or link.is_file():
                        link.unlink(missing_ok=True)
                    elif link.is_dir():
                        shutil.rmtree(link)
                    rel_placeholder = os.path.relpath(placeholder_root / layer, start=active_dir)
                    os.symlink(rel_placeholder, link)
                    rel_real = os.path.relpath(target_dir, start=active_dir)
                    (active_dir / f"{layer}.path").write_text(rel_real + "\n", encoding="utf-8")

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )

            self.assertEqual(main(["update", str(target)]), 0)

            expected_ids = {
                "initiative": "init-local-00001",
                "epic": "epic-local-00001",
                "issue": "iss-local-00001",
            }
            for layer, expected_id in expected_ids.items():
                with self.subTest(layer=layer):
                    pointer = active_dir / layer
                    self.assertTrue(pointer.is_symlink())
                    self.assertEqual(pointer.resolve(), entry_targets[layer].resolve())

                    resolved = cli._resolve_existing_active_entrypoint(
                        specdock_dir,
                        active_dir=active_dir,
                        layer=layer,
                    )
                    self.assertIsNotNone(resolved)
                    if resolved is None:
                        continue
                    self.assertEqual(resolved[1], expected_id)

            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "requirement.md"),
                (initiative_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "epic", "requirement.md"),
                (epic_dir / "requirement.md").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- initiative: init-local-00001", context_pack_text)
            self.assertIn("- epic: epic-local-00001", context_pack_text)
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("- initiative: (none)", context_pack_text)
            self.assertNotIn("- epic: (none)", context_pack_text)
            self.assertNotIn("- issue: (none)", context_pack_text)
            self.assertNotIn("init-local-99999", context_pack_text)
            self.assertNotIn("epic-local-99999", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_same_layer_non_symlink_file_conflict_using_real_pathfile_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            issue_link = active_dir / "issue"
            issue_pathfile = active_dir / "issue.path"

            if issue_link.is_symlink() or issue_link.is_file():
                issue_link.unlink(missing_ok=True)
            elif issue_link.is_dir():
                shutil.rmtree(issue_link)
            issue_pathfile.unlink(missing_ok=True)

            issue_pathfile.write_text(os.path.relpath(issue_dir, start=active_dir) + "\n", encoding="utf-8")
            issue_link.write_text("stale non-symlink conflict\n", encoding="utf-8")
            self.assertTrue(issue_link.exists())
            self.assertFalse(issue_link.is_symlink())

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-99999",
                        "path": (
                            "spec-dock/initiatives/init-local-99999-missing/epics/"
                            "epic-local-99999-missing/issues/iss-local-99999-missing"
                        ),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            if issue_link.exists():
                self.assertTrue(issue_link.is_symlink())
                self.assertEqual(issue_link.resolve(), issue_dir.resolve())
            else:
                self.assertTrue(issue_pathfile.is_file())
                rel_target = issue_pathfile.read_text(encoding="utf-8").strip()
                self.assertEqual((active_dir / rel_target).resolve(), issue_dir.resolve())
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_same_layer_invalid_directory_conflict_using_real_pathfile_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(main(["init", str(target)]), 0)
            _initiative_dir, _epic_dir, issue_dir = self._create_minimal_local_tree(target)
            specdock_dir = target / "spec-dock"
            active_dir = specdock_dir / "active"
            placeholder_root = specdock_dir / "system" / "active-none"
            issue_link = active_dir / "issue"
            issue_pathfile = active_dir / "issue.path"

            if issue_link.is_symlink() or issue_link.is_file():
                issue_link.unlink(missing_ok=True)
            elif issue_link.is_dir():
                shutil.rmtree(issue_link)
            issue_pathfile.unlink(missing_ok=True)

            issue_link.mkdir(parents=True, exist_ok=True)
            (issue_link / "report.md").write_text("stale invalid directory conflict\n", encoding="utf-8")
            self.assertFalse((issue_link / ".meta.json").exists())
            issue_pathfile.write_text(
                os.path.relpath(placeholder_root / "issue", start=active_dir) + "\n",
                encoding="utf-8",
            )
            self.assertTrue(issue_link.exists())
            self.assertFalse(issue_link.is_symlink())

            self._write_json_force(
                specdock_dir / ".agent" / "active.json",
                {
                    "schema_version": 2,
                    "initiative": {"id": "init-local-99999", "path": "spec-dock/initiatives/init-local-99999-missing"},
                    "epic": {
                        "id": "epic-local-99999",
                        "path": "spec-dock/initiatives/init-local-99999-missing/epics/epic-local-99999-missing",
                    },
                    "issue": {
                        "id": "iss-local-00001",
                        "path": issue_dir.relative_to(target).as_posix(),
                    },
                },
            )
            (active_dir / "context-pack.md").write_text(
                (
                    "# Context Pack (stale)\n\n"
                    "## Active\n"
                    "- initiative: init-local-99999\n"
                    "- epic: epic-local-99999\n"
                    "- issue: iss-local-99999\n"
                ),
                encoding="utf-8",
            )

            self.assertEqual(main(["update", str(target)]), 0)

            if issue_link.exists():
                self.assertTrue(issue_link.is_symlink())
                self.assertEqual(issue_link.resolve(), issue_dir.resolve())
            else:
                self.assertTrue(issue_pathfile.is_file())
                rel_target = issue_pathfile.read_text(encoding="utf-8").strip()
                self.assertEqual((active_dir / rel_target).resolve(), issue_dir.resolve())
            self.assertEqual(
                self._read_active_pointer_text(target, "issue", "report.md"),
                (issue_dir / "report.md").read_text(encoding="utf-8"),
            )

            context_pack_text = (active_dir / "context-pack.md").read_text(encoding="utf-8")
            self.assertIn("- issue: iss-local-00001", context_pack_text)
            self.assertNotIn("iss-local-99999", context_pack_text)

    def test_update_repairs_dangling_active_symlink_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            if not self._can_create_symlink(target):
                self.skipTest("symlink is not supported in this environment")

            self.assertEqual(main(["init", str(target)]), 0)

            active_dir = target / "spec-dock" / "active"
            pointer = active_dir / "initiative"
            pointer.unlink(missing_ok=True)
            os.symlink("../system/active-none/missing-initiative", pointer)
            self.assertTrue(pointer.is_symlink())
            self.assertFalse(pointer.exists())

            self.assertEqual(main(["update", str(target)]), 0)

            placeholder = target / "spec-dock" / "system" / "active-none" / "initiative" / "README.md"
            self.assertEqual(
                self._read_active_pointer_text(target, "initiative", "README.md"),
                placeholder.read_text(encoding="utf-8"),
            )
