# 課題 execution ワークフロー（workflow: issue execution / Agent-Native TDD）

Issue の approved plan を実装・検証・送達する workflow です。
この文書は execution-only の正本です。Issue の requirement / design / plan authoring は [workflow_issue_planning.md](workflow_issue_planning.md) に戻してください。

対応 leaf skill:
- `.agents/skills/spec-dock-issue-execution/SKILL.md`

## 入場条件

- active issue が set され、対象 issue を確認できる。
- `requirement.md` / `design.md` / `plan.md` が fresh `spec-reviewer` pass 済みである。
- `report.md` の Spec Authoring Gate に、phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes が記録されている。
- Evidence Adoption Ledger に unresolved `blocked` / `stale` entry がない。
- `plan.md` が approved executable workflow contract / command queue として読める。

これらを満たさない場合、実装を開始せず [workflow_issue_planning.md](workflow_issue_planning.md) に戻す。

## 実行 contract

- 実装前に `requirement.md` / `design.md` / `plan.md` の整合を確認し、特に `design.md` の依存関係分析 / module dependency diagram / directory tree と `plan.md` の step 順が一致していることを確認する。
- 実装前に `workflow_spec_authoring.md` の requirement / design / plan gate がすべて pass し、`Spec Authoring Gate` evidence が `report.md` に残っていることを確認する。
- `plan.md` は planned executable workflow contract / command queue である。実行者は step を上から順に読み、各 step の behavior goal、planned obligation、Red または代替 evidence、implementation scope、Green verification、refactor guardrail、closure requirements、report evidence destination、amendment trigger に従って作業する。
- `report.md` は observed evidence ledger である。実際の Red / Green / Refactor evidence / 結果、verification result、discovered tests、closure delta、reviewer verdict、commit/no-op evidence は `report.md` に記録し、`plan.md` を実行結果の正本にしない。
- Sub-agent-created discussion draft は lightweight provenance として `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []`、`diff_guard_result`、adoption ledger note を持つ。task manifest / profile / probe / session hash fields は標準 delegated draft evidence として要求しない。
- Delegated authoring output filenames は既存 discussion rules に従う。標準は `<ts>-<kind>-<slug>.md`、same-second collisions は `<ts>-<nn>-<kind>-<slug>.md` とする。新規 delegated run は per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を作らない。
- Historical `iss-00126` delegated-authoring manifest/Profile/probe/session artifacts は grandfathered evidence である。current standard が scope-local flat discussion drafts を使うことだけを理由に削除、rename、validation failure 化しない。
- `report.md` の仕様解釈 / 判断台帳（`Spec Interpretation / Decision Ledger`）は実行中判断の audit trail であり、planned contract の正本ではない。report に durable decision が残った場合は、completion 前に canonical artifact への promotion、follow-up 化、または issue-local disposition の evidence を残す。

## 親エージェント不変条件（Parent Agent Invariant）

- normal execution における親 Codex は inspect / plan / delegate / verify / integrate / report を担当する orchestration owner であり、code / runtime / tests / scaffold behavior / templates / shipped docs / skills / workflow text の直接実装者ではない。
- 親 Codex が直接作成・更新してよいのは、`report.md`、handoff note、phase evidence など run-local orchestration metadata に限定する。shipped docs / templates / skills / workflow text、runtime-facing scaffold、コード、テスト、runtime behavior は delegated worker work として扱う。
- 親 Codex が例外的に直接実装する場合は `Parent Implementation Exception` として、delegation 不可理由、user approval、allowed files、allowed operation、rollback plan、post-change verification、reviewer gate を事前に記録する。`approved-local-execution` はこの exception record を満たす場合だけ使用し、小さい変更、機械的変更、親が修正を知っていることを理由にした無記録 direct implementation として扱ってはならない。

## ステップ実行順序（step execution cadence）

- 各 implementation step は `step closure contract`（step クロージャ契約）→ implementation delegation decision → bounded implementation batch → verification → refactor/tidy → report draft update → step reviewer gate → fix → re-review → commit → clean確認 の順で進める。
- 完成版 `plan.md` には仕様固定クロージャ索引（`Spec-Locked Closure Index`）を置き、各 behavior slice の仕様ロックと closure owner step を実装前に固定する。
- 仕様固定クロージャ索引（`Spec-Locked Closure Index`）は Issue 全体のテストケース一覧や詳細なテスト実装指示ではなく、観測可能な入力・状態・locked expectation・防ぐ欠陥クラス・required/evidence level を固定する coverage ledger である。
- step クロージャ契約（`step closure contract`）は closure index の `id` を参照し、どの検証契約をその step で満たせば close してよいかを追えるようにする。
- 実装開始前に required closure id が step-local close condition と verification command または evidence path へ追跡できることを確認する。field semantics、card schema、risk-calibrated obligation coverage の詳細は [authoring/issue-plan.md](authoring/issue-plan.md) を正本にする。
- required closure row、`locked expectation`、`required`、`spec link` を変更する場合は plan amendment と re-review を先に通す。
- `pre-implementation evidence` は expected red / characterization pass / test sensitivity evidence のいずれかを記録し、failing-first を完全要求できない場合もテストが欠陥を検出できる根拠を残す。
- plan field semantics、`具体テストケース一覧` の card schema、docs-only / inspect-only / manual-required の書き方は [authoring/issue-plan.md](authoring/issue-plan.md) を正本にする。この workflow は lifecycle、実行順、reviewer gate、completion policy を所有し、field-level template manual を再定義しない。
- `bounded implementation batch` は step の scope、allowed files、forbidden scope に収まる最小実装単位とする。
- `refactor/tidy` は verification 後の bounded decision point とし、plan では詳細 task を事前確定しない。
- step 順は `design.md` の依存関係分析、module dependency diagram、directory / file change plan を根拠に、upstream / prerequisite から downstream へ組む。
- cleanup が既知で大きい場合は `bounded implementation batch` / design / 別 step へ切り出す。
- `1 step = 1 つの観測可能な振る舞い` を原則にし、各 step に観測用の 1 本のコマンドを置く。
- `plan.md` では agent-native TDD cycle を step / block / behavior slice に埋め込み、配置ルールは `phase_plan_issue.md` に従う。
- 各 step は step result approval を得てから次へ進む。

## 実装委任ゲート（Implementation Delegation Gate）

- `Implementation Delegation Gate` は各 implementation step の開始前に必ず置く。
- runtime / CLI / infra / code / tests / scaffold behavior は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` を primary delegated worker とする。
- step が複数 layer / module / package にまたがる、runtime / CLI / infra / templates / shipped scaffold / shared docs に影響する、既存 pattern 調査や影響範囲分析が必要、integration test / migration / backward compatibility / filesystem / GitHub / active state に関わる、または独立 worker scope に分割できる大きさの場合は、適切なサブエージェント利用を必須にする。
- delegated worker handoff には、`delegated role`、`scope`、`source of truth`、`allowed changes`、`forbidden changes`、`required verification`、`stop conditions`、`output required` を必ず含める。
- 複数 layer / package / shipped asset にまたがる step は、親 Codex が direct implementation せず、allowed paths と dependency boundary を明記して委任する。
- `delegated` の場合は delegated role、scope、source of truth、allowed changes、forbidden changes、required verification、stop conditions、output required、worker summary、changed files、verification result、unresolved risks、取り込み結果を `report.md` に残す。
- delegated worker の output には `Ledger Note` または `No material implementation decisions beyond the approved plan.` を含める。orchestrator は worker note を accepted decision として扱わず、report decision ledger へ採用 / 却下 / 保留 / 昇格するかを明示する。

## レビュアーゲート対応（reviewer gate mapping）

- reviewer gate state は `passed` / `failed` / `unavailable` / `denied` / `waived` / `provisional` のいずれかで記録する。required reviewer gate を満たすのは fresh `passed` だけである。
- `waived` はユーザーの明示的 risk acceptance が `report.md` にある場合だけ許可する。waiver は reviewer pass ではなく、delegation / reviewer gate の unavailable / denied を degraded success にしない。waiver 後に親 Codex が直接実装する場合も、別途 `Parent Implementation Exception` の user approval、allowed files、allowed operation、rollback plan、post-change verification、reviewer gate を必要とする。
- サブエージェント機能が利用できない、拒否された、または host policy と衝突する場合、required delegation / reviewer gate は `unavailable` / `denied` として blocked / 未完了に分類する。unavailable / denied / host conflict は degraded success でも、親 Codex の direct implementation 自動承認でもない。degraded mode は status/context gathering や追加 verification に限定し、reviewer gate、implementation readiness、最終品質ゲート（final quality gate）を満たさない。
- review / QA / spec の各 stage gate は `pass` まで回す。
- reviewer gate mapping は step の変更種別で決める。code / runtime / tests / scaffold behavior を含む step は per-step `code-reviewer` pass を必要とし、docs-only / template-only / skill-text-only step は `spec-reviewer` docs/spec alignment pass を必要とする。両方を含む場合は step を分割するか、両方の reviewer focus を明記して必要な gate を通す。
- implementation delegation は reviewer gate の代替ではない。`dev-coder` / `doc-writer` などの worker が実作業した場合でも、step diff は上記 mapping に従う reviewer pass を得る。
- reviewer が `fail` を返した場合、親 Codex は原則として自分で direct fix せず、指摘を bounded delegated follow-up として同じ delegated worker または適切な worker に再委任する。親 Codex が直接修正するには `Parent Implementation Exception` を別途満たす。

## ステップ commit ゲート（step commit gate）

- `1 implementation step = 1 review scope = 1 commit` を標準とし、複数 step の変更を 1 commit に混ぜてはならない。step が大きすぎる場合は commit をまとめず step を分割する。
- step commit 後は `git status --short` などで、次 step へ持ち越す意図しない staged / unstaged 変更がないことを確認する。
- step の close state は `committed` または `approved-no-op` のどちらかにする。`approved-no-op` は差分が本当にない場合だけ許可し、小さい変更、あとでまとめる、report だけ、時間不足を理由にしてはならない。
- `approved-no-op` には対象 step、変更不要の理由、確認した契約やファイル、差分なし確認コマンド、review 不要または read-only 確認の根拠を `report.md` に残す。

## 最終品質ゲート（final quality gate）

- 最終品質ゲート（final quality gate）の前に `S90 docs 影響解決 / docs 更新（S90 docs impact resolution / docs refresh）` を必ず置く。
- docs impact `none` は、docs / templates / README / workflow / skill / migration notes を確認し、更新不要の根拠と `spec-reviewer` の docs/spec alignment 結果を `report.md` に記録した場合だけ使える。
- 更新が必要な場合は `doc-writer` が対象 docs を更新し、`spec-reviewer` が docs と requirement / design / plan の整合を確認する。
- `S99 最終品質ゲート（S99 final quality gate）` は独立 step にし、final review だけで step review を代替してはならない。
- `S99 最終品質ゲート（S99 final quality gate）` では、`qa-reviewer` がテスト十分性と issue 全体を達成する integration test の要否を確認し、必要な integration test が不足していれば追加を要求する。
- `S99 最終品質ゲート（S99 final quality gate）` では、`code-reviewer` が issue 全体の統合 diff を俯瞰し、構造、責務、回帰リスク、保守性を確認する。
- `S99 最終品質ゲート（S99 final quality gate）` では、`spec-reviewer` が requirement / design / plan / report、実装、テスト、docs が一致し、全要件を満たしているか確認する。
- `qa-reviewer` / issue-wide `code-reviewer` / `spec-reviewer` のいずれかが `fail` の場合は修正し、該当 reviewer を再実行して `pass` まで回す。
- 三者すべての final gate が `pass` した後、final report ledger に各 step の closure、三者 final review、final commit scope、post-commit external evidence の記録先を更新し、final commit を作成する。final commit の hash と clean check は final commit 後にしか確定できないため、committed `report.md` 内の必須記録ではなく、最終応答、PR、issue comment などの external delivery evidence として残す。

## planning gap handling

Execution 中に次のいずれかを見つけた場合は、実装継続ではなく planning phase へ戻す。

- requirement / design / plan の不足または矛盾。
- stale / missing / failed reviewer pass。
- Spec Authoring Gate evidence の欠落。
- unresolved 仕様判断、scope / non-scope uncertainty、acceptance criteria gap。
- current plan の amendment trigger に該当する発見。

戻す場合は `report.md` に reason、影響 step、必要な planning phase、next action を記録する。

## report evidence

`report.md` には少なくとも次を残す。

- Spec Interpretation / Decision Ledger
- Evidence Adoption Ledger
- Workflow Delegation Consent
- Implementation Delegation Gate
- Delegated Worker Evidence
- Step Contract Closure
- Test Contract Closure
- Closure Coverage
- Reviewer Gate Status
- Step Commit Gate
- PR Delivery Gate
- Merge Preparation Gate
- Final QA Gate
- Final Code Review Gate
- Final Spec Review Gate
- Final Commit

Material な仕様解釈、plan 逸脱、tradeoff、open question、follow-up がある場合は `Ledger Note` を canonical report ledger へ統合する。Material decision がない worker output は `No material implementation decisions beyond the approved plan.` と明示する。

## PR / finish

- Final commit gates 後、`issue finish` の前に PR Delivery Gate と Merge Preparation Gate を通す。
- `issue finish` は lifecycle-only command であり、PR 作成、merge readiness、checks、review、final delivery completion を保証しない。
- `issue finish` 前に active issue を確認できる状態で、required validation、review、PR / merge-preparation evidence を `report.md` に残す。
- 完了条件を満たせない状態は `blocked` または `未完了` として扱い、成功報告をしない。

## 仕上げ

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```
