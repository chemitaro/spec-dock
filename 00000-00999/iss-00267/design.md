---
種別: 設計書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00267 Workflow docs skills and README alignment — 設計

## 目的と判断
この Issue は、既に実装済みの `new artifact` / `artifacts/` future surface を、shipped workflow docs、rules、template guidance、README、repo-local / installed skills の説明面へ反映する。runtime behavior、validation behavior、scaffold behavior、delegated authoring diff guard は先行 Issue の責務であり、この Issue ではそれらを変更せず、利用者と agent が参照する guidance の矛盾を解消する。

`new doc` は future command として廃止済みであるため、新規作成手順として案内しない。ただし legacy `discussions/`、過去の discussion artifacts、runtime removal tests、historical examples は残り得る。残存参照は「future guidance」「legacy/historical/preservation」「removed-command/test evidence」「source/runtime identifier」のいずれかへ分類し、文脈なしに機械削除しない。

## 現行構造
- Provider-side docs:
  - `src/spec_dock/assets/spec_dock/docs/**` が shipped workflow / phase / reference guidance の source of truth。
  - `docs/rules/{initiative,epic,issue}/{artifacts,discussions}.md` は scope-local `artifacts/rules.md` / legacy `discussions/rules.md` symlink target。
  - `phase_*`、`workflow_*`、`authoring/*` には delegated authoring や長い調査ログの置き場所として旧 `discussions/` guidance が残る。
- Provider-side templates:
  - `src/spec_dock/assets/spec_dock/templates/README.md` と report templates は shipped scaffold の説明面。
  - report templates は先行 Issue で artifacts-aware になっているが、dogfooding mirror 側に古い内容が残る可能性がある。
- Provider-side installed skills:
  - `src/spec_dock/assets/install_root/.agents/skills/**` が installed agent skill の source of truth。
  - repo-local `.agents/skills/**` は dogfooding mirror / local installed surface として provider-side source と比較する。
- Top-level README:
  - repo の導入例と dogfooding説明に `new doc` / `discussions/` 旧記述が残る可能性がある。
- Dogfooding mirror:
  - `spec-dock/docs/**`、`spec-dock/templates/**` は consumer-side validation target。
  - provider-side source から派生する surface は、意図した差分でない限りこの Issue で整合させる。

## 変更方針
- Future creation guidance:
  - 新規 artifact 作成例は `./spec-dock/scripts/spec-dock new artifact <type> --{initiative|epic|issue} <id> --title "..."` に統一する。
  - ADR、research、interview、disc、decision-candidate、pr-repair-batch、Issue scope の draft-requirement / draft-design / draft-plan は `new artifact` catalog として案内する。
  - raw / untyped capture は `blank` を使う。`scratch` は legacy discussion type としてのみ扱う。
- Legacy `discussions/` wording:
  - `discussions/` は historical / legacy preservation surface と説明する。
  - 既存 `discussions/` は移動、rename、削除しない。
  - 過去判断や legacy ADR を読む文脈では `discussions/` 参照を残してよい。
  - 新規 working artifact / delegated output の推奨先として `discussions/` を案内しない。
- Removed `new doc` wording:
  - README、workflow docs、rules、skills の手順例から future `new doc` command examples を除去または `new artifact` へ更新する。
  - runtime removal tests、コード識別子、過去互換説明、historical changelog 的な文脈は残してよいが、future command に見えない説明を添える。
- Delegated authoring guidance:
  - system-architect / implementation-planner / delegated draft output は target scope の `artifacts/` direct child flat Markdown と説明する。
  - canonical docs は main orchestrator single-writer authority のまま。
  - delegated draft は evidence であり、Evidence Adoption Ledger と fresh reviewer pass を経てから canonical docs へ反映する。
- Provider / mirror parity:
  - Provider-side source を先に更新する。
  - Dogfooding mirror は shipped asset parity が期待される範囲で更新または差分理由を report に記録する。
  - `.agents/skills/**` と `src/spec_dock/assets/install_root/.agents/skills/**` は future guidance の矛盾を解消する。どちらか一方だけを更新する場合は理由を report に残す。

## 設計契約
| ID | 契約 | 対応 AC | 対象面 | 検証 |
|---|---|---|---|---|
| DES-267-001 | 新規 working artifact 作成 guidance は `new artifact` / `artifacts/` を示す | AC-267-001 | README / docs / rules / skills | `rg "new doc"` classification and docs inspection |
| DES-267-002 | `discussions/` は legacy / historical / preservation surface として説明され、新規作成先として推奨されない | AC-267-002 | docs / rules / skills | `rg "discussions"` classification |
| DES-267-003 | 残存 `new doc` references は removed-command test、legacy/historical reference、runtime/source identifier のいずれかに分類される | AC-267-003 | docs / tests / source / report | classification ledger |
| DES-267-004 | shipped skills と repo-local skills は delegated future output を `artifacts/` direct child と説明する | AC-267-004 | install_root skills / `.agents/skills` | skill inspection / provider-mirror comparison |
| DES-267-005 | template guidance は artifact catalog、draft-* issue-scope limitation、legacy discussions preservation と一致する | AC-267-001, AC-267-002, AC-267-005 | templates README / rules docs | docs inspection |
| DES-267-006 | dogfooding mirror は provider-side source と意図した範囲で整合し、差分は report に記録される | AC-267-004, AC-267-005 | `spec-dock/docs`, `spec-dock/templates`, `.agents/skills` | comparison / diff inspection |
| DES-267-007 | docs-only Issue として runtime behavior、tests semantics、scaffold logic を変更しない | AC-267-005 | source / tests | diff inspection |

## 対象ファイル境界
- Provider-side docs / rules:
  - `src/spec_dock/assets/spec_dock/docs/**`
  - 特に `phase_requirement.md`, `phase_design.md`, `workflow_*.md`, `reference_naming.md`, `rules/**`, `authoring/**`
- Provider-side template guidance:
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - docs-only wording in provider templates when future guidance is embedded in scaffold text
- Provider-side installed skills:
  - `src/spec_dock/assets/install_root/.agents/skills/**`
- Repo-local / dogfooding mirrors:
  - `.agents/skills/**`
  - `spec-dock/docs/**`
  - `spec-dock/templates/**`
- Repository README:
  - `README.md`
- Issue-level canonical evidence:
  - this Issue's `design.md`, `plan.md`, `report.md`

## 非対象 / 禁止事項
- Runtime command implementation、parser、registry、help generation の変更。
- `new artifact` catalog / filename grammar / artifact validation の再設計。
- Existing `discussions/` の移動、rename、削除、自動 migration。
- `new doc` の compatibility shim 追加または復活。
- Code / test changes unless a docs-only assertion or shipped asset parity test must be adjusted to reflect documentation wording.
- Per-Issue PR creation。PR は Epic closeout 後に 1 件だけ作成する。

## 分類方針
| 分類 | 意味 | 期待される処置 |
|---|---|---|
| Future guidance | 新規作業者/agent が現在の手順として読む説明 | `new artifact` / `artifacts/` へ更新 |
| Legacy preservation | 既存 `discussions/` や旧 artifact を読む、残す、検証する説明 | 残す。historical / legacy / preservation と明記 |
| Removed-command evidence | `new doc` が削除済みであることを示す tests / docs / diagnostics | 残す。future usage と誤読されない文脈に限定 |
| Runtime/source identifier | コード内の旧関数名、test name、migration fixture など | この docs Issue では原則変更しない |
| Ambiguous stale guidance | 文脈上 future 手順にも legacy 説明にも見える記述 | doc-writer が判断し、必要なら report Decision Ledger に記録 |

## テスト / レビュー戦略
- Inspection:
  - `rg -n "new doc|new artifact|discussions|artifacts"` を provider docs / skills / README / mirrors に対して実行し、残存参照を分類する。
  - `git diff --check` で Markdown formatting の基本不備を確認する。
- Provider / mirror:
  - provider-side source と repo-local mirror の意図した alignment を diff で確認する。
  - mirror を更新しない差分は report に理由を残す。
- Runtime safety:
  - docs-only diff であれば focused runtime tests は不要。source/tests に触れた場合のみ該当 focused tests を走らせる。
  - `./spec-dock/scripts/spec-dock validate` は最終確認として実行する。
- Review:
  - implementation 後に `spec-reviewer` で docs/spec alignment を確認する。
  - source/tests に触れた場合は `code-reviewer` / `qa-reviewer` も追加する。

## 後続 Issue への引き渡し
- `iss-00268` はこの guidance を前提に、dogfooding workspace で `new artifact` を使った integrated smoke と Epic closeout evidence を作成する。
- `iss-00268` は既存 `discussions/` を migration しないことを検証するため、この Issue で legacy wording を historical/preservation として残した箇所を参照できる。
