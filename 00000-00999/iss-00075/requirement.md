---
種別: 要件定義書（Issue）
ID: "iss-00075"
タイトル: "Multi host agent and config asset install"
関連GitHub: ["#75"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-15"
親: ["epic-00074", "init-local-00002"]
---

# iss-00075 Multi host agent and config asset install — 要件定義（WHAT / WHY）

## 目的
- `spec-manager` を requirement/design/plan/report specialist ではなく、SpecDock command operator として再定義する。
- SpecDock 操作の調査と実行をメインオーケストレーターから分離し、command execution を `spec-manager` へ集約する。
- 一方で issue docs の本文作成、文脈統合、要件判断は引き続きメインオーケストレーター側に残す。

## 今回の実行スコープ（2026-04-15 follow-up セッション）
- このセッションでは `spec-manager` の設定ファイルと、それを呼び出す main 側 guidance だけを更新対象とする。
- 対象 host は Codex CLI と GitHub Copilot の両方とする。
- 変更対象は provider-side assets、メイン agent guidance、関連 installer tests、dogfooding parity に限定する。

## 背景・現状
- 現状の `spec-manager` は thin adapter への静的委譲だけを持つ薄い shim であり、SpecDock command surface を十分に知らない。
- dogfooding では、本来 `spec-manager` が担うべき SpecDock command operation を main オーケストレーターが直接扱う場面があった。
- requirement/design/plan/report などの docs 本文は、active issue docs と会話文脈を踏まえた main 側作業のほうが効率的であり、これを `spec-manager` へ毎回 handoff するのは非効率である。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - main orchestrator
  - SpecDock command operation を delegated execution したい maintainer
- 代表シナリオ:
  1. main orchestrator が active issue docs とユーザー意図から command task を切り出す。
  2. SpecDock 操作が必要になったら `spec-manager` を default operator として使う。
  3. `spec-manager` は `./spec-dock/scripts/spec-dock ...` と必要最小限の `gh` 連携を使って command execution を行う。
  4. requirement/design/plan/report の本文作成や編集は main 側が継続して担う。

## スコープ
- MUST:
  - `spec-manager` の role を command-first operator へ変更する。
  - Codex / Copilot 両方の `spec-manager` に SpecDock command surface、read order、関連 docs 参照、completion boundary を埋め込む。
  - main 側 guidance に「SpecDock command operation は原則 `spec-manager` へ委任する」を明記する。
  - `spec-manager` が docs 本文作成や manual file edit を担当しないことを明記する。
  - GitHub Copilot `spec-manager` は `user-invocable: false` を維持する。
  - GitHub Copilot `spec-manager` の tools を `read/search/execute/todo` に限定する。
  - Codex `spec-manager` に mini model、notification 無効化、shell 実行許可、manual edit 禁止 guidance を与える。
- MUST NOT:
  - new installer mechanism を作らない。
  - runtime protocol や generated state contract を再定義しない。
  - `spec-manager` に requirement/design/plan/report/discussion/ADR の本文作成責務を与えない。
  - GitHub Copilot `spec-manager` に `edit` / `agent` / `web` tools を与えない。
  - role-local MCP 設定を追加しない。
- OUT OF SCOPE:
  - `spec-manager` 以外の specialist role 再設計
  - workflow/runtime semantics の再設計
  - Copilot config 系 asset の配布拡張
  - prompt asset 配布

## 境界
- Always:
  - source of truth は `src/spec_dock/assets/install_root/` とする。
  - issue docs 本文の正本は `spec-dock/active/issue/*` とする。
  - `spec-manager` は command execution と command evidence 収集に集中する。
- Never:
  - `spec-manager` に docs 本文を書かせない。
  - `spec-manager` に `apply_patch` や手編集を前提とした役割を与えない。
  - main 側 guidance から `spec-manager` への routing を曖昧なまま放置しない。

## 非交渉制約
- `spec-manager` canonical filename は Codex が `.codex/agents/spec-manager.toml`、Copilot が `.github/agents/spec-manager.agent.md` とする。
- GitHub Copilot primary entrypoint は `.github/agents/orchestrator.agent.md` のままとする。
- GitHub Copilot `spec-manager` は subagent 専用であり、`user-invocable: false` とする。
- `spec-manager` は `./spec-dock/scripts/spec-dock ...` と必要最小限の `gh` 連携を扱う operator であり、issue docs 本文は作成しない。
- requirement/design/plan/report の本文作成、文脈統合、ユーザーとの擦り合わせは main オーケストレーターの責務とする。

## 変更境界
- primary touchpoints:
  - `src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml`
  - `src/spec_dock/assets/install_root/.github/agents/spec-manager.agent.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/config.toml`
  - `src/spec_dock/assets/install_root/.github/agents/orchestrator.agent.md`
  - `tests/test_init_update.py`
- thin adapter skills:
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - これらは thin adapter contract を維持し、今回の主変更対象にはしない。

## 受け入れ条件
- AC-001:
  - Actor:
    - main orchestrator
  - Given:
    - SpecDock command operation を含む task を扱う
  - When:
    - main agent guidance を読む
  - Then:
    - SpecDock command execution は原則 `spec-manager` に委任することが明記されている
    - docs 本文作成は main 側責務として残っている
  - 観測点:
    - `.codex/AGENTS.md`
    - `.codex/config.toml`
    - `.github/agents/orchestrator.agent.md`
- AC-002:
  - Actor:
    - `spec-manager`
  - Given:
    - SpecDock command execution task を受ける
  - When:
    - host-native agent instructions を読む
  - Then:
    - command surface、read order、reference docs、manual edit prohibition、completion boundary を自前 knowledge として持てる
    - thin host adapter への delegation path は維持される
  - 観測点:
    - `.codex/agents/spec-manager.toml`
    - `.github/agents/spec-manager.agent.md`
- AC-003:
  - Actor:
    - GitHub Copilot host
  - Given:
    - `spec-manager` custom agent をロードする
  - When:
    - tool frontmatter を解釈する
  - Then:
    - `spec-manager` は `user-invocable: false` のままである
    - `tools` は `read/search/execute/todo` に限定され、`edit` / `agent` / `web` は含まれない
    - `mcp-servers` は追加されない
  - 観測点:
    - `.github/agents/spec-manager.agent.md`
- AC-004:
  - Actor:
    - Codex host
  - Given:
    - `spec-manager` native shim をロードする
  - When:
    - agent config を解釈する
  - Then:
    - `model = "gpt-5.4-mini"` と `model_reasoning_effort = "high"` が明示される
    - `notify = []` が設定される
    - shell 実行は許可される
    - manual edit 禁止と command-first mutation が instructions で明記される
  - 観測点:
    - `.codex/agents/spec-manager.toml`
- AC-005:
  - Actor:
    - maintainer
  - Given:
    - 実装差分一式
  - When:
    - relevant tests と validate を実行する
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
    - `spec-manager` が requirement/design/plan/report を自分で編集し始める
  - 期待:
    - instructions と tools の両方で command-only boundary に戻す
- EC-002:
  - 条件:
    - Codex 側で manual file edit を hard に禁止できない
  - 期待:
    - model / notify / shell を設定しつつ、instructions で manual edit 禁止と command-first mutation を明示する
- EC-003:
  - 条件:
    - main orchestrator が SpecDock 操作を直接処理したくなる
  - 期待:
    - routing guidance により `spec-manager` へ送る
