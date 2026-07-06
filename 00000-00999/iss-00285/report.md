---
種別: レポート（Issue）
ID: "iss-00285"
タイトル: "安全な仕様作成パック検査とスキーマ検証を実装する"
状態: "finish-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#285"]
---

# iss-00285 安全な仕様作成パック検査とスキーマ検証を実装する — レポート

## 進捗サマリー

- 現在地:
  - Issue-local draft artifacts と ChatGPT Use planning result を evidence-only handoff として確認済み。
  - ChatGPT Use session `specdock-iss-00285-planning` は current branch / GitHub connector を参照できたことを回答内で確認し、ZIP validator の具体案を返した。
  - main orchestrator が採用判断し、`requirement.md` / `design.md` / `plan.md` を `review_chatgpt_authoring_pack.py` と `authoring_pack_review.py` の dogfood-only validator 実装へ具体化済み。
  - `authoring_pack_review.py` / `review_chatgpt_authoring_pack.py` / focused tests / README 更新を実装済み。
  - focused pytest、既存 preflight regression、ruff、SpecDock validate / assurance verify、`git diff --check` は実装後に通過済み。final spec-reviewer 指摘後に focused tests を 48 件へ拡張し、再実行済み。
- 次のマイルストーン:
  - Issue commit を作成し、`issue finish`、次 Issue `iss-00286` の `issue start` へ進む。
- ブロッカー:
  - 現時点で実装完了を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151018z-draft-requirement-draft-requirement-from-authoring-pack.md` | planning spec-review |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design の初期 input として採用した。 | `artifacts/20260706t151018z-01-draft-design-draft-design-from-authoring-pack.md` | planning spec-review |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan の初期 input として採用した。 | `artifacts/20260706t151019z-draft-plan-draft-plan-from-authoring-pack.md` | planning spec-review |
| EAL-004 | `adopted` | ChatGPT Use planning | `requirement.md` / `design.md` / `plan.md` | ZIP を主入力、tree を補助入力とする dogfood-only validator 案を採用し、schema、path safety、source hash、unsafe claim、status taxonomy、reviewer obligations を具体化した。 | `artifacts/20260706t210249z-chatgpt-use-planning-summary.md`; session `specdock-iss-00285-planning` | planning spec-review |
| EAL-005 | `deferred` | scope review | staged diff / profile skeleton / dogfood scenarios / metrics / PR delivery | これらは `iss-00286` 以降または `iss-00293` の責務であり、この Issue では扱わない。 | `requirement.md` 対象外 / `plan.md` Final Exit Contract | 後続 Issue で扱う |
| EAL-006 | `adopted` | implementation | `scripts/authoring-pack/authoring_pack_review.py` | ZIP / tree review の安全検査、schema validation、stale/source hash、unsafe authority claim、status taxonomy、sanitized report generation を dogfood-only library として実装した。code-reviewer 指摘を受け、generic absolute path / traversal / hidden path redaction、encrypted ZIP entry rejection、tree executable rejection、safe extraction failure `blocked`、unsafe source path `rejected`、Python 3.10-compatible UTC を修正した。QA reviewer P2 を受け、missing source observation は `blocked` として扱うよう修正した。final spec-reviewer P1 を受け、preflight repository identity / observed ref-head / stale_if source_paths を shape validation に追加し、preflight / pack の `stale_if` source が preflight source snapshot にない場合は `stale` として止め、pack `stale-if.json` の condition-level schema を fail-closed にした。 | `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` = 48 passed | implementation reviewer gate |
| EAL-007 | `adopted` | implementation | `scripts/authoring-pack/review_chatgpt_authoring_pack.py` | public CLI wrapper と exit code mapping を追加し、JSON / Markdown report を output dir ownership marker 付きで書けるようにした。 | focused pytest CLI cases / ruff check | implementation reviewer gate |
| EAL-008 | `adopted` | implementation | `tests/manual_tests/test_review_chatgpt_authoring_pack.py` | valid ZIP/tree、missing metadata、unsafe path/file、non-pass preflight、source drift、unsafe claim、redaction、no-mutation を focused manual test として固定した。QA reviewer 指摘を受け、tree unsafe、device-like ZIP mode、executable regular file、invalid UTF-8、token-like redaction、invalid-run no-mutation、mandatory metadata 全件欠落、missing source observation coverage、full trace assertion、wrong root、unsafe claim categories を追加した。code-reviewer 指摘を受け、generic absolute / traversal / hidden path report redaction、encrypted ZIP entry、tree executable、safe extraction failure、unsafe source path coverage も追加した。AC-006 explicit claim として `adoption_status: adopted` と `canonical overwrite` も追加した。final spec-reviewer P1 を受け、missing repository identity、missing observed ref/head、unsafe preflight stale_if source path、preflight / pack stale_if path missing from preflight source snapshot、malformed pack stale-if condition schema を追加した。 | `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` = 48 passed | QA reviewer gate |
| EAL-009 | `adopted` | docs impact | `scripts/authoring-pack/README.md` | preflight helper と review helper の責務を dogfood-only / evidence-only として説明し、runtime command / PR / reviewer gate / canonical overwrite の誤認を避ける説明に更新した。 | README diff / S90 docs inspection | final spec-review |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00285 specs | `requirement.md` の目的 / 親 Epic trace / AC-001〜AC-008 | `design.md` の module split / schema model / safety rules、`plan.md` の S01〜S99 / reviewer obligations | 中。ZIP validator は安全境界の実装であり、tree input や ChatGPT output を正本採用と誤認するリスクがある。正本には evidence-only / no canonical overwrite / no reviewer-gate self-claim を明記した。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement、ChatGPT Use planning summary、`iss-00284` preflight contract | blocking question なし | EAL-001 / EAL-004 を採用し canonical requirement へ再記述した | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design、ChatGPT Use planning summary、ZIP / tree 境界、preflight / stale validation、status taxonomy | blocking question なし | EAL-002 / EAL-004 を採用し canonical design へ再記述した | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan、ChatGPT Use implementation plan、step-local execution contract | blocking question なし | EAL-003 / EAL-004 を採用し canonical implementation plan へ再記述した | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| item | value |
|---|---|
| repo / branch | `chemitaro/spec-dock` / `iss-00285-implement-safe-authoring-pack-review-and-schema-validation` |
| active scope | `iss-00285` under `epic-00283` |
| allowed implementation paths | `scripts/authoring-pack/**`, `tests/manual_tests/test_review_chatgpt_authoring_pack.py`, `tests/fixtures/authoring_pack/**` if needed, this Issue `report.md`, `scripts/authoring-pack/README.md` |
| planning metadata exception | `.assurance.json` は planning 中の `assurance classify` による command-generated source binding metadata として更新済み。validator library / CLI / tests / README は `.assurance.json` を変更しない。 |
| forbidden paths | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`, unrelated Issue docs, canonical docs auto-overwrite, PR / CI operations, validator 実行または実装による `.assurance.json` mutation |
| invalidation trigger | runtime command 追加、canonical overwrite、reviewer-gate self-claim、profile mutation、PR 作成、ZIP / tree boundary の変更 |

## Delegated Draft Evidence

| created_by_role | source_role | draft_path | source_paths | generated_at | adoption_status | reflected_to | diff_guard | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| chatgpt-use | gpt-5.5-pro extended | `artifacts/20260706t210249z-chatgpt-use-planning-summary.md` | Issue docs、Epic docs、`scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`、focused tests | 2026-07-06 | unreviewed | [] | pass | main orchestrator が EAL-004 として採用範囲を再記述した。raw draft 自体は authority を持たない | ZIP fail-closed、tree 補助境界、no runtime command、no canonical overwrite、taxonomy consistency | none | pending after review repair | planning spec-review requested |
| manual-authoring | orchestrator canonical integration | `artifacts/20260706t210249z-chatgpt-use-planning-summary.md` | EAL-004 | 2026-07-06 | not used | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger; delegated direct-write authority not used | authority boundary、report gate、step contract | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | manual fallback | ChatGPT Use planning + main orchestrator adoption; failure-mode record below | `artifacts/20260706t210249z-chatgpt-use-planning-summary.md`; `assurance verify` ok; `spec-dock validate` ok | pass | ready |

## Reviewer Gate Status

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f394e-65e0-72f3-9c71-ccd2ae0d607d`; no findings |
| implementation | implementation code-review | code-reviewer | fresh | pass | no | final-spec-review-ready | fresh pass `019f396b-cded-74c1-af5f-b6049b08cf41`; no findings |
| implementation | implementation QA-review | qa-reviewer | fresh | pass | no | final-spec-review-ready | fresh pass `019f3971-dc4f-7ea0-8693-5344ee1c32ae`; no findings; focused suite 40 passed |
| final | issue finish spec-review | spec-reviewer | fresh | pass | no | issue-finish-ready | fresh pass `019f3986-8e1a-7091-b8cb-b14f64ea497c`; no findings |

## Planning Spec Review History

| reviewer | result | findings | disposition |
|---|---|---|---|
| `019f3942-c8a5-7630-98af-08349a125e7a` | failed-p1 | executable plan shape、preflight / stale validation semantics、status / exit-code taxonomy。P2: strict planning evidence、bare adopted / accepted denylist | fixed in canonical docs; superseded by re-review |
| `019f3948-8eb2-70b2-b1f3-f98ec3b38669` | failed-p1 | step contract schema、delegated draft source state。P2: auditable verification evidence | fixed in canonical docs; re-review pending |
| `019f394e-65e0-72f3-9c71-ccd2ae0d607d` | pass | no P0/P1 planning-readiness blockers | current planning gate pass |

## Planning Verification Log

| command | result | observed_at | note |
|---|---|---|---|
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json` | pass | 2026-07-06T21:17:55Z | `.assurance.json` source binding updated after P1/P2 repair |
| `./spec-dock/scripts/spec-dock validate` | pass | 2026-07-06T21:17:55Z | `spec-dock: ok (validate) nodes=189` |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | 2026-07-06T21:17:55Z | issue `iss-00285`; `authorized_profile=standard`; `reason=ok` |
| `git diff --check` | pass | 2026-07-06T21:17:55Z | no whitespace errors |

## Execution Evidence

| step | status | evidence | observed_at | notes |
|---|---|---|---|---|
| S01 | pass | `./spec-dock/scripts/spec-dock assurance verify`; preflight fixture / planning docs inspection | 2026-07-06T21:17:55Z | `authorized_profile=standard`; `iss-00284` preflight / source / forbidden-claim contract を validator input として trace 済み |
| S02 | pass | `scripts/authoring-pack/authoring_pack_review.py`; `scripts/authoring-pack/review_chatgpt_authoring_pack.py`; focused valid ZIP / tree / metadata / source mismatch tests | 2026-07-06T21:30:56Z | actual ZIP central directory inspection、safe extraction、schema validation、report writing を実装 |
| S03 | pass | focused negative tests for wrong root, traversal / hidden / generic absolute / Windows path redaction, symlink, device-like mode, executable bit in ZIP/tree, encrypted ZIP, nested archive, binary / invalid UTF-8, unsafe tree, non-pass preflight, stale_if drift and missing source observation, unsafe source path, safe extraction failure, unsafe claim categories, token/private-key redaction, valid/invalid no-mutation | 2026-07-06T21:30:56Z | `rejected` / `fail` / `stale` / `blocked` / `deferred` / `pass` taxonomy を tests で固定 |
| S90 | pass | `scripts/authoring-pack/README.md` updated; this report refreshed | 2026-07-06T21:30:56Z | dogfood-only / evidence-only helper boundary を README に記録 |
| S99 | pass | final rerun of commands and reviewers | 2026-07-06T22:24:34Z | final command rerun、code-reviewer、qa-reviewer、final spec-reviewer pass |

## Implementation Verification Log

| command | result | observed_at | note |
|---|---|---|---|
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T21:30:56Z | 19 passed |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T21:45:00Z | 24 passed after QA reviewer finding fixes |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T21:50:00Z | 26 passed after code-reviewer finding fixes |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T21:55:00Z | 31 passed after P2 finding fixes |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:00:00Z | 33 passed after final P2 finding fixes |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:01:38Z | 38 passed after QA P2 breadth fixes |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:01:38Z | 40 passed after explicit AC-006 claim fixtures |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:07:04Z | 43 passed after final spec-reviewer P1 fix |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:11:37Z | 44 passed after stale_if snapshot P1 fix |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:16:43Z | 45 passed after pack stale-if snapshot P1 fix |
| `uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:21:28Z | 48 passed after pack stale-if schema P1 fix |
| `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:21:28Z | 81 passed |
| `uv run ruff check scripts/authoring-pack/authoring_pack_review.py scripts/authoring-pack/review_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:21:28Z | no diagnostics |
| `uv run ruff format --check scripts/authoring-pack/authoring_pack_review.py scripts/authoring-pack/review_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py` | pass | 2026-07-06T22:21:28Z | `3 files already formatted` |
| `./spec-dock/scripts/spec-dock validate` | pass | 2026-07-06T22:21:28Z | `spec-dock: ok (validate) nodes=189` |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | 2026-07-06T22:21:28Z | issue `iss-00285`; `authorized_profile=standard`; `reason=ok` |
| `git diff --check` | pass | 2026-07-06T22:21:28Z | no whitespace errors |

## Failure-Mode Record

| failure mode | planned status | prevention / evidence | owning step |
|---|---|---|---|
| unsafe ZIP entry is extracted before validation | `rejected` | central directory inspection before extraction; unsafe extraction tests | S02 / S03 |
| non-pass preflight is accepted as trusted baseline | `fail` / `blocked` / `stale` / `rejected` propagated | preflight status must be `pass`; non-pass never returns validator `pass` | S02 / S03 |
| preflight source hash or `stale_if` current hash mismatches | `stale` | preflight-vs-ZIP source-manifest comparison and current repo source hash check | S02 / S03 |
| missing mandatory metadata is treated as adoption-ineligible only | `fail` | manifest / provenance / source-manifest / stale-if / adoption-map required schema tests | S02 / S03 |
| unsafe authority claim is mistaken for reviewer gate evidence | `rejected` | scoped denylist for reviewer / canonical / assurance / PR / implementation-complete claims | S02 / S03 |
| tree input is treated as ZIP safety evidence | `deferred` note | tree mode report records ZIP central directory safety as non-substitute | S02 / S03 |
| diagnostics leak host path, token, or private key | `rejected` or sanitized non-pass | redaction tests over stdout / stderr / JSON / Markdown | S03 |
| validator mutates canonical docs or `.assurance.json` | non-pass completion gate | bytes equality / git status evidence | S03 / S99 |

## Deferred PR Delivery Gate

- この Issue 単独では Pull Request を作成しない。
- 実装と検証が完了したら `issue finish` し、次 Issue `iss-00286` を `issue start` する。
- PR 作成、CI / review 指摘対応、manual test evidence、mergeable 確認は `iss-00293` に集約する。

## 受け入れ条件（AC）の達成状況

| AC | status | current evidence | next_action |
|---|---|---|---|
| AC-001 | pass | `validation-report.json` shape に trace を固定し、report / EAL / planning evidence へ親 Epic trace と `iss-00284` preflight dependency を記録済み。focused test は issue id、parent epic、requirements、acceptance、preflight snapshot を assert する。 | final spec-review |
| AC-002 | pass | ZIP mode は `zipfile.ZipFile.infolist()` の central directory inspection 後にのみ extraction へ進む。path traversal fixture は extract dir 不作成で `rejected`。 | code-reviewer 確認 |
| AC-003 | pass | 単一 root `specdock-authoring-pack/` と mandatory metadata 全件を library / focused tests で検査。wrong root は `rejected`、いずれかの欠落 metadata は `fail`。 | QA reviewer 確認 |
| AC-004 | pass | traversal、generic absolute/Windows path、hidden/secret-looking path、symlink、device-like mode、executable regular file in ZIP/tree、encrypted ZIP、nested archive、binary / invalid UTF-8、unsafe tree、unsafe source path を `rejected` にする tests を追加。 | QA reviewer / code-reviewer 確認 |
| AC-005 | pass | preflight non-pass propagation、source-manifest mismatch、`stale_if` current source hash mismatch を `stale`、missing current source observation / safe extraction failure を `blocked` として固定。 | QA reviewer 確認 |
| AC-006 | pass | scoped denylist で reviewer/canonical/assurance/PR/implementation-complete 系の unsafe authority claim を `rejected` にする。explicit fixtures と representative categories を parameterized tests で固定。 | final spec-review |
| AC-007 | pass | stdout / stderr / JSON / Markdown summary に traversal、hidden path、generic absolute path、host path、private key、token-like value が出ない redaction tests を追加。 | QA reviewer / code-reviewer 確認 |
| AC-008 | pass | valid / invalid validator tests で canonical docs / `.assurance.json` bytes equality を確認し、出力は指定 output dir に限定。 | final spec-review |

## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / `iss-00284` preflight contract / local assurance 確認 | ChatGPT Use planning summary と canonical specs に反映済み。`assurance verify` pass、planning spec-review `019f394e-65e0-72f3-9c71-ccd2ae0d607d`。 | closed |
| tc-002 | pass | validator source / CLI / sample validation report / 正本直接上書きなし | `authoring_pack_review.py` / CLI wrapper / focused valid ZIP-tree tests / no canonical overwrite contract を実装。 | code-reviewer 確認 |
| tc-003 | pass | valid / negative fixture / status taxonomy / redaction | 48 focused tests で `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred`、redaction、valid/invalid no-mutation を確認。 | QA reviewer / code-reviewer 確認 |
| tc-004 | pass | docs impact / EAL / SID / Closure Delta | README に review helper 例と dogfood-only boundary を追加し、EAL/SID/Deferred PR Delivery Gate を report へ更新。 | final spec-review |
| tc-005 | pass | `spec-dock validate` / `assurance verify` / focused tests / fresh reviewer results | final command rerun は pass。code-reviewer pass `019f396b-cded-74c1-af5f-b6049b08cf41`、qa-reviewer pass `019f3971-dc4f-7ea0-8693-5344ee1c32ae`、final spec-reviewer pass `019f3986-8e1a-7091-b8cb-b14f64ea497c`。 | closed |

## Final Spec Review History

| reviewer | result | findings | disposition |
|---|---|---|---|
| `019f3974-af6c-7a82-8c15-b25061460941` | failed-p1 | preflight trust baseline validation が `repository.full_name` / `requested_ref` / observed ref-head / safe `stale_if.source_paths` を完全に検査していない | fixed in `authoring_pack_review.py`; focused tests added; re-review pending |
| `019f3979-91d8-72e3-8023-5508bedaaa06` | failed-p1 | preflight `stale_if.source_paths` が preflight source snapshot に無い場合でも pass しうる | fixed in `authoring_pack_review.py`; focused test added; re-review superseded by pack-side review |
| `019f397d-99fd-7d21-a43e-4155a1d64d41` | failed-p1 | pack `stale-if.json` の source paths が preflight source snapshot / current repo check に含まれていない | fixed in `authoring_pack_review.py`; focused test added; re-review pending |
| `019f3982-66ff-7f72-8fbd-ccd93e6bd0d4` | failed-p1 | pack `stale-if.json` の condition-level schema が fail-closed で検査されていない | fixed in `authoring_pack_review.py`; focused tests added; re-review pending |
| `019f3986-8e1a-7091-b8cb-b14f64ea497c` | pass | no findings | final issue-finish spec gate passed |

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00285-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical docs へ再記述した。 | accepted | EAL-001〜EAL-003 | planning spec-review |
| SID-iss-00285-002 | この Issue 単独では PR を作成せず、実装完了後に `issue finish` して `iss-00286` へ進む。 | accepted | Epic `plan.md` リレー実行 / PR 方針 | final gate で deferred PR delivery evidence を記録 |
| SID-iss-00285-003 | validator は actual `.zip` を主入力、extracted tree を補助入力にする。tree input は ZIP central directory safety の代替証跡にしない。 | accepted | ChatGPT Use planning summary、`design.md` | reviewer に境界を確認してもらう |
| SID-iss-00285-004 | valid pack root は単一 `specdock-authoring-pack/` とし、mandatory metadata は `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`adoption/adoption-map.json` とする。 | accepted | `requirement.md` / `design.md` | S02 / S03 で fixture 化 |
| SID-iss-00285-005 | unsafe path / symlink / nested archive / binary / secret-looking entry は adoption-ineligible ではなく safety violation として `rejected` にする。 | accepted | `design.md` safety validation | negative ZIP tests |
| SID-iss-00285-006 | reviewer gate completion / adopted / canonical overwrite / `.assurance.json` mutation claims は fresh reviewer result として扱わず、pack-level safety violation として止める。 | accepted | `design.md` unsafe authority claim detection | unsafe claim tests |
| SID-iss-00285-007 | helper 実装は dogfood-only に閉じ、provider runtime command には昇格しない。 | accepted | README / allowed paths / no `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` diff | final spec-review |
| SID-iss-00285-008 | この Issue の implementation closure は local verification と reviewers で閉じ、PR delivery は `iss-00293` へ deferred として残す。 | accepted | Deferred PR Delivery Gate / Epic relay policy | issue finish after reviewer gates |

## フォローアップ

- commit、`issue finish`、`iss-00286` start へ進む。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は SpecDock reviewer gate の代替として扱わない。
- `.assurance.json` / `authorized_profile` は validator によって変更しない。planning 中の `assurance classify` による `.assurance.json` 更新は Planning Verification Log に記録済み。
