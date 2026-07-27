---
種別: 設計書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "approved"
作成者: "Blue Team"
最終更新: "2026-07-27"
依存: ["requirement.md"]
親: ["epic-00331", "init-00322"]
planning_profile_guidance: "strict"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — 設計

## 0. Design Position

本設計はE1-I1のwalking skeletonを一つのvertical implementation sliceとして実装するcanonical Designである。Candidate由来のprovenanceは`report.md`へ分離し、本書はcurrent implementation contractだけを所有する。Mainがassurance classification／composition、fresh Review、Human implementation-start gateを完了するまでimplementation authorityは成立しない。

## 1. Responsibility Model

| Component / Actor | Responsibility | Must not do |
|---|---|---|
| Human | Issue Plan adoption、implementation start、merge decision | automated approvalを委任しない |
| Planning Skill | active scope確認、context framing、mode／lane／Human Gate選択、Main handoff | raw outputをauthority化しない |
| Codex Main | source inspection、deterministic placement、Git transaction、evidence integration | semantic reviewを代行しない |
| `spec-dock-chatgpt` | target/Git preflight、closed Prompt、Oracle/backend invocation、artifact retrieval、Human-supplied apply evidenceのpublic受付 | Human decision生成、unbound lifecycle mutation、semantic adoption、mergeを行わない |
| Core Runtime | three-document response validation、immutable Issue Candidate packaging、archive validation、identity、adoption/parity、validation/publication/readiness evaluation | Human decisionを生成しない |
| Oracle/backend | browser/session/transport and downloadable artifact retrieval | SpecDock authorityを付与しない |
| ChatGPT Planner | complete三文書response生成 | control-file生成、canonical write、assurance writeを行わない |
| ChatGPT Reviewer | read-only Review result生成 | Candidate、patch、repositoryを変更しない |

## 2. System Context

```text
Human
  → spec-dock-issue-planning Skill
      → Codex Main context framing
          → spec-dock-chatgpt
              → Git preflight
              → closed Prompt resources
              → Oracle/backend
                  → ChatGPT Planner / Reviewer
          ← downloaded Candidate / Review result
      → Main deterministic adoption and publication
      → Core Runtime parity / validation / readiness evaluation
  → existing shared delivery workflow after S99
```

`spec-dock-chatgpt`はindependent repo-local entrypointだが、安全性実装を複製しない。existing `authoring_pack` Git preflight、direct-argv backend、archive review、digest、approval validationをthin application façadeから再利用する。

## 3. Public Command Design

```text
./spec-dock/scripts/spec-dock-chatgpt planning create \
  --issue <id> \
  --output <external-dir>

./spec-dock/scripts/spec-dock-chatgpt planning revise \
  --candidate <zip-or-tree> \
  --lane <semantic|mechanical> \
  --output <external-dir>

./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue <id> \
  --mode archive-candidate \
  --candidate <zip> \
  --logical-filename <name> \
  --zip-sha256 <sha256> \
  --output <external-dir>

./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue <id> \
  --mode git-bound \
  --reviewed-head <sha> \
  --target <repo-relative-path> [--target <repo-relative-path> ...] \
  --base-kind <none|semantic-base> \
  [--base-head <sha>] \
  --output <external-dir>

./spec-dock/scripts/spec-dock-chatgpt planning apply \
  --issue <id> \
  --mode archive-candidate \
  --candidate <zip> \
  --logical-filename <name> \
  --zip-sha256 <sha256> \
  --review-result <external-json> \
  --human-decision <external-json> \
  --decision-artifact <issue-artifacts-relative-json> \
  --expected-head <sha> \
  --output <external-dir>

./spec-dock/scripts/spec-dock-chatgpt planning apply \
  --issue <id> \
  --mode git-bound \
  --reviewed-head <sha> \
  --target <repo-relative-path> [--target <repo-relative-path> ...] \
  --base-kind <none|semantic-base> \
  [--base-head <sha>] \
  --review-result <external-json> \
  --human-decision <external-json> \
  --decision-artifact <issue-artifacts-relative-json> \
  --expected-head <sha> \
  --output <external-dir>
```

- parser／dispatchが公開するChatGPT planning command familyは`planning create`、`planning revise`、`review planning`、`planning apply`の四つだけである。上記archive／git-bound表記は二つのcommandを追加するものではなく、同一commandのclosed mode variantsである。
- `--issue`はReview resultとHuman decisionがbindするexact Issue IDであり、`review planning`と`planning apply`の両modeで必須とする。target pathからIssue IDを推測しない。
- repository rootはcurrent managed repositoryから解決する。repository identityはcurrent branch upstream remote URLからcanonical `owner/repository`へ変換し、branchはcurrent non-detached symbolic branchとそのupstream branchから解決する。public `--repository`、`--branch`、default-branch overrideを提供しない。
- detached HEAD、upstream欠落、unparseableまたはnon-GitHub upstream、current branch／upstream branch mismatch、local／remote／expected HEAD mismatchはbackendまたはrepository mutation前にfail closedとする。
- archive mode identityはCandidate bytesと`--logical-filename`／`--zip-sha256`から構築する。Candidate ID、internal root、source repository／branch／HEADは§4.2のcontrol filesから導出し、CLI overrideを提供しない。
- git-bound mode identityはderived repository／branch、`--issue`、`--reviewed-head`、repeatable `--target`、`--base-kind`、conditional `--base-head`から構築する。
- git-bound v1では`--base-kind none`または`--base-kind semantic-base`だけを許可する。
  - `none`: `--base-head`は禁止し、identityは`{"kind":"none","head":null}`を持つ。
  - `semantic-base`: `--base-head`を必須とし、identityは`{"kind":"semantic-base","head":"<sha>"}`を持つ。base HEADはrepositoryに存在し、`reviewed_head`のancestorでなければならない。
  - `merge-base`はv1で未対応であり、parserが`rejected`する。必要になった場合はcomparison counterpartを含むclosed identityをDesign amendmentで定義し、fresh Reviewを得る。
- `--target`は1件以上を要求し、CLI supplied orderがUTF-8 byte lexicographic ascending、duplicateなしでなければ拒否する。Runtimeがsilent sortして別identityを生成しない。
- archive modeは`--reviewed-head`、`--target`、`--base-kind`、`--base-head`を禁止する。git-bound modeは`--candidate`、`--logical-filename`、`--zip-sha256`を禁止する。
- `semantic-base`で`--base-head`欠落、`none`で`--base-head`指定、cross-mode option、unknown option、同一optionの禁止された重複は`rejected`、exit `1`、backend／repository mutation 0とする。
- `planning create`はscope、parent、dependencies、source HEADを解決し、closed Promptからcomplete三文書responseを要求する。response検証後、Core Runtimeが§4.2のexact controlsを生成してimmutable Issue Candidate ZIPをfinal public artifactとして返す。
- `planning revise`はSkillが選択済みlaneを受ける。CLIはlaneを推測しない。
- `review planning`はmodeを推測せず、CLIから構築した`ReviewedPlanningIdentityV1`を検証してread-only reviewerを起動する。Human-readable companion、raw transcript、Markdown verdictだけをauthority-bearing apply evidenceとして受け付けない。
- `planning apply`は後半lifecycleの唯一のsupported public entrypointである。両modeで`PlanningReviewResultV1`、`PlanningHumanDecisionV1`、decision artifact destination、expected HEAD、external output directoryを要求する。
- required `--review-result`または`--human-decision` option／fileが欠落する場合は`blocked`、exit `1`、mutation 0とする。それ以外のrequired request identity option欠落はmalformed invocationとして`rejected`、exit `1`、mutation 0とする。
- RuntimeはReview／Human JSONをそれぞれ一回だけbytesとして読み、そのsame bytesからSHA-256計算とJSON validationを行う。
- Review result、Human decision、CLI mode identityは同一の`ReviewedPlanningIdentityV1` objectと`reviewed_identity_sha256`へbindしなければならない。Human decisionはexact Review-result file bytesの`review_result_sha256`にもbindする。
- `decision=approved`はReview `pass`とdual authorizationが成立した場合だけfull adoption transactionへ進む。
- `decision=rejected`はvalid Review resultと同じidentityへbindされている場合、decision artifactだけを記録するdecision-record transactionへ進む。verified remote publication後のstatusは`blocked`、exit `1`であり、canonical三文書を変更しない。
- `decision=revoked`はv1 unsupported enumとして`rejected`、exit `1`、mutation 0とする。
- `--decision-artifact`はactive Issueの`artifacts/` direct childにある新規lowercase JSON pathだけを受け付け、既存file、symlink parent、scope外pathを`rejected`する。
- text／JSONは同じclosed `status`と`reason`を返す。`status`は`ready|blocked|stale|rejected|rolled_back|publication_pending|blocked_remote_diverged|recovery_required`だけであり、`ready`だけexit `0`、それ以外はexit `1`とする。`failed`、`invalid`、`insufficient evidence`をpublic statusとして追加せず、必要な区別はclosed `reason`で表す。同じnamed observable conditionは常に同じstatus／reasonを返す。
- output directoryはrepository／canonical tree外のexisting non-symlink directoryに限定する。

## 4. Core Contracts

### 4.1 Planning Request

```text
PlanningRequest
- scope_id = iss-00334形式のexisting Issueまたはapproved Seed
- repository / branch / expected_head
- parent_epic / parent_initiative
- dependency_state
- relevant_paths
- operator_context (redacted free-form)
- prompt_resource_id
- output_directory
```

### 4.2 Planner Response, Runtime Package, Candidate Controls, and Identity

```text
ChatGPTPlannerResponse
- requirement.md
- design.md
- plan.md

RuntimeIssueCandidatePackage
- requirement.md
- design.md
- plan.md
- SOURCE-BASELINE.json
- MANIFEST.json
- CHECKSUMS.sha256
- PLACEHOLDER-ORACLE-MAP.json
- optional static package-only artifacts declared by MANIFEST
```

S05 is the sole implementation owner for final package construction and Candidate identity finalization. ChatGPT Plannerは三文書だけを生成し、control files、authority evidence、Review resultを生成しない。

#### 4.2.1 Canonical control JSON bytes

`SOURCE-BASELINE.json`、`MANIFEST.json`、`PLACEHOLDER-ORACLE-MAP.json`は`CanonicalControlJsonV1`でserializeする。

1. UTF-8、BOMなし、top-level JSON object。
2. duplicate keyはparse時に拒否し、required keyはexact、unknown keyは禁止する。
3. object keyは全階層でUTF-8 byte lexicographic ascending。
4. separatorは`,`と`:`だけを使い、insignificant whitespaceを含めない。
5. non-ASCII文字をescapeせずUTF-8でencodeする。
6. integerはbase-10でleading zeroなし。floatは使用しない。
7. array orderはschemaで固定し、producerまたはvalidatorがsilent sortしない。
8. fileはexactly one JSON valueの後に一つのLF (`0x0a`)を置く。CRLF、trailing whitespace、extra line、BOMを拒否する。

以下のpretty-printed JSONはmember setを示す。actual bytesは上記canonical one-line formである。

#### 4.2.2 `SOURCE-BASELINE.json`

```json
{
  "dependency_ids": [],
  "issue_id": "iss-00334",
  "parent_epic_id": "epic-00331",
  "parent_initiative_id": "init-00322",
  "relevant_paths": [],
  "schema_version": "spec-dock.issue-candidate-source-baseline.v1",
  "source_branch": "iss-00334-implement-chatgpt-issue-planning-workflow",
  "source_head": "0000000000000000000000000000000000000000",
  "source_repository": "chemitaro/spec-dock"
}
```

- exact top-level keysは上記9件。`schema_version`はexact literal `spec-dock.issue-candidate-source-baseline.v1`。
- `issue_id`、parent IDsはresolved Planning requestと一致する。
- `source_repository`、`source_branch`、`source_head`はexact Git preflight resultと一致し、`source_head`は40文字lowercase hexadecimalとする。
- `dependency_ids`はsorted unique Issue ID array。
- `relevant_paths`はsorted unique repo-relative POSIX path arrayで、各pathは`source_head`でtracked regular fileへ解決する。
- default branch、attached file、memory、first-match fallbackからfieldを補完しない。

#### 4.2.3 `MANIFEST.json`

```json
{
  "candidate": {
    "candidate_id": "iss-00334-v1-20260727t030000z",
    "created_at_utc": "2026-07-27T03:00:00Z",
    "internal_root": "20260727t030000z-iss-00334-issue-planning-candidate-v1/",
    "issue_id": "iss-00334",
    "logical_filename": "20260727t030000z-iss-00334-issue-planning-candidate-v1.zip",
    "version": 1
  },
  "checksum_algorithm": "sha256",
  "checksum_file": "CHECKSUMS.sha256",
  "entries": [],
  "placeholder_oracle_map_sha256": "<64 lowercase hexadecimal characters>",
  "schema_version": "spec-dock.issue-candidate-manifest.v1",
  "source_baseline_sha256": "<64 lowercase hexadecimal characters>"
}
```

- exact top-level keysは`candidate`、`checksum_algorithm`、`checksum_file`、`entries`、`placeholder_oracle_map_sha256`、`schema_version`、`source_baseline_sha256`。
- `schema_version`はexact literal `spec-dock.issue-candidate-manifest.v1`。
- `candidate` exact keysは`candidate_id`、`created_at_utc`、`internal_root`、`issue_id`、`logical_filename`、`version`。
- `version`はpositive integer。initial createは`1`、revisionはpredecessor version + 1。complete response validation後にrun-scoped UTC timestampを一度だけ取得する。
- `created_at_utc`はexact UTC RFC 3339 seconds form、filename timestampは同じinstantの`YYYYMMDDtHHMMSSz` form。
- `logical_filename = <timestamp>-<issue-id>-issue-planning-candidate-v<version>.zip`、`candidate_id = <issue-id>-v<version>-<timestamp>`、`internal_root = logical_filename`から`.zip`を除いたstem + `/`。
- `candidate.issue_id`は`SOURCE-BASELINE.json.issue_id`と一致する。
- source baselineとplaceholder mapのdigestは各exact file bytesのSHA-256。
- `checksum_algorithm`は`sha256`、`checksum_file`は`CHECKSUMS.sha256`。
- `entries`はactual regular file setとexact一致し、pathのUTF-8 byte lexicographic ascending、duplicateなし。
- 各entry exact keysは`checksum_covered`、`content_mode`、`path`、`role`。required seven rolesは各一件だけ存在する。
- `CHECKSUMS.sha256`だけが`checksum_covered=false`。その他はすべて`true`。v1 `content_mode`は`static`だけを許可する。
- optional artifactは`artifacts/<safe-relative-path>`配下、role=`package-artifact`、static、coveredとして明示し、authorityを主張してはならない。未宣言extra fileを拒否する。

#### 4.2.4 `PLACEHOLDER-ORACLE-MAP.json`

```json
{
  "files": [],
  "schema_version": "spec-dock.issue-candidate-placeholder-map.v1"
}
```

- exact top-level keysは`files`と`schema_version`。versionはexact literal `spec-dock.issue-candidate-placeholder-map.v1`。
- v1では`files`はexact empty arrayだけを許可する。全semantic文書とoptional artifactはstatic exact bytesであり、placeholder substitution、dynamic token、regex oracle、value-source lookupを許可しない。
- dynamic placeholder supportはnew schema version、closed token grammar、replacement source、parity rule、negative testsを伴うDesign amendmentを必要とする。

#### 4.2.5 `CHECKSUMS.sha256`

`CHECKSUMS.sha256`はUTF-8 ASCII subset、BOMなし、LF-only textとし、各lineは次のexact formである。

```text
<64 lowercase hexadecimal SHA-256><two ASCII spaces><entry path><LF>
```

- MANIFESTで`checksum_covered=true`の全entryを一件ずつ含み、`CHECKSUMS.sha256`自身を含めない。
- line orderはentry pathのUTF-8 byte lexicographic ascending。
- duplicate、missing、extra、uppercase digest、one-space／tab separator、CRLF、blank line、trailing space、root-prefixed pathを拒否する。
- digestはinternal-root-relative entryのexact uncompressed file bytesに対して計算する。

#### 4.2.6 Cross-file and archive closure

RuntimeとReviewerは、single rootとMANIFEST root、actual file setとentries、required roles、Candidate fields、source／placeholder digests、source binding、CHECKSUMS coverage／digests、static bytes、external ZIP SHA、CLI supplied ZIP SHAをcross-checkする。normalized logical filename、closed transport alias、internal root、Candidate ID、MANIFEST identity、external ZIP SHAが一つでも不一致なら`rejected`とする。

external ZIP SHAはarchive close後にZIP全bytesから計算し、ZIP内部control fileへ格納しない。validation failure時はfinal ZIP、final extraction tree、Review result、adoption output、owned temporary entryを残さない。Packagingはsafe external output directory内のowned temporary pathへ書き、新規final filenameへatomic publishする。existing final targetを上書きせず、ChatGPT response三文書をrewriteしない。

### 4.3 Reviewed Planning Identity

`ReviewedPlanningIdentityV1`は、次の二つのclosed objectのどちらか一つだけである。全object levelでrequired keyはexact、unknown keyとduplicate keyは禁止する。文字列を暗黙trim／case-fold／path-normalizeして別identityへ変換しない。

#### archive-candidate identity

```json
{
  "candidate_id": "<candidate id>",
  "internal_root": "<single candidate root ending with />",
  "issue_id": "iss-00334",
  "logical_filename": "<normalized logical ZIP filename>",
  "mode": "archive-candidate",
  "observed_transport_filename": "<observed external filename>",
  "source_branch": "<named branch>",
  "source_head": "<40 lowercase hexadecimal characters>",
  "source_repository": "<owner/repository>",
  "zip_sha256": "<64 lowercase hexadecimal characters>"
}
```

- `issue_id`、logical filename、ZIP SHA、internal root、Candidate ID、source repository／branch／HEADは§4.2 controlsおよびactual Candidate bytesと一致する。
- `observed_transport_filename`は実際に受け取ったfilenameである。transportによるclosed `(N)` aliasだけを既存contractどおりlogical filenameへnormalizeでき、それ以外のrename、root変更、repackagingを許可しない。

#### git-bound identity

```json
{
  "base": {
    "head": null,
    "kind": "none"
  },
  "branch": "<derived named branch>",
  "issue_id": "iss-00334",
  "mode": "git-bound",
  "repository": "<derived owner/repository>",
  "reviewed_head": "<40 lowercase hexadecimal characters>",
  "target_paths": [
    "<repo-relative POSIX path>"
  ]
}
```

`base` v1は`{"head":null,"kind":"none"}`または`{"head":"<40 lowercase hexadecimal characters>","kind":"semantic-base"}`だけである。

- `none`はCLI `--base-kind none`から構築し、`--base-head`を禁止する。
- `semantic-base`はCLI `--base-kind semantic-base --base-head <sha>`から構築する。base HEADはsame repositoryに存在し、`reviewed_head`のancestorでなければならない。
- `merge-base`はv1 identityで許可しない。
- `repository`と`branch`は§3のcurrent Git preflightから導出し、CLI overrideしない。
- `issue_id`はrequired `--issue`から解決し、target pathから推測しない。
- `target_paths`は1件以上、supplied orderがUTF-8 byte lexicographic ascending、duplicateなしでなければならない。
- 各pathはrelative POSIX pathであり、absolute path、`.`／`..` segment、backslash、NUL、empty segmentを拒否する。
- 各pathは`reviewed_head`でrepository内のtracked regular blobへ解決しなければならない。
- repository、branch、Issue、reviewed HEAD、target paths、baseのいずれかが変われば別identityである。

#### Canonical identity digest

`reviewed_identity_sha256`は、validated `ReviewedPlanningIdentityV1` objectを次のcanonical JSONへ変換したbytesのSHA-256である。

1. input JSONはUTF-8、BOMなしであり、duplicate keyをparse時に拒否する。
2. object keyを全階層でUTF-8 byte lexicographic ascendingにする。
3. separatorは`,`と`:`だけを使用し、insignificant whitespaceを含めない。
4. non-ASCII文字をescapeせずUTF-8でencodeする。
5. array orderは保持する。`target_paths`はvalidation前に並べ替えず、既にsortedであることを要求する。
6. digestは64文字lowercase hexadecimalで表す。

Review result、Human decision、CLIから構築したmode-specific identityは、same validated objectとのexact equalityとsame `reviewed_identity_sha256`の双方を満たさなければならない。digest一致だけでobject mismatchを許可せず、object一致だけでdigest mismatchを許可しない。

### 4.4 Review Result and Human Authorization Evidence

authority-bearing apply evidenceは`PlanningReviewResultV1`と`PlanningHumanDecisionV1`の二つだけである。既存Candidate decomposition／node creation approval contractとは別のnamed data contractだが、新しいschema registry、receipt registry、database、custom Git refを作らない。実装ownerは既存`domain/issue_planning_contracts.py`内のclosed data validationである。

全JSON objectはUTF-8、BOMなし、top-level object、duplicate keyなし、required key exact、unknown keyなしでなければならない。将来versionをv1 validatorがbest-effortで受理してはならない。

#### 4.4.1 `PlanningReviewResultV1`

```json
{
  "schema_version": "spec-dock.planning-review-result.v1",
  "evidence_kind": "planning-review-result",
  "issue_id": "iss-00334",
  "reviewer_role": "spec-reviewer",
  "reviewer_id": "<non-empty non-secret stable identifier>",
  "freshness": "fresh",
  "authority": "read-only",
  "verdict": "pass",
  "reviewed_at_utc": "2026-07-27T00:46:53Z",
  "reviewed_identity": {
    "<exact ReviewedPlanningIdentityV1 object>": "<mode-specific shape>"
  },
  "reviewed_identity_sha256": "<64 lowercase hexadecimal characters>",
  "finding_ids": []
}
```

Field semantics:

- `schema_version`はexact literal `spec-dock.planning-review-result.v1`。
- `evidence_kind`はexact literal `planning-review-result`。
- `issue_id`はCLI `--issue`、reviewed target Issue、`reviewed_identity.issue_id`とexact一致する。
- `reviewer_role`のv1許可値は`spec-reviewer`だけである。
- `reviewer_id`は1〜200文字のnon-secret attribution identifierであり、control character、line break、empty stringを拒否する。単独でapproval authorityを付与しない。
- `freshness`のv1許可値は`fresh`だけである。freshnessはwall-clock TTLではなく、exact reviewed identityとapply時current sourceのno-driftによって再検証する。
- `authority`のv1許可値は`read-only`だけである。
- `verdict`の許可値は`pass`または`fail`だけである。
- `reviewed_at_utc`はvalid calendar valueを持つexact UTC RFC 3339 seconds form `YYYY-MM-DDTHH:MM:SSZ`とする。offset、timezone abbreviation、date-only、missing secondsを拒否する。
- `reviewed_identity`は§4.3のclosed mode-specific objectである。
- `reviewed_identity_sha256`は§4.3のcanonical identity digestと一致する。
- `finding_ids`は0〜256件のsorted unique string arrayであり、各要素は1〜128文字、control characterなしとする。`fail`は1件以上を要求する。`pass`は0件以上を許可し、nonblocking observationの存在をauthorityへ昇格させない。

Review-result file identityはself-referential JSON fieldにしない。Runtimeがexternal fileを一回だけ読み、そのexact bytesから計算したSHA-256を`review_result_sha256`とする。Human decisionはこのexact file digestへbindし、別serialization、copy-and-edit、Markdown companion、同じ意味と推測された別bytesを代用できない。

#### 4.4.2 `PlanningHumanDecisionV1`

```json
{
  "approver_id": "<non-empty non-secret stable identifier>",
  "approver_role": "human",
  "decided_at_utc": "2026-07-27T01:00:00Z",
  "decision": "approved",
  "evidence_kind": "planning-human-decision",
  "implementation_start": true,
  "issue_id": "iss-00334",
  "plan_adoption": true,
  "review_result_sha256": "<SHA-256 of the exact PlanningReviewResultV1 file bytes>",
  "reviewed_identity": {
    "<exact ReviewedPlanningIdentityV1 object>": "<mode-specific shape>"
  },
  "reviewed_identity_sha256": "<64 lowercase hexadecimal characters>",
  "schema_version": "spec-dock.planning-human-decision.v1"
}
```

Field semantics:

- exact required keysは上記12件。unknown／duplicate keyは禁止する。
- `schema_version`はexact literal `spec-dock.planning-human-decision.v1`。
- `evidence_kind`はexact literal `planning-human-decision`。
- `issue_id`はCLI `--issue`、Review result、`reviewed_identity.issue_id`と一致する。
- `decision`のv1許可値は`approved`と`rejected`だけである。`revoked`を含む他値はinvalid enumとして`rejected`する。
- `approver_role`のv1許可値は`human`だけである。
- `approver_id`は1〜200文字のnon-secret stable identifierであり、control character、line break、empty stringを拒否する。
- `decided_at_utc`はexact UTC RFC 3339 seconds formであり、`reviewed_at_utc`より前であってはならない。
- `review_result_sha256`はRuntimeがsame invocationで一回だけ読み込んだexact Review-result file bytesのSHA-256と一致する。
- `reviewed_identity`と`reviewed_identity_sha256`はReview resultおよびCLI mode identityとexact一致する。

Allowed decision combinations are closed:

| `decision` | `plan_adoption` | `implementation_start` | Review verdict required for action | Effect |
|---|---:|---:|---|---|
| `approved` | `true` | `true` | `pass` | full adoption transactionへ進める |
| `rejected` | `false` | `false` | structurally valid `pass`または`fail` | decision-record transactionへ進める。canonical三文書を変更せず、verified publication後も`blocked` |

上記以外のpartial authorization、`approved` with false、`rejected` with trueはschema-semantic violationとして`rejected`する。

`PlanningHumanDecisionV1`はrevocation registryではない。approved publication後のwithdrawal／stop／revertはexisting shared Human／Main workflowのowner境界で扱い、`planning apply`はrevocation claimを受理・永続化・推測しない。

#### 4.4.3 Validation order and deterministic status semantics

`planning apply`は次のordered classificationをrepository mutation前から順に適用する。複数条件が同時に成立する場合は、番号が最も小さい条件だけをpublic `status`／`reason`に使用する。

1. required option／source presence。
2. mode-specific option matrixとpath safety。
3. Review／Human exact file-byte readとdigest。
4. JSON／schema／field validation。
5. reviewed identity validationとdigest再計算。
6. Review／Human／CLI／Issue cross-binding。
7. apply-time source freshness。
8. Review verdict／Human decision combination。
9. recovery-state classification。
10. transaction／publication result。

Pre-mutation mapping:

| Named reason | Status | Exit | Repository mutation |
|---|---|---:|---:|
| `missing_review_source` | `blocked` | 1 | 0 |
| `missing_human_source` | `blocked` | 1 | 0 |
| `malformed_evidence` | `rejected` | 1 | 0 |
| `wrong_schema_version` | `rejected` | 1 | 0 |
| `wrong_evidence_kind` | `rejected` | 1 | 0 |
| `missing_required_key` | `rejected` | 1 | 0 |
| `unknown_key` | `rejected` | 1 | 0 |
| `duplicate_key` | `rejected` | 1 | 0 |
| `invalid_field_type` | `rejected` | 1 | 0 |
| `invalid_enum` | `rejected` | 1 | 0 |
| `invalid_timestamp` | `rejected` | 1 | 0 |
| `invalid_digest` | `rejected` | 1 | 0 |
| `partial_authorization` | `rejected` | 1 | 0 |
| `wrong_reviewer_role` | `rejected` | 1 | 0 |
| `nonfresh_review_declaration` | `rejected` | 1 | 0 |
| `non_read_only_review_authority` | `rejected` | 1 | 0 |
| `mode_mismatch` | `rejected` | 1 | 0 |
| `issue_mismatch` | `rejected` | 1 | 0 |
| `identity_object_mismatch` | `rejected` | 1 | 0 |
| `identity_digest_mismatch` | `rejected` | 1 | 0 |
| `review_result_digest_mismatch` | `rejected` | 1 | 0 |
| `unsafe_decision_destination` | `rejected` | 1 | 0 |
| `unsupported_revocation` | `rejected` | 1 | 0 |
| `source_identity_drift` | `stale` | 1 | 0 |
| `candidate_identity_drift` | `stale` | 1 | 0 |
| `git_target_drift` | `stale` | 1 | 0 |
| `review_failed_for_approval` | `blocked` | 1 | 0 |
| `review_only` | `blocked` | 1 | 0 |
| `human_only` | `blocked` | 1 | 0 |
| `parity_only` | `blocked` | 1 | 0 |
| valid Review `pass` + valid Human `approved` | transaction preflightへ継続 | not yet ready | 0 until staging |
| valid Review `pass|fail` + valid Human `rejected` | decision-record transactionへ継続 | not yet final | 0 until staging |

Post-mutation／publication mapping:

| Named reason | Status | Exit | Required state |
|---|---|---:|---|
| `precommit_fault_restored` | `rolled_back` | 1 | bytes／mode／index／HEAD／clean statusがH0とexact一致 |
| `restore_incomplete` | `recovery_required` | 1 | original recovery workspaceとbounded remediationを保持 |
| `repository_visible_partial_without_workspace` | `recovery_required` | 1 | new mutation 0、original exact outputを要求 |
| `publication_incomplete` | `publication_pending` | 1 | exact local H1保持 |
| `remote_diverged` | `blocked_remote_diverged` | 1 | force／reset／amend／new commit 0 |
| `rejection_record_published` | `blocked` | 1 | decision artifact + exact Planning decision commitだけ |
| `adoption_published` | `ready` | 0 | full readiness conjunction成立 |

stage-only workspace orphanが別output invocationから不可視で、repository／index／HEADがexact clean H0、supplied outputにmanifestがない場合は`repository_visible_partial_without_workspace`に分類しない。§4.6の`new_workspace_attempt`として扱う。

Review-only、Human-only、parity-only、published rejectionでは`ready`を導出しない。mode reinterpretation、waiver、silent fallback、missing-field default、unknown-key ignore、unsupported revocation translationを行わない。

### 4.5 Readiness Result

```text
ReadinessResult = conjunction(
  valid PlanningReviewResultV1 with verdict = pass,
  valid PlanningHumanDecisionV1 with
      decision = approved,
      plan_adoption = true,
      implementation_start = true,
  exact review_result_sha256 binding,
  exact ReviewedPlanningIdentityV1 object and digest binding,
  apply-time source freshness,
  mode-specific parity,
  validation,
  Planning publication remote parity
)
```

専用state storeへ永続化せず、current Git／GitHub、exact external evidence bytes、canonical decision artifact、canonical filesから再構成する。いずれか一項だけ、またはReview／Human evidenceの構造上validなnegative decisionだけでは`ready`を導出しない。

### 4.6 Apply Request, Operation Identity, and Recovery Workspace

```text
PlanningApplyRequest
- issue_id / repository / branch / expected_head
- mode = archive-candidate | git-bound
- operation_kind = adoption | rejection-record
- reviewed_identity = validated ReviewedPlanningIdentityV1
- reviewed_identity_sha256
- review_result_path
- review_result_bytes = one read of the external file
- review_result_sha256 = sha256(review_result_bytes)
- review_result = validated PlanningReviewResultV1 parsed from the same bytes
- human_decision_path
- human_decision_bytes = one read of the external file
- human_decision_sha256 = sha256(human_decision_bytes)
- human_decision = validated PlanningHumanDecisionV1 parsed from the same bytes
- decision_artifact_repo_path
- archive identity:
    candidate_path / logical_filename / external_zip_sha256
  or git identity:
    reviewed_head / exact_target_paths / base
- canonical_output_directory
- output_directory_identity_sha256

PlanningApplyOperation
- operation_id = sha256(canonical JSON of:
    operation_kind,
    issue_id,
    repository,
    branch,
    expected_head,
    mode,
    reviewed_identity_sha256,
    review_result_sha256,
    human_decision_sha256,
    decision_artifact_repo_path)
- phase = preflight | staged | replaced | validated | committed | pushed | verified
- planning commit trailers:
    SpecDock-Planning-Operation: <operation_id>
    SpecDock-Planning-Workspace: <output_directory_identity_sha256>
```

`operation_kind`はHuman decisionからpureに導出し、`approved`は`adoption`、`rejected`は`rejection-record`とする。operation IDはtimestamp、host path、output directory、process IDを含めず、same reviewed identity／exact Review bytes／exact Human decision bytes／source binding／destination／operation kindからpureに導出する。

`review_result_sha256`と`human_decision_sha256`はCLI supplied literalを信用せず、Runtimeが一回だけ読み込んだbytesから計算する。Human decision内の`review_result_sha256`はactual Review-result bytesと一致しなければならない。

validated `approved`または`rejected` gate通過後だけ、`human_decision_bytes`を`decision_artifact_repo_path`へbyte-exactにstageする。Review result、Human decision、identity、source、destinationのvalidation中はcanonical tree、index、HEAD、operation manifestを変更しない。

#### Recovery workspace identity and bounded observability

1. `--output`はexisting non-symlink directoryとして検証する。
2. `canonical_output_directory`はstrict realpath解決後のabsolute normalized pathとする。
3. `output_directory_identity_sha256 = sha256(UTF-8 bytes of canonical_output_directory)`。
4. `workspace_attempt_id = sha256(canonical JSON of operation_id and output_directory_identity_sha256)`。
5. operation directoryは次のexact pathとする。

```text
<canonical-output-directory>/
  .spec-dock-planning-operations/
    <operation-id>/
```

6. recovery manifestは次のexact pathとする。

```text
<operation-directory>/recovery-manifest.json
```

`RecoveryManifestV1`はcanonical JSONであり、次をexact required fieldsとして持つ。

```text
schema_version = spec-dock.planning-recovery-manifest.v1
operation_id
operation_kind
workspace_attempt_id
output_directory_identity_sha256
issue_id
expected_head
reviewed_identity_sha256
review_result_sha256
human_decision_sha256
decision_artifact_repo_path
phase
targets[
  repo_path,
  before_sha256 or null,
  staged_sha256,
  backup_relative_path or null,
  completed
]
```

manifestはphase／target完了ごとにatomic replacementする。backup locatorはoperation-directory-relative non-symlink pathだけを許可する。

Recovery state classes are closed:

##### A. `workspace_only_stage`

次がすべて成立する状態。

- manifest phaseが`preflight`または`staged`。
- repository targetを一件も変更していない。
- 全target `completed=false`。
- 全`backup_relative_path=null`。
- index／worktree／HEADがexact clean H0。
- operation commit trailerが存在しない。

Behavior:

- same exact output invocationはmanifest identityを照合し、owned staged bytesとmanifestを安全にcleanupしてpreflightから再開する。cleanup失敗だけを`recovery_required: stage_orphan_cleanup_failed`とする。
- different／missing output invocationがsupplied outputにmanifestを持たず、repositoryがexact clean H0なら`new_workspace_attempt`として開始できる。別outputを列挙・検索せず、未知のstage-only orphanだけを理由に`recovery_required`を返さない。
- original output workspaceはauthorityを持たないinert orphanである。same-output reuse時にRuntimeがcleanupする。Mainが手動cleanupする場合は、exact known operation path、valid manifest、stage-only phase、completed target 0、backup 0、operation commit 0を確認した場合だけoperation directoryを削除し、その観測結果をCandidate外evidenceへ記録する。
- global orphan registry、home scan、repository-wide output scan、custom Git refを作らない。

##### B. `repository_visible_precommit`

repository／indexはH0から変化しているがcommitは存在せず、current bytesがexact immutable inputsから導出したtransaction prefixと一致する状態。

Transaction prefixは次の順だけを許可する。

```text
decision artifact
→ requirement.md
→ design.md
→ plan.md
```

- same exact outputとvalid manifestがある場合だけrollback／resumeできる。
- different／missing outputでmanifestを取得できない場合は`recovery_required: repository_visible_partial_without_workspace`、exit 1、new operation directory作成 0、new repository mutation 0とする。
- current dirty stateがexact transaction prefixと一致しない場合はrecovery stateと推測せず`blocked: dirty_tree`とする。

##### C. `committed_publication`

exact local H1がoperation trailerとworkspace trailerを持つ状態。

- same output identity、parent H0、tree、operation trailer、workspace trailerが一致する場合だけpush／remote verificationからresumeする。
- different／missing output identityは`recovery_required: committed_operation_workspace_mismatch`とし、new commit／reset／amend／force pushを行わない。
- remote divergenceは`blocked_remote_diverged`とする。

##### D. `clean_new_attempt`

supplied outputにmanifestがなく、repository／index／HEADがexact clean H0で、operation commitも存在しない状態。

- new invocationとして開始できる。
- 他outputの存在を推測またはscanしない。

completed success時はbackupを削除する。completed manifestとexternal result JSONはoperation-local observational evidenceとして保持できるが、readiness authorityにはしない。

## 5. One Decision, Adoption, and Publication Lifecycle

```text
Candidate or reviewed git target at H0
→ read-only Review bound to H0
→ Human decision bound to the exact Review bytes and H0 identity
→ approved:
     archive atomic adoption + candidate parity
       OR git-bound reviewed-blob-preserving adoption
     → validate
     → dedicated Planning adoption commit H1
     → push / fetch / remote == H1 / tree parity
     → ready
  rejected:
     decision artifact only
     → validate approval-free diff
     → dedicated Planning decision commit H1
     → push / fetch / remote == H1 / tree parity
     → blocked; no canonical three-document mutation
```

- archive adoption source parentはreviewed source H0。
- git-bound target blobsはreviewed H0のbytesを維持する。
- approved adoptionはsame reviewed planning identityを消費する。
- rejected decision-recordはsame reviewed identityとexact Review bytesを記録するが、canonical三文書を変更せずreadinessを導出しない。
- rejection publicationによるH1はH0-bound Review／approvalをstaleにする。その後のapprovalにはH1-bound fresh Review／Human decisionが必要である。
- Review output、Human decision、adoption、decision recording、publicationは異なるauthority／operation phaseであり、一つのresultへ統合しない。
- approved publication後のrevocationは本v1 lifecycleに含めず、existing Human／Main stop-or-revert ownerへrouteする。

### 5.1 Apply State Machine and Transaction Boundary

```text
preflight
  → validate all immutable inputs
  → classify recovery state using:
       supplied output workspace
       exact repository/index/HEAD
       exact operation/tree trailers
  → workspace_only_stage at same output:
       cleanup owned stage-only workspace
       restart preflight
  → clean_new_attempt:
       bind new workspace attempt
  → repository_visible_precommit:
       require exact original workspace
       rollback or stop recovery_required
  → committed_publication:
       require exact original workspace
       resume publication or stop
  → if operation_kind = adoption:
       stage decision artifact + canonical replacement set outside repository
    else operation_kind = rejection-record:
       stage decision artifact only outside repository
  → validate staged set
  → backup every existing target byte/mode
  → add decision artifact
  → if adoption:
       replace requirement → design → plan
  → validate exact allowed diff, bytes, parity, and operation kind
  → create one Planning commit with operation/workspace trailers
  → push
  → fetch and verify remote HEAD/tree
  → if adoption: ready
    else rejection-record: blocked
```

- `ScopedFileTransaction`を`infra/scoped_file_transaction.py`へ置き、`runbook_store.py`のcurrent stage／backup／restore behaviorを同primitiveへ移してcharacterization testsを維持する。Issue Planningは同primitiveを使用し、private helperをimportせず同等実装を複製しない。
- mutation前にCandidate／git identity、Review result、Human decision、operation kind、decision destination、clean branch、upstream、local／remote／expected HEAD、workspace safetyを検証する。
- adoptionのallowed diffはnew decision artifactとexact canonical replacement setだけである。
- rejection-recordのallowed diffはnew decision artifact一件だけであり、`requirement.md`、`design.md`、`plan.md`、`.assurance.json`、他artifactを変更しない。
- external staging完了前またはstage-only完了後のcrashでrepositoryがexact clean H0なら、repository rollbackは不要である。same-output retryはowned stage-only workspaceをcleanupして再開する。
- stage-only crash後のdifferent-output invocationは、supplied outputにmanifestがなくrepositoryがexact clean H0ならfresh workspace attemptとして開始できる。unknown original outputをscanせず、false `recovery_required`を生成しない。
- decision artifact追加後からcommit成功前までの例外、validation failure、commit failure、process interruptはreverse-order restoreを試み、new decision artifactを除去し、original bytes／mode／index／HEAD／`git status --porcelain=v1`を照合する。
- restore成功は`rolled_back: precommit_fault_restored`。
- restore不一致は`recovery_required: restore_incomplete`。
- wrong-output retryでrepositoryがexact transaction prefixに一致する場合は`recovery_required: repository_visible_partial_without_workspace`。
- wrong-output retryでdirty stateがtransaction prefixと一致しない場合は`blocked: dirty_tree`。
- commit成功後はautomatic rollback、reset、amend、force pushを行わない。
- push failureまたはresponse lossではlocal H1を保持して`publication_pending: publication_incomplete`を返す。
- same-operation retryはoperation trailer、workspace trailer、exact tree、parent H0、same output identityを照合する。
- wrong output identityを持つpost-commit retryは`recovery_required: committed_operation_workspace_mismatch`とする。
- remoteがH1ならremote verificationへ進む。remoteがH0かつlocal H1がexactならpushをretryする。それ以外は`blocked_remote_diverged: remote_diverged`。
- adoption verified successだけが`ready: adoption_published`。
- rejection-record verified successは`blocked: rejection_record_published`。
- success時はbackupを削除する。external result JSONとcompleted manifestは観測Evidenceであり、readiness authorityはReview、Human approval、canonical parity、validation、local／remote commit/treeから再構成する。

## 6. Review Transport and Isolation

### 6.1 archive-candidate

- default for pre-canonical semantic iteration。
- single root、regular UTF-8 text、MANIFEST／CHECKSUMS、source bindingを検証する。
- outer ZIP 10,000,000 bytes、64 entries、per-entry 2,000,000 bytes、expanded total 10,000,000 bytes、path 240 UTF-8 bytes、compression ratio 100をinclusive ceilingとする。
- rejected inputからfinal extraction tree、review result、adoption outputを残さない。

### 6.2 git-bound

- actual repository path、CI、inline review等が必要なときだけ選択する。
- exact Issue ID、derived repository／branch、reviewed HEAD、sorted target paths、v1 baseを固定する。
- v1 baseは`none`またはexact ancestor `semantic-base`だけである。merge-base comparisonはv1外であり、new identity schemaなしに推測しない。
- archiveへsilent fallbackせず、別modeまたはbase kindへ切り替える場合はnew Review identityとする。

### 6.3 Read-only guard

1. Review前にCandidate SHAと`git status --porcelain=v1`を記録する。
2. Reviewerへread-only sourceとseparate output directoryだけを渡す。
3. Review後にCandidate SHAとtracked/untracked inventoryを再取得する。
4. Candidateまたはrepository mutationがあればReview resultをinvalidとする。

forensic database、custom refs、generalized mutation inventoryは作らない。

## 7. Revision Lanes

| Lane | Allowed | Executor | Result |
|---|---|---|---|
| Semantic | Requirement、Architecture、scope、AC、Gate、Workflow meaning | ChatGPT Blue Team | complete replacement Candidate |
| Mechanical | closed path／field／literal、meaning invariant、bounded diff | Main／deterministic script | complete new Candidate identity or bounded git correction |

Skillがlaneを選択する。CLI／wrapperはmaterialityを推測しない。Review findingがparent boundaryやshared policyへ属する場合、本Issueへ取り込まずowning scopeへrouteする。

## 8. Provider-first Implementation

### 8.1 Module Dependency

```text
spec-dock-chatgpt entrypoint
  → chatgpt CLI parser / restricted registry
    → planning command handlers
      → issue planning application service
        → existing authoring_pack preflight / backend / review / approval primitives
        → planning domain contracts
        → filesystem / Git / Oracle adapter
      → planning presentation renderer
```

Provider `src/spec_dock/`がimplementation authorityであり、root `spec-dock/`はgenerated dogfood projectionである。workerはgenerated projectionを直接編集しない。

### 8.2 Directory / File Change Plan

```text
src/spec_dock/
├── cli.py                                           # install/update executable handling
└── assets/
    ├── install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
    └── spec_dock/
        ├── docs/
        │   ├── README.md
        │   ├── workflow_planning.md                 # new shared planning reference
        │   └── reference_chatgpt_cli.md             # new CLI reference
        ├── system/prompts/issue-planning/
        │   ├── create.md
        │   ├── revise.md
        │   └── review.md
        └── scripts/
            ├── spec-dock-chatgpt                    # new independent executable
            └── spec_dock_runtime/
                ├── chatgpt_app.py
                ├── cli/chatgpt_parser.py
                ├── commands/planning.py
                ├── application/issue_planning.py
                ├── domain/issue_planning_contracts.py
                ├── domain/authoring_pack/zip_contract.py # bounded additive shared archive contract
                ├── infra/issue_planning_io.py
                ├── infra/scoped_file_transaction.py
                ├── infra/runbook_store.py               # shared transaction primitiveへ移行
                └── presentation/issue_planning.py

tests/
├── cli_runtime/test_authoring.py                  # existing generic archive default regression
├── cli_runtime/test_chatgpt_planning.py
├── manual_tests/test_review_chatgpt_authoring_pack.py # existing compatibility regression
├── unit/application/test_issue_planning.py
├── unit/domain/test_issue_planning_contracts.py
├── unit/infra/test_issue_planning_archive.py
├── unit/infra/test_scoped_file_transaction.py
├── unit/infra/test_runbook_store.py
├── unit/infra/test_init_update.py
├── unit/presentation/test_issue_planning.py
└── integration/
    ├── test_chatgpt_planning_fake_oracle.py
    └── test_chatgpt_planning_dogfood.py
```

既存`authoring_pack` archive primitiveはS05でだけbounded additive extensionする。`review_pack_input(input_path)`の既存default root、required metadata、limits、status taxonomyを変えず、closed data-only `ArchiveReviewContract` parameterへ既存defaultとIssue Candidate用の二つのnamed contractを与える。

Issue Candidate contractは§4.2のexact root、mandatory paths、control-file schema versions、canonical JSON bytes、MANIFEST inventory、CHECKSUMS format、cross-file digests、external ZIP digest、Candidate identity fields、current ceilingsをdataとして列挙する。schema registry、plugin/callback framework、parallel validator、allocator、new state storeを導入しない。既存default behaviorを保てない場合はstopし、Design amendmentへ戻る。

## 9. Prompt and Output Design

- Prompt resourceはprovider-managed Markdownで、scope identity、parent context、exact source、closed output contract、security constraintsを含む。
- ChatGPT Planner responseはexactly three complete Markdown files (`requirement.md`, `design.md`, `plan.md`)であり、control filesやReview resultを含めない。
- Core Runtime final artifactは三文書と§4.2のexact-versioned `SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`を必須とするsingle-root immutable ZIPである。
- v1 Placeholder Oracle mapはemptyであり、全Candidate entryをstatic exact bytesとして扱う。
- optional package-only artifactはMANIFESTへ明示され、static、checksummed、non-authoritativeな場合だけ含められる。
- incomplete／duplicate／unexpected response file、non-UTF-8、authority claim、raw transcript、prohibited secret-like payloadをcontrol generation前に拒否する。
- wrong schema version、missing／unknown／duplicate key、noncanonical serialization、inventory／checksum／cross-file digest／identity／source binding mismatchはfinal ZIPまたはReview outputを残さず拒否する。
- `planning create`成功resultはfinal ZIP path、logical filename、Candidate ID、version、internal root、source binding、external ZIP SHAを返し、そのpathを変更・再packagingせずarchive Reviewへ渡せる。
- external ZIP SHAはZIP内部へ格納せず、archive close後のexact ZIP bytesから計算する。

## 10. Human Gate and Adoption

- `PlanningReviewResultV1`はHuman decisionの入力であり、単独ではstart authorityではない。
- archive Human decisionはexact archive identity object／digestとexact Review-result file SHAへbindする。
- git-bound Human decisionはexact Issue／repository／branch／reviewed HEAD／target paths／base object／digestとexact Review-result file SHAへbindする。
- positive Human gateは`decision=approved`、`plan_adoption=true`、`implementation_start=true`、Review `pass`が同時に成立する場合だけである。
- valid `decision=rejected`はnegative Human decisionであり、decision-record transactionとしてexact bytesをcanonical Issue artifactへpublishできる。canonical三文書を変更せず、final statusは`blocked`である。
- `decision=revoked`はv1 unsupportedであり、Runtimeは生成、推測、保存、supersession lookupを行わない。
- approved publication後のHuman withdrawal／stop／revertはcurrent shared workflowへrouteし、source-changing evidenceがないrevocation claimをproduct authorityにしない。
- MainだけがHuman-supplied evidenceを確認して`planning apply`を起動する。CLI／RuntimeはReview verdict、Human decision、approver identity、missing field、modeを生成・推測しない。
- Runtimeはshared transaction primitiveでfull adoptionまたはdecision-recordを処理し、Main authority下でGit commit／pushを行う。
- RuntimeはPA-NF-01〜PA-NF-09、PA-NF-10A、PA-NF-10Bの11 fixtureをexact named statusで独立に拒否またはnon-ready化する。
- Candidate adoption、decision recording、publication、readinessの副作用として`.assurance.json`を変更しない。

## 11. Security and Failure Handling

| Named observable failure | Public result | Recovery |
|---|---|---|
| unknown Issue | `blocked: unknown_issue` | valid Issue IDを選択してnew run |
| dirty tree before operation | `blocked: dirty_tree` | unrelated workを解消しclean H0からnew run |
| upstream missing | `blocked: upstream_missing` | upstreamを設定してnew run |
| remote access unavailable | `blocked: remote_unavailable` | remote accessを復旧してnew run |
| current branch／upstream branch mismatch | `stale: branch_upstream_mismatch` | intended named branchへsource refresh |
| local／remote HEAD mismatch | `stale: local_remote_mismatch` | fetch／reconcile後にfresh identity |
| expected HEAD mismatch | `stale: expected_head_mismatch` | current exact HEADへfresh Review／Human decision |
| information insufficient | `blocked: information_insufficient` | bounded missing contextを補いnew run |
| unsafe Prompt／attachment／output path | `rejected: unsafe_path` | safe external pathを選択 |
| prohibited secret-like content | `rejected: prohibited_content` | prohibited contentを除去。backend call 0 |
| backend missing | `blocked: backend_unavailable` | backendを利用可能にしてsame contractでnew run |
| backend timeout | `blocked: backend_timeout` | bounded diagnostic後にnew run |
| backend nonzero | `blocked: backend_nonzero` | bounded redacted diagnosticに従いnew run |
| malformed／partial Planner response | `rejected: malformed_planner_response` | Semantic rerun／revision。final Candidate 0 |
| unexpected response file | `rejected: unexpected_response_file` | closed three-file responseでrerun |
| non-UTF-8 response | `rejected: non_utf8_response` | valid UTF-8 responseでrerun |
| authority claim in Planner response | `rejected: planner_authority_claim` | authority claimを含まないfresh response |
| unsafe archive／integrity mismatch | `rejected: archive_rejected` | new complete Candidate |
| Review mutation detected | `rejected: review_mutation_detected` | clean stateへ戻しfresh Review |
| Human approved against Review fail | `blocked: review_failed_for_approval` | findings反映後にfresh Review |
| valid Human rejection | decision-record transaction後`blocked: rejection_record_published` | published H1へsource refreshし、後続approvalはfresh Review |
| unsupported Human revocation claim | `rejected: unsupported_revocation` | shared Human／Main stop-or-revert ownerへroute |
| stage-only same-output cleanup failure | `recovery_required: stage_orphan_cleanup_failed` | exact original outputでbounded cleanup |
| repository-visible precommit state + original workspace unavailable | `recovery_required: repository_visible_partial_without_workspace` | exact original outputを再指定 |
| unrelated dirty state during retry | `blocked: dirty_tree` | unrelated workを解消 |
| pre-commit fault + exact restore | `rolled_back: precommit_fault_restored` | clean H0からsame or new run |
| restore incomplete | `recovery_required: restore_incomplete` | automatic continuation禁止 |
| push failure／response loss after H1 | `publication_pending: publication_incomplete` | same operation／workspaceでresume |
| wrong workspace for committed operation | `recovery_required: committed_operation_workspace_mismatch` | exact original outputを再指定 |
| retry remote divergence | `blocked_remote_diverged: remote_diverged` | force／resetせずHuman／Main reconcile |

Classification orderはCLI／path → target／Git → prohibited content → backend → Planner response → Review／Human apply evidence → recovery state → transaction／publicationとする。同じnamed fixtureに複数statusを許可しない。

Sensitive diagnostics are bounded and redacted. Direct argv is default. Shell exception is unavailable without explicit Human-approved Design and rollback evidence.

## 12. Compatibility and Projection

- `uv build` produces wheel／sdist using repository provisioning.
- fresh environments install each artifact and run `spec-dock init` and `spec-dock update`.
- both repo-local entrypoints are regular non-symlink files with executable mode on POSIX and can run directly.
- provider managed file set equals installed and dogfood projections after init/update.
- existing Core CLI, authoring-pack tests, validate／sync behavior remain green.
- physical removal of old planning routes remains E1-I3 work; this Issue only adds and activates the replacement path needed for its acceptance.

## 13. JIT Dogfood

S09Aではfake backend／fake remote／temporary repositoryだけを使うhermetic testとして、eligible／ineligible selection、pre-mutation abort、transaction rollback、publication retryを検証する。S09Aのworkerはcredential、live backend、real canonical path、push authorityを持たない。

S09BはMain/Human operation gateであり、pytestではない。Humanがtarget Issue、dedicated clean worktree／branch、selected mode、許可するcanonical paths、push先、evidence destinationを明示承認した場合だけMainが実行する。Mainは開始前にtargetがREQ-018を満たすこと、他作業がないこと、pre-commit rollback pathがGreenであることを記録する。abort／failureは§5.1に従い、push済みcommitの取り消しは自動化せず別のHuman-authorized revertとして扱う。Dogfood evidenceはiss-00334 `artifacts/` direct childとtargetのauthorized decision artifactへ保存し、raw transcriptやcredentialを残さない。

## 14. Risk Register

| Risk ID | Risk | Design control | Verification owner |
|---|---|---|---|
| RISK-001 | multi-file partial adoptionでcanonical bytesが混在する | shared scoped transaction、reverse restore、recovery manifest、fault injection | S06 |
| RISK-002 | unsafe／ambiguous archiveがresource exhaustionまたはpath escapeを起こす | closed Issue archive contract、class-by-class fail-closed matrix、partial-output 0 | S05 |
| RISK-003 | live dogfoodが別Issue／remoteへ無許可変更する | S09A hermetic testとS09B Human/Main gateの分離 | S09A/S09B |
| RISK-004 | shared archive／runbook behaviorが新機能で退行する | default contractとrunbook characterizationを先に固定 | S05/S06/S08 |
| RISK-005 | commit済みpush失敗をrollbackして履歴／identityを曖昧にする | `publication_pending`、operation trailer、same-operation resume、no force/reset | S06 |

## 15. External Delivery Boundary

After S99, Main uses the current shared delivery workflow for PR delivery and merge preparation. The implementation remains one Issue／one branch／one Delivery PR; required review precedes Human-only merge. This design does not redefine report/HEAD ordering, merge strategy, `issue finish`, or lifecycle recovery.
