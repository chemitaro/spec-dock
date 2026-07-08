---
種別: 要件定義書（Issue）
ID: "iss-00302"
タイトル: "Initiative Epic Validation"
関連GitHub: ["#302"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00302 Initiative Epic Validation — Issue 要件定義

## 1. 目的

この Issue は、ChatGPT batch planning output に含まれる Initiative -> Epic candidates と Epic -> Issue candidates を、node creation 前の evidence-only candidate として検証する runtime command を実装する。

検証 pass は local validation pass であり、Epic / Issue node creation、canonical adoption、`.assurance.json` mutation、reviewer pass、execution-ready、PR-ready、mergeable PR を意味しない。

## 2. 背景

Epic `epic-00295` は、ChatGPT 5.5 Pro Extended による長時間 authoring output を SpecDock installed runtime / installed skill surface で扱うための仕組みを整備している。

前段 Issue `iss-00301` では、ChatGPT output ZIP/tree を canonical docs に触れる前に `authoring pack review` / `authoring pack stage` で安全検査し、staged evidence として配置できるようにした。

次に必要なのは、staged evidence 内の Initiative -> Epic candidate と Epic -> Issue candidate を、実際の node creation 前に検証し、重複、境界曖昧性、親スコープ不一致、危険なパス、authority claim、secret/raw transcript、stale source を検出できるようにすることである。

## 3. 親 Epic から継承する条件

- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` に置く。
- Dogfood workspace の `spec-dock/...` は installed runtime mirror / validation surface として扱う。
- Runtime は `commands/`、`application/`、`domain/`、`presentation/` の layered architecture を維持する。
- ChatGPT-derived output は `authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を保持する。
- Candidate validation は node creation、canonical adoption、`.assurance.json` mutation、reviewer pass、execution-ready、PR-ready を行わない。
- Candidate validation pass は human approval / reviewer approval ではない。
- 中間 Issue では PR を作成せず、Epic-wide quality gate / PR delivery は `iss-00307` に defer する。

## 4. Scope

この Issue で実現すること:

- `./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates` を deferred command から implemented command へ昇格する。
- `./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates` を deferred command から implemented command へ昇格する。
- Initiative -> Epic candidate schema / validation contract を定義する。
- Epic -> Issue candidate schema / validation contract を定義する。
- Candidate index、candidate payload、draft requirement/design/plan path、parent trace、boundary、dependency、grade/profile recommendation を検証する。
- Candidate ID / title / slug の重複、scope signature の重複、scope/non-scope overlap、明確な boundary overlap を deterministic diagnostics として検出する。
- Parent Initiative / Epic mismatch、source manifest hash mismatch、review digest mismatch を `stale` に分類する。
- malformed JSON、non-object JSON、missing required fields、empty candidate list、unsupported grade/profile を `fail` に分類する。
- unsafe path、host-local path、hidden path、secret-looking path、unsupported suffix、binary / oversized Markdown、secret/raw transcript、forbidden authority claim を `rejected` に分類する。
- Text / JSON output と optional report output で、validation pass と approval / adoption / reviewer pass / readiness / node creation を明確に分離する。
- Provider-side runtime と dogfood mirror の両方で tests / smoke を通す。

この Issue で実現しないこと:

- Initiative / Epic / Issue node creation。
- Candidate output の canonical docs への直接 adoption。
- `.assurance.json` の作成・更新。
- `authorized_profile` の決定。
- reviewer pass / spec-review pass / qa-review pass / code-review pass の付与。
- execution-ready / PR-ready / mergeable PR の付与。
- `authoring validate issue-draft-adoption`、`authoring validate selected-skeleton-fill`、`authoring approval check` の実装。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring set-authorized-profile` の実装。
- 中間 Issue 単位の PR 作成。

## 5. Actor / Trigger

| Actor | 役割 | Trigger |
| --- | --- | --- |
| Codex orchestrator | ChatGPT batch planning output を検証し、採否判断材料にする | `authoring validate initiative-epic-candidates`; `authoring validate epic-issue-candidates` |
| SpecDock runtime user | consumer repo 上で installed command を実行する | provider / dogfood runtime smoke |
| ChatGPT backend | candidate pack / draft docs を生成する | `authoring backend invoke` 後の review / stage output |
| scope owner / human approver | node creation 前の explicit approval を判断する | validation report 確認後の別 gate |
| spec-reviewer / code-reviewer / qa-reviewer | canonical adoption や実行前 gate を評価する | command pass ではなく fresh reviewer gate で判断 |

## 6. Functional Requirements

| ID | 要件 |
| --- | --- |
| RQ-001 | `authoring validate initiative-epic-candidates --help` は implemented command として `--input`、`--expected-parent-initiative`、`--review-report`、`--expected-source-manifest-hash`、`--evidence-mode`、`--report-path`、`--format` を案内する。 |
| RQ-002 | `authoring validate epic-issue-candidates --help` は implemented command として `--input`、`--expected-parent-epic`、`--review-report`、`--expected-source-manifest-hash`、`--evidence-mode`、`--report-path`、`--format` を案内する。 |
| RQ-003 | 両 command は review/stage 済み evidence directory または reviewed authoring pack tree を input とし、review report が見つからない、または review status が `pass` でない場合は fail-closed する。 |
| RQ-004 | 全 output は `authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を保持する。 |
| RQ-005 | Initiative -> Epic validator は parent Initiative trace、candidate Epic boundaries、scope/non-scope、dependencies、draft requirement/design/plan、human approval before Epic node creation marker を検証する。 |
| RQ-006 | Epic -> Issue validator は parent Epic trace、Issue boundaries、dependency order、draft requirement/design/plan、grade recommendation、profile recommendation advisory-only を検証する。 |
| RQ-007 | Candidate index / candidate JSON / profile JSON / Markdown draft は UTF-8 text として読み、malformed JSON、non-object JSON、missing required fields、empty required arrays を `fail` にする。 |
| RQ-008 | Candidate ID、title、slug の重複は `fail` とし、scope signature の重複または明確な boundary overlap は deterministic diagnostics に含める。 |
| RQ-009 | parent scope mismatch、source manifest hash mismatch、review digest mismatch は `stale` とする。 |
| RQ-010 | path traversal、absolute / host-local path、hidden path、secret-looking path、unsupported suffix、symlink、executable、binary、oversized file は `rejected` とする。 |
| RQ-011 | secret-like text、credential / token / private key、raw transcript は `rejected` とし、raw value は durable report に残さない。 |
| RQ-012 | `authorized_profile` は validator が決定しない。Issue candidate profile 内では `authorized_profile: null` のみを許容し、recommendation は advisory-only を必須にする。 |
| RQ-013 | Forbidden authority claims（canonical adoption、`.assurance.json` mutation、reviewer pass、execution-ready、PR-ready、PR delivery、mergeable PR、node creation without approval）は `rejected` とする。 |
| RQ-014 | Output は validation pass と approval / adoption / reviewer pass / execution-ready / PR-ready / node creation を区別し、`node_creation_performed=false`、`canonical_written=false`、`assurance_mutated=false`、`reviewer_pass_claimed=false` を明示する。 |
| RQ-015 | Optional report path は canonical docs、active docs、`.assurance.json`、symlink parent を拒否する。 |
| RQ-016 | Provider-side runtime と dogfood mirror の両方を更新し、installed runtime behavior を検証する。 |
| RQ-017 | Compatibility helper `validate_issue_candidates.py` と `validate_initiative_epic_candidates.py` は runtime contract と同じ authority / status / safety semantics を返す。 |
| RQ-018 | finish evidence は no-per-Issue-PR rationale、local verification、`iss-00307` への PR delivery defer を記録する。 |

## 7. Acceptance Criteria

| ID | 受け入れ条件 | 証跡 |
| --- | --- | --- |
| AC-001 | `authoring validate initiative-epic-candidates` が deferred diagnostics ではなく implemented command として help / JSON output を返す。 | CLI test |
| AC-002 | `authoring validate epic-issue-candidates` が deferred diagnostics ではなく implemented command として help / JSON output を返す。 | CLI test |
| AC-003 | Existing deferred command tests は更新され、`iss-00303` / `iss-00305` の deferred commands は引き続き fail-closed を検証する。 | pytest |
| AC-004 | valid Initiative -> Epic fixture は `status=pass`、`authority=evidence_only`、candidate_count、valid_candidate_count、approval_required を出力し、node creation を行わない。 | JSON fixture |
| AC-005 | valid Epic -> Issue fixture は parent Epic trace、Issue dependencies、draft requirement/design/plan、profile recommendation advisory-only を検証し、`authorized_profile` を決定しない。 | JSON fixture |
| AC-006 | malformed JSON、non-object JSON、missing required fields、empty candidate list は `fail` になる。 | negative fixture |
| AC-007 | duplicate IDs / titles / slugs、duplicate scope signatures、overlapping boundaries は deterministic diagnostics を返す。 | negative fixture |
| AC-008 | path traversal / host-local path / hidden path / unsupported suffix / binary / oversized draft は `rejected` になる。 | negative fixture |
| AC-009 | secret-like payload / raw transcript / credential / token / private key は `rejected` になり、raw secret value は report に出ない。 | negative fixture |
| AC-010 | forbidden authority claim は `rejected` になり、warning に downgrade されない。 | negative fixture |
| AC-011 | `authorized_profile` が non-null、または profile recommendation が advisory-only でない場合は `rejected` になる。 | negative fixture |
| AC-012 | source manifest hash mismatch、parent Initiative mismatch、parent Epic mismatch、review digest mismatch は `stale` になる。 | negative fixture |
| AC-013 | report path が canonical docs / `.assurance.json` / symlink target の場合、report は書かれず `rejected` になる。 | filesystem test |
| AC-014 | text output と JSON output は `pass` を adoption / approval / reviewer pass / execution readiness と誤読させる語を含まない。 | stdout assertions |
| AC-015 | provider-side runtime path と dogfood installed runtime path の両方で smoke test が通る。 | pytest / subprocess |
| AC-016 | `./spec-dock/scripts/spec-dock validate`、関連 `pytest`、`git diff --check` が通る。 | local verification |
| AC-017 | この Issue は PR delivery を行わず、finish handoff で `iss-00307` への defer rationale を記録する。 | `report.md` |

## 8. Failure Modes

| Failure mode | Status | 期待される扱い |
| --- | --- | --- |
| input path missing / unreadable | `blocked` | report 可能な診断を返し、canonical docs を変更しない |
| review report missing | `blocked` | review/stage を先に実行するよう案内 |
| review report status `stale` | `stale` | candidate validation を進めない |
| review report status `rejected` | `rejected` | candidate validation を進めない |
| review report status `fail` | `fail` | candidate validation を進めない |
| review report status `blocked` or unsupported non-pass status | `blocked` | candidate validation を進めない |
| malformed candidate JSON / non-object JSON | `fail` | schema failure として出力 |
| required candidate fields missing | `fail` | missing field diagnostics |
| duplicate IDs / titles / slugs | `fail` | deterministic comparison diagnostics |
| ambiguous / overlapping boundaries | `fail` | candidate comparison report に group を出す |
| parent Initiative / Epic mismatch | `stale` | expected parent を再確認 |
| source manifest hash mismatch | `stale` | pack を再生成 |
| unsafe artifact path | `rejected` | path を report し、payload 内容は漏らさない |
| secret / raw transcript payload | `rejected` | raw secret / transcript body を report に含めない |
| unsupported grade / profile value | `fail` | allowed value diagnostics |
| `authorized_profile` claim | `rejected` | advisory-only recommendation へ修正要求 |
| canonical adoption / reviewer pass / execution-ready / PR-ready claim | `rejected` | warning downgrade 禁止 |
| report target is canonical docs / `.assurance.json` | `rejected` | report を書かない |
| intermediate Issue attempts PR delivery | `blocked` | `iss-00307` へ defer |

## 9. Grade

Issue Grade は `standard` とする。

根拠:

- Consumer-visible CLI behavior を変更し、deferred command を implemented command に昇格する。
- Candidate schema、authority boundary、safe path / secret / raw transcript scanning、stale source manifest、profile recommendation boundary を扱う。
- Provider-side source-of-truth と dogfood mirror の両方に変更が必要である。
- DB migration、external irreversible mutation、credentialed GitHub mutation、PR delivery は含まない。

## 10. Evidence Sources

- ChatGPT Use / Oracle session `specdock-iss-00302-planning` transcript: `/Users/iwasawayuuta/.oracle/sessions/specdock-iss-00302-planning/artifacts/transcript.md`
- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/plan.md`
- `spec-dock/active/issue/artifacts/20260707t171259z-draft-requirement-validate-initiative-epic-and-epic-issue-candidates-draft-requirement.md`
- `spec-dock/active/issue/artifacts/20260707t171300z-draft-design-validate-initiative-epic-and-epic-issue-candidates-draft-design.md`
- `spec-dock/active/issue/artifacts/20260707t171300z-01-draft-plan-validate-initiative-epic-and-epic-issue-candidates-draft-plan.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/prompt_pack_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py`
- `tests/cli_runtime/test_authoring.py`
