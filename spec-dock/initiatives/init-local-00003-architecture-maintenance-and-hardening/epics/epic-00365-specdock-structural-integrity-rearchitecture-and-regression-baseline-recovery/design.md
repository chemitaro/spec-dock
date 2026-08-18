---
種別: 設計書（Epic）
ID: "epic-00365"
タイトル: "SpecDock Distribution Reconciliation and Recovery Architecture"
関連GitHub: ["#365"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["init-local-00003"]
---

# epic-00365 SpecDock Distribution Reconciliation and Recovery Architecture — 設計

詳細: [Design Guide](../../../../docs/authoring/design.md)

## 設計目標

Requirement の public behavior と data-preservation contract を維持しながら、distribution lifecycle を次の一方向 dependency に整理する。

```text
CLI Adapter
  -> Distribution Operation Service
       -> Distribution Contract
       -> Workspace Assessment
       -> Journaled Executor
            -> Descriptor-bound Filesystem Kernel
```

設計上の中心は「一つの巨大 transaction」ではない。read-only assessment と executable authority を分離し、各 action を exact identity と checkpoint に束縛して、部分失敗後に安全な forward recovery を可能にする。

## Current / Target

### Current: exact commit で確認した事実

- `src/spec_dock/managed_distribution.py` は `DistributionOperation = Literal["fresh", "update", "init-force", "uninstall"]`、`DistributionAction`、`DistributionPlan`、`DistributionResult`、`admit_distribution_operation()`、`build_distribution_plan()`、`apply_distribution_plan()` を持つ。
- current/historical identity、recognized workspace version、trusted consumer manifest、obsolete exact file、shortcut identity、target/root/parent snapshot を扱う read-only plan と identity-checked apply がすでに存在する。
- current tests は unknown collision、modified content、mode drift、symlink/hardlink、parent/root rebind、provider change、staging cleanup、no-replace publish、retry admission を固定している。
- `src/spec_dock/cli.py` は `_UninstallTargetIdentity`、`_UninstallAction`、`_build_uninstall_plan()`、`_apply_uninstall_plan()`、`_verify_uninstall_postcondition()` と独自の descriptor-relative recursive removal を持つ。
- update/init-force は `.distribution-retry.json`、uninstall は `.uninstall-retry.json` を使う。後者の current payload は `schema_version`、`managed_by`、`purpose` だけで、root、original intent、plan digest、checkpoint を証明できない。
- `apply_distribution_plan()` は `scaffold_applier` と `allow_blocked_scaffold_paths` を受け取り、plan action grammar の外側に scaffold mutation seam を接続できる。
- `cli.py` は private `_rename_distribution_no_replace` を import する。
- `tests/unit/infra/test_init_update.py` は fresh/current catalog byte parity、unmanaged content preservation、uninstall dry-run、`--keep-specs` / `--remove-specs`、JSON one-object output、symlink boundary、partial failure/retry guidance を検証する。

### Target

- `managed_distribution.py`、または同じ domain boundary の明示的な module 群が、Distribution Contract、Assessment、Mutation Plan、Journal、Executor、Filesystem Kernel の invariants を所有する。
- `cli.py` は adapter に縮退し、command/flag/path parse、package resource resolution、service dispatch、既存 human/JSON/exit contract への mapping だけを持つ。
- all intents は同じ action grammar と journal protocol を使う。intent policy と authority が、各 action の許可範囲と postcondition を変える。
- plan construction は常に side-effect free とし、blocker がある assessment から executable plan を作らない。
- mutation 開始後は journal と re-observation による forward recovery を正規経路とする。operation 全体の rollback は保証しない。

## 責務・Interface

### 1. CLI Adapter

入力:

- public command: `init`、`update`、`uninstall`
- public flags: `--force`、`--apply`、`--keep-specs`、`--remove-specs`、`--json`
- target path

責務:

- public surface を `OperationIntent` と explicit authority に正規化する。
- package resources と executing package version を service に渡す。
- `ProcessResult` を現行 text、JSON schema version 1、exit code へ写像する。

禁止事項:

- ownership classification
- recursive copy/remove
- journal write/transition
- staging lease cleanup
- private filesystem helper import
- operation 固有 action type の定義

### 2. Distribution Operation Service

概念 interface:

```text
execute(intent, target_root, package_contract, output_mode) -> ProcessResult
assess(intent, target_root, package_contract) -> WorkspaceAssessment
```

処理順:

1. capability と root binding を admission で確認する。
2. legacy marker または current journal を read-only に解釈する。
3. Distribution Contract と workspace observation から assessment を作る。
4. blocker がなければ root/intent/contract/assessment digest に束縛した plan を作る。
5. dry-run なら plan-derived result を返す。write を行わない。
6. apply なら journal を開始または resume し、executor を呼ぶ。
7. postcondition を再評価し、成功時だけ journal/staging を完了する。

### 3. Distribution Contract

次の authority source を一つの immutable input に正規化する。

- Desired Managed Assets
- Historical Ownership Evidence
- Managed Content Roots
- operation ごとの intent policy
- preservation policy
- postconditions
- package version
- journal protocol version と compatible-resume range

Current physical catalog と historical evidence は区別する。current catalog を historical manifest に複製しない。unknown content を parent root の membership だけで owned と判定しない。

### 4. Workspace Assessment

`WorkspaceAssessment` は read-only で、少なくとも次を持つ。

```text
root_binding
intent
contract_identity
observations[]
dispositions[]
blockers[]
diagnostic_summary
```

各 disposition は path、observed identity、ownership provenance、proposed action、reason、blocking を持つ。diagnostic は bytes、absolute path、credential を含めず、repository-relative path と stable reason code に限定する。

`blockers` が非空なら `ExecutableMutationPlan` を発行しない。safe action だけを選んで実行する分岐は禁止する。

### 5. Executable Mutation Plan と共通 action grammar

共通 action は implementation language の命名にかかわらず、次の意味を区別する。

- create: absent target に desired asset を作る
- adopt: exact desired state で mutation 不要
- replace/upgrade: proven-owned current/historical target を desired state に更新する
- remove/prune: proven-owned obsolete target を削除する
- ensure-directory: validated managed directory boundary を作る
- remove-empty-directory: owned children 除去後の空 directory だけを除去する
- preserve: authority 外または user-owned state を保持する
- block: executable authority を発行しない

plan は `root_binding`、`intent`、`authority`、`contract_identity`、ordered actions、各 action の exact precondition、expected postcondition、`plan_digest` を持つ。action の順序は deterministic とし、digest は canonical serialization から計算する。

### 6. Operation Journal

journal は retry hint ではなく durable recovery protocol とする。最低限の field は次のとおり。

```text
schema_version
protocol_version
operation_id
root_binding
intent
authority
package_version
contract_identity
plan_digest
created_at
last_checkpoint
actions[]
staging_leases[]
status
```

各 action record は repository-relative path、action kind、exact pre-action identity、expected post-action identity、checkpoint state を持つ。regular file の pre-action identity は SHA-256、mode、size、no-follow file identity を含む。symlink identity は link target と no-follow identity、directory identity は root/parent binding と mutation snapshot を用途別に持つ。

**exact pre-action SHA rule:** recovery は「historical identities の何番目」や catalog index を参照してはいけない。未完了 action は現状が journal の exact pre-action identity と一致するときだけ再実行できる。完了 action は expected post-action identity と一致するときだけ完了扱いを維持する。どちらにも一致しない状態は ambiguous として block する。

checkpoint は単調に進む。partial failure では journal と証明済み staging lease を保持し、same root / same intent / same authority / same plan / compatible protocol の package が re-observe して収束させる。postcondition 成功後だけ journal を完了・除去する。

### 7. Descriptor-bound Filesystem Kernel

filesystem mutation の唯一の owner とし、次を提供する。

- root descriptor binding と operation lock
- no-follow parent-chain open
- type-specific identity capture/revalidation
- private staging creation と lease identity
- atomic regular-file replacement
- no-replace publish
- exact symlink create/replace
- exact unlink
- bounded recursive copy/remove
- mode application
- empty-directory cleanup
- journal file atomic publish

すべての mutation は validated root descriptor と safe relative path を通す。absolute path による recursion、symlink follow、unverified hardlink mutation を許可しない。Linux/Darwin の syscall 差は kernel 内に閉じ込め、上位層へ platform-specific policy を漏らさない。

### 8. ProcessResult

内部 result は少なくとも次の状態を区別する。

- `planned`
- `completed`
- `blocked`
- `recovery_required`
- `error`

result は phase、last checkpoint、summary、actions、failed/pending paths、retry guidance、sanitized errors を持つ。CLI adapter は既存 `uninstall --json` の key、schema version 1、one-object stdout、status semantics を保持する compatibility mapper を使う。新しい internal type を理由に public JSON を変更しない。

## data / failure

### Identity の分離

一つの汎用 tuple に統合しない。

| Identity | 用途 | 必須要素の例 |
|---|---|---|
| Directory binding identity | root/parent path が同じ directory object を指すことの確認 | device、inode、file type |
| Directory mutation snapshot | child mutation 前後の再観測 | binding identity、必要な child set/digest |
| Regular-file content identity | ownership、precondition、postcondition | no-follow identity、SHA-256、size、mode、link count |
| Symlink identity | target を follow せず shortcut を確認 | no-follow identity、link target |
| Staging lease identity | cleanup authority の限定 | relative stage name、device、inode、ctime、type |

Directory の child mutation は directory ctime を変えるため、ctime をすべての binding comparison に無条件で含めない。用途ごとの identity contract を test で固定する。

### Failure semantics

- preflight blocker: write 0、journal 0、staging 0
- journal create failure: managed target mutation 0
- action failure before publish: target unchanged、証明済み staging の cleanup を試み、cleanup 不能なら lease を journal に残す
- action failure after atomic publish/checkpoint before journal flush: resume 時に pre/post identity を照合し、一意に判定できなければ block
- postcondition failure: journal retained、typed recovery state
- journal/root/intent/plan/protocol mismatch: write 0、journal/staging unchanged
- unknown stage-like sibling: cleanup しない
- authority mismatch: write 0、特に deprovision から purge への昇格を拒否

## 変更対象

### 主対象

- `src/spec_dock/managed_distribution.py`
- 必要に応じて同じ package 内に抽出する distribution domain/kernel module
- `src/spec_dock/cli.py`
- packaged distribution manifest/assets と compatibility metadata
- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- provider/dogfood/package parity tests
- Linux/macOS focused CI evidence
- README と recovery/migration guidance

### 変更しない領域

- node `.meta.json`、Epic/Issue ID、existing path/slug
- public command/flag set
- runtime feature 全般
- Full Regression failure の修復
- AI review orchestration
- Windows support
- generic transaction abstraction

## 移行・互換性・rollback

### Vertical hard cutover

D1〜D4 は対象 public flow を新 engine へ移した同じ Issue で、その flow の legacy mutation path を削除する。長期 dual mode、runtime toggle、二重 writer は作らない。D5 は残存 seam の absence と parity を確定する。

### Legacy marker

- `.distribution-retry.json` は operation、package version、root identity、phase、stage ownership を持つ。current package contract と exact root/operation を検証し、same plan を再構成できる場合だけ one-way conversion または限定 compatibility resume を許可する。
- `.uninstall-retry.json` の current payload は original specs mode、root identity、plan digest、checkpoint を持たない。この情報不足を推測で補わない。exact conversion を証明できない場合は `legacy-marker-ambiguous` として write 前に停止し、current-compatible package での完了または人間の明示的 recovery 手順を案内する。
- dual marker、malformed marker、cross-root replay、downgrade は block する。

### Code rollback と operation recovery

- 新 journal を作る前の candidate は通常の code revert が可能である。
- journal 作成後は old code が new protocol を理解できると証明されない限り、単純な code rollback を実行経路にしない。同一または compatible newer package による forward recovery を優先する。
- whole-operation rollback は non-goal である。per-action atomicity と exact pre/post identity で convergence を保証し、復元不能な ambiguous state は自動修復しない。

## testability

### Ownership / preservation matrix

missing、current identical、historical exact、wrong mode、unknown modified/user-owned、symlink、hardlink、parent symlink、root rebind、generated state、spec history、unknown sibling を intent ごとに表形式 test と end-to-end test で覆う。

### Failure / resume matrix

- blocker before journal: write 0
- journal write failure: target write 0
- staging write/publish/cleanup failure
- checkpoint write failure
- postcondition failure
- same-root/same-intent/same-plan resume convergence
- root/intent/authority/plan/protocol mismatch block
- exact pre-action SHA mismatch block
- unknown staging collision preservation
- deprovision-to-purge authority expansion rejection

### Public compatibility

- `init [--force] [path]`
- `update [path]`
- `uninstall [--apply] [--keep-specs|--remove-specs] [--json] [path]`
- current human summary intent
- JSON schema version 1、one object、existing action fields and recovery guidance
- exit code mapping

### Distribution / platform parity

provider source、checked-in dogfood、wheel、sdist、installed resources、fresh consumer の inventory/bytes/behavior を比較する。focused suite を `ubuntu-latest` と `macos-latest` で実行する。Full Regression は exact SHA ごとに再計測して attribution を分類するが、旧 artifact の件数を current assertion にしない。

## risk

| Risk | 軽減 |
|---|---|
| unified model 導入時に現行 safety test が抜ける | current tests を characterization として先に固定し、各 vertical cutover で旧 path と新 path の matrix parity を確認する。 |
| journal が rollback log と誤解される | forward recovery protocol と明記し、pre/post identity 不一致は自動復元せず block する。 |
| legacy uninstall marker の情報不足を推測する | exact conversion 条件を狭く定義し、証明不能なら fail closed とする。 |
| filesystem kernel 抽出で platform 差が隠れる | Linux/macOS の focused matrix と capability gate を必須にする。 |
| JSON adapter が schema を意図せず変える | golden payload/field/one-object tests を cutover 前後で固定する。 |
| purge authority が update/deprovision/retry へ漏れる | intent と authority を journal/plan digest に含め、negative test で昇格を拒否する。 |
| node title と metadata title の不一致を手編集で解消しようとする | `.meta.json` と path は対象外とし、canonical title は文書内だけで採用する。 |
