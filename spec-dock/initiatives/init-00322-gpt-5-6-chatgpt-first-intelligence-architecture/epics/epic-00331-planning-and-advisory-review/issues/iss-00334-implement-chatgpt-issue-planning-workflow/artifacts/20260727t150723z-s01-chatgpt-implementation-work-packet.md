---
created_by_role: chatgpt-pro
scope_id: iss-00334
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
intended_targets:
  - iss-00334/S01
adoption_status: execution-input
reflected_to: []
diff_guard_result: passed
source_head: b1ee8d091deba166b805145e7367190de6a14578
oracle_session: iss00334-s01-implementa-brief
---

# S01 ChatGPT implementation work packet

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a670ae6-f780-83e8-9e0f-0c0b3b6063c3

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Context: This is chemitaro/spec-dock on branch iss-00334-implement-chatgpt-issue-planning-workflow at exact HEAD b1ee8d091deba166b805145e7367190de6a14578. SpecDock is a Python provider/scaffold repository; src/spec_dock/assets/spec_dock is provider authority and root spec-dock is dogfood projection. The approved Issue is iss-00334. We are executing only S01 CLI Skeleton and Domain Contracts. You MUST first inspect @GitHub current branch and exact HEAD; attachments are supplementary. Task: produce a concrete Japanese Markdown implementation work packet for a dev-coder subagent. Ground every instruction in current repository files and existing patterns. S01 scope is only the separate repo-local spec-dock-chatgpt executable skeleton, parser/help/dispatch wiring, command result envelope, and closed validation/data contracts for PlanningContext, Candidate identity, Reviewed identity, PlanningRevisionRequestV1, PlanningReviewResult, PlanningHumanDecisionV1, plus existing-Issue canonical-three-path resolution. Do not implement GitHub remote preflight/backend invocation, Candidate ZIP packaging, Review execution, filesystem adoption, commit/push, installed Skill/Prompt, distribution projection, or dogfood; those belong to later steps. Prefer the smallest vertical tracer bullet and existing layered architecture. Do not create a generic workflow engine, registry database, arbitrary target option, arbitrary prompt option, or parallel implementation subsystem. Preserve the existing Core spec-dock CLI. Identify exact existing and proposed file paths after inspecting the repository; avoid speculative files when an existing owner fits. Define Red-first tests with fixture setup, command/operation, expected observable result, and regression caught. Include public help expectations and text/JSON status-reason parity, ok versus ready, existing Issue/Seed rejection, exact canonical three paths, revision semantic/mechanical validation including P2/P3 rejection, Human decision truth table, duplicate/unknown keys, and identity digest mismatch. Give an ordered implementation sequence, narrow verification commands, allowed paths, forbidden paths, stop/amendment conditions, and any assumptions requiring Main verification. End with a ready-to-send subagent instruction block that is bounded, imperative, and includes required return evidence: changed files, tests and results, unresolved risks, and either Ledger Note or the exact sentence No material implementation decisions beyond the approved plan. Do not produce a patch. Do not review or redesign the approved specification. Do not include S02 or later implementation. Requested output headings: Scope confirmation; Repository findings; Exact allowed paths; Red-first test cases; Implementation sequence; Verification commands; Forbidden changes; Stop conditions; Subagent instruction.

## Answer

## Scope confirmation

**結論:** S01 は、既存 Core Runtime を複製せずに、provider authority 配下へ独立した `spec-dock-chatgpt` の CLI shell を追加し、既存 `CommandSpec`／`dispatch`／`UseCases`／`CliText` を再利用する形で実装する。実装対象は parser/help/dispatch の公開境界、result envelope、主要 domain contract、existing Issue の canonical three paths resolver までとする。

GitHub connector で `chemitaro/spec-dock` の branch `iss-00334-implement-chatgpt-issue-planning-workflow` を exact SHA `b1ee8d091deba166b805145e7367190de6a14578` と比較し、`status=identical`、`ahead_by=0`、`behind_by=0` を確認した。commit fetch でも同 SHA を取得した。取得時点は 2026-07-27。

対象 node は `.meta.json` 上で `type=issue`、`id=iss-00334`、親は `epic-00331`／`init-00322`、GitHub scope は `chemitaro/spec-dock` と確認済みである。

S01 の完了境界は次のとおりとする。

* 独立 executable `spec-dock-chatgpt` が provider tree に存在し、top-level／group／leaf help が成立する。
* 公開 command は `planning create`、`planning revise`、`review planning`、`planning apply` の四つだけで、Core `spec-dock` の command treeへ追加しない。
* parser から既存 dispatch を通して injected use case へ到達し、同一 `PlanningCommandResult` から text／JSON を描画できる。
* `ok` と `ready` を型・validation・renderer test で区別する。
* PlanningContext、Candidate identity、Reviewed identity、Revision request、Review result、Human decision の closed contract が実装される。
* existing Issue から canonical three paths を決定し、unknown Issue、Initiative／Epic、未 materialize の Seed を fail closed で拒否する。
* valid production operation が Candidate生成、Review完了、adoption完了を偽って返してはならない。S01 の dispatch tracer は injected fake use case で検証し、`candidate_created` 等の実 success を live handler から発生させない。
* focused CLI／domain／application／presentation tests が Green となり、Core CLI regression がない。これは approved S01 の Goal／Work／Tests／Exit と一致する。 

以下は明示的に S01 外である。

* current GitHub remote、branch、upstream、remote HEAD の preflight
* ChatGPT backend process、Prompt transport、secret scan
* Candidate ZIP の生成・展開・検証・atomic publish
* 実際の Review execution
* canonical files の replacement、decision artifact 書込み、rollback
* commit、push、remote parity
* installed Skill／Prompt
* `src/spec_dock/cli.py` による distribution handling
* root `spec-dock/` dogfood projection
* wheel／sdist、fresh init／update parity、live dogfood

添付された Requirement／Design／Plan も同じ S01 境界を補助的に示しているが、以下の packet は GitHub exact HEAD の正本を優先している。 

---

## Repository findings

### 検証済み repository facts

1. Provider executable の既存 pattern は、shebang、`sys.dont_write_bytecode`、runtime path guard、`spec_dock_runtime.app.main` 呼出しだけを持つ thin entrypoint である。新 executable もこの形に合わせる。

2. Core `app.main` は、registry→parser→parse→managed repo 解決→runtime bootstrap→dispatch の順で動き、help の `SystemExit(0)` を runtime 構築前に処理している。新 `chatgpt_app.main` はこの制御順を再利用する。

3. Core CLI は既に以下の責務へ分離されている。

   * parser: command tree と `command_key` binding
   * registry: 各 command module の `command_specs()` 集約
   * dispatch: `args_factory`、`run`、`CliText` emission
   * bootstrap: Ports／UseCases construction
   * command module: typed args、argument definition、use-case invocation、renderer selection

   Registry は command module から `CommandSpec` を集め、dispatch は `CommandOutcome` の exit code と `CliText` をそのまま出力する。

4. `CommandArgs`、`CommandOutcome`、`CommandSpec`、`CommandRegistry` は既に shared contract として存在するため、ChatGPT CLI 専用に複製しない。

5. text output の共通 transport は `CliText(stdout_lines, stderr_lines, warnings)` である。新 result renderer もこれを返す。

6. `workflow.py` は、typed args、`--format {text,json}`、`command_specs()`、use-case invocation、text／JSON renderer の既存最小例である。`issue_planning.py` command module はこの構造に合わせる。

7. Existing Issue の authority は `.meta.json` であり、`infra.fs_repo.load_node_records()` は node type、ID、path、parent／initiative／epic を `StoredMetaRecord` として返す。新 resolver は directory glob を別実装せず、この record surface を入力とする。

8. Repository 内には canonical JSON digest の既存 precedent がある。`ensure_ascii=False`、`sort_keys=True`、`separators=(",", ":")` で UTF-8 bytes を作り、SHA-256 を計算している。Reviewed identity digest もこの方式を用いる。

9. 既存 authoring-pack の JSON reader は通常の `json.loads` であり、duplicate-key rejection を持たない。S01 の strict contract のために generic authoring-pack validatorを変更せず、`issue_planning_contracts.py` 内だけに duplicate-key-aware loader を置く。

10. CLI test には、provider runtime modules を直接 importし、parser help、dispatch、injected `UseCases` を検証する既存 pattern がある。新 CLI test はこれを踏襲し、fresh installerやdogfood projectionには依存させない。

11. Installer は provider の `scripts/` tree 全体を managed directory として同期するが、明示的に executable bit を付けているのは現在の Core `spec-dock` だけである。したがって S01 では provider source file を executable mode にするところまでとし、wheel／fresh install／update 後の mode parity は S06 に残す。`src/spec_dock/cli.py` は変更しない。

### CLI surface to freeze

`prog` は既存表記に合わせて次とする。

```text
spec-dock/scripts/spec-dock-chatgpt
```

公開 leaf と argument は以下に限定する。

| Leaf              | 必須 argument                                                                                                                                                     | mode-specific                                                                            | 共通                                    |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------- |
| `planning create` | `--issue <iss-id>`、`--output <external-dir>`                                                                                                                    | なし                                                                                       | `--format {text,json}`、default `text` |
| `planning revise` | `--candidate <zip>`、`--request <json>`、`--output <external-dir>`                                                                                                | なし                                                                                       | `--format {text,json}`、default `text` |
| `review planning` | `--issue <iss-id>`、`--mode <archive-candidate\|git-bound>`、`--output <external-dir>`                                                                            | archive: `--candidate`; git-bound: `--reviewed-head`                                     | `--format {text,json}`、default `text` |
| `planning apply`  | `--issue <iss-id>`、`--mode <archive-candidate\|git-bound>`、`--review-result <json>`、`--human-decision <json>`、`--expected-head <sha>`、`--output <external-dir>` | archive: `--candidate`、`--logical-filename`、`--zip-sha256`; git-bound: `--reviewed-head` | `--format {text,json}`、default `text` |

`--mode` は required とする。`archive-candidate` を製品上の default lane とする一方、CLI が mode を silent selection してはならないためである。Public syntax と mode-specific identity option は approved Design に定義されている。

次の option は help、parser、typed args のいずれにも追加しない。

```text
--repo
--repository
--branch
--upstream
--target
--target-path
--prompt
--prompt-file
--backend
--backend-command
--registry
--workflow
```

### Canonical Issue path resolution

Current `iss-00334` の canonical three paths は次の三つである。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/design.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/plan.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/requirement.md
```

Identity 内の ordering は Design の「UTF-8 byte順」に従い、`design.md`、`plan.md`、`requirement.md` とする。ファイルの自然言語上の Requirement→Design→Plan 順へ並べ替えない。Git-bound reviewed target はこの exact three-path tuple だけを持つ。

Resolver は次の手順だけを持つ。

1. 既存 ID parser／normalization を使用して Issue ID を正規化する。
2. `StoredMetaRecord` の exact normalized ID を一件だけ解決する。
3. record が存在しない場合は unknown Issue として拒否する。
4. record.kind が `issue` でなければ、Initiative／Epic／Seed として拒否する。
5. `record.path` を `repo_root` 相対 POSIX path に変換する。
6. path が `spec-dock/initiatives/**` 外、symlink、または repository 外へ解決される場合は拒否する。
7. 同一 directory の exact filenames 三つを構築する。
8. 三つが regular non-symlink files であることを確認する。
9. UTF-8 byte順の immutable tuple として返す。

Issue node を作る、Seedを materializeする、active pointerから対象を推測する、任意 path を受け取る処理は持たせない。Existing-Issue-only と Seed routing は approved Requirement に明記されている。

### Domain contracts to close

すべて `@dataclass(frozen=True)` とし、Pydantic、JSON Schema registry、新 dependency は追加しない。現在の project dependencies は runtimeで `tomli` のみ、devで pytest／ruff／mypy である。

#### `PlanningContext`

| Field                   | S01 type               | Validation                                                |
| ----------------------- | ---------------------- | --------------------------------------------------------- |
| `issue_id`              | `str`                  | normalized existing Issue ID                              |
| `repository`            | `str`                  | non-empty normalized `owner/name`                         |
| `branch`                | `str`                  | non-empty、NUL／改行なし                                        |
| `source_head`           | `str`                  | lowercase 40-hex SHA                                      |
| `parent_epic_id`        | `str`                  | normalized Epic ID                                        |
| `parent_initiative_id`  | `str`                  | normalized Initiative ID                                  |
| `dependency_summary`    | `tuple[str, ...]`      | 各要素 non-empty、重複なし                                        |
| `canonical_issue_paths` | `tuple[str, str, str]` | exact three filenames、同一親、repo-relative POSIX、UTF-8 byte順 |
| `relevant_source_paths` | `tuple[str, ...]`      | safe repo-relative POSIX、重複なし                             |
| `operator_context`      | `tuple[str, ...]`      | 各要素 non-empty。secret scan は S02                           |

Design が nested value shape を固定していないため、`dependency_summary` と `operator_context` を immutable string tuple とする点は Main verification assumption とする。Field set 自体は変更しない。PlanningContext の required fields と existing Issue gate は approved Design のとおりである。

#### `IssueCandidateIdentity`

| Field                         | Validation                                          |
| ----------------------------- | --------------------------------------------------- |
| `issue_id`                    | normalized Issue ID                                 |
| `candidate_id`                | trim後 non-empty、control characterなし                 |
| `version`                     | `int >= 1`。`bool` は拒否                               |
| `logical_filename`            | basename-only `.zip`                                |
| `observed_transport_filename` | logical filename と同一、または closed ` (N)` suffix alias |
| `internal_root`               | safe relative POSIX path、absolute／`..`／backslashなし  |
| `source_repository`           | normalized non-empty `owner/name`                   |
| `source_branch`               | non-empty、NUL／改行なし                                  |
| `source_head`                 | lowercase 40-hex                                    |
| `zip_sha256`                  | lowercase 64-hex                                    |

Closed transport alias は、logical `candidate.zip` に対し `candidate (1).zip` のような正規形だけを許可する。fuzzy rename、別 extension、directory component は拒否する。ZIP bytesとの再計算、manifest照合、repack判定は S03 に残す。Candidate identity fields は approved Design に定義されている。

#### `ReviewedPlanningIdentity`

共通 field:

```text
mode
issue_id
repository
branch
source_head
```

Mode-specific closure:

| Mode                | 必須                       | 禁止                       |
| ------------------- | ------------------------ | ------------------------ |
| `archive-candidate` | `candidate_identity`     | `canonical_target_paths` |
| `git-bound`         | `canonical_target_paths` | `candidate_identity`     |

追加 validation:

* archive identity の issue/repository/branch/source_head は outer identity と一致する。
* git-bound path は resolver が返す exact three-path tuple と一致する。
* mode-specific field の両方あり／両方なしを拒否する。
* digest は `to_dict()` の canonical JSON UTF-8 bytes に対する SHA-256。
* dict insertion order に依存しない。
* digest対象に digest自身は含めない。

#### Strict JSON loader

`issue_planning_contracts.py` 内に private helper を一つ置く。

* UTF-8 strict decode
* root object required
* `object_pairs_hook` による duplicate key rejection
* nested objectでも duplicate key rejection
* `NaN`、`Infinity`、`-Infinity` rejection
* 各 contract ごとに exact allowed／required key set
* unknown key rejection
* missing key rejection
* JSON booleanをintegerとして受理しない
* file I/O、repository lookup、result renderingは入れない

Generic schema engine、registry、decorator frameworkへ拡張しない。

#### `PlanningReviewFinding`／`PlanningReviewResult`

`PlanningReviewFinding` の exact keys:

```text
id
severity
exact_location
violated_requirement_or_contradiction
concrete_impact
```

Validation:

* `severity` は `p0|p1|p2|p3`
* finding ID は non-empty、result内で一意
  -説明 field はすべて non-empty
* unknown key、duplicate key を拒否

`PlanningReviewResult` の exact keys:

```text
reviewed_identity
reviewed_identity_sha256
verdict
findings
```

Validation:

* reviewed identity object と canonical digest が一致
* `verdict` は `pass|fail`
* P0／P1が一件以上なら `fail`
* P0／P1が0件なら `pass`
* P2／P3-only result は `pass`
* inconsistent declared verdict を拒否

この severity rule は approved Requirement／Design の blocking定義に従う。

#### `PlanningRevisionRequestV1`

Common exact keys:

```text
schema_version
lane
candidate_identity
preserve_assumptions
```

`schema_version` は integer `1` のみ。

Semantic lane exact additional keys:

```text
finding_ids
review_result_sha256
```

Semantic validation は二段階にする。

1. Structural parse

   * finding IDs non-empty、unique
   * review result digest は lowercase 64-hex
   * Mechanical field が混入したら unknown key として拒否

2. `validate_against(review_result, exact_review_result_bytes)`

   * exact raw Review result bytes の SHA-256 と一致
   * Review mode が `archive-candidate`
   * request candidate identity が reviewed archive candidate identity と一致
   * finding ID がすべて存在
   * 選択 finding はすべて P0／P1
   * P2／P3-only、P1＋P2 mixed、unknown ID を拒否

Mechanical lane exact additional keys:

```text
target_file
old_text
new_text
meaning_invariant
diff_budget
```

Mechanical structural validation:

* `target_file` は `requirement.md|design.md|plan.md`
* `old_text`／`new_text` は non-empty、互いに異なる
* `meaning_invariant` は non-empty
* `diff_budget` は positive integer、`bool` rejection
* Semantic field が混入したら拒否

old text の0件／複数match、actual diff count、meaning invariant の実行時判定、Candidate再 packaging は S04 である。S01 で file mutation helperを追加しない。Revision field set と P2／P3 rejection は approved Design に定義されている。

#### `PlanningHumanDecisionV1`

Exact keys:

```text
schema_version
issue_id
reviewed_identity
reviewed_identity_sha256
review_result_sha256
decision
plan_adoption
implementation_start
decided_at
```

Validation:

* `schema_version == 1`
* issue ID と reviewed identity issue ID が一致
* reviewed identity object と canonical digest が一致
* `review_result_sha256` は exact raw Review file bytes の SHA-256 と一致
* `decided_at` は timezone付き ISO-8601／RFC 3339
* decision truth table は次の二行だけを受理する

| decision   | plan_adoption | implementation_start |
| ---------- | ------------: | -------------------: |
| `approved` |        `true` |               `true` |
| `rejected` |       `false` |              `false` |

その他の6組合せ、duplicate key、unknown key、wrong digest、stale／different identity は拒否する。Human decision contract と truth table は approved Design のとおりである。

Review verdict が `fail` なのに Human が `approved` とした場合の apply readiness 判定は S05 に残す。S01 の Human contract validator は truth table と identity bindingを閉じ、repository mutation判断を行わない。

#### `PlanningCommandResult`

Exact top-level fields:

```text
status
reason
issue_id
output
details
```

Status union:

```text
ok
ready
blocked
stale
rejected
rolled_back
recovery_required
publication_pending
blocked_remote_diverged
```

Success pair validation:

| Operation outcome  | Required pair              |
| ------------------ | -------------------------- |
| Candidate create   | `ok/candidate_created`     |
| Candidate revise   | `ok/candidate_revised`     |
| Review completion  | `ok/review_completed`      |
| Published adoption | `ready/adoption_published` |

次を拒否する。

```text
ready/candidate_created
ready/review_completed
ok/adoption_published
```

追加規則:

* `reason` は lower snake_case
* `issue_id` は normalized Issue ID
* `output` は string-keyed JSON object
* `details` は immutable string tuple
* Path、bytes、set、non-string dict key、NaN等の非JSON値を拒否
* `is_ready` は `status == "ready"` のみ
* exit code は `ok|ready => 0`、その他の result status は `1`
* argparse structural error は `2`

Text／JSON renderer は同一 object の `to_dict()` を source とする。JSON は既存 renderer patternに合わせて UTF-8非escape、compact separators を使用する。Text の先頭三行は固定する。

```text
status: <status>
reason: <reason>
issue_id: <issue_id>
```

`output` と `details` は後続行に描画してよいが、status／reason を別計算してはならない。Result contract と `ok`／`ready` の意味差は approved Design に明記されている。

### Main verification assumptions

Worker開始前に Main が次の4点だけを確認する。

1. `PlanningContext.dependency_summary` と `operator_context` を `tuple[str, ...]` とする。
2. `decided_at` を timezone-aware ISO-8601 とする。
3. `chatgpt_app.py` が existing private `_find_specdock_dir()` を再利用する。拒否する場合は、locatorを複製せず、shared helper extractionを別判断にする。
4. S01 live operation に temporary public reasonを追加しない。dispatch tracer は injected fake use caseで実施し、実 Candidate／Review／apply success は後続stepまで発生させない。

これら以外の field set、command surface、status semantics は approved documents から直接決定できる。

---

## Exact allowed paths

以下は **変更可能 path の上限** である。責務が不要なら作らない。ここにない path は変更しない。

| Path                                                                                          | Action | Bounded responsibility                                                           |
| --------------------------------------------------------------------------------------------- | ------ | -------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`                                    | new    | thin executable、shebang、runtime import、`main()` delegation                       |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py`                     | new    | ChatGPT CLI専用 main。既存 repo locator／bootstrap／dispatchを再利用                        |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`              | new    | 四commandだけの parser/help                                                          |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py`            | new    | `commands.issue_planning.command_specs()` だけを登録                                  |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py`         | new    | typed CLI args、mode option closure、UseCases call、result renderer selection       |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`      | new    | command request types、existing Issue resolver、canonical path result              |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py` | new    | strict JSON、identities、review/revision/human/result contracts、digest helpers     |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`     | new    | text／JSON renderer、`CliText` conversion                                          |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`           | modify | 四 planning use-case callable boundaryを末尾へ追加。既存 field／defaultを変更しない               |
| `tests/unit/domain/test_issue_planning_contracts.py`                                          | new    | strict contract、digest、revision、review、human、result tests                        |
| `tests/unit/application/test_issue_planning.py`                                               | new    | existing Issue／canonical path resolver tests                                     |
| `tests/unit/commands/test_issue_planning.py`                                                  | new    | args mapping、mode closure、fake use-case dispatch tests                           |
| `tests/unit/presentation/test_issue_planning.py`                                              | new    | text／JSON parity、ok／ready rendering tests                                        |
| `tests/cli_runtime/test_chatgpt_cli.py`                                                       | new    | provider executable help、command tree、full parser→dispatch tracer、Core isolation |

`application/contracts.py` へ追加する planning callables は既存 manual test constructionを壊さないよう、既存 required fieldsの後に fail-closed default付きで置く。既存 `build_runtime()` がそれらを実成功へ wire する変更は行わない。

明示的に変更しない shared files:

```text
src/spec_dock/assets/spec_dock/scripts/spec-dock
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py
```

新 CLI はこれらを importして再利用する。コピーやforkを作らない。

---

## Red-first test cases

| ID             | Fixture setup                                                                    | Command／operation                                                        | Expected observable result                            | Regression caught                                 |
| -------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------- |
| S01-CLI-001    | provider executable pathを直接使用                                                    | `python .../spec-dock-chatgpt --help`                                    | exit 0。`planning`、`review`だけを表示                       | Core command family混入、repo解決をhelp前に実行             |
| S01-CLI-002    | 同上                                                                               | `planning --help`                                                        | `create`、`revise`、`apply`だけ                           | `review planning` の誤配置、generic workflow command追加 |
| S01-CLI-003    | 同上                                                                               | `review --help`                                                          | `planning`だけ                                          | arbitrary review framework化                       |
| S01-CLI-004    | leaf help matrix                                                                 | 四leafの `--help`                                                          | 上記CLI surfaceのrequired／conditional optionを表示          | option欠落、`--target`／`--prompt`／`--repo`追加         |
| S01-CLI-005    | Core provider executable                                                         | Core `spec-dock --help`                                                  | 既存 command helpが成立し、ChatGPT四commandを含まない              | Core CLIへの誤登録                                     |
| S01-CLI-006    | parser＋spy use case                                                              | 各leafのvalid argvをparseしてdispatch                                         | exact typed request一件、spy call一回、他use case call 0     | command key取り違え、argument loss                     |
| S01-CLI-007    | parser＋spy                                                                       | archive Reviewに`--reviewed-head`、git-boundに`--candidate`                 | nonzero、spy call 0                                    | cross-mode identity混入                             |
| S01-CLI-008    | parser＋spy                                                                       | apply archiveで三archive identity optionの一つを欠落／git-boundでarchive optionを指定 | nonzero、spy call 0                                    | partial identityのapply流入                          |
| S01-CLI-009    | 同一 `PlanningCommandResult` を返すfake use case                                      | 同一commandを`--format text`と`--format json`でdispatch                       | 両方のstatus／reason／issue_idが完全一致                        | rendererごとの意味分岐                                   |
| S01-CLI-010    | executable source file                                                           | stat、先頭行確認                                                               | shebangあり、provider sourceがuser-executable             | executable skeletonが単なるPython moduleになる           |
| S01-RES-001    | tmp repoにInitiative→Epic→Issue `.meta.json` と三文書を作成。`StoredMetaRecord` はissueを指す | `resolve_existing_issue_target("iss-00003", ...)`                        | parent IDsとexact three-path tupleを返す                  | arbitrary path、active state推測                     |
| S01-RES-002    | recordsに対象IDなし                                                                   | unknown `iss-99999` をresolve                                             | typed rejection、filesystem write 0                    | unknown Issueの暗黙作成                                |
| S01-RES-003    | Initiative／Epic recordsとSeed文字列を用意                                               | `init-...`、`epic-...`、`"build payment flow"` をresolve                    | existing Issue requiredとして拒否                          | Seed／親nodeの暗黙materialization                      |
| S01-RES-004    | issue directory外、`..`、symlink、repository外pathをrecordへ設定                          | resolve                                                                  | 全件拒否                                                  | canonical target escape                           |
| S01-RES-005    | 三文書の一つを欠落またはsymlink化                                                             | resolve                                                                  | canonical target incompleteとして拒否                      | git-bound targetの部分集合化                            |
| S01-CTX-001    | valid PlanningContext                                                            | construct／`to_dict()`                                                    | immutable、exact field set、exact path order            | mutable context、path order drift                  |
| S01-CTX-002    | invalid HEAD、duplicate paths、wrong filenames、non-Issue ID                        | construct                                                                | validation rejection                                  | malformed identityが後段へ流入                          |
| S01-ID-001     | valid Candidate identity、logical filenameと` (1)` transport alias                 | parse／construct                                                          | accept、fields round-trip                              | transport suffixの過剰拒否                             |
| S01-ID-002     | fuzzy rename、absolute internal root、wrong SHA、version bool/0                     | parse／construct                                                          | reject                                                | rename ambiguity、unsafe identity                  |
| S01-ID-003     | archive／git-bound valid Reviewed identities                                      | digest計算                                                                 | canonical digestが安定、dict insertion order非依存           | nondeterministic identity binding                 |
| S01-ID-004     | outer identityとCandidate source／Issue不一致、mode field両方あり                          | parse／construct                                                          | reject                                                | cross-candidate／cross-mode binding                |
| S01-JSON-001   | 各contract JSONに同一keyを二回記述                                                        | strict parse                                                             | duplicate key rejection                               | last-key-wins approval bypass                     |
| S01-JSON-002   | top-levelとnested objectへunknown key追加                                            | strict parse                                                             | unknown key rejection                                 | schema拡張によるauthority混入                            |
| S01-JSON-003   | `NaN`、`Infinity`、non-object root                                                 | strict parse                                                             | reject                                                | 非標準JSON、shape ambiguity                           |
| S01-REVIEW-001 | findings 0件またはP2／P3-only                                                         | Review result parse                                                      | `verdict=pass`だけaccept                                | non-blocking observationのFAIL化                    |
| S01-REVIEW-002 | P0またはP1 findingあり                                                                | Review result parse                                                      | `verdict=fail`だけaccept                                | blocking findingのPASS化                            |
| S01-REVIEW-003 | duplicate finding ID、verdict矛盾                                                   | parse                                                                    | reject                                                | finding selection ambiguity                       |
| S01-REV-001    | archive ReviewにP0／P1 findings、exact result bytes、matching Candidate              | Semantic request validation                                              | accept                                                | legitimate semantic revision阻害                    |
| S01-REV-002    | P2-only、P3-only、P1＋P2 mixed、unknown finding ID                                   | Semantic request validation                                              | 全件reject                                              | P2／P3をrevision triggerに使用                         |
| S01-REV-003    | wrong Review bytes SHA、wrong Candidate、git-bound Review                          | Semantic request validation                                              | reject                                                | stale／unrelated Review reuse                      |
| S01-REV-004    | valid Mechanical fields                                                          | structural validation                                                    | accept。filesystem不変                                   | mechanical contract欠落                             |
| S01-REV-005    | invalid target、empty/equal old/new、diff_budget 0／bool、semantic key混入             | structural validation                                                    | reject                                                | cross-lane fallback、unbounded edit                |
| S01-HUM-001    | decision×plan_adoption×implementation_startの全8組合せ                                | Human decision validation                                                | approved/true/true と rejected/false/false の2件だけaccept | Human authority補完・推測                              |
| S01-HUM-002    | wrong reviewed identity digest                                                   | validation                                                               | reject                                                | identity object差替え                                |
| S01-HUM-003    | same JSON semanticsだがReview result file bytesを変更                                 | validation                                                               | raw bytes digest mismatchでreject                      | reserialized／modified Review流用                    |
| S01-HUM-004    | duplicate `decision`、unknown `approved_by`                                       | strict parse                                                             | reject                                                | duplicate／unknown approval metadata               |
| S01-RESULT-001 | 四success pair                                                                    | construct／render                                                         | create/revise/reviewは`ok`、applyだけ`ready`              | `ok`をimplementation readinessとして扱う                |
| S01-RESULT-002 | `ready/candidate_created`、`ok/adoption_published`                                | construct                                                                | reject                                                | status／reason semantic drift                      |
| S01-RESULT-003 | 全statusのrepresentative result                                                    | text／JSON render                                                         | status、reason、issue_id parity。exit code mapping一致     | format別 semantics、wrong exit ownership            |
| S01-RESULT-004 | outputにPath、bytes、set、non-string key                                             | construct                                                                | reject                                                | JSON render時のlate failure                         |
| S01-REG-001    | existing core runtime test                                                       | `tests/cli_runtime/test_runtime_shell_s11.py`                            | Green                                                 | shared CommandSpec／UseCases変更によるCore破壊            |

各 Red test は、対象production codeを追加する前に失敗を確認する。Red evidenceとして少なくとも test name と failure reason を残し、単に「file not found」で失敗しただけのケースを contract Red と数えない。

---

## Implementation sequence

1. **Baselineを固定する**

   ```bash
   test "$(git rev-parse HEAD)" = "b1ee8d091deba166b805145e7367190de6a14578"
   test "$(git branch --show-current)" = "iss-00334-implement-chatgpt-issue-planning-workflow"
   git status --short
   ```

   worktreeがdirty、branch／HEADが異なる場合は変更を開始しない。

2. **Result envelope と rendererを最初の tracer bullet にする**

   * `PlanningCommandResult` の status union、success pair、JSON-value validation、exit-code mappingをRed化する。
   * `presentation/issue_planning.py` の text／JSON rendererを実装する。
   * 同一resultからstatus／reasonが一致することをGreenにする。
   * `CommandOutcome`／`CliText` は再定義しない。

3. **Parser／registry／command wrapper の vertical tracerを作る**

   * `chatgpt_parser.py` に四commandだけを追加する。
   * `chatgpt_registry.py` は planning command specs だけを集める。
   * `commands/issue_planning.py` にtyped argsと四run wrapperを置く。
   * `application/contracts.py` の末尾へ四use-case callable boundaryをdefault付きで追加する。
   * injected fake use caseを用い、parser→registry→dispatch→renderer の一周をGreenにする。
   * Candidate生成等のproduction successは実装しない。
   * temporary `ok`／`ready`、temporary public reasonを作らない。

4. **Strict JSONとidentity foundationを実装する**

   * duplicate-key-aware loader
   * safe string／SHA／path／filename helper
   * canonical JSON bytes／SHA helper
   * `IssueCandidateIdentity`
   * `ReviewedPlanningIdentity`
   * identity mismatch tests

   Helper は `issue_planning_contracts.py` 内の private function とし、generic schema frameworkへ抽出しない。

5. **Review、Revision、Human contractsを実装する**

   * Review finding／verdict invariant
   * semantic request structural parseとReview-bound validation
   * P2／P3 rejection
   * mechanical structural closure
   * Human truth table
   * exact identity digestとraw Review bytes digest

   actual revision、file replacement、diff calculationは追加しない。

6. **PlanningContext と existing-Issue resolverを実装する**

   * resolverは `Sequence[StoredMetaRecord]` と `repo_root` を入力にする。
   * record loadingそのものは既存 node reader／infra ownerに残す。
   * resolver内部でdirectory scanやactive state fallbackを作らない。
   * exact three paths、parent IDs、safe repo-relative conversionをGreenにする。

7. **`chatgpt_app.py` と executableを追加する**

   `chatgpt_app.main` は Core `app.main` の制御順に合わせる。

   1. chatgpt registryを構築
   2. chatgpt parserを構築
   3. parseし、helpの`SystemExit(0)`を返す
   4. existing `_find_specdock_dir()` を再利用
   5. existing `build_runtime()` を再利用
   6. existing `dispatch()` を呼ぶ

   `spec-dock-chatgpt` は thin entrypoint とし、business validationを置かない。source fileに executable bitを設定する。

8. **Core isolation regressionを閉じる**

   * Core parser／registryに新commandがないことを確認する。
   * existing shell/dispatch testを実行する。
   * import cycle、type error、ruff violationを解消する。
   * refactorは重複除去に限定し、新frameworkへ拡張しない。

9. **Diff boundaryを確認する**

   * changed pathが allowed list内だけであることを確認する。
   * root dogfood、installer、Skill、Prompt、Issue canonical docsが不変であることを確認する。
   * workerは `report.md`／`.assurance.json` を更新しない。

---

## Verification commands

最小単位から順に実行する。

```bash
uv run pytest -q tests/unit/domain/test_issue_planning_contracts.py
```

```bash
uv run pytest -q tests/unit/application/test_issue_planning.py
```

```bash
uv run pytest -q \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py
```

```bash
uv run pytest -q tests/cli_runtime/test_chatgpt_cli.py
```

Core compatibility:

```bash
uv run pytest -q tests/cli_runtime/test_runtime_shell_s11.py
```

Provider help smoke:

```bash
uv run python \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  --help
```

```bash
uv run python \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  planning create --help
```

```bash
uv run python \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  review planning --help
```

Lint:

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py
```

Type check:

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py
```

Canonical tree and diff checks:

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
git diff --name-only
```

S01 では次を実行対象にしない。

```text
uv build
full `uv run pytest`
fresh init/update parity
tests/integration
live ChatGPT
GitHub remote mutation
dogfood update
```

---

## Forbidden changes

次の path／責務への変更は禁止する。

```text
spec-dock/**
```

root `spec-dock/` は dogfood projectionであり、provider sourceと同時編集しない。

```text
src/spec_dock/cli.py
pyproject.toml
src/spec_dock/assets/install_root/.agents/**
src/spec_dock/assets/install_root/.codex/**
src/spec_dock/assets/install_root/.github/**
```

distribution、installed Skill、Prompt、native shimを変更しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec-dock
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
```

Core CLIの command surface／runtime behaviorを変更しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/**
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/**
src/spec_dock/assets/spec_dock/scripts/authoring-pack/**
```

既存 authoring-pack generic contractを拡張・破壊しない。

以下を新設しない。

* generic workflow engine
* plugin command registry
* persistent planning registry／database
* custom Git ref
* operation manifest store
* backend adapter
* GitHub client／remote preflight
* archive packager／extractor
* transaction manager
* filesystem adoption helper
* commit／push helper
* arbitrary target／Prompt／backend option
* parallel `CommandOutcome`／`CliText`／dispatch implementation

以下の product behaviorを実装しない。

* Candidate ZIP作成または検証
* ChatGPT起動
* Review実行
* mechanical replacement
* canonical三文書書換え
* Human decision artifact書込み
* rollback
* validation/sync orchestration
* commit/push/publication
* live dogfood

次の Issue-local filesも変更しない。

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/requirement.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/design.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/plan.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/report.md
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/.assurance.json
```

---

## Stop conditions

次のいずれかが成立したら、推測で拡張せず変更を停止し、Mainへ返す。

1. branch が `iss-00334-implement-chatgpt-issue-planning-workflow` でない、または HEAD が `b1ee8d091deba166b805145e7367190de6a14578` でない。
2. baseline worktreeが既にdirtyで、既存差分とworker差分を安全に分離できない。
3. S01を成立させるために forbidden path の変更が必要になる。
4. Core parser／registry／dispatchを変更しなければ新 CLI を作れないことが判明する。
5. `_find_specdock_dir()` の再利用が不可能で、repo locatorの複製またはCore app refactorが必要になる。
6. Valid S01 command にtemporary public status／reasonを導入しないとquality gateを通せない。Mainがreason codeを承認するまで追加しない。
7. `PlanningContext.dependency_summary`／`operator_context` の具体型が後続Prompt contractと衝突する証拠が見つかる。
8. Approved field setだけでは identity digestを一意に構築できない。
9. P2／P3 severityを判定するために Review result以外のdatabase／registryが必要になる。
10. Existing Issue resolverが `.meta.json` authorityではなくactive pointer、directory name推測、GitHub Issue APIを必要とする。
11. exact canonical three paths以外を reviewed targetへ追加する必要が出る。
12. duplicate-key rejectionを実装するためにgeneric JSON loaderやauthoring-pack public contractを変更する必要が出る。
13. 新 executable のwheel／fresh-install executable-bit保証のためinstaller変更が必要になる。これはS06へ残す。
14. focused testsで approved status semantics、Human truth table、P2／P3 ruleと直接矛盾する既存behaviorが判明する。
15. Ruff／mypyを通すために global config、dependency、broad ignoreを追加する必要が出る。
16. Core CLI regression testが失敗し、修正がS01 allowed paths内に収まらない。
17. Git、backend、archive、filesystem adoption、commit／pushの実装が必要になった時点。
18. Public command family、Candidate inventory、Human authority、review severity semanticsの変更が必要になった時点。これは approved Plan の amendment triggerである。

---

## Subagent instruction

```text
Repository: chemitaro/spec-dock
Branch: iss-00334-implement-chatgpt-issue-planning-workflow
Required HEAD: b1ee8d091deba166b805145e7367190de6a14578
Task: iss-00334 / S01 CLI Skeleton and Domain Contracts only

作業開始前に branch、HEAD、git status を確認せよ。branchまたはHEADが一致しない場合、あるいは既存差分を安全に分離できない場合は変更せず停止せよ。

S01だけを実装せよ。独立した provider-side repo-local executable `spec-dock-chatgpt`、四commandのparser/help/dispatch wiring、PlanningCommandResult、PlanningContext、IssueCandidateIdentity、ReviewedPlanningIdentity、PlanningRevisionRequestV1、PlanningReviewResult、PlanningHumanDecisionV1、existing-Issue canonical-three-path resolverを実装せよ。

公開commandは次の四つだけとせよ。

- planning create
- planning revise
- review planning
- planning apply

Core `spec-dock` CLIへcommandを追加するな。

CLI argumentsは以下に固定せよ。

- planning create:
  --issue, --output, --format {text,json}
- planning revise:
  --candidate, --request, --output, --format {text,json}
- review planning:
  --issue, --mode {archive-candidate,git-bound}, --output,
  archiveでは--candidate、
  git-boundでは--reviewed-head、
  --format {text,json}
- planning apply:
  --issue, --mode, --review-result, --human-decision, --expected-head, --output,
  archiveでは--candidate、--logical-filename、--zip-sha256、
  git-boundでは--reviewed-head、
  --format {text,json}

--repo、--branch、--target、--prompt、--backend、任意path overrideを追加するな。

既存の CommandArgs、CommandSpec、CommandRegistry、CommandOutcome、dispatch、CliText、build_runtime、repo locatorを再利用せよ。これらを複製したChatGPT専用frameworkを作るな。

変更可能pathは以下だけとする。

- src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_registry.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
- tests/unit/domain/test_issue_planning_contracts.py
- tests/unit/application/test_issue_planning.py
- tests/unit/commands/test_issue_planning.py
- tests/unit/presentation/test_issue_planning.py
- tests/cli_runtime/test_chatgpt_cli.py

ここにないpathを変更するな。

最初にRed testsを書け。各Redが単なるmissing importではなく、対象contractの欠落で失敗していることを確認せよ。

最低限、以下をtestせよ。

- top-level、group、leaf help
- 四command以外が公開されない
- forbidden optionが存在しない
- Core spec-dock helpが不変
- archive／git-bound option closure
- parser→registry→existing dispatch→injected fake use case→renderer tracer
- text／JSONのstatus、reason、issue_id parity
- okとreadyの区別
- exact success pairs:
  ok/candidate_created
  ok/candidate_revised
  ok/review_completed
  ready/adoption_published
- existing Issue positive
- unknown Issue rejection
- Initiative／Epic／Seed rejection
- exact canonical three pathsをUTF-8 byte順で返す
- missing／symlink／outside-repository canonical path rejection
- strict JSON duplicate-key rejection
- unknown-key rejection
- Candidate transport filenameのclosed (N) suffix
- archive／git-bound Reviewed identity closure
- canonical identity SHA-256 mismatch
- Review resultのP0／P1 verdict rule
- P2／P3-only Reviewはpass
- Semantic revisionでP0／P1だけ受理
- P2／P3-only、mixed、unknown finding rejection
- Review raw bytes digest mismatch
- Mechanical target allowlist、old/new、meaning invariant、positive diff budget
- Human decision全8組合せのtruth table
- Human reviewed identity／Review bytes digest mismatch
- non-JSON output value rejection
- Core runtime shell regression

canonical JSONは既存precedentと同じく、ensure_ascii=False、sort_keys=True、separators=(",", ":")、UTF-8、SHA-256を使え。

Reviewed identity digestはcanonical identity objectをhashせよ。Review result SHAは再serializeせず、exact file bytesをhashせよ。

PlanningReviewResultではP0／P1が一件以上ならfail、0件ならpassとせよ。P2／P3だけならpassとせよ。

PlanningRevisionRequestV1のSemantic laneでは、exact Review resultに存在するP0／P1 finding IDだけを受理せよ。P2／P3、unknown ID、wrong Candidate、wrong Review digest、git-bound Reviewを拒否せよ。Mechanical laneではschemaだけを閉じ、actual replacement、unique match、diff executionは実装するな。

PlanningHumanDecisionV1では次の二組だけを受理せよ。

- approved / plan_adoption=true / implementation_start=true
- rejected / plan_adoption=false / implementation_start=false

Human decisionを生成、補完、推測するな。

Existing Issue resolverはStoredMetaRecordを入力にし、active pointer、directory-name推測、GitHub API、Seed materializationを使うな。canonical targetは同一Issue directoryのdesign.md、plan.md、requirement.mdのexact three pathsだけとせよ。

S01ではCandidate ZIP、Git preflight、ChatGPT process、Review execution、filesystem adoption、commit、push、Skill、Prompt、installer、distribution、dogfoodを実装するな。

Live handlerからcandidate_created、candidate_revised、review_completed、adoption_publishedを偽って返すな。S01のdispatch tracerはinjected fake use caseで検証せよ。temporary public status／reasonが必要になった場合は追加せず停止せよ。

次の順でverificationを実行せよ。

1. uv run pytest -q tests/unit/domain/test_issue_planning_contracts.py
2. uv run pytest -q tests/unit/application/test_issue_planning.py
3. uv run pytest -q tests/unit/commands/test_issue_planning.py tests/unit/presentation/test_issue_planning.py
4. uv run pytest -q tests/cli_runtime/test_chatgpt_cli.py
5. uv run pytest -q tests/cli_runtime/test_runtime_shell_s11.py
6. allowed Python filesとtestsに対するruff
7. changed runtime modulesに対するmypy
8. ./spec-dock/scripts/spec-dock validate
9. git diff --check
10. git diff --name-only

full suite、uv build、fresh init/update、integration、live backend、dogfoodは実行対象に含めるな。

完了時は次の見出しで証拠を返せ。

Changed files
- 各変更fileと責務
- allowed path外の変更が0であること

Tests and results
- Redで確認したtest名とfailure reason
- 実行command
- exit code
- passed／failed／skipped count
- Core regression result
- validate、ruff、mypy、git diff --check結果

Unresolved risks
- 未解決risk
- Main verification assumption
- S02以降へ明示的に残した事項

Ledger Note
- approved planを超えるmaterial implementation decisionを行った場合だけ、decision、alternatives、rationale、affected paths、follow-upを記載せよ。
- material decisionがなければ、次の一文を文字どおり返せ。

No material implementation decisions beyond the approved plan.
```
