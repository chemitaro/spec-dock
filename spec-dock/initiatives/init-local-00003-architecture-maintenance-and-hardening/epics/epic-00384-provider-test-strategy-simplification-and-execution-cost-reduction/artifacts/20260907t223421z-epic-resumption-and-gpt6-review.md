---
種別: artifact
ID: "20260907t223421z"
タイトル: "Epic 384 再開時の現在地と GPT-6 Max 仕様レビュー記録"
状態: "evidence"
作成者: "Codex"
最終更新: "2026-09-08"
親: ["epic-00384"]
template: "blank"
authority: "evidence"
derived_from: ["requirement.md", "design.md", "plan.md"]
reflected_to: ["requirement.md", "design.md", "plan.md"]
---

# Epic #384 再開時の現在地と独立レビュー記録

## 1. 今回のスコープ

ユーザーは、このworktreeをEpic具体化専用とした。各Issueの詳細R/D/P作成と実装は、後日新しく作るIssue branch/worktreeで行う。外部ChatGPT Useが機能しない状況で、主担当GPT-6がauthoring・判断を行い、独立したGPT-6・推論Maxのサブエージェントをreviewerとする指示を受けた。

Reviewerは `/root/epic_384_gpt6_review`、model `gpt-6-astra`、reasoning effort `max`。初回はfresh contextで読み、修正後は同じreviewerを再利用する。Luna Max reviewer、外部Oracle/ChatGPT呼出し、Product implementation、Issue start、新しいIssue branch/worktree作成は行わない。

## 2. 合格地点と古い記録の区別

| 過去の候補 | 意味 |
|---|---|
| `240e561e94b50250a4a6309452a7fd0fb511458a` | 元のpack authoring-source。freezeではない。 |
| `ce7e46cf2603e6fc52b4d4339faa7d3f7f3bac83` | 3 Issue packを導入した、最初のreview fail候補。 |
| `177937163526c369108c97ef7c024adb3dd05f77` | qualification修正後のreview 740 fail候補。 |
| `1429c2f899c6d2086d5bd03c0dcea01f5b168435` | 2026-09-02にreview 747でpassとなった親候補。 |

`.workbench/parent-freeze-receipt.md` と `.workbench/review-analysis/review-747-source.json` に過去pass、findings `[]` が記録されている。GitHub body projectionは `.workbench/github-issue-projection-receipt.md` に記録されている。当時のreadbackは文字数と先頭・末尾行の一致を確認したもので、全byte hash比較を実施したとは主張しない。

本更新前の親R/D/P/Reportにはreview 740後の「未実施」がcurrentとして残っていたため、過去のfail、過去のpass、今後の候補確認を分離した。過去passは変更後の候補へ持ち越さない。

## 3. 初回GPT-6 Maxレビュー

対象は編集開始時のHEAD `1429c2f899c6d2086d5bd03c0dcea01f5b168435`。結果は `changes_required`、P0=0、P1=3、P2=2。外部Strictの判定ではない。

| ID | 優先度 | 指摘と採否 | 反映先 |
|---|---|---|---|
| R1 | P1 | 20回のwindow合否を各attemptへ戻すと初回受入が循環する。採用し、全roleを含むper-attempt acceptanceとrolling qualificationを分離する。数・window・失敗保持は変えない。 | Requirement `E384-QUAL-001` |
| R2 | P1 | incomplete record公開直後、全6 target presentの正当なuninstall状態をaction profileが拒否する。採用し、0〜6 target absentを許容する。状態はrecord/owner identityから判定する。 | Wire `WIR-ACT-005` |
| R3 | P1 | ACTIVE unlink後のcrashでtokenized retryが拒絶され、保存済みcontinuationを返せない。採用し、完了応答直前のcrash後も再提示できる親契約を閉じる。 | Wire `WIR-CLEANUP-001`、修正ADR |
| R4 | P2 | U5/U6/U7にstage cleanup actionがなく、U9/I1のguidanceが規範表と違う。採用し、action、summary、guidanceを同期する。 | Wire JSON goldens |
| R5 | P2 | 旧HTMLが10分割／単一Issueを現在形で説明する。採用し、過去版表示と現行3 Issueガイドを用意する。本文は歴史として保持する。 | 新旧HTML |

Reviewerは、3 Issueの責務・依存順・各merge後のGREEN・最終main統合方針は整合していると判断した。Issue追加分割や、この環境での子Issue詳細化は要求していない。

### 同一reviewerによる再レビュー

最初の修正候補はmanifest digest `ad0b90e04d4212100786a525bad2f60acb4a7bc7ff570925eccb4a2174165462`、全46ファイルを固定してreviewした。R1/R2/R4/R5は解消、R3にP1一件が残った。Receiptへ最初のrequestを保存した後にACTIVE mirror更新が失敗すると、古いACTIVE参照からcontinuationが欠けるという指摘である。

この残件を採用し、検証済みmatching receiptを優先するclosed `continuation_owner` にfailure/success profileとselectorを統一した。不正・不一致receiptのACTIVE fallbackは禁止した。同じreviewerでこの差分を再確認し、最終結果は下記receiptへ記録する。

## 4. 検証の範囲

- SpecDock構造確認: `./spec-dock/scripts/spec-dock validate`、nodes=236。
- Git差分形式: `git diff --check`。
- WireのJSON blocks: 37件（record 4、public 33）をparse。publicのsummary/action集計とfailed/pending pathsを照合。これは製品runtime testではない。
- Qualificationの抽象真理値確認: 初期19件は未達、正常20件は成立、window内失敗／retry／証拠欠落は拒否、古い失敗はchronological境界からだけ外れる。
- Uninstall profile: 6 targetの存在・不在64組合せを確認。全presentと全absentの双方を含む。
- 新HTMLは1図、旧HTML2本は各4図。公式validatorでheadless browserのSVG描画、クリック／キーボード拡大、倍率境界、focus trap、閉じる操作とfocus復帰を確認。
- この作業でProductの全回帰テスト、実装完了、main merge、branch protectionの変更を確認したとは主張しない。

## 5. Review receiptと開始許可

最終reviewはこの記録を含む候補全体に対して行う。具体的なfile identity、review結果、Git HEAD/upstream/remote確認はtracked tree外の `.workbench/reviews/20260908-gpt6-max-review.md` に記録する。本記録はfuture commit SHAや未実施のpassを予測しない。Git commit/pushが未実施なら、この候補を別worktreeの確定済み開始点として扱わない。

Epic候補のacceptance後に可能になるのは、別worktreeでの#392詳細化である。#392/#395/#396はいずれも現在のdraftから直ちに実装可能な状態ではない。後続Issueの詳細化はB1/B2受け入れ後に行う。
