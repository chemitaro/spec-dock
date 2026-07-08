# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a4deadc-45d8-83e8-997e-64be58d0b15c

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00305-implement-approval-check-and-stop-gate-reports
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt file as the task brief. Inspect the GitHub repository current branch first, then use attached files as supplementary context. Return the requested planning recommendation.

## Answer

## 結論

推奨は、`iss-00305` を **「承認 evidence を検証する stop gate 実装」だけに閉じる strict-grade の小さな runtime slice** として扱うことです。`authoring approval check` は実装対象にしますが、Epic/Issue node creation、canonical docs adoption、`.assurance.json` 更新、reviewer pass、execution-ready、PR-ready は引き続き対象外にします。

GitHub connector で現行ブランチ `iss-00305-implement-approval-check-and-stop-gate-reports` を確認しました。現行ブランチでは Issue の `requirement.md` はテンプレート未具体化状態で、`design.md` と `plan.md` は「まだ合成されていない placeholder」であり、本文を書き始めない指示が残っています。
一方、Epic 側では `authoring approval check` が初期 command surface に含まれ、approval check は「node creation 前の explicit human approval evidence がない場合に block」するものとして定義されています。

現在の runtime 実装では `authoring approval check` は `_DEFERRED_COMMANDS` に残っており、実行時は `status=deferred` / `authority=evidence_only` / `next_issue=iss-00305` を返すだけです。
したがって `iss-00305` の実装判断は、「この deferred entry を実実装へ置換し、承認 evidence の machine-readable / reviewer-readable report を出す」ことに集中すべきです。

以下は patch ではなく、Codex が canonical docs へ採否統合するための evidence-only planning recommendation です。添付 brief が要求する 1〜9 の成果物に沿って整理しています。

---

## 根拠

* Epic は ChatGPT output を正本ではなく evidence-only とし、canonical adoption、`.assurance.json` mutation、authorized profile、reviewer pass、execution-ready、PR-ready を禁止しています。
* Epic の対象外には node creation / adopt / reviewer-pass / profile-setting / execution-ready / pr-ready 系 command と中間 Issue の PR delivery が明示されています。
* Runtime requirements は command output に machine-readable summary と human-readable diagnostics を要求し、`pass` は command-local validation pass であって canonical adoption 等ではないとしています。
* Candidate / adoption requirements は approval check を「node creation 前の explicit human approval evidence がない場合に block」としています。
* Existing domain contract には `authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=True`、`node_creation_performed=False` 等の authority 境界 field が既にあります。
* Candidate contract には candidate pack の `tree_digest`、source manifest hash、parent trace、boundary、authority claim rejection の部品が既にあり、approval check でも再利用できます。

---

## 1. 推奨 `requirement.md` content（正式日本語案）

````md
---
種別: 要件定義書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00305 Approval Stop Gate Reports — Issue 要件定義

## 1. 概要

### 1.1 目的

この Issue は、Initiative から Epic candidates を作る前、および Epic から Issue candidates を作る前に必要な explicit human approval を、machine-readable かつ reviewer-readable な evidence として検証する `authoring approval check` を実装する。  
承認 evidence が missing / stale / scope mismatch / candidate pack mismatch / self-approval の場合は fail-closed に停止する。  
この Issue は承認確認だけを扱い、Epic / Issue node creation、canonical adoption、`.assurance.json` 更新、reviewer pass、execution-ready、PR-ready は実行しない。

### 1.2 観測可能な成果

- `./spec-dock/scripts/spec-dock authoring approval check` が provider-side installed runtime に実装される。
- 承認 evidence と candidate pack の digest / scope / approver / timestamp / statement を検証できる。
- 正常時は `status=pass` を返すが、これは command-local validation pass であり node creation 実行許可や canonical adoption ではない。
- 異常時は `blocked` / `stale` / `rejected` / `fail` の deterministic diagnostics を返す。
- JSON output と text output の双方で、承認状態、scope、candidate digest、authority boundary、node creation が未実行であることを確認できる。
- `--report-path` 指定時、安全な non-canonical path に machine-readable report を書ける。
- canonical docs、`.assurance.json`、Issue / Epic node は変更されない。

### 1.3 Issue 種類

- [x] 新規振る舞いの追加
- [x] CLI / script 挙動変更
- [x] workflow / skill / agent導線の変更
- [x] metadata / sync / validate / lifecycle の変更
- [x] セキュリティ・プライバシー / authorization に関係する変更
- [ ] migration / compatibility を伴う変更

## 2. 背景・現状

### 2.1 現在の状態

- Epic 00295 では ChatGPT authoring pack workflow を installed runtime / skill surface として整備している。
- 既存 runtime には preflight、pack prepare、backend invoke、pack review / stage、candidate validation、issue draft adoption validation がある。
- `authoring approval check` は command surface に含まれているが、現行実装では deferred command として扱われている。
- Candidate validation pass は node creation の十分条件ではない。
- Human approval がなければ Epic / Issue node creation へ進んではならない。

### 2.2 現在の問題

- candidate pack が valid でも、人間がその candidate decomposition を承認した evidence がない。
- ChatGPT output や staged evidence が approval / reviewer pass / execution readiness を自己主張する余地が残る。
- approval が古い candidate pack や別 scope に紐づく場合、reviewer が目視で見落とす危険がある。
- 現在の deferred diagnostic だけでは、承認 evidence の pass / stale / mismatch を機械判定できない。

## 3. 親スコープと継承条件

### 3.1 親 Epic

- Epic ID: `epic-00295`
- 継承する制約:
  - ChatGPT output は evidence-only。
  - `pass` は command-local validation pass であり、canonical adoption / reviewer pass / execution-ready / PR-ready ではない。
  - Generated pack / staged evidence は `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を維持する。
  - Runtime command は canonical docs を直接上書きしない。
  - Node creation / adopt / reviewer-pass / profile-setting / execution-ready / pr-ready は初期実装対象外。
  - 中間 Issue では PR delivery を行わない。

### 3.2 この Issue で再定義してはいけないもの

- Candidate pack schema 全体。
- ZIP safety contract 全体。
- GitHub sync preflight contract 全体。
- Issue draft adoption workflow。
- Fresh reviewer gate semantics。
- Node creation workflow。
- Final PR delivery workflow。

## 4. Actor / Trigger

| Actor | 役割 | この Issue との関係 |
|---|---|---|
| Human scope owner / reviewer | Candidate decomposition を承認または拒否する | approval evidence の発行元 |
| Main orchestrator / Codex | Evidence を採否判断し canonical docs へ統合する | approval check result を後続判断材料にする |
| ChatGPT authoring lane | Candidate / draft evidence を生成する | approval を自己発行できない |
| Runtime CLI user | `authoring approval check` を実行する | machine-readable / reviewer-readable report を得る |

### Trigger

- [x] CLI command
- [x] workflow / skill stop gate
- [x] human approval evidence review

## 5. Scope

### 5.1 In scope

- `authoring approval check` の CLI contract 実装。
- approval evidence JSON schema の最小実装。
- approval evidence の required field 検証。
- candidate pack digest の照合。
- requested scope / effective scope の照合。
- candidate kind と parent scope の照合。
- approver が human であることの検証。
- ChatGPT / tool / self-approval の拒否。
- approval timestamp の parseability と report 表示。
- approval statement の存在確認と安全性検査。
- missing / malformed / stale / mismatch / forbidden authority claim の fail-closed diagnostics。
- safe `--report-path` への JSON report 出力。
- text / JSON renderer。
- provider-side installed runtime と dogfood runtime path の focused tests。
- 既存 deferred test の更新。

### 5.2 Out of scope

- Epic / Issue node creation。
- `authoring create-issues-from-zip` の実装。
- `authoring adopt` の実装。
- `authoring mark-reviewer-pass` の実装。
- `authoring set-authorized-profile` の実装。
- `authoring issue-execution-ready` / `authoring pr-ready` の実装。
- approval evidence の暗号署名検証。
- GitHub Issue / PR 作成。
- `.assurance.json` 変更。
- canonical docs 直接更新。
- planning skill 文書全体の user-facing 改訂。必要最小の command help / diagnostics 以外は C11 へ送る。

### 5.3 Unchanged

- `authority: evidence_only` / `adoption_status: unreviewed` / `bundle_generation_not_promotion: true` の evidence boundary。
- Candidate validators の「node creation しない」性質。
- Stage は EAL candidate を作るだけで final EAL row ではないという境界。
- 中間 Issue で PR delivery しない relay policy。

## 6. Required behavior

### BH-001: 有効な human approval evidence は pass になる

- Given:
  - candidate pack が valid。
  - review report が `status=pass`。
  - approval evidence が required fields を持つ。
  - approval evidence の candidate digest / requested scope / effective scope が現在の input と一致する。
  - approver が human で ChatGPT self-approval ではない。
- When:
  - `authoring approval check` を実行する。
- Then:
  - `status=pass`。
  - `approval_result=approved`。
  - `node_creation_performed=false`。
  - `canonical_written=false`。
  - `assurance_mutated=false`。
  - `reviewer_pass_claimed=false`。
  - `execution_ready=false`。
  - `pr_ready=false`。

### BH-002: approval evidence がない場合は blocked

- Given:
  - candidate pack はある。
  - approval evidence path が存在しない、または指定されていない。
- When:
  - approval check を実行する。
- Then:
  - `status=blocked`。
  - finding に `missing_approval_evidence` を含む。
  - node creation は実行されない。

### BH-003: candidate digest mismatch は stale

- Given:
  - approval evidence に記録された `candidate_pack_digest` が現在の candidate pack digest と一致しない。
- Then:
  - `status=stale`。
  - comparison に `candidate_pack_digest_mismatch` を含む。
  - node creation は実行されない。

### BH-004: requested / effective scope mismatch は blocked

- Given:
  - approval evidence の `requested_scope` または `effective_scope` が CLI 期待値または candidate pack parent scope と一致しない。
- Then:
  - `status=blocked`。
  - comparison に `requested_scope_mismatch` または `effective_scope_mismatch` を含む。
  - node creation は実行されない。

### BH-005: ChatGPT self-approval は rejected

- Given:
  - approval evidence の approver が `actor_type=chatgpt`、`actor_type=assistant`、`created_by_role=chatgpt-authoring`、またはそれに相当する self-approval を示す。
- Then:
  - `status=rejected`。
  - finding に `self_approval_forbidden` を含む。
  - node creation は実行されない。

### BH-006: malformed approval evidence は fail

- Given:
  - approval evidence が JSON として壊れている、non-object、required field 欠落、timestamp 不正。
- Then:
  - `status=fail`。
  - field-level finding を返す。
  - node creation は実行されない。

### BH-007: unsafe report path は rejected

- Given:
  - `--report-path` が canonical docs、`.assurance.json`、symlink、または unsafe path を指す。
- Then:
  - `status=rejected`。
  - report は書かれない。

## 7. Acceptance criteria

### AC-001: CLI help

- `./spec-dock/scripts/spec-dock authoring approval check --help` が実装済み contract を表示する。
- `--input`、`--approval`、`--candidate-kind`、`--expected-parent-initiative` / `--expected-parent-epic`、`--expected-requested-scope`、`--expected-effective-scope`、`--expected-candidate-pack-digest`、`--expected-source-manifest-hash`、`--review-report`、`--format`、`--evidence-mode`、`--report-path` を確認できる。
- `--force` は存在しない。

### AC-002: Valid approval pass

- Valid approval fixture で `status=pass`。
- output は `authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を持つ。
- `approval_status=approved`。
- `node_creation_performed=false`。

### AC-003: Missing approval blocked

- approval evidence がない場合 `status=blocked`。
- `missing_approval_evidence` を返す。

### AC-004: Stale candidate digest

- approval evidence の digest が現在の candidate pack digest と違う場合 `status=stale`。
- `candidate_pack_digest_mismatch` を返す。

### AC-005: Scope mismatch

- requested scope mismatch / effective scope mismatch は fail-closed。
- status は `blocked`。
- comparison に mismatch reason を残す。

### AC-006: Self approval rejected

- ChatGPT / assistant / tool-generated self-approval は `status=rejected`。
- `self_approval_forbidden` を返す。

### AC-007: Candidate validation is not node creation approval

- candidate validation pass だけでは `authoring approval check` は pass しない。
- approval evidence がなければ blocked。
- `approval_required=true` を出力する。

### AC-008: No mutation

- 実行前後で canonical docs / `.assurance.json` / Issue or Epic node tree が変更されない。
- output に `canonical_written=false`、`assurance_mutated=false`、`node_creation_performed=false` を持つ。

### AC-009: Safe report output

- safe non-canonical report path には JSON report が書かれる。
- unsafe report path は rejected で report を書かない。

### AC-010: Deferred auto-creation boundary

- `create-issues-from-zip` 等の auto-creation command は実装しない。
- 既に parser placeholder が存在する場合のみ unsupported / deferred fail-closed diagnostics を返す。
- 存在しない場合は help / docs 上で available command として表示しない。

## 8. Edge cases

- EC-001: approval JSON が存在しない → `blocked`。
- EC-002: approval JSON が invalid UTF-8 / invalid JSON → `fail`。
- EC-003: approval JSON が object ではない → `fail`。
- EC-004: `schema_version` 不一致 → `fail`。
- EC-005: `approval_status != approved` → `blocked`。
- EC-006: `candidate_pack_digest` mismatch → `stale`。
- EC-007: source manifest hash mismatch → `stale`。
- EC-008: requested scope mismatch → `blocked`。
- EC-009: effective scope mismatch → `blocked`。
- EC-010: parent Initiative / Epic mismatch → `stale` または `blocked`。推奨は candidate pack mismatch として `stale`。
- EC-011: self-approval → `rejected`。
- EC-012: forbidden authority claim → `rejected`。
- EC-013: approval statement missing → `fail`。
- EC-014: approval statement に secret / raw transcript marker → `rejected`。
- EC-015: unsafe report path → `rejected`。
- EC-016: candidate validation status non-pass → non-zero。status は candidate status を尊重し、approval pass にはしない。

## 9. 契約例

### Valid approval evidence

```json
{
  "schema_version": 1,
  "approval_evidence_kind": "candidate_decomposition_approval",
  "approval_status": "approved",
  "approval_scope": "epic-issue-node-creation",
  "candidate_kind": "epic-issue",
  "requested_scope": {
    "scope_type": "epic",
    "scope_id": "epic-00295",
    "ref": "iss-00305-implement-approval-check-and-stop-gate-reports"
  },
  "effective_scope": {
    "scope_type": "epic",
    "scope_id": "epic-00295",
    "ref": "iss-00305-implement-approval-check-and-stop-gate-reports"
  },
  "candidate_pack": {
    "digest_algorithm": "sha256-tree-v1",
    "candidate_pack_digest": "<tree_digest>",
    "source_manifest_hash": "<source_manifest_hash>",
    "candidate_ids": ["iss-candidate-001", "iss-candidate-002"]
  },
  "approver": {
    "actor_type": "human",
    "id": "iwasawayuuta",
    "role": "scope_owner"
  },
  "approved_at": "2026-07-08T00:00:00Z",
  "approval_statement": "I approve this candidate decomposition for the stated scope before node creation.",
  "authority_boundary": {
    "node_creation_performed": false,
    "canonical_written": false,
    "assurance_mutated": false,
    "reviewer_pass_claimed": false,
    "execution_ready": false,
    "pr_ready": false
  }
}
````

## 10. 非機能要求

* deterministic: 同じ input から同じ status / findings / comparison を返す。
* fail-closed: 不明または不足は pass にしない。
* safe output: canonical docs / `.assurance.json` には report を書かない。
* privacy: approval statement は secret / credential / raw transcript marker を含む場合 rejected。
* compatibility: old workspace migration は行わない。
* authority boundary: output は validation report であり adoption / reviewer pass / execution readiness ではない。

## 11. 制約

* CON-001: ChatGPT は self-approval できない。fixed。
* CON-002: Candidate validation pass は node creation approval ではない。fixed。
* CON-003: Approval check は read/validate/report のみで node を作らない。fixed。
* CON-004: `pass` は command-local validation pass。fixed。
* CON-005: 中間 Issue で PR delivery しない。fixed。
* CON-006: `--force` style bypass は導入しない。fixed。

## 12. Grade

推奨 Issue Grade: `strict`

理由:

* public CLI contract を追加する。
* workflow stop gate / authorization-like approval evidence を扱う。
* fail-closed semantics を誤ると node creation boundary を越えた誤用につながる。
* ただし、この Issue 自体は node creation / GitHub mutation / secret handling / irreversible migration を行わないため `critical` までは不要。

## 13. 設計への引き渡し

設計で扱う論点:

* approval evidence schema。
* candidate pack digest 算出と照合。
* requested / effective scope 正規化。
* self-approval rejection。
* status mapping。
* safe report path。
* renderer / command integration。
* existing candidate validation contract との重複最小化。

## 14. 実装計画への引き渡し

計画で分解すべき成果:

* Domain result/schema。
* Application approval check use case。
* CLI args / dispatch。
* Text / JSON renderer。
* Tests / fixtures。
* Existing deferred command test update。
* Final report evidence / relay evidence。

## 15. 未確定事項

* Q-001: approval evidence の durable storage location。

  * 推奨: この Issue では CLI input path と safe report path のみ定義し、標準保存場所は C11 docs または上位 workflow へ defer。
* Q-002: 署名強度。

  * 推奨: 暗号署名検証は対象外。human approver field と statement / timestamp の machine-checkable evidence まで。
* Q-003: scope object の exact schema。

  * 推奨: `scope_type`、`scope_id`、`ref` を必須最小 field とする。

````

---

## 2. 推奨 `design.md` content（正式日本語案）

```md
---
種別: 設計書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "strict"
---

# iss-00305 Approval Stop Gate Reports — 設計

## 1. 設計結論

`authoring approval check` を、既存 authoring runtime の candidate validation 後に置く read-only stop gate として実装する。  
入力は staged candidate pack / approval evidence / optional review report / expected scope metadata であり、出力は command-local validation report である。  
この command は node creation、canonical docs 更新、`.assurance.json` 更新、reviewer pass 付与、execution-ready / PR-ready 判定を行わない。

## 2. 対象 layer

### 2.1 Provider-side source of truth

主対象:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/approval_check_renderer.py
tests/cli_runtime/test_authoring.py
````

補助対象:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py
```

`diagnostics.py` は共通 diagnostic helper が必要な場合だけ触る。現行の authoring runtime は feature ごとに renderer file を分けているため、approval check も `approval_check_renderer.py` を追加する方が既存 layout に合う。

## 3. Command integration

現状:

```python
_DEFERRED_COMMANDS = {
    "authoring_approval_check": ("authoring approval check", "iss-00305"),
}
```

設計後:

* `_DEFERRED_COMMANDS` から `authoring_approval_check` を削除する。
* `AuthoringApprovalCheckArgs` を追加する。
* `_add_approval_check_arguments` を追加する。
* `_approval_check_args` を追加する。
* `_run_approval_check` を追加する。
* `_expect_approval_check_args` を追加する。
* `run_approval_check` と renderer を import する。

## 4. CLI contract

推奨 command:

```bash
./spec-dock/scripts/spec-dock authoring approval check \
  --input <staged-pack-or-pack-root> \
  --approval <approval-evidence.json> \
  --candidate-kind epic-issue \
  --expected-parent-epic epic-00295 \
  --expected-requested-scope epic:epic-00295 \
  --expected-effective-scope epic:epic-00295 \
  --expected-candidate-pack-digest <sha256-tree-v1> \
  --expected-source-manifest-hash <sha256> \
  --review-report <review-report.json> \
  --evidence-mode github-synced \
  --format json \
  --report-path <safe-noncanonical-report.json>
```

Initiative → Epic の場合:

```bash
./spec-dock/scripts/spec-dock authoring approval check \
  --input <staged-pack-or-pack-root> \
  --approval <approval-evidence.json> \
  --candidate-kind initiative-epic \
  --expected-parent-initiative init-local-00003 \
  --expected-requested-scope initiative:init-local-00003 \
  --expected-effective-scope initiative:init-local-00003 \
  --format json
```

### Arguments

| Arg                                |                       必須 | 用途                                                       |
| ---------------------------------- | -----------------------: | -------------------------------------------------------- |
| `--input`                          |                      yes | staged candidate pack または `specdock-authoring-pack` root |
| `--approval`                       |                      yes | human approval evidence JSON                             |
| `--candidate-kind`                 |                      yes | `initiative-epic` / `epic-issue`                         |
| `--expected-parent-initiative`     |              conditional | initiative-epic の parent trace                           |
| `--expected-parent-epic`           |              conditional | epic-issue の parent trace                                |
| `--expected-requested-scope`       |                      yes | approval evidence の requested scope 期待値                  |
| `--expected-effective-scope`       |                      yes | approval evidence の effective scope 期待値                  |
| `--expected-candidate-pack-digest` | optional but recommended | stale approval 検出                                        |
| `--expected-source-manifest-hash`  |                 optional | source stale 検出                                          |
| `--review-report`                  |                 optional | candidate pack review report 明示指定                        |
| `--evidence-mode`                  |                       no | `github-synced` / `local-context`                        |
| `--format`                         |                       no | `text` / `json`                                          |
| `--report-path`                    |                       no | safe non-canonical report path                           |

`--force` は追加しない。

## 5. Domain design

### 5.1 Status types

```python
ApprovalCheckStatus = Literal["pass", "fail", "blocked", "stale", "rejected"]
ApprovalDecisionStatus = Literal["approved", "rejected", "revoked", "superseded", "draft"]
```

### 5.2 Result object

`candidate_contract.py` に最小追加する案を第一候補にする。

```python
@dataclass(frozen=True)
class ApprovalCheckResult:
    status: ApprovalCheckStatus
    input_path: str
    approval_path: str | None
    candidate_kind: CandidateKind
    authority: str = AUTHORITY
    adoption_status: str = ADOPTION_STATUS
    bundle_generation_not_promotion: bool = BUNDLE_GENERATION_NOT_PROMOTION
    evidence_mode: str = "github-synced"

    approval_status: str | None = None
    approval_scope: str | None = None
    approver_actor_type: str | None = None
    approver_id: str | None = None
    approved_at: str | None = None

    requested_scope: str | None = None
    effective_scope: str | None = None
    expected_requested_scope: str | None = None
    expected_effective_scope: str | None = None

    candidate_pack_digest: str | None = None
    approved_candidate_pack_digest: str | None = None
    expected_candidate_pack_digest: str | None = None

    expected_source_manifest_hash: str | None = None
    observed_source_manifest_hash: str | None = None

    candidate_validation_status: str | None = None
    review_status: str | None = None
    review_gate_passed: bool = False

    approval_required: bool = True
    node_creation_performed: bool = False
    canonical_written: bool = False
    assurance_mutated: bool = False
    reviewer_pass_claimed: bool = False
    execution_ready: bool = False
    pr_ready: bool = False

    findings: tuple[str, ...] = ()
    comparison: tuple[str, ...] = ()
    candidates: tuple[str, ...] = ()
```

`to_dict()` は既存 `CandidateValidationResult.to_dict()` と同じ deterministic / sort-friendly shape にする。

### 5.3 Approval evidence schema

```json
{
  "schema_version": 1,
  "approval_evidence_kind": "candidate_decomposition_approval",
  "approval_status": "approved",
  "approval_scope": "epic-issue-node-creation",
  "candidate_kind": "epic-issue",
  "requested_scope": {
    "scope_type": "epic",
    "scope_id": "epic-00295",
    "ref": "iss-00305-implement-approval-check-and-stop-gate-reports"
  },
  "effective_scope": {
    "scope_type": "epic",
    "scope_id": "epic-00295",
    "ref": "iss-00305-implement-approval-check-and-stop-gate-reports"
  },
  "candidate_pack": {
    "digest_algorithm": "sha256-tree-v1",
    "candidate_pack_digest": "<digest>",
    "source_manifest_hash": "<hash>",
    "candidate_ids": ["iss-candidate-001"]
  },
  "approver": {
    "actor_type": "human",
    "id": "iwasawayuuta",
    "role": "scope_owner"
  },
  "approved_at": "2026-07-08T00:00:00Z",
  "approval_statement": "I approve this candidate decomposition for this scope before node creation.",
  "authority_boundary": {
    "node_creation_performed": false,
    "canonical_written": false,
    "assurance_mutated": false,
    "reviewer_pass_claimed": false,
    "execution_ready": false,
    "pr_ready": false
  }
}
```

### 5.4 Validation rules

| Rule                                         | Failure status    | Finding / comparison                              |
| -------------------------------------------- | ----------------- | ------------------------------------------------- |
| approval file missing                        | `blocked`         | `missing_approval_evidence`                       |
| approval JSON invalid                        | `fail`            | `invalid_json:approval`                           |
| approval is non-object                       | `fail`            | `non_object_json:approval`                        |
| `schema_version != 1`                        | `fail`            | `invalid_schema_version:approval`                 |
| required field missing                       | `fail`            | `missing_or_invalid_field:<field>`                |
| `approval_status != approved`                | `blocked`         | `approval_not_approved:<status>`                  |
| `candidate_kind` mismatch                    | `stale`           | `candidate_kind_mismatch`                         |
| parent scope mismatch                        | `stale`           | `parent_scope_mismatch`                           |
| requested scope mismatch                     | `blocked`         | `requested_scope_mismatch`                        |
| effective scope mismatch                     | `blocked`         | `effective_scope_mismatch`                        |
| candidate pack digest mismatch               | `stale`           | `candidate_pack_digest_mismatch`                  |
| source manifest hash mismatch                | `stale`           | `source_manifest_hash_mismatch`                   |
| approver actor not human                     | `rejected`        | `self_approval_forbidden` or `non_human_approval` |
| approval statement missing                   | `fail`            | `missing_or_invalid_field:approval_statement`     |
| statement contains forbidden authority claim | `rejected`        | `forbidden_authority_claim:*`                     |
| statement contains secret / raw transcript   | `rejected`        | `secret_like_payload:*` / `raw_transcript:*`      |
| authority boundary claims true               | `rejected`        | `forbidden_authority_claim:<key>`                 |
| candidate validation not pass                | same or `blocked` | `candidate_validation_not_pass:<status>`          |
| unsafe report path                           | `rejected`        | existing `_unsafe_report_path` result             |

Rejected takes precedence over stale, stale over blocked where both arise from pack mismatch, and fail over blocked for malformed input. Scope mismatch should be `blocked` because it is an approval applicability problem rather than source freshness only.

## 6. Application design

`application/authoring_pack/approval_check.py`:

```python
@dataclass(frozen=True)
class ApprovalCheckRequest:
    input_path: Path
    approval_path: Path
    candidate_kind: CandidateKind
    output_format: Literal["text", "json"] = "text"
    evidence_mode: Literal["github-synced", "local-context"] = "github-synced"
    review_report: Path | None = None
    expected_parent_initiative: str | None = None
    expected_parent_epic: str | None = None
    expected_requested_scope: str | None = None
    expected_effective_scope: str | None = None
    expected_candidate_pack_digest: str | None = None
    expected_source_hash: str | None = None
    report_path: Path | None = None
```

Flow:

1. Resolve pack root using same convention as candidate validation.
2. Run or reuse candidate validation gate:

   * candidate validation non-pass prevents approval pass.
   * approval result should expose `candidate_validation_status`.
3. Compute current candidate pack digest with existing `tree_digest`.
4. Read approval evidence JSON.
5. Validate schema and required fields.
6. Normalize requested / effective scope.
7. Compare scope, candidate kind, parent, digest, source hash.
8. Reject self-approval / forbidden authority claims / sensitive payload.
9. Build `ApprovalCheckResult`.
10. Write report only if `_unsafe_report_path(report_path)` returns none.
11. Return exit code `0` only for `status == "pass"`.

## 7. Presentation design

`presentation/authoring_pack/approval_check_renderer.py`:

```python
def render_approval_check_json(result: ApprovalCheckResult) -> str:
    return json.dumps(result.to_dict(), sort_keys=True)

def render_approval_check_text(result: ApprovalCheckResult) -> list[str]:
    return [
        "spec-dock: authoring approval check",
        f"status={result.status}",
        f"authority={result.authority}",
        f"adoption_status={result.adoption_status}",
        f"bundle_generation_not_promotion={str(result.bundle_generation_not_promotion).lower()}",
        f"candidate_kind={result.candidate_kind}",
        f"approval_status={result.approval_status}",
        f"approval_required={str(result.approval_required).lower()}",
        f"review_gate_passed={str(result.review_gate_passed).lower()}",
        f"node_creation_performed={str(result.node_creation_performed).lower()}",
        f"canonical_written={str(result.canonical_written).lower()}",
        f"assurance_mutated={str(result.assurance_mutated).lower()}",
        f"reviewer_pass_claimed={str(result.reviewer_pass_claimed).lower()}",
        f"execution_ready={str(result.execution_ready).lower()}",
        f"pr_ready={str(result.pr_ready).lower()}",
        "findings=" + ",".join(result.findings),
        "comparison=" + ",".join(result.comparison),
    ]
```

Text output must not contain `adopted`, `reviewer pass`, `execution-ready`, `pr-ready`, `merge-ready`, or `success` as authority-like claims. Existing tests already guard similar forbidden strings for deferred authoring command output.

## 8. Safety design

* Report path safety uses existing `_unsafe_report_path`.
* Approval statement is scanned with existing authoring payload / sensitive payload scanner.
* Command never opens output path under canonical `spec-dock/active` or `.assurance.json`.
* Command never creates directories except safe report parent.
* Command never writes staged pack content.
* Command never writes canonical docs.
* No `--force`.
* No auto-creation command implementation.

## 9. Reuse decisions

Reuse:

* `AUTHORITY`, `ADOPTION_STATUS`, `BUNDLE_GENERATION_NOT_PROMOTION` from `prompt_pack_contract.py`.
* `CandidateKind`, `tree_digest`, `_source_manifest_hash` pattern from `candidate_contract.py`.
* `_unsafe_report_path` from `pack_review.py`.
* Candidate validation report / review gate semantics from `candidate_validation.py`.

Do not create:

* broad approval framework。
* generic policy engine。
* cryptographic signature abstraction。
* node creation service。

````

---

## 3. 推奨 `plan.md` content（正式日本語案）

```md
---
種別: 実装計画書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "strict"
---

# iss-00305 Approval Stop Gate Reports — 実装計画

## 1. 方針

この Issue は `authoring approval check` の実装だけを行う。  
承認 evidence を検証し report を出力するが、Epic / Issue node creation、canonical docs adoption、`.assurance.json` 更新、reviewer pass、execution-ready、PR-ready、PR delivery は行わない。  
実装対象は provider-side source of truth under `src/spec_dock/assets/...` を優先し、dogfood workspace は検証対象として扱う。

## 2. Step sequence

### S01: Requirement adoption / assurance preparation

- 現行 `requirement.md` の placeholder を具体要件へ置換する。
- grade を `strict` 推奨として分類材料を入れる。
- `design.md` / `plan.md` は placeholder の指示に従い、requirement classification / compose 後に canonical body を反映する。
- Closure:
  - `requirement.md` に目的、scope、out-of-scope、AC、EC、grade がある。
  - node creation 非対象が明記されている。

### S02: Domain approval contract

- `candidate_contract.py` に `ApprovalCheckStatus`、`ApprovalDecisionStatus`、`ApprovalCheckResult`、approval evidence validation helpers を追加する。
- `tree_digest` を candidate pack digest として再利用する。
- approval evidence schema v1 を検証する。
- self-approval / forbidden authority / sensitive payload rejection を実装する。
- Closure:
  - valid payload が `ApprovalCheckResult(status="pass")` を作れる。
  - missing / malformed / mismatch / self-approval が status taxonomy に分類される。
  - result に authority boundary false fields がある。

### S03: Application use case

- `application/authoring_pack/approval_check.py` を追加する。
- `ApprovalCheckRequest` を追加する。
- pack root 解決、candidate validation gate、approval evidence load、digest / scope comparison、safe report write を実装する。
- Closure:
  - approval evidence missing は blocked。
  - candidate digest mismatch は stale。
  - scope mismatch は blocked。
  - unsafe report path は rejected。
  - safe report path に JSON report を書く。

### S04: CLI command integration

- `commands/authoring.py` の `_DEFERRED_COMMANDS` から `authoring_approval_check` を削除する。
- `AuthoringApprovalCheckArgs`、arg parser、args factory、runner、expect helper を追加する。
- `command_specs()` に implemented command として登録する。
- Closure:
  - `authoring approval check --help` に implemented args が表示される。
  - `authoring approval check` は deferred ではなく approval check use case を呼ぶ。
  - `--force` が存在しない。

### S05: Renderer

- `presentation/authoring_pack/approval_check_renderer.py` を追加する。
- JSON renderer は `sort_keys=True`。
- Text renderer は status / authority boundary / findings / comparison を表示する。
- Closure:
  - pass / blocked / stale / rejected / fail の text output が deterministic。
  - output が reviewer pass / execution-ready / pr-ready を claim しない。

### S06: Tests and fixtures

- `tests/cli_runtime/test_authoring.py` に focused approval check tests を追加する。
- Existing deferred command tests から `authoring approval check` を外す。
- Valid / missing / stale / scope mismatch / self-approval / unsafe report fixtures を helper で作る。
- Closure:
  - provider-side installed runtime path で pass / negative tests がある。
  - dogfood runtime path smoke がある。
  - no mutation snapshot assertion がある。

### S07: Finish evidence / relay

- `report.md` に実装範囲、変更ファイル、検証予定、未解決リスク、no-per-Issue-PR rationale、C12 への relay edge を記録する。
- この Issue では PR delivery を行わない。
- Closure:
  - Final response / report に no PR delivery rationale がある。
  - C12 に final quality gate / PR delivery を defer している。

## 3. Test contract

### New / updated pytest targets

```text
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_help_exposes_implemented_contract
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_valid_epic_issue_approval_passes
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_valid_initiative_epic_approval_passes
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_missing_approval_evidence
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_reports_stale_candidate_digest
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_requested_scope_mismatch
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_effective_scope_mismatch
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_chatgpt_self_approval
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_forbidden_authority_claim
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_sensitive_statement
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_unsafe_report_path
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_writes_safe_noncanonical_report_path
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_does_not_create_nodes_or_mutate_canonical_docs
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_dogfood_runtime_path_valid_payload
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_deferred_commands_fail_closed_with_stable_diagnostics
````

`test_authoring_deferred_commands_fail_closed_with_stable_diagnostics` は、`authoring approval check` を deferred list から外す方向で更新する。自動 node creation command は、存在しない場合は absent behavior を許容し、存在する placeholder がある場合だけ deferred / unsupported diagnostics を検証する。

## 4. Red / Green / Refactor plan

* Red:

  * approval check help がまだ deferred なので失敗する test を追加。
  * missing approval / stale digest / scope mismatch / self-approval tests を追加。
* Green:

  * minimal domain result + application + CLI + renderer を実装。
* Refactor:

  * duplicate JSON reading / safe report writing helper が既存 pattern と揃っているか点検。
  * broad abstraction は追加しない。

## 5. File inventory

Expected changed files:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/approval_check_renderer.py
tests/cli_runtime/test_authoring.py
spec-dock/.../issues/iss-00305-implement-approval-check-and-stop-gate-reports/requirement.md
spec-dock/.../issues/iss-00305-implement-approval-check-and-stop-gate-reports/design.md
spec-dock/.../issues/iss-00305-implement-approval-check-and-stop-gate-reports/plan.md
spec-dock/.../issues/iss-00305-implement-approval-check-and-stop-gate-reports/report.md
```

Potential optional file:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py
```

## 6. Verification commands to record later

この回答では実行済みとは主張しない。実装後に Codex 側で候補として記録する command:

```bash
pytest tests/cli_runtime/test_authoring.py -k "approval_check"
pytest tests/cli_runtime/test_authoring.py -k "authoring_deferred_commands or authoring_approval_check"
pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_dogfood_runtime_path_valid_payload
```

Final C12 では broader checks:

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
pytest tests/cli_runtime/test_authoring.py
```

## 7. Stop conditions

* approval check が node creation を行う設計になった場合。
* `pass` を reviewer pass / execution-ready として扱う出力が入った場合。
* `.assurance.json` を読むだけでなく mutation する場合。
* safe report path guard を迂回する場合。
* `--force` が追加された場合。
* ChatGPT self-approval を pass する場合。

````

---

## 4. 推奨 approval evidence schema / status model

### Schema summary

最小 schema は次です。

```json
{
  "schema_version": 1,
  "approval_evidence_kind": "candidate_decomposition_approval",
  "approval_status": "approved",
  "approval_scope": "initiative-epic-node-creation | epic-issue-node-creation",
  "candidate_kind": "initiative-epic | epic-issue",
  "requested_scope": {
    "scope_type": "initiative | epic",
    "scope_id": "init-local-00003 | epic-00295",
    "ref": "<requested branch/ref>"
  },
  "effective_scope": {
    "scope_type": "initiative | epic",
    "scope_id": "init-local-00003 | epic-00295",
    "ref": "<effective branch/ref>"
  },
  "candidate_pack": {
    "digest_algorithm": "sha256-tree-v1",
    "candidate_pack_digest": "<digest>",
    "source_manifest_hash": "<hash>",
    "candidate_ids": []
  },
  "approver": {
    "actor_type": "human",
    "id": "<human id>",
    "role": "scope_owner | reviewer | maintainer"
  },
  "approved_at": "2026-07-08T00:00:00Z",
  "approval_statement": "<explicit statement>",
  "authority_boundary": {
    "node_creation_performed": false,
    "canonical_written": false,
    "assurance_mutated": false,
    "reviewer_pass_claimed": false,
    "execution_ready": false,
    "pr_ready": false
  }
}
````

### Check result status model

| Result status | 意味                                                                                     |     Exit |
| ------------- | -------------------------------------------------------------------------------------- | -------: |
| `pass`        | explicit human approval が現在の candidate pack / scope に一致する                              |        0 |
| `blocked`     | approval missing、not approved、scope mismatch、candidate validation prerequisite missing | non-zero |
| `stale`       | candidate digest / source hash / parent trace が approval 時点と違う                         | non-zero |
| `rejected`    | self-approval、forbidden authority claim、unsafe path、secret/raw transcript              | non-zero |
| `fail`        | malformed JSON、schema failure、required field invalid                                   | non-zero |

`pass` は node creation 実行ではありません。Epic の status taxonomy でも `pass` は command-local validation succeeded と定義され、canonical adoption 等ではないとされています。

---

## 5. CLI command shape recommendation

最小推奨 shape:

```bash
./spec-dock/scripts/spec-dock authoring approval check \
  --input <stage-dir-or-pack-root> \
  --approval <approval-evidence.json> \
  --candidate-kind <initiative-epic|epic-issue> \
  --expected-parent-initiative <init-id> \
  --expected-parent-epic <epic-id> \
  --expected-requested-scope <scope-type:scope-id> \
  --expected-effective-scope <scope-type:scope-id> \
  --expected-candidate-pack-digest <sha256-tree-v1> \
  --expected-source-manifest-hash <sha256> \
  --review-report <review-report.json> \
  --evidence-mode <github-synced|local-context> \
  --format <text|json> \
  --report-path <safe-report.json>
```

Conditional rule:

* `--candidate-kind initiative-epic` requires `--expected-parent-initiative`.
* `--candidate-kind epic-issue` requires `--expected-parent-epic`.
* `--expected-parent-initiative` and `--expected-parent-epic` should not both be required.
* `--review-report` can be optional if discovery follows existing candidate validation behavior, but explicit path should be supported.

Do not add:

```bash
--force
--create
--apply
--adopt
--mark-reviewer-pass
--set-authorized-profile
--execution-ready
--pr-ready
```

---

## 6. Concrete implementation sequence by repository layer

### Repository / workflow docs layer

1. Replace Issue requirement placeholder with the concrete requirement content.
2. Run the project’s assurance classify / compose workflow on the Codex side before writing canonical `design.md` / `plan.md`, because the current placeholders explicitly say not to write body content before composition.
3. Record draft adoption decisions in `report.md`.

### Domain layer

1. Extend `candidate_contract.py` with approval result/status/schema helpers.
2. Reuse existing authority constants from `prompt_pack_contract.py`.
3. Reuse `tree_digest` for candidate pack digest.
4. Reuse authority claim validation style; existing validator rejects true values for `node_creation_performed`, `canonical_written`, `assurance_mutated`, `reviewer_pass_claimed`, `execution_ready`, and `pr_ready`.

### Application layer

1. Add `approval_check.py`.
2. Use the same pack root convention as candidate validation.
3. Gate on candidate validation / review report status before approving.
4. Load approval evidence.
5. Validate status / scope / digest / human approver / statement.
6. Write safe report path only.

### Command layer

1. Remove `authoring_approval_check` from `_DEFERRED_COMMANDS`.
2. Add implemented command spec in `command_specs()`.
3. Add args dataclass / parser / runner / expect helper.
4. Keep exit code convention: `0` only on `pass`, non-zero otherwise.

### Presentation layer

1. Add `approval_check_renderer.py`.
2. JSON output sorted.
3. Text output concise and boundary-preserving.
4. Avoid forbidden success/readiness language.

### Tests layer

1. Update deferred tests.
2. Add positive/negative approval check tests.
3. Add safe report path tests.
4. Add no mutation snapshot tests.
5. Add dogfood runtime path smoke.

---

## 7. Test strategy and exact focused pytest targets

Add or update these targets:

```text
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_help_exposes_implemented_contract
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_valid_epic_issue_approval_passes
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_valid_initiative_epic_approval_passes
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_missing_approval_evidence
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_reports_stale_candidate_digest
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_requested_scope_mismatch
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_blocks_effective_scope_mismatch
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_chatgpt_self_approval
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_forbidden_authority_claim
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_sensitive_statement
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_rejects_unsafe_report_path
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_writes_safe_noncanonical_report_path
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_does_not_create_nodes_or_mutate_canonical_docs
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_approval_check_dogfood_runtime_path_valid_payload
tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_deferred_commands_fail_closed_with_stable_diagnostics
```

Focused commands to record after implementation, not as already run:

```bash
pytest tests/cli_runtime/test_authoring.py -k "approval_check"
pytest tests/cli_runtime/test_authoring.py -k "authoring_deferred_commands or authoring_approval_check"
```

---

## 8. Failure modes and reviewer focus points

### Failure modes

* `status=pass` を node creation permission と誤読させる。
* Candidate validation pass だけで approval check を pass させる。
* Approval evidence の candidate digest を検査しない。
* Scope object の requested / effective mismatch を見逃す。
* ChatGPT / assistant / tool-generated approval を human approval として通す。
* Approval statement に forbidden authority claim があるのに通す。
* Report path guard が canonical docs / `.assurance.json` 書き込みを許す。
* `authoring approval check` 実装時に `create-issues-from-zip` まで広げる。
* Docs / help が未実装 auto-creation command を available に見せる。
* `--force` 相当の bypass を入れる。
* 中間 Issue で PR-ready / PR delivery を claim する。

### Reviewer focus

* `authoring.py` から approval deferred entry が消え、implemented command spec に置換されているか。
* `ApprovalCheckResult` が existing authority boundary fields を維持しているか。
* `pass` output に `node_creation_performed=false` 等が必ずあるか。
* `self_approval_forbidden` path があるか。
* digest mismatch が `stale` になるか。
* requested / effective scope mismatch が fail-closed になるか。
* unsafe report path が既存 pattern と同じ強さで拒否されるか。
* Tests が provider-side installed runtime と dogfood runtime path の双方を見ているか。
* No per-Issue PR delivery rationale が report に残るか。

---

## 9. Draft claims to reject or narrow

1. **Draft requirement の branch trace は修正する。**
   Draft artifact は `Branch: codex/authoring-pack-installed-runtime` と記載していますが、今回の required current branch は `iss-00305-implement-approval-check-and-stop-gate-reports` です。

2. **`Issue Grade: standard` は `strict` へ引き上げ推奨。**
   Draft design / plan は `standard` としていますが、public CLI contract と approval stop gate を扱うため `strict` が妥当です。

3. **Docs / Skill impact は C10 では最小化する。**
   Draft design は Docs / Skill まで impact としていますが、Epic plan では runtime docs / workflow guidance は C11 の主対象です。C10 は command help / diagnostics に必要な最小変更に絞るべきです。

4. **`unsupported auto-creation diagnostics` は新 command 実装要求ではない。**
   `create-issues-from-zip` を追加しない。既に placeholder がある場合のみ deferred / unsupported を安定化し、ない場合は absent でよい。Epic の deferred items に auto node creation は残っています。

5. **Approval pass fixture は node creation readiness ではない。**
   Draft の “approval pass fixture” は command-local validation fixture としてのみ採用する。`pass` は canonical adoption / reviewer pass / execution-ready / PR-ready ではない。

6. **`diagnostics.py` 変更は必須ではない。**
   Draft target は `presentation/authoring_pack/diagnostics.py` を挙げていますが、現行 runtime は command ごとの renderer file を持つため、`approval_check_renderer.py` 追加を主案にする。共通 diagnostic helper が必要な場合だけ `diagnostics.py` を触る。

---

## 仮定

* GitHub connector で取得できた現行ブランチを primary source とし、添付 prompt / draft artifacts は supplementary evidence として扱った。
* `approval evidence` の標準保存場所は未決であり、この Issue では CLI input path と safe report output に限定する。
* 暗号署名検証はこの Issue の対象外。
* `tree_digest(pack_root)` は現行 candidate pack digest として再利用できる前提。ただし digest algorithm name は report に `sha256-tree-v1` として明示する。

## 不確実性

* `spec-dock/active/...` は GitHub connector では直接取得できず、canonical issue path under `spec-dock/initiatives/.../issues/iss-00305-...` を確認対象にした。
* Approval evidence の durable location と署名強度は Epic の open question に残っており、C10 で固定しすぎない方がよいです。
* CLI parser の auto-creation command absence behavior は、実装時に現在の parser hierarchy を Codex 側で再確認する必要があります。

## 未検証主張

* 上記 pytest target は実行結果ではなく、追加・更新すべき focused test recommendation です。
* この回答は patch ではなく、Codex が canonical docs / implementation へ採否統合するための planning evidence です。
