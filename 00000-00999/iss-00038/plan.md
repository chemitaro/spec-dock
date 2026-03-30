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
- 制約:
  - `iss-00040` と ownership を重複させない
  - provider-side と dogfooding docs の両方を対象にする
  - final spec review verdict を `pass` まで上げる

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
    - `iss-00040` prerequisite が narrative spec と `deps.json` / authoritative generated deps evidence の両方で一致する
  - closes:
    - EC-006
  - review gate:
    - `iss-00038/deps.json` と `spec-dock/.agent/index-all.json` が `iss-00040` prerequisite を反映する
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
    - epic report / issue report / generated state / GitHub status の authority reconciliation が完了し、epic close readiness を branch diff review で説明できる
  - closes:
    - AC-004
    - EC-005
  - review gate:
    - epic-level spec review が committed branch diff を `pass` と判定する

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S04
- AC-004 -> S09
- EC-001 -> S02
- EC-002 -> S03
- EC-003 -> S01, S04
- EC-004 -> S05, S06, S08
- EC-005 -> S09
- EC-006 -> S07

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
  - epic-level branch diff review で authority / deps / audit trail finding が出た場合は、S07-S09 を追加 corrective path として実行し、epic-level spec review pass を再取得してから epic completion を主張する

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
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- `iss-00040` 完了済み scope を再度実行しない。もし upstream evidence 欠落が見つかった場合は、re-execute ではなく blocker として記録する。
- S02 で targeted docs list 外の stale old-contract assumption を見つけた場合は、その場で修正範囲を広げず step を停止し、path / assumption / scope外理由 / escalation 先を `report.md` に記録して reviewer 判断を待つ。
- acceptance review で report artifact の整合不備が見つかった場合は、runtime / docs contract へ波及させず、S05/S06 の corrective close-out として扱う。
- epic-level review で deps graph mismatch が見つかった場合は、spec narrative を弱めるのではなく、原則として machine-readable deps と generated artifacts を spec に合わせる。
- branch-diff review に使う corrective report/update は actual commit hash または真の no-op のどちらかで説明できなければ pass にしない。
- S08 では既存 S06 chronology を上書きせず、append-only の normalization record を追加する。S06 の `working tree`/`なし` 表記は履歴として残してよいが、S08 で superseded であることと actual authoritative commit を明記し、最終 authoritative artifact は S08 record を参照する。

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
  - `iss-00040` prerequisite を machine-readable deps と authoritative generated deps/status view に反映する

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
  - `iss-00038 -> iss-00040` prerequisite を `deps.json` と `index-all.json` の authoritative view で追えるようにする

###### Red
- failing test:
  - `iss-00038/deps.json` と `spec-dock/.agent/index-all.json` の prerequisite evidence が食い違う
- expected failure:
  - readiness semantics が narrative spec と矛盾する

###### Green
- minimum implementation:
  - `deps.json` を authoritative generated state と整合させ、必要な generated artifacts を再生成する
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
  - `rg -n 'iss-00038|iss-00040' spec-dock/.agent/index-all.json`
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

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs
- 対応:
  - S02 で扱った targeted docs list を最終見直しし、provider-side と dogfooding 側の parity を再確認する
  - no-op だった場合も、その旨と 6 ファイル個別 current-contract verification 済みであることを report に残す

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00038` で更新した issue docs、report、deps graph corrective、epic status reconciliation 差分、必要時のみ targeted docs list
- required validation:
  - AC-001/002/003 の evidence が diff と report から追える
  - AC-004 の authority reconciliation が diff と generated artifacts から追える
  - `todo_total: 0` 時の active-only projection 空状態が `index-all.json` authority を覆していない
  - `iss-00040` 非重複が最終 diff 上でも保たれている
  - acceptance review で指摘された report artifact 整合不備が解消している
  - epic-level review で指摘された deps / audit trail / status authority 不整合が解消している
- reviewer approvals:
  - final SG1 spec review pass
  - final QG1 close-out review pass
  - epic-level spec review pass

## 未確定事項
- なし:
  - close-out の execution path は S01-S04 + S05/S06 corrective path + S07-S09 epic corrective path + S90 + S99 で固定する

## final exit contract
- AC/EC 達成:
  - targeted docs parity が確認済みであり、6 ファイル個別の current-contract verification evidence がある
  - `validate` / `sync` の成功結果がある
  - final spec review record が verdict=`pass` で残っている
  - `report.md` front matter と S04 コミット記録が final 状態に正規化されている
  - `iss-00038/deps.json` と generated deps graph が `iss-00040` prerequisite を反映している
  - epic report / issue report / generated state / GitHub status の authority reconciliation が branch diff 上で説明できる
  - corrective report/update が committed audit trail から追える
- docs impact resolved:
  - targeted docs list の差分または no-op evidence が report にある
  - S01 承認記録と S02 の 6 ファイル個別レビュー表が report から追える
- final diff approved:
  - `iss-00040` 非重複を保ったまま reviewer pass を取得している
