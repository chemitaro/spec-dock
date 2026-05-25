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
| D-002 | superseded-by-s05 | implementation | deep-consultant / orchestrator | static adapter で scope-local `discussions/` write をどこまで表現するか未確定だった | A: broad write with guard; B: no broad static write; C: keep canonical draft target write | S05 で superseded。static adapter は read-mostly fallback ではなく、system-architect / implementation-planner に限り scope-local `discussions/*.md` write を静的に持つ。canonical docs write と broad `spec-dock/initiatives` write は引き続き禁止する | User follow-up clarified that proposal-only/read-mostly is too restrictive for these authoring roles, while canonical docs remain main-orchestrator-only | superseded_by_D-S05-001 | `requirement.md` Q-002 historical decision; S05 `D-S05-001`; updated adapters/tests/report | none |
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
| D-013 | superseded-by-s05 | implementation | qa-reviewer / spec-reviewer / code-reviewer / orchestrator | S04 の scoped-write execution path が `discussions/` directory write root と advisory `write_policy` だけでは nested / non-md / per-agent dir を実行境界で止められない | A: directory write root + post-run diff-guard に委ねる; B: static adapter に broad write を足す; C: runtime scoped-context で選択済み direct child Markdown 1ファイルだけを `write` root にする | S05 で superseded。`delegated-authoring scoped-context --discussion-file` と動的設定書き換えは削除し、静的 scope-local `discussions/*.md` write + post-run diff-guard/report adoption を採用する | User clarified that per-run config rewrite is too complex and unsuitable for multi-scope delegated authoring; the durable rule should stay static, simple, and file-based | superseded_by_D-S05-001 | S04 historical reviewer findings; S05 deletion regression tests; S05 `D-S05-001`; runtime removal diff | none |

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
| EAL-015 | adopted | reviewer | code-reviewer / qa-reviewer / spec-reviewer | S04 scoped-context must select the generated permission profile and enforce exact direct child Markdown file write roots, not just declare a policy label | runtime delegated_authoring application/command, tests, adapter/skill guidance, report | S04 implementation correction | Findings identified the exact mismatch between user intent, S04 plan, and the first implementation attempt; fixing this prevents `discussions/delegated-authoring/` or nested files from being writable through the execution path | strong | sub-agent review results 2026-05-25; targeted scoped-context tests | orchestrator | code-reviewer pass / qa-reviewer pass / spec-reviewer pass | no | reflected to runtime, assets, tests, design, and report |
| EAL-016 | adopted | reviewer | qa-reviewer / orchestrator | S04 must also pin read-only specialist and workspace-write worker taxonomy so the scoped-write correction does not broaden adjacent agent permissions | `tests/test_init_update.py`, provider agent assets | S04 regression coverage | This directly covers `tc-s04-003` and prevents repeating the static/scoped role classification mistake that triggered the issue | strong | qa-reviewer result 2026-05-25; `test_s04_codex_agent_permission_taxonomy_contract` | orchestrator | qa-reviewer pass | no | reflected to tests |

## 委任ドラフト証跡
- 委任 authoring の使用: not used
- 現時点の委任利用:
  - Read-only sub-agent analysis and spec review were used.
  - No write-capable sub-agent discussion draft has been produced or promoted for this issue yet.
- 軽量 delegated draft evidence contract for future runs:
  - manually authored sub-agent draft / analysis / discussion-local report は、必要に応じて `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []` を持つ。
  - S06 command-created `draft-requirement` / `draft-design` / `draft-plan` は canonical-template-derived draft artifact であり、draft 専用 envelope/provenance metadata を要求しない。draft 性は scope-local `discussions/` placement、`draft-*` filename、canonical template source selection、diff-guard result、Evidence Adoption Ledger で扱う。
  - required output eligibility evidence for delegated write runs: `diff_guard_result`, `allowed_paths_summary`, `forbidden_diff_summary`, `baseline_reference`
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
| S04 correction | QA reviewer | qa-reviewer | fresh | passed | N/A | proceed | 2026-05-25: initial P1/P2 findings fixed by exact `--discussion-file` write root, exact write-root assertion, and taxonomy tests; re-review found no P0/P1 blockers |
| S04 correction | spec reviewer | spec-reviewer | fresh | passed | N/A | proceed | 2026-05-25: initial P1/P2 findings fixed by exact-file scoped context, S04 report evidence, and design CLI contract update |
| S04 correction | code reviewer | code-reviewer | fresh | passed | N/A | proceed | 2026-05-25: initial P1 findings fixed with `default_permissions` and exact file write root; re-review found no P0/P1/P2 findings |

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

### S04 Agent permission taxonomy and scoped-write execution correction
- 状態: implemented / targeted local tests passed / reviewer gates passed
- delegated role: orchestrator direct implementation with code-reviewer / qa-reviewer / spec-reviewer review findings
- observed changes:
  - `delegated-authoring scoped-context` now requires `--discussion-file` and resolves it against the target scope `discussions/`.
  - scoped context blocks discussion file targets outside the resolved scope, nested paths, non-Markdown files, non-compliant discussion filenames, symlinks, and non-file existing targets.
  - scoped context emits `default_permissions = <generated profile>` so the generated profile is selected when used as runtime context.
  - generated permission profile grants write only to the exact selected direct child Markdown file, not to the whole `discussions/` directory or `spec-dock/initiatives`.
  - static `system-architect` / `implementation-planner` adapters remain read-mostly fallback surfaces with no static write roots and no broad workspace write.
  - provider and dogfooding mirror `.codex/AGENTS.md`, adapter TOMLs, and role skills describe runtime scoped context with `--discussion-file`.
  - taxonomy regression coverage asserts researcher / consultant / deep-consultant / repo-analyst / reviewers / pr-monitor / spark-worker remain read-only specialists, dev-coder / doc-writer / utility-worker / worker remain workspace-write workers, and system-architect / implementation-planner remain static no-write scoped delegated authors.
- required closure ids: `tc-s04-001`, `tc-s04-002`, `tc-s04-003`, `tc-s04-004`
- required verification: scoped-context CLI tests, taxonomy asset tests, provider/mirror parity, `validate`, `sync`, `doctor`, `git diff --check`, reviewer re-review

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
| tc-s04-001 | S04 | scoped-write authoring agents are not read-only specialists | `test_scoped_context_writes_external_permission_context_for_exact_discussion_file` passed for system-architect and implementation-planner; static adapter tests passed | passed | runtime context provides write-capable exact-file profile while static adapters remain no-write fallback |
| tc-s04-002 | S04 | scoped-write does not become broad write | scoped-context tests passed: write root is exact discussion file; target directory itself is not a write root; nested, non-md, and bad-name targets are blocked | passed | fixes reviewer P1 about advisory-only direct-child policy |
| tc-s04-003 | S04 | read-only specialists and workspace-write workers keep their taxonomy | `test_s04_codex_agent_permission_taxonomy_contract` passed | passed | read-only specialists remain `sandbox_mode = "read-only"`; worker roles remain `workspace-write`; scoped delegated authors have no static write roots |
| tc-s04-004 | S04 | diff guard remains adoption eligibility check, not write-boundary substitute | `tests.cli_runtime.test_delegated_authoring` and `tests.domain_runtime.test_delegated_authoring` passed; scoped-context write boundary is exact-file before diff-guard | passed | post-run diff-guard still required by context metadata and docs |

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

python -m unittest tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_writes_external_permission_context_for_exact_discussion_file tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_rejects_non_exact_discussion_file_targets tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_rejects_repo_local_output -v
Ran 3 tests in 2.781s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_s04_codex_agent_permission_taxonomy_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v
Ran 4 tests in 0.019s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 41 tests in 32.094s
OK

./spec-dock/scripts/spec-dock delegated-authoring scoped-context --role system-architect --scope iss-00127 --discussion-file 20260525t120000z-disc-system-architect-draft.md
spec-dock: ok (delegated-authoring scoped-context)
reason=scoped_context_ready
write_policy=exact_direct_child_markdown_file

./spec-dock/scripts/spec-dock delegated-authoring scoped-context --role implementation-planner --scope iss-00127 --discussion-file 20260525t120001z-disc-implementation-planner-draft.md
spec-dock: ok (delegated-authoring scoped-context)
reason=scoped_context_ready
write_policy=exact_direct_child_markdown_file

./spec-dock/scripts/spec-dock delegated-authoring scoped-context --role system-architect --scope iss-00127 --discussion-file delegated-authoring/20260525t120002z-disc-bad.md
spec-dock: blocked (delegated-authoring scoped-context)
reason=discussion_file_outside_target_discussions

python -m unittest tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_writes_external_permission_context_for_exact_discussion_file tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_rejects_non_exact_discussion_file_targets tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_rejects_repo_local_output tests.test_init_update.TestInitUpdate.test_s04_codex_agent_permission_taxonomy_contract tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers -v
Ran 5 tests in 2.728s
OK

python -m unittest discover -v
Ran 917 tests in 464.233s
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
| S04 QA Gate | qa-reviewer | scoped-context write boundary and taxonomy coverage | passed | initial P1/P2 findings fixed; final remaining P2 exact write-root assertion addressed |
| S04 Code Review Gate | code-reviewer | runtime permission context and selected profile | passed | re-review found no P0/P1/P2 findings |
| S04 Spec Review Gate | spec-reviewer | S04 docs/report/implementation alignment | passed | re-review found no P0/P1 blockers; P2 design CLI contract update addressed |

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
- 問題: S04 初期実装は generated scoped context に `default_permissions` がなく、かつ write root が target `discussions/` directory 全体だったため、実行境界として direct child Markdown only を保証できなかった。
  - 解決: `--discussion-file` を必須にし、resolved scope の `discussions/` direct child にある naming-rule compliant Markdown 1ファイルだけを write root とする context を生成するようにした。`default_permissions` で generated profile を選択し、nested / non-md / bad-name target を blocked にする tests を追加した。
- 問題: S04 初期実装は read-only specialist / full workspace-write worker / scoped delegated author の taxonomy regression coverage が不足していた。
  - 解決: `test_s04_codex_agent_permission_taxonomy_contract` を追加し、対象 agent 群の static permission classification を asset-level で固定した。

## S05 追補実装証跡

### S05 Red / 代替証跡
- `rg -n "scoped-context|--discussion-file|DelegatedAuthoringScopedContext|generate_delegated_authoring_scoped_context|read-mostly fallback|runtime scoped context required|one exact direct child Markdown file|no scoped context" src/spec_dock/assets spec-dock/scripts spec-dock/docs .codex .agents tests`:
  - 実装前は provider runtime、dogfooding runtime mirror、`.codex` adapters、`.agents` role skills、workflow docs、`tests/cli_runtime/test_delegated_authoring.py`、`tests/test_init_update.py` に S04 exact-file scoped-context 経路が残っていた。
  - static adapters は write root を持たず、run ごとの exact-file permission context を標準経路として要求していた。
- 旧 targeted tests:
  - `python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v` は実装前に S04 scoped-context exact-file tests を含む旧期待で走っていた。

### S05 実装内容
- Runtime:
  - `delegated-authoring scoped-context` parser binding、command spec、args class、argument builder、args factory、runner、expectation helper、renderer を削除した。
  - application layer から `DelegatedAuthoringScopedContextRequest` / `DelegatedAuthoringScopedContextResult` / `_SCOPED_CONTEXT_PERMISSION_PROFILES` / `generate_delegated_authoring_scoped_context` / `_blocked_scoped_context_result` / `_render_scoped_context_toml` / `_resolve_scoped_discussion_file` / `_scoped_discussion_file_error` / `_toml_string` を削除した。
  - `manifest` deprecated / blocked stub、`diff-guard`、`baseline-status` は維持した。
- Assets / guidance:
  - provider と dogfooding mirror の `system-architect` / `implementation-planner` adapters を static all scope-local `discussions/*.md` write capability に更新した。
  - canonical docs direct-write、implementation/test/config/secrets write、per-agent directory、run/task directory、`discussions/delegated-authoring/` は禁止のまま維持した。
  - role skills と workflow docs から read-mostly fallback / exact-file context requirement を削除し、static discussions write + post-run diff guard + orchestrator adoption ledger に更新した。
- Tests:
  - scoped-context exact-file generation tests を削除した。
  - adapter asset tests と taxonomy tests を static discussion write roots の期待へ更新した。
  - review follow-up として、`delegated-authoring scoped-context` が CLI subcommand として登録されていないことを自動テストで固定した。
  - review follow-up として、provider runtime/assets/docs、dogfooding mirror、agent guidance、runtime/domain tests に `--discussion-file` / scoped-context helper identifiers が再導入されない focused asset assertion を追加した。
  - stale `exact target` wording を phase plan issue docs と同 wording の epic docs から削除し、static scope-local discussion Markdown write + invocation scope + diff-guard/report adoption に整合させた。

### S05 Green 検証
```text
python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 38 tests in 28.350s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers tests.test_init_update.TestInitUpdate.test_s04_codex_agent_permission_taxonomy_contract -v
Ran 2 tests in 0.007s
OK

rg -n "scoped-context|--discussion-file|DelegatedAuthoringScopedContext|generate_delegated_authoring_scoped_context" src/spec_dock/assets spec-dock/scripts spec-dock/docs .codex .agents tests
only intentional deletion-regression test reference remains in tests/cli_runtime/test_delegated_authoring.py

rg -n "read-mostly fallback|runtime scoped context required|one exact direct child Markdown file|no scoped context|read-only fallback" src/spec_dock/assets spec-dock/docs .codex .agents tests
no matches

./spec-dock/scripts/spec-dock delegated-authoring scoped-context --help
exit code 2; valid choices are manifest, baseline-status, diff-guard

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=65

./spec-dock/scripts/spec-dock sync
spec-dock: ok (sync)

./spec-dock/scripts/spec-dock doctor
spec-dock: ok (doctor) findings=0

git diff --check
OK

# S05 review follow-up, 2026-05-25
python -m unittest tests.cli_runtime.test_delegated_authoring.TestDelegatedAuthoringCli.test_scoped_context_subcommand_is_not_registered tests.test_init_update.TestInitUpdate.test_issue_127_removed_scoped_context_contract_stays_removed -v
Ran 2 tests in 0.864s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 39 tests in 29.927s
OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_127_removed_scoped_context_contract_stays_removed tests.test_init_update.TestInitUpdate.test_issue_116_delegated_authoring_phase_gate_contract_assets tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers tests.test_init_update.TestInitUpdate.test_s04_codex_agent_permission_taxonomy_contract tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
Ran 5 tests in 0.030s
OK

rg -n -e "--discussion-file|scoped-context|DelegatedAuthoringScopedContext|generate_delegated_authoring_scoped_context|delegated_authoring_scoped_context" src/spec_dock/assets spec-dock/scripts spec-dock/docs .codex .agents tests --glob "!spec-dock/initiatives/**"
tests/cli_runtime/test_delegated_authoring.py:54: intentional negative CLI deletion-regression test reference only

rg -n "exact target" src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md spec-dock/docs/phase_plan_issue.md src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md spec-dock/docs/phase_plan_epic.md
no matches

rg -n 'scope-local `discussions/\*\.md` write|invocation scope|report ledger adoption evidence' src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md spec-dock/docs/phase_plan_issue.md src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md spec-dock/docs/phase_plan_epic.md
matches in provider/mirror phase_plan_issue.md and phase_plan_epic.md

git diff --check
OK
```

### S05 Step Contract Closure
| Closure ID | Result | Evidence |
|---|---|---|
| tc-s05-001 | passed | `system-architect` / `implementation-planner` adapters now declare static write roots for initiative / epic / issue scope-local `discussions/*.md`; adapter tests passed |
| tc-s05-002 | passed | static write roots are limited to discussion Markdown patterns; canonical docs, `src`, `tests`, `.agents`, `.codex`, `.github`, `.env*` remain non-write targets; diff-guard tests still pass forbidden path cases |
| tc-s05-003 | passed | runtime command surface now exposes only `manifest`, `baseline-status`, `diff-guard`; scoped-context command returns argparse invalid choice; deletion is covered by `test_scoped_context_subcommand_is_not_registered` |
| tc-s05-003a | passed | focused asset/test assertion blocks scoped-context / discussion-file / scoped context request/helper residue in runtime/assets/guidance target paths; residual `rg` found only the intentional negative CLI test reference |
| tc-s05-004 | passed | delegated_authoring CLI/domain tests passed; diff guard remains adoption eligibility check and was not replaced by permission generation |
| tc-s05-005 | passed | taxonomy asset test confirms read-only specialists remain read-only and workspace-write workers remain workspace-write |

### S05 Evidence Adoption Ledger
| ID | status | source_type | source | target | adoption rationale | evidence |
|---|---|---|---|---|---|---|
| EAL-S05-001 | adopted | discussion | `discussions/20260525t010211z-disc-static-all-discussions-write-permission-analysis.md` | provider/mirror adapters, skills, workflow docs, runtime, tests | S05 supersedes S04 exact-file context because delegated authoring should use static all scope-local discussions write with post-run diff guard adoption | S05 implementation diff and Green verification above |

### S05 Decision Ledger
| ID | status | type | source | ambiguity / constraint | proposed decision | evidence | follow-up |
|---|---|---|---|---|---|---|---|
| D-S05-001 | adopted-with-host-smoke-limitation | implementation | dev-coder + main orchestrator | Codex adapter TOML is inspectable in tests, but this local multi-agent runtime did not expose `system-architect` / `implementation-planner` as spawnable agent types for a live host write smoke. | Adopt explicit static glob-style discussion Markdown write-root keys in the adapter and keep broad `spec-dock/initiatives` write out of the profile. Do not restore scoped-context or dynamic settings rewriting. | TOML parses; asset tests verify only those three write roots; no broad write roots are present; provider/dogfooding mirrors match; attempted live authoring-role smoke was blocked by unavailable agent types in this runtime. | If host glob semantics differ in a runtime where these roles are spawnable, revise only the static permission expression; do not reintroduce scoped-context or broad write. |

## S06 追補実装証跡

### S06 Red / 代替証跡
- `./spec-dock/scripts/spec-dock new doc draft-design --issue iss-00127 --title "S06 Red Design Draft"`:
  - exit code 1
  - stderr: `error: Unknown discussion doc type: draft-design (allowed: adr, disc, research, interview, scratch)`
- `python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 -v` before implementation:
  - Ran 56 tests
  - OK
  - 既存 targeted tests は旧 `new doc` catalog の characterization として通過し、draft artifact type が未実装であることは上記 CLI Red で確認した。
- Corrective Red / alternative evidence after user clarification:
  - `find src/spec_dock/assets/spec_dock/templates/discussions spec-dock/templates/discussions -maxdepth 1 -type f` showed prohibited untracked `draft-requirement.md`, `draft-design.md`, and `draft-plan.md` under both provider and dogfooding mirror.
  - Existing S06 tests/report expected discussion-local envelope metadata, `template_source`, `diff_guard_result`, and canonical frontmatter stripping, which contradicted the corrected requirement/design/plan.
  - `find src/spec_dock/assets/spec_dock/templates/discussions spec-dock/templates/discussions -maxdepth 1 -type f | rg 'draft-'` returned matches before correction and no matches after correction.

### S06 実装内容
- Superseded / corrected:
  - The previous S06 implementation note that added `templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` is superseded by the user clarification. Draft-specific discussion templates are prohibited because they duplicate canonical templates.
  - The previous envelope/provenance/frontmatter-stripping expectation is superseded. Draft artifacts are identified by `discussions/` placement and `draft-*` filename, not by a dedicated wrapper template.
- Runtime:
  - `new doc` の creatable discussion doc type に `draft-requirement` / `draft-design` / `draft-plan` を追加した。
  - discussion filename parser / validation / diff-guard recognition を hyphenated draft kind に対応させた。
  - malformed discussion filename detection を補強し、`draft-requirement-kickoff.md` / `draft-design-kickoff.md` / `draft-plan-kickoff.md` のような non-timestamp hyphenated draft names を malformed として reject するようにした。
  - draft type の場合、scope kind と target artifact から既存 canonical `templates/{initiative,epic,issue}/{requirement,design,plan}.md` を直接 source として render し、`discussions/<ts>-draft-*-<slug>.md` に配置するようにした。
  - canonical template frontmatter は stripping せず、rendered canonical template content として保持する。
  - diff-guard は `draft-requirement` / `draft-design` / `draft-plan` filename の新規作成と明示 allowlist された既存 draft artifact 更新について、dedicated envelope metadata がなくても valid discussion draft artifact として許可する。ただし non-editable self-claim は従来通り拒否する。
  - `new draft` command は追加していない。
- Templates / docs:
  - provider と dogfooding mirror の `templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` を削除した。
  - `templates/README.md` と discussion rules / guidance docs は、`new doc draft-*` が draft 専用 template ではなく既存 canonical templates を source として使うことを案内するよう更新した。
  - provider docs rules と dogfooding mirror の discussion catalog / create examples を更新した。
- Tests:
  - CLI creation testsで initiative draft requirement、issue draft design、epic draft plan の作成、draft 専用 envelope 不在、scope-specific canonical template source 由来 content を固定した。
  - application runtime tests で initiative / epic / issue x draft-requirement / draft-design / draft-plan の 3x3 template source matrix、canonical frontmatter retention、same-second suffix allocation for hyphenated kinds を固定した。
  - `templates/discussions/draft-*.md` の偽 template が存在しても S06 draft artifact 生成で使われないことを固定した。
  - diff-guard tests で新規 draft artifact 作成、明示 allowlist された既存 draft artifact 更新、既存 draft artifact の accepted/adopted/stale self-claim rejection を固定した。
  - installer/update tests は `templates/discussions/draft-*.md` が存在しないこと、`app.py` と `domain/delegated_authoring.py` を含む provider/dogfooding runtime mirror parity を固定した。
  - validate tests は valid timestamped draft filenames と malformed non-timestamp hyphenated draft filenames の両方を固定した。

### S06 Green 検証
```text
python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09 -v
Ran 58 tests in 28.233s
OK

python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_delegated_authoring -v
Ran 69 tests in 114.617s
OK

python -m unittest tests.test_init_update -v
Ran 176 tests in 54.551s
OK

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=65

./spec-dock/scripts/spec-dock sync
spec-dock: sync: active unchanged (matched id in branch: iss-00127)
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md

./spec-dock/scripts/spec-dock doctor
spec-dock: ok (doctor) findings=0

git diff --check
OK

find src/spec_dock/assets/spec_dock/templates/discussions spec-dock/templates/discussions -maxdepth 1 -type f | rg 'draft-'
no matches (exit code 1 from rg)

Additional verification after QA/code-review hardening:

python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v
Ran 16 tests in 0.819s
OK

python -m unittest tests.cli_runtime.test_delegated_authoring tests.domain_runtime.test_delegated_authoring -v
Ran 42 tests in 34.603s
OK

python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.test_init_update -v
Ran 259 tests in 172.639s
OK

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=65

./spec-dock/scripts/spec-dock sync
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md

./spec-dock/scripts/spec-dock doctor
spec-dock: ok (doctor) findings=0

git diff --check
OK

find src/spec_dock/assets/spec_dock/templates/discussions spec-dock/templates/discussions -maxdepth 1 -type f
only adr.md / disc.md / interview.md / research.md / scratch.md under provider and dogfooding mirror
```

### S06 Step Contract Closure
| Closure ID | Result | Evidence |
|---|---|---|
| tc-s06-001 | passed | `test_new_doc_creates_draft_artifacts_from_scope_specific_templates` creates initiative `draft-requirement` and verifies naming, no draft envelope/provenance metadata, `templates/initiative/requirement.md`, and rendered canonical template content |
| tc-s06-002 | passed | same CLI test creates issue `draft-design` and verifies naming, no draft envelope/provenance metadata, `templates/issue/design.md`, and rendered canonical template content |
| tc-s06-003 | passed | same CLI test creates epic `draft-plan` and verifies naming, no draft envelope/provenance metadata, `templates/epic/plan.md`, and rendered canonical template content |
| tc-s06-004 | passed | `test_draft_doc_types_render_scope_specific_template_bodies` verifies full 3x3 scope-kind/template-source matrix across initiative / epic / issue and draft-requirement / draft-design / draft-plan |
| tc-s06-005 | passed | `test_draft_doc_types_render_scope_specific_template_bodies` verifies same-second suffix allocation for `draft-requirement` / `draft-design` / `draft-plan` in the same issue discussions directory |
| tc-s06-006 | passed | `test_validate_accepts_mixed_same_timestamp_unsuffixed_and_suffixed_slots` accepts draft filenames; `test_validate_rejects_malformed_discussion_doc_candidates` rejects malformed non-timestamp draft filenames; diff-guard accepts new and explicit existing draft updates while rejecting non-editable self-claims |
| tc-s06-007 | passed | CLI/runtime/tests verify dedicated draft template absence, fake discussion draft templates are not used, direct canonical template rendering, and canonical template frontmatter retention |

### S06 Test Contract Closure
| Command / Area | Result | Evidence |
|---|---|---|
| `tests.cli_runtime.test_new` + `tests.cli_runtime.test_runtime_new_doc_s09` | passed | 58 tests OK |
| `tests.cli_runtime.test_validate` + `tests.cli_runtime.test_delegated_authoring` | passed | 69 tests OK |
| `tests.test_init_update` | passed | 176 tests OK; provider/dogfooding mirror docs/templates/runtime parity included; draft discussion templates are asserted absent |
| QA/code-review hardening rerun | passed | 16 runtime new-doc tests OK; 42 delegated-authoring tests OK; 259 validate/new/init-update tests OK |
| repo-local workflow commands | passed | validate / sync / doctor / git diff --check OK; draft-template find/rg no matches |

### S06 Evidence Adoption Ledger
| ID | status | source_type | source | target | adoption rationale | evidence |
|---|---|---|---|---|---|---|
| EAL-S06-001 | superseded-corrected | discussion | `discussions/20260525t055851z-research-draft-artifact-template-command-analysis.md` | runtime `new doc`, discussion templates, rules docs, validation, diff-guard, tests | Earlier research selected a discussion-local envelope plus canonical template body; user clarification superseded that portion because draft-specific templates duplicate canonical templates | Corrected S06 implementation diff and Green verification above |
| EAL-S06-002 | adopted | user clarification / active docs | updated S06 requirement/design/plan | runtime `new doc`, docs/rules/templates README, validation, diff-guard, tests | `new doc draft-*` remains the extension point, but generated content comes directly from existing scope-specific canonical templates and no `templates/discussions/draft-*.md` files exist | Corrected S06 implementation diff, find/rg no matches, and Green verification above |
| EAL-S06-003 | adopted | qa-reviewer | full 3x3 template matrix / existing draft update / runtime parity coverage findings | tests for runtime new-doc, delegated-authoring diff-guard, init/update parity | The QA findings closed a real coverage gap in the S06 acceptance matrix and protected provider/dogfooding mirror parity for changed runtime files | dev-coder hardening diff and additional Green verification |
| EAL-S06-004 | adopted | code-reviewer | malformed hyphenated draft filename finding | validation runtime and tests | The finding exposed a real validation bug where non-timestamp hyphenated draft filenames were ignored instead of rejected | regression test failed before fix, then 259-test rerun passed |

### S06 Decision Ledger
| ID | decision | status | rationale | evidence |
|---|---|---|---|---|
| D-S06-001 | Keep `new doc draft-requirement` / `draft-design` / `draft-plan` as the command surface; do not add `new draft`. | adopted | The draft artifacts are discussion documents and should stay in the existing `new doc <type>` catalog. | requirement/design S06, command tests |
| D-S06-002 | Do not create `templates/discussions/draft-requirement.md`, `draft-design.md`, or `draft-plan.md`. | adopted | Separate draft templates would duplicate canonical requirement/design/plan templates and create two sources to maintain. | user clarification, EAL-S06-001, absence checks |
| D-S06-003 | Render S06 draft artifacts directly from existing `templates/{initiative,epic,issue}/{requirement,design,plan}.md` based on the target scope kind. | adopted | Initiative drafts must use initiative templates, epic drafts must use epic templates, and issue drafts must use issue templates. | runtime implementation, S06 Green verification |
| D-S06-004 | Do not add a discussion-local envelope or strip canonical template frontmatter for S06 command-created draft artifacts. | adopted | The file's draft status is represented by `discussions/` placement and `draft-*` filename; adding envelope metadata would reintroduce a duplicate schema. | user clarification, tests asserting no envelope metadata |
| D-S06-005 | Treat non-timestamp filenames beginning with known hyphenated draft doc types as malformed discussion doc filename candidates. | adopted | Without this, `draft-requirement-kickoff.md`-style files bypass validation even though they are visibly failed attempts at the new S06 doc types. | code-reviewer P2 finding, validation regression |

## 今後の推奨事項
- #119 を main へ merge した後、#128 を `main` へ retarget / rebase し、GitHub checks と Codex review を再確認する。
