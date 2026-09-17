---
種別: 実装計画書（Issue）
ID: "iss-00396"
タイトル: "Build Once Provider Gate and Regression Policy Cutover"
関連GitHub: ["#396"]
状態: "draft"
詳細化状態: "implementation-ready-candidate"
最終更新: "2026-09-18"
依存:
  - "requirement.md"
  - "design.md"
  - "iss-00395"
  - "../../plan.md"
  - "../../artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["epic-00384", "init-local-00003"]
Planning Level: "implementation-ready"
実装開始許可: false
owner_decisions_required: []
human_merge_only: true
repository_evidence:
  role: "issue-elaboration-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00396-build-once-provider-gate-and-regression-policy-cutover"
  sha: "fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d"
  tree: "37eabc1aa250838dcd9f61d627309b0ff27e0db7"
qualification_authority: "E384-QUAL-001"
---

# iss-00396 Build Once Provider Gate and Regression Policy Cutover — 実装計画

## 1. Execution boundary

本Planはimplementation-ready specification candidateであり、Product/test/workflow/policy実装をまだ許可しない。実行開始には次を全て要求する。

1. 本R/D/P、`artifacts/20260917t124918z--luna-max-implementation-handoff.md`、closed contract schema、role-ownership baseline、snapshot helper、B1/B2 receiptとraw evidence、人間向けHTMLが同一ZIP artifactへ収録され、R/D/PとhandoffがIssue canonical copyへbyte-identicalに反映される。
2. clean pushed exact SHA/treeがGitHub connectorで一致する。
3. 初回は`iss396-spec-review-red`で独立`chatgpt-spec-review-strict`を実行し、修正候補は同じsession IDへ`--followup`して、最新結果が`review_status=pass`、P0=0、P1=0となる。
4. 主担当がGitHub Issue #396 bodyをcanonical projectionへ更新し、readbackする。
5. ユーザーがexplicit implementation dispatchを出す。
6. concurrent writerがいない。

Formal `issue start`済みという事実、#392/#395 CLOSED、B1/B2 GREEN、`owner_decisions_required=[]`だけでは実装を開始しない。

実装者はcheckpointを順に一つずつ完了し、各checkpointのexit evidenceを保存する。後段の証拠を前段へ流用しない。中間stateはIssue branch内の作業状態であり、mergeable/acceptedではない。

## 2. Fixed identities and shell constants

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
ISSUE_ID='iss-00396'
ISSUE_BRANCH='iss-00396-build-once-provider-gate-and-regression-policy-cutover'
INTEGRATION_BRANCH='codex/epic-00384-provider-test-strategy-planning'
B2_SHA='fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d'
B2_TREE='37eabc1aa250838dcd9f61d627309b0ff27e0db7'
QUAL_AUTHORITY='E384-QUAL-001'
ISSUE_DIR='spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover'
PARENT_DIR='spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction'
EVIDENCE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/iss-00396-evidence.XXXXXXXX")"
chmod 700 "$EVIDENCE_ROOT"
```

`SPEC_FREEZE_SHA` / `SPEC_FREEZE_TREE`は独立review対象のclean pushed tipから実行時に設定する。B2 SHAはentry provenanceであり、spec-only commits後のcurrent tipと混同しない。

Implementation admissionで再検証するB2 exact entry identityは`fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`である。B2のraw resultとbefore-ledgerはそれぞれIssue artifact `20260917t124918z-02--iss-00395-b2-full-regression-result.json`（SHA-256 `bd4630014ee046967713c89c7b8112a2ebe7f10aa85100256aca8a677d817786`）と`20260917t124919z--iss-00395-b2-ledger-before.json`（SHA-256 `838f1415f2a4399a3f18cf7914dc0b2f3648cb06a5d623de4ca7a22648a87a0d`）である。これは#395のpost-merge B1/B2 entry proofだけで、#396のB3・replacement gate・Product実装を証明しない。

`artifacts/provider-gate-contracts-v1.schema.json`がruntime/evidence/execution wireの唯一のclosed schema sourceである。`artifacts/role-ownership-v1.json`とそこから参照される2つのraw collect-only outputsはreviewed 2,214-node baselineである。Implementation時のruntime copiesはcanonical artifactsとbyte-identicalに保ち、schema/ownership hashをpacketのEvidenceIndexへ含める。

## 3. Planned change inventory

### 3.1 NEW

```text
scripts/maintenance/generate_provider_qualification_policy.py
scripts/quality/provider_gate/__init__.py
scripts/quality/provider_gate/contracts.py
scripts/quality/provider_gate/codec.py
scripts/quality/provider_gate/identity.py
scripts/quality/provider_gate/artifacts.py
scripts/quality/provider_gate/environment.py
scripts/quality/provider_gate/process_tree.py
scripts/quality/provider_gate/pytest_plugin.py
scripts/quality/provider_gate/history.py
scripts/quality/provider_gate/faults.py
scripts/quality/provider_gate/consumer_scan.py
scripts/quality/provider_gate/evaluator.py
scripts/quality/provider_gate/evidence.py
scripts/quality/provider_gate/cli.py
scripts/quality/provider_gate/_qualification_policy_generated.py
scripts/quality/provider_gate/contracts/specdock-linux-qualification-v1.json
scripts/quality/provider_gate/contracts/provider-gate-contracts-v1.schema.json
scripts/quality/provider_gate/contracts/role-ownership-v1.json
scripts/quality/provider_gate/contracts/seeded-fault-catalogue-v1.json
scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json
tests/unit/provider_gate/__init__.py
tests/unit/provider_gate/test_policy_projection.py
tests/unit/provider_gate/test_contracts.py
tests/unit/provider_gate/test_identity.py
tests/unit/provider_gate/test_artifacts.py
tests/unit/provider_gate/test_environment.py
tests/unit/provider_gate/test_process_tree.py
tests/unit/provider_gate/test_role_ownership.py
tests/unit/provider_gate/test_role_transition_seam.py
tests/unit/provider_gate/test_history.py
tests/unit/provider_gate/test_fault_catalogue.py
tests/unit/provider_gate/test_evaluator.py
tests/unit/provider_gate/test_consumer_inventory.py
tests/integration/test_provider_gate_role_graph.py
tests/integration/test_provider_gate_faults.py
docs/provider-gate.md
```

### 3.2 MODIFY

```text
.github/workflows/provider-ci.yml
AGENTS.md
pyproject.toml
tests/integration/test_epic_00343_distribution.py
tests/cli_runtime/test_distribution_cutover.py
```

`src/spec_dock/assets/**`、`spec-dock/**`、provider lifecycle production sourceはdefault planで変更しない。

### 3.3 DELETE after replacement and consumer-zero

```text
.github/workflows/provider-full-regression.yml
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
tests/conftest.py
tests/unit/test_full_regression_baseline.py
tests/unit/test_provider_test_lanes.py
```

`tests/conftest.py`はcurrent contentがold lane/policy hookだけであることをimplementation tipで再確認してからfile deleteする。共通fixtureが追加されていた場合はold symbolsだけを削除し、他内容をpreserveする。

### 3.4 NO-TOUCH / protected

```text
.github/workflows/ci.yml
src/spec_dock/assets/install_root/.github/workflows/ci.yml
src/spec_dock/provider_lifecycle/**
tests/unit/provider_lifecycle/**
spec-dock/initiatives/**  # canonical #396 docs publicationを除き、Product実装中はread-only
spec-dock/active/**
spec-dock/.agent/**
spec-dock/diagrams/**
spec-dock/.workbench/**   # dedicated new evidence path以外
```

## 4. Checkpoint P00 — Specification publication and independent review

Owner: 主担当 / independent reviewer。Product mutation禁止。

1. `artifacts/issue-396-specification-pack.zip`のrootに`README.md`を置き、repository-relative path hierarchyを保ってcanonical Issue R/D/P、handoff、regular Issue artifacts（対象ZIP自身を除く）、親Epic R/D/Pと明示dependency artifactsを収録する。ZIP内Issue docsとartifactsはcanonical direct-child filesにbyte-identicalとする。
2. ZIP内`manifest.sha256`はREADMEを含む全payload entryをpath順にhashし、manifest自身とZIP file自身は自己参照させない。個別entry hash検証後、ZIPのSHA-256と`git hash-object`出力を`EVIDENCE_ROOT/p00-zip-identity.txt`へ記録する。commit後は`git rev-parse HEAD:$ISSUE_DIR/artifacts/issue-396-specification-pack.zip`が記録済みblob IDと一致することを確認する。
3. schema、role ownership、raw collection output、snapshot helper、remediation analysis、B1/B2 receipt/raw JSON、説明HTMLをIssue direct-child `artifacts/`へ配置し、ZIP内とbyte-identicalであることを確認する。
4. `./spec-dock/scripts/spec-dock validate`を実行する。
5. spec-only diffを確認し、commit/pushする。
6. GitHub connectorでrepository/branch/full SHAをverifyする。
7. 初回は新しい独立Red session `iss396-spec-review-red`で`chatgpt-spec-review-strict`を実行する。P0/P1指摘の修正後は同じsessionへ`--followup iss396-spec-review-red`を渡し、目的・範囲を変えず、候補SHAごとにStrict gatesを再実行する。P2/P3は記録だけで、修正・task化・合否条件化しない。
8. latest reviewがpass、P0=0、P1=0の後、GitHub Issue #396 body projectionを主担当が更新し、readbackする。

Exact local verification:

```bash
./spec-dock/scripts/spec-dock validate | tee "$EVIDENCE_ROOT/p00-validate.txt"
git diff --check
git status --short
git diff --name-only "$B2_SHA"...HEAD | tee "$EVIDENCE_ROOT/p00-spec-diff.txt"
git hash-object "$ISSUE_DIR/artifacts/issue-396-specification-pack.zip" \
  | tee "$EVIDENCE_ROOT/p00-zip-identity.txt"
shasum -a 256 "$ISSUE_DIR/artifacts/issue-396-specification-pack.zip" \
  | tee -a "$EVIDENCE_ROOT/p00-zip-identity.txt"
```

Expected output class:

- validate exit 0、`nodes=236`またはspec publicationに伴う正当なnode count不変。
- ZIP member hashesとIssue canonical copyのhashが一致し、HTML browser validationが成功。ZIP SHA-256とpre-commit Git blob IDはEvidenceRootに記録し、commit後のpath blob IDと一致。
- diffは#396 canonical R/D/P/Artifactsと、projectionに必要なgenerated docsだけ。
- Product、tests、workflow、policy data差分0。
- 同一Red sessionの最新Strict reviewが`pass`, P0=0, P1=0。

Failure: Product file差分、review fail、SHA mismatchでは停止。過去reviewへfallbackしない。

## 5. Checkpoint P01 — Read-only implementation admission

Owner: implementation agent。Mutation前。

### 5.1 Repository identity

```bash
CURRENT_HEAD="$(git rev-parse HEAD^{commit})"
CURRENT_TREE="$(git rev-parse HEAD^{tree})"
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')"
UPSTREAM_HEAD="$(git rev-parse '@{upstream}^{commit}')"
REMOTE_HEAD="$(git ls-remote --heads origin "$ISSUE_BRANCH" | awk '{print $1}')"

printf '%s\n' "$CURRENT_HEAD" "$CURRENT_TREE" "$UPSTREAM" "$UPSTREAM_HEAD" "$REMOTE_HEAD" \
  > "$EVIDENCE_ROOT/p01-identity.txt"

test "$CURRENT_HEAD" = "$SPEC_FREEZE_SHA"
test "$CURRENT_TREE" = "$SPEC_FREEZE_TREE"
test "$UPSTREAM_HEAD" = "$SPEC_FREEZE_SHA"
test "$REMOTE_HEAD" = "$SPEC_FREEZE_SHA"
test -z "$(git status --porcelain=v1)"
```

Expected: all exact equality、clean worktree。

### 5.2 Entry provenance and dependency

```bash
git merge-base --is-ancestor "$B2_SHA" HEAD
git show -s --format='%H %T' "$B2_SHA" | tee "$EVIDENCE_ROOT/p01-b2-identity.txt"
./spec-dock/scripts/spec-dock deps check "$ISSUE_ID" | tee "$EVIDENCE_ROOT/p01-deps.txt"
./spec-dock/scripts/spec-dock active show | tee "$EVIDENCE_ROOT/p01-active.txt"
./spec-dock/scripts/spec-dock validate | tee "$EVIDENCE_ROOT/p01-validate.txt"
```

Expected:

- `B2_SHA B2_TREE` exact。
- dependency #395 ready/closed。
- active Issue exact `iss-00396`。
- nodes=236、validation pass。

### 5.3 B1/B2 raw evidence

Receiptに記載した二つのraw JSONをprivate evidence workspaceへcopyしhashを再検証する。Tracked implementation treeへraw local absolute pathsをcommitしない。

```bash
sha256sum "$B2_RESULT_JSON"
sha256sum "$B2_BEFORE_LEDGER_JSON"
```

Expected:

```text
bd4630014ee046967713c89c7b8112a2ebe7f10aa85100256aca8a677d817786  <result>
838f1415f2a4399a3f18cf7914dc0b2f3648cb06a5d623de4ca7a22648a87a0d  <before-ledger>
```

Failure: hash不一致、B2 evaluation mismatchでは停止。添付本文からJSONを再構成しない。

### 5.4 Concurrent writer

`git status`、current worktree list、open PR/branch activityをread-only確認し、same Issue branchへ別writerがいないことをexecution packetに記録する。自動lock/daemonを追加しない。

## 6. Checkpoint P02 — Current external state capture

Owner: implementation agent read-only + human when admin read is unavailable。Mutation禁止。

Capture:

1. current `.github/workflows/provider-ci.yml` emitted check names/jobs。
2. representative PRのcheck-runs/check-suites。
3. effective required contexts/ruleset scope。
4. merge queue/merge_group state。
5. unrelated required contexts `U`。
6. Actions artifact retention policy/available maximum。
7. runner provider/class/image/effective resource observations。

Repository/API commands use actual authorized tooling. Examples:

```bash
gh api "repos/${REPOSITORY}/actions/workflows" \
  > "$EVIDENCE_ROOT/p02-workflows.json"

gh api "repos/${REPOSITORY}/actions/runs?branch=${ISSUE_BRANCH}&per_page=100" \
  > "$EVIDENCE_ROOT/p02-runs.json"
```

Ruleset/branch protection endpointsはconnection permissionに依存する。404/403/unsupportedをpermission denialと決めつけず、observed statusを記録する。未確認ならhumanがUIまたはread-only `gh api` exportを提供する。

Exit criteria:

- `OLD_REQUIRED_CONTEXTS`、`UNRELATED_REQUIRED_CONTEXTS`、merge queue scopeをactual stringsで取得。
- `NEW_CONTEXT_NAME`はreplacement shadow runのactual check-run nameから後で確定する。ここで創作しない。
- runner environment candidateがparent capability boundaryを証明可能、またはP02 stop。
- artifact retentionがpost-merge B3 campaignまでbytesを保持可能、またはP02 stop。

P02のcaptureが揃うまでworkflow codeを書かない。

## 7. Checkpoint P03 — Protected data and current-surface baseline

### 7.1 Protected snapshot

`artifacts/capture_protected_snapshot.py`が唯一のreview済みcapture実装である。P03/P16の双方で同一script SHA-256を確認し、専用evidence pathをtracked tree外へ置く。

```bash
test "$(sha256sum "$ISSUE_DIR/artifacts/capture_protected_snapshot.py" | awk '{print $1}')" = "$SNAPSHOT_HELPER_SHA256"
python "$ISSUE_DIR/artifacts/capture_protected_snapshot.py" \
  --repository . \
  --output "$EVIDENCE_ROOT/p03-protected-before.json"
```

`SNAPSHOT_HELPER_SHA256`はIssue artifact SHA manifestおよびExecutionPacket EvidenceIndexから得る。Snapshot roots/exclusionはRequirement §4.3 / Design §13.3とschema `ProtectedTreeSnapshotV1`が同一値で定義する。Symlinkをfollowしない。Outputはfresh pathへexclusive作成する。

### 7.2 Current old consumer inventory

```bash
rg -n --hidden --glob '!.git/**' \
  'full-regression-ledger|full-regression-timing-weights|verify_full_regression|full_regression_baseline|--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|provider-full-regression' \
  . > "$EVIDENCE_ROOT/p03-old-consumers-rg.txt" || true
```

これはdiscoveryのみで、mechanical proofではない。結果から`old-policy-retirement-v1.json`の初期expected inventoryを作る。Historical parent docs、receipt、retained pathsを分類する。

### 7.3 Retained workflow proof

```bash
cmp --silent \
  .github/workflows/ci.yml \
  src/spec_dock/assets/install_root/.github/workflows/ci.yml
sha256sum \
  .github/workflows/ci.yml \
  src/spec_dock/assets/install_root/.github/workflows/ci.yml \
  > "$EVIDENCE_ROOT/p03-retained-workflow.txt"
```

Expected: byte-identical。

## 8. Checkpoint P04 — First RED: policy projection and closed schemas

最初にtestsだけを追加する。

Add:

- `tests/unit/provider_gate/test_policy_projection.py`
- `tests/unit/provider_gate/test_contracts.py`
- initial contract goldens/fixtures

Run:

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_policy_projection.py \
  tests/unit/provider_gate/test_contracts.py \
  --tb=short | tee "$EVIDENCE_ROOT/p04-red.txt"
```

Expected RED class:

- missing `scripts.quality.provider_gate` / generator / generated projection。
- no unrelated existing test failure。
- RED reasonがassertion/missing implementationであり、test collection policy skipではない。

Then implement:

- `contracts.py`
- `codec.py`
- generator
- generated projection

GREEN:

```bash
uv run python scripts/maintenance/generate_provider_qualification_policy.py --check
uv run pytest -q \
  tests/unit/provider_gate/test_policy_projection.py \
  tests/unit/provider_gate/test_contracts.py \
  --tb=short | tee "$EVIDENCE_ROOT/p04-green.txt"
```

Expected: exit 0、skip/xfail 0。Generated diff 0。

Stop if parent section parse is ambiguous or semantic tokens cannot be extracted without manual duplicated constants。

## 9. Checkpoint P05 — Candidate identity and artifact build/reuse RED→GREEN

### 9.1 RED tests

Add artifact/identity tests covering:

- exact source SHA/tree。
- manifest canonical bytes/hash。
- one producer resolution。
- actual wheel/sdist bytes mismatch。
- missing/multiple/expired producer artifact。
- source/tree mismatch。
- rerun producer rejection。
- no downstream build command。

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_identity.py \
  tests/unit/provider_gate/test_artifacts.py \
  --tb=short | tee "$EVIDENCE_ROOT/p05-red.txt"
```

Expected RED: missing implementation only。

### 9.2 Implement

Implement `identity.py`, `artifacts.py`, required contracts and CLI commands.

Candidate build command invoked by producer path:

```bash
uv run python -m scripts.quality.provider_gate.cli resolve-source-identity \
  --repository "$REPOSITORY" \
  --event-payload "$GITHUB_EVENT_PATH" \
  --workflow-run-id "$GITHUB_RUN_ID" \
  --run-attempt "$GITHUB_RUN_ATTEMPT" \
  --output "$RUNNER_TEMP/source_identity.json"

uv run python -m scripts.quality.provider_gate.cli build-candidate \
  --repository . \
  --source-identity "$RUNNER_TEMP/source_identity.json" \
  --workflow-run-id "$GITHUB_RUN_ID" \
  --run-attempt "$GITHUB_RUN_ATTEMPT" \
  --output "$CANDIDATE_DIR"
```

`resolve-source-identity`はDesign §12.2と`SourceIdentityV1`に従ってevent別にSHAを解決する。`pull_request`はpayloadのhead SHA/repository、`workflow_dispatch`はrequired `inputs.source_sha`、`merge_group`はmerge-group SHAを使う。全consumerはproducerが保存した同じ`source_identity.json` bytesを検証する。PRのraw `GITHUB_SHA`をcandidate SHAへ使わない。

Inside CLI, top-level packaging process is exactly:

```bash
uv build --sdist --wheel --out-dir "$CANDIDATE_DIR/dist" --clear .
```

The CLI refuses preexisting dist output, additional wheel/sdist, `run_attempt != 1`, source mismatch, second producer observation。

### 9.3 GREEN

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_identity.py \
  tests/unit/provider_gate/test_artifacts.py \
  --tb=short | tee "$EVIDENCE_ROOT/p05-green.txt"
```

Expected: all pass、skip/xfail 0。

Do not run a real qualification build yet; synthetic/temp artifact tests only。A real source SHA packaging build must be performed by the selected workflow producer to preserve count semantics。

## 10. Checkpoint P06 — Environment and process collector RED→GREEN

### 10.1 Environment RED

Add tests for:

- exact contract schema/order。
- fingerprint deterministic。
- provider/class/CPU family/quota/memory/image/Python/dependency/tool/filesystem capture。
- CPU/memory unprovable/out-of-bound rejection。
- architecture wrong、GPU/high-tier/burst drift rejection。
- fingerprint drift。

```bash
uv run pytest -q tests/unit/provider_gate/test_environment.py --tb=short \
  | tee "$EVIDENCE_ROOT/p06-environment-red.txt"
```

Implement `environment.py` and freeze **candidate** contract only after P02 actual capture. No placeholder strings such as `unknown` / `ubuntu-latest` alone are accepted as final fingerprint evidence。

### 10.2 Process RED

Add controlled Linux tests:

- root + CPU child totals。
- grandchild CPU included。
- child exits after root and interval stays open。
- parent process killed、subreaper reaps orphan。
- descendant leak causes reject。
- second pytest root / worker/shard detected。
- wall/cpu raw values and Decimal ratio。
- missing cgroup v2/effective limit fail closed。

```bash
uv run pytest -q tests/unit/provider_gate/test_process_tree.py --tb=short \
  | tee "$EVIDENCE_ROOT/p06-process-red.txt"
```

Implement `process_tree.py`。通常のdeveloper環境でcgroup controlを利用できない場合、adapter unit testsはhermeticなfake filesystem/process fixtureを使う。実platform integration testは指定Linux qualification environmentで必ず実行し、そのroleではskipしない。Localで利用不能であることをpassへ変換しない。

### 10.3 GREEN

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_environment.py \
  tests/unit/provider_gate/test_process_tree.py \
  --tb=short | tee "$EVIDENCE_ROOT/p06-green.txt"
```

Expected: unit GREEN。Actual runner admission remains pending until shadow workflow。

## 11. Checkpoint P07 — Role ownership and pytest plugin RED→GREEN

### 11.1 Freeze ownership before executing role nodes

Review済みbaselineは`artifacts/role-ownership-v1.json`であり、source `3ded647d247b9399a4b79ad6f854d6a87fbf4313` / tree `614778cc7e6e64609a7de80bf2428b3e7f5ec4b7`におけるLinux/macOS各2,214 unique node IDsである。normalized set hashは`b6e742ecba64ec02512892cf99d0c0c7273c175f56e0bc5a5666127f885f03da`、owner countはLinux canonical 2,191、sdist smoke 1、macOS delta 22。raw output filesは同じartifact directory内にあり、contractのEvidenceRef/hashとbyte一致する。

P07の最初のcollection-only testは、実装branch SHAで収集したnode集合とreview済みbaselineの差分を表示する。差分が0ならownership contractをそのまま使用する。追加・削除・rename nodeがある場合は、test bodyや旧fast/full markerを実行・owner決定へ使う前にcollection-only差分を確認し、明示的な役割根拠と一意ownerをcontractへ登録し直し、そのhashと差分をreviewする。Baselineと新candidateの母集団を暗黙に混ぜない。

### 11.2 Tests

- every collected node gets exactly one role owner。
- role intersections empty。
- union complete。
- Linux role uses one pytest process and no worker/shard option。
- role-out nodes are deselected, not skipped/xfail。
- execution observation detects duplicate node、policy skip、approved failure。
- macOS selectors include actual platform-specific nodes; Linux does not execute them。
- sdist role owns package artifact tests; no duplicate execution in Linux canonical。
- `tests/conftest.py` role transition seamがCLIの`-p scripts.quality.provider_gate.pytest_plugin`登録をrequireする。plugin自身はcollection filter hookを登録せず、root conftestから`prepare_role_collection(config, items)`を一度だけ呼ぶ。plugin未登録・role option欠落・schema不正・unknown node・old flag併用をcollection開始前にrejectし、role modeではlegacy `POLICY_SKIP_REASON` hookを通さない。

```bash
uv run pytest -q tests/unit/provider_gate/test_role_transition_seam.py --tb=short \
  | tee "$EVIDENCE_ROOT/p07-transition-seam.txt"
uv run pytest -q tests/unit/provider_gate/test_role_ownership.py --tb=short \
  | tee "$EVIDENCE_ROOT/p07-role-ownership.txt"
```

Implement `pytest_plugin.py` and role contract. GREEN expected all pass。

### 11.3 Integration dry graph

```bash
uv run pytest -q tests/integration/test_provider_gate_role_graph.py --tb=short \
  | tee "$EVIDENCE_ROOT/p07-role-graph.txt"
```

This test uses synthetic/small candidate bytes and must not claim qualification。Expected: role count exact、same manifest all roles、duplicate 0。

## 12. Checkpoint P08 — Attempt/history/evaluator/fault catalogue RED→GREEN

### 12.1 History tests

Add exact cases:

- chronological first five from `created_at` + run ID。
- first 1–5にfailure/cancel/missingを残す。
- sixth successで置換しない。
- same candidateでcampaign ID変更をreject。
- latest twenty includes failed/cancel/missing。
- 19 member => incomplete not per-attempt failure。
- 21件目以降はchronological latest-twenty境界により最古memberだけが自然にwindow外となる。
- same run ID `run_attempt=2` rejected/rerun count。
- duplicate attempt ID/artifact replacement reject。

### 12.2 Evaluator tests

- per-attempt result independent from campaign/window completeness。
- all roles conjunction。
- identity/raw missing reject。
- parent-generated wall/CPU/correctness predicates applied independently。
- aggregate cannot mean/median/round/offset failures。
- macOS role does not receive Linux performance predicate。

### 12.3 Fault catalogue tests

Freeze catalogue denominator before execution and inject all entries. Test denominator reduction、missing execution、wrong expected violation、miss。

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_history.py \
  tests/unit/provider_gate/test_evaluator.py \
  tests/unit/provider_gate/test_fault_catalogue.py \
  --tb=short | tee "$EVIDENCE_ROOT/p08-red.txt"
```

Implement `history.py`, `evaluator.py`, `faults.py`, `evidence.py` and contracts。Then GREEN expected all pass、skip/xfail 0。

## 13. Checkpoint P09 — Consumer scanner and retained workflow guard

### 13.1 RED

Add `test_consumer_inventory.py` first. At this checkpoint old consumer count is intentionally >0, so tests have two modes:

- `inventory-current`: exact expected current old consumers must match contract。
- `inventory-final`: requires zero and is RED until retirement checkpoint。

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_current_inventory_matches_pre_cutover_contract \
  --tb=short | tee "$EVIDENCE_ROOT/p09-current-green.txt"

set +e
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_final_source_has_zero_old_policy_consumers \
  --tb=short | tee "$EVIDENCE_ROOT/p09-final-red.txt"
status=$?
set -e
test "$status" -ne 0
```

Expected final RED lists concrete current consumers; it must not fail because scanner/module is missing。

### 13.2 Scanner implementation

Implement AST/YAML/JSON/text scanner. Historical allowlist paths may mention old names but cannot import/call/execute them. The retirement contract itself is metadata, not a runtime consumer。

Retained workflow test:

```bash
uv run pytest -q \
  tests/unit/provider_gate/test_consumer_inventory.py::test_retained_installed_consumer_workflow_is_present_and_byte_identical \
  --tb=short
```

Expected GREEN throughout all checkpoints。

## 14. Checkpoint P10 — Packaging consumer refactor and nonpolicy test move

### 14.1 `candidate_wheel` dual mode

Refactor `tests/integration/test_epic_00343_distribution.py::candidate_wheel`:

- `SPECDOCK_CANDIDATE_MANIFEST` + bundle paths present => qualification artifact mode、hash/source verify、build helper not called。
- absent => local-test-build mode、existing helper may build for local test only、result explicitly`qualification_eligible=false`。
- CI final gate must always set artifact mode。
- unit/workflow static test proves final gate cannot enter local fallback。

Preserve existing CandidateWheel assertions and Product behavior。

### 14.2 Move nonpolicy regression

Move `test_distribution_cutover_reuses_plain_init_only_as_update_or_uninstall_setup` into `tests/cli_runtime/test_distribution_cutover.py` with imports/helpers adjusted。Run before deleting old file:

```bash
uv run pytest -q \
  tests/cli_runtime/test_distribution_cutover.py \
  --tb=short | tee "$EVIDENCE_ROOT/p10-distribution-cutover.txt"
```

Expected: behavior pass。No old lane flags。

### 14.3 Focused package tests

```bash
uv run pytest -q \
  tests/integration/test_epic_00343_distribution.py \
  --tb=short | tee "$EVIDENCE_ROOT/p10-local-package.txt"
```

This local run is not qualification evidence. Record its build count separately and never mix with Actions candidate manifest。

## 15. Checkpoint P11 — Shadow replacement workflow

Modify `.github/workflows/provider-ci.yml` additively while retaining old jobs. Target planned job IDs:

```text
provider-tests                 # old, temporary
provider-distribution-parity   # old, temporary
provider-candidate             # new
provider-static-analysis       # new
provider-linux-canonical       # new
provider-sdist-smoke           # new
provider-macos-delta           # new
provider-attempt-evaluate      # new shadow result
```

Exact external check-run/context name is observed after first shadow run, not assumed from job IDs。

Workflow design gates:

- `fetch-depth: 0` and exact checkout SHA verification。
- `run_attempt == 1` check。
- permissions minimized from P02 evidence。
- no `cancel-in-progress: true` for qualification attempts。
- candidate producer/resolver uses Actions API chronology。
- all roles consume exact artifact IDs/hashes。
- evidence uploaded `if: always()` but missing evidence remains reject。
- no old flags/sharder inside new jobs。
- no packaging build in role jobs。

Static tests parse workflow and assert job needs/commands/permissions。Run:

```bash
uv run pytest -q \
  tests/unit/provider_gate \
  tests/integration/test_provider_gate_role_graph.py \
  tests/integration/test_provider_gate_faults.py \
  --tb=short | tee "$EVIDENCE_ROOT/p11-focused.txt"

make lint | tee "$EVIDENCE_ROOT/p11-lint.txt"
```

Commit/push shadow candidate only after local GREEN and authorization。First shadow run outcomes:

- one build producer。
- same manifest all new roles。
- per-attempt evaluator returns actual result。
- old jobs remain required/observed。
- runner environment capture yields acceptable exact contract candidate。

If environment cannot prove effective limits or image identity, stop before context migration/deletion。

## 16. Checkpoint P12 — Freeze environment contract and rerun shadow on new source SHA

The first shadow workflow may reveal exact environment facts. Freezing/changing `specdock-linux-qualification-v1.json` changes source SHA, therefore it creates a **new candidate**. Do not reuse first shadow artifact/campaign。

1. Populate environment contract with observed actual values。
2. Review parent capability conformance。
3. Run unit/generator/contract tests。
4. Commit/push new source SHA。
5. That SHA’s first workflow run becomes its sole build producer。
6. Confirm all shadow roles use same bytes/fingerprint。

Commands:

```bash
uv run python -m scripts.quality.provider_gate.cli validate-contracts
uv run pytest -q tests/unit/provider_gate/test_environment.py tests/unit/provider_gate/test_artifacts.py --tb=short
make lint
```

Expected: no placeholder/unknown fields; generated policy diff 0; accepted environment fingerprint stable across new roles。

## 17. Checkpoint P13 — Required-context additive transition and intentional RED

Human-only settings phase。Repository agent prepares receipt templates and evidence; human performs settings mutation。

### 17.1 Additive new context

Human adds actual `NEW_CONTEXT_NAME` while old context(s) remain。Readback must show:

```text
U + old + new
```

No unrelated context/review/merge-queue drift。
この段階ではold contextを削除しない。変更前後のactual context names、branch/ruleset scope、merge queue scopeをreadback evidenceへ記録する。

### 17.2 Intentional RED

Before final candidate five-run freeze, create one controlled source candidate whose new per-attempt gate fails for a source-controlled canary without making old compatibility gate fail. The canary is test-only/workflow input and must not weaken Product tests or inject secrets。

Required observation:

- old and unrelated contexts GREEN。
- new context RED。
- PR merge blocked, including merge_group if active。
- attempt appears in rolling history as failed/nonaccepted。
- no rerun of that run。

After proof, fix the canary by a new commit/source SHA and obtain new context GREEN。This recovery candidate is not automatically final B3 candidate; final source after retirement will create its own identity。Replacement GREENだけではold contextを外さず、P14 consumer-zero後にhuman removal/readbackを行う。

If RED does not block, restore settings before-state and stop。Do not remove old context。

## 18. Checkpoint P14 — Migrate all consumers to replacement

Remove old policy use from current consumers while keeping old providers/data and old check emitter present:

1. `.github/workflows/provider-ci.yml` new jobs become authoritative per-attempt path; old jobs still present temporarily。
2. Refactored package tests consume stored artifacts in final gate。
3. docs/operator commands point to provider-gate CLI, not old verifier。
4. no code imports old evaluator/sharder except historical/retirement contract。
5. `tests/conftest.py` keeps a temporary, role-only transition seam: for `--provider-gate-role`, require the registered provider-gate plugin, validate the closed role contract and all collected node assignments, then hand the collection to the new plugin before legacy classification/skip/ledger logic. Without that option, existing ordinary and legacy behavior remains unchanged. Reject missing plugin, invalid contract, unknown node, or mixed legacy flags before test bodies run. Add focused tests for all branches. This seam and legacy hooks are deleted together only after consumer-zero.

Run scanner:

```bash
uv run python -m scripts.quality.provider_gate.cli scan-old-consumers \
  --repository . \
  --contract scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json \
  --output "$EVIDENCE_ROOT/p14-consumer-scan.json"
```

Exit criteria: `runtime_consumers=0`, `workflow_consumers=0`, `test_consumers=0` excluding listed providers scheduled for deletion and historical allowlist。If any consumer remains, do not delete provider/data。

After replacement roles are GREEN and consumer-zero is proven, keep the old workflow/check emitter intact while the human removes only the old required context. Read back the final effective context set as `U + new`, including active merge-queue `merge_group` coverage. Save before/change/readback/rollback evidence. If settings are unreadable, scope changes, or readback is not exactly `U + new`, stop and retain both old provider and emitter.

## 19. Checkpoint P15 — Delete old provider/data/workflow in one cutover

Only after P14 consumer-zero and successful human old-context removal/readback while the old check emitter still exists:

1. delete root ledger/timing。
2. delete old quality modules。
3. delete old evaluator/sharder/skip tests/hooks。
4. remove old marker declarations。
5. remove old jobs/commands from provider-ci, retaining final provider gate。
6. delete provider-full-regression workflow。
7. preserve retained installed-consumer workflow。
8. update AGENTS/docs final guidance。

Before deleting `tests/unit/test_provider_test_lanes.py`, verify moved nonpolicy test exists and passes。Before deleting `tests/conftest.py`, AST-check current file contains no unrelated fixture/hook。

Final consumer scan:

```bash
uv run python -m scripts.quality.provider_gate.cli scan-old-consumers \
  --repository . \
  --contract scripts/quality/provider_gate/contracts/old-policy-retirement-v1.json \
  --require-zero \
  --output "$EVIDENCE_ROOT/p15-consumer-zero.json"
```

Expected: zero old runtime/workflow/test consumers; deleted providers absent; historical references allowed; retained workflows present and byte-equal。

The old check emitter is removed in this same cutover only after the `U + new` readback exists. P20 is read-only confirmation and never performs a late old-context removal.

No compatibility shim、empty ledger、stub verifier、deprecated flag aliasを残さない。

## 20. Checkpoint P16 — Final-source local verification

Run on the final source after old retirement。

### 20.1 Generated/contracts

```bash
uv run python scripts/maintenance/generate_provider_qualification_policy.py --check
uv run python -m scripts.quality.provider_gate.cli validate-contracts
```

Expected exit 0。

### 20.2 Focused tests

```bash
uv run pytest -q tests/unit/provider_gate --tb=short \
  | tee "$EVIDENCE_ROOT/p16-provider-gate-unit.txt"
uv run pytest -q \
  tests/integration/test_provider_gate_role_graph.py \
  tests/integration/test_provider_gate_faults.py \
  --tb=short | tee "$EVIDENCE_ROOT/p16-provider-gate-integration.txt"
uv run pytest -q tests/unit/provider_lifecycle --tb=short \
  | tee "$EVIDENCE_ROOT/p16-lifecycle-read-only.txt"
uv run pytest -q tests/cli_runtime/test_distribution_cutover.py --tb=short \
  | tee "$EVIDENCE_ROOT/p16-distribution.txt"
```

Expected: exit 0、unexpected/approved/policy-skip 0。Local pytest summary counts may change with role refactor; exact counts are not authority。

### 20.3 Ordinary suite and lint

```bash
make lint | tee "$EVIDENCE_ROOT/p16-lint.txt"
uv run pytest -q --tb=short | tee "$EVIDENCE_ROOT/p16-ordinary.txt"
./spec-dock/scripts/spec-dock validate | tee "$EVIDENCE_ROOT/p16-specdock-validate.txt"
```

Expected:

- Ruff check/format pass、mypy pass。
- ordinary suite exit 0。
- no old policy skip reason in output。
- validate exit 0、nodes expected 236 unless canonical spec publication changed only generated count with documented reason。

### 20.4 Source guards

```bash
test ! -e full-regression-ledger.json
test ! -e full-regression-timing-weights.json
test ! -e scripts/quality/full_regression_baseline.py
test ! -e scripts/quality/verify_full_regression.py
test ! -e .github/workflows/provider-full-regression.yml
cmp --silent .github/workflows/ci.yml src/spec_dock/assets/install_root/.github/workflows/ci.yml
! rg -n --hidden --glob '!.git/**' --glob '!spec-dock/initiatives/**' \
  -- '--run-full-regression|--full-regression-shard|POLICY_SKIP_REASON|verify_full_regression|full_regression_baseline'
```

`rg` is supplemental; canonical proof is scanner JSON。

### 20.5 Protected snapshot compare

Capture after snapshot with same script and compare exact entries, excluding the dedicated new evidence directory。Any protected drift stops。

## 21. Checkpoint P17 — Final-source workflow attempt before merge

Commit/push final source candidate only under explicit commit/push authorization。The first Actions run for this SHA is sole build producer。

Required final-source PR attempt:

- build invocation count 1。
- all roles same manifest/wheel/sdist bytes。
- per-attempt accepted。
- Linux process evidence complete。
- fault campaign 100%（candidate-bound、run once per candidate campaign）。
- consumer-zero、retained workflow、protected evidence pass。
- new required context GREEN。
- P14 human readback is exactly `U + new`; old context has already been removed while its emitter still existed.
- final candidate no longer emits the old context; no required context is missing.

For `pull_request`, resolve and test the PR head SHA/tree from event payload. If merge queue is active, separately resolve the `merge_group` SHA/tree and verify that the replacement required check is emitted there. Neither event may silently substitute the other event's source SHA.

Do not start first-five final campaign on PR head if human merge creates a different source SHA. PR evidence proves implementation and per-attempt behavior, not post-merge B3 candidate qualification。

## 22. Checkpoint P18 — Independent implementation reviews

### 22.1 Code Review Strict

On clean pushed exact final-source SHA:

- run `chatgpt-code-review-strict` fresh session。
- require pass、P0/P1=0。
- remediation stays same reviewer session for same purpose。
- any source change invalidates prior receipt。

### 22.2 Final Quality Gate Strict v2

After code review pass and full final-source verification:

- run `chatgpt-final-quality-gate-strict-v2` with Pro。
- bind exact SHA/tree、test receipts、workflow result、consumer-zero、context state。
- require pass。

Neither review authorizes agent merge。

## 23. Checkpoint P19 — Merge-ready PR and human boundary

PR base exact `codex/epic-00384-provider-test-strategy-planning`, never main。

PR evidence:

- problem/outcome and Issue #396 link。
- exact source SHA/tree。
- changed path classification NEW/MODIFY/DELETE/NO-TOUCH。
- test/lint/consumer-zero/protected receipts。
- candidate manifest and final-source per-attempt summary。
- new context RED/GREEN evidence。
- settings before/current/rollback。
- code review/final gate receipts。
- post-merge B3 runbook。

Human alone merges。Agent stops merge-ready。

## 24. Checkpoint P20 — Post-merge exact identity and context readback

After human merge to Epic integration branch:

1. resolve exact merge SHA/tree。
2. require merged tree equals accepted PR head tree; SHA may differ。
3. this merge SHA is a **new candidate identity**。
4. Read back the effective required-context set `U + new` and merge-queue `merge_group` coverage after the earlier P14 removal.
5. Confirm the old emitter is absent from the accepted merge tree and no old context is required.
6. Do not mutate settings in this checkpoint; if readback is unavailable or differs, stop before B3.
7. no main merge yet。

```bash
MERGED_SHA='<read from GitHub>'
MERGED_TREE='<read from GitHub>'
git show -s --format='%H %T' "$MERGED_SHA"
```

If tree differs, stop and do not start B3 campaign。

## 25. Checkpoint P21 — Post-merge candidate build once and B3 campaign

### 25.1 First attempt is sole producer

Dispatch one fresh `workflow_dispatch` run with required input `source_sha=MERGED_SHA`; the resolver must produce `source_identity.json` with `source_reference=workflow_dispatch_source_sha` and exact merged SHA/tree. Do not substitute `GITHUB_SHA` or branch tip, and do not rerun the run. It builds wheel/sdist exactly once and freezes candidate manifest/environment/campaign IDs.

If build/role fails, candidate is rejected; create a forward-fix source SHA and repeat human review/merge as applicable。Do not rebuild same SHA。

### 25.2 First five

Dispatch four additional independent workflow runs, each with the same required `source_sha=MERGED_SHA` but a new run ID, all consuming the producer artifact and exact producer `source_identity.json` bytes. The chronological first five started attempts are immutable population. No retries/reruns/replacement.

Evaluate:

```bash
uv run python -m scripts.quality.provider_gate.cli evaluate-qualification \
  --repository "$REPOSITORY" \
  --source-sha "$MERGED_SHA" \
  --mode campaign \
  --output "$EVIDENCE_ROOT/p21-campaign-result.json"
```

Expected: five complete accepted members、parent predicates all true。

### 25.3 Latest twenty

Because intentional RED remains in history, dispatch additional independent successful attempts until the latest twenty chronological attempts under the same gate/environment contract are all accepted。This normally requires twenty new successes after RED; first five are included in those twenty where chronology permits。Do not create 5×20 nested execution。

Each attempt runs one role graph and consumes stored bytes。Use no reruns。

### 25.4 Fault campaign

Run source-controlled catalogue once for the merge candidate and require all entries executed/detected。Fault fixtures do not mutate candidate bytes or Product source。

### 25.5 Final evaluation

```bash
uv run python -m scripts.quality.provider_gate.cli evaluate-qualification \
  --repository "$REPOSITORY" \
  --source-sha "$MERGED_SHA" \
  --mode final \
  --required-context-readback "$FINAL_CONTEXT_READBACK" \
  --consumer-zero "$CONSUMER_ZERO_JSON" \
  --protected-before "$PROTECTED_BEFORE_JSON" \
  --protected-after "$PROTECTED_AFTER_JSON" \
  --output "$EVIDENCE_ROOT/p21-qualification-result.json"
```

Expected:

- candidate/source/tree/manifest/artifact identity complete。
- first five accepted independently。
- fault catalogue 100%。
- latest twenty complete/all accepted、flakes/retry/rerun 0。
- context final set correct。
- consumer-zero、protected-data GREEN。
- B3 `accepted=true`。

B3 is not claimed until this exact output and API/raw readback are independently inspected。

## 26. Checkpoint P22 — B3 receipt and handoff to Epic main merge

Create post-merge B3 receipt outside tracked future-fact docs first。Receipt includes:

- exact integration SHA/tree。
- producer run/artifact IDs、manifest/wheel/sdist hashes。
- environment fingerprint。
- first-five attempt IDs/raw hashes。
- fault catalogue digest/result。
- latest-twenty attempt IDs/results。
- final context before/after/readback。
- consumer-zero/deletion proof。
- protected snapshot proof。
- qualification-result hash。
- review receipts and rollback readiness。

Only after B3 GREEN may主担当 update canonical Report/Issue projection and prepare final Epic PR to main。One human Epic merge remains required。

## 27. Exact command/output matrix

| Stage | Command | Expected output class |
|---|---|---|
| Spec validation | `./spec-dock/scripts/spec-dock validate` | exit 0, nodes observed |
| Policy projection | `uv run python scripts/maintenance/generate_provider_qualification_policy.py --check` | exit 0, diff 0 |
| Contracts | `uv run python -m scripts.quality.provider_gate.cli validate-contracts` | all schema/catalogue/role contracts valid |
| Unit | `uv run pytest -q tests/unit/provider_gate --tb=short` | pass, skip/xfail 0 |
| Integration | `uv run pytest -q tests/integration/test_provider_gate_role_graph.py tests/integration/test_provider_gate_faults.py --tb=short` | pass, synthetic only |
| Lifecycle non-regression | `uv run pytest -q tests/unit/provider_lifecycle --tb=short` | pass |
| Distribution non-regression | `uv run pytest -q tests/cli_runtime/test_distribution_cutover.py --tb=short` | pass |
| Lint | `make lint` | Ruff check/format + mypy pass |
| Ordinary suite | `uv run pytest -q --tb=short` | exit 0, no old policy skip reason |
| Consumer scan | `... scan-old-consumers --require-zero` | consumer 0, retained workflow protected |
| Linux role | `... run-role --role linux-canonical` | one pytest root, worker1, no shard, raw metrics |
| sdist role | `... run-role --role sdist-smoke` | no build, actual sdist parity pass |
| macOS role | `... run-role --role macos-delta` | owned delta pass, no Linux performance predicate |
| Attempt eval | `... evaluate-attempt` | accepted only with all role/raw identity complete |
| Final eval | `... evaluate-qualification --mode final` | B3 accepted only with five/fault/twenty/context/protection |

Exact pass counts are observations, not specification constants。Any expected output class change requires diff/reason review, not blanket update。

## 28. Stop-and-return payload

唯一のstop-and-return wire schemaは`artifacts/provider-gate-contracts-v1.schema.json#/$defs/StopReturnV1`である。Plan/Handoffに別JSON shapeを定義しない。Evidenceはrepository-relative path / run ID / redacted API receiptとし、credentials、tokens、private absolute pathsを含めない。原因を特定できない場合は`cause="原因未特定"`とする。

## 29. Stop conditions

### Identity / admission

- repository/branch/full SHA/tree/upstream/remote mismatch。
- B2 raw hash/evaluation mismatch。
- dependency/active/concurrent writer ambiguity。
- spec review pass/P0/P1条件未達。

### Parent authority

- `E384-QUAL-001`を一意にprojectできない。
- value/population/window/aggregation/platform/rejection/escapeの変更が必要。
- hidden workflow thresholdが必要。

### Candidate/environment

- producer一意性、actual bytes、source/tree binding、retention不十分。
- effective limit/image/class/fingerprint不明またはdrift。
- same SHA rebuild/retry/rerunが必要。

### Role/process

- role ownership欠落/重複。
- skip/approved failure/shard/worker追加が必要。
- descendant-inclusive CPU/reapを証明不能。

### History/evidence

- first five/latest twenty/API chronology/raw evidence不完全。
- failure/cancel/missingを残せない。
- fault detection 100%未達。

### Cutover/context/protection

- old consumer remaining。
- retained installed-consumer workflowに削除/変更が及ぶ。
- ruleset/context/merge queue state未確認、REDがblockしない、no-gap不可。
- Product/lifecycle/15-row/protected data変更が必要。
- dogfood partial projection。

### Governance

- extra Issue、direct-main、agent merge、human merge removal、portfolio reprioritizationが必要。

## 30. Rollback and recovery matrix

| State | Valid recovery |
|---|---|
| Spec candidate unaccepted | docsだけ修正しfresh Strict review |
| Implementation uncommitted | Issue branchで修正/abandon、B2 untouched |
| Shadow workflow failed | new source commit、same run rerun禁止 |
| Context additive migration failed | human restores captured `U + old`; merge blocked |
| Final source PR unmerged | repair with new source SHA、full revalidation |
| #396 merged, B3 not accepted | stop Epic main; human whole-merge revert + settings restore to complete B2, or owned forward-fix/new candidate |
| B3 accepted, Epic main unmerged | repair on integration branch; B3 evidence invalidated by source change |
| Epic main merged | parent-controlled suffix recovery/forward-fix; automatic rollback禁止 |

## 31. Completion criteria

本Issueは次が全て成立するまで完了しない。

1. implementation-ready spec independently accepted。
2. replacement final gate implemented/tested。
3. old consumer 0 then old policy removed on final source。
4. final-source per-attempt gate GREEN、review GREEN、PR human merged to Epic branch。
5. merged SHA candidate built once。
6. current candidate first five accepted。
7. candidate-bound seeded faults 100%。
8. latest twenty complete/all accepted、retry/rerun/flake 0。
9. context final set/readback GREEN。
10. docs/protected/retained workflow/consumer-zero GREEN。
11. B3 receipt complete。

この時点でもEpic main mergeは別human gateである。
