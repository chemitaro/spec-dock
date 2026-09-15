---

種別: artifact
ID: "iss-00395-chatgpt-spec-pack-manifest"
タイトル: "Issue #395 ChatGPT Spec Pack Manifest"
状態: "draft"
作成者: "ChatGPT specification author"
最終更新: "2026-09-15"
親: ["iss-00395"]
対象:
initiative: "init-local-00003"
epic: "epic-00384"
github_epic: "#384"
issue: "iss-00395"
github_issue: "#395"
template: "blank"
authority: "advisory-evidence"
canonical_authority_replacement: false
implementation_allowed: true
owner_decisions_required: []
derived_from:

* "../requirement.md"
* "../design.md"
* "../plan.md"
* "../../../requirement.md"
* "../../../design.md"
* "../../../plan.md"
* "../../../artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md"
* "../../../artifacts/epic-integration-branch-contract.md"
* "../../../artifacts/rolling-wave-issue-elaboration-contract.md"
* "../../../artifacts/active-failure-disposition-register.md"
* "../../../artifacts/provider-lifecycle-wire-contract.md"
* "../../iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md"
  reflected_to:
* "../requirement.md"
* "../design.md"
* "../plan.md"
  repository_evidence:
  role: "elaboration-input-provenance"
  repository: "chemitaro/spec-dock"
  branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
  sha: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
  tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
  p392_entry_evidence:
  role: "product-test-ledger-entry-baseline"
  sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
  tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
support_history_evidence:
  role: "grandfathered-immutable-support-history"
  sha: "c0736434503117d5d468d1438fb18da16d382a56"
  tree: "cec02ce70fbcbbbac811a04106dcc15540ad4d09"
  strict_authoring_evidence:
  requested_model: "GPT-5.6 Pro（GPT-5.6 Sol + Pro 推論）"
  runtime_model_identity: "GPT-5.6 Sol Pro"
  github_connector_verification: "passed"
  signed_external_model_attestation: "未取得"

---

# Issue #395 ChatGPT Spec Pack Manifest

## 1. 目的

このmanifestは、formal Issue start済みのIssue #395「Regression Baseline Terminalization and Product Defect Repair」について、既存のcontract-only draftをLunaMaxが実装判断に迷わないimplementation-readyな仕様へ具体化したChatGPT生成packの構成、生成履歴、入力identity、ファイルidentity、authority境界、immutable contract、ローカル反映後のvalidation/review gateを記録する。

本packが行った作業は、仕様、設計、実装計画、実装引継ぎ資料、人間向け説明資料およびprovenance manifestの作成に限定される。次の操作は実行していない。

* Product sourceの変更
* regression testの変更
* `full-regression-ledger.json`の遷移
* dogfood candidateの更新
* SpecDock managed metadataの手編集
* Pack生成時点でのimplementation permissionの付与
* commitまたはpush
* Pull Requestの作成またはmerge
* Issue #392またはIssue #395のclosure
* Issue #396の開始
* mainへのmerge

Pack生成時点ではimplementation permissionを付与していなかった。現在のcanonical R/D/Pおよび本manifestのimplementation_allowed: trueは、ユーザーの明示dispatchを反映する。ただし、packの生成、ローカル配置、静的検査、SpecDock validate、commitまたはpushのいずれも、独立Strict specification reviewと明示的なimplementation dispatchを代替しない。修正後のfresh Strict specification reviewがpassするまで、実効的なProduct/test/ledger/dogfood mutationはblockedである。

Current canonical specification packはexact 6 pathsである。Elaboration input後に既に存在したexact 16 support artifactsは、c0736434503117d5d468d1438fb18da16d382a56 / cec02ce70fbcbbbac811a04106dcc15540ad4d09をcheckpointとするimmutable、non-authoritative、grandfathered support historyである。Support historyはcurrent authority、implementation input、permission evidenceではなく、編集、削除、rename、再生成、再圧縮、再分類、新規追加を行わない。

## 2. 対象コンテキスト

| 区分                                | Exact value                                                               |
| --------------------------------- | ------------------------------------------------------------------------- |
| Initiative                        | `init-local-00003`                                                        |
| Epic                              | `epic-00384`                                                              |
| GitHub Epic                       | `#384`                                                                    |
| Epic title                        | `Provider Test Strategy Simplification and Execution Cost Reduction`      |
| Issue                             | `iss-00395`                                                               |
| GitHub Issue                      | `#395`                                                                    |
| Issue title                       | `Regression Baseline Terminalization and Product Defect Repair`           |
| Predecessor Issue                 | `iss-00392` / GitHub `#392`                                               |
| Successor Issue                   | `iss-00396` / GitHub `#396`                                               |
| Integration branch                | `codex/epic-00384-provider-test-strategy-planning`                        |
| Issue branch                      | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Delivery order                    | `#392 -> #395 -> #396 -> Epic human merge to main`                        |
| Current implementation permission | `true`                                                                    |
| Current owner decisions           | `[]`                                                                      |

implementation_allowed=trueはユーザーの明示dispatchを記録する。これはfresh Strict review pass前の実効的なmutation許可ではない。

現在のgenerated contextはInitiative `init-local-00003`、Epic `epic-00384`、Issue `iss-00395`をactive contextとして示す。Generated active stateは作業案内であり、canonical Issue R/D/P、accepted ADR、normative artifactsおよびexact repository stateを置換しない。

## 3. Strict GitHub connector verification

### 3.1 最新検証結果

この最終manifest本文の作成前に、connected GitHub repositoryに対して次を実行した。

| Operation                            | Requested target                                                          | Observed result                                           |
| ------------------------------------ | ------------------------------------------------------------------------- | --------------------------------------------------------- |
| GitHub connector operation discovery | `GitHub`, query `branch`                                                  | Repository、branch search、direct fetchを含む利用可能なoperationを確認 |
| Repository access                    | `chemitaro/spec-dock`                                                     | `repository_full_name=chemitaro/spec-dock`、access成功       |
| Target branch search                 | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` | Exact branchを1件取得                                         |
| Direct target branch fetch           | GitHub branch endpoint                                                    | Full tip SHAとtreeを取得                                      |
| SHA comparison                       | expected `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                       | Exact byte-for-byte match                                 |
| Tree observation                     | target branch commit tree                                                 | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                |

検証済みidentityは次で固定する。

```yaml
repository: chemitaro/spec-dock
branch: iss-00395-regression-baseline-terminalization-and-product-defect-repair
head_sha: fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9
head_tree: 4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599
verification: exact-match
```

Default branchのcontent、別branch、public Web、memoryまたはattachmentへfallbackしてbranch tipを代替していない。Repository metadata取得時にdefault branch名が返されたが、そのbranchのcontentは本検証の根拠として参照していない。

### 3.2 会話内の反復検証

次の各成果物をinlineで再提示する直前にも、同じrepositoryとtarget branchをGitHub connectorで再取得し、full tip SHAが同じexpected SHAと一致することを確認した。

1. `requirement.md`
2. `design.md`
3. `plan.md`
4. `artifacts/iss-00395-luna-max-implementation-handoff.md`
5. 本manifest最終本文

これらの検証中、target branch tipは一貫して次の値だった。

```text
fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9
```

## 4. P392と仕様作成tipの境界

### 4.1 二つのidentity role

| Role               | SHA                                        | Tree                                       | Authority                                                                           |
| ------------------ | ------------------------------------------ | ------------------------------------------ | ----------------------------------------------------------------------------------- |
| P392 Product entry | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3` | `190bc566a18cd84813c4b7c043f8724e275cb55d` | Issue #395が受け取るProduct、tests、ledger、timing、current verifierおよびpolicyのentry baseline |
| Elaboration input  | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9` | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599` | P392後のreceipt文書を含むIssue #395仕様作成source                                              |

P392はIssue #392のhuman merge tipであるが、B1、Issue #392 acceptance、Issue #392 closure、Issue #395 implementation permissionまたはIssue #396 start permissionではない。

### 4.2 P392後のdoc-only差分

`921bf7512c72bfa2887673cb7ec9bc512cec6ff3`から`fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`までの変更対象は、次の二つの文書だけである。

1. `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/plan.md`
2. `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md`

この差分は、P392 merged-tip verification receiptとIssue #395へのhandoff状態を記録するdoc-only変更である。次はP392から変更されていない入力として扱う。

* Provider-side Product source
* Checked-in dogfood runtime
* Regression tests
* `full-regression-ledger.json`
* `full-regression-timing-weights.json`
* `scripts/quality/full_regression_baseline.py`
* `scripts/quality/verify_full_regression.py`
* `tests/conftest.py`
* Provider CI workflow
* Provider Full Regression workflow
* Current skip/xfail policy
* Required-fast four nodeids
* Provider lifecycle wireおよびruntime coordination contract

Packをローカル反映した後のnew clean pushed SHAはspec freeze candidateであり、P392 Product entry SHAまたはelaboration input SHAを置換しない。

## 5. Pack生成履歴

### 5.1 初回生成

2026-09-15に、次の六ファイルを一つのspec packとして生成した。

1. `requirement.md`
2. `design.md`
3. `plan.md`
4. `artifacts/iss-00395-luna-max-implementation-handoff.md`
5. `artifacts/iss-00395-human-guide.html`
6. `artifacts/iss-00395-chatgpt-spec-pack-manifest.md`

同じ生成処理で次の配布補助物も作成した。

* 六ファイルを格納した`iss-00395-spec-pack.zip`
* 各相対パス行とコードフェンスを一続きにした`iss-00395-spec-pack-inline.txt`

初回sandbox packのZIPは、六ファイルと二つのdirectory entryを含み、archive testで全entryが正常と確認された。

### 5.2 Inline再提示履歴

初回sandbox fileを利用者環境へ回収できなかったため、その後、Strict GitHub connector verificationを各回で繰り返し、次のファイルを全文inlineで再提示した。

| Order | Output                                                   | Result      |
| ----: | -------------------------------------------------------- | ----------- |
|     1 | `requirement.md`                                         | 全文inline再提示 |
|     2 | `design.md`                                              | 全文inline再提示 |
|     3 | `plan.md`                                                | 全文inline再提示 |
|     4 | `artifacts/iss-00395-luna-max-implementation-handoff.md` | 全文inline再提示 |
|     5 | `artifacts/iss-00395-chatgpt-spec-pack-manifest.md`      | 全文inline再提示 |
|     6 | `artifacts/iss-00395-human-guide.html`                  | 全文inline再提示 |

HTMLは初回sandbox packから回収できなかったため、同じStrict会話で完全本文を再提示し、Codexがローカル保存した。その後、HTML検証契約に必要なモーダル`role="dialog"`とviewportの`tabindex="0"`を追加し、PlantUML sourceを壊していたMarkdown fence行を除去した。本文の説明、PlantUMLソース、描画処理およびズーム機能の意図は変更していない。

### 5.3 Byte identityに関する制約

初回sandbox packのhashは履歴上の証拠として保持し、ローカルに配置した最終6ファイルのhashはCodexが再計算した。後続のchat inline再提示は初回sandbox fileとbyte-for-byte同一とは限らないため、初回hashを現在の配置物のidentityとして流用しない。

従って、hash authorityは次のように扱う。

* 初回sandbox fileおよび初回ZIP member: 履歴hashとして検証済み
* ローカルに配置したRequirement、Design、Plan: 次表のlocal hashで検証済み
* ローカルに配置したhandoff、HTML: inline回収後のlocal hashで検証済み
* ローカルに配置したmanifest自身: 自己参照による循環を避けるため本文へhashを埋め込まず、外部receiptで記録
* ローカルに配置したfinal ZIP: `unzip -t`、member一覧、local fileとのhash照合および外部receiptのhashで検証済み

## 6. 生成ファイル一覧とSHA-256

### 6.1 Hash計算条件

次のhashは、UTF-8、LF、terminal newlineありのローカル配置物に対してCodexが計算した。初回sandbox packのhashは、異なるinline回収物へ適用しない。

* Encoding: UTF-8
* Line ending: LF
* CRLF count: 0
* Terminal newline: あり
* Digest algorithm: SHA-256
* Path名はdigest入力に含めず、file bytesだけをdigest対象とする

### 6.2 Pack member identities

| Relative path                                            | Lines |  Bytes | SHA-256                                                            | Status                                         |
| -------------------------------------------------------- | ----: | -----: | ------------------------------------------------------------------ | ---------------------------------------------- |
| `requirement.md`                                         |   319 | 29,786 | `1c6465d01c80849fe8ef3d0fca03ae162c4f00bce948504d25cc46ceb03e460d` | 初回sandbox fileおよび初回ZIP memberで一致確認済み           |
| `design.md`                                              |   411 | 23,605 | `fffead31e108132df18ecf1f0633bd652cf24c0d2beb98bf3b1a633cf859ea5d` | 初回sandbox fileおよび初回ZIP memberで一致確認済み           |
| `plan.md`                                                | 1,043 | 50,994 | `961950680ed015115d0e6f3d33f49025e1b8c226664b05a4a38ea67ecf25ea70` | 初回sandbox fileおよび初回ZIP memberで一致確認済み           |
| `artifacts/iss-00395-luna-max-implementation-handoff.md` | 2,622 | 90,673 | `992b9b63b9968b2a3c185d5fba21a5eb385368ea6d798a59b67748e3804ad8bc` | inline回収後のlocal fileで一致確認済み |
| `artifacts/iss-00395-human-guide.html`                   |   703 | 41,623 | `aad8d14f8bcdb0e987b24c57cfd241da8d15fb8dfd1168ce1381cfc8fd2cfbb9` | inline回収、HTML契約修正、PlantUML fence除去後のlocal fileで一致確認済み |
| `artifacts/iss-00395-chatgpt-spec-pack-manifest.md`      | 1,006 | 53,827 | `未記録` | 自己参照を避け、最終local hashは外部receiptで記録 |

### 6.3 manifest自身のhash

`artifacts/iss-00395-chatgpt-spec-pack-manifest.md`のfull-file SHA-256は、本文へ自己参照を埋め込むと値が変わるため、ここには記録しない。Codexは最終配置後のhashを外部receiptとして計算する。

また、manifest本文の中へそのmanifest自身のordinary full-file SHA-256を埋め込むと、その値を埋め込んだこと自体でfile bytesが変化する。従って、更新後manifestのfinal SHA-256は次のいずれかで外部に記録する。

1. ローカル保存後の完了receipt
2. ZIP外のchecksum manifest
3. Git blob identityと対応付けたexternal evidence record

本manifest自身へ推測値または自己参照値を埋め込まない。

### 6.4 ZIP identities

| Artifact                  |  Bytes | SHA-256                                                            | Integrity           |
| ------------------------- | -----: | ------------------------------------------------------------------ | ------------------- |
| `iss-00395-spec-pack.zip` | 65,637 | `5400b0f0fe66e5537b50795e6185f113aa9eeb849356f621b8c25e29306d321d` | 初回sandbox ZIPの履歴identity。`unzip -t`で全entry正常 |

初回ZIPの内容は次の六ファイルである。

```text
iss-00395-spec-pack/requirement.md
iss-00395-spec-pack/design.md
iss-00395-spec-pack/plan.md
iss-00395-spec-pack/artifacts/iss-00395-chatgpt-spec-pack-manifest.md
iss-00395-spec-pack/artifacts/iss-00395-luna-max-implementation-handoff.md
iss-00395-spec-pack/artifacts/iss-00395-human-guide.html
```

初回ZIPのuncompressed file payload合計は192,728 bytesである。

このZIPには初回sandbox版manifestが含まれる。

Codexがローカル配置した最終6ファイルから再生成したfinal ZIPは次である。

| Artifact | Bytes | SHA-256 | Integrity |
| --- | ---: | --- | --- |
| `iss-00395-spec-pack.zip` | 最終生成時に計算 | `未記録` | `unzip -t` pass、8 entries、6 file payloads。最終hashは外部receiptで記録 |

final ZIPのhashはmanifest自身を編集した後に再計算した外部receiptの値であり、manifest本文へ同じ値を追記してZIPを再生成することはしない。

### 6.5 配布補助テキスト

次はrepositoryへ配置するcanonical pack memberではなく、初回配布用の補助fileである。

| Artifact                         | Lines |   Bytes | SHA-256                                                            |
| -------------------------------- | ----: | ------: | ------------------------------------------------------------------ |
| `iss-00395-spec-pack-inline.txt` | 3,278 | 193,000 | `2b6395bdda44a0abede63be98ffc4ad025d394ff99471a2f458bdda3dca552a3` |

## 7. Strictモデルとthinking-time evidence

### 7.1 Model identity

| Field                              | Recorded value                                  |
| ---------------------------------- | ----------------------------------------------- |
| User-requested designation         | `GPT-5.6 Pro（GPT-5.6 Sol + Pro 推論）`             |
| Runtime model identity             | `GPT-5.6 Sol Pro`                               |
| Operational route                  | Strict GitHub connector verificationを各成果物作成前に実施 |
| External signed model attestation  | 未取得                                             |
| Cryptographic model identity proof | 未取得                                             |

`Strict`は、このpackではrepository、branch、full SHAをGitHub connectorでexact verificationし、不一致時に停止する運用contractを指す。`Strict`を、別個のcryptographically attested model binary名として扱わない。

### 7.2 UI-reported worked-time history

会話UIが各完了済みauthoring responseについて表示したworked-time summaryは次のとおりである。

| Authoring stage                   | UI-reported worked time |
| --------------------------------- | ----------------------: |
| 初回spec pack一式、HTML、manifest、ZIP生成 |               `50m 27s` |
| `requirement.md` inline再提示        |                `2m 34s` |
| `design.md` inline再提示             |                `3m 43s` |
| `plan.md` inline再提示               |                `4m 24s` |
| LunaMax handoff inline再提示         |                `6m 05s` |
| 上記五responseの既知合計                  |            `1h 07m 13s` |
| 本manifest最終化response              |      応答完了前には確定できないため未確認 |

これらはconversation UIが示したelapsed work summaryである。次を意味しない。

* Pure hidden reasoningだけの時間
* CPU time
* Billable compute time
* Server-side signed timing attestation
* 各tool callだけの合計
* 人間が実際に待機した時間の独立計測

Raw server timing logまたは署名付きthinking-time artifactは取得していない。未確認の時間を推測で補わない。

## 8. 根拠として使用した情報

### 8.1 Canonicalおよびnormative documents

* Parent Epic Requirement
* Parent Epic Design
* Parent Epic Plan
* Issue #395 Requirement、Design、Planの既存contract-only draft
* Accepted P392 sequence ADR
* Epic Integration Branch Contract
* Rolling-Wave Issue Elaboration Contract
* Post-#387 Regression Baseline Register
* Provider Lifecycle Wire Contract
* Issue #392 merged-tip Report、特にP392 receipt
* Issue #392 LunaMax handoff
* Issue #392 lifecycle test ownership/migration Artifact
* Generated active context pack

### 8.2 Current repository implementation

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`

  * `_remote_get_url`
  * `_parse_github_repo_slug`
  * `_remote_has_userinfo`
  * `_redact_remote_url`
  * `origin_github_repo_slug`
  * `origin_github_publication_endpoint`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py`

  * `import_node_core`
  * `_validate_url_repo_identity`
  * `_require_numeric_import_repo_scope`
  * `_resolve_import_issue_view_repo_slug`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`

  * `GitGateway.origin_github_repo_slug`
  * `TemplateScaffolder.copy_scaffolded_tree_at`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`

  * `_GitGateway.origin_github_repo_slug`
  * `_TemplateScaffolder.copy_scaffolded_tree_at`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`

  * `execute_create_plan`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py`

  * `copy_scaffolded_tree_at`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`

### 8.3 Current regression and policy files

* `full-regression-ledger.json`
* `full-regression-timing-weights.json`
* `scripts/quality/full_regression_baseline.py`
* `scripts/quality/verify_full_regression.py`
* `tests/conftest.py`
* `tests/unit/test_full_regression_baseline.py`
* `.github/workflows/provider-ci.yml`
* `.github/workflows/provider-full-regression.yml`

### 8.4 Current regression tests

* `tests/cli_runtime/test_delete.py`
* `tests/cli_runtime/test_import.py`
* `tests/cli_runtime/test_runtime_import_s10.py`
* `tests/cli_runtime/test_runtime_shell_s11.py`
* `tests/cli_runtime/test_sync.py`
* `tests/cli_runtime/test_workbench.py`
* `tests/cli_runtime/test_distribution_cutover.py`
* Provider lifecycle focused test family
* Provider lifecycle package/dogfood parity test family
* Provider lifecycle platform and coordination test families

### 8.5 Supplied context input

今回添付された`context-pack.md`について、ローカルに取得できたfile identityは次である。

| Input             | Lines | Bytes | SHA-256                                                            |
| ----------------- | ----: | ----: | ------------------------------------------------------------------ |
| `context-pack.md` |    36 | 1,382 | `f4cf34ec2a357a78574ff133f85eee13668e6065898e57952f6a9cd9096d6165` |

このcontext packはactive contextとcanonical read orderを示す補助入力であり、canonical repository documentsの代替authorityではない。

初回pack作成時に補助資料として使用したと記録されたattachment bundleについては、この最終manifest作成時にcomplete original bytesおよびSHA-256を再取得していない。そのattachment bundleのhashは未確認である。

## 9. Generated file inventory

| Order | Relative path                                            | Classification                     | Purpose                                                                                                                                                                                                                                 |
| ----: | -------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|     1 | `requirement.md`                                         | Canonical Issue document candidate | Exact P392/current identities、entry/stop gates、14-row acceptance、owned/shared/no-touch、ledger transition、non-regression、rollback、implementation permission separation、traceabilityを固定する。                                                |
|     2 | `design.md`                                              | Canonical Issue document candidate | Existing provider-side paths/symbols、responsibility boundaries、dependency direction、runtime flows、test harness seam、identity/publication separation、application contract、compatibility、error/rollback、observation/evidence designを固定する。 |
|     3 | `plan.md`                                                | Canonical Issue document candidate | Read-only preflight、14-row RED/GREEN、ordered changes、dogfood projection、ledger transition、ordinary/focused/full gates、Strict review、human merge、same-tip B1/B2、rollbackを固定する。                                                           |
|     4 | `artifacts/iss-00395-luna-max-implementation-handoff.md` | Artifact / execution guidance      | LunaMax向けexecution packet、preflight、row table、exact commands、禁止事項、stop-and-return schema、evidence schema、commit/PR/human boundaryを固定する。                                                                                                 |
|     5 | `artifacts/iss-00395-human-guide.html`                   | Artifact / human guidance          | 新規参加者向けのself-contained日本語説明、背景、用語、構成、14 rows、正常/失敗flow、verification、rollback、editable PlantUMLを提供する。                                                                                                                                    |
|     6 | `artifacts/iss-00395-chatgpt-spec-pack-manifest.md`      | Artifact / provenance              | Packのidentity、生成履歴、hash、authority、validation/review gateを記録する。                                                                                                                                                                          |

Canonical Issue R/D/Pは、ローカル反映、reviewおよび採用後にIssue正本候補となる。Artifactsは実行指示、説明およびprovenance/evidenceであり、canonical R/D/P、accepted parent contractまたはrepository sourceを上書きしない。

## 10. Packが保持するimmutable contract

本packは次を意味変更しない。

1. Delivery orderは`#392 -> #395 -> #396`である。
2. Issue PR baseはEpic integration branchであり、人間だけがmerge、revertおよびrequired-context変更を行う。
3. P392は唯一のpre-B1 non-GREEN stateである。
4. Issue #395はhuman-merged exact P392 tipだけをProduct entryとして受け取る。
5. Baseline inputは15 total、14 active、1 resolvedである。
6. Active rowsはregister row 1およびrows 3–15である。
7. Row 2は既存`resolved/superseded`でread-onlyである。
8. Post-#395 targetは15 total、0 active、15 resolved、14 fixed-in-place、1 superseded、approved failure 0、unexpected failure 0である。
9. Timingは243 entriesのままIssue #396まで保持する。
10. Required-fastはexact four nodeidsのまま保持する。
11. Current ledger evaluator、sharder、policy hook、Provider CI、main-push Full RegressionはIssue #395完了まで保持する。
12. 14 active rowsのnodeidとhistorical signatureを変更しない。
13. 修復面はtest harness/observer 12件、Product boundary 2件である。
14. Skip、xfail、approved failure追加、row削除、signature書換え、assertion弱化、silent retirement、unrelated successor substitutionを禁止する。
15. Issue #392 lifecycle、wire、record、migration、uninstall、recovery、runtime coordinationおよびprotected-data contractはread-onlyである。
16. Issue #396の`E384-QUAL-001` implementation、policy retirement、required-context transition、main mergeはIssue #395の対象外である。
17. Pack完成だけではProduct implementation permissionを付与しない。
18. `owner_decisions_required=[]`を維持する。
19. Current canonical specification packはexact 6 pathsである。
20. Existing exact 16 support artifactsは、support-history checkpoint c0736434503117d5d468d1438fb18da16d382a56 / cec02ce70fbcbbbac811a04106dcc15540ad4d09に束縛されたimmutable、non-authoritative、grandfathered support historyである。
21. Support historyはcurrent authority、implementation input、permission evidenceではなく、path、mode、object type、Git object IDをspec freezeでcheckpointと一致させる。
22. 22 pathsを単一のcurrent-spec allowlistとして扱わず、support historyのedit、delete、rename、regenerate、recompress、reclassify、新規追加を行わない。

## 11. Row-specific contractの固定内容

### 11.1 Rows 1、13、14、15

* 廃止済み`active set --force`を復活させない。
* 廃止済み`--no-checkout`を復活させない。
* Current selection-only CLIで同じProduct behaviorを観測する。
* Row 15はactive operationのsuccessを確認してからgenerated active stateを読む。
* Delete、sync、tree、PUML、ready-board、Workbench opacityのexisting assertionsを保持する。

### 11.2 Rows 4–11

* Productionのdescriptor-bound write pathを維持する。
* Test doubleをcurrent `TemplateScaffolder.copy_scaffolded_tree_at` call shapeへ追随させる。
* Current infra adapterへ委譲し、独自のpathname writerを増やさない。
* `application.create_node.execute_create_plan`をobsolete `copy_scaffolded_tree`へ戻さない。
* Parent fallback、active manifest chain、lock-side re-resolution、GitHub repo slug、artifact projection、negative sync path、single-writer seamのassertionsを保持する。

### 11.3 Row 3

* Read-only repository identity解析をpublication endpoint policyから分離する。
* Credential-bearing HTTPS fetch originからowner/repository identityを解決できる。
* Read-only pathはcredential-bearing URLをpublication endpointとして受理したことを意味しない。
* Publication pathではfetch/push双方のuserinfoを拒否する。
* Publication pathではfetch/push repository slug一致を要求する。
* Same-repository import validationを維持する。
* Credential、username、password、tokenまたはcredential-bearing URLをstdout、stderr、exceptionまたはevidenceへ露出しない。
* Existing `GitGateway.origin_github_repo_slug` signatureを変更しない。

### 11.4 Row 12

Verified P392/current sourceでは、accepted boundaryは既に次の形で存在する。

```text
commands/new.py
  -> application/contracts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
     -> domain/artifacts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
```

Current full verifierのrow 12 violationは`coverage_mismatch`であり、current structural nodeはnormal passする。

従って、implementation ruleは次で固定する。

* Current blobsとAST/import boundaryが一致する場合、row 12のProduct sourceを変更しない。
* Existing structural testをnormal passとして保持する。
* 14 rowsのnormal pass後、row 12を含めledgerを`resolved/fixed-in-place`へ遷移する。
* Current boundaryにdriftがある場合、推測修正を行わずstop-and-returnする。
* Catalogueの複製、新しいwrapper type、直接domain importまたはobsolete type復活を行わない。

## 12. 初回sandbox packに対して実施した静的検査

この最終manifest作成時に、初回sandbox packへ次の再検査を実施した。

### 12.1 Markdownおよびfront matter

* Markdown五ファイルのYAML front matterをPyYAMLでparse
* 五ファイルすべてparse成功
* `requirement.md`から14 active rowsのexact nodeid/signature pairを抽出
* Unique pair countは14
* `plan.md`に14 nodeidsおよび14 signaturesが存在
* LunaMax handoffに14 nodeidsおよび14 signaturesが存在
* Human guide HTMLに14 nodeidsおよび14 signaturesが存在
* `TODO`、`TBD`、`FIXME`、`<TODO>`、`未定`、`要検討`に一致する未解決作業markerなし

### 12.2 JSON code blocks

初回sandbox pack内の次のJSON code blocksをparseした。

| File            | Parsed JSON blocks |
| --------------- | -----------------: |
| `design.md`     |                  3 |
| `plan.md`       |                  1 |
| LunaMax handoff |                  1 |

全blockがJSON parse成功した。

### 12.3 Bash code blocks

初回sandbox pack内のbash blocksを個別に`bash -n`で検査した。

| File               | Checked bash blocks | Result             |
| ------------------ | ------------------: | ------------------ |
| `plan.md`          |                  37 | 全block syntax pass |
| LunaMax handoff    |                   7 | 全block syntax pass |
| 初回sandbox版manifest |                   1 | syntax pass        |

本回答の更新後manifestは初回sandbox版と異なるため、ローカル反映後に再検査する。

### 12.4 Human guide HTML

初回sandbox版`artifacts/iss-00395-human-guide.html`について次を確認した。

* `lang="ja"`あり
* `data-plantuml-contract="2"`あり
* `@plantuml/core@1.2026.6`へversion pin
* CDN URL:

  * `https://unpkg.com/@plantuml/core@1.2026.6/viz-global.js`
  * `https://unpkg.com/@plantuml/core@1.2026.6/plantuml.js`
* PlantUML source block: 5
* 各source blockに`@startuml`と`@enduml`
* External PlantUML Server参照なし
* Kroki参照なし
* `renderToString` callback使用
* Sourceは`sourceElement.textContent`から取得
* 表示用sourceは`textContent`へ設定
* `data-diagram-type`、Syntax Error text、PlantUML diagnostic structureおよびdiagnostic text styleを検査してerror SVGを拒否
* Shared zoom modalあり
* Click、Enter、Spaceでzoom open
* 50%–300% zoom制限
* Focus trapあり
* Escape closeあり
* Backdrop closeあり
* Focus restoreあり
* Inline executable JavaScript block: 2
* Classic JavaScriptとmodule JavaScriptの両方が`node --check`でsyntax pass

このstatic checkはbrowserでの実render成功、network availabilityまたはPlantUML outputのvisual correctnessを独立に証明しない。ローカル反映後、実browserまたはapproved validation harnessでrenderを再確認する。

## 13. Authority boundary

### 13.1 Canonical authority

次が本packより上位のauthorityである。

1. Accepted parent ADR
2. Parent Epic Requirement、Design、Plan
3. Epic Integration Branch Contract
4. Rolling-Wave Issue Elaboration Contract
5. Post-#387 Regression Baseline Register
6. Provider Lifecycle Wire Contract
7. Exact verified repository source、tests、ledger、timingおよびworkflow
8. 独立review後に採用されたIssue #395 canonical Requirement、Design、Plan

### 13.2 Artifact authority

次はArtifactであり、canonical authorityを置換しない。

* LunaMax implementation handoff
* Human guide HTML
* 本manifest

Artifactとcanonical R/D/Pが矛盾する場合、Artifactを修正する。Artifactを根拠にstable parent contract、Product behavior、policy value、repository identityまたはmerge stateを変更しない。

### 13.3 ChatGPT advisory boundary

このpackはChatGPTによる分析・草案であり、次を主張しない。

* Repositoryへ反映済みであること
* Independent spec reviewをpassしたこと
* Product implementationが開始または完了したこと
* Testsが修正またはGREENになったこと
* Ledgerが15/0/15へ遷移したこと
* PRが作成またはmergeされたこと
* B1またはB2が成立したこと
* #392または#395がcloseされたこと
* #396が開始されたこと

## 14. ローカル配置契約

### 14.1 配置先

Packは次のIssue directoryへ配置する。

```text
spec-dock/initiatives/
  init-local-00003-architecture-maintenance-and-hardening/
    epics/
      epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/
        issues/
          iss-00395-regression-baseline-terminalization-and-product-defect-repair/
            requirement.md
            design.md
            plan.md
            artifacts/
              iss-00395-luna-max-implementation-handoff.md
              iss-00395-human-guide.html
              iss-00395-chatgpt-spec-pack-manifest.md
```

### 14.2 配置時の禁止事項

* `.meta.json`を手編集しない。
* Active pointerを手編集しない。
* Dependency storageを手編集しない。
* Generated index、tree、diagramを手編集しない。
* Product sourceを同じspec-only commitへ混在させない。
* Testsを同じspec-only commitへ混在させない。
* Ledger、timing、policyまたはworkflowを同じspec-only commitへ混在させない。
* Dogfood runtimeまたはcandidate recordを同じspec-only commitへ混在させない。
* Issue #392またはIssue #396のcanonical documentsを変更しない。
* Parent Epic stable contractを変更しない。

SpecDock managed stateを変更する必要がある場合は、current SpecDock commandを使用する。

## 15. ローカル配置後の必須検証

### 15.1 File presenceおよびcontent

* Exact six relative pathsが存在する。
* 六ファイルがnon-emptyである。
* UTF-8として読める。
* LF line endingsを使用する。
* Terminal newlineを保持する。
* Requirement、Design、Planのfront matterに次がある。

  * `ID: "iss-00395"`
  * `実装開始許可: true`
  * `owner_decisions_required: []`
* LunaMax handoffに次がある。

  * `implementation_allowed: true`
  * `owner_decisions_required: []`
* Manifestに次がある。

  * `authority: "advisory-evidence"`
  * `canonical_authority_replacement: false`
  * `implementation_allowed: true`

### 15.2 SHA-256検証

次のhashは修正前packの履歴identityであり、今回の仕様修正後のcurrent bytesとの一致を要求しない。修正後は、六つのprimary filesを保存した最終candidateでSHA-256を再計算し、Git SHA/treeとexternal receiptへ束縛する。

```text
1c6465d01c80849fe8ef3d0fca03ae162c4f00bce948504d25cc46ceb03e460d  requirement.md
fffead31e108132df18ecf1f0633bd652cf24c0d2beb98bf3b1a633cf859ea5d  design.md
961950680ed015115d0e6f3d33f49025e1b8c226664b05a4a38ea67ecf25ea70  plan.md
2b9b214883a9bb9cdec25a069d65b80e43f8044cb14447f6764fc2a08b2ceedc  artifacts/iss-00395-luna-max-implementation-handoff.md
26df95657c669bf62fcbba03897240c289f3b76c55c26002498eb2333788fd5a  artifacts/iss-00395-human-guide.html
```

本回答の更新後manifestは、ローカル保存後にSHA-256を計算し、external receiptへ記録する。初回sandbox版manifestのhash `8bb563b0c2ae78806f35bdf11bf544de0feafb0cd6194042c61e2b1c2daa7149`との一致を要求しない。

### 15.3 P392 boundary検証

```bash
git diff --name-only \
  921bf7512c72bfa2887673cb7ec9bc512cec6ff3 \
  fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9
```

Expected exact output:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/plan.md
```

Extra Product、test、ledger、timing、policyまたはworkflow pathがある場合は停止する。

### 15.4 Specification admission history boundary

Support-history checkpointからreviewed specification freezeまでのcurrent diffについて、exact six primary pathsだけが変更されていることを確認する。Elaboration inputからsupport-history checkpointまでのexact 22 pathsは、別の履歴segmentとして既に検証済みである。

Expected set:

```text
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/requirement.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/design.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/plan.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-luna-max-implementation-handoff.md
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-human-guide.html
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-chatgpt-spec-pack-manifest.md
```

Support-history checkpointは c0736434503117d5d468d1438fb18da16d382a56、treeは cec02ce70fbcbbbac811a04106dcc15540ad4d09 である。exact 16 support pathsについて、checkpointとreviewed specification freezeのGit tree entry（path、mode、object type、object ID）が一致することを確認する。22 pathsをcurrent-spec allowlistとして扱わず、directory prefix、glob、Manifestの自己申告、working-tree存在、過去のZIP hashで代替しない。Support historyのedit、delete、rename、copy substitution、regenerate、recompress、reclassify、新規追加は停止条件である。

SpecDock commandが正当に再生成するdocumentation projectionがある場合は、そのcommand、before/after identityおよび理由を別receiptへ記録する。Product source、tests、ledger、timing、policy、workflowまたはdogfood runtimeが含まれる場合はcommit/push前に停止する。

### 15.5 Markdown、JSONおよびshell static checks

* 五Markdown filesのYAML front matterをparseする。
* JSON Schema/code blocksをJSON parserで検査する。
* Bash code blocksを個別に`bash -n`で検査する。
* Python code blocksに対し、必要に応じて`ast.parse`を実行する。
* Exact 14 active nodeidsと14 signaturesがRequirement、Plan、handoffおよびhuman guideに存在することを確認する。
* `TODO`、`TBD`、`FIXME`、`未定`、`要検討`などの未解決markerがないことを確認する。
* P392 SHA/tree、elaboration input SHA/tree、15/14/1、243、15/0/15、approved 0、owner decisions emptyが文書間で一致することを確認する。

### 15.6 HTML checks

* HTML parserでdocumentを読める。
* `lang="ja"`を保持する。
* `data-plantuml-contract="2"`を保持する。
* CDNは`@plantuml/core@1.2026.6`のpinned URLだけを使用する。
* `renderToString`がsuccess/error callback付きで使用される。
* PlantUML sourceを`textContent`から取得する。
* Source表示も`textContent`を使用する。
* Diagnostic/error SVGをrejectする。
* 外部PlantUML ServerまたはKrokiを参照しない。
* Shared zoom modalを保持する。
* 50%–300% zoom、click、Enter、Space、focus trap、Escape、backdrop close、focus restoreを保持する。
* Inline classic JavaScriptとmodule JavaScriptを抽出して`node --check`する。
* Browserで全PlantUML diagramがdiagnostic SVGではなく正常SVGとして描画されることを確認する。

### 15.7 Repository checks

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
git diff --name-only \
  fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9...HEAD
```

Expected SpecDock validation:

```text
spec-dock: ok (validate) nodes=236
```

異なるnode count、metadata error、broken relative linkまたはgenerated-state inconsistencyがある場合は、Product implementationへ進まずspec reflectionを修正する。

### 15.8 ZIP再生成

更新後manifestを含むfinal packをZIP化する場合は、次を満たす。

* Six completed filesだけを含める。
* Temporary files、cache、duplicate file、credential、private logを含めない。
* Relative directory structureを保持する。
* `unzip -t`をpassする。
* 各ZIP memberを展開し、local source fileのSHA-256と比較する。
* Repacked ZIPのSHA-256をexternal distribution receiptへ記録する。
* 初回ZIP hash `5400b0f0fe66e5537b50795e6185f113aa9eeb849356f621b8c25e29306d321d`を更新後ZIPへ流用しない。

## 16. Independent Strict review gate

ローカル反映後、Product implementation前に次を実行する。

1. Packだけを含むcandidateをcommitする。
2. Configured upstreamへpushする。
3. Worktreeをcleanにする。
4. Local `HEAD`、upstreamおよびremote target branch full SHAをexact一致させる。
5. GitHub connectorで同じrepository、branch、full SHAを再確認する。
6. Fresh independent browser sessionで`chatgpt-spec-review-strict`を実行する。
7. Requirement、Design、Plan、LunaMax handoff、human guide、manifestの全六ファイルをreview対象にする。
8. Parent Epic R/D/P、P392 ADR、Integration Branch Contract、Rolling-Wave Contract、Register、Issue #392 P392 receiptとの整合をreviewする。
9. Acceptance条件を次で固定する。

   * `review_status=pass`
   * P0=0
   * P1=0
10. Findingsを修正した場合、new exact clean pushed SHAへreviewを再束縛する。
11. 過去review receiptをnew SHAへ流用しない。
12. Review receiptをtracked Product tree外のapproved evidence locationへ保存する。

Independent review pass後も、implementation_allowedを自動的に変更しない。現在のtrueはユーザーの明示dispatchを記録した値であり、fresh review pass前のeffective mutation permissionではない。Implementation dispatch、spec review pass、execution packet、concurrent-writer absenceは別のゲートとして扱う。

## 17. LunaMax implementation dispatch gate

LunaMaxへ渡すexecution packetには少なくとも次をactual valuesで含める。

* Repository
* Issue branch
* Integration branch
* P392 SHA/tree
* Reviewed spec freeze SHA/tree
* Spec review receipt identity
* `review_status=pass`
* P0=0
* P1=0
* `implementation_authorized=true`
* `concurrent_writer_absent=true`
* Commit/push authorization boolean
* PR preparation authorization boolean
* Exact owned paths
* Exact no-touch paths
* 14-row table
* First RED commands
* Expected RED causes
* GREEN commands
* Ledger transition timing
* Dogfood projection contract
* Stop-and-return schema
* Implementation evidence schema
* Human-only merge boundary
* Same-tip B1/B2 boundary
* Whole-merge rollback boundary

次のいずれかが欠ける場合、LunaMaxはread-only preflight以外を実行しない。

* Actual spec freeze SHA
* Exact review receipt
* Review pass
* Explicit implementation authorization
* Concurrent writer absence
* Exact P392 ancestry
* Clean local/upstream/remote identity

## 18. Implementation後の証拠境界

本packはProduct implementationを行わないが、implementation candidateの受入には次を要求する。

1. Row-by-row RED/GREEN
2. Row 3 credential secrecy
3. Row 3 publication userinfo rejection
4. Row 3 fetch/push mismatch rejection
5. Rows 4–11 descriptor-bound test double
6. Rows 1、13、14、15 selection-only active observer
7. Row 12 source drift guard
8. 14 active historical nodesのnormal pass
9. Row 2 successor normal pass
10. Ledger 15/0/15
11. 14 fixed-in-place、1 superseded
12. Approved failure 0
13. Unexpected failure 0
14. Current full verifier exit 0、`status=verified`
15. Timing 243
16. Required-fast exact 4
17. Policy、workflow、lifecycle no-touch
18. Provider source/dogfood runtime parity
19. Ready recordとtwo slot markerのcandidate digest equality
20. Ordinary tests
21. Provider lifecycle tests
22. Platform/package/dogfood tests
23. `make lint`
24. SpecDock validate
25. Clean pushed implementation SHA
26. Exact implementation SHAでのfull verifier再実行
27. Independent Code Review Strict
28. Final Quality Gate Strict v2 Pro
29. Human PR review
30. Human merge
31. Same exact merged tipでB1
32. 同じtipでB2
33. Whole-merge rollback readiness

Working-tree verifierの`candidate_sha`はuncommitted bytesを識別しないため、merge-ready evidenceに使用しない。

## 19. Human merge、B1/B2およびrollback

### 19.1 Human merge boundary

* Issue PR baseは`codex/epic-00384-provider-test-strategy-planning`
* Issue PR headはIssue #395 branch
* Integration branchへのdirect pushは禁止
* Agent mergeは禁止
* Agent revertは禁止
* Required-context変更は禁止
* Main向けIssue PRは禁止
* Issue closeはhuman/Codex operational gate

### 19.2 Same-tip B1/B2

Issue #395 PRをhuman mergeした後、integration branchのexact full SHA/treeを固定する。

同じSHAで次の順に評価する。

1. B1

   * Current required gate GREEN
   * Ordinary tests GREEN
   * Current full verifier GREEN
   * Provider parity GREEN
   * #392 lifecycle/protected-data invariants維持
   * Unexpected failure 0

2. B2

   * 15 total
   * 0 active
   * 15 resolved
   * 14 fixed-in-place
   * 1 superseded
   * Approved failure 0
   * Unexpected failure 0

B1とB2を異なるcommit、異なるrerun identityまたはfuture SHAへ分離しない。

### 19.3 Rollback

Rollback unitはwhole Issue #395 mergeである。

* Human merge前: Issue branchをabandonまたは修正
* Human merge後、#396開始前:

  * Human whole-merge revertでP392へ戻す、または
  * #395 owned boundary内でforward-fixし、new exact tipでB1/B2を再実行
* #396 work開始後:

  * #396を停止・保存
  * Humanがsuffix dispositionを決定
  * Reverse dependency orderまたはowned forward-fix

次は禁止する。

* Ledger-only rollback
* Product-only rollback
* Test-only rollback
* Generated mirror-only rollback
* Automatic rollback
* Obsolete CLI/APIへのfallback
* Accepted historyのforce rewrite

## 20. 未確認事項

次は推測で埋めず、未確認として保持する。

| Item                                          | Status      | Required next evidence                              |
| --------------------------------------------- | ----------- | --------------------------------------------------- |
| 本manifest full-file SHA-256                         | 外部receiptへ記録 | 自己参照を避けるため本文には埋め込まない                         |
| final ZIP SHA-256                                    | 外部receiptへ記録 | 最終manifestをstageしてrepack、`unzip -t`、member hash比較後に計算 |
| 本manifest finalization responseのthinking time | 応答完了前のため未確認 | UI-reported completion summaryが存在する場合に外部receiptへ記録  |
| External signed model attestation             | 未取得         | 利用可能な正式attestationがある場合のみ記録                         |
| Initial attachment bundle SHA-256             | 未確認         | Original bytesを再取得できた場合に計算                          |
| Local repositoryへの六ファイル反映                     | 完了         | Codexによる配置と`git diff`確認                             |
| SpecDock validate after reflection            | pass         | `./spec-dock/scripts/spec-dock validate` (`nodes=236`)            |
| Independent specification review              | 修正後candidateで実施前。receiptは外部evidence locationへ保存 | Clean pushed exact SHAで`chatgpt-spec-review-strict` |
| Implementation permission                     | ユーザーの明示dispatch済み（`true`）。実効mutationは別ゲート | Fresh review pass、execution packet、concurrent-writer absence |
| Product implementation                        | 未実施         | LunaMax execution packet                            |
| Test修正                                        | 未実施         | LunaMax execution packet                            |
| Ledger transition                             | 未実施         | 14 rows normal pass後                                |
| Human PR merge                                | 未実施         | Human gate                                          |
| Same-tip B1/B2                                | 未実施         | Human merge後のexact integration tip                  |

## 21. Final status

* Pack purpose: Issue #395のimplementation-ready specification
* Initial six-file generation: 完了
* Requirement inline recovery: 完了
* Design inline recovery: 完了
* Plan inline recovery: 完了
* LunaMax handoff inline recovery: 完了
* Human guide inline recovery and local validation: 完了
* PlantUML fence混入の表示不具合修正: 完了
* Manifest final body: 配置済み
* Initial sandbox ZIP integrity: pass
* Initial sandbox member hashes: 記録済み
* Final local member hashes: 記録済み
* Final manifest hash: 外部receiptで記録
* Final ZIP hash: 外部receiptで記録
* Strict GitHub verification: pass
* Repository: `chemitaro/spec-dock`
* Branch: `iss-00395-regression-baseline-terminalization-and-product-defect-repair`
* Verified HEAD: `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`
* Verified tree: `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`
* P392 SHA: `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`
* P392 tree: `190bc566a18cd84813c4b7c043f8724e275cb55d`
* P392後のProduct/test/policy drift: なし。Epic PlanとIssue #392 Reportのdoc-only差分
* Implementation permission: `true` records the user's explicit dispatch. Effective Product/test/ledger/dogfood mutation remains blocked until the repaired specification receives a fresh Strict review pass with P0=0 and P1=0 and the execution packet is complete.
* Product implementation: 未実施
* Independent spec review: 未実施
* Human merge: 未実施
* `owner_decisions_required=[]`
* Canonical authority replacement: しない
