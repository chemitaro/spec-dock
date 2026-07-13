---
種別: 要件定義書（Epic）
ID: "epic-00312"
タイトル: "Experimental Local Workbench And Worktree Handoff"
関連GitHub: ["#312"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["init-local-00003"]
---

# epic-00312 Experimental Local Workbench And Worktree Handoff — 要件定義（何を、なぜ行うか）

## 目的（Initiative との紐づき）
- Initiative 目標 / 指標:
  - canonical state、runtime、scaffold、docs の責務境界を明確にし、temporary workaround を新たな正本へ昇格させない。
  - provider-side authority と installed consumer / dogfood surface の parity を維持する。
- この Epic が提供する能力:
  - canonical specification や durable evidence とは分離された、Git-ignored、local-only、disposable な低摩擦の一時作業領域を提供する。
  - default runtime discovery が一時ファイルを node、ADR、dependency、context、authoring source と誤解釈しない opaque boundary を提供する。
  - current worktree の一つの Initiative / Epic / Issue に閉じた一時作業領域を、明示操作によって同一 repository の別 linked worktree へ引き継げるようにする。
- 親 Initiative の `local-only は完全廃止する` との整合:
  - 廃止対象は local-only node identity、canonical state、永続的な正本、または GitHub authority の代替である。
  - 本 Epic の `.workbench/` は phase completion、review pass、Issue readiness、受け入れ証跡、永続状態のいずれにも使えない disposable scratch であり、local-only canonical contract を復活させない。

## 能力 / モデル envelope（capability / model envelope）
- 対象 capability:
  - root/pre-scope Workbench: `spec-dock/.workbench/YYYY-MM-DD/`。
  - scoped Workbench: Initiative、Epic、Issue directory の direct child `.workbench/`。
  - `.workbench/` を runtime-wide reserved opaque subtree とする default traversal policy。
  - scoped Workbench の明示的な one-shot copy。
  - provider assets/runtime から `spec-dock init/update` への experimental distribution。
- model / lifecycle boundary:
  - `.workbench/` は schema、manifest、session、catalog、promotion state、TTL を持たない。
  - Workbench は scope または worktree の削除とともに失われてよく、削除 blocker にならない。
  - durable evidence は `artifacts/`、採用済み authority は canonical specs、accepted ADR、`report.md` の EAL に残す。
- cross-Issue invariant の seed:
  - provider-side implementation が唯一の authority であり、dogfood-only duplicate implementation を作らない。
  - default discovery は `.workbench/` 内部のentryを列挙、読取、解釈しない。
  - copy は source=current worktree、scope=exactly one Initiative/Epic/Issue ID、target=exactly one same-repository linked worktree に限定する。
  - destination-only entry を保持し、同一 relative path の leaf は source wins とする。
- 対象外の model / capability:
  - 第二の artifact store、knowledge base、file catalog、session manager、backup、sync service。
  - root Workbench の automatic/bulk handoff、copy-on-worktree-create、continuous sync、copy-back。
  - Workbench content の自動昇格、分類、secret scan、archive inspection、allowlist/denylist。

## ユースケース
- 正常系:
  - モデルまたは利用者が、scope 作成前の雑多な一時資料を `spec-dock/.workbench/YYYY-MM-DD/` に置き、古い date bucket を人間判断で削除する。
  - Initiative / Epic / Issue に閉じた一時資料を、その scope directory 直下の `.workbench/` に整理せず置く。
  - worktree 作成後、利用者の明示指示により current worktree の一つの scoped Workbench を target worktree へ one-shot copy する。
  - destination に既存 Workbench がある場合、destination-only entry を残したまま source content を重ねる。
- 例外 / 運用シナリオ:
  - root Workbench から必要な file を引き継ぐ場合、command は使わず、モデルが必要な file だけを選び scoped Workbench へ通常の filesystem 操作で移す。
  - target worktree、source/target scope、または scope ID が missing / ambiguous の場合、mutation 前に失敗する。
  - source と target が同一 canonical worktree の場合、selector 表現が異なっていても失敗する。
  - copy 中に I/O failure が発生した場合、完了扱いにせず失敗を報告する。tree-wide rollback は要求しない。

## エピック要件（Epic requirements）
- E-RQ-001 Git ignore:
  - root および supported scope 配下の `.workbench/` が Git ignored になる managed rule を配布する。
- E-RQ-002 Root Workbench convention:
  - `spec-dock/.workbench/YYYY-MM-DD/` を pre-scope 作業の convention とするが、runtime は date bucket の作成、列挙、検証、期限管理、削除を担わない。
- E-RQ-003 Scoped Workbench placement:
  - Initiative / Epic / Issue directory の direct child `.workbench/` を supported scoped placement とし、内部構造を規定しない。
- E-RQ-004 Opaque reserved subtree:
  - default scanner、validator、node metadata loader、dependency / ADR / context discovery、derived-state generation、authoring source-manifest discovery は `.workbench/` 内へ descend してはならない。
  - Workbench内部のentryやscratch subtree sizeがdefault discoveryの結果・エラー・処理量へ影響してはならない。
- E-RQ-005 Authority isolation:
  - Workbench content を canonical document、node metadata、dependency、ADR、EAL、review evidence、source manifest input として解釈してはならない。
- E-RQ-006 Explicit scoped copy:
  - copy は automatic hook ではなく、利用者が command を明示実行した場合だけ発生する。
  - source は current worktree に固定し、明示 source path option を持たない。
  - scope は Initiative / Epic / Issue ID を一件、target は同一 Git repository の linked worktree を一件だけ受け付ける。
- E-RQ-007 Root exclusion:
  - copy command は root `.workbench/`、date bucket、任意 relative path、topic directory を入力として受け付けない。
- E-RQ-008 Independent resolution:
  - source worktree と target worktree で scope ID を独立解決し、source の directory name や relative path を target に機械転写しない。
  - target worktree の指定方法は既存 worktree command contract と整合させ、新しい独立したtarget identityを導入しない。
- E-RQ-009 Complete content without semantic filtering:
  - scoped `.workbench/` を通常の recursive filesystem copy として扱い、extension、language、purpose、content、text/binary、archive、`.env`、nested `.git` 等による選別を行わない。
  - allowlist、denylist、language registry、file classifier、special-entry classifier を持たない。
  - OSまたは標準copy primitiveが処理できないentryやI/O failureは通常のcopy errorとして報告し、別fileを黙って除外してsuccessにしない。
- E-RQ-010 Merge semantics:
  - destination `.workbench/` を wholesale replacement しない。
  - destination-only content は保持し、source-only content は追加し、same-relative-path content は source wins とする。
  - content-level merge は行わない。
- E-RQ-011 Copy boundary safety:
  - current source、指定scope、同一repositoryのtarget worktreeというcommand境界を外れてread/writeしてはならない。
  - source/target/scopeを解決できない場合、または同一worktreeへのcopyである場合はcopyを開始しない。
- E-RQ-012 Failure transparency:
  - 標準copyが完了しなかった場合はsuccessとして扱わず、失敗したことを利用者とmodelが識別できるようにする。
  - full transactionality、backup、rollback log は要求しない。
- E-RQ-013 Minimal management surface:
  - Workbench contentのsession、manifest、catalog、TTL、retention、promotion stateをruntime管理しない。
- E-RQ-014 No synchronization:
  - copy 後の変更を同期せず、watcher、background process、copy-back を作らない。
- E-RQ-015 Disposable deletion:
  - scope delete または worktree remove の際、Workbench の存在を blocker にせず、ともに消失してよい。
- E-RQ-016 Experimental exposure:
  - CLI help、text/JSON output、reference docs で capability が experimental、non-canonical、one-shot であることを明示する。
- E-RQ-017 Provider authority:
  - implementation authority を `src/spec_dock/assets/spec_dock/**` に置き、dogfood `spec-dock/**` は generated/installed validation surface とする。
- E-RQ-018 Update preservation:
  - `spec-dock update` は既存 root/scoped `.workbench/` content を削除・置換せず、managed runtime/assets のみを更新する。

## エピック受け入れ条件（Epic acceptance criteria）
- E-AC-001 Git ignore matrix:
  - 前提: fresh `init` または `update` 後の consumer repository。
  - 操作: root、Initiative、Epic、Issue 配下へ `.workbench/probe` を置く。
  - 期待結果: すべて Git ignored になる。
  - 観測点: `git check-ignore` と installer/update regression test。
- E-AC-002 Opaque traversal:
  - 前提: `.workbench/` 内に偽 `.meta.json`、legacy `meta.json`、dependency-like JSON、ADR-like Markdown、large/broken scratch subtree がある。
  - 操作: validate、sync、deps、context、authoring source-manifest 等の default discovery を実行する。
  - 期待結果: 内部へ descend せず、node、dependency、ADR、manifest entry、validation error を生成しない。
  - 観測点: scanner inventory に基づく focused regression tests。
- E-AC-003 Root separation:
  - 前提: root `.workbench/YYYY-MM-DD/` に file がある。
  - 操作: CLI help と scoped copy interface を確認する。
  - 期待結果: root bulk-copy route がなく、root/date bucket を scope として選択できない。
  - 観測点: parser/help/error test。
- E-AC-004 Explicit scoped handoff:
  - 前提: current と target linked worktree に同一 scope ID があり、source scoped Workbench が存在する。
  - 操作: scope ID と target を明示して copy する。
  - 期待結果: target scope direct child `.workbench/` に source tree が配置される。
  - 観測点: CLI text/JSON output と target filesystem。
- E-AC-005 Target and scope resolution:
  - 前提: target を ID、absolute path、basename で参照でき、missing/ambiguous/same-worktree case もある。
  - 操作: 各 selector で copy を試みる。
  - 期待結果: 既存 worktree command contract と整合するtargetを選び、missing、ambiguous、same-worktree、missing scopeはcopy開始前に明示失敗する。
  - 観測点: application/CLI tests。
- E-AC-006 Merge contract:
  - 前提: source-only、destination-only、same-relative-path contentが混在する。
  - 操作: copy を実行し、同一入力で再実行する。
  - 期待結果: destination-only を保持し、source-only を追加し、same-relative-path contentはsource winsとなり、再実行結果は同一になる。
  - 観測点: target tree comparison test。
- E-AC-007 Content opacity:
  - 前提: binary、archive、`.env`、nested `.git`、多様な言語/設定fileを含む。
  - 操作: copy を実行する。
  - 期待結果: command独自の内容選別や解析をせず、標準filesystem copyの結果として配置される。
  - 観測点: fixture comparison と content非表示のoutput test。
- E-AC-008 Copy failure transparency:
  - 前提: OS/標準copy primitiveが処理できないentryまたはI/O conditionがある。
  - 操作: copy を試みる。
  - 期待結果: failureをsuccessとして隠さず、独自のfile分類・除外へfallbackしない。
  - 観測点: adapter fault-injection test。
- E-AC-009 No managed lifecycle or synchronization:
  - 前提: copy完了後にsource/targetのcontentが変更され、古いroot date bucketも存在する。
  - 操作: Workbench command surfaceとbackground processを確認する。
  - 期待結果: watcher、sync、copy-back、TTL cleanup、catalog更新は動作せず、root cleanupは人間判断のままである。CLI help、successful/failed text output、JSON output、reference docsはexperimental、non-canonical、one-shotであることを明示する。
  - 観測点: CLI help/text/JSON tests、process absence、docs/spec alignment review。
- E-AC-010 Disposable deletion:
  - 前提: Initiative / Epic / Issueまたはlinked worktree内にnonempty `.workbench/` が存在する。
  - 操作: 対象scopeのdelete、またはworktree removeを明示実行する。
  - 期待結果: Workbenchの存在がdeletion blockerにならず、対象とともに消失してよい。Durable evidenceの自動promotion/backupは発生しない。
  - 観測点: delete/worktree removal regression testとdocs/spec alignment review。
- E-AC-011 Update and parity:
  - 前提: 既存 Workbench content を持つ consumer と dogfood repository。
  - 操作: package install/update と provider-to-dogfood refresh を行う。
  - 期待結果: contentを保持し、provider runtime/assets と installed/dogfood surface が一致する。
  - 観測点: package-data、init/update preservation、inventory parity test。
- E-AC-012 Final quality gate:
  - 前提: すべての implementation Issue が完了している。
  - 操作: focused/full tests、static analysis、manual worktree handoff、spec/code review を行う。
  - 期待結果: Epic requirements/AC の evidence が report に trace され、blocking finding がなく、mergeable Epic PR が用意される。
  - 観測点: final quality Issue report と Epic EAL/OAL/AC closure。

## 証跡の権限境界（artifact authority）
- raw evidence として扱うもの:
  - `artifacts/`:
    - clarification interviews、ChatGPT transcript、scanner inventory、manual test log、review output。
- canonical authority として扱うもの:
  - `requirement.md`: 採用済み capability、scope、要件、受け入れ条件。
  - `design.md`: layer boundary、command contract、traversal/copy mechanism、error/output contract。
  - `plan.md`: Issue分割、依存、verification/final quality gate。
  - accepted ADR: 将来 hard-to-reverse な共有storage/authority/promotion modelを採用する場合のみ。
  - `report.md` Evidence Adoption Ledger: evidence の adopted/refined/rejected/deferred disposition。

## スコープ
- 必須:
  - provider `.gitignore` / installer fallback。
  - default recursive discovery callsite の inventory と `.workbench` traversal pruning。
  - experimental scoped copy の layered runtime implementation と tests。
  - init/update preservation、dogfood parity、reference docs、final quality gate。
- 禁止:
  - root Workbench copy command、automatic/bulk copy、sync/copy-back。
  - content allowlist/denylist、secret scan、archive extraction、session/manifest/catalog/TTL。
  - Workbench を canonical/durable authority として扱うこと。
- 対象外:
  - arbitrary directory/cross-repository copy。
  - owner、ACL、xattr、device semantics の cross-platform fidelity。
  - raw ZIP quarantine/promotion policy の変更。
  - unrelated installer/scanner refactor。

## 非機能要件
- 性能:
  - default discovery は `.workbench` root で prune し、scratch subtree size に比例して内部を走査しない。
  - copy/merge は source tree に対して線形を基本とし、hash manifest/databaseを導入しない。
- 信頼性 / 一貫性:
  - concurrent mutation がなければ同一copyの再実行は idempotent。
  - directory全体のatomic transactionは要求しない。copy failureをsuccessとして扱わない。
- セキュリティ:
  - commandがcurrent source、指定scope、同一repositoryのtarget worktreeという境界外を意図的にread/writeしない。
  - outputにfile contents、secret-like value、全entry listingを含めない。
  - content安全性を保証する機能ではないことを明示する。
- 運用:
  - Workbenchは消失可能であり、必要な証跡は利用者/モデルが`artifacts/`へ移す。
  - root date bucketのcleanupは人間判断とし、自動retentionを導入しない。

## 依存 / 影響範囲
- 影響する component:
  - `src/spec_dock/assets/spec_dock/.gitignore`、installer fallback/package data。
  - runtime CLI/parser/registry、commands、application、ports、infra、presentation。
  - node/legacy metadata、validate/sync/deps/context、authoring source-manifest 等の default traversal。
  - provider/dogfood parity、reference docs、init/update tests。
- 外部依存:
  - Git linked worktree records と既存 target resolver semantics。
  - 新規 third-party dependency は導入しない。
- 互換性:
  - existing canonical files/nodes/APIを変更せず、`.workbench` pathを新たなreserved subtreeとする。
  - `.workbench` 内を意図的にcanonical discoveryへ混入させていた非契約運用は非対応となる。

## 後続 Issue seed
- parent requirement trace:
  - Foundation Issue: E-RQ-001–005、E-RQ-013、E-RQ-015、E-RQ-017–018。
  - Copy Issue: E-RQ-006–012、E-RQ-014、E-RQ-016。
  - Final quality Issue: 全要件/AC、distribution、docs、parity、PR delivery。
- acceptance seed:
  - Foundation: E-AC-001–002、E-AC-010–011 のscanner/delete/update部分。
  - Copy: E-AC-003–009 のroot exclusion/copy/CLI部分。
  - Final: E-AC-011–012 と全AC再検証。
- allowed local delta:
  - exact command spelling、error code/result field naming、adapter granularity、test fixture detail。
- forbidden parent boundary changes:
  - root copy、automatic sync、content filtering、second storage/catalog、dogfood-only implementation。
- expected evidence:
  - scanner callsite inventory、focused/full test log、Git-ignore matrix、manual two-worktree handoff、provider/dogfood inventory、review findings/disposition。
- suggested grade:
  - Foundation: M。
  - Copy: M。
  - Final quality/PR: M。

## 未確定事項
- 現時点で product decision を妨げる未確定事項はない。
- exact CLI spelling、error code、port分割は design / Issue-local delta とし、親境界を変更しない範囲で確定する。
