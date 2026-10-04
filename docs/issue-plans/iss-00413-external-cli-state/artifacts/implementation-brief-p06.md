# Issue #413 P-06 実装ブリーフ
**対象:** immutable direct target と Start-only OS exclusion を前提にした、branch / checkout / readiness / partial effects の残作業
**実装担当:** GPT-6.1 Sol
**Reasoning:** High
**成果物種別:** 実装計画を具体化するブリーフ。実装完了報告・レビュー合格報告ではない。

## 1. 検証済みの実装基準

GitHubコネクタで次を直接確認した。

| 項目 | 検証値 |
|---|---|
| repository | `chemitaro/spec-dock` |
| target branch | `codex/iss-00413-external-cli-state` |
| branch tip | `ddef15e82abf24adf43ec1afc916c9f6b201c1de` |
| expected SHA | `ddef15e82abf24adf43ec1afc916c9f6b201c1de` |
| 比較結果 | 完全一致 |

以後の仕様・コード・試験の確認は、この完全SHAを直接指定して行った。

本ブリーフは、仕様正本を変更せず、検証済みcommitの現実装と試験を区別し、具体的な作業対象・順序・観測可能な完了証拠を示す。これは添付された実装ブリーフの停止条件と成果物条件に従う。:chatgpt-content-reference{index="1"}

## 2. 目的と完了像

P-06で完成させるのは、次の一つの縦経路である。

> 固定された対象Scopeと固定されたbranch tipを、必要なlive readinessが成立した状態で、Start専用のclone共通排他の中で安全にcheckoutし、現在worktreeのimmutable direct targetを最後に公開する。途中で止まった場合は、実際に起きたGit・record効果を `succeeded / failed / not_attempted / unknown` で偽りなく返す。

最終的に成立させる保証は次である。

1. GitHub-backedの対象、祖先、実効依存は、Start実行ごとのlive観測で判定する。
2. 新branchのbaseまたは既存branch tipにあるScope metadataを、Git変更前に検査する。
3. lock取得後、Git変更前にlocal bytes、branch tip、clean状態、全worktree inventory、direct targetを再照合する。
4. checkout後とdirect target公開直前にも、必要なsnapshotとinventoryを再照合する。
5. 異なるdirect targetへの切替だけが `--switch-active` を要求する。同じScopeの別branchへのStartは、flagなしで旧tokenを限定解除し、新tokenへ置換する。
6. branch作成、checkout、旧token解除、record公開は独立した効果として扱い、自動rollbackしない。
7. Git timeout、signal、non-zero、checkout失敗は、実際のref・HEADを事後観測して効果を分類する。
8. recordのrename後にdurabilityまたはreadbackを確認できない場合、`selection.publish=unknown` とする。
9. 通常Startへ旧control、RegistryStore、WriterLock、operation journal、resume、rollbackを戻さない。

D-03〜D-07はimmutable record、inventory、Start専用排他、branch/checkout順序、direct selection規則を定め、D-09は実効依存とlive readinessを定めている。P-06はこれらを一つのStart経路として閉じる工程である。

## 3. 正本と実装資料の優先順位

| 優先 | 資料 | この作業での扱い |
|---:|---|---|
| 1 | `requirement.md` | 要求・受入条件の正本 |
| 2 | `design.md` D-03, D-04, D-05, D-06, D-07, D-09 | 型、順序、排他、部分成功の正本 |
| 3 | `plan.md` P-06 | 実装順、禁止事項、完了条件 |
| 4 | `artifacts/cli-contract.md`、`data-schema.json`、`cli-schema.json`、`examples.json` | wire、persistence、exit、effectsの正本 |
| 5 | `artifacts/user-decisions.md` | rollbackなし、Start-only lock、journalなし等の確定判断 |
| 6 | 現コード・現試験 | 現在地を示す資料。正本との不一致は実装残として扱う |

確定判断として、Startのbranch/checkout維持、一worktree一direct target、自動rollbackなし、Git原文保持、Startだけの共通排他、共通registry/journal/cacheの廃止が記録されている。

正本間に、P-06の実装を止める矛盾は見つからない。現コードとの不一致は仕様変更要請ではなく、以下で閉じる実装残である。

## 4. 現在成立しているものと残作業

現在の `application/work_start.py` は、最初の縦経路をすでに持つ。

- 新branch作成、checkout、direct target公開
- dry-runでlock・Git・record書込をしない
- 新branchには `--base`、既存branchには明示 `--branch`
- dirty、ignore不足、他worktree重複の拒否
- lock内でroot/common-dir identity、HEAD、target metadata、clean、selectionを再確認
- 同一妥当record・同一branch・同一HEADの `unchanged`
- branch作成後のcheckout失敗を `partial` とし、Git stderrとreturncodeを保持

これらは既存CLI試験でも固定されている。

残作業は次の通り。

| 領域 | 現状 | P-06で必要な状態 |
|---|---|---|
| readiness | 対象と祖先のopenだけをGET | 対象・祖先open＋実効依存completedをcandidate commit基準で判定 |
| candidate snapshot | 現checkoutのtarget bytesだけ | base / existing branch tipのworkspace＋Scope graphをGit効果前に検査 |
| local race検知 | target `.meta.json` 一つ | 計画作成時に読んだworkspace・Scope metadataのexact bytesを再確認 |
| branch race | preflightでtipを解決 | lock内で既存tipまたは新branch不存在を再確認 |
| inventory | Git効果前の一回 | lock内基準、checkout後、公開直前の再観測 |
| switch-active | 別targetを一律拒否 | 別Scopeはflag必須、同Scope別branchはflag不要でtoken置換 |
| expect guards | parserには存在するが未使用 | canonical ID/backendをpreflightとlock内で照合 |
| Git失敗 | timeoutならmutationを一律unknown扱い | ref/HEADの事後観測で succeeded / failed / unknown を決定 |
| publish境界 | rename後失敗を通常例外で失う | rename前失敗とrename後確認不能を型で区別 |
| recovery | v2 rendererは常にnull | partial時のみ、人間向けinstructions。resume/rollbackはfalse |
| public Start入力 | cache、allow-stale、resumeが残る | Startについて廃止入力をcontext解決前にexit 2で拒否 |

現在のcatalogはまだ `--source cache`、`--allow-stale`、Startの `--resume` を生成している。一方、CLI正本はこれらを `ARGUMENT_RETIRED` としてcontext解決前に拒否する。

## 5. 変更範囲

### 主変更対象

| ファイル | 責務 |
|---|---|
| `src/spec_dock/runtime/application/work_start.py` | preflight、StartPlan、lock内実行、effects/result組立 |
| `src/spec_dock/runtime/application/worktree_observation.py` | Start向けinventory snapshotを、既存の狭い他WT観測を壊さず提供 |
| `src/spec_dock/runtime/infra/git_process.py` | stdout/stderr/timeout/signalを保持するGit境界 |
| `src/spec_dock/runtime/infra/work_target_store.py` | publishのrename前失敗とrename後unknownを区別 |
| `src/spec_dock/runtime/presentation/envelope.py` | v2 recovery advice、Git原文とredaction metadata |
| `src/spec_dock/runtime/cli/catalog.py` | Start固有のretired option除去・拒否 |
| `src/spec_dock/runtime/cli/options.py` | `ARGUMENT_RETIRED` とexpect guardの入口確認 |
| `tests/cli_runtime/test_issue413_work_start.py` | 公開Start契約の主試験 |
| `tests/unit/infra/test_work_target_store.py` | publish commit境界 |
| `tests/unit/infra/test_git_process.py` | 新規。timeout/signal/raw output |
| `tests/unit/application/test_work_start_plan.py` | 新規。純粋な計画・selection判断 |
| `tests/integration/test_issue413_start_races.py` | 新規。同時Start、checkout後race、kill境界 |
| `tests/integration/test_issue413_observation.py` | 既存の狭い他WT観測が退行しないことを確認 |

### 参照のみ

`domain/dependency_vnext.py` の実効依存・graph検証・readiness純粋規則は再利用対象である。

`application/dependency_vnext.py`、`application/branch_vnext.py`、`application/work_lifecycle.py` は、旧業務の意味を確認する資料としてだけ使う。これらはcontrol、WriterLock、RegistryStore、journal、cache、resumeを含むため、通常Startから呼ばない。

## 6. 内部型と公開境界

型名は実装中に微調整してよいが、責務の混同はしない。

### 6.1 exact local bytes

```python
@dataclass(frozen=True)
class LocalMetadataBytes:
    relative_path: PurePosixPath
    payload: bytes
    content_hash: str
    file_identity: tuple[int, int]
```

用途は、preflightで読んだlocal inputがlock取得まで変わっていないことの確認である。

対象は「計画作成時に実際に読んだもの」に限定する。

- `spec-dock/workspace.json`
- 現作業treeのScope graph検証で読んだ全 `.meta.json`
- current direct targetの`SelectionHandle`
- preflightのHEAD、branch、root/common-dir identity

JSONを再serializeして比較してはならない。空白や未知fieldを含む**exact bytes**で比較する。現在の `read_guarded_json` はbytesを返さないため、no-follow・single-link・identity確認を維持した `read_guarded_json_bytes` 相当をinfraに追加する。

### 6.2 candidate commit snapshot

```python
@dataclass(frozen=True)
class CommittedMetadataBytes:
    relative_path: PurePosixPath
    payload: bytes
    object_id: str


@dataclass(frozen=True)
class CandidateScopeGraph:
    commit_oid: str
    workspace_payload: bytes
    views: tuple[ScopeView, ...]
    dependencies: tuple[tuple[str, tuple[str, ...]], ...]
    metadata: tuple[CommittedMetadataBytes, ...]
```

candidateは次のどちらかである。

- 新branch: `--base` をcommit OIDへ一度だけ固定したもの
- 既存branch: `refs/heads/<name>^{commit}` の固定tip

candidate graphはcheckoutせずに読む。既存 `git_snapshot.py` の「metadataだけを一時領域へmaterializeする」考え方は再利用できるが、現在のhelperはGitエラーを一般化するため、P-06の公開経路では `GitProcessError` の原文を失わない読取境界へ分離する。

candidate検証では次を確認する。

1. `workspace.json` が既知schema 3と新writer protocolである。
2. target IDが一意に存在する。
3. target、ancestor chain、GitHub linkage、backend、type、parent関係が有効である。
4. dependency graphが有効である。
5. target・ancestor・実効依存の必要集合をcandidate graphから導く。
6. titleやslugのbranch間差分を、それだけで新しい拒否条件にしない。
7. checkout後は、作業treeのmetadata bytesがcandidate snapshotと一致することを確認する。

### 6.3 readiness evidence

```python
ExpectedState = Literal["open", "completed"]


@dataclass(frozen=True)
class RequiredScopeState:
    scope_id: str
    expected_state: ExpectedState
    backend: Literal["github", "local"]
    github_ref: str | None


@dataclass(frozen=True)
class LiveScopeState:
    scope_id: str
    state: Literal["open", "completed", "not-planned", "unknown"]
    observed_at: str | None
```

必要集合は以下である。

- targetと全ancestor: `open`
- targetおよびancestorに宣言された実効依存: `completed`

GitHub-backedだけを、lock取得前に一対象一回GETする。local-backedはcandidate metadataのlifecycleを使う。GitHub responseのrepository・issue numberはgatewayで照合する。

`--offline` は、必要集合にGitHub-backedが一つでもあれば副作用前に停止する。local-only Startまで一律拒否しない。

GitHub GET失敗は「readyでない」と偽装せず、通信・認証・process失敗としてexit 5へ分類する。GET成功で期待stateと異なる場合はreadiness failureとしてexit 3にする。

### 6.4 selection decision

```python
SelectionAction = Literal[
    "unchanged",
    "publish",
    "replace_same_scope",
    "switch_scope",
]


@dataclass(frozen=True)
class SelectionPlan:
    action: SelectionAction
    observed_record: WorkTarget | None
    observed_handle: SelectionHandle | None
```

決定表は次で固定する。

| current direct target | requested target | branch状態 | `--switch-active` | action |
|---|---|---|---|---|
| empty | 任意 | 任意 | 不要 | `publish` |
| valid A | A | 同じbranch・HEAD・tip | 不要 | `unchanged` |
| valid A | A | 別branchまたはbranch差 | 不要 | `replace_same_scope` |
| valid A | B | 任意 | なし | `SWITCH_ACTIVE_REQUIRED`、効果前停止 |
| valid A | B | 任意 | あり | `switch_scope` |
| stale / invalid / unavailable | 任意 | 任意 | 任意 | 効果前停止 |

`replace_same_scope` と `switch_scope` は、checkout成功後に旧handleを `remove_observed(handle)` で限定解除し、その後に新recordをpublishする。旧recordのscope IDからfilenameを再推定したり、「最新record」を探して削除してはならない。

他worktreeでは、recordがtargetと同じfull ID、または同じ非null GitHub linkageを持つ場合、staleであっても予約として重複拒否する。無関係なworktreeがinvalid/unavailableなら、重複不存在を証明できないためfail closedにする。

### 6.5 StartPlan

```python
@dataclass(frozen=True)
class StartPlan:
    target_id: str
    github_ref: str | None
    backend: Literal["github", "local"]

    branch_name: str
    branch_tip: str
    create_branch: bool

    branch_before: str | None
    head_before: str | None

    local_inputs: tuple[LocalMetadataBytes, ...]
    candidate: CandidateScopeGraph
    readiness: tuple[RequiredScopeState, ...]
    live_states: tuple[LiveScopeState, ...]

    selection: SelectionPlan
    expect_current_id: str | None
    expect_backend: Literal["github", "local"] | None
```

`StartPlan` は永続化しないmemory値である。operation ID、epoch、engine digest、journal recordは持たせない。

## 7. CLI入口で先に閉じる契約

Start本体へ入る前に、Start固有の入力契約を正す。

1. `--source` は `github` だけを受け付け、既定も `github` とする。
2. `--source cache`、`--allow-stale`、`--resume`、`--rollback` はexit 2、`ARGUMENT_RETIRED`。
3. retired optionはproject/contextを解決する前に拒否する。
4. `--expect-current` はpreflightのScope snapshotでcanonical IDへ固定する。
5. `--expect-backend` は解決されたtarget backendと比較する。
6. `--expect-current` はlock内でもraw direct recordのIDと再照合する。
7. `--expect-backend` はlock内metadata bytes再確認によって変化していないことを保証する。

CLI正本では、retired入力をcontext前に拒否し、Startの `--expect-current` をlock内でも再確認することが明記されている。

この変更はStart行だけに限定する。他leafの全面的なcatalog移行へP-06を拡張しない。

## 8. preflight順序

lock外で次を順に行う。

1. `ProjectContext.require_writer()`。
2. 現在root/common-dirのphysical identityを取得。
3. current workspaceとScope graphを読み、exact bytesを捕捉。
4. requested target、`--expect-current`、`--expect-backend` をcanonical化。
5. current direct targetを読み、selection actionを仮決定。
6. 全worktree inventoryを観測し、既知の重複、invalid、unavailable、branch占有を拒否。
7. work-target pathのtracked/ignore条件を確認。
8. worktree cleanを確認。`git status --porcelain -z --untracked-files=all` を使う。
9. branch名を決定し、`check-ref-format --branch`。
10. 新branchなら `--base` 必須、既存branchなら明示 `--branch` 必須かつ `--base` 禁止。
11. baseまたは既存tipをcommit OIDへ固定。
12. candidate workspace/Scope graphをcheckoutせず読み、schema、target、ancestor、linkage、dependency graphを検査。
13. candidate graphからreadiness必要集合を導出。
14. 必要なGitHub GETを重複なく実行。
15. readinessを純粋規則で判定。
16. `StartPlan` を完成させる。
17. dry-runならここで `planned` を返す。lock・branch・checkout・record書込はしない。

networkと将来のpromptはここまでで完了し、lock内へ持ち込まない。

## 9. lock内実行順序

StartLockを取得してからreleaseするまで、次の順序を変えない。

### 9.1 Git効果前のauthoritative recheck

1. root `DirectoryIdentity` とcommon-dirを保持し、両identityを再検証。
2. `resolve_context` を再実行し、root、common-dir、HEAD、branchを確認。
3. `workspace.json` と計画作成時に読んだ全local metadataのexact bytesを再読。
4. current direct targetを再読し、record、handle、content hashが計画と同じであることを確認。
5. `--expect-current` を再確認。
6. work-target tracked/ignore条件を再確認。
7. clean状態を再確認。
8. 新branchならrefが依然として不存在であることを確認。
9. 既存branchならtipが `StartPlan.branch_tip` と完全一致することを確認。
10. 全worktree inventoryを再観測する。
11. target ID / linkage重複とbranch占有を再確認する。
12. このinventoryを `locked_inventory_before` として保持する。

ここまでの失敗ではGit・selection効果を一件も起こさない。

### 9.2 unchanged fast path

次がすべて成立する場合だけ `unchanged` を返す。

- valid direct recordがrequested target
- recordの`selected_branch`がplanned branch
- current branchがplanned branch
- current HEADがplanned tip
- record handleとbytesがpreflightから不変
- inventory、readiness input、expect guardがすべて有効

既存tokenをそのまま返し、recordを再公開しない。

### 9.3 branch作成

新branchの場合だけ、固定OIDを用いてbranchを作成する。

```text
git branch <branch_name> <fixed_commit_oid>
```

成功後、`refs/heads/<branch_name>` が固定OIDを指すことをread-onlyに確認する。

既存branchではprocessを起動せず、`git.branch.create=unchanged` とする。

### 9.4 checkout

current branchとHEADがすでにplanned branch/tipならprocessを起動せず、`git.checkout=unchanged`。

それ以外はcheckoutを実行する。checkout後は次を確認する。

1. current branchがplanned branch。
2. HEADがplanned tip。
3. worktreeがclean。
4. root/common-dir identityが不変。
5. workspaceとScope metadataがcandidate snapshotと一致。
6. target、ancestor、dependency graphがcandidate snapshotどおり有効。
7. direct target handleがまだ計画どおり。
8. 全worktree inventoryに重複・占有・unavailableがない。
9. current row以外のinventoryが `locked_inventory_before` から変わっていない。
10. current rowの差分が、今回のcheckoutで期待されたbranch/HEAD変更だけである。

live GitHub GETは再実行しない。local metadataが変化したなら、固定したlive evidenceと結び付けられないためpartialまたはfailedとして停止する。

### 9.5 公開直前inventory照合

selectionを変更する直前に、全inventoryをもう一度読む。

- 新しいworktreeが増えた
- 他worktreeのdirect recordが変わった
- target ID / linkageが他worktreeで選択された
- branchが他worktreeで使用された
- 読めないrowが出現した

これらのいずれかがあればselectionへ進まない。

この再照合は、StartLockを使わない外部Git操作とのraceを検出するためであり、省略しない。

### 9.6 旧tokenの限定解除

`replace_same_scope` または `switch_scope` の場合だけ実行する。

```python
result = store.remove_observed(planned_handle)
```

| 戻り値 | 扱い |
|---|---|
| `removed` | `selection.clear=succeeded` |
| `already_absent` | 競合。新recordをpublishしない |
| `conflict` | 競合。新recordをpublishしない |

`already_absent` や `conflict` を成功扱いしない。別processが置いた新tokenを削除してはならない。

### 9.7 新record公開と確認

新しい `WorkTarget` は、checkout後のcurrent physical identityとplanned branchを用いて作る。

公開のcommit境界は、次をすべて確認した時点である。

1. stage payloadのfsync成功
2. no-replace rename成功
3. parent directory fsync成功
4. final basenameをno-followで再読
5. exact bytes、identity、schema、record内容が一致
6. store全体が一つの妥当recordとして読める

ここまで成功して初めて、次を返す。

- `selection.publish=succeeded`
- `status=succeeded`
- `started=true`
- `selection_token=<confirmed token>`

lockは確認完了後にだけreleaseする。

## 10. WorkTargetStoreのpublish境界

現在のstoreはstage、fsync、no-replace rename、directory fsync、readbackを実行しているが、rename後の例外をcallerが分類できない。

次の型を追加する。

```python
PublishCommitState = Literal[
    "not_renamed",
    "renamed_unconfirmed",
]


class WorkTargetPublishError(OSError):
    commit_state: PublishCommitState
    token: str | None
```

分類規則は次とする。

| 失敗位置 | `commit_state` | effect |
|---|---|---|
| stage作成・write・stage fsync | `not_renamed` | `failed` |
| no-replace rename自体が失敗 | `not_renamed` | `failed` |
| rename成功後のdirectory fsync失敗 | `renamed_unconfirmed` | `unknown` |
| rename成功後のreadback不能・bytes不一致 | `renamed_unconfirmed` | `unknown` |

rename後のunknownで、同じStartの中から別tokenを再発行してはならない。自動削除もしない。

`selection.publish=unknown` の場合は、現物が存在していても次を返す。

- `status=partial`
- `exit_code=6`
- `started=false`
- `selection_token=null`

CLI契約も、record公開後に確認不能なら `started=true` を返さないとしている。

## 11. Git process境界と事後判定

### 11.1 GitProcessError

現在の `GitProcessError` はstderr、returncode、timeout uncertaintyを持つが、stdout、timeout flag、signalを十分に公開していない。

次へ拡張する。

```python
class GitProcessError(RuntimeError):
    argv: tuple[str, ...]
    stdout: bytes
    stderr: bytes
    returncode: int | None
    timed_out: bool
    signal: int | None
    process_started: bool
```

`details.git` は最低限次を持つ。

```json
{
  "argv": ["git", "-C", "...", "checkout", "..."],
  "stdout": "",
  "stderr": "Gitの原文\n",
  "returncode": 1,
  "timed_out": false,
  "signal": null,
  "decoding_replaced": false,
  "redacted": false
}
```

通常のUTF-8 stdout/stderrはstrip、翻訳、切捨てをしない。JSON modeのprocess出力はconsoleへ直接流さない。text modeではヘッダの後に、redaction後のGit stderrを元の改行のまま出す。exit/effectsとGit原文の契約はCLI正本に従う。

### 11.2 mutation error後の観測

Git mutationで例外が出たら、そのまま一律failed/unknownにしない。lockを保持したままread-only probeを行い、そこでStartを停止する。

#### branch create

| 事後観測 | `git.branch.create` |
|---|---|
| refがplanned OID | `succeeded` |
| refが不存在 | `failed` |
| 別OID、またはref観測不能 | `unknown` |

#### checkout

事前のsource branch/HEADもStartPlanに保持する。

| 事後観測 | `git.checkout` |
|---|---|
| branch/HEADがplanned targetで、clean | `succeeded` |
| branch/HEADが確認済みsource状態のまま | `failed` |
| detached、別HEAD、dirty化、観測不能 | `unknown` |

Git processがnon-zero、timeout、signalで終わった場合、事後状態がplanned targetでも次のselection公開へは進まない。Gitエラーを隠さず、確認済みGit効果をeffectsへ残したpartialとして返す。

親CLI process自体が未捕捉signalで終了し、出力できない場合の有効JSONは保証しない。次processはjournalではなく実ref、HEAD、recordだけを読む。

## 12. effectsと終了状態の分類

effectsの順序は固定する。

1. `git.branch.create`
2. `git.checkout`
3. `selection.clear` — 置換時のみ
4. `selection.publish`

主な分類は次の通り。

| 状況 | effectsの要点 | status / exit |
|---|---|---|
| preflight/readiness/lock内Git効果前失敗 | `[]` または失敗前段のみ | `failed` / 3, 4, 5 |
| branch command失敗、ref不存在 | branch=`failed`、以降=`not_attempted` | `failed` / 5 |
| branch command異常後、planned ref確認 | branch=`succeeded`、以降=`not_attempted` | `partial` / 6 |
| branch結果不明 | branch=`unknown`、以降=`not_attempted` | `partial` / 6 |
| branch成功後checkout失敗 | branch=`succeeded`、checkout=`failed` | `partial` / 6 |
| 既存branchでcheckout失敗、source不変 | branch=`unchanged`、checkout=`failed` | `failed` / 5 |
| checkout異常後、target到達確認 | checkout=`succeeded`、publish=`not_attempted` | `partial` / 6 |
| checkout後metadata/inventory不一致 | Git効果を保持、publish=`not_attempted` | 適用効果ありなら`partial` / 6 |
| clear競合 | clear=`failed`、publish=`not_attempted` | 先行効果ありなら`partial` / 6 |
| clear成功後、rename前publish失敗 | clear=`succeeded`、publish=`failed` | `partial` / 6 |
| rename後確認不能 | publish=`unknown` | `partial` / 6 |
| publish確認済み | 必要効果=`succeeded/unchanged` | `succeeded` / 0 |
| 同一record・branch・tip | 全effect=`unchanged`または空 | `unchanged` / 0 |

`failed` は `succeeded` または `unknown` を含めてはならず、それらが一件でもあれば `partial / exit 6` に昇格する。正本のeffectとexit規則にそのまま従う。

## 13. recovery表示

journal、resume、rollbackは追加しない。

partialのときだけ、v2 envelopeの `recovery` に人間向け助言を入れる。

```python
@dataclass(frozen=True)
class RecoveryAdvice:
    can_resume: Literal[False] = False
    can_rollback: Literal[False] = False
    instructions: tuple[str, ...] = ()
```

例:

```json
{
  "can_resume": false,
  "can_rollback": false,
  "instructions": [
    "Inspect the current branch, HEAD, worktree status, and active selection.",
    "Do not delete or reset the created branch automatically.",
    "After inspection, issue a new explicit work start request using the existing branch without --base."
  ]
}
```

`render_json_v2()` が現在のように常に `recovery: null` を出す実装は修正する。ただしoperation ID、旧commands、epoch等をv2へ露出しない。CLI正本ではrecoveryはnullまたは、両flag falseとinstructionsだけである。

## 14. 最小Red→Green実装順

各段階で追加したRedだけをGreenにしてから次へ進む。大規模な一括書換えは避ける。

### R1. Start入力契約

**Red**

- `--source cache` がcontext解決前に `ARGUMENT_RETIRED / exit 2`
- `--allow-stale` が同様に拒否
- `--resume` が同様に拒否
- `--expect-backend` mismatchがeffectsなし
- `--expect-current` mismatchがeffectsなし

**Green**

Startのcatalog行とparser処理だけを修正する。他leafへ拡張しない。

### R2. candidate commit snapshot

**Red**

- baseにtargetがない
- target schemaが不正
- ancestor chainが欠損
- GitHub linkageがcurrent targetと異なる
- existing branch tipにtargetがない
- detached source HEADから固定baseへ新branchを作れる
- candidate読取失敗のGit stderrが原文で返る

**Green**

checkoutせずにworkspaceとScope metadataを読むhelperを追加し、StartPlanへ固定する。

### R3. 実効依存とlive readiness

**Red**

- target、epic、initiativeのいずれかがopenでなければeffectsなし
- target dependencyがcompletedでなければeffectsなし
- ancestorが宣言したdependencyも必要
- completed childが未完了parentの代わりにならない
- 必要なGitHub ScopeだけGETする
- GitHub unknownをreadyにしない
- local-only Startはofflineでも可能
- GitHub-backed必要集合があればoffline拒否

**Green**

`domain/dependency_vnext.py` の純粋規則をcandidate graphに適用する。旧application use caseは呼ばない。

### R4. lock内pre-effect再照合

**Red**

StartLock取得時にfixtureを変化させる。

- local metadata exact bytes変更
- direct record handle変更
- existing branch tip変更
- 新branchが別processで作成済み
- cleanからdirtyへ変化
- other worktree追加
- duplicate direct target出現
- `--expect-current` の対象変更

すべてGit効果前に停止する。

**Green**

StartPlanとfresh observationを構造化比較する。比較失敗を一つのgeneric booleanへ潰さず、診断箇所を保持する。

### R5. switch-activeと限定token置換

**Red**

- A選択中にBをflagなしでStartするとeffectsなし
- `--switch-active` ありでA tokenを削除しB tokenをpublish
- 同じAの別branchはflagなしでtoken置換
- 同じA・同じbranchは既存tokenのままunchanged
- clear直前にold tokenが置換された場合、新tokenを削除しない
- clear成功後publish失敗はselection lossをpartialで返す

**Green**

`SelectionPlan` と `remove_observed(handle)` だけで実装する。scope ID指定による削除は禁止。

### R6. Git failureの事後観測

**Red**

- branch non-zeroかつref不存在
- branch timeout後にplanned ref存在
- branch結果観測不能
- checkout non-zeroでsource不変
- checkout timeout後にtarget到達
- checkout signalで別HEAD
- stdout/stderr複数行・returncode・timeout・signal
- JSON stderr空、text stderr末尾がGit原文

**Green**

`GitProcessError` を拡張し、mutation phaseごとのread-only observerを追加する。一律 `mutation=True => unknown` は廃止する。

### R7. checkout後と公開直前inventory

**Red**

- checkout後にcandidate metadataと違う
- checkout後に他WTがtargetを選択
- post-check後、publish直前に新WTが追加
- branchが別WTにcheckoutされた
- unrelated WTがunavailableになった

先行Git効果があればpartial、publishはnot_attempted。

**Green**

inventory snapshotの比較でcurrent rowの期待差分だけを許す。他WTのmetadata読取はdirect targetとancestorに限定したままにする。既存の「無関係metadataを読まない」integration testを壊さない。

### R8. publish unknown

**Red**

- stage fsync失敗はfinal recordなし、publish failed
- rename後directory fsync失敗はpublish unknown
- rename後readback不能はpublish unknown
- unknownでも `started=false`
- unknownでも自動削除・再publishなし
- old clear後unknownは一record、empty、invalidの実状態を次processがそのまま観測

**Green**

`WorkTargetPublishError.commit_state` を導入する。既存のimmutable recordとexact-handle removal試験を維持する。

### R9. concurrent Startとkill境界

**Red**

- 同cloneの二worktreeが同じtargetを同時Startし、一方だけがpublish成功
- 後続はlock取得後のinventoryで重複拒否
- branch作成直後にprocess kill
- checkout直後にprocess kill
- rename直後にprocess kill
- 次processの `active show` とGit観測が現物だけから正しい状態を返す
- `.git/spec-dock`、journal、operation recordが生成されない

**Green**

既存common-dir handleへのStartLockを公開確認まで保持する。別のlockやfile lockを追加しない。POSIXのprocess排他・owner終了時自動解放は既存試験が固定している。

## 15. fixture設計

既存 `make_workspace()` は多くの契約試験で使われるため、三階層・複数branch・依存を直接追加して複雑化しない。

新しい `tests/cli_runtime/issue413_start_fixture.py` 相当へ、次のhelperを置く。

```python
class StartWorkspaceBuilder:
    def add_scope(
        self,
        *,
        scope_id: str,
        kind: str,
        parent_id: str | None,
        backend: Literal["github", "local"],
        lifecycle: str | None,
        depends_on: tuple[str, ...] = (),
    ) -> Path: ...

    def commit(self, message: str) -> str: ...
    def create_branch(self, name: str, oid: str) -> None: ...
    def add_linked_worktree(self, path: Path, oid: str) -> Path: ...
    def publish_target(
        self,
        worktree: Path,
        scope_id: str,
        branch: str,
    ) -> SelectionHandle: ...
```

live readiness用gatewayは、呼出順ではなくcanonical `(repository, number)` で応答する。

```python
class FakeReadinessGateway:
    records: dict[tuple[str, int], GithubIssueRecord]
    calls: list[tuple[str, int]]
```

race試験では、既存のように `StartLock.__enter__` をwrapするほか、checkout後・公開直前は新しく分離したapplication helperを一回だけwrapする。productionにtest-only hookや環境変数を追加しない。

process kill試験はchild Python process内で関数をwrapし、実効果直後に `os._exit()` する。journalや専用checkpointをproductionへ追加しない。

## 16. 既存試験を守る条件

次の既存試験は削除・緩和しない。

- branch create → checkout → record publish
- dry-runがlockを取らない
- checkout失敗時にbranchを保持
- Git stderrとreturncodeの原文保持
- 既存branchは明示reuse、`--base` 禁止
- private stateのignore条件
- lock後のclean再検査
- stale他WT recordによる予約
- 同一妥当target・branchのunchanged
- 無関係な他WT metadataを読まない
- exact handle以外を削除しない
- multiple final recordをinvalid扱い
- symlink/redirect拒否
- physical identity差替え検出
- StartLockがファイルを作らずprocessを排他

現在の試験はP-06の初期縦経路を実証しているため、古い試験を消して新実装を通す方法は認めない。

## 17. 禁止事項

以下は実装案から除外する。

- GitHub GETやpromptをStartLock内へ入れる
- StartLockをcheckout後、record公開前にreleaseする
- 既存branchをresetする
- checkout失敗時に元branchへ自動的に戻す
- 作成branchを自動削除する
- dirty変更をstashする
- old direct targetを自動復元する
- stage fileやunknown recordを証拠確認なしに掃除する
- retry用operation ID、journal、receiptを作る
- `control_store`、`writer_lock`、`registry_store`、`operation_journal` を通常Startへimportする
- Git stderrを一般文へ置換する
- timeoutを「効果なし」と決めつける
- POSIX identity、flock、renameをWindows実装として扱う
- requirement、design、plan、artifactを実装都合で書き換える
- 既存試験の削除、広すぎるxfail、型エラー抑制で成功扱いする

## 18. Windows境界

P-06ではWindows native identity、named mutex、native immutable storeを実装しない。現在の `DirectoryIdentity`、`StartLock`、`WorkTargetStore` はPOSIX実装であり、Windows adapter未接続を明示している。

したがって、P-06の報告は次のように分ける。

- POSIX: P-06 Start契約の試験結果
- Windows: P-03/P-05未完了のため未検証・未達
- 全platform保証: 未達

Windows試験をPOSIX adapterのmockで通し、全platform合格と表現してはならない。

## 19. 検証コマンドと証拠

リポジトリ指示に従い、まず狭い試験を実行し、最後に全体gateを実行する。リポジトリは `uv run pytest` と `make lint` を標準検証としている。

```text
uv run pytest tests/unit/application/test_work_start_plan.py
uv run pytest tests/unit/infra/test_git_process.py
uv run pytest tests/unit/infra/test_work_target_store.py
uv run pytest tests/cli_runtime/test_issue413_work_start.py
uv run pytest tests/integration/test_issue413_observation.py
uv run pytest tests/integration/test_issue413_start_races.py
uv run pytest tests/cli_runtime/test_cli_v2_redaction.py
uv run pytest tests/cli_runtime/test_cli_vnext_contract.py
make lint
uv run pytest
```

完了証拠には最低限、次を含める。

| 証拠 | 必須内容 |
|---|---|
| CLI contract | v2 schema、started、effects、exit、recoveryを検査 |
| readiness | 三階層、target/ancestor、target/ancestor由来の実効依存 |
| branch | new、explicit existing、detached source、tip race、other-WT占有 |
| lock | 同時Startで一件だけpublish |
| selection | empty、unchanged、same-Scope replacement、switch-active |
| Git errors | non-zero、timeout、signal、stdout/stderr、事後ref/HEAD |
| publication | rename前failed、rename後unknown |
| interruption | branch後、checkout後、rename後のkill |
| persistence | journal、registry、control、operation IDが増えていない |
| platform | POSIX結果とWindows未完了を分離 |

`make lint` または全体pytestが失敗している状態を、狭い試験だけで「実装完了」と扱わない。既存の全体型検査に失敗がある場合も、失敗内容とP-06変更との関係を明示し、削除・ignore・設定緩和で隠さない。

## 20. P-06完了条件

次がすべて成立した時だけ、P-06実装完了候補とする。

1. fixed candidate commitから実効依存と必要live観測を組み立てる。
2. preflightのnetworkがlock外で完結する。
3. lock内でlocal exact bytes、branch tip、clean、全inventory、direct targetを再確認する。
4. checkout後と公開直前にinventoryを再確認する。
5. same-Scope別branchと `--switch-active` の規則が試験で区別される。
6. old token以外を削除しない。
7. Git timeout/signal/non-zeroをref/HEAD事後観測で分類する。
8. rename後確認不能をpublish unknownとして返す。
9. partialは必ず `started=false / exit 6` で、確認済み・unknown効果を隠さない。
10. raw Git stderr、stdout、returncode、timeout、signalが契約どおり保持される。
11. recoveryは人間向けinstructionsだけで、resume/rollbackはfalse。
12. journal、registry、control、rollback、stashを追加していない。
13. 既存Issue #413 Start・observation・store・identity・lock試験を維持している。
14. POSIX結果をWindows完了と表現していない。
15. requirement、design、plan、artifactを変更していない。

このブリーフ自体は実装、試験実行、レビュー、merge gateの通過を意味しない。
