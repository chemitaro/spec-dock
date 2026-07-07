---
種別: レポート（Issue）
ID: "iss-00291"
タイトル: "仕様作成パックのワークフローと採用台帳例を文書化する"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00283", "init-local-00003"]
関連GitHub: ["#291"]
---

# iss-00291 仕様作成パックのワークフローと採用台帳例を文書化する — レポート

## 進捗サマリー

- 現在地:
  - ChatGPT ZIP 仕様作成パック由来の Issue-local draft artifacts を evidence-only handoff として配置済み。採否判断済みの内容は `requirement.md` / `design.md` / `plan.md` へ canonical Issue specs として再記述済み。
  - `scripts/authoring-pack/README.md` を日本語ファーストの dogfood-only workflow 入口として拡張済み。
  - Issue-local `artifacts/20260707t024417z-workflow-docs/` に workflow、prompt contract、EAL examples、manual fallback notes、ChatGPT Use planning summary を配置済み。
  - Issue 単位の final fresh reviewer gates は `spec-reviewer` `019f3a7b-42d8-7162-a87f-2eb07c0f4c02`、`code-reviewer` `019f3a7b-43c6-7e63-ae99-1880ea34310d`、`qa-reviewer` `019f3a7b-44d3-79e1-806e-60fcde4e5501` で pass 済み。
- 次のマイルストーン:
  - `issue finish` し、次 Issue `iss-00292` を開始する。
- ブロッカー:
  - 現時点で仕様 authoring を止める blocker はない。

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | ChatGPT ZIP authoring pack draft | `requirement.md` | 親 Epic の Issue candidate draft を Issue scope / AC / non-scope として正本化した。 | `artifacts/20260706t151021z-draft-requirement-draft-requirement-from-authoring-pack.md` | execute approved plan |
| EAL-002 | `adopted` | ChatGPT ZIP authoring pack draft | `design.md` | draft-design の責務境界、入出力契約、失敗設計、観測性、テスト戦略を canonical design として再記述した。 | `artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md` | execute approved plan |
| EAL-003 | `adopted` | ChatGPT ZIP authoring pack draft | `plan.md` | draft-plan の実装ステップ、検証計画、リスク、完了条件を canonical implementation plan として再記述した。 | `artifacts/20260706t151021z-02-draft-plan-draft-plan-from-authoring-pack.md` | execute approved plan |
| EAL-004 | `partially_adopted` | ChatGPT Use planning summary | `scripts/authoring-pack/README.md`; Issue-local docs | `iss-00291` の文書化対象は dogfood-only README と Issue-local artifacts に閉じる提案を採用し、`spec-dock/docs/**` 更新と backend adapter 実装は除外 / deferred とした。 | `artifacts/20260707t024417z-workflow-docs/chatgpt-use-planning-summary.md` | final reviewer gate |
| EAL-005 | `partially_adopted` | docs implementation | `scripts/authoring-pack/README.md`; `artifacts/20260707t024417z-workflow-docs/` | 日本語 README、prompt contract、EAL examples、manual fallback notes を作成し、formal runtime docs / backend adapter / PR delivery は scope 外として除外した。 | `scripts/authoring-pack/README.md`; `artifacts/20260707t024417z-workflow-docs/` | final reviewer gate |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| iss-00291 specs | `requirement.md` の目的 / 親 Epic trace / AC | `design.md` と `plan.md` の権威境界、失敗設計、検証計画 | 低。ChatGPT 出力は evidence-only handoff として保持し、採否判断済みの内容だけを canonical docs へ再記述済みである。 | pass |
| workflow docs | `scripts/authoring-pack/README.md` と Issue-local workflow docs | prompt contract、EAL examples、manual fallback notes | 低。SpecDock runtime command ではないこと、backend adapter は `iss-00293` へ deferred であることを明示した。 | pass |

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
| active scope | `epic-00283` / `iss-00291` |
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
| standard | manual fallback | used | execution evidence: README / Issue-local docs implemented; full authoring-pack manual suite `201 passed`; `spec-dock validate` passed; final reviewers passed | pass | ready |

## Reviewer Gate Status

| gate | required state | current state | promotion / completion decision |
|---|---|---|---|
| spec-reviewer | fresh `passed` | pass: planning pass `019f3999-911a-7381-8155-3cda5fcf3403`; final re-review pass `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` | local completion gate passed; no per-Issue PR |
| code-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: initial pass and re-review pass `019f3a7b-43c6-7e63-ae99-1880ea34310d`; P2 README example findings addressed | docs / command examples gate passed, final PR gate は `iss-00293` に残す |
| qa-reviewer | required if implementation diff or risk profile warrants; final Epic-wide gate is owned by `iss-00293` | pass: `019f3a7b-44d3-79e1-806e-60fcde4e5501` | docs-focused QA gate passed, final PR gate は `iss-00293` に残す |

| phase | gate | reviewer_role | freshness | state | risk_acceptance | promotion_decision | evidence |
|---|---|---|---|---|---|---|---|
| planning | spec-authoring | spec-reviewer | fresh | pass | no | execute approved plan | fresh pass `019f3999-911a-7381-8155-3cda5fcf3403` |
| final-local | code-review | code-reviewer | fresh | pass | no | local docs gate passed; no per-Issue PR | fresh re-review pass `019f3a7b-43c6-7e63-ae99-1880ea34310d` |
| final-local | qa-review | qa-reviewer | fresh | pass | no | local QA gate passed; no per-Issue PR | fresh pass `019f3a7b-44d3-79e1-806e-60fcde4e5501` |
| final-local | spec-review | spec-reviewer | fresh | pass | no | execute approved plan; local spec gate passed; no per-Issue PR | final re-review pass `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` |

## Reviewer Finding Disposition

| reviewer | finding | disposition | evidence |
|---|---|---|---|
| spec-reviewer `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` | P1 delegated draft row could be read as ChatGPT reviewer pass | addressed: reviewer_result now references fresh spec-reviewer gate and explicitly excludes ChatGPT self-review | Delegated Draft Evidence |
| spec-reviewer `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` | P2 EAL rows marked `adopted` before final reviewer gate | addressed: EAL-004 / EAL-005 now use `partially_adopted`, with excluded / deferred scope stated | Evidence Adoption Ledger |
| code-reviewer `019f3a7b-43c6-7e63-ae99-1880ea34310d` | P2 review example lacked `--extract-dir` | addressed: README review example now writes `$scratch_dir/iss-00285-extract` | `scripts/authoring-pack/README.md` |
| code-reviewer `019f3a7b-43c6-7e63-ae99-1880ea34310d` | P2 angle-bracket placeholders were shell-hostile | addressed: README examples now use `scratch_dir` variable and quoted `$scratch_dir/...` paths | `scripts/authoring-pack/README.md` |
| code-reviewer `019f3a7b-43c6-7e63-ae99-1880ea34310d` | P2 verification glob skipped validator tests | addressed: README now lists all five authoring-pack manual test files explicitly | `scripts/authoring-pack/README.md` |
| final spec re-review `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` | previous P1/P2 disposition scope | pass: no findings | Reviewer Gate Status |
| final code re-review `019f3a7b-43c6-7e63-ae99-1880ea34310d` | previous README P2 findings | pass: no findings | Reviewer Gate Status |

## ChatGPT Use Planning Evidence

| field | value |
|---|---|
| session | `specdock-iss00291-docs-planning` |
| result | completed |
| adopted recommendation | README を日本語ファースト入口に拡張し、Issue-local artifacts に workflow / prompt contract / EAL examples / manual fallback notes を置く |
| adopted no-op | `spec-dock/docs/**` は直接矛盾がない限り触らない |
| deferred item | ChatGPT Use / Oracle backend command adapter は `iss-00293` の final gate scope に残す |
| full browser conversation log | not committed |
| durable summary | `artifacts/20260707t024417z-workflow-docs/chatgpt-use-planning-summary.md` |

## Documentation Deliverables

| deliverable | status | evidence |
|---|---|---|
| 日本語 README | pass | `scripts/authoring-pack/README.md` |
| workflow docs | pass | `artifacts/20260707t024417z-workflow-docs/authoring-pack-workflow.ja.md` |
| prompt contract | pass | `artifacts/20260707t024417z-workflow-docs/prompt-contract.ja.md` |
| EAL examples | pass | `artifacts/20260707t024417z-workflow-docs/evidence-adoption-ledger-examples.ja.md` |
| manual fallback notes | pass | `artifacts/20260707t024417z-workflow-docs/manual-fallback-notes.ja.md` |
| `spec-dock/docs/**` impact | no-op | dogfood-only helper docs と Issue-local evidence に閉じる。runtime adapter / formal workflow update は `iss-00293` または後続判断に残す。 |

## Final Verification Evidence

| command / check | result | evidence |
|---|---|---|
| full authoring-pack manual suite | pass | `uv run pytest tests/manual_tests/test_prepare_chatgpt_authoring_pack.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/manual_tests/test_stage_chatgpt_authoring_pack.py tests/manual_tests/test_validate_selected_skeleton_fill.py tests/manual_tests/test_validate_issue_candidates.py -q` -> `201 passed` |
| whitespace diff check | pass | `git diff --check` -> no output |
| SpecDock structural validation | pass | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=189` |
| actual host-local path leakage | pass | host-local absolute path / Oracle local-state marker scan after redaction -> no actual host-local path adoption target |
| unsafe-claim inspection | pass | unsafe words appear only as forbidden-claim examples / anti-patterns, not as adopted authority claims |

## Delegated Draft Evidence

| field | value |
|---|---|
| delegated draft use | used; EAL-001〜EAL-003 の ChatGPT ZIP authoring pack draft を main orchestrator が採否判断し、採用部分だけ canonical docs へ再記述済み。 |
| source evidence | EAL / Issue-local `artifacts/*from-authoring-pack.md` を参照する。 |
| integration rule | draft artifact は evidence-only。採用済み内容だけ canonical docs に再記述し、追加採用または差分変更は Closure Delta と fresh reviewer gate を通す。 |
| reviewer caveat | ChatGPT self-review / reviewer-focus は SpecDock reviewer pass として扱わない。 |

| created_by_role | scope_id | draft_artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | reviewer_focus | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00291 | `artifacts/20260706t151021z-01-draft-design-draft-design-from-authoring-pack.md` | Epic `requirement.md`; Epic `design.md`; Epic `plan.md`; Issue-local draft artifacts | `requirement.md`; `design.md`; `plan.md`; `report.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `report.md` | pass | manual-authored canonical docs integrated through Evidence Adoption Ledger | authority boundary; no direct canonical overwrite; ChatGPT self-review excluded | none | fresh spec-reviewer gate (pass); not ChatGPT self-review | execute approved plan |

## Deferred PR Delivery Gate

| defer_target | dependency_basis | reason | intermediate_completion_boundary | final_pr_gate |
|---|---|---|---|---|
| `iss-00293` | Epic `plan.md` リレー実行 / PR 方針 | 個別 Issue ごとに Pull Request を作成せず、Epic 最後の品質ゲートで PR / CI / review / mergeable 確認を集約する。 | この Issue は local completion / `issue finish` まで進めても merge-prepared とは主張しない。 | `iss-00293` の PR Delivery Gate / Merge Preparation Gate が残る。 |

## 受け入れ条件（AC）の達成状況

- AC-001〜AC-004:
  - Pass。親 trace は `requirement.md` / Epic plan / Issue artifacts で確認でき、ChatGPT output は evidence-only、local validation と fresh reviewer gate が必要であることを README / workflow docs / prompt contract に明記した。
- AC-005〜AC-006:
  - Pass。日本語 README、prompt contract、EAL examples、manual fallback notes を作成し、`adopted` / `partially_adopted` / `rejected` / `stale` / `blocked` / `deferred` の使い分けを Issue-local artifact に記録した。


## Closure Evidence Ledger

| closure id | status | required evidence | current evidence | next_action |
|---|---|---|---|---|
| tc-001 | pass | 親 Epic trace / 依存 Issue / local assurance 確認 | E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012 への trace を requirement / Epic plan / report で確認。local `authorized_profile` は `standard`。 | S02 evidence 参照 |
| tc-002 | pass | Issue 固有成果物 / 正本直接上書きなし | `scripts/authoring-pack/README.md` と `artifacts/20260707t024417z-workflow-docs/` を作成。canonical Issue specs、`.assurance.json`、runtime source は変更なし。 | S03 evidence 参照 |
| tc-003 | pass | 正常系 / negative fixture / validation status | EAL examples と prompt contract が `pass` / `unreviewed` / `rejected` / `stale` / `blocked` / `deferred` を区別。full authoring-pack manual suite は `201 passed`。 | S90 evidence 参照 |
| tc-004 | pass | docs impact / EAL / Closure Delta | `spec-dock/docs/**` は no-op。dogfood-only helper README と Issue-local artifacts に閉じる。EAL-004 / EAL-005 を追加。 | S99 へ進む |
| tc-005 | pass | `spec-dock validate` / 関連テスト / fresh reviewer result | tests、`git diff --check`、`spec-dock validate` は pass。code-reviewer `019f3a7b-43c6-7e63-ae99-1880ea34310d`、qa-reviewer `019f3a7b-44d3-79e1-806e-60fcde4e5501`、final spec-reviewer `019f3a7b-42d8-7162-a87f-2eb07c0f4c02` は pass。 | `issue finish` へ進む |

## フォローアップ

- final reviewer pass 後、`issue finish` し、次 Issue `iss-00292` を開始する。

## 省略 / 例外メモ

- ChatGPT self-review / reviewer-focus は spec-reviewer pass として扱わない。
- `.assurance.json` / `authorized_profile` はこの report では変更しない。

## Spec Interpretation / Decision Ledger

| ID | decision | status | evidence | next_action |
|---|---|---|---|---|
| SID-iss-00291-001 | Issue-local draft artifacts は evidence-only handoff として保持し、採否判断済みの内容を canonical `design.md` / `plan.md` へ再記述した。 | accepted | Epic EAL-008b / EAL-008c / EAL-009; Issue-local `artifacts/*from-authoring-pack.md` | fresh reviewer gate を実行する |
| SID-iss-00291-002 | リレー実行方針は draft-plan artifact の補足として保持し、この Issue 単独では PR を作成しない。 | accepted | Epic `plan.md` リレー実行 / PR 方針; draft-plan のリレー節 | 実装完了後に `issue finish` し、次 Issue を `issue start` する |
| SID-iss-00291-003 | `spec-dock/docs/**` はこの Issue では no-op とし、dogfood-only workflow docs は `scripts/authoring-pack/README.md` と Issue-local artifacts に閉じる。 | accepted | ChatGPT Use planning summary; Documentation Deliverables | final reviewer gate を実行する |
| SID-iss-00291-004 | ChatGPT Use / Oracle backend command adapter は `iss-00293` の final gate scope に deferred とし、この Issue では境界文書化だけを行う。 | accepted | Epic plan EAL-011; prompt contract; manual fallback notes | `iss-00293` execution で実装 / 検証する |
