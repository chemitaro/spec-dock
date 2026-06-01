---
種別: 要件定義書（Issue）
ID: "iss-00149"
タイトル: "Issue finish synthetic approval closeout bug"
関連GitHub: ["#149"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-01"
親: ["epic-00080", "init-00079"]
---

# iss-00149 Issue finish synthetic approval closeout bug — 要件定義（WHAT / WHY）

## 目的
- `issue start` で開始した通常 issue を、PR merge / GitHub issue close 後に、手動 `spec-dock/.agent/active.json` 編集なしで公式 CLI path から `issue finish` できるようにする。
- synthetic active selection と lifecycle approval の区別は維持しつつ、synthetic state から finish 可能な lifecycle-approved state へ到達する supported transition を提供する。
- `issue finish` が fail-closed する場合は、operator が次に実行すべき公式 recovery path を理解できる error guidance を返す。

## 背景・現状
- 現状の挙動:
  - `./spec-dock/scripts/spec-dock issue start <issue>` は active manifest entry に `authority=approved`、全 grants、`promotion_record.promotion_decision=runtime_active_selection` を設定する。
  - `./spec-dock/scripts/spec-dock issue finish` は GitHub close / active clear の前に active issue entry の lifecycle authority gate を評価する。
  - authority gate は `implementation_start`、`issue_ready`、`issue_finish`、`phase_completion` に対して `runtime_active_selection` を `active_synthetic_approval_not_lifecycle_approval` として拒否する。
  - 現在の `spec-dock/active/context-pack.md` でも active initiative / epic / issue に `downstream_block=active_synthetic_approval_not_lifecycle_approval` が出ている。
- 現状の課題:
  - `workflow_issue.md` は primary path を `issue start` -> `issue finish` としているが、`issue start` 由来の active state を `issue finish` が拒否するため、通常 closeout が完結しない。
  - GitHub issue / PR / checks が問題ない状態でも、local active authority state が原因で active clear まで進めない。
  - 既存 workaround は `spec-dock/.agent/active.json` の active issue entry を手動編集し、`promotion_decision` を lifecycle-grade 値へ変えることだが、generated/runtime state の直接編集を標準手順にできない。
  - active entry は grants に `issue_finish` を含むため、operator からは grant があるのに拒否されるように見え、diagnostics が分かりにくい。
- 再現手順:
  1. GitHub-linked local issue を `./spec-dock/scripts/spec-dock issue start <issue>` で開始する。
  2. 実装、検証、PR 作成、PR merge、GitHub issue close または already-closed まで進める。
  3. 同じ active issue state で `./spec-dock/scripts/spec-dock issue finish` を実行する。
  4. `active_synthetic_approval_not_lifecycle_approval` で block され、GitHub close / active clear へ進まない。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock issue finish`
  - Active state:
    - `spec-dock/.agent/active.json`
    - `spec-dock/active/context-pack.md`
  - Code:
    - `spec-dock/scripts/spec_dock_runtime/domain/authority.py`
    - `spec-dock/scripts/spec_dock_runtime/application/set_active.py`
    - `spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - Tests:
    - `tests/domain_runtime/test_authority.py`
    - `tests/cli_runtime/test_issue_lifecycle.py`
- 情報源:
  - GitHub issue #149
  - `discussions/20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md`
  - `discussions/20260601t091408z-01-interview-closeout-recovery-path-preference.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock で issue lifecycle を実行する maintainer / agent。
  - PR merge 後に linked GitHub issue と active state を closeout する operator。
- 代表シナリオ:
  - maintainer が `issue start` で issue branch を開始し、実装と PR merge を終えた後、`issue finish` だけで linked GitHub issue close / already-closed 確認、active clear、post-mutation sync まで進めたい。
  - agent が closeout 中に authority gate failure を受けた場合、`active.json` 直接編集ではなく、公式 CLI guidance に従って recovery したい。

## スコープ
- 必須:
  - `issue start` 由来の active issue state から、公式 CLI 操作だけで `issue finish` 可能な lifecycle-approved state へ到達できること。
  - `issue finish` が successful close / already-closed path に到達した場合、既存契約どおり active state を clear し、lifecycle-owned post-mutation sync を実行できること。
  - synthetic active selection と lifecycle approval の区別を維持し、単に `runtime_active_selection` を全 lifecycle grants で許可しないこと。
  - fail-closed する場合は、`active.json` 直接編集ではなく、次に実行できる公式 recovery / transition command または path を error guidance に含めること。
  - provider-side runtime と dogfooding mirror の挙動、docs、tests を一致させること。
- 禁止:
  - `active_synthetic_approval_not_lifecycle_approval` の安全境界を削除して、synthetic approval を lifecycle approval と同一視すること。
  - generated/runtime state `spec-dock/.agent/active.json` の直接手編集を標準 workaround として要求すること。
  - GitHub issue / PR state だけを根拠に、local requirement / design / plan / report / reviewer gate の不足を無視して finish できるようにすること。
  - `issue finish` を PR delivery、merge readiness、review pass、test pass、final delivery completion の代替にすること。
- 対象外:
  - GitHub PR 作成、PR merge、CI failure 修正。
  - `close <target>` command の lifecycle completion 化。
  - delegated authoring authority model 全体の再設計。
  - `implementation_start` / `issue_ready` / `phase_completion` 全体の transition UX 再設計。ただし `issue_finish` と同じ root cause への影響調査は design phase の入力として扱う。

## 境界
- 常に行う:
  - `issue start` / `active set` が作る synthetic selection と、lifecycle closure に必要な approval を別概念として扱う。
  - `issue finish` の前に GitHub state と local active authority state を分けて診断する。
  - already-closed GitHub issue でも active clear が必要なケースを success path に含める。
  - docs / tests / runtime の contract を同時に更新し、operator guidance と実装を一致させる。
- 判断が必要:
  - active manifest の grants 表示を synthetic selection に合わせて狭めるか、grant と promotion decision の診断表示を改善するか。
  - `issue_finish` 以外の lifecycle grants も同じ issue で扱うか、follow-up にするか。
- 行わない:
  - local active state を手で書き換える手順を acceptance criteria にしない。
  - GitHub issue が CLOSED であることだけを completion とみなさない。
  - scope 外の lifecycle / delegated authority architecture を大規模に作り直さない。

## 非交渉制約
- `issue finish` は lifecycle-only command であり、PR delivery / merge readiness / review / tests / final delivery completion を保証しない既存契約を維持する。
- `issue finish` は GitHub close / active clear の前に local authority gate を fail-closed で評価する。
- synthetic active selection は review / planning / design baseline などの input 用 approval としては使えても、lifecycle closure approval そのものにはしない。
- provider-side source of truth は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` であり、dogfooding mirror `spec-dock/scripts/spec_dock_runtime/...` と parity を保つ。
- 手動 recovery guidance は、operator が実行可能な公式 CLI 操作として提示する。

## 前提
- GitHub #149 の報告どおり、問題は GitHub state ではなく local `spec-dock/.agent/active.json` の lifecycle authority state にある。
- `issue start` / `active set` は active selection を作る操作であり、現状の `promotion_decision=runtime_active_selection` は lifecycle-grade promotion ではない。
- 既存 tests は synthetic active approval が lifecycle grants を満たさないことを safety invariant として固定している。

## 受け入れ条件
- AC-001:
  - アクター:
    - maintainer / agent operator。
  - 前提:
    - GitHub-linked issue を `./spec-dock/scripts/spec-dock issue start <issue>` で開始している。
    - issue の delivery evidence は別 workflow で満たされ、GitHub issue は close 可能または already-closed である。
  - 操作:
    - 公式 CLI path に従って `./spec-dock/scripts/spec-dock issue finish` を完了する。
  - 期待結果:
    - `active_synthetic_approval_not_lifecycle_approval` による通常 closeout block が解消される。
    - linked GitHub issue close または already-closed 確認が行われる。
    - active state が clear される。
    - lifecycle-owned post-mutation sync が実行される。
  - 観測点:
    - CLI stdout / stderr
    - `spec-dock/.agent/active.json`
    - GitHub issue stub / snapshot
    - runtime tests
- AC-002:
  - アクター:
    - maintainer / agent operator。
  - 前提:
    - active issue entry が synthetic active selection のままで、finish に必要な supported transition 条件を満たしていない。
  - 操作:
    - `./spec-dock/scripts/spec-dock issue finish` を実行する。
  - 期待結果:
    - GitHub close や active clear の前に fail-closed する。
    - error message は `active.json` 直接編集ではなく、次に実行できる公式 recovery / transition path を提示する。
  - 観測点:
    - CLI stderr
    - GitHub close stub が呼ばれないこと
    - active state が保持されること
- AC-003:
  - アクター:
    - reviewer。
  - 前提:
    - synthetic active approval と lifecycle approval の authority gate tests が存在する。
  - 操作:
    - 変更後の authority gate / issue lifecycle tests を確認する。
  - 期待結果:
    - synthetic active approval を lifecycle grants へ単純に通す regression がない。
    - supported transition path だけが finish success path を開く。
  - 観測点:
    - `tests/domain_runtime/test_authority.py`
    - `tests/cli_runtime/test_issue_lifecycle.py`
- AC-004:
  - アクター:
    - maintainer / document reviewer。
  - 前提:
    - docs と runtime behavior が更新されている。
  - 操作:
    - `workflow_issue.md`、CLI guidance、active/context-pack 表示を確認する。
  - 期待結果:
    - `issue start` -> `issue finish` の primary path と authority / recovery guidance が矛盾しない。
    - `issue finish` が PR delivery / test / review completion を保証しない既存境界も維持されている。
  - 観測点:
    - docs inspection
    - spec-reviewer evidence

## 例外・エッジケース
- EC-001:
  - 条件:
    - GitHub issue がすでに CLOSED だが、active issue は synthetic state のまま残っている。
  - 期待:
    - 公式 transition path 後に `issue finish` が already-closed success として active clear まで進む。
  - 観測点:
    - issue lifecycle tests
- EC-002:
  - 条件:
    - active issue が別 issue 用の stale promotion record を持つ。
  - 期待:
    - `promotion_record_not_bound_to_active_entry` または同等の stale record reason で fail-closed し、GitHub close / active clear へ進まない。
  - 観測点:
    - authority / issue lifecycle tests
- EC-003:
  - 条件:
    - active issue の `report.md` に unresolved `blocked` / `stale` Evidence Adoption Ledger entry がある。
  - 期待:
    - finish transition または finish execution が fail-closed し、ledger 解消を求める。
  - 観測点:
    - issue lifecycle tests
- EC-004:
  - 条件:
    - delegated `design.md` / `plan.md` artifact が proposed / missing metadata のまま downstream authority に使われる。
  - 期待:
    - finish transition または finish execution が fail-closed し、fresh reviewer / promotion を要求する。
  - 観測点:
    - issue lifecycle tests

## 入力→出力例
- EX-001:
  - 入力:
    - `./spec-dock/scripts/spec-dock issue start iss-00149`
    - official transition path
    - `./spec-dock/scripts/spec-dock issue finish`
  - 出力:
    - `spec-dock: ok (issue finish) issue=iss-00149 ... active_cleared=true`
- EX-002:
  - 入力:
    - transition 条件を満たさない active issue で `./spec-dock/scripts/spec-dock issue finish`
  - 出力:
    - fail-closed reason と公式 recovery / transition command guidance。

## 用語
- TERM-001: synthetic active selection
  - `issue start` / `active set` が作る active selection 用 approval。`promotion_decision=runtime_active_selection` を持つ。
- TERM-002: lifecycle approval
  - `implementation_start`、`issue_ready`、`issue_finish`、`phase_completion` を通すための approval。synthetic active selection とは別扱いにする。
- TERM-003: supported transition path
  - synthetic active selection から lifecycle approval へ、手動 `active.json` 編集なしで移る公式 CLI 操作。
- TERM-004: lifecycle-owned post-mutation sync
  - `issue finish` が active clear 後に実行する post-mutation sync。manual sync とは区別する。

## 決定事項
- DEC-001:
  - 論点:
    - `issue finish` が synthetic active state で止まる問題を、どの supported transition path として解くか。
  - 採用:
    - `issue finish` が close / active clear の前に finish-scoped lifecycle transition を内部生成する。
  - 具体化:
    - `issue finish` は active issue entry が `promotion_decision=runtime_active_selection` の場合でも、それを直接 lifecycle approval として扱わない。
    - 代わりに、finish 前 local gates を fail-closed で検査し、成立した場合だけ issue-finish-scoped lifecycle approval を生成 / 永続化する。
    - その後、既存の `issue_finish` authority gate を通してから GitHub close / already-closed 確認、active clear、lifecycle-owned post-mutation sync へ進む。
  - 棄却:
    - 明示 command 追加は、独立した人間承認イベントが必要という根拠がないため、この issue では採用しない。
    - guidance 改善のみは root cause である supported transition 不在を解決しないため、単独解として採用しない。
  - 制約:
    - transition 対象は `issue_finish` に限定する。
    - `implementation_start` / `issue_ready` / `phase_completion` を同時に自動昇格しない。
    - domain authority gate の invariant、つまり `runtime_active_selection` が lifecycle grants を直接満たせないことは維持する。
    - `issue finish` を PR delivery / review / test completion の代替にしない。
  - 根拠:
    - `discussions/20260601t091408z-research-issue-finish-synthetic-approval-source-analysis.md`
    - `discussions/20260601t092641z-disc-deep-consultant-lifecycle-transition-decision.md`

## 未確定事項
- なし:
  - transition path は DEC-001 で決定済み。詳細な state persistence timing、promotion decision token、diagnostic wording は design phase で固定する。
