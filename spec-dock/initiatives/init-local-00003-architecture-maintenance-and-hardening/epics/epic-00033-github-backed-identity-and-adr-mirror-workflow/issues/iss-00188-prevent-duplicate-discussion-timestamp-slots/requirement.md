---
種別: 要件定義書（Issue）
ID: "iss-00188"
タイトル: "Prevent duplicate discussion timestamp slots when creating multiple artifacts"
関連GitHub: ["#188"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["epic-00033", "init-local-00003"]
---

# iss-00188 Prevent duplicate discussion timestamp slots when creating multiple artifacts — 要件定義

## 目的
- Shipped SpecDock workflows / skills が discussion artifact filename を手作業で組み立てる経路をなくし、runtime-owned generation に統一する。
- PR repair batch artifact を first-class `new doc` type として作成できるようにし、skill は runtime が返した path を正本として本文を更新する。
- 同一 `discussions/` 内の timestamp collision では、通常経路で suffix をなるべく出さず、suffix は safety fallback として残す。

## 背景・現状
- GitHub issue #188 の症状:
  - 同じ `discussions/` directory に同じ timestamp slot の discussion docs が複数作られると、validation / sync preflight が `Duplicate discussion timestamp slot detected` で停止する。
- 現状の runtime:
  - `new doc` は `doc_type`, scope, `--title`, optional `--slug` を受け取り、timestamped filename を生成する。
  - `create_discussion_doc` には create lock、suffix allocator、duplicate guard がある。
  - 同一秒の timestamp family collision では、現行 allocator は suffix (`01..99`) を割り当てる。
- 現状の shipped guidance:
  - `github-pr-merge-preparer` は `<ts>-disc-pr-repair-batch.md` / `<ts>-disc-pr-repair-unit-...md` のような target filename を agent が手作業で作るよう読める。
  - `.codex/agents/system-architect.toml` / `.codex/agents/implementation-planner.toml` などにも `Use filenames <timestamp>-...` と読める delegated authoring guidance がある。
- ユーザー判断:
  - Root problem は timestamp の桁数ではなく、skill / workflow が filename を手作業で作る経路があること。
  - `new doc` の body/template input interface は増やさない。
  - `pr-repair-batch` doc type を追加する。
- Parent epic との差分:
  - Parent epic `epic-00033` の original timestamp naming contract は `kind in {adr, disc}` を前提にしている。
  - #188 はその後に追加された `new doc` discussion catalog（`research` / `interview` / `scratch` / draft types）と user-approved `pr-repair-batch` を反映し、reference docs / validation / runtime catalog を現在の creatable discussion doc types へ拡張する issue-local amendment として扱う。

## 情報源
- GitHub issue:
  - `#188`
- Accepted ADR:
  - `discussions/20260617t003044z-adr-runtime-owned-discussion-artifact-creation.md`
  - `discussions/20260617t003048z-adr-wait-on-discussion-timestamp-collision.md`
- Research / interview / discussion evidence:
  - `discussions/20260617t000227z-research-timestamp-collision-source-grounding.md`
  - `discussions/20260617t000333z-interview-scope-boundary-for-timestamp-collision-prevention.md`
  - `discussions/20260617t002152z-disc-artifact-filename-generation-strategy.md`
  - `discussions/20260617t003232z-research-manual-filename-guidance-inventory.md`
  - `discussions/20260617t003432z-interview-artifact-body-generation-scope.md`
  - `discussions/20260617t011204z-interview-pr-branch-doc-type-boundary.md`
  - `discussions/20260617t011851z-research-pr-repair-batch-doc-type-implementation-surface.md`
- Code / docs:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/templates/discussions/`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock runtime user creating discussion artifacts via `new doc`.
  - Agent workflows / shipped skills that create issue-local discussion artifacts.
  - PR merge preparation workflow that creates PR repair batch artifacts.
- 代表シナリオ:
  - PR observation after review/check failure creates a `pr-repair-batch` artifact under the active issue `discussions/`.
  - Skill captures the generated path from `new doc` stdout and updates that file body with batch metadata, concern inventory, repair queue, and merge-prepared gate content.
  - Multiple artifacts are created rapidly in the same issue scope without duplicate timestamp slot failure.

## スコープ
- 必須:
  - `pr-repair-batch` を creatable discussion doc type として追加する。
  - Parent epic の historical `kind in {adr, disc}` contract と矛盾しないよう、reference docs / workflow docs では current discussion doc catalog を更新し、ADR mirror 対象は引き続き `adr` に限定されることを明示する。
  - `new doc pr-repair-batch --issue|--epic|--initiative <id> --title "..." [--slug ...]` が runtime-owned filename/path generation で file を作成する。
  - `pr-repair-batch` は existing `new doc` interface shape に従う。`--template-file` / `--body-file` / stdin body option は追加しない。
  - `pr-repair-batch` の filename / doc_id は existing timestamp discussion contract に従う。
  - `pr-repair-batch` は same timestamp family collision handling に参加する。
  - Runtime は同じ `discussions/` directory 内で生成予定 timestamp slot が使われている場合、suffix を即時付与する前に bounded wait / retry を行う。
  - Bounded wait / retry が成功しない場合、既存 suffix fallback (`01..99`) を使う。
  - Shipped skills / workflows / agent role configs は、新規 generated discussion artifacts の timestamped filename を手作業で組み立てるよう指示しない。
  - PR repair batch workflow は generated path を正本として扱い、本文更新は generated path に対して行う。
- 禁止:
  - New artifact generation guidance で `<ts>-...` target filename を agent に手作業作成させること。
  - `new doc` に caller-provided basename / explicit doc_id override を追加すること。
  - `--template-file` / `--body-file` 等の body/template rendering option を #188 で追加すること。
  - `z` marker の意味変更や custom base-N sub-second token の導入。
  - Existing artifacts の自動 rename / repair。
- 対象外:
  - `pr-repair-unit` doc type の追加。
  - Full public batch allocator API の追加。
  - Legacy sequential filename の新規生成。
  - Existing duplicate timestamp files の migration tooling。
  - PR repair workflow 全体の meaning / merge-prepared gate の再設計。

## 境界
- 常に行う:
  - Provider source of truth under `src/spec_dock/assets/...` を更新対象とする。
  - Dogfooding copy under `spec-dock/` / `.agents/` / `.codex/` は必要に応じて確認・同期対象として扱う。
  - Grammar reference docs と generation procedure guidance を分離して書く。
- 判断が必要:
  - `pr-repair-batch` template を skill-local template から provider discussion template へどの程度移植するか。
  - Hyphenated doc type を扱うため、doc type list / regex / malformed detection を shared source に寄せるか、最小差分で更新するか。
- 行わない:
  - Repair unit artifact を new doc type 化しない。Repair unit は existing `disc` または future follow-up とする。
  - Manual filename examples を grammar reference から完全削除しない。Reference docs では contract 説明として残してよい。

## 非交渉制約
- Existing second-precision timestamp grammar `yyyymmddthhmmssz` を維持する。
- Suffix fallback `01..99` を維持する。
- `note` は retired のままにする。
- Malformed discussion filename candidates は fail-closed のままにする。
- Legacy sequential docs は grandfathered only とし、新規生成しない。
- `pr-repair-batch` は hyphenated doc type として validation / malformed detection / doc_id / stdout / templates / docs / tests で一貫して扱う。

## 前提
- Runtime clock は UTC timestamp を生成する。
- Create lock は discussion doc creation 中の local concurrent creation を serialize する。
- Shipped asset updates は provider source under `src/spec_dock/assets/` を正とする。
- Skill/workflow は runtime-generated path を stdout 等から取得できる。

## 受け入れ条件
- AC-001 runtime-owned PR repair batch creation:
  - アクター:
    - SpecDock CLI user / shipped PR repair workflow.
  - 前提:
    - Valid issue / epic / initiative scope exists.
  - 操作:
    - `./spec-dock/scripts/spec-dock new doc pr-repair-batch --issue <issue-id> --title "PR Repair Batch"`
  - 期待結果:
    - Scope-local `discussions/` direct child に timestamped `pr-repair-batch` artifact が作成される。
    - stdout includes `type=pr-repair-batch`, slugless `id=<ts>-pr-repair-batch` or suffixed equivalent, and generated `path=...`.
    - Created file renders the `pr-repair-batch` template and keeps front matter / doc_id consistent.
  - 観測点:
    - CLI stdout.
    - Created file path / content.
    - `validate` pass.
- AC-002 existing `new doc` interface shape preserved:
  - アクター:
    - CLI user / tests.
  - 前提:
    - #188 implementation applied.
  - 操作:
    - Inspect help and command parser behavior.
  - 期待結果:
    - `new doc` still accepts `doc_type`, scope, `--title`, optional `--slug`.
    - No `--template-file`, `--body-file`, stdin body, explicit basename, or explicit doc_id override is introduced.
  - 観測点:
    - CLI help / parser tests.
- AC-003 manual filename guidance removed from shipped generation workflows:
  - アクター:
    - Agent following shipped skill / role config.
  - 前提:
    - Shipped assets installed or inspected from provider source.
  - 操作:
    - Inspect every known in-scope agent-facing generation guidance surface from `20260617t003232z-research`.
  - 期待結果:
    - New generated discussion artifact creation is described as command-first / returned-path-first.
    - In-scope shipped surfaces do not instruct agents to create target filenames such as `<ts>-disc-pr-repair-batch.md` or `Use filenames <timestamp>-...` for new generation.
    - In-scope surfaces include provider and dogfooding copies of:
      - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
      - `.agents/skills/github-pr-merge-preparer/SKILL.md`
      - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
      - `.codex/AGENTS.md`
      - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
      - `.codex/agents/system-architect.toml`
      - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
      - `.codex/agents/implementation-planner.toml`
      - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
      - `.agents/skills/spec-dock-hub/SKILL.md`
    - Workflow / spec-authoring docs that describe filename grammar as validation / allowed-path contract are classified explicitly as grammar references, and any generation procedure text in those docs points to `new doc` command usage and returned path authority.
    - Grammar references may remain in reference docs where they describe validation contract, not generation procedure.
  - 観測点:
    - Asset text regression / inspection.
    - Docs inspection for grammar-reference vs generation-procedure classification.
- AC-004 wait before suffix fallback:
  - アクター:
    - Runtime creating discussion docs rapidly in the same scope.
  - 前提:
    - Existing timestamp slot is already used in the target `discussions/` directory.
  - 操作:
    - Create another discussion doc through runtime-owned path.
  - 期待結果:
    - Runtime waits/retries for a later timestamp slot before suffix allocation.
    - If clock advances within budget, the new file is created suffix-less with the later timestamp.
    - If clock does not advance or budget is exhausted, suffix fallback is used.
  - 観測点:
    - Application tests with controllable clock / sleep behavior.
    - Created filenames / doc_ids.
- AC-005 hyphenated doc type validation:
  - アクター:
    - Runtime validation.
  - 前提:
    - `pr-repair-batch` artifacts exist under `discussions/`.
  - 操作:
    - Run `validate`.
  - 期待結果:
    - Valid `pr-repair-batch` timestamp filenames pass.
    - Malformed `pr-repair-batch`-intent filenames fail closed with explicit error.
    - Duplicate standard / suffix timestamp slots involving `pr-repair-batch` are detected consistently with other discussion doc types.
  - 観測点:
    - Validation tests / CLI stderr.

## 例外・エッジケース
- EC-001 frozen / non-advancing clock:
  - 条件:
    - Same timestamp remains occupied and clock does not advance during bounded retry.
  - 期待:
    - Runtime falls back to suffix allocation instead of hanging.
  - 観測点:
    - Application test with frozen clock.
- EC-002 suffix exhaustion:
  - 条件:
    - All suffixes `01..99` are occupied for a timestamp after wait/retry fallback path.
  - 期待:
    - Existing suffix exhaustion error behavior remains fail-closed.
  - 観測点:
    - Existing or updated suffix exhaustion test.
- EC-003 generated path body update:
  - 条件:
    - Skill needs to apply PR repair batch template sections.
  - 期待:
    - Skill updates only the runtime-generated path and preserves front matter / doc_id / scope identity.
  - 観測点:
    - Skill guidance inspection.
- EC-004 repair unit creation:
  - 条件:
    - PR repair batch identifies a repair unit.
  - 期待:
    - #188 does not require a `pr-repair-unit` doc type; existing `disc` can remain the repair unit artifact type.
  - 観測点:
    - Skill guidance / docs.

## 入力→出力例
- EX-001:
  - 入力:
    - `./spec-dock/scripts/spec-dock new doc pr-repair-batch --issue iss-00188 --title "PR Repair Batch"`
  - 出力:
    - `spec-dock: ok (new doc) type=pr-repair-batch id=20260617t011851z-pr-repair-batch scope=iss-00188 path=.../discussions/20260617t011851z-pr-repair-batch-pr-repair-batch.md`

## 用語（ドメイン語彙）
- TERM-001 `discussion artifact`:
  - Initiative / Epic / Issue scope-local `discussions/` direct child Markdown artifact created by `new doc`.
- TERM-002 `timestamp slot`:
  - A second-level UTC timestamp family under one `discussions/` directory, such as `20260617t011851z`.
- TERM-003 `suffix fallback`:
  - Same timestamp family collision fallback using `01..99` in filename / doc_id.
- TERM-004 `runtime-owned generation`:
  - Runtime/script allocates filename/doc_id/path and writes the initial file. Callers do not provide basename/doc_id.
- TERM-005 `pr-repair-batch`:
  - PR repair workflow batch artifact type used to record observation metadata, concern inventory, repair queue, stop conditions, and merge-prepared gate.

## 未確定事項
- なし。Requirement phase の user-facing ambiguity は `20260617t003432z-interview` と `20260617t011204z-interview` で回答済み。
