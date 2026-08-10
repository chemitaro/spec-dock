---
種別: ADR（Architecture Decision Record）
ID: "20260701t055644z-adr"
タイトル: "Artifacts Future Only Command Unification"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259"]
template: "adr"
authority: "accepted"
derived_from:
  - "../discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md"
  - "../discussions/20260701t043624z-interview-delegated-authoring-artifact-boundary.md"
  - "../discussions/20260701t044839z-interview-blank-versus-scratch-artifact-template.md"
  - "../discussions/20260701t050929z-interview-adr-artifact-boundary.md"
  - "../discussions/20260701t051314z-interview-future-adr-command-surface.md"
  - "../discussions/20260701t052324z-interview-draft-artifact-command-boundary.md"
  - "../discussions/20260701t052702z-interview-new-doc-removal-failure-mode.md"
  - "../discussions/20260701t055220z-interview-legacy-discussions-validation-boundary.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260701t055644z-adr Artifacts Future Only Command Unification

## 位置づけ
- 用途: Phase 2 の `artifacts/` future-only adoption と command surface を固定する。
- この ADR は Epic-level decision であり、後続 Issue の requirement / design / plan / acceptance criteria の前提にする。
- この ADR 自体は Phase 2 実装前の bootstrap artifact として、将来の `new artifact adr` と同じ intended destination である `artifacts/` 配下に直接作成した。

## ADR 化基準
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- ADR として残す理由:
  - `discussions/` から `artifacts/` への移行、`new doc` の完全削除、ADR / draft / delegated authoring output の command 統一は、複数 Issue と将来の agent workflow に影響する長期 contract である。

## 結論（Decision）
- Phase 2 は future working artifacts の標準作成先を `artifacts/` に切り替える。
- 既存 `discussions/` は移動・rename・link rewrite せず、そのまま残す。
- 既存 `discussions/` は legacy surface として valid / readable / link-stable に維持する。
- 新規 artifact 作成 command は `spec-dock new artifact <type> --{initiative|epic|issue} ...` に統一する。
- `new doc` は compatibility shim / alias を置かず、parser / help / command registry から完全削除する。
- `new artifact` は ADR と draft artifacts を含むすべての future artifact creation を扱う。
- 新規 ADR original は `artifacts/` に作成する。
- 既存 `discussions/` 配下の ADR original は移動しない。
- ADR mirror collection は legacy `discussions/` と future `artifacts/` の両方から ADR originals を収集する。
- Delegated authoring / sub-agent draft / scope-local direct-write output も `artifacts/` に移行する。
- Delegated authoring の permission boundary、diff guard、validation、safety checks は `artifacts/` direct child を基準に切り替える。
- `draft-requirement` / `draft-design` / `draft-plan` も `new artifact` で作成し、`artifacts/` に出力する。
- Draft artifacts は safety-sensitive artifact type として扱い、現行の `.assurance.json` / authorized profile 検査、profile-specific template selection、missing / stale / invalid 時の no-write fail-closed behavior を維持する。
- `artifacts/` の freeform / raw capture 用 template は `blank` に統一する。
- `scratch` は new artifact catalog に含めず、既存 `new doc scratch` / existing `discussions/` compatibility の legacy type として残す。
- 既存 `discussions/` の malformed discussion-intent filename / duplicate doc_id validation は fail として維持する。
- `artifacts/` には別途 strict filename / duplicate validation を追加する。

## 背景（Context）
- 現在の `spec-dock` は working docs を scope-local `discussions/` 配下に作成している。
- `discussions/` は名前に反して、research、interview、scratch、draft、decision candidate、evidence、ADR などを含む working artifact store として使われている。
- Phase 2 の目的は、今後作成する working artifacts の標準作成先をより抽象的な `artifacts/` に切り替えること。
- 初期 ZIP 案では `new doc` compatibility、ADR / draft-* exclusion、6 種 artifact template catalog が提案されていた。
- ユーザー interview により、初期案から以下を変更した。
  - `new doc` compatibility は不要。
  - ADR と draft-* も `new artifact` に統一する。
  - Delegated authoring output も `artifacts/` に移行する。
  - Future ADR original は `artifacts/` に置き、legacy ADR original は `discussions/` に残す。

## 選択肢（Options considered）
- Option A: compatibility-only legacy with `new doc` preserved
  - 概要:
    - 既存 `discussions/` を残し、新規 generic artifacts だけ `new artifact` に移す。`new doc` は互換 command として残す。
  - 良い点:
    - 初期 ZIP 案に近く、変更範囲が小さい。
  - 悪い点 / 制約:
    - command surface が二重化し、agent guidance が曖昧になる。
  - 棄却理由:
    - ユーザーが compatibility として `new doc` を残す必要はないと明示した。
- Option B: command unification under `new artifact`
  - 概要:
    - ADR、draft-*、delegated authoring output を含め、future artifact creation を `new artifact` に統一する。
  - 良い点:
    - Future command surface が明確になる。
    - `artifacts/` adoption が docs guidance だけでなく runtime contract になる。
  - 悪い点 / 制約:
    - 実装範囲が広い。
    - ADR mirror、draft assurance/profile checks、delegated authoring diff guard の切替が必要。
  - 採用理由:
    - ユーザーが command unification と `new doc` 完全削除を明示した。
- Option C: hard migration including existing discussion files
  - 概要:
    - 既存 `discussions/` を `artifacts/` へ移動・rename する。
  - 良い点:
    - 最終形が単純になる。
  - 悪い点 / 制約:
    - 既存リンクや historical evidence を壊す。
  - 棄却理由:
    - 既存 `discussions/` の rename / move / link rewrite は行わない方針と矛盾する。

## 判断理由（Rationale）
- `artifacts/` は今後の working artifact / evidence / delegated output の作成面として明確に使う。
- `new doc` を残すと、agent が新旧 command を混同し、future-only adoption の徹底が弱くなる。
- ADR と draft-* を例外扱いすると、最も重要な decision / draft surfaces だけが旧 command に残り、workflow docs と runtime contract が分裂する。
- Draft artifacts は通常 template ではなく safety-sensitive output なので、`new artifact` に統一しても existing assurance/profile checks をそのまま保持する。
- Existing `discussions/` は歴史的証跡として価値があるため、移動せずに validation と mirror collection の対象として扱う。
- ADR mirror は decision discovery のための projection なので、新旧 original location の両方を収集する必要がある。

## 影響（Consequences）
- Positive:
  - Future artifact creation command が `new artifact` に一本化される。
  - `artifacts/` の意味が runtime / docs / skills / validation / delegated authoring で揃う。
  - New node scaffolds、delegated authoring、ADR、draft artifacts の output location が将来形として統一される。
- Negative / Debt:
  - Initial ZIP plan より implementation scope が大きい。
  - Existing `new doc` tests / docs / skills / commands を広く置き換える必要がある。
  - Bootstrapping phase では `new artifact` が未実装のため、この ADR や interview は legacy command または direct write を使って作成されている。
- 影響範囲:
  - Runtime CLI parser / command registry
  - artifact domain model / filename parser / generator
  - templates catalog
  - node scaffolding
  - validation / sync / ADR mirror collection
  - delegated authoring diff guard
  - workflow docs / skills / README
  - CLI and unit tests
- Migration / rollback:
  - Existing `discussions/` files are preserved.
  - Rollback can reintroduce `new doc` command, but no existing file move is required because legacy `discussions/` remains untouched.
  - New `artifacts/` outputs would remain working artifacts and can be read independently.
- Follow-ups / Issues:
  - Define artifacts policy and ADR adoption in Epic canonical docs.
  - Implement artifact domain model / filename contract including ADR and draft-*.
  - Add artifacts templates including `blank`, ADR, decision-candidate, delegated evidence-friendly templates, and safety-sensitive draft generation.
  - Add `new artifact` command and remove `new doc`.
  - Switch new node scaffolds to `artifacts/`.
  - Update validation / sync / ADR mirror / agent projections.
  - Update delegated authoring diff guard and workflow docs.
  - Dogfood with artifacts without migrating existing `discussions/`.

## 参考（References）
- Related interviews:
  - `../discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md`
  - `../discussions/20260701t043624z-interview-delegated-authoring-artifact-boundary.md`
  - `../discussions/20260701t044839z-interview-blank-versus-scratch-artifact-template.md`
  - `../discussions/20260701t050929z-interview-adr-artifact-boundary.md`
  - `../discussions/20260701t051314z-interview-future-adr-command-surface.md`
  - `../discussions/20260701t052324z-interview-draft-artifact-command-boundary.md`
  - `../discussions/20260701t052702z-interview-new-doc-removal-failure-mode.md`
  - `../discussions/20260701t055220z-interview-legacy-discussions-validation-boundary.md`
- External planning pack:
  - `/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip`
