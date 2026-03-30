---
種別: 実装計画書（Issue）
ID: "iss-00038"
タイトル: "Docs Dogfooding Parity and Final Regression Gate"
関連GitHub: ["#38"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00038 Docs Dogfooding Parity and Final Regression Gate — 実装計画（Execution Contract）

## この計画で満たす要件ID
- epic mapping:
  - `E-RQ-005`
  - `E-AC-005` docs/spec-review slice
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004
  - EC-005
  - EC-006
  - EC-007
  - EC-008
- 制約:
  - `iss-00040` と ownership を重複させない
  - provider-side と dogfooding docs の両方を対象にする
  - final spec review verdict を `pass` まで上げる
  - `iss-00040/report.md` に触る場合でも report-artifact normalization のみとし、implementation/test rerun を行わない

## 実施状況チェック
- [x] S01 close-out baseline and ownership lock
- [x] S02 targeted docs current-contract review / parity close-out
- [x] S03 generated-state review / final sync snapshot確認
- [x] S04 final spec review record / close-out bundle
- [x] S05 acceptance corrective close-out / report normalization
- [x] S06 corrective acceptance alignment / spec re-review
- [x] S07 dependency graph alignment
- [x] S08 committed audit-trail normalization
- [x] S09 epic status reconciliation and branch-diff rereview
- [x] S10 upstream evidence normalization
- [x] S11 final committed rereview closure
- [x] S12 narrow rules/docs-authority alignment
- [x] S90 docs impact resolution / docs refresh
- [x] S99 final diff review quality gate
- note:
  - 最新の committed branch diff を対象にした fresh final review cycle は、この S99 で閉じる

## マイルストーン一覧
- M1:
  - 対象:
    - close-out baseline と non-overlap boundary の固定
  - exit:
    - `iss-00038` の残責務が docs/spec-review slice のみであることを requirement/design/plan と report で説明できる
- M2:
  - 対象:
    - targeted docs parity の確認と必要差分の反映
  - exit:
    - docs diff または no-op parity evidence が揃う
- M3:
  - 対象:
    - `validate` / `sync` と generated state の close-out evidence
  - exit:
    - 両コマンドの成功結果と generated state review が揃う
- M4:
  - 対象:
    - final spec review record の完成
  - exit:
    - verdict=`pass` の review record が report に残る
- M5:
  - 対象:
    - acceptance review 指摘への corrective close-out
  - exit:
    - `report.md` front matter と S04 コミット記録が最終状態に正規化され、再 review で受け入れ可能と判断できる
- M6:
  - 対象:
    - epic-level branch diff review 指摘への corrective close-out
  - exit:
    - epic report / deps graph / corrective audit trail が branch diff review で矛盾なく辿れる
- M7:
  - 対象:
    - upstream evidence normalization と final committed rereview closure
  - exit:
    - `iss-00040/report.md` / `epic-00033/report.md` の rereview input ambiguity が解消し、normalized artifact set に対する epic-level committed rereview を含む fresh final rereview record が committed artifact として残る
- M8:
  - 対象:
    - post-S11 narrow rules/docs-authority alignment
  - exit:
    - `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の provider/dogfooding docs に残る stale `--no-github` guidance が GitHub-mandatory create contract に揃い、S02 original six-file verdict と区別して report から追える

## ステップ進捗サマリー
- [x] S01 close-out baseline and ownership lock
- [x] S02 targeted docs current-contract review / parity close-out
- [x] S03 generated-state review / final sync snapshot確認
- [x] S04 final spec review record / close-out bundle
- [x] S05 acceptance corrective close-out / report normalization
- [x] S06 corrective acceptance alignment / spec re-review
- [x] S07 dependency graph alignment
- [x] S08 committed audit-trail normalization
- [x] S09 epic status reconciliation and branch-diff rereview
- [x] S10 upstream evidence normalization
- [x] S11 final committed rereview closure
- [x] S12 narrow rules/docs-authority alignment
- [x] S13 canonical guidance test expectation realignment

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - split 後の issue ownership と close-out baseline が docs に固定される
  - closes:
    - なし（baseline / EC-003 support）
  - review gate:
    - `git --no-pager diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md` で baseline diff を観測できる
    - spec review が requirement/design/plan を pass し、`iss-00040` との非重複確認先を含む S01 承認記録が `report.md` に残る
- S02:
  - 観測可能な振る舞い:
    - targeted docs list が current contract 観点で close-out 可能だと、6 ファイル個別 evidence 付きで示せる
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - docs diff または no-op parity evidence に加え、6 ファイル個別の current contract verification evidence が report に残る
    - targeted docs list 外の stale assumption を見つけた場合は blocker と escalation が report に残る
- S03:
  - 観測可能な振る舞い:
    - `validate` / `sync` と generated state review が close-out evidence として成立する
  - closes:
    - AC-002
    - EC-002
  - review gate:
    - command outputs と state review が report に残る
- S04:
  - 観測可能な振る舞い:
    - upstream issue evidence を束ねた final spec review record が `pass` になる
  - closes:
    - AC-003
    - EC-003
  - review gate:
    - reviewer verdict=`pass`
- S05:
  - 観測可能な振る舞い:
    - acceptance review 指摘を受けて、`report.md` の final artifact が実 commit / approved 状態と整合する
  - closes:
    - EC-004
  - review gate:
    - `report.md` front matter の状態値が単一の確定値である
    - S04 のコミット記録が actual git history と矛盾しない
- S06:
  - 観測可能な振る舞い:
    - corrective close-out を反映した issue docs が再度 spec review で整合 pass する
  - closes:
    - AC-003
    - EC-004
  - review gate:
    - spec reviewer が corrective plan と issue docs の整合を `pass` と判定する
- S07:
  - 観測可能な振る舞い:
    - `iss-00040` prerequisite が narrative spec と `deps.json` / `spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` の両方で一致する
  - closes:
    - EC-006
  - review gate:
    - `iss-00038/deps.json` と `spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` が `iss-00040` prerequisite を反映する
    - per-node `nodes.iss-00038.deps` は readiness projection として扱い、closed issue prerequisite edge の不保持だけで mismatch 判定しない
    - `spec-dock/dashboard.md` が `todo_total: 0` の場合、active-only projection の空状態は許容される
- S08:
  - 観測可能な振る舞い:
    - branch diff review に使う corrective report/update が actual commit から追跡できる
  - closes:
    - EC-004
  - review gate:
    - `report.md` の S06 corrective log が committed audit trail と整合する
- S09:
  - 観測可能な振る舞い:
    - epic report / issue report / generated state / GitHub status の authority reconciliation execution evidence が揃い、epic close readiness rereview の前提を branch diff review で説明できる
  - closes:
    - EC-005
  - review gate:
    - epic-level spec review が committed branch diff を `pass` と判定する
- S10:
  - 観測可能な振る舞い:
    - final rereview が参照する upstream reports の provisional / conflicting evidence marker が、session chronology を保持したまま最小差分で正規化される
  - closes:
    - EC-003
    - EC-005
    - EC-008
  - review gate:
    - `epic-00033/report.md` の `#33` authority note が本文・例外メモ・generated state と単一結論で読める
    - `iss-00040/report.md` の normalization が report-artifact only であり、implementation/test rerun を伴っていない
    - `iss-00040/report.md` の normalization は authoritative citation layer / front matter / final summary note に限定され、historical session-log の time-scoped `コミット: なし` entry を rewrite していない
- S11:
  - 観測可能な振る舞い:
    - S09 execution evidence と S10 normalized upstream evidence を参照する fresh final rereview record が committed closure として残り、normalized artifact set に対する committed branch diff `main...HEAD` の epic-level rereview gate が `pass` として追える
  - closes:
    - AC-003
    - AC-004
    - EC-004
    - EC-007
  - review gate:
    - final spec reviewer が fresh final rereview を `pass` と判定する
    - `iss-00038/report.md` に reviewer / verdict / referenced evidence / actual commit hash を含む committed closure record が残る
    - normalized artifact set に対する committed branch diff `main...HEAD` の epic-level rereview gate `pass` が report から追える
- S12:
  - 観測可能な振る舞い:
    - final close-out rereview で見つかった `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の stale `--no-github` guidance が、GitHub-mandatory create contract に整合した wording へ是正される
  - closes:
    - AC-001
  - review gate:
    - provider-side / dogfooding 両側の `docs/rules/initiative/epics.md` が `workflow_epic.md` と矛盾しない
    - `report.md` に、これは original six-file targeted docs slice の broader scope reopening ではなく narrow rules/docs-authority corrective だと追記される
- S13:
  - 観測可能な振る舞い:
    - S12 corrective 後に stale `--no-github` guidance を期待していた canonical guidance tests が、current shipped docs contract を正本として pass する
  - closes:
    - AC-001
    - EC-009
  - review gate:
    - `tests/cli_runtime/test_wrappers.py` と `tests/test_init_update.py` の failing expectations が current docs wording に揃っている
    - docs contract rollback なしで targeted failing tests が pass する

## 要件 ↔ ステップ対応
- AC-001 -> S02, S12, S13
- AC-002 -> S03
- AC-003 -> S04, S11
- AC-004 -> S11
- EC-001 -> S02
- EC-002 -> S03
- EC-003 -> S01, S04, S10
- EC-004 -> S05, S06, S08, S11
- EC-005 -> S09, S10
- EC-006 -> S07
- EC-007 -> S11
- EC-008 -> S10
- EC-009 -> S13

## レビュー / QA ゲート方針
- SG1 spec review:
  - timing:
    - 実装着手前に requirement/design/plan を review し、pass まで修正する
    - S04 完了後に final spec review record 自体も確認する
  - scope:
    - ownership boundary
    - docs/spec-review slice への再定義
    - AC/EC と step の整合
- RG1 docs/evidence review:
  - timing:
    - S02 完了後
    - S03 完了後
  - scope:
    - targeted docs diff/no-op parity evidence の妥当性
    - command outputs と generated state review の妥当性
- QG1 close-out review:
  - timing:
    - S03 完了後
    - S04 完了後
  - scope:
    - close evidence の不足有無
    - epic close-out readiness
  - step approval loop:
  - SG1/spec review pass 前には execution に進まない
  - S02 着手前に S01 の baseline 固定について、観測コマンド結果または観測 artifact、reviewer、verdict、非重複確認先を report に記録する
  - S03 着手前に S02 の docs/evidence review を記録する
  - S04 着手前に S03 の close-out review を記録する
  - S04 完了後に final SG1/QG1 verdict を report に記録する
  - acceptance review で corrective findings が出た場合は、S05 で report artifact を正規化し、S06 で spec review pass を再取得してから受け入れ判定へ進む
  - epic-level branch diff review で authority / deps / audit trail finding が出た場合は、S07-S09 を追加 corrective path として実行し、S10 で upstream evidence normalization、S11 で fresh final rereview closure を完了してから epic completion を主張する
  - S11 後の final close-out rereview で `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の stale `--no-github` guidance が見つかった場合は、S02 original six-file verdict を broader claim に書き換えず、S12 で narrow rules/docs-authority corrective として append-only に閉じる
  - S12 corrective 後に canonical guidance tests が旧 `--no-github` wording を期待して fail した場合は、docs rollback ではなく S13 で test expectation realignment を行う
  - close-out は S10 で upstream evidence normalization、S11 で normalized artifact set に対する fresh final rereview closure、必要時のみ S12 で narrow rules/docs-authority corrective、さらに必要時のみ S13 で canonical guidance test expectation realignment を完了して初めて exit できる

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- `iss-00038` の close-out flow は S01-S11 を必須経路とし、S10/S11 を省略して S90 / S99 / final exit へ進まない。S12 は final close-out rereview で `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の rules/docs-authority mismatch が見つかった場合のみ追加で実行する。S13 は S12 corrective 後に canonical guidance tests が stale expectation で fail した場合のみ追加で実行する。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- `iss-00040` 完了済み scope を再度実行しない。もし upstream evidence 欠落が見つかった場合は、re-execute ではなく blocker として記録する。
- S02 で targeted docs list 外の stale old-contract assumption を見つけた場合は、その場で修正範囲を広げず step を停止し、path / assumption / scope外理由 / escalation 先を `report.md` に記録して reviewer 判断を待つ。
- acceptance review で report artifact の整合不備が見つかった場合は、runtime / docs contract へ波及させず、S05/S06 の corrective close-out として扱う。
- epic-level review で deps graph mismatch が見つかった場合は、spec narrative を弱めるのではなく、原則として machine-readable deps と generated artifacts を spec に合わせる。
- branch-diff review に使う corrective report/update は actual commit hash または真の no-op のどちらかで説明できなければ pass にしない。
- S08 では既存 S06 chronology を上書きせず、append-only の normalization record を追加する。S06 の `working tree`/`なし` 表記は履歴として残してよいが、S08 で superseded であることと actual authoritative commit を明記し、最終 authoritative artifact は S08 record を参照する。
- S09 は execution evidence 記録 step であり、fresh final rereview pass の代用にしない。close claim は S11 の committed closure record まで保留する。
- S10 で `iss-00040/report.md` を触る場合は report-artifact normalization only とし、code/test/runtime/dogfooding surface を変更しない。
- S10 では `epic-00033/report.md` の `#33` authority ambiguity を解消してから S11 へ進む。
- S10 で `iss-00040/report.md` を触る場合は authoritative citation layer / front matter / final summary note のみを正規化対象とし、historical session-log の `コミット: なし` entry が時点事実なら保持する。
- S10 完了後は、S11 で normalized artifact set に対する epic-level committed rereview を再度 `pass` させなければ close-out を完了できない。
- S11 後に `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の stale `--no-github` guidance が見つかった場合は、S02 の six-file no-op conclusion を rewrite せず、S12 で provider/dogfooding 両側の current create wording だけを GitHub-mandatory contract へ揃える。
- S13 では docs contract を再変更せず、`tests/cli_runtime/test_wrappers.py` と `tests/test_init_update.py` の canonical guidance assertions だけを current shipped wording に揃える。

## 実装ステップ

### S01 — close-out baseline and ownership lock
- target:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
- design refs:
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
  - `iss-00040` requirement / design / plan / report
- step boundary:
  - issue の残責務を docs close-out と final spec review に限定し、split 前の stale scope を除去する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — collect authoritative evidence
- purpose:
  - epic と upstream issue の正本から close-out baseline を固定する
- files:
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
  - `iss-00040` report

##### I1 — lock scope
- slice goal:
  - `iss-00040` との non-overlap を requirement/design/plan に反映する

###### Red
- failing test:
  - 該当なし
- expected failure:
  - split 前の stale scope が issue docs に残っている

###### Green
- minimum implementation:
  - issue spec docs を close-out owner 向けに更新する
- pass condition:
  - spec review へ出せる draft が揃う

###### Refactor
- cleanup target:
  - requirement/design/plan の用語統一
- invariants to keep green:
  - regression ownership を再導入しない

#### step gate
- review:
  - spec review pass
  - S01 承認記録（観測コマンドまたは観測 artifact / reviewer / verdict / 非重複確認先）が `report.md` にある
- expected tests:
  - `git --no-pager diff -- spec-dock/active/issue/requirement.md spec-dock/active/issue/design.md spec-dock/active/issue/plan.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S02 — targeted docs parity review and refresh
- target:
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_naming.md`
  - `spec-dock/docs/reference_sync.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/requirement.md`
- step boundary:
  - current contract に対する docs drift の有無を確定し、必要時のみ parity 修正する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — review targeted docs list
- purpose:
  - old local-only / sequential / index assumption の残存有無を 6 ファイル個別に確認する
- files:
  - targeted docs list 6 ファイル

##### I1 — parity baseline
- slice goal:
  - provider/dogfooding parity が no-op か、実差分修正が要るかを確定する

###### Red
- failing test:
  - `diff -q` 相当の比較
- expected failure:
  - drift があれば差分が出る

###### Green
- minimum implementation:
  - 必要差分のみ修正する。差分不要なら no-op evidence を記録する
- pass condition:
  - AC-001 を満たす evidence が揃う

###### Refactor
- cleanup target:
  - docs 文言の重複と表現ぶれ
- invariants to keep green:
  - provider-side と dogfooding 側の整合

##### I2 — current-contract verification
- slice goal:
  - parity の有無に関係なく、6 ファイルそれぞれで old assumption 不在を示す

###### Red
- failing test:
  - 6 ファイル個別レビュー表が欠けている状態
- expected failure:
  - parity no-op でも current-contract verification evidence がなく、AC-001 を閉じられない

###### Green
- minimum implementation:
  - `report.md` に 6 ファイル個別レビュー表（path / parity 結果 / local-only 不在 / sequential 不在 / index assumption 不在 / note）を残す
- pass condition:
  - parity だけではなく current-contract verification evidence まで揃う

###### Refactor
- cleanup target:
  - 6 ファイル個別レビュー表の表記揺れ
- invariants to keep green:
  - parity no-op の場合でも 6 ファイル個別 evidence を省略しない

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - targeted docs diff / parity check
  - 6 ファイル個別の current-contract verification review
- report update:
  - `./spec-dock/active/issue/report.md`

#### blocker rule
- trigger:
  - targeted docs list 外で stale old-contract assumption を見つけた場合
- action:
  - その場で修正対象を追加せず S02 を停止する
  - `report.md` に path / assumption / scope外理由 / reviewer への escalation を記録する
- exit:
  - reviewer が follow-up issue または別 scope judgment を返すまで S02 を pass にしない

### S03 — validate sync close-out evidence
- target:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `spec-dock/dashboard.md`
  - `spec-dock/.agent/index-all.json`
  - `spec-dock/.agent/index.json`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/report.md`
- step boundary:
  - close-out を current repo state と generated state の両面から確認する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — command execution
- purpose:
  - close-out に必要な runtime evidence を取得する
- files:
  - generated state files

##### I1 — command success and state review
- slice goal:
  - command success と issue readiness の整合を示す

###### Red
- failing test:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
- expected failure:
  - exit non-zero または generated state drift

###### Green
- minimum implementation:
  - drift があれば原因を修正し、なければ evidence を記録する
- pass condition:
  - AC-002 を満たす evidence が揃う

###### Refactor
- cleanup target:
  - report 上の command/evidence 表記の整理
- invariants to keep green:
  - epic report と generated state の整合

#### step gate
- review:
  - RG1 docs/evidence review
  - QG1 close-out review
- expected tests:
  - `validate`
  - `sync`
- report update:
  - `./spec-dock/active/issue/report.md`

### S04 — final spec review record
- target:
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/report.md`
  - upstream issue reports
- step boundary:
  - final verdict と evidence 参照、non-overlap check を 1 つの record にまとめる

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — assemble evidence index
- purpose:
  - reviewer が `E-AC-005` docs/spec-review slice を辿れるようにする
- files:
  - `spec-dock/active/issue/report.md`
  - upstream issue reports

##### I1 — verdict pass
- slice goal:
  - pass verdict を出せる材料を report に束ねる

###### Red
- failing test:
  - spec review
- expected failure:
  - evidence 欠落または ownership ambiguity

###### Green
- minimum implementation:
  - final spec review record を作成し、不足があれば補う
- pass condition:
  - AC-003 を満たす record が完成する

###### Refactor
- cleanup target:
  - evidence 参照順と verdict 記述
- invariants to keep green:
  - `iss-00040` scope を再実行 ownership にしない

#### step gate
- review:
  - final SG1 spec review
  - final QG1 close-out review
- expected tests:
  - review record inspection
- report update:
  - `./spec-dock/active/issue/report.md`

### S05 — report artifact normalization
- target:
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t053149z-disc-acceptance-review-findings-analysis.md`
- step boundary:
  - acceptance review で見つかった report artifact の不整合だけを最小差分で正規化する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] `./spec-dock/active/issue/report.md` の修正位置を決めた

#### B1 — normalize final state markers
- purpose:
  - final close-out record を actual git history / approved state に揃える
- files:
  - `spec-dock/active/issue/report.md`

##### I1 — front matter normalization
- slice goal:
  - `状態` を単一の確定値へ正規化する

###### Red
- failing test:
  - `report.md` front matter が `draft | approved` のような曖昧値のまま
- expected failure:
  - final artifact の状態が確定しない

###### Green
- minimum implementation:
  - `状態` を final 状態に更新する
- pass condition:
  - front matter が単一の確定値になる

###### Refactor
- cleanup target:
  - front matter の表記揺れ
- invariants to keep green:
  - requirement/design/plan の `approved` と矛盾しない

##### I2 — commit record normalization
- slice goal:
  - S04 記録のコミット状態を actual git history と揃える

###### Red
- failing test:
  - `report.md` に「未コミット」などの暫定表記が残っている
- expected failure:
  - git history と report artifact が矛盾する

###### Green
- minimum implementation:
  - actual commit hash または finalized state に更新する
- pass condition:
  - S04 記録が git history と整合する

###### Refactor
- cleanup target:
  - finalized wording の表記揺れ
- invariants to keep green:
  - commit message フォーマット自体は今回の corrective scope 外

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - `git log --oneline -n 3`
  - `rg -n '状態:|未コミット|commit は final review pass 後に実施予定' spec-dock/active/issue/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S06 — corrective acceptance alignment
- target:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t053149z-disc-acceptance-review-findings-analysis.md`
- step boundary:
  - corrective findings を反映した issue docs 一式が再 review で整合していることを確認する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] 再 review 対象と観点を整理した

#### B1 — rerun spec review
- purpose:
  - corrective close-out が requirement/design/plan/report と整合していることを再確認する
- files:
  - issue docs 一式

##### I1 — acceptance-focused rereview
- slice goal:
  - corrective findings が解消されたことを reviewer が判定できる状態にする

###### Red
- failing test:
  - spec review
- expected failure:
  - corrective step が docs と整合しない

###### Green
- minimum implementation:
  - 必要なら issue docs を微修正し、review pass を取得する
- pass condition:
  - corrective close-out に対する spec review が `pass`

###### Refactor
- cleanup target:
  - corrective step と final exit contract の表現揺れ
- invariants to keep green:
  - 既存 S01-S04 の完了記録は上書きせず、追加 corrective step として扱う

#### step gate
- review:
  - final SG1 spec review
- expected tests:
  - spec review record
- report update:
  - `./spec-dock/active/issue/report.md`

### S07 — dependency graph alignment
- target:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/deps.json`
  - `spec-dock/.agent/index-all.json`
  - `spec-dock/.agent/deps-issues.json`（`todo_total: 0` なら空でもよい）
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/issue/discussions/20260330t090200z-disc-deps-graph-and-readiness-alignment-analysis.md`
- step boundary:
  - `iss-00040` prerequisite を machine-readable deps と authoritative generated deps/status view に反映する。generated edge authority は `spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` とする

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] narrative prerequisite と generated edge の観測点を整理した

#### B1 — normalize deps contract
- purpose:
  - human docs と deps graph の prerequisite semantics を一致させる
- files:
  - `iss-00038/deps.json`
  - generated deps artifacts

##### I1 — add missing edge
- slice goal:
  - `iss-00038 -> iss-00040` prerequisite を `deps.json` と `index-all.json` の top-level `deps.issue_edges` authoritative view で追えるようにする

###### Red
- failing test:
  - `iss-00038/deps.json` と `spec-dock/.agent/index-all.json` の top-level `deps.issue_edges` prerequisite evidence が食い違う
- expected failure:
  - readiness semantics が narrative spec と矛盾する

###### Green
- minimum implementation:
  - `deps.json` を authoritative generated state と整合させ、必要な generated artifacts を再生成する。per-node `nodes.<id>.deps` は readiness projection として補助確認に留める
- pass condition:
  - EC-006 の mismatch が解消し、`todo_total: 0` 時の active-only projection 空状態を例外扱いできる

###### Refactor
- cleanup target:
  - dependency explanation の wording
- invariants to keep green:
  - `iss-00040` を ownership 再取得対象にはしない

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - `cat spec-dock/.../iss-00038/deps.json`
  - `rg -n 'issue_edges|iss-00038|iss-00040' spec-dock/.agent/index-all.json`
  - `rg -n 'todo_total' spec-dock/dashboard.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S08 — committed audit-trail normalization
- target:
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t090300z-disc-commit-backed-audit-trail-normalization-analysis.md`
- step boundary:
  - S06 corrective close-out を committed branch diff review の監査証跡へ正規化する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] corrective commit hash の観測点を決めた

#### B1 — replace working-tree-only evidence
- purpose:
  - branch-diff review で使える actual commit-backed artifact にする
- files:
  - `spec-dock/active/issue/report.md`

##### I1 — record actual corrective commit
- slice goal:
  - S06 chronology を保持したまま、S08 専用の normalization record で actual corrective commit を authoritative に追跡可能にする

###### Red
- failing test:
  - S06 commit 欄が `working tree` や `なし` のまま
- expected failure:
  - committed branch diff review の監査証跡として使えない

###### Green
- minimum implementation:
  - corrective report update を commit し、S06 を改変せずに S08 normalization record へその hash と `S06 working-tree note is superseded by this committed record` を記録する
- pass condition:
  - report corrective trail が actual commit から追え、監査時の authoritative reference が S08 record だと判定できる

###### Refactor
- cleanup target:
  - corrective step のコミット記録 wording
- invariants to keep green:
  - S06 の original fail/pass chronology は append-only で保持する
  - S06 の旧 `working tree`/`なし` wording は履歴としてのみ残し、最終 authoritative reference には使わない
  - 真の no-op でない限り `なし` を使わない

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - `git log --oneline -n 5`
  - `rg -n 'working tree|なし（working tree|未コミット' spec-dock/active/issue/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S09 — epic status reconciliation and branch-diff rereview
- target:
  - `spec-dock/active/epic/report.md`
  - `spec-dock/.agent/index.json`
  - `spec-dock/.agent/index-all.json`
  - `spec-dock/dashboard.md`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t090100z-disc-epic-close-status-reconciliation-analysis.md`
- step boundary:
  - epic close を主張できる authority reconciliation を完成させ、committed branch diff を再 review する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録した
- [x] status authority の優先順位と blocker 条件を確認した

#### B1 — reconcile status authorities
- purpose:
  - GitHub issue state / generated state / epic report / issue report を authority order に従って同じ結論へ収束させる
- files:
  - epic report
  - generated state artifacts
  - issue report

##### I1 — finalize epic close readiness
- slice goal:
  - `E-AC-005` と remaining-open summary を final authority に合わせる

###### Red
- failing test:
  - epic report が `Partial/open` のまま、または authority が相互に矛盾する
- expected failure:
  - branch diff review が epic completion を受け入れられない

###### Green
- minimum implementation:
  - GitHub issue state を先頭 authority とし、`sync --github` / generated state / epic report / issue report を順に一致させる
- pass condition:
  - AC-004 / EC-005 を満たす authority reconciliation evidence が揃い、fresh final re-review に引き渡せる

###### Refactor
- cleanup target:
  - `approved` と `closed` の記述分離
- invariants to keep green:
  - authority が open の間は epic close を宣言しない

#### step gate
- review:
  - epic-level spec review pass
- expected tests:
  - `./spec-dock/scripts/spec-dock sync --github`
  - `rg -n 'E-AC-005|iss-00038|open|Partial|Pass' spec-dock/active/epic/report.md spec-dock/.agent/index.json spec-dock/.agent/index-all.json spec-dock/dashboard.md spec-dock/active/issue/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S10 — upstream evidence normalization
- target:
  - `spec-dock/active/epic/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t174600z-disc-epic-report-33-open-closed-authority-mismatch-analysis.md`
  - `spec-dock/active/issue/discussions/20260330t174700z-disc-upstream-evidence-normalization-for-iss-00040-report-analysis.md`
- step boundary:
  - fresh final rereview の入力となる upstream reports の ambiguity を最小差分で正規化する。`iss-00040/report.md` に触る場合も report-artifact normalization のみで、authoritative citation layer / front matter / final summary note だけを整え、historical session-log chronology は保持したまま S11 の normalized artifact set を用意する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録する
- [x] upstream report ごとの ambiguity と normalization boundary を整理する

#### B1 — normalize upstream review inputs
- purpose:
  - final rereview が読む upstream evidence を単一解釈にする
- files:
  - epic report
  - `iss-00040/report.md`

##### I1 — normalize authority and status markers
- slice goal:
  - `#33` authority note と `iss-00040` provisional marker を rereview 用の artifact として読める形に揃える

###### Red
- failing test:
  - `rg -n '#33|OPEN|CLOSED' spec-dock/active/epic/report.md`
  - `rg -n '状態:|draft \\| approved|コミット: なし' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md`
- expected failure:
  - upstream evidence が final rereview input として曖昧

###### Green
- minimum implementation:
  - epic report と `iss-00040/report.md` を report-artifact normalization の範囲で整え、final rereview が引用すべき authoritative note を明確化する
- pass condition:
  - EC-003 / EC-005 / EC-008 の blocker が解消し、chronology-preserving な normalized artifact set が揃って S11 の epic-level rereview を開始できる

###### Refactor
- cleanup target:
  - upstream report 内の status wording と citation anchor
- invariants to keep green:
  - `iss-00040` の implementation / test / regression ownership は reopen しない
  - `iss-00040/report.md` の historical session-log chronology は保持し、time-scoped `コミット: なし` fact を rewrite しない

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - `rg -n '#33|OPEN|CLOSED' spec-dock/active/epic/report.md`
  - `rg -n '状態:|draft \\| approved|コミット: なし|最終|summary' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S11 — final committed rereview closure
- target:
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t174500z-disc-s09-final-rereview-record-closure-analysis.md`
  - `spec-dock/active/issue/discussions/20260330t174600z-disc-epic-report-33-open-closed-authority-mismatch-analysis.md`
  - `spec-dock/active/issue/discussions/20260330t174700z-disc-upstream-evidence-normalization-for-iss-00040-report-analysis.md`
- step boundary:
  - S09 execution evidence と S10 normalized upstream evidence を参照し、normalized artifact set に対する epic-level committed rereview を fresh final rereview の一部として実施し、committed closure record として確定する

#### update_plan（着手時に登録）
- [x] `update_plan` に step の作業単位を登録する
- [x] rereview で引用する evidence set と commit 観測点を整理する

#### B1 — capture fresh final rereview
- purpose:
  - latest blocker である final rereview record 欠落を、report 正本上の committed closure で解消する
- files:
  - `spec-dock/active/issue/report.md`

##### I1 — record final closure verdict
- slice goal:
  - reviewer / verdict / referenced normalized evidence / actual commit hash を含む rereview record を残す

###### Red
- failing test:
  - `rg -n 'fresh final re-review|S11|reviewer:|verdict:' spec-dock/active/issue/report.md`
- expected failure:
  - S09 execution evidence はあるが final closure record がない

###### Green
- minimum implementation:
  - fresh final rereview entry を追加し、S09 + S10 を引用した最終 verdict と commit-backed closure を記録する
- pass condition:
  - AC-003 / AC-004 / EC-004 / EC-007 を満たす committed closure record が完成し、normalized artifact set に対する epic-level rereview `pass` が追える

###### Refactor
- cleanup target:
  - rereview record の evidence ordering と wording
- invariants to keep green:
  - 既存 S09 execution evidence は rewrite せず、後段 closure record として追加する

#### step gate
- review:
  - final SG1 spec review
  - final QG1 close-out review
  - normalized artifact set に対する epic-level spec review pass
- expected tests:
  - `git log --oneline -n 5`
  - `rg -n 'fresh final re-review|S11|reviewer:|verdict:' spec-dock/active/issue/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`

### S12 — narrow rules/docs-authority alignment
- target:
  - `src/spec_dock/assets/spec_dock/docs/github.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md`
  - `spec-dock/docs/github.md`
  - `spec-dock/docs/workflow-tree.md`
  - `spec-dock/docs/rules/initiative/epics.md`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/docs/reference_github.md`
- step boundary:
  - final close-out rereview で見つかった `docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の stale `--no-github` guidance を、GitHub-mandatory create contract に整合させる。S02 original six-file verdict は履歴として保持し、broader docs reopening には広げない

#### B1 — align docs/rules entrypoint wording
- purpose:
  - rules/docs-authority mismatch を provider/dogfooding docs だけで閉じる
- files:
  - `src/spec_dock/assets/spec_dock/docs/github.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md`
  - `spec-dock/docs/github.md`
  - `spec-dock/docs/workflow-tree.md`
  - `spec-dock/docs/rules/initiative/epics.md`
  - `spec-dock/active/issue/report.md`

##### I1 — replace stale create command
- slice goal:
  - `reference_github.md` と矛盾する `--no-github` guidance を除去する

###### Red
- failing test:
  - `rg -n -- '--no-github' src/spec_dock/assets/spec_dock/docs/github.md src/spec_dock/assets/spec_dock/docs/workflow-tree.md src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md spec-dock/docs/github.md spec-dock/docs/workflow-tree.md spec-dock/docs/rules/initiative/epics.md`
- expected failure:
  - provider/dogfooding docs に stale `--no-github` guidance が残っている

###### Green
- minimum implementation:
  - provider/dogfooding 両側の `github.md` / `workflow-tree.md` / `rules/initiative/epics.md` を current create contract に揃える
  - `report.md` に、これは original six-file targeted docs slice の broader scope reopening ではなく narrow rules/docs-authority corrective だと記録する
- pass condition:
  - docs/rules set が GitHub-mandatory create contract と整合し、S02 original six-file conclusion と later corrective が区別して追える

###### Refactor
- cleanup target:
  - rules/docs-authority と issue close-out wording の整列
- invariants to keep green:
  - targeted docs list 6 ファイルの original verdict は rewrite しない
  - code/test/runtime scope へ広げない

#### step gate
- review:
  - RG1 docs/evidence review
  - final QG1 close-out review
- expected tests:
  - `rg -n -- '--no-github|current-repo Issue|Create command' src/spec_dock/assets/spec_dock/docs/github.md src/spec_dock/assets/spec_dock/docs/workflow-tree.md src/spec_dock/assets/spec_dock/docs/rules/initiative/epics.md spec-dock/docs/github.md spec-dock/docs/workflow-tree.md spec-dock/docs/rules/initiative/epics.md`
  - `rg -n 'original six-file|rules/docs-authority corrective|S12' spec-dock/active/issue/report.md`
- report update:
  - `./spec-dock/active/issue/report.md`
  - S12 の commit-backed traceability として `ba732ec` と `d018c86` の両方を記録する

### S13 — canonical guidance test expectation realignment
- target:
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/test_init_update.py`
  - `spec-dock/active/issue/report.md`
- design refs:
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/discussions/20260330t122947z-disc-s13-guidance-test-expectation-realignment-analysis.md`
- step boundary:
  - S12 で是正済みの current docs contract を正本とし、canonical guidance tests に残った旧 `--no-github` 期待値だけを最小 realignment する。docs/runtime contract 自体は再変更しない

#### B1 — update stale test oracle only
- purpose:
  - docs corrective を regression と誤判定している stale test oracle を閉じる
- files:
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/test_init_update.py`
  - `spec-dock/active/issue/report.md`

##### I1 — replace legacy epic create expectation
- slice goal:
  - initiative 配下 epic create guidance に対する旧 `--no-github` 期待値を current wording に揃える

###### Red
- failing test:
  - `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs tests.test_init_update.TestInitUpdate.test_current_guidance_documents_match_discussion_numbering_contract tests.test_init_update.TestInitUpdate.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set tests.test_init_update.TestInitUpdate.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set -v`
- expected failure:
  - canonical guidance tests が `docs/rules/initiative/epics.md` に旧 `--no-github` wording を期待して fail する

###### Green
- minimum implementation:
  - `tests/cli_runtime/test_wrappers.py` の expected command を current shipped wording に更新する
  - `tests/test_init_update.py` の canonical rules expectation を current shipped wording に更新し、`--no-github` は absent side で扱う
  - `report.md` に S13 corrective を追記する
- pass condition:
  - targeted failing tests が pass し、docs contract rollback を伴わない

###### Refactor
- cleanup target:
  - test oracle wording を canonical rules contract と一致させる
- invariants to keep green:
  - runtime/docs contract を再変更しない
  - S12 corrective の scope を broader docs reopening に広げない

#### step gate
- review:
  - RG1 docs/evidence review
  - QG1 close-out review
- expected tests:
  - `python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs tests.test_init_update.TestInitUpdate.test_current_guidance_documents_match_discussion_numbering_contract tests.test_init_update.TestInitUpdate.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set tests.test_init_update.TestInitUpdate.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set -v`
  - `python -m unittest discover -v`
- report update:
  - `./spec-dock/active/issue/report.md`
  - implementation self-review だけで完了扱いにせず、reviewer-recorded な RG1/QG1 verdict を残した後に S99 へ進む

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs
- 対応:
  - S02 で扱った targeted docs list を最終見直しし、provider-side と dogfooding 側の parity を再確認する
  - no-op だった場合も、その旨と 6 ファイル個別 current-contract verification 済みであることを report に残す

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00038` で更新した issue docs、report、deps graph corrective、epic status reconciliation 差分、upstream report normalization 差分、必要時のみ targeted docs list と `docs/rules/initiative/epics.md` pair
- required validation:
  - AC-001/002/003 の evidence が diff と report から追える
  - AC-004 の authority reconciliation が diff と generated artifacts から追える
  - `todo_total: 0` 時の active-only projection 空状態が `index-all.json` authority を覆していない
  - `iss-00040` 非重複が最終 diff 上でも保たれている
  - acceptance review で指摘された report artifact 整合不備が解消している
  - epic-level review で指摘された deps / audit trail / status authority 不整合が解消している
  - latest fresh review で指摘された S09 final rereview record 欠落、`#33` authority mismatch、`iss-00040/report.md` ambiguity が解消している
  - S12 の docs-authority corrective が `ba732ec` と `d018c86` の両 anchor から trace できる
  - S13 の RG1/QG1 reviewer evidence が `report.md` に残っている
- reviewer approvals:
  - final SG1 spec review pass
  - final QG1 close-out review pass
  - epic-level spec review pass
- report update:
  - `./spec-dock/active/issue/report.md` に committed S99 gate record を追記する

## 未確定事項
- なし:
  - close-out の execution path は S01-S04 + S05/S06 corrective path + S07-S09 epic corrective path + S10/S11 final normalization/rereview path + 必要時のみ S12 rules/docs-authority corrective + 必要時のみ S13 canonical guidance test expectation realignment + S90 + S99 で固定する

## final exit contract
- AC/EC 達成:
  - targeted docs parity が確認済みであり、6 ファイル個別の current-contract verification evidence がある
  - `validate` / `sync` の成功結果がある
  - final spec review record が verdict=`pass` で残っている
  - `report.md` front matter と S04 コミット記録が final 状態に正規化されている
  - `iss-00038/deps.json` と generated deps graph が `iss-00040` prerequisite を反映している
  - epic report / issue report / generated state / GitHub status の authority reconciliation が branch diff 上で説明できる
  - corrective report/update が committed audit trail から追える
  - S10 で正規化した `epic-00033/report.md` / `iss-00040/report.md` を含む normalized artifact set に対する epic-level committed rereview が `pass` であり、S11 の committed closure record から追える
  - final close-out rereview で rules/docs-authority mismatch が見つかった場合は、`docs/github.md` / `docs/workflow-tree.md` / `docs/rules/initiative/epics.md` の narrow corrective が report から追える
- docs impact resolved:
  - targeted docs list の差分または no-op evidence が report にある
  - S01 承認記録と S02 の 6 ファイル個別レビュー表が report から追える
- final diff approved:
  - `iss-00040` 非重複を保ったまま reviewer pass を取得している
  - S10/S11 と、必要時のみ S12/S13 を含む close-out 必須経路が完了している
