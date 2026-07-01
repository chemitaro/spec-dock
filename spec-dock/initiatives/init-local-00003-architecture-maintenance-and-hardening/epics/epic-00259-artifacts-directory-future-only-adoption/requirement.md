---
種別: 要件定義書（Epic）
ID: "epic-00259"
タイトル: "Artifacts Directory Future Only Adoption"
関連GitHub: ["#259"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["init-local-00003"]
---

# epic-00259 Artifacts Directory Future Only Adoption — 要件定義（何を、なぜ行うか）

## 目的（Initiative との紐づき）
- Initiative 目標 / 指標:
  - `init-local-00003` の architecture maintenance / governance / hardening の一環として、working artifact の source-of-truth 境界、作成 command、validation、sync / projection、agent workflow guidance を一貫した contract にする。
  - `discussions/` が議論以外の research / interview / draft / evidence / ADR も抱える現状を整理し、future working artifact surface を `artifacts/` に移す。
- この Epic が提供する能力:
  - 今後作成する working artifacts を `artifacts/` 配下へ作成する runtime / docs / skill / template contract。
  - 既存 `discussions/` を移動・rename・link rewrite せず、legacy evidence として valid / readable / link-stable に維持する互換境界。
  - `new doc` を残さず、ADR、draft artifacts、delegated authoring output を含めた future artifact creation を `new artifact` に統一する command surface。

## ユースケース
- 正常系:
  - maintainer / agent が `spec-dock new artifact <type> --issue <id> --title "..."` などを使い、対象 scope の `artifacts/` 直下に working artifact を作成できる。
  - old node に `artifacts/` が存在しない場合でも、`new artifact` が必要な directory / rules entry を on demand に作成して artifact を保存できる。
  - new initiative / epic / issue scaffold は future surface として `artifacts/` を持ち、`discussions/` を default scaffold として作成しない。
  - ADR discovery / mirror は legacy `discussions/` と future `artifacts/` の両方に存在する ADR original を収集できる。
  - delegated authoring / sub-agent draft output は `artifacts/` を scope-local output surface として使い、canonical docs へ直接書き込まない。
- 例外 / 運用シナリオ:
  - 既存 `discussions/` しか持たない node は引き続き validate / sync の対象として valid である。
  - malformed discussion-intent filename / duplicate discussion doc_id は legacy 側でも fail を維持する。
  - malformed artifact-intent filename / duplicate artifact id は `artifacts/` 側の strict validation で fail する。
  - `new doc` を呼び出した場合は、parser / help から完全削除済みの command として unknown subcommand / argparse error 相当で失敗する。custom migration hint、compatibility shim、alias は提供しない。

## エピック要件（Epic requirements）
- E-RQ-001: Future working artifact surface
  - 今後作成する working artifacts の標準作成先を `artifacts/` にする。
  - `artifacts/` は root canonical `requirement.md` / `design.md` / `plan.md` / `report.md` ではない。
  - `artifacts/` 内の多くの artifact は、canonical docs / accepted ADR / report evidence へ反映されるまで未採用または補助的な working evidence として扱う。
  - 例外として、`artifacts/` 内に作成された ADR original は、ADR workflow により `状態: "accepted"` / `authority: "accepted"` へ昇格した時点で ADR authority を持ち、ADR mirror collection の対象になる。
- E-RQ-002: Legacy discussions preservation
  - 既存 `discussions/` directory / files / links / ADR originals は移動、rename、削除、link rewrite、自動 migration しない。
  - 既存 `discussions/` は legacy working artifact surface として readable / valid / link-stable に維持する。
- E-RQ-003: Unified `new artifact` command surface
  - Future artifact creation は `spec-dock new artifact <type> --{initiative|epic|issue} <id> --title "..." [--slug ...]` に統一する。
  - `new doc` は parser / help / command registry から削除し、alias / shim / hidden compatibility command として残さない。
- E-RQ-004: Artifact type catalog
  - Artifact domain / filename / template-routing contract はこの Epic の accepted ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md` を authority とし、child Issue で policy を決めない。
  - `new artifact` は少なくとも `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`, `adr`, `draft-requirement`, `draft-design`, `draft-plan` を扱う。
  - `blank` は freeform / raw capture 用であり、filename に `blank` token を含めない。
  - `scratch` は future artifact catalog に含めず、legacy `discussions/` に存在する historical type として扱う。
- E-RQ-005: Safety-sensitive draft artifacts
  - `draft-requirement`, `draft-design`, `draft-plan` は `new artifact` で作成できるが、既存の `.assurance.json` / authorized profile 検査、profile-specific template selection、missing / stale / invalid 時の no-write fail-closed behavior を維持する。
  - `draft-requirement`, `draft-design`, `draft-plan` 用に独自の draft-only content templates を作らず、既存の requirement / design / plan template contract を再利用する。
  - Issue scope の `draft-design` / `draft-plan` は既存の Issue grade / authorized profile template selection を使う。
  - ADR だけ、draft だけ、delegated authoring だけを例外的に旧 surface へ残してはならない。
- E-RQ-006: Validation / sync / projection parity
  - validate は old-only (`discussions/` only), new-only (`artifacts/` only), mixed (`discussions/` + `artifacts/`) の各 layout を正しく扱う。
  - sync / `.agent` projection / ADR mirror は canonical docs、future artifacts、legacy discussions を混同しない。
- E-RQ-007: Provider-side source of truth and dogfooding
  - 実装変更は provider-side `src/spec_dock/assets/...` を正とし、dogfooding workspace `spec-dock/...` は検証・反映対象として扱う。
  - 最終段階で dogfooding により `artifacts/` 作成、legacy `discussions/` 非移行、validate / sync を確認する。
- E-RQ-008: Workflow and skill guidance alignment
  - workflow docs、rules、templates README、repo-local / shipped skills は `new artifact` と `artifacts/` future surface を案内する。
  - legacy `discussions/` は参照可能な historical / compatibility surface として説明し、新規作成先として推奨しない。

## エピック受け入れ条件（Epic acceptance criteria）
- E-AC-001: `new artifact` command creation
  - 前提:
    - 対象 workspace に initiative / epic / issue node が存在する。
  - 操作:
    - `spec-dock new artifact blank --issue <id> --title "Free form note"` を実行する。
  - 期待結果:
    - `<issue>/artifacts/<timestamp>-free-form-note.md` が作成され、filename に `blank` が含まれない。
    - frontmatter は `template: "blank"` を記録する。
  - 観測点:
    - CLI stdout, created path, file content, validate result.
- E-AC-002: typed artifact filename
  - 前提:
    - 対象 scope が存在する。
  - 操作:
    - `spec-dock new artifact research --epic <id> --title "Compatibility notes"` を実行する。
  - 期待結果:
    - `<epic>/artifacts/<timestamp>-research-compatibility-notes.md` が作成される。
  - 観測点:
    - created path and parser / validation tests.
- E-AC-003: `new doc` removal
  - 前提:
    - runtime command registry / help が利用可能である。
  - 操作:
    - `spec-dock new --help` と `spec-dock new doc ...` を確認する。
  - 期待結果:
    - help / parser に `new doc` が残っていない。
    - `new doc` は alias / shim として動作せず、unknown subcommand / argparse error 相当で失敗する。
    - `new doc` 専用の custom migration hint は実装されていない。
  - 観測点:
    - CLI runtime tests and help output assertions.
- E-AC-004: artifact catalog coverage
  - 前提:
    - target initiative / epic / issue scopes and required draft assurance fixture are available.
  - 操作:
    - `new artifact` の supported catalog を parser / domain / template / creation tests で確認する。
  - 期待結果:
    - `blank`, `research`, `interview`, `disc`, `decision-candidate`, `pr-repair-batch`, `adr`, `draft-requirement`, `draft-design`, `draft-plan` が supported future artifact catalog として扱われる。
    - `scratch` は supported future artifact catalog に含まれない。
    - unknown artifact type は no-write で fail する。
  - 観測点:
    - Domain catalog tests, CLI creation tests, no-write failure assertions.
- E-AC-005: ADR source collection
  - 前提:
    - legacy `discussions/` ADR original と future `artifacts/` ADR original が同一 tree 内に存在する。
  - 操作:
    - ADR mirror / sync を実行する。
  - 期待結果:
    - `spec-dock/adrs` mirror は両方を収集し、既存 `discussions/` ADR path を移動しない。
  - 観測点:
    - symlink target list, sync output, tests.
- E-AC-006: draft artifacts safety
  - 前提:
    - issue scope に `.assurance.json` / authorized profile が存在する。
  - 操作:
    - `new artifact draft-requirement`, `new artifact draft-design`, `new artifact draft-plan` を実行する。
  - 期待結果:
    - artifacts は `artifacts/` に作成され、必要な profile-specific template と assurance preflight を使う。
    - missing / stale / invalid profile では no-write fail-closed になる。
  - 観測点:
    - CLI runtime tests, no-write file diff checks.
- E-AC-007: validation layouts
  - 前提:
    - old-only, new-only, mixed layout の fixture がある。
  - 操作:
    - `spec-dock validate` を実行する。
  - 期待結果:
    - 3 layout は pass し、malformed discussion / artifact intent filename と duplicate id は fail する。
  - 観測点:
    - validation tests and command output.
- E-AC-008: scaffold and docs alignment
  - 前提:
    - provider-side scaffold assets が更新されている。
  - 操作:
    - new initiative / epic / issue scaffold を作成し、docs / skills の command examples を検索する。
  - 期待結果:
    - future nodes は `artifacts/` を default 作成し、`discussions/` を default 作成しない。
    - docs / skills は new working artifact creation として `new artifact` を案内する。
  - 観測点:
    - scaffold tests, `rg "new doc|new artifact"` review.
- E-AC-009: old-node on-demand artifact setup
  - 前提:
    - legacy node が `discussions/` を持ち、`artifacts/` を持たない。
  - 操作:
    - `spec-dock new artifact blank --issue <legacy-id> --title "Legacy node artifact"` を実行する。
  - 期待結果:
    - `<legacy-node>/artifacts/` が on demand に作成される。
    - `<legacy-node>/artifacts/<timestamp>-legacy-node-artifact.md` が作成される。
    - rules entry は既存 rules model と整合する形で作成または参照可能になる。
    - 既存 `<legacy-node>/discussions/` は移動、rename、削除、link rewrite されない。
  - 観測点:
    - CLI runtime test, filesystem assertions before/after, validate result.
- E-AC-010: dogfooding evidence
  - 前提:
    - provider-side 実装が dogfooding workspace に反映可能である。
  - 操作:
    - dogfooding node で blank / typed artifact を作成し、validate / sync を実行する。
  - 期待結果:
    - `artifacts/` evidence が残り、既存 `discussions/` は移動されない。
  - 観測点:
    - created artifact paths, validate / sync output, Epic report evidence.

## スコープ
- 必須:
  - Epic-level ADR で確定した artifact domain model / filename parser / id generation / collision handling の実装。
  - `templates/artifacts/` catalog and rules.
  - `new artifact` runtime command.
  - `new doc` command removal from parser / help / command registry.
  - new node scaffold default switch from `discussions/` to `artifacts/`.
  - validation / sync / `.agent` projection / ADR mirror support for artifacts and legacy discussions.
  - delegated authoring output boundary switch to `artifacts/`.
  - workflow docs / shipped skills / README / template guidance update.
  - dogfooding validation without migrating existing `discussions/`.
- 禁止:
  - 既存 `discussions/` の rename / move / delete / link rewrite / auto migration.
  - `new doc` compatibility shim / alias / hidden legacy command.
  - `scratch` を future `new artifact` catalog に追加すること。
  - `artifacts/` を canonical requirement / design / plan / report として扱うこと。
  - malformed legacy discussion filename validation を緩めること。
- 対象外:
  - 既存全 workspace の一括 migration.
  - 実装そのものや各 Issue の execution。具体 Issue scaffold は Epic plan gate pass 後の decomposition step として扱う。
  - artifact content の full semantic validation.
  - external tracker / multi-repo strategy.

## 境界
- 常に行う:
  - Provider-side assets / runtime / tests を primary source として扱う。
  - Existing `discussions/` は historical evidence として尊重し、読み取り・validation・ADR mirror の対象に残す。
  - Future creation surface は `artifacts/` と `new artifact` に寄せる。
  - ADR / draft / delegated output を例外にせず command surface を統一する。
- 判断が必要:
  - Existing tests / docs が `new doc` 前提を持つ箇所は、削除対象、legacy reference、historical fixture のどれかへ分類する。
  - `artifacts/rules.md` を symlink にするか copy にするかは既存 rules model と installer behavior に合わせて決める。
  - Dogfooding workspace 反映は provider-side 実装後の検証として最小範囲に留める。
- 行わない:
  - `discussions/` を不正・deprecated failure 扱いにする。
  - `new artifact` 未実装段階で downstream Issue を execution-ready と扱う。
  - Plan に未承認の policy 判断を先送りする。

## 非機能要件
- 性能:
  - filename parsing / validation は既存 tree validation と同程度の規模で実行でき、old / mixed layouts で過剰な全内容読み込みをしない。
- 信頼性 / 一貫性:
  - file creation は overwrite せず、same-second collision を 01..99 suffix で扱う。
  - command failure は no-write / fail-closed を基本とする。
  - draft artifacts の assurance/profile preflight は既存 safety behavior を劣化させない。
- セキュリティ:
  - Delegated authoring は canonical docs、implementation、tests、package/config、`.agents`、`.codex`、`.github`、`.env*` を直接変更しない。
  - Artifact creation は scope-local direct child の Markdown file に限定し、nested directories / symlinks / non-Markdown writes を禁止する。
- 運用:
  - CLI help / docs / skills が同じ command surface を示す。
  - validate / sync / dogfooding evidence によって migration boundary を観測できる。

## 依存 / 影響範囲
- 影響する component:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/discussion_docs.py`
  - new artifact domain module under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `tests/cli_runtime/`, `tests/unit/`
  - dogfooding workspace `spec-dock/` as validation target.
- 外部依存:
  - No new external service dependency.
  - Existing GitHub linkage remains part of node identity but this Epic does not change GitHub lifecycle semantics.
- 互換性:
  - Existing `discussions/` content remains valid.
  - `new doc` command compatibility is intentionally not preserved.
  - Existing historical docs mentioning `new doc` must be updated or explicitly framed as legacy/historical where retained.

## 未確定事項
- なし:
  - Issue 01 相当の policy decisions は user interviews and accepted ADR `artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md` により固定済み。
  - 以降の未確定は implementation detail として design / downstream Issue planning で扱うが、scope / non-scope / acceptance criteria を変更しない。
