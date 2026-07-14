# Implementation Planner Review: GitHub Sync Preflight Reliability

## Provenance

- `created_by_role`: implementation-planner
- `scope_id`: `iss-00314`
- `source_paths`:
  - `requirement.md`, `design.md`, `plan.md`, `report.md`
  - `artifacts/20260713t024106z-research-chatgpt-pro-issue-planning-candidate-set.md`
  - `artifacts/20260713t031029z-draft-design-system-architect-preflight-reliability-design-review.md`
  - parent Epic requirement/design/plan
  - current runtime under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - `tests/cli_runtime/` and `tests/unit/`
- `intended_targets`: `plan.md` implementation sequencing and review only
- `adoption_status`: `unreviewed`
- `reflected_to`: `[]`
- `diff_guard_result`: `passed` (main orchestratorがartifact作成直後の変更範囲を確認し、このartifact以外のcanonical/code/tests/GitHub変更がないことを確認)

## 結論

ChatGPTの候補計画は、失敗分類、限定retry、receipt、fresh snapshot、TOCTOU、provider/consumer parity、S90/S99まで網羅しており、Issueの方向性は妥当である。一方で「First PR」に14項目を同梱しており、実装単位として大きすぎる。`pack prepare` binding、配布 parity、skill/docsまでを同一変更に含めると、fetch契約の失敗原因を局所化できず、step gateも形骸化する。

推奨は、同一Issue内で依存順を固定した6 vertical slices（C1〜C6）に分割し、各sliceをレビュー・focused test・コミットで閉じること。C1〜C3をruntimeの最小閉包、C4をconsumer境界、C5を運用文書、C6を最終証跡とする。

## 候補計画の採用判定

| 項目 | 判定 | 理由／修正 |
|---|---|---|
| 固定 `git fetch --prune origin` | 採用 | freshness保証の前提であり、削除・fallbackは禁止。 |
| typed outcome/classifier/redaction | 採用 | `origin_fetch_failed` 一択を解消する最小ドメイン契約。unknownは推測せずblock。 |
| 同一capability shapeの最大1回retry | 採用 | argv、環境、権限、timeoutを変えない。設定可能化は範囲外。 |
| `--output-dir` 固定filename | 採用 | `--report-path`追加より攻撃面とAPI面が小さい。既存canonical fileを拒否する。 |
| post-fetch snapshot/concurrent guard | 採用（C3） | fetch前観測との混在を避け、HEAD/ref/source manifestを同一時点で扱う。 |
| `pack prepare` receipt binding | 部分採用（C4） | preflight schemaのconsumer検証だけ。pack時点の再fetch・全面再検証はLATER。 |
| provider/dogfood/installed parity | 部分採用（C4） | provider testsを先にし、projectionは生成・smoke確認に限定。 |
| skill/docs変更 | 採用（C5） | `require_escalated`やraw fetchを復旧手順にしないことを明記。 |
| immutable launcher、Trace2、openat、all-writer refactor | 棄却／follow-up | Issue closureを阻害しないが、今回のstepへ混ぜない。 |

## 推奨 vertical slices と依存順

| Slice | 目的／主な変更面 | 依存 | 必須テストカード | gate／commit候補 |
|---|---|---|---|---|
| C1 (S01) | `FetchAttempt`/typed result、argv固定、timeout、`GIT_TERMINAL_PROMPT=0`、bounded diagnostic | なし | fake subprocessでsuccess、timeout、nonzero、secret redaction、argv/env固定 | focused unit + code-reviewer。`fix(github-sync): fetch outcomeを型付き化` |
| C1b (S02) | classifier/confidence/retry policyをapplicationへ接続 | C1 | transient allowlistのみ1 retry、unknown/auth/lock/config no-retry、attempt履歴、exit code | unit/CLI + code-reviewer。C1と同一コミット可だが、Red/Green証跡は分離 |
| C2 (S03) | receipt schema version、blocked/pass diagnostics、safe `--output-dir`、atomic writer | C1b | fixed filename、temp+replace、既存canonical拒否、path traversal/absolute/repo内拒否、stdout独立 | CLI/filesystem tests + code-reviewer。`fix(github-sync): receiptを安全に公開` |
| C3 (S04) | fetch後snapshot、sync評価、final concurrent-change guard | C2 | clean/synced、dirty/ahead/behind/diverged、HEAD/ref/source変更で`concurrent_repo_change`、staleはpass不可 | hermetic Git integration + code-reviewer。`fix(github-sync): post-fetch snapshotを固定` |
| C4 (S05) | `pack prepare`のreceipt integrity/binding、provider→dogfood→installed parity | C3 | schema/digest/source identity mismatch、legacy fields、provider asset install smoke | runtime/install tests + code-reviewer。`fix(github-sync): receipt consumer境界を接続` |
| C5 (S06/S90) | skill/docs/helpと既存互換性の更新 | C4 | grep/contract inspection、legacy text/json、`local-context`/fallback semantics維持 | docs/spec-reviewer S90。`docs(github-sync): 権限昇格禁止を明記` |
| C6 (S99) | closure/report/ledger、full verification、delivery evidence | C1〜C5 | focused/full pytest、ruff/mypy、SpecDock validate、diff guard、provider/install parity | QA reviewer + issue-wide code-reviewer + fresh spec-reviewer。最終証跡のみコミット |

※上表のコミットメッセージは候補であり、実際のメッセージは staged diff に基づき `git-commit-message` 規約で生成する。

## Closure index と証跡先

候補の `CLOS-001`〜`CLOS-021` は保持してよいが、各行の検証対象を上記sliceへ一対一で割り当てる。特に次を明示しない行は実装開始前に補正する。

- fetch contract/classification: `tests/unit/...` と `report.md#S01-S02`
- output/atomic/redaction: `tests/unit/infra/...` と `report.md#S03`
- snapshot/concurrency: `tests/cli_runtime/...` または hermetic Git integration と `report.md#S04`
- pack binding/parity: `tests/cli_runtime/...`, installer/runtime smoke と `report.md#S05`
- docs/skill: diff inspection と `report.md#S06-S90`
- issue closure: `report.md#S99`（closure、EAL、decision、reviewer、commit ledger）

各test cardは「fixture／刺激／期待status・receipt field／exit code／redaction／証跡コマンド／report destination」を必須フィールドとする。単に「pytestを実行」とするカードは不十分。

## Delegation contract review

委任stepごとに、少なくとも次をplanへ記載する必要がある。

1. `step_id` と目的（AC/EC/closure IDs）。
2. 対象ファイル／許可変更面と禁止変更面。
3. 前提入力（canonical docs、直前commit、fixture）。
4. 実行コマンド、focused test、期待するRed/Green結果。
5. 出力先（`report.md` の節、artifact path、reviewer evidence）。
6. success/failure/block条件と停止時の返却形式。
7. reviewer role、レビュー対象diff、コミット境界。
8. amendment trigger（API/schema、scope、dependency、security、parity drift）。

候補計画はroleと大半のgateを示すが、S01〜S06について「失敗時の停止条件」「report節名」「返却artifact名」が抽象的である。各委任カードに上記8項目を埋め、`adoption_status`やreviewer passをworkerが自己主張できないことを明記する。

## S90 / S99 gate

### S90（spec gate）

- requirement/design/planのAC、DES、CLOSが相互参照され、wildcard/template placeholderがない。
- provider source、dogfood projection、installed runtimeの責任境界がdocsと実装で一致する。
- fresh `spec-reviewer` passを取得する。candidate artifactの自己判定は証拠にしない。

### S99（issue closure gate）

- CLOS全required行がpassまたは明示的approved-no-op。
- focused/full tests、lint/typecheck、`spec-dock validate`、diff guardがpass。
- S01〜S06のstep result、レビュー、コミット、EAL、decision ledger、deferred follow-upが`report.md`に記録済み。
- QA reviewer、issue-wide code-reviewer、fresh final spec-reviewerの3 passが揃う。
- worktree clean、LATER項目混入なし。未解決open ledgerはblock。

## 重大な修正提案／過大・矛盾点

1. **First PRの過大化**: pack binding、parity、docsをruntime coreと同時に実装しない。上記C1〜C5へ分割する。
2. **retry分類の曖昧さ**: stderr文字列を恒久契約にせず、終了コード／例外型／安全な限定tokenの優先順位をdesignへ固定する。unknownはno-retry。
3. **receipt writerの権限境界**: `--output-dir`の既存ディレクトリ、固定basename、symlink／canonical docs拒否、atomic replaceの失敗時旧receipt保持をtestで固定する。
4. **TOCTOU検証不足**: snapshot比較対象（branch、HEAD、worktree、remote-tracking ref、source manifest）と比較順序をC3のtest cardに列挙する。
5. **互換性の未検証**: additive JSONを前提にせず、旧consumerがunknown fieldを無視すること、旧text/status/exit codeが変わらないことを実測する。
6. **delegationの証跡不足**: report destinationとblock returnをstep単位で明示する。workerの「ready」「adopted」自己claimは禁止。
7. **CLOSのtemplate残存**: `CLOS-XXX`、`B-XXX`、`...`行はcanonical planへ昇格する前に削除または実IDへ置換する。
8. **retry delayの未確定**: delay/jitterは外部API化せず、定数としてplan/design双方に同一値を置く。テストは時間依存を避け、clock injectionまたは即時fakeを使う。

## Amendment triggers

次を発見した場合はreport記録だけで続行せず、plan amendment → fresh design/spec reviewへ戻す。

- `--report-path`や任意basenameなどAPI面が増える。
- retryが権限、argv、environment、remote、timeoutを変える。
- raw stderr／credential helper出力をreceiptへ保存する必要が生じる。
- `pack prepare`で再fetch／current repo再検証が必須になる。
- provider/installed parityが別IssueやEpic boundaryを変更する。
- canonical docsや`.assurance.json`をruntime writerが更新する。
- lock自動削除、fallback、権限昇格、shell wrapperを導入する。

## Implementation planner verdict

**条件付き採用（implementation-readyではない）**。候補計画の技術方針は採用可能だが、canonical planへ反映する前に、vertical slice依存順、test cardの具体フィールド、delegation return、CLOS実ID、S90/S99証跡節を補正すること。補正後にfresh design/spec reviewerを通し、各sliceを一つずつ実装・レビュー・コミットする。
