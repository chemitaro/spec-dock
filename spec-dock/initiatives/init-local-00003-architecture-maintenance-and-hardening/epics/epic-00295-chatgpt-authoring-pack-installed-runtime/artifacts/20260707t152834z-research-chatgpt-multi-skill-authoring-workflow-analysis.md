---
種別: research
ID: "20260707t152834z-research"
タイトル: "ChatGPT multi-skill authoring workflow analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295"]
関連: []
scope: "epic"
scope_id: "epic-00295"
created_at: "2026-07-07T15:28:34Z"
created_by: "codex"
status: "proposed"
authority: "evidence_only"
adoption_status: "unreviewed"
derived_from:
  - "ChatGPT Use session: specdock-multiskill-chatgpt-authoring-analysis"
  - "artifacts/20260707t150325z-research-chatgpt-workflow-best-practices-final-analysis.md"
  - "artifacts/20260707t143000z-interview-workflow-first-chatgpt-authoring-redesign-interview-1.md"
  - "artifacts/20260707t144547z-interview-human-approval-checkpoint-for-batch-planning-workflow.md"
reflected_to:
  - "report.md#Evidence Adoption Ledger EAL-007"
---

# ChatGPT multi-skill authoring workflow analysis

## 位置づけ

この artifact は、ユーザーの追加方針「単一 skill ではなく、human quality gate ごとに複数 skill / script に分ける案」を受けて、ChatGPT-Use / GPT-5.5 Pro Extended に依頼した追加分析の結果である。

ChatGPT には、現在の `epic-00295` artifacts、既存 planning / execution skills、workflow docs、root `scripts/authoring-pack/` helper、既存 delegated authoring runtime と tests を添付した。

## ChatGPT 実行メモ

- session: `specdock-multiskill-chatgpt-authoring-analysis`
- model: `gpt-5.5-pro`
- mode: Pro Extended
- prompt estimate: 約 284,573 tokens
- files: 78
- caveat:
  - GitHub connector では current branch `codex/authoring-pack-installed-runtime` が解決できず、default branch `main` と添付ファイルを基準に分析した。
  - current branch の untracked Epic artifact は GitHub には存在しないため、添付ファイルが supplementary evidence である。
  - code patch、tests、runtime command 実行、installer packaging verification は未実施。

## 結論

ChatGPT の推奨は、**複数の scope authoring workflow skill + 1つの共通 ChatGPT evidence lane skill** である。

単一の巨大な `spec-dock-chatgpt-authoring` だけにすると、Initiative / Epic / Issue の human gate が混ざる。一方で Issue authoring を `zero-base` / `requirement-first` / `draft-adoption` で最初から別 skill に割ると、同じ canonical Issue docs / reviewer gate へ到達する責務が重複する。

したがって、初期実装は以下を推奨する。

- 既存の `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` を human-facing workflow entrypoint として維持する。
- 新規に `spec-dock-chatgpt-authoring` を追加し、ChatGPT prompt pack / backend invocation / ZIP review / staging / validation を扱う cross-scope evidence producer にする。
- Issue authoring は当面 `spec-dock-issue-planning` の modes として `zero-base` / `requirement-first` / `draft-adoption` を持たせる。
- `adopt` / `create-issues-from-zip` / `mark-reviewer-pass` / `set-authorized-profile` / `execution-ready` / `pr-ready` 系 command は初期実装で作らない。

## Skill taxonomy

### `spec-dock-initiative-planning`

人間向け表示名:

```text
Initiative Authoring / Epic Slicing
```

責務:

- 大きな product objective または Initiative requirement から、Initiative requirement/design/plan の draft evidence と Epic portfolio を作る。
- 既存 Initiative / Epic との fit を確認する。
- Epic candidate portfolio、cross-Epic dependency / risk、rejected alternatives、各 Epic の boundary seed を作る。

入力:

- 既存 Initiative docs。
- 関連 Epic 一覧。
- ADR / research / interview artifacts。
- ユーザー要求。
- GitHub synced source context。

出力:

- Initiative docs の採用候補。
- Epic candidate portfolio。
- cross-Epic dependency / risk。
- rejected alternatives。
- 各 Epic の boundary seed。

停止 gate:

- Epic node 作成前の human approval。

禁止事項:

- ChatGPT 生成 Epic list をそのまま `new epic` すること。
- 既存 Epic との重複確認なしに downstream を作ること。
- reviewer pass や canonical adoption を ChatGPT output に主張させること。

### `spec-dock-epic-planning`

人間向け表示名:

```text
Epic Authoring / Issue Slicing
```

これを central workflow とする。

Modes:

- `full-batch`
  - rough Epic objective から Epic requirement/design/plan と Issue decomposition proposal、各 Issue draft pack を作る。
- `requirement-first`
  - human/Codex が Epic requirement を reviewer-passed にした後、ChatGPT に design/plan/Issue slicing/draft packs を依頼する。

出力:

- Epic requirement/design/plan の採用候補。
- Issue decomposition proposal。
- per-Issue draft requirement/design/plan。
- dependency proposal。
- reviewer focus。
- risk / non-scope / follow-up proposal。

停止 gate:

- `Issue Decomposition Approval Gate`。
- 人間の明示承認は Epic-level concretization と Issue decomposition proposal の後、Issue node 作成前に置く。

承認対象:

- Issue slicing。
- node creation decision。
- proposed Issue list。
- 責務境界。
- 依存概要。
- draft pack summary。

禁止事項:

- Issue node を承認前に作ること。
- draft pack を canonical Issue docs として扱うこと。
- Issue execution-ready を主張すること。

### `spec-dock-issue-planning`

人間向け表示名:

```text
Issue Authoring / Draft Adoption
```

Issue authoring は初期実装では split せず、1 skill + 3 modes にする。

Modes:

- `zero-base`
  - interview / artifacts / ADR / context から Issue requirement/design/plan を作る。
- `requirement-first`
  - approved Issue requirement から design / plan を作る。
- `draft-adoption`
  - Epic-generated draft requirement/design/plan を claim / section 単位で採否判断し、canonical Issue docs に正本化する。

分割しない理由:

- 3 modes はいずれも同じ停止 gate に到達する。
- 到達点は canonical `requirement.md` / `design.md` / `plan.md`、`report.md` ledger、fresh `spec-reviewer` pass、execution handoff readiness である。
- `draft-adoption` が十分大きくなり、専用 validator / EAL lint / automation policy を持つようになってから split すればよい。

### `spec-dock-chatgpt-authoring`

人間向け表示名:

```text
ChatGPT Batch Evidence Lane
```

これは planning leaf skill ではなく、各 planning skill から呼ぶ shared evidence producer とする。

責務:

- prompt pack 作成。
- backend invocation。
- ZIP/tree review。
- staging。
- mode-specific validation。
- EAL candidate 生成。
- forbidden claims の検査。

入力:

- scope-specific prompt config。
- source manifest。
- stale-if。
- repo/branch preflight。
- safe output constraints。
- selected skeleton / assurance snapshot。

出力:

- reviewed/staged evidence。
- validation report。
- dry-run diff。
- EAL candidates。
- Issue/Epic candidate comparison summary。

停止 gate:

- reviewed/staged evidence まで。

禁止事項:

- canonical docs の上書き。
- `.assurance.json` 更新。
- `authorized_profile` 決定。
- fresh reviewer pass 主張。
- execution readiness。
- PR readiness。
- Issue/Epic completion 主張。

## Runtime command / script taxonomy

### Provider-side source of truth

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  commands/authoring.py
  application/authoring_pack/
  domain/authoring_pack/
  presentation/authoring_pack/
```

### Installed wrapper / compatibility surface

```text
src/spec_dock/assets/spec_dock/scripts/authoring-pack/
  prepare_chatgpt_authoring_pack.py
  invoke_chatgpt_backend.py
  review_chatgpt_authoring_pack.py
  stage_chatgpt_authoring_pack.py
  validate_selected_skeleton_fill.py
  validate_issue_candidates.py
```

### Installed skill

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
```

`src/spec_dock/cli.py` の `_MANAGED_SKILL_NAMES` に `spec-dock-chatgpt-authoring` を追加する必要がある。

### Primary command group

```bash
./spec-dock/scripts/spec-dock authoring ...
```

### Shared primitives

```bash
./spec-dock/scripts/spec-dock authoring preflight github-sync
./spec-dock/scripts/spec-dock authoring pack prepare
./spec-dock/scripts/spec-dock authoring backend invoke
./spec-dock/scripts/spec-dock authoring pack review
./spec-dock/scripts/spec-dock authoring pack stage
./spec-dock/scripts/spec-dock authoring validate epic-issue-candidates
./spec-dock/scripts/spec-dock authoring validate initiative-epic-candidates
./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption
./spec-dock/scripts/spec-dock authoring validate selected-skeleton-fill
./spec-dock/scripts/spec-dock authoring approval check
```

`approval check` は Issue creation 前の gate state を読むだけにし、Issue 作成はしない。

### Workflow-specific orchestrators

初期では薄くする。

```bash
./spec-dock/scripts/spec-dock authoring workflow initiative-slice prepare
./spec-dock/scripts/spec-dock authoring workflow epic-slice prepare
./spec-dock/scripts/spec-dock authoring workflow issue-zero-base prepare
./spec-dock/scripts/spec-dock authoring workflow issue-requirement-first prepare
./spec-dock/scripts/spec-dock authoring workflow issue-draft-adoption prepare
```

ただし、初期 Epic では workflow orchestrator を全部作らず、shared primitives を先に実装し、skills が組み合わせる形を推奨する。

### 初期で作らない command

```bash
./spec-dock/scripts/spec-dock authoring adopt
./spec-dock/scripts/spec-dock authoring create-issues-from-zip
./spec-dock/scripts/spec-dock authoring mark-reviewer-pass
./spec-dock/scripts/spec-dock authoring set-authorized-profile
./spec-dock/scripts/spec-dock authoring issue-execution-ready
./spec-dock/scripts/spec-dock authoring pr-ready
```

理由:

- canonical adoption、reviewer pass、execution-ready は main orchestrator / reviewer gates の責務である。
- stage は EAL candidate を作るだけで、final EAL row ではない。

### Backend command contract

backend は configurable にする。

優先順位:

1. CLI `--backend-command`
2. `SPECDOCK_CHATGPT_COMMAND`
3. optional compatibility fallback `ORACLE_CHATGPT_COMMAND`
4. 未設定なら fail-closed

設定値は `shlex.split` で argv にし、shell injection を避ける。

## GitHub sync / branch preflight

### 基本方針

ChatGPT/Oracle を repo-aware analysis に使う前に、local branch が GitHub connector で読める exact snapshot になっていなければならない。

### Pass 条件

`authoring preflight github-sync` は次をすべて満たした場合だけ backend invocation を許可する。

1. `git rev-parse --show-toplevel` が成功する。
2. `git status --porcelain=v1` が空。untracked も block。
3. `origin` が存在し、GitHub repo full name が expected `owner/name` と一致する。
4. current branch が detached HEAD でない。
5. `git ls-remote --heads origin <branch>` が成功する。
6. `git fetch --prune origin <branch>` が成功する。
7. `HEAD == origin/<branch>`。ahead / behind / diverged は全部 block。
8. default branch を GitHub repo metadata から取得できる。
9. prompt sources の sha256 を記録できる。
10. GitHub connector で `repository + requested_ref` を開けることを wrapper prompt が要求する。

### Block するもの

- uncommitted tracked changes。
- untracked files。
- staged changes。
- unpushed commits。
- remote behind。
- diverged branch。
- branch missing on GitHub。
- origin repo mismatch。
- source hash mismatch。
- connector inaccessible。
- default branch unknown。
- prompt output directory が repo 内にある場合。

### Branch missing の扱い

installed workflow の通常 preflight では、branch missing は block。

今回の分析では current branch が GitHub connector で開けなかったため default branch `main` を確認したが、正式 workflow では silently fallback してはいけない。fallback する場合は、`requested_ref` と `effective_ref` を分け、生成物を default-branch evidence として明示する。

### ChatGPT に渡す repository context

```json
{
  "repository": {
    "full_name": "chemitaro/spec-dock",
    "requested_ref": "<current-branch>",
    "effective_ref": "<current-branch-or-explicit-default-fallback>",
    "observed_head": "<sha>",
    "default_branch": "main",
    "remote": "origin",
    "sync_state": "exact_remote_match"
  },
  "connector_requirement": {
    "must_inspect_github_repository": true,
    "first_ref": "<requested_ref>",
    "fallback_ref": "main",
    "hard_failure_text": "repository access failed"
  }
}
```

## End-to-end workflows

### Initiative -> Epics

1. Preflight: GitHub sync / source hashes / stale-if / existing Initiative/Epic fit。
2. 入力が vague large work の場合、まず Initiative requirement draft を作る。
3. ChatGPT Batch Evidence Lane で Initiative requirement/design/plan draft、Epic portfolio、dependency/risk、rejected alternatives を生成。
4. Local review: ZIP/tree safety、metadata、source staleness、existing Epic duplication。
5. Codex が Initiative canonical docs に採用候補を再記述。
6. fresh `spec-reviewer`。
7. Epic candidate list を `Epic Portfolio Approval Gate` として `report.md` に記録。
8. human approval 後だけ Epic node を作成。

Artifacts:

```text
initiative/artifacts/<ts>-research-chatgpt-initiative-epic-portfolio.md
initiative/report.md#Epic Portfolio Approval Gate
candidate pack: candidates/epics/index.json
```

Failure modes:

- existing Epic に収めるべき scope を新 Epic に切っている。
- Initiative requirement が未承認。
- source branch stale。
- candidate が cross-Initiative product decision を含む。
- ZIP unsafe / metadata missing。

### Epic -> Issues + Issue draft packs

1. Mode selection: `full-batch` or `requirement-first`。
2. Preflight pass。
3. ChatGPT produces Epic requirement/design/plan candidates, Issue decomposition proposal, per-Issue draft packs。
4. Review / validate `candidates/issues/index.json`。
5. Codex が Epic canonical docs に claim-level 採用。
6. requirement/design/plan 各 phase で fresh `spec-reviewer`。
7. `Issue Decomposition Approval Gate` を `report.md` に記録。
8. `approval_state=approved` 後だけ `new issue`。
9. Issue-local `draft-requirement` / `draft-design` / `draft-plan` artifacts を runtime command で作成。
10. Epic Execution へ handoff。

### Issue zero-base planning

1. `spec-dock-issue-planning(mode=zero-base)`。
2. interview / clarification / artifacts / ADR / parent docs を読む。
3. Issue requirement を Codex-led で作る。
4. scope / non-scope が曖昧なら clarification。
5. ChatGPT は requirement が固まった後の design/plan brainstorm に限定。
6. canonical docs を main orchestrator が再記述。
7. fresh reviewer per phase。
8. execution-ready gate。

Failure modes:

- parent envelope を Issue が勝手に再定義している。
- requirement gap を design/plan で隠している。
- reviewer pass なし。
- `.assurance.json` / profile authority が未確定。

### Issue requirement-first design/plan generation

1. approved Issue requirement と selected skeleton / `.assurance.json` を読む。
2. ChatGPT に design/plan fill candidates を作らせる。
3. `selected-skeleton-fill` validation。
4. stale / profile mismatch / extra section / forbidden claim を reject。
5. canonical design rewrite -> fresh reviewer。
6. canonical plan rewrite -> fresh reviewer。
7. execution-ready handoff。

### Issue draft-adoption during Epic Execution

1. Epic Execution が 1 Issue を選ぶ。
2. canonical docs がない、または draft-only なら `spec-dock-issue-planning(mode=draft-adoption)` に route。
3. Epic handoff package と Issue-local draft artifacts を読む。
4. source hash / parent trace / dependency order / draft pack digest を確認。
5. EAL disposition: adopt / partially_adopt / reject / stale / blocked。
6. canonical requirement/design/plan を再記述。
7. fresh reviewer gates。
8. execution-ready になったら Issue Execution へ渡す。

## ZIP/tree output contract

### Root

```text
specdock-authoring-pack/
```

### Recommended schema

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  source-manifest.json
  stale-if.json
  safe-output-constraints.md

  adoption/
    adoption-map.json
    eal-candidates.json

  summaries/
    executive-summary.md
    risk-register.md
    rejected-alternatives.md
    reviewer-focus.md

  candidates/
    epics/
      index.json
      <candidate-id>/
        candidate.json
        requirement-draft.md
        design-brief.md
        plan-brief.md
        boundary.md
    issues/
      index.json
      <candidate-id>/
        candidate.json
        requirement-draft.md
        design-brief.md
        plan-brief.md
        profile-recommendation.json

  drafts/
    initiative/
      requirement.md
      design.md
      plan.md
    epic/
      requirement.md
      design.md
      plan.md
    issue/
      requirement.md
      design.md
      plan.md

  selected-skeleton-fill/
    section-fills.json
```

### Required metadata

`manifest.json`:

```json
{
  "schema_version": "1",
  "pack_id": "<stable-id>",
  "mode": "initiative-slice | epic-slice | issue-zero-base | issue-requirement-first | issue-draft-adoption",
  "expected_zip_root": "specdock-authoring-pack/",
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

`provenance.json`:

```json
{
  "source": "chatgpt_zip_authoring_pack",
  "model": "gpt-5.5-pro",
  "generated_at": "<UTC>",
  "repository": {
    "full_name": "<owner/repo>",
    "requested_ref": "<branch>",
    "effective_ref": "<branch>",
    "observed_head": "<sha>",
    "default_branch": "main"
  },
  "connector_access": "verified | fallback_default | blocked"
}
```

`source-manifest.json`:

```json
{
  "sources": [
    {
      "path": "spec-dock/.../requirement.md",
      "sha256": "<sha256>",
      "role": "requirement",
      "required": true
    }
  ]
}
```

`stale-if.json`:

```json
{
  "stale_if": [
    {
      "kind": "source_hash_changed",
      "source_paths": ["..."]
    }
  ]
}
```

### Safety validation

Reject するもの:

- path traversal。
- absolute / host-local paths。
- hidden paths。
- secret-looking paths。
- raw transcript。
- private key / credential / token。
- nested archive。
- executable entry。
- symlink。
- binary payload。
- oversized file。
- unsupported suffix。
- encrypted ZIP entry。
- wrong ZIP root。
- metadata missing。
- source hash mismatch。
- forbidden authority claim。

## Implementation sequence for `epic-00295`

### Issue 1: Epic docs / decision contract 固定

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md`
- 必要なら ADR candidate

固定する内容:

- Option A primary / B downstream。
- Issue Decomposition Approval Gate。
- ChatGPT evidence-only boundary。
- provider asset / installed runtime boundary。
- branch sync preflight。
- no `adopt` command policy。

### Issue 2: shipped workflow docs

追加:

```text
src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md
src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md
```

更新:

```text
workflow_spec_authoring.md
workflow_initiative.md
workflow_epic.md
workflow_issue.md
phase_plan_epic.md
phase_plan_issue.md
```

### Issue 3: skills

追加:

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
```

更新:

```text
spec-dock-hub
spec-dock-initiative-planning
spec-dock-epic-planning
spec-dock-issue-planning
spec-dock-epic-execution
```

`_MANAGED_SKILL_NAMES` への追加もここで行う。

### Issue 4: runtime command skeleton / help / packaging

追加:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py
```

最初は help と dry-run only の subcommands でよい。

### Issue 5: GitHub sync preflight

実装:

```bash
./spec-dock/scripts/spec-dock authoring preflight github-sync
```

tests:

- dirty worktree blocks。
- untracked blocks。
- unpushed blocks。
- branch missing blocks。
- origin mismatch blocks。
- default branch unknown blocks。
- exact remote match passes。

### Issue 6: port shared primitives to runtime modules

移植対象:

```text
prepare
backend
review
stage
selected_skeleton_fill
issue_candidates
```

現行 root scripts は thin wrapper 化し、README は temporary dogfood compatibility surface と明記する。

### Issue 7: approval gate / candidate validators

追加:

```bash
authoring validate initiative-epic-candidates
authoring validate epic-issue-candidates
authoring approval check
```

`approval check` は Issue 作成 readiness を判定するだけで、Issue 作成はしない。

### Issue 8: issue draft-adoption validator

追加:

```bash
authoring validate issue-draft-adoption
```

EAL disposition、parent trace、stale source、profile mismatch、selected skeleton mismatch を検査する。

### Issue 9: tests / dogfood

最低限:

- `spec-dock init/update` 後に docs / skill / runtime command が入る。
- `./spec-dock/scripts/spec-dock authoring --help`。
- backend 未設定 fail-closed。
- `SPECDOCK_CHATGPT_COMMAND` shell injection なし。
- unsafe ZIP reject。
- forbidden claims reject。
- stale source reject。
- Issue candidate validation は approval gate なしに issue creation-ready としない。
- handoff-ready と execution-ready を混同しない。

### Deferred

- `authoring adopt`。
- ZIP から Issue 自動作成。
- semantic LLM validator。
- ChatGPT を Issue Execution に直接使う workflow。
- PR creation / PR readiness automation。
- `.assurance.json` mutation。
- Initiative-scale execution coordinator。
- full repository error recovery UI。

## Docs / skills に貼れる wording

### ChatGPT authoring authority boundary

```text
ChatGPT の出力は batch planning evidence であり、SpecDock の正本権限ではない。ChatGPT は requirement、design、plan、Issue 分割、draft artifact、reviewer focus、risk list を提案できるが、canonical adoption、`.assurance.json` authority、`authorized_profile`、fresh `spec-reviewer` pass、execution readiness、implementation completion、PR readiness、Issue/Epic completion を主張してはならない。
```

### Multiple authoring skills

```text
SpecDock の authoring workflow は scope ごとの planning skill が入口を持つ。Initiative は Epic portfolio まで、Epic は Issue decomposition proposal と Issue draft packs まで、Issue は canonical Issue docs と execution handoff readiness までを担当する。ChatGPT backend / ZIP review / staging / validation は `spec-dock-chatgpt-authoring` が共有 evidence lane として提供し、scope skill は次の human quality gate を越えない。
```

### GitHub sync preflight

```text
ChatGPT に repo-aware analysis を依頼する前に、local branch は GitHub connector で同じ ref と HEAD を読める状態でなければならない。uncommitted change、untracked file、unpushed commit、remote behind/divergence、origin mismatch、branch missing、source hash mismatch、connector failure は preflight blocked とし、backend invocation を行わない。default branch fallback は明示的に選択された場合だけ許可し、生成物には requested_ref と effective_ref の差分を記録する。
```

### Human approval gates

```text
人間の明示承認は、Epic-level concretization と Issue decomposition proposal の後、実際の Issue node 作成前に置く。この承認は Issue slicing と node creation decision を承認するものであり、Issue draft packs を execution-ready にするものではない。Issue 作成後の draft adoption / canonicalization は自動化してよいが、fresh reviewer gates と Evidence Adoption Ledger disposition は省略しない。
```

### ZIP artifact handling

```text
ZIP/tree output は canonical docs に直接コピーしない。まず repo 外 scratch に保存し、安全に展開し、固定 root、metadata、source hash、stale-if、forbidden claims、unsafe path、secret-looking content、raw transcript、nested archive を検査する。stage できるのは unreviewed evidence candidates だけであり、canonical rewrite と final EAL row は main orchestrator が claim/section/artifact 単位で採否判断して記録する。
```

## 採用候補

特に採用価値が高いもの:

- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` を scope authoring entrypoint として維持し、共通 evidence lane として `spec-dock-chatgpt-authoring` を追加する hybrid taxonomy。
- `spec-dock-issue-planning` は初期では split せず、`zero-base` / `requirement-first` / `draft-adoption` modes にする。
- `authoring preflight github-sync` を block-first で設計し、dirty / untracked / unpushed / branch missing / connector failure を backend invocation block にする。
- root `scripts/authoring-pack/` helper を正本にせず、provider-side runtime command と installed skill へ移す。
- 初期実装では `authoring adopt` と Issue 自動作成 command を作らない。

## 未検証事項

- current branch `codex/authoring-pack-installed-runtime` は GitHub connector で開けなかったため、current branch 固有の未 push 変更は ChatGPT 側では検証されていない。
- command names / schema は設計提案であり、実装済み contract ではない。
- tests はこの artifact 作成時点では実行していない。
