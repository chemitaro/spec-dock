---
種別: disc
ID: "20260630t084325z-disc"
タイトル: "Grade-Aware Authoring Rules Definition"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224"]
関連: ["iss-00247", "#247", "20260630t082805z-disc"]
authority: "proposed"
derived_from:
  - "/Users/iwasawayuuta/.codex/attachments/7d1d7ff9-799a-40ae-a732-da5eb7b06d0f/pasted-text.txt"
  - "20260630t055323z-disc-issue-247-manual-test-followup-analysis.md"
  - "20260630t080402z-disc-manual-test-readiness-failure-root-cause-analysis.md"
  - "20260630t082805z-disc-epic-224-amendment-and-followup-issue-draft.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md"
reflected_to:
  - "20260630t111316z-adr-grade-aware-issue-authoring-rules.md"
---

# 20260630t084325z-disc Grade-Aware Authoring Rules Definition

## 位置づけ
この artifact は、前回 draft `20260630t082805z-disc-epic-224-amendment-and-followup-issue-draft.md` のうち、`W1. Define Grade-Aware Issue Authoring Workflow Matrix` を follow-up Issue として切り出した判断を補正するためのものです。

結論として、grade 別の作業ルール定義は Issue で実装する対象ではありません。これは Epic #224 の上流設計判断であり、Epic の `requirement.md` / `design.md` / `plan.md` に反映してから、具体的な実装 Issue へ分解します。

この文書は canonical authority ではありません。採用する場合は Epic #224 の canonical docs と `report.md` Evidence Adoption Ledger へ反映します。

## 結論

`W1` は follow-up Issue から削除し、Epic #224 amendment の設計内容として扱います。

補正後の進め方は次の通りです。

1. この文書の grade-aware authoring rules を Epic #224 の canonical docs に採用する。
2. 前回 draft の Issue 構成から `W1` を取り除く。
3. 実装 Issue は、readiness correction、guidance compiler、delegated role routing、review/evidence gate、smoke tests に絞る。
4. 各 Issue は、ここで定義した作業ルールを前提として requirement / design / plan を作る。

## 用語定義

| 用語 | 定義 |
|---|---|
| `authorized_profile` | `.assurance.json` に記録される runtime authority。template / guidance / obligation selection はこれを使う。 |
| Issue authoring grade | Issue の仕様書作成で適用する作業強度。原則として `authorized_profile` と一致するが、人間判断で強められる。 |
| manual escalation | `authorized_profile` を silent override せず、planning / delegated role / review / report evidence / manual gate を強める判断。 |
| grade template pack | provider-side `templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md`。Issue design / plan の materialization source。 |
| delegated specialist | `system-architect` / `implementation-planner` などの委任ロール。scope-local `discussions/` evidence を作るだけで、canonical docs を直接確定しない。 |
| fresh spec-reviewer gate | 各 phase promotion に必要な新規 `spec-reviewer` pass。draft author や過去 reviewer result で代替しない。 |

## 共通ルール

- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator が所有する。
- Delegated specialist の output は scope-local `discussions/` evidence であり、canonical authority ではない。
- Delegated output を採用する場合は、main orchestrator が canonical docs と `report.md` Evidence Adoption Ledger に反映する。
- 各 phase promotion は fresh `spec-reviewer` の `review_status: pass` を必要とする。
- `waived` / `provisional` / `unavailable` / `denied` は reviewer pass ではない。
- `authorized_profile` は runtime template / guidance selection の authority であり、manual escalation はそれを silent override しない。
- Manual escalation は gate を弱めるためではなく、強めるためにだけ使う。
- `lite` は automatic default にしない。unknown / ambiguous の場合は `standard` 以上として扱い、Lite は明示根拠がある場合だけ使う。
- `assurance compose` の成功は execution readiness ではない。readiness は `workflow status` / `guidance issue-execution` の fail-closed preflight が判定する。
- 未解決 placeholder、template-only content、heading-only plan、実行可能作業単位のない plan、stale reviewer evidence、missing adoption evidence がある場合は execution-ready にしない。

## Grade 判定と Escalation Trigger

| Grade | 基本位置づけ | Escalation trigger |
|---|---|---|
| `lite` | 小さく可逆で、runtime / contract / scaffold / template / security / migration 影響がない変更。 | 影響範囲が少しでも不明、または設計判断が必要なら `standard` へ上げる。 |
| `standard` | 通常の Issue。要件、設計、計画の traceability と focused test が必要。 | runtime behavior、TDD behavior、複数ファイル、workflow/docs/template 影響がある場合は少なくとも `standard`。 |
| `strict` | contract、compatibility、template/scaffold/runtime/workflow、migration、review gate、cross-module 影響を持つ変更。 | public contract、既存ユーザー互換性、generated scaffold、authoring/runtime readiness、state transition を変える場合。 |
| `critical` | destructive / protected / credentialed / security / privacy / external mutation / recovery を含む変更。 | secret、GitHub mutation、manual approval、rollback/recovery、irreversible migration、protected asset に触れる場合。 |

## Requirement Phase ルール

| Grade | 作成者 | Specialist | Reviewer focus | Gate |
|---|---|---|---|---|
| `lite` | main orchestrator | 原則なし | Lite 前提を破っていないか。runtime / contract / migration / security 影響がないか。 | fresh spec-reviewer pass。 |
| `standard` | main orchestrator | 原則なし。調査補助は必要時のみ。 | acceptance criteria、behavior、constraint、grade signal、scope drift。 | fresh spec-reviewer pass。 |
| `strict` | main orchestrator | 必要時に consultant / repo evidence を使う。 | contract、compatibility、migration、template/scaffold/workflow 影響。 | fresh spec-reviewer pass。未解決 risk は design へ送らず requirement に残す。 |
| `critical` | main orchestrator | 必要時に security / deep consultant を使う。 | no-go、protected assets、manual gate、recovery、security/privacy。 | fresh spec-reviewer pass に加え、manual approval 必要性を明示する。 |

Requirement phase では、`system-architect` / `implementation-planner` は原則使いません。使う場合も設計 draft ではなく、要件曖昧性や risk classification の補助 evidence として扱います。

## Design Phase ルール

| Grade | Template | `system-architect` | Reviewer focus | Gate |
|---|---|---|---|---|
| `lite` | lite design | 原則なし。必要になった時点で `standard` 以上へ上げる。 | Lite validity、影響なし、scope containment。 | fresh spec-reviewer pass。 |
| `standard` | standard design | 推奨。設計差分、runtime behavior、責務境界、TDD handoff がある場合は使う。スキップ時は理由を report に残す。 | requirement traceability、責務境界、failure design、TDD handoff。 | fresh spec-reviewer pass。 |
| `strict` | strict design | 原則必須。利用不可なら unavailable と manual fallback 理由を report に残す。 | contract、compatibility、migration、readiness、review gate。 | delegated evidence adoption + fresh spec-reviewer pass。 |
| `critical` | critical design | 必須。必要に応じて clean-room / security / recovery consultant を追加する。 | safety、protected assets、no-go、manual gate、rollback/recovery。 | delegated evidence adoption + fresh spec-reviewer pass + manual gate。 |

`system-architect` は canonical `design.md` を直接編集しません。draft を採用する場合は、main orchestrator が採用箇所、却下箇所、理由を `report.md` に記録します。

## Plan Phase ルール

| Grade | Template | `implementation-planner` | Reviewer focus | Gate |
|---|---|---|---|---|
| `lite` | lite plan | 原則なし。必要になった時点で `standard` 以上へ上げる。 | 小さな checklist、focused verification、非影響の確認。 | fresh spec-reviewer pass。 |
| `standard` | standard plan | 推奨。TDD behavior、milestone decomposition、validation ladder が必要な場合は使う。スキップ時は理由を report に残す。 | milestone、Behavior Backlog、TDD Cycle、Validation Ladder、commit candidate。 | fresh spec-reviewer pass。 |
| `strict` | strict plan | 原則必須。利用不可なら unavailable と manual fallback 理由を report に残す。 | contract / compatibility / migration / review gate / evidence gate。 | delegated evidence adoption + fresh spec-reviewer pass。 |
| `critical` | critical plan | 必須。必要に応じて safety / recovery / migration dry-run review を追加する。 | safety gate、manual gate、dry-run、rollback、recovery、security/privacy。 | delegated evidence adoption + fresh spec-reviewer pass + manual gate。 |

`implementation-planner` は canonical `plan.md` を直接編集しません。Plan は reviewer-pass 済み requirement / design を前提にし、未解決設計判断を execution step に先送りしません。

## Review Phase ルール

| Grade | 必須 review | 追加 review | Pass 条件 |
|---|---|---|---|
| `lite` | fresh spec-reviewer | 原則なし | Lite 前提を破っていないこと、過剰 workflow ではないこと。 |
| `standard` | fresh spec-reviewer | 必要時に code/doc/repo reviewer | requirement-design-plan traceability と TDD 実行可能性があること。 |
| `strict` | fresh spec-reviewer | 必要時に code/doc/compatibility reviewer | contract、compatibility、migration、review gate が閉じていること。 |
| `critical` | fresh spec-reviewer | manual approval、security/safety/recovery reviewer | no-go / protected / manual / recovery gate が閉じていること。 |

Reviewer gate は grade により弱めません。変えるのは focus、追加 reviewer、manual gate、evidence density です。

## Report Evidence ルール

`report.md` の `Spec Authoring Gate` には、grade-aware authoring を行った証跡として次を残します。

| 項目 | 記録内容 |
|---|---|
| grade source | `authorized_profile`、manual escalation の有無、escalation reason。 |
| template source | materialize した design / plan template grade。 |
| delegated specialist | 使用した role、未使用理由、unavailable / skipped / blocked / stale の状態。 |
| adoption ledger | delegated evidence の採用、部分採用、却下、stale、blocked とその理由。 |
| reviewer evidence | phase、reviewer scope、freshness、verdict、fix summary。 |
| promotion decision | 次 phase へ進めるか、blocked / incomplete の理由。 |
| execution readiness | compose success ではなく readiness preflight を通った根拠、または未通過理由。 |

## Epic Canonical Docs への反映先

| Artifact | 反映内容 |
|---|---|
| `requirement.md` | `E-RQ-006` を `Grade Template Pack Selection And Artifact Readiness Contract` へ再定義する。`authorized_profile` と manual escalation の分離、fail-closed readiness、grade-aware authoring rules を acceptance criteria に追加する。 |
| `design.md` | `Profile Template Resolver`、`Template Materializer`、`Artifact Readiness Validator`、`Grade-Aware Authoring Router`、`Spec Authoring Evidence Gate` を design component として追加する。 |
| `plan.md` | 前回 draft の `W1` を削除し、Epic-level adopted design rule として扱う。Implementation Issue は R0 + G1〜G4 へ補正する。 |
| `report.md` | この discussion、手動テスト failure、GPT-5.5 Pro report、root-cause analysis を Evidence Adoption Ledger に記録する。 |

## 補正後の Issue 構成

前回 draft の `W1. Define Grade-Aware Issue Authoring Workflow Matrix` は Issue として作らない。代わりに、この文書の内容を Epic canonical docs へ採用する。

補正後の follow-up Issue は次の 5 本です。

```text
R0. Enforce Fail-Closed Issue Artifact Readiness Preflight
G1. Compile Grade-Aware Issue Planning Guidance
G2. Connect Delegated Specialist Role Routing To Guidance And Evidence
G3. Add Grade-Aware Spec Review And Evidence Gates
G4. Add Grade-Aware Issue Authoring Smoke Tests
```

### R0. Enforce Fail-Closed Issue Artifact Readiness Preflight

- 目的: 手動テストで見つかった false positive を先に閉じる。
- Scope:
  - unresolved placeholder detection
  - template-only / heading-only artifact detection
  - requirement / design / plan readiness classifier の fail-closed 化
  - `workflow status` / `guidance issue-execution` の readiness preflight 修正
- 前提:
  - この Issue は grade-aware authoring guidance より先に実装してよい。
  - ただし requirement/design/plan 作成時は本 artifact の grade rule を参照する。

### G1. Compile Grade-Aware Issue Planning Guidance

- 目的: `guidance issue-planning` が grade、phase、readiness state に応じて、必要な authoring action を提示できるようにする。
- Scope:
  - requirement / design / plan phase ごとの guidance
  - `authorized_profile` と manual escalation の表示
  - template materialization と readiness preflight の区別
  - Lite automatic default 禁止の明示

### G2. Connect Delegated Specialist Role Routing To Guidance And Evidence

- 目的: `system-architect` / `implementation-planner` を shipped skill file 前提ではなく delegated role routing として guidance / docs / evidence に接続する。
- Scope:
  - grade 別 specialist use rule
  - skipped / unavailable / manual fallback の report evidence
  - scope-local discussion output の adoption ledger
  - role が存在しない場合の fail-closed ではない manual path

### G3. Add Grade-Aware Spec Review And Evidence Gates

- 目的: fresh spec-reviewer gate を維持しつつ、grade 別 review focus と追加 gate を導入する。
- Scope:
  - lite / standard / strict / critical review focus
  - delegated evidence adoption check
  - manual approval / safety / recovery gate
  - stale / waived / provisional を pass 扱いしない検査

### G4. Add Grade-Aware Issue Authoring Smoke Tests

- 目的: Issue authoring workflow が grade 別に期待通り動くことを regression として固定する。
- Scope:
  - lite: specialist 不使用、軽量 gate
  - standard: guidance に推奨 routing と TDD plan focus
  - strict: delegated evidence requirement と compatibility focus
  - critical: manual/safety/recovery gate
  - R0 の false positive fixtures

## 採用判断

この文書は ADR candidate ではなく、Epic #224 の canonical docs amendment seed として扱うのが妥当です。理由は、長期アーキテクチャ判断というより、既存 Epic の `Dynamic Workflow Resource Allocation` を Issue authoring workflow に適用する具体設計だからです。

未解決のユーザー確認事項はありません。必要になった場合の確認点は「standard で `system-architect` / `implementation-planner` を必須にするか、推奨に留めるか」ですが、現時点の推奨は `standard=推奨、strict以上=原則必須` です。

## 次アクション

- Epic #224 `requirement.md` に、grade-aware authoring rules、`authorized_profile` / manual escalation の分離、fail-closed readiness contract を採用する。
- Epic #224 `design.md` に、Grade-Aware Authoring Router と Artifact Readiness Validator を設計 component として追加する。
- Epic #224 `plan.md` から follow-up Issue としての `W1` を外し、R0 + G1〜G4 の Issue 構成へ補正する。
- その後、R0 から順に Issue を具体化する。
