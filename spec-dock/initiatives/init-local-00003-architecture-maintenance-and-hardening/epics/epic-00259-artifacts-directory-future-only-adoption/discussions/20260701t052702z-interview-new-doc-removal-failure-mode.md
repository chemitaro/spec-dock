---
種別: interview
ID: "20260701t052702z-interview"
タイトル: "New Doc Removal Failure Mode"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00259"
created_at: "2026-07-01THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t051314z-interview-future-adr-command-surface.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t052324z-interview-draft-artifact-command-boundary.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py"
  - "tests/cli_runtime/test_new.py"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t052702z-interview New Doc Removal Failure Mode

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Backward compatibility / migration policy for removed command.
  - `design.md`:
    - CLI parser behavior, error message contract, and command registry changes.
  - `plan.md`:
    - Test updates and migration guidance tasks.
  - `ADR`:
    - Command unification decision and compatibility consequence.
- chat 上の軽微な一問では足りない理由:
  - Removing `new doc` can mean several different user-visible behaviors. The choice affects help text, error code, migration diagnostics, and tests.

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner.
- 何を明確にする質問か:
  - How the CLI should behave when users run the legacy `new doc` command after Phase 2.
- 回答が後続判断へ与える影響:
  - Determines whether parser removes the subcommand entirely, keeps a fail-fast shim, or aliases to `new artifact`.

## 質問 (必須)
- pressure-test question:
  - Backward compatibility is not required, but do you want old `new doc` invocations to fail with a clear migration hint, disappear as an unknown command, or be accepted as an alias?
- 質問:
  - Phase 2 後に `spec-dock new doc ...` が実行された場合、CLI はどう振る舞うべきですか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - Current parser exposes `spec-dock new doc`.
  - Current command registry has `new_doc`, `CreateDiscussionDocRequest`, `render_new_doc_text`, and many tests expecting `discussions/` output.
  - User decision: backward compatibility is not required; future artifact creation should be unified under `new artifact`, including ADR and draft-*.
- local context で解決できたこと:
  - Removing all `new doc` behavior requires broad test/docs updates.
  - Keeping an alias would preserve compatibility, but conflicts with the user's stated desire that `new doc` is unnecessary.
- まだ人間判断が必要な理由:
  - Whether to keep a migration shim is a product UX decision, not derivable from code.

## 回答案 (必須)
- Option A:
  - Fail-fast migration shim: keep `new doc` parser entry only to return non-zero with a clear message such as "`new doc` was removed; use `new artifact <type> ...`". No files are written.
- Option B:
  - Hard removal: remove `new doc` from parser/help entirely. Running it fails as an unknown subcommand / argparse error, with no custom migration guidance.
- Option C:
  - Alias: keep `new doc` as a compatibility alias that internally calls `new artifact` and writes to `artifacts/`.

## Codex の分析 (必須)
- 判断軸:
  - Migration clarity, API cleanliness, implementation simplicity, and risk of accidental legacy use.
- tradeoff:
  - Option A is slightly more code than hard removal but gives future agents a precise correction. Option B is cleanest API removal but produces a generic error. Option C is user-friendly but contradicts removing compatibility.
- リスク:
  - Option B may make old instructions fail opaquely. Option C may keep old docs/skills alive longer than intended.
- 具体シナリオ / edge case:
  - A stale skill runs `new doc research --issue ...`; with Option A it fails before writing and tells the agent to use `new artifact research --issue ...`.

## Codex の推奨案 (必須)
- 推奨:
  - Option A.
- 理由:
  - It honors the decision that backward compatibility is not required because no legacy write occurs, while still preventing unhelpful generic argparse failures during the transition.
- 未回答時の影響:
  - Cannot finalize parser behavior, CLI tests, or migration diagnostics for `new doc`.

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option B を採用する。
- 回答:
  - 「オプションBを採用します。完全削除をOにしてください。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Existing legacy `discussions/` validation should remain strict, become read-only lenient, or be limited to ADR mirror sources only.

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `ADR`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが hard removal を明示採用した。Phase 2 後、`new doc` は parser/help から完全削除し、migration shim / alias は設けない。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `new doc` compatibility is not required. Phase 2 removes the `new doc` command surface entirely.
- `design.md`:
  - Parser/help/registry no longer expose `new doc`; legacy invocations fail as unknown subcommand / argparse errors. No migration shim and no alias are provided.
- `plan.md`:
  - Remove or rewrite `new doc` tests/docs/skills and add assertions that `new doc` is no longer available.
- `ADR`:
  - Command unification ADR must record hard removal of `new doc`.
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Adopted policy is stricter than the recommended migration shim. Future agents should not implement compatibility alias or custom migration guidance for `new doc`.

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
