---
種別: 設計書（Issue）
ID: "iss-00127"
タイトル: "Scoped Discussion Draft Authoring Correction"
関連GitHub: ["#127"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-25"
依存: ["requirement.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00127 Scoped Discussion Draft Authoring Correction — 設計

## 親図参照
- 親 Epic: `spec-dock/active/epic/design.md`
- 再利用する決定:
  - `discussions/20260524t133442z-adr-flat-scope-local-discussion-drafts.md`
  - `discussions/20260524t150117z-disc-scoped-discussion-draft-authoring-requirement-draft-v2.md`
  - `discussions/20260524t150916z-disc-fresh-consultant-review-v2-discussion-direct-write-model.md`
  - `discussions/20260524t235542z-disc-agent-permission-classification-gap-analysis.md`
  - `discussions/20260525t010211z-disc-static-all-discussions-write-permission-analysis.md`

## 目的・制約
- 目的:
  - delegated authoring v2 を、manifest / Permission Profile / canonical draft write 中心の設計から、scope-local flat `discussions/` direct-write 中心の設計へ修正する。
  - sub-agent の file-based context persistence は維持し、canonical docs の authoring / promotion authority は main orchestrator に戻す。
- 必須:
  - system-architect / implementation-planner が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集できる成功パスをなくす。
  - sub-agent は initiative / epic / issue の scope-local `discussions/` 直下に flat Markdown draft / analysis / discussion-local report を直接作成・編集できる。
  - post-run diff guard を runtime helper として追加し、delegated output の採用資格を機械的に判定できるようにする。
  - `delegated-authoring manifest` は deprecated / blocked / no-artifact path として残し、新規 manifest / profile / probe / session artifact を生成しない。
- 禁止:
  - proposal-only を標準運用に戻すこと。
  - per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` を新規 delegated output として生成・推奨すること。
  - S06 の契約外で ad hoc に `draft-requirement` / `draft-design` / `draft-plan` kind を追加すること。
- 前提:
  - `iss-00126` 以前の historical delegated-authoring artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

## 既存実装 / 規約の理解
- 既存実装:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py` は `delegated-authoring manifest` を成功時 exit 0 とし、manifest / permission profile / probe plan / session invocation path を出力する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py` は scope の `discussions/delegated-authoring/<task-id>/` を生成し、target artifact を scope の `design.md` / `plan.md` に解決する。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py` は manifest schema、input authority validation、Permission Profile rendering、probe plan rendering、session invocation rendering を中心にしている。
  - provider install_root の skills / adapters は verified task manifest / Permission Profile / probe を条件に `design.md` / `plan.md` draft authoring を許す表現を持つ。
- 採用する既存パターン:
  - runtime は `commands`、`application`、`domain`、`presentation` の層を維持する。
  - provider assets を source of truth とし、dogfooding mirror は sync / update / parity tests で揃える。
  - docs / templates は shipped asset API として扱い、consumer repo に入る文言まで変更する。
- 採用しないもの:
  - delegated authoring manifest を新規成功経路として維持すること。
  - `spec-dock/initiatives` 全体や repo-wide write のように、canonical docs まで含む広い write root を post-run guard で正当化すること。
  - JSON/TOML authority graph を user-facing acceptance contract として必須にすること。

## 採用方針 / トレードオフ
- D-001: post-run diff guard
  - 決定: `spec-dock delegated-authoring diff-guard` を minimal runtime helper として追加する。
  - スコープ: git diff / status の path-level eligibility classifier に限定する。adoption ledger、canonical artifact、discussion draft schema の深い意味解析は更新しない。
  - 理由: sub-agent direct write を許容する以上、forbidden diff を機械的に reject / ineligible にできる安全弁が必要である。
- D-002: static adapter permissions
  - 決定: system-architect / implementation-planner の static adapter は、全 scope-local `discussions/` への write capability を持つ delegated authoring surface として表現する。
  - スコープ: canonical docs write、manifest/Profile/probe 前提、`.codex/permission-probe-evidence` 自然出力先、repo-wide / `spec-dock/initiatives` broad write を削除する。
  - 境界: static adapter の write capability は `discussions/` に限る。canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*` は引き続き禁止する。
- D-003: scoped-write delegated authoring execution
  - 決定: system-architect / implementation-planner は scoped-write delegated authoring agent として扱い、initiative / epic / issue の scope-local `discussions/` direct child を静的に書ける execution path を持つ。
  - スコープ: read は repo / active scope / source docs / relevant implementation を許可する。write は scope-local `discussions/<ts>-<kind>-<slug>.md` または `discussions/<ts>-<nn>-<kind>-<slug>.md` の新規作成と、main orchestrator が明示指定した既存 proposed discussion draft の更新に限定する。
  - 禁止: canonical docs、implementation files、tests、config、`.agents`、`.codex`、`.github`、`.env*`、nested directory、per-agent directory、run/task directory、`discussions/delegated-authoring/`。
  - 実現方針: run ごとの exact file context generation を削除し、static `.codex/agents/*.toml` に all discussions write capability を事前定義する。host permission model が `**/discussions/` 相当を表現できない場合は、`delegated-authoring scoped-context` を fallback として復活させず、`spec-dock/initiatives` 全体 write へも逃げず、最小の代替案を report に記録して決める。
- D-004: manifest command retirement
  - 決定: `delegated-authoring manifest` は command を残して fail-closed stub にする。
  - 理由: unknown command よりも migration message が明確で、historical artifacts の grandfathered 方針とも整合する。

## インターフェース契約
- CLI:
  - `spec-dock delegated-authoring manifest ...`
    - exit code: non-zero
    - output: `spec-dock: blocked (delegated-authoring manifest)`、`status=deprecated`、`reason=deprecated_scope_local_discussion_drafts`
    - side effect: no artifact generation
  - `spec-dock delegated-authoring diff-guard --scope <scope-id> [--baseline-status <path>] [--allow-existing-discussion <path> ...]`
    - exit code: 0 when all inspected diffs are eligible, non-zero otherwise
    - output: `spec-dock: ok (delegated-authoring diff-guard)` or `spec-dock: blocked (delegated-authoring diff-guard)` plus detail lines
    - side effect: none
  - `spec-dock delegated-authoring scoped-context ...`
    - status: removed from the runtime command surface.
    - expected handling: remove parser binding, command args/runner/renderer, application request/result/helper functions, provider and dogfooding mirror copies, exact-file context tests, and adapter/skill/workflow guidance.
    - constraint: do not keep this command as deprecated or diagnostic fallback. The product must not require run-by-run agent setting rewrites or exact-file permission context generation for normal system-architect / implementation-planner authoring.
- Diff guard eligibility:
  - Allowed:
    - scope-local `discussions/` 直下にある、既存 discussion 命名規則 `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md` に適合した `.md` file の create。
    - `--allow-existing-discussion` で明示された既存 proposed draft `.md` file の update。対象 file も既存 discussion 命名規則 `<ts>-<kind>-<slug>.md` または `<ts>-<nn>-<kind>-<slug>.md` に適合している必要がある。
  - Forbidden:
    - canonical `requirement.md` / `design.md` / `plan.md` / `report.md`
    - implementation / tests / config / docs outside scope-local `discussions/`
    - `.agents` / `.codex` / `.github` / `.env*`
    - nested dirs, symlinks, non-Markdown, naming-rule noncompliant Markdown, delete, rename, copied paths
    - inspected scope-local `discussions/` 外の discussion file
  - Baseline:
    - default は current worktree diff を検査する。`--baseline-status` は helper 自身の status file と pre-existing non-target dirtiness を切り分けるために使う。
    - inspected scope-local `discussions/` は baseline 時点で clean であることを要求する。baseline に inspected discussion の dirty/untracked entry がある場合、本文 snapshot がないため `dirty_baseline_discussion` として blocked にする。
    - baseline file が解釈できない場合は blocked にする。
- Discussion draft front matter:
  - required: `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`
  - forbidden self-claims: `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`
- Agent execution surfaces:
  - read-only static specialist:
    - `researcher`, `consultant`, `deep-consultant`, `repo-analyst`, `spec-reviewer`, `code-reviewer`, `qa-reviewer`, `pr-monitor`, `spark-worker`
    - no file write
  - full workspace-write worker:
    - `dev-coder`, `doc-writer`, `worker`, `utility-worker`, `default`, `explorer`
    - task-scoped broad edits under main orchestrator control
  - scoped-write delegated authoring agent:
    - `system-architect`, `implementation-planner`
    - all scope-local `discussions/` direct child write only
  - canonical authority:
    - main orchestrator / spec-manager-like orchestration support
    - canonical docs integration and Evidence Adoption Ledger

## 依存関係分析
- Runtime dependency:
  - `cli/parser.py` binds subcommands to `commands/delegated_authoring.py`
  - `commands/delegated_authoring.py` converts argparse args and renders CLI text
  - `application/delegated_authoring.py` resolves scope and orchestrates domain helpers
  - `domain/delegated_authoring.py` owns request validation and path-level classification rules
- Agent permission dependency:
  - static `.codex/agents/system-architect.toml` and `implementation-planner.toml` grant scoped write only for all scope-local `discussions/` direct-child Markdown authoring.
  - normal delegated authoring must not depend on run-by-run exact file permission context generation; the S04 `scoped-context` generation code and tests are deletion targets, not fallback paths.
  - diff guard validates post-run eligibility and rejects canonical / implementation / config / secret / non-discussion mutations before adoption.
- Asset dependency:
  - provider `src/spec_dock/assets/install_root/` -> installed `.agents` / `.codex`
  - provider `src/spec_dock/assets/spec_dock/` -> installed `spec-dock/` docs / templates / scripts
- Test dependency:
  - CLI tests fix user-facing command behavior.
  - domain tests fix classifier invariants.
  - installer/update tests fix provider and mirror parity plus shipped wording.
- 実装起点:
  - runtime contract を先に固定し、旧 artifact generation tests を red にする。
  - diff-guard classifier を domain で固定してから CLI / docs / skills を合わせる。
  - docs / templates / mirror を最後に広げ、parity tests と validation で閉じる。

## モジュール依存図
- Title: Delegated Authoring V2 Runtime / Asset Boundary
- Question answered: `delegated-authoring manifest` retirement、`diff-guard` 追加、provider asset / dogfooding mirror 更新をどの依存順で実装するか。
- Scope: runtime delegated_authoring modules、provider install_root assets、provider spec_dock assets、dogfooding mirror、tests。
- Excluded details: 全 command registry、全 installer copy path、全 docs link graph、各 test method の網羅的 call graph。
- Update trigger: runtime command boundary、provider / mirror source of truth、diff-guard classifier responsibility、または implementation step order が変わるとき。

```plantuml
@startuml
top to bottom direction

rectangle "cli/parser.py" as Parser
rectangle "commands/delegated_authoring.py" as Command
rectangle "application/delegated_authoring.py" as App
rectangle "domain/delegated_authoring.py" as Domain
rectangle "provider install_root assets" as InstallRoot
rectangle "provider spec_dock assets" as SpecDockAssets
rectangle "dogfooding mirror" as Mirror
rectangle "tests" as Tests

Parser --> Command : binds manifest / diff-guard
Command --> App : request and result
App --> Domain : scope resolution and classification
InstallRoot --> Mirror : update / sync parity
SpecDockAssets --> Mirror : update / sync parity
Tests --> Command : CLI behavior
Tests --> Domain : classifier invariants
Tests --> InstallRoot : shipped adapter / skill contract
Tests --> SpecDockAssets : shipped docs / templates / runtime
@enduml
```

## ディレクトリ / ファイル変更計画
```text
.
|-- src/spec_dock/assets/install_root/
|   |-- .agents/skills/spec-dock-system-architect/SKILL.md
|   |-- .agents/skills/spec-dock-implementation-planner/SKILL.md
|   |-- .agents/skills/spec-driven-tdd-workflow/SKILL.md
|   |-- .codex/AGENTS.md
|   `-- .codex/agents/
|       |-- system-architect.toml
|       `-- implementation-planner.toml
|-- src/spec_dock/assets/spec_dock/
|   |-- docs/
|   |   |-- workflow_spec_authoring.md
|   |   |-- workflow_issue.md
|   |   |-- phase_design.md
|   |   |-- phase_plan.md
|   |   |-- phase_plan_epic.md
|   |   |-- phase_plan_issue.md
|   |   |-- authoring/issue-plan.md
|   |   `-- rules/
|   |       |-- initiative/discussions.md
|   |       |-- epic/discussions.md
|   |       `-- issue/discussions.md
|   |-- scripts/spec_dock_runtime/
|   |   |-- cli/parser.py
|   |   |-- commands/delegated_authoring.py
|   |   |-- application/delegated_authoring.py
|   |   `-- domain/delegated_authoring.py
|   |-- system/active-none/
|   |   |-- initiative/report.md
|   |   |-- epic/report.md
|   |   `-- issue/report.md
|   `-- templates/
|       |-- initiative/report.md
|       |-- epic/report.md
|       `-- issue/report.md
|-- .agents/                          # dogfooding mirror
|-- .codex/                           # dogfooding mirror
|-- spec-dock/                         # dogfooding mirror
`-- tests/
    |-- cli_runtime/test_delegated_authoring.py
    |-- domain_runtime/test_delegated_authoring.py
    `-- test_init_update.py
```

## 要件 → 設計マッピング
- AC-001 -> skills / adapters / workflow docs から canonical direct-write success path を削除し、tests で旧語彙・旧契約を更新する。
- AC-002 -> skills / adapters / discussion rules / docs に all scope-local `discussions/` flat Markdown direct-write contract を明記する。
- AC-002a -> S04 exact-file scoped-context runtime command, application helpers, tests, and guidance を削除する。
- AC-003 -> manifest command を fail-closed stub にし、`discussions/delegated-authoring/` と `.codex/permission-probe-evidence` を新規出力先として生成・推奨しない。
- AC-004 -> report ledger と Markdown front matter contract に集約し、独立 JSON/TOML manifest 必須契約を削除する。
- AC-005 -> front matter forbidden self-claims を docs / skills / inspection tests に反映する。
- AC-006 -> ADR / discussion / canonical authority boundary を workflow docs と issue docs に明記する。
- AC-007 -> `delegated-authoring diff-guard` を追加し、allowed / forbidden diff を tests で固定する。
- AC-008 -> report templates の Evidence Adoption Ledger を V2 の採用判断に合わせて簡素化する。
- AC-009 -> manifest command の blocked / deprecated / no artifact generation behavior を CLI / domain tests で固定する。
- AC-010 -> provider assets と dogfooding mirror を同期し、parity tests / sync / doctor で確認する。
- AC-011 -> targeted tests、`validate`、`sync`、`doctor`、`git diff --check`、reviewer gates で閉じる。
- EC-001 -> static adapter で all scope-local `discussions/` write を表現する。表現できない場合でも exact-file context generation を fallback として残さず、`spec-dock/initiatives` 全体 write へ逃げない代替案を選ぶ。
- EC-002 -> diff guard の forbidden categories と report ledger rejection contract で扱う。
- EC-003 -> docs / tests で historical artifacts を grandfathered とし、削除や validation failure にしない。
- EC-004 -> `--allow-existing-discussion` と skill contract で既存 proposed draft の明示 allowlist だけを許可する。
- EC-005 -> docs / review gate で secrets / credentialed logs を rejected / ineligible にする。

## テスト戦略
- Red / characterization:
  - 既存 `test_manifest_command_generates_*` が旧成功経路を期待して失敗することを確認する。
  - 新規 diff-guard tests を先に書き、allowed discussion create/update と forbidden path categories を固定する。
- Unit / domain:
  - `tests/domain_runtime/test_delegated_authoring.py`
    - manifest generation は deprecated blocked result を返し、artifact paths を持たない。
    - diff classifier は flat Markdown create/update only を許可し、nested / symlink / delete / rename / non-md / forbidden dirs を拒否する。
- CLI:
  - `tests/cli_runtime/test_delegated_authoring.py`
    - `manifest` は non-zero / deprecated / no artifact。
    - `diff-guard` は allowed case で exit 0、forbidden case で non-zero。
- Installer / asset:
  - `tests/test_init_update.py`
    - shipped skills/adapters/docs/templates の旧 manifest/Profile/canonical draft write wording を新 contract へ更新する。
    - provider asset と dogfooding mirror の parity を確認する。
- Workflow / validation:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock doctor`
  - `git diff --check`

## リスク / 移行 / ロールバック
- リスク:
  - diff guard が正当な draft を false positive で拒否する。
  - baseline dirty diff と sub-agent post-run diff の切り分けが曖昧になる。
  - docs / skills / tests の旧 manifest/Profile 語彙が多く、部分更新だと矛盾が残る。
- 緩和:
  - 初回 diff guard は採用資格判定に限定し、canonical artifact mutation を行わない。
  - baseline file が曖昧な場合、または target discussions が baseline 時点で dirty/untracked な場合は blocked に寄せる。
  - provider asset と dogfooding mirror の両方を検索し、旧成功語彙を targeted tests で更新する。
- ロールバック:
  - manifest command は fail-closed stub のまま残せる。
  - diff guard に問題があれば adoption-ineligible とし、main orchestrator が手動で discussion evidence を採用する運用へ戻せる。
  - historical `iss-00126` artifact は削除しないため、過去証跡の復元性は維持される。

## 未確定事項
- なし。実装中に新しい gap が見つかった場合は `report.md` Decision Ledger に記録し、必要なら plan amendment と spec-reviewer 再レビューを行う。

## 追加設計 S06: `new doc` draft artifact types

### 設計目的

`system-architect` / `implementation-planner` が、canonical docs を直接編集せずに、scope-specific な canonical template 構造を持つ draft requirement / draft design / draft plan を `discussions/` に作成できるようにする。

この追加設計は既存 S01-S05 の権限境界を変更しない。S06 は `new doc` の doc type と template rendering を拡張するだけであり、canonical `requirement.md` / `design.md` / `plan.md` の single-writer authority は main orchestrator に残る。

### Command surface

既存 `new doc` に doc type を追加する。

```bash
./spec-dock/scripts/spec-dock new doc draft-requirement --initiative <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-requirement --epic <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-requirement --issue <id> --title "<title>"

./spec-dock/scripts/spec-dock new doc draft-design --initiative <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-design --epic <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-design --issue <id> --title "<title>"

./spec-dock/scripts/spec-dock new doc draft-plan --initiative <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-plan --epic <id> --title "<title>"
./spec-dock/scripts/spec-dock new doc draft-plan --issue <id> --title "<title>"
```

`new draft` のような別 command は追加しない。discussion docs 作成の入口を `new doc` に統一する。

### File naming

`draft-requirement` / `draft-design` / `draft-plan` は discussion doc kind として扱う。

```text
<ts>-draft-requirement-<slug>.md
<ts>-<nn>-draft-requirement-<slug>.md
<ts>-draft-design-<slug>.md
<ts>-<nn>-draft-design-<slug>.md
<ts>-draft-plan-<slug>.md
<ts>-<nn>-draft-plan-<slug>.md
```

filename parser は fixed alternatives で `draft-requirement` / `draft-design` / `draft-plan` を認識する。hyphen split に依存しない。

### Template rendering structure

生成物は既存 canonical template を直接 source として render する。

draft 専用 template file は追加しない。`templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` を作ると、canonical `templates/{initiative,epic,issue}/{requirement,design,plan}.md` と二重管理になるため禁止する。

`draft-requirement` の body source:

```text
initiative -> templates/initiative/requirement.md
epic       -> templates/epic/requirement.md
issue      -> templates/issue/requirement.md
```

`draft-design` の body source:

```text
initiative -> templates/initiative/design.md
epic       -> templates/epic/design.md
issue      -> templates/issue/design.md
```

`draft-plan` の body source:

```text
initiative -> templates/initiative/plan.md
epic       -> templates/epic/plan.md
issue      -> templates/issue/plan.md
```

生成される discussion draft は、選択された既存 canonical template を render した内容を持つ。draft であることは content wrapper ではなく、`discussions/` 配置、`draft-*` filename、post-run diff guard、canonical `report.md` Evidence Adoption Ledger で扱う。

### Placeholder strategy

既存 `plan_discussion_doc` の replacements を拡張する。

追加 placeholders:

- `<DRAFT_ID>`
- `<DRAFT_TITLE>`
- `<DRAFT_KIND>`
- `<TEMPLATE_SOURCE>`
- `<INTENDED_TARGET>`
- `<INIT_ID>` / `<INIT_TITLE>`
- `<EPIC_ID>` / `<EPIC_TITLE>`
- `<ISS_ID>` / `<ISS_TITLE>`

scope node と親 node から、可能な限り actual id/title を埋める。GitHub linkage が不明な placeholder は既存 template と同じ placeholder または empty value に留める。`<DRAFT_*>` 系 placeholder は実装内部または将来拡張用であり、draft 専用 template file を導入する理由にはしない。

### Runtime impact

変更対象:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md
spec-dock/ dogfooding mirror equivalents
tests/
```

`domain/validation.py` や `sync_state.py` は fixed discussion filename regex / doc type 判定を持つ可能性があるため、`create_node.py` だけでなく横断検索で更新する。

### Interaction with delegated authoring

- `system-architect` / `implementation-planner` は必要に応じて `draft-requirement` を作成する標準経路として使える。
- `system-architect` は `draft-design` を作成する標準経路として使える。
- `implementation-planner` は `draft-plan` を作成する標準経路として使える。
- これらは canonical docs ではなく discussion evidence である。
- post-run diff guard は `draft-requirement` / `draft-design` / `draft-plan` の valid create/update を allowed discussion Markdown として扱う。
- 採用は main orchestrator が `report.md` Evidence Adoption Ledger に記録し、必要な内容だけ canonical `requirement.md` / `design.md` / `plan.md` へ再記述する。

### Test impact

- `new doc --help` が `draft-requirement` / `draft-design` / `draft-plan` を表示する。
- `new doc draft-requirement` / `draft-design` / `draft-plan` が initiative / epic / issue で正しい path と content を生成する。
- same-second suffix allocation が hyphenated kind でも機能する。
- `validate` が `draft-requirement` / `draft-design` / `draft-plan` filename を valid として扱う。
- `sync` が discussion doc として扱い、canonical artifact として扱わない。
- `delegated-authoring diff-guard` が valid draft create/update を許可する。
- `templates/discussions/draft-requirement.md` / `draft-design.md` / `draft-plan.md` が存在しないことを確認する。
- provider assets と dogfooding mirror が一致する。

### Decision

S06 は Option A を採用する。

- `new doc` に `draft-requirement` / `draft-design` / `draft-plan` を追加する。
- 既存 canonical requirement / design / plan template を source として使う。
- 生成物は scope kind に対応する既存 canonical template を `discussions/` 直下に render したものとする。
- draft 専用 template file は追加しない。
