---
種別: disc
ID: "20260524t133442z-01-disc"
タイトル: "Scoped Discussion Draft Authoring Requirement Draft"
状態: "superseded"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
親: ["iss-00127"]
関連: []
authority: "proposed"
derived_from:
  - "20260524t131259z-research-scoped-discussion-draft-authoring-model-analysis.md"
  - "20260524t133442z-adr-flat-scope-local-discussion-drafts.md"
superseded_by:
  - "20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md"
reflected_to: []
---

# 20260524t133442z-01-disc Scoped Discussion Draft Authoring Requirement Draft

## 位置づけ
- この document は、`iss-00127` の `requirement.md` / `design.md` / `plan.md` を書く前の要件・設計・実装作業ドラフトである。
- この document は正本ではない。ユーザー決定済み ADR と research をもとに、main orchestrator が canonical docs に反映すべき内容を整理する。
- この document は 2026-05-25 の追加方針により superseded になった。最新ドラフトは `20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md` を参照する。

## 議題 (必須)
- `epic-00112` の delegated authoring 実装を、重い write-capable canonical draft authoring model から、flat scope-local discussion draft model へ修正するために何を実装すべきか。
- 修正は、ユーザーが採用した次の運用ルールを満たす必要がある。
  - canonical docs は `requirement.md` / `design.md` / `plan.md` / `report.md`。
  - sub-agent は canonical docs を直接編集しない。
  - sub-agent output は対象 node の `discussions/` 直下へ flat timestamp-prefixed Markdown docs として置く。
  - delegated authoring 専用の agent directory / run directory / global draft store は採用しない。
  - JSON manifest / authority graph / session-invocation / acceptance_counted などの重い機械契約は user-facing workflow から退役する。

## 背景 (必須)
- 現行 v2 は `iss-00126` で write-capable delegated draft authoring を実装した。
- しかし現行 model は、sub-agent が条件付きで canonical `design.md` / `plan.md` を直接 draft 更新できる経路を持つ。
- 現行 model は manifest / permission-profile / probe-plan / session-invocation / input-authority JSON などを生成し、権限・証跡管理が複雑化している。
- ユーザーは、canonical docs の責任を main orchestrator に戻し、sub-agent は `discussions/` に draft / analysis を作る contributor にする方針を採用した。
- ADR `Flat Scope Local Discussion Drafts` により、run/task directory 例外も採らず、`discussions/` 直下 flat docs に統一することが決定済み。

## 選択肢 (必須)
- Option A: 現行 v2 を維持して manifest / Permission Profile / canonical draft write を改善する
  - Pros:
    - 既存 `iss-00126` 実装を大きく変えずに済む。
    - 実行時 ACL / hash / probe による監査性は高い。
  - Cons:
    - ユーザーの採用方針とずれる。
    - canonical docs の writer boundary が複雑になる。
    - draft の主役が文書ではなく機械証跡になる。
    - JSON / TOML / session evidence が workflow の理解を重くする。
- Option B: flat scope-local discussion draft model へ修正する
  - Pros:
    - 既存 `discussions/` 命名規則と一致する。
    - canonical docs の single-writer model が明確になる。
    - sub-agent は自律的に draft / analysis を作れるが、authority は持たない。
    - 人間と future agent が `discussions/` を時系列に読める。
    - JSON authority machinery を削減できる。
  - Cons:
    - runtime ACL だけでなく diff guard / review discipline が必要。
    - draft status の整理を怠ると stale discussion が残る。
    - 大量 document の検索性は将来 `list` helper などで補う必要があるかもしれない。

## 推奨案 (必須)
- Option B を採用する。
- `iss-00127` は、現行 v2 の補修ではなく、delegated authoring contract の単純化 issue として扱う。
- 実装の中心は、canonical edit 成功パスの削除、flat discussion draft output contract の追加、docs/skills/adapters/tests の整合である。

## 要件ドラフト
- RQ-001: Canonical docs single-writer
  - `requirement.md` / `design.md` / `plan.md` / `report.md` の canonical 更新は main orchestrator の責任である。
  - system-architect / implementation-planner / consultant / reviewer は canonical docs を直接編集しない。
- RQ-002: Scope-local flat discussions output
  - delegated authoring output は対象 initiative / epic / issue の `discussions/` 直下に置く。
  - output は既存 naming rule の `<ts>-<kind>-<slug>.md` に従う。
  - delegated authoring 専用の per-agent directory、run/task directory、global draft directory は新規生成しない。
- RQ-003: Lightweight Markdown metadata
  - draft docs は Markdown front matter または冒頭 header に、scope id、status、created_by_role、intended canonical target、canonical authority none、source refs を持つ。
  - JSON manifest / input-authority / session-invocation / acceptance_counted は user-facing acceptance contract から外す。
- RQ-004: Orchestrator adoption
  - draft にしかない内容は未反映として扱う。
  - main orchestrator が draft を採用・部分採用・却下し、採用部分だけ canonical docs に再記述する。
  - report には source discussion path、採用状態、反映先、理由を軽量に記録する。
- RQ-005: Safety guard
  - sub-agent 実行後、許可された差分が対象 `discussions/` docs のみであることを確認できる。
  - canonical docs / implementation files / tests / config / `.agents` / `.codex` / `.env*` に sub-agent が変更を残した場合は採用不可とする。

## 設計ドラフト
- Skill contract:
  - `spec-dock-system-architect` は `draft-design` / `research` / `disc` を `discussions/` 直下に作る role へ変更する。
  - `spec-dock-implementation-planner` は `draft-plan` / `risk-notes` / `validation-notes` を `discussions/` 直下に作る role へ変更する。
  - 両 skill から canonical `design.md` / `plan.md` を直接更新する成功パスを削除する。
- Adapter contract:
  - `.codex/agents/system-architect.toml` / `implementation-planner.toml` は canonical write を許可しない。
  - default Permission Profile は repo read + target `discussions/` write を基本にする。
  - `.codex/permission-probe-evidence` を delegated authoring output の自然な置き場として使わない。
- Discussion template:
  - 既存 `research` / `disc` / `adr` に加え、必要なら `draft-requirement` / `draft-design` / `draft-plan` kind を追加する。
  - ただし初期実装では既存 `disc` / `research` でも運用できるため、template kind 追加は design で要否を判断する。
- Runtime / CLI:
  - 重い `delegated-authoring manifest` command は新規成功パスとして使わない方向に整理する。
  - 将来 helper を残す場合は、`spec-dock new doc ...` の拡張として flat discussion doc を作る程度に留める。
- Validation:
  - `validate` / `issue finish` は canonical docs を authority として扱う。
  - discussion draft の存在だけで fail しない。
  - canonical docs が missing placeholder や unresolved adoption note を持つ場合は failure または warning にする。

## 実装対象ドラフト
- Provider-side authority:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- Shipped docs/templates:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/*`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
- Dogfooding mirrors:
  - `.agents/skills/...`
  - `.codex/agents/...`
  - `spec-dock/docs/...`
  - `spec-dock/templates/discussions/...`
- Runtime/tests:
  - `tests/test_init_update.py`
  - delegated-authoring runtime tests if existing command behavior is deprecated or replaced
  - discussion doc creation / naming tests if new kind is added

## 受け入れ条件ドラフト
- AC-001:
  - system-architect / implementation-planner の shipped skill に canonical docs direct edit success path が残っていない。
- AC-002:
  - delegated authoring output contract は対象 scope の `discussions/` 直下 flat Markdown docs を要求している。
- AC-003:
  - per-agent directory / run directory / `.codex/permission-probe-evidence` / global draft store を新規 delegated authoring output として生成しない。
- AC-004:
  - draft docs の最小 metadata は Markdown に閉じ、独立 JSON manifest を必須にしない。
- AC-005:
  - main orchestrator adoption と canonical rewrite が唯一の promotion path として docs に明記されている。
- AC-006:
  - provider assets と dogfooding mirrors が同期している。
- AC-007:
  - targeted tests と `spec-dock validate` が通る。

## 未決事項 (任意)
- `draft-requirement` / `draft-design` / `draft-plan` を新しい discussion doc kind として追加するか、既存 `disc` / `research` の title/slug 運用で始めるか。
- 既存 `spec-dock delegated-authoring manifest` command を deprecated にするか、内部 helper として残すか。
- draft adoption note を `report.md` のどの section に記録するか。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - ADR の決定を `iss-00127/requirement.md` の非交渉制約と受け入れ条件へ反映する。
  - この draft の要件・設計・実装対象・AC を `requirement.md` / `design.md` / `plan.md` に分割して昇格する。
  - spec-reviewer を fresh に通し、必要ならこの discussion に戻って補正する。
- 追加で作る discussion docs:
  - 現時点では不要。要件レビューで新論点が出た場合のみ `interview` / `disc` / `research` を追加する。
