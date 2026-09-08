---
種別: artifact
ID: "20260908t010201z"
タイトル: "Issue #392 詳細化調査と親契約への差し戻し"
状態: "parent-return"
作成者: "Codex"
最終更新: "2026-09-08"
親: ["iss-00392"]
template: "blank"
authority: "evidence"
derived_from:
  - "../../../artifacts/provider-lifecycle-wire-contract.md"
  - "../../../artifacts/rolling-wave-issue-elaboration-contract.md"
reflected_to: ["../requirement.md", "../design.md", "../plan.md", "../report.md"]
---

# Issue #392 詳細化調査と親契約への差し戻し

## 1. 結論と現在地

#392は正式start済みだが、**Luna Maxへの実装委譲はまだ不可**である。詳細化で必要な通常のI/O失敗を、固定済みの親wireだけでは表現できないことを確認した。Issue内で新codeを追加したり既存codeの意味を変えたりせず、Rolling-Wave Contract §2・§7に従って親へ戻す。

調査は現在の要件・設計・計画段階で行った。調査用Issueを別に作らず、3 Issueの分割・依存順・Epic集約ブランチ・#395/#396の責務・採用済みE384-DEC-001/002を維持する。

本Artifactは調査証拠と**未採用の修正提案**であり、親wireを上書きする仕様でも、コーダーが着手してよい実装計画でもない。

## 2. 証拠の固定点

| 項目 | 確認した値 |
|---|---|
| Repository / Issue | `chemitaro/spec-dock` / `iss-00392` |
| 調査branch | `iss-00392-provider-lifecycle-and-regression-gate-hard-cutover` |
| 調査HEAD | `14a72044738ce698c3113a0ee70f052015e3be8a` |
| HEAD tree | `af8e50ed3e20e5a03ef1e2a46332142befa1251f` |
| 親wire | `provider-lifecycle-wire-contract.md` v11 |
| wire SHA-256 | `b62cf025ea8edfe0dc32ae5626970ef01b334fce1a059e7e17e7414e1ddf3051` |
| Rolling-Wave Contract SHA-256 | `24010935702671d8263a2d53e7b5e4112d57673472621a69dce1d027d0373c41` |
| 調査開始時working tree | clean |
| 今回の変更範囲 | 当該Issueの文書のみ。Product・親契約・他Issue・GitHub bodyは未変更 |
| 独立調査 | freshな `/root/issue_392_spec_review`、`gpt-6-astra` / Max、read-only |

過去のEpic acceptance、commit/push、正式startを、今回のIssue実装準備のpassへ流用しない。今回、Product試作・fault注入・実装検証はしていない。以下は規範表と現行sourceの照合による**設計上の反例**である。

## 3. 親契約へ戻す確定事項

### P392-001（P1）— 正しいcandidateの作業領域を準備できない

**反例:** repository binding・所有者・lock・native rename capabilityが正常で、packaged candidateも正しい。一方、Consumer外の同一filesystem上のprivate namespace/stageを準備する `mkdir`、copy/write、`fsync` が `EACCES`、`ENOSPC`、`EIO` などで失敗する。Consumer target変更前にも発生する。

**不足の根拠:**

- [Wire §1](../../../artifacts/provider-lifecycle-wire-contract.md) は未列挙の関係・code・catch-all mappingを禁止する。
- §10の全152データ行を抽出した。phase=`candidate-staging` にあるcodeは `resume-candidate-mismatch`、`candidate-invalid`、`candidate-digest-mismatch`、`stage-owner-mismatch` のみ。
- §11の診断は、candidate不正・digest相違・resume不一致・既存stage所有者不一致という別の原因を表す。正しい内容の書込不能・容量不足・fsync失敗を丸めると意味が変わる。
- `repository-coordination-unavailable` は§16でlock/descriptor admission失敗へ限定される。取得済みlockの後に起きるstage I/O失敗へ流用できない。
- §1の「予期しない未型付け例外」はプログラム欠陥の扱いであり、通常のOS障害を意図的に未型付けで放置する根拠ではない。

**残存状態:** Consumer mutationは0でも、private namespace/stageは部分作成され得る。lifecycle resumeの前提となるincomplete recordも、terminal cleanup retryの前提もない。

**必要な親判断:** 結果、phase/last-completed、Consumer mutationとprivate残存物の区別、保全・cleanup・再実行の扱いをclosed relationへ含める。新codeの必要性・名称はここで仮採用しない。

### P392-002（P1）— 最初のincomplete recordを確立できない

**反例:** 準備完了後、最初の `publish-incomplete-record` のtemporary write、atomic rename、parent `fsync` が失敗する。fresh installだけでなく既存readyへのupdate/uninstallにも存在する。

**不足の根拠:**

- §6の実行順序は、最初のroot公開・除去に先立ってincomplete recordを要求する。
- §10にはphase=`publish-incomplete-record` の結果行が**0件**。
- install/updateのpartial行は `publish-docs`、uninstallは `detach-docs` から始まり、そのlast-completedは `publish-incomplete-record`。当該recordの確立成功を前提とする。
- 失敗phaseを `publish-docs` に偽装したり、成立していないrecord公開を成功済みにしたりして表へ合わせられない。
- rename前とrename済み・fsync未確立では可視状態と耐久性が異なる。常にmutation-zeroとも、常に有効なresumeありとも断定できない。
- fresh bootstrap rollbackだけでは既存readyのupdate/uninstallを扱えない。

**残存状態:** 置換前のupdate/uninstallならConsumer mutation 0。fresh container作成済み、またはrecord置換後なら部分mutation。durable incomplete成立後は同一tuple recoveryを利用できるが、そこへの到達失敗の結果が不足している。

**必要な親判断:** record公開前後の状態、expected I/O failureの結果とexact retryを有限に定める。§12 action・failed/pending・retry/continuation・fault例も同期する。

### 差し戻し範囲を限定する

`publish-terminal-record` の失敗行はinstall二種/update/uninstallに既に存在する。completion receipt公開失敗にもWIR-CLEANUP-002とterminal-cleanup-failedの規定がある。これらを「行がない」という別findingには数えない。今回は**準備から最初のincomplete record耐久化まで**の未被覆境界に絞る。

既存行があるだけで実装全体を認証したわけではない。親修正reviewでは、追加境界と既存terminal/cleanup規定の整合も確認する。

## 4. 親への最小修正提案（未承認・未採用）

1. 通常のI/O失敗を、所有者/binding違反・未型付けプログラム欠陥から区別する。
2. Consumer変更前、record公開前、rename後/fsync前後の区間を分け、結果と残存状態を定める。private prepared metadataが必要なら有界な責務を同時に閉じる。
3. 関係表・診断・action・serialization例・retry/fault期待値を同時に更新する。未列挙値の追加をIssueへ委ねない。
4. parent ADRで変更理由・影響範囲・B0再開点を記録する。#395/#396は参照と受入境界を再確認し、実装詳細は作らない。
5. 親候補の独立review、freeze/projection手順を完了してから#392の詳細化へ戻る。

固定root、保護データ、exact recoveryの既存方針を変えない。汎用catch-all、旧journalへのfallback、新しい調査Issueや4番目のIssueは提案しない。承認前の親契約変更・commit/push・GitHub更新は未実施。

## 5. 再利用できるsource調査

以下は調査時の実在path/symbolで、確定した編集指示ではない。runtime prefixは `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`。dogfood側を先に直す計画にしない。

| 現行対象 | 観測と詳細化すべき接点 |
|---|---|
| `src/spec_dock/cli.py` | 2,874行。`_exclusive_distribution_operation`、`_parse_args`、`main` に旧lifecycle/admission/表示が結合。小さいengine Interfaceへ接続する対象 |
| `src/spec_dock/managed_distribution.py` | 22,332行。per-file plan/journal/reconciliation/deprovisionとFS操作が同居。旧構造をそのまま新packageへ移さない |
| 同ファイルの `_resolve_distribution_no_replace_rename` / `_resolve_distribution_swap_rename` | OS別native primitiveの既存接点。Linux/macOSの実fault証拠が必要 |
| `src/spec_dock/assets/spec_dock/scripts/spec-dock` | stdlib-only不変bootstrapと、payload import前のSH admissionの配置先 |
| runtime `commands/contracts.py::CommandOutcome` / `cli/dispatch.py::dispatch` | 現行outcomeはexit_code/textで、その場でrenderする。外部handoffをそのまま表せない |
| runtime `application/worktree.py` / `infra/make_cli.py::run_make_init_if_available` | use-case内でmake検出/実行を行う。publication後のhookとrenderをbootstrapへ移す必要がある |
| runtime `application/ports.py::GitGateway` / `infra/git_cli.py` / `cli/bootstrap.py` | checkoutはbranch名だけを受け取る。pinしたcommitと実Git操作を結ぶ接点が必要 |
| runtime `application/issue_lifecycle.py` / `application/set_active.py` | checkout/active/syncの接続点。同世代判定・post-checkout drift・実branch変更報告を閉じる |
| `tests/unit/infra/test_init_update.py` | 10,337行。旧lifecycleと保持すべきruntime/docs/workflow/packaging検証が混在。file丸ごと削除不可 |
| `tests/unit/infra/test_managed_distribution.py` | 19,700行。旧engineへ密結合。新保証の証拠ができてからobsolete-onlyを除去する対象 |
| `tests/cli_runtime/test_distribution_cutover.py` | 3,478行。旧契約と現行retained-skill identityが混在。resolved rowのsuccessorを保持する |
| `tests/unit/infra/conftest.py` / `tests/cli_runtime/conftest.py` | installed templateのsession作成/cloneによるsetup最適化。移行faultをcacheで隠さない設計が必要 |

### 触らない境界

- 親R/D/P・wire・integration/rolling-wave契約は、差し戻し承認まで不変。
- `full-regression-ledger.json` の14 active identities/signatures/lifecycle。Product/test修復は#395。
- `full-regression-timing-weights.json`、`scripts/quality/full_regression_baseline.py`、`scripts/quality/verify_full_regression.py`、`tests/conftest.py` のpolicy/shard/permission保証。最終gate切替は#396。
- `tests/conftest.py` の4 required-fast nodeを欠落させない。resolved successor `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood` も保持を優先。
- 他Issue実装、Consumerのinitiative/Artifact/workbench/active/generated projection、無関係なskill/CI seed。
- 旧engine参照がある `tests/unit/infra/test_runtime_fs_cli_workbench.py`、`tests/unit/infra/test_installer_workbench_resolver_opacity.py`、`tests/cli_runtime/test_runtime_doctor_s04.py` も参照だけを根拠に削除しない。

## 6. Issue内で閉じる局所設計事項

以下を追加P1や人間判断へ水増ししない。ただし親修正後に、外部挙動を変えず実装できることを検証する。

- 新 `src/spec_dock/lifecycle/` を小さいpublic Interfaceとengine/state/fs/candidate/wireの責務に分ける案。新名称は候補で、まだ確定した編集指示ではない。
- private namespaceのpath/所有者/mode、厳格なACTIVE schema、candidate tree digestの符号化。
- same-candidate updateでは旧readyと新terminalのrecord bytesが一致し得る。初回ACTIVEを無条件readyにすると旧terminalを新operation完了と誤認する。bounded prepared状態等で区別し、per-file journalは復活させない。
- installer execとworktree hookをprimitive terminal requestで区別する。hook後のresult/警告renderも不変bootstrapへ閉じ、old-moduleへ戻らない。
- `PinnedCheckout` に相当するcommit/closure/実Git argv/branch attachmentとdrift報告を一体で定める。事前rev-parseして旧adapterへbranch名を渡すだけでは不足。
- actual BのEX、entrypoint-last materialization、元B inodeのみのremoval cleanup、独立openのnonlocking B fdを具体化する。lease fdのdupをnonlocking化と扱わない。
- 各書込helper/descendantのfd allowlistと生存期間を固定し、親だけのSIGKILLでもlockが維持されることを実processで確認する。
- `set_active` のselection-only、issue-startのguard→deps→checkout→active→sync、既存worktree blockers/部分削除情報、make失敗でもcreation exit 0、両wrapperのstream/statusを保持する。
- 新candidateのpublic切替・旧writer除去・complete dogfood受入は同一Issue。途中checkpoint単独mergeは不可。

## 7. ステップ粒度評価

- Result: `RETURN_TO_ISSUE`。
- Issue check: #392のgoal/non-goalと単一受入単位は明確。ただしI392-RQ-004/005を現行closed tableだけで実装可能と確定できない。
- Basis: P392-001/002はhelper分割やtest配置では解決しない、親仕様の失敗経路。
- AC trace: I392-RQ-004（closed wire）、005（filesystem/recovery）、006（migration/uninstall）、010（実装gate）に影響。
- Steps: 実装ステップ分割は未採用。契約が閉じる前にphase/error設計をLuna Maxへ委ねない。
- Unresolved facts: failure resultと初期record耐久化の復旧境界。親修正後に因果的checkpointと確認可能な中間状態を再評価する。

`assess-behavior-step-granularity` は評価に使用し、新Issue/branchは作成していない。`codebase-design` はInterface/Seam/Adapterの責務整理、`writing-for-agents` は未決事項を実装者へ渡さないhandoff境界に適用した。

## 8. 親からの戻り条件

親修正の承認だけではProduct実装を開始しない。修正後の親ADR/wire/review/freezeを基準に、Issueの要件・設計・唯一の実装計画を詳細化する。exact owned/shared/no-touch files、全test disposition、内部schema、最初のRED、ordered steps、各step終了状態、Linux/macOS fault、baseline保持、dogfood、rollback、exact command/expected exitを閉じ、Luna Max handoffを作る。

同じIssue reviewerで完全な候補をレビューし、`P0/P1=0`・`review_status=pass` まで `実装開始許可: false` を保持する。今回の早期reviewは不足の確認で、完成したR/D/Pのreview passではない。
