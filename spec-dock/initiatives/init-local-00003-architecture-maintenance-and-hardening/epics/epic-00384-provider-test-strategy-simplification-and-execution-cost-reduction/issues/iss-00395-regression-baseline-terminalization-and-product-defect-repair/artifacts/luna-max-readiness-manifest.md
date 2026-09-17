---

kind: "readiness-pack-manifest"
issue: "iss-00395"
title: "Issue #395 LunaMax Readiness Pack Manifest"
artifact_path: "artifacts/luna-max-readiness-manifest.md"
state: "sealed-local-pack"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
integration_branch: "codex/epic-00384-provider-test-strategy-planning"
verified_branch_tip: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
verified_branch_tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
agents_md_blob: "cca009c9f5e25ece3a4f66fda710ff20e850a189"
current_verdict: "実装不可"
corrected_pack_state: "条件付き実装可能"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-provenance-and-packaging-contract"
canonical_authority_replacement: false
distribution_file_count: 5
zip_name: "luna-max-readiness-pack.zip"
zip_member_root: "artifacts/"
hash_algorithm: "sha256"
hash_byte_contract: "UTF-8 without BOM, LF line endings, exactly one terminal LF"
hash_record_state: "first-four-recorded; self-and-archive-recorded-in-external-receipt"
packaging_receipt_path: "artifacts/luna-max-readiness-pack.receipt.md"
files:

  - path: "artifacts/luna-max-readiness-analysis.md"
    role: "readiness-analysis"
    sha256: "3e6a80d0fa6c8ff6aafa0429567a699d5b73b25b275aca0a507a53f01658a080"
    sha256_record_required: true
    sha256_record_location: "this manifest before ZIP creation"
  - path: "artifacts/design-luna-max-ready.md"
    role: "corrected-design"
    sha256: "3ad20682f7545861da8542472b03f49ab02a4de75186ea588c065ccdb684660c"
    sha256_record_required: true
    sha256_record_location: "this manifest before ZIP creation"
  - path: "artifacts/plan-lunamax-ready.md"
    role: "corrected-plan"
    sha256: "314e90979ce29c564836f9b7150ad32be81fbffd1d689cee441e2d42fb3372ae"
    sha256_record_required: true
    sha256_record_location: "this manifest before ZIP creation"
  - path: "artifacts/luna-max-implementation-handoff-ready.md"
    role: "implementation-handoff"
    sha256: "3526babb2989fa6186292c90286daf900e6f1c50b79566df86b684d90d058f34"
    sha256_record_required: true
    sha256_record_location: "this manifest before ZIP creation"
  - path: "artifacts/luna-max-readiness-manifest.md"
    role: "readiness-pack-manifest"
    sha256: null
    sha256_record_required: true
    sha256_record_location: "external packaging receipt after final manifest bytes are fixed"
    zip_sha256: null
    zip_sha256_record_location: "external packaging receipt"
    derived_from:
    - "chemitaro/spec-dock@fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
    - "AGENTS.md@cca009c9f5e25ece3a4f66fda710ff20e850a189"
    - "Issue #395 Requirement"
    - "Issue #395 Design"
    - "Issue #395 Plan"
    - "Issue #395 LunaMax handoff"
    - "Parent Epic Requirement/Design/Plan"
    - "P392 provisional-merge and deferred-B1 ADR"
    - "active-failure-disposition-register.md"
    - "provider-lifecycle-wire-contract.md"
    - "epic-integration-branch-contract.md"
    - "rolling-wave-issue-elaboration-contract.md"
    - "Product/test/ledger/timing/verifier/policy/workflow evidence at the verified branch tree"
    operations_not_performed:
    - "Product source modification"
    - "test modification"
    - "ledger modification"
    - "policy modification"
    - "workflow modification"
    - "commit"
    - "push"
    - "pull request creation or update"
    - "merge"
    - "revert"
    - "Issue closure"

---

# Issue #395 LunaMax Readiness Pack Manifest

## 1. 目的とauthority

このmanifestは、Issue #395「Regression Baseline Terminalization and Product Defect Repair」について作成した、LunaMax実装準備度分析、修正版Design、修正版Plan、修正版implementation handoff、および本manifestの構成、生成元、依存関係、integrity contract、配布契約を記録する。

本packのauthorityはadvisoryである。次の正本を置換しない。

* Repositoryの実コード、tests、ledger、timing、policy、workflow
* Issue #395 canonical Requirement、Design、Plan
* Parent Epic Requirement、Design、Plan
* P392 ADRおよびhuman merge receipt
* Failure disposition register
* Provider Lifecycle Wire Contract
* Epic Integration Branch Contract
* Rolling-Wave Issue Elaboration Contract
* 独立specification review
* 明示的なimplementation dispatch
* Human merge判断

本packの作成完了は、実装、commit、push、PR preparation、merge、Issue closure、#396 startの許可を意味しない。

```yaml
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
```

現行の未修正版Design、Plan、handoffをそのままLunaMaxへ渡す場合のreadiness判定は「実装不可」である。修正版packは、canonical文書への採用、clean push、exact-tipの独立specification review、明示的なimplementation dispatchがすべて成立した場合に限り「条件付き実装可能」とする。

## 2. Repository identity

| 項目                   | 値                                                                         |
| -------------------- | ------------------------------------------------------------------------- |
| Repository           | `chemitaro/spec-dock`                                                     |
| Issue branch         | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Integration branch   | `codex/epic-00384-provider-test-strategy-planning`                        |
| Verified branch tip  | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| Verified branch tree | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                                |
| P392 entry SHA       | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| P392 entry tree      | `190bc566a18cd84813c4b7c043f8724e275cb55d`                                |
| `AGENTS.md` blob     | `cca009c9f5e25ece3a4f66fda710ff20e850a189`                                |

Branch identityは指定されたIssue branchを直接確認したものであり、default branchまたは別branchへfallbackしていない。

P392 entryとverified branch tipを混同しない。

* P392 entryはIssue #395が受け取るProduct/test/ledger baselineである。
* Verified branch tipはP392後のdocumentation receiptを含むelaboration inputである。
* Future specification freeze、implementation candidate、human-merged integration tipは、別々のSHA/treeとして扱う。
* Future SHAを本manifestへ事前に固定しない。

## 3. 配布ファイル一覧

配布対象は次の5ファイルだけである。Path、大小文字、hyphen位置を変更してはならない。

|  # | Relative path                                        | Role                                                                                   | SHA-256記録                                                |
| -: | ---------------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------- |
|  1 | `artifacts/luna-max-readiness-analysis.md`           | 現行仕様のreadiness判定、P0/P1/P2課題、修正理由、残余リスクを記録する。                                           | Final bytes確定後に64文字lowercase hexを記録する。                   |
|  2 | `artifacts/design-luna-max-ready.md`                 | Product/test/ledger/dogfood/evidence/permission境界を修正したnormative design candidateを記録する。 | Final bytes確定後に64文字lowercase hexを記録する。                   |
|  3 | `artifacts/plan-lunamax-ready.md`                    | LunaMaxの実行順序、RED/GREEN、test lane、mutation gate、evidence、stop条件を固定する。                   | Final bytes確定後に64文字lowercase hexを記録する。                   |
|  4 | `artifacts/luna-max-implementation-handoff-ready.md` | Execution packet、11変更許可files、13 repair rows、row 2/12特別扱い、merge境界を実装agentへ引き継ぐ。         | Final bytes確定後に64文字lowercase hexを記録する。                   |
|  5 | `artifacts/luna-max-readiness-manifest.md`           | 上記4ファイルとpackaging/integrity contractのprovenanceを記録する。                                  | Final manifest bytes確定後、external packaging receiptへ記録する。 |

`artifacts/plan-lunamax-ready.md`が正しい配布名である。次の旧名または別名は配布memberとして認めない。

```text
artifacts/plan-luna-max-ready.md
artifacts/plan-luna-max-readiness.md
artifacts/lunamax-plan-ready.md
```

## 4. 各成果物の役割

### 4.1 `luna-max-readiness-analysis.md`

目的:

* 現行Design、Plan、handoffがLunaMaxへ安全に渡せる状態かを判定する。
* 判定を「実装可能」「条件付き実装可能」「実装不可」のいずれかで明示する。
* P0、P1、P2を区別する。
* Test bodyを実行せずskipでGREENになり得るlane問題を特定する。
* Ledger historical-field drift、dogfood proof、exact candidate、post-merge B1/B2、permission separationの欠陥を記録する。
* 修正版packが必要となった理由と残余リスクを記録する。

Normative dependency:

* Repository identity
* Issue Requirement
* Existing Design、Plan、handoff
* Parent Epic R/D/P
* P392 ADR
* Failure disposition register
* Product/test/ledger/timing/verifier/policy/workflow evidence

このfileは実装手順の正本ではない。Design、Plan、handoffの修正理由を説明するanalysis artifactである。

### 4.2 `design-luna-max-ready.md`

目的:

* Issue #395のimmutable parent/P392/Issue boundaryを維持する。
* Product row 3のread-only identityとpublication strictnessを分離する。
* Rows 4–11のdescriptor-bound test-double contractを固定する。
* Rows 1、13、14、15のselection-only observer contractを固定する。
* Row 12をProduct/test no-edit guardとして扱う。
* Row 2の`resolved/superseded`をread-onlyで保持する。
* Dogfood projection、protected-data snapshot、ledger transitionを設計する。
* Test lane、permission、evidence、human merge、same-tip B1/B2を設計する。

Dependencies:

```text
luna-max-readiness-analysis.md
Issue #395 Requirement
Parent Epic contracts
P392 entry evidence
Repository AGENTS.md
```

DesignはPlanより上位である。PlanまたはhandoffがDesignと矛盾する場合は、実装を開始せずpackを修正する。

### 4.3 `plan-lunamax-ready.md`

目的:

* Read-only preflightとmutation authorizationを分離する。
* Fixed SHA/tree、branch、upstream、remote、ancestry、clean statusを検証する。
* Heavy testに`--run-full-regression --full-regression-shard`を付与する。
* 13 repair rowsの個別first REDを証明する。
* Row 12のentry evaluator REDとnode GREENを分離する。
* Row 2 successorをnormal-pass gateへ含める。
* Product/test GREEN後にだけdogfood projectionとledger transitionを行う。
* Working-tree provisional evidenceとexact clean evidenceを区別する。
* Exact 11-file set、no-touch、independent reviews、human merge boundaryを検証する。
* Stop-and-return JSONとsame-tip B1/B2を固定する。

Dependencies:

```text
design-luna-max-ready.md
luna-max-readiness-analysis.md
Issue #395 Requirement
Repository commands and test-lane policy
Current verifier and ledger contracts
```

Planは実装許可ではない。Execution packetに明示的なauthorizationがない状態でmutation phaseへ進んではならない。

### 4.4 `luna-max-implementation-handoff-ready.md`

目的:

* CodexからLunaMaxへ渡すexecution packet schemaを固定する。
* Specification review receiptとconcurrent-writer assertionを要求する。
* Implementation、commit/push、PR preparation、human mergeのpermissionを分離する。
* Exact 11変更許可filesを固定する。
* 13 repair rows、row 2、row 12の扱いを固定する。
* Test command contractとevidence return contractを固定する。
* Stop-and-return JSON、pre-merge terminal point、post-merge B1/B2 handoffを固定する。

Dependencies:

```text
design-luna-max-ready.md
plan-lunamax-ready.md
luna-max-readiness-analysis.md
Issue #395 Requirement
Repository AGENTS.md
```

HandoffはDesignとPlanを置換しない。Handoffの簡略記述がDesignまたはPlanを弱める場合は、弱めた記述を採用しない。

### 4.5 `luna-max-readiness-manifest.md`

目的:

* 5ファイルのidentity、role、generation source、dependency、hash fieldを記録する。
* Cross-file consistency rulesを固定する。
* ZIP member contractを固定する。
* Self-hashとZIP hashのexternal recording ruleを固定する。
* Packがimplementation authorizationを付与しないことを固定する。

Dependencies:

```text
luna-max-readiness-analysis.md
design-luna-max-ready.md
plan-lunamax-ready.md
luna-max-implementation-handoff-ready.md
packaging contract
```

Manifestは他4ファイルの内容を変更しない。Manifestと他4ファイルの不一致はpackaging failureである。

## 5. Dependency graph

```text
Repository identity
Issue Requirement
Parent Epic contracts
P392 ADR / register / lifecycle contracts
Product/test/ledger/verifier evidence
        |
        v
luna-max-readiness-analysis.md
        |
        v
design-luna-max-ready.md
        |
        v
plan-lunamax-ready.md
        |
        v
luna-max-implementation-handoff-ready.md
        |
        v
luna-max-readiness-manifest.md
        |
        v
luna-max-readiness-pack.zip
```

次の依存逆転を認めない。

* HandoffがDesignを上書きする。
* PlanがRequirementまたはDesignのboundaryを拡張する。
* Manifestがimplementation permissionを付与する。
* Analysisだけを実装仕様として使用する。
* ZIP member名からcanonical repository pathを推測する。

## 6. SHA-256記録契約

### 6.1 Hash byte contract

各fileのSHA-256は、次のexact bytesに対して計算する。

* Encoding: UTF-8
* BOM: なし
* Line ending: LF
* Terminal newline: exactly one LF
* Unicode normalization: 書換えない
* Trailing spaces: 書換えない
* Path content: hash対象に含めない
* Hash representation: 64文字lowercase hexadecimal
* Algorithm: SHA-256

計算例:

```bash
python - <<'PY'
from pathlib import Path
import hashlib

paths = [
    Path("artifacts/luna-max-readiness-analysis.md"),
    Path("artifacts/design-luna-max-ready.md"),
    Path("artifacts/plan-lunamax-ready.md"),
    Path("artifacts/luna-max-implementation-handoff-ready.md"),
    Path("artifacts/luna-max-readiness-manifest.md"),
]

for path in paths:
    raw = path.read_bytes()
    print(hashlib.sha256(raw).hexdigest(), path.as_posix())
PY
```

### 6.2 Record order

Packaging時は次の順序を守る。

1. Analysis、Design、Plan、handoffのfinal bytesを固定する。
2. 4ファイルをcontent validationする。
3. 4ファイルのSHA-256を計算する。
4. 本manifestのfront matterと§6.4のrecord tableへ、その4 hashを記録する。
5. Manifestをcontent validationする。
6. Manifestのfinal SHA-256を計算する。
7. 5ファイルをZIPへ格納する。
8. ZIP member bytesがsource bytesと一致することを確認する。
9. ZIPのSHA-256を計算する。
10. Manifest SHA-256とZIP SHA-256をexternal packaging receiptまたはdelivery metadataへ記録する。

Manifest自身のhashをmanifest内へ埋め込むとbytesが変化して自己参照になるため、manifestのfinal SHA-256はexternal recordとする。本manifest内にはmanifest用のrecord fieldを保持するが、値は`null`のままとし、external receiptがauthorityとなる。

ZIP SHA-256もarchive外へ記録する。ZIPへ六つ目のreceipt fileを追加してはならない。

### 6.3 Hash validity

次の状態ではpackをsealedまたはrelease-readyと扱わない。

* Analysis、Design、Plan、handoffの`sha256`が`null`または実体と不一致
* Hashが64文字lowercase hexでない
* Hashがfinal file bytesと一致しない
* Manifest SHA-256のexternal recordがない
* ZIP SHA-256のexternal recordがない
* ZIP member bytesがsource bytesと一致しない

4つの配布文書はローカルの最終bytesを固定し、manifestへSHA-256を記録済みである。Manifest自身とZIPは自己参照を避けるため、final SHA-256を外部packaging receiptへ記録する。未計算値を推測値または過去artifactのhashで埋めてはならない。

### 6.4 SHA-256 record table

| Path                                                 | SHA-256 | Record state                                |
| ---------------------------------------------------- | ------- | ------------------------------------------- |
| `artifacts/luna-max-readiness-analysis.md`           | `3e6a80d0fa6c8ff6aafa0429567a699d5b73b25b275aca0a507a53f01658a080` | Manifestへ記録済み。 |
| `artifacts/design-luna-max-ready.md`                 | `3ad20682f7545861da8542472b03f49ab02a4de75186ea588c065ccdb684660c` | Manifestへ記録済み。 |
| `artifacts/plan-lunamax-ready.md`                    | `314e90979ce29c564836f9b7150ad32be81fbffd1d689cee441e2d42fb3372ae` | Manifestへ記録済み。 |
| `artifacts/luna-max-implementation-handoff-ready.md` | `3526babb2989fa6186292c90286daf900e6f1c50b79566df86b684d90d058f34` | Manifestへ記録済み。 |
| `artifacts/luna-max-readiness-manifest.md`           | `null`  | Final hashをexternal packaging receiptへ記録する。 |
| `luna-max-readiness-pack.zip`                        | `null`  | Final hashをexternal packaging receiptへ記録する。 |

## 7. Cross-file content validation

### 7.1 Common front matter

5ファイルすべてについて次を要求する。

* First lineがexact `---`
* Front matter終端が独立したexact `---`
* YAML safe parse成功
* Duplicate keyなし
* `issue: "iss-00395"`
* `repository: "chemitaro/spec-dock"`
* `branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"`
* `implementation_allowed: false`
* `owner_decisions_required: []`
* `human_merge_only: true`
* P392 SHA/treeが一致
* Elaboration inputまたはverified branch SHA/treeが一致
* UTF-8 decode成功
* NUL byteなし
* CRLFなし
* Exactly one terminal LF

File-specific front-matter `kind`は次で固定する。

| Path                                       | Required `kind`           |
| ------------------------------------------ | ------------------------- |
| `luna-max-readiness-analysis.md`           | `readiness-analysis`      |
| `design-luna-max-ready.md`                 | `corrected-design`        |
| `plan-lunamax-ready.md`                    | `corrected-plan`          |
| `luna-max-implementation-handoff-ready.md` | `implementation-handoff`  |
| `luna-max-readiness-manifest.md`           | `readiness-pack-manifest` |

### 7.2 Analysis content

Analysisは少なくとも次を含む。

* 現行判定「実装不可」
* 修正版pack状態「条件付き実装可能」
* P0/P1/P2分類
* Heavy test skip false-GREEN問題
* Ledger historical-field preservation問題
* Post-merge B1 completeness問題
* Implementation permission separation問題
* 修正理由
* 残余リスク
* 実施していない操作

Analysisが「現行Planをそのまま実装可能」と結論づけている場合はvalidation failureである。

### 7.3 Design content

Designは少なくとも次を含む。

* P392、elaboration input、future spec freeze、future implementation SHAの分離
* `implementation_allowed=false`
* `owner_decisions_required=[]`
* Human-only merge
* Heavy test lane contract
* Product row 3のidentity/publication分離
* Rows 4–11 descriptor-bound test-double
* Rows 1、13、14、15 selection-only observer
* Row 12 Product/test no-edit guard
* Row 2 read-only superseded
* Exact 11 implementation paths
* Dogfood digest deltaとprotected-data proof
* Historical-preserving ledger transition
* Exact clean candidate rerun
* Same-tip B1 then B2
* Stop、recovery、rollback boundary

Designがpolicy、workflow、P392 lifecycle、#396 scopeを本Issueのwrite surfaceへ追加している場合はvalidation failureである。

### 7.4 Plan content

Planは少なくとも次を含む。

* Read-only preflightとmutation authorizationの分離
* Repository、branch、SHA/tree、upstream、remote、ancestry、clean checks
* Private evidence directory
* `--run-full-regression --full-regression-shard` contract
* Entry full-verifier exact allowance
* 13 repair rowsのindividual RED
* Row 12 evaluator RED/node GREEN
* Row 2 successor GREEN
* Mutation authorization receipt
* Scoped concurrent-writer assertion
* Exact implementation order
* Dogfood projection前後snapshot
* Ledger full before/after preservation
* Working-tree provisional distinction
* Exact clean rerun
* Exact 11-file set
* No-touch gates
* Independent implementation reviews
* Commit/pushとPR preparationのseparate permission
* Human merge boundary
* Same-tip B1/B2
* Stop-and-return JSON schema

Heavy path commandがlane permissionなしで記載されている場合はvalidation failureである。

### 7.5 Handoff content

Handoffは少なくとも次を含む。

* Execution packet schema
* Fixed repository、branch、P392、elaboration identities
* Specification review receipt fields
* `implementation_authorized`
* `commit_push_authorized`
* `pr_prepare_authorized`
* `human_merge_only`
* Scoped concurrent-writer assertion
* Exact 11 changed paths
* 13 repair rows
* Row 2 special handling
* Row 12 special handling
* Test lane contract
* Evidence artifact inventory
* Stop-and-return JSON
* Working-tree provisional terminal point
* Exact clean candidate terminal point
* Human merge前後の境界
* LunaMaxがmerge、Issue close、#396 startを行わないこと

Handoffがformal Issue startまたは本packの存在だけでimplementation authorizationが成立すると記載している場合はvalidation failureである。

### 7.6 Manifest content

Manifestは少なくとも次を含む。

* Exact five distribution files
* 各fileのrole
* Generation source
* Dependency graph
* SHA-256 record fields
* Self-hash external-record rule
* Content validation rules
* ZIP member contract
* Secret/temporary-file exclusions
* `implementation_allowed=false`
* `owner_decisions_required=[]`
* `human_merge_only=true`

## 8. Code-block validation

Markdown code fenceはbalancedでなければならない。

Language tagごとのvalidation:

* `json`: `json.loads`成功
* `yaml` / `yml`: YAML safe parse成功
* `python`: `ast.parse`成功
* `bash`: Heredocを含むsyntaxが`bash -n`を通過
* `text`: syntax validation対象外
* Languageなし: balanced fenceだけを検査

Runtime placeholder、environment-dependent command、future SHAを含むcode blockは、syntax validation成功をruntime successとみなさない。

Code-block validatorがsource documentを書換えてはならない。

## 9. Semantic consistency rules

5ファイル間で次が一致しなければならない。

| Contract                  | Required value                                                            |
| ------------------------- | ------------------------------------------------------------------------- |
| Repository                | `chemitaro/spec-dock`                                                     |
| Issue branch              | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Integration branch        | `codex/epic-00384-provider-test-strategy-planning`                        |
| P392 SHA                  | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| P392 tree                 | `190bc566a18cd84813c4b7c043f8724e275cb55d`                                |
| Elaboration input SHA     | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| Elaboration input tree    | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                                |
| Entry ledger              | 15 total / 14 active / 1 resolved                                         |
| Target ledger             | 15 total / 0 active / 15 resolved                                         |
| Target modes              | 14 fixed-in-place / 1 superseded                                          |
| Timing                    | 243                                                                       |
| Required-fast             | 4                                                                         |
| Implementation files      | Exact 11                                                                  |
| Repair rows               | 13                                                                        |
| Active rows transitioned  | 14                                                                        |
| Row 2                     | Read-only resolved/superseded                                             |
| Row 12                    | Product/test no-edit when verified blobs match                            |
| Approved target           | 0                                                                         |
| Unexpected target         | 0                                                                         |
| Implementation permission | `false`                                                                   |
| Owner decisions           | `[]`                                                                      |
| Merge authority           | Human only                                                                |

次の矛盾がある場合はpackaging failureである。

* Analysisが実装不可、Designが無条件実装可能とする。
* Planがpermission gate前のmutationを許可する。
* HandoffがDesignまたはPlanのstop条件を弱める。
* File listが11件より多い、または少ない。
* Row 2をfixed-in-placeへ変更する。
* Row 12にsource editを要求する。
* Policy、workflow、timing、sharderをwrite surfaceへ追加する。
* Agent mergeを許可する。
* `owner_decisions_required`をnon-emptyにする。
* `implementation_allowed`をtrueにする。

## 10. ZIP contract

### 10.1 Archive identity

```text
Archive name: luna-max-readiness-pack.zip
Regular file members: exactly 5
Member root: artifacts/
```

ZIP member pathは次のexact setである。

```text
artifacts/luna-max-readiness-analysis.md
artifacts/design-luna-max-ready.md
artifacts/plan-lunamax-ready.md
artifacts/luna-max-implementation-handoff-ready.md
artifacts/luna-max-readiness-manifest.md
```

### 10.2 ZIP exclusions

ZIPへ次を含めない。

* 明示的directory entry
* Sixth file
* Nested ZIP
* Source attachment bundle
* Product source
* Tests
* Ledger
* Timing
* Policy
* Workflow
* Human-guide HTML
* Existing canonical Issue files
* Temporary file
* Backup file
* Swap file
* Cache
* `__pycache__`
* `.pyc`
* `.pyo`
* `.DS_Store`
* `__MACOSX`
* Raw verifier artifact
* Raw test log
* External review receipt
* Secret
* Credential
* Token
* Private key
* `.env`
* Symlink
* Device file
* FIFO
* Absolute path
* `..` path traversal
* Duplicate member
* Case-conflicting member

### 10.3 ZIP member properties

各memberは次を満たす。

* Regular file
* Relative POSIX path
* Path prefix `artifacts/`
* UTF-8 Markdown
* Source file bytesとbyte-for-byte一致
* SHA-256がmanifest recordと一致
* Encryptionなし
* ZIP commentなし
* Member commentなし
* Executable permission不要
* Secret-bearing extra fieldなし

### 10.4 ZIP validation

```bash
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile
import hashlib

archive = Path("luna-max-readiness-pack.zip")

expected = [
    "artifacts/luna-max-readiness-analysis.md",
    "artifacts/design-luna-max-ready.md",
    "artifacts/plan-lunamax-ready.md",
    "artifacts/luna-max-implementation-handoff-ready.md",
    "artifacts/luna-max-readiness-manifest.md",
]

with ZipFile(archive) as package:
    assert package.testzip() is None
    assert package.namelist() == expected

    for member in expected:
        info = package.getinfo(member)

        assert not info.is_dir()
        assert not member.startswith("/")
        assert ".." not in Path(member).parts

        source = Path(member).read_bytes()
        archived = package.read(member)

        assert archived == source

        print(
            hashlib.sha256(archived).hexdigest(),
            member,
        )

print(
    hashlib.sha256(
        archive.read_bytes()
    ).hexdigest(),
    archive.name,
)
PY
```

Member orderは上記expected orderで固定する。

## 11. Packaging acceptance conditions

Packは次をすべて満たした場合だけsealedとする。

1. Exact five source filesが存在する。
2. Exact pathとfilenameが一致する。
3. 5ファイルがUTF-8/LF/terminal-LF contractを満たす。
4. 5 front matterがYAML safe parseに成功する。
5. Common permission fieldsが一致する。
6. Cross-file semantic consistencyが成立する。
7. Markdown code fencesがbalancedである。
8. JSON、YAML、Python、Bash code-block validationが成功する。
9. Analysis、Design、Plan、handoffのSHA-256がmanifestへ記録済みである。
10. ZIPはexact five regular membersだけを含む。
11. ZIP member bytesがsource bytesと一致する。
12. Manifest final SHA-256がexternal packaging receiptへ記録済みである。
13. ZIP final SHA-256がexternal packaging receiptへ記録済みである。
14. Secret、temporary file、cache、raw logsが含まれない。
15. Product source、tests、ledger、timing、policy、workflowが含まれない。
16. Repository変更、commit、push、PR、mergeが実行されていない。
17. `implementation_allowed=false`が維持されている。
18. `owner_decisions_required=[]`が維持されている。
19. `human_merge_only=true`が維持されている。

一つでも不成立ならpackを配布済み、sealed、reviewed、implementation-ready、merge-readyとして扱わない。

## 12. Implementation permission boundary

本packが成立させるのは、実装前に使用できる分析・設計・計画・handoff候補の配布だけである。

Implementation mutationへ進むには、本packとは別に次が必要である。

1. Canonical Issue文書への採用
2. Clean pushed specification SHA/tree
3. Exact SHA/treeに対するindependent specification review
4. `review_status=pass`
5. P0=0
6. P1=0
7. Immutable review receipt
8. Explicit `implementation_authorized=true`
9. Scoped concurrent-writer absence assertion
10. Mutation直前のclean identity revalidation

Commit/pushには別の`commit_push_authorized=true`が必要である。

PR preparationには別の`pr_prepare_authorized=true`が必要である。

Mergeはhuman onlyである。LunaMaxは次を実行しない。

* Integration branch direct push
* PR merge
* Revert
* Required-context変更
* Branch-protection変更
* Issue #392 close
* Issue #395 close
* Issue #396 start
* Main merge
* Automatic rollback

## 13. 未確認事項

本manifest作成時点では次は未実施または未確定である。

* Clean specification commit
* Push
* Independent specification review
* Implementation dispatch
* Product/test/ledger implementation
* Dogfood projection
* Full test execution
* Code Review Strict
* Final Quality Gate
* PR preparation
* Human merge
* Post-merge B1
* Post-merge B2
* Issue closure
* #396 start

これらを実施済みとして扱わない。

## 14. Final state

```yaml
distribution_contract_complete: true
distribution_bytes_materialized: true
hashes_recorded: true
zip_created: true
canonical_spec_adopted: true
independent_spec_review_passed: false
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
```

本manifestは、5ファイルの配布内容とvalidation/packaging contractを固定する。最終bytes、4文書のhashes、ZIP、ZIP/member integrityはローカルで確定済みであり、Manifest自身とZIPのfinal SHA-256は外部receiptへ記録する。Independent review、implementation authorization、commit、push、PR、mergeは未実施である。
