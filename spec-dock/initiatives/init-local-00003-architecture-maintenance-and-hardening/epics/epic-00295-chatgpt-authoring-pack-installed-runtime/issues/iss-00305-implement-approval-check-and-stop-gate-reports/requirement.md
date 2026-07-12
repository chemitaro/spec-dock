---
種別: 要件定義書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00305 Approval Stop Gate Reports — Issue 要件定義

## 1. 概要

この Issue は、ChatGPT authoring pack が生成した Initiative/Epic candidates または Epic/Issue candidates を実際の node creation へ進める前に、明示的な人間承認 evidence を machine-readable かつ reviewer-readable に検査する `authoring approval check` を実装する。

承認 evidence が存在しない、現在の candidate pack と紐付かない、対象 scope と一致しない、ChatGPT や tool による self-approval である、または authority boundary を越える claim を含む場合は fail-closed に停止する。

この Issue は承認 evidence の検査と stop-gate report の生成だけを扱い、Epic / Issue node creation、canonical docs adoption、`.assurance.json` mutation、reviewer pass、execution-ready、PR-ready、PR delivery は実行しない。

## 2. 背景

`epic-00295` は、ChatGPT GPT-5.5 Pro Extended を使った長時間・高精度の仕様書生成を SpecDock workflow に組み込むため、installed runtime / installed skills / prompt pack / ZIP review / candidate validation を整備している。

ここまでの Issue で、GitHub sync / `local-context` preflight、prompt pack、backend invocation、ZIP/tree review、staging、candidate validation、Issue draft adoption validation、`spec-dock-chatgpt-authoring` skill relationship は段階的に実装された。

一方で、candidate validation が pass しても、それだけでは人間が candidate decomposition を承認したことにはならない。Initiative を Epic に分割する、または Epic を Issue に分割する境界は、ユーザーが明示的に承認する stop gate であり、ChatGPT output や staged evidence が自己承認してはならない。

現状の `authoring approval check` は deferred command として存在するだけで、承認 evidence の digest / scope / approver / statement / authority boundary を機械的に判定できない。このため、candidate pack が stale になった場合や別 scope の承認 evidence を誤って再利用した場合に、後続の node creation 判断へ進む危険がある。

## 3. 親スコープから継承する制約

- ChatGPT output は `authority: evidence_only` の evidence であり、正本化は main orchestrator と SpecDock planning workflow が担う。
- `adoption_status: unreviewed` と `bundle_generation_not_promotion: true` を維持する。
- `pass` は command-local validation pass であり、canonical adoption、reviewer pass、execution-ready、PR-ready、PR delivery を意味しない。
- Runtime command は canonical docs、`.assurance.json`、Issue / Epic node tree を直接変更しない。
- 中間 Issue では per-Issue PR を作成しない。PR delivery は final quality gate Issue `iss-00307` に defer する。
- `--force` のような安易な bypass は導入しない。

## 4. 利用者と開始条件

| Actor | 役割 | この Issue との関係 |
|---|---|---|
| Human scope owner / maintainer | Candidate decomposition を承認または拒否する | approval evidence の唯一の正当な承認主体 |
| Main orchestrator | Evidence を確認し、後続 node creation の可否判断へ進める | `authoring approval check` の結果を stop-gate evidence として扱う |
| ChatGPT authoring lane | Candidate / draft evidence を生成する | approval evidence を自己発行できない |
| SpecDock runtime user | CLI を実行する | text / JSON report を取得する |

開始条件:

- Candidate pack が ZIP review / staging / candidate validation の対象になっている。
- Initiative/Epic candidates または Epic/Issue candidates を実際の node creation 判断へ進める前である。
- 人間承認 evidence が別途用意されている、または未承認で block されることを確認したい。

## 5. Scope

### 5.1 In scope

- `./spec-dock/scripts/spec-dock authoring approval check` の実装。
- approval evidence JSON の最小 schema 定義と検査。
- `candidate_kind`、requested scope、effective scope、parent scope の照合。
- candidate pack digest と source manifest hash の照合。
- `approver.actor_type=human` の検査。
- ChatGPT / assistant / tool / delegated authoring による self-approval の拒否。
- `approval_statement` の存在確認と unsafe payload 検査。
- missing / malformed / stale / mismatch / self-approval / forbidden authority claim の deterministic diagnostics。
- text / JSON output と safe `--report-path` report。
- 既存 deferred command list から `authoring approval check` を外し、実装済み command として登録する。
- provider-side runtime と dogfooding runtime path を使った focused tests。

### 5.2 Out of scope

- Epic / Issue node creation command の追加。
- ChatGPT output からの自動 GitHub Issue 作成。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` の実装。
- `.assurance.json` の mutation。
- canonical docs の直接更新。
- approval evidence の暗号署名検証。
- broad workflow docs / skill docs の全面改訂。user-facing docs 整備は後続 `iss-00306` を主対象にする。
- per-Issue PR delivery。

## 6. 承認 evidence contract

Approval evidence は少なくとも次の情報を持つ JSON object とする。

- `schema_version`: `1`
- `approval_evidence_kind`: `candidate_decomposition_approval`
- `approval_status`: `approved`
- `approval_scope`: `initiative-epic-node-creation` または `epic-issue-node-creation`
- `candidate_kind`: `initiative-epic` または `epic-issue`
- `requested_scope`: `scope_type`、`scope_id`、任意の `ref`
- `effective_scope`: `scope_type`、`scope_id`、任意の `ref`
- `candidate_pack`: `digest_algorithm`、`candidate_pack_digest`、任意の `source_manifest_hash`、任意の `candidate_ids`
- `approver`: `actor_type=human`、`id`、任意の `role`
- `approved_at`: ISO-like timestamp string
- `approval_statement`: 明示的な承認文
- 任意の `authority_boundary`: `node_creation_performed=false`、`canonical_written=false`、`assurance_mutated=false`、`reviewer_pass_claimed=false`、`execution_ready=false`、`pr_ready=false`

`authority_boundary` が存在する場合、いずれかの forbidden flag が true であってはならない。存在しない場合でも output result は forbidden flag をすべて false として返す。

## 7. Required behavior

### RB-001 Valid approval pass

有効な candidate pack、pass した review report、現在の candidate digest / scope に一致する human approval evidence がある場合、`authoring approval check` は `status=pass` を返す。

その場合でも、output は必ず次を示す。

- `authority=evidence_only`
- `adoption_status=unreviewed`
- `bundle_generation_not_promotion=true`
- `approval_required=true`
- `node_creation_performed=false`
- `canonical_written=false`
- `assurance_mutated=false`
- `reviewer_pass_claimed=false`
- `execution_ready=false`
- `pr_ready=false`

### RB-002 Missing approval blocked

Approval evidence が指定されない、または指定 path が存在しない場合は `status=blocked` とし、`missing_approval_evidence` を findings に含める。

### RB-003 Candidate digest stale

Approval evidence の `candidate_pack.candidate_pack_digest` が現在の candidate pack digest または明示された expected digest と一致しない場合は `status=stale` とし、`candidate_pack_digest_mismatch` を comparison に含める。

### RB-004 Source hash stale

Approval evidence の `candidate_pack.source_manifest_hash` または CLI の expected source manifest hash が現在の source manifest hash と一致しない場合は `status=stale` とする。

### RB-005 Scope mismatch blocked

Approval evidence の requested scope または effective scope が CLI expected scope、candidate kind、parent Initiative / Epic と一致しない場合は `status=blocked` とする。

### RB-006 Self-approval rejected

Approval evidence が ChatGPT、assistant、tool、delegated authoring lane、または non-human actor による承認を示す場合は `status=rejected` とし、`self_approval_forbidden` を findings に含める。

### RB-007 Malformed evidence fail

Approval evidence が invalid UTF-8、invalid JSON、non-object、required field missing、timestamp invalid、unsupported `schema_version`、unsupported `approval_status` の場合は `status=fail` または `blocked` にする。未承認 status は `blocked`、形式不正は `fail` とする。

### RB-008 Unsafe report rejected

`--report-path` が canonical docs、`.assurance.json`、symlink、または unsafe path を指す場合は `status=rejected` とし、report を書かない。

### RB-009 No mutation

Command 実行は read / validate / optional safe report write のみを行い、canonical docs、`.assurance.json`、Issue / Epic node tree、GitHub state を変更しない。

## 8. CLI acceptance criteria

- `authoring approval check --help` が deferred ではなく実装済み contract を表示する。
- help に `--input`、`--approval`、`--candidate-kind`、`--candidate-evidence`、`--expected-parent-initiative`、`--expected-parent-epic`、`--expected-requested-scope`、`--expected-effective-scope`、`--expected-candidate-pack-digest`、`--expected-candidate-evidence-digest`、`--expected-source-manifest-hash`、`--review-report`、`--format`、`--evidence-mode`、`--report-path` がある。
- `--force` は存在しない。
- `--candidate-kind initiative-epic` は `--expected-parent-initiative` を要求する。
- `--candidate-kind epic-issue` は `--expected-parent-epic` を要求する。
- `--expected-parent-initiative` と `--expected-parent-epic` を同時必須にしない。
- JSON output は stable key order で machine-readable にする。
- Text output は reviewer が status / digest / scope / findings / mutation boundary を読める内容にする。

## 9. Acceptance criteria

| ID | 条件 | 期待結果 |
|---|---|---|
| AC-001 | Help contract | `authoring approval check --help` が実装済み command の引数を表示し、`--force` を表示しない |
| AC-002 | Valid Epic/Issue approval | valid approval fixture で `status=pass`、authority boundary false |
| AC-003 | Valid Initiative/Epic approval | initiative-epic candidate kind でも valid approval が pass |
| AC-004 | Missing approval | approval evidence missing で `status=blocked` |
| AC-005 | Stale candidate digest | digest mismatch で `status=stale` |
| AC-006 | Requested scope mismatch | `status=blocked`、comparison に mismatch |
| AC-007 | Effective scope mismatch | `status=blocked`、comparison に mismatch |
| AC-008 | Self approval | ChatGPT / assistant / tool approval は `status=rejected` |
| AC-009 | Forbidden authority claim | approval statement や payload に forbidden authority claim があれば `status=rejected` |
| AC-010 | Sensitive statement | secret / raw transcript marker があれば `status=rejected` |
| AC-011 | Unsafe report path | canonical docs / `.assurance.json` / symlink report path は rejected |
| AC-012 | Safe report path | safe non-canonical path へ JSON report を書ける |
| AC-013 | No mutation | canonical docs、`.assurance.json`、node tree を変更しない |
| AC-014 | Candidate validation is not approval | candidate validation pass だけでは approval check は pass しない |
| AC-015 | Relay policy | この Issue で PR を作らず、final `iss-00307` へ relay する |

## 10. Edge cases

- approval evidence file がない。
- approval evidence が invalid UTF-8 / invalid JSON / non-object。
- required field がない。
- `schema_version` が `1` ではない。
- `approval_status` が `approved` ではない。
- `candidate_kind` が CLI と違う。
- parent Initiative / Epic が CLI expectation と違う。
- candidate digest が違う。
- source manifest hash が違う。
- requested scope / effective scope が違う。
- approver actor が human ではない。
- approval statement が空。
- approval statement に forbidden authority claim、secret marker、raw transcript marker がある。
- report path が unsafe。
- review report が non-pass。

## 11. Issue grade

推奨 Issue Grade は `strict` とする。

理由:

- public installed runtime command の実装である。
- workflow stop gate と authorization-like approval evidence を扱う。
- fail-open すると、人間承認なしに node creation 判断へ進む誤用を招く。
- ただし、この Issue 自体は irreversible mutation、GitHub mutation、`.assurance.json` mutation、node creation、secret storage を行わないため `critical` までは要求しない。

## 12. Evidence and adoption

この要件定義は、次の evidence を採用した。

- Issue-local draft requirement / design / plan artifacts.
- ChatGPT Use GPT-5.5 Pro Extended analysis artifact: `artifacts/20260708t061422z-chatgpt-approval-stop-gate-planning-analysis.md`.
- Parent Epic requirement / design / plan.
- Existing authoring runtime implementation and `tests/cli_runtime/test_authoring.py`.

採用時の補正:

- Draft の branch trace `codex/authoring-pack-installed-runtime` は現在 branch と一致しないため採用しない。
- Draft の `Issue Grade: standard` は stop gate の性質に合わせて `strict` へ引き上げる。
- Draft の Docs / Skill impact は後続 `iss-00306` へ寄せ、この Issue は runtime command と最小 diagnostics に絞る。
- `unsupported auto-creation diagnostics` は auto-creation command 追加ではなく、未実装 boundary を越えないことの確認として扱う。
