---
種別: 要件定義書（Issue）
ID: "iss-00250"
タイトル: "Route Issue Draft Design And Plan Through Profile Templates"
関連GitHub: ["#250"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
親: ["epic-00224", "init-local-00003"]
Issue Grade: "strict"
---

# iss-00250 Route Issue Draft Design And Plan Through Profile Templates — Issue 要件定義

## 1. 目的

`spec-dock new doc draft-design` / `spec-dock new doc draft-plan` が Issue scope で discussion draft を作成するとき、旧来の `templates/issue/design.md` / `templates/issue/plan.md` 由来の薄い draft ではなく、Issue の `.assurance.json` に記録された `authorized_profile` に対応する grade 別 template を使うようにする。

この Issue は、Issue #247 で導入した `templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` と、`20260630t111316z-adr Grade-Aware Issue Authoring Rules` で固定した grade-aware authoring rules を、discussion draft 生成コマンドにも接続する。

## 2. 背景

Issue #247 により、Issue design / plan の canonical source は grade 別 profile template pack へ移った。`assurance compose` は `.assurance.json` の `authorized_profile` を読み、`templates/issue-profiles/<profile>/{design,plan}.md` から canonical `design.md` / `plan.md` を materialize できる。

一方、調査 `20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md` では、`new doc draft-design` / `new doc draft-plan` が `issue-profiles` を参照せず、`templates/issue/design.md` / `templates/issue/plan.md` を source としていることが分かった。これらの template は compose 前 placeholder であり、現在の draft 生成実装は placeholder marker を削除したうえで、grade 非対応の薄い本文へ正規化している。

この状態では、`system-architect` や `implementation-planner` が discussion draft を作る際、canonical compose 後の grade 別 design / plan 構造と異なる draft を出発点にしてしまう。

## 3. Scope

### In scope

- Issue scope の `new doc draft-design` / `new doc draft-plan` の template routing を修正する。
- classified Issue では `.assurance.json` の `authorized_profile` に基づき、`templates/issue-profiles/<profile>/design.md` または `plan.md` を source として discussion draft を作成する。
- Issue scope の `draft-requirement` は従来通り common requirement template を source とする。
- Initiative / Epic scope の `draft-design` / `draft-plan` は従来通り scope canonical template を source とする。
- missing / invalid / stale `.assurance.json` の Issue で `draft-design` / `draft-plan` を作ろうとした場合の fail-closed 挙動を定義する。
- `tests/cli_runtime/test_new.py` など、旧挙動を固定しているテストを更新する。
- provider-side source of truth と dogfooding docs の整合を取る。

### Out of scope

- `assurance compose` の profile template materialization 自体の再設計。
- grade 別 profile template 本文の全面改訂。
- `system-architect` / `implementation-planner` を新しい shipped skill file として追加すること。
- Issue execution readiness preflight 全体の修正。これは R0 系の別 Issue で扱う。
- GitHub Issue / PR delivery workflow の変更。

## 4. 要求

- REQ-001: classified Issue の `new doc draft-design --issue <id>` は、`.assurance.json` の `authorized_profile` に対応する `templates/issue-profiles/<profile>/design.md` を source として discussion draft を作成する。
- REQ-002: classified Issue の `new doc draft-plan --issue <id>` は、`.assurance.json` の `authorized_profile` に対応する `templates/issue-profiles/<profile>/plan.md` を source として discussion draft を作成する。
- REQ-003: Issue scope の `draft-requirement` は、従来通り `templates/issue/requirement.md` を source とする。
- REQ-004: Initiative / Epic scope の `draft-design` / `draft-plan` は、従来通り `templates/{initiative,epic}/{design,plan}.md` を source とする。
- REQ-005: Issue scope の `draft-design` / `draft-plan` で `.assurance.json` が missing / invalid / stale の場合、薄い fallback draft を作らず fail-closed にする。
- REQ-006: fail-closed 時の error message は、先に `requirement.md` を具体化し、`assurance classify --stage requirement` と必要な compose / verification を実行する必要があることを示す。
- REQ-007: draft 生成は canonical `design.md` / `plan.md` を変更しない。出力先は対象 Issue の `discussions/` 直下の timestamped Markdown のみとする。
- REQ-008: generated discussion draft は canonical authority を自己主張しない。`authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己設定しない。
- REQ-009: provider-side assets / runtime と dogfooding docs の記述が、grade-aware draft routing と矛盾しない。
- REQ-010: 既存の `assurance compose` tests と new doc tests が、profile template source と fail-closed 挙動を regression として固定する。

## 5. 受け入れ条件

- AC-001: Standard profile の classified Issue で `new doc draft-design --issue <id>` を実行すると、作成された discussion draft に `Issue 設計書（Standard）` が含まれる。
- AC-002: Standard profile の classified Issue で `new doc draft-plan --issue <id>` を実行すると、作成された discussion draft に `Issue 実装計画書（Standard / TDD）` と Standard 固有 section が含まれる。
- AC-003: Strict / Critical profile の classified Issue で、対応する profile template の主要見出しが discussion draft に含まれる。
- AC-004: `.assurance.json` が missing の Issue で `draft-design` / `draft-plan` を実行すると失敗し、generic fallback draft は作成されない。
- AC-005: `.assurance.json` が invalid または stale の Issue で `draft-design` / `draft-plan` を実行すると失敗し、generic fallback draft は作成されない。
- AC-006: `draft-requirement`、Initiative / Epic scope の `draft-design` / `draft-plan` の既存挙動は維持される。
- AC-007: `tests/cli_runtime/test_new.py` の旧期待値である `templates/issue/design.md` / `templates/issue/plan.md` source 前提は更新される。
- AC-008: `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py` が成功する。

## 6. 制約

- Provider-side `src/spec_dock/assets/spec_dock/...` を source of truth とする。
- Dogfooding `spec-dock/...` は必要に応じて整合させる。
- `assurance compose` の既存安全制約、symlink escape guard、template validation guard を弱めない。
- Missing / invalid / stale contract を理由に automatic Standard fallback をしてはならない。
- Lite automatic default は有効化しない。

## 7. 根拠

- `20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md`
- `20260630t111316z-adr-grade-aware-issue-authoring-rules.md`
- `20260630t084325z-disc-grade-aware-authoring-rules-definition.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_assurance_compose.py`
