---
種別: 実装計画書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00319 Installed Runtime Dogfood Parity Final Quality And Mergeable PR — 実装計画書（Standard）

## 0. 実行原則

- Approved Requirement/Designと`authorized_profile=standard`をauthorityとする。
- S00 → S01 → S02 → S03 → S04 → S05 → S90 → S99 → S100をone-step-at-a-timeで実行する。
- 各stepは実装/記録 → narrow verification → fresh reviewer → focused commit → push → clean/upstream checkの順で閉じる。No-opはexact read-only evidenceとreviewer承認を必要とし、empty commitを作らない。
- DevCoder、qa/code/spec reviewerはすべて`gpt-5.6-sol` / reasoning `medium`を使う。
- Reviewerはread-onlyで、finding修復はfresh DevCoderへ戻す。
- Issue319からPR deliveryを別Issueへ延期しない。PR mergeは行わない。
- Workbench/Artifact本文、secret-like value、absolute host pathをreport/PR/logへ記録しない。
- New product semantics、root bulk copy、automatic sync、classifier、typed `chatgpt-output`、general refactorを追加しない。

## 1. Spec-locked closure index

| Closure ID | Requirement / AC | Close condition | Owning step |
|---|---|---|---|
| C319-01 | RQ-319-001 / AC-319-001〜002 | Dependency、preserved ChatGPT Artifact、EAL/OAL、approved planning/assurance | S00 |
| C319-02 | RQ-319-002 / AC-319-003 | Latest main統合、conflict解消、ahead/behind再計測 | S01 |
| C319-03 | RQ-319-003 / AC-319-004 | Clean wheel inventoryがexpected assets/forbidden absenceを満たす | S02 |
| C319-04 | RQ-319-004 / AC-319-005 | Wheel-only fresh initで全surface利用可能 | S02 |
| C319-05 | RQ-319-005 / AC-319-006 | Existing update前後の4 Workbench placement bytes/type/path一致 | S02 |
| C319-06 | RQ-319-006 / AC-319-007 | Provider/dogfood exact pair/inventoryとexception ledgerが閉じる | S03 |
| C319-07 | RQ-319-007 / AC-319-008 | Root/public docs/help/output semanticsが一貫する | S03 |
| C319-08 | RQ-319-008 / AC-319-009 | Focused W1〜W4、unit/CLI/integration/full/staticがlatest headでpass | S04 |
| C319-09 | RQ-319-009 / AC-319-010 | Ubuntu/Linux publication pathをcurrent CI/checkで実証 | S04/S100 |
| C319-10 | RQ-319-010 / AC-319-011 | Installed manual copy→import→EAL→rewrite scenarioがcontent-free evidenceでpass | S05 |
| C319-11 | RQ-319-011 / AC-319-012 | Epic全E-RQ/E-AC、EAL/OAL/docs/risk/Issue links closure | S90 |
| C319-12 | RQ-319-012 / AC-319-013 | Fresh QA→code→specがlatest pre-PR headでpass | S99 |
| C319-13 | RQ-319-013 / AC-319-014〜015 | Single PR、checks/reviews/mergeability/base driftをfinal headで観測 | S100 |
| C319-14 | RQ-319-014 / AC-319-016 | Final-head observation後versioned mutationなしでissue finish、no merge | S100 |
| C319-15 | RQ-319-015 | 全evidenceがcontent-free、安全なsynthetic fixtureのみ | S00〜S100 |
| C319-16 | RQ-319-016 | Minimal diff、scope expansion/version/migrationはverified necessityのみ | S00〜S100 |

## 2. Step summary

| Step | Objective | Worker | Reviewer | Commit boundary |
|---|---|---|---|---|
| S00 | Planning/baseline/evidence inventory | repo-analyst + orchestrator | spec-reviewer | Planning docs/Artifact/report/assurance only |
| S01 | Latest main integration and conflict routing | orchestrator + DevCoder if repair | code + spec reviewer | Merge/integration repair only |
| S02 | Wheel, fresh init, existing update preservation | DevCoder | code + spec reviewer | Package/installer tests/repair/report |
| S03 | Public docs and provider/dogfood parity | doc-writer + DevCoder for projection/tests | spec + code reviewer | Provider docs/projection/tests/report |
| S04 | Focused/full/static/Linux quality | DevCoder | code + QA reviewer | Quality repair/tests/report |
| S05 | Installed integrated manual scenario | orchestrator | spec + QA reviewer | Safe evidence/report only |
| S90 | Epic E-RQ/E-AC/EAL/OAL/docs closure | repo-analyst + orchestrator | spec-reviewer | Epic/Issue reports only |
| S99 | Final QA→code→spec review | reviewers read-only; DevCoder on finding | QA→code→spec | Final review ledger only |
| S100 | Push/PR/final-head report/observation/repair/finish | orchestrator + DevCoder | checks/reviewers as affected | PR URL report commit before terminal observation; no versioned mutation after terminal pass |

## 3. S00 — Planning and live baseline

### Scope

- Confirm active Issue319、dependency edges、GitHub #315〜#318 closed、#319/#312 open。
- Confirm ChatGPT Artifact receipt/hash/bytes/source ignored、EAL/OAL、Requirement/Design/Plan review order。
- Verify assurance/profile、local/remote branch、merge-base/ahead-behind、existing PR absence/presence。
- Inventory exact provider/dogfood pairs、root-only/generated exceptions、public docs paths、package-data、focused test files/commands、full/static commands、Ubuntu workflow、manual fixture strategy。S00 reportでfile-level rowsとして固定し、category/wildcardだけではcloseしない。
- Record exact pre-feature update baseline candidate only after checking history; do not infer it from ChatGPT output。

### Allowed changes

- Issue319 `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`, imported planning Artifact。
- No provider/runtime/docs/tests/root projection changes。

### Verification

```bash
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock assurance verify --issue iss-00319 --format json
./spec-dock/scripts/spec-dock validate
git fetch origin
git rev-list --left-right --count origin/main...HEAD
git merge-base origin/main HEAD
git status --short --branch
git diff --check
```

- Confirm scope-local `.workbench` source is ignored and Artifact `cmp`/SHA/bytes match without printing body。
- Record exact target inventory and historical/current evidence distinction。

### Test contract

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s00-01 | inspect-only | C319-01 planning/preservation/assurance valid |
| tc319-s00-02 | inspect-only | C319-02 divergence and integration precondition observed |
| tc319-s00-03 | inspect-only | C319-03〜10 target command/path inventory exists |

### Gate / commit

- Fresh spec-reviewer passes final planning set。
- Commit candidate: `docs(issue-319): final distribution計画を具体化`。
- Push、clean、upstream `0 0` before S01。

## 4. S01 — Latest main integration

### Preconditions

- S00 committed/pushed/clean。
- Fetch latest `origin/main`; re-measure divergence。

### Execution

1. Behind/diverged時は`git merge --no-commit --no-ff origin/main`でuncommitted integration stateを作る。
2. Before resolution, classify every conflict by owner: current main、Issue315〜318 accepted contract、Issue319 planning/report。
3. Delegate semantic repairs to DevCoder only for exact conflicting paths。
4. Do not rebase/force-push/history rewrite。
5. Re-run affected contract tests and assurance/validate after resolution。
6. Integration resultをuncommittedのままfresh code → spec reviewし、両方pass後に一つのintegration commitを作る。

### Allowed / forbidden

- Allowed: merge result and exact conflict repair。
- Forbidden: unrelated cleanup、accepted capability redesign、dropping main changes、test/check disable。

### Verification

```bash
git diff --check
git rev-list --left-right --count origin/main...HEAD
./spec-dock/scripts/spec-dock assurance verify --issue iss-00319 --format json
./spec-dock/scripts/spec-dock validate
```

- `origin/main` left count must be 0 at step close。
- Run focused tests for every conflict owner。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s01-01 | integration | C319-02 latest main integrated without history rewrite |
| tc319-s01-02 | affected regression | Conflict owners preserve accepted semantics |

- Fresh code-reviewer then spec-reviewer before integration commit。
- 両reviewer pass後に一つのmerge/integration commitを作る。
- Approved-no-opはleft count 0、conflict/repairなし、exact main/head evidence、read-only code/spec reviewer承認を全て満たす場合だけ許し、empty commitを作らない。
- Push、clean/upstream `0 0`。

## 5. S02 — Candidate wheel, fresh init, existing update

### Preconditions

- S01 closed on latest main。
- `codex-tmp`のmanaged session pathをrepository外のbuild/install fixtureに使い、実行中は`MANAGED_TMP`へbindする。

### Execution

1. Build clean candidate wheel with `uv build --out-dir "$MANAGED_TMP/wheel"` and record wheel hash/inventory content-free。
2. Compare archive entries against provider package-data expectations。
3. Select the single generated wheel absolute path as `CANDIDATE_WHEEL`; create fresh git repo and initialize with `uvx --no-cache --from "$CANDIDATE_WHEEL" spec-dock init "$MANAGED_TMP/fresh-consumer"`。
4. Verify four Workbench placements under `<repo>/spec-dock/.workbench/` and scope directories are ignored/opaque。
5. Exercise installed help/smoke for scoped copy、Artifact import、planning skill assets。
6. Create an existing consumer from verified pre-feature baseline, add safe text/binary/nested sentinels to four Workbench placements, then run `uvx --no-cache --from "$CANDIDATE_WHEEL" spec-dock update "$MANAGED_TMP/existing-consumer"`。
7. Compare relative path、entry type、byte count、SHA-256 before/after and verify managed assets update。
8. Add/update hermetic installer/package tests where current suite lacks sensitivity。

### Primary paths

- `pyproject.toml`
- `src/spec_dock/cli.py`
- `src/spec_dock/assets/**`
- `tests/unit/infra/test_init_update.py`
- Existing package/installer tests under `tests/unit/infra/`

Only modify provider/package code if a verified distribution defect exists。Version/`uv.lock`変更はbuild/release contractが必要と証明した場合だけ。

### Verification

```bash
uv build --out-dir "$MANAGED_TMP/wheel"
uv run pytest tests/unit/infra
uv run pytest tests/cli_runtime/test_workbench.py tests/cli_runtime/test_artifact_import_chatgpt_output.py
git diff --check
```

- Fresh/update commands must use the absolute candidate wheel with `uvx --no-cache --from`; record wheel hash、installed version、resolved executable evidence。`PYTHONPATH`や`uvx --from .`をconsumer evidenceに使わない。
- Evidence records paths/bytes/hash/counts only; no sentinel/body output。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s02-01 | package inspection | C319-03 expected/forbidden wheel inventory |
| tc319-s02-02 | fresh installed smoke | C319-04 all required surfaces available |
| tc319-s02-03 | update byte comparison | C319-05 four placement path/type/bytes unchanged |

- Fresh code-reviewer then spec-reviewer。
- Commit only actual package/test/report repair; approved-no-op with exact evidence if no code delta。
- Push、clean/upstream `0 0`。

## 6. S03 — Public docs and exact dogfood parity

### Preconditions

- S02 proves candidate distribution/update preservation。

### Execution

1. Resolve docs impact for root/public/provider/dogfood surfaces。
2. Update provider authority first; refresh dogfood via approved candidate/provider projection。
3. Ensure root/public docs explain root manual selection、scoped source-wins、no sync/copy-back、Artifact byte/source preservation、blank coexistence、EAL/canonical boundary、experimental status。
4. Include Issue318 workflow docs in exact parity inventory。
5. Enumerate every parity exception as exact path/pair with owner、reason、generation direction、rebuild command。
6. Reject wildcard/category blanket exceptions and dogfood-only edits。

### Candidate path inventory

- `README.md`
- Provider/dogfood `docs/README.md`
- Provider/dogfood `docs/guide.md`
- Provider/dogfood `docs/reference_naming.md`
- Provider/dogfood `docs/reference_worktree.md`
- Provider/dogfood `docs/workflow_spec_authoring.md`
- Provider/dogfood `docs/workflow_chatgpt_authoring_pack.md`
- Provider/dogfood `docs/authoring/chatgpt-pack.md`
- Provider/install-root and root installed skills/assets affected by Issue315〜318
- Existing wrapper/init-update contract tests

Dedicated migration file、version bump、lock update are approved-no-op unless exact necessity is demonstrated。

### Verification

```bash
uv run pytest tests/cli_runtime/test_wrappers.py tests/unit/infra/test_init_update.py
git diff --check
```

- Exact pair `cmp`/SHA inventory。
- Search docs/help for forbidden automatic sync/root bulk copy/typed token claims and missing experimental/authority terms。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s03-01 | structural parity | C319-06 exact pairs/exceptions closed |
| tc319-s03-02 | docs contract | C319-07 public semantics complete/consistent |
| tc319-s03-03 | installer projection | Candidate update reproduces dogfood asset shape |

- Fresh spec-reviewer and, for executable/test changes, code-reviewer。
- Commit candidate: `docs(workbench): installed運用とArtifact import導線を整備` or exact observed repair。
- Push、clean/upstream `0 0`。

## 7. S04 — Focused, full, static, Linux quality

### Preconditions

- S01〜S03 final distribution/docs head committed。

### Execution order

1. Run Issue315 focused ignore/opacity/update/delete/source tests。
2. Run Issue316 focused copy application/infra/CLI/presentation tests。
3. Run Issue317 focused Artifact import domain/application/infra/CLI tests。
4. Run Issue318 wrapper/init-update/authoring-pack preservation tests。
5. Run unit, CLI runtime, integration, then full pytest。
6. Run repository authoritative configured static gate `make lint`（`scripts/static_analysis/run.sh`: Ruff check/format-check + mypy on `src/spec_dock tests`）。
7. Classify failures by owner; delegate minimal repair to DevCoder。
8. Explicitly inspect known Ruff relay:
   - `scripts/authoring-pack/authoring_pack_review.py`
   - `scripts/authoring-pack/invoke_chatgpt_backend.py`
9. Verify `.github/workflows/provider-ci.yml` Ubuntu full pytest collects/executes Artifact import publication tests on PR head。

### Commands

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
uv run pytest tests/integration
uv run pytest
make lint
uv run ruff check .
uv run ruff format --check .
git diff --check
```

`make lint` is the configured static/format authority。Global `ruff check .` / `ruff format --check .` are additional broader gates for the known `scripts/authoring-pack/**` relay and do not replace `make lint`。Focused selectors must be copied from existing test files/reports at execution time; do not invent absent node IDs。

### Repair boundaries

- Allowed: exact failing source/test/static paths and report evidence。
- Forbidden: skip/disable/exclude gate、unrelated formatting sweep beyond failing configured scope、new semantics。
- After repair: affected check → `make lint` → required broader Ruff gate → affected test lane/full rerun → fresh review。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s04-01 | focused regression | W1〜W4 contract pass on final head |
| tc319-s04-02 | full regression | C319-08 unit/CLI/integration/full pass |
| tc319-s04-03 | static | mypy/Ruff configured gates pass without disable |
| tc319-s04-04 | Linux CI | C319-09 publication path included and PR Ubuntu run required |

- Fresh code-reviewer then QA-reviewer。
- Focused repair commit(s) by owner; no mixed cleanup。
- Push、clean/upstream `0 0`。

## 8. S05 — Fresh installed integrated manual scenario

### Preconditions

- S04 local quality pass。
- Candidate wheel hash/head fixed。
- Fresh `codex-tmp` managed pathへfixtureを作る。Live GitHub mutationを一切許可しない。

### Scenario

1. `uvx --no-cache --from "$CANDIDATE_WHEEL" spec-dock init <fixture-repo>`でsafe fresh consumerを作り、`git init`と`git remote add origin https://github.com/example/repo.git`を実行する。このoriginはrepo scope解決用のsynthetic文字列であり、fetch/push/networkを行わない。
2. Fixture-local fake `gh`をfixture `PATH`へ置く。Exact argvは`gh issue list ...`と`gh issue view 90001|90002|90003 ...`だけをallowlistし、各payloadは`number`、`state: OPEN`、safe title、empty labels、deterministic `updatedAt`、`https://github.com/example/repo/issues/<n>`だけを返す。Create/edit/close/comment/unknown argv/network操作はexit 99で拒否し、全argvをfixture-local logへ記録する。
3. Candidate executableとfake `gh`で実在commandを実行する。
   - `spec-dock new initiative --title "Fixture Initiative" --github-issue 90001`
   - `spec-dock new epic --initiative init-90001 --title "Fixture Epic" --github-issue 90002`
   - `spec-dock new issue --epic epic-90002 --title "Fixture Issue" --github-issue 90003`
4. Synthetic node scaffoldをfixture repoへcommitし、そのcommitからsecond same-repository linked worktreeを作って両側に同じGitHub-linked nodeを投影する。
5. `<fixture-repo>/spec-dock/.workbench/<date-bucket>/`へsafe synthetic complete Markdownを置く。
6. その一fileだけをsource `iss-90003` scope-local `.workbench/`へmanual selection/copyする。
7. Source worktreeでcandidate installed executableの`spec-dock workbench copy --scope iss-90003 --to <target-worktree-absolute-path> --json`を実行する。
8. Destination-only retention、source-wins、binary/config/nested content opacity、source symlink policyを本文出力なしで検証する。
9. Target worktreeで`spec-dock artifact import chatgpt-output --issue iss-90003 --file <repo-relative-iss-90003-workbench-markdown> --title "Fixture ChatGPT output" --slug fixture-chatgpt-output --json`を実行する。
10. Receipt、source survival、SHA/bytes/cmp、no overwrite/collision behaviorを検証する。
11. Preservation statusとEAL adoption statusを別々に記録する。
12. Preservation/adoption/review checkpoint後だけsafe canonical rewriteし、Artifact不変を確認する。
13. Default semantic discoveryが全Workbench contentを無視することを確認する。

### Evidence boundary

- Version control may contain only safe Artifact/manual report evidence explicitly required。
- Root/scoped Workbench sources remain ignored/untracked and may be deleted after evidence handoff。
- Report records repo-relative paths、hash、byte count、result code、warning/committed status only。
- Fake `gh`がunknown operationを受けた場合、candidate executableがsource checkoutへ解決された場合、external GitHub state mutationが疑われる場合は即停止する。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s05-01 | direct manual | C319-10 complete installed flow pass |
| tc319-s05-02 | authority inspection | EAL/preservation/canonical states remain separate |
| tc319-s05-03 | secrecy inspection | C319-15 no body/secret/absolute path exposure |

- Fresh spec-reviewer then QA-reviewer。
- Commit safe evidence/report only; never stage Workbench sources。
- Push、clean/upstream `0 0`。

## 9. S90 — Epic closure and docs impact

### Execution

- Build exact Issue315〜319 inventory from merge-base/main to current head。
- Update Epic report E-RQ-001〜024 and E-AC-001〜016 with current evidence links/results。
- Close Epic EAL/OAL/docs impact/Issue links/risk register without unresolved blocked/stale entries。
- Distinguish historical Issue evidence、Issue319 current local evidence、PR/CI pending evidence。
- Confirm no new product semantics、migration、version/release decision was introduced without authority。
- Confirm PR URL is still pending and no merge-prepared claim exists。

### Test contract / review / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s90-01 | trace inspection | C319-11 all E-RQ/E-AC mapped to evidence or explicit pending PR gate |
| tc319-s90-02 | ledger inspection | EAL/OAL/docs/risk/Issue links complete; no blocked/stale |
| tc319-s90-03 | scope inspection | C319-16 minimal diff/non-goals preserved |

- Fresh spec-reviewer。
- Commit candidate: `docs(epic-312): Workbench機能の品質証跡を統合`。
- Push、clean/upstream `0 0`。

## 10. S99 — Final QA → code → spec review

### Preconditions

- S00〜S90 committed/pushed/clean。
- Current branch remains current with latest main; if not, return S01 and rerun affected gates。
- Full/static/manual pass on current head。

### Ordered gates

1. `qa-reviewer` `gpt-5.6-sol` / medium:
   - Whole Issue/Epic obligation coverage、package/fresh/update/dogfood/manual/full/platform evidence。
   - Explicit decision whether additional integration test is required。
2. Fresh `code-reviewer` `gpt-5.6-sol` / medium after QA pass:
   - `origin/main...HEAD` integrated diff、provider authority、preservation/copy/import safety、test sensitivity、static quality。
3. Fresh `spec-reviewer` `gpt-5.6-sol` / medium after code pass:
   - Requirement/Design/Plan/Report/Epic/implementation/tests/docs/EAL/OAL alignment and PR-pending claim integrity。

### Repair loop

- Any failure stops promotion。
- Route finding to owning step/contract and fresh DevCoder。
- Run affected/full/static gates as impact requires。
- Rerun from failed gate; downstream previous pass becomes stale if head changes。

### Test contract / commit

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s99-01 | ordered fresh review | C319-12 QA→code→spec pass on one head |

- Commit final review ledgers/reports, push, verify clean/upstream `0 0`。
- Do not create PR before this commit is pushed。

## 11. S100 — PR creation, final-head observation, repair, finish

### Phase A: PR creation and final report head

1. Re-fetch main; return S01 if behind/diverged/conflicted。
2. Push current clean branch and verify upstream `0 0`。
3. Create or discover single `main` PR using approved GitHub PR workflow。
4. Update Issue/Epic report with PR URL、head、planned checks/review observation、no-merge boundary。
5. Commit/push that report update。This commit becomes final observation head。

### Phase B: terminal observation

1. Trigger fixed Codex review endpoint as required by project workflow。
2. Observe GitHub Actions checks including Ubuntu provider full pytest。
3. Observe review submissions、comments、inline threads、mergeability、base drift。
4. If any blocking finding/check/base drift occurs:
   - route to S01/S02/S03/S04/S05/S90 as owner;
   - fresh DevCoder repair;
   - rerun affected local/reviewer gates;
   - commit/push;
   - update report before re-observation if needed;
   - treat new head as final and repeat all terminal observation。
5. Do not disable checks、dismiss valid findings、force push、or self-claim mergeability。

### Phase C: lifecycle

- When final head has required checks pass、no unresolved blocking review/thread、mergeable/no conflict、no base drift:
  - Do not create another versioned report commit。
  - Record terminal evidence in GitHub state/PR comment/final response as external post-commit evidence。
  - Run `issue finish` only now。
  - Immediately run `git status --short` and upstream comparison. Current runtime is expected to mutate only GitHub Issue state and ignored active/derived projections; if any tracked delta appears, terminal status is revoked, the delta is reviewed/committed/pushed, and final-head observation runs again。
  - Keep PR open and unmerged。
  - Distinguish Epic spec/quality closure from GitHub Epic #312 close and PR merge。

### Test contract

| Test ID | Evidence level | Expected close |
|---|---|---|
| tc319-s100-01 | external PR observation | C319-13 PR/check/review/mergeability/base state pass on final head |
| tc319-s100-02 | lifecycle | C319-14 issue finish after terminal observation、no merge、no post-observation versioned mutation |

## 12. Docs impact inventory contract

Before S03/S90 close, every candidate path must have one disposition:

- `update-complete`
- `verified-no-op` with exact reason/command
- `generated-exception` with exact path/owner/direction/rebuild command
- `rejected-scope-expansion`

No wildcard/category-only disposition is allowed。At minimum inspect:

- `README.md`
- Provider/dogfood `docs/README.md`, `guide.md`, `reference_naming.md`, `reference_worktree.md`
- Provider/dogfood ChatGPT authoring/workflow docs
- Provider/install-root and root installed planning skills
- Provider/dogfood runtime/scripts for Issue315〜317
- `.github/workflows/provider-ci.yml`
- `pyproject.toml`, `src/spec_dock/cli.py`, `src/spec_dock/__init__.py`, `uv.lock`
- Installer/package/focused/full/static/manual tests

## 13. Completion gate

Issue319 is complete only when:

- C319-01〜16 all passed with current evidence。
- Planning/assurance valid and no unresolved blocked/stale EAL/OAL。
- Latest main integrated。
- Package/fresh/update/parity/docs/full/static/Linux/manual gates passed。
- Epic E-RQ/E-AC closure reviewed。
- Final QA→code→spec passed on latest pre-PR head。
- PR final report head pushed, checks/reviews/mergeability/base drift terminally observed。
- `issue finish` executed after observation and PR remains unmerged。

If terminal evidence requires a versioned change, completion is revoked and the relevant step/observation must rerun。
