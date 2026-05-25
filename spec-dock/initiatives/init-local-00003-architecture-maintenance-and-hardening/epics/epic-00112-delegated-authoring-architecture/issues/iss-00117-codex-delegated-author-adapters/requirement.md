---
種別: 要件定義書（Issue）
ID: "iss-00117"
タイトル: "Codex Delegated Author Adapters"
関連GitHub: ["#117"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["epic-00112", "init-local-00003"]
---

# iss-00117 Codex Delegated Author Adapters — 要件定義（WHAT / WHY）

## 目的
- .codex/agents に thin callable entrypoints を追加し、role skill を正本にした host adapter boundary を固定する。
- 親 Epic の `E-RQ-010` / `E-AC-002 host-adapter portion` を、この Issue の変更範囲で閉じられる状態にする。

## 背景・現状
- 現状の挙動:
  - Epic `epic-00112` は delegated authoring を draft-only evidence として導入する方針を固定した。
  - この Issue の対象領域 `Codex adapters` は、まだ shipped provider assets と dogfooding consumer workspace に実装されていない。
- 現状の課題:
  - 対象 contract が未実装のままだと、後続 Issue が reviewer pass / evidence / parity を安全に前提化できない。
- 観測点:
  - docs: 対象 provider / dogfooding docs に contract が存在する。
  - tests: 必要に応じて managed asset / init-update / content assertion が更新される。
  - spec-dock: `validate` / `sync` が成功する。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`

## スコープ
- 必須:
  - 対象成果物: `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml; implementation-planner.toml`
  - Provider-side source of truth を先に更新し、dogfooding workspace の parity を確認する。
  - Managed asset parity coverage in `tests/test_init_update.py` or equivalent must be updated; this is not optional for shipped adapter assets.
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
  - 変更した provider asset と dogfooding mirror の関係を確認する。
- 判断が必要:
  - `tests/test_init_update.py` に追加するか同等の targeted test にするか。manual parity evidence は補助証跡に限り、test-required parity の代替にしない。
- 行わない:
  - 親 Epic の scope / non-scope を再定義しない。

## 非交渉制約
- Manual authoring path を壊さない。
- Fresh `spec-reviewer` gate を維持する。
- Provider source と dogfooding consumer を混同しない。

## 前提
- Depends on: iss-00115, iss-00116
- 親 Epic requirement/design/plan は fresh `spec-reviewer` pass 済み。

## 受け入れ条件
- AC-001:
  - アクター: maintainer / orchestrator
  - 前提: この Issue の依存 Issue が完了または reviewer-approved no-op である。
  - 操作: 対象成果物を確認する。
  - 期待結果: `.codex/agents に thin callable entrypoints を追加し、role skill を正本にした host adapter boundary を固定する。` が provider-side source of truth に反映される。
  - 観測点: git diff、対象ファイル、report evidence。
- AC-002:
  - アクター: maintainer / test runner
  - 前提: 対象成果物が更新済み。
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
  - 条件: 対象 host / asset path が実装時に確認できない。
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


## Verified Adapter vs Documented Uncertainty Closure
- Verified adapter closure path:
  - `.codex/agents/system-architect.toml` exists in provider and dogfooding mirror.
  - `.codex/agents/implementation-planner.toml` exists in provider and dogfooding mirror.
  - Each adapter is thin and points to the role skill as authority.
  - Evidence shows the adapter syntax/path is valid for Codex host usage.
- Documented uncertainty closure path:
  - If path or TOML schema cannot be verified, do not create placeholder files that imply verified callability.
  - Record the attempted verification, unknowns, and adapter contract in `report.md`.
  - Close only as adapter contract + documented uncertainty / approved no-op, not as verified host integration.
- Non-scope remains fixed:
  - `.github/agents` / Copilot agent support is not implemented in this Issue.

## Closure Classification
- `verified_host_adapter`:
  - Codex host path and TOML schema are verified.
  - Dogfooding may claim host-callable role invocation.
- `adapter_contract_only`:
  - Path or schema remains unverified.
  - The Issue may close with documented uncertainty.
  - The Epic and Issue 006 must not claim verified Codex host callability.
