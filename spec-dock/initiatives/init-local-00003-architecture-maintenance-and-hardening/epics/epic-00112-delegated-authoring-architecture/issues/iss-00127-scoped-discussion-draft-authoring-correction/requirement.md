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
  - "discussions/20260525t010211z-disc-static-all-discussions-write-permission-analysis.md"
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
  - sub-agent が initiative / epic / issue の scope-local `discussions/` 直下に flat Markdown draft / analysis / discussion-local report を直接作成・編集できる契約を shipped skills / adapters / workflow docs に反映する。
  - system-architect / implementation-planner を read-only static specialist ではなく scoped-write delegated authoring agent として分類し、静的 permission で全 scope-local `discussions/` への write-capable execution path を成立させる。
  - S04 で追加された run-by-run exact-file permission context generation の runtime code、parser/command binding、tests、adapter/skill guidance を削除し、deprecated / diagnostic fallback として残さない。
  - `discussions/` の出力は既存命名規則 `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` に従い、per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を新規生成しない。
  - `delegated-authoring manifest` を新規 user-facing success path として使えない状態にし、新規 manifest / profile / probe / session artifact を生成しない。
  - accepted ADR と discussion draft と canonical docs の authority 境界を明記する。
  - sub-agent direct-write の安全性を、post-run diff guard、orchestrator-owned adoption ledger、stale/rejected handling、authority claim 禁止で補完する。
  - provider assets と dogfooding mirror を同期し、対象 tests と `validate` / `sync` / `doctor` / `git diff --check` で確認する。
- 禁止:
  - sub-agent が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集できる成功パスを残すこと。
  - `sub-agent proposal-only` を標準方針にすること。
  - 独立 JSON/TOML manifest、input authority、session invocation、`acceptance_counted`、authority graph を user-facing acceptance contract として必須にすること。
  - S06 の契約外で ad hoc に `draft-requirement` / `draft-design` / `draft-plan` kind を追加すること。
  - 既存 `iss-00126` の historical evidence を削除・rename・validate failure 化すること。
- 対象外:
  - GitHub Copilot / `.github/agents` support の追加。
  - 汎用的な権限サンドボックス基盤や、任意 scope / 任意 host に対応する完全な permission engine を新規設計すること。
  - `spec-dock/initiatives` 全体や repo-wide write のように、canonical docs まで含む広い write root で解決すること。
  - `validate` / `issue finish` に discussion draft schema の深い意味解析を追加すること。

## 境界
- 常に行う:
  - Canonical artifacts は main orchestrator が採用内容を再記述して更新する。
  - Sub-agent output は persistent proposal / evidence channel として扱い、それ自体は implementation start / issue finish / phase completion authority にならない。
  - Accepted ADR は architecture decision authority を持ち得るが、implementation readiness / phase promotion authority は canonical docs への反映後に成立する。
  - `reflected_to` は実際に canonical artifact へ反映済みの対象だけを表し、予定先は `intended_targets` で表す。
- 解決済み判断:
  - post-run diff guard は今回 runtime helper として最小実装する。helper は delegated output の採用資格を判定するだけで、adoption ledger や canonical artifact を更新しない。
  - system-architect / implementation-planner の static adapter は read-only fallback ではなく、全 scope-local `discussions/` への scoped write capability を持つ delegated authoring surface として扱う。canonical docs、implementation files、tests、config、secrets への write は引き続き禁止する。
  - `delegated-authoring scoped-context --discussion-file` は標準経路から外すだけでなく削除する。役割を終えた exact-file context generation code / tests / docs は、コード清潔性のために残さない。
- 行わない:
  - Sub-agent に canonical artifact の authoring authority / promotion authority / reviewer pass claim を与えない。
  - Per-agent directory や run directory を `discussions/` 配下に作らない。

## 非交渉制約
- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は sub-agent が直接編集しない。
- Sub-agent は initiative / epic / issue の scope-local `discussions/` 直下に限り、flat Markdown draft / analysis / discussion-local report を直接作成・編集できる。
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
  - 契約: canonical docs や implementation files は編集しない。一方で、initiative / epic / issue の scope-local `discussions/` direct child に限り、命名規則準拠の flat Markdown draft / analysis / discussion-local report を直接作成できる。
  - 補足: static `.codex/agents/*.toml` は、この 2 role に all discussions write capability を事前付与する。run ごとに agent 設定や permission context を生成・注入する方式は標準経路にしない。
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
  - 前提: initiative / epic / issue の scope-local `discussions/` が存在する。
  - 操作: system-architect / implementation-planner の output contract と execution permission contract を確認する。
  - 期待結果: system-architect / implementation-planner は全 scope-local `discussions/` 直下に `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` の flat Markdown draft / analysis / discussion-local report を直接作成できる。read-only specialist と同列に扱われず、run ごとの exact file context generation を標準経路として要求されない。
  - 観測点: shipped skills、adapters、discussion rules、permission / execution path tests。
- AC-002a: Obsolete exact-file context implementation removal
  - アクター: maintainer / dev-coder
  - 前提: S04 exact-file scoped-context implementation が存在する。
  - 操作: runtime command、application helper、parser binding、tests、adapter / skill / workflow docs を検索・点検する。
  - 期待結果: `delegated-authoring scoped-context --discussion-file` の command path、context TOML generation、exact-file write-root tests、runtime scoped context guidance は削除されている。deprecated / diagnostic fallback として残っていない。
  - 観測点: runtime diff、asset tests、CLI tests、`rg` inspection。
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
  - 期待結果: 許可 diff は scope-local `discussions/` 直下の naming-rule compliant Markdown create/update のみである。canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.env*`、nested dirs、symlinks、non-Markdown、delete、rename、baseline 時点で dirty/untracked な inspected discussion entry、新規 discussion の non-editable state claim があれば delegated output は rejected / ineligible になる。
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
- EC-001: Static adapter cannot express all discussions glob
  - 条件: `.codex/agents/*.toml` だけでは `spec-dock/initiatives/**/discussions/` 相当の write を静的に表現できない。
  - 期待: run ごとの exact file context generation へ戻さず、host permission model の表現力を確認した上で最小の代替案を選ぶ。`delegated-authoring scoped-context` を fallback として復活させず、`spec-dock/initiatives` 全体や repo-wide write のように canonical docs まで含む広い write root も採用しない。
  - 観測点: adapter contract、permission feasibility evidence、report ledger、tests / inspection。
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
  - 入力: Active issue scope、approved requirement、source docs、scope-local `discussions/` directory。
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
  - 判断: system-architect / implementation-planner は static adapter で全 scope-local `discussions/` への write capability を持つ。canonical docs write は常に禁止し、`spec-dock/initiatives` 全体や repo-wide write のような broad write は採用しない。run ごとに agent 設定や permission context を書き換える方式は標準経路にしない。
  - 理由: file-based context persistence を重視する delegated authoring では、sub-agent が複数 initiative / epic / issue の `discussions/` に連続して draft を残せる必要がある。post-run diff guard は broad permission の正当化ではなく、delegated output の採用資格を判定する安全弁である。役割を終えた exact-file context generation code は将来の誤用と設計誤読を招くため削除する。
  - 影響範囲: `.codex/agents/*.toml`、skills、workflow docs、runtime delegated_authoring parser / command / application、tests、diff-guard の inspected discussions handling。

## 追加要件 S06: Discussion-local artifact draft creation

### 背景
- S05 により、`system-architect` / `implementation-planner` は canonical docs ではなく scope-local `discussions/` に draft / analysis / discussion-local report を作成できる権限境界になった。
- しかし現行 `spec-dock new doc` で作成できる discussion doc type は `adr` / `disc` / `research` / `interview` / `scratch` のみであり、canonical `requirement.md` / `design.md` / `plan.md` の scope-specific template を discussion-local draft として作成する正規コマンドがない。
- `disc` や `research` へ自由記述するだけでは、initiative / epic / issue ごとに異なる requirement / design / plan template の構造を再利用できず、delegated authoring の draft artifact としての品質と機械的識別性が不足する。

### 追加スコープ
- `spec-dock new doc` に、discussion-local artifact draft を作成する doc type を追加する。
  - 必須: `draft-requirement`
  - 必須: `draft-design`
  - 必須: `draft-plan`
- `draft-requirement` は対象 scope kind に応じて既存 canonical requirement template を source として使う。
  - initiative -> `templates/initiative/requirement.md`
  - epic -> `templates/epic/requirement.md`
  - issue -> `templates/issue/requirement.md`
- `draft-design` は対象 scope kind に応じて既存 canonical design template を source として使う。
  - initiative -> `templates/initiative/design.md`
  - epic -> `templates/epic/design.md`
  - issue -> `templates/issue/design.md`
- `draft-plan` は対象 scope kind に応じて既存 canonical plan template を source として使う。
  - initiative -> `templates/initiative/plan.md`
  - epic -> `templates/epic/plan.md`
  - issue -> `templates/issue/plan.md`
- 生成先は既存 discussion rule と同じ flat layout とする。
  - `discussions/<ts>-draft-requirement-<slug>.md`
  - `discussions/<ts>-draft-design-<slug>.md`
  - `discussions/<ts>-draft-plan-<slug>.md`
  - same-second collision は既存通り `discussions/<ts>-<nn>-draft-requirement-<slug>.md` / `discussions/<ts>-<nn>-draft-design-<slug>.md` / `discussions/<ts>-<nn>-draft-plan-<slug>.md`

### 追加非スコープ
- canonical `requirement.md` / `design.md` / `plan.md` の直接作成・直接編集権限を sub-agent に与えない。
- `new draft` など別系統の command surface は追加しない。
- `disc --template design` のように既存 `disc` / `research` の variant として draft artifact を埋め込まない。
- `discussions/` 配下に per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を作らない。
- `templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` のような draft 専用テンプレートを追加しない。canonical template との二重管理を避けるため、既存 `templates/{initiative,epic,issue}/{requirement,design,plan}.md` を唯一の template source とする。

### 追加受け入れ条件
- AC-012: draft-requirement creation
  - アクター: CLI user / delegated authoring role
  - 前提: initiative / epic / issue のいずれかの scope が存在する。
  - 操作: `./spec-dock/scripts/spec-dock new doc draft-requirement --<scope-kind> <id> --title "<title>"` を実行する。
  - 期待結果: 対象 scope の `discussions/` 直下に naming-rule compliant な `draft-requirement` Markdown が作成され、対象 scope kind に対応する canonical requirement template source が draft body として使われる。
  - 観測点: created path、rendered content、tests。
- AC-013: draft-design creation
  - アクター: CLI user / delegated authoring role
  - 前提: initiative / epic / issue のいずれかの scope が存在する。
  - 操作: `./spec-dock/scripts/spec-dock new doc draft-design --<scope-kind> <id> --title "<title>"` を実行する。
  - 期待結果: 対象 scope の `discussions/` 直下に naming-rule compliant な `draft-design` Markdown が作成され、対象 scope kind に対応する canonical design template source が draft body として使われる。
  - 観測点: created path、rendered content、tests。
- AC-014: draft-plan creation
  - アクター: CLI user / delegated authoring role
  - 前提: initiative / epic / issue のいずれかの scope が存在する。
  - 操作: `./spec-dock/scripts/spec-dock new doc draft-plan --<scope-kind> <id> --title "<title>"` を実行する。
  - 期待結果: 対象 scope の `discussions/` 直下に naming-rule compliant な `draft-plan` Markdown が作成され、対象 scope kind に対応する canonical plan template source が draft body として使われる。
  - 観測点: created path、rendered content、tests。
- AC-015: canonical template source without duplicate draft templates
  - アクター: maintainer / reviewer
  - 前提: `draft-requirement`、`draft-design`、または `draft-plan` が作成された。
  - 操作: template source と generated file を確認する。
  - 期待結果: generated draft は対象 scope kind の既存 canonical template を render した内容であり、draft 専用 template file を source にしない。draft であることは `discussions/` 配置、`draft-*` filename、report adoption ledger、post-run diff guard によって扱う。
  - 観測点: generated file、template source path、tests、spec-reviewer。
- AC-016: validation and diff-guard compatibility
  - アクター: maintainer
  - 前提: `draft-requirement` / `draft-design` / `draft-plan` discussion docs が存在する。
  - 操作: `validate`、`sync`、`delegated-authoring diff-guard`、relevant tests を実行する。
  - 期待結果: `draft-requirement` / `draft-design` / `draft-plan` filename は valid discussion Markdown として扱われ、canonical artifact としては扱われない。diff-guard は valid draft create/update を allowed discussion output として扱い、forbidden paths は従来通り拒否する。
  - 観測点: `tests/cli_runtime/test_new.py`、`tests/cli_runtime/test_runtime_new_doc_s09.py`、`tests/cli_runtime/test_validate.py`、`tests/cli_runtime/test_delegated_authoring.py`。

### 追加入力→出力例
- EX-003: initiative requirement draft
  - 入力: `./spec-dock/scripts/spec-dock new doc draft-requirement --initiative init-local-00003 --title "Delegated Authoring Requirement Draft"`
  - 出力: `initiatives/init-local-00003-.../discussions/<ts>-draft-requirement-delegated-authoring-requirement-draft.md`
  - 内容: `templates/initiative/requirement.md` を直接 source として render した内容。draft 専用 envelope は付与しない。
- EX-004: issue design draft
  - 入力: `./spec-dock/scripts/spec-dock new doc draft-design --issue iss-00127 --title "Static Discussion Write Design Draft"`
  - 出力: `issues/iss-00127-.../discussions/<ts>-draft-design-static-discussion-write-design-draft.md`
  - 内容: `templates/issue/design.md` を直接 source として render した内容。draft 専用 envelope は付与しない。
- EX-005: epic plan draft
  - 入力: `./spec-dock/scripts/spec-dock new doc draft-plan --epic epic-00112 --title "Delegated Authoring Plan Draft"`
  - 出力: `epics/epic-00112-.../discussions/<ts>-draft-plan-delegated-authoring-plan-draft.md`
  - 内容: `templates/epic/plan.md` を直接 source として render した内容。draft 専用 envelope は付与しない。
