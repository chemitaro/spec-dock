---
種別: 設計書（Issue）
ID: "iss-00315"
タイトル: "Experimental Workbench Ignore And Opaque Traversal Foundation"
関連GitHub: ["#315"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00315 Experimental Workbench Ignore And Opaque Traversal Foundation — Issue 設計書（Standard）

## 1. 設計判断と等級

Assurance classification は `standard`。公開CLIやnode schemaは変更せず、既存scaffoldへignored scratch boundaryを加える局所変更である。一方、installer、runtime discovery、authoring manifestへ横断的に影響するため、単なるdocs/template変更として扱わない。

- `[N]` `.workbench`はexact path componentだけをreserved boundaryとする。
- `[N]` default semantic discoveryはboundary自体を認識しても、そのdescendantを列挙・stat・read・parse・hashしない。
- `[N]` explicit user operationやknown generated treeを一律にpruneしない。
- `[N]` provider assetを正本とし、dogfood treeはinstalled verification surfaceとする。
- `[N]` Workbenchはnon-canonical、Git-ignored、disposableであり、lifecycle/catalog/promotionを追加しない。

Strictへの引き上げ条件は、公開CLI/schemaの変更、migration、credential-aware処理、既存scope delete semanticsの破壊が必要になった場合とする。

## 2. 正本と根拠

| 種別 | 参照 | このIssueへの意味 |
|---|---|---|
| Issue requirement | `requirement.md` | RQ-315-001–010、AC-315-001–009 |
| Epic requirement/design/plan | `../../../requirement.md`, `../../../design.md`, `../../../plan.md` | DS-001とW1境界 |
| Accepted ADR | `../../../artifacts/20260713t031808z-adr-template-free-artifact-import-and-blank-filename-coexistence.md` | Workbenchはraw input laneでcanonical authorityではない |
| ChatGPT evidence | `artifacts/20260713t044108z-research-chatgpt-5-6-pro-issue-planning-evidence.md` | callsite候補、段階実装、リスク分析 |
| Provider source | `src/spec_dock/assets/spec_dock/**` | 実装正本 |
| Dogfood surface | `spec-dock/**` | update後の配布確認 |

優先順位は ADR / Initiative / Epic → Issue requirement → 本design → plan → evidence とする。

## 3. 現状と責任配置

現在、`.workbench`専用のignore/opaque contractは存在しない。metadata discovery以外にも、独立したrecursive resolverがnode-like contentを探索するため、単一helperの修正だけでは閉じない。

| 責任 | 現在の対象 | 目標責任 |
|---|---|---|
| Git ignore | `src/spec_dock/assets/spec_dock/.gitignore`, `src/spec_dock/cli.py` fallback | 全supported placementの`.workbench/`をignore |
| Node discovery | runtime `infra/fs_repo.py` | exact componentをtop-down prune |
| Assurance issue discovery | runtime `infra/assurance_store.py::_issue_records` | `**/.meta.json`探索からWorkbenchを除外 |
| Installer recovery | `src/spec_dock/cli.py::_resolve_manifest_target_dir` | Workbench metadataを候補にしない |
| Delete fallback | runtime `application/delete_node.py::_matching_target_directories` | Workbench metadataを候補にしない |
| Delegated authoring scope | runtime `application/delegated_authoring.py::_resolve_scope_dir` | Workbench metadataを候補にしない |
| Authoring sources | runtime `domain/authoring_pack/source_manifest.py`およびpreflight | exact Workbench inputをread前にrejectし、parent selectionではsubtreeをprune |
| Update | installer managed asset copy | existing Workbench bytesを保持 |

実装前inventoryでは `rg` と本文確認によりrecursive callsiteを次の3分類へ固定する。

1. `default-semantic-discovery`: prune必須。
2. `explicit-user-operation`: 意図的なtree操作として維持。
3. `generated-known-tree`: 既知の生成物だけを扱うため原則維持。

## 4. 設計差分

### DES-315-001 Ignore contract

Provider `.gitignore`にscoped patternを加え、installer fallbackも同じ結果を生成する。patternはroot/Initiative/Epic/Issue direct-child placementを包含し、`.workbench-notes`等のnear-nameをreserved扱いしない。

### DES-315-002 Shared exact-component predicate

Runtime内ではpath component列にexact `.workbench`があるかを判定する小さなpredicateを再利用してよい。ただし、filesystem traversal自体は各責任の既存構造に沿ってtop-down pruneする。substring、suffix、case-foldingは行わない。

### DES-315-003 Node and graph isolation

`fs_repo`のcurrent/legacy metadata discoveryはWorkbench directoryへ降りない。そこから組み立てられるvalidate/sync/deps/active/context graphは追加filterなしで同じ結果を継承する。Workbench外のmalformed metadata errorは維持する。

### DES-315-004 Independent resolver isolation

common readerを迂回するinstaller recovery、delete fallback、delegated scope resolver、assurance issue discoveryはそれぞれの探索点で同じexact-component contractを守る。全`rglob`の機械的置換は行わない。

### DES-315-005 Authoring isolation

- exact Workbench file、directory、descendantをexplicit sourceにした場合はcontent access前にstable blockerを返す。
- Workbenchのparent directoryをsourceにした場合は、そのsubtreeをmanifest traversalからpruneする。
- blockerはpath/body/secret-like contentsを展開しない。
- publish/ZIP生成、hashingはblocker解消前に開始しない。

### DES-315-006 Explicit operations preservation

Scope delete、worktree remove、template/pack generation、explicit copy等はsemantic discoveryではない。Workbench専用のbackup、promotion、confirmation、blockerを加えず、既存対象scope/worktreeと共に削除される。

### DES-315-007 Update preservation and parity

Installer updateはmanaged provider assetsのみを配布し、既存のunmanaged `.workbench/**`を削除・上書きしない。fresh initとupdateの双方でignore/runtime contractを確認し、dogfood projectionは通常のprovider→consumer update経路で同期する。

## 5. 要件追跡

| Requirement / AC | Design |
|---|---|
| RQ-315-001, AC-315-001 | DES-315-001 |
| RQ-315-002–004, AC-315-002–003 | DES-315-002, DES-315-003 |
| RQ-315-005, AC-315-004 | DES-315-004 |
| RQ-315-006, AC-315-005 | DES-315-005 |
| RQ-315-007–008, AC-315-006–007 | DES-315-006 |
| RQ-315-009, AC-315-008–009 | DES-315-007 |
| RQ-315-010 | 全設計差分のscope guard |

## 6. 失敗・互換性・性能

- Workbench外の既存error semanticsは変更しない。
- unreadable/large/broken descendantを用いたsentinel testで、prune後にdescendant accessがないことを検証する。
- traversal complexityはWorkbench body sizeに比例させない。
- 新dependency、persistent metadata、migrationは追加しない。
- exact source rejectionのerror token/textは既存authoring blocker表現へ合わせ、planでfocused testを固定する。

## 7. 変更禁止領域

- Issue 316のcopy command、merge semantics。
- Issue 317のArtifact import。
- Issue 318のworkflow/skill preservation rule。
- TTL、catalog、secret scanner、auto cleanup、Workbench自体のGit管理。
- Public node/artifact schema。

## 8. 検証設計

| Verification ID | 保証 | レベル |
|---|---|---|
| V-315-001 | init/update ignore matrixとnear-name | installer/CLI test + `git check-ignore` |
| V-315-002 | current/legacy metadataとgraph opacity | runtime unit/CLI regression |
| V-315-003 | descendant no-access | sentinel/characterization test |
| V-315-004 | independent resolver parity | focused unit tests |
| V-315-005 | source reject/prune before hash/read | authoring unit tests |
| V-315-006 | delete/remove explicit semantics unchanged | characterization/CLI tests |
| V-315-007 | update preserves sentinel bytes and dogfood parity | installer update test + diff inspection |

## 9. Plan handoff

Planはinventory/baseline、ignore、node/graph、independent resolvers、authoring、delete/remove characterization、update/parity、docs、final gateの順で進める。各stepは単独commit候補とし、fresh code reviewerを通過してから次へ進む。未列挙callsiteが見つかった場合、3分類へ追加してから実装し、scope拡張が必要ならplanを再レビューする。

## 10. Open questions

Blocking open questionはない。helper名、error token、test名は既存patternに合わせて実装時に決定できる。
