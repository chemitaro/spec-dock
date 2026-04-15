---
種別: 実装報告書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 実装報告（LOG）

## 実装サマリー
- `install_root` を正本として、Codex/Copilot の multi-host agent/config inventory を追加した。
- `spec-manager` canonical specialist を導入し、Copilot primary を `orchestrator.agent.md` に固定した。
- installer に `bootstrap_only_exact_file_paths` を追加し、`.codex/config.toml` を init 生成 / update preserve へ変更した。
- obsolete managed paths（旧 `spec-dock` canonical など）の prune 契約を metadata と tests で固定した。
- dogfooding parity のため repo root `.agents/.codex/.github` を install_root と整合する状態に更新した。

## 実装記録（セッションログ）

### 2026-04-15 13:20 - review follow-up repair

#### 対象
- Step: PR #76 review follow-up
- Findings:
  - `pr-monitor` helper path がインストール先 repo に存在しない固定絶対パスを参照していた
  - bootstrap-only `.codex/config.toml` が preflight exact symlink rejection に先に遮られ、preserve semantics に到達できなかった

#### 実施内容
- `pr-monitor` guidance の helper path を provider asset / dogfooding mirror の両方で `./.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh` に統一した。
- `src/spec_dock/cli.py` の preflight に bootstrap-only current managed path を渡し、`.codex/config.toml` の exact symlink が file を指す場合だけ narrow exemption で許可するようにした。
- broken symlink / non-file symlink / symlink parent は従来どおり reject-before-writes を維持するよう、installer tests を追加した。
- `tests/test_init_update.py` に `pr-monitor` helper path contract と bootstrap-only symlink contract の回帰 test を追加した。

#### 実行コマンド / 結果
```bash
PYTHONPATH=src python -m unittest \
  tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_issue_75_init_allows_bootstrap_only_exact_file_symlink \
  tests.test_init_update.TestInitUpdate.test_issue_75_update_allows_bootstrap_only_exact_file_symlink \
  tests.test_init_update.TestInitUpdate.test_issue_75_init_rejects_bootstrap_only_broken_symlink_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_75_init_rejects_bootstrap_only_non_file_symlink_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_75_pr_monitor_guidance_uses_repo_relative_helper_path
# OK (7 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

#### レビュー分析
- Copilot review:
  - 妥当
  - 4 comments は同一論点であり、`pr-monitor` guidance の broken absolute path を指摘していた
- Codex review:
  - 妥当
  - bootstrap-only `.codex/config.toml` の symlink repo で `init/update` が失敗する regression を指摘していた
- verdict:
  - どちらも修正対象
  - scope は上記 2 論点のみに限定した

### 2026-04-15 12:30 - spec-manager command-operator enrichment

#### 対象
- Step: follow-up contract enrichment
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003

#### 実施内容
- issue docs を follow-up scope に切り替え、`spec-manager = command operator`、`main orchestrator = docs/context owner` の split を正本化した。
- Codex / Copilot の `spec-manager` を、thin adapter 委譲を維持したまま command-only operator として rich 化した。
  - command surface
  - read order
  - docs authoring / manual edit prohibition
  - completion boundary
- Codex 側には `gpt-5.4-mini`、`high` reasoning、`notify = []`、`shell_tool = true` を追加した。
- Copilot 側には `model: gpt-5.4-mini`、`tools: ['read', 'search', 'execute', 'todo']`、`user-invocable: false` を固定した。
- main guidance（Codex bootstrap / Codex main config / Copilot orchestrator）に、SpecDock command operation は原則 `spec-manager` へ送ることと、docs authoring は main 側責務であることを追加した。
- `tests/test_init_update.py` の helper と contract assertions を更新し、thin shim 前提ではなく richer operator contract を guard する形へ切り替えた。
- `PYTHONPATH=src python -m spec_dock.cli update .` 実行時に scope 外の旧 docs deletion が発生したため、該当 files は `HEAD` 内容で復元し、最終差分を current scope に戻した。

#### 実行コマンド / 結果
```bash
PYTHONPATH=src python -m spec_dock.cli update .
# spec-dock: ok (update) -> /srv/mount/spec-dock

PYTHONPATH=src python -m unittest \
  tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_update_manages_native_shims_with_gate_2_five_subchecks
# OK (3 tests)

PYTHONPATH=src python -m unittest \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_update_manages_native_shims_with_gate_2_five_subchecks
# OK (4 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

#### 変更したファイル
- provider assets:
  - `src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml`
  - `src/spec_dock/assets/install_root/.github/agents/spec-manager.agent.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/config.toml`
  - `src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md`
- tests:
  - `tests/test_init_update.py`
- issue docs:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
- dogfooding mirror:
  - `.codex/AGENTS.md`
  - `.codex/config.toml`
  - `.codex/agents/spec-manager.toml`
  - `.github/agents/orchestrator.agent.md`
  - `.github/agents/spec-manager.agent.md`

#### レビュー
- manual diff review:
  - pass
  - `spec-manager` が command operator に限定され、main guidance に docs-owner split が入っていることを確認した。
- targeted regression:
  - pass
- validate:
  - pass

#### コミット
- なし

### 2026-04-15 12:45 - codex main config wording trim

#### 対象
- Step: follow-up wording refinement

#### 実施内容
- `.codex/config.toml` のオーケストレーター責務に追加していた 3 行を、`spec-manager` への command delegation だけを残す 1 行へ圧縮した。
- docs-owner split の説明は `.codex/AGENTS.md` と Copilot orchestrator 側に残し、Codex main config からは重複説明を削除した。
- `tests/test_init_update.py` の Codex main config assertion と issue design wording を新しい簡潔版へ合わせた。

#### 実行コマンド / 結果
```bash
PYTHONPATH=src python -m unittest \
  tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract
# OK (2 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

### 2026-04-15 11:00 - naming scope reset

#### 対象
- Step: current-session scope alignment
- AC/EC: AC-001, AC-002, AC-003

#### 実施内容
- 現セッションの実装対象を agent pack の kebab-case naming unification のみに限定する方針で issue docs を更新した。
- `spec-manager` の文言整理や host-specific config 強化は follow-up として切り離した。

#### 実行コマンド / 結果
```bash
# docs-only alignment; no runtime command executed
```

#### 変更したファイル
- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`
- `spec-dock/active/issue/report.md`

#### レビュー
- pending

#### コミット
- なし

### 2026-04-15 11:00 - kebab-case naming unification

#### 対象
- Step: S01 naming-only execution slice
- AC/EC: AC-001, AC-002, AC-003

#### 実施内容
- Codex / GitHub Copilot の agent pack で snake_case role filenames / internal names を kebab-case に統一した。
- `spec-manager` は名前維持とし、本文・model・notify・MCP などの rich化は未着手のまま切り分けた。
- provider-side assets、repo root dogfooding mirror、installer metadata、role 名参照、`tests/test_init_update.py` の inventory / prune expectations を rename 契約へ揃えた。
- `meta.json` の obsolete list に旧 snake_case managed paths を追加し、update 時 prune 対象にした。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_handoff_surface_inventories_match tests.test_init_update.TestInitUpdate.test_init_installs_host_adapter_metadata_with_fixed_contract tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_exact_file_path
# OK

PYTHONPATH=src python -m spec_dock.cli update .
# spec-dock: ok (update) -> /srv/mount/spec-dock

python -m unittest tests.test_init_update -f
# OK (151 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

#### 変更したファイル
- provider assets:
  - `src/spec_dock/assets/install_root/.codex/agents/*.toml` の rename 対象 9 files
  - `src/spec_dock/assets/install_root/.github/agents/*.agent.md` の rename 対象 8 files
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `src/spec_dock/assets/install_root/.codex/config.toml`
  - `src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md`
  - `src/spec_dock/assets/install_root/.codex/agents/researcher.toml`
  - `src/spec_dock/assets/install_root/.github/agents/researcher.agent.md`
  - `src/spec_dock/assets/install_root/.agents/skills/git-commit-conventional-ja/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
- dogfooding mirror:
  - `.codex/agents/*.toml` の同名 rename 対象
  - `.github/agents/*.agent.md` の同名 rename 対象
  - `.agents/host-adapters/meta.json`
  - `.codex/config.toml`
  - `.github/agents/orchestrator.agent.md`
  - `.codex/agents/researcher.toml`
  - `.github/agents/researcher.agent.md`
  - `.agents/skills/git-commit-conventional-ja/SKILL.md`
  - `.agents/skills/github-pr-creator/SKILL.md`
- tests:
  - `tests/test_init_update.py`

#### レビュー
- manual diff review:
  - pass
  - rename 対象の残存 snake_case は `meta.json` の obsolete paths とそれを検証する test fixture のみであることを確認した。
- automated validation:
  - pass

#### コミット
- なし

#### メモ
- `spec-dock update .` は shell PATH 上の `spec-dock` が無かったため、`PYTHONPATH=src python -m spec_dock.cli update .` を使用した。
- update に巻き込まれた scope 外 docs 削除は restore 済みで、最終差分は naming unification に閉じている。

### 2026-04-15 00:00 - 00:00

#### 対象
- Step: readiness / issue creation
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- `spec-dock new issue --create-github-issue --epic epic-00074 --title 'Multi host agent and config asset install'` で issue `iss-00075` / GitHub `#75` を作成した。
- issue docs を approved state に更新し、Codex / Copilot host pack placement、shared skills、prune safety、docs/report boundary を明文化した。
- `active set --checkout` と validate / sync を通す前提条件を整えた。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock new issue --create-github-issue --epic epic-00074 --title 'Multi host agent and config asset install'
# ok (new issue) id=iss-00075 epic=epic-00074 initiative=init-local-00002 path=spec-dock/spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install github=#75
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/requirement.md`
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/design.md`
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/plan.md`
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/report.md`

#### レビュー
- spec review:
  - pending
- code review:
  - pending

#### コミット
- なし

#### メモ
- この report は issue creation の readiness evidence を残すための初期記録であり、実装実績はまだない。

### 2026-04-15 00:00 - 00:00

#### 対象
- Step: S01 / S90 / S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- `src/spec_dock/assets/install_root/` に Codex managed inventory、Copilot managed inventory、shared skills（`git-commit-conventional-ja` / `github-codex-pr-review-comments` / `github-pr-creator`）を追加。
- `spec-manager` canonical specialist を新規配置し、旧 `spec-dock` specialist assets を install_root から除去。
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を最小拡張し、`bootstrap_only_exact_file_paths` と obsolete list を更新。
- `src/spec_dock/cli.py` に bootstrap-only path 解釈と copy preserve を追加し、canonical target constants を更新。
- `tests/test_init_update.py` と `tests/cli_runtime/harness.py` を新 inventory/canonical/bootstrap 契約に整合させた。
- repo root `.agents/.codex/.github` を install_root mirror に同期し、dogfooding parity を維持。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update -f
# OK (151 tests)

python -m unittest tests.test_cli tests.cli_runtime.test_active tests.cli_runtime.test_deps tests.cli_runtime.test_import tests.cli_runtime.test_new tests.cli_runtime.test_sync tests.cli_runtime.test_validate
# OK (248 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
- `src/spec_dock/assets/install_root/.agents/skills/git-commit-conventional-ja/**`
- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/**`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/**`
- `src/spec_dock/assets/install_root/.codex/AGENTS.md`
- `src/spec_dock/assets/install_root/.codex/config.toml`
- `src/spec_dock/assets/install_root/.codex/agents/*.toml`（`spec-manager.toml` 含む）
- `src/spec_dock/assets/install_root/.github/agents/*.agent.md`（`orchestrator.agent.md`, `spec-manager.agent.md` 含む）
- `src/spec_dock/assets/install_root/.codex/agents/spec-dock.toml`（削除）
- `src/spec_dock/assets/install_root/.github/agents/spec-dock.agent.md`（削除）
- `src/spec_dock/cli.py`
- `tests/cli_runtime/harness.py`
- `tests/test_init_update.py`
- `.agents/**`, `.codex/**`, `.github/agents/**`, `.agents/host-adapters/meta.json`（dogfooding parity mirror）

#### レビュー
- spec review:
  - pass（issue docs）
- code/test review:
  - targeted test suite pass

#### コミット
- pending

#### メモ
- Copilot orchestrator は static delegation shim ではないため、テストを orchestrator contract 検証へ更新した。

### 2026-04-15 00:00 - 00:00（follow-up fix）

#### 対象
- Step: follow-up quality fix after reviewer findings
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002

#### 実施内容
- Copilot primary orchestrator の frontmatter から `disable-model-invocation: true` を除去し、provider asset と repo root mirror の parity を維持した。
- QA 指摘に対応して `tests/test_init_update.py` を最小拡張した。
  - bootstrap-only `.codex/config.toml` の update preserve を直接検証
  - obsolete prune に旧 canonical（`.codex/agents/spec-dock.toml`, `.github/agents/spec-dock.agent.md`）の削除検証を追加
  - Codex direct orchestrator（`.codex/agents/orchestrator.toml`）非生成の否定検証を追加
  - dogfooding parity を host-pack 全量比較（inventory + bytes）に強化
- Copilot orchestrator contract assertion に `disable-model-invocation: true` 不可を追加し、再発防止を明文化した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_init_generated_native_shims_satisfy_static_delegation_only_contract tests.test_init_update.TestInitUpdate.test_update_manages_native_shims_with_gate_2_five_subchecks
# OK (4 tests)

python -m unittest tests.test_init_update -f
# OK (151 tests)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=31
```

#### 変更したファイル
- `src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md`
- `.github/agents/orchestrator.agent.md`
- `tests/test_init_update.py`
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/issues/iss-00075-multi-host-agent-and-config-asset-install/report.md`

#### レビュー
- code review finding:
  - resolved（orchestrator frontmatter 契約）
- qa findings:
  - resolved（4件）

#### コミット
- pending
