---
created_by_role: chatgpt-pro
scope_id: iss-00334
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
intended_targets:
  - iss-00334/S02
adoption_status: execution-input
reflected_to: []
diff_guard_result: passed
source_head: c597bd146c1d68e619cdc1e24b1b76dd405fe36a
oracle_session: iss00334-s02-implementa-brief
---

# S02 ChatGPT implementation work packet

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a677f30-5744-83ee-b4ba-49cda3df283c

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

Use the attached prompt file as the complete task brief. Inspect the exact GitHub branch and attached repository sources, then return only the requested S02 implementation work packet.

## Answer

## 1. Scope confirmation

GitHub connector で `chemitaro/spec-dock` の現行 branch `iss-00334-implement-chatgpt-issue-planning-workflow` を開き、branch HEAD が指定 SHA `c597bd146c1d68e619cdc1e24b1b76dd405fe36a` と同一であることを確認した。current branch が存在したため、default branch `main` への fallback は使用していない。以下は、この exact HEAD と添付 task brief を実行境界とする S02 専用 work packet である。

S02 の実装範囲は次に限定する。

| 区分               | S02 で実装するもの                                                                                                             |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Git identity     | current repository、named branch、upstream、local HEAD、remote branch HEAD                                                  |
| Git gate         | dirty worktree/index、detached HEAD、upstream 不在、non-GitHub upstream、fetch failure、local/remote mismatch の fail-closed 判定 |
| Planning context | existing Issue、親 ID、direct dependencies、canonical 3 paths、明示された関連 source、operator context                               |
| Prompt           | provider-owned Planner／Reviewer Prompt と transport output contract                                                      |
| Backend          | 固定 ChatGPT Use wrapper の direct-argv invocation                                                                         |
| Backend failure  | missing executable、timeout、nonzero、missing output、partial／malformed response                                            |
| Security         | invocation 前の secret／credential／private absolute-path 検査、diagnostic 前の redaction                                        |
| Evidence         | repository／branch／upstream／local HEAD／remote HEAD を含む source identity evidence                                          |

承認済み Plan は S02 を「exact GitHub source へ bind した安全な Planner／Reviewer invocation」と定義し、Candidate packaging を S03、Review／Revision の意味解析を S04 に分離している。

次は明示的に実装しない。

* Candidate ZIP、Candidate ID、version、ZIP SHA。
* Candidate 用 `SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`。
* Planner の三文書意味解析、front matter 検証、complete-document 判定。
* Reviewer finding、severity、verdict の意味解析。
* revision、Human decision、apply、canonical rewrite、rollback。
* validate、commit、push、remote publication、dogfood。
* root `spec-dock/` または root `.agents/` への projection。
* installer／update／wheel／sdist parity。
* public CLI option、arbitrary Prompt、arbitrary target、arbitrary backend command の追加。

既存 `invoke_backend` の ABI が要求する一時的な prompt-transport metadata は、repository 外の一時 directory にだけ生成し、呼出し終了後に削除してよい。この directory は Candidate ではなく、S03 の Candidate control files を生成・公開してはならない。

S01 の `PlanningCommandResult` success pair は変更しない。S02 の transport 成功だけで `ok/candidate_created`、`ok/candidate_revised`、`ok/review_completed` を返してはならない。S02 は in-memory payload と source evidence を後続 S03／S04 に渡す内部 transport boundary を完成させる。

---

## 2. Repository findings

### 2.1 現行 owner と実装状況

| Concern                  | Exact owner                                                                  | Exact HEAD の状況                                                                                                                | S02 の判断                                                      |
| ------------------------ | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Existing Issue 解決        | `application/issue_planning.py`                                              | Issue kind、親 ID、安全な Issue directory、exact canonical 3 paths を既に解決する                                                           | 同 module を application orchestration owner として拡張する           |
| PlanningContext          | `domain/issue_planning_contracts.py`                                         | repository、branch、source HEAD、親、dependency summary、canonical paths、relevant sources、operator context の closed dataclass が存在する | public field を増やさず利用する                                       |
| GitHub sync preflight    | `application/authoring_pack/github_sync_preflight.py`                        | branch、fetch、upstream、worktree/index、remote tracking ref、local/remote mismatch、concurrent change を既に判定する                      | 並行 preflight を作らず、そのまま呼ぶ                                     |
| GitHub repository slug   | `infra/git_cli.py::origin_github_repo_slug`                                  | origin の fetch URL と push URL がともに GitHub で同一 `owner/repo` かを検証する                                                             | preflight 後の GitHub identity postcondition に再利用する            |
| Backend process          | `application/authoring_pack/backend_invoke.py`                               | argv list による `subprocess.run`、missing executable、OS error、timeout、nonzero を分類する                                              | subprocess framework を新設せず、transient stream capture だけ最小拡張する |
| Backend result redaction | `domain/authoring_pack/backend_invoke_contract.py`                           | serialized argv／path／blocker を redact し、stdout／stderr 本文を result に保存しない                                                       | public serialization contract を維持する                          |
| Sensitive-content scan   | `domain/authoring_pack/authority_boundary.py`                                | structured secret、credential-like path、raw transcript marker の scanner が存在する                                                  | dynamic context の scan に再利用し、private absolute-path scan だけ補う |
| Public CLI               | `commands/issue_planning.py` ほか S01 files                                    | 四 command だけが登録済み。backend／Prompt／repository override option はない                                                               | surface を変更しない                                               |
| Runtime wiring           | `application/contracts.py`、`cli/bootstrap.py`                                | planning use cases は fail-closed unconfigured。bootstrap は planning handler をまだ注入しない                                           | S02 では public command success path を wire しない                |
| Prompt authority         | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/` | `SKILL.md` は存在する                                                                                                              | 同 Skill 配下に S02 Prompt resources だけを追加する                     |

`resolve_existing_issue_target` は exact 3 paths を UTF-8 byte order で返し、repository 外、`..`、symlink、欠落 document を拒否している。

`PlanningContext` の既存 field と validation は approved Design の field set と一致している。

既存 preflight は以下を既に持つ。

* detached HEAD → `detached_head`
* origin missing → `origin_missing`
* fetch failure → `origin_fetch_failed`
* upstream missing → `remote_branch_missing`
* non-origin upstream → `origin_mismatch`
* untracked／staged／dirty tracked
* ahead／behind／diverged／head mismatch
* fetch 後 snapshot と final guard による concurrent change 検出

したがって、S02 独自の Git command sequence や第二の preflight module は不要である。

既存 `origin_github_repo_slug` は GitHub HTTPS／SSH URL を closed parser で処理し、fetch/push URL の repository mismatch も拒否する。例外文には remote URL が入り得るため、S02 はその例外文字列を diagnostic へ転送せず、stable reason に変換する。

既存 backend は `shell=True` を使わず、`subprocess.run(list(invocation_argv), ...)` を使用している。missing、timeout、nonzero の分類と raw stream 非永続化も既にある。

### 2.2 File placement decision

S02 は次の配置とする。

* **`application/issue_planning.py` を拡張する**
  Git preflight orchestration、existing Issue／dependency の解決、bounded PlanningContext assembly、failure-to-command-result mapping を置く。

* **`application/issue_planning_prompt.py` を新設する**
  Provider Prompt resource と dynamic PlanningContext を合成する純粋 application module とする。process、Git、filesystem publication は持たせない。

* **`infra/issue_planning_chatgpt.py` を新設する**
  固定 wrapper、ephemeral prompt-transport directory、backend invocation、response framing の transport boundary を置く。

* **汎用 `workflow` module や `planning_backend` registry は作らない**。

* **`cli/bootstrap.py` は変更しない**
  S02 transport success は Candidate／Review completion ではないため、public `planning create`／`review planning` の successful use case wiring は S03／S04 integration まで行わない。

### 2.3 Internal result boundary

S02 用に、public lifecycle result と分離した closed internal result を置く。

```text
PlanningSourceEvidence
- repository
- branch
- upstream
- local_head
- remote_head
- source_manifest_hash
- snapshot_id
- remote_head_disposition

PlanningInvocationResult
- status = pass | blocked | rejected
- reason
- source_evidence
- backend_exit_code
- response_bytes
- response_sha256
- transient_payload  # in-memory only; repr/serialization対象外
```

Stable reason は少なくとも次に閉じる。

```text
transport_received
git_preflight_blocked
github_upstream_required
upstream_branch_mismatch
planning_context_rejected
sensitive_input_rejected
backend_unavailable
backend_timeout
backend_nonzero
backend_output_missing
backend_response_partial
backend_response_malformed
```

`transient_payload` は `to_dict()`、JSON、text output、summary file、exception message、test failure messageに含めない。

### 2.4 Git acceptance postconditions

`run_github_sync_preflight` が `pass` を返した後、S02 はさらに次を全て確認する。

```text
repository.branch is not None
repository.upstream == "origin/" + repository.branch
effective_ref == repository.branch
local_head == remote_head
remote_head_disposition == "fetched_remote_tracking_ref"
origin_github_repo_slug(repo_root) returns owner/repo
```

この postcondition は既存 preflight の置換ではない。Issue Planning が必要とする「current named branch とその exact upstream branch」の追加 narrowing である。

### 2.5 Bounded context policy

Public CLI に relevant source option を追加しない。S02 application API が内部入力として受ける `relevant_source_paths` と `operator_context` に、次の closed bounds を適用する。

| Input                      | Bound                                                                                   |
| -------------------------- | --------------------------------------------------------------------------------------- |
| Canonical Issue paths      | resolver が返す exact 3 paths                                                              |
| Parent identities          | exact Epic ID と Initiative ID                                                           |
| Dependencies               | existing deps topology reader が解決した direct dependencies のみ。最大 32。超過は truncate せず reject |
| Relevant source paths      | 最大 16 files                                                                             |
| Relevant source file size  | 1 file 最大 256 KiB                                                                       |
| Relevant source aggregate  | 最大 2 MiB                                                                                |
| Operator context entries   | 最大 16                                                                                   |
| Operator context entry     | 最大 4 KiB                                                                                |
| Operator context aggregate | 最大 32 KiB                                                                               |

Relevant source は次を全て満たす regular UTF-8 file に限定する。

* repository-relative POSIX path。
* directory ではない。
* repository 内。
* symlink および symlink ancestor なし。
* `..`、absolute path、backslash なし。
* `.workbench`、credential-like path、`.env`、private key、binary、hidden secret path を含まない。
* UTF-8 byte order で deduplicate／sort。
* repository-wide auto-discovery、grep-based discovery、directory recursion をしない。

---

## 3. Exact allowed paths

### 3.1 Write allowlist

以下だけを変更または新設してよい。

| Path                                                                                                               | Responsibility                                                                            |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`                           | preflight orchestration、Issue／parent／dependency resolution、bounded context、result mapping |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`                    | Planner／Reviewer Prompt synthesis、dynamic block rendering、pre-invocation scan             |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`                      | `PlanningSourceEvidence` と internal `PlanningInvocationResult` の closed contracts         |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`                         | fixed wrapper adapter、ephemeral transport pack、backend mapping、response framing           |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py`            | existing execution core のまま transient stream capture entrypoint を追加                       |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py`        | optional verified working directory field。serialized result contract は変更しない               |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py`             | content-free private absolute-path finding helper。既存 secret scanner を維持                   |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md`            | provider-owned Planner role、S02 scope、non-goals                                           |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md`           | provider-owned read-only Reviewer role、defect-only boundary                               |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md` | common response start/end framing、no transcript／secret／path rule                          |
| `tests/unit/application/test_issue_planning.py`                                                                    | context assembly、preflight short-circuit、source evidence                                  |
| `tests/unit/application/test_issue_planning_prompt.py`                                                             | resource loading、Prompt content、bounded dynamic context、security                          |
| `tests/unit/domain/test_issue_planning_contracts.py`                                                               | source／invocation result validationと非serialization                                        |
| `tests/unit/infra/test_issue_planning_chatgpt.py`                                                                  | fixed argv、cwd、output framing、backend classification                                      |
| `tests/unit/authoring_pack/test_backend_invoke_capture.py`                                                         | shared backend capture compatibility、raw stream non-persistence                           |
| `tests/integration/test_issue_planning_chatgpt_transport.py`                                                       | synced fake repo→Prompt→fake wrapper の tracer bullet                                      |
| `tests/cli_runtime/test_chatgpt_cli.py`                                                                            | S01 public surface と unconfigured boundary の回帰だけ                                          |

`tests/cli_runtime/test_chatgpt_cli.py` は、既存 assertion で十分なら変更しない。

### 3.2 Read-only reuse paths

以下は参照・import・test execution は許可するが、S02 では変更しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/authoring_pack/git_fetch.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue_planning.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py
tests/cli_runtime/test_authoring.py
tests/cli_runtime/test_runtime_shell_s11.py
tests/unit/commands/test_issue_planning.py
tests/unit/presentation/test_issue_planning.py
```

### 3.3 Prompt resource／S06 boundary

`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/` は既に provider-side Skill authority であり、package data は `assets/install_root/.agents/**` を含める設定になっている。したがって、S02 Prompt source files はここに置ける。

ただし S02 では次を行わない。

```text
.agents/skills/spec-dock-issue-planning/resources/*
spec-dock/...
installer/update logic
fresh-init fixtures
provider/dogfood byte parity assertions
```

これらへの projection と parity は S06 owner である。

---

## 4. Reuse map

| S02 need                         | Reuse target                                                  | Required adaptation                                                                           |
| -------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Existing Issue と canonical paths | `resolve_existing_issue_target`                               | 変更せず利用                                                                                        |
| Context contract                 | `PlanningContext`                                             | 既存 field set を利用                                                                              |
| Direct dependencies              | `DepsTopologyReader.load_direct_dependency_resolutions`       | application 側で ID/kind/title の bounded summary に変換                                            |
| Source path safety/hash          | `source_path_blockers`、`build_source_manifest`                | explicit file listだけを渡す。default recursive source setを使わない                                     |
| Git preflight                    | `run_github_sync_preflight`                                   | `allow_default_branch_fallback=False`、real current branch、explicit sources                    |
| Fetch policy                     | `run_origin_fetch_policy`／`execute_git_fetch`                 | 変更なし                                                                                          |
| GitHub owner/repo                | `origin_github_repo_slug`                                     | exception textを捨て stable reasonへ変換                                                            |
| Process execution                | `invoke_backend` の既存 execution core                           | transient capture を返す sibling entrypoint を同 module 内に追加                                       |
| Request ABI                      | `BackendInvokeRequest`                                        | verified `working_dir=repo_root` を optional field として追加                                       |
| Wrapper argv suffix              | existing `_backend_invocation_argv`                           | 変更せず利用                                                                                        |
| Fixed wrapper                    | internal constant                                             | `/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt`。public/env overrideなし |
| Secret scan                      | `scan_constraint_sensitive_payload`、`is_credential_like_path` | dynamic values/filesだけに適用                                                                     |
| Private path scan                | authority-boundary helper                                     | finding は path 値でなく stable code のみ                                                            |
| Diagnostic redaction             | `BackendInvokeResult.to_dict()`                               | raw capture を serialization から除外                                                              |
| Prompt pack validation           | `validate_prompt_pack`                                        | ephemeral S02 transport packを既存 required-file contractに適合させる                                  |
| Public command result            | `PlanningCommandResult`                                       | success pairを増やさない。blocked/rejected mapping時のみ `output.source_identity` を利用                   |

### Backend execution shape

S02 adapter は次の固定 contract のみを生成する。

```python
FIXED_CHATGPT_USE_ARGV = (
    "/Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt",
)
```

既存 backend request へ内部的にこの一要素 command を渡す。S02 CLI／environment／operator input から executable、arguments、model、browser profile を上書きできる経路は作らない。

Process は verified `repo_root` を `cwd` として起動し、ChatGPT Use wrapper の current repository inference に GitHub context を委ねる。GitHub REST／GraphQL／`gh api` fallback は追加しない。

### Transient capture rule

Shared backend module は一つの execution core を持つ。

```text
_invoke_backend_core(...) -> (BackendInvokeResult, BackendStreamCapture)

invoke_backend(...) -> BackendInvokeResult
invoke_backend_with_capture(...) -> (BackendInvokeResult, BackendStreamCapture)
```

* `invoke_backend` の既存 behavior と return type は不変。
* `BackendStreamCapture` は internal、`repr=False`、JSON 化不可。
* summary には stdout/stderr byte count だけを残す。
* S02 は stdout を framing 判定後、payload と SHA-256 に分ける。
* stderr 本文は捨て、classification に使用しない。
* exception、pytest assertion、diagnostic file に stream 本文を入れない。

### Response framing

`transport-output-contract.md` は exact framing を固定する。

```text
<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=<planner|reviewer> source_head=<40-hex>>>
<payload>
<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>
```

判定規則:

| Observation                                                      | Classification                        |
| ---------------------------------------------------------------- | ------------------------------------- |
| stdout が空または空白だけ                                                 | `blocked/backend_output_missing`      |
| exact start marker あり、end marker なし                              | `blocked/backend_response_partial`    |
| exact frame があるが payload が空                                      | `blocked/backend_response_partial`    |
| marker 重複、順序不正、role 不一致、HEAD 不一致、frame 外 non-whitespace、UTF-8 不正 | `rejected/backend_response_malformed` |
| exact marker が一組、role／HEAD 一致、payload 非空                         | `pass/transport_received`             |

S02 は payload 内の requirement／design／plan、finding、JSON schema を解析しない。

---

## 5. Red-first test cases

### 5.1 Git preflight and source identity

| ID          | Fixture setup                                                                                                                          | Operation                                                     | Expected observable result                                                                            | Regression caught                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| S02-GIT-001 | Temporary Git repo、named branch、commit、`refs/remotes/origin/<branch>` を同じ SHA に設定、GitHub fetch/push URL、upstream 設定、fake fetch success | Real `run_github_sync_preflight` を通して planning invocation を実行 | preflight pass、backend call count `1`、repository=`owner/repo`、branch／upstream／local／remote HEAD exact | preflight bypass、wrong source binding    |
| S02-GIT-002 | tracked file を unstaged modify                                                                                                         | invocation                                                    | `blocked/git_preflight_blocked`、details に `dirty_tracked`、backend count `0`                           | dirty worktree から ChatGPT 起動             |
| S02-GIT-003 | tracked file を stage                                                                                                                   | invocation                                                    | blocker `staged_changes`、backend count `0`                                                            | dirty index の見落とし                        |
| S02-GIT-004 | untracked file を追加                                                                                                                     | invocation                                                    | blocker `untracked_files`、backend count `0`                                                           | untracked context drift                  |
| S02-GIT-005 | exact commit を detached checkout                                                                                                       | invocation                                                    | blocker `detached_head`、backend count `0`                                                             | unnamed branch invocation                |
| S02-GIT-006 | branch の upstream config を削除                                                                                                           | invocation                                                    | blocker `remote_branch_missing`、backend count `0`                                                     | unpublished／untracked branch invocation  |
| S02-GIT-007 | branch が `origin/other-branch` を track。current branch remote ref も存在                                                                   | invocation                                                    | `blocked/upstream_branch_mismatch`、backend count `0`                                                  | current branch と別 upstream の誤 binding    |
| S02-GIT-008 | origin fetch/push が GitLab URL または local path                                                                                          | invocation                                                    | `blocked/github_upstream_required`、backend count `0`、diagnostic に URL/path なし                         | non-GitHub upstream の受理、private URL leak |
| S02-GIT-009 | origin fetch URL と push URL が別 GitHub repo                                                                                             | invocation                                                    | `blocked/github_upstream_required`、backend count `0`                                                  | GitHub scope split                       |
| S02-GIT-010 | injected fetch executor が nonzero／timeout outcome                                                                                      | invocation                                                    | blocker `origin_fetch_failed`、backend count `0`                                                       | stale remote cache からの invocation        |
| S02-GIT-011 | local HEAD と remote HEAD が ahead／behind／diverged                                                                                       | parameterized invocation                                      | existing blocker が保持され、backend count `0`                                                              | mismatch の silent acceptance             |
| S02-GIT-012 | first snapshot 後に HEAD／source file を mutate                                                                                            | snapshot hook 付き invocation                                   | blocker `concurrent_repo_change`、backend count `0`                                                    | TOCTOU                                   |

### 5.2 PlanningContext and Prompt synthesis

| ID             | Fixture setup                                                                            | Operation                                         | Expected observable result                                                                                    | Regression caught                    |
| -------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| S02-CTX-001    | existing Issue record、Epic／Initiative records、canonical 3 docs、direct dependency records | context assembly                                  | exact Issue ID、parent IDs、UTF-8 ordered canonical 3 paths、sorted direct dependency summary                    | Seed／別 Issue／wrong parent 混入         |
| S02-CTX-002    | direct dependencies 32 件                                                                 | context assembly                                  | 32 件を deterministic order で保持                                                                                 | nondeterministic Prompt              |
| S02-CTX-003    | direct dependencies 33 件                                                                 | context assembly                                  | `planning_context_rejected`、backend count `0`                                                                 | silent truncation                    |
| S02-CTX-004    | relevant source 16 files、size／aggregate limit 内                                          | context assembly                                  | exact explicit filesだけが選択される。repository の unrelated files は選ばれない                                              | repository-wide scan、scope expansion |
| S02-CTX-005    | 17 files、oversized file、aggregate超過                                                      | parameterized assembly                            | stable context rejection、backend count `0`                                                                    | unbounded context                    |
| S02-CTX-006    | source path に absolute、`..`、backslash、symlink、directory、`.workbench`、`.env`              | parameterized assembly                            | reject、backend count `0`、diagnostic は category code のみ                                                        | path escape、secret file attachment   |
| S02-CTX-007    | same paths in different input order／duplicate                                            | assembly                                          | identical ordered PlanningContext／Prompt bytes                                                                | order-dependent Prompt identity      |
| S02-PROMPT-001 | clean exact repo + captured ephemeral prompt pack                                        | Planner synthesis                                 | Prompt に exact `owner/repo`、branch、local HEAD、remote HEAD、upstream、Issue、parents、dependencies、canonical paths | source identity omission             |
| S02-PROMPT-002 | same fixture                                                                             | Reviewer synthesis                                | read-only、fresh conversation、defect-only、no patch／replacement／ZIP authority を含む                               | Reviewer scope drift                 |
| S02-PROMPT-003 | Planner／Reviewer role                                                                    | inspect invocation                                | fixed `-p` text と repeated `--file` のみ。dynamic context は file data 内                                          | operator text の argv option 化        |
| S02-PROMPT-004 | transport success                                                                        | inspect internal result and public failure mapper | source evidence に repository／branch／upstream／local／remote HEAD。origin raw URLなし                               | result から source trace 消失            |

### 5.3 Security and direct argv

| ID          | Fixture setup                                                                               | Operation                      | Expected observable result                                                                         | Regression caught                    |
| ----------- | ------------------------------------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------------------------- | ------------------------------------ |
| S02-SEC-001 | operator context に `token=abc123secret`、`sk-...`、GitHub token                               | invocation                     | `rejected/sensitive_input_rejected`、backend count `0`、secret value が result／log／pytest message にない | secret送信                             |
| S02-SEC-002 | relevant source content に structured credential                                             | invocation                     | backend count `0`、content-free finding                                                             | source secret送信                      |
| S02-SEC-003 | operator context に `/Users/alice/private/file`、`/private/...`、`/var/folders/...`、`/tmp/...` | parameterized invocation       | reject または diagnostic-only redaction、backend count `0`                                             | host-private path送信                  |
| S02-SEC-004 | approved static Prompt 内に一般語として “token”／“secret” が存在する                                      | synthesis                      | false positive なし                                                                                  | marker-only overblocking             |
| S02-SEC-005 | operator text に `$(touch sentinel)`、`; touch sentinel`、backticks、pipe、redirect              | fake wrapper invocation        | sentinel 不在。captured argv は list。metacharacter は attached file data のまま                            | shell injection                      |
| S02-SEC-006 | fake subprocess spy                                                                         | invocation                     | `shell` parameter absent、`cwd == verified repo_root`、argv[0] が fixed wrapper                       | shell execution、wrong repo inference |
| S02-SEC-007 | wrapper absolute path と temp pack path                                                      | serialized BackendInvokeResult | path は `[redacted]`、raw absolute pathなし                                                            | diagnostic path leak                 |

### 5.4 Backend/output classification

| ID         | Fixture setup                                                    | Operation                  | Expected observable result                                     | Regression caught                       |
| ---------- | ---------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------- | --------------------------------------- |
| S02-BE-001 | fixed wrapper path missing                                       | invocation                 | `blocked/backend_unavailable`、source evidenceあり                | missing executable traceback            |
| S02-BE-002 | fake runner raises `TimeoutExpired` with partial stdout/stderr   | invocation                 | `blocked/backend_timeout`、raw streamsなし                        | timeout transcript leak                 |
| S02-BE-003 | fake wrapper exits `7`                                           | invocation                 | `blocked/backend_nonzero`、exit_code=`7`、stderr本文なし             | nonzeroのpass化                           |
| S02-BE-004 | exit `0`、stdout empty                                            | invocation                 | `blocked/backend_output_missing`                               | exit codeだけで成功扱い                        |
| S02-BE-005 | matching start marker、end markerなし                               | invocation                 | `blocked/backend_response_partial`                             | truncated response acceptance           |
| S02-BE-006 | matching markers、empty body                                      | invocation                 | `blocked/backend_response_partial`                             | empty response acceptance               |
| S02-BE-007 | duplicate markers／wrong role／wrong HEAD／frame外text／invalid UTF-8 | parameterized invocation   | `rejected/backend_response_malformed`                          | cross-run response、ambiguous parsing    |
| S02-BE-008 | exact frame と non-empty body                                     | invocation                 | `pass/transport_received`、payload SHA、payload は memory only    | transport positive                      |
| S02-BE-009 | complete response body に secret-like string                      | post-receive scan          | S02 transport resultは rejected、payload／secretは diagnosticsに出ない | generated secret persistence            |
| S02-BE-010 | timeout／nonzero／malformed result を serialize                     | `to_dict()` と summary read | stable status/reason/byte counts/source evidenceのみ             | raw transcript／private path persistence |

### 5.5 Regression

| ID          | Fixture setup                               | Operation                                               | Expected observable result                                                 | Regression caught                   |
| ----------- | ------------------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- | ----------------------------------- |
| S02-REG-001 | existing generic authoring backend fixtures | existing `invoke_backend` tests                         | CLI/env/fallback resolution、dry-run、summary shape が不変                      | shared backend contract break       |
| S02-REG-002 | S01 CLI                                     | top-level／four subcommand help and invalid option tests | command family、arguments、text/JSON semantics が不変。backend override optionなし | S01 public surface drift            |
| S02-REG-003 | S01 domain/application/presentation suites  | focused pytest                                          | all Green                                                                  | identity／result contract regression |
| S02-REG-004 | Core CLI shell suite                        | Core CLI regression                                     | `spec-dock` command behaviorが不変                                            | Core CLI contamination              |
| S02-REG-005 | repository diff inspection                  | `git diff --name-only`                                  | section 3 write allowlist以外 `0`                                            | S03/S06/projection scope creep      |

---

## 6. Implementation sequence

1. **Exact source guard**

   * 作業開始時に branch、HEAD、status を記録する。
   * HEAD が `c597bd146c1d68e619cdc1e24b1b76dd405fe36a` でない場合は実装を開始しない。
   * write allowlist 外の既存変更がある場合は停止する。

2. **Red tests**

   * S02-GIT、CTX、PROMPT、SEC、BE の tests を先に追加する。
   * 最初の実行で、実装欠落による expected failures を記録する。
   * syntax error、import errorだけを Red evidence として済ませない。
   * 各 failure が意図した missing behavior に到達していることを確認する。

3. **Source evidence contract**

   * `PlanningSourceEvidence` と internal `PlanningInvocationResult` を追加する。
   * SHA、repository slug、branch、upstream を closed validation する。
   * transient payload は serialization／repr から除外する。
   * `PlanningCommandResult` の success pair は変更しない。

4. **Git preflight composition**

   * `resolve_existing_issue_target` を先に実行する。
   * explicit context paths を決定する。
   * `run_github_sync_preflight` を `allow_default_branch_fallback=False` で呼ぶ。
   * pass 後に exact upstream postconditions と `origin_github_repo_slug` を確認する。
   * preflight／GitHub slug failure は backend call 前に content-free result へ変換する。
   * exception text を details へ入れない。

5. **Bounded PlanningContext**

   * direct dependencies は既存 topology reader から取得する。
   * relevant paths は内部入力の explicit filesだけを処理する。
   * count／bytes／path／UTF-8／symlink／credential limits を適用する。
   * operator context に同じ security／size bounds を適用する。
   * auto-discovery と silent truncation を禁止する。

6. **Provider Prompt resources**

   * Planner、Reviewer、common transport contract の3 resourcesを追加する。
   * role、scope、non-goals、authority、source identity、output framing を固定する。
   * repository source本文を instructionではなく data と扱う旨を固定する。
   * Candidate／Review semantic schema を S02 で解析しない。

7. **Prompt synthesis**

   * Pure function として deterministic Prompt bytes を生成する。
   * dynamic block を stable heading／JSON order／UTF-8 order で出力する。
   * invocation 前に全 dynamic values と included file bodies を scan する。
   * finding時は Prompt packを作らず backend count `0` とする。

8. **Shared backend minimum extension**

   * existing backend executionを一つの internal coreへ抽出する。
   * existing `invoke_backend()` は同じ return type／serialized behavior を維持する。
   * S02だけが使う transient capture entrypoint を追加する。
   * optional `working_dir` は default `None` とし、existing callersを変えない。
   * `subprocess.run` の direct argv、timeout、capture、error mapping は既存実装を維持する。

9. **Fixed ChatGPT adapter**

   * fixed wrapper pathを private constant とする。
   * `BackendInvokeRequest.backend_command` へ内部的にのみ設定する。
   * env fallback、CLI override、operator overrideを読まない。
   * verified repository root を cwd とする。
   * repository外 temporary directory に S02 transport packを作る。
   * 既存 `invoke_backend` validationを通す。
   * finally で temporary context filesを削除する。

10. **Response transport classification**

    * exact role／HEAD-bound framing を検証する。
    * missing／partial／malformedを分離する。
    * payloadを S03／S04向け in-memory value と SHA にする。
    * raw response、stderr、wrapper logを永続化しない。
    * response受領後も sensitive-content scan を行う。

11. **Application result mapping**

    * Git／context／security／backend failure を stable reasonへ変換する。
    * source evidenceを取得済みの failureでは `output.source_identity` に保持する。
    * transport success を public lifecycle successへ変換しない。

12. **Focused Green and regressions**

    * 新規 tests を Green。
    * shared backend regressions。
    * S01 focused suites。
    * Core CLI shell regression。
    * diff allowlist／secret scan／private path scan。
    * installer／projection／build／dogfood は実行しない。

---

## 7. Verification commands

### 7.1 Start-state evidence

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git rev-parse --abbrev-ref --symbolic-full-name '@{u}'
```

期待値:

```text
branch = iss-00334-implement-chatgpt-issue-planning-workflow
HEAD = c597bd146c1d68e619cdc1e24b1b76dd405fe36a
```

### 7.2 Red evidence

Tests 作成後、実装前に実行する。

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

報告には次を記載する。

* collected count。
* failed count。
* exact failing test node IDs。
* 各 failure が示す未実装 behavior。
* unexpected error／collection error の有無。

### 7.3 Focused Green

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

### 7.4 S01 regression

```bash
uv run pytest -q \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py
```

### 7.5 Shared backend/preflight regression

```bash
uv run pytest -q tests/cli_runtime/test_authoring.py -k 'backend or preflight'
```

```bash
uv run pytest -q \
  tests/unit/authoring_pack/test_github_fetch_policy.py \
  tests/unit/authoring_pack/test_preflight_receipt_writer.py
```

### 7.6 Core CLI regression

```bash
uv run pytest -q tests/cli_runtime/test_runtime_shell_s11.py
```

### 7.7 Static and repository checks

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/authoring_pack/test_backend_invoke_capture.py \
  tests/integration/test_issue_planning_chatgpt_transport.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
```

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
git status --short
git diff --name-only
```

### 7.8 Explicit non-runs

S02 subagent は次を実行しない。

```text
uv build
full uv run pytest
fresh init/update parity
dogfood projection update
live ChatGPT dogfood
planning apply
git commit
git push
```

Main が追加 regression を指示した場合だけ、full suite を別証跡として実行する。

---

## 8. Forbidden changes

* `spec-dock/` 配下の dogfood runtime、canonical planning docs、report、artifacts。
* root `.agents/`、root `.codex/`、installed projection。
* `requirement.md`、`design.md`、`plan.md`。
* `.assurance.json`。
* `report.md`。
* `cli/bootstrap.py` の planning use case wiring。
* `application/contracts.py` の planning success behavior。
* `commands/issue_planning.py`、parser、registry、presentation の public surface。
* `spec-dock-chatgpt` に backend、Prompt、repository、branch、HEAD、target、source path optionを追加すること。
* default branch fallback。
* local-context fallback。
* manual GitHub API／`gh api`／REST／GraphQL fallback。
* agent-owned second `git fetch` path。
* generic workflow engine。
* backend registry、plugin registry、provider registry。
* public backend command／environment override。
* shell command string、`shell=True`、pipe、redirect、heredoc、command substitution。
* credential transport。
* arbitrary file／directory recursion。
* source pathのsilent truncation。
* Candidate ZIP、Candidate manifest、checksums、placeholder map。
* Review finding／verdict parsing。
* revision、Human decision、apply。
* canonical write、validation orchestration、commit、push。
* raw stdout、stderr、transcript、response payload の persistence。
* secret value、credential、remote URL、host-private absolute path の result／exception／test report への出力。
* S02 transport success を `candidate_created`、`candidate_revised`、`review_completed`、`adoption_published` として返すこと。
* unrelated refactor、rename、format-only churn。

---

## 9. Stop conditions

次のいずれかが成立したら、scope を拡張せず停止して Main へ返す。

1. 作業開始時の branch／HEAD が指定値と一致しない。
2. write allowlist 外に既存変更がある。
3. current branch または upstream を安全に特定できない。
4. `run_github_sync_preflight` を使わずにしか要求を満たせない。
5. non-GitHub 判定のために generic Git/GitHub preflight の全面改修が必要になる。
6. existing backend execution coreを再利用できず、第二の subprocess framework が必要になる。
7. fixed wrapper が model responseを stdout または現行 ABIで観測可能な channelへ返さず、wrapper変更やbrowser automation変更が必要になる。
8. response completion判定に requirement／design／plan または Review finding の意味解析が必要になる。
9. Prompt resourcesを利用可能にするため、S06 installer／projection変更が必要になる。
10. public CLI optionまたは bootstrap wiringが必要になる。
11. relevant sourceを得るため、repository-wide discovery、arbitrary target、directory recursionが必要になる。
12. dependency contextを得るため、shared dependency graph semanticsの変更が必要になる。
13. secret／private pathを除去すると context の意味を安全に維持できない。redactして継続せず blockする。
14. generic `invoke_backend` の existing CLI/env/fallback contractを破壊しないと transient captureを追加できない。
15. Red tests が intended missing behaviorではなく、既存 S01 defect／unrelated failureを示す。
16. Prompt resource pathに既存の同責務 fileがあり、置換／merge判断が必要になる。
17. Candidate、Review semantics、revision、Human Gate、apply、installer、dogfoodへ変更が波及する。
18. stable diagnosticを作るために raw exception／remote URL／stream本文を保持する必要が生じる。

停止時は、変更済み files、Red evidence、必要になった境界、scope owner、再開条件を報告し、代替実装へ進まない。

---

## 10. Subagent instruction

```text
Repository chemitaro/spec-dock の branch
iss-00334-implement-chatgpt-issue-planning-workflow、
開始 HEAD c597bd146c1d68e619cdc1e24b1b76dd405fe36a に対して、
iss-00334 の S02 — Git Context and ChatGPT Invocation だけを実装せよ。

開始時に branch、HEAD、git status を確認し、HEAD 不一致または allowlist 外の既存変更があれば停止せよ。

実装範囲は次だけとする。

1. existing run_github_sync_preflight を使用して current named branch、upstream、
   local HEAD、remote branch HEAD、clean worktree/index、fetch success、remote parity を検証する。
2. existing origin_github_repo_slug を使用して origin fetch/push が同一 GitHub owner/repo であることを確認する。
3. existing Issue resolver、parents、direct dependencies、canonical three paths、
   explicit relevant source paths、operator context から bounded PlanningContext を構築する。
4. provider-owned Planner、Reviewer、transport-output Prompt resourcesを合成する。
5. fixed wrapper
   /Users/iwasawayuuta/.agents/skills/chatgpt-use/scripts/oracle-chatgpt
   を existing invoke_backend / BackendInvokeRequest 経由の direct argv で起動する。
6. verified repository root を process cwd とし、wrapper の current repository inference を使う。
7. backend unavailable、timeout、nonzero、missing output、partial response、
   malformed response を stable status/reason に分類する。
8. dynamic Prompt、included source、operator context、backend responseを
   secret／credential／private absolute-path scannerへ通す。
9. raw stdout、stderr、transcript、response payload、secret value、
   remote URL、host-private absolute pathを永続化またはdiagnosticへ返さない。
10. repository、branch、upstream、local HEAD、remote HEAD、
    source manifest hash、snapshot IDをsource identity evidenceとして保持する。
11. S02 transport successをCandidate／Review lifecycle successへ変換しない。

write allowlist は次だけである。

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/backend_invoke_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/planner-prompt.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/reviewer-prompt.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/resources/transport-output-contract.md
- tests/unit/application/test_issue_planning.py
- tests/unit/application/test_issue_planning_prompt.py
- tests/unit/domain/test_issue_planning_contracts.py
- tests/unit/infra/test_issue_planning_chatgpt.py
- tests/unit/authoring_pack/test_backend_invoke_capture.py
- tests/integration/test_issue_planning_chatgpt_transport.py
- tests/cli_runtime/test_chatgpt_cli.py

allowlist 外を変更するな。特に root spec-dock/、root .agents/、report.md、
.assurance.json、canonical planning docs、bootstrap、public CLI、installer、
projection、Candidate packaging、Review parsing、revision、apply、commit、pushを変更するな。

Red-firstで実装せよ。最初に次を網羅する failing testsを追加し、
実装前の exact failing test IDs と failure summaryを記録せよ。

- clean synced GitHub branch positive
- dirty tracked worktree、staged index、untracked files
- detached HEAD
- missing upstream
- current branch/upstream branch mismatch
- non-GitHub upstream
- GitHub fetch/push repository mismatch
- fetch failure
- ahead、behind、diverged、remote mismatch
- concurrent repository/source change
- exact repository/branch/HEAD transport and source evidence
- canonical Issue、parents、direct dependencies
- bounded relevant source and operator context
- secret-bearing content
- private absolute paths
- shell metacharacters remaining inert
- fixed direct argv and verified cwd
- wrapper missing
- timeout
- nonzero exit
- missing output
- partial output
- malformed output
- complete framed output
- diagnostic non-leakage
- generic backend regression
- S01 CLI/domain/application/presentation regression
- Core spec-dock CLI regression

existing invoke_backend の subprocess pathを複製するな。
一つの internal execution coreから、既存 invoke_backend と
S02 transient-capture entrypointを提供せよ。
既存 invoke_backend の public return type、summary JSON、CLI/env/fallback behaviorを維持せよ。

response framingは次をexact contractとせよ。

<<<SPECDOCK-ISSUE-PLANNING-RESPONSE-V1 role=<planner|reviewer> source_head=<40-hex>>>
<payload>
<<<END-SPECDOCK-ISSUE-PLANNING-RESPONSE-V1>>>

S02ではframe、role、source HEAD、completion、non-empty payloadだけを検査し、
三文書、front matter、Review finding、severity、verdictを解析するな。

実装後、work packetのVerification commandsをnarrowest commandから実行せよ。
full suite、build、installer parity、dogfood、live ChatGPT、commit、pushは実行するな。

完了報告は必ず次の順序で返せ。

1. Changed files and responsibilities
   - 変更した全fileを列挙し、各fileの責務を一文で説明すること。

2. Exact Red evidence
   - tests作成後・実装前に実行したcommand。
   - collected / passed / failed / error counts。
   - exact failing test node IDs。
   - 各failureが証明した未実装behavior。
   - collection errorやsyntax errorをRed evidenceに含めていないこと。

3. Verification commands and exact results
   - 実行した全commandを順番どおり記載すること。
   - 各commandのexit code、passed/failed/skipped countsを正確に記載すること。
   - 実行しなかったcommandを実行済みと書かないこと。

4. Allowlist confirmation
   - git diff --name-only の全pathを列挙すること。
   - 全pathがwrite allowlist内であることを明示すること。
   - root spec-dock/、root .agents/、canonical docs、report.md、
     .assurance.json、bootstrap、public CLI、installer、projectionへの変更が0であること。

5. Unresolved risks
   - fixed wrapperの実環境ABI、stdout framing、Prompt projectionなど、
     hermetic testsだけでは未検証の事項を列挙すること。
   - 未検証事項をpassまたは完了と表現しないこと。

6. Ledger Note
   - approved planを超えるmaterial implementation decisionがあれば、
     decision、選択肢、理由、影響、後続ownerを詳細に記載すること。
   - material decisionがなければ、次の文を一字一句そのまま記載すること。

No material implementation decisions beyond the approved plan.

Candidate ZIP、Review semantics、revision、Human Gate、apply、canonical mutation、
validation orchestration、commit、push、projectionが必要になった時点で停止し、
scopeを拡張せずMainへ返せ。
```
