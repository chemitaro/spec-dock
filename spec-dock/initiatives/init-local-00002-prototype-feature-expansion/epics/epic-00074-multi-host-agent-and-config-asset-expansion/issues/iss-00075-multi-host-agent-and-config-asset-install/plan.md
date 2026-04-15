---
種別: 実装計画書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md"]
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
  - `AC-004`
  - `AC-005`
- EC:
  - `EC-001`
  - `EC-002`
  - `EC-003`

## 今回の実装スライス（2026-04-15 follow-up セッション）
- `spec-manager` を command operator として rich 化する。
- main orchestrator から `spec-manager` への routing guidance を強化する。
- related installer/content tests と dogfooding validate までを current session で閉じる。

## マイルストーン
- M1:
  - issue docs を command-operator split に更新する
- M2:
  - host assets を更新する
  - `spec-manager` host files
  - main guidance files
- M3:
  - tests を content contract に合わせて更新する
- M4:
  - validation / review / report で close-ready にする

## 実装順序の根拠
- 先に issue docs で責務分界を固定しないと、main と `spec-manager` の境界が再び曖昧になる。
- 次に host assets を更新して contract を実装する。
- 最後に tests と validate で provider / generated parity を確認する。

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - issue docs が `spec-manager = command operator`, `main = docs owner` を正本として表現する
  - closes:
    - contract fixation
- S02:
  - 観測可能な振る舞い:
    - Codex / Copilot の `spec-manager` が command knowledge と boundary を持つ
  - closes:
    - `AC-002`
    - `AC-003`
    - `AC-004`
- S03:
  - 観測可能な振る舞い:
    - main guidance が SpecDock command operation を `spec-manager` へ送る
  - closes:
    - `AC-001`
    - `EC-003`
- S04:
  - 観測可能な振る舞い:
    - tests が新 content/routing contract を guard する
  - closes:
    - `AC-005`
- S99:
  - 観測可能な振る舞い:
    - tests / validate / reviews / report evidence が揃う
  - closes:
    - final exit contract

## 実装ステップ

### S01 — issue docs contract fixation
- main agent が `requirement.md` / `design.md` / `plan.md` を更新する。
- ここで command-operator split、host-specific enforcement、test scope を固定する。

### S02 — `spec-manager` host asset enrichment
- delegate:
  - `dev-coder`
- target:
  - `src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml`
  - `src/spec_dock/assets/install_root/.github/agents/spec-manager.agent.md`
- expected change:
  - command operator description
  - command matrix
  - read order
  - docs authoring prohibition
  - thin adapter delegation 維持
  - Copilot tools restriction
  - Codex model / reasoning / notify / shell settings

### S03 — main guidance reinforcement
- delegate:
  - `dev-coder`
- target:
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/config.toml`
  - `src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md`
- expected change:
  - SpecDock command operation は原則 `spec-manager`
  - docs authoring は main
  - mixed task では docs/context を main が保持し、command 部分だけを `spec-manager` へ送る

### S04 — regression coverage update
- delegate:
  - `dev-coder`
- target:
  - `tests/test_init_update.py`
- expected change:
  - old thin-shim assertion を新 contract に合わせて更新する
  - provider/generated parity checks は維持する
  - Copilot tools restriction と Codex config surface を確認する

### S05 — review and validation
- delegate:
  - `code-reviewer`
  - `qa-reviewer`
- expected checks:
  - role split と accidental regression がないか
  - tests が新 contract を十分 guard しているか
- local validation:
  - relevant installer tests
  - `./spec-dock/scripts/spec-dock validate`

### S99 — report close-out
- main agent が `spec-dock/active/issue/report.md` へ以下を残す。
  - 実装要約
  - review verdict
  - test command / result
  - validate command / result
  - 未解決事項

## レビュー / QA ゲート方針
- code review:
  - `spec-manager` が docs authoring を始めない boundary が十分に表現されているかを見る
- qa review:
  - Copilot tools restriction、Codex config surface、routing guidance assertion が guard されているかを見る
- spec review:
  - 今回は issue docs を main で更新済みなので、必要なら final close-out で自己整合を確認する

## 完了条件
- host assets が新 contract を表現する
- main guidance が `spec-manager` default delegation を表現する
- tests が pass する
- `./spec-dock/scripts/spec-dock validate` が pass する
- `report.md` に evidence が残る
