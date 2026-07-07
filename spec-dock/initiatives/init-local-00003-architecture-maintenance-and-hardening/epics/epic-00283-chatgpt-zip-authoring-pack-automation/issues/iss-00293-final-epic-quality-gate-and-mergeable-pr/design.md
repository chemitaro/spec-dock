---
種別: 設計書（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — Issue 設計

## 設計方針

この Issue は、Epic 全体の最終統合ゲートとして設計する。個別実装 slice の所有権は `iss-00284` から `iss-00292` に残し、この Issue はそれらをまとめて検証し、Pull Request がレビュー可能かつ mergeable になる状態へ運ぶ。

PR はこの Issue で一度だけ作成または更新する。先行 Issue の完了は、`issue finish` と各 `report.md` の証跡で確認する。これにより、実装中の認知負荷を「今の Issue を完了して次へ渡す」ことに絞り、PR 作成、CI、レビュー指摘対応、手動テスト証跡を最後に集約する。

## ワークフロー設計

```text
iss-00284 implementation -> issue finish -> issue start iss-00285
iss-00285 implementation -> issue finish -> issue start iss-00286
iss-00286 implementation -> issue finish -> issue start iss-00287
iss-00287 implementation -> issue finish -> issue start iss-00288
iss-00288 implementation -> issue finish -> issue start iss-00289
iss-00289 implementation -> issue finish -> issue start iss-00290
iss-00290 implementation -> issue finish -> issue start iss-00291
iss-00291 implementation -> issue finish -> issue start iss-00292
iss-00292 implementation -> issue finish -> issue start iss-00293
iss-00293 quality gate -> manual tests -> PR -> review/CI fix loop -> mergeable
```

先行 Issue は PR を作らない。各 Issue は自身の完了証跡を残し、次の Issue へ実行コンテキストを渡す。最後の `iss-00293` が、全体をレビュー単位としてまとめる。

## 不具合修正ループ

1. 不具合またはレビュー指摘を `report.md` に記録する。
2. Epic スコープ内の修正であることを確認する。
3. 最小差分で修正する。
4. 関連テスト、`spec-dock validate`、必要な手動確認を再実行する。
5. 変更を push し、PR の状態を再確認する。

修正が Epic スコープを超える場合は、この Issue で抱え込まず、残課題として明記する。

## ChatGPT backend invocation contract

SpecDock repo 内の正式ワークフローやスクリプトは、ユーザー個人環境の ChatGPT Use / Oracle wrapper 絶対パスを直接参照しない。Oracle 本体や ChatGPT automation は SpecDock に同梱せず、SpecDock 側は backend command を解決して呼び出す薄い adapter / invocation contract だけを持つ。

- primary 設定: `SPECDOCK_CHATGPT_COMMAND`
- compatibility fallback: `ORACLE_CHATGPT_COMMAND`
- 将来の拡張: 必要なら設定ファイルまたは CLI 引数で同じ backend command contract を渡せるようにする。
- 未設定時: command を推測せず、どの設定が必要かを示す明確なエラーで fail する。
- 既存のローカル `oracle-chatgpt` wrapper: ユーザー環境で `SPECDOCK_CHATGPT_COMMAND` などに指定できる一例であり、SpecDock repo の必須依存ではない。

### Adapter ABI v1

この Issue で実装する backend adapter は、Oracle 互換の ChatGPT backend を「設定された argv prefix」として扱う。設定値を shell script として評価しない。

- command resolution:
  - `SPECDOCK_CHATGPT_COMMAND` が空でなければそれを使う。
  - 未設定または空なら `ORACLE_CHATGPT_COMMAND` を使う。
  - どちらも未設定または空なら `blocked` とし、`SPECDOCK_CHATGPT_COMMAND` または `ORACLE_CHATGPT_COMMAND` の設定が必要であることを stdout / stderr から分かる形で返す。
- parsing:
  - 設定値は `shlex.split(..., posix=True)` で argv に分解する。
  - shell expansion、pipe、redirect、command substitution は adapter では解釈しない。
  - quoted path with spaces は `shlex.split` の範囲で許可する。
- invocation shape:
  - adapter CLI は `--slug <slug>`、`-p/--prompt <text>`、`--file <path>`（repeatable）を受け取る。
  - 実行時は `backend_argv + ["--slug", slug, "-p", prompt, "--file", file1, ...]` を `subprocess.run(..., shell=False)` で呼ぶ。
  - backend がこの ABI と異なる場合、ユーザーは自身の環境でこの ABI に合わせた shim を `SPECDOCK_CHATGPT_COMMAND` に指定する。
- cwd / env:
  - cwd は呼び出し元の current working directory を維持する。
  - 環境変数は既存環境を継承し、adapter は provider token、cookie、Oracle binary、ChatGPT automation を追加しない。
- output and exit:
  - `--dry-run` は backend を実行せず、resolved source、argv、files、cwd を JSON で返す。
  - 実行モードでは backend の stdout / stderr をそのまま転送し、exit code も backend の終了コードを返す。
  - adapter 自身の設定不足、parse error、file path error、timeout は backend を起動せず、明確な診断を返す。
- timeout:
  - `--timeout-seconds` は任意。未指定または `0` の場合は adapter 側 timeout を無効にする。
  - timeout した場合は backend process を停止し、`blocked` 診断を返す。

この contract は、`iss-00293` の PR 作成前に品質ゲート対象として確認する。検証では、未設定時の fail-closed、設定時の command 解決、個人環境絶対パスの非直書きを確認し、結果を `report.md` に残す。


## 依存関係分析

- 上流入力: 親 Epic requirement / acceptance criteria、親 Epic の Issue readiness contract、Issue-local draft artifact の採否台帳。
- 下流出力: Issue 固有成果物、検証証跡、report ledger
- 実行順: Epic `plan.md` のリレー実行順と handoff prerequisite を前提にする。これは実行上の順序契約であり、現時点では `.meta.json.depends_on` の runtime dependency edge を直接更新しない。
- 権威境界: ChatGPT output、ZIP、staged artifact は evidence-only であり、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映は main orchestrator の採否判断と reviewer gate を通す。
- 実装境界: この Issue は最終品質ゲートと PR delivery を所有し、先行 Issue の実装 slice を再定義しない。欠陥修正は owning Issue の allowed paths に戻して bounded に扱う。
- ChatGPT backend 境界: SpecDock は backend command の解決と fail-closed 契約だけを所有し、Oracle / ChatGPT automation 本体や個人環境 wrapper の配布を所有しない。

## Module Dependency Diagram

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam componentStyle rectangle

title iss-00293 module dependency sketch

component "親 Epic
readiness contract" as EpicContract
component "Issue canonical docs
requirement/design/plan" as IssueDocs
component "scripts/authoring-pack
dogfood-only scripts" as ManualPack
component "Issue artifacts/report
evidence ledger" as EvidenceLedger
component "SpecDock canonical docs
main orchestrator adoption" as CanonicalDocs

EpicContract --> IssueDocs : scope / acceptance / relay order
IssueDocs --> ManualPack : allowed dogfood work
ManualPack --> EvidenceLedger : validation / staged output
EvidenceLedger --> CanonicalDocs : adoption decision only
@enduml
```

## ディレクトリ / ファイル変更計画

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00293-final-epic-quality-gate-and-mergeable-pr/
|-- artifacts/                            # final manual-test / PR evidence when needed
`-- report.md                             # final gate evidence ledger
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/
`-- report.md                             # Epic-level final quality gate summary
scripts/authoring-pack/                  # backend command adapter / invocation contract when implemented by this Issue
tests/manual_tests/                       # adapter contract tests when implemented by this Issue
# Other bounded defect fixes stay in the prior owning Issue's allowed paths.
```

- 通常の許可パス: `iss-00293/report.md`, Epic `report.md`, PR / manual-test evidence artifacts; backend command adapter / invocation contract の実装と検証に必要な `scripts/authoring-pack/**` と `tests/manual_tests/**`; その他の bounded fixes は prior owning Issue の allowed paths に限定する。
- `src/spec_dock/**` と `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` は v1 の通常許可 path ではない。配布 runtime へ昇格する場合は、`iss-00292` の判断材料、plan amendment、fresh reviewer gate を経て明示的に scope を拡張する。
- generated ZIP / staged artifact は canonical docs を直接上書きしない。
