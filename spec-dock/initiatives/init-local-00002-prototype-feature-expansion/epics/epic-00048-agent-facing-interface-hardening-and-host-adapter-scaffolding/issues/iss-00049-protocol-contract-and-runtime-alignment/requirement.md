---
種別: 要件定義書（Issue）
ID: "iss-00049"
タイトル: "Protocol Contract And Runtime Alignment"
関連GitHub: ["#49"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
親: ["epic-00048", "init-local-00002"]
---

# iss-00049 Protocol Contract And Runtime Alignment — 要件定義（WHAT / WHY）

## 目的
- `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の責務を、runtime 実装・provider docs・dogfooding docs・tests で一致させる。
- 通常実行の default working set を `active.json` + `index.json` + `deps-issues.json` に固定し、`index-all.json` を escalation 専用に寄せる contract を実装可能な形にする。

## 背景・現状
- 現状の挙動:
  - `sync` はすでに `index-all.json`（all）と `index.json`（todo projection）を分けて生成している。 
  - `deps-issues.json` は todo issue-only graph として別生成されている。
  - `active.json` と `context-pack.md` も別 artifact として生成される。
  - ただし `context-pack.md` は `index.json` / `tree.json` までしか案内せず、`deps-issues.json` と `index-all.json` の既定/例外の読み分けが明文化されていない。
  - `json_state.py` が出力する `index.json` / `index-all.json` は、projection の意味づけを payload 上で明示していない。
- 現状の課題:
  - 実ファイルは分かれていても、agent-facing contract が弱く、host adapter 実装時に `index-all.json` を通常入口として扱う余地がある。
  - provider docs / generated docs / runtime artifact の説明にずれがあり、実装者依存の解釈が入りやすい。
  - current/future projection と full-history の境界が docs と JSON schema の双方で十分に可視化されていない。
- 再現手順:
  1. `spec-dock/docs/reference_sync.md` を読む。
  2. `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` と `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` の generated output / context pack を確認する。
  3. `spec-dock/.agent/index.json`、`spec-dock/.agent/index-all.json`、`spec-dock/.agent/deps-issues.json`、`spec-dock/.agent/active.json` を見比べる。
- 観測点:
  - Filesystem:
    - `spec-dock/.agent/index.json`
    - `spec-dock/.agent/index-all.json`
    - `spec-dock/.agent/deps-issues.json`
    - `spec-dock/.agent/active.json`
  - Docs:
    - `spec-dock/docs/reference_sync.md`
    - `spec-dock/active/context-pack.md`
  - Code:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
- 情報源:
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/requirement.md`
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/design.md`
  - `spec-dock/docs/reference_sync.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` を実行する orchestrator / sub-agent / host adapter 実装者
  - runtime/docs/tests を保守する maintainer
- 代表シナリオ:
  - agent が active issue を扱うとき、`active.json` を入口に `index.json` / `deps-issues.json` を既定 working set として使い、必要時だけ `index-all.json` を読む。
  - host adapter 実装者が docs と JSON payload を見て、`index-all.json` を通常入口にしてはいけないことを誤解なく実装できる。

## スコープ
- MUST:
  - `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の責務と読み順を provider docs / generated docs / runtime artifact で一致させる。
  - `index.json` を default working set / current-future projection、`index-all.json` を full-history / audit / search / escalation として明示する。
  - `deps-issues.json` を通常実行の dependency view として明示する。
  - `context-pack.md` の generated guidance を上記契約に沿って更新する。
  - runtime/tests を調整し、JSON shape と docs の説明が同じ意味を指すことを検証可能にする。
  - `index.json` / `index-all.json` / `deps-issues.json` には `projection` を、必要箇所には `source` を持たせる。
- MUST NOT:
  - host adapter 実装や installer 配布ロジックの追加には踏み込まない。
  - `index-all.json` を削除したり、full-history artifact を弱めたりしない。
  - invalid artifact prevention の architecture-level 対処を本 issue に含めない。
- OUT OF SCOPE:
  - Codex/Copilot adapter scaffold の導入
  - `.agents/skills` managed asset 機構の変更
  - multi-host 展開

## 境界
- Always:
  - 通常実行の入口は `active.json` である。
  - 通常実行の working set は `index.json` と `deps-issues.json` である。
  - `index-all.json` は必要時のみ読む full-history artifact として残す。
- Ask:
  - projection 名や metadata key を payload にどこまで明示するか。
  - `context-pack.md` に machine-facing detail をどこまで書くか。
- Never:
  - `context-pack.md` を唯一正本にしない。
  - `index-all.json` を通常実行の第一読取対象に戻さない。

## 非交渉制約
- provider-side source of truth は `src/spec_dock/assets/spec_dock/...` に置くこと。
- 既存の all/todo artifact 分離を壊さず、意味づけを強化する方向で修正すること。
- uppercase path を新たに増やさないこと。

## 前提
- `sync` の current implementation は all/todo projection をすでに生成している。
- issue-00050 で host adapter を載せる前に、本 issue で protocol contract を fixed point にする。

## 受け入れ条件
- AC-001:
  - Actor:
    - agent / host adapter 実装者
  - Given:
    - active issue が設定済みで、generated state が存在する
  - When:
    - docs と generated JSON を参照して読取順を決定する
  - Then:
    - `active.json` を入口、`index.json` と `deps-issues.json` を通常実行の working set、`index-all.json` を必要時のみ使う artifact として一貫して解釈できる
  - 観測点:
    - `spec-dock/docs/reference_sync.md`
    - `spec-dock/active/context-pack.md`
    - generated JSON payload
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - `sync` が JSON artifact を生成する
  - When:
    - current-future projection と full-history projection を確認する
  - Then:
    - payload 上でも projection/用途が判別でき、tests で検証できる
  - 観測点:
    - `tests/presentation_runtime/` または `tests/cli_runtime/` の relevant tests
    - `spec-dock/.agent/index.json`
    - `spec-dock/.agent/index-all.json`
    - `spec-dock/.agent/deps-issues.json`
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - provider docs と dogfooding docs が更新対象である
  - When:
    - parity を確認する
  - Then:
    - provider/dogfooding の protocol guidance に矛盾がない
  - 観測点:
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - `spec-dock/docs/reference_sync.md`
    - relevant tests / diff

## 例外・エッジケース
- EC-001:
  - 条件:
    - active が未設定で `active-none` placeholder が使われる
  - 期待:
    - 入口が `active.json` であることは変わらず、context pack は placeholder read order を示す
  - 観測点:
    - `spec-dock/.agent/active.json`
    - `spec-dock/system/active-none/`
- EC-002:
  - 条件:
    - deps preflight failure により `deps-issues.json` が placeholder 上書きされる
  - 期待:
    - default dependency view という責務は維持しつつ、invalid state が payload と docs の両方で説明可能である
  - 観測点:
    - `sync --force` の generated payload
    - `spec-dock/docs/reference_sync.md`
- EC-003:
  - 条件:
    - full-history が必要な監査・履歴参照を行う
  - 期待:
    - `index-all.json` を読む導線が docs から辿れ、通常実行の入口とは区別される
  - 観測点:
    - docs guidance
    - payload metadata

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - active issue が設定された repo で generated context pack と `.agent/*.json` を読む
  - Output:
    - `active.json` -> `index.json` / `deps-issues.json` -> `context-pack.md` -> `index-all.json`(必要時) の順序が docs / payload / tests で一致する

## 用語（ドメイン語彙）
- TERM-001:
  - current-future projection:
    - 現在から未来の open/todo work に必要な working set
- TERM-002:
  - full-history projection:
    - 完了済みを含む監査・履歴・全体検索向け state
- TERM-003:
  - default working set:
    - 通常実行の agent が最初に読むべき state 群

## 未確定事項
- なし:
  - `projection` と `source` metadata を payload に追加する方針で固定した。
