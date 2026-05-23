---
種別: 要件定義書（Issue）
ID: "iss-00118"
タイトル: "Delegated Authoring Dogfooding Pilot"
関連GitHub: ["#118"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# iss-00118 Delegated Authoring Dogfooding Pilot — 要件定義（WHAT / WHY）

## 目的
- shipped workflow / skills / adapters を dogfooding workspace で使い、draft-only delegated authoring の実地証跡を残す。
- 親 Epic の `E-RQ-009, E-RQ-012` / `E-AC-004 operational evidence, E-AC-005 operational evidence, E-AC-007, E-AC-008` を、この Issue の変更範囲で閉じられる状態にする。

## 背景・現状
- 現状の挙動:
  - Epic `epic-00112` は delegated authoring を draft-only evidence として導入する方針を固定した。
  - `iss-00113`..`iss-00117` が shipped provider assets / host adapter / phase gate contract を実装する前提である。
  - この Issue は新しい provider contract を追加するのではなく、先行 Issue の成果を dogfooding workspace で使い、実地証跡として評価する。
- 現状の課題:
  - pilot が provider 実装 Issue と混同されると、未実装の新 contract を達成したように見せる false success が発生する。
  - 先行成果が不足している場合は、この Issue で勝手に実装せず、approved no-op / documented uncertainty / follow-up として閉じる必要がある。
- 観測点:
  - docs: pilot artifacts と canonical integration evidence が `discussions/` / `report.md` に存在する。
  - tests: 必要に応じて validate / sync / parity inspection evidence が残る。
  - spec-dock: `validate` / `sync` が成功する。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`

## スコープ
- 必須:
  - 対象成果物: `spec-dock active docs and discussions; provider/consumer parity evidence; validate/sync outputs`
  - 先行 Issue の provider-side 成果物を確認し、この Issue では dogfooding pilot evidence を追加する。
  - 追加 provider 更新が不要な場合は approved no-op として記録し、新規 provider 変更を行ったように主張しない。
  - `report.md` に変更対象、検証、reviewer 結果を記録できる状態にする。
- 禁止:
  - 初期 Epic の非スコープである write-capable delegation、runtime validation、role registry、`.github/agents` / Copilot support を実装しない。
  - delegated draft を fresh `spec-reviewer` pass の代替として扱わない。
- 対象外:
  - Issue scope を超える実装コード変更。
  - GitHub issue close/update automation。

## 境界
- 常に行う:
  - 親 Epic の ownership / draft-only / provider-first contract に従う。
  - 先行 Issue の provider asset と dogfooding mirror の関係を確認する。
- 判断が必要:
  - 先行成果の不足を、この Issue の amendment で扱うか follow-up に分離するか。
- 行わない:
  - 親 Epic の scope / non-scope を再定義しない。

## 非交渉制約
- Manual authoring path を壊さない。
- Fresh `spec-reviewer` gate を維持する。
- Provider source と dogfooding consumer を混同しない。

## 前提
- Depends on: iss-00113, iss-00114, iss-00115, iss-00116, iss-00117
- 親 Epic requirement/design/plan は fresh `spec-reviewer` pass 済み。

## 受け入れ条件
- AC-001:
  - アクター: maintainer / orchestrator
  - 前提: この Issue の依存 Issue が完了または reviewer-approved no-op である。
  - 操作: 先行 provider contracts と pilot prerequisites を確認し、必要な no-op / uncertainty を記録する。
  - 期待結果: この Issue が新規 provider update を主張せず、pilot evidence の実行前提が `report.md` に明示される。
  - 観測点: prerequisite ledger、git diff、report evidence。
- AC-002:
  - アクター: maintainer / test runner
  - 前提: pilot prerequisites が確認済み。
  - 操作: `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する。
  - 期待結果: 成功し、必要な parity evidence が残る。
  - 観測点: command output、report evidence。
- AC-003:
  - アクター: `spec-reviewer`
  - 前提: requirement/design/plan/report と差分が揃っている。
  - 操作: Issue final spec review を行う。
  - 期待結果: 親 Epic の該当 E-RQ/E-AC と矛盾せず `review_status: pass`。
  - 観測点: reviewer result。

## 例外・エッジケース
- EC-001:
  - 条件: 先行 provider contract / host adapter / asset path が pilot 時点で確認できない。
  - 期待: verified implementation と偽らず、documented uncertainty / approved no-op / follow-up のいずれかで閉じる。
  - 観測点: report evidence。
- EC-002:
  - 条件: dogfooding mirror が provider source と異なる。
  - 期待: 意図した差分か drift かを report に記録し、必要なら修正する。
  - 観測点: diff evidence。

## 用語（ドメイン語彙）
- TERM-001: delegated draft evidence
  - delegated author が返す draft-only artifact。canonical authority ではない。
- TERM-002: provider-first
  - shipped source を `src/spec_dock/assets/...` で変更し、consumer workspace で検証する方針。

## 未確定事項
- なし。


## Required Dogfooding Pilot Evidence
- Required artifacts:
  - at least one delegated design draft saved under `discussions/`
  - at least one delegated plan draft saved under `discussions/`
  - canonical integration evidence in `report.md`
  - fresh `spec-reviewer` result for the pilot artifacts and canonical integration
- Required pilot metrics:
  - draft count
  - integration ratio / integration cost
  - rejected reasons
  - traceability defects
  - scope creep or gate violations
  - forbidden action attempts
  - reviewer findings
  - stale draft events
  - provider/consumer drift
  - implementation deviation if implementation follows
- Required decision:
  - `write-capable delegation remains deferred` unless a later Epic / Issue explicitly approves it.
- Pilot must use shipped/documented workflow assets rather than ad hoc prompt-only delegation.
