# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a66b411-5e70-83e8-bd27-1c2c18b35763

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Continue only as the dedicated Blue Team author for iss-00334. The attached file is the new formal fresh Red review of the corrected snapshot. First use @GitHub to inspect the current branch at the exact actual remote HEAD 546245f1072e6d7822fc7885eff814ac1eca1dc5 and confirm the latest canonical requirement.md, design.md, plan.md, report.md, .assurance.json, and this review artifact. Candidate identity is unambiguous: this is the commit you must correct. P1-11 was caused solely by Main supplying an incorrect requested SHA; do not change the product specification for that finding, but record that the next review must use the actual full HEAD. Produce bounded replacement-ready Markdown blocks for P1-12 through P1-16 and P2-03/P2-04 only. Reconcile EC-005 status semantics; close all public CLI mode-specific identity arguments including git base fields; make rejection/revocation semantics coherent and enforceable without inventing a broad authority subsystem; close versioned byte-level Candidate control-file schemas; split benign direct-argv and prohibited-secret pre-invocation tests; define multi-owner Closure partial/final semantics; and deterministically bind recovery-manifest lookup. Preserve all previously closed controls and the one-Issue/one-branch/one-PR boundary. Do not review for PASS, do not edit the repository, do not produce a patch or ZIP. Return verified HEAD/paths, exact Design replacements/additions, exact Plan replacements/additions, Requirement changes only if strictly necessary, traceability/test impacts, and a non-regression self-check.

## Answer

# 1. Verified source identity and inspected inputs

GitHub connector access succeeded.

| Field                  | Verified value                                                                                  |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| Repository             | `chemitaro/spec-dock`                                                                           |
| Default branch         | `main`                                                                                          |
| Current branch         | `iss-00334-implement-chatgpt-issue-planning-workflow`                                           |
| Actual remote HEAD     | `546245f1072e6d7822fc7885eff814ac1eca1dc5`                                                      |
| Branch/HEAD comparison | identical; ahead `0`, behind `0`                                                                |
| Commit purpose         | bounded Design/Plan correction, Assurance rebinding, Report update, and Blue artifact recording |

The exact commit exists and records the prior bounded correction.

Canonical Issue directory:

```text
spec-dock/initiatives/
  init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
  epics/epic-00331-planning-and-advisory-review/
  issues/iss-00334-implement-chatgpt-issue-planning-workflow/
```

| Canonical path    | Git blob at verified HEAD                  |
| ----------------- | ------------------------------------------ |
| `requirement.md`  | `df1ca20421d3d7d56fc920d735e5f59ef7cacfa5` |
| `design.md`       | `59e26d57d693d996226fc473923c2b7d7c650b97` |
| `plan.md`         | `ae61ebf5f16a1c960a80a2bba0e9efab2e05b870` |
| `report.md`       | `1ff9ac76752d82459bfaf1f95c9f5d4e85fbf1e5` |
| `.assurance.json` | `9b99ee8bb3a826da4bcafcb248f75f66203d44a8` |

The Requirement currently assigns all EC-005 conditions to `blocked`; the corrected Design and Plan instead divide them among `rejected`, `stale`, and `blocked`.  The current Design still uses `[mode identity]`, does not expose every git base field, names but does not schema-close the four Candidate controls, treats `revoked` as valid durable evidence without a durable mutation path, and permits the combined argv/redaction oracle identified by the Red review.    The current Plan contains the corresponding ambiguous PA-NF status, combined S03 security test, high-level S05 control validation, and operation-directory lookup gap.

The new Red artifact is an attached review of this snapshot rather than a Git blob contained in the reviewed commit. Its source table independently identifies the same actual HEAD and the same canonical blobs.

## P1-11 disposition

No product Requirement, Design, or Plan change is made for P1-11.

The next fresh review invocation must use this exact requested identity:

```text
546245f1072e6d7822fc7885eff814ac1eca1dc5
```

It must not reuse the incorrect SHA:

```text
546245f1b0a7f8fe616fe6f13b6f4534f40d77cc
```

The attached review confirms that the latter was a different, nonexistent 40-character identifier supplied to the reviewer.

No repository mutation, patch, ZIP, or review verdict is produced below.

# 2. Requirement replacements strictly required

Requirement changes are necessary only for P1-12 and P1-14. REQ-004 and REQ-021 already require the relevant outcomes; their byte-level and test-level realization remains Design/Plan ownership.

## Requirement replacement R-01 — replace all of `### REQ-015 Workbench and Durable Evidence`

```markdown
### REQ-015 Workbench and Durable Evidence

Workbenchはprompt、explicit external files、downloaded Candidate、Review result、Human decision source、operation-local staging／backup／recovery manifest、diagnosticsのtemporary surfaceに限定する。raw transcriptを保存せず、`report.md`をPlanning receipt、Review authority、Human authorization authority、readiness state storeにしない。

`PlanningHumanDecisionV1`のv1許可decisionは`approved`と`rejected`だけである。

- `approved`はexact Review-result bytesとexact reviewed identityへbindし、`plan_adoption=true`かつ`implementation_start=true`を要求する。`planning apply`はvalidated Human decision sourceのexact bytesを明示されたIssue `artifacts/` direct-child JSONへ記録し、mode固有のcanonical adoption、validation、Planning publicationを一つのtransactionとして実行する。
- `rejected`はexact Review-result bytesとexact reviewed identityへbindし、`plan_adoption=false`かつ`implementation_start=false`を要求する。`planning apply`はdecision artifactだけを追加するbounded decision-record transactionを実行し、`requirement.md`、`design.md`、`plan.md`を変更しない。dedicated Planning decision commitのpushとremote parityが成立した後もresultは`blocked`、exit `1`であり、readinessを導出しない。
- published rejectionはrepository HEADを変更するため、rejection前のHEADへbindされたReview result、Human approval、Candidate identity、git-bound identityを`stale`にする。その後のapprovalはnew HEADへbindしたfresh Reviewとnew Human decisionを必要とする。
- `revoked`は`PlanningHumanDecisionV1` v1に含めない。approved publication後のHuman withdrawal、implementation stop、または履歴取消しはcurrent shared Human／Main stop-or-revert workflowのowner境界で扱い、`planning apply`は`decision=revoked`を`rejected`としてrepository mutation前に拒否する。source-changing stop／revert evidenceがない口頭またはWorkbench上のrevocation claimを、既存approvalを失効させるproduct authorityとして扱わない。

decision artifactは`planning apply --decision-artifact`で明示された新規Issue `artifacts/` direct-child JSONだけへbyte-exactに記録する。operation完了後はbackupを削除し、external result JSONは観測Evidenceとしてだけ保持する。専用authority registry、revocation registry、state database、custom Git refを新設しない。
```

## Requirement replacement R-02 — replace the `EC-005` row in `## 7. Error Conditions`

```markdown
| EC-005 | Review／Human gate evidenceまたはdecision destinationの不成立 | required Review-result sourceまたはHuman-decision sourceの欠落／不存在は`blocked`、mutation 0。malformed JSON、wrong schema version／kind、missing／unknown／duplicate key、invalid enum／timestamp／digest、partial authorization、Review／Human／CLI mode・Issue・identity・digest mismatch、unsafe／existing／scope外destination、unsupported `decision=revoked`は`rejected`、mutation 0。validated identityに対するcurrent source／Candidate／target driftは`stale`、mutation 0。valid Review `fail`とHuman `approved`の組合せは`blocked`、mutation 0。valid Human `rejected`はdecision-record transactionへ進み、verified remote publication後に`blocked`、exit `1`、canonical三文書mutation 0 |
```

## Requirement replacement R-03 — replace all of `### AC-010 Adoption Negative Set`

```markdown
### AC-010 Adoption Negative Set

PA-NF-01〜PA-NF-10を各独立named fixtureとして実行し、各fixtureがDesign／Planで固定された一つのexact stable status、exit `1`、readinessなし、許可されたmutation contractだけを返すことを確認する。genericな「reject」または複数statusの許容を代替証拠にせず、10／10でexpected status一致、violations 0を得る。
```

# 3. Exact Design replacements and additions

## Design replacement D-01 — replace all of `## 3. Public Command Design`

````markdown
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
- text／JSONは同じstable `status`を返す。`ready`だけexit `0`、`blocked`、`stale`、`rejected`、`rolled_back`、`publication_pending`、`blocked_remote_diverged`、`recovery_required`はexit `1`。
- output directoryはrepository／canonical tree外のexisting non-symlink directoryに限定する。
````

## Design replacement D-02 — replace all of `### 4.2 Planner Response, Runtime Package, and Candidate Identity`

````markdown
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

1. UTF-8、BOMなし。
2. top-level JSON object。
3. duplicate keyはparse時に拒否。
4. required keyはexact、unknown keyは禁止。
5. object keyは全階層でUTF-8 byte lexicographic ascending。
6. separatorは`,`と`:`だけを使い、insignificant whitespaceを含めない。
7. non-ASCII文字をescapeせずUTF-8でencodeする。
8. integerはbase-10でleading zeroなし。floatは使用しない。
9. array orderはschemaで固定し、producerまたはvalidatorがsilent sortしない。
10. fileはexactly one JSON valueの後に一つのLF (`0x0a`)を置く。CRLF、trailing whitespace、extra line、BOMを拒否する。

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

- exact top-level keysは上記9件。
- `schema_version`はexact literal `spec-dock.issue-candidate-source-baseline.v1`。
- `issue_id`、parent IDsはresolved Planning requestと一致する。
- `source_repository`、`source_branch`、`source_head`はexact Git preflight resultと一致する。
- `source_head`は40文字lowercase hexadecimal。
- `dependency_ids`はsorted unique Issue ID array。
- `relevant_paths`はsorted unique repo-relative POSIX path arrayであり、各pathは`source_head`でtracked regular fileへ解決する。
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
  "entries": [
    {
      "checksum_covered": false,
      "content_mode": "static",
      "path": "CHECKSUMS.sha256",
      "role": "checksums"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "MANIFEST.json",
      "role": "manifest"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "PLACEHOLDER-ORACLE-MAP.json",
      "role": "placeholder-map"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "SOURCE-BASELINE.json",
      "role": "source-baseline"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "design.md",
      "role": "design"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "plan.md",
      "role": "plan"
    },
    {
      "checksum_covered": true,
      "content_mode": "static",
      "path": "requirement.md",
      "role": "requirement"
    }
  ],
  "placeholder_oracle_map_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "schema_version": "spec-dock.issue-candidate-manifest.v1",
  "source_baseline_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
}
```

- exact top-level keysは`candidate`、`checksum_algorithm`、`checksum_file`、`entries`、`placeholder_oracle_map_sha256`、`schema_version`、`source_baseline_sha256`。
- `schema_version`はexact literal `spec-dock.issue-candidate-manifest.v1`。
- `candidate` exact keysは`candidate_id`、`created_at_utc`、`internal_root`、`issue_id`、`logical_filename`、`version`。
- `version`はpositive integer。initial createは`1`、revisionはpredecessor version + 1。
- complete Planner response validation後にrun-scoped UTC timestampを一度だけ取得する。
- `created_at_utc`はexact UTC RFC 3339 seconds form。
- filename timestampは同じinstantの`YYYYMMDDtHHMMSSz` form。
- `logical_filename = <timestamp>-<issue-id>-issue-planning-candidate-v<version>.zip`。
- `candidate_id = <issue-id>-v<version>-<timestamp>`。
- `internal_root = logical_filename`から`.zip`を除いたstem + `/`。
- `candidate.issue_id`は`SOURCE-BASELINE.json.issue_id`と一致する。
- `source_baseline_sha256`はexact `SOURCE-BASELINE.json` file bytesのSHA-256。
- `placeholder_oracle_map_sha256`はexact `PLACEHOLDER-ORACLE-MAP.json` file bytesのSHA-256。
- `checksum_algorithm`はexact literal `sha256`、`checksum_file`はexact literal `CHECKSUMS.sha256`。
- `entries`はactual regular file setとexact一致し、`path`のUTF-8 byte lexicographic ascending、duplicateなし。
- required seven rolesは各一件だけ存在する。
- `CHECKSUMS.sha256`だけが`checksum_covered=false`。その他はすべて`true`。
- v1 `content_mode`は`static`だけを許可する。
- optional package-only artifactは`artifacts/<safe-relative-path>`配下、role=`package-artifact`、`content_mode=static`、`checksum_covered=true`として明示する。未宣言extra fileを拒否する。
- optional artifactはReview、Human authorization、readiness authorityを主張してはならない。

#### 4.2.4 `PLACEHOLDER-ORACLE-MAP.json`

```json
{
  "files": [],
  "schema_version": "spec-dock.issue-candidate-placeholder-map.v1"
}
```

- exact top-level keysは`files`と`schema_version`。
- `schema_version`はexact literal `spec-dock.issue-candidate-placeholder-map.v1`。
- v1では`files`はexact empty arrayだけを許可する。
- v1 Candidate内の全semantic文書とoptional artifactはstatic exact bytesであり、placeholder substitution、dynamic token、regex oracle、value-source lookupを許可しない。
- dynamic placeholder supportが必要になった場合はnew schema version、closed token grammar、replacement source、parity rule、negative testsをDesign amendmentで定義する。

#### 4.2.5 `CHECKSUMS.sha256`

`CHECKSUMS.sha256`はUTF-8 ASCII subset、BOMなし、LF-only textとする。各lineは次のexact formである。

```text
<64 lowercase hexadecimal SHA-256><two ASCII spaces><entry path><LF>
```

- MANIFESTで`checksum_covered=true`の全entryを一件ずつ含む。
- `CHECKSUMS.sha256`自身を含めない。self-checksum、placeholder digest、zero digestによる循環回避を行わない。
- line orderはentry pathのUTF-8 byte lexicographic ascending。
- duplicate、missing、extra、uppercase digest、one-space separator、tab separator、CRLF、blank line、trailing space、root-prefixed pathを拒否する。
- digestはinternal-root-relative entryのexact uncompressed file bytesに対して計算する。

#### 4.2.6 Cross-file and archive closure

RuntimeとReviewerは次をすべて検証する。

1. ZIPは`MANIFEST.candidate.internal_root`とexact一致するsingle rootを持つ。
2. actual regular file setは`MANIFEST.entries.path` setとexact一致する。
3. required seven files／rolesはexactly one。
4. MANIFEST candidate fields、logical filename、Candidate ID、version、timestamp、internal rootは相互一致する。
5. SOURCE baseline digest、placeholder-map digestはMANIFEST値と一致する。
6. SOURCE baseline Issue／repository／branch／HEADはPlanning preflightと一致する。
7. `CHECKSUMS.sha256` line setとdigestはMANIFEST coverageおよびactual bytesと一致する。
8. static filesはReview前後、adoption前までbyte-exact不変。
9. external ZIP SHA-256はarchive close後にZIP全bytesから計算し、ZIP内部control fileには格納しない。
10. Review／apply CLI supplied `--zip-sha256`はactual external ZIP SHA-256と一致する。
11. normalized logical filename、observed transport filenameのclosed alias、internal root、Candidate ID、MANIFEST identity、external ZIP SHAが一つでも不一致なら`rejected`とする。
12. validation failure時はfinal ZIP、final extraction tree、Review result、adoption output、owned temporary entryを残さない。

Packagingはsafe external output directory内のowned temporary pathへ書き、new final filenameへatomic publishする。existing final targetを上書きしない。ChatGPT response三文書はcontrol-file generation中にrewriteしない。
````

## Design replacement D-03 — replace all of `### 4.3 Reviewed Planning Identity`

````markdown
### 4.3 Reviewed Planning Identity

`ReviewedPlanningIdentityV1`は次の二つのclosed objectのどちらか一つだけである。全object levelでrequired keyはexact、unknown keyとduplicate keyは禁止する。文字列を暗黙trim／case-fold／path-normalizeして別identityへ変換しない。

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

`base` v1は次の二形だけである。

```json
{"head": null, "kind": "none"}
```

```json
{"head": "<40 lowercase hexadecimal characters>", "kind": "semantic-base"}
```

- `none`はCLI `--base-kind none`から構築し、`--base-head`を禁止する。
- `semantic-base`はCLI `--base-kind semantic-base --base-head <sha>`から構築する。base HEADはsame repositoryに存在し、`reviewed_head`のancestorでなければならない。
- `merge-base`はv1 identityで許可しない。
- `repository`と`branch`は§3のcurrent Git preflightから導出し、CLI overrideしない。
- `issue_id`はrequired `--issue`から解決し、target pathから推測しない。
- `target_paths`は1件以上、supplied orderがUTF-8 byte lexicographic ascending、duplicateなしでなければならない。
- 各pathはrelative POSIX pathであり、absolute path、`.`／`..` segment、backslash、NUL、empty segmentを拒否する。
- 各pathは`reviewed_head`でrepository内のtracked regular blobへ解決する。
- repository、branch、Issue、reviewed HEAD、target paths、baseのいずれかが変われば別identityである。

#### Canonical identity digest

`reviewed_identity_sha256`はvalidated `ReviewedPlanningIdentityV1` objectを次のcanonical JSONへ変換したbytesのSHA-256である。

1. input JSONはUTF-8、BOMなしであり、duplicate keyをparse時に拒否する。
2. object keyを全階層でUTF-8 byte lexicographic ascendingにする。
3. separatorは`,`と`:`だけを使用し、insignificant whitespaceを含めない。
4. non-ASCII文字をescapeせずUTF-8でencodeする。
5. array orderは保持する。`target_paths`はvalidation前に並べ替えず、既にsortedであることを要求する。
6. digestは64文字lowercase hexadecimalで表す。

Review result、Human decision、CLIから構築したmode-specific identityは、same validated objectとのexact equalityとsame `reviewed_identity_sha256`の双方を満たさなければならない。digest一致だけでobject mismatchを許可せず、object一致だけでdigest mismatchを許可しない。
````

## Design replacement D-04 — in `#### 4.4.1 PlanningReviewResultV1`, replace the `issue_id` field-semantics bullet

```markdown
- `issue_id`はCLI `--issue`、reviewed target Issue、`reviewed_identity.issue_id`とexact一致する。
```

## Design replacement D-05 — replace all of `#### 4.4.2 PlanningHumanDecisionV1`

````markdown
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
  "review_result_sha256": "<SHA-256 of exact PlanningReviewResultV1 file bytes>",
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
````

## Design replacement D-06 — replace all of `#### 4.4.3 Validation order and rejection semantics`

```markdown
#### 4.4.3 Validation order and stable status semantics

`planning apply`は次の順序で検証する。

1. required request identity options、Review／Human source options、output、decision destinationの存在を確認する。
2. path safetyとmode-specific option matrixを検証する。
3. Review／Human external JSONをそれぞれ一回だけbytesとして読み、exact file SHA-256を計算する。
4. UTF-8、JSON object、duplicate key、schema version、evidence kind、required／unknown key、field type、enum、timestamp、digest formatを検証する。
5. 各`reviewed_identity`を§4.3で検証し、canonical digestを再計算する。
6. Review、Human、CLI mode identity、Issue IDのexact cross-bindingを検証する。
7. Human `review_result_sha256`とactual Review-result bytesを照合する。
8. current repository／branch／HEAD／Candidate bytes／target blobsをreviewed identityへ照合し、source freshnessを再評価する。
9. Review verdictとHuman decision combinationを評価する。
10. `approved`はfull adoption transaction、`rejected`はdecision-record transactionへ進む。

Stable mapping:

| Named condition | Status | Exit | Repository mutation |
|---|---|---:|---:|
| `missing-review-source` | `blocked` | 1 | 0 |
| `missing-human-source` | `blocked` | 1 | 0 |
| malformed JSON、wrong version／kind、missing／unknown／duplicate key、invalid type／enum／timestamp／digest | `rejected` | 1 | 0 |
| partial authorization | `rejected` | 1 | 0 |
| wrong reviewer role、non-fresh declaration、non-read-only authority | `rejected` | 1 | 0 |
| Review／Human／CLI mode mismatch | `rejected` | 1 | 0 |
| Review／Human／CLI Issue／identity object／identity digest mismatch | `rejected` | 1 | 0 |
| Human `review_result_sha256` mismatch | `rejected` | 1 | 0 |
| unsafe／existing／scope外 decision destination | `rejected` | 1 | 0 |
| unsupported `decision=revoked` | `rejected` | 1 | 0 |
| valid identityに対するcurrent source／Candidate／target drift | `stale` | 1 | 0 |
| valid Review `fail` + Human `approved` | `blocked` | 1 | 0 |
| valid Review `pass` + Human `approved` with both authorizations | full adoption transactionへ継続 | not yet ready | 0 until staging |
| valid Review `pass|fail` + Human `rejected` with both authorizations false | decision-record transactionへ継続 | not yet final | 0 until staging |
| rejection-record commit／push／remote parity verified | `blocked` | 1 | decision artifact + one Planning decision commit only |

decision-record transaction中のpre-commit failure、restore failure、push failure、remote divergenceはfull adoptionと同じ`rolled_back`、`recovery_required`、`publication_pending`、`blocked_remote_diverged` semanticsを使用する。

Review-only、Human-only、parity-onlyでは`ready`にしない。mode reinterpretation、waiver、silent fallback、missing field default、unknown-key ignore、unsupported revocationのbest-effort translationを行わない。
```

## Design replacement D-07 — replace all of `### 4.6 Apply Request and Operation Identity`

````markdown
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

`operation_kind`はHuman decisionからpureに導出する。

- `approved` → `adoption`
- `rejected` → `rejection-record`

operation IDはtimestamp、host path、output directory、process IDを含めない。same reviewed identity／exact Review bytes／exact Human decision bytes／source binding／destination／operation kindからpureに導出する。

#### Recovery workspace identity

1. `--output`はexisting non-symlink directoryとして検証する。
2. `canonical_output_directory`はstrict realpath解決後のabsolute normalized pathである。
3. `output_directory_identity_sha256 = sha256(UTF-8 bytes of canonical_output_directory)`。
4. operation directoryは次のexact pathである。

```text
<canonical-output-directory>/.spec-dock-planning-operations/<operation-id>/
```

5. recovery manifestは次のexact pathである。

```text
<operation-directory>/recovery-manifest.json
```

`RecoveryManifestV1`はCanonicalControlJsonV1相当のUTF-8 canonical JSONであり、少なくとも次をexact required fieldsとして持つ。

```text
schema_version = spec-dock.planning-recovery-manifest.v1
operation_id
operation_kind
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

- manifestはphase／target完了ごとにatomic replacementする。
- backup locatorはoperation directory relative pathであり、scope外path、absolute path、symlinkを許可しない。
- same-operation pre-commit retryはsame `--output`を必須とし、computed output identity、operation directory、manifest operation ID／digestsがexact一致しなければ`recovery_required`、exit `1`、new mutation 0とする。
- same-operation post-commit retryはcommitの二つのtrailers、exact tree、parent H0、same output identityを照合する。
- different／missing output directoryでpartial worktree、operation trailer、またはrecovery-required stateを検出した場合、他directoryを列挙・検索せず`recovery_required`とする。bounded remediationはoriginal exact output directoryを再指定することである。
- supplied output directoryにmanifestがなく、worktree／index／HEADがexact clean H0ならnew invocationとしてpreflightから開始できる。
- global registry、home-directory scan、repository scan、custom Git ref、databaseを作らない。
- verified success時はbackupを削除する。completed manifestとexternal result JSONはoperation-local observational evidenceとして保持できるが、readiness authorityにしない。
````

## Design replacement D-08 — replace all of `## 5. One Adoption and Publication Lifecycle`

````markdown
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
````

## Design replacement D-09 — replace all of `### 5.1 Apply State Machine and Transaction Boundary`

````markdown
### 5.1 Apply State Machine and Transaction Boundary

```text
preflight
  → validate all immutable inputs
  → bind deterministic recovery workspace
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

- `ScopedFileTransaction`を`infra/scoped_file_transaction.py`へ置き、`runbook_store.py`のcurrent stage／backup／restore behaviorを同primitiveへ移してcharacterization testsを維持する。Issue Planningは同primitiveを使用し、private helperをimportせず、同等実装を複製しない。
- mutation前にCandidate／git identity、Review result、Human decision、operation kind、decision destination、clean branch、upstream、local==remote==expected HEAD、deterministic operation directory safetyをすべて検証する。
- adoptionのallowed diffはnew decision artifactとexact canonical replacement setだけである。
- rejection-recordのallowed diffはnew decision artifact一件だけであり、`requirement.md`、`design.md`、`plan.md`、`.assurance.json`、他artifactを変更してはならない。
- stage完了後からcommit成功前までの例外、validation failure、commit failure、process interruptはreverse-order restoreを試み、new decision artifactを除去し、original bytes／mode／index／HEAD／`git status --porcelain=v1`を照合する。成功は`rolled_back`、一点でも不一致なら`recovery_required`で停止する。
- recovery manifestは§4.6のdeterministic pathにatomic updateする。same-operation invocationだけがsame output identityのmanifestを読み、commitが存在しなければrollbackを完了してclean baselineから再開する。
-異なるoperationはexisting operation directory／manifestを上書きしない。
- commit成功後はautomatic rollback、reset、amend、force pushを行わない。push失敗またはresponse lossではlocal H1を保持して`publication_pending`を返す。
- same-operation retryはoperation trailer、workspace trailer、exact tree、parent H0、manifest identityを照合してpushまたはremote verificationから再開する。
- retry時にremote==H1ならpush済みとしてremote/tree verificationへ進む。remoteがH0でもlocal H1がexactならpushをretryする。それ以外は`blocked_remote_diverged`とし、Human／Mainへreconcileを返す。
- adoption verified successだけが`ready`を返す。
- rejection-record verified successは`blocked`、exit `1`を返し、evidence locator、old H0、new H1、decision digest、fresh Review requiredを示す。
- success時はbackupを削除する。external result JSONとcompleted recovery manifestは観測Evidenceであり、readiness authorityはReview、Human approval、canonical parity、validation、local／remote commit/treeから再構成する。
````

## Design replacement D-10 — replace all of `### 6.2 git-bound`

```markdown
### 6.2 git-bound

- actual repository path、CI、inline review等が必要なときだけ選択する。
- exact Issue ID、derived repository／branch、reviewed HEAD、sorted target paths、v1 baseを固定する。
- v1 baseは`none`またはexact ancestor `semantic-base`だけである。merge-base comparisonはv1外であり、new identity schemaなしに推測しない。
- archiveへsilent fallbackせず、別modeまたはbase kindへ切り替える場合はnew Review identityとする。
```

## Design replacement D-11 — replace the final paragraph of `### 8.2 Directory / File Change Plan`

```markdown
既存`authoring_pack` archive primitiveはS05でだけbounded additive extensionする。`review_pack_input(input_path)`の既存default root、required metadata、limits、status taxonomyを変えず、closed data-only `ArchiveReviewContract` parameterへ既存defaultとIssue Candidate用の二つのnamed contractを与える。

Issue Candidate contractは§4.2のexact root、mandatory paths、control-file schema versions、canonical JSON bytes、MANIFEST inventory、CHECKSUMS format、cross-file digests、external ZIP digest、Candidate identity fields、current ceilingsをdataとして列挙する。schema registry、plugin/callback framework、parallel validator、allocator、new state storeを導入しない。既存default behaviorを保てない場合はstopし、Design amendmentへ戻る。
```

## Design replacement D-12 — replace all of `## 9. Prompt and Output Design`

```markdown
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
```

## Design replacement D-13 — replace all of `## 10. Human Gate and Adoption`

```markdown
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
- RuntimeはPA-NF-01〜PA-NF-10をexact named statusで独立に拒否またはnon-ready化する。
- Candidate adoption、decision recording、publication、readinessの副作用として`.assurance.json`を変更しない。
```

## Design replacement D-14 — replace the `Human rejection` row in `## 11. Security and Failure Handling` and add the following row after it

```markdown
| valid Human rejection | bounded decision-record transaction。verified remote parity後も`blocked`、canonical三文書mutation 0 | published rejection HEADへsourceをrefreshし、後続approvalはfresh Reviewから開始 |
| unsupported Human revocation claim | `rejected`、mutation 0 | current shared Human／Main stop-or-revert ownerへroute |
```

# 4. Exact Plan replacements and additions

## Plan replacement P-01 — replace the introductory paragraph under `## 8. Spec-Locked Closure Index`

````markdown
この索引はmaterial obligationsのbounded coverage ledgerであり、全test implementation inventoryやglobal proof registryではない。summary rowは既存test-card参照を安定させるaliasで`required=no`であり、closure stateを持たない。individual `required=yes` rowがS99で閉じる必須契約である。

Closure stateは`Closure ID`と`Closure owner`の組で管理する。

- single-owner rowは一つのowner portionを持つ。
- multi-owner rowはownerごとに独立したportionを持つ。例: owner=`S01/S06`は`(Closure ID,S01)`と`(Closure ID,S06)`の二portionである。
- owner portion stateの許可値は`open`、`passed`、`failed`、`blocked`だけである。
- stepは自身のowner portionだけを`passed`にできる。他owner portionまたはaggregate rowをcloseできない。
- aggregate stateは、全owner portionが`passed`のときだけ`closed`である。一つでも`open|failed|blocked`ならaggregateは`open`である。
- observed testだけ、reviewerだけ、commit候補だけではowner portionを`passed`にしない。step-local required evidence、required reviewer、Main Result Approval、commitまたはapproved-no-op、post-commit clean checkの全条件を要求する。
- 後続drift、invalidated evidence、failed re-reviewは該当owner portionを再び`open|failed|blocked`にし、aggregateを再openする。
- 本Plan内でmulti-owner rowについて「closeする」と書かれている箇所は、明示的にaggregate closureと書かれていない限り、そのstepのowner portionだけを意味する。

Mainは`report.md#Step-Contract-Closure`または`report.md#Test-Contract-Closure`へ次のexact fieldsを一行ずつ記録する。

```text
closure_id
closure_owner
owner_portion_state
observed_evidence
reviewer_verdict
commit_or_approved_noop
post_commit_clean
recorded_at_head
````

`report.md#Closure-Coverage`は各required rowについて全owner portion stateとderived aggregate stateを表示する。S99は全`required=yes` aggregate stateが`closed`であることを検証し、portion-level passをaggregate closureの代用にしない。

````

## Plan replacement P-02 — replace the indicated summary Closure rows

```markdown
| `CLOS-CLI` | REQ-002 / AC-002 | independent entrypoint help and parser matrix | four commands; exact archive/git review/apply options; no placeholder or cross-mode acceptance | hidden／incomplete public route | S01 | no | summary | `tc-s01-001`, `tc-s01-004` | `report.md#Step-Contract-Closure` |
| `CLOS-CREATE` | REQ-004 / AC-001,004 | complete Planner response | immutable seven-file Candidate with closed v1 controls and direct Review handoff | partial／schema-ambiguous／repacked Candidate | S03/S05 | no | summary | `tc-s05-001`, `tc-s05-003`, `tc-s05-006` | `report.md#Step-Contract-Closure` |
| `CLOS-SEC` | REQ-021 / AC-011 | benign metacharacter fixture and prohibited-content fixture | direct argv without shell; prohibited content blocked before backend | shell injection／secret transmission | S03 | no | summary | `tc-s03-003`, `tc-s03-004` | `report.md#Step-Contract-Closure` |
| `CLOS-ARCHIVE` | REQ-010,022 / AC-006 | Candidate ZIP bytes and control schemas | v1 controls, every archive class, cross-file and external digest fail closed with outputs 0 | path escape／resource exhaustion／identity or control substitution | S05 | no | summary | `tc-s05-003`, `tc-s05-004[*]`, `tc-s05-006[*]` | `report.md#Step-Contract-Closure` |
| `CLOS-ADOPTION` | REQ-009–012 / AC-008,009 | exact parser identity + Review v1 + Human decision v1 | approved full apply or rejected decision-record only; sole public transactional route; remote-equal publication | unbound authority／partial adoption／undurable rejection | S06 | no | summary | `tc-s06-001`, `tc-s06-002`, `tc-s06-009`–`tc-s06-012` | `report.md#Step-Contract-Closure` |
````

## Plan replacement P-03 — replace the indicated Requirement Closure rows

```markdown
| `CLOS-REQ-002` | REQ-002 / AC-002 / Design §3 | CLI help and parser argv matrix | four commands; exact archive/git review/apply options; repository/branch derived; mode options closed | lifecycle available only through internals／placeholder argv | S01 | yes | red-required | `tc-s01-001`, `tc-s01-004` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-004` | REQ-004 / AC-001,004 / Design §4.2 | complete three-doc response and four exact controls | canonical v1 control bytes, exact inventory/checksums/cross-file binding, no overwrite | schema-divergent／identity-inconsistent artifact | S03/S05 | yes | red-required | `tc-s05-001`, `tc-s05-003`, `tc-s05-006[*]` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-006` | REQ-006 / AC-005 / Design §§3,4.3 | explicit Review mode and full parser identity | archive identity or git identity with exact Issue/base; no silent fallback／reuse | cross-mode／base-field evidence reuse | S05 | yes | red-required | `tc-s05-005`, `tc-s01-004` + archive positive | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-009` | REQ-009 / AC-008,009 / Design §§3,4.3–5.1 | exact CLI identity + Review v1 + Human decision v1 | approved full apply; rejected decision-record; both modes admitted without reinterpretation | ad-hoc call／Candidate-only gate／undurable rejection | S01/S06 | yes | red-required | `tc-s01-004`, `tc-s06-001`, `tc-s06-002`, `tc-s06-009`–`tc-s06-012` | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-015` | REQ-015 / AC-013 / Design §§4.4–5.1 | exact Review bytes／Human decision bytes／decision artifact／publication | approved adoption or durable rejected decision-record; revoked unsupported; no authority registry | evidence substitution／false revocation／partial approval | S06 | yes | red-required | `tc-s06-009`, `tc-s06-010`, `tc-s06-011`, state-boundary assertions | `report.md#Test-Contract-Closure` |
| `CLOS-REQ-021` | REQ-021 / AC-011 | benign metacharacter and prohibited sentinel fixtures | benign values remain argv elements; prohibited content rejected before backend call | shell injection／secret disclosure to backend | S03/S08 | yes | red-required | `tc-s03-003`, `tc-s03-004`, integrated security fixture | `report.md#Test-Contract-Closure` |
```

## Plan replacement P-04 — replace the `CLOS-EC-005` row

```markdown
| `CLOS-EC-005` | EC-005 / Design §4.4.3 | named missing／malformed／negative／mismatched／stale／destination fixtures | missing Review/Human=`blocked`; malformed/cross-binding/unsafe/unsupported-revoked=`rejected`; source drift=`stale`; valid rejection publishes decision-only then returns `blocked`; no named fixture accepts multiple status | approval bypass／wrong status masking／undurable rejection | S06 | yes | red-required | `tc-s06-003`, `tc-s06-009`, `tc-s06-010`, `tc-s06-011` | `report.md#Test-Contract-Closure` |
```

## Plan replacement P-05 — replace the indicated PA-NF rows

```markdown
| `CLOS-PA-NF-01` | PA-NF-01 | valid archive Review v1 only; Human source absent | `blocked`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-01]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-02` | PA-NF-02 | valid git-bound Review v1 only; Human source absent | `blocked`, exit 1, mutation 0 | Review-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-02]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-03` | PA-NF-03 | Human approved source only; Review-result source absent | `blocked`, exit 1, mutation 0 | approval-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-03]` | `report.md#Test-Contract-Closure` |
| `CLOS-PA-NF-04` | PA-NF-04 | parity only; Review and Human sources absent | `blocked`, exit 1, mutation 0 | parity-only start | S06/S08 | yes | red-required | `tc-s06-003[pa-nf-04]` | `report.md#Test-Contract-Closure` |
```

## Plan replacement P-06 — replace the `CLOS-ARC-19` row

```markdown
| `CLOS-ARC-19` | REQ-004,022 inventory／controls | each required control key, canonical bytes, MANIFEST inventory, CHECKSUMS coverage, cross-file digest | valid exact v1 controls pass; every missing／unknown／duplicate／wrong-version／serialization／inventory／digest parameter rejects with outputs 0 | missing/substituted/ambiguous control file | S05 | yes | red-required | `tc-s05-004[arc-19-inventory]`, `tc-s05-006[ctl-*]` | `report.md#Test-Contract-Closure` |
```

## Plan replacement P-07 — replace the S01 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- test obligation:
  - four-command public help。
  - exact archive／git-bound `review planning` and `planning apply` option inventory。
  - required `--issue`。
  - deterministic repository／branch derivation and absence of public overrides。
  - git base `none`／`semantic-base` positive contract。
  - omitted、cross-mode、contradictory、unsupported merge-base negative matrix。
  - known-valid Issue exact target resolution。
  - unknown Issue fail-closed resolution。
- positive target oracle: known-valid fixtureはrepo root、canonical Issue path、parent Epic／Initiative、declared dependencies、explicit branch／HEADをexactに返し、default branch、active alias、attached／tracked file、first-match searchへのfallbackがないことを観測する。
- red or alternative evidence requirement: red-required: current source has no complete public parser surface or approved exact target-resolution contract。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいcommand family、repository／branch override、merge-base support、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

## Plan replacement P-08 — replace `tc-s01-001` and add `tc-s01-004` after `tc-s01-003`

```markdown
- `tc-s01-001` acceptance: 独立CLIが四つのsupported commandとexact mode helpを公開する
  - 前提: temp managed repositoryを使う。
  - 操作: entrypoint、各command、archive／git mode helpを直接実行する。
  - 期待結果:
    - planning create／planning revise／review planning／planning applyだけが表示される。
    - archive Review helpは`--issue --mode archive-candidate --candidate --logical-filename --zip-sha256 --output`を示す。
    - git Review helpは`--issue --mode git-bound --reviewed-head --target --base-kind [--base-head] --output`を示す。
    - archive apply helpとgit apply helpがDesign §3のexact argsを示す。
    - `[mode identity]`、public repository／branch override、Core lifecycle commandは表示されない。
  - 失敗検出: incomplete public identity、placeholder contract、entrypoint混線を検出する。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-REQ-002`

- `tc-s01-004` contract: mode-specific parser matrixを閉じる
  - 前提:
    - positive: `archive-review`、`archive-apply-approved`、`archive-apply-rejected`、`git-review-none`、`git-review-semantic-base`、`git-apply-none`、`git-apply-semantic-base`。
    - negative: `missing-issue`、`missing-mode-identity`、`archive-with-git-option`、`git-with-archive-option`、`missing-target`、`unsorted-targets`、`duplicate-target`、`none-with-base-head`、`semantic-base-without-base-head`、`semantic-base-nonancestor`、`unsupported-merge-base`、`repository-override`、`branch-override`。
  - 操作: parserとidentity constructorを各named parameterで実行する。
  - 期待結果:
    - positiveはone exact `ReviewedPlanningIdentityV1`を構築する。
    - missing Review／Human authority sourceだけは`blocked`。
    - 他negativeは`rejected`。
    - backend call、filesystem mutation、Git mutationは0。
    - repository／branchはfixture current Git/upstreamから導出される。
  - 失敗検出: hidden defaults、Issue inference、cross-mode option、base field omission、silent sortingを防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`, `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-CLI`, `CLOS-REQ-002`, `CLOS-REQ-006`, `CLOS-REQ-009`
```

## Plan replacement P-09 — replace S01 `step closure contract`

```markdown
#### step closure contract

`CLOS-CLI`、`CLOS-REQ-002`、`CLOS-REQ-009`のS01 owner portion、`CLOS-EC-001`のS01 owner portion、およびClosure IndexでS01をownerに持つ全`required=yes` owner portionは、exact help Green、parser matrix全件、unknown-target negative Green、known-valid target positive Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけ`passed`にする。

S01は`CLOS-REQ-009` aggregateをcloseしない。S06 owner portionが`passed`になるまでaggregate stateは`open`のままとする。
```

## Plan replacement P-10 — replace the S03 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- test obligation:
  - exact Git preflight。
  - backend non-invocation on source mismatch。
  - complete three-document response validation。
  - benign shell metacharacterのplanning-specific direct argv capture。
  - prohibited secret-like contentのpre-invocation rejection。
  - no repository mutation。
- direct-argv fixtureとprohibited-content fixtureを分離し、一つのfixtureで双方をcloseしない。
- planning-specific fixture ownerは`tests/unit/application/test_issue_planning.py`または`tests/integration/test_chatgpt_planning_fake_oracle.py`のS03 allowed pathだけ。authoring-pack fixtureをS03 Red ownerにしない。
- prohibited-content validationはPrompt rendering、attachment materialization、backend argv construction、backend invocationより前に行う。
- red or alternative evidence requirement:
  - direct-argv Red: benign metacharacterがshell stringへ結合されるknown-bad。
  - prohibited-content Red: sentinelがbackend argvまたはrendered inputへ到達するknown-bad。
- owned Green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- covered-existing regression: `uv run pytest tests/unit/authoring_pack/test_github_fetch_policy.py -q`。file変更、planning fixture追加、S03 Red ownershipは禁止する。
- refactor guardrail: Candidate packaging、archive identity、new persistent state、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

## Plan replacement P-11 — replace `tc-s03-003` and add `tc-s03-004`

```markdown
- `tc-s03-003` security: benign shell metacharacterをseparate direct argv elementsとして扱う
  - 前提: spaces、quotes、semicolon、dollar、parentheses、Unicodeを含むがREQ-021 prohibited contentではないoperator contextとsafe external path、argv-capturing fake backendを用意する。
  - 操作: planning createのbackend invocationを実行する。
  - 期待結果:
    - backend call countは1。
    - each untrusted valueはone argv elementとしてbyte-preservingに保持される。
    - `shell=False`相当でshell string construction／shell executionは0。
    - repository mutationは0。
  - 失敗検出: command injection、argv element collapse、shell fallbackを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`, `CLOS-REQ-021`

- `tc-s03-004` security: prohibited secret-like contentをbackend invocation前に拒否する
  - 前提: unique secret sentinelと、secret／token／cookie／credential／private-key marker、`.env` path、production-dump marker、private-customer-data markerを各独立parameterとしてoperator context、explicit file、attachment candidateへ配置する。
  - 操作: planning createのpre-invocation input validationを実行する。
  - 期待結果:
    - status=`rejected`、exit 1。
    - backend call countは0。
    - rendered Prompt、attachment staging tree、attachment inventory、captured argv、diagnostics、text／JSON result、Planner response、Candidate outputのいずれにもsentinelが存在しない。
    - repository／output final artifact mutationは0。
  - 失敗検出: direct argvでshell injectionだけを防ぎ、secretをbackendへ送信する回帰を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-SEC`, `CLOS-REQ-021`
```

## Plan replacement P-12 — replace S03 `step closure contract`

```markdown
#### step closure contract

`CLOS-GIT`、`CLOS-SEC`、`CLOS-REQ-003`、`CLOS-REQ-021`のS03 owner portion、`CLOS-EC-001`、`CLOS-EC-002`のS03 owner portion、およびClosure IndexでS03をownerに持つ全`required=yes` owner portionは、source／response Green、benign direct-argv Green、prohibited-content backend-call-zero Green、covered-existing Git-fetch policy Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけ`passed`にする。

`tests/unit/authoring_pack/test_github_fetch_policy.py`はcovered-existingであり、S03 planning fixture、allowed edit、Red ownerにはしない。`CLOS-CREATE`と`CLOS-REQ-004` aggregateはS05 owner portionがpassedになるまでopenのままにする。
```

## Plan replacement P-13 — replace the S05 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- packaging owner: S05のみ。ChatGPT responseはexact三文書、Runtime final artifactは三文書＋Design §4.2のexact-versioned four controlsのimmutable ZIP。
- control serialization:
  - JSON controlsはCanonicalControlJsonV1。
  - Placeholder map v1はexact empty。
  - CHECKSUMSはall covered entries except itself。
  - external ZIP SHAはarchive外で計算。
- identity rule: initial createはversion 1、revisionはpredecessor version + 1。one timestampからlogical filename／Candidate ID／internal rootを導出する。source bindingはS03 preflight resultを使う。
- publication rule: owned temporary fileからsafe external output directoryのnew final filenameへatomic publishし、existing final targetを上書きしない。
- shared primitive rule: `zip_contract.py`へclosed data-only Issue Candidate contractを追加し、argument omitted時のexisting authoring-pack default behaviorを完全に保持する。
- test obligation:
  - create→exact final ZIP→archive Review direct handoff。
  - generic default regression。
  - exact control-schema positive。
  - every required-key／unknown／duplicate／version／canonical-byte／inventory／checksum／cross-file／external-SHA negative。
  - archive／git Review identity including Issue and git base。
  - read-only mutation guard。
- red or alternative evidence requirement:
  - red-required for direct handoff and Issue-specific control schema。
  - covered-existing for generic authoring-pack default。
- green verification: `uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: generic default意味変更、dynamic placeholder support、merge-base support、new schema registry、parallel validator、unrelated cleanupを追加しない。
- amendment trigger: existing generic behaviorを保てない、control schema拡張、target追加、new persistent state、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。
```

## Plan replacement P-14 — replace `tc-s05-003`, replace `tc-s05-005`, and add `tc-s05-006`

```markdown
- `tc-s05-003` acceptance: exact v1 Candidate controlsとidentityを検証する
  - 前提: Design §4.2のcanonical source baseline、manifest、empty placeholder map、checksums、三文書を持つsafe Candidateを用意する。
  - 操作: Issue Candidate named contractでpackagingとarchive validationを実行する。
  - 期待結果:
    - required seven rolesがexactly one。
    - actual inventory == MANIFEST entries。
    - JSON controlsはcanonical bytes。
    - source／placeholder digests、CHECKSUMS lines、entry bytesが一致する。
    - Candidate ID／version／timestamp／logical filename／root／Issue／source bindingが一致する。
    - actual external ZIP SHAがresultへ返る。
  - 失敗検出: mandatory control omission、cross-Candidate substitution、stale source、ambiguous serialization、checksum mismatchを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-ARCHIVE`, `CLOS-REQ-004`

- `tc-s05-005` contract: Review identityはexact Issueとclosed git baseを要求する
  - 前提:
    - archive positive。
    - git positive `base=none`。
    - git positive `base=semantic-base` with exact ancestor。
    - negative `missing-issue`、`missing-reviewed-head`、`missing-target`、`unsorted-target`、`duplicate-target`、`none-with-head`、`semantic-base-without-head`、`semantic-base-nonancestor`、`unsupported-merge-base`、cross-mode options。
  - 操作: `review planning` identity constructionとpreflightを実行する。
  - 期待結果: positiveはexact `ReviewedPlanningIdentityV1`へbindする。negativeはbackend前に`rejected`でarchive fallbackなし。
  - 失敗検出: Issue inference、base omission、mode混同、silent fallbackを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REVIEW`, `CLOS-REQ-006`

- `tc-s05-006` contract: Candidate control-file schemasをfield-by-fieldにfail closedで検証する
  - 前提: valid Candidateをbaselineとし、次のnamed parameter generatorを各controlへ適用する。
    - `ctl-<file>-missing-<required-key>`: 各required keyを一件ずつ除去。
    - `ctl-<file>-unknown-key`。
    - `ctl-<file>-duplicate-<key>`: 各representative object level。
    - `ctl-<file>-wrong-version`。
    - `ctl-<file>-bom`、`ctl-<file>-crlf`、`ctl-<file>-trailing-space`、`ctl-<file>-extra-line`。
    - SOURCE: wrong Issue／parent／repository／branch／HEAD、unsorted／duplicate dependencies、unsorted／unsafe／untracked relevant path。
    - MANIFEST: wrong Candidate ID／version／timestamp／filename／root、wrong source digest、wrong placeholder digest、missing／extra／duplicate／unsorted entry、wrong role、wrong coverage、nonstatic content mode。
    - PLACEHOLDER: nonempty files、unknown token field。
    - CHECKSUMS: missing／extra／duplicate line、self-entry、wrong digest、uppercase digest、wrong order、one-space／tab separator、root-prefixed path、CRLF。
    - archive: supplied external ZIP SHA mismatch。
  - 操作: each named parameterをpackaging validationまたはReview validationへ渡す。
  - 期待結果: 全negativeが`rejected`、exit 1。final ZIP、extraction tree、Review result、adoption output、owned temp leakは0。parameter IDはtest reportへ保持する。
  - 失敗検出: permissive control parsing、unknown-key tolerance、serialization divergence、self-referential checksum、cross-file substitutionを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-ARCHIVE`, `CLOS-REQ-004`, `CLOS-ARC-19`
```

## Plan replacement P-15 — replace S05 `step closure contract`

```markdown
#### step closure contract

`CLOS-CREATE`、`CLOS-REVIEW`、`CLOS-ARCHIVE`、`CLOS-REQ-004`、`CLOS-REQ-006`、`CLOS-REQ-008`、`CLOS-REQ-022`、`CLOS-EC-002`〜`CLOS-EC-004`、`CLOS-ARC-01`〜`CLOS-ARC-25`、`CLOS-RISK-002`、`CLOS-RISK-004`のS05 owner portion、およびClosure IndexでS05をownerに持つ全`required=yes` owner portionは、direct create→Review Green、control-schema positive、field-by-field control negative全件、git base identity matrix、generic default regression、archive matrix 25/25、reject cleanup evidence、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけ`passed`にする。

S03/S05またはS05/S08等のmulti-owner aggregateは、他owner portionがpassedになるまでopenのままとする。
```

## Plan replacement P-16 — replace the S06 `planned contract`

```markdown
#### planned contract

- scope: 上記exact target filesだけ。
- evidence schema obligation: Design §§4.3–4.4のclosed Review／Human schemasを実装する。Human v1 decisionはapproved／rejectedだけで、revokedを拒否する。
- parser obligation: Design §3のexact archive／git apply args、Issue、derived repository／branch、git base rules、mutual exclusionsを実装する。
- no-new-subsystem obligation: external schema registry、authority／revocation registry、database、custom Git ref、general approval frameworkを追加しない。
- status obligation:
  - missing Review/Human source=`blocked`。
  - malformed／partial／cross-binding／unsafe destination／unsupported revoked=`rejected`。
  - current source drift=`stale`。
  - Review fail + Human approved=`blocked`。
  - valid Human rejectedはdecision-record transaction。
- adoption obligation: approved + Review passだけがdecision artifact＋canonical三文書をtransactionalに処理する。
- rejection obligation: rejected decisionはdecision artifactだけをtransactionalに処理し、verified publication後も`blocked`。publicationでHEADを変更し、old H0-bound evidenceをstaleにする。
- revocation boundary: post-publication withdrawalはshared Human／Main stop-or-revert ownerへrouteし、planning runtime内でsupersession lookupを実装しない。
- transaction obligation: adoptionとrejection-recordの双方でpre-commit rollback、restore verification、post-commit no-resetを維持する。
- recovery lookup obligation:
  - operation directoryは`<canonical-output>/.spec-dock-planning-operations/<operation-id>/`。
  - manifestとcommit workspace trailerへoutput-directory identityをbindする。
  - pre-commit same-operation retryはsame exact output directoryを必須とする。
  - missing／different outputでpartial stateを検出した場合は`recovery_required`、new mutation 0、directory scan 0。
- shared reuse obligation: runbook stage／backup／restoreをshared scoped transactionへ抽出し、existing runbook characterizationを維持する。
- test obligation:
  - Review schema matrix。
  - Human approved／rejected truth table。
  - revoked unsupported。
  - exact Review SHA／identity binding。
  - exact public CLI mode matrix。
  - archive／git approved positives。
  - durable rejected decision-record。
  - PA-NF exact status 10/10。
  - replacement／validation／commit fault。
  - rollback failure。
  - same-output crash recovery。
  - wrong-output recovery failure。
  - push retry／remote divergence。
  - runbook regression／state boundary。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_scoped_file_transaction.py tests/unit/infra/test_runbook_store.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Designで承認済みのclosed evidence validation、approved adoption、rejected decision-record、deterministic recovery workspace、shared transaction以外のpublic contract／shared policyを追加しない。
- amendment trigger: revocation implementation、merge-base support、new state registry、target追加、parent boundary変更、existing behavior破壊が必要なら停止しplan amendment／fresh reviewへ戻る。
```

## Plan replacement P-17 — replace `tc-s06-001`, `tc-s06-002`, and `tc-s06-003`

```markdown
- `tc-s06-001` acceptance: exact archive applyでapproved full conjunctionだけがreadyになる
  - 前提: valid archive Candidate v1 controls、Review pass、Human approved、safe new decision destination、clean local=remote=expected H0を用意する。
  - 操作: Design §3 archive apply exact argvでpublic CLIを実行する。
  - 期待結果: decision artifactと三文書だけをPlanning adoption commitに含め、remote/tree parity後にtext／JSONとも`status=ready`、exit 0。operation／workspace trailersとevidence locatorsを返す。
  - 失敗検出: hidden args、Review-only／Human-only start、control substitutionを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-002` acceptance: exact git-bound applyでtarget blobとbase identityを維持する
  - 前提:
    - positive `base=none`。
    - positive `base=semantic-base` with exact ancestor。
    - Review pass、Human approved、approval-only diff。
  - 操作: Design §3 git-bound apply exact argvでpublicationを実行する。
  - 期待結果: reviewed target blobsとbase identityが不変でlocal／remote publication parityが成立し`ready`。
  - 失敗検出: Review後semantic mutation、base omission、CLI identity driftを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-003` negative: PA-NF setを一つのexact statusで評価する
  - 前提: 次のnamed parametersを用意する。
  - 期待status:
    - `pa-nf-01-review-only-archive` → `blocked`
    - `pa-nf-02-review-only-git` → `blocked`
    - `pa-nf-03-human-only` → `blocked`
    - `pa-nf-04-parity-only` → `blocked`
    - `pa-nf-05-wrong-archive-identity` → `rejected`
    - `pa-nf-06-wrong-git-identity` → `rejected`
    - `pa-nf-07-source-drift` → `stale`
    - `pa-nf-08-semantic-mutation-during-adoption` → `rolled_back`
    - `pa-nf-09-parity-failure-before-commit` → `rolled_back`
    - `pa-nf-10-validation-failure` → `rolled_back`
    - `pa-nf-10-publication-failure` → `publication_pending`
  - 操作: each named parameterを`planning apply`／readiness evaluatorへ渡す。
  - 期待結果: each parameterが上記exact status、exit 1、no readinessを返す。pre-mutation parametersはmutation 0。rollback parametersはbaseline exact restore。publication failureはlocal committed H1だけを保持する。
  - 失敗検出: status union、generic reject、複合gate短絡を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-PA-NF-01`〜`CLOS-PA-NF-10`
```

## Plan replacement P-18 — replace `tc-s06-010` and add `tc-s06-011`／`tc-s06-012`

```markdown
- `tc-s06-010` contract: Human decision truth table、exact Review SHA、mode-neutral gateを検証する
  - 前提: valid archive／git Review resultsとnamed fixtures:
    - `approved-archive`
    - `approved-git-none`
    - `approved-git-semantic-base`
    - `rejected-review-pass`
    - `rejected-review-fail`
    - `partial-plan-only`
    - `partial-start-only`
    - `wrong-review-sha`
    - `wrong-mode`
    - `wrong-issue`
    - `wrong-archive-identity`
    - `wrong-git-identity`
    - `stale-source`
    - `review-fail-human-approved`
    - `review-only-archive`
    - `review-only-git`
    - `human-only`
    - `revoked-unsupported`
  - 操作: preflight／authority evaluationを各parameterで実行する。
  - 期待結果:
    - approved three positivesだけがfull adoptionへ進む。
    - rejected two positivesだけがdecision-recordへ進む。
    - partial、wrong SHA／mode／Issue／identity、revoked unsupportedは`rejected`。
    - source driftは`stale`。
    - Review fail + Human approved、Review-only、Human-onlyは`blocked`。
    - pre-mutation negativeでrepository／index／HEAD／manifest mutation 0。
  - 失敗検出: Candidate-only gate、git exclusion、partial approval、Review substitution、false revocationを防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`, `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`, `CLOS-REQ-009`, `CLOS-REQ-015`, `CLOS-EC-005`

- `tc-s06-011` acceptance／recovery: rejected decisionをdurable decision-only transactionとしてpublishする
  - 前提: valid Review passまたはfail、same-identity Human rejected、safe new decision destination、clean H0を用意する。
  - 操作:
    1. rejected decisionで`planning apply`を実行する。
    2. decision artifact add後、commit前validation、commit、pushに各faultを注入する。
    3. published rejection H1へold H0-bound approved decisionを再投入する。
  - 期待結果:
    - normal pathはdecision artifact一件だけをcommit／pushし、remote parity後`blocked`、exit 1。
    - canonical三文書bytes、`.assurance.json`は不変。
    - pre-commit faultは`rolled_back`または`recovery_required`。
    - post-commit push faultは`publication_pending`。
    - H1でold H0 Review／approvalは`stale`となりfull adoptionへ進まない。
  - 失敗検出: nondurable rejection、rejectionによるcanonical rewrite、old approval reuseを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-REQ-015`, `CLOS-EC-005`

- `tc-s06-012` recovery: deterministic operation workspaceへmanifest lookupをbindする
  - 前提:
    - canonical output A。
    - different output B。
    - same operation ID。
    - adoption／rejection-record双方についてstage後またはfirst replacement後のcrash state。
  - 操作:
    1. output Aでcrashさせる。
    2. same args + output Aでretryする。
    3. fresh crash stateを作り、same args + output Bまたはmissing Aでretryする。
    4. post-commit `publication_pending` stateでoperation／workspace trailersを照合する。
  - 期待結果:
    - output A retryはexact deterministic operation directory／manifestを読み、rollbackまたはresumeする。
    - output B／missing Aは`recovery_required`、exit 1、new operation directory作成 0、directory scan 0、new mutation 0。
    - post-commit retryはboth trailers、tree、parent、output identity一致時だけ再開する。
  - 失敗検出: lost manifest、wrong-workspace resume、global directory search、backup取り違えを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`, `tests/unit/infra/test_scoped_file_transaction.py`, `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-EC-006`, `CLOS-EC-008`, `CLOS-RISK-001`, `CLOS-RISK-005`
```

## Plan replacement P-19 — replace S06 `step closure contract`

```markdown
#### step closure contract

`CLOS-ADOPTION`、`CLOS-READINESS`、`CLOS-REQ-009`〜`CLOS-REQ-016`のS06 owner portion、`CLOS-EC-005`〜`CLOS-EC-009`、`CLOS-PA-NF-01`〜`CLOS-PA-NF-10`、`CLOS-RISK-001`、`CLOS-RISK-004`、`CLOS-RISK-005`のS06 owner portion、およびClosure IndexでS06をownerに持つ全`required=yes` owner portionは、次がすべて揃った場合だけ`passed`にする。

- exact archive／git apply parser positives。
- omitted／cross-mode／base negative matrix。
- Review schema matrix全件。
- Human approved／rejected truth table全件。
- revoked unsupported。
- exact Review SHA／Issue／identity cross-binding。
- exact EC-005 status matrix。
- archive／git approved positive。
- durable rejected decision-record positive。
- old-approval stale assertion。
- PA-NF exact status 10/10。
-全pre-commit fault rollback。
- rollback-failure stop。
- deterministic same-output recovery。
- wrong-output `recovery_required`。
- push resume。
- remote-divergence stop。
- runbook regression。
- required reviewer pass。
- commit候補または正当なapproved-no-op。
- post-commit clean check。

S06 portionがpassedしても、S08をownerに含むmulti-owner aggregateはS08 portionがpassedになるまでopenのままとする。
```

## Plan replacement P-20 — replace S06 `step gate`

````markdown
#### step gate

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_scoped_file_transaction.py \
  tests/unit/infra/test_runbook_store.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/integration/test_chatgpt_planning_fake_oracle.py \
  -q
```

scope外diff 0、exact parser matrix、Review schema matrix、Human approved／rejected truth table、revoked unsupported、archive／git approved positives、durable rejection、PA-NF exact status全件、fault matrix、same／wrong-output recovery、existing runbook unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。
````

# 5. Traceability and acceptance-test impact

The attached Red review assigns the requested changes to EC-005, Design §§3–5, S03, S05, S06, the Closure Index, and recovery lookup. It also states that P1-10, P2-01, and P2-02 remain closed and that the transaction, archive matrix, source binding, and authority separation controls remain structurally preserved.

| Finding                                  | Owner-document closure                                                      | Primary acceptance tests                                                           |
| ---------------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| P1-12 — EC-005 status conflict           | Requirement R-02/R-03; Design D-06; Plan P-04/P-05/P-17/P-18                | `tc-s06-003`, `tc-s06-010`, `tc-s06-011`                                           |
| P1-13 — incomplete public identity argv  | Design D-01/D-03/D-10; Plan P-07/P-08/P-14/P-17                             | `tc-s01-001`, `tc-s01-004`, `tc-s05-005`, `tc-s06-001`, `tc-s06-002`, `tc-s06-010` |
| P1-14 — rejection/revocation incoherence | Requirement R-01/R-02; Design D-05–D-09/D-13/D-14; Plan P-03/P-04/P-16/P-18 | `tc-s06-010`, `tc-s06-011`                                                         |
| P1-15 — open Candidate control schemas   | Design D-02/D-11/D-12; Plan P-02/P-03/P-06/P-13–P-15                        | `tc-s05-003`, `tc-s05-006`, existing `tc-s05-004[arc-19]`                          |
| P1-16 — secret may reach backend         | Plan P-03/P-10–P-12                                                         | `tc-s03-003`, `tc-s03-004`, S08 integrated security fixture                        |
| P2-03 — multi-owner closure ambiguity    | Plan P-01/P-09/P-12/P-15/P-19                                               | report owner-portion rows; S99 aggregate-closure assertion                         |
| P2-04 — recovery lookup ambiguity        | Design D-07/D-09; Plan P-16/P-18/P-20                                       | `tc-s06-012`                                                                       |

No product implementation tests were run in this thread. These are replacement-ready planned contracts, not observed Green evidence.

After Main integrates the blocks, the canonical document hashes will change. `.assurance.json` must then be rebound to the resulting Requirement／Design／Plan bytes, `report.md` must record the attached Red finding adoption and the correction snapshot, and the next fresh review must use the actual resulting 40-character remote HEAD. The current Assurance remains `provisional` and is bound to the pre-correction document hashes.  The current Report remains an observational ledger with S01 blocked and implementation evidence absent.

# 6. Non-regression self-check

| Previously closed control                                 | Effect of these blocks                                                                 |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Explicit public `planning apply`                          | Preserved as the sole supported late-lifecycle route; its mode surfaces are made exact |
| Review/Human authority separation                         | Preserved; Review never generates Human authority                                      |
| Dual Plan-adoption and implementation-start authorization | Preserved for `approved`; partial approval remains rejected                            |
| Archive and git-bound modes                               | Preserved; git Issue/base identity is now closed without archive fallback              |
| Exact Review-result byte binding                          | Preserved                                                                              |
| Source repository／branch／HEAD binding                     | Preserved and strengthened with explicit Issue and git base                            |
| Crash-safe pre-commit rollback                            | Preserved for both adoption and rejection-record operations                            |
| Post-commit `publication_pending` retry                   | Preserved                                                                              |
| Remote divergence stop; no force/reset/amend              | Preserved                                                                              |
| Shared runbook transaction primitive                      | Preserved                                                                              |
| Twenty-five archive safety classes                        | Unchanged                                                                              |
| Inclusive archive ceilings                                | Unchanged                                                                              |
| Existing generic authoring-pack behavior                  | Explicitly protected as covered-existing                                               |
| Closure Index schema completeness                         | Preserved; multi-owner aggregate semantics are added without removing any required row |
| S02A/S02B ownership split                                 | Unchanged                                                                              |
| S09A/S09B Human/worker boundary                           | Unchanged                                                                              |
| Provider-first ownership                                  | Unchanged                                                                              |
| `.assurance.json` product-flow immutability               | Preserved                                                                              |
| Report as observational ledger                            | Preserved                                                                              |
| One Issue／one branch／one Delivery PR                      | Unchanged                                                                              |
| Human-only merge                                          | Unchanged                                                                              |
| P1-10 archive/git start gate                              | Preserved                                                                              |
| P2-01 positive S01 target oracle                          | Preserved                                                                              |
| P2-02 S03 allowlist ownership                             | Preserved; the split security tests remain within S03-allowed planning tests           |
| P1-11 product behavior                                    | No change; only the next review invocation’s exact SHA is corrected                    |
