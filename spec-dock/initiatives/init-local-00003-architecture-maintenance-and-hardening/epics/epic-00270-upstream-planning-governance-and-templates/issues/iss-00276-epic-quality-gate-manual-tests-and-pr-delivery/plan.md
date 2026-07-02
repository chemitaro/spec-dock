---
種別: 実装計画書（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — 実装計画

## 0. 実行方針
- この Issue は `critical` 相当の final quality / PR delivery gate として扱う。
- `plan.md` は planned executable workflow contract であり、実行結果は `report.md` に記録する。
- PR はこの Issue の最後に一つだけ作成する。PR merge、GitHub Issue close、post-merge closeout は行わない。
- Runtime `authorized_profile=standard` は compose template の事情として記録し、Issue 要件の critical-grade obligations を弱めない。

## 1. 開始条件
- `./spec-dock/scripts/spec-dock deps check iss-00276` が ready である。
- `iss-00271` から `iss-00275` が完了済み、または defer / blocker が理由と次アクション付きで記録されている。
- `requirement.md` / `design.md` / `plan.md` / `report.md` が fresh `spec-reviewer` の planning gate 対象になる。
- `.assurance.json`、pre-start draft artifacts、specialist draft artifacts の採否を `report.md` に記録する。

## 2. この計画で満たす要件ID
- `I276-AC-001`: 前段 Issue completion / defer audit。
- `I276-AC-002`: automated checks と SpecDock validation。
- `I276-AC-003`: manual dogfooding / scaffold / skill read-through summary と raw artifact hygiene。
- `I276-AC-004`: fresh `spec-reviewer` による Epic fulfillment / 日本語ファースト確認。
- `I276-AC-005`: `qa-reviewer` と必要時 `code-reviewer` による final gate 確認。
- `I276-AC-006`: PR description completeness。
- `I276-AC-007`: 1PR delivery feasibility。
- `I276-AC-008`: 日本語ファースト authoring readiness。
- `I276-AC-009`: 前段 completion evidence と pre-start draft migration 確認。
- `I276-AC-010`: canonical `design.md` / `plan.md` の misplaced draft body absence。
- `I276-AC-011`: PR description の handoff-ready / execution-ready boundary と draft artifact adoption 説明。
- `I276-EC-001..005`: 前段未完了無視、failure hiding、scope expansion、raw artifact commit、PR merge / Issue close 暗黙化の禁止。

## 3. 依存関係から導く実装順序
```text
iss-00271 -> iss-00272 -> iss-00273 -> iss-00274 -> iss-00275 -> iss-00276
```

`iss-00276` の内部順序は、前段 audit、planning review、automated checks、manual dogfooding、reviewer gates、Epic report update、final commit、PR delivery の順に固定する。PR 作成は S07 まで行わない。

## 4. 仕様固定クロージャ索引（Spec-Locked Closure Index）
| Closure | 要件 | 設計 | 閉じる内容 | 検証 / 証跡 |
|---|---|---|---|---|
| `C276-001` | `I276-AC-001` | `D276-001`, `D276-004` | 前段 Issue completion / defer / blocker audit | `deps check`, reports audit, `report.md` |
| `C276-002` | `I276-AC-002` | `D276-002`, `D276-006` | automated checks / validation | pytest, `validate`, `assurance verify` |
| `C276-003` | `I276-AC-003` | `D276-005` | manual dogfooding summary / raw artifact hygiene | read-through summary, `git status --short` |
| `C276-004` | `I276-AC-004` | `D276-007`, `D276-010` | fresh `spec-reviewer` gate | reviewer output |
| `C276-005` | `I276-AC-005` | `D276-007` | `qa-reviewer` / `code-reviewer` gate | reviewer output or explicit fallback |
| `C276-006` | `I276-AC-006` | `D276-008` | PR description completeness | PR body / PR URL |
| `C276-007` | `I276-AC-007` | `D276-009` | 1PR feasibility | no split or plan amendment evidence |
| `C276-008` | `I276-AC-008` | `D276-010` | 日本語ファースト確認 | manual summary + `spec-reviewer` |
| `C276-009` | `I276-AC-009` | `D276-001`, `D276-010` | completion evidence + draft migration | reports audit + grep |
| `C276-010` | `I276-AC-010` | `D276-010` | misplaced draft body absence | targeted grep |
| `C276-011` | `I276-AC-011` | `D276-008`, `D276-011` | PR body readiness boundary explanation | PR body |
| `C276-012` | `I276-EC-001` | `D276-001`, `D276-009` | 前段未完了の無視禁止 | reports audit |
| `C276-013` | `I276-EC-002` | `D276-006`, `D276-007` | failure hiding 禁止 | command / reviewer evidence |
| `C276-014` | `I276-EC-003` | `D276-003`, `D276-009` | scope expansion 禁止 | diff / repair log |
| `C276-015` | `I276-EC-004` | `D276-005` | raw manual files commit 禁止 | `git status --short`, staged diff |
| `C276-016` | `I276-EC-005` | `D276-011` | PR merge / GitHub Issue close 禁止 | PR workflow boundary |

## 5. 要件 ↔ ステップ対応
| 要件 | 主担当ステップ | 補助ステップ |
|---|---|---|
| `I276-AC-001` | S00 | S05 |
| `I276-AC-002` | S02 | S04 |
| `I276-AC-003` | S03 | S06 |
| `I276-AC-004` | S04 | S01 |
| `I276-AC-005` | S04 | S02, S03 |
| `I276-AC-006` | S07 | S05 |
| `I276-AC-007` | S00, S07 | S05 |
| `I276-AC-008` | S03, S04 | S05 |
| `I276-AC-009` | S00, S03 | S05 |
| `I276-AC-010` | S00, S03 | S01 |
| `I276-AC-011` | S07 | S05 |
| `I276-EC-001..005` | S00, S02, S03, S06, S07 | S04 |

## 6. ステップ一覧（実装ステップ）

### S00: current-state bootstrap と前段 Issue audit
- 目的:
  - active context、branch、dirty state、dependency readiness、前段 completion evidence を固定する。
- 実行:
  - `git status --short`
  - `git branch --show-current`
  - `./spec-dock/scripts/spec-dock active show`
  - `./spec-dock/scripts/spec-dock deps check iss-00276`
  - `iss-00271..iss-00275/report.md` の completion / verification / reviewer / unresolved entries を確認する。
  - `rg -n "artifact_state: awaiting-assurance-compose|draft-before-issue-start" spec-dock/active/issue/{design.md,plan.md}`
- Closure:
  - `C276-001`, `C276-007`, `C276-009`, `C276-010`, `C276-012`, `C276-014`
- delegation contract:
  - delegated role: none。親 orchestration の read-only audit。
  - allowed paths: read-only。必要な記録は `report.md`。
  - forbidden changes: 前段 report の historical rewrite。
- 具体テストケース一覧:
  - `deps check iss-00276` が ready であること。
  - active context が `iss-00276` を指すこと。
  - canonical `design.md` / `plan.md` に `draft-before-issue-start` が残らないこと。
- step closure contract:
  - 前段状態、依存状態、misplaced draft absence を `report.md` Step Evidence に記録する。
- behavior slice execution:
  - inspect-only。状態を観測して分類し、repair は行わない。
- step gate:
  - blocker があれば S01 へ進まない。
- 停止条件:
  - 前段未完了または unresolved blocker が理由なしで残る。
  - canonical `design.md` / `plan.md` に pre-start draft body が戻っている。

### S01: planning adoption と fresh spec-review
- 目的:
  - pre-start seed、specialist drafts、assurance compose 結果を採否判断し、execution-ready な正規 planning set にする。
- 実行:
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement`
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all`
  - `./spec-dock/scripts/spec-dock assurance verify`
  - `report.md` の EAL、Spec Authoring Gate、Grade Specialist Evidence Gate、Reviewer Gate Status を更新する。
  - fresh `spec-reviewer` に `requirement.md` / `design.md` / `plan.md` / `report.md` / relevant artifacts / Epic docs をレビューさせる。
- Closure:
  - `C276-004`, `C276-009`, `C276-010`
- delegation contract:
  - delegated role: specialist drafts は完了済み。正本統合は main orchestrator。
  - allowed paths: `iss-00276/design.md`, `iss-00276/plan.md`, `iss-00276/report.md`, `.assurance.json`, Issue-local artifacts。
  - forbidden changes: implementation files、Epic docs、PR / GitHub state。
- 具体テストケース一覧:
  - `assurance verify` が現在の正本 hash で成功すること。
  - fresh `spec-reviewer` が planning set に P0/P1 findings を残さないこと。
- step closure contract:
  - EAL、Spec Authoring Gate、Grade Specialist Evidence Gate、Reviewer Gate Status に採用判断と reviewer result を残す。
- behavior slice execution:
  - characterization / authoring。未レビューの正本を execution-ready としない。
- step gate:
  - fresh `spec-reviewer` pass まで S02 へ進まない。
- 停止条件:
  - `design.md` / `plan.md` が template-only のまま。
  - delegated draft を authority や reviewer pass として扱っている。

### S02: automated checks
- 目的:
  - Epic-wide delivery の regression risk を broad checks で確認する。
- 実行:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest` を可能なら実行する。不実施の場合は理由、代替 evidence、残リスクを記録する。
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock assurance verify`
- Closure:
  - `C276-002`, `C276-013`
- delegation contract:
  - delegated role: test failure repair が必要なら `dev-coder`。
  - allowed paths: failure root cause に必要な provider assets、dogfooding mirror、tests の最小範囲。
  - forbidden changes: failure hiding、scope expansion、raw logs commit。
- 具体テストケース一覧:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `uv run pytest` if practical
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock assurance verify`
- step closure contract:
  - command、result、failure reason、repair / skip rationale を `report.md` に記録する。
- behavior slice execution:
  - automated validation。failure は Red evidence として扱い、Green まで修復または blocker 記録を行う。
- step gate:
  - unexplained failure が残る場合は S03 / S04 / PR へ進まない。
- 停止条件:
  - failing checks を unexplained のまま PR readiness に進める必要がある。

### S03: manual dogfooding / read-through / hygiene
- 目的:
  - automated tests では拾いにくい authoring / workflow / Japanese-first / raw artifact hygiene を確認する。
- 実行:
  - Initiative / Epic templates、workflow docs、planning / execution skills、scope-layering reference を read-through する。
  - `git diff --name-status`
  - `git diff --check`
  - `git status --short`
  - targeted `rg` で `draft-before-issue-start`、`handoff-ready`、`execution-ready`、`日本語ファースト`、`raw artifact`、`canonical authority` の境界を確認する。
- Closure:
  - `C276-003`, `C276-008`, `C276-009`, `C276-010`, `C276-015`
- delegation contract:
  - delegated role: docs / skill repair が必要なら `doc-writer`。
  - allowed paths: final gate summary のための `report.md`、in-scope docs repair のみ。
  - forbidden changes: raw manual workspace、captures、temporary logs の commit。
- 具体テストケース一覧:
  - `git diff --name-status`
  - `git diff --check`
  - `git status --short`
  - targeted `rg` for draft boundary and readiness wording。
- step closure contract:
  - manual read-through summary、Japanese-first observation、raw artifact hygiene を `report.md` に残す。
- behavior slice execution:
  - manual-required / inspect-only。必要な修復は別 step evidence として記録する。
- step gate:
  - raw artifact が tracked / staged されている場合は S04 へ進まない。
- 停止条件:
  - raw manual workspace / log / capture が tracked / staged される。

### S04: reviewer gates と repair loop
- 目的:
  - validation adequacy、diff risk、spec fulfillment を fresh reviewers で確認する。
- 実行:
  - `qa-reviewer`: automated / manual validation の十分性を確認する。
  - `code-reviewer`: material code / runtime / tests / scaffold diff がある場合に実行する。docs / report-only なら not applicable 理由を記録する。
  - `spec-reviewer`: Epic / Issue fulfillment、日本語ファースト、draft boundary、PR readiness を確認する。
  - blocking finding は in-scope repair、再検証、fresh re-review で閉じる。
- Closure:
  - `C276-004`, `C276-005`, `C276-013`, `C276-014`
- delegation contract:
  - delegated role: reviewer 指摘修復は変更面に応じて `dev-coder` または `doc-writer`。
  - allowed paths: reviewer finding の root cause に限定。
  - forbidden changes: P2/P3 だけを理由に無関係修正を広げること。
- 具体テストケース一覧:
  - `qa-reviewer` fresh pass または blocker / fallback evidence。
  - material diff がある場合の `code-reviewer` fresh pass。
  - final `spec-reviewer` fresh pass。
- step closure contract:
  - Reviewer Gate Status、repair evidence、再検証結果を `report.md` に残す。
- behavior slice execution:
  - review / repair loop。blocking finding は閉じるまで readiness claim をしない。
- step gate:
  - P0/P1 finding が残る場合は S05 / S07 へ進まない。
- 停止条件:
  - reviewer pass なしに readiness を主張する必要がある。
  - repair が new policy / PR split / scope expansion を要求する。

### S05: Epic report update
- 目的:
  - `epic-00270/report.md` を current final state に更新する。
- 実行:
  - `iss-00271..iss-00276` の状態、E-AC-001..008 の達成状況、automated / manual / reviewer / PR readiness を記録する。
  - 古い active wording を current state に直す。
- Closure:
  - `C276-006`, `C276-008`, `C276-009`, `C276-011`
- delegation contract:
  - delegated role: docs-only report repair が大きい場合は `doc-writer`。
  - allowed paths: `epic-00270/report.md`, `iss-00276/report.md`。
  - forbidden changes: observed evidence のない completion claim。
- 具体テストケース一覧:
  - E-AC-001..008 の final status が current evidence と一致すること。
  - PR body に転記する validation / risk / follow-up summary が report に存在すること。
- step closure contract:
  - Epic report EAL / E-AC status / final summary を更新し、`report.md` に evidence を残す。
- behavior slice execution:
  - docs/report evidence update。予定ではなく観測結果のみを書く。
- step gate:
  - Epic report に unresolved blocker が残る場合は S06 へ進まない。
- 停止条件:
  - observed evidence ではなく予定を完了証跡として書く必要がある。

### S06: final commit / clean state
- 目的:
  - final gate の local changes を commit し、PR 作成前の clean state を作る。
- 実行:
  - `git status --short`
  - `git diff --check`
  - staged diff inspection
  - Japanese Conventional Commit
  - post-commit `git status --short`
- Closure:
  - `C276-015`
- delegation contract:
  - delegated role: none。親が stage / commit scope を確認する。
  - allowed paths: final gate で承認された差分のみ。
  - forbidden changes: raw artifacts、temporary files、unreviewed unrelated changes の commit。
- 具体テストケース一覧:
  - `git status --short`
  - `git diff --check`
  - staged diff inspection
  - post-commit clean check
- step closure contract:
  - commit hash、staged file list、post-commit clean state を `report.md` に残す。
- behavior slice execution:
  - commit gate。コミット後に新しい未追跡 raw artifact がないことを確認する。
- step gate:
  - clean state まで S07 へ進まない。
- 停止条件:
  - raw artifacts / temp files が commit 対象に混じる。

### S07: PR creation / observation via `github-pr-merge-preparer`
- 目的:
  - 原則1PRを作成または再利用し、merge-prepared evidence または human gate を得る。
- 実行:
  - `github-pr-merge-preparer` の手順に従う。
  - PR body に scope、背景、変更内容、影響範囲、検証、manual summary、risk、follow-up、handoff-ready / execution-ready、draft adoption、final validation を含める。
  - observation result を `report.md` と final response に記録する。
- Closure:
  - `C276-006`, `C276-007`, `C276-011`, `C276-012`, `C276-013`, `C276-016`
- delegation contract:
  - delegated role: `github-pr-merge-preparer`。
  - allowed paths: PR metadata、必要な PR repair batch artifacts、in-scope repair。
  - forbidden changes: PR merge、GitHub Issue close、review dismissal。
- 具体テストケース一覧:
  - PR URL / number / base / head SHA が記録されること。
  - PR observation が latest head SHA に対して行われること。
  - required CI / blocking review findings / merge conflict がない、または human gate として記録されること。
- step closure contract:
  - PR Delivery Gate、Merge Preparation Gate、observation result を `report.md` と final response に残す。
- behavior slice execution:
  - PR delivery / observation。blocking repair は PR workflow に従う。
- step gate:
  - `merge-prepared` evidence または明示 human gate を得るまで Issue 完了を主張しない。
- 停止条件:
  - local final gates が閉じていない。
  - PR split が必要だが Epic plan amendment がない。
  - PR merge / GitHub Issue close を要求される。

## 7. S90 docs 影響解決 / docs 更新（S90 docs impact resolution / docs refresh）
- S03-S05 に含めて扱う。Final gate で docs / templates / skills への repair が必要になった場合は、S90 として `report.md` に独立 evidence を残す。
- 変更面が docs-only の場合でも fresh `spec-reviewer` か reviewer finding disposition を必要とする。

## 8. S99 最終品質ゲート（S99 final quality gate）
- S04-S07 を合わせた最終品質ゲートとする。
- S99 が閉じる条件は、automated checks、manual summary、reviewer gates、Epic report update、final commit、PR observation のすべてが `report.md` に記録されていること。

## 9. 委任方針
- Runtime / tests / scaffold repair は `dev-coder` に委任する。
- Shipped docs / templates / skills / workflow text repair は `doc-writer` に委任する。
- Parent が直接修正する場合は `report.md` に Parent Implementation Exception を記録する。
- Reviewer gates は `spec-reviewer` / `qa-reviewer` / `code-reviewer` を使い、worker output で代替しない。

## 10. Final Exit Contract
- `C276-001..016` が `report.md` の Step Evidence / Reviewer Gate / PR Delivery Gate で閉じている。
- `epic-00270/report.md` が final state に更新されている。
- required automated checks、manual summary、reviewer gates、PR observation が記録されている。
- worktree が clean で、raw manual files が tracked / staged されていない。
- PR が作成または再利用され、merge-prepared evidence または human gate が明示されている。
