---
種別: 要件定義書（Issue）
ID: "iss-00055"
タイトル: "Close Linked Github Issues From Specdock Command"
関連GitHub: ["#55"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-09"
親: ["epic-00054", "init-local-00002"]
---

# iss-00055 Close Linked Github Issues From Specdock Command — 要件定義（WHAT / WHY）

## 目的
- SpecDock の command surface から linked GitHub issue を close できるようにし、dogfooding 中に残っている「create は command、close は Web UI」という lifecycle の分断を解消する。
- local tree を触らずに remote issue lifecycle だけを進める安全な close 操作を、docs / tests / CLI guidance を含めて固定する。

## 背景・現状
- 現状の挙動:
  - `new initiative` / `new epic` / `new issue` は command 側で GitHub issue を作成または link できる。
  - `sync --github` は GitHub issue の `OPEN/CLOSED` を読み取り、local state へ `open/done` として反映できる。
  - 一方で、SpecDock には linked GitHub issue を close する command が無く、dogfooding では GitHub Web UI 側で close している。
- 現状の課題:
  - create から close まで同一 tool surface で完結せず、日常運用で command と Web UI を往復する必要がある。
  - close 操作の contract が docs / runtime / tests に存在しないため、将来 delete 機能を足す前提の lifecycle 境界も曖昧なままである。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock new issue --epic epic-00054 --title "..."` などで linked GitHub issue を持つ node を作成する。
  2. SpecDock 側で close 相当の command を探しても見つからず、GitHub Web UI で手動 close する。
- 観測点:
  - UI:
    - GitHub issue は Web UI からは close できるが、SpecDock CLI からは close できない。
  - HTTP:
    - 該当なし。runtime は `gh` CLI を使用する。
  - DB:
    - 該当なし。
  - Log:
    - `cli/registry.py` と parser 上に close command が存在しない。
    - `infra/github_cli.py` には create/view/list はあるが close 操作は未実装である。
- 情報源:
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/requirement.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - daily dogfooding を行う maintainer
  - SpecDock を通じて issue lifecycle を進める coding agent / orchestrator
- 代表シナリオ:
  - 実装と review が完了した issue に対し、maintainer が SpecDock command から linked GitHub issue を close する。
  - close 後に `sync --github` を実行し、local 側の `done` 反映を確認する。

## スコープ
- MUST:
  - linked GitHub issue を command 側から close できること
  - close 対象の解決、失敗時のエラー、成功時の観測方法を docs / CLI / tests で固定すること
  - epic / initiative を target にした場合でも、close 対象は指定 node 自身の linked GitHub issue のみとし、child issue へ cascade しないこと
  - local tree は削除せず、remote lifecycle のみを閉じること
- MUST NOT:
  - GitHub-side issue delete を扱わない
  - local issue / epic / initiative directory を削除しない
- OUT OF SCOPE:
  - local delete command
  - epic / initiative subtree close-or-delete orchestration
  - final epic close-out

## 境界
- Always:
  - remote handling は close-only であり、delete を success path に含めない
  - close command は linked GitHub issue を持つ node を対象にする
  - close command は target node 自身の linked GitHub issue のみを閉じ、child node の linked issue には波及しない
  - close 操作だけでは local docs / directory を消さない
- Ask:
  - close 対象の指定形式を新 command でどこまで既存 target resolution と揃えるか
- Never:
  - GitHub Web UI 依存を前提としたまま requirement を閉じない
  - close と delete を同義として扱わない

## 非交渉制約
- additive change とし、既存 create / import / sync / validate / active contract を壊さないこと
- `gh` CLI と current repo linkage の前提を崩さないこと
- remote delete を convenience path として導入しないこと

## 前提
- current repo は GitHub-linked consumer repo であり、`gh` auth / permission が有効である
- close 後の local `done` 反映は `sync --github` の観測経路に委ねる
- issue-level review と success verification は本 issue 自身で完結させる

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - linked GitHub issue を持つ issue / epic / initiative node が存在する
  - When:
    - maintainer が SpecDock command から close 操作を実行する
  - Then:
    - linked GitHub issue が close される
    - target が epic / initiative の場合でも child issue は close されない
    - local directory や docs は削除されない
  - 観測点:
    - runtime / CLI tests
    - `gh issue view` 相当の state 確認
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - close 操作が成功した node が存在する
  - When:
    - maintainer が `./spec-dock/scripts/spec-dock sync --github` を実行する
  - Then:
    - local generated state で対象 node の GitHub state が `CLOSED` / `done` として観測できる
    - docs / CLI guidance に close 後の確認導線がある
  - 観測点:
    - sync-related tests
    - docs contract

## 例外・エッジケース
- EC-001:
  - 条件:
    - target node が linked GitHub issue を持たない
  - 期待:
    - close は fail-fast し、local state を変更しない
  - 観測点:
    - runtime / CLI tests
- EC-002:
  - 条件:
    - `gh` auth / permission / network 状態により remote close が失敗する
  - 期待:
    - close は失敗として返り、local directory と local docs はそのまま残る
  - 観測点:
    - runtime / CLI tests
- EC-003:
  - 条件:
    - linked GitHub issue が既に closed である
  - 期待:
    - close command は success/no-op として一貫して返り、close 済みであることを観測できる
  - 観測点:
    - runtime / CLI tests
    - docs contract

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock <close-command> --id iss-00055`
  - Output:
    - linked GitHub issue close 成功を示す CLI result
    - local tree unchanged
- EX-002:
  - Input:
    - `./spec-dock/scripts/spec-dock sync --github`
  - Output:
    - target node が `done` と観測できる generated state

## 用語（ドメイン語彙）
- TERM-001:
  - linked GitHub issue:
    - `.meta.json` の `github.issue_number` で node に紐づく current-repo GitHub issue
- TERM-002:
  - close-only:
    - remote side に対して issue delete を行わず、issue state を closed へ遷移させる扱い
- TERM-003:
  - local tree unchanged:
    - close command 実行時に node directory、issue docs、parent-child tree を削除しないこと

## 未確定事項
- なし:
  - close command の idempotent 挙動は success/no-op として固定する
  - issue55 の close は target node 単位であり、child cascade は扱わない
