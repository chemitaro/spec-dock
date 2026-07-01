---
種別: 要件定義書（Issue）
ID: "iss-00261"
タイトル: "Artifact domain model and filename contract"
関連GitHub: ["#261"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00261 Artifact domain model and filename contract — Issue 要件定義

## 目的
`artifacts/` 用の domain model、artifact type catalog、filename parser/generator、artifact id、collision handling、malformed candidate detection を provider-side runtime に追加する。後続 Issue はこの契約を前提に template、command、scaffold、validation、sync、delegated authoring を実装する。

## 上位 trace
- Epic requirements: E-RQ-001, E-RQ-004, E-RQ-006.
- Epic acceptance criteria: E-AC-001, E-AC-002, E-AC-004, E-AC-007 foundations.
- Epic design decisions: D-001, D-004, D-005.
- Accepted ADR: `artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md`.

## スコープ
- 必須:
  - Future `Artifact` と legacy `DiscussionDoc` を別 domain concept として扱う。
  - Supported artifact type catalog を定義する。
  - typed filename と blank filename の parse/generate/id contract を定義する。
  - same-second collision suffix `01..99` を扱う。
  - malformed artifact-intent filename と duplicate artifact id を検出できる domain helper を提供する。
  - legacy `discussion_docs.py` の strict validation を緩めない。
- 対象外:
  - CLI command registration。
  - template rendering。
  - filesystem write / scaffold mutation。
  - ADR mirror / sync projection。

## 受け入れ条件
- AC-261-001 catalog:
  - `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`, `adr`, `draft-requirement`, `draft-design`, `draft-plan` が future artifact catalog に含まれる。
  - `scratch` は future catalog に含まれない。
- AC-261-002 filename:
  - typed artifact は `<timestamp>-<type>-<slug>.md` と `<timestamp>-<nn>-<type>-<slug>.md` を parse/generate できる。
  - blank artifact は `<timestamp>-<slug>.md` と `<timestamp>-<nn>-<slug>.md` を parse/generate でき、filename に `blank` を含めない。
- AC-261-003 identity:
  - artifact id は timestamp/suffix/type/slug から安定して導出され、legacy discussion doc id と衝突しても別 namespace として扱える。
- AC-261-004 negative:
  - unknown type、invalid slug、malformed timestamp、duplicate artifact id、artifact-intent の曖昧な filename は fail できる。
- AC-261-005 legacy non-interference:
  - 既存 discussion filename validation と grandfathered historical discussion types はこの Issue で変更されない。

## 検証期待
- Domain unit tests for catalog, parse/generate, collision, blank naming, malformed candidates, duplicate id, and legacy non-interference.
- `uv run pytest tests/unit` の関連 domain lane。

## 依存
- 依存なし。T1 foundation の最初の Issue。
