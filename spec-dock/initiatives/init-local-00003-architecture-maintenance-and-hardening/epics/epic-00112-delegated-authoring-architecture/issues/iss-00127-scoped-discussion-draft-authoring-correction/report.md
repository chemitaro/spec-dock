---
種別: 実装報告書（Issue）
ID: "iss-00127"
タイトル: "Scoped Discussion Draft Authoring Correction"
関連GitHub: ["#127"]
状態: "review"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00127 Scoped Discussion Draft Authoring Correction — 実装報告

`report.md` は観測証跡台帳です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際に観測した判断、証跡採用、検証、reviewer status、commit/no-op evidence を記録する。

## 仕様解釈・判断台帳
| ID | Status | Type | Raised By | Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | implementation | deep-consultant / orchestrator | post-run diff guard を docs-only 契約に留めるか runtime helper にするか未確定だった | A: docs/plan/report contract only; B: minimal runtime helper; C: full enforcement / adoption automation | B を採用。`delegated-authoring diff-guard` を minimal eligibility classifier として設計・実装対象にする | V2 は sub-agent direct write を許容するため、canonical single-writer と adoption ledger だけでは採用資格検査が人力に寄りすぎる | promoted_to_design | `requirement.md` Q-001 resolved decision; deep-consultant decision support; `design.md` | none |
| D-002 | resolved | implementation | deep-consultant / orchestrator | static adapter で scope-local `discussions/` write をどこまで表現するか未確定だった | A: broad write with guard; B: no broad static write; C: keep canonical draft target write | B を採用。static adapter は read-mostly fallback とし、canonical docs write を禁止する | post-run diff guard は broad permission の正当化ではなく delegated output eligibility の検査である | promoted_to_design | `requirement.md` Q-002 resolved decision; deep-consultant decision support; `design.md` | none |
| D-003 | resolved | implementation | spec-reviewer / orchestrator | diff-guard allowed filename が collision-safe naming rule を含んでいなかった | A: stricter `<ts>-<kind>-<slug>.md` only; B: include `<ts>-<nn>-<kind>-<slug>.md` collision form | B を採用。既存 discussion rules と同じ collision-safe naming rule を diff-guard 契約へ含めた | `spec-dock/active/issue/discussions/rules.md` が same-second collision form を許可しており、正当な `new doc` output を拒否しないため | applied | `requirement.md`, `design.md`, `plan.md` | none |
| D-004 | resolved | refactor | fresh deep-consultant / orchestrator | deprecated `delegated-authoring manifest` の旧 manifest/Profile/probe/session 生成 helper を runtime に残すか未確定だった | A: legacy helper を履歴参照として残す; B: external deprecated stub だけ残し、内部生成 helper を削除する | B を採用。CLI/API の deprecated/blocked 挙動は残し、旧生成 helper は削除する | 今回の標準経路は flat discussion draft + diff-guard であり、死んだ生成 helper は将来の誤再利用と設計誤読を招く | applied | deep-consultant result 2026-05-25; runtime diff | none |
| D-005 | resolved | implementation | code-reviewer / qa-reviewer / orchestrator | `--baseline-status` が dirty baseline の forbidden path mutation を見逃す可能性と、allowlisted existing discussion update の lifecycle eligibility が不足していた | A: baseline entries を従来どおり無視する; B: content snapshot を追加する; C: baseline 内の forbidden dirty entry は fail-closed、allowlist は proposed/unreviewed state を要求する | C を採用。baseline で無視できるのは diff-guard 自体が許可できる entry だけにし、existing discussion update は `status: proposed` または `adoption_status: unreviewed` を要求する | baseline-status だけでは content mutation を厳密に比較できないため、canonical/config/test などの forbidden dirty path は安全側に倒す。追加 JSON/manifest なしで user 方針の軽量運用を保つ | applied | code-reviewer / qa-reviewer findings 2026-05-25; runtime diff; targeted tests | none |
| D-006 | resolved | implementation | code-reviewer / qa-reviewer / orchestrator | allowlisted existing discussion update が採用済み状態を proposed/unreviewed に書き換えてから通過する可能性が残っていた | A: current content だけを見る; B: Git HEAD の pre-change text も見る; C: separate JSON snapshot を導入する | B を採用。tracked existing discussion update は current text と Git HEAD pre-change text の両方が proposed/unreviewed eligible でなければ拒否する | file-based context を維持しつつ、追加 manifest を増やさず、採用済み evidence の巻き戻しを post-run diff-guard で検知するため | applied | code-reviewer / qa-reviewer P2 findings 2026-05-25; runtime diff; targeted tests | none |
| D-007 | resolved | implementation | qa-reviewer / code-reviewer / orchestrator | dirty baseline 内の target discussion entry は baseline 時点の本文 snapshot がなく、HEAD/current text だけでは lifecycle rewrite を証明できない | A: baseline dirty discussion を許可する; B: baseline content/hash snapshot を導入する; C: target discussions に dirty/untracked baseline entry がある場合は fail-closed にする | C を採用。`--baseline-status` に target scope `discussions/` の entry が含まれる場合は `dirty_baseline_discussion` としてブロックし、新規 discussion でも非編集対象 state claim は拒否する | user 方針はシンプルな file-based 運用であり、content snapshot manifest を追加するより、delegated run の開始前に target discussions を clean にする方が明快で安全 | applied | qa-reviewer P1 finding 2026-05-25; code-reviewer P2 finding 2026-05-25; targeted tests | none |
| D-008 | resolved | implementation | Codex PR review / orchestrator | staged blob と working tree が混在する discussion diff、unmerged status、非 UTF-8 HEAD blob が diff-guard を bypass / crash させうる | A: index blob を個別検査する; B: mixed staged/unstaged と unmerged status を fail-closed にし、HEAD decode error を blocked reason にする | B を採用。target discussion の mixed staged/unstaged status と unmerged status は拒否し、HEAD pre-change blob が UTF-8 decode できない場合は `existing_discussion_head_non_utf8` で拒否する | diff-guard は delegated output adoption eligibility の安全弁であり、index/working tree の二重状態や conflict を許可する必要はない。単純な fail-closed の方が運用契約に合う | applied | Codex PR review #128; runtime diff; targeted tests | none |
| D-009 | resolved | implementation | Codex PR review / deep-consultant / code-reviewer / orchestrator | baseline に存在する未変更 canonical doc dirtiness が `canonical_doc` として残り、diff-guard が global clean tree gate 化していた | A: status key 一致なら全 baseline entry を無条件に除外する; B: mtime で unchanged を推定する; C: repo 外 lightweight file-state snapshot を baseline-status text に入れる | C を採用。`delegated-authoring baseline-status --output` が repo 外に `file-state-sha256` snapshot を持つ baseline file を生成し、pre-existing non-target dirtiness は current content hash と mode が一致し、かつ mixed index/worktree status でない場合だけ除外する | diff-guard は delegated output guard であり global clean tree を要求しない。一方で status key や mtime だけでは本文/モード/index 変更を証明できず、repo 内 snapshot は改ざん可能なため、JSON manifest ではなく repo 外の軽量 text snapshot で file-based 運用を保つ | applied | Codex PR review #128 commit `8dc47c5`; deep-consultant result 2026-05-25; code-reviewer mtime / repo-local tamper / mode / nested discussion / mixed-index findings; targeted 22/24-test runs; full 897-test run | none |
| D-010 | resolved | implementation | Codex PR review / orchestrator | baseline entry が delegated run 後に current status から消えると、pre-existing non-target dirtiness の削除/復元を見逃しうる。加えて porcelain text parsing が quoted path と ` -> ` を含む通常ファイル名を誤読しうる | A: baseline-only entry を無視する; B: disappeared baseline entry は fail-closed で評価対象へ戻す; C: separate manifest で lifecycle を追跡する | B を採用。baseline-only entry は delegated run 中の non-target 変更として diff-guard に戻し、`git status --porcelain=v1 -z` で current status を取得して quoted path / rename separator 誤読を避ける | user 方針の軽量 file-based 運用を維持しながら、baseline subtraction を delta guard として閉じるには、消えた baseline entry を安全側に扱うのが最小で堅い | applied | Codex PR review #128 commit `1f95b09`; targeted 25/27-test runs | none |
| D-011 | resolved | implementation | Codex PR review / orchestrator | editable-state 判定が本文中の説明文でも満たされ、新規 discussion draft が provenance metadata なしで通過し、baseline-status の tab / C-quoted path が誤分割されうる | A: proposal-only に戻す; B: frontmatter metadata を唯一の editable-state source にし、新規作成にも editable state を要求し、baseline path field を escaped text として扱う; C: JSON manifest を再導入する | B を採用。sub-agent direct write は維持しつつ、metadata は frontmatter の `status: proposed` または `adoption_status: unreviewed` のみを信頼する。baseline-status の path field は JSON escaping で出力し、JSON/C-quoted text を decode する | user 方針は proposal-only ではなく file-based direct discussion draft authoring である。一方で本文 prose や制御文字 path による誤承認は権限境界を曖昧にするため、軽量 metadata と escaped text format で閉じる | applied | Codex PR review #128 commit `bec31c4`; targeted 28/30-test runs; full 903-test run | none |
| D-012 | resolved | implementation | Codex PR review / orchestrator | baseline text の rename 行で quoted original path 内に ` -> ` が含まれると、rename separator と誤分割され baseline key が壊れる | A: rename baseline text を禁止する; B: quoted field の終端を解釈し、その外側の ` -> ` だけを rename separator とする; C: baseline format を別ファイルに分離する | B を採用。baseline-status は JSON-escaped path field を使う前提を維持し、parser は quote/escape を見て rename left field の終端を決める | 追加 manifest や format 変更なしに、既存の escaped text format を正しく読めば足りる。pre-existing rename dirtiness を安全に baseline subtraction するための最小修正 | applied | Codex PR review #128 commit `3f78a74`; targeted 29/31-test runs; full 904-test run | none |

## 証跡採用台帳
| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | discussion | user/orchestrator | V2 は proposal-only ではなく scope-local flat `discussions/` direct-write と canonical single-writer 境界を採用する | `requirement.md`, `design.md`, `plan.md` | purpose / scope / interface / steps | User decision と accepted ADR 後の最新要件案である | strong | `spec-dock/active/issue/discussions/20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md` | orchestrator | spec-reviewer requirement pass | no | reflected to requirement/design/plan |
| EAL-002 | adopted | reviewer | spec-reviewer | Current requirement is phase-ready | `requirement.md` | entire artifact | Fresh reviewer found no P0/P1 blockers | strong | spec-reviewer result 2026-05-25: `review_status=pass` | orchestrator | spec-reviewer | no | requirement used as design input |
| EAL-003 | adopted | sub-agent | repo-analyst | Old manifest/Profile/probe/canonical draft write model remains across runtime, skills, adapters, docs, templates, tests, and mirrors | `design.md`, `plan.md` | file tree / step split / risks | Repo impact mapping identified concrete collision points and high-risk tests | strong | repo-analyst result 2026-05-25 | orchestrator | pending design/plan review | no | reflected to design/plan |
| EAL-004 | adopted | sub-agent | deep-consultant | diff guard should be a minimal runtime helper and static adapter should not allow broad write | `requirement.md`, `design.md`, `plan.md` | resolved decisions / interface / steps | Recommendation aligns with user preference for direct file-based collaboration while keeping canonical docs protected | strong | deep-consultant result 2026-05-25 | orchestrator | pending design/plan review | no | reflected to requirement/design/plan |
| EAL-005 | adopted | reviewer | spec-reviewer | Design/plan needed naming rule collision form, step-local closure gates, correct S02 reviewer gate, and report cleanup | `requirement.md`, `design.md`, `plan.md`, `report.md` | implementation-ready corrections | Findings were concrete workflow-gate blockers and have been addressed before implementation | strong | spec-reviewer results 2026-05-25: two `review_status=fail` passes | orchestrator | pending re-review | no | rerun spec-reviewer |
| EAL-006 | adopted | sub-agent | fresh deep-consultant | Old manifest generation helpers should be removed, leaving only deprecated stub plus diff-guard | runtime delegated_authoring modules | implementation cleanup | This prevents deprecated manifest-heavy design from appearing active while preserving the external blocked command surface | strong | deep-consultant result 2026-05-25 | orchestrator | pending code review | no | reflected to runtime implementation |
| EAL-007 | adopted | reviewer | code-reviewer / qa-reviewer | diff-guard must fail closed for forbidden dirty-baseline paths and non-proposed allowlisted discussion updates | runtime delegated_authoring modules, tests | implementation safety hardening | Findings identified P1 eligibility gaps in the exact post-run guard that protects canonical single-writer authority | strong | code-reviewer and qa-reviewer results 2026-05-25: initial `review_status=fail`, final `review_status=pass` | orchestrator | code-reviewer / qa-reviewer | no | reflected to runtime and tests |
| EAL-008 | adopted | reviewer | code-reviewer / qa-reviewer | existing discussion update eligibility must include pre-change lifecycle state, not only post-change text | runtime delegated_authoring modules, tests | implementation safety hardening | This closes the accepted/adopted/stale to proposed rewrite bypass without reintroducing manifest-heavy metadata | strong | code-reviewer / qa-reviewer P2 results 2026-05-25; final re-review pass | orchestrator | code-reviewer / qa-reviewer | no | reflected to runtime and tests |
| EAL-009 | adopted | reviewer | qa-reviewer / code-reviewer | dirty baseline target discussions and untracked lifecycle-locked discussion creates must fail closed | runtime delegated_authoring modules, tests, report | implementation safety hardening | `--baseline-status` has no content snapshot, so scope-local discussion dirtiness before delegated execution cannot be safely ignored | strong | qa-reviewer P1 result and code-reviewer P2 result 2026-05-25; final re-review pass | orchestrator | code-reviewer / qa-reviewer / spec-reviewer | no | reflected to runtime, docs, tests, and report |
| EAL-010 | adopted | reviewer | Codex PR review | diff-guard must reject staged/working-tree mixed discussion states, unmerged statuses, and non-UTF-8 HEAD pre-change blobs | runtime delegated_authoring modules, tests, report | PR review hardening | These findings cover post-PR adoption integrity gaps not exercised by earlier reviewer gates | strong | Codex PR review #128, 2026-05-25; targeted 16-test run | orchestrator | implemented / locally verified | no | reflected to runtime, tests, and report |
| EAL-011 | adopted | reviewer | Codex PR review / deep-consultant / code-reviewer | diff-guard baseline subtraction must ignore unchanged pre-existing non-target dirtiness without allowing target discussion baseline dirtiness, mtime-preserved canonical rewrites, mode-only changes, mixed-index staged changes, or repo-local baseline tampering | runtime delegated_authoring application/command/parser, workflow docs, tests, report | PR review hardening | This preserves delegated output scope checking without turning the helper into a global clean tree gate, while requiring repo-external file-state proof for unsafe baseline exclusions and refusing ambiguous index/worktree states | strong | Codex PR review #128, 2026-05-25; deep-consultant result; code-reviewer mtime, repo-local tamper, mode, nested-discussion, and mixed-index findings; targeted 22/24-test runs; full 897-test run | orchestrator | code-reviewer pass / local tests pass | no | reflected to runtime, docs, tests, and report |
| EAL-012 | adopted | reviewer | Codex PR review | baseline-only entries and porcelain quoted paths must not bypass or falsely block diff-guard | runtime delegated_authoring application, workflow docs, tests, report | PR review hardening | Disappeared baseline entries represent delegated-run mutation of pre-existing dirtiness, and status parsing must preserve filenames before file-state matching can be trusted | strong | Codex PR review #128, 2026-05-25; targeted 25/27-test runs | orchestrator | implemented / locally verified | no | reflected to runtime, docs, tests, and report |
| EAL-013 | adopted | reviewer | Codex PR review | editable-state must come from frontmatter metadata, new draft files must carry editable provenance state, and baseline-status path fields must be escaped / decoded losslessly | runtime delegated_authoring application/domain, tests, report | PR review hardening | These findings prevent prose-only lifecycle claims and control-character filenames from bypassing the delegated output guard while preserving scope-local discussion direct-write | strong | Codex PR review #128, 2026-05-25; targeted 28/30-test runs; full 903-test run | orchestrator | implemented / locally verified | no | reflected to runtime, tests, and report |
| EAL-014 | adopted | reviewer | Codex PR review | quoted rename baseline lines must not split inside escaped path fields | runtime delegated_authoring application, tests, report | PR review hardening | Pre-existing rename dirtiness can be a legitimate baseline entry, and filenames may contain the textual arrow separator; parser correctness is required before file-state matching can be trusted | strong | Codex PR review #128, 2026-05-25; targeted 29/31-test runs; full 904-test run | orchestrator | implemented / locally verified | no | reflected to runtime, tests, and report |

## 委任ドラフト証跡
- 委任 authoring の使用: not used
- 現時点の委任利用:
  - Read-only sub-agent analysis and spec review were used.
  - No write-capable sub-agent discussion draft has been produced or promoted for this issue yet.
- 軽量 delegated draft evidence contract for future runs:
  - required discussion draft provenance: `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`
  - required output eligibility evidence: `diff_guard_result`, `allowed_paths_summary`, `forbidden_diff_summary`, `baseline_reference`
  - forbidden self-claims: `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`
  - adoption authority: only this report's Evidence Adoption Ledger can record adoption into canonical docs or implementation decisions.
- Current promotion decision:
  - No delegated draft promotion has occurred.
  - Read-only analysis was adopted through EAL-003 and EAL-004.

## ワークフロー委任同意の証跡
| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture` | iss-00127 | current session | repo-analyst / deep-consultant / spec-reviewer / future doc-writer / future dev-coder / future code-reviewer / future qa-reviewer | same repo, active issue, issue objective; destructive action / credentialed external access / publishing / scope expansion requires separate confirmation where host policy requires it | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

## レビューゲート状態
| Step / Phase | Gate | Reviewer Role | Freshness | State | Risk Acceptance | Promotion / Completion Decision | Notes |
|---|---|---|---|---|---|---|---|
| requirement | requirement reviewer | spec-reviewer | fresh | passed | N/A | proceed to design | 2026-05-25: current requirement reviewed against workflow_spec_authoring.md, phase_requirement.md, workflow_issue.md and V2 discussions; findings none |
| design/plan/report | spec authoring reviewer | spec-reviewer | fresh | failed | no | blocked until fixes and re-review | 2026-05-25: naming rule, plan closure gates, S02 reviewer gate, and report placeholder / retired contract findings were addressed in current working tree |
| design/plan/report | spec authoring reviewer | spec-reviewer | fresh | passed | N/A | proceed to implementation | 2026-05-25: fresh review found no P0/P1 blockers; requirement/design/plan/report and ADR are phase-ready and implementation-ready |
| implementation | code reviewer | code-reviewer | fresh | failed | no | blocked until fixes and re-review | 2026-05-25: P1 dirty-baseline forbidden path gap and P2 dangling symlink gap were fixed |
| implementation | QA reviewer | qa-reviewer | fresh | failed | no | blocked until fixes and re-review | 2026-05-25: P1 dirty-baseline coverage gap and P1 non-proposed allowlisted update gap were fixed |
| implementation/docs | final spec reviewer | spec-reviewer | fresh | passed | N/A | proceed after report ledger cleanup | 2026-05-25: no P0/P1 spec blockers; P2 stale final gate row cleanup addressed in this report |

## Spec Authoring Gate
| Phase | investigated facts | open questions | delegation consent | reviewer | verdict | fixes | promotion |
|---|---|---|---|---|---|---|---|
| requirement | Active issue V2 discussions, accepted ADR, workflow_spec_authoring.md, phase_requirement.md, workflow_issue.md, current repo impact | none remaining; Q-001/Q-002 resolved into requirement/design | user instruction for repo-analyst / deep-consultant / spec-reviewer within active issue scope | fresh spec-reviewer, requirement scope | passed | requirement rewritten from V2 draft; post-run diff guard and static adapter decisions resolved | promoted to design input |
| design | requirement.md, accepted ADR, V2 draft, repo-analyst impact map, deep-consultant decision support, runtime / asset file structure | none remaining | same active issue consent; read-only consultants/reviewers used | fresh spec-reviewer passes were failed until naming rule and diagram metadata were fixed; latest fresh review passed | passed | added collision-safe naming rule, diagram metadata, runtime helper boundary, static adapter no-broad-write stance, manifest deprecated behavior | promoted to plan / implementation input |
| plan | design.md, issue-plan authoring docs, phase_plan_issue.md, workflow_issue.md, closure index, reviewer feedback | none remaining | same active issue consent; future dev-coder/doc-writer/code-reviewer/qa-reviewer permitted by user instruction within issue scope | fresh spec-reviewer passes were failed until step-local tests, closure gates, S02/S03 delegation contracts, S02 reviewer gate, report cleanup, and ADR reflection were fixed; latest fresh review passed | passed | added concrete tests, closure contracts, step gates, Final Exit Contract, mixed reviewer gates, complete S02/S03 handoff contracts, lightweight report ledger | promoted to implementation |

## 実装記録
- Implementation is complete in the working tree and final local reviewer/test gates passed.
- Latest post-review safety hardening is complete in the working tree.
- Planned implementation steps are defined in `plan.md`.
- No step commit has been created for implementation yet.

### S01 Runtime delegated-authoring behavior
- 状態: implemented / full local tests passed
- delegated role: dev-coder
- allowed paths: runtime delegated_authoring modules and runtime delegated_authoring tests
- observed changes:
  - `delegated-authoring manifest` now returns deprecated/blocked and writes no `discussions/delegated-authoring/` artifacts.
  - `delegated-authoring diff-guard` classifies only post-run diffs and permits target scope `discussions/` direct-child Markdown with collision-safe names.
  - baseline entries are ignored when the same entry is independently eligible under diff-guard, or when a non-target pre-existing dirty path has a repo-external baseline `file-state-sha256` snapshot matching current file content and mode and is not a mixed index/worktree status.
  - baseline entries that disappear from current status are returned to diff-guard evaluation, so deleting/restoring pre-existing non-target dirtiness during a delegated run fails closed.
  - current Git status is parsed with porcelain v1 `-z`, and baseline text parsing only treats ` -> ` as rename/copy syntax for rename/copy statuses, so paths containing spaces or arrow text keep their real filename.
  - tracked existing discussion updates validate both current file text and Git HEAD pre-change text, so accepted/adopted/stale artifacts cannot be rewritten to `proposed` to bypass lifecycle eligibility.
  - existing discussion lifecycle eligibility is anchored to frontmatter metadata only; body text that merely mentions `status: proposed` or `adoption_status: unreviewed` is ignored.
  - target scope `discussions/` subtree must be clean at delegated-run baseline time; dirty or untracked discussion entries in `--baseline-status` are rejected because delegated output and existing draft/provenance state cannot be safely separated there.
  - canonical docs that newly appear or differ from the repo-external baseline file-state snapshot remain rejected as delegated output, while unchanged pre-existing orchestrator dirtiness does not make the helper a global clean tree gate.
  - new discussion creates are rejected unless frontmatter metadata declares editable draft state such as `adoption_status: unreviewed` or `status: proposed`, and they are also rejected when they claim non-editable states such as `accepted`, `adopted`, `superseded`, or `stale`.
  - `delegated-authoring baseline-status` writes path fields as escaped text and the baseline parser decodes JSON-escaped and legacy C-quoted path fields before file-state matching.
  - baseline text rename entries split only on the ` -> ` separator outside a quoted path field, so quoted filenames containing arrow text preserve their actual original path.
  - mixed staged/unstaged target discussion statuses and unmerged statuses are rejected so diff-guard does not approve a different index payload than the working tree text it inspects.
  - non-UTF-8 Git HEAD pre-change discussion blobs are rejected with `existing_discussion_head_non_utf8` instead of crashing.
  - canonical docs, implementation/test/config roots, `.agents`, `.codex`, `.github`, `.env*`, nested discussions, symlinks including dangling symlinks, non-Markdown, retired `note` kind, rename/copy/delete, unallowlisted existing discussion updates, and allowlisted existing discussion updates without proposed/unreviewed state are rejected.
  - legacy manifest/Profile/probe/session rendering helpers were removed after fresh deep-consultant analysis.
- required closure ids: `tc-001`, `tc-002`, `tc-003`, `tc-004`
- required verification: `python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v`

### S02 Shipped authoring contract
- 状態: implemented / full local tests passed
- delegated role: doc-writer
- allowed paths: provider docs / authoring docs / skills / adapters / templates / active-none reports
- observed changes:
  - workflow / phase / authoring docs describe scope-local flat discussion direct-write, canonical single-writer authority, lightweight provenance, diff guard, and grandfathered historical manifest evidence.
  - system architect and implementation planner skills now write only scope-local flat discussion evidence and deny canonical docs, implementation files, GitHub mutation, phase promotion, reviewer-pass claims, and user-dialogue ownership.
  - Codex static adapters are read-mostly fallback surfaces and no longer grant static write roots.
  - report templates / active-none reports carry lightweight delegated draft evidence and evidence adoption ledger destinations.
- required closure ids: `tc-005`, `tc-006`, `tc-007`, `tc-009`
- required verification: targeted `rg` inspection and relevant asset assertions after integration

### S03 Dogfooding mirror and parity
- 状態: implemented / sync-validate-doctor passed
- observed changes:
  - Provider-side runtime/docs/skills/adapters/templates/active-none report changes were mirrored into local dogfooding `spec-dock/`, `.agents/`, and `.codex/`.
  - Targeted runtime and asset contract tests, full unittest, `sync`, `validate`, and `doctor` passed after mirror sync.
- required closure id: `tc-008`
- required verification: provider/mirror parity, `sync`, `validate`, `doctor`

## クロージャ状況
| Closure ID | Step | Planned Evidence | Observed Evidence | Result | Notes |
|---|---|---|---|---|---|
| tc-001 | S01 | CLI/domain tests for manifest deprecated blocked no-artifact behavior | `python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring ... -v` passed targeted cases | passed | manifest returns deprecated/blocked and no artifact path output |
| tc-002 | S01 | CLI/domain tests for allowed naming-rule compliant discussion draft create | same targeted test run passed | passed | `<ts>-<kind>-<slug>.md` and `<ts>-<nn>-<kind>-<slug>.md` allowed forms covered |
| tc-003 | S01 | CLI/domain tests for forbidden path rejection | same targeted test run passed | passed | canonical docs, forbidden roots, env file covered |
| tc-004 | S01 | domain tests for malformed discussion diff rejection | same targeted test run passed | passed | nested, symlink including dangling symlink, non-md, bad name, retired `note`, delete, rename/copy, unallowlisted update, non-proposed allowlisted update, accepted-to-proposed pre-change spoof, dirty-baseline discussion rewrite, missing frontmatter editable state on new draft, body-only editable-state spoof, non-editable new-create claim, mixed staged/unstaged status, unmerged status, non-UTF-8 HEAD blob, unchanged non-target baseline dirtiness, disappeared baseline forbidden path, escaped tab path, quoted/space path, arrow filename, quoted rename baseline arrow original path, after-baseline canonical touch, other scope covered |
| tc-005 | S02 | skill text inspection / asset tests / spec-reviewer | `test_issue_116_delegated_authoring_phase_gate_contract_assets` and `test_bundled_skill_routing_contract` passed in targeted and full runs | passed | no remaining S02 spec blocker observed |
| tc-006 | S02 | adapter inspection / asset tests / code-reviewer | `test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` passed in targeted and full runs | passed | no remaining adapter-specific blocker observed |
| tc-007 | S02 | report template inspection / asset tests / spec-reviewer | `test_issue_116_delegated_authoring_phase_gate_contract_assets`, active-none/template parity tests, and full unittest passed | passed | stale final-reviewer wording removed |
| tc-008 | S03 | provider/mirror parity tests / sync / validate / doctor | provider/dogfooding mirror parity tests passed; `sync`, `validate`, `doctor`, and `git diff --check` passed | passed | `validate` nodes=65; `doctor` findings=0 |
| tc-009 | S90 | docs inspection / spec-reviewer | local asset tests, full unittest, and final spec-reviewer pass observed | passed | P2 stale report row cleanup addressed |
| tc-010 | S99 | final tests / validation / reviewers | full unittest and spec-dock validation passed; targeted tests passed after dirty-baseline fail-closed hardening; final reviewers passed | passed | code-reviewer / qa-reviewer / spec-reviewer final re-review passed |

## 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=65

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract -v
Ran 12 tests in 3.486s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 11 tests in 4.708s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_spec_document_templates_keep_policy_out_of_scaffold tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_templates_match_provider_assets -v
Ran 4 tests in 0.090s
OK

python -m unittest discover -v
Ran 884 tests in 417.849s
OK

python -m unittest discover -v
Ran 886 tests in 423.165s
OK

python -m unittest discover -v
Ran 887 tests in 423.306s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 12 tests in 5.896s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 14 tests in 6.946s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
Ran 1 test in 0.001s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_workflow_issue_doc_matches_bundled_asset -v
Ran 18 tests in 6.731s
OK

python -m unittest discover -v
Ran 889 tests in 422.243s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 16 tests in 7.985s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
Ran 1 test in 0.004s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 18 tests in 7.796s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 17 tests in 8.946s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 18 tests in 9.894s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 19 tests in 10.837s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 21 tests in 13.071s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 22 tests in 14.988s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 19 tests in 8.800s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 20 tests in 9.966s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 23 tests in 13.036s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 24 tests in 15.123s
OK

python -m unittest discover -v
Ran 891 tests in 424.017s
OK

python -m unittest discover -v
Ran 892 tests in 431.121s
OK

python -m unittest discover -v
Ran 897 tests in 436.938s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 25 tests in 17.406s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 27 tests in 17.262s
OK

python -m unittest discover -v
Ran 900 tests in 436.407s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 28 tests in 18.498s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 30 tests in 18.114s
OK

python -m unittest discover -v
Ran 903 tests in 436.598s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 29 tests in 19.748s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 31 tests in 19.342s
OK

python -m unittest discover -v
Ran 904 tests in 439.939s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 34 tests in 22.513s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 36 tests in 22.549s
OK

python -m unittest discover -v
Ran 909 tests in 441.194s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
Ran 36 tests in 24.019s
OK

python -m unittest discover -v
Completed with exit code 0; detailed output included the new nested ignored `.env*` regression test passing and was truncated by the execution tool before the unittest summary line.

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
Ran 37 tests in 24.852s
OK

python -m unittest discover -v
Ran 911 tests in 444.878s
OK

./spec-dock/scripts/spec-dock sync
spec-dock: sync: active unchanged (matched id in branch: iss-00127)
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=65

./spec-dock/scripts/spec-dock doctor
spec-dock: ok (doctor) findings=0

git diff --check
OK
```

## 最終品質ゲート
| Gate | Reviewer / Command | Scope | Result | Notes |
|---|---|---|---|---|
| Docs Impact Resolution | spec-reviewer | docs/templates/workflow/skill/adapter guidance | passed | final spec-reviewer found no P0/P1 spec blockers |
| Final QA Gate | qa-reviewer | issue obligation coverage | passed | final QA re-review found no P0/P1/P2 findings |
| Final Code Review Gate | code-reviewer | issue-wide integrated diff | passed | final code re-review found no P0/P1/P2 findings |
| Final Spec Review Gate | spec-reviewer | requirement/design/plan/report/implementation/tests/docs alignment | passed | final spec-reviewer found no P0/P1 blockers; P2 evidence freshness addressed in this report |
| Final Commit Gate | git status / commit evidence | final report ledger and commit scope | external-evidence-required | implementation commit and report updates have been delivered to PR; final post-commit head SHA and clean check are recorded as external PR/final-response evidence because they necessarily occur after this committed report text |

## PR 送達ゲート
| Field | Evidence |
|---|---|
| PR URL | https://github.com/chemitaro/spec-dock/pull/128 |
| selected base | `iss-00118-delegated-authoring-dogfooding-pilot` |
| base-resolution source | current stacked epic branch and GitHub PR #119 |
| base-resolution conflict / handling | `origin/main...HEAD` contains the parent Epic stack, while `origin/iss-00118-delegated-authoring-dogfooding-pilot...HEAD` isolates iss-00127; retargeting #128 to `main` now would turn this into a broad Epic PR instead of the iss-00127 correction PR |
| draft / ready decision | ready PR |
| head branch | `iss-00127-scoped-discussion-draft-authoring-correction` |
| issue linkage | `Closes #127` in PR body |
| existing PR reuse / new PR creation decision | reused existing PR #128 |

## マージ準備ゲート
| Field | Evidence |
|---|---|
| PR open state | open / ready |
| monitor status | passed for latest monitored implementation head before this report-only evidence update |
| latest monitored head SHA | `6f0612741cf0aefb4dfc6d0f50a611bafec8aa35` |
| fix loop count / history | Codex review fix loop closed P1/P2 findings through staged/working-tree, baseline delta, path parsing, metadata anchoring, and quoted rename baseline fixes |
| required check status | GitHub `validate` and `provider-tests` succeeded on latest monitored head |
| non-required check status and waiver evidence | none observed / no waiver used |
| blocking review status | Codex Review latest response: `Didn't find any major issues`; previous P1/P2 comments target older commits and are reflected in D-008 through D-012 |
| merge conflict / visible merge blocker status | GitHub `mergeable=MERGEABLE` for PR #128 against selected stacked base |
| unresolved review-thread limitation status | thread-level resolution not available in this workflow run; latest Codex review comment found no major issues |
| unresolved blockers | none for selected stacked base; direct `main` merge remains pending parent PR #119 |
| final merge-prepared decision | merge-prepared as stacked PR; not yet main-direct merge-prepared until #119 is merged and #128 is retargeted/rebased to `main` |

## Main マージ可能性
- 現在の #128 は `main` 直ではなく #119 (`iss-00118-delegated-authoring-dogfooding-pilot`) に積む stacked PR である。
- #119 は確認時点で open / ready / `MERGEABLE`、`validate` と `provider-tests` は success。
- #128 を現時点で `main` へ retarget すると、#119 由来の Epic 全体差分も含む broad PR になり、iss-00127 単体の review boundary を失う。
- したがって main への最終 merge path は、#119 を先に main へ merge し、その後 #128 を `main` へ retarget / rebase して再度 checks / review を確認すること。
- この状態は product implementation blocker ではないが、ユーザー objective の「main branch にマージ可能な PR」完了条件に対しては外部順序依存として残る。

## 遭遇した問題と解決
- 問題: 初期 report に旧 manifest-heavy delegated draft evidence fields と template placeholder rows が残っていた。
  - 解決: 現在観測済みの evidence だけを残す軽量 ledger へ置き換え、future delegated draft evidence は scope-local discussion provenance、diff-guard result、orchestrator adoption ledger を中心にした。
- 問題: code-reviewer / qa-reviewer が、dirty baseline の forbidden path mutation が status-key filtering で見逃されうること、dangling symlink が `exists()` check の後ろで漏れうること、allowlisted existing discussion update が proposed/unreviewed state を検査していないことを指摘した。
  - 解決: baseline で無視できる entry を diff-guard eligible entry に限定し、forbidden dirty path は fail-closed にした。symlink は dangling でも拒否し、allowlisted existing discussion update は `status: proposed` または `adoption_status: unreviewed` を必須にした。追加 CLI/domain tests で確認した。
- 問題: allowlisted existing discussion update が、採用済み状態を proposed/unreviewed に書き換えて diff-guard を通過する余地が残っていた。
  - 解決: tracked update では Git HEAD の pre-change text と current text の両方を検査し、accepted/adopted/stale などの非編集対象状態が変更前に含まれていた場合は拒否するようにした。baseline-status の ignore 判定にも同じ pre-change enrichment を適用した。
- 問題: `--baseline-status` は status key だけで本文 snapshot を持たないため、baseline 時点ですでに dirty な target discussion が lifecycle-locked state を経由して delegated run 後に proposed へ戻るケースを証明できなかった。
  - 解決: target scope `discussions/` の dirty/untracked baseline entry は `dirty_baseline_discussion` として fail-closed にし、run 開始前の target discussions clean 状態を要求した。あわせて新規 discussion create が accepted/adopted/stale などの非編集対象 state を自己主張するケースを拒否した。
- 問題: Codex PR review が、mixed staged/unstaged discussion status、unmerged status、非 UTF-8 HEAD blob の P1 safety gaps を指摘した。
  - 解決: target discussion の mixed staged/unstaged status と unmerged status を fail-closed にし、HEAD pre-change blob が UTF-8 decode できない場合は blocked reason として返すようにした。追加 CLI/domain tests で確認した。
- 問題: Codex PR review が、baseline に存在して delegated run 後も変わっていない canonical doc dirtiness まで `canonical_doc` としてブロックされ、diff-guard が global clean tree gate 化していると指摘した。
  - 解決: target `discussions/` subtree の dirty baseline は fail-closed のまま維持し、repo 外に置いた `delegated-authoring baseline-status --output` の `file-state-sha256` snapshot と current file content/mode が一致し、mixed index/worktree status でない non-target baseline entry だけを除外するようにした。未変更 canonical doc の許可、mtime が戻されても content が変わった canonical doc の拒否、mode-only canonical change の拒否、mixed staged canonical change の拒否、nested dirty baseline discussion の拒否、repo-local baseline output の拒否を CLI tests で確認した。
- 問題: Codex PR review が、baseline entry が current status から消えた場合に pre-existing non-target dirtiness の削除/復元を見逃せること、porcelain text parsing が quoted path と ` -> ` を含む通常ファイル名を誤読しうることを指摘した。
  - 解決: baseline-only entry を diff-guard 評価対象へ戻して fail-closed にし、current status は `git status --porcelain=v1 -z` で取得するようにした。あわせて baseline text parser は rename/copy status の場合だけ ` -> ` を rename separator として扱う。disappeared `.env.local`、space path、arrow filename の CLI tests で確認した。
- 問題: Codex PR review が、本文 prose に `status: proposed` があるだけで既存 discussion update が editable と判定されること、新規 draft が editable provenance metadata なしで通過すること、baseline-status の path field が tab や C-quoted path で誤分割されうることを指摘した。
  - 解決: editable-state 判定を frontmatter metadata に限定し、新規 draft create でも `adoption_status: unreviewed` または `status: proposed` を必須にした。baseline-status の path field は JSON escaping で出力し、parser は JSON-escaped / legacy C-quoted path を decode する。missing-frontmatter、body-only spoof、tab path の tests で確認した。
- 問題: Codex PR review が、baseline text の rename 行で quoted original path 内の ` -> ` を rename separator として誤分割しうることを指摘した。
  - 解決: rename/copy baseline line の parser を、quoted path field の終端を escape-aware に特定してから、その外側の ` -> ` だけで分割する形にした。`"manual -> notes.md" -> "renamed notes.md"` の baseline を使う CLI test と full unittest で確認した。
- 問題: Codex PR review が、`discussions/` root または timestamp 付き discussion draft が symlink の場合に、Git status diff が空だと diff-guard を通過しうること、ignored `.env*` などの forbidden output が status 収集から漏れうること、porcelain `-z` path を UTF-8 強制 decode して非 UTF-8 filename を status parse failure にしていたことを指摘した。
  - 解決: `discussions/` root symlink と valid discussion filename の symlink child を、status entry がなくても fail-closed にした。既存 scaffold の `discussions/rules.md` は正式な guidance symlink であり delegated draft filename ではないため許容する。ignored forbidden output は全 ignored tree ではなく `.env*` / `.agents` / `.codex` / `.github` / `src` / `tests` に限定して `git ls-files --others --ignored --exclude-standard -z` で追加収集する。porcelain `-z` path は filesystem decode で扱い、baseline path field は ASCII-safe JSON escaping にした。CLI/domain tests、mirror parity tests、full unittest で確認した。
- 問題: Codex PR review が、ignored forbidden output の `.env*` pathspec が repo root 直下だけを対象にしており、`**/.env*` のような ignore rule で隠れた nested secret output を捕捉できないと指摘した。
  - 解決: ignored forbidden output の収集 pathspec に `:(glob)**/.env*` を追加し、nested ignored `.env.secret` が delegated run 後に作成された場合も `reason=env_file` で fail-closed する CLI regression test を追加した。targeted CLI/domain/mirror test と full unittest exit code 0 で確認した。
- 問題: Codex PR review が、`.env.d/secret.txt` のような `.env*` directory descendant は `.env*` / `:(glob)**/.env*` だけでは ignored forbidden output として収集できないと指摘した。
  - 解決: ignored forbidden output の収集 pathspec に `.env*/**` と `:(glob)**/.env*/**` を追加し、path part のいずれかが `.env` で始まる場合も `reason=env_file` に分類するようにした。`tmp/.env.d/secret.txt` の CLI regression test、provider/dogfooding mirror parity、full unittest で確認した。

## 今後の推奨事項
- #119 を main へ merge した後、#128 を `main` へ retarget / rebase し、GitHub checks と Codex review を再確認する。
