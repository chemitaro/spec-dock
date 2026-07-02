---
created_by_role: system-architect
scope_id: iss-00272
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/artifacts/20260702t081002z-draft-design-epic-template-redesign-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - src/spec_dock/assets/spec_dock/templates/epic/requirement.md
  - src/spec_dock/assets/spec_dock/templates/epic/design.md
  - src/spec_dock/assets/spec_dock/templates/epic/plan.md
  - src/spec_dock/assets/spec_dock/templates/initiative/requirement.md
  - src/spec_dock/assets/spec_dock/templates/initiative/design.md
  - src/spec_dock/assets/spec_dock/templates/initiative/plan.md
intended_targets:
  - spec-dock/active/issue/design.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00272 Epic template redesign system-architect design draft

## Evidence boundary

この artifact は `iss-00272` の正本 `design.md` 作成に向けた delegated draft evidence であり、canonical authority、採用済み設計、reviewer pass、phase completion、implementation readiness を主張しない。採否は main orchestrator が `report.md` Evidence Adoption Ledger と fresh review gate で判断する。

Source requirement revision: `spec-dock/active/issue/requirement.md` 最終更新 `2026-07-02`、Issue ID `iss-00272`。

Leaf evidence used: none. この draft は指定された local files の read-through に基づく。

Forbidden actions avoided: canonical docs、implementation files、tests、package/config、workflow、secrets、GitHub state は編集していない。

## 1. Requirement Coverage

| AC | 設計対応 | 採用時の確認点 |
|---|---|---|
| `I272-AC-001` | Epic `requirement.md` template に、capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope を表す専用 section を追加する。 | Issue detail や TDD cadence ではなく、Epic が束ねる能力・境界・観測可能な成果を記述できること。 |
| `I272-AC-002` | Epic `design.md` template に、cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を追加する。 | DDD / EDA 前提にせず、必要な場合だけ既存 architecture 語彙に合わせられること。 |
| `I272-AC-003` | Epic `plan.md` template に、Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を追加する。 | downstream Issue が parent trace、許可差分、禁止変更、expected evidence を受け取れること。 |
| `I272-AC-004` | Epic template には Issue-level TDD step、test function detail、private helper / class design を必須欄として置かない。 | `plan.md` は Issue slicing と gate を扱い、Issue 実行手順は Issue plan へ残すこと。 |
| `I272-AC-005` | 3 template 全体に artifact authority boundary を置き、raw artifact は evidence、採用判断は canonical docs / accepted ADR / `report.md` EAL で扱うよう誘導する。 | artifact path の存在だけを採用や実行準備完了と誤認させないこと。 |
| `I272-AC-006` | 作成方針 section で日本語ファーストを明示し、識別子・コマンド・ファイルパス・固定語は原文保持可とする。 | 英語説明文の放置を避けつつ、技術識別子の過翻訳を避けること。 |
| `I272-AC-007` | Epic `plan.md` の Issue handoff package に parent requirement / design trace、allowed local delta、forbidden parent boundary changes、expected evidence を持たせる。 | shipped template に `iss-00272` など dogfooding 固有 ID を入れないこと。 |

## 2. Existing Context Findings

現行 Epic templates は日本語の基本 scaffold を持つが、Epic が Initiative と Issue の間で持つべき「複数 Issue を束ねる envelope」と「downstream handoff」の表現が薄い。

- `epic/requirement.md` は目的、ユースケース、要件、AC、scope を持つが、capability / model envelope、主要 use case cluster、downstream Issue seed への接続が明示されていない。
- `epic/design.md` は component、package dependency、domain model、contract、flow、failure、migration、test strategy を持つが、Issue 横断境界や design slice catalog として読む導線が弱い。
- `epic/plan.md` は Issue list、統合 checkpoint、quality gate、readiness criteria を持つが、Issue handoff package の field が不足している。
- 完了済み Initiative templates は、作成方針、日本語ファースト、DDD / EDA 非必須、artifact adoption、reviewer gate、handoff seed を明示しており、Epic templates も同等の語彙でそろえるのが自然である。
- 親 Epic design は、raw artifact / delegated draft を canonical authority にせず、採用は canonical docs、accepted ADR、`report.md` EAL で扱う方針を採用している。

## 3. Design Decisions

### D-272-001: Epic templates use an envelope-first model

Epic requirement template は、個別 Issue の実装 detail ではなく、Epic が提供する capability、model / lifecycle envelope、主要ユースケース、scope / non-scope、Epic-level acceptance を最初に固定する構成にする。

### D-272-002: Epic design template becomes the cross-Issue contract surface

Epic design template は、複数 Issue にまたがる責務境界、design slice catalog、contract portfolio、failure / migration / test strategy を記述する surface にする。private implementation design や TDD step は必須にしない。

### D-272-003: Epic plan template owns handoff, order, and gates

Epic plan template は、Issue handoff package、suggested grade、dependencies、integration checkpoint、final quality gate を扱う。Issue plan の実行手順や Red-Green-Refactor cadence は移さない。

### D-272-004: Artifact authority is explicit and conservative

Template 内では、`artifacts/` を raw evidence surface として扱う。採用済み判断は canonical docs、accepted ADR、または `report.md` EAL に記録された場合だけ downstream input として扱える。

### D-272-005: Architecture-neutral by default, architecture-aware when grounded

DDD / EDA は必須前提にしない。対象 repo の既存 architecture、accepted ADR、親 docs が明確な場合に限り、その語彙を使える形にする。

### D-272-006: Japanese-first prose is part of the template contract

作成方針として、説明文、判断理由、AC、設計説明、計画説明は日本語ファーストとする。ファイルパス、コマンド、コード識別子、SpecDock 固定語、外部固有名詞は原文保持を許容する。

## 4. Alternatives Considered

| 代替案 | 判断 | 理由 |
|---|---|---|
| 現行 Epic templates に小さな項目だけ追加する | 不採用 | `I272-AC-002` と `I272-AC-007` が求める cross-Issue boundary / handoff field が散らばり、後続 Issue が必要情報を見落としやすい。 |
| Initiative template の構造を Epic template へほぼコピーする | 部分採用 | 日本語ファースト、architecture-neutral、artifact adoption の語彙は再利用するが、Epic は Issue slicing / handoff を持つためそのままでは過不足がある。 |
| DDD / EDA 固有 section を標準化する | 不採用 | 親 Epic の D-002 と `I272-EC-002` に反する。必要時 section と補助語彙に留める。 |
| Epic plan に Issue-level TDD checklist を追加する | 不採用 | `I272-AC-004` と親 plan の責務分離に反する。Epic plan は handoff と gate を扱う。 |

## 5. Boundary / Contract Model

| Layer | Epic template で表現する責務 | 表現しない責務 |
|---|---|---|
| Epic requirement | capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope、下流 Issue seed の前提 | Issue 内部設計、TDD cadence、個別 test case |
| Epic design | cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy、artifact authority boundary | private helper / class design、Issue の実装順序、個別 Issue の local decision |
| Epic plan | Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate | Issue plan steps、Red-Green-Refactor detail、implementation task breakdown |
| Report | EAL、reviewer result、deviation、採否、final evidence | 将来の未採用 design commitment |

Authority flow:

```text
raw artifact / delegated draft
  -> main orchestrator adoption decision
    -> canonical requirement/design/plan or accepted ADR
      -> report.md EAL / reviewer gate
        -> downstream Issue handoff
```

## 6. Dependency Analysis

- `iss-00272` は `iss-00271` の Initiative template 語彙を受け取り、Epic-specific handoff field へ拡張する。
- `iss-00273` は、この Issue で作る Epic template の handoff / scope-layering 語彙へ thin links と workflow guidance を接続する。
- `iss-00274` は、Issue handoff package と readiness boundary を Epic execution workflow で消費する。
- `iss-00275` は、template fields、artifact authority、日本語ファースト、architecture-neutral wording を focused checks / smoke tests で確認する。
- `iss-00276` は、final quality gate と PR readiness で Epic 全体を確認する。

この Issue 内では provider-side template source を更新対象とし、dogfooding workspace は確認対象に留めるのが自然である。

## 7. Source of Record

正本候補への反映時は、以下を優先する。

1. Accepted ADRs と親 Epic `design.md` の決定。
2. `spec-dock/active/issue/requirement.md` の `I272-AC-001..007` と例外条件。
3. 完了済み Initiative templates の authoring pattern。
4. 現行 Epic templates の既存 structure。
5. Issue-local draft artifacts。

この artifact は 5 番目の advisory evidence であり、上位 source of record を置き換えない。

## 8. Data Flow / Domain Model / Interface Contract

### Template authoring flow

```text
Epic requirement template
  -> capability / model envelope and acceptance surface
Epic design template
  -> cross-Issue boundary and contract portfolio
Epic plan template
  -> Issue handoff package, dependencies, gates
Issue planning
  -> local adoption decision and executable plan
Report EAL
  -> evidence adoption / rejection / stale / blocker record
```

### Proposed requirement template contract

- `作成方針`
  - 日本語ファースト。
  - DDD / EDA 非必須。
  - Epic は Issue implementation detail を固定しない。
- `目的（Initiative との紐づき）`
  - Initiative 目標。
  - Epic が提供する capability。
- `能力 / モデル envelope`
  - 対象 capability。
  - model / lifecycle boundary。
  - cross-Issue invariant の seed。
- `ユースケース`
  - 正常系。
  - 例外 / 運用 scenario。
- `エピック要件`
  - E-RQ IDs。
- `エピック受け入れ条件`
  - 前提、操作、期待結果、観測点。
- `スコープ`
  - 必須、禁止、対象外。
- `後続 Issue seed`
  - Issue 候補へ渡す parent trace / acceptance seed の初期材料。

### Proposed design template contract

- `作成方針`
  - cross-Issue design surface。
  - private implementation design 非必須。
- `全体像`
  - 対象境界、影響領域、既存関係。
- `責務境界 / cross-Issue boundary`
  - Epic が固定する判断。
  - Issue に委譲する local delta。
  - forbidden parent boundary changes。
- `design slice catalog`
  - Slice ID。
  - purpose。
  - closes E-RQ / E-AC。
  - owning Issue candidate。
  - contract impact。
  - evidence expectation。
- `contract portfolio`
  - API / CLI / event / metadata / docs / template contracts。
  - system of record。
  - compatibility expectation。
- `artifact adoption`
  - raw evidence。
  - accepted ADR。
  - report EAL destination。
- `failure / migration / rollback`
  - failure modes。
  - migration / compatibility。
  - rollback boundary。
- `test strategy`
  - template / scaffold / smoke / reviewer focus。

### Proposed plan template contract

- `作成方針`
  - Issue handoff と実施順序を扱う。
  - Issue-level TDD detail を扱わない。
- `この計画で閉じる E-RQ / E-AC`
- `課題分割方針`
- `Issue handoff package`
  - parent trace。
  - allowed local delta。
  - forbidden parent boundary changes。
  - acceptance seed。
  - constraints。
  - expected evidence。
  - suggested grade。
  - dependencies。
  - escalation triggers。
  - relevant artifacts / ADRs。
- `課題一覧`
- `Issueリレー依存`
- `統合チェックポイント`
- `品質ゲート`
- `最終完了条件`

## 9. File / Module Change Plan

| 対象 | 変更方針 | 注意点 |
|---|---|---|
| `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | 作成方針、capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope、後続 Issue seed を追加する。 | dogfooding 固有 ID や `iss-00272` 固有語を入れない。 |
| `src/spec_dock/assets/spec_dock/templates/epic/design.md` | cross-Issue boundary、design slice catalog、contract portfolio、artifact adoption、failure / migration / rollback、test strategy を Epic 用に再整理する。 | DDD / EDA は必要時の補助に留める。private implementation design を必須にしない。 |
| `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を明示する。 | Issue plan の TDD steps を移植しない。 |
| `tests/` | 必要なら template / scaffold focused assertions を追加または更新する。 | 実装判断は正本 plan で確定する。 |
| `spec-dock/` | provider-side 変更後に dogfooding read-through または update 結果を確認する。 | consumer workspace を implementation source と誤認しない。 |

## 10. Migration / Compatibility / Rollback

- Migration:
  - database や runtime state migration は想定しない。
  - shipped templates の構造変更なので、新規 scaffold と `spec-dock update` の受け取り方が主な影響である。
- Compatibility:
  - 既存 managed repo の historical docs は自動変換対象にしない。
  - 新規または更新後の Epic docs が improved template を受け取る。
  - DDD / EDA 未採用 repo でも使える語彙を維持する。
- Rollback:
  - template wording が過剰なら provider-side template diff を Issue / PR 単位で戻す。
  - raw artifact を authority とする方向、Issue-level TDD detail を Epic template に移す方向、DDD / EDA 必須化への rollback は避ける。

## 11. Observability

- `report.md` Evidence Adoption Ledger に、この draft の採否を `adopted` / `partially_adopted` / `rejected` / `stale` / `blocked` として記録する。
- 正本 `design.md` へ反映する場合は、どの design decision と template contract を採用したかを明示する。
- reviewer gate では、artifact authority leak、Issue handoff package の具体性、日本語ファースト、DDD / EDA 非必須、Issue-level TDD detail の混入を確認する。
- final quality gate では、template read-through、focused tests、dogfooding confirmation の evidence を report に残す。

## 12. Test Strategy

- Template structure checks:
  - Epic requirement template が capability / model envelope、scope / non-scope、acceptance、Issue seed を含むこと。
  - Epic design template が cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を含むこと。
  - Epic plan template が Issue handoff package、suggested grade、dependencies、integration checkpoints、final gate を含むこと。
- Negative checks:
  - Epic templates が DDD / EDA を必須前提にしていないこと。
  - Epic templates が Issue-level TDD cadence、private implementation design、test function detail を必須化していないこと。
  - Template 本文に dogfooding 固有 Issue ID が混入していないこと。
- Authority checks:
  - `artifacts/` は raw evidence であり、採用判断は canonical docs / accepted ADR / `report.md` EAL に置く wording があること。
- Japanese-first checks:
  - 説明文が日本語ファーストで、識別子・コマンド・ファイルパス・固定語は原文保持可と説明していること。

## 13. ADR Candidates

- なし。

現時点の設計判断は親 Epic の accepted ADRs と `iss-00272` requirement の範囲内で説明できる。Epic template で追加するのは template contract の具体化であり、新しい durable architecture decision は不要と見込む。

## 14. Risks

- Template が厚くなりすぎ、実際の Epic authoring で空欄が増える risk。
  - Mitigation: required prompts と optional prompts を分け、必要時 section を明示する。
- Issue handoff package が抽象的すぎ、後続 Issue が境界を判断できない risk。
  - Mitigation: field 名を具体化し、parent trace / allowed local delta / forbidden changes / expected evidence を最低限にする。
- Epic design template が DDD / EDA 固有に見える risk。
  - Mitigation: domain model / event contract は必要時扱いにし、architecture-neutral な contract portfolio を中心にする。
- Artifact authority leak の risk。
  - Mitigation: artifact adoption と `report.md` EAL の wording を 3 template に配置する。
- 日本語ファースト guidance が識別子の過翻訳を誘発する risk。
  - Mitigation: ファイルパス、コマンド、コード識別子、SpecDock 固定語、外部固有名詞は原文保持可と明示する。

## 15. Requirement Clarification Requests

none

指定 source と親 Epic docs から、正本 design 作成前に必要な追加質問は見つからない。

## 16. Integration Notes for Main Orchestrator

- 正本 `design.md` へ統合する場合は、`D-272-001` から `D-272-006` をそのまま採用せず、main orchestrator の wording で再記述する。
- `Issue Grade` は Issue requirement の pre-start handoff では `strict` とされている。生成 artifact の元 template が `standard` を含んでいた場合でも、正本 design では `strict` 前提に合わせる。
- `src/spec_dock/assets/spec_dock/templates/epic/*` に入れる文面は generic template wording にし、`iss-00272`、`epic-00270`、この dogfooding workspace 固有 path を入れない。
- `iss-00271` の Initiative templates と同じ authoring pattern を使い、Epic では Issue handoff package と cross-Issue design surface を追加する。
- 正本採用時は `report.md` EAL に、この artifact の採用状態と採用しなかった部分を記録する。
- Fresh `spec-reviewer` は、template authority、handoff completeness、日本語ファースト、DDD / EDA 非必須、Issue detail 非必須を重点確認する。

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.

diff_guard_result: passed - この delegated artifact 作成前から `spec-dock/active/issue/design.md`、`plan.md`、`report.md` と `.assurance.json` に dirty state が存在したが、本作業で編集したのはこの Issue-local artifact のみ。canonical docs は編集していない。
