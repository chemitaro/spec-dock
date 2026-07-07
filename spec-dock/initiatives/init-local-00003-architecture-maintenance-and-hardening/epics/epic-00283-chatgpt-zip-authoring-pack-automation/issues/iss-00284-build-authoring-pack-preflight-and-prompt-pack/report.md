---
種別: レポート（Issue）
ID: "iss-00284"
タイトル: "仕様作成パックの事前確認とプロンプトパックを作る"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#284"]
---

# iss-00284 仕様作成パックの事前確認とプロンプトパックを作る — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - ChatGPT Use follow-up `required-repository-connector-context-github-2` により、current branch を参照した `iss-00284` planning package refresh を取得済み。main orchestrator が採用判断し、実装対象を `scripts/authoring-pack/` の dogfood-only preflight / prompt-pack 基盤として具体化済み。
  - `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`、fixtures、focused pytest を実装済み。
  - valid fixture から `/private/tmp/specdock-authoring-pack/iss-00284-prompt-pack-finalcheck-31` に prompt-pack を生成できることを確認済み。
  - Issue 単位の fresh `spec-reviewer` gate は、最新の report-ledger P1 修正後の re-review `019f387a-e7c2-73b3-ae10-89d8dd487cfb` で P0/P1/P2 findings なしの pass を確認済み。
  - 実装後の fresh `code-reviewer` / `qa-reviewer` で指摘された P1/P2/P3（unknown-file output の ownership marker、untrusted ownership marker cleanup、pack-owned cleanup failure、unreadable output_dir listing、diagnostics symlink、unsafe source role、secret-marker source role、whitespace-normalized / separator-normalized forbidden claim、private-key header variants、secret-like ZIP root、forbidden-claim ZIP root、multiline / control-character ZIP root、control-character source / stale_if path、unsafe prompt metadata、invalid issue_id shape、unsafe output_dir summary basename、false no-per-Issue-PR、empty source manifest、missing optional sources only、missing repository fields taxonomy、in-repo symlink secret target、symlink-loop output path、unowned pack-named file deletion、missing config traceback、file-valued output path traceback、nested output path creation failure、prompt-pack / diagnostics write failure、Windows absolute repo path、non-string assurance_path traceback、invalid assurance classification、source I/O failure、observed_ref / observed_full_name sanitization、observed_ref CLI redaction evidence、branch-pinned positive fixture）を修正し、focused pytest は 81 passed に更新済み。
- 次のマイルストーン:
  - P1 修正後の fresh `code-reviewer` / `qa-reviewer` / final `spec-reviewer` gate を通し、Issue finish readiness を確認する。
- ブロッカー:
  - 現時点で仕様 authoring / execution handoff を止める P0/P1 blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t150659z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151018z-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151018z-01-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use planning package refresh | `requirement.md` / `design.md` / `plan.md` | 既存 draft の目的を維持し、preflight JSON、source manifest、stale_if、built-in path/secret rules、`safe_output_constraints.forbidden_claims`、assurance snapshot、prompt-pack、status taxonomy、fixtures / tests、relay policy を実装可能な粒度へ具体化した。 | `artifacts/20260706t171812z-chatgpt-use-planning-refresh-summary.md` | execute approved plan |
| EAL-005 | `deferred` | Issue scope review | `iss-00285`〜`iss-00293` | ZIP intake、schema validation、staged rendering、profile skeleton fill、dogfood scenarios、metrics、final PR delivery は `iss-00284` の scope 外である。 | Issue `requirement.md` / `design.md` / `plan.md` non-scope | 後続 Issue で扱う |
| EAL-006 | `adopted` | local assurance observation | Issue readiness / prompt-pack profile boundary | `.assurance.json` の `authorized_profile=standard` / `status=provisional` を observation-only として扱い、ChatGPT が変更しない境界を docs と prompt-pack に固定した。 | Issue-local `.assurance.json` | S99 で no-mutation evidence を記録 |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00284 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement、ChatGPT Use planning refresh summary、manual-tests policy | なし | EAL-001 / EAL-004 / EAL-006 を採用し canonical requirement へ再記述した | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design、親 Epic path contract | なし | EAL-002 / EAL-004 を採用し canonical design へ再記述した | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan、S99 reviewer obligation | なし | EAL-003 / EAL-004 を採用し canonical implementation plan へ再記述した | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| item | value |
|---|---|
| repo / branch | `chemitaro/spec-dock` / `iss-00284-build-authoring-pack-preflight-and-prompt-pack` |
| active scope | `iss-00284` under `epic-00283` |
| allowed implementation paths | `scripts/authoring-pack/**`, `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py`, `tests/fixtures/authoring_pack/**`, this Issue `report.md` |
| forbidden paths | `src/spec_dock/**`, `.assurance.json`, unrelated Issue docs, canonical docs auto-overwrite, tracked files under `manual-tests/**`, PR / CI operations |
| invalidation trigger | runtime command 追加、ZIP intake 実装、profile mutation、PR 作成、source / ref / assurance contract 変更 |

## Delegated Draft Evidence

| created_by_role | source_role | draft_path | source_paths | generated_at | adoption_status | reflected_to | diff_guard | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| chatgpt-use | gpt-5.5-pro extended | artifacts/20260706t171812z-chatgpt-use-planning-refresh-summary.md | requirement.md; design.md; plan.md; report.md | 2026-07-06 | adopted | requirement.md; design.md; plan.md; report.md | pass | manual-authored canonical docs integrated by main orchestrator | authority boundary、path scope、AC closure | none | pass | execute approved plan |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00284 | `artifacts/20260706t150659z-draft-requirement-draft-requirement-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | manual fallback | manual fallback | manual fallback evidence: ChatGPT Use summary artifact、main-orchestrator adoption、assurance verify ok、spec-dock validate ok | pass | ready |

| profile | required_or_fallback | usage | evidence | reviewer_verdict | readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |

## Reviewer Gate Status

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | post-fix fresh pass `019f387a-e7c2-73b3-ae10-89d8dd487cfb`; no P0/P1/P2 findings |
| implementation | implementation code-review | code-reviewer | fresh | pass | no | ready for final spec-review | fresh pass `019f3926-506d-7fb3-9107-dd92a1ee1768`; no P0/P1/P2 findings |
| implementation | implementation QA-review | qa-reviewer | fresh | pass | no | ready for final spec-review | fresh pass `019f3926-8788-75a0-a541-2cf7f41623d8`; no P0/P1/P2 findings |
| final | issue finish spec-review | spec-reviewer | fresh | pass | no | execute approved plan | post-fix fresh pass `019f392e-e19d-71b2-addc-4dc77511217a`; no P0/P1/P2 findings |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |

## Post-Implementation Reviewer Obligations

| phase | required reviewer | timing | evidence destination |
|---|---|---|---|
| S99 | code-reviewer | 実装後、issue finish 前 | Reviewer Gate Status / Final Gate |
| S99 | qa-reviewer | targeted pytest と手動確認後、issue finish 前 | Reviewer Gate Status / Final Gate |
| S99 | spec-reviewer | 実装後の最終仕様差分確認後、issue finish 前 | Reviewer Gate Status / Final Gate |

## Spec Review History

| reviewer | result | reason | disposition |
|---|---|---|---|
| `019f385e-daa7-7b62-888e-4ee9fbd8d748` | failed-p1 | gate-state wording、step-local contracts、AC / closure traceability | fixed |
| `019f3865-495f-7890-9009-bba29613f43e` | failed-p1 | AC traceability、final reviewer gate scope | fixed |
| `019f386d-8dbd-7412-a7c7-bb4c66cee60b` | failed-p1 | parent Epic path contract mismatch | fixed |
| `019f3871-15b1-7193-85f4-32453d81cd6e` | pass-with-p2 | AC-010 manual test path was broad | P2 fixed |
| `019f3873-3338-7e30-9042-5a8499cf4a06` | failed-p1 | report gate still showed stale failed status | fixed by separating current gate and history |
| `019f3876-9938-7341-93d9-a0a7b1c1d090` | failed-p1 | current gate cited a pass older than the latest failed review; Epic report still said P1 repair was active | fixed; post-fix re-review pending |
| `019f3878-eb6c-7ee2-86ba-ab82587c09c4` | failed-p1 | Grade Specialist Evidence Gate still showed pass / ready while current reviewer gate was pending | fixed; post-fix re-review pending |
| `019f387a-e7c2-73b3-ae10-89d8dd487cfb` | pass | no P0/P1/P2 findings after pending/not-ready gate alignment | current planning gate pass |

## Implementation Review History

| reviewer | result | reason | disposition |
|---|---|---|---|
| `019f38ba-88ff-7f32-ab34-5df9aff1212c` | failed-p1 | unknown-file diagnostics dir が ownership marker により後続削除対象になる、source role が未サニタイズ、secret-like ZIP root が prompt に出力される | fixed; post-fix re-review pending |
| `019f38ba-cab1-7b31-addd-f79141e67f2d` | failed-p1 | unknown-file diagnostics dir が ownership marker により後続削除対象になる、source role が未サニタイズ | fixed; post-fix re-review pending |
| `019f38c1-9698-7cf3-b13a-68657d9915a8` | failed-p1 | source role に forbidden authority claim を入れると generated manifest に出力できる | fixed; post-fix re-review pending |
| `019f38c1-6e1a-7272-821d-6ee094f543cc` | failed-p1/p2 | ownership marker のない output_dir で pack 名と衝突する user-owned file を削除できる。config 読み込み失敗時に diagnostics 書き込み失敗で traceback になる | fixed; post-fix re-review pending |
| `019f38c7-3458-75e1-9930-400930a94433` | pass-with-p2 | file-valued output path が traceback になる edge case | P2 fixed; post-fix re-review pending |
| `019f38c7-5f11-7f92-9072-cf163445ffba` | failed-p1 | source role の `.env` / `private_key` など secret marker が未拒否 | fixed; post-fix re-review pending |
| `019f38cb-a086-7c33-b74b-aa8b27077e62` | pass-with-p2 | Windows absolute repo path と non-string assurance_path が fail-closed にならない edge case | P2 fixed; post-fix re-review pending |
| `019f38cb-c9f7-7831-a2e9-09aa361f8a5a` | pass | no P0/P1/P2 QA coverage gaps; focused pytest 43 passed | superseded by 46-test post-P2-fix review pending |
| `019f38d1-56f0-7b51-87b8-59d37dc14b02` | pass-with-p2 | untrusted ownership marker cleanup、whitespace/control-character variants of forbidden claims、private-key header variants | P2 fixed; post-fix re-review pending |
| `019f38d1-8660-7b73-9738-3ebd4939cb53` | pass | no P0/P1/P2 QA coverage gaps; focused pytest 46 passed | superseded by 50-test post-P2-fix review pending |
| `019f38d7-dc49-7e90-8a91-1589bb6d4ec1` | pass-with-p2 | diagnostics symlink in unowned output、invalid assurance classification、source file I/O errors | P2 fixed; post-fix re-review pending |
| `019f38d8-0c7d-7d00-9ce1-22a7241c0a1d` | pass-with-p3 | valid fixture の `requested_ref` が issue branch に固定され merge 後に brittle | P3 fixed; post-fix re-review pending |
| `019f38e1-af27-7273-9e21-67ac31860bc5` | failed-p1 | invalid assurance classification を pass として許容するテストになっていた | fixed; post-fix re-review pending |
| `019f38e1-7a72-7402-b090-ab024c6192c9` | failed-p1/p2 | `expected_zip_root` 経由の forbidden reviewer claim injection、observed Git ref の未サニタイズ | fixed; post-fix re-review pending |
| `019f38e8-91b2-7990-adce-2822bf64e2a7` | pass-with-p2 | file-valued parent 配下の output_dir 作成失敗が traceback / host path leak になる edge case | P2 fixed; post-fix re-review pending |
| `019f38e8-c7fc-70e0-87fc-d00a8d6f4777` | pass-with-p2 | multiline ZIP root が non-denylisted instruction を prompt に描画できる edge case | P2 fixed; post-fix re-review pending |
| `019f38ee-a6ff-7ed2-9af0-a57afe9fc1a8` | failed-p1 | non-whitespace control character ZIP root が prompt に描画できる edge case | fixed; post-fix re-review pending |
| `019f38ee-7a9e-7931-86bb-15d31919b66d` | pass-with-p2 | prompt-pack / diagnostics write failure の traceback、control-character source path の prompt injection | P2 fixed; post-fix re-review pending |
| `019f38f7-b048-7e73-82f3-40f149baaa7a` | failed-p1/p2 | prompt-rendered metadata の control-character authority claim、`no_per_issue_pr=false` の contradictory evidence | fixed; post-fix re-review pending |
| `019f38f7-af65-7fa0-952f-fa4348808e16` | failed-p1/p2 | symlink-loop output_dir の traceback / host path leak、separator variant forbidden claim bypass | fixed; post-fix re-review pending |
| `019f3901-b57b-7342-8cb9-f5c0a0ebf1b8` | failed-p1 | `sources: []` が source provenance なしで prompt-pack を生成できる | fixed; post-fix re-review pending |
| `019f3901-b4a2-7bb0-9a4f-020fb97ab447` | failed-p1/p2 | pack-owned output_dir cleanup failure の traceback / host path leak、unsafe observed repository full name leakage | fixed; post-fix re-review pending |
| `019f3908-1699-7273-87b0-df65651c1d2e` | failed-p1 | in-repo symlink target が secret-looking path に解決されても source manifest に入れられる | fixed; post-fix re-review pending |
| `019f3908-176f-71a1-abd8-ebec4c438879` | failed-p1 | missing `repository.requested_ref` が stale になる、optional missing source だけで空 manifest が pass になる | fixed; post-fix re-review pending |
| `019f390e-e120-78d3-b104-b5980999a91d` | pass-with-p2 | missing `repository.full_name` / non-object repository の test coverage gap | P2 fixed; post-fix re-review pending |
| `019f3913-a58e-75c0-86a9-712077c9e618` | failed-p1 | unreadable output_dir listing が traceback / host path leak になる edge case | fixed; post-fix re-review pending |
| `019f3913-a666-7531-bc1d-06cc9c10c355` | failed-p1/p2 | observed_ref sanitization の CLI end-to-end coverage gap、separator-normalized source role claim coverage gap | fixed; post-fix re-review pending |
| `019f391b-f453-7471-a4ac-08e6a4b7ec8f` | pass-with-p2 | missing / empty / non-string `issue_id` の boundary coverage gap | P2 fixed; post-fix re-review pending |
| `019f3921-0fec-7120-a7d8-b82dc99b4a55` | pass-with-p2 | secret-like `output_dir` basename が CLI summary に出る redaction gap | P2 fixed; post-fix re-review pending |
| `019f3921-45e0-7f22-9218-6082bfe8dd45` | pass | no P0/P1/P2 QA coverage gaps; focused pytest 80 passed | superseded by 81-test post-P2-fix review pending |
| `019f3926-506d-7fb3-9107-dd92a1ee1768` | pass | no P0/P1/P2 correctness/security findings | current implementation code gate pass |
| `019f3926-8788-75a0-a541-2cf7f41623d8` | pass | no P0/P1/P2 QA coverage gaps | current implementation QA gate pass |
| `019f392a-30b5-7171-9357-b12d1883beed` | pass-with-p2 | `denylist` field contract が仕様上曖昧 | P2 fixed by clarifying contract as built-in path/secret rules plus `safe_output_constraints.forbidden_claims`; post-fix re-review pending |
| `019f392e-e19d-71b2-addc-4dc77511217a` | pass | no P0/P1/P2 spec or closure findings after denylist-equivalent contract clarification | current final spec gate pass |

## Deferred PR Delivery Gate

- この Issue 単独では Pull Request を作成しない。
- 実装と検証が完了したら `issue finish` し、次 Issue `iss-00285` を `issue start` する。
- PR 作成、CI / review 指摘対応、manual test evidence、mergeable 確認は `iss-00293` に集約する。

## 受け入れ条件（AC）の達成状況

| AC | status | current evidence | next_action |
|---|---|---|---|
| AC-001 | pass | 親 Epic trace、local assurance、relay policy は docs と report に記録済み | 実装後 reviewer gate で確認する |
| AC-002 | pass | generated `/private/tmp/specdock-authoring-pack/iss-00284-prompt-pack-finalcheck-31/preflight.json` が repo / ref / source hashes / stale_if / assurance snapshot を含む | issue finish ready |
| AC-003 | pass | `missing-required-source.json` fixture が exit code `1` / status `fail` になり prompt を生成しないことを pytest で確認 | 実装後 reviewer gate で確認する |
| AC-004 | pass | `.assurance.json` は observation-only。pytest `test_assurance_file_is_not_mutated` で script 実行前後の bytes 一致を確認 | 実装後 reviewer gate で確認する |
| AC-005 | pass | `missing-assurance-snapshot.json` fixture が exit code `2` / status `blocked` になり profile 推定しないことを pytest で確認 | 実装後 reviewer gate で確認する |
| AC-006 | pass | generated `chatgpt-use-prompt.md` が `authority: evidence_only`、`bundle_generation_not_promotion: true`、expected ZIP root、no-per-Issue-PR policy を含む | 実装後 reviewer gate で確認する |
| AC-007 | pass | `unsafe-output-claim.json` fixture が exit code `4` / status `rejected` になり prompt を生成しないことを pytest で確認 | 実装後 reviewer gate で確認する |
| AC-008 | pass | `stale-source-hash.json` fixture が exit code `3` / status `stale` になり prompt を生成しないことを pytest で確認 | 実装後 reviewer gate で確認する |
| AC-009 | pass | generated `validation-taxonomy.json` が `pass` / `fail` / `blocked` / `stale` / `rejected` / `deferred` と `unreviewed` を分離 | 実装後 reviewer gate で確認する |
| AC-010 | pass | `git diff --check` pass。script / fixtures / focused pytest / report 以外の runtime provider 変更なし。script 実行では `.assurance.json` / `manual-tests/**` を変更しない | 実装後 reviewer gate で確認する |
| AC-011 | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` 81 passed、`./spec-dock/scripts/spec-dock validate` ok、`./spec-dock/scripts/spec-dock assurance verify` ok、`git diff --check` pass | 実装後 reviewer gate で確認する |


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / local assurance / relay policy 確認 | S01 inspection: E-RQ-001〜E-RQ-003 / E-AC-001、`authorized_profile=standard`、no-per-Issue-PR relay を確認 | 実装後 reviewer gate で確認する |
| tc-002 | pass | Valid preflight output with repo / ref / source manifest / stale_if | `python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py ...` が status `pass`。`preflight.json` / `source-manifest.json` 生成済み | 実装後 reviewer gate で確認する |
| tc-003 | pass | missing source / empty sources / invalid issue_id shape / missing optional sources only / missing nested repository required fields / non-object repository / missing stale_if / missing assurance / stale source hash / stale assurance snapshot / stale ref / stale repo / origin unobservable fail-closed | focused pytest で `fail` / `blocked` / `stale` negative fixtures を確認 | 実装後 reviewer gate で確認する |
| tc-004 | pass | prompt authority boundary / forbidden claims / expected ZIP root / no-per-Issue-PR relay | generated `chatgpt-use-prompt.md` と `safe-output-constraints.md` を確認 | 実装後 reviewer gate で確認する |
| tc-005 | pass | unsafe source path / Windows absolute source path / control-character source path / in-repo symlink secret target / unsafe source role / secret-marker source role / forbidden source role claim / whitespace-normalized and separator-normalized forbidden source / metadata / ZIP-root claim / private-key header source role / unsafe symlink / unsafe stale_if path/key/value / Windows absolute stale_if path / control-character stale_if path / secret-like nested stale_if / unsafe repository metadata / unsafe observed_ref / unsafe observed_full_name / observed_ref CLI redaction / unsafe issue id / unsafe custom forbidden claim / unsafe claim / default forbidden claim / unsafe ZIP root / forbidden-claim ZIP root / multiline ZIP root / non-whitespace control ZIP root / secret-like ZIP root / private-key header ZIP root / repo 内 output rejected | focused pytest で status `rejected` / exit code `4` になり prompt-pack、raw claim、raw unsafe constraints、secret-like strings を残さないことを確認 | 実装後 reviewer gate で確認する |
| tc-006 | pass | stale source hash detected as stale | focused pytest で stale hash fixture が status `stale` / exit code `3` になることを確認 | 実装後 reviewer gate で確認する |
| tc-007 | pass | status taxonomy transferable to report | generated `validation-taxonomy.json` と AC table に taxonomy mapping を記録 | 実装後 reviewer gate で確認する |
| tc-008 | pass | no canonical overwrite / no PR / no `.assurance.json` mutation / output_dir cleanup | focused pytest の bytes equality、trusted-marker pack-owned top-level / nested stale output cleanup、pack-owned cleanup failure no-traceback、unreadable output_dir listing no-traceback、secret-like output_dir CLI summary redaction、untrusted-marker cleanup block、diagnostics symlink no-follow、non-pack unknown file preserve と no-ownership-marker 再利用保護、unowned pack-named file preserve、missing config no-traceback、file-valued output no-traceback、nested output path creation failure no-traceback、symlink-loop output path no-traceback、prompt-pack / diagnostics write failure no-traceback、non-string assurance_path no-traceback、invalid assurance classification no-traceback、source I/O failure blocked、branch-independent valid fixture helper、`git diff --check` pass、`manual-tests/**` 変更なし | 実装後 reviewer gate で確認する |
| tc-009 | pass | targeted pytest / validate / assurance verify / diff check | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` 81 passed、`spec-dock validate` ok、`spec-dock assurance verify` ok、`git diff --check` pass | 実装後 reviewer gate で確認する |
| tc-010 | pass | fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` result | planning spec review pass `019f387a-e7c2-73b3-ae10-89d8dd487cfb`; final code review pass `019f3926-506d-7fb3-9107-dd92a1ee1768`; final QA review pass `019f3926-8788-75a0-a541-2cf7f41623d8`; final spec review pass `019f392e-e19d-71b2-addc-4dc77511217a` | issue finish ready |

## 実行証跡（Execution Evidence）

| step | status | evidence |
|---|---|---|
| S01 | pass | 親 Epic trace、allowed / forbidden paths、no-per-Issue-PR relay、local assurance authority を確認 |
| S02 | pass | `prepare_chatgpt_authoring_pack.py` に status taxonomy、diagnostics、exit code policy を実装 |
| S03 | pass | source hashing、repo/ref observation、assurance read-only snapshot、stale comparison を実装 |
| S04 | pass | status `pass` の場合だけ prompt-pack files を生成し、authority boundary / forbidden claims / no-per-Issue-PR relay を出力 |
| S05 | pass | valid / invalid fixtures と `tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` を追加。focused pytest 81 passed |
| S90 | pass | `manual-tests/**` を tracked 実装先から除外し、Epic / Issue report の path contract と evidence ledger を整合 |
| S99 | pass | code-reviewer / qa-reviewer / spec-reviewer gates pass。仕様文言修正後に `assurance classify --stage requirement --format json` で source binding を再同期し、`assurance verify` ok |

## 検証ログ（Verification Log）

| command | result | note |
|---|---|---|
| `python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py --config tests/fixtures/authoring_pack/valid/iss-00284-preflight-input.json --output-dir /tmp/specdock-authoring-pack/iss-00284-prompt-pack-finalcheck-31` | pass | status `pass`; CLI stdout is path-sanitized; 7 prompt-pack files plus ownership marker generated |
| `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | pass | 81 passed |
| `uv run ruff check scripts/authoring-pack/prepare_chatgpt_authoring_pack.py tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | pass | All checks passed |
| `uv run ruff format --check scripts/authoring-pack/prepare_chatgpt_authoring_pack.py tests/manual_tests/test_prepare_chatgpt_authoring_pack.py` | pass | 2 files already formatted |
| `./spec-dock/scripts/spec-dock validate` | pass | `spec-dock: ok (validate) nodes=189` |
| `./spec-dock/scripts/spec-dock assurance verify` | pass | `assurance verify: ok`; issue `iss-00284`; authorized_profile `standard` |
| `git diff --check` | pass | no whitespace errors |
| `rg -n '/Users/|/home/|BEGIN PRIVATE KEY|OPENSSH PRIVATE KEY|/Volumes/990p2t|\\.oracle|/private/|C:\\\\Users' /tmp/specdock-authoring-pack/iss-00284-prompt-pack-finalcheck-31` | pass | no matches |

## フォローアップ

- Epic plan の依存順に従って実装対象として扱う。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00284-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00284-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00284-003 | v1 の `prepare_chatgpt_authoring_pack.py` は `scripts/authoring-pack/` の dogfood-only script とし、配布 runtime command へ昇格しない。`manual-tests/` には tracked workspace / fixture / evidence を追加しない。 | accepted | ChatGPT Use planning package refresh; Issue `design.md`; `manual-tests/README.md` | 実装時に `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` と `manual-tests/**` を変更しないことを確認する |
| SID-iss-00284-004 | preflight は repo / ref / source hashes / stale_if / built-in path/secret rules / `safe_output_constraints.forbidden_claims` / assurance snapshot を固定する。 | accepted | Issue `requirement.md` AC-002〜AC-009 | S02〜S05 の test evidence を Closure Evidence Ledger に記録する |
| SID-iss-00284-005 | `.assurance.json` の `authorized_profile` は read-only observation とし、ChatGPT 推奨や prompt-pack 生成で変更しない。 | accepted | Issue-local `.assurance.json`; Epic readiness contract | S03 / S05 / S99 で no-mutation evidence を記録する |
| SID-iss-00284-006 | prompt-pack は ChatGPT Use 用の Markdown / JSON set とし、ZIP intake、schema validation、staged rendering、profile-controlled skeleton fill は後続 Issue に残す。 | accepted | Issue non-scope / dependency order | 後続 Issue への deferred scope として維持する |
