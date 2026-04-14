---
種別: 要件定義書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 要件定義（WHAT / WHY）

## 目的
- 既存 installer foundation の additive change として、Codex pack、GitHub Copilot pack、shared skills を `install_root` から install/update/prune できる状態にする。
- exact inventory、ownership、metadata delta、prune/preserve behavior を固定し、1 issue で実装から validation まで閉じる。

## 背景・現状
- 現状の挙動:
  - `src/spec_dock/assets/install_root/` は shared skills と host native shim だけを正本として持ち、`spec-dock update` は `install_root` 再帰列挙を current managed file set として同期する。
  - canonical host file は Codex が `.codex/agents/spec-dock.toml`、Copilot が `.github/agents/spec-dock.agent.md` に固定されている。
  - obsolete cleanup は `.agents/host-adapters/meta.json` の `managed_assets.obsolete_exact_file_paths` だけを使う。
- 現状の課題:
  - epic で確定した `spec-manager` rename、Copilot `orchestrator` primary、Codex bootstrap-only `config.toml`、shared skills 追加を current installer contract がまだ表現できていない。
  - `config.toml` をそのまま current managed として扱うと update ごとに user edit を潰してしまう。
  - discussion 側 reference input はあるが、provider-side source of truth と install target mapping が issue 契約として未固定である。
- 情報源:
  - `spec-dock/active/epic/{requirement.md,design.md,plan.md}`
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `spec-dock/.../discussions/add-codex/.codex/**`
  - `spec-dock/.../discussions/add-githobcopilot/agents/**`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - provider-side maintainer
  - `spec-dock init/update` を実行する consumer repo maintainer
- 代表シナリオ:
  1. maintainer が provider-side `install_root` に host pack assets を追加する。
  2. consumer repo で `spec-dock init` または `spec-dock update` を実行する。
  3. Codex/Copilot/shared skills が正しい project path に配置される。
  4. update 時は obsolete managed path だけが prune され、unknown custom files と編集済み `.codex/config.toml` は保持される。

## スコープ
- MUST:
  - `src/spec_dock/assets/install_root/` を provider-side source of truth として更新する。
  - Codex pack の exact inventory を install/update 対象として追加する。
  - GitHub Copilot pack の exact inventory を install/update 対象として追加する。
  - shared skills の exact inventory を `.agents/skills/` に追加する。
  - `spec-manager` を canonical specialist 名として導入し、旧 `spec-dock` specialist 名を置き換える。
  - `.codex/config.toml` を bootstrap-only asset として扱い、init では生成し、update では既存 user edit を保持する。
  - obsolete managed path と preserve path の境界を metadata と tests で固定する。
- MUST NOT:
  - new installer mechanism を作らない。
  - runtime protocol を再定義しない。
  - Copilot `config` / `mcp-config` を ship しない。
  - direct `.codex/agents/orchestrator.toml` を ship しない。
  - prompt assets を current issue scope に入れない。
- OUT OF SCOPE:
  - future host support
  - prompt file 配布
  - workflow/runtime semantics の再設計
  - Copilot config 系 asset の project install

## 境界
- Always:
  - source of truth は `src/spec_dock/assets/install_root/` とする。
  - discussion 配下の `add-codex` / `add-githobcopilot` は reference input としてのみ扱う。
  - shared skills は `.agents/skills/` に集約する。
  - bootstrap-only preserve は `.codex/config.toml` だけに適用する。
- Ask:
  - なし。host split、rename、backward compatibility 不要、prompt out-of-scope は epic で固定済み。
- Never:
  - unknown custom file を prune しない。
  - `config.toml` に secret / token / personal identity を含めない。

## 非交渉制約
- backward compatibility は要求しない。
- `spec-manager` canonical filename は Codex が `.codex/agents/spec-manager.toml`、Copilot が `.github/agents/spec-manager.agent.md` とする。
- GitHub Copilot primary entrypoint は `.github/agents/orchestrator.agent.md` とする。
- Codex orchestrator responsibility は `.codex/config.toml` developer instructions だけが担う。

## 前提
- existing `install_root` 再帰列挙 + `meta.json` obsolete list の基盤を継続利用できる。
- shared skills と host packs の provider-side asset 追加で機能を拡張できる。
- issue-71 系 parity test により、`src/spec_dock/assets/install_root/` と dogfooding root の一致が求められる。

## Exact inventory
- Codex managed files:
  - `.codex/AGENTS.md`
  - `.codex/agents/code_reviewer.toml`
  - `.codex/agents/consultant.toml`
  - `.codex/agents/default.toml`
  - `.codex/agents/dev_coder.toml`
  - `.codex/agents/doc_writer.toml`
  - `.codex/agents/explorer.toml`
  - `.codex/agents/pr_monitor.toml`
  - `.codex/agents/qa_reviewer.toml`
  - `.codex/agents/repo_analyst.toml`
  - `.codex/agents/researcher.toml`
  - `.codex/agents/spark_worker.toml`
  - `.codex/agents/spec_reviewer.toml`
  - `.codex/agents/spec-manager.toml`
  - `.codex/agents/utility_worker.toml`
  - `.codex/agents/worker.toml`
- Codex bootstrap-only files:
  - `.codex/config.toml`
- Codex managed exclusion:
  - `.codex/agents/orchestrator.toml` は生成しない。
- Copilot managed files:
  - `.github/agents/code_reviewer.agent.md`
  - `.github/agents/consultant.agent.md`
  - `.github/agents/dev_coder.agent.md`
  - `.github/agents/doc_writer.agent.md`
  - `.github/agents/orchestrator.agent.md`
  - `.github/agents/pr_monitor.agent.md`
  - `.github/agents/qa_reviewer.agent.md`
  - `.github/agents/repo_analyst.agent.md`
  - `.github/agents/researcher.agent.md`
  - `.github/agents/spec_reviewer.agent.md`
  - `.github/agents/spec-manager.agent.md`
  - `.github/agents/utility_worker.agent.md`
- Copilot managed exclusion:
  - `.github/copilot-instructions.md`
  - `.github/mcp-config.json`
  - `.github/config.json`
- Shared skills managed files:
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-adr-facilitation/SKILL.md`
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - `.agents/skills/git-commit-conventional-ja/SKILL.md`
  - `.agents/skills/git-commit-conventional-ja/agents/openai.yaml`
  - `.agents/skills/git-commit-conventional-ja/references/conventional-commits-v1.0.0.md`
  - `.agents/skills/github-codex-pr-review-comments/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/agents/openai.yaml`
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - `.agents/skills/github-pr-creator/SKILL.md`
  - `.agents/skills/github-pr-creator/agents/openai.yaml`

## Metadata delta
- `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` は current schema を最小拡張し、少なくとも次を持つ:
  - rename 後 canonical target file
  - `managed_assets.bootstrap_only_exact_file_paths` に `.codex/config.toml`
  - `managed_assets.obsolete_exact_file_paths` に旧 canonical / rename 前 managed path
- current managed inventory 自体は、引き続き `install_root` 再帰列挙を正本とする。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - clean repo に対して `spec-dock init` または `spec-dock update` を実行する
  - When:
    - Codex pack を同期する
  - Then:
    - `Exact inventory` に列挙した Codex managed files が生成される
    - `.codex/config.toml` は生成される
    - `.codex/agents/orchestrator.toml` は存在しない
  - 観測点:
    - installer tests
    - installed file inventory assertion
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - clean repo に対して `spec-dock init` または `spec-dock update` を実行する
  - When:
    - Copilot pack を同期する
  - Then:
    - `Exact inventory` に列挙した Copilot managed files が生成される
    - `.github/agents/orchestrator.agent.md` が primary entrypoint として存在する
    - Copilot config 系 files は存在しない
  - 観測点:
    - installer tests
    - installed file inventory assertion
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - update 対象 repo に old managed files、unknown custom files、編集済み `.codex/config.toml` が存在する
  - When:
    - `spec-dock update` を実行する
  - Then:
    - obsolete managed files だけが prune される
    - unknown custom files は保持される
    - `.codex/config.toml` の編集内容は保持される
  - 観測点:
    - update/prune tests
    - file content preservation assertion
- AC-004:
  - Actor:
    - maintainer
  - Given:
    - 実装差分一式
  - When:
    - tests と validate を実行し、issue report を確認する
  - Then:
    - relevant installer tests が pass する
    - `./spec-dock/scripts/spec-dock validate` が pass する
    - issue report に validation と review evidence が残る
  - 観測点:
    - test output
    - validate output
    - `report.md`

## 例外・エッジケース
- EC-001:
  - 条件:
    - Codex で orchestrator file を追加したくなる
  - 期待:
    - `.codex/agents/orchestrator.toml` は ship しない
  - 観測点:
    - inventory assertion
- EC-002:
  - 条件:
    - update 前に `.codex/config.toml` を編集済み
  - 期待:
    - update 後も同じ編集内容が残る
  - 観測点:
    - file content diff
- EC-003:
  - 条件:
    - repo に unknown custom agent/skill file が混在する
  - 期待:
    - managed obsolete 以外は削除されない
  - 観測点:
    - update/prune assertion

## 用語
- TERM-001:
  - host pack:
    - host-specific install target へ展開される file set
- TERM-002:
  - bootstrap-only:
    - init で生成するが update で既存内容を上書きしない asset
- TERM-003:
  - obsolete managed path:
    - 過去の managed file として明示 prune 対象にする exact path

## 未確定事項
- なし:
  - issue 実装に必要な inventory、ownership、metadata delta、prune/preserve boundary は本書で固定する
