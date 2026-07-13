---
種別: 要件定義書（Issue）
ID: "iss-00316"
タイトル: "Experimental Scoped Workbench Copy And Source Wins Merge"
関連GitHub: ["#316"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312", "init-local-00003"]
---

# iss-00316 Experimental Scoped Workbench Copy And Source Wins Merge — Issue 要件定義

## 目的
- Current worktreeの一つのInitiative/Epic/Issue scopeにある`.workbench/`を、同一repositoryの一つのtarget worktreeへ、利用者が明示的に一度だけcopyできるようにする。
- 内容を分類・選別せず、target固有fileを保持しつつ同一relative pathではsourceを優先する、単純で再実行可能なhandoffを提供する。

## 親trace
- Epic requirements: E-RQ-006–012、E-RQ-014、E-RQ-016のCLI help/text/JSON surface。
- Epic acceptance: E-AC-003–009。
- Epic design: DS-002 Scoped one-shot Workbench copy。
- 依存: Issue 315のignore/opaque traversal foundationが完了していること。
- 継承する不変条件:
  - Provider authorityは`src/spec_dock/assets/spec_dock/**`。Dogfood `spec-dock/**`はinstalled verification surface。
  - `.workbench/`はnon-canonical、disposableであり、copy成功はsync、promotion、adoption、review readinessを意味しない。
  - Root Workbenchは一括copyせず、必要なfileだけをagentが手動選択する。

## 観測可能な成果
- `workbench copy`がcurrent worktreeをsourceとして、scope ID一つとtarget worktree selector一つを受け取る。
- Target selectorは既存worktree commandと同じstable ID、absolute path、unambiguous basenameの意味論を共有する。
- Sourceとtargetは各worktreeのnode inventoryから同じscope IDを独立解決するため、branch間でscope directory slugが異なってもtarget側の正しいdirectoryへ配置される。
- Source scoped `.workbench/`がない場合は`no_source`として失敗し、target filesystemを変更しない。
- Copyはrecursiveで、destination-only entryを保持し、same-relative source entryを優先し、source/targetの同時変更がなければ再実行後の結果が同じになる。
- Python、設定、binary、archive、`.env`、nested `.git`、その他のentryをextension・language・contentで判定せず扱う。
- Source descendant symlinkはdereferenceせずlink objectとして扱い、destination ancestryを経由したscope外writeを行わない。
- Help、text、JSONはexperimental、non-canonical、one-shot、no-syncの境界を示し、file bodyやtree全entryを出力しない。

## Issue要件
- RQ-316-001 Explicit command contract:
  - Current worktreeを暗黙sourceとする明示的な`workbench copy` commandを提供する。
  - 入力はInitiative/Epic/Issueのfull scope ID一つとtarget selector一つに限定し、`--from`、root/date/path scope route、自動hookを設けない。
- RQ-316-002 Target selector parity:
  - Targetのstable ID、absolute path、unambiguous basename、not-found、ambiguity、unsupported branch-only selectorの意味論を既存worktree resolverと共有し、独自に複製しない。
  - Same-current、bare worktree、存在しないtarget pathはcopy開始前に拒否する。
- RQ-316-003 Independent scope resolution:
  - Sourceとtargetでnode inventoryを別々に読み、scope IDを各側で解決する。
  - Source側directory名やrelative pathをtargetへ文字列転写しない。
- RQ-316-004 Pre-mutation failure:
  - Target selector、source/target scope、containment、source Workbench存在の全preflightをcopy mutation前に完了する。
  - Source `.workbench/`不存在はstable `no_source` failureとし、target `.workbench/`を作成・変更しない。
- RQ-316-005 Recursive source-wins merge:
  - Destination `.workbench/`をwhole-tree置換せず、destination-only entryを保持する。
  - Same-relative ordinary leafはsourceで置換し、nested directoryはrecursive mergeする。
  - Directoryとnon-directoryの型衝突ではdestination subtreeを暗黙削除せずfailureにする。
- RQ-316-006 Opaque content copy:
  - Extension、language、MIME、secret、filename、contentによるallow/deny判定を追加しない。
  - 通常fileは標準filesystem copy primitiveが提供するbyte-preserving copyを行い、unsupported entryを黙ってskipしない。
- RQ-316-007 Symlink and containment safety:
  - Source descendant symlinkはtargetを読まずlink textを保持してcopyする。
  - Source/target scope root、Workbench root、destination directory ancestryがcommand boundary外へのread/writeを媒介しないよう、dereference前に検査する。
  - Destination symlink leafとの衝突ではlink自身だけを置換できるが、directory traversal位置のsymlinkは辿らない。
- RQ-316-008 Failure semantics:
  - I/O error、型衝突、runtime raceはsuccessにせずstable failureとして返す。
  - Tree-wide transaction、rollback、automatic retryを保証せず、copy開始後のpartial mutation可能性を隠さない。
- RQ-316-009 Output and authority isolation:
  - Help、success/failure text、JSONはexperimental、non-canonical、disposable、one-shot、no-sync/copy-backを表現する。
  - File body、secret-like value、完全なentry list、canonical/review/adoption claimを出力しない。
- RQ-316-010 Distribution and compatibility:
  - Provider-side layered runtimeを実装し、通常のdogfood projectionと必要最小限のinstalled consumer確認が可能な状態でIssue 319へ引き渡す。
  - Existing worktree create/list/show/remove、validate/sync/deps、Issue 315のWorkbench opacity、existing Workbench contentを変更しない。
  - Provider/dogfood inventory parityの最終確定、package-data/fresh init/existing update smoke、public reference docs、full regression/static analysis、Epic PR deliveryはIssue 319へrelayする。ただしcommand自身のhelp/text/JSON contractとfocused regressionは本Issueで閉じる。

## 受け入れ条件
- AC-316-001 CLI contract:
  - Help/parse testsでscope一つ、target一つ、current-source fixedを確認し、`--from`、root/date/path routeが存在しない。
- AC-316-002 Target resolution:
  - Stable ID、absolute path、basenameが同じtargetを解決し、ambiguous/missing/branch-only/same-current/bare/path-missingはmutation前にstable failureとなる。
- AC-316-003 Independent scope mapping:
  - 同じscope IDを持つsource/targetのdirectory slugが異なるfixtureで、target側record pathの`.workbench/`へcopyされる。
  - Source/target scope missing、ambiguous、invalid metadataの各failureでcopy adapterは呼ばれずtarget stateが不変である。
- AC-316-004 No-source no-mutation:
  - Source Workbench absent時、target Workbench absent/existingの両方でtarget stateが不変である。
- AC-316-005 Merge contract:
  - Source-onlyは追加、destination-onlyは保持、same-relative leafはsource wins、nested mergeとrepeat-run idempotencyが成立する。
- AC-316-006 Unfiltered copy:
  - Binary、archive、`.env`、Python、config、nested `.git`を含むfixtureで内容が分類なしにcopyされる。
- AC-316-007 Boundary safety:
  - Source descendant symlinkはdereferenceされずlink objectとしてcopyされる。
  - Repo/spec-dock rootからsource/target scope/Workbenchまでのancestor、Workbench root、destination traversal位置にsymlinkを含むfixtureはlexical/physical boundary検査でfailし、scope外sentinelを読書きしない。
- AC-316-008 Failure visibility:
  - Injected I/O errorとdirectory/non-directory collisionはsuccessを返さず、no-rollback境界と再実行可能性を偽らない。
- AC-316-009 Presentation:
  - Text/JSON success/errorがexperimental/non-canonical/one-shot/no-syncを示し、file body・secret sentinel・全entry listを含まない。
- AC-316-010 Distribution/regression:
  - Provider implementationのfocused tests、必要最小限のdogfood projection確認、manual two-linked-worktree handoff、既存worktree/validate/sync/deps focused regressionがpassし、最終distribution/parity gateの引渡し証跡がIssue 319向けに残る。

## 例外・境界条件
- EC-316-001: Emptyだが存在するsource `.workbench/`はsuccessとしてtarget rootを用意できる。
- EC-316-002: Brokenまたはexternal targetを持つsource descendant symlinkをdereferenceしない。
- EC-316-003: Source leafとdestination symlink leafの衝突は外部targetを変更せずsource leafで置換する。
- EC-316-004: Source directoryとdestination file/symlink、source leafとdestination directoryの衝突はdestructive replacementせずfailする。
- EC-316-005: Concurrent filesystem mutationとTOCTOUの完全排除は保証せず、検査前提が崩れた場合はcopy failureとする。
- EC-316-006: Detached/locked worktreeはその属性だけで拒否せず、existing resolver recordとfilesystem eligibilityに従う。
- EC-316-007: `SPEC_DOCK_WORKTREE_ROOT` managed classification不能だけを理由にvalid same-repository linked worktreeを拒否しない。
- EC-316-008: Symlink作成不能hostのOS integration testは明示skipできるが、adapter guard decisionはportable testで検証する。
- EC-316-009: Source `.workbench`がdirectoryでない場合はtarget mutation前にfailする。Target `.workbench`がnon-directoryの場合も外部targetや既存destinationを暗黙削除せずfailする。

## 非機能・安全性
- New third-party dependency、persistent manifest/catalog、per-entry accounting、filesystem transaction frameworkを追加しない。
- Resolverは既存意味論を共有し、Workbench固有copy処理はapplication/infra boundaryへ局所化する。
- Ordinary file contentとsymlink target contentはlog、text、JSONへ露出しない。
- Idempotencyはsource/targetへのconcurrent mutationがない条件で評価する。

## スコープ
- 必須:
  - Provider parser/registry/command/application/ports/infra/presentation、focused tests、必要最小限のdogfood projection確認、manual handoff evidence、Issue 319へのdistribution relay。
- 対象外:
  - Root Workbench bulk copy、自動copy、sync/copy-back、cross-repository copy、content/secret classifier、catalog/TTL、transaction/rollback、Artifact import、ChatGPT preservation workflow、Epic final PR。

## Evidence / authority
- Raw planning evidence:
  - `artifacts/20260713t072536z-research-chatgpt-5-6-pro-issue-planning-evidence.md`（SHA-256 `c65aa09c49271beb0bbef87aa4c210c6a6a227a46cc05509acf8c52e5c238765`）。
- Canonical authority:
  - 本requirement、fresh review後のdesign/plan、parent Epic/accepted ADR。
- Evidenceの採否とreviewer verdictは`report.md` EAL/Spec Authoring Gateへ記録する。

## 未確定事項
- Product/parent boundaryを変更する未確定事項はない。
- Exact module/helper/error/result field名とdirectory/leaf collisionの内部表現は、上記観測契約を変えないIssue-local design deltaとする。
