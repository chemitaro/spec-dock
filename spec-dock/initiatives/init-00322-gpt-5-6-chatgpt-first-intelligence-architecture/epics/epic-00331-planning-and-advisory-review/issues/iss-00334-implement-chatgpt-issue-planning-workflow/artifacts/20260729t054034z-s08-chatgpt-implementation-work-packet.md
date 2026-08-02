---
種別: artifact
ID: "20260729t054034z"
タイトル: "S08 ChatGPT Implementation Work Packet"
状態: "archived"
作成者: "ChatGPT Pro / Codex Main"
最終更新: "2026-07-29"
親: ["iss-00334"]
template: "blank"
authority: "execution-input"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md#S08"
  - "GitHub chemitaro/spec-dock@08aa8f564f7265a64ce772d50d56ff1fb8ffd185"
reflected_to: ["report.md"]
---

# S08 Implementation Work Packet

## 位置づけ

本書は、canonical Planの`S08 — Provider-owned Direct Oracle Adapter`を実装する直前にChatGPT Proで具体化した、レビュー不要のstep execution inputである。Requirement／Design／Planの代替、仕様変更、reviewer verdictではない。実装時にrepository factsと矛盾する記述が見つかった場合はcanonical docsを優先し、PlanのStop Conditionsに従う。

ChatGPT sessionは`iss00334-s08-jit`。model selection evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`。ChatGPTはGitHub connectorでrepository `chemitaro/spec-dock`、branch `iss-00334-implement-chatgpt-issue-planning-workflow`、HEAD `08aa8f564f7265a64ce772d50d56ff1fb8ffd185`のexact一致を確認し、default branch fallbackを使用しなかった。

## Current-State Findings

1. `infra/issue_planning_chatgpt.py`は個人home配下の`oracle-chatgpt`を`_FIXED_CHATGPT_USE`として固定し、`--write-output`とlegacy marker frameをactive transportに使っている。
2. 最終spawnはlist argvだが、adapter境界はshared generic backend command stringと`shlex.split`へ依存する。現行`env={}`はchild environmentのsanitizeになっておらず、ambient environmentを継承する。
3. `PlanningInvocationResult`はgeneric transient bytesを一つ持つだけで、Planner／Semantic RevisionのZIPとReviewer JSONを型で区別しない。
4. Oracle version／capability preflight、session identity、same-session recovery、artifact inventory、metadata size／SHA、safe staging copy、copy後rehashは未実装。
5. 現行focused tests 29件は`_FIXED_CHATGPT_USE`と`--write-output`をpositive contractとして保護しているため、新Oracle境界へ置換する必要がある。
6. `cli/bootstrap.py`が既存callableをinjectするseamは維持でき、新CLI／registry／backend optionは不要。
7. S08はPrompt本文、Candidate接続、installer／projection／docsを変更せず、S09〜S11へ明示的にhandoffする。

判定は`GO`。S08はapproved-no-opではなく実変更が必要であり、現時点でcanonical amendmentを必要とする矛盾はない。

## Bounded Scope

### Allowed paths

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `tests/unit/infra/test_issue_planning_chatgpt.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- 必要な場合のみ:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
  - `tests/unit/infra/test_issue_planning_oracle_artifact.py`

### Preserve

- `invoke_issue_planning_chatgpt` callableとbootstrap injection。
- `resolve_issue_planning_github_repository`。
- Public command family。
- Candidate／Review／Human decision／apply／publication semantics。
- Serialized resultのstatus、reason、source evidence、byte count、SHA、details。
- transient bytes、session locator、private pathをserializeしない性質。

### Forbidden changes

- application orchestrationとPrompt resources。
- Candidate parser／builder。
- CLI parser／bootstrap。
- shared generic authoring-pack backend。
- installer／distribution／dogfood projection。
- integration E2Eとworkflow docs。
- canonical Issue／Epic docs、`report.md`、`.assurance.json`。
- Oracle本体、commit、push、PR、merge。

## Typed Result Contract

- `OracleAuthoringZipSnapshot`
  - expected logical filename
  - observed transport filename
  - internal root
  - size
  - SHA-256
  - transient ZIP bytes
- `OracleReviewJsonPayload`
  - size
  - SHA-256
  - transient JSON bytes
- `status="pass"`ではroleに対応するtyped outputをexactly one要求する。
- blocked／rejected resultはtyped outputを持たない。
- generic-only transient payload、cross-kind output、bytesとsize／SHAの不一致を拒否する。
- session ID、session root、source artifact path、raw stdout／stderrをformal resultに含めない。

Closed reasonは次に限定する。

- `blocked/oracle_unavailable`
- `blocked/oracle_capability_unsupported`
- `blocked/oracle_session_recovery_required`
- `rejected/oracle_artifact_missing`
- `rejected/oracle_artifact_ambiguous`
- `rejected/oracle_artifact_rejected`

旧`backend_*` reasonとlegacy frame reasonを新adapterのactive success/failure pathに使用しない。

## Red-First Test Cases

- `S08-R01`: PATH上の`oracle` symlinkを最終regular executableへ解決する。
- `S08-R02`: Oracle不在時は`oracle_unavailable`、process start 0、fallback 0。
- `S08-R03`: directory、FIFO、broken link、loop、non-executableを拒否する。
- `S08-R04`: unsupported version／browser／attachment／session capabilityではPrompt submit 0。
- `S08-R05`: resolved Oracleをargv[0]とするdirect argv、`shell=False`、metacharacter保持、submit exactly one、`--write-output` 0。
- `S08-R06`: child environmentからAPI credentialとbackend selectorを除去し、PATH／localeは維持する。
- `S08-R07`: Reviewer JSONをtyped payloadとして返し、bytes／private dataをserializeしない。
- `S08-R08`: exactly-one ZIP artifactのmetadata、containment、size、SHAを確認してprivate snapshotを返す。
- `S08-R09`: matching artifact 0件／2件をmissing／ambiguousとして拒否する。
- `S08-R10`: unsupported metadata schema／wrong session identityを拒否する。
- `S08-R11`: absolute escape、`../`、symlink parent/file、directory、FIFOを拒否する。
- `S08-R12`: size／SHA mismatch、copy中mutation、copy後rehash不一致を拒否する。
- `S08-R13`: submit後timeoutでもsame-session status／reattach／harvestだけを使い、submit countを1に保つ。
- `S08-R14`: session identity不明またはterminal state不明ならnew submitせずrecovery-required。
- `S08-R15`: stderr／metadata内のtoken、raw transcript、private pathをresult／exceptionへ漏らさない。
- `S08-R16`: Planner expectationへのJSON、Reviewer expectationへのZIPを拒否する。
- `S08-R17`: runtime denylistでpersonal path、wrapper、`--write-output`、backend selector、`shell=True`が0件。

## Implementation Sequence

1. Domain testsをRedにし、role別output expectation、typed payload、result invariants、closed reason、non-serializationを固定する。
2. PATHから`oracle`を解決し、strict symlink resolution、regular executable、spawn直前identityを検証する。
3. supported Oracle version／capability profileをprivate adapter tableに閉じる。未確認versionを推測で許可しない。
4. shared generic backendを使わないOracle専用direct argv runnerを追加し、actual child environmentをsanitizeする。
5. Prompt-bearing submitを一回に限定するstate machineを実装する。
6. timeout／disconnect後は、確立済みsame-sessionに対するstatus／reattach／harvestだけを実行する。
7. 必要な場合だけversioned artifact metadata readerを一つのprivate infra moduleへ隔離する。
8. session root containment、`O_NOFOLLOW`、`fstat`、bounded copy、metadata照合、private staging、copy後rehashを実装する。
9. Reviewer JSON／Planner ZIPをtyped resultへmapし、raw Oracle diagnosticを破棄する。
10. `_FIXED_CHATGPT_USE`、`shlex` backend construction、`BackendInvokeRequest`、`invoke_backend_with_capture`、`--write-output`、legacy marker parserをactive adapterから削除する。

## Verification Commands

```bash
uv run pytest -q tests/unit/infra/test_issue_planning_chatgpt.py
uv run pytest -q tests/unit/domain/test_issue_planning_contracts.py
uv run pytest -q tests/unit/infra/test_issue_planning_oracle_artifact.py
uv run pytest -q tests/unit/application/test_issue_planning.py -k "transport_short_circuits_backend_for_git_preflight_failures"
uv run pytest -q tests/unit/cli/test_cli_smoke.py
uv run ruff check <S08 changed paths>
uv run ruff format --check <S08 changed paths>
uv run mypy <S08 runtime paths>
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

Oracle artifact helperを追加しない場合は、そのtest pathを実行対象から外す。runtime denylistでは`_FIXED_CHATGPT_USE`、`/Users/`、`chatgpt-use`、`oracle-chatgpt`、`--write-output`、`SPECDOCK_CHATGPT_COMMAND`、`ORACLE_CHATGPT_COMMAND`、`backend_command`、`shell=True`を確認する。API credential keyはsanitizer testのliteralになり得るため、behavior testでchild environmentへの非伝播を確認する。

## Stop Conditions

- Supported Oracleからbounded version／capability情報を得られない。
- stable session identityをPrompt submit前またはtimeout後に得られない。
- artifact inventoryの取得にhome／Downloads／mtime latestのfuzzy scanが必要。
- recoveryにnew prompt submissionが必要。
- Oracle本体、新public export API、persistent registry／database／custom Git refの変更が必要。
- personal wrapper、API fallback、Project／Chrome profile／LaunchAgent、user absolute pathが必要。
- shell command stringまたはprivate path／raw transcriptのformal保存が必要。
- Public CLI、Candidate、Review、Human decision、apply／publicationの変更が必要。
- application Prompt、Candidate builder、installer、projection、docsへS08変更を広げる必要。
- metadata couplingを一つのprivate versioned infra boundaryへ閉じられない。
- 開始時のbranch／HEAD／worktreeが本artifactのsource identityと一致しない。

## Dev-Coder Handoff

### Objective

PATH-resolved Oracleをdirect argvで起動し、supported capabilityをfail closedに確認し、Promptを一回だけsubmitし、same-session recoveryと安全なtyped artifact snapshotを行うprovider-owned S08境界を実装する。

### Required evidence

1. changed-file inventory。
2. focused pytest／ruff／format／mypy結果。
3. fake Oracle captured argvとsubmit count 1の証拠。
4. sanitized environment fixture。
5. same-session recovery positive／negative。
6. artifact metadata negative matrix。
7. runtime denylistと`git diff --check`。
8. real Oracle version／schemaの未検証点。
9. Stop Condition非該当。
10. S09／S10へ残したhandoff事項。
11. `Ledger Note`または`No material implementation decisions beyond the approved plan.`。

Workerは実装とfocused verificationまでを担当し、`report.md`、commit、push、PR、mergeを行わない。Mainはworker evidenceの統合、ChatGPT code review、commit、push、clean check、S08 Result Approvalを担当する。

## Assumptions and Uncertainty

未確認のimplementation-local facts:

- supported Oracleのexact version。
- version／capability probeのexact argvとschema。
- submit／status／reattach／harvestのexact flag。
- caller-selected slugのstable session identity利用可否。
- first-class artifact exportの有無。
- Oracle private session metadata schema。
- sanitizeすべきOracle-specific API credential environment keyの全集合。

これらは実装時にcurrent Oracle CLIとrepository sourceで確認する。bounded interfaceが存在しなければ推測やfallbackで進めずStop ConditionとしてMainへ返す。
