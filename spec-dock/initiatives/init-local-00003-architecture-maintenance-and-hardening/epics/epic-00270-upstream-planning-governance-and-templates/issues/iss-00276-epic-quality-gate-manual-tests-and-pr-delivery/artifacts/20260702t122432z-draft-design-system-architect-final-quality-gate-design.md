---
created_by_role: system-architect
scope_id: iss-00276
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/active/issue/../iss-00271*/report.md
  - spec-dock/active/issue/../iss-00272*/report.md
  - spec-dock/active/issue/../iss-00273*/report.md
  - spec-dock/active/issue/../iss-00274*/report.md
  - spec-dock/active/issue/../iss-00275*/report.md
  - git status --short
  - git log --oneline -8
intended_targets:
  - spec-dock/active/issue/design.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00276 Epic Quality Gate Manual Tests And PR Delivery — system-architect draft design

この artifact は `iss-00276` の正規 `design.md` 作成に使うための delegated draft evidence である。Canonical docs、実装ファイル、tests、Epic docs、PR、GitHub state は変更していない。

Runtime `assurance classify` が返す `authorized_profile=standard` は、現時点では template authority としてだけ扱う。Issue requirement と Epic plan は `iss-00276` を `critical` quality / delivery Issue として扱っているため、正規設計では `critical` 相当の証跡義務を採用する。すなわち、specialist drafts、fresh `spec-reviewer`、`code-reviewer`、`qa-reviewer`、PR 作成後の `github-pr-merge-preparer` / observation evidence、raw manual artifacts 非混入確認を final gate の設計契約に含める。

## 1. Requirement Coverage

### 1.1 採用する設計ID

| Design ID | 固定度 | 設計契約 |
|---|---|---|
| `D276-001` | `[N]` | `iss-00276` は final integrator であり、新機能を広げず Epic 全体の automated checks、manual summary、reviewer gates、PR readiness を統合する。 |
| `D276-002` | `[N]` | Runtime `authorized_profile=standard` だけでは execution / delivery readiness としない。Issue requirement の `critical` を優先し、critical-grade evidence obligations を要求する。 |
| `D276-003` | `[N]` | 変更面は final gate repair、report evidence、PR metadata に限定する。gate repair を超える新しい upstream planning policy や新機能 scope は禁止する。 |
| `D276-004` | `[N]` | 前段 `iss-00271..iss-00275` の reports、reviewer results、verification outputs、defer / unresolved entries を final gate input として分類する。 |
| `D276-005` | `[N]` | Manual dogfooding / scaffold / skill read-through は summary として `report.md` または scope-local artifact に要約し、raw workspaces、logs、captures、fixtures は commit しない。 |
| `D276-006` | `[N]` | Automated verification は focused prior evidence の再確認に加え、final gate で `uv run pytest tests/unit`、`uv run pytest tests/cli_runtime`、必要に応じた `uv run pytest`、`./spec-dock/scripts/spec-dock validate` を実行または失敗理由付きで記録する。 |
| `D276-007` | `[N]` | Reviewer gate は fresh `spec-reviewer` を必須とし、implementation diff が大きい場合の `code-reviewer`、検証十分性の `qa-reviewer` を必須級の evidence とする。利用不能時は risk acceptance、fallback、追加確認、rollback-safety evidence を記録し、pass と同等には扱わない。 |
| `D276-008` | `[N]` | PR は原則1PR delivery とする。PR description は scope、背景、変更内容、影響範囲、検証、manual summary、risks、follow-up、handoff-ready / execution-ready boundary、draft artifact adoption を説明する。PR merge / GitHub issue close は行わない。 |
| `D276-009` | `[N]` | Failing checks、blocking reviewer findings、前段未完了、raw artifact混入、scope expansion、1PR破綻を検出した場合は readiness を主張せず、repair / re-review / replan / defer を選ぶ。 |
| `D276-010` | `[N]` | 日本語運用の canonical docs / artifacts は識別子を除き日本語ファーストにする。Issue-local draft artifacts は evidence-only とし、canonical `design.md` / `plan.md` に misplaced draft body を戻さない。 |
| `D276-011` | `[N]` | Source of record は `iss-00276/report.md` と `epic-00270/report.md` の ledger / step evidence / reviewer gate evidence とする。実行証跡は draft artifact ではなく report に残す。 |
| `D276-012` | `[N]` | PR 作成後の review / CI / repair loop は PR workflow の境界に渡す。merge、GitHub issue close、post-merge closeout はユーザー明示指示後の別作業とする。 |

### 1.2 AC / EC trace

| Requirement ID | 設計ID | 設計上の扱い |
|---|---|---|
| `I276-AC-001` | `D276-004`, `D276-009`, `D276-011` | 前段完了 / defer / unresolved blocker を reports から分類し、理由なしの未完了を gate blocker にする。 |
| `I276-AC-002` | `D276-006`, `D276-011` | Automated checks と `validate` の結果を final report evidence として記録する。失敗時は原因、影響、次アクションを残す。 |
| `I276-AC-003` | `D276-005`, `D276-011` | Manual dogfooding / scaffold / skill read-through は summary だけを採用し、raw manual files 非混入を確認する。 |
| `I276-AC-004` | `D276-007`, `D276-010` | Fresh `spec-reviewer` が Epic fulfillment と日本語ファースト authoring を確認する。 |
| `I276-AC-005` | `D276-007` | 大きい実装 diff には `code-reviewer`、検証十分性には `qa-reviewer` を使う。使えない場合は fallback evidence を report に残す。 |
| `I276-AC-006` | `D276-008` | PR description の必須内容を設計契約として固定する。 |
| `I276-AC-007` | `D276-008`, `D276-009` | 1PR delivery が破綻する場合、PR分割前に Epic plan update と fresh review を必須にする。 |
| `I276-AC-008` | `D276-007`, `D276-010` | 日本語ファースト確認を manual / reviewer gate に含める。 |
| `I276-AC-009` | `D276-004`, `D276-010`, `D276-011` | 前段 completion evidence と pre-start draft migration completion を final input として確認する。 |
| `I276-AC-010` | `D276-003`, `D276-010` | Canonical Issue `design.md` / `plan.md` に misplaced draft body が戻っていないことを検査する。 |
| `I276-AC-011` | `D276-008`, `D276-010`, `D276-011` | PR description と final report で handoff-ready / execution-ready boundary、draft artifact adoption、final validation を説明する。 |
| `I276-EC-001` | `D276-004`, `D276-009`, `D276-012` | 前段未完了を理由なしで無視して PR を作らない。 |
| `I276-EC-002` | `D276-006`, `D276-007`, `D276-011` | Failing checks を隠して PR readiness を主張しない。 |
| `I276-EC-003` | `D276-003`, `D276-009` | Final gate repair を超える新規 scope を導入しない。 |
| `I276-EC-004` | `D276-003`, `D276-005` | Raw manual workspace、temporary logs、local-only artifacts を staged / commit しない。 |
| `I276-EC-005` | `D276-008`, `D276-012` | PR merge や GitHub issue close を暗黙作業にしない。 |

## 2. Existing Context Findings

- Active context は `init-local-00003` / `epic-00270` / `iss-00276` を指している。
- `iss-00276` requirement は Issue grade を `critical` とし、specialist output がない場合は原則 blocked としている。
- Pre-start design / plan seed は evidence-only artifact へ移されており、canonical adoption は Issue Start 後の EAL / assurance compose / fresh reviewer gate で判断する前提である。
- Epic plan は `iss-00276` を Slice 06 / `critical` final delivery Issue として定義し、`iss-00271..iss-00275` の completion / defer、automated / manual gates、review repairs、one-PR readiness を確認する責務を与えている。
- Epic design の `D-007` は one-PR delivery default、`D-008` は Japanese-first authoring、`D-009` は Issue-local draft artifact boundary and grade-role policy を定義している。
- `iss-00275` report は focused tests、`./spec-dock/scripts/spec-dock validate`、`git diff --check`、tracked file hygiene、fresh `code-reviewer` / `spec-reviewer` pass を final gate input として残している。一方で full `uv run pytest` は未実施であり、`iss-00276` final quality gate で広域 suite を実行する引き継ぎになっている。
- Current git status では `iss-00276/design.md`、`plan.md`、`report.md` に既存変更があり、`.assurance.json` と本 artifact / implementation-planner artifact が未追跡である。この delegated draft はそれらを変更済み authority として扱わず、現時点の dirty state として report / final gate で再確認すべき入力にする。
- Recent commits は `iss-00271..iss-00275` の template / guidance / validation 実装を積み上げており、PR はまだ作成されていない。

## 3. Design Decisions

### `D276-001` Final gate aggregator

`iss-00276` は実装 feature slice ではなく、Epic delivery readiness を観測・修復・説明する final integrator とする。前段 Issue の成果をまとめ、Epic requirement / design / plan の fulfillment を検査し、未解決リスクを final report と PR description に集約する。

### `D276-002` Critical-grade evidence override

Runtime `authorized_profile=standard` は generated template の初期形を決めるだけであり、Issue requirement の `critical` を弱めない。正規設計では、critical-grade として次を必須 evidence obligation にする。

- `system-architect` draft と `implementation-planner` draft の採用判断。
- Fresh `spec-reviewer` による requirement / design / plan / report / Epic fulfillment / Japanese-first authoring 確認。
- 実装 diff が大きい場合の fresh `code-reviewer`。
- Validation adequacy の fresh `qa-reviewer`。
- PR 作成後の `github-pr-merge-preparer` または PR observation evidence。
- Raw manual artifacts 非混入確認。

### `D276-003` Allowed / forbidden change surface

Allowed:

- `iss-00276` の正規 `design.md` / `plan.md` / `report.md` を main orchestrator が更新すること。
- `epic-00270/report.md` に final evidence、E-AC 達成状況、PR readiness を追記すること。
- Final gate で検出した in-scope repair と、その再検証に必要な provider assets、dogfooding mirror、tests の最小修正。
- PR description / PR metadata 作成。

Forbidden:

- この delegated draft が canonical docs、code、tests、Epic docs、PR、GitHub issue state を変更すること。
- Gate repair を超える新しい upstream planning policy、新機能 scope、Issue re-slicing を無断で導入すること。
- Raw manual workspaces、logs、captures、fixtures、temporary files を tracked / staged にすること。
- 明示許可のない PR merge、GitHub issue close、credentialed external mutation。

### `D276-004` Evidence intake model

前段 reports を input ledger として読み、各 Issue を `completed`, `deferred`, `blocked`, `stale`, `needs_repair` に分類する。`issue finish` の実行有無だけでなく、report 内の reviewer pass、verification result、unresolved finding、no-PR handoff、raw artifact hygiene を見る。

### `D276-005` Manual evidence model

Manual dogfooding は raw artifact を残す作業ではなく、観測結果の要約を `report.md` に残す作業である。必要なら scope-local artifact は使えるが、manual workspace 自体、command logs、captures、temporary fixtures は commit 対象にしない。

### `D276-006` Verification ladder

Final gate は既存 focused evidence を信頼するだけでは足りない。最低限、次を実行または明示的に不実行理由つきで記録する。

- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`
- 必要に応じた `uv run pytest`
- `./spec-dock/scripts/spec-dock validate`
- 必要に応じた `./spec-dock/scripts/spec-dock sync`
- `git diff --check`
- `git status --short` による raw manual artifact / temp artifact hygiene

### `D276-007` Reviewer gate and repair loop

Reviewer gate は delivery readiness の evidence であり、draft artifact や過去 reviewer pass の転用ではない。Blocking finding がある場合は repair し、影響する checks を再実行し、fresh re-review を取る。Reviewer 利用不可時の fallback は pass ではなく risk acceptance として記録する。

### `D276-008` PR boundary

PR は Epic 全体の coherent delivery unit として 1PR を既定にする。PR description は implementation summary だけでなく、draft artifact boundary、handoff-ready / execution-ready boundary、manual summary、reviewer evidence、remaining risks を説明する。PR merge / GitHub issue close はこの Issue の暗黙完了条件に含めない。

### `D276-009` Failure / repair policy

Final gate で failure を見つけた場合は、失敗を隠さず `report.md` に記録する。修復が approved Epic / Issue scope 内なら最小修正して再検証する。修復が scope expansion、new policy、PR split、migration、destructive operation を要求する場合は停止し、Epic plan update / fresh review / user decision へ戻す。

### `D276-010` Japanese-first and draft boundary

Japanese-first は final review の観点であり、本文説明の英語混在を許容しない。ただし file paths、commands、code identifiers、SpecDock fixed terms、external proper nouns は原文保持を許す。Issue-local draft artifacts は evidence-only とし、canonical Issue `design.md` / `plan.md` に pre-start draft body を戻さない。

### `D276-011` Source of record

実行事実、test result、manual summary、reviewer result、PR readiness、deviation、failure は `iss-00276/report.md` と `epic-00270/report.md` に残す。Artifact draft は設計入力であり、実行済み evidence ではない。

### `D276-012` Post-PR boundary

PR 作成後の CI / review / repair observation は PR workflow に渡す。`github-pr-merge-preparer` / observation は merge readiness evidence を作るために使えるが、merge 自体や issue close はユーザー明示指示があるまで行わない。

## 4. Alternatives Considered

| Alternative | 判断 | 理由 |
|---|---|---|
| Runtime `authorized_profile=standard` に合わせて Standard gate にする | rejected | Issue requirement と Epic plan は `critical` を明示している。Template authority は evidence obligation を下げられない。 |
| 前段 Issue の focused checks だけをまとめて PR ready とする | rejected | `iss-00275` が full `uv run pytest` 未実施を final gate に渡しており、Epic-wide regression と delivery readiness を確認できない。 |
| Manual workspaces / command logs を artifact として commit する | rejected | Requirement と Epic plan が raw manual artifacts の commit を禁止している。Summary evidence で足りる。 |
| Reviewer gate を `spec-reviewer` だけにする | rejected | `critical` final delivery では implementation diff と verification adequacy の観点が必要であり、`code-reviewer` / `qa-reviewer` の利用または明示 fallback が必要。 |
| PR split を final gate 内で直接決める | rejected | `D-007` と `I276-AC-007` により、1PR破綻時は Epic plan update と fresh review が先である。 |
| PR merge / GitHub issue close まで含める | rejected | Requirement `I276-EC-005` が暗黙作業化を禁止している。 |

## 5. Boundary / Contract Model

| Boundary | Contract | Owner |
|---|---|---|
| Delegated draft boundary | この artifact は evidence-only。`adoption_status: unreviewed`、`reflected_to: []` のまま、canonical edit / reviewer pass / execution readiness を claim しない。 | `system-architect` |
| Canonical design boundary | `design.md` は main orchestrator が採用判断をして書く。Draft の内容は正規 EAL / reviewer gate を通るまで authority ではない。 | Main orchestrator |
| Final gate boundary | Automated checks、manual summary、reviewer gates、repair loop、PR readiness を統合する。新機能や新 policy を増やさない。 | `iss-00276` |
| Evidence boundary | 実行結果は `report.md` / Epic report / PR description に要約する。Raw logs / workspaces は commit しない。 | Main orchestrator / final gate executor |
| PR boundary | PR description と observation evidence まで。Merge / GitHub issue close は別指示。 | PR workflow / user decision |

## 6. Dependency Analysis

- Hard prerequisite:
  - `iss-00271..iss-00275` が完了済み、または defer / unresolved state が理由と次アクション付きで記録されていること。
  - `iss-00275` の final validation handoff と report evidence が確認されていること。
- Current predecessor evidence:
  - `iss-00271`: Initiative templates、focused tests、validate、post-implementation `spec-reviewer` / `code-reviewer` / `qa-reviewer` pass が report に記録済み。
  - `iss-00272`: Epic templates、focused tests、validate、diff check、review repair loop が report に記録済み。
  - `iss-00273`: scope-layering reference / planning guidance、focused tests、validate、diff check、review repair loop が report に記録済み。
  - `iss-00274`: Epic execution handoff / readiness workflow は Epic report 上で completed とされ、`iss-00275` の input になっている。
  - `iss-00275`: provider assets smoke matrix、draft artifact canonical non-mutation checks、readiness / grade evidence characterization、validate、diff check、raw artifact hygiene、fresh `code-reviewer` / `spec-reviewer` pass が記録済み。Full `uv run pytest` は未実施で final gate に渡されている。
- Blocking dependency:
  - 前段 report に unresolved P0/P1/P2 finding、failing command、raw artifact混入、PR split decision が残る場合は `D276-009` により停止する。
- Downstream dependency:
  - PR 作成後は PR observation / merge-preparer evidence に依存する。Merge / closeout はこの設計の外側。

## 7. Source of Record

| Record | 用途 |
|---|---|
| `spec-dock/active/issue/requirement.md` | `iss-00276` の AC / EC / critical grade / specialist obligation の正本。 |
| `spec-dock/active/epic/requirement.md` | `E-RQ-008..010`, `E-AC-006..008` の正本。 |
| `spec-dock/active/epic/design.md` | `D-007`, `D-008`, `D-009` と evidence authority flow の正本。 |
| `spec-dock/active/epic/plan.md` | Slice 06 の allowed / forbidden / reviewer focus / final gate checklist の正本。 |
| `spec-dock/active/epic/report.md` | Epic-wide EAL、completed Issue state、reviewer history、final E-AC status の source of record。 |
| `iss-00271..iss-00275/report.md` | 前段 Issue の completion evidence、verification、reviewer gates、known gaps の source of record。 |
| `iss-00276/report.md` | この Issue の execution evidence、failure / repair、reviewer gates、PR readiness の source of record。 |
| PR description / PR observation evidence | PR delivery boundary と merge readiness observation の source of record。 |

## 8. Data Flow / Domain Model / Interface Contract

```text
前段 Issue reports
  -> completion / defer / blocker classification
  -> final automated verification
  -> manual dogfooding summary
  -> reviewer gates and repair loop
  -> iss-00276/report.md + epic-00270/report.md
  -> PR description
  -> PR observation / merge-preparer evidence
  -> user-directed merge / closeout workflow
```

### Domain model

| Concept | Meaning |
|---|---|
| `GateInput` | 前段 Issue report、Epic docs、current diff、recent commits、active state、draft artifacts、existing test evidence。 |
| `GateFinding` | `pass`, `warning`, `repair_required`, `blocked`, `defer_candidate` のいずれかに分類される観測結果。 |
| `RepairScope` | `in_scope_gate_repair`, `requires_replan`, `requires_user_decision`, `out_of_scope`。 |
| `EvidenceSummary` | Automated checks、manual summary、reviewer result、PR readiness を report / PR description 向けに要約したもの。 |
| `RawManualArtifact` | manual workspaces、temporary logs、captures、fixtures。Commit 禁止。 |
| `ReadinessClaim` | PR ready / merge-prepared / issue complete などの主張。Fresh evidence がない場合は claim しない。 |

### Interface contract

- `report.md` は final gate evidence を構造化して保持する。
- PR description は report evidence から delivery-readable summary を作る。
- Reviewer outputs は source of record への参照として記録し、draft artifact の自己主張を採用しない。
- `github-pr-merge-preparer` / observation は PR 作成後に merge readiness を観測するが、merge 実行権限を意味しない。

## 9. File / Module Change Plan

この delegated draft 作成時点では、指定 artifact 以外を編集しない。

正規 `design.md` 採用後の expected final gate change surface:

| Target | 変更方針 |
|---|---|
| `spec-dock/active/issue/design.md` | Main orchestrator がこの draft の採用判断を行い、critical final gate design として正規化する。 |
| `spec-dock/active/issue/plan.md` | Implementation-planner draft と本設計を踏まえ、final gate step / verification ladder / stop condition を具体化する。 |
| `spec-dock/active/issue/report.md` | EAL、Spec Authoring Gate、Grade Specialist Evidence Gate、Step Evidence、Reviewer Gate、PR readiness evidence を記録する。 |
| `spec-dock/active/epic/report.md` | E-AC status、final validation summary、PR readiness、remaining follow-up を更新する。 |
| provider assets / dogfooding mirror / tests | Final gate で検出した approved scope 内の最小 repair のみ。 |
| PR metadata | PR title / body / validation / risk / follow-up / no-merge boundary を記録する。 |

Forbidden change surface:

- この delegated draft による canonical docs / code / tests / Epic docs / GitHub state mutation。
- `spec-dock/active/issue/../iss-00271..iss-00275` の historical report rewriting。ただし final gate が summary として参照することは可能。
- `.github/`, secrets, credentialed state、raw manual artifacts。

## 10. Migration / Compatibility / Rollback

- Migration:
  - Database / persisted data migration はない。
  - Existing managed repos への影響は既存 provider asset changes の delivery に限られる。
  - Pre-start draft migration は既に evidence-only artifact boundary として扱われており、final gate で再確認する。
- Compatibility:
  - Existing Issue grade / TDD workflow は維持する。
  - `authorized_profile=standard` の runtime template behavior は保持し、Issue requirement の critical evidence obligation を上乗せする。
  - Existing historical artifacts は保持し、raw evidence を canonical authority と誤認しない。
- Rollback:
  - In-scope repair が失敗した場合は該当 file-level diff を戻し、failure と next action を report に残す。
  - PR split が必要になった場合は、直接 split せず Epic plan update と fresh reviewer gate に戻る。
  - Raw manual artifact が staged された場合は stage 解除 / tracking 回避を行い、原因と再発防止を report に記録する。

## 11. Observability

Final gate は次を観測可能にする。

- 前段 Issue completion / defer / blocker classification。
- Automated command、exit result、failure reason、rerun result。
- Manual dogfooding / scaffold / skill read-through の summary。
- Raw manual artifact / temp artifact 非混入確認。
- Fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` の reviewer IDs、scope、state、remaining findings。
- Repair loop の before / after と影響 check。
- Japanese-first authoring review 結果。
- PR description / PR URL / PR observation / merge-preparer evidence。
- Merge / GitHub issue close を行っていない boundary。

## 12. Test Strategy

### Automated

- `uv run pytest tests/unit`
- `uv run pytest tests/cli_runtime`
- 必要に応じた `uv run pytest`
- `./spec-dock/scripts/spec-dock validate`
- 必要に応じた `./spec-dock/scripts/spec-dock sync`
- `git diff --check`
- `git status --short`

### Targeted carry-over checks

- `iss-00275` が追加した provider assets smoke matrix を再実行または上位 suite に含める。
- `new artifact draft-design` / `draft-plan` の canonical non-mutation、missing / invalid / stale assurance fail-closed、Strict / Critical readiness gate を確認する tests を含める。
- `iss-00276/design.md` / `plan.md` に `draft-before-issue-start` が戻っていないことを確認する。

### Manual

- Initiative / Epic scaffold shape の read-through。
- Planning / execution skills の source-grounded / artifact authority / Japanese-first / handoff-ready distinction の read-through。
- Dogfooding workspace の provider / mirror coherence inspection。
- PR description の scope / validation / risk / follow-up / no-merge boundary inspection。

Manual check の raw files は commit せず、summary だけを report に残す。

### Reviewer

- `spec-reviewer`: Epic requirement / design / plan fulfillment、日本語ファースト、draft artifact boundary、EAL / Spec Authoring Gate の解消。
- `code-reviewer`: 実装 diff の regression risk、scope leak、unrelated refactor、provider / dogfooding parity。
- `qa-reviewer`: test adequacy、manual summary adequacy、failure handling、raw artifact hygiene。
- `github-pr-merge-preparer` / observation: PR 作成後の CI / review / merge readiness evidence。ただし merge は行わない。

## 13. ADR Candidates

- なし。現時点では新しい material architecture decision は不要であり、`D-007`, `D-008`, `D-009` と既存 accepted ADRs で足りる。
- PR split、critical-grade default policy、merge-preparer evidence の標準化が将来の反復で再利用される場合は、別 Epic / ADR candidate として検討する。

## 14. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Runtime `standard` template をそのまま採用して critical gate が弱まる | Delivery readiness の過大主張 | `D276-002` で critical evidence override を正規設計に入れる。 |
| 前段 report の stale / unresolved findings を見落とす | PR readiness の誤判定 | `D276-004` で reports を分類し、blocking / stale entry を final input にする。 |
| Focused tests のみで広域 regression を見逃す | PR後CI failure / reviewer failure | `D276-006` で broader test ladder を final gate に置く。 |
| Manual raw artifacts が commit される | Repo 汚染 / secrets risk | `D276-005` と `git status --short` hygiene を必須にする。 |
| Reviewer pass が古い / scope が狭い | Readiness claim の信頼性低下 | Fresh reviewer scope と repair re-review を `D276-007` に固定する。 |
| PR split が必要なのに gate 内で場当たり対応する | Epic plan / review boundary の破綻 | `D276-009` により plan update / fresh review へ戻す。 |
| PR merge / issue close まで暗黙で進む | ユーザー明示指示の逸脱 | `D276-012` で post-PR boundary を固定する。 |

## 15. Requirement Clarification Requests

なし。

現時点の sources から、`iss-00276` の正規 `design.md` 作成前にユーザーへ追加確認すべき blocker は見つからない。Critical-grade obligation、1PR default、raw manual artifact 禁止、PR merge / issue close 禁止は requirement / Epic plan で十分に定義されている。

## 16. Integration Notes for Main Orchestrator

- この draft は `iss-00276/design.md` の構造入力として使えるが、canonical authority ではない。
- 正規設計へ採用する場合は、`iss-00276/report.md` の EAL に `partially_adopted` / `adopted` / `rejected` を記録し、採用しない部分を明示する。
- 正規 `design.md` では `Issue Grade: critical` 相当の記述に直し、template の `standard` 表現を残さない。
- `authorized_profile=standard` は runtime template authority としてだけ説明し、evidence obligation は Issue requirement の `critical` に合わせる。
- Fresh `spec-reviewer` は canonical `requirement.md` / `design.md` / `plan.md` / `report.md` と、この draft artifact、implementation-planner draft、前段 reports、Epic docs を対象にする。
- Final gate 実行中に code / tests / docs repair が必要になった場合は、`D276-003` の allowed surface に収まるか確認し、scope expansion なら停止する。
- PR 作成後は `github-pr-merge-preparer` / observation evidence を取得し、merge は行わない。

## Ledger Note

Material decisions proposed:

- Treat runtime `authorized_profile=standard` as template authority only; use Issue requirement `critical` as the evidence obligation.
- Require critical-grade final gate evidence: specialist drafts, fresh `spec-reviewer`, `code-reviewer`, `qa-reviewer`, PR merge-preparer / observation evidence, and raw manual artifact exclusion.
- Keep PR merge and GitHub issue close outside this Issue unless the user explicitly instructs them.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
