---
種別: 実装計画書（Issue）
ID: "iss-00305"
タイトル: "Approval Stop Gate Reports"
関連GitHub: ["#305"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00305 Approval Stop Gate Reports — Issue 実装計画書

## 1. Plan readiness

- `requirement.md`: 具体化済み。
- `design.md`: approval check の責務境界、schema、status model、CLI contract を定義済み。
- `.assurance.json`: `authorized_profile=standard`。
- ChatGPT analysis: `artifacts/20260708t061422z-chatgpt-approval-stop-gate-planning-analysis.md`。
- 実装開始条件: fresh `spec-reviewer` pass。

## 2. この計画で満たす要件ID

- AC-001: Help contract。
- AC-002: Valid Epic/Issue approval。
- AC-003: Valid Initiative/Epic approval。
- AC-004: Missing approval blocked。
- AC-005: Stale candidate digest。
- AC-006: Requested scope mismatch。
- AC-007: Effective scope mismatch。
- AC-008: Self approval rejected。
- AC-009: Forbidden authority claim rejected。
- AC-010: Sensitive statement rejected。
- AC-011: Unsafe report path rejected。
- AC-012: Safe report path writes JSON。
- AC-013: No mutation。
- AC-014: Candidate validation pass is not approval。
- AC-015: No per-Issue PR relay。

## 3. 依存関係から導く実装順序

1. Tests first: existing deferred behavior を Red にして、新 command contract を固定する。
2. Domain result/schema: approval evidence と status model を最小実装する。
3. Application use case: candidate validation gate と approval evidence を接続する。
4. CLI / renderer: `authoring approval check` を implemented command へ置換する。
5. Verification / report: focused tests、validate、assurance、reviewer gates、relay evidence を閉じる。

## 4. 許可変更面

| 種別 | パス | 許可する変更 |
|---|---|---|
| Runtime command | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` | approval check command args / runner / spec registration |
| Application | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py` | approval check use case 追加 |
| Domain | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py` | approval result / helpers 追加 |
| Presentation | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/approval_check_renderer.py` | JSON / text renderer 追加 |
| Tests | `tests/cli_runtime/test_authoring.py` | focused approval check tests 追加 / deferred tests 更新 |
| Planning evidence | `spec-dock/active/issue/*` | report evidence、reviewer gate、closure 更新 |

## 5. 禁止変更

- Auto node creation command を追加しない。
- `authoring adopt`、`mark-reviewer-pass`、`set-authorized-profile`、`issue-execution-ready`、`pr-ready` を追加しない。
- `.assurance.json` mutation を approval check から行わない。
- Canonical docs を runtime command から書かない。
- GitHub Issue / PR を runtime command から作らない。
- `--force` bypass を追加しない。
- 中間 Issue の PR を作らない。

## 6. Spec-Locked Closure Index

| Closure ID | 要件ID | 設計ID | 閉じる内容 | 検証レベル | Report evidence |
|---|---|---|---|---|---|
| CLOS-001 | AC-001 | DES-001 | help が implemented approval check contract を表示する | CLI test | `Test Contract Closure` |
| CLOS-002 | AC-002/003 | DES-002 | valid approval evidence が pass する | CLI/domain through runtime | `Test Contract Closure` |
| CLOS-003 | AC-004 | DES-003 | approval missing が blocked になる | CLI negative | `Test Contract Closure` |
| CLOS-004 | AC-005 | DES-004 | candidate digest mismatch が stale になる | CLI negative | `Test Contract Closure` |
| CLOS-005 | AC-006/007 | DES-005 | requested/effective scope mismatch が blocked になる | CLI negative | `Test Contract Closure` |
| CLOS-006 | AC-008 | DES-006 | ChatGPT/tool self-approval が rejected になる | CLI negative | `Test Contract Closure` |
| CLOS-007 | AC-009/010 | DES-007 | forbidden claim / sensitive statement が rejected になる | CLI negative | `Test Contract Closure` |
| CLOS-008 | AC-011/012 | DES-008 | unsafe report rejected / safe report written | CLI filesystem test | `Test Contract Closure` |
| CLOS-009 | AC-013/014 | DES-009 | mutation boundary false and candidate validation alone not enough | CLI regression / inspection | `Test Contract Closure` |
| CLOS-010 | AC-015 | DES-010 | no per-Issue PR relay | lifecycle evidence | `No-PR Relay Policy` |
| CLOS-011 | RB-004 | DES-011 | source manifest hash mismatch が stale になる | CLI negative | `Test Contract Closure` |
| CLOS-012 | AC-005/RB-003 | DES-011 | candidate evidence file digest mismatch が stale になる | CLI negative | `Test Contract Closure` |
| CLOS-013 | output contract | DES-011/DES-009 | JSON/text が candidate/source comparisons と authority boundary false を含む | CLI output test | `Test Contract Closure` |

## 7. ステップ一覧

### S00 Planning evidence and review readiness

目的: ChatGPT analysis、draft artifacts、repo inspection を採用し、requirement/design/plan/report を reviewer-ready にする。

Delegation contract:

- delegated role: manual planning fallback by orchestrator.
- input docs: active Issue docs、draft artifacts、ChatGPT transcript、parent Epic docs。
- allowed paths: `spec-dock/active/issue/{requirement,design,plan,report}.md`, `.assurance.json`, issue `artifacts/`。
- forbidden changes: runtime implementation。
- required verification: `assurance verify`、`git diff --check`。
- reviewer focus: spec-reviewer。
- stop conditions: unresolved requirement gap、placeholder design/plan、missing EAL。
- output required: planning docs、EAL、Spec Authoring Gate。

具体テストケース一覧:

- `tc-s00-001` planning: assurance contract is valid
  - 前提: `requirement.md`、`design.md`、`plan.md` が正本として具体化されている。
  - 操作: `./spec-dock/scripts/spec-dock assurance verify` を実行する。
  - 期待結果: `status=valid`。
  - 失敗検出: stale source binding、placeholder、missing report gate を検出する。
  - 検証方法: command evidence。
  - 関連 closure id: planning-readiness（Spec-Locked Closure Index 外）

### S01 Red tests for implemented command contract

目的: `authoring approval check` が deferred ではなく implemented command であることを Red-first で固定する。

Delegation contract:

- delegated role: dev-coder。
- input docs: `requirement.md`, `design.md`, existing `tests/cli_runtime/test_authoring.py`。
- allowed paths: `tests/cli_runtime/test_authoring.py`。
- forbidden changes: production runtime。
- required verification: `pytest tests/cli_runtime/test_authoring.py -k "approval_check_help"`.
- reviewer focus: command surface and no `--force`。
- stop conditions: parser hierarchy が想定と違う、auto-creation command が必要になる。
- output required: Red evidence and changed test summary。

具体テストケース一覧:

- `tc-s01-001` red: approval check help exposes implemented contract
  - 前提: 現行 command は deferred skeleton。
  - 操作: `authoring approval check --help` を実行する CLI runtime test を追加する。
  - 期待結果: `--input`、`--approval`、`--candidate-kind`、`--candidate-evidence`、`--expected-candidate-evidence-digest`、expected scope flags、`--report-path` が表示され、`--force` は表示されない。
  - 失敗検出: deferred command のまま、または bypass flag が出る回帰。
  - 検証方法: `tests/cli_runtime/test_authoring.py`。
  - 関連 closure id: CLOS-001

### S02 Domain approval evidence contract

目的: approval evidence schema、status model、authority boundary を domain で表現する。

Delegation contract:

- delegated role: dev-coder。
- input docs: `design.md` schema/status model、`candidate_contract.py` existing patterns。
- allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py`, `tests/cli_runtime/test_authoring.py`。
- forbidden changes: candidate validation behavior の unrelated rewrite。
- required verification: approval check negative / positive tests の domain-through-CLI seeds。
- reviewer focus: fail-closed status mapping、self-approval rejection、forbidden authority fields。
- stop conditions: schema expansion が generic framework 化する、secret handling が既存 scanner と矛盾する。
- output required: changed files, Red/Green evidence, residual risk。

具体テストケース一覧:

- `tc-s02-001` acceptance: valid approvals pass
  - 前提: candidate pack と review report が pass、approval evidence が digest/scope/human approver を持つ。
  - 操作: epic-issue と initiative-epic の valid fixture を `authoring approval check --format json` で検査する。
  - 期待結果: `status=pass`、authority boundary false。
  - 失敗検出: schema が valid approval を通せない、または node creation claim を出す。
  - 検証方法: CLI runtime tests。
  - 関連 closure id: CLOS-002

- `tc-s02-002` negative: missing approval blocks
  - 前提: candidate validation は pass するが approval evidence がない。
  - 操作: approval path missing で command を実行する。
  - 期待結果: `status=blocked`, `missing_approval_evidence`。
  - 失敗検出: candidate validation pass だけで approval pass になる回帰。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-003

- `tc-s02-003` negative: stale digest blocks promotion
  - 前提: approval evidence の digest が現在の candidate pack digest と異なる。
  - 操作: stale approval fixture を検査する。
  - 期待結果: `status=stale`, `candidate_pack_digest_mismatch`。
  - 失敗検出: 古い承認 evidence の再利用。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-004

- `tc-s02-003b` negative: stale source manifest hash blocks promotion
  - 前提: approval evidence または candidate evidence の source manifest hash が CLI expectation と異なる。
  - 操作: `--candidate-evidence` と `--expected-source-manifest-hash` を指定して検査する。
  - 期待結果: `status=stale`, `source_manifest_hash_mismatch`。
  - 失敗検出: 生成元が変わった candidate pack を古い承認で通す回帰。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-011

- `tc-s02-003c` negative: candidate evidence file digest mismatch blocks promotion
  - 前提: `--candidate-evidence` file digest が `--expected-candidate-evidence-digest` と異なる。candidate pack tree digest とは別に検査する。
  - 操作: candidate evidence fixture を差し替えて検査する。
  - 期待結果: `status=stale`, `candidate_evidence_file_digest_mismatch`。
  - 失敗検出: approval evidence と異なる file を同じ candidate として扱う回帰。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-012

- `tc-s02-004` negative: self approval rejected
  - 前提: approver actor が `chatgpt` または `assistant`。
  - 操作: self-approval fixture を検査する。
  - 期待結果: `status=rejected`, `self_approval_forbidden`。
  - 失敗検出: ChatGPT output が人間承認として扱われる。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-006

### S03 Application use case and report path

目的: candidate validation gate、approval evidence validation、safe report write を application layer で接続する。

Delegation contract:

- delegated role: dev-coder。
- input docs: `candidate_validation.py`, `pack_review.py` safe report helper, `design.md`。
- allowed paths: `application/authoring_pack/approval_check.py`, `candidate_contract.py`, tests。
- forbidden changes: canonical docs writing, `.assurance.json` writing。
- required verification: safe report / unsafe report / no mutation tests。
- reviewer focus: pack root resolution, review report gate, safe report path strength。
- stop conditions: report path guard を弱める必要がある、canonical path へ書く必要がある。
- output required: report write evidence and no mutation evidence。

具体テストケース一覧:

- `tc-s03-001` negative: scope mismatch blocked
  - 前提: approval evidence の requested/effective scope が CLI expectation と違う。
  - 操作: mismatch fixture を実行する。
  - 期待結果: `status=blocked`、comparison に mismatch。
  - 失敗検出: 別 scope の approval evidence が使われる。
  - 検証方法: CLI runtime tests。
  - 関連 closure id: CLOS-005

- `tc-s03-002` report: safe report path writes JSON
  - 前提: safe non-canonical path を `--report-path` に指定する。
  - 操作: valid approval check を実行する。
  - 期待結果: JSON report が書かれ、payload は stdout と同じ status / boundary を持つ。
  - 失敗検出: report が書かれない、または canonical path へ誘導される。
  - 検証方法: CLI runtime filesystem test。
  - 関連 closure id: CLOS-008

- `tc-s03-003` negative: unsafe report path rejected
  - 前提: `report.md`、`.assurance.json`、symlink report path を指定する。
  - 操作: approval check を実行する。
  - 期待結果: `status=rejected`、unsafe finding、report は書かれない。
  - 失敗検出: canonical docs / assurance mutation。
  - 検証方法: CLI runtime filesystem test。
  - 関連 closure id: CLOS-008

### S04 CLI integration and renderer

目的: deferred command を implemented command に置換し、JSON/text output を安定化する。

Delegation contract:

- delegated role: dev-coder。
- input docs: `commands/authoring.py`, existing renderers。
- allowed paths: `commands/authoring.py`, `presentation/authoring_pack/approval_check_renderer.py`, tests。
- forbidden changes: parser tree の unrelated rewrite、auto-creation command addition。
- required verification: help / JSON / text / deferred boundary tests。
- reviewer focus: output wording が readiness / adoption / reviewer pass を claim しないこと。
- stop conditions: command registration が existing command を壊す、`--force` が必要になる。
- output required: command contract evidence。

具体テストケース一覧:

- `tc-s04-001` renderer: text output preserves authority boundary
  - 前提: valid approval result。
  - 操作: text format で command を実行する。
  - 期待結果: `authority=evidence_only`、`node_creation_performed=false` 等が表示される。
  - 失敗検出: readiness / adoption を示す文言が出る。
  - 検証方法: CLI runtime test。
  - 関連 closure id: CLOS-009

- `tc-s04-002` deferred boundary: auto-creation remains absent or fail-closed
  - 前提: auto node creation は Epic deferred item。
  - 操作: authoring help と関連 command tree を確認する。
  - 期待結果: auto-creation command を available command として表示しない。placeholder が存在する場合は deferred/fail-closed。
  - 失敗検出: `create-issues-from-zip` などが実装済みのように見える。
  - 検証方法: CLI runtime test / inspection。
  - 関連 closure id: CLOS-009

### S05 Verification, docs evidence, and relay closeout

目的: 実装全体の focused verification、reviewer gates、no-PR relay を閉じる。

Delegation contract:

- delegated role: orchestrator with reviewers。
- input docs: final diff、plan/report。
- allowed paths: `spec-dock/active/issue/report.md`。
- forbidden changes: new feature implementation after final gate without plan amendment。
- required verification: focused tests、validate、assurance verify、diff-check、reviewer gates。
- reviewer focus: code-reviewer / qa-reviewer / spec-reviewer。
- stop conditions: any non-pass reviewer, failing tests, dirty uncommitted state after commit。
- output required: final report evidence, commit/push evidence, issue finish evidence。

具体テストケース一覧:

- `tc-s05-001` verification: focused approval checks pass
  - 前提: implementation complete。
  - 操作: `uv run pytest tests/cli_runtime/test_authoring.py -k "approval_check"`.
  - 期待結果: pass。
  - 失敗検出: approval command regression。
  - 検証方法: command evidence。
  - 関連 closure id: CLOS-001 through CLOS-009, CLOS-011 through CLOS-013

- `tc-s05-002` verification: broader authoring lane remains stable
  - 前提: focused tests pass。
  - 操作: `uv run pytest tests/cli_runtime/test_authoring.py -q`.
  - 期待結果: pass。
  - 失敗検出: existing authoring pack behavior の回帰。
  - 検証方法: command evidence。
  - 関連 closure id: CLOS-001 through CLOS-009, CLOS-011 through CLOS-013

- `tc-s05-003` lifecycle: no per-Issue PR relay
  - 前提: implementation committed and pushed。
  - 操作: `issue finish` し、次 Issue `iss-00306` へ進む。
  - 期待結果: PR は作成せず、PR delivery は `iss-00307` に defer。
  - 失敗検出: intermediate PR creation。
  - 検証方法: report / git / spec-dock lifecycle evidence。
  - 関連 closure id: CLOS-010

## 8. 要件 ↔ ステップ対応

| 要件 | Step |
|---|---|
| AC-001 | S01, S04 |
| AC-002/003 | S02, S03, S04 |
| AC-004/005/006/007/008 | S02, S03 |
| AC-009/010 | S02, S04 |
| AC-011/012 | S03 |
| AC-013/014 | S03, S04, S05 |
| AC-015 | S05 |

## 9. Amendment triggers

次の場合は実装を止め、plan amendment と fresh spec-review を行う。

- Approval check が node creation を行う必要が出た。
- Canonical docs または `.assurance.json` を runtime command から書く必要が出た。
- Approval evidence の保存場所や署名強度をこの Issue で固定する必要が出た。
- `--force` bypass が必要だと判明した。
- `candidate_contract.py` の大規模分割や candidate schema 破壊が必要になった。
- Existing authoring tests の多数が unrelated に壊れた。

## 10. Final Exit Contract

この Issue は次を満たすまで finish しない。

- `requirement.md` / `design.md` / `plan.md` が fresh `spec-reviewer` pass を持つ。
- Planned implementation が完了し、CLOS-001 through CLOS-013 の evidence が `report.md` に記録されている。
- Focused authoring tests が pass している。
- `./spec-dock/scripts/spec-dock validate` が pass している。
- `./spec-dock/scripts/spec-dock assurance verify` が pass している。
- `git diff --check` が pass している。
- code-reviewer と qa-reviewer が pass している。
- 変更が commit / push されている。
- Per-Issue PR は作成せず、`iss-00306` へ relay する。
