---
種別: 設計書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

implementation architectureを追加するのではなく、D1〜D4のtarget architectureが唯一のproduction pathであることをmechanical evidenceで固定する。code boundary、package projection、public semantics、platform behavior、documentationを同じcandidate SHAへ束縛する。

## Current / Target

### Current baseline at Epic start

- `cli.py`にはprivate rename import、uninstall action/plan/apply/postverify、recursive removal、separate marker writerがある。
- `managed_distribution.py`にはcommon distribution plan/applyとcallback/fallback seamがある。
- provider CIはUbuntuで実行され、current attachmentのworkflowではmacOS jobがない。
- package/dogfood parity testsは既に複数surfaceを検査するが、new journal/kernel/operation assetsを含むcomplete parityはD1〜D4後に再固定が必要。

### Target

- domain dependency graph:

```text
cli.py -> operation service -> contract/assessment/executor -> filesystem kernel
```

- CLIからkernel/private helperへのdirect edgeなし。
- service外writerなし。
- current/legacy marker readerはmigration-only allowlistに限定し、writer/resume authorityはnew journalだけ。
- source package asset、dogfood projection、built artifacts、fresh installed behaviorが同一contract。
- Linux/macOS evidenceがrequired gate。

## 責務・Interface

### Structural absence contract

AST/import/symbol testsは少なくとも次を検査する。

- `cli.py`がprivate distribution symbolをimportしない。
- CLIに`_UninstallAction`またはoperation固有action typeがない。
- CLIにrecursive filesystem mutation helper、journal writer/transition、staging cleanupがない。
- production serviceが`scaffold_applier`、`allow_blocked_scaffold_paths`、legacy uninstall plan/applyへcallしない。
- `.distribution-retry.json` / `.uninstall-retry.json` writerがない。readerが残る場合はmigration-only read pathとfail-closed testを持つ。
- all intent dispatchがsingle service entrypointへ到達する。

Testはline countやname heuristicだけに依存せず、AST/import/callable referenceとruntime spyを組み合わせる。

### Package parity model

Canonical inventoryをprovider physical install rootとvalidated distribution manifestから導出し、次surfaceを比較する。

- source provider resources
- checked-in dogfood projection
- wheel contents
- sdist contents
- installed package resources
- fresh consumer output

比較対象:

- relative path set
- regular file bytes/SHA-256
- executable/mode contract
- symlink target
- manifest/protocol metadata
- absence of stale legacy writer/assets

Build contextにseeded stale outputsを置き、wheel/sdistがそれを誤収録しないnegative testを維持する。

### Platform evidence

focused distribution suiteをGitHub Actions等で`ubuntu-latest`と`macos-latest`に対して同じcommit SHAで実行する。matrixはfilesystem kernel、journal crash/resume、symlink/hardlink/root-rebind、no-replace publish、package fresh init/uninstallを含む。

platform-specific implementationはkernel内に閉じ、result/reason semanticsは共通とする。capability不足caseはwrite-zero diagnostic testを持つ。

### Public semantic parity

pre-Epic characterization/golden fixturesとcandidateを比較する。

- parser commands/flags/mutual exclusion
- success/error exit code
- dry-run/apply semantics
- unknown/modified preservation
- text summary essentials
- JSON schema version 1、keys、actions、one-object output、sanitization
- retry authority/mismatch behavior。ただしlegacy internal marker schemaのbyte compatibilityはpublic parity対象外。

### Documentation parity

canonical Requirement/Design/Planとaccepted ADRをauthorityとし、README/recovery docs/HTMLはimplementation names、commands、failure behaviorに追随する。HTMLはauthorityではなくexplanatory projectionである。

## data / failure

Evidence recordは次を持つ。

```text
candidate_sha
surface_or_platform
command
runtime_versions
result
artifact/inventory digest
failure attribution
```

Full Regression comparisonはpre-Epic exact baseline SHAとcandidate SHAに別々のraw resultを持ち、旧artifact countをcopyしない。failureをstable identity/root causeで分類し、Epic changeにattributableなnew failureだけをD5 blockerとする。

## 変更対象

- source structural cleanup
- AST/import/dependency/runtime route tests
- package inventory/byte parity tests
- `.github/workflows/provider-ci.yml`等のfocused macOS evidence path
- README/recovery/migration docs
- full regression comparison evidence generation

D1〜D4 public semantics、node metadata、unrelated regression codeは変更しない。

## 移行・互換性・rollback

- residual legacy readersはexplicit allowlistとremoval conditionを持つ。writer/authority routeは残さない。
- structural cleanupはbehavior tests green後に行い、dead seam removalでunexpectedconsumerが見つかった場合はprivate APIのpublic guaranteeを新設せずrepository内callersを移行する。
- release rollback前にactive new-journal consumerのcompatible forward recoveryを確認する。
- package parity failure時はreleaseを止め、surface-specificmanual patchではなくcanonical provider source/projectionを修正する。

## testability

- AST/import/symbol/call-route absence tests
- runtime spy: each public command invokesone service
- no legacy marker writer
- source/dogfood/wheel/sdist/installed/fresh inventory/bytes/modes/links
- stale build-context negative test
- Linux/macOS same-SHA matrix
- public parser/text/JSON/exit golden tests
- ownership/preservation/failure/resume all-intent matrix
- docs command/name/static link check
- exact baseline/candidate Full Regression attribution

## risk

- dead codeをharmlessとして残すrisk:production source absenceをexit conditionにする。
- macOS flaky/evidence drift:same SHA、pinned commands、rerun policy、raw logを記録する。
- package parity testがinventoryだけでbehaviorを見落とす:fresh consumer end-to-end operationを含める。
- Full Regression unrelated failureにscopeが引かれる:attribution-only contractを守る。
- D5でnew behaviorを決めるrisk:gapはowner Requirement/Designへ戻す。
