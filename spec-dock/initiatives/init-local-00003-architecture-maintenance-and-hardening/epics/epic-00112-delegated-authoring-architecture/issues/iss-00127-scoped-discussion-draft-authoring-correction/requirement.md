---
種別: 要件定義書（Issue）
ID: "iss-00127"
タイトル: "Scoped Discussion Draft Authoring Correction"
関連GitHub: ["#127"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
親: ["epic-00112", "init-local-00003"]
derived_from:
  - "discussions/20260524t131259z-research-scoped-discussion-draft-authoring-model-analysis.md"
  - "discussions/20260524t133442z-adr-flat-scope-local-discussion-drafts.md"
  - "discussions/20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md"
  - "discussions/20260524t150916z-disc-fresh-consultant-review-v2-discussion-direct-write-model.md"
  - "discussions/20260524t235542z-disc-agent-permission-classification-gap-analysis.md"
---

# iss-00127 Scoped Discussion Draft Authoring Correction — 要件定義

## 目的
- `epic-00112` で導入された delegated authoring v2 の過剰な manifest / Permission Profile / canonical draft write model を、scope-local flat `discussions/` direct-write model へ修正する。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator の single-writer authority とし、sub-agent は canonical docs を直接編集しない。
- 一方で、sub-agent は対象 scope の `discussions/` 直下に flat Markdown draft / analysis / discussion-local report を直接作成・編集できる。これは agent context の揮発性と伝言ゲームを減らし、設計判断と中間成果物を file-based project context として永続化するための意図的な設計である。

## 背景・現状
- 現行 v2 は `iss-00126` で write-capable delegated draft authoring を実装し、task manifest、input authority、session invocation、Permission Profile、probe、hash、`acceptance_counted` などの機械契約を導入した。
- 現行 skill / workflow docs は、条件付きで system-architect が `design.md`、implementation-planner が `plan.md` を直接 draft 更新できる成功パスを持つ。
- 現行 runtime は `delegated-authoring manifest` の成功時に `discussions/delegated-authoring/<task-id>/` 配下の manifest / profile / probe / session artifact を生成し、canonical target write 用 Permission Profile を作る。
- この model は安全性と監査性を重視したが、ユーザーが求めるシンプルな運用、scope-local `discussions/` の既存命名規則、agentic collaboration、file-based context persistence とずれている。
- 2026-05-25 の方針決定により、`sub-agent proposal-only / orchestrator-only discussion write` は標準方針として採用しない。安全性だけを最大化するよりも、sub-agent が自分の分析と draft を `discussions/` に直接保存できる協働効率を優先する。

## スコープ
- 必須:
  - system-architect / implementation-planner の canonical docs direct edit success path を削除する。
  - sub-agent が対象 scope の `discussions/` 直下に flat Markdown draft / analysis / discussion-local report を直接作成・編集できる契約を shipped skills / adapters / workflow docs に反映する。
  - system-architect / implementation-planner を read-only static specialist ではなく scoped-write delegated authoring agent として分類し、対象 scope の `discussions/` 直下に限る write-capable execution path を成立させる。
  - `discussions/` の出力は既存命名規則 `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` に従い、per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を新規生成しない。
  - `delegated-authoring manifest` を新規 user-facing success path として使えない状態にし、新規 manifest / profile / probe / session artifact を生成しない。
  - accepted ADR と discussion draft と canonical docs の authority 境界を明記する。
  - sub-agent direct-write の安全性を、post-run diff guard、orchestrator-owned adoption ledger、stale/rejected handling、authority claim 禁止で補完する。
  - provider assets と dogfooding mirror を同期し、対象 tests と `validate` / `sync` / `doctor` / `git diff --check` で確認する。
- 禁止:
  - sub-agent が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集できる成功パスを残すこと。
  - `sub-agent proposal-only` を標準方針にすること。
  - 独立 JSON/TOML manifest、input authority、session invocation、`acceptance_counted`、authority graph を user-facing acceptance contract として必須にすること。
  - 初回対応で `draft-requirement` / `draft-design` / `draft-plan` kind を追加すること。
  - 既存 `iss-00126` の historical evidence を削除・rename・validate failure 化すること。
- 対象外:
  - GitHub Copilot / `.github/agents` support の追加。
  - 汎用的な権限サンドボックス基盤や、任意 scope / 任意 host に対応する完全な permission engine を新規設計すること。
  - static adapter だけで exact target scope write を表現できない場合に、static adapter へ広い write root を与えて解決すること。
  - `validate` / `issue finish` に discussion draft schema の深い意味解析を追加すること。

## 境界
- 常に行う:
  - Canonical artifacts は main orchestrator が採用内容を再記述して更新する。
  - Sub-agent output は persistent proposal / evidence channel として扱い、それ自体は implementation start / issue finish / phase completion authority にならない。
  - Accepted ADR は architecture decision authority を持ち得るが、implementation readiness / phase promotion authority は canonical docs への反映後に成立する。
  - `reflected_to` は実際に canonical artifact へ反映済みの対象だけを表し、予定先は `intended_targets` で表す。
- 解決済み判断:
  - post-run diff guard は今回 runtime helper として最小実装する。helper は delegated output の採用資格を判定するだけで、adoption ledger や canonical artifact を更新しない。
  - static adapter は broad write を許可せず、read-mostly fallback として扱う。ただし static fallback は `system-architect` / `implementation-planner` の本命実行経路ではない。これら 2 role は、別途 target scope `discussions/` direct child だけを書ける scoped-write delegated authoring execution path を持たなければならない。
- 行わない:
  - Sub-agent に canonical artifact の authoring authority / promotion authority / reviewer pass claim を与えない。
  - Per-agent directory や run directory を `discussions/` 配下に作らない。

## 非交渉制約
- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は sub-agent が直接編集しない。
- Sub-agent は対象 scope の `discussions/` 直下に限り、flat Markdown draft / analysis / discussion-local report を直接作成・編集できる。
- Sub-agent-created draft は `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己主張しない。
- Sub-agent-created draft は最低限 `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []` を持つ。
- Sub-agent は原則として discussion file を新規作成する。既存 discussion file の編集は main orchestrator が明示指定した proposed draft に限定する。
- Accepted ADR、superseded / stale / rejected / adopted 済み discussion file は sub-agent workflow から直接編集しない。
- Post-run diff guard で forbidden diff が検出された delegated output は rejected / ineligible とし、canonical adoption に使わない。

## 前提
- Active issue は `iss-00127`、親 Epic は `epic-00112`、親 Initiative は `init-local-00003` である。
- `discussions/20260524t133442z-adr-flat-scope-local-discussion-drafts.md` は accepted ADR として、本 issue の file layout / operation policy の根拠である。
- `discussions/20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md` が最新の discussion draft であり、V1 draft は superseded である。
- Existing historical artifacts from `iss-00126` are grandfathered evidence and are not migrated or deleted by this issue.

## Agent 権限分類
- Read-only static specialist:
  - 対象: `researcher`, `consultant`, `deep-consultant`, `repo-analyst`, `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `pr-monitor`, `spark-worker`。
  - 契約: 調査、分析、レビュー、監視に限定し、ファイル作成・編集・削除を行わない。
- Full workspace-write worker:
  - 対象: `dev-coder`, `doc-writer`, `worker`, `utility-worker`, `default`, `explorer`。
  - 契約: main orchestrator の委任範囲内で実装、テスト、ドキュメント編集を行える。
- Scoped-write delegated authoring agent:
  - 対象: `system-architect`, `implementation-planner`。
  - 契約: canonical docs や implementation files は編集しない。一方で、target initiative / epic / issue の `discussions/` direct child に限り、命名規則準拠の flat Markdown draft / analysis / discussion-local report を直接作成できる。
  - 補足: static `.codex/agents/*.toml` が read-mostly fallback であることは、この 2 role を read-only specialist に分類する根拠ではない。実運用では target scope を解決した scoped-write execution path が必要である。
- Canonical authority / orchestrator:
  - 対象: main orchestrator と spec-manager-like orchestration support。
  - 契約: discussion draft の採否判断、canonical docs への統合、Evidence Adoption Ledger、phase / lifecycle authority を担う。

## 受け入れ条件
- AC-001: Canonical direct-write path removal
  - アクター: system-architect / implementation-planner
  - 前提: shipped skills、dogfooding mirror、workflow docs、adapters が更新済みである。
  - 操作: skill / adapter / workflow docs を検索・点検する。
  - 期待結果: canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を sub-agent が直接作成・更新できる成功パスが残っていない。
  - 観測点: `rg` による旧語彙・旧契約検索、targeted tests、spec-reviewer pass。
- AC-002: Scope-local flat discussion direct-write contract
  - アクター: sub-agent / main orchestrator
  - 前提: target initiative / epic / issue scope が解決済みである。
  - 操作: system-architect / implementation-planner の output contract と execution permission contract を確認する。
  - 期待結果: system-architect / implementation-planner は対象 scope の `discussions/` 直下に `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` の flat Markdown draft / analysis / discussion-local report を直接作成できる。static fallback が read-only の場合でも、別途 scoped-write execution path が存在し、read-only specialist と同列に扱われていない。
  - 観測点: shipped skills、adapters、discussion rules、permission / execution path tests。
- AC-003: Forbidden delegated output locations
  - アクター: delegated authoring runtime / docs / tests
  - 前提: delegated authoring output を生成または案内する経路を確認する。
  - 操作: `discussions/delegated-authoring/`、per-agent directory、run directory、global draft store、`.codex/permission-probe-evidence` の扱いを確認する。
  - 期待結果: これらは新規 delegated authoring output として生成・推奨されない。
  - 観測点: runtime tests、asset tests、`rg` search。
- AC-004: Lightweight metadata and no manifest-heavy user-facing contract
  - アクター: sub-agent / main orchestrator
  - 前提: sub-agent-created draft が作成される。
  - 操作: front matter と report ledger の契約を確認する。
  - 期待結果: 必須 provenance は Markdown / report ledger に閉じ、独立 JSON/TOML manifest は必須ではない。
  - 観測点: discussion templates / skill docs / workflow docs。
- AC-005: Forbidden authority self-claims
  - アクター: sub-agent
  - 前提: sub-agent-created draft がある。
  - 操作: `authority`、`adoption_status`、`reflected_to` を点検する。
  - 期待結果: draft は `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己主張しない。
  - 観測点: docs contract、testsまたはinspection。
- AC-006: ADR / discussion / canonical authority boundary
  - アクター: main orchestrator / reviewer
  - 前提: accepted ADR と discussion draft が存在する。
  - 操作: requirement / design / workflow docs を点検する。
  - 期待結果: accepted ADR は architecture decision authority、discussion draft は evidence、canonical docs は implementation / phase authority という境界が明記されている。
  - 観測点: spec-reviewer pass。
- AC-007: Post-run diff guard
  - アクター: main orchestrator
  - 前提: sub-agent が discussion draft を作成・編集した。
  - 操作: 実行前 baseline と実行後 diff を比較する。
  - 期待結果: 許可 diff は target scope `discussions/` 直下の naming-rule compliant Markdown create/update のみである。canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.env*`、nested dirs、symlinks、non-Markdown、delete、rename、baseline 時点で dirty/untracked な target discussion entry、新規 discussion の non-editable state claim があれば delegated output は rejected / ineligible になる。
  - 観測点: report ledger、diff guard evidence。
- AC-008: Orchestrator-owned adoption ledger
  - アクター: main orchestrator
  - 前提: discussion draft の内容を canonical docs または実装判断に使う。
  - 操作: `report.md` の Evidence Adoption Ledger を確認する。
  - 期待結果: source discussion path、source role、target artifact/section、adoption status、rationale、blocking、next action が記録されている。
  - 観測点: report.md、spec-reviewer pass。
- AC-009: Deprecated delegated-authoring manifest path
  - アクター: CLI user
  - 前提: `spec-dock delegated-authoring manifest` command が存在する。
  - 操作: command behavior と tests を確認する。
  - 期待結果: command は新規 user-facing success path として artifact を生成せず、deprecated / blocked / no artifact generation として扱われる。
  - 観測点: `tests/cli_runtime/test_delegated_authoring.py`、`tests/domain_runtime/test_delegated_authoring.py`。
- AC-010: Provider / dogfooding parity
  - アクター: maintainer
  - 前提: provider assets を更新した。
  - 操作: dogfooding mirror と provider assets の parity tests / sync を実行する。
  - 期待結果: `.agents`、`.codex`、`spec-dock/docs`、`spec-dock/templates`、`spec-dock/scripts` が意図した更新状態と一致する。
  - 観測点: `tests/test_init_update.py`、`spec-dock sync`、`spec-dock doctor`。
- AC-011: Verification gate
  - アクター: maintainer
  - 前提: 実装完了後。
  - 操作: targeted tests、full validation、review gates を実行する。
  - 期待結果: targeted tests、`spec-dock validate`、`spec-dock sync`、`spec-dock doctor`、`git diff --check` が成功し、required reviewers が pass する。
  - 観測点: command output、report.md、PR checks。

## 例外・エッジケース
- EC-001: Static adapter cannot enforce exact target scope
  - 条件: `.codex/agents/*.toml` だけでは active target scope の `discussions/` 直下 write を厳密に表現できない。
  - 期待: static adapter は read-mostly fallback のままにし、過剰な broad write を正当化しない。ただし system-architect / implementation-planner の本命経路として、target scope `discussions/` direct child だけを書ける scoped-write execution path を別に提供する。
  - 観測点: adapter contract、report ledger、tests / inspection。
- EC-002: Sub-agent modifies forbidden file
  - 条件: sub-agent execution 後の diff に canonical docs、implementation、tests、config、`.agents`、`.codex`、`.env*`、nested dirs、symlinks、non-Markdown、delete、rename が含まれる。
  - 期待: その delegated output は rejected / ineligible であり、canonical adoption しない。
  - 観測点: post-run diff guard、Evidence Adoption Ledger。
- EC-003: Existing historical delegated-authoring artifacts
  - 条件: `iss-00126` など過去 issue の manifest / profile / probe / session evidence が存在する。
  - 期待: grandfathered historical evidence として残し、この issue で削除・rename・validate failure 化しない。
  - 観測点: docs / tests。
- EC-004: Existing discussion file edit request
  - 条件: sub-agent が既存 discussion file の更新を求める。
  - 期待: main orchestrator が明示指定した proposed draft 以外は直接編集しない。accepted ADR / superseded / stale / rejected / adopted 済み discussion は編集不可。
  - 観測点: skill contract、diff guard。
- EC-005: Discussion draft contains secrets or raw credentialed logs
  - 条件: sub-agent draft に secrets、`.env` 内容、credentialed output、private raw transcript が含まれる。
  - 期待: draft は rejected / ineligible とし、必要なら安全な summary に作り直す。
  - 観測点: docs contract、reviewer gate。

## 入力→出力例
- EX-001: system-architect draft
  - 入力: Active issue scope、approved requirement、source docs、target `discussions/` directory。
  - 出力: `discussions/<ts>-disc-design-boundary-analysis.md` with `authority: proposed`, `created_by_role: system-architect`, `scope_id: iss-00127`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`。
- EX-002: rejected forbidden diff
  - 入力: sub-agent output plus diff modifying `.codex/agents/system-architect.toml` directly.
  - 出力: Evidence Adoption Ledger entry with `adoption_status: rejected`, reason `forbidden diff`, and no canonical adoption.

## 用語
- Canonical artifact:
  - `requirement.md` / `design.md` / `plan.md` / `report.md`。Main orchestrator が統合・更新し、reviewer gate 後に phase / implementation authority の根拠になる。
- Discussion draft:
  - `discussions/` 直下の flat Markdown evidence。Sub-agent が直接作成・編集できるが、phase / implementation authority を持たない。
- Discussion-local report:
  - `discussions/<ts>-<kind>-<slug>.md` または same-second collision 用 `discussions/<ts>-<nn>-<kind>-<slug>.md` として保存される analysis / report document。Canonical `report.md` ではない。
- Evidence Adoption Ledger:
  - Main orchestrator が discussion / worker / reviewer / command evidence の採否を記録する canonical `report.md` の台帳。

## 解決済み判断
- Q-001: post-run diff guard の実装場所
  - 判断: 初回 issue で runtime helper として最小実装する。
  - 理由: V2 は sub-agent direct write を採用するため、canonical single-writer authority と adoption ledger だけでなく、post-run diff の機械的 eligibility classifier が必要である。docs-only に閉じると、直接書き込みは許す一方で検証だけ人力に寄る。
  - 影響範囲: runtime command / application / domain、tests、workflow docs、report ledger。
- Q-002: static adapter の scope-local write enforcement 粒度
  - 判断: static adapter では broad write を許可しない。canonical docs write は常に禁止し、scope-local write を host 側で厳密に表現できない場合でも broad write を「許可」とは呼ばない。一方で、system-architect / implementation-planner は read-only static specialist ではなく scoped-write delegated authoring agent であるため、target scope `discussions/` direct child だけを書ける本命 execution path を完了条件に含める。
  - 理由: post-run diff guard は broad permission の正当化ではなく、delegated output の採用資格を判定する安全弁である。direct-write authoring を採用する以上、権限分類上も実行経路上も write-capable でなければ要件を満たさない。
  - 影響範囲: `.codex/agents/*.toml`、scoped execution path、skills、workflow docs、tests。
