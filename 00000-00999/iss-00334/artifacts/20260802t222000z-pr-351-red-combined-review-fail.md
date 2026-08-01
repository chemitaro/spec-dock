# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6e5cfa-ae90-83e8-b028-7e17cf52e3ca

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

Use the attached Red Team brief as the task contract. Review the exact GitHub branch and HEAD, then return the formal read-only verdict.

## Answer

REVIEW_IDENTITY
repository: chemitaro/spec-dock
branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: d3c72b6b58f301b5609566d7cdb9e94f4d08aa2c
pr: [https://github.com/chemitaro/spec-dock/pull/351](https://github.com/chemitaro/spec-dock/pull/351)
repository_access: PASS
head_match: PASS

SCOPE
in_scope: concrete P0/P1 defects only
out_of_scope: redesign, proposals, P2/P3, speculative issues

SPEC_FINDINGS

* none

CODE_FINDINGS

* [P1] id: REVIEW-CLEANUP-OWNERSHIP-TOCTOU
  evidence: `infra/issue_planning_review.py` の `_remove_evidence_directory_at()` は、最初に公開ディレクトリと二つの子ファイルのdevice／inodeを確認するが、その後はcaptured directoryをquarantineへ隔離せず、子をdescriptor-relativeにunlinkした後、親descriptor上の`evidence.name`を再度identity確認せず`os.rmdir()`している。したがって、子検証後から`rmdir`までの間にcaptured directoryを別名へrenameし、元の`evidence.name`へ空のreplacement directoryを置くと、`rmdir`は未知replacementを削除して成功し、helperは所有物のcleanup成功を誤って返す。captured Review directoryは別名で残存し得る。 Blue Team packetは、captured directoryをidentity-checked quarantineへ移し、そのidentityを再確認して、captured child identitiesとcaptured directoryだけを削除し、相違時は未知objectを保持してpublication failureにすることを明示している。現実装はこの必須cleanup手順を実装していない。 追加テストはrename前のstaging-name置換、最初の検証後のchild置換、競合のない`publication_guard=False` cleanupを扱うが、identity検証後から最終`rmdir`までのnamespace置換を注入していない。
  impact: repository外のcaller-owned output directoryで、今回のReview publicationに属さないreplacement entryを削除できる。また、owned Review directoryを残したままcleanup成功と判定し、applicationが`stale/review_target_changed`を返し得る。これは既知のreview-stage publication／cleanup TOCTOUを完全には閉じておらず、外部証跡の破壊と誤ったcleanup確定を生む。
  required_fix: captured Review directoryを、親descriptor上でidentityを確認したままprivate quarantine nameへatomicに移す。移動後のdirectory device／inodeと二つのchild device／inodeを再検証し、captured childだけを削除してからquarantine上のcaptured directoryだけを削除する。rename、child identity、final directory identityのいずれかが不一致なら未知entryを一切削除せず、`ReviewSourceStale`ではなくcontent-freeな既存publication failureを返す。identity検証完了後・最終削除直前に元nameをreplacementへ差し替えるdeterministic regression testを追加し、replacement保持、owned directory cleanup未確定、`review_completed`／structured stale不成立を確認する。

QA_FINDINGS

* none

VERDICT
P0: 0
P1: 1
overall: FAIL
reason: repository、required branch、PR #351、およびPR headのexact SHAは一致した。 apply-origin resolverの`RuntimeError`／未解決値はcontent-freeな`blocked/github_upstream_required`へ正規化され、解決済み別repositoryは従来のstale経路を維持している。 shared JSON parserも`RecursionError`を`ValueError("invalid JSON")`へ正規化している。 Create、Review、Semantic／Mechanical Reviseにはpublication-completion source／Candidate guardとcommand-specific stale mappingが接続されている。   しかし、Review stale／failure cleanupに未知replacementを削除できる具体的なpathname raceが残るため、既知P1のclosure条件を満たさない。

NON_BLOCKING_NOTES

* provider authorityとdogfood projectionの対象5モジュールは、それぞれ同一blob SHAである。
* current repair commitに対するGitHubのCIおよびProvider CIは成功しているが、上記cleanup-time raceを注入するtestは含まれていないため、P1を相殺しない。
