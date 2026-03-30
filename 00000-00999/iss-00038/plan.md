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
- EC:
  - EC-001
  - EC-002
  - EC-003
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

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - split 後の issue ownership と close-out baseline が docs に固定される
  - closes:
    - なし（baseline / EC-003 support）
  - review gate:
    - spec review が requirement/design/plan を pass し、`iss-00040` との非重複が確認できる
- S02:
  - 観測可能な振る舞い:
    - targeted docs list が current contract 観点で close-out 可能だと示せる
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - docs diff または no-op parity evidence が report に残る
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

## 要件 ↔ ステップ対応
- AC-001 -> S02
- AC-002 -> S03
- AC-003 -> S04
- EC-001 -> S02
- EC-002 -> S03
- EC-003 -> S01, S04

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
  - S02 着手前に S01 の baseline 固定を report に記録する
  - S03 着手前に S02 の docs/evidence review を記録する
  - S04 着手前に S03 の close-out review を記録する
  - S04 完了後に final SG1/QG1 verdict を report に記録する

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
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

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
- expected tests:
  - なし
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
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — review targeted docs list
- purpose:
  - old local-only / sequential / index assumption の残存有無を確認する
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

#### step gate
- review:
  - RG1 docs/evidence review
- expected tests:
  - targeted docs diff / parity check
- report update:
  - `./spec-dock/active/issue/report.md`

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
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

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
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

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

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs
- 対応:
  - S02 で扱った targeted docs list を最終見直しし、provider-side と dogfooding 側の parity を再確認する
  - no-op だった場合も、その旨を report に残す

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00038` で更新した issue docs、report、必要時のみ targeted docs list
- required validation:
  - AC-001/002/003 の evidence が diff と report から追える
  - `iss-00040` 非重複が最終 diff 上でも保たれている
- reviewer approvals:
  - final SG1 spec review pass
  - final QG1 close-out review pass

## 未確定事項
- なし:
  - close-out の execution path は S01-S04 + S90 + S99 で固定する

## final exit contract
- AC/EC 達成:
  - targeted docs parity が確認済みである
  - `validate` / `sync` の成功結果がある
  - final spec review record が verdict=`pass` で残っている
- docs impact resolved:
  - targeted docs list の差分または no-op evidence が report にある
- final diff approved:
  - `iss-00040` 非重複を保ったまま reviewer pass を取得している
