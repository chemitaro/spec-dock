---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
状態: "parent-planning"
最終更新: "2026-09-14"
依存: ["requirement.md", "design.md", "plan.md", "artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md", "artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md", "artifacts/20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md"]
親: ["init-local-00003"]
---

# Result Summary

## Outcome

2026-09-08のEpic全体再評価により、三Issue（#392 → #395 → #396）をEpic integration branchへ順次統合し、最後にmainへ一度mergeする構成は維持する。以前の計画をそのまま「問題なし」とせず、独立GPT-6 Max reviewerの指摘をsourceと実測へ照合し、親契約を修正した。

現在の方針は[全体再評価ADR](artifacts/20260907t234210z-adr-whole-plan-reassessment-and-executable-gates.md)に記録した。

1. #395の14件を一律のProduct bugとして扱う計画を改め、12件のtest harness/observerと2件のProduct責務境界へ原因別に修復を割り当てた。
2. 置換されるsystem root内のruntime lockだけでは更新と通常commandを排他できないため、repository-root inodeの共有coordination、pre-import admission、managed helperの寿命とwrapperのrelease→execを#392へ追加した。
3. 通常gateの単回attemptと最終qualificationを分け、五回測定と二十件履歴が同じ観測を参照できるようにした。失敗・欠測の除外やcampaign取り直しは認めない。
4. Hardware escalationを判定できる参照環境の能力境界を親へ定義した。
5. 管理下checkoutの同世代限定、実際の作成・削除先worktreeのEX、entrypoint-lastの公開障壁、パス再利用時の保存とconsumer hookへの終端handoffを親wireへ具体化した。

初回0.2.3移行だけの停止運用 `E384-DEC-001` は「推奨案を採用します」により、既存branchへの同世代checkout `E384-DEC-002` は続く「オッケーです。それではコミットプッシュした上で最初のイシューをスタートしてください」により採用済みである。`owner_decisions_required=[]`。旧start保留はこの明示依頼で解除したが、親G0・公開工程とIssue詳細化reviewは省略しない。

## Current scope

- Epic integration branch: `codex/epic-00384-provider-test-strategy-planning`。
- この文書候補を作成した時点ではActiveはEpic `epic-00384`、Issueなし。次の承認済み操作は親計画のcommit/push・projection後の#392正式startである。実際の到達状態は外部receiptとSpecDock active/Gitから確認する。
- 変更対象はEpicのR/D/P、原因別register、横断契約、三Issueのdraft、再評価ADR、人間向けHTML。
- Product source、tests、CI、root ledger/timingの実装変更はない。
- #392はユーザー指定の同じworktreeで専用Issue branchを使う。Epic集約branchは維持する。
- Formal startはbranch/active選択であり、詳細化と独立reviewを経たProduct実装許可とは別である。

## Verification evidence

再評価の開始点はHEAD `6b20f6bab378cb5b538894e1a7993dde08e4b05b`、tree `c1a518952c5e5016513b3ed2c726c8dfca9fafb7`。Local/upstream一致とclean状態を確認してから文書を変更した。これはsource observationであり、修正候補のfreeze receiptではない。

14 active nodeのfocused diagnosticは **14 failed / 14.43s / exit 1**。最初の失敗境界を原因別registerに反映した。元node/signature/historyは保存し、normal passを偽装していない。これはfull suiteやLinux性能qualificationの合格ではない。

Raw evidenceはEpic配下のGit管理外 `.workbench/reviews/20260908-baseline-diagnostic.txt` と同名JUnit XMLにある。初回の文書検証・候補hash・同一reviewer再確認は `.workbench/reviews/20260908-whole-plan-reassessment.md`、その後のwire再レビューは `.workbench/reviews/20260908-runtime-coordination-review.md` に保存した。後者の `wire_only_review=fail` / `whole_plan_review=blocked` は修正前の候補に対する履歴であり、上書きしない。

今回の最終候補は新規の `.workbench/reviews/20260908-parent-ready-candidate.sha256` で固定し、結果を `.workbench/reviews/20260908-parent-ready-review.md` に記録する。実行前にこのReportを根拠にpassを推測しない。公開済みtipの証拠は `.workbench/parent-freeze-20260908.md`、GitHub readbackは `.workbench/github-issue-projection-20260908.json` に分離し、tracked文書へ自分自身のcommit SHAを書き込む循環を作らない。

## Review history and acceptance boundary

9月2日の外部review pass `1429c2f899c6d2086d5bd03c0dcea01f5b168435` と、その後の限定的GPT-6 reviewは、それぞれ記録済みの候補だけに有効である。[前回再開記録](artifacts/20260907t223421z-epic-resumption-and-gpt6-review.md)は履歴として残す。

今回のwhole-plan reviewはfreshなGPT-6 Max `epic_384_strategic_reassessment` が担当し、修正後も同じreviewerを使う。外部ChatGPT/Oracleを実行したとは主張しない。採用された方針決定、独立review、公開済みtipのG0受入、formal start、実装検証を別々の証拠として扱う。

## Next authorized sequence

1. accepted ADR、Epic/Issue R/D/P、Handoff、Test Ownership Artifactを一つの候補として独立Strict reviewし、P0/P1=0・`review_status=pass`を得る。
2. reviewed bytesをcommit/pushしてexact SHAを固定し、#384/#392/#395/#396のGitHub projection/readbackをそのfreezeへ収束させる。
3. 親G0、依存、B0、#387、15/14/1、243 timing、required-fast fourを再確認する。#392のformal startは完了済みなので再実行しない。
4. G0後はIssue #392 Plan §2.1から既存candidateの限定re-entryを行い、CP1を作り直さずCP2から進める。#392 mergeはP392、#395はそのexact tipから開始し、B1/B2は#395 merge後の同一tipで評価する。

[2026-09-08 HTML guide](artifacts/epic-00384-current-plan-guide.html)は当時の再評価、正式start、実装許可の区別を説明するhistoryです。Option 1後の再開条件と現行Strict review routeは本文のEpic R/D/PおよびRolling-Wave Contract §5を正本とし、このguideはそれらを上書きしません。旧10分割／単一Issue資料もhistorical evidenceであり、実装権限ではありません。

## 2026-09-12 later decision — Issue #392 safe stop (superseded)

[Same-EUID safe-stop ADR](artifacts/20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md)は当時の脅威モデルに基づく履歴として保持し、現在の再開判断は後続のE384-DEC-004に置き換わりました。

## 2026-09-12 later decision — Issue #392 scope reopening

ユーザーはOption 1を採用し、同一EUIDの非協調actorを保証対象外としました。[Superseding ADR](artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md)とE384-DEC-004がcurrent authorityです。SpecDock協調lease、通常I/O failure、process interruption、Wire-defined recovery、protected-data preservation、baseline、required-fast、CI、human merge gateは変更しません。

改訂親/Wire/Issue R/D/Pの独立review、clean pushed freeze、Issue projection/readbackが終わるまでProduct実装許可はfalseです。B1および#395/#396は未達のままです。Issue Report §28–29のfailure/safe-stop記述は当時の証拠として保持し、新しいtest dispositionは後続実装結果で追記します。

ユーザーは2026-09-12にChatGPT Use系Strict skill/scriptの利用再開を指示しました。過去の一時的なGPT-6 subagent review routeは現在の運用authorityではなく、独立review routeは更新済み[Rolling-Wave Contract §5](artifacts/rolling-wave-issue-elaboration-contract.md)に従います。執筆/Blue Team分析とRed Team reviewは別sessionとし、exact clean pushed SHAをそれぞれStrictに確認します。

## 2026-09-14 P392 sequence and dependency update

ユーザー承認済み[P392 sequence ADR](artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md)をEpic acceptanceへ反映しました。#392 human merge後はP392として記録し、#395はそのexact merged tipから作業します。B1/B2は#395 merge後の同一tipで評価し、#392はB1、#395と#396はB2成立後の所定gateを満たすまでclosure/開始しません。P392のfull-verifier例外は、そのexact runの全violationが#395-owned active rowsに対応する場合だけ許可します。

SpecDock CLIでiss-00395からiss-00392へのclose-based metadata dependencyを削除し、iss-00396からiss-00395へのdependencyは維持しました。したがってdeps check上の#395 ready=trueはP392証拠でもstart許可でもなく、#395の実行には人間がmergeしたP392 exact SHAと現在のfull-verifier row対応確認が別途必須です。#396は#395 dependencyにより引き続きblockedです。SpecDock validateはpassしました。

#392 test migrationは現行public behavior・保護データ・baseline/policy検証を残し、obsolete-only/absence-onlyおよび分類専用testを恒久suiteから削るよう仕様化しました。Product source/testにはまだ変更を加えていません。改訂R/D/Pのindependent Strict review、clean pushed freeze、GitHub projection/readbackが済むまでProduct実装は再開しません。

## 2026-09-14 Blue Strict analysis follow-up

`chatgpt-use-strict` session `issue-392-p392-blue`（GPT-5.6 Sol、Extra High）は、verified branch SHA `13ed9de5fd6180b635f5c32d3a7ec3e6b53e7401`に対してBLOCKを返しました。これはP0/P1 classificationではなくG0未充足の判定です。live GitHub readbackで#384/#392/#395 bodiesに旧freeze/B1依存表現が残り、#396の#395 dependencyは現行契約どおり維持されていることを確認しました。現行sourceには`test_s40b_provider_scaffold_excludes_removed_docs_and_templates`というabsence-only testがあり、Test Ownership ArtifactのRule 5には未記載でした。また、同Artifactの`test_s40b_legacy_bootstrap_and_skill_apply_paths_are_retired` KEEP entryはcurrent sourceに存在しないstale classificationです。

macOSでrequired-fastを既定`/var/folders`から実行すると、no-follow root bindingが`/var` symlinkを拒否して2件が失敗しました。同じ実体directoryを`/private/var/...`で指定すると通り、`TMPDIR=/private/tmp`でrequired-fast fourは`4 passed`でした。no-follow実装は変更せず、後続のローカルmacOS検証ではこの明示的temporary-rootを使います。

この追補時点ではtest-disposition文書修正、independent Strict review、freeze後のGitHub projection/readbackは未完了です。従ってG0とProduct実装許可は未達のままです。
