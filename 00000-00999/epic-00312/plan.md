---
種別: 計画書（Epic）
ID: "epic-00312"
タイトル: "Experimental Local Workbench And Worktree Handoff"
関連GitHub: ["#312"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00312 Experimental Local Workbench And Worktree Handoff — 計画（Issue と実施順序）

## この計画で閉じる E-RQ / E-AC
- 全E-RQ-001–018とE-AC-001–012を3 Issue候補で閉じる。
- W1はignore/opaque boundary/delete/update foundation、W2はscoped copy、W3はdistribution/docs/full quality/Epic PRを所有する。

## 課題分割方針（Issue slicing policy）
- 分割原則:
  - Runtime-wide safety foundationをcopy commandより先に完成させる。
  - Copy commandをprovider-side layered implementationとして独立検証する。
  - Multi-Issue implementation Epicのため、全implementation Issueに依存するfinal quality/mergeable PR Issueを最後に置く。
- Epic classification: `multi-issue implementation`
- final quality Issue policy:
  - required: yes
  - final quality issue id: Issue node作成後に確定するW3。
  - dependency-on-all-implementation-Issues: W3 depends on W1 and W2。
  - intermediate deferred PR delivery policy:
    - W1/W2はreviewed Epic planに基づきper-Issue PRを作らず、W3へPR deliveryをrelayできる。
    - W1/W2 reportにはW3 ID、dependency edge、no-per-Issue-PR理由、merge-prepared未主張、remaining final PR gateを記録する。
    - W3はdeferred PR deliveryを使えず、Epic-level quality/repair/manual test/push/mergeable PRを所有する。

## 共通Issue handoff package
- parent trace:
  - `requirement.md` E-RQ/E-AC、`design.md` DS-001–003とcross-Issue invariants。
- allowed local delta:
  - exact symbol/file placement、CLI option/error/result names、adapter/test fixture details。
- forbidden parent boundary changes:
  - root bulk copy、automatic/sync/copy-back、content classifier、secret scan、manifest/catalog/TTL、cross-repository copy、dogfood-only implementation。
- constraints:
  - provider-side authority first。Dogfood surfaceを直接primary implementationにしない。
  - `.workbench/`はnon-canonical/disposableで、evidence/readinessに使わない。
  - standard filesystem copyを単純に使い、extension/language/content/special-entry classifierを作らない。
- draft lifecycle:
  - ChatGPT 5.6 Pro transcript内のW1/W2/W3 draft requirementはevidence-only。
  - HumanがIssue分割を承認後にIssue nodeを作成し、各Issue planningが最新repository stateとprior Issue resultを基にcanonical requirement/design/planへ採否・再記述する。
  - Issue node作成だけではexecution-readyにならない。Fresh Issue-level `spec-reviewer` passが必要。
- relevant evidence:
  - 8件のclarification evidence。
  - `artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md`。
  - Epic canonical requirement/design/report。

## W1候補 — Experimental Workbench Ignore And Opaque Traversal Foundation
- 目的:
  - `.workbench/`をGit-ignored reserved subtreeとし、default semantic discoveryが内部を列挙・読取・解釈しない基盤を作る。
- scope:
  - provider `.gitignore` assetとinstaller fallback/package data。
  - Recursive callsite inventoryと`default-semantic-discovery` / `explicit-user-operation` / `generated-known-tree`分類。
  - Node/legacy metadata、validate/sync/deps/ADR/context/derived-state、authoring source selectionのopaque boundary。
  - Exact `.workbench` file/dirをauthoring semantic sourceとして拒否。
  - Scope delete/worktree removeでblockerを追加しないこと、update preservation。
- non-scope:
  - Copy command、root helper、content classification、catalog/TTL、final docs/PR。
- closes:
  - E-RQ-001–005、013、015、017–018。
  - E-AC-001–002、010、E-AC-011のupdate-preservation foundation。
- dependencies: none（Epic requirement/design passのみ）。
- deliverables:
  - Provider ignore/traversal changes、inventory artifact、focused tests、W1 report、W3へのdeferred PR evidence。
- acceptance:
  - 4 placementがGit ignored。
  - Fake metadata/ADR/dependency/source contentをdefault discoveryが読まない。
  - Exact Workbench authoring sourceをrejectする。
  - Workbench size/broken contentがdefault discovery処理量/結果へ影響しない。
  - Delete/removeはWorkbenchでblockせず、updateはcontentを保持する。
- verification:
  - node/legacy loader、validate/sync/deps/context/source-manifest、`git check-ignore`、init/update/delete/worktree remove、existing regression、static analysis。
- suggested grade: M / Standard。

## W2候補 — Experimental Scoped Workbench Copy And Source-Wins Merge
- 目的:
  - Current worktreeの一つのInitiative/Epic/Issue Workbenchを、一つのsame-repository target worktreeへ明示one-shot copyする。
- scope:
  - `workbench copy` parser/registry/commands/application/ports/infra/presentation。
  - Existing target resolver semanticsの共有。
  - Source/target scope ID独立解決。
  - `no_source` failure/no target mutation。
  - Standard recursive filesystem copy、destination-only保持、source wins。
  - Source symlink非dereference、destination ancestry containment。
  - Text/JSON error/resultとexperimental marker。
- non-scope:
  - Root copy、automatic hook、cross-repo、content classification、secret scan、sync/copy-back、tree-wide rollback、final PR。
- closes:
  - E-RQ-006–012、014、E-RQ-016のCLI help/text/JSON surface。
  - E-AC-003–008、E-AC-009のCLI help/text/JSON / no-sync behavior。
- dependencies: W1 complete。
- deliverables:
  - Provider-side layered runtime、focused tests、manual two-worktree fixture/result、W2 report、W3へのdeferred PR evidence。
- acceptance:
  - Source=current、one scope ID、one target。
  - Root選択不可、missing/ambiguous/stale/same-worktree/scope missing/no_sourceはcopy開始前error。
  - Target resolver parityとsource/target independent scope resolution。
  - Destination-only保持、source wins、repeat-run idempotency。
  - Python/config/binary/archive/`.env`/nested `.git`等を分類なしでcopy。
  - Source symlinkをdereferenceせず、target scope外writeを防ぐ。
  - Copy failureをsuccessにせず、contentをoutputしない。
  - Help/success text/failure text/JSONでexperimental/non-canonical/one-shotを明示。
- verification:
  - New focused application/CLI/infra tests、existing worktree/validate regression、manual linked-worktree handoff、static analysis。
- suggested grade: M / Standard。

## W3候補 — Installed Runtime, Dogfood Parity, Final Quality And Mergeable PR
- 目的:
  - W1/W2をinstalled consumer/dogfoodへ配布し、docs、full quality、Epic closure、mergeable PRを完成する。
- scope:
  - Provider/dogfood synchronization、package-data/fresh init/existing update smoke。
  - Existing root/scoped Workbench preservation。
  - CLI/reference docs、root manual-selection、experimental/non-canonical/no-sync guidance。
  - Focused/full tests、static analysis、manual scenario、review/repair loop。
  - Epic EAL/OAL/AC closure、push、Epic PR、merge preparation。
- non-scope:
  - 新product semantics、copy redesign、root helper、secret scan、general installer/scanner refactor。
- closes:
  - E-RQ-016のreference docs surface、E-AC-009のreference docs alignment。
  - E-AC-011のdistribution/parity closure、E-AC-012、全E-RQ/E-ACの最終再検証。
- dependencies: W1 and W2 complete。
- deliverables:
  - Installed runtime/assets、dogfood mirror、docs、package/init/update evidence、full quality evidence、final reports/ledgers、mergeable Epic PR。
- acceptance:
  - Fresh installとexisting updateでcapability利用可能、Workbench bytes保持。
  - Provider/dogfood inventory一致（generated cache等のdocumented exceptionを除く）。
  - Full pytest/static analysis/manual handoff成功。
  - Docs/help/outputがexperimental/root manual/no sync/no canonical authorityを説明。
  - Final `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`にblocking findingなし。
  - Epic AC coverageがreportへtraceされ、mergeable PRが用意される。
- suggested grade: M / Standard final quality。

## 課題リレー依存（Issue relay dependency）

```text
W1 Ignore/Opaque Foundation
  -> W2 Scoped Copy
       -> W3 Distribution/Docs/Final Quality/Epic PR

W1 -------------------------------------------> W3
```

- parallelizable lanes:
  - Implementationは原則直列。W1のinventory中にW3 docs outlineを作ることは可能だが、canonical docs更新はW2 contract確定後に行う。
- blocker/gate:
  - W1 passなしでW2開始不可。
  - W1/W2 closureとdependency evidenceなしでW3 final verification不可。

## 統合チェックポイント
- G1 分解レビュー:
  - HumanがW1/W2/W3のscope、順序、final quality ownershipを明示承認するまでIssue nodeを作らない。
- G2 W1 foundation:
  - Scanner inventory、opaque traversal、ignore/delete/update tests、fresh Issue reviewer pass。
- G3 W2 copy:
  - Layered runtime、unfiltered copy、containment、text/JSON、manual handoff、fresh Issue reviewer pass。
- G4 W3 rollout/docs:
  - Provider/dogfood/package parity、docs impact closure、full regression。
- G9 Final Epic review:
  - QA/code/spec reviewer repair loop、Epic AC/EAL/OAL closure、PR delivery/merge preparation。

## 品質ゲート
- Narrow checks first, then full suite。
- Runtime/code/test/scaffold stepはper-step `code-reviewer` pass。
- Docs-only stepは`spec-reviewer` docs/spec alignment pass。
- W1/W2はreviewed relay policyによりPRをdeferできるが、commit/evidence/clean-tree gateは省略しない。
- W3はfull `qa-reviewer` / issue-wide `code-reviewer` / `spec-reviewer` passを必須とし、deferred PRを使用しない。

## ロールアウト / ドキュメント影響
- Provider asset/runtimeを実装authorityとし、local dogfood `spec-dock update .`相当でconsumer projectionをrefreshする。
- Reference docsにplacement、root date convention/manual selection、scoped copy、source-wins、no sync、disposable/evidence authority、experimental statusを記載する。
- Migration noteは既存`.workbench` contentをpreserveし、canonical migrationを行わないことを明示する。

## 課題準備完了条件（Issue readiness criteria）
- Human-approved Issue decompositionとcreated Issue ID/dependency edge。
- Issue-local draft evidenceの採否をEALへ記録。
- Canonical Issue requirement/design/planをIssue planningで作成。
- Fresh Issue `spec-reviewer: pass`、grade evidence、executable steps、verification/reviewer focus。
- Handoff-readyとexecution-readyを混同しない。

## 最終完了条件
- E-AC-001–012がobserved evidenceでPass。
- Provider/dogfood/installed consumer parityとupdate preservationがPass。
- Docs impact resolved。
- W3 final QA/code/spec review、PR delivery、merge preparationがPass。
- Epic reportのEAL/OAL/AC、Issue/PR links、follow-upが閉じ、unresolved blocked/stale entryがない。

## 未確定事項
- Product/architecture/Issue slicingを妨げる未確定事項はない。
- Issue IDはHumanが本planの3-Issue分割を承認した後に作成して確定する。
