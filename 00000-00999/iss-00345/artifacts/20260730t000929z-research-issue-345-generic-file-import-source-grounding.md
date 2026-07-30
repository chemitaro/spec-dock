---
種別: research
ID: "20260730t000929z-research"
タイトル: "Issue 345 汎用ファイルインポートのソース根拠"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00345"]
関連: ["epic-00343", "iss-00344", "iss-00346"]
authority: "synthesized"
derived_from:
  - "epic-00343/requirement.md"
  - "epic-00343/design.md"
  - "epic-00343/plan.md"
  - "epic-00343/artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md"
reflected_to: []
---

# 20260730t000929z-research Issue 345 汎用ファイルインポートのソース根拠

## 位置づけ

本書は `iss-00345` のdraft-onlyなplanning evidenceである。canonical authority、accepted decision、review pass、readiness、実装済みの主張ではない。採否とcanonical反映はmain orchestrator、続くfresh spec review、およびIssue planning workflowに残る。

## sources read / 参照したソース

| Source | 読んだ範囲 | 本調査で使う根拠 |
|---|---|---|
| `issues/iss-00345.../requirement.md` | 現在のscaffold | requirementは未具体化のplaceholder、`design.md` / `plan.md`は`awaiting-assurance-compose`であること |
| `epic-00343/requirement.md` | E-RQ-008〜025、E-AC-008〜018 | command、target、source、bytes、privacy、opaque lifecycle、互換性、docsの必須契約 |
| `epic-00343/design.md` | D-003〜009 | additive use case、root resolver、FD-bound publication、name/slot/normalizer、result/privacy、opaque lifecycle |
| `epic-00343/plan.md` | Candidate 2、ownership、test/delivery boundary | Issue 345はcritical vertical slice、Issue 346がconsumer E2E等を所有すること |
| `epic-00343/artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md` | accepted Decision | generic family、privacy、commit stateの再解釈禁止契約 |
| `iss-00344` approved docs | merged Candidate 1 premise | Workbench shellを既存前提として扱い、generic importをIssue 344へ戻さないこと |
| 現行実装の既知surface | `application/import_artifact.py`、`contracts.py`、`commands/artifact_import.py`、`infra/binary_artifact_publisher.py`、`presentation/cli_text.py` | planned vertical sliceの調査開始点。実装の正しさ・存在・適合は未検証 |

## confirmed facts / 確認済みの事実

- 新規public commandは `artifact import file --file <path>` であり、`--root` / `--initiative <id>` / `--epic <id>` / `--issue <id>` からexactly one targetを要求する（E-RQ-008〜009）。rootはfake graph nodeではなく、root rulesで `spec-dock/artifacts/` に解決する（D-004）。
- relative source pathはrepository root基準であり、`..`を含むrepository外relative path、absolute path、Workbench内外を同じexplicit-path contractで受ける（E-RQ-010、012）。sourceはreadable regular single fileだけで、leaf symlinkは拒否しancestor symlinkは許容する（E-RQ-011）。
- sourceはopaque bytesである。bytes、source file、original basenameを保持し、commandはsourceをwrite/delete/move/renameしない（E-RQ-013、020）。cross-filesystem sourceもsource locationではなく読み取り済みFDからpublicationへ渡す設計が必要である（D-005）。
- filenameは標準`<timestamp>--<safe-original-basename>`、collision時`<timestamp>-<nn>--<safe-original-basename>`である。`--`はtyped `file` tokenではなくgeneric family delimiterであり、typed/blank/genericがslotを共有する。normalizationはextension、case、space、Unicodeを可能な限り残す最小限に限る（E-RQ-014〜016、D-006〜007、accepted ADR）。
- external sourceではbasenameだけが外部出力に現れてよい。absolute/parent path、body、hash、byte count、MIME、encoding、countその他content-derived valueをtext、JSON、diagnostic、tracked provenanceへ出してはならず、failureもcontent-freeである（E-RQ-018、D-008、accepted ADR）。
- successful commit pointはFD-bound no-replace publicationだけである。capability不足はfail closed、commit前は`not_committed`、commit後のdurability/owned-temp cleanup warningは`committed_with_warning`かつretry不要である（E-RQ-017、D-005/D-008、accepted ADR）。
- generic bodyは`validate`、`sync`、deps/context、ADR mirror/default discoveryのsemantic inputではない。generic `.md`もtyped Artifact/ADRへ昇格しない（E-RQ-020、D-009）。
- existing `artifact import chatgpt-output` はWorkbench-only lowercase `.md` guard、title/slug、blank naming/result contractを変更しない（E-RQ-021）。

## inference / 設計・計画へ渡す含意

- これはCLIだけの追加ではなく、CLI → application → domain/contracts → infra publisher → presentation → docs/testsを一貫して閉じるcritical vertical sliceである。既知surfaceはそれぞれ `commands/artifact_import.py`、`application/import_artifact.py`、`contracts.py`、`infra/binary_artifact_publisher.py`、`presentation/cli_text.py` である。
- source pathの文字列表現を後段へ無制限に渡すとexternal privacy contractを破り得る。application boundaryはsource classification後に、presentationへprivacy-safe resultだけを渡す必要がある。
- no-replace commit、shared slot、opaque discoveryは既存typed/blank flowとの同時実行で検証する必要があり、generic-only happy pathでは不足する。
- Issue 345はfocused/default laneとfeatureを所有する。一方、candidate wheel consumer E2E、generic importを含むintegrated dogfood、opt-in full regression、Epic final review/PRは`iss-00346`所有であり、345の完了条件に先取りしない。

## scenario matrix / 最低限のspecification対象

| 区分 | 成功または拒否の観測 |
|---|---|
| target | root / Initiative / Epic / Issueの4 destinationでexactly one selector。zero/multipleはmutation前にreject |
| location | root/scoped Workbench、repo内、external absolute、`..` relative、cross-FS sourceが同じauthorizationで動作 |
| eligibility | regular leafはaccept、missing/directory/leaf symlink/FIFO/socket/device/unreadableはformal destinationなしでreject。ancestor symlinkはaccept |
| bytes/lifecycle | empty、NUL、invalid UTF-8、binary、ZIP、multi-suffix、no extensionをopaqueに同一bytesで保存しsourceは不変 |
| naming | Unicode/space/case/extension chainを保持し、unsafe/NAME_MAXのみ最小normalize。generic/typed/blank/ChatGPT outputとのcollisionはno overwrite |
| fault/privacy | source identity mutation、hash mismatch、write/publish failure、capabilityなし、post-commit warningでcontent-free observable state。external sourceはbasename-only |
| compatibility | `validate` / `sync` / deps/context / ADR mirrorがbodyをdecode/parseせず、`chatgpt-output`既存contractも不変 |

## gap classification / 未検証事項と限界

| 分類 | 内容 | 次の扱い |
|---|---|---|
| canonical gap | Issue 345 requirementはscaffold、design/planはplaceholderであり、Issue-local normative R/D/Pはまだない | `spec-dock-issue-planning`でdraftを作り、orchestrator adoptionとfresh reviewへ戻す |
| source inspection gap | 上記5 implementation surfaceの現行API、existing parser、publisher capability、正確なtest pathは本artifactでは未読 | planning時にsource/testsを直接確認し、想定と異なればcanonical amendment判断へ戻す |
| security test gap | FD-bound no-replace、TOCTOU、cross-FS、warning injectionの実現可能なtest seamは未確認 | critical planでfault-injectionとhermetic test strategyを固定する |
| delivery gap | wheel consumer/integrated dogfood/full regression/Epic final reviewは意図的に345外 | `iss-00346`へ明記してhandoffする |

## unresolved / 質問候補

- user-intent blocker: なし。高影響なproduct choice（filename、privacy、commit/retry、semantic isolation）はaccepted ADRとEpic R/D/Pで回答済みである。
- implementation-open question: あり得るが、現行source/testの具体的seamを確認してからのtechnical planning questionであり、人間intent interviewを必要としない。

## risks and escalation

- accepted ADRの`--` family、full destination basename identity、external basename-only、content-derived metadata非公開、FD-bound commit/retry不要を変える必要が判明した場合は、Issue内で代替を決めずEpic design/ADR amendmentとfresh reviewへescalateする。
- rootをgraph nodeに偽装する、generic bodyをMarkdownとしてparseする、existing `chatgpt-output` を共用parserへ吸収する、Issue 346のdelivery scopeを345へ取り込む案はscope逸脱としてrejectする。
- 本書はrepository sourceとcanonical Epic docsのreading evidenceであり、実装・test・wheel/dogfoodの実行証拠ではない。

## 反映候補

- `requirement.md`: E-RQ-008〜025、privacy/authority、target/source/scenario matrixをIssue acceptanceへ具体化する候補。
- `design.md`: D-003〜009、accepted ADR boundary、各layer contractとfail-closed publicationを具体化する候補。
- `plan.md`: critical vertical micro-batch、focused tests、Issue 346 handoffを具体化する候補。
- `report.md` Evidence Adoption Ledger: main orchestratorのみが本researchのclaim単位の採否を記録する。
