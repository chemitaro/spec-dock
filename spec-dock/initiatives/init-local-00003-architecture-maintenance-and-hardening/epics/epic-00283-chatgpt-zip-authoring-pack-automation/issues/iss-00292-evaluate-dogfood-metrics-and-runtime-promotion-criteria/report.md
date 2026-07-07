---
種別: レポート（Issue）
ID: "iss-00292"
タイトル: "ドッグフード指標とランタイム昇格基準を評価する"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#292"]
---

# iss-00292 ドッグフード指標とランタイム昇格基準を評価する — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - ChatGPT Use / GPT-5.5 Pro Extended に `iss-00292` の判断材料設計を依頼し、採用した提案を Issue-local artifacts として配置済み。
  - dogfood metrics report、machine-readable metrics summary、source evidence index、runtime promotion criteria draft、defer / reject rationale template、sample defer rationale、ChatGPT Use planning summary を作成済み。
  - runtime promotion はこの Issue では承認しない。現時点の推奨 stance は `defer_formal_runtime_promotion` として記録し、backend command adapter readiness は `iss-00293` に引き渡す。
  - Issue planning の fresh `spec-reviewer` gate は `019f3999-911a-7381-8155-3cda5fcf3403` で pass 済み。
  - S99 final reviewer gates は pass 済み。`spec-reviewer` re-review `019f3a97-0d88-7f42-b08a-bdbc7355d11c`、`code-reviewer` re-review `019f3a97-3101-7fd1-8963-e51236c3d5a9`、`qa-reviewer` re-review `019f3a97-58ae-7fb2-aa6f-67e73acae80f` を記録した。
- 次のマイルストーン:
  - `issue finish` 後に `iss-00293` へ進む。
- ブロッカー:
  - runtime promotion の未決定は意図した defer evidence であり、この Issue の完了 blocker ではない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151021z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151022z-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `adopted` | ChatGPT Use planning session `specdock-iss00292-metrics-planning` | Issue-local artifacts | `iss-00292` は runtime promotion approval ではなく、dogfood metrics と promote / defer / reject 判断材料を作る Issue として扱う提案を採用した。 | `artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/chatgpt-use-planning-summary.md` | local verification and fresh reviewers |
| EAL-005 | `partially_adopted` | dogfood metrics / criteria artifacts | `report.md`; Epic `report.md` | 指標・昇格基準・保留/却下理由 template は採用するが、runtime promotion decision は採用しない。現時点では formal runtime promotion を defer する判断材料として扱う。 | `artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/` | hand off unresolved adapter / final gate items to `iss-00293` |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00292 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |
| iss-00292 metrics artifacts | `dogfood-metrics-report.ja.md` と `dogfood-metrics-summary.json` は `iss-00288`〜`iss-00291` の evidence を source として参照する。 | `runtime-promotion-criteria-draft.ja.md` と `defer-reject-rationale-template.ja.md` は promote / defer / reject を分離する。 | 低。runtime promotion は未決定であり、backend adapter readiness を `iss-00293` に残す。 | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic docs、Issue-local draft requirement | blocking question なし | EAL-001 を採用 | pass | いいえ | execute approved plan |
| design | canonical requirement、Issue-local draft design | blocking question なし | EAL-002 を採用し canonical design へ再記述 | pass | いいえ | execute approved plan |
| plan | canonical requirement / design、Issue-local draft plan | blocking question なし | EAL-003 を採用し canonical implementation plan へ再記述 | pass | いいえ | execute approved plan |

## Workflow-Scoped Authorization

| field | value |
|---|---|
| authorization source | ユーザーの SpecDock workflow / ChatGPT Use / reviewer gate 利用依頼 |
| repo/worktree | `<local-worktree>` |
| active scope | `epic-00283` / `iss-00292` |
| named roles | `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `dev-coder`, `doc-writer`, `spec-manager` as required by plan |
| boundary | canonical docs は main orchestrator single-writer。sub-agent / ChatGPT output は evidence であり、reviewer pass や local authority の代替にしない。 |
| invalidation | scope expansion、stale branch/source、failed reviewer、requirement/design/plan の material change、allowed path 外変更の必要性 |

## Grade Specialist Evidence Gate

| field | value |
|---|---|
| local authorized_profile | `standard` |
| assurance status | `provisional` |
| Epic obligation | standard obligation |
| specialist / fallback evidence | Issue execution 開始前に specialist evidence または manual fallback evidence を `report.md` へ記録する。strict 相当 Issue では skip reason だけを readiness evidence としない。 |
| promotion rule | `.assurance.json` / `authorized_profile` は ChatGPT 推奨や Epic 側の推奨で上書きしない。 |

| profile | required_or_fallback | usage | evidence | reviewer_verdict | readiness |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual evidence: fresh spec-reviewer `019f3999-911a-7381-8155-3cda5fcf3403` passed and canonical docs were integrated by main orchestrator | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | passed: planning `019f3999-911a-7381-8155-3cda5fcf3403`; S99 re-review `019f3a97-0d88-7f42-b08a-bdbc7355d11c` | final S99 pass recorded |
| code-reviewer | fresh `passed` for docs / JSON diff | passed: focused re-review `019f3a97-3101-7fd1-8963-e51236c3d5a9` | final S99 pass recorded |
| qa-reviewer | fresh `passed` for metrics / criteria adequacy | passed: focused re-review `019f3a97-58ae-7fb2-aa6f-67e73acae80f`; P2 count fix applied | final S99 pass recorded |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| S99 | final-gate | spec-reviewer | fresh | pass | no | issue finish eligible | `019f3a97-0d88-7f42-b08a-bdbc7355d11c`; prior P1 final-gate contradiction fixed; P2 count finding fixed |
| S99 | final-gate | code-reviewer | fresh | pass | no | issue finish eligible | `019f3a97-3101-7fd1-8963-e51236c3d5a9`; self-matching leakage guard wording fixed; focused re-review no findings |
| S99 | final-gate | qa-reviewer | fresh | pass | no | issue finish eligible | `019f3a97-58ae-7fb2-aa6f-67e73acae80f`; JSON full metric coverage, sample metric snapshot, and count fix applied |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00292 | `artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite | none | pass | execute approved plan |

## ChatGPT Use Planning Evidence

| field | value |
|---|---|
| session slug | `specdock-iss00292-metrics-planning` |
| adopted output | dogfood metrics report、metrics summary JSON、source evidence index、runtime promotion criteria draft、defer / reject rationale template、sample defer rationale、planning summary |
| raw transcript policy | raw browser conversation log is not committed |
| authority boundary | advisory evidence only; local artifacts and `report.md` are the adoption record after local verification and reviewer gates |
| runtime promotion decision | not decided |
| recommended current stance | `defer_formal_runtime_promotion` |
| deferred to `iss-00293` | ChatGPT Use / Oracle backend command adapter implementation and verification, final PR delivery, final quality gate |

## Dogfood Metrics Report Summary

| metric group | observed evidence | interpretation |
|---|---|---|
| Scenario A | candidate-only focused tests `19 / 19 pass`; Scenario A full suite `188 / 188 pass` | candidate-only validation has positive evidence, while correction deltas remain a defer signal for more samples |
| Scenario B | selected-profile review / validation / dry-run pass; `canonical_written=false`; `assurance_mutated=false`; `reviewer_pass_claimed=false` | selected-profile staged flow preserved local authority and no-overwrite boundary |
| Scenario C | negative probes `6 / 6 adoption_eligible=false`; stale staging returned `status=stale` and `staged_artifact_count=0` | stale / mismatch / unsafe-claim paths fail closed |
| Docs | README, prompt contract, EAL examples, manual fallback notes exist | documentation readiness is positive evidence |
| Unmeasured / deferred | human edit burden、manual fallback success rate、aggregate repair-loop semantics、backend adapter readiness | formal runtime promotion should remain deferred |

## Runtime Promotion Criteria Draft Summary

- Promote requires positive dogfood validation, no authority-boundary regression, docs readiness, backend command adapter verification, manual fallback exercise, and fresh reviewer gates.
- Defer applies while human edit burden, manual fallback success rate, aggregate reviewer loop definition, backend adapter readiness, or sample diversity remain incomplete.
- Reject applies if ChatGPT output claims reviewer pass / canonical adoption / `.assurance.json` mutation / runtime availability, or if stale / mismatch / unsafe-claim probes become adoption eligible.
- Current decision material recommends defer, not reject, because no safety-boundary violation requiring rejection was observed.

## Defer / Reject Rationale Template Summary

- `defer-reject-rationale-template.ja.md` records rationale type, evidence reviewed, metric snapshot, authority-boundary checks, defer / reject rationale, re-evaluation trigger, and follow-up owner.
- `sample-defer-rationale.ja.md` demonstrates a defer rationale for the dogfood-only helper workflow, with backend adapter readiness delegated to `iss-00293`.
- The template is designed for future runtime promotion review and does not itself approve promotion.

## Verification Evidence

| check | result | evidence |
|---|---|---|
| JSON validity | pass | `python -m json.tool .../dogfood-metrics-summary.json`; `python -m json.tool .../source-evidence-index.json` |
| artifact file set | pass | 7 files exist under `artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/` |
| patch marker guard | pass | `rg -n "^\\*\\*\\* Add File:" .../20260707t031203z-dogfood-metrics-and-runtime-criteria` returned no matches |
| whitespace guard | pass | `git diff --check` |
| host-local path leakage guard | pass | dedicated absolute-path / local-oracle marker scan returned no matches for active Issue report/artifacts and Epic report; the exact pattern is not persisted here to avoid self-matching |
| unsafe claim inspection | pass | unsafe terms appear only in boundary/caveat/prohibited-example contexts, not as runtime promotion approval or reviewer pass claim |
| SpecDock validation | pass | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189` |
| focused authoring-pack tests | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py -q` -> `201 passed in 9.91s` |

## Reviewer Finding Disposition

| reviewer | finding | disposition |
|---|---|---|
| spec-reviewer `019f3a97-0d88-7f42-b08a-bdbc7355d11c` | P1 final-gate contradiction: report claimed a pass while `tc-005` remained pending. | fixed; S99 gate status separated from planning pass, then re-reviewed as pass |
| spec-reviewer `019f3a97-0d88-7f42-b08a-bdbc7355d11c` | P2 computed positive count mismatch. | fixed; `computed_positive_signals` changed to `13` |
| code-reviewer `019f3a97-3101-7fd1-8963-e51236c3d5a9` | P2 self-matching local path leakage pattern in report. | fixed; exact pattern is not persisted in report, focused re-review passed |
| qa-reviewer `019f3a97-58ae-7fb2-aa6f-67e73acae80f` | P2 JSON metric subset vs Markdown full report. | fixed; JSON now covers all 18 metrics |
| qa-reviewer `019f3a97-58ae-7fb2-aa6f-67e73acae80f` | P3 sample rationale lacked metric snapshot. | fixed; sample now includes computed / partial / unmeasured / deferred snapshot |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。親 trace、権威境界、local validation requirement、独立 review 観測点を canonical docs と metrics artifacts で保持した。
- AC-005〜AC-006:
  - Pass。dogfood metrics report と runtime promotion criteria draft、defer / reject rationale template を作成し、昇格 / 保留 / 却下の判断材料を分離した。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | `iss-00288`〜`iss-00291` の report を source evidence とし、local `authorized_profile=standard` を変更していない。 | closed |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/` に 7 ファイルを配置し、canonical docs の直接上書きは行っていない。 | closed |
| tc-003 | pass | 正常系 / negative fixture / validation status | metrics report は Scenario A/B/C/docs positive evidence と unmeasured / deferred signals を分離し、promotion decision を未決定のまま保持する。 | closed |
| tc-004 | pass | docs impact / EAL / Closure Delta | EAL-004 / EAL-005、SID-iss-00292-003〜005、Epic report への summary 反映対象を作成した。 | closed |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | local checks passed; spec-reviewer / code-reviewer / qa-reviewer fresh S99 gates passed; non-blocking P2/P3 findings fixed | closed |

## フォローアップ

- `issue finish` 後、Epic plan の依存順に従って `iss-00293` を開始する。
- runtime promotion そのものの採否は `iss-00293` final quality gate 以降に再評価する。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00292-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00292-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00292-003 | dogfood metrics / criteria artifacts は evidence-only decision material であり、runtime promotion approval ではない。 | accepted | `artifacts/20260707t031203z-dogfood-metrics-and-runtime-criteria/` | `issue finish` 後に `iss-00293` へ引き渡す |
| SID-iss-00292-004 | 現時点の runtime promotion stance は `defer_formal_runtime_promotion`。reject は不要だが、human edit burden、manual fallback success rate、aggregate reviewer loop、backend adapter readiness は未完了または未計測である。 | accepted | `dogfood-metrics-report.ja.md`; `runtime-promotion-criteria-draft.ja.md`; `dogfood-metrics-summary.json` | `iss-00293` final gate へ引き渡す |
| SID-iss-00292-005 | ChatGPT Use / Oracle backend command adapter readiness は `iss-00293` の PR 作成前品質ゲート対象であり、`iss-00292` では未実装の defer signal として扱う。 | accepted | user supplemental requirement 2026-07-07; Epic EAL-011; `iss-00293` specs | `iss-00293` で実装 / 検証する |
