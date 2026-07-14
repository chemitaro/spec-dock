---
種別: research
ID: "20260713t014710z-research"
タイトル: "ChatGPT Pro GitHub Sync Preflight Reliability Analysis"
状態: "completed"
作成者: "Codex and ChatGPT Pro"
最終更新: "2026-07-13"
親: ["iss-00314"]
関連:
  - "https://github.com/chemitaro/spec-dock/issues/314"
  - "https://github.com/chemitaro/taikyohiyou_project/issues/2098"
authority: "synthesized"
derived_from:
  - "ChatGPT Pro browser session: specdock-issue-314-preflight-reliabilit"
  - "provider-side runtime, CLI, domain contract, docs, installed skill, Epic requirement, and tests"
reflected_to: []
---

# SpecDock Issue #314 — GitHub sync preflight の信頼性・receipt 契約分析

## このartifactの読み方

この文書は、GitHub Issue [chemitaro/spec-dock#314](https://github.com/chemitaro/spec-dock/issues/314) の修正方針を検討するため、ChatGPT Proへ現行コード・関連仕様・テスト・元インシデント [chemitaro/taikyohiyou_project#2098](https://github.com/chemitaro/taikyohiyou_project/issues/2098) を渡して得た分析結果を、回答の構造を保ったまま保存したresearch evidenceである。

- 実行モデル: ChatGPT Pro（browserで選択確認済み）
- 実行時間: 28分22秒
- 入力規模: 約127.39k tokens、添付10ファイル
- 出力規模: 約15.11k tokens
- ChatGPT conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a5443fc-0118-83ee-9e4d-6815ce357ac5
- authority: `synthesized`。このartifact単体はcanonical requirement/design/planではなく、採否判断前の分析証拠である。

### 先に読むべき結論

ChatGPT Proは、最初のPRの合格ラインを次のように要約している。

> 原因を完璧に言い当てるclassifierではなく、原因不明でも権限・shell shapeを変えず、安全にretryまたはblockし、その判断材料をdurable receiptとして残せること。

推奨の中心は、`github-synced` preflightを以下の一つのSpecDock-owned transactionとして扱うことである。

```text
固定 fetch
  -> bounded same-capability retry
  -> fetch後の一貫したrepository/source snapshot
  -> concurrent-change再確認
  -> typed blocked/pass receipt
  -> 安全なatomic publication
```

### Codexによる照合メモ

以下はローカルprovider側ソースと照合済みである。

- `_refresh_origin()` は固定argvで `git fetch --prune origin` を実行する。
- fetchのnonzeroは公開resultでは `origin_fetch_failed` 一種類へ集約され、取得したdiagnostic文字列は保持されない。
- preflight CLIには現時点で `--output-dir` / `--report-path` がない。
- source manifest、worktree、branch、local HEADの一部はfetch前に取得され、remote-tracking observationはfetch後に行われる。
- `pack prepare` はreceipt内部の整合を検査するが、現在のrepository stateとの完全な再照合は行わない。
- provider-side assetが実装上の正本であり、dogfooding projectionだけを直接修正してはならない。

以下は提案または未確定事項であり、canonical docsへ採用する前にmaintainer判断と実装検証が必要である。

- retry対象class、attempts=2、timeout=60秒、250ms+jitterなどの具体値。
- `--output-dir`のみを公開し、固定filenameを `github-sync-preflight.receipt.json` とする判断。
- failure taxonomy、receipt data shape、diagnostic excerpt上限、legacy schema移行期間。
- 最初のPRへpack stale validationまで含めるか、直後のsmall PRへ分けるか。
- ChatGPT回答中の「添付のExceptionBase / FailureResult taxonomy」という言及は、今回明示的に選んだ添付セットからは確認できないため、Issue #314の根拠として採用しない。

---

## ChatGPTへの依頼

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a5443fc-0118-83ee-9e4d-6815ce357ac5

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt as the complete task brief. Inspect all attached repository evidence and provide the requested Japanese architecture and implementation analysis. Do not produce a patch.

---

## ChatGPT Proの分析回答（原文）

# SpecDock Issue #314 — GitHub sync preflight の信頼性・receipt 契約分析

## 調査基準と証拠区分

GitHub connector で指定ブランチ `iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract` を先に検索・直接参照しましたが、その ref は GitHub 上に存在しませんでした。そのため、指定どおり既定ブランチ `main` を調査基準に切り替えました。確認時点の `main` は commit `081ba64823f66d4efb051fb88e2a160915efdfa0` です。

GitHub Issue #314 は open ですが、GitHub 側の本文はローカル specs を参照する最小限の内容です。 したがって本レポートでは、次の順で証拠を扱います。

1. **確認済みリポジトリ事実**: GitHub connector で読んだ `main` のコード、契約、docs、skill、tests。
2. **確認済み incident 事実**: 公開 Issue `taikyohiyou_project#2098`。
3. **補助証拠**: 添付された task brief と current-branch 相当の bundle。
4. **提案**: 以下のアーキテクチャ、スコープ、data shape、受け入れ条件。Codex 側での独立検証対象です。

添付の「設計判断と提案」は `ExceptionBase` / `FailureResult` taxonomy に関する別テーマであり、Issue #314 の実装根拠には採用していません。証拠の混入を避けるため明示します。

---

## 1. エグゼクティブサマリー

### 結論

最善の修正は、`git fetch` の単発エラー処理だけを増補することではなく、`github-synced` preflight を次の一つの **SpecDock-owned reliable preflight transaction** として成立させることです。

```text
固定 fetch
  -> bounded same-capability retry
  -> fetch 後の一貫した repository/source snapshot
  -> concurrent-change 再確認
  -> typed blocked/pass receipt
  -> 安全な atomic publication
```

最初の PR には、少なくとも次を一つの閉じたスコープとして含めるべきです。

| 優先度        | 最初の PR に含める内容                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------------ |
| **MUST**   | `git fetch --prune origin` を維持し、固定 argv・`shell=False`・timeout・非対話化を明示契約にする                       |
| **MUST**   | fetch outcome、failure class、attempt、duration、exit code、bounded/redacted diagnostic を receipt に残す |
| **MUST**   | retryable と高信頼に判定できた失敗だけ、同一 capability shape で最大 1 回 retry する                                    |
| **MUST**   | `--output-dir` と固定 filename を追加し、blocked receipt も atomic に保存する                                  |
| **MUST**   | worktree、HEAD、upstream、remote-tracking HEAD、source manifest を fetch 後に観測する                       |
| **MUST**   | receipt 公開直前に critical fingerprint を再確認し、変化時は `concurrent_repo_change` で fail-closed にする         |
| **MUST**   | skill/docs に「fetch 非ゼロは権限不足の証拠ではない」「shell syntax と権限昇格を追加しない」を明記する                               |
| **SHOULD** | `pack prepare` で receipt の local HEAD・source hash・age を再検証し、古い receipt を拒否する                     |
| **LATER**  | backend invocation 直前の最終 fetch、または preflight→prepare→invoke の単一 orchestration                    |
| **LATER**  | immutable launcher、Git Trace2、強化された POSIX `dir_fd/openat` writer、全 authoring writer の共通化         |

推奨 output API は、最初の PR では **`--output-dir` のみ**です。

```bash
./spec-dock/scripts/spec-dock authoring preflight github-sync \
  --repo-root . \
  --source-path path/to/source \
  --format json \
  --output-dir /approved/temp/specdock-preflight-run
```

固定出力名:

```text
github-sync-preflight.receipt.json
```

`--report-path` より `--output-dir` を優先する理由は、任意 basename、親 traversal、拡張子、canonical filename への書き込みという入力面を減らせるためです。既存の `review` / `validate` が `--report-path` を使うことは事実ですが、その writer は直接 `Path.write_text()` しており、今回必要な atomic receipt 契約をそのまま満たしてはいません。

---

## 2. 問題の再定義と因果関係

### 2.1 直接的な因果関係

Incident の因果関係は次です。

```text
preflight 内部 fetch が非ゼロ
  ↓
result には origin_fetch_failed しか残らない
  ↓
timeout / DNS / auth / lock / config / policy を区別できない
  ↓
SpecDock-owned retry 契約もない
  ↓
agent が sandbox/network restriction と推測
  ↓
preflight 全体に require_escalated を追加
  ↓
JSON 保存のため shell redirect も追加
  ↓
既存の direct command prefix と異なる command shape になる
  ↓
不要なユーザー承認
```

Incident では、一度は preflight が pass し、local/remote SHA が一致しました。その後、redirect 付きの実行で `origin_fetch_failed` となり、明示的な raw `git fetch` は成功した一方、後続の preflight 内部 fetch は再び失敗しました。保存された receipt に stderr と failure classification がないため、実際の原因は事後確定不能です。

### 2.2 主因ではないもの

Epic directory 全体を `--source-path` に渡した際、配下の `rules.md` symlink が拒否されたことは、期待された fail-closed behavior です。現行の source validation は、直接 symlink、ancestor symlink、repo 外 absolute path、parent traversal を blocker にします。

したがって、これを回避するため source validation を緩めるべきではありません。

### 2.3 問題の本質

本質は「fetch が失敗した」こと自体ではなく、次の三つの契約欠落です。

1. **実行契約の欠落**
   timeout、非対話化、retry budget、cancellation、環境 policy が明示されていない。

2. **診断契約の欠落**
   operation outcome が一種類の blocker に圧縮され、なぜ失敗したかを安全に残せない。

3. **artifact 契約の欠落**
   receipt を shell なしで永続化する API と、安全な publication semantics がない。

さらに、preflight receipt と pack/backend の間に binding がなく、pass receipt が作成直後から陳腐化し得るという第四の問題があります。

---

## 3. 現行実装・契約の評価

### 3.1 維持すべき良い点

現行 `_refresh_origin()` は次の重要な性質を既に持っています。

* executable と argv が固定されている。
* shell wrapper を使わない。
* `capture_output=True`。
* `check=False` で outcome を明示的に評価する。
* `github-synced` mode で fetch を省略しない。

この責務は SpecDock 内に維持すべきです。agent-owned raw `git fetch` を標準経路にすると、対象 repository、remote、refspec、permission shape、receipt との binding が分断されます。

### 3.2 現行の主要な欠陥

| 項目                 | 確認済み現状                                               | 問題                                          |
| ------------------ | ---------------------------------------------------- | ------------------------------------------- |
| Fetch diagnostics  | `_refresh_origin()` は stderr または stdout を返す          | caller が文字列を破棄し、`origin_fetch_failed` のみにする |
| Observation order  | source manifest、worktree、branch、local HEAD は fetch 前 | remote observation と異なる時点の snapshot になり得る   |
| Timeout            | なし                                                   | helper、network、credential flow が無期限に近く停止し得る |
| Prompt suppression | なし                                                   | terminal/credential interaction の扱いが暗黙      |
| Retry              | なし                                                   | agent 側の推測と command 再構築を誘発する                |
| Receipt schema     | schema version なし                                    | additive change と breaking change を判別できない   |
| Output API         | `--format` のみ                                        | redirect、pipe、`tee` を誘発する                   |
| Persistence        | stdout のみ                                            | blocked result を安全な durable evidence にできない  |
| Freshness binding  | pack/backend で current repo を再観測しない                  | pass receipt の TOCTOU                       |
| Remote observation | default observer は `refs/remotes/origin/*`           | docs の「connector-visible」と意味がずれる            |

現行処理では、source manifest と local state を先に取得し、その後 fetch します。 upstream と remote-tracking ref の観測は fetch 後です。

このため、たとえば fetch 中に別 process が checkout、commit、source edit を行うと、一つの result に複数時点の値が混在します。

### 3.3 Receipt contract の不足

現在の `PreflightResult` は、status、mode、sync state、refs、heads、source manifest、blockers、remediation を持ちますが、以下を持ちません。

* `schema_version`
* receipt kind
* observed time
* fetch attempt
* timeout
* return code
* termination kind
* failure class
* retry disposition
* diagnostic digest
* repository identity
* snapshot ID
* receipt digest
* observation source
* concurrent-change guard result。

### 3.4 CLI / presentation の不足

Preflight CLI args に output destination はなく、`--format`、repo、ref、source/context parameters のみです。 Command handler は result を renderer に渡して stdout に出すだけです。

JSON renderer も `result.to_dict()` の単純な dump であり、artifact publication の責務は持ちません。

### 3.5 既存 writer の評価

既存 authoring commands には、canonical docs、`.assurance.json`、symlink ancestor を拒否する path check があります。これは再利用すべき知見です。

ただし publication 自体は次の形式です。

```python
report_path.write_text(...)
```

または:

```python
(output_dir / SUMMARY_FILENAME).write_text(...)
```

であり、same-directory temporary file、fsync、atomic replace、existing target ownership の契約はありません。

### 3.6 Downstream freshness の不足

`pack prepare` は preflight JSON の required fields と source hash の内部整合性を検査しますが、現在の worktree、HEAD、remote-tracking ref、source files を読み直しません。

`stale-if.json` には heads と source hash が書かれますが、backend validation はその object の存在・形を確認するだけで、current repository と比較しません。

### 3.7 契約 drift

Epic design は GitHub connector-visible branch/head を preflight observation として列挙しています。 一方、CLI default observer は local の `refs/remotes/origin/<ref>` を読む実装です。

これは最初の PR で connector integration まで追加すべきという意味ではありません。しかし receipt では observation source を正直に、

```text
fetched_remote_tracking_ref
```

と記録すべきです。「GitHub connector による直接確認」と誤認させてはいけません。

---

## 4. 推奨アーキテクチャと責務配置

Epic design は、commands、application、domain、infra、presentation の分離と、provider-side assets を source of truth とする方針を既に定めています。 Issue #314 もこの分離に従うべきです。

### 4.1 責務配置

| Layer                         | 推奨責務                                                                                                |
| ----------------------------- | --------------------------------------------------------------------------------------------------- |
| `domain/authoring_pack`       | enum、immutable attempt/result/receipt、snapshot identity、schema validation                           |
| `application/authoring_pack`  | preflight orchestration、failure classification policy、retry policy、sync evaluation、stale validation |
| `infra/authoring_pack`        | subprocess adapter、Git observation adapter、安全な JSON writer、OS clock/sleeper                         |
| `commands/authoring.py`       | CLI flags、destination の構築、dependency wiring、exit code                                               |
| `presentation/authoring_pack` | text/JSON rendering。raw stderr の処理や file I/O はしない                                                   |
| installed skill / docs        | agent operation policy、禁止事項、operator remediation                                                    |
| `spec-dock/` projection       | provider asset から生成・同期される dogfood consumer surface                                                  |

### 4.2 推奨 port

```python
class GitFetchPort(Protocol):
    def fetch(self, request: GitFetchRequest) -> GitProcessOutcome: ...

class RepositorySnapshotPort(Protocol):
    def capture_identity(self, repo_root: Path) -> RepositoryIdentity: ...
    def capture_snapshot(
        self,
        repo_root: Path,
        source_paths: tuple[str, ...],
        requested_ref: str | None,
    ) -> RepositorySnapshot: ...
    def capture_guard(self, repo_root: Path, source_paths: tuple[str, ...]) -> SnapshotGuard: ...

class ReceiptWriterPort(Protocol):
    def publish(
        self,
        output_root: Path,
        filename: str,
        payload: bytes,
    ) -> PublicationResult: ...

class Clock(Protocol):
    def monotonic(self) -> float: ...
    def utc_now(self) -> datetime: ...

class Sleeper(Protocol):
    def sleep(self, seconds: float) -> None: ...
```

Clock、sleeper、classifier を injection 可能にすることで、retry/backoff tests を実時間や network に依存させずに済みます。

### 4.3 推奨 domain shape

```python
class FetchFailureClass(str, Enum):
    TIMEOUT = "timeout"
    TRANSIENT_TRANSPORT = "transient_transport"
    REMOTE_THROTTLED = "remote_throttled"
    LOCAL_REF_LOCK_CONTENTION = "local_ref_lock_contention"
    REMOTE_ACCESS_DENIED_OR_NOT_FOUND = "remote_access_denied_or_not_found"
    HOST_IDENTITY_FAILURE = "host_identity_failure"
    REPOSITORY_CONFIGURATION = "repository_configuration"
    EXECUTION_OR_FILESYSTEM_DENIED = "execution_or_filesystem_denied"
    SPAWN_FAILURE = "spawn_failure"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class TerminationKind(str, Enum):
    EXITED = "exited"
    TIMEOUT = "timeout"
    SPAWN_ERROR = "spawn_error"
    CANCELLED = "cancelled"


class ClassificationConfidence(str, Enum):
    CERTAIN = "certain"
    PROBABLE = "probable"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GitProcessOutcome:
    return_code: int | None
    termination: TerminationKind
    stdout: bytes
    stderr: bytes
    duration_ms: int
    os_error_kind: str | None = None


@dataclass(frozen=True)
class FetchAttempt:
    attempt_number: int
    started_at: str
    duration_ms: int
    return_code: int | None
    termination: TerminationKind
    failure_class: FetchFailureClass | None
    confidence: ClassificationConfidence
    retryable: bool
    diagnostic_code: str | None
    diagnostic_excerpt: str | None
    diagnostic_sha256: str | None
    diagnostic_bytes: int
    diagnostic_truncated: bool


@dataclass(frozen=True)
class FetchSummary:
    status: Literal["success", "failed", "cancelled"]
    remote: Literal["origin"]
    executable: str
    argv: tuple[str, ...]
    timeout_seconds: float
    policy_id: str
    attempts: tuple[FetchAttempt, ...]


@dataclass(frozen=True)
class RepositorySnapshot:
    repository_identity: str
    branch: str | None
    local_head: str | None
    upstream: str | None
    remote_tracking_head: str | None
    remote_observation_source: Literal["fetched_remote_tracking_ref"]
    worktree_status_digest: str
    source_manifest_hash: str
    snapshot_id: str
```

### 4.4 Application transaction

```python
def run_github_sync_preflight(request, deps):
    repo_root = resolve_repo_root(request.repo_root)
    destination = validate_output_destination(request.output_dir)

    static_findings = validate_static_paths_and_configuration(
        repo_root,
        request.source_paths,
    )

    pre_fetch_identity = deps.snapshot.capture_identity(repo_root)

    fetch_summary = run_fetch_with_policy(
        request=fixed_origin_fetch(repo_root),
        fetcher=deps.fetcher,
        classifier=deps.classifier,
        retry_policy=deps.retry_policy,
    )

    if fetch_summary.status != "success":
        result = blocked_fetch_receipt(
            static_findings=static_findings,
            fetch_summary=fetch_summary,
            remote_freshness="not_verified",
        )
        return publish_if_requested(result, destination)

    snapshot = deps.snapshot.capture_snapshot(
        repo_root,
        request.source_paths,
        request.ref,
    )

    result = evaluate_sync_contract(
        request,
        static_findings,
        fetch_summary,
        snapshot,
    )

    final_guard = deps.snapshot.capture_guard(
        repo_root,
        request.source_paths,
    )

    if final_guard.fingerprint != snapshot.snapshot_id:
        result = result.as_blocked(
            blocker="concurrent_repo_change",
            remediation="rerun preflight after repository activity has stopped",
        )

    return publish_if_requested(result, destination)
```

重要なのは、pre-fetch identity は最終 freshness evidence ではなく、fetch 中の branch/repository 変更を検出する guard としてのみ使うことです。

---

## 5. 推奨する最小修正スコープ（最初のPR）

### 5.1 MUST scope

#### A. Typed fetch execution

`_refresh_origin() -> str | None` を、typed `GitProcessOutcome` を返す adapter に置き換えます。

固定 command は維持します。

```text
git fetch --prune origin
```

retry 時も executable、argv、cwd、environment policy、timeout、output capture policy を一切変更しません。

#### B. Timeout と非対話化

推奨 default:

```text
max_attempts:       2   # 初回 + 1 retry
timeout_per_attempt: 60 seconds
backoff:            250 ms + 0–100 ms jitter
```

portable な最低契約として:

```text
GIT_TERMINAL_PROMPT=0
```

を設定します。

環境は全面 allowlist 化せず、既存 credential helper、`HOME`、`SSH_AUTH_SOCK`、proxy、CA settings を維持するため **inherited-but-sanitized** とします。

除去・上書き候補:

```text
GIT_TRACE
GIT_TRACE_PACKET
GIT_TRACE_CURL
GIT_CURL_VERBOSE
GIT_TRACE2
GIT_TRACE2_EVENT
GIT_TRACE2_PERF
```

full environment や environment digest は receipt に保存しません。保存するのは `environment_policy_id` のみです。

#### C. Conservative classification

OS-level outcome、timeout、preflight configuration check、bounded stderr signal を組み合わせます。

retry を許可するのは、高信頼に次と判定できた場合だけです。

```text
timeout
transient_transport
remote_throttled
local_ref_lock_contention
```

`unknown` は retry しません。

#### D. First-class output API

追加:

```text
--output-dir <directory>
```

固定 filename:

```text
github-sync-preflight.receipt.json
```

`--output-dir` を省略した場合は、従来どおり stdout のみです。

#### E. Atomic blocked/pass receipt

fetch が失敗しても、destination が安全なら blocked receipt を保存します。

publication が失敗した場合は、たとえ sync evaluation 自体が pass でも command 全体は nonzero とし、

```text
receipt_publication_failed
```

を返します。persisted evidence を要求された呼び出しで、保存できなかったのに pass としてはいけません。

#### F. Post-fetch snapshot と concurrent guard

次は fetch 成功後に収集します。

* branch
* local HEAD
* origin URL の sanitized identity
* upstream
* remote-tracking HEAD
* worktree status
* explicit source existence
* source manifest
* ahead/behind/diverged

公開直前に critical fingerprint を再取得し、変化があれば `concurrent_repo_change` にします。

#### G. Additive schema

現在の top-level keys は維持し、nested fields を追加します。既存の `origin_fetch_failed` blocker も互換性のため残します。

#### H. Immediate agent guidance

Installed skill と workflow docs を同じ PR で修正します。

### 5.2 最初の PR に入れないもの

| 対象外                                        | 理由                                                                        |
| ------------------------------------------ | ------------------------------------------------------------------------- |
| GitHub connector の本実装追加                    | fetch reliability bug と別の integration scope                               |
| `git ls-remote` への置換                       | remote-tracking refs の更新を行わず、mandatory fetch の代替にならない                     |
| 全 authoring writer の一括移行                   | blast radius が大きい。共通 writer の導入後に段階移行する                                   |
| `GIT_TRACE2_EVENT` parsing                 | semantic classification が保証されず、path/URL leakage と fixture complexity が増える |
| retry count/backoff/timeout の多数の CLI knobs | policy が agent に再委譲される。まず固定 policy で観測する                                  |
| global repository lock                     | user/editor/Git workflow を阻害し、deadlock と stale lock を増やす                  |
| backend invocation 直前の mandatory fetch     | end-to-end hardening phase で共有 adapter を再利用する                             |
| privileged immutable launcher              | permission architecture phase に分離する                                       |

### 5.3 Over-engineering を避ける線引き

最初の PR で必要なのは、詳細なエラー名を大量に増やすことではなく、次の三つの意思決定を安全に行えることです。

```text
retryする
retryしないでoperator remediationを返す
分類不能としてfail-closedする
```

分類 enum はこの decision を支える最小限に留めるべきです。

---

## 6. 段階的ハードニング案

| Phase                                        | 内容                                                                                                    | 完了条件                                                      |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Phase 0: 即時運用封じ込め**                        | skill/docs に direct argv、no redirect、no escalation、no implicit fallback を明記                           | agent が `origin_fetch_failed` から権限昇格へ進まない                 |
| **Phase 1: 最初の PR**                          | typed fetch、timeout、bounded retry、schema receipt、`--output-dir`、atomic writer、post-fetch snapshot     | incident の直接原因を閉じる                                        |
| **Phase 1.5: Receipt consumer binding**      | `pack prepare` で local HEAD/source hash/receipt age を再検証                                              | 古い local receipt を fail-closed                            |
| **Phase 2: End-to-end freshness**            | pack provenance に receipt digest/snapshot ID を bind。backend 直前に final fetch/check、または単一 orchestration | remote move を含め invocation 直前まで freshness を閉じる            |
| **Phase 3: Writer/platform hardening**       | POSIX `dir_fd/openat`、Windows semantics、全 report writer 共通化                                           | path race と publication semantics を共通保証                   |
| **Phase 4: Permission capability hardening** | immutable/digest-verified launcher、operator-managed policy identity                                   | mutable repo-local executable と広い prefix approval のリスクを低減 |
| **Phase 5: Classifier observability**        | real Git version fixture、必要なら Trace2 評価                                                               | false retry / false permanent classification の測定          |

Phase 1 完了時点で、「receipt publication 時の GitHub sync evidence」は大幅に改善します。ただし backend invocation 直前まで remote freshness を保証したとは主張できません。その保証は Phase 2 の受け入れ条件に分けるべきです。

---

## 7. Fetch failure taxonomy と retry decision table

### 7.1 Exit code、stderr、structured mechanism の評価

#### Git exit code

Git の非ゼロ exit code は、失敗したという事実には使えますが、原因分類には不足します。同じ broad exit code が network、authentication、repository、ref update、configuration で使われ得るためです。

**結論:** exit code 単独で retry 可否を決めない。

#### stderr pattern

stderr は、DNS、HTTP、SSH、credential helper、local ref lock などの有用な signal を含み得ます。一方で次に依存します。

* Git version
* OS
* locale
* transport
* SSH implementation
* credential helper
* hosting provider
* proxy

**結論:** allowlisted pattern を heuristic signal としてだけ使い、`confidence` を記録する。

#### Structured Git mechanism

通常の `git fetch` には、全 transport/provider に共通する machine-readable semantic failure class はありません。`GIT_TRACE2_EVENT` は execution event を提供できますが、根本原因 taxonomy を直接保証せず、URL、path、helper details を追加で収集するリスクがあります。

**結論:** first PR では採用しない。必要性を実測してから別 issue で評価する。

### 7.2 推奨 taxonomy

| Failure class                       | 判定可能性 | Retry | 最終挙動                                           | 注意                                                            |
| ----------------------------------- | ----: | ----: | ---------------------------------------------- | ------------------------------------------------------------- |
| `timeout`                           |     高 |   1 回 | budget exhausted 後 blocked                     | timeout は原因ではなく termination class                             |
| `transient_transport`               |     中 |   1 回 | blocked                                        | connection reset、temporary DNS、502/503/504 等の明確 signal のみ     |
| `remote_throttled`                  |     中 |   1 回 | blocked                                        | retry-after を Git が常に公開するとは限らない                               |
| `local_ref_lock_contention`         |   中～高 |   1 回 | blocked                                        | lock file を自動削除しない                                            |
| `remote_access_denied_or_not_found` |     中 |    なし | blocked、credential/repo visibility remediation | private repo では not-found と auth failure を安全に分離できない           |
| `host_identity_failure`             |     高 |    なし | blocked                                        | host key policy を自動変更しない                                      |
| `repository_configuration`          |     高 |    なし | blocked                                        | origin/refspec/repository configuration 修正                    |
| `execution_or_filesystem_denied`    |   低～高 |    なし | blocked                                        | `PermissionError` は強い signal。stderr の “permission denied” は曖昧 |
| `spawn_failure`                     |     高 |    なし | blocked                                        | executable missing、OS spawn error                             |
| `cancelled`                         |     高 |    なし | exit 130 相当                                    | user cancellation を retry しない                                 |
| `unknown`                           |     高 |    なし | blocked                                        | retryable と推測しない                                              |

### 7.3 Retry decision table

| 条件                                  | Decision                |         Backoff | Capability change |
| ----------------------------------- | ----------------------- | --------------: | ----------------- |
| Attempt 1 success                   | stop/pass               |              なし | なし                |
| Timeout                             | retry if budget remains | 250 ms + jitter | 禁止                |
| High-confidence transient transport | retry if budget remains | 250 ms + jitter | 禁止                |
| High-confidence throttling          | retry if budget remains | 500 ms + jitter | 禁止                |
| Ref lock contention                 | retry if budget remains |      100–250 ms | lock 削除禁止         |
| Auth/not-found/host-key/config      | no retry                |              なし | 禁止                |
| Policy/filesystem denial            | no retry                |              なし | 自動昇格禁止            |
| Unknown                             | no retry                |              なし | 禁止                |
| Cancellation                        | abort                   |              なし | 禁止                |

### 7.4 Retry invariant

全 attempt について、次の tuple が同一でなければなりません。

```text
(
  executable,
  argv,
  repository identity,
  cwd identity,
  remote,
  timeout policy,
  inherited/sanitized environment policy,
  permission/sandbox context,
  output policy
)
```

ただし external sandbox mode は SpecDock process から観測できない場合があります。その場合、receipt に推測値を書かず、

```json
{
  "execution_policy_context": "unreported"
}
```

とします。将来 host が structured policy ID を渡せる場合だけ記録します。

---

## 8. Receipt/output API と安全な書き込み契約

### 8.1 推奨 CLI

```text
--output-dir DIR
```

を optional に追加します。

出力は必ず:

```text
DIR/github-sync-preflight.receipt.json
```

です。

最初の PR では `--report-path` と併設しません。二つの destination semantics を同時導入すると、precedence、mutual exclusion、basename safety、migration tests が増えます。

### 8.2 Safe-root policy

`--output-dir` は単なる path ではなく、caller が SpecDock に委任する **directory capability root** として扱います。

推奨許可 root:

1. platform temp root の配下
2. repository 配下の明示的 evidence root、たとえば `.specdock-authoring/`
3. 将来の operator-configured evidence root

ただし `main` の root `.gitignore` には、確認範囲では `.specdock-authoring` が含まれていません。 したがって最初から repo-local directory を暗黙 default にすると、preflight 自身が untracked state を作る危険があります。

推奨は次です。

* persistence が必要な場合は `--output-dir` を明示必須にする。
* incident と同様の managed temporary directory を正規経路として許可する。
* repo-local root は明示指定された場合だけ許可する。
* 将来 repo-local default を設ける場合は、ignore/ownership 契約を同時に導入する。

### 8.3 Path defenses

writer は次を拒否します。

* lexical または resolved canonical roots:

  * `spec-dock/active`
  * `spec-dock/initiatives`
  * `spec-dock/system`
* `.assurance.json` を含む protected target
* parent traversal
* symlink leaf
* symlink ancestor
* broken symlink
* output root が file / device / socket / FIFO
* target が non-regular file
* existing target が SpecDock receipt ではない
* trusted root 外
* fixed filename から外れる任意 basename

既存 regular target を上書きできるのは、JSON を読み、次を確認できた場合だけとします。

```json
{
  "receipt_kind": "spec-dock.authoring.github-sync-preflight"
}
```

malformed existing target は `non_owned_existing_receipt_target` として拒否します。

### 8.4 Atomic publication

推奨 algorithm:

```text
1. output root と全 existing ancestor を lstat
2. canonical/protected/symlink/non-directory を拒否
3. output root を必要なら mode 0700 で作成
4. target ownership を検査
5. 同一 directory に random temporary file を O_CREAT|O_EXCL で作る
6. mode 0600
7. serialized bytes を全量 write
8. flush + fsync(temp)
9. target/ancestor を再検査
10. os.replace(temp, target)
11. 対応 platform では fsync(parent directory)
12. target が regular non-symlink であることを再確認
13. 失敗時は temp を best-effort cleanup
```

same-directory temporary file を使うことで、cross-filesystem rename を避けます。

POSIX の hostile concurrent parent replacement まで強く防ぐには `dir_fd/openat` が望ましいですが、Python/Windows portability を含めると first PR の範囲を超えやすいため、最初は pre/post lstat と same-directory replace を MUST、`dir_fd` hardening を SHOULD/LATER とするのが妥当です。

### 8.5 Blocked result persistence

次の結果も receipt に保存します。

* timeout exhausted
* authentication/configuration failure
* ref lock contention exhausted
* unknown fetch failure
* dirty/staged/untracked
* branch missing
* source hash mismatch
* concurrent repository change

例外は destination 自体が unsafe な場合です。その場合はそこに書かず、stdout に sanitized blocked result を返します。

### 8.6 推奨 schema

現在は schema version がないため、最初の明示 version は `1` とするのが自然です。現行 payload は `legacy_unversioned` として扱います。

```json
{
  "schema_version": 1,
  "receipt_kind": "spec-dock.authoring.github-sync-preflight",
  "status": "blocked",
  "evidence_mode": "github-synced",
  "sync_state": "blocked",
  "github_sync": "failed",

  "requested_ref": "feature/example",
  "effective_ref": "feature/example",
  "local_head": "0123456789abcdef",
  "remote_head": null,

  "source_manifest_hash": "sha256-value",
  "source_paths": ["path/to/source"],
  "source_hashes": {
    "path/to/source/file.py": "sha256-value"
  },

  "repository": {
    "remote": "origin",
    "origin_identity": "github.com/owner/repository",
    "origin_url_persisted": false,
    "git_dir_fingerprint": "sha256-value",
    "remote_observation_source": "fetched_remote_tracking_ref"
  },

  "fetch": {
    "status": "failed",
    "executable": "git",
    "argv": ["git", "fetch", "--prune", "origin"],
    "timeout_seconds": 60,
    "policy_id": "github-fetch-v1",
    "environment_policy_id": "inherit-sanitized-v1",
    "attempt_count": 2,
    "final_failure_class": "transient_transport",
    "classification_confidence": "probable",
    "attempts": [
      {
        "attempt_number": 1,
        "duration_ms": 1234,
        "termination": "exited",
        "return_code": 128,
        "failure_class": "transient_transport",
        "retryable": true,
        "diagnostic": {
          "code": "connection_reset",
          "excerpt": "fatal: unable to access [redacted-remote]: connection reset",
          "sha256": "sha256-of-original-stream",
          "byte_count": 482,
          "truncated": false
        }
      },
      {
        "attempt_number": 2,
        "duration_ms": 1198,
        "termination": "exited",
        "return_code": 128,
        "failure_class": "transient_transport",
        "retryable": false,
        "diagnostic": {
          "code": "connection_reset",
          "excerpt": "fatal: unable to access [redacted-remote]: connection reset",
          "sha256": "sha256-of-original-stream",
          "byte_count": 482,
          "truncated": false
        }
      }
    ]
  },

  "freshness": {
    "fetch_completed_at": "2026-07-13T02:00:00Z",
    "snapshot_observed_at": null,
    "snapshot_id": null,
    "remote_freshness": "not_verified",
    "concurrent_change_check": "not_applicable"
  },

  "blockers": ["origin_fetch_failed"],
  "remediation": [
    "network transport failed after bounded same-capability retry; inspect network and remote availability without changing command permissions"
  ],

  "authority": "evidence_only",
  "adoption_requires": "explicit_eal_disposition",
  "bundle_generation_not_promotion": true,

  "receipt_digest": {
    "algorithm": "sha256-canonical-json-v1",
    "value": "sha256-value"
  }
}
```

### 8.7 Diagnostic redaction contract

Raw stdout/stderr は durable receipt に保存しません。

保存可能なのは:

* original byte count
* SHA-256 digest
* bounded redacted excerpt
* classifier-generated diagnostic code
* truncation flag

推奨上限:

```text
1024 UTF-8 bytes per attempt
```

必須 redaction 対象:

* URL userinfo
* query strings
* `Authorization`
* token/password/api-key/secret/credential assignment
* GitHub、Slack、AWS 等の recognizable token
* credential helper output
* private key material
* `/Users/...`
* `/private/...`
* `/tmp/...`
* `/var/folders/...`
* complete environment

既存 backend contract には token/host-path redaction の実装知見があります。 ただし fetch diagnostics では、credential-bearing URL と helper output に対応する追加 rule が必要です。

---

## 9. Freshness/TOCTOU設計

### 9.1 「完全な transaction」ではなく optimistic consistency

Git repository と worktree 全体を、通常の user workflow を止めずに atomic snapshot することはできません。したがって本設計が提供するのは database transaction isolation ではなく、

```text
observe → fingerprint → reobserve → mismatchならfail-closed
```

という optimistic consistency です。

### 9.2 推奨 transaction boundary

#### T0: Static safety validation

fetch 前に実施してよいもの:

* output root safety
* source path の lexical traversal
* direct/ancestor symlink
* repo root resolution
* origin existence
* request parameter consistency

これらは freshness claim ではありません。

#### T1: Pre-fetch identity guard

取得:

* repository identity
* Git dir identity
* branch
* HEAD

これは最終 receipt の freshness evidence ではなく、fetch 中の checkout/commit/repository switch を検出する guard です。

#### T2: Mandatory fetch

固定 argv、bounded retry、timeout、非対話化。

#### T3: Post-fetch full snapshot

fetch 成功後に一括取得します。

* current branch
* local HEAD
* upstream
* remote-tracking HEAD
* worktree status
* ahead/behind/diverged
* explicit source existence
* source manifest
* normalized origin identity

fetch 失敗時は cached remote-tracking ref を `verified remote_head` として扱いません。既存 field を互換性上出す場合も、次を必須にします。

```json
{
  "remote_freshness": "not_verified",
  "remote_head_source": "unverified_cache"
}
```

より安全なのは fetch failure 時の `remote_head` を `null` にすることです。

#### T4: Contract evaluation

既存 blockers を評価します。

#### T5: Pre-publication guard

critical fingerprint:

```text
sha256(
  repository_identity,
  branch,
  local_head,
  upstream,
  remote_tracking_head,
  status_porcelain_digest,
  source_manifest_hash
)
```

を再取得します。

一致しなければ:

```text
status=blocked
blocker=concurrent_repo_change
github_sync=failed
```

とします。最初の PR では internal observation retry をせず、一度で fail-closed にする方が単純で安全です。

#### T6: Atomic receipt publication

serialize 済み payload を atomic replace します。publication 後に repository state が変わる可能性は残ります。そのため receipt には `observed_at` と `snapshot_id` が必要です。

### 9.3 Source manifest の安定読み取り

現行 implementation は directory を走査し、各 file を順次 hash します。 多数の file がある場合、hash 中に一部が変わると mixed source snapshot になり得ます。

最初の PR の最低線:

1. manifest hashing 前に guard を取得。
2. manifest hashing。
3. hashing 後に guard を再取得。
4. source file list、status、mtime/size summary、HEAD のいずれかが変われば block。

より強い follow-up:

* file open 後の `fstat`
* read 後の `fstat`
* inode/device/size/mtime_ns の比較
* changed file の限定再読
* directory inventory digest の前後比較

### 9.4 Receipt → pack prepare

最初の PR または直後の小 PR で、`pack prepare` に optional `--repo-root` を追加し、次を比較することを推奨します。

* repository identity
* branch
* local HEAD
* remote-tracking HEAD
* clean worktree
* source manifest hash
* receipt age
* receipt digest

推奨最大 age:

```text
300 seconds
```

ただし TTL は freshness の証明ではありません。TTL 内でも remote は動き得ます。したがって comparison mismatch と age の両方を使います。

Legacy unversioned receipt は、移行期間中だけ次の条件で受け入れます。

* current local HEAD と source manifest を再計算
* GitHub-synced state labels の整合性を確認
* `legacy_preflight_receipt` warning を出す

### 9.5 Pack → backend invocation

最終的な GitHub freshness を invocation 直前まで保証するには、次のどちらかが必要です。

#### 案 A: backend invoke 内の final validation

```text
validate pack
  -> final mandatory fetch
  -> compare receipt-bound snapshot
  -> invoke backend immediately
```

#### 案 B: 単一 orchestration command

```text
authoring workflow invoke
  = preflight
  + pack prepare
  + final validation
  + backend invoke
```

長期的には案 B の方が transaction boundary が明確です。ただし既存 CLI surface への影響が大きいため Phase 2 とします。

### 9.6 Receipt binding

Prompt pack の `provenance.json` に次を継承します。

```json
{
  "preflight_receipt_schema_version": 1,
  "preflight_receipt_digest": "sha256-value",
  "preflight_snapshot_id": "sha256-value",
  "preflight_observed_at": "2026-07-13T02:00:00Z",
  "remote_observation_source": "fetched_remote_tracking_ref"
}
```

これにより、任意の別 receipt を差し替えることを検出できます。

---

## 10. CLI・JSON schema・互換性

### 10.1 既存 CLI 互換性

既存 invocation はそのまま維持します。

```bash
./spec-dock/scripts/spec-dock authoring preflight github-sync \
  --repo-root . \
  --format json
```

この場合:

* stdout JSON は従来どおり出る。
* file は作らない。
* exit code は従来どおり、`pass=0`、それ以外 `1`。
* argument contract error は `2`。

新しい persistence:

```bash
./spec-dock/scripts/spec-dock authoring preflight github-sync \
  --repo-root . \
  --format json \
  --output-dir /managed/temp/run-123
```

shell redirect は不要です。

### 10.2 JSON compatibility

既存 top-level fields は削除・rename しません。

維持対象:

```text
status
evidence_mode
sync_state
github_sync
requested_ref
effective_ref
local_head
remote_head
source_manifest_hash
source_paths
source_hashes
source_hash_mismatch_checked
blockers
remediation
authority
adoption_requires
bundle_generation_not_promotion
```

新規 fields は原則 nested にします。

```text
schema_version
receipt_kind
repository
fetch
freshness
receipt_digest
```

### 10.3 Text output compatibility

現在の text output key は維持し、末尾に次を追加します。

```text
receipt_schema_version=1
fetch_status=failed
fetch_attempt_count=2
fetch_failure_class=transient_transport
fetch_classification_confidence=probable
fetch_timeout_seconds=60
remote_freshness=not_verified
snapshot_id=null
concurrent_change_check=not_applicable
```

raw diagnostic excerpt は text output に無条件で出しません。必要なら JSON receipt 内の bounded/redacted field に限定します。

### 10.4 Version skew

| Producer            | Consumer                         | 推奨挙動                                                                      |
| ------------------- | -------------------------------- | ------------------------------------------------------------------------- |
| 新 preflight         | 旧 pack prepare                   | 既存 top-level fields があるため基本的に動く。extra fields を無視できることを tests で確認          |
| 旧 preflight         | 新 pack prepare                   | `legacy_unversioned` として一時受理し、current local/source revalidation と warning |
| 新 installed runtime | 古い dogfood projection            | parity test を failure にする。片側だけ release しない                                |
| 新 provider asset    | `spec-dock init/update` consumer | install simulation で CLI help、skill、runtime、schema を確認                    |

Epic contract は provider-side assets を authoritative とし、installed runtime と dogfood path の双方を test することを要求しています。

既存 install simulation は init 後の `spec-dock-chatgpt-authoring` skill を実際に読み、mode や authority wording を検査しています。 この test surface に新しい permission/output guidance を追加すべきです。

---

## 11. テストマトリクス（優先度付き）

| 優先度 | Layer                 | 必須ケース                                                                            |  First PR |
| --- | --------------------- | -------------------------------------------------------------------------------- | --------: |
| P0  | Fetch adapter unit    | fixed executable/argv、cwd、`shell=False`、bytes capture                            |        必須 |
| P0  | Fetch adapter unit    | `GIT_TERMINAL_PROMPT=0`、trace env 除去、full env 非記録                                |        必須 |
| P0  | Timeout               | timeout outcome、attempt duration、blocked receipt                                 |        必須 |
| P0  | Retry policy          | transient/timeout/lock は最大 1 retry                                               |        必須 |
| P0  | Retry policy          | auth/config/policy/unknown は retry なし                                            |        必須 |
| P0  | Retry invariant       | retry 前後で executable/argv/cwd/remote/policy が同一                                  |        必須 |
| P0  | Classifier            | representative DNS/reset/5xx/throttle/lock/auth/host-key/config/unknown fixtures |        必須 |
| P0  | Classifier            | locale、non-UTF-8、empty stderr、stdout-only failure                                |        必須 |
| P0  | Redaction             | credential URL、token、password、helper output、host path が非露出                       |        必須 |
| P0  | Receipt model         | schema version、kind、attempts、digest、legacy keys                                  |        必須 |
| P0  | CLI                   | `--output-dir` help、parser、dispatch、exit code                                    |        必須 |
| P0  | Persistence           | pass receipt、blocked receipt の両方を保存                                              |        必須 |
| P0  | Output security       | canonical root、assurance、leaf/ancestor/broken symlink、non-directory、non-regular  |        必須 |
| P0  | Ownership             | malformed/non-SpecDock existing target を上書きしない                                   |        必須 |
| P0  | Atomicity             | replace 前失敗で旧 file が保持される                                                        |        必須 |
| P0  | Atomicity             | reader は old または new の valid JSON だけを見る                                          |        必須 |
| P0  | Concurrency           | fetch 中の checkout/commit、snapshot 中の source edit                                 |        必須 |
| P0  | Concurrency           | publication 前 remote-tracking ref change                                         |        必須 |
| P0  | Hermetic Git          | local bare remote で clean/ahead/behind/diverged/prune                            |        必須 |
| P0  | No shell policy       | argv 中に redirect/pipe/tee/heredoc がない                                            |        必須 |
| P0  | Skill/docs            | `origin_fetch_failed` が escalation 根拠でないことを assert                               |        必須 |
| P0  | Provider parity       | provider runtime と dogfood projection の同一 behavior                               |        必須 |
| P0  | Installer parity      | `init/update` 後の skill/help/runtime output                                       |        必須 |
| P1  | Receipt consumer      | pack prepare が HEAD/source/age mismatch を stale にする                              |        推奨 |
| P1  | Process cleanup       | timeout/cancel 時の credential helper descendant cleanup                           | Follow-up |
| P1  | Platform              | Linux/macOS/Windows の atomic replace semantics                                   | Follow-up |
| P1  | Classification corpus | 複数 Git/SSH/credential helper version の fixtures                                  | Follow-up |
| P1  | TOCTOU                | remote が receipt 後に動いたケース                                                        | Follow-up |
| P2  | Backend E2E           | invocation 直前 final fetch/check                                                  |   Phase 2 |
| P2  | Security race         | parent directory swap、`dir_fd/openat` tests                                      |   Phase 3 |
| P2  | Performance           | 大規模 source manifest、many refs、slow remote                                        |   Phase 3 |

### Hermetic test 方針

Network に依存する test は避けます。

* success/ahead/behind/diverged は local bare repository。
* DNS/auth/HTTP/throttle helper output は fake `git` executable または subprocess shim。
* retry/backoff は fake clock/sleeper。
* classifier fixture は raw bytes。
* cancellation は controlled child process。

現行 tests は clean sync、worktree states、ahead/behind/diverged、fetch-before-comparison、fallback、source symlink、local-context、dogfood path を既に広くカバーしています。  したがって新 tests は既存 matrix を置換せず、fetch execution と receipt publication の欠落部分を追加する形がよいです。

---

## 12. 実装順序と変更対象候補

### 12.1 推奨実装順序

| 順序 | 作業                                              |
| -: | ----------------------------------------------- |
|  1 | Domain enum/dataclass/schema と unit tests       |
|  2 | Subprocess fetch adapter と fake adapter         |
|  3 | Classifier と retry policy                       |
|  4 | `run_github_sync_preflight` の orchestration 再構成 |
|  5 | Snapshot observer と pre-publication guard       |
|  6 | Safe atomic JSON writer                         |
|  7 | CLI `--output-dir` と command wiring             |
|  8 | JSON/text renderer の additive fields            |
|  9 | `pack prepare` local stale validation           |
| 10 | Installed skill / docs guidance                 |
| 11 | Provider/dogfood/install parity tests           |
| 12 | Hermetic Git/concurrency/output-security E2E    |

### 12.2 変更対象候補

#### Domain

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/
  preflight_contract.py
  git_fetch_contract.py            # 新規候補
  receipt_contract.py              # 必要なら分離
```

`preflight_contract.py` にすべて詰め込むと責務が肥大化するため、fetch attempt と receipt serialization contract は分離する方がよいです。

#### Application

```text
application/authoring_pack/
  github_sync_preflight.py
  github_fetch_policy.py           # classifier/retry policy
  preflight_freshness.py           # snapshot comparison
  pack_prepare.py
```

#### Infra

```text
infra/authoring_pack/
  git_fetch_subprocess.py
  git_repository_snapshot.py
  safe_json_receipt_writer.py
```

Repository には既に `spec_dock_runtime/infra/` が存在するため、subprocess と filesystem publication を application file に残す必要はありません。

#### Commands / presentation

```text
commands/authoring.py
presentation/authoring_pack/diagnostics.py
```

#### Guidance

```text
src/spec_dock/assets/install_root/.agents/skills/
  spec-dock-chatgpt-authoring/SKILL.md

src/spec_dock/assets/spec_dock/docs/
  workflow_chatgpt_authoring_pack.md
```

#### Tests

```text
tests/unit/authoring_pack/test_git_fetch_policy.py
tests/unit/authoring_pack/test_safe_receipt_writer.py
tests/cli_runtime/test_authoring.py
tests/cli_runtime/test_wrappers.py
```

巨大な `test_authoring.py` にすべての pure policy cases を追加すると保守性が落ちるため、classifier/writer は unit test file に分け、CLI/E2E だけ既存 file に置くことを推奨します。

### 12.3 Provider/dogfood projection

実装 source of truth は provider-side asset です。dogfood `spec-dock/scripts/...` だけを直接修正してはいけません。Epic design も standalone/dogfood surface を implementation authority ではないと定義しています。

推奨順序:

```text
provider asset 変更
  -> provider tests
  -> init/update projection
  -> dogfood parity verification
```

---

## 13. セキュリティ・運用・観測性

### 13.1 Operation failure は permission evidence ではない

`git fetch` の非ゼロ結果から確実に分かるのは「その operation が成功しなかった」ことだけです。

それだけでは次を区別できません。

* DNS
* proxy
* transport reset
* remote 5xx
* authentication
* authorization
* private repository の not-found masking
* host key
* local ref lock
* repository config
* credential helper
* filesystem
* sandbox
* execution policy
* unknown Git error

したがって、次の推論は禁止すべきです。

```text
fetch failed
  therefore
additional permission is required
```

権限昇格には、host が提供する structured policy denial など、fetch stderr とは別の根拠が必要です。

### 13.2 Skill に即時追加すべき運用文言

現行 skill は generic な retryable/recoverable/blocked taxonomy を持ちますが、command shape と権限については明示が不足しています。

次を明文化します。

```text
- Run authoring preflight as direct argv.
- Do not wrap it in a shell.
- Do not use redirect, pipe, tee, heredoc, command substitution, or inline environment assignment.
- Use the first-class --output-dir option to persist receipts.
- A nonzero fetch result is not evidence that additional permissions are required.
- Never add require_escalated or change the sandbox/permission mode in response to a fetch result.
- Retry is owned by SpecDock and must preserve the same executable, argv, repository, remote, output policy, and execution context.
- Do not replace preflight with an agent-owned raw git fetch.
- Do not silently switch to local-context or the default branch.
```

### 13.3 Credential boundary

Receipt に保存しないもの:

* raw origin URL
* URL userinfo
* complete command environment
* credential helper stdout/stderr
* raw SSH diagnostics without redaction
* raw HTTP headers
* full Git config
* raw transcript
* complete stderr

保存できるもの:

* normalized host/repository identity
* remote name `origin`
* error code/class
* bounded redacted excerpt
* digest と byte count
* attempt timing
* exact fixed argv
* policy IDs

### 13.4 Audit fields

最低限の audit fields:

```text
receipt schema/kind
policy ID
git executable
fixed argv
remote name
attempt number/count
start/end timestamps
duration
timeout
termination kind
return code
failure class
classification confidence
retry decision
diagnostic digest/bytes/truncation
repository identity fingerprint
snapshot ID
observation source
concurrent-change result
receipt digest
```

記録してはいけない audit field:

```text
complete environment
raw HOME
raw SSH_AUTH_SOCK
credential helper command/output
credential-bearing remote URL
sandbox mode inferred from stderr
```

### 13.5 Cancellation

推奨 contract:

* `SIGINT` / `KeyboardInterrupt` は即時停止。
* retry しない。
* exit code は 130 相当。
* child process を確実に reap。
* output destination が安全で、遅延なく可能なら best-effort cancelled receipt。
* receipt publication のために user cancellation を長く遅延させない。

`subprocess.run(timeout=...)` は direct child の containment には使えますが、credential helper や SSH descendant の process-tree cleanup は platform 差があるため、follow-up hardening 対象です。

### 13.6 Operator remediation

Receipt の remediation は class ごとに限定します。

| Class                       | Remediation                                                                       |
| --------------------------- | --------------------------------------------------------------------------------- |
| timeout/transient           | same command shape で SpecDock retry budget を使い切った。network/remote availability を確認 |
| ref lock                    | 他の Git process の終了を確認。lock file を手動判断なしで削除しない                                     |
| access denied/not found     | origin identity、credential、repository visibility を確認                              |
| host identity               | operator-managed known_hosts / SSH policy を確認                                     |
| configuration               | origin、fetch refspec、repository state を修正                                         |
| execution/filesystem denied | execution policy と filesystem permission を確認。自動昇格しない                              |
| unknown                     | protected diagnostics と receipt digest を用いて再現。推測 retry しない                        |

---

## 14. 非推奨案と理由

| 非推奨案                                                    | 理由                                                                             |
| ------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Mandatory fetch を削除する                                   | cached ref を fresh GitHub evidence と誤認する                                       |
| `git ls-remote` に置き換える                                  | remote-tracking state を更新せず、local comparison transaction と分離する                 |
| Agent が先に raw `git fetch` する                            | repo/remote/ref/capability/receipt の binding が失われる                             |
| Preflight 全体を `require_escalated` で再実行                  | operation failure を permission evidence と誤認し、command shape を変える                |
| Redirect / pipe / `tee`                                 | direct argv approval matching を崩し、partial file や pipeline exit semantics を導入する |
| 全 fetch failure を retry                                 | auth、host-key、config、policy failure を無意味に繰り返す                                  |
| Unknown failure を一度だけ retry                             | 「一度だけなら安全」という根拠がない。未知の credential helper や policy prompt を再発火し得る               |
| Exit code だけで分類                                         | Git の broad nonzero code から semantic root cause を得られない                         |
| stderr regex を真実として扱う                                   | locale/version/helper/provider 依存で false classification が起きる                   |
| First PR で Trace2 を導入                                   | information leakage と複雑性に対して、semantic classification の保証が弱い                    |
| Ref lock file を自動削除                                     | active Git process の lock を破壊し、repository corruption を誘発し得る                    |
| `local-context` へ自動降格                                   | requested evidence authority を変える                                              |
| Default branch へ自動 fallback                             | requested ref と evidence scope を変える                                            |
| TTL だけで receipt freshness を判断                           | TTL 内の repository/remote change を検出できない                                        |
| Backend 完了まで repository lock を保持                        | user workflow を阻害し、deadlock/stale lock risk が大きい                               |
| 新 dependency を導入                                        | stdlib で timeout、hash、atomic replace、path checks を実装可能                         |
| 既存 writer をそのまま流用                                       | path checks はあるが atomic publication contract がない                               |
| First PR で全 writer を再設計                                 | Issue #314 の修正範囲を超え、regression surface が大きい                                    |
| Mutable repo-local script に広い privileged capability を付与 | agent が変更可能な executable に強い権限を与えることになる                                         |

---

## 15. 未確定事項・仮定・意思決定が必要な点

### 15.1 判断不能な点

1. **Incident fetch failure の実原因**
   現行 receipt に stderr、timeout、exit classification がないため判断不能です。DNS、auth、ref lock、sandbox のいずれとも断定できません。

2. **External sandbox mode**
   SpecDock child process から current host permission/sandbox mode を確実に取得できる evidence は提示されていません。

3. **Credential helper の interaction semantics**
   `GIT_TERMINAL_PROMPT=0` は portable な最低措置ですが、すべての third-party credential helper が完全非対話になるとは未確認です。

4. **Current branch の実装状態**
   指定 branch は GitHub に存在しないため、branch-local worktree の ground truth は connector では確認できません。添付 bundle は補助証拠としてのみ扱っています。

### 15.2 明示した仮定

* Python 3.10+ stdlib を使用する。
* Git executable は通常 `git` として PATH 解決される。
* `origin` は mandatory remote 名として維持する。
* `git fetch --prune origin` の refspec scope は最初の PR では変更しない。
* `--output-dir` は caller/operator が明示的に委任した evidence root である。
* Existing JSON consumers は未知の additive keys を無視できる。ただし tests で検証する。
* Pack preparation は対象 repository を識別できるよう、cwd discovery または optional `--repo-root` を使用する。

### 15.3 Maintainer decision が必要な点

| Decision                          | 推奨                                                |
| --------------------------------- | ------------------------------------------------- |
| Output flag                       | 最初の PR は `--output-dir` のみ                        |
| Filename                          | `github-sync-preflight.receipt.json`              |
| First explicit schema             | `schema_version: 1`                               |
| Retry budget                      | total attempts 2                                  |
| Timeout                           | 60 秒/attempt                                      |
| Backoff                           | 250 ms + 0–100 ms jitter                          |
| Unknown failure retry             | しない                                               |
| Raw diagnostic persistence        | 禁止                                                |
| Excerpt limit                     | 1024 UTF-8 bytes/attempt                          |
| Legacy unversioned receipt        | 1 release 程度、warning + current-state revalidation |
| Repo-local default output         | 現時点では設けない                                         |
| Pack prepare revalidation         | first PR または直後の必須 small PR                        |
| Backend final fetch               | Phase 2                                           |
| Connector-visible wording         | runtime 実装に合わせて observation source を明示            |
| POSIX `dir_fd` hardening          | follow-up                                         |
| Windows directory fsync semantics | platform-specific follow-up                       |

### 15.4 特に注意すべき契約上の未決定

Epic requirements は connector-visible branch/head を記録対象としています。 現行 runtime は fetched remote-tracking ref を使います。

選択肢は次の二つです。

1. 現行実装を正として docs を `fetched remote-tracking ref` に訂正する。
2. 将来 connector observer を実際に wiring し、両 observation を receipt に分離する。

推奨は、Issue #314 では option 1 に相当する truthful field を追加し、connector integration は別 issue にすることです。

---

## 16. 推奨受け入れ条件

### First PR — MUST

| ID        | 受け入れ条件                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------- |
| AC-314-01 | `github-synced` の正常な request は必ず `git fetch --prune origin` を実行する                                       |
| AC-314-02 | Fetch は固定 argv、`shell=False`、固定 remote、固定 cwd policy で実行される                                             |
| AC-314-03 | Retry 前後で executable、argv、repo、remote、timeout、environment policy、output policy が同一である                   |
| AC-314-04 | Total attempts は default 2 以下である                                                                        |
| AC-314-05 | Timeout、transient transport、throttling、ref lock 以外は retry しない                                           |
| AC-314-06 | `unknown` failure は retry せず fail-closed する                                                             |
| AC-314-07 | `GIT_TERMINAL_PROMPT=0` が fetch environment に設定される                                                      |
| AC-314-08 | Timeout が明示され、receipt に記録される                                                                            |
| AC-314-09 | Fetch attempt ごとに termination、duration、return code、failure class、confidence、retry decision が記録される       |
| AC-314-10 | Complete stdout/stderr と complete environment は receipt に保存されない                                         |
| AC-314-11 | Diagnostic excerpt は redacted、bounded、digest/byte count/truncation 付きである                                |
| AC-314-12 | Credential-bearing URL、token、password、private key、helper output、host-local path が JSON/text/file に露出しない |
| AC-314-13 | `--output-dir` が CLI help と parser に存在する                                                                |
| AC-314-14 | `--output-dir` 使用時、固定 filename の receipt が作成される                                                         |
| AC-314-15 | Fetch failure、timeout、auth/config/unknown failure を含む blocked receipt が保存される                            |
| AC-314-16 | Unsafe output root、canonical docs、assurance、symlink、non-regular target は拒否される                           |
| AC-314-17 | Existing non-SpecDock target は上書きされない                                                                   |
| AC-314-18 | Publication は same-directory temporary file と atomic replace を使用する                                      |
| AC-314-19 | Publication failure 時、command は pass を返さない                                                              |
| AC-314-20 | Final worktree/HEAD/source/remote snapshot は fetch 成功後に取得される                                            |
| AC-314-21 | Publication 前の critical fingerprint mismatch は `concurrent_repo_change` で block する                      |
| AC-314-22 | Fetch failure 時、cached remote ref を fresh verified evidence として扱わない                                     |
| AC-314-23 | Existing top-level JSON fields と exit code policy が維持される                                                |
| AC-314-24 | Receipt に `schema_version: 1` と `receipt_kind` が存在する                                                    |
| AC-314-25 | Existing text output keys は削除されず、新 fields は additive である                                                |
| AC-314-26 | Installed skill に no shell、no redirect、no escalation、no implicit fallback が明記される                        |
| AC-314-27 | `origin_fetch_failed` が追加 permission の証拠ではないと明記される                                                      |
| AC-314-28 | Raw agent-owned `git fetch` を標準復旧経路として案内しない                                                             |
| AC-314-29 | Provider-side runtime、dogfood projection、installed runtime の tests が通る                                  |
| AC-314-30 | P0 unit、hermetic Git、output-security、concurrency、CLI、installer tests が追加される                             |

### First PR または直後の必須 small PR — SHOULD

| ID        | 受け入れ条件                                                                         |
| --------- | ------------------------------------------------------------------------------ |
| AC-314-31 | `pack prepare` が receipt digest と schema を検証する                                 |
| AC-314-32 | `pack prepare` が current repo identity、branch、HEAD、source hash を receipt と比較する |
| AC-314-33 | Receipt age が policy limit を超えた場合は stale にする                                   |
| AC-314-34 | Legacy unversioned receipt の使用時は warning と current-state revalidation を行う      |
| AC-314-35 | Prompt pack provenance に receipt digest、snapshot ID、observed time を bind する    |

### Later hardening — 明示的に別受け入れ条件とするもの

| ID        | 受け入れ条件                                                              |
| --------- | ------------------------------------------------------------------- |
| AC-314-L1 | Strict `github-synced` backend invocation 直前に final fetch/check を行う |
| AC-314-L2 | Remote が preflight 後に動いた場合、backend invocation を fail-closed する      |
| AC-314-L3 | POSIX `dir_fd/openat` または同等の race-resistant writer を評価する            |
| AC-314-L4 | Windows/macOS/Linux の publication/cancellation semantics を検証する      |
| AC-314-L5 | 必要性が実測された場合だけ Trace2 や immutable launcher を導入する                     |

---

Issue #314 の最初の PR の合格ラインは、**「原因を完璧に言い当てる classifier」ではなく、「原因不明でも権限・shell shape を変えず、安全に retry または block し、その判断材料を durable receipt として残せること」**です。

その上で、receipt publication 後の freshness は別問題として隠さず、最初の PR では local/concurrent change を閉じ、remote-to-backend の最終 TOCTOU は Phase 2 の明示的な契約として完成させるのが、最小でありながら過小修正ではないリリース設計です。
