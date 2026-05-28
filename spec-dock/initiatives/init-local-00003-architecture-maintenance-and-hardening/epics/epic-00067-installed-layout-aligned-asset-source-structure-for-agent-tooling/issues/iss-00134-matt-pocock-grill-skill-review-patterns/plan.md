---
種別: 実装計画書（Issue）
ID: "iss-00134"
タイトル: "Matt Pocock grill-style clarification workflow を spec-dock に取り込む"
関連GitHub: ["#134"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-28"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
derived_from:
  - "requirement.md"
  - "design.md"
  - "discussions/20260528t070322z-disc-deep-consultant-issue-planning-execution-split.md"
---

# iss-00134 Matt Pocock grill-style clarification workflow を spec-dock に取り込む — 実装計画

## 計画サマリー

この計画は、Matt Pocock `grill-me` / `grill-with-docs` の essence を、spec-dock の provider-side templates / docs / skill guidance に統合し、Issue planning と Issue execution の入口を分離するための実行契約である。

初期実装では新しい discussion doc type を追加しない。したがって runtime catalog は原則 read-only verification 対象とし、`interview` / `research` / `disc` / `adr` / canonical `report.md` の責務を既存 common template / workflow / skill guidance の中で再設計する。

実装はまだ開始しない。この plan は、将来の issue execution で `doc-writer` / `dev-coder` へ委任するための planned contract として扱う。

## この計画で満たす要件ID

- AC:
  - AC-001 source-grounded clarification
  - AC-002 one-question-at-a-time
  - AC-003 unanswered question sheet
  - AC-004 answered question completion
  - AC-005 artifact unit and synthesis
  - AC-006 promotion lifecycle
  - AC-007 role boundary
  - AC-008 canonical authoring mode
  - AC-009 clarification / analysis mode
  - AC-010 cleanup and simplification
  - AC-011 issue planning / execution interface separation
- EC:
  - EC-001 質問が local context で解ける
  - EC-002 回答が別の未確認事項を生む
  - EC-003 大きな判断が複数質問にまたがる
  - EC-004 専門 agent が追加確認を必要とする
  - EC-005 外部支援による artifact が存在する
  - EC-006 execution 中に planning gap が見つかる
- 制約:
  - 一問一答を agent-to-human question の標準にする。
  - formal `interview.md` と lightweight chat question の起動条件を分離する。
  - new doc type を増やさず、既存 common templates を再設計する。
  - canonical docs / `report.md` は main orchestrator authority とする。
  - `spec-dock-issue-planning` は requirement / design / plan authoring と fresh reviewer pass までを扱い、実装 / PR / finish を claim しない。
  - `spec-dock-issue-execution` は approved plan execution 専用とし、planning gap を見つけた場合は planning phase へ戻す。

## 依存関係から導く実装順序

依存関係の正本:

- `design.md` の `依存関係分析`
- `design.md` の `Module Dependency Diagram`
- `design.md` の `ディレクトリ / ファイル変更計画`

順序ルール:

- provider-side template contract を最初に固定する。
- catalog / rules docs は template contract に従う。
- workflow docs と skills は catalog / role boundary を参照する。
- tests は changed contract を固定するため、docs/templates/skills の後に更新する。
- dogfooding mirror は provider-side changes の後に検証する。

step 依存サマリー:

- S01:
  - 依存: requirement / design
  - unblock: S02, S03, S04, S05
  - 対象: `interview.md`
- S02:
  - 依存: S01 の lifecycle vocabulary
  - unblock: S03, S04, S05
  - 対象: `research.md`, `disc.md`, `adr.md`
- S03:
  - 依存: S01, S02
  - unblock: S04, S05, S06
  - 対象: template catalog / discussion rules
- S04:
  - 依存: S01, S02, S03
  - unblock: S05, S06
  - 対象: workflow docs / issue report template / installed skills
- S05:
  - 依存: S01-S04
  - unblock: S06, S99
  - 対象: tests
- S06:
  - 依存: S01-S05
  - unblock: S90, S99
  - 対象: dogfooding mirror / installed asset mirror

## マイルストーン一覧

- M01: common template contract 固定
  - 対象 step: S01, S02
  - 完了条件: `interview` / `research` / `disc` / `adr` の責務と frontmatter policy が design contract と一致し、new doc type を追加しない方針が保たれている。
- M02: workflow / skill guidance 固定
  - 対象 step: S03, S04
  - 完了条件: template catalog、discussion rules、workflow docs、installed skill guidance が、一問一答、orchestrator-owned question routing、source-grounding、external artifact evidence、Issue planning / execution 分離の同じ意味を共有している。
- M03: regression guard 固定
  - 対象 step: S05
  - 完了条件: changed shipped contracts と runtime catalog unchanged が targeted tests で固定されている。
- M04: dogfooding parity 固定
  - 対象 step: S06, S90
  - 完了条件: provider-side source、dogfooding mirror、root `.agents/skills` mirror の矛盾と stale guidance が解消されている。
- M99: issue-wide final gate
  - 対象 step: S99
  - 完了条件: closure ids、reviewer gates、validation commands、report evidence が実装完了後の issue finish 前条件を満たしている。

## ステップ一覧

- S01: `interview.md` を一問一答の正式質問シートへ再設計する。
- S02: `research.md` / `disc.md` / `adr.md` の source-grounding / synthesis / ADR triage 契約を再設計する。
- S03: template catalog と discussion rules を common template semantics に同期する。
- S04: workflow docs、issue report template、installed skill guidance を orchestrator-owned one-question workflow と Issue planning / execution 分離に揃える。
- S05: changed shipped contracts と runtime catalog unchanged を tests で固定する。
- S06: dogfooding scaffold mirror と root `.agents/skills` mirror を検証 / 必要時に同期する。
- S90: docs impact resolution / docs refresh を閉じる。
- S99: final quality gate を閉じる。

## 要件 -> ステップ対応

- AC-001 / EC-001 -> S02, S04, S05
- AC-002 -> S01, S04, S05
- AC-003 -> S01, S05
- AC-004 -> S01, S05
- AC-005 -> S02, S03, S05
- AC-006 -> S02, S03, S04
- AC-007 / EC-004 -> S04, S05
- AC-008 / AC-009 -> S03, S04
- AC-010 -> S01-S06, S90
- AC-011 -> S04, S05, S06
- EC-002 -> S01, S04, S05
- EC-003 -> S02, S03, S05
- EC-005 -> S03, S04, S05
- EC-006 -> S04, S05, S06

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | Step | Slice | Type | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S02/S04 | source-grounding | acceptance | AC-001, EC-001 | local context で解ける疑問は人間に聞かず、`research` / `disc` に source-grounding を残す | `research.md`, workflow docs, skills | source を読まずに質問する regression | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-002 | S01/S04 | one-question formal interview | acceptance | AC-002, AC-003, EC-002 | 重要質問は一問一答で、回答前に unanswered `interview.md` を作る | `interview.md`, workflow docs, skills | 複数質問を一括提示する regression | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-003 | S01 | answered interview completion | acceptance | AC-004 | 回答後は同一 `interview` artifact に回答、採用判断、含意を追記する | `interview.md` | 回答 record が別 file / chat のみになる regression | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-004 | S02/S03 | synthesis and promotion | acceptance | AC-005, AC-006, EC-003 | `disc.md` が synthesis / reflection proposal / ADR triage を扱い、`report.md` ledger と混同されない | `disc.md`, catalog docs | proposal と observed ledger の混同 | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-005 | S04 | specialist role boundary | acceptance | AC-007, EC-004 | 専門 agent は人間へ直接質問せず、質問候補を orchestrator へ返す | workflow docs, skills | specialist が直接ユーザー質問する regression | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-006 | S03/S04 | authoring modes and external evidence | acceptance | AC-008, AC-009, EC-005 | canonical authoring mode / analysis-only mode / external artifact evidence を分離し、外部支援 artifact は Evidence Adoption Ledger / Spec Authoring Gate で採否、target、evidence、next_action を追跡する | catalog docs, workflow docs, report guidance | external tool 操作を spec-dock 要件へ混入する regression / external evidence 採否が trace されない regression | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-007 | S01-S05 | cleanup and no new doc type | negative | AC-010, design D-001/D-003 | grill 専用 template variant、`reflection.md`、`new doc report` を追加しない | templates, runtime catalog, tests | template / catalog bloat | yes | inspect-only | report Step/Test/Closure Coverage |
| cl-008 | S06/S90/S99 | dogfooding parity | acceptance | design verification | provider-side assets と dogfooding mirror / root `.agents/skills` mirror が整合する | provider assets, `spec-dock/`, `.agents/skills` | shipped assets と dogfood の不一致 | yes | manual-required | report Step/Test/Closure Coverage |
| cl-009 | S04/S05/S06 | issue planning/execution split | acceptance | AC-011, EC-006 | `spec-dock-issue-planning` は Issue authoring と fresh reviewer pass まで、`spec-dock-issue-execution` は approved plan execution 以降に限定され、planning gap は planning phase return / blocked evidence へ route される | workflow_issue umbrella, workflow_issue_planning, workflow_issue_execution, issue report template, skills, tests | premature implementation / execution skill authoring misuse / missing Spec Authoring Gate handoff | yes | inspect-only | report Spec Authoring Gate / Step/Test/Closure Coverage |

## レビュー / QA ゲート方針

- S01-S04:
  - reviewer: `spec-reviewer`
  - focus: docs / template / skill text が requirement / design / plan と整合すること。
- S05:
  - reviewer: `code-reviewer`
  - focus: tests が changed contracts を正しく固定し、runtime behavior を意図せず変えていないこと。
- S06:
  - reviewer: `spec-reviewer`
  - focus: dogfooding mirror が provider-side source と矛盾しないこと。
  - code / runtime behavior の diff が出る場合は `code-reviewer` も必要。
- S90:
  - reviewer: `spec-reviewer`
  - focus: stale guidance / duplicate concept / docs impact が残っていないこと。
- S99:
  - reviewers: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`

## 実行ルール（全ステップ共通）

- 各 implementation step は `1 behavior slice / 1 review scope / 1 commit boundary` を標準とする。
- 親 orchestrator は orchestration / integration / report evidence / reviewer gate を所有し、実装作業は原則 `doc-writer` または `dev-coder` に委任する。
- Worker は `Ledger Note` または `No material implementation decisions beyond the approved plan.` を返す。
- 実行中に runtime catalog 変更、新 doc type 追加、scope 外 path 変更、追加 ADR 必要性が見つかった場合は、plan amendment と fresh spec review を行うまで停止する。
- Observed result は `report.md` に記録し、`plan.md` には追記しない。

## 共通 report evidence destinations

各 implementation step / inspection gate は、step-local な `report evidence` に加えて、次の `report.md` sections を必ず更新対象として扱う。

- Workflow Delegation Consent:
  - issue-scoped workflow delegation consent、named roles、boundary、expiry / invalidation、denied / unavailable handling。
- Implementation Delegation Gate:
  - step、delegation decision、required reason、delegated role、delegated scope、source of truth、allowed changes、forbidden changes、required verification、stop conditions、output required、observed result。
- Delegated Worker Evidence:
  - worker summary、changed files、tests or docs-only verification、reviewer verdict、unresolved risks、parent integration decision。
- Spec Interpretation / Decision Ledger:
  - worker の `Ledger Note` を orchestrator が採用 / 却下 / 昇格 / follow-up / no_action へ処理した結果。material decision がない場合は `No material interpretation changes.` と `No decision entries.` を記録する。
- Evidence Adoption Ledger:
  - delegated draft、reviewer finding、research、external support artifact、discussion evidence を canonical artifact / implementation decision へ取り込む場合の adoption_status、source、target、evidence、next_action。
- Spec Authoring Gate:
  - requirement / design / plan の phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes。
  - implementation start / issue execution handoff の前提として、fresh reviewer pass 済みであることを確認する。
- Step Contract Closure / Test Contract Closure / Closure Coverage:
  - plan の closure id、test id、observed evidence、result、approved-no-op の根拠。
- Reviewer Gate Status:
  - step reviewer / final reviewer の role、freshness、state、completion decision。
- Step Commit Gate:
  - committed / approved-no-op、commit scope、commit hash or final ledger reference、post-commit clean check、no-op rationale、checked contracts / files、diff-clean command、read-only confirmation。

## 実装ステップ

### 実装ステップ S01 - `interview.md` formal one-question sheet

- behavior goal:
  - 新規 `interview.md` template が、一問一答、未回答から回答済みへの completion、追加曖昧さ発生時の次 unanswered artifact 作成を表現する。
- design 参照:
  - `interface contract` の `interview.md`
  - `正式質問シートの起動条件`
- depends on:
  - requirement / design pass
- unblocks:
  - S02, S03, S04, S05
- target files:
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`

#### planned contract

- scope:
  - `interview.md` の frontmatter compatibility policy、formal question trigger、required sections、conditional PlantUML、answer/adoption fields を更新する。
  - frontmatter は既存 identity fields（`種別`、`ID`、`タイトル`、`状態`、`作成者`、`最終更新`、`親`、`関連`、`authority`、`derived_from`、`reflected_to`）を削除・rename せず維持する。
  - frontmatter / lifecycle fields は `scope`、`scope_id`、`created_at`、`created_by`、`status`、`authority`、`adoption_status`、`derived_from`、`reflected_to` を持つ。
  - `status` は `unanswered` / `answered` / `superseded` / `deferred`、`authority` は `proposed` / `user-approved` / `synthesized`、`adoption_status` は `unreviewed` / `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked` を扱う。
  - required body sections は、`位置づけ`、`質問の目的`、`質問`、source-grounded context、回答案、Codex の分析、Codex の推奨案、ユーザー回答、追加確認の要否、採用判断、requirement / design / plan / ADR への含意を持つ。
  - conditional body sections は、必要な場合だけ PlantUML 図、詳細 tradeoff、具体シナリオ / edge case、後続 reflection proposal を持てる。
- test obligation:
  - closure ids: `cl-002`, `cl-003`, `cl-007`
  - coverage rationale: 既存 template は複数質問ブロック前提であり、一問一答 workflow の中心 contract なので content assertion が必要。
- red / alternative evidence:
  - evidence level: inspect-only
  - pre-implementation evidence: 現 template に `質問ブロック（必要な数だけ繰り返す）` が存在することを確認する。
- green verification:
  - docs inspection of `interview.md`
  - S05 で `python -m unittest tests.test_init_update -v` により regression assertion を閉じる。
- refactor guardrail:
  - `research` / `disc` / `adr` の責務変更をこの step に混ぜない。
  - runtime catalog を変更しない。
- amendment trigger:
  - `interview` 以外の new doc type が必要になる場合。

#### delegation contract

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/phase_design.md`
  - target `interview.md` template listed in this step
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
- forbidden changes:
  - `spec-dock/active/**`
  - `src/spec_dock/assets/spec_dock/scripts/**`
  - tests
  - existing discussion artifacts
- acceptance criteria:
  - `cl-002`, `cl-003`, `cl-007`
- required verification:
  - docs-only inspection plus targeted template assertions when S05 runs.
- reviewer focus:
  - `spec-reviewer`
- stop conditions:
  - frontmatter compatibility policy cannot be represented without runtime changes.
  - new doc type appears necessary.
- output required:
  - changed files
  - verification result
  - unresolved risks
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s01-001` acceptance: `interview.md` is one-question formal sheet
  - 前提: provider-side `interview.md` template exists.
  - 操作: template content を inspection する。
  - 期待結果: 既存 identity fields（`種別`、`ID`、`タイトル`、`状態`、`作成者`、`最終更新`、`親`、`関連`、`authority`、`derived_from`、`reflected_to`）を削除・rename しない。
  - 期待結果: frontmatter / lifecycle fields として `scope`、`scope_id`、`created_at`、`created_by`、`status`、`authority`、`adoption_status`、`derived_from`、`reflected_to` を持つ。
  - 期待結果: `status` は `unanswered` / `answered` / `superseded` / `deferred`、`authority` は `proposed` / `user-approved` / `synthesized`、`adoption_status` は `unreviewed` / `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked` を扱える。
  - 期待結果: single `質問` section に加えて、`位置づけ`、`質問の目的`、source-grounded context、回答案、Codex の分析、Codex の推奨案、ユーザー回答、追加確認の要否、採用判断、requirement / design / plan / ADR への含意を持つ。
  - 期待結果: conditional body sections として、必要な場合だけ PlantUML 図、詳細 tradeoff、具体シナリオ / edge case、後続 reflection proposal を扱える。
  - 失敗検出: 複数質問ブロック前提が残り、一問一答 workflow と衝突する regression を検出する。
  - 検証方法: `tests/test_init_update.py` の template assertion。
  - 関連 closure id: `cl-002`, `cl-003`

- `tc-s01-002` negative: grill-specific variant is not introduced
  - 前提: template catalog に `interview.md` が存在する。
  - 操作: `src/spec_dock/assets/spec_dock/templates/discussions/` を確認する。
  - 期待結果: `grill-interview.md` や `reflection.md` は追加されない。
  - 失敗検出: 重複 template 増殖を検出する。
  - 検証方法: filesystem inspection / `rg --files` assertion.
  - 関連 closure id: `cl-007`

#### step closure contract

- closure id: `cl-002`, `cl-003`, `cl-007`
- close condition:
  - `interview.md` が one-question sheet として spec-reviewer pass を得る。
  - S05 の content assertion で regression が固定される。
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - 既存 multiple-question artifacts は grandfathered のため、自動移行は行わない。

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - pass condition: review_status: pass
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S01 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

### 実装ステップ S02 - `research` / `disc` / `adr` artifact semantics

- behavior goal:
  - source-grounding、synthesis、ADR sparing の記録先を common templates に固定する。
- target files:
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/adr.md`
- depends on:
  - S01 lifecycle vocabulary
- unblocks:
  - S03, S04, S05

#### planned contract

- scope:
  - `research.md`: facts / inference / unverified / terminology conflicts / edge cases / implications を分離する。
  - `disc.md`: 意思決定前の synthesis artifact として、対象論点、derived question sheets / research、synthesis、選択肢 / tradeoff、reflection proposal、ADR candidate triage、推奨反映先、未採用 / deferred 理由を持つ。
  - `disc.md` は adoption decision を直接確定する canonical ledger ではなく、複数質問 / research を束ねた proposal と反映候補を整理する。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
  - `adr.md`: durable decision と ADR sparing criteria を明確化する。
- test obligation:
  - closure ids: `cl-001`, `cl-004`, `cl-007`
- red / alternative evidence:
  - evidence level: inspect-only
  - pre-implementation evidence: 現 templates に terminology conflict / ADR sparing criteria が不足していることを確認する。
- green verification:
  - docs inspection
  - S05 で `python -m unittest tests.test_init_update -v` により regression assertion を閉じる。
- refactor guardrail:
  - `report.md` を discussion catalog に追加しない。
- amendment trigger:
  - `disc.md` と `report.md` の責務分離で不足し、独立 `reflection.md` が必要になる場合。

#### delegation contract

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - target templates listed in this step
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/adr.md`
- forbidden changes:
  - runtime catalog
  - `report.md` discussion template
  - canonical active docs
- acceptance criteria:
  - `cl-001`, `cl-004`, `cl-007`
- required verification:
  - docs-only inspection plus S05 tests.
- reviewer focus:
  - `spec-reviewer`
- stop conditions:
  - new doc type becomes necessary.
  - ADR criteria conflict with existing workflow ADR policy.
- output required:
  - changed files
  - verification result
  - unresolved risks
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s02-001` acceptance: `research.md` supports source-grounding
  - 前提: `research.md` template exists.
  - 操作: template sections を確認する。
  - 期待結果: sources、facts、inference、unverified、terminology conflict、edge case、implication が分離されている。
  - 失敗検出: 調査結果が推測や判断と混ざる regression を検出する。
  - 検証方法: `tests/test_init_update.py` content assertion.
  - 関連 closure id: `cl-001`

- `tc-s02-002` acceptance: `disc.md` owns synthesis and ADR triage
  - 前提: `disc.md` template exists.
  - 操作: template sections を確認する。
  - 期待結果: 対象論点、derived question sheets / research、synthesis、選択肢 / tradeoff、reflection proposal、ADR candidate triage、推奨反映先、未採用 / deferred 理由を持つ。
  - 期待結果: 複数質問にまたがる判断について、options、tradeoff、推奨反映先、未採用理由を整理できるが、issue `report.md` の observed evidence ledger として採否を確定しない。
  - 失敗検出: synthesis が issue `report.md` ledger に混入する regression、または未採用 / deferred 理由が残らず判断根拠が失われる regression を検出する。
  - 検証方法: `tests/test_init_update.py` content assertion.
  - 関連 closure id: `cl-004`

- `tc-s02-003` acceptance: `adr.md` records sparing criteria
  - 前提: `adr.md` template exists.
  - 操作: ADR criteria を確認する。
  - 期待結果: hard to reverse、surprising without context、real tradeoff、ADR 化しない場合の反映先を持つ。
  - 失敗検出: ADR candidate が濫発される guidance regression を検出する。
  - 検証方法: template inspection.
  - 関連 closure id: `cl-004`

#### step closure contract

- closure id: `cl-001`, `cl-004`, `cl-007`
- close condition:
  - templates が design contract と一致し、spec-reviewer pass を得る。
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - ADR candidate criteria の運用判断は reviewer と orchestrator の interpretation に依存する。

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - pass condition: review_status: pass
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S02 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

### 実装ステップ S03 - catalog and discussion rules alignment

- behavior goal:
  - template catalog / discussion rules が common template semantics、`report` 非 catalog、new doc type 非追加を明確にする。
- target files:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- depends on:
  - S01, S02
- unblocks:
  - S04, S05, S06

#### planned contract

- scope:
  - catalog description を `scratch` / `interview` / `research` / `disc` / `adr` / `draft-*` に保つ。
  - `report.md` は canonical observed ledger であり `new doc report` ではないと明記する。
  - existing multiple-question artifacts は grandfathered と明記する。
- test obligation:
  - closure ids: `cl-004`, `cl-006`, `cl-007`
- red / alternative evidence:
  - evidence level: inspect-only
  - pre-implementation evidence: README/rules に old semantics や不足説明があることを inspection する。
- green verification:
  - docs / catalog inspection
  - S05 で `python -m unittest tests.test_init_update -v` と `python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v` により regression assertion を閉じる。
- refactor guardrail:
  - `commands/new.py` / `create_node.py` / validation regex は変更しない。
- amendment trigger:
  - catalog 変更が必要になった場合。

#### delegation contract

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - target catalog / discussion rule docs listed in this step
- allowed paths:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- forbidden changes:
  - runtime catalog files
  - new template files
  - canonical active docs
- acceptance criteria:
  - `cl-004`, `cl-006`, `cl-007`
- required verification:
  - docs inspection and S05 tests.
- reviewer focus:
  - `spec-reviewer`
- stop conditions:
  - docs/rules cannot express design without catalog mutation.
- output required:
  - changed files
  - verification result
  - unresolved risks
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s03-001` negative: no new discussion catalog types
  - 前提: README/rules describe current discussion catalog.
  - 操作: catalog entries を確認する。
  - 期待結果: `report`, `reflection`, `grill-*` は new doc catalog に含まれない。
  - 失敗検出: runtime catalog と docs catalog が diverge する regression を検出する。
  - 検証方法: `tests/cli_runtime/test_runtime_new_doc_s09.py` and content inspection.
  - 関連 closure id: `cl-007`

- `tc-s03-002` acceptance: `report.md` is canonical ledger, not discussion doc
  - 前提: README/rules mention report handling.
  - 操作: report wording を確認する。
  - 期待結果: `report.md` は observed evidence ledger と説明され、`new doc report` と誤読されない。
  - 失敗検出: synthesis と evidence ledger の混同を検出する。
  - 検証方法: content assertion / spec-reviewer inspection.
  - 関連 closure id: `cl-004`, `cl-006`

#### step closure contract

- closure id: `cl-004`, `cl-006`, `cl-007`
- close condition:
  - catalog docs / rules docs が current runtime catalog と一致する。
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - future issue が `report` doc type を追加したい場合は別設計が必要。

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - pass condition: review_status: pass
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S03 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

### 実装ステップ S04 - workflow docs and installed skill guidance

- behavior goal:
  - workflow docs、issue report template、installed skills が、one-question-at-a-time、formal trigger、role boundary、external evidence handling、Issue planning / execution 分離を同じ意味で案内する。
- design trace:
  - `design.md` の `report.md` contract は、canonical report template / workflow guidance が Evidence Adoption Ledger と Spec Authoring Gate に discussion / external support artifact の採否、canonical docs 反映先、reviewer verdict、blocking / non-blocking、next action を記録すると定義している。
  - `design.md` の D-005 は、`spec-dock-issue-planning` を Issue authoring / Spec Authoring Gate entry とし、`spec-dock-issue-execution` を approved plan execution 以降に限定すると定義している。
  - S04 の report template 対象は issue `report.md` の Spec Authoring Gate handoff evidence に限定する。これを超える report template 構造変更、discussion catalog への `report` 追加、execution ledger の再設計が必要になった場合は design amendment と fresh spec review を行う。
- target files:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue_planning.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue_execution.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/issue/report.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/agents/spec-manager.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.github/agents/spec-manager.agent.md`
- depends on:
  - S01, S02, S03
- unblocks:
  - S05, S06

#### planned contract

- scope:
  - authoring workflow に formal question trigger / lightweight one-question boundary / escalation guardrail を追加する。
  - design workflow に source-grounding / terminology sharpening / edge-case clarification handoff を追加する。
  - `workflow_issue.md` は互換用 umbrella として残し、Issue planning と Issue execution の入口、handoff、scope 外を短く示す。
  - `workflow_issue_planning.md` は Issue 固有の requirement / design / plan authoring、grill 型 clarification、Spec Authoring Gate、planning-only stop conditions を扱う。
  - `workflow_issue_execution.md` は fresh reviewer pass 済み canonical docs と Spec Authoring Gate evidence を前提に、approved plan execution、report evidence、review loop、PR delivery、merge preparation、issue finish を扱う。
  - issue workflow / skills に specialist does not ask human directly の境界を同期する。
  - `spec-dock-issue-planning` は Issue authoring の入口として新設し、実装 edits、tests edits、PR 作成、merge-prepared、issue finish、implementation readiness claim を禁止する。
  - `spec-dock-issue-execution` は execution-only に狭め、requirement / design / plan authoring request を `spec-dock-issue-planning` へ route し、planning gap を見つけた場合は implementation continuation ではなく planning phase return / blocked evidence へ route する。
  - `spec-driven-tdd-workflow` は Issue planning と Issue execution を別 route として案内する。
  - Codex / Copilot adapter、bootstrap AGENTS、`execute-issue` prompt、Codex / GitHub role configs に残る旧 `workflow_issue.md` execution-policy 正本参照を `workflow_issue_planning.md` / `workflow_issue_execution.md` へ同期する。
  - issue `report.md` template に Spec Authoring Gate section を追加し、requirement / design / plan の phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes を記録できるようにする。
  - issue `plan.md` template に残る旧 `workflow_issue.md` execution-policy 正本参照を、`workflow_issue.md` umbrella、`workflow_issue_planning.md` authoring / planning、`workflow_issue_execution.md` execution / reviewer / completion policy へ同期する。
  - docs README / phase plan docs / issue plan authoring docs / reference docs に残る旧 `workflow_issue.md` execution-policy 正本参照を `workflow_issue_planning.md` / `workflow_issue_execution.md` へ同期する。
  - active-none issue report placeholder は canonical template ではないため、必要な場合だけ missing / stale previous reviewer pass の reference guidance を Spec Authoring Gate / reviewer evidence に同期する。
  - external support artifact は外部ツール固有の操作を spec-dock 要件へ入れず、issue report template / workflow guidance の Evidence Adoption Ledger / Spec Authoring Gate に adoption decision、target artifact / section、evidence、next_action を記録する guidance として扱う。
  - skills は concise reminder に留め、長い policy は docs へ route する。
- test obligation:
  - closure ids: `cl-001`, `cl-002`, `cl-005`, `cl-006`, `cl-007`, `cl-009`
- red / alternative evidence:
  - evidence level: inspect-only
  - pre-implementation evidence: existing docs/skills が one-question formal trigger を十分に持たないことを inspection する。
- green verification:
  - docs / skills inspection
  - S05 で `python -m unittest tests.test_init_update -v` により shipped skill / docs assertion を閉じる。
- refactor guardrail:
  - skill files に workflow docs の長い本文を複製しない。
  - direct user-question permission を specialist skills に追加しない。
  - runtime CLI command split / lifecycle state machine redesign / existing artifact auto migration / PR / finish lifecycle redesign を行わない。
- amendment trigger:
  - parent orchestrator direct implementation exception や delegation policy の変更が必要になる場合。

#### delegation contract

- delegated role: `doc-writer`
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - target workflow docs / issue report template / installed skills / role configs listed in this step
- allowed paths:
  - listed target files only
- forbidden changes:
  - implementation/runtime code
  - tests
  - unlisted `.github` / `.codex` files
  - secrets / `.env*`
- acceptance criteria:
  - `cl-001`, `cl-002`, `cl-005`, `cl-006`, `cl-007`, `cl-009`
- required verification:
  - docs inspection, skill inspection, S05 tests.
- reviewer focus:
  - `spec-reviewer`
- stop conditions:
  - workflow policy change beyond current requirement/design.
  - skill guidance would need to grant direct human questioning to specialists.
  - runtime CLI command split or lifecycle redesign becomes necessary.
- output required:
  - changed files
  - verification result
  - unresolved risks
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s04-001` acceptance: specialists route human questions through orchestrator
  - 前提: installed skill guidance exists.
  - 操作: system architect / implementation planner / issue execution guidance を確認する。
  - 期待結果: 専門 agent は質問候補を返し、人間へ直接質問しない。
  - 失敗検出: sub-agent が直接人間質問を許される regression を検出する。
  - 検証方法: content assertion / spec-reviewer inspection.
  - 関連 closure id: `cl-005`

- `tc-s04-002` acceptance: formal trigger and lightweight question boundary are documented
  - 前提: workflow authoring docs exist.
  - 操作: formal `interview.md` required conditions と lightweight chat conditions を確認する。
  - 期待結果: important decision は unanswered `interview.md`、軽微な確認は chat 上の一問でよいが、重要判断化したら formal lifecycle へ戻る。
  - 失敗検出: 実装者が独自に formal trigger を作る regression を検出する。
  - 検証方法: docs inspection.
  - 関連 closure id: `cl-002`

- `tc-s04-003` acceptance: external support artifacts use report adoption evidence
  - 前提: workflow authoring / issue workflow docs exist and issue `report.md` template owns Evidence Adoption Ledger / Spec Authoring Gate.
  - 操作: external support artifact の扱いを workflow docs、issue report template、report guidance で確認する。
  - 期待結果: 外部支援 artifact は通常 evidence として扱われ、Evidence Adoption Ledger / Spec Authoring Gate に adoption decision、target artifact / section、evidence、next_action を記録する。
  - 期待結果: 外部ツール固有の操作手順、責務、セッション管理は spec-dock の要件 / 設計 / workflow contract に混入しない。
  - 失敗検出: external artifact の採否が trace されない regression、または external tool 固有手順が spec-dock docs に混入する regression を検出する。
  - 検証方法: docs inspection / `tests.test_init_update` content assertion when feasible.
  - 関連 closure id: `cl-006`

- `tc-s04-004` acceptance: Issue planning and execution routes are separated
  - 前提: workflow docs and installed skill guidance exist.
  - 操作: `workflow_issue.md`、`workflow_issue_planning.md`、`workflow_issue_execution.md`、`spec-driven-tdd-workflow`、`spec-dock-issue-planning`、`spec-dock-issue-execution` を確認する。
  - 期待結果: `workflow_issue.md` は umbrella として planning / execution 入口と handoff を示す。
  - 期待結果: `spec-dock-issue-planning` は requirement / design / plan authoring と fresh reviewer pass までに限定され、実装 / PR / finish を claim しない。
  - 期待結果: `spec-dock-issue-execution` は approved plan execution 以降に限定され、planning request を planning skill へ route する。
  - 失敗検出: execution skill が authoring entry として残る regression、または planning skill が implementation readiness を claim する regression を検出する。
  - 検証方法: docs / skills inspection, S05 content assertion.
  - 関連 closure id: `cl-009`

- `tc-s04-005` acceptance: issue report template records Spec Authoring Gate handoff
  - 前提: issue `report.md` template exists.
  - 操作: issue report template sections を確認する。
  - 期待結果: `Spec Authoring Gate` section があり、phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes を記録できる。
  - 期待結果: execution 前に fresh reviewer pass 済み requirement / design / plan を確認できる。
  - 失敗検出: reviewer pass evidence が active issue 固有の report にだけ存在し、template から新規 issue へ継承されない regression を検出する。
  - 検証方法: template inspection, S05 content assertion.
  - 関連 closure id: `cl-009`

#### step closure contract

- closure id: `cl-001`, `cl-002`, `cl-005`, `cl-006`, `cl-007`, `cl-009`
- close condition:
  - docs / skills が design guardrails と一致し、spec-reviewer pass を得る。
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - skills は concise reminder なので、詳細 contract は docs に残る。

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - pass condition: review_status: pass
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S04 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

### 実装ステップ S05 - regression tests for shipped contracts

- behavior goal:
  - changed template / docs / skill contracts と runtime catalog unchanged を tests で固定する。
- target files:
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/harness.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/domain_runtime/test_delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
- depends on:
  - S01-S04
- unblocks:
  - S06, S99

#### planned contract

- scope:
  - template/content assertions を更新する。
  - Issue planning / execution workflow docs、new issue-planning skill、execution-only skill、hub routing、issue report Spec Authoring Gate の content assertions を追加する。
  - runtime discussion doc catalog が unchanged であることを regression として固定する。
  - managed skill catalog は `spec-dock-issue-planning` を install/update 管理対象へ追加する。これは shipped skill asset を consumer repo へ配布するための catalog-only 変更であり、discussion doc type / runtime command / lifecycle behavior の追加ではない。
  - `tests/cli_runtime/harness.py` は unsupported doc type regression の shared expectation を更新するためだけに変更できる。
  - delegated-authoring tests / contracts は、新しい `interview` / `disc` semantics と flat discussion draft / provenance / diff guard contract が矛盾しないことを必ず確認する。
  - delegated-authoring の production behavior 変更が不要な場合でも、approved-no-op evidence として確認した contracts / tests / diff-clean command を `report.md` に残す。
- test obligation:
  - closure ids: `cl-001` through `cl-009`
- red / alternative evidence:
  - `tc-s05-001`: `covered-existing`
  - `tc-s05-002`: `red-required`
  - `tc-s05-003`: `covered-existing`
  - `tc-s05-004`: `red-required`
  - pre-implementation evidence: `tc-s05-002` は old assertions が new template contract を検出できないことを確認する。`tc-s05-001` / `tc-s05-003` は既存 tests / contract inspection が対象 regression を検出できる根拠を記録する。
- green verification:
  - `python -m unittest tests.test_init_update -v`
  - `python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v`
  - `python -m unittest tests.domain_runtime.test_delegated_authoring -v`
  - `python -m unittest tests.cli_runtime.test_delegated_authoring -v`
- refactor guardrail:
  - production/runtime behavior を変更しない。ただし managed skill catalog への `spec-dock-issue-planning` 追加は、S04 で追加した shipped skill を install/update 対象へ反映する catalog-only 変更として許可する。
  - tests の期待値を実装に合わせて弱めない。
- amendment trigger:
  - discussion doc catalog / runtime command / lifecycle behavior mutation becomes necessary.

#### delegation contract

- delegated role: `dev-coder`
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - changed provider templates / docs / skills from S01-S04
  - target test files listed in this step
- allowed paths:
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/harness.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/domain_runtime/test_delegated_authoring.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
- forbidden changes:
  - provider docs/templates/skills
  - runtime code unless plan amendment approves
  - canonical docs
- acceptance criteria:
  - closure ids `cl-001` through `cl-009`
- required verification:
  - targeted unittest commands.
- reviewer focus:
  - `code-reviewer`
- stop conditions:
  - tests require product behavior changes not covered by design.
  - runtime catalog must change.
- output required:
  - changed files
  - commands run
  - failures and fixes
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s05-001` regression: runtime catalog remains unchanged
  - 前提: `new doc` runtime supports current catalog.
  - 操作: runtime new doc tests を実行する。
  - 証跡レベル: `covered-existing`
  - 期待結果: `scratch` / `interview` / `research` / `disc` / `adr` / `draft-*` は維持され、`report` / `reflection` は追加されない。
  - 失敗検出: accidental catalog expansion を検出する。
  - 検証方法: `python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v`
  - 関連 closure id: `cl-007`

- `tc-s05-002` regression: shipped templates expose new semantics
  - 前提: provider-side templates are updated by S01-S02.
  - 操作: init/update content assertions を実行する。
  - 証跡レベル: `red-required`
  - 期待結果: interview / research / disc / adr の required sections と `interview.md` full frontmatter / lifecycle / body / conditional field contract が test で確認される。
  - 期待結果: issue `report.md` template の `Spec Authoring Gate` fields が test で確認される。
  - 失敗検出: shipped wheel / scaffold から old template が出る regression を検出する。
  - 検証方法: `python -m unittest tests.test_init_update -v`
  - 関連 closure id: `cl-001`, `cl-002`, `cl-003`, `cl-004`, `cl-009`

- `tc-s05-003` regression: delegated-authoring compatibility remains intact
  - 前提: S02 で `disc.md` semantics、S04 で installed system-architect / implementation-planner skills が更新される。
  - 操作: delegated-authoring targeted tests と contract inspection を実行する。
  - 証跡レベル: `covered-existing`
  - 期待結果: flat discussion draft、lightweight provenance、`adoption_status: unreviewed`、`reflected_to: []`、diff guard contract が新しい `interview` / `disc` semantics と矛盾しない。
  - 期待結果: delegated authoring が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の single-writer authority を侵害しない。
  - 失敗検出: direct-write draft / provenance / diff guard と新 semantics が diverge する regression を検出する。
  - 変更不要の場合: tests / contract inspection を実行したうえで、production behavior update の approved-no-op evidence を `report.md` に残す。
  - 検証方法: `python -m unittest tests.domain_runtime.test_delegated_authoring -v`, `python -m unittest tests.cli_runtime.test_delegated_authoring -v`, contract inspection.
  - 関連 closure id: `cl-005`, `cl-006`, `cl-007`

- `tc-s05-004` regression: issue planning / execution split is shipped
  - 前提: S04 updates workflow docs and installed skills.
  - 操作: init/update content assertions を実行する。
  - 証跡レベル: `red-required`
  - 期待結果: `workflow_issue_planning.md` と `workflow_issue_execution.md` が shipped scaffold に含まれる。
  - 期待結果: `workflow_issue.md` が umbrella として planning / execution へ route する。
  - 期待結果: `spec-dock-issue-planning` skill が installed agent tooling に含まれ、requirement / design / plan authoring と fresh reviewer pass までに限定される。
  - 期待結果: `spec-dock-issue-execution` skill は execution-only で、planning request / planning gap を planning phase へ戻す。
  - 期待結果: `spec-driven-tdd-workflow` が Issue planning と Issue execution を別 route として案内する。
  - 失敗検出: shipped scaffold / installed skill から planning skill が欠落する regression、または execution skill が authoring entry として残る regression を検出する。
  - 検証方法: `python -m unittest tests.test_init_update -v`
  - 関連 closure id: `cl-009`

#### step closure contract

- closure id: `cl-001` through `cl-009`
- close condition:
  - targeted tests pass.
  - code-reviewer pass.
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - Full regression remains S99 responsibility.

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `code-reviewer`
  - pass condition: review_status: pass
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S05 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

### 実装ステップ S06 - dogfooding mirror and installed asset parity

- behavior goal:
  - provider-side shipped assets と dogfooding workspace / root installed skill mirror の整合を確認し、必要な mirrored outputs を同期する。
- target files:
  - `spec-dock/templates/**`
  - `spec-dock/docs/**`
  - `spec-dock/system/active-none/issue/report.md`
  - `.agents/skills/**`
  - `.codex/AGENTS.md`
  - `.codex/agents/spec-manager.toml`
  - `.codex/agents/spec-reviewer.toml`
  - `.codex/prompts/execute-issue.md`
  - `.github/agents/spec-manager.agent.md`
- depends on:
  - S01-S05
- unblocks:
  - S90, S99

#### planned contract

- scope:
  - provider-side changes を dogfooding scaffold mirror に反映 / 検証する。
  - installed agent-tooling mirror は root `.agents/skills/**`、root `.codex` entrypoints / role configs、root `.github/agents/spec-manager.agent.md` を対象とする。
  - dogfooding docs mirror では `workflow_issue.md` umbrella、`workflow_issue_planning.md`、`workflow_issue_execution.md`、issue `report.md` template が provider-side source と矛盾しないことを確認する。
  - root `.agents/skills/**` mirror では `spec-dock-issue-planning` の追加、`spec-dock-issue-execution` の execution-only 化、`spec-driven-tdd-workflow` の routing が provider-side source と矛盾しないことを確認する。
  - root `.codex` / `.github` installed mirror では role configs と execute prompt が `workflow_issue.md` umbrella、`workflow_issue_planning.md` authoring、`workflow_issue_execution.md` execution / reviewer / completion policy を正しく案内することを確認する。
  - `spec-dock/system/active-none/issue/report.md` は provider active-none placeholder の dogfooding mirror として同期できる。
- test obligation:
  - closure ids: `cl-008`, `cl-009`
- red / alternative evidence:
  - evidence level: manual-required
  - pre-implementation evidence: provider-side diff と dogfooding mirror の差分を確認する。
- green verification:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - targeted diff inspection
- refactor guardrail:
  - provider-side source changes をこの step で追加しない。
  - unlisted `.github` / `.codex` files と secrets は触らない。
- amendment trigger:
  - update/sync が runtime catalog mutation を要求する場合。

#### delegation contract

- delegated role:
  - `doc-writer` for docs/templates/skills mirror.
  - `dev-coder` only if scaffold/runtime behavior changes appear.
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - provider-side changed files from S01-S05
  - dogfooding mirror / root installed skill mirror target files listed in this step
- allowed paths:
  - `spec-dock/templates/**`
  - `spec-dock/docs/**`
  - `spec-dock/system/active-none/issue/report.md`
  - `.agents/skills/**`
  - `.codex/AGENTS.md`
  - `.codex/agents/spec-manager.toml`
  - `.codex/agents/spec-reviewer.toml`
  - `.codex/prompts/execute-issue.md`
  - `.github/agents/spec-manager.agent.md`
- forbidden changes:
  - `src/**` provider source changes
  - unlisted `.github/**`
  - unlisted `.codex/**`
  - `.env*`
  - unrelated dogfooding data
- acceptance criteria:
  - `cl-008`, `cl-009`
- required verification:
  - validate / sync / diff inspection.
- reviewer focus:
  - `spec-reviewer`; add `code-reviewer` if scaffold behavior changes.
- stop conditions:
  - sync modifies unexpected active issue state.
  - generated mirror diverges from provider source for unclear reasons.
- output required:
  - changed mirrored files
  - commands run
  - unresolved risks
  - Ledger Note or no material decision statement

#### 具体テストケース一覧

- `tc-s06-001` manual-required: dogfooding mirrors provider changes
  - 前提: S01-S05 are complete.
  - 操作: update/sync or documented mirror verification を行う。
  - 期待結果: `spec-dock/templates/**`, `spec-dock/docs/**`, `spec-dock/system/active-none/issue/report.md`, root `.agents/skills/**`, root `.codex` entrypoints / role configs、root `.github/agents/spec-manager.agent.md` が provider-side source と矛盾しない。
  - 期待結果: dogfooding mirror に Issue planning / execution docs と `spec-dock-issue-planning` skill が存在し、execution-only routing と Spec Authoring Gate handoff が provider-side source と一致する。
  - 失敗検出: local dogfooding workspace が stale guidance を保持する regression を検出する。
  - 検証方法: `./spec-dock/scripts/spec-dock validate`, `./spec-dock/scripts/spec-dock sync`, diff inspection.
  - 関連 closure id: `cl-008`, `cl-009`

#### step closure contract

- closure id: `cl-008`, `cl-009`
- close condition:
  - dogfooding mirror / installed skill mirror が provider-side changes と整合し、reviewer pass を得る。
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Reviewer Gate Status
- residual risk:
  - local dogfooding workspace may have unrelated existing changes; report must distinguish them.

#### step gate

- report update gate:
  - step reviewer / commit の前に、`report.md` の Step Contract Closure / Test Contract Closure / Closure Coverage / Reviewer Gate Status へ観測証跡を記録する。
- step reviewer gate:
  - reviewer: `spec-reviewer`
  - additional reviewer: `code-reviewer` if scaffold behavior changes
  - pass condition: required reviewer `review_status: pass`
- commit / no-op gate:
  - closure state: committed or approved-no-op
  - commit scope: S06 files only
  - approved-no-op の場合は、変更不要の理由、確認した契約 / ファイル、差分なし確認コマンド、read-only confirmation を `report.md` に残す。

## ドキュメント影響の解消ステップ S90

- behavior goal:
  - docs impact を明示的に解決し、stale multiple-question guidance、duplicate grill-specific artifact concept、outdated catalog text が残っていないことを確認する。
- target:
  - docs / templates / README / workflow / skill / migration notes
- owner:
  - parent orchestrator for inspect-only integration gate.
- depends on:
  - S01-S06
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - changed docs / templates / skills from S01-S06
- planned contract:
  - S90 は inspect-only gate であり、新規 file edit を行わない。
  - S01-S06 で触った docs/templates/skills と、関連 README / workflow / migration notes を横断 inspection する。
  - docs impact `none` は許可しない。今回の issue では docs impact が存在し、S90 は S01-S06 で解消済みかを確認する。
  - S90 inspection で新しい stale guidance、duplicate concept、missing docs update が見つかった場合は、S90 で直接編集せず、plan amendment または bounded follow-up implementation step を作成して fresh spec review を通す。
- delegation contract:
  - delegated role: N/A（inspect-only parent gate）
  - allowed paths for write: none
  - allowed paths for read: docs / templates / README / workflow / skill / migration notes
  - forbidden changes: all files
  - output required: inspected paths、stale guidance findings、amendment need、report evidence update
- 具体テストケース一覧:
  - `tc-s90-001` inspect-only: stale guidance cleanup resolved
    - 前提: S01-S06 are complete.
    - 操作: changed docs/templates/skills と関連 README / workflow / migration notes を inspection する。
    - 証跡レベル: `inspect-only`
    - 期待結果: 古い複数質問 guidance、grill 専用 duplicate concept、outdated catalog text、外部 tool 固有手順の混入、Issue planning / execution の古い一体型 guidance が残っていない。
    - 失敗検出: cleanup 不足、docs impact 漏れ、S01-S06 の範囲外編集が必要な状態を検出する。
    - 検証方法: docs diff inspection、`git diff --check`、`spec-reviewer` docs/spec alignment。
    - 関連 closure id: `cl-007`, `cl-008`, `cl-009`
- verification:
  - docs diff inspection
  - `git diff --check`
  - `spec-reviewer` docs/spec alignment
- amendment trigger:
  - S90 inspection で新規 file edit が必要になった場合。
  - S01-S06 の allowed paths を超える stale guidance が見つかった場合。
  - report / docs / skill guidance の meaning が requirement / design / plan と矛盾する場合。
- closure ids:
  - `cl-007`, `cl-008`, `cl-009`
- report evidence destination:
  - 共通 report evidence destinations
  - Reviewer Gate Status
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
- step gate:
  - report update gate:
    - inspection result、amendment need、approved-no-op rationale を `report.md` に記録する。
  - step reviewer gate:
    - reviewer: `spec-reviewer`
    - pass condition: review_status: pass
  - commit / no-op gate:
    - closure state: approved-no-op unless a plan amendment adds a bounded implementation step.
    - no-op evidence: inspected paths、diff-clean command、read-only confirmation を `report.md` に残す。

## 最終品質ゲートステップ S99

- behavior goal:
  - issue 全体が requirement / design / plan と一致し、実装前に定義した closure が全て閉じていることを確認する。
- depends on:
  - S01-S06, S90
- branch diff scope:
  - provider-side templates / docs / skills
  - tests
  - dogfooding mirror / root `.agents/skills` mirror
  - canonical issue docs / report evidence
- required validation:
  - `python -m unittest discover -v`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `git diff --check`
- final QA gate:
  - reviewer: `qa-reviewer`
  - scope: closure id coverage、missing high-value tests、integration test 要否
  - pass condition: reviewer pass
- final code review gate:
  - reviewer: issue-wide `code-reviewer`
  - scope: integrated diff、tests、runtime catalog unchanged、scaffold impact
  - pass condition: review_status: pass
- final spec review gate:
  - reviewer: final `spec-reviewer`
  - scope: requirement / design / plan / report / docs / templates / skills alignment
  - pass condition: review_status: pass
- final commit gate:
  - all implementation steps committed or valid approved-no-op.
  - final report ledger updated before final commit.
  - final commit hash and clean check recorded as external delivery evidence after commit.

## 未確定事項

なし。

design は fresh `spec-reviewer` pass 済みであり、plan 作成を妨げる未解決設計論点はない。

## 最終完了条件

- AC / EC:
  - `cl-001` through `cl-009` が report の Step Contract Closure / Test Contract Closure / Closure Coverage で pass または approved-no-op として閉じている。
- docs impact:
  - S90 が `spec-reviewer` pass で閉じている。
- implementation steps:
  - S01-S06 が committed または valid approved-no-op。
- final quality gate:
  - `qa-reviewer`: pass
  - issue-wide `code-reviewer`: pass
  - final `spec-reviewer`: pass
- validation:
  - `python -m unittest discover -v`: pass
  - `./spec-dock/scripts/spec-dock validate`: pass
  - `./spec-dock/scripts/spec-dock sync`: pass
  - `git diff --check`: pass
- final state:
  - unintended staged / unstaged changes がない。
  - PR delivery / merge preparation / issue finish は、実装完了後の execution workflow で扱う。
