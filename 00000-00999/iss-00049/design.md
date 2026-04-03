---
種別: 設計書（Issue）
ID: "iss-00049"
タイトル: "Protocol Contract And Runtime Alignment"
関連GitHub: ["#49"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-03"
依存: ["requirement.md"]
親: ["epic-00048", "init-local-00002"]
---

# iss-00049 Protocol Contract And Runtime Alignment — 設計（HOW）

## 目的・制約
- 目的:
  - all/todo/active artifact の既存分離を、agent-facing contract として runtime・provider docs・dogfooding docs・tests に固定する。
  - issue-00050 が host adapter を実装するときの fixed point を提供する。
- MUST / MUST NOT:
  - MUST:
    - `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の責務を 1 つの read-order contract に揃える。
    - top-level metadata contract を artifact ごとに固定する:
      - `index.json`: `projection=current-future` を追加し、new top-level `source` は追加しない。
      - `index-all.json`: `projection=full-history` を追加し、new top-level `source` は追加しない。
      - `deps-issues.json`: `projection=open-issues-dependency-view` を追加し、top-level `source` は artifact provenance（`index.json` と schema version）として維持する。
      - 既存 per-node issue status `source` semantics は変更しない。
    - provider docs と dogfooding docs のうち、本 issue が変更する contract surface を同時に更新する。
  - MUST NOT:
    - host adapter scaffold 自体を追加しない。
    - issue-00050 が担当する adapter scaffold docs parity / final epic parity まで広げない。
    - full-history artifact を default working set に戻さない。
- 非交渉制約:
  - `src/spec_dock/assets/spec_dock/...` を provider-side source of truth とする。
  - current all/todo split と deps fail-closed behavior を維持する。
- 前提:
  - `sync_state.py` は `render_index_artifact()` / `render_deps_issues_artifact()` / `render_context_pack()` で関連 artifact を組み立てる。

## 既存実装 / 規約の理解
- 参照した実装 / docs:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_sync.md`
- 現状理解:
  - `render_index_artifact()` は all/todo の 2 payload を返すが、payload 自体に `projection` の意味づけはない。
  - `render_deps_issues_artifact()` は `source.index=index.json` を持つため、`deps-issues.json` を todo projection 由来の dependency view と説明しやすい。
  - `render_context_pack()` と `infra.active_store._render_context_pack()` は `index` / `tree` のみを列挙しており、`deps-issues.json` と `index-all.json` の扱いが抜けている。
  - `reference_sync.md` は all/todo projection を説明しているが、agent の既定読取順までは固定していない。
- 採用するパターン:
  - 既存 artifact 名は維持し、meaning を metadata と docs で強化する。
  - generated context pack と provider/dogfooding docs の両方で同じ read order を示す。
  - projection metadata は `json_state.py` 側で付与し、top-level `source` の有無は artifact ごとに固定して tests で検証する。
- 採用しないもの:
  - artifact 名の全面変更
  - new state file の追加
  - host-specific contract の埋め込み
- 影響範囲:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_sync.md`
  - relevant tests and dogfooding generated outputs

## 採用方針 / トレードオフ
- 論点:
  - contract を docs だけで固定するか、payload metadata でも固定するか
- 選択肢:
  - Option A:
    - docs だけを直し、runtime payload は現状維持にする
  - Option B:
    - docs と payload metadata を両方更新し、tests で固定する
- 決定:
  - Option B を採る
  - 理由:
    - host adapter 実装者は JSON payload を直接読む可能性が高く、docs だけでは guardrail が弱い
    - current-future / full-history の境界を payload 自体に持たせた方が review 可能性が高い

## インターフェース契約
- API / function / protocol / data boundary:
  - `active.json`
    - entry / current target を示す最小文脈
  - `index.json`
    - top-level `projection=current-future` を持つ default working set
    - new top-level `source` は追加しない
  - `deps-issues.json`
    - top-level `projection=open-issues-dependency-view` を持つ default dependency view
    - top-level `source` は artifact provenance（`index.json` と schema version）を維持する
    - issue node / issue status の既存 `source` semantics はそのまま維持する
  - `index-all.json`
    - top-level `projection=full-history` を持つ escalation artifact
    - new top-level `source` は追加しない
  - `context-pack.md`
    - human summary と read order の案内であり、唯一正本ではない

### UML（推奨: module / dependency）
```plantuml
@startuml
skinparam monochrome true

rectangle "active.json" as active
rectangle "index.json
(current-future)" as index
rectangle "deps-issues.json
(default dependency view)" as deps
rectangle "index-all.json
(full-history)" as all
rectangle "context-pack.md
(human summary)" as context

active --> index : normal path
index --> deps : normal path
index ..> all : escalate if needed
context ..> active : read order summary
context ..> index
context ..> deps
context ..> all
@enduml
```

## クラス / インターフェース詳細設計（必要時）
- Class / Interface:
  - `render_index_artifact()` / `_build_state_payloads()`
- responsibility:
  - projection metadata を index/deps payload に埋め、top-level `source` contract を artifact ごとに維持する
- collaboration:
  - `sync_state.py` が生成タイミングを制御し、docs/tests が意味を固定する

## 変更計画
- Add:
  - payload metadata（artifact ごとに固定した `projection`、および `deps-issues.json` の provenance `source`）
- Modify:
  - `json_state.py` の index/deps payload
  - `active_store.py` と presentation 側の context pack rendering
  - `reference_sync.md` の read-order guidance
  - related tests
- Delete:
  - なし
- Move/Rename:
  - なし
- Read only:
  - installer managed skill logic
  - host adapter assets

## 要件 → 設計マッピング
- AC-001 -> docs と context pack に `active -> index/deps -> index-all(if needed)` を明示する
- AC-002 -> payload metadata と tests で projection を固定する
- AC-003 -> 本 issue が変更した protocol contract surface について provider/dogfooding docs parity を同一 wording で保つ
- EC-001 -> active-none placeholder path でも entry contract は `active.json` で維持し、context pack の read order で証明する
- EC-002 -> deps invalid 時も `deps-issues.json` が default dependency view であり、top-level projection/provenance contract を崩さない
- EC-003 -> full-history read path を docs/payload で辿れるようにする

## テスト戦略
- Unit:
  - `json_state.py` の payload shape / metadata tests
- Integration:
  - `sync` 実行後に generated `.agent/*.json` と `active/context-pack.md` を検証する runtime tests
- E2E / manual:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - generated output diff 確認
- migration / rollback / feature flag if needed:
  - feature flag なし
  - rollback は payload metadata と docs wording の issue 単位 revert

## 要件 / 例外 -> verification mapping
- AC-001 -> docs/context-pack snapshot verification
- AC-002 -> JSON payload verification（artifact ごとの top-level `projection` / `source` contract を含む）
- AC-003 -> provider/dogfooding parity verification（本 issue の contract surface 限定）
- EC-001 -> active-none placeholder / context-pack read-order verification
- EC-002 -> deps invalid placeholder / fail-closed provenance verification
- EC-003 -> docs read-order verification

## リスク / 移行 / ロールバック（必要時）
- risk:
  - provider docs だけ更新して dogfooding docs/context pack が追随しないと再び drift する。
  - artifact ごとの top-level `source` contract が曖昧だと issue-00050 で再解釈が入る。
- migration:
  - 既存 file path は不変で、meaning だけを強化する。
- rollback:
  - metadata 追加と docs wording をまとめて戻す。

## 未確定事項
- なし:
  - payload metadata の contract は artifact ごとに固定し、`deps-issues.json` top-level provenance `source` と既存 per-node issue status `source` semantics を維持する。
