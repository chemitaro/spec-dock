---
種別: disc
ID: "20260524t150117z-disc"
タイトル: "Scoped Discussion Draft Authoring Requirement Draft V2"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
親: ["iss-00127"]
関連: []
authority: "proposed"
derived_from:
  - "20260524t131259z-research-scoped-discussion-draft-authoring-model-analysis.md"
  - "20260524t133442z-adr-flat-scope-local-discussion-drafts.md"
  - "20260524t133442z-01-disc-scoped-discussion-draft-authoring-requirement-draft.md"
  - "fresh deep-consultant analyses 2026-05-24"
  - "user decision 2026-05-25"
  - "20260524t150916z-disc-fresh-consultant-review-v2-discussion-direct-write-model.md"
intended_targets:
  - "iss-00127 requirement.md"
  - "iss-00127 design.md"
  - "iss-00127 plan.md"
reflected_to: []
---

# 20260524t150117z-disc Scoped Discussion Draft Authoring Requirement Draft V2

## 位置づけ
- この document は、`iss-00127` の canonical `requirement.md` / `design.md` / `plan.md` を書く前の V2 要件・設計・実装作業ドラフトである。
- V1 draft は `20260524t133442z-01-disc-scoped-discussion-draft-authoring-requirement-draft.md` とし、この V2 が最新の discussion draft である。
- この document は canonical artifact ではない。main orchestrator が採用内容を canonical docs に再記述して初めて実行可能な仕様 authority になる。

## 議題 (必須)
- `epic-00112` の delegated authoring 実装を、canonical direct-write / manifest-heavy model から、scope-local flat discussion draft model へ反転する。
- ただし、fresh consultant が提案した `sub-agent proposal-only` は採用しない。
- system-architect / implementation-planner などの sub-agent は canonical docs を直接編集しない一方で、対象 scope の `discussions/` 直下に draft / analysis / report Markdown を直接作成・編集できる。
- この write permission は、agent が持つ揮発的 context を file-based project context として永続化し、伝言ゲームを減らすための harness engineering / context engineering 上の意図的な設計である。

## 背景 (必須)
- 現行 v2 実装は、manifest / Permission Profile / probe-plan / session-invocation / input-authority JSON/TOML を使い、条件付きで canonical `design.md` / `plan.md` の draft 更新を許可する。
- この model は安全性と監査性を重視したが、ユーザーが求めるシンプルな運用、agentic collaboration、file-based context persistence とずれている。
- 一方で、sub-agent が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集できるのは authority boundary として過剰である。
- 採用するバランスは、canonical docs は main orchestrator の single-writer、sub-agent draft は scope-local `discussions/` direct-writer である。
- accepted ADR は architecture decision authority を持ち得るが、implementation readiness / phase promotion authority は持たない。実行可能な仕様 authority は canonical docs への反映後に成立する。

## 選択肢 (必須)
- Option A: 現行 v2 の manifest / Permission Profile / canonical draft write model を維持する
  - Pros:
    - 実行時 ACL / hash / probe による監査性は高い。
    - 既存実装との差分は小さい。
  - Cons:
    - canonical writer boundary が複雑になる。
    - draft の主役が文書ではなく機械証跡になる。
    - user-facing workflow が重く、今回のシンプル化方針とずれる。
- Option B: sub-agent proposal-only / orchestrator-only discussion write
  - Pros:
    - 最も狭い write boundary になる。
    - host permission enforcement は単純になる。
  - Cons:
    - sub-agent の分析・設計判断が conversation context に滞留し、context compaction で失われやすい。
    - orchestrator が再転記する伝言ゲームが増える。
    - file-based context engineering として、specialist agent が persistent evidence を直接残せない。
- Option C: scope-local flat discussion direct-write model
  - Pros:
    - canonical docs single-writer と sub-agent evidence authoring を分離できる。
    - sub-agent の中間成果物を `discussions/` に直接永続化できる。
    - 既存 `discussions/` naming rule と一致し、per-agent / run directory を増やさない。
    - JSON/TOML manifest-heavy workflow を退役できる。
  - Cons:
    - proposal-only より write boundary は広い。
    - stale draft や forbidden diff の管理を report ledger / diff guard で補う必要がある。

## 推奨案 (必須)
- Option C を採用する。
- `iss-00127` は、現行 v2 の微修正ではなく、delegated authoring contract の反転 issue として扱う。
- 実装の中心は、canonical direct-write 成功パスの削除、sub-agent scope-local `discussions/` direct-write contract の明文化、旧 manifest command の非成功化、docs/skills/adapters/tests の整合である。

## 要件ドラフト
- RQ-001: Canonical artifacts are single-writer
  - `requirement.md` / `design.md` / `plan.md` / `report.md` の canonical 更新は main orchestrator の責任である。
  - system-architect / implementation-planner / consultant / reviewer は canonical artifacts を直接編集しない。
- RQ-002: Sub-agents may directly write scope-local discussion drafts
  - delegated authoring output は、対象 initiative / epic / issue の `discussions/` 直下に置く。
  - sub-agent は対象 scope の `discussions/` 直下に draft / analysis / report Markdown を直接作成・編集できる。
  - output は既存 naming rule の `<ts>-<kind>-<slug>.md` に従う。
  - slug は role-first / run-first ではなく、canonical target と論点を表す。
  - delegated authoring 専用の per-agent directory、run/task directory、global draft directory は新規生成しない。
  - sub-agent direct write は safety boundary ではなく、persistent proposal / evidence channel である。安全性は canonical single-writer、post-run diff guard、orchestrator adoption ledger、stale/rejected handling の組み合わせで成立する。
  - sub-agent は原則として discussion file を新規作成する。既存 discussion file の編集は main orchestrator が明示指定した proposed draft に限定する。
  - accepted ADR、superseded / stale / rejected / adopted 済み discussion file は sub-agent が直接編集しない。
- RQ-003: Discussion drafts are evidence, not phase authority
  - discussion draft は implementation start / issue finish / phase completion の根拠にならない。
  - accepted ADR は architecture decision authority を持ち得るが、implementation readiness / phase promotion authority は持たない。
  - main orchestrator が採用部分を canonical docs に再記述し、必要な reviewer gate を通して初めて実行可能な仕様 authority になる。
- RQ-004: Lightweight metadata, no manifest-heavy user-facing contract
  - sub-agent-created draft docs は既存 front matter を基本とし、`created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []` を持つ。
  - `reflected_to` は実際に反映済みの canonical artifact のみに使い、予定先は `intended_targets` に分ける。
  - `adoption_status` と `reflected_to` の authoritative source は main orchestrator が管理する `report.md` adoption ledger である。draft front matter は検索補助であり、promotion authority ではない。
  - sub-agent-created draft は `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己主張しない。
  - JSON/TOML manifest / input-authority / session-invocation / acceptance_counted / authority graph は user-facing acceptance contract から外す。
- RQ-005: Diff guard and adoption ledger
  - sub-agent 実行前に main orchestrator は dirty diff baseline を確認する。
  - sub-agent 実行後、許可 diff は対象 scope の `discussions/` 直下にある naming-rule compliant Markdown create/update に限定する。
  - canonical docs / implementation files / tests / config / `.agents` / `.codex` / `.env*` / nested `discussions/delegated-authoring/` / symlink / non-Markdown / delete / rename への変更があれば、その delegated output は rejected / ineligible とする。
  - main orchestrator が draft を採用・部分採用・却下・延期・stale と判断し、`report.md` に source discussion path、adoption status、反映先、理由、next action を軽量に記録する。
  - source artifact が draft 作成後に更新された場合、canonical target が draft 作成後に更新された場合、superseding draft がある場合、または adoption ledger が stale / blocked とした場合、draft は stale または要再確認として扱う。

## 設計ドラフト
- Skill contract:
  - `spec-dock-system-architect` は canonical `design.md` を直接更新しない。
  - `spec-dock-implementation-planner` は canonical `plan.md` を直接更新しない。
  - 両 skill は、対象 scope の `discussions/` 直下に draft / analysis / discussion-local report Markdown を作成・編集する role として記述する。
  - discussion-local report は `discussions/<ts>-<kind>-<slug>.md` の一種であり、canonical `report.md` ではない。
  - write eligibility を満たせない場合は blocked / ineligible とし、proposal-only を標準 fallback にはしない。ユーザーまたは orchestrator が明示した場合だけ read-only proposal として扱える。
- Adapter contract:
  - `.codex/agents/system-architect.toml` / `implementation-planner.toml` は canonical docs write を許可しない。
  - sub-agent の write surface は scope-local `discussions/` output に限定する。
  - static adapter で exact scope write enforcement が困難な場合でも、canonical docs direct write の成功パスは置かず、post-run diff guard を必須にする。
  - `.codex/permission-probe-evidence` を delegated authoring output の自然な置き場として使わない。
- Discussion template:
  - 初回実装では `draft-requirement` / `draft-design` / `draft-plan` kind を追加しない。
  - 既存 `disc` / `research` / `adr` と semantic slug / lightweight front matter で運用する。
  - 新 kind が必要になった場合は future issue で naming rules、templates、runtime、tests を同時に扱う。
- Runtime / CLI:
  - `spec-dock delegated-authoring manifest` は新規 user-facing success path として使わない。
  - 初回実装では deprecated / blocked / no artifact generation に変更し、既存 historical evidence は grandfathered として残す。
  - `discussions/delegated-authoring/<task_id>/` は新規生成しない。
- Validation / finish:
  - `validate` / `issue finish` は canonical docs を implementation authority として扱う。
  - discussion draft の存在だけでは fail しない。
  - delegated draft を canonical claim に使う場合、`report.md` の adoption ledger がないものは incomplete と扱う。

## 実装対象ドラフト
- Provider-side authority:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- Runtime:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py`
- Shipped docs/templates:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md`
  - `src/spec_dock/assets/spec_dock/templates/*/report.md`
- Dogfooding mirrors:
  - `.agents/skills/...`
  - `.codex/agents/...`
  - `spec-dock/docs/...`
  - `spec-dock/templates/...`
  - `spec-dock/scripts/...`
- Tests:
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_delegated_authoring.py`
  - `tests/domain_runtime/test_delegated_authoring.py`
  - discussion naming / validation tests only if affected by implementation

## 受け入れ条件ドラフト
- AC-001:
  - system-architect / implementation-planner の shipped skill と dogfooding mirror に、canonical docs direct edit success path が残っていない。
- AC-002:
  - delegated authoring output contract は、sub-agent が対象 scope の `discussions/` 直下に flat Markdown docs を直接作成・編集できることを明記している。
- AC-003:
  - per-agent directory / run directory / `.codex/permission-probe-evidence` / global draft store / `discussions/delegated-authoring/` を新規 delegated authoring output として生成しない。
- AC-004:
  - draft docs の metadata は Markdown front matter と report ledger に閉じ、独立 JSON/TOML manifest を必須にしない。
- AC-005:
  - sub-agent-created draft docs は `created_by_role`、`scope_id`、`source_paths`、`intended_targets`、`adoption_status: unreviewed`、`reflected_to: []` を持つ。
- AC-006:
  - sub-agent-created draft docs は `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` を自己主張しない。
- AC-007:
  - accepted ADR と canonical docs の authority 境界が明記されている。
- AC-008:
  - `reflected_to` に pending や予定を書かず、未反映の予定先は `intended_targets` または本文 next action に分離している。
- AC-009:
  - sub-agent は原則として新規 discussion file を作成し、既存 discussion file の編集は orchestrator が明示指定した proposed draft に限定される。
- AC-010:
  - accepted ADR、superseded / stale / rejected / adopted 済み discussion file は sub-agent workflow から直接編集されない。
- AC-011:
  - post-run diff guard が、許可された discussion draft 以外の変更を検出した場合、その delegated output を rejected / ineligible として扱うことを docs に明記している。
- AC-012:
  - main orchestrator adoption と canonical rewrite が唯一の promotion path として docs に明記されている。
- AC-013:
  - `spec-dock delegated-authoring manifest` は新規 user-facing success path として artifact を生成しない。
- AC-014:
  - provider assets と dogfooding mirrors が同期している。
- AC-015:
  - targeted tests、`spec-dock validate`、`spec-dock sync`、`spec-dock doctor`、`git diff --check` が通る。

## 未決事項 (任意)
- static adapter でどの粒度まで scope-local `discussions/` write を enforce できるか。実装時に過剰な broad write になる場合は post-run diff guard を必須安全弁とする。
- `report.md` adoption ledger の section 名と最小 field 名。
- post-run diff guard を runtime helper として実装するか、初回は orchestrator workflow docs に閉じるか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` へ反映する内容:
  - V2 の要件・設計・実装対象・AC を canonical docs に分割して昇格する。
  - `sub-agent proposal-only` を標準方針として採用しないことを明記する。
  - sub-agent `discussions/` direct write と canonical docs single-writer の境界を明記する。
  - accepted ADR と canonical docs の authority 境界を明記する。
- 追加で作る discussion docs:
  - V2 に対する fresh deep-consultant 分析を必要に応じて `research` または `disc` として記録する。
