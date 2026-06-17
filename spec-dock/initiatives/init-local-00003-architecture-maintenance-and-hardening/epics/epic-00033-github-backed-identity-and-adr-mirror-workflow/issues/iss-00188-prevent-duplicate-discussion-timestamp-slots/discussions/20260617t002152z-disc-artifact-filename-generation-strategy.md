---
種別: disc
ID: "20260617t002152z-disc"
タイトル: "Artifact Filename Generation Strategy"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連: []
authority: "proposed"
derived_from:
  - "20260617t000227z-research"
  - "20260617t000333z-interview"
reflected_to: []
---

# 20260617t002152z-disc Artifact Filename Generation Strategy

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - SpecDock-provided skills / workflows が `discussions/` artifact filename を手作業で組み立てる経路をなくす。
  - Runtime/script 側で discussion artifact filename allocation と write を担い、skills は semantic input（doc type, scope, title, template/body, metadata）だけを渡す。
  - 通常の連続生成では suffix をなるべく出さず、suffix は clock collision / concurrent race / non-advancing clock の safety fallback として残す。
- この synthesis が必要な理由:
  - GitHub issue #188 の再現は duplicate timestamp を validator が検出したものだが、root cause は validator ではなく generation path にある。
  - User clarification により、PR repair batch / repair unit などの skill/workflow artifact generation を今回 issue scope に含めることが確定した。
  - Timestamp grammar / waiting / suffix fallback は durable naming contract に影響するため、requirement/design/plan へ反映する前に選択肢を整理する必要がある。

## derived question sheets / research (必須)
- `interview`:
  - `20260617t000333z-interview-scope-boundary-for-timestamp-collision-prevention.md`
- `research`:
  - `20260617t000227z-research-timestamp-collision-source-grounding.md`
- その他の根拠:
  - `spec-dock/docs/reference_naming.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `deep-consultant`: keep current second-precision grammar for #188; add runtime wait-on-collision before suffix fallback; remove shipped skill guidance that manually constructs `<ts>-...` paths.

## synthesis (必須)
- 合意済みのこと:
  - 手作業で `<ts>-...` filename を作る skill/workflow guidance は今回の root problem として扱う。
  - `discussions/` artifact は SpecDock runtime/script が filename allocation して作るべき。
  - Suffix fallback は残す。ただし通常の連続生成では suffix が出にくい設計にする。
  - Filename を無駄に長くしすぎない。
- 未合意 / 未確定のこと:
  - Timestamp grammar を変えるか、既存 grammar のまま wait-on-collision で避けるか。
  - PR repair batch / repair unit 用に `new doc` へ external template/body support を追加するか、別 command/helper を追加するか。
- source-grounded に解決できたこと:
  - Existing `new doc` path already has create lock, suffix allocator, duplicate guard, and parallel create tests.
  - Existing skill guidance still tells agents to create timestamped target names such as `<ts>-disc-pr-repair-batch.md`, which can lead to timestamp reuse.

## 選択肢 / tradeoff (必須)
- Option A:
  - Keep current second-precision grammar and add wait-on-collision before suffix fallback.
  - Pros:
    - Public filename grammar changes minimally.
    - Existing files and docs stay conceptually aligned.
    - Suffix appears only after bounded wait fails or clock does not advance.
  - Cons:
    - With second precision, avoiding suffix can require waiting up to nearly 1 second per extra artifact.
    - Batch workflows that create several artifacts may feel unnecessarily slow.
    - Fake/frozen test clocks must fall back to suffix or receive special handling.
- Option B:
  - Extend generated timestamp precision by two decimal digits before `z` (centisecond / 10ms tick), keep old second-precision names valid, and add short wait/retry before suffix fallback.
  - Pros:
    - Normal consecutive artifacts usually sort chronologically without suffix.
    - Wait duration can be around 10ms per collision instead of up to 1s.
    - Filename length increases only by 2 characters.
    - Existing suffix fallback remains as safety mechanism.
    - Existing old files can remain valid if validator/parser accept both timestamp forms.
  - Cons:
    - Durable naming grammar changes and docs/tests must be updated.
    - Parent epic E-RQ-003 currently states second precision, so issue docs must explicitly justify the refinement.
    - All parsers that understand discussion timestamps must be checked.
- Option C:
  - Replace `z` with one base-N sub-second token or otherwise encode fractional time in a single character.
  - Pros:
    - Very compact.
    - Could preserve near-chronological ordering if alphabet is carefully chosen.
  - Cons:
    - `z` currently communicates UTC and is embedded in docs/tests/regexes.
    - A custom alphabet makes filenames less obvious and more surprising.
    - The gain over two decimal digits is small relative to complexity.
- Option D:
  - Add a public batch artifact allocator API and keep timestamp grammar unchanged for now.
  - Pros:
    - Could allocate multiple names with one consistent strategy.
    - Useful long-term for generated workflows.
  - Cons:
    - Larger product/API design.
    - Does not by itself solve suffix sort order unless paired with A or B.

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `requirement.md`: manual timestamped filename construction by shipped skills/workflows is forbidden for new discussion artifact generation.
  - `requirement.md`: generated artifacts must be created through SpecDock runtime/script-owned allocator/writer.
  - `design.md`: introduce an allocator/writer surface that can create custom `disc` artifacts from a skill-local template or supplied body without caller-provided filename.
  - `design.md`: prefer Option B for compact normal-case chronological names, while keeping suffix fallback.
  - `plan.md`: tests for PR repair batch + repair unit created in rapid sequence without duplicate timestamp slot.
  - `plan.md`: contract tests or text checks that shipped skill guidance no longer instructs agents to reuse `<ts>` manually.
- まだ proposal に留める理由:
  - Canonical requirement/design/plan have not yet been rewritten and reviewed.
  - Deep consultant recommended a smaller #188 scope than this draft's initial Option B preference: keep timestamp grammar unchanged and solve normal-case suffixes through runtime-owned wait/retry.

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Scope / non-scope / acceptance criteria for generated artifact creation.
- `design.md`:
  - Command/API shape and timestamp allocation strategy.
- `plan.md`:
  - Implementation steps and test obligations.
- `ADR`:
  - Probably not required if accepted as refinement of discussion timestamp contract. Consider ADR only if replacing `z` or changing identity semantics.
- `report.md` Evidence Adoption Ledger:
  - Adopt user interview and this synthesis into canonical issue docs.

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - medium
- surprising without context:
  - no for centisecond digits; yes for replacing `z` with custom alphabet
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`

## 推奨案 (必須)
- Primary recommendation:
  - Add/extend a SpecDock runtime command path that creates discussion artifacts from semantic inputs without caller-provided filename. For PR repair artifacts, the skill should call this path with doc type `disc`, scope issue id, title/slug, and either a skill-local template/body source plus replacement metadata. The skill must not instruct agents to handcraft `<ts>-...` paths.
- Timestamp recommendation:
  - Prefer Option A for #188: keep the existing `yyyymmddthhmmssz` grammar and add runtime-owned wait-on-collision before suffix fallback.
  - Under the create lock, if the generated second-level timestamp slot is already used, sleep until the clock reaches the next second and retry within a bounded budget. If the clock does not advance, the wait budget is exhausted, or another writer still races, fall back to the existing suffix allocation.
  - Defer Option B (centisecond / 10ms timestamp digits) to a later issue or ADR only if real batch workflows prove that waiting up to roughly one second per extra artifact is too slow.
- Rationale:
  - It addresses the confirmed root cause: shipped skills/workflows should not manually create timestamped filenames.
  - It keeps the current durable naming grammar stable and avoids parser/docs/test churn that is not necessary for the first fix.
  - It keeps filenames shortest in the normal path and preserves `z` as UTC marker.
  - It maintains suffix fallback for safety and compatibility.

## 推奨反映先 (必須)
- `requirement.md`:
  - MUST: no manual timestamped filename construction in shipped skill/workflow guidance for new discussion artifacts.
  - MUST: runtime/script-owned allocator/writer creates discussion artifacts.
  - MUST: normal rapid sequential generation avoids duplicate timestamp slots and usually avoids suffix.
  - MUST: suffix remains fallback.
- `design.md`:
  - Add command/API shape for custom generated `disc` artifacts.
  - Update timestamp allocation strategy to wait/retry before suffix fallback while preserving existing parser grammar.
  - Update PR repair skill guidance to use generator path.
- `plan.md`:
  - S01: canonicalize artifact generator surface.
  - S02: timestamp allocation normal-case no-suffix strategy.
  - S03: update PR repair skill/provider assets.
  - S90/S99: docs and validation.
- `ADR`:
  - none unless grammar change is judged larger than issue-local refinement.
- `report.md` Evidence Adoption Ledger:
  - adopt `research`, `interview`, and this `disc`.

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Replace `z` with custom alphabet token: rejected for readability / surprise / parser complexity.
  - Centisecond / 10ms timestamp digits in #188: not adopted initially because the root cause can be fixed without changing durable filename grammar.
- deferred:
  - Full public batch allocation API: defer unless implementation proves a single-artifact generator cannot support PR repair use cases.
  - Centisecond / 10ms timestamp grammar: reconsider if runtime-owned wait-to-next-second makes common generated-artifact workflows measurably slow.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Rewrite issue `requirement.md` with adopted scope and acceptance criteria.
  - Then draft design with command/API shape and timestamp allocation decision.
  - Then plan step-by-step implementation with red tests.
- 追加で作る discussion docs:
  - none currently. Add another `disc` only if deep consultant identifies a materially different recommendation.
