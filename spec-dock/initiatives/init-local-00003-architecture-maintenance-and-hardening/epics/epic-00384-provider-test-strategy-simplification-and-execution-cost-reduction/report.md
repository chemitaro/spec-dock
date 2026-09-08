---
種別: レポート（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
状態: "parent-planning"
最終更新: "2026-09-08"
依存: ["requirement.md", "design.md", "plan.md"]
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

1. 両DECと対象worktree修正を含む候補を同じreviewerで再確認し、P0/P1=0・review passを得る。
2. 文書・HTML検証後、reviewed bytesをcommit/pushし、同一SHA・clean状態・外部freeze receiptと四つのGitHub projection/readbackを確認する。
3. 親G0、依存、B0を確認して同じworktreeで#392を正式startする。
4. #392のR/D/PとLuna Max handoffを詳細化し、そのIssueの独立review合格後だけ実装へ進む。#395はB1、#396はB2待ち。

[現行HTML](artifacts/epic-00384-current-plan-guide.html)は再評価の修正点、採用済み判断、正式startと実装許可の区別を説明する。旧10分割／単一Issue資料はhistorical evidenceであり、実装権限ではない。
