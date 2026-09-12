---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-12"
依存:
  - "requirement.md"
  - "design.md"
  - "artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md"
  - "artifacts/20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md"
  - "artifacts/20260902t070000z-adr-multi-issue-epic-integration-branch-and-rolling-wave-elaboration-policy.md"
  - "artifacts/epic-integration-branch-contract.md"
  - "artifacts/rolling-wave-issue-elaboration-contract.md"
親: ["init-local-00003"]
実装開始許可: false
repository_evidence:
  role: "authoring-source-provenance"
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "240e561e94b50250a4a6309452a7fd0fb511458a"
  tree: "181f7eb28da0edff3ca1352edf4cb2ae1f21d433"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

**現行状態（2026-09-12）:** [E384-DEC-004](artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md)はsame-EUID非協調actorを保証対象外とし、#392の安全停止を置き換えた。改訂R/D/Pの独立review・clean pushed freeze/projectionまではProduct変更を行わない。#395/#396はB1/B2受入まで開始しない。

## 1. 今回の位置づけ

親計画のcommit/pushとIssue #392の正式startは完了した。安全停止前にCP1–CP4の実装candidateとその検証を行ったが、Issueとして未受入である。現在はOption 1反映後の親／Issue R/D/Pを独立reviewし、clean pushed freezeとGitHub projection/readbackを完了するG0段階にある。G0後はIssue Plan §2.1の限定re-entry（不要になった一件のtest削除と影響gateの再検証）から続け、CP1をやり直さない。過去のGPT-5.6／GPT-6 reviewはそれぞれの記録済みcandidateだけに有効で、現在候補のacceptanceへ流用しない。

目的はprovider状態数・重複検証・実行コストの削減であり、文書数やIssue数を増やすことではない。実装・検証単位は#392 → #395 → #396の三件を維持する。各Issue PRをEpic branchへ人間が順次mergeし、最後にmainへ一度mergeする。

## 2. 作業場所と開始の区別

- Integration branchは `codex/epic-00384-provider-test-strategy-planning` のまま残す。
- 各Issueは最新の受理済みintegration tipから分岐した専用branchで作業する。
- 専用branchは新worktreeでも、ユーザーが明示した本worktreeの再利用でもよい。作業場所の選択はIssueの受入単位やPR baseを変えない。
- SpecDock `issue start` はbranch/activeの正式選択であり、Product実装開始許可ではない。
- Issue詳細R/D/P、Luna Max handoff、独立reviewが揃うまでProduct実装を行わない。formal startだけ、Epic passだけ、dependency readyだけを実装許可にしない。

以前のstart/checkout保留は、2026-09-08の明示的な開始依頼で解除された。#392の正式startを繰り返さない。改訂候補の内容review後、Product実装の開始前にその候補のcommit/push・freeze/projectionを確認する。#395/#396を先にstartしない。

## 3. 依存順と受入条件

| Gate | 必要な入力 | 受入条件 | 次の段階 |
|---|---|---|---|
| G0 Parent freeze | 現行親R/D/P、三Issue draft、契約、原因別register、E384-DEC-004 | 同一候補の独立review pass、P0/P1=0、親の未決判断0。clean pushed tipのfreeze receiptと4 Issue body projection readback | #392は正式start済み。改訂候補の受理後、Issue Plan §2.1から既存candidateを再開 |
| G1 #392 | G0受入済み、#387完了、Option 1の脅威範囲と改訂Issue R/D/P | Issue Plan §2.1から既存candidateを再開し、不要になったtest一件だけを削除して影響gateを再検証する。#395所有baselineは変更せず、全gate結果と責務境界を正確に記録する。Code Review Strict／Final Quality Gate Strictのpass後にmerge-ready候補とする。 | 人間がEpic branchへmergeし、merge後tipでB1 GREENを確認してから#395。 |
| G2 #395 | B1が未達 | 開始しない。baselineの修復・変更を行わない | 停止 |
| G3 #396 | B2が未達 | 開始しない。regression gate/policyを変更しない | 停止 |
| G4 Epic main | B3が未達 | Epic merge/closureを行わない | 停止 |

`E384-DEC-001` / `E384-DEC-002` / `E384-DEC-004` はユーザー採用済みで、親の未決判断は0件である。G0は改訂候補の独立review・clean pushed freeze receipt・projection readbackで受理する。Option 1の採用だけでG0や実装開始を完了扱いにしない。

## 4. 各Issueで繰り返す進め方

1. 受理済みEpic tip、前Issueのmerge/GREEN、dependency、main driftを確認する。
2. ユーザーが開始を依頼したら、現行CLIの正式`issue start`で専用branch/activeを選択する。worktreeはユーザーの指定を守る。
3. 選択したIssueの契約をcurrent treeへ具体化し、R/D/PとIssue専用handoffを作る。調査Issueは作らない。
4. Blue Teamの必要な分析とRed Teamの独立仕様reviewを分離する。Red Teamは`chatgpt-spec-review-strict`をclean pushed exact SHAに対して実行し、初回fresh、同一目的の修正reviewは同じreviewer sessionを使う。P0/P1=0かつ`review_status=pass`になるまでProduct実装を開始しない。
5. 実装・そのIssue自身のテスト/保護/回復確認を行い、Epic baseのPRをmerge-readyにする。
6. 人間merge後のexact integrated tipで、その段階のGREENを確認してからIssueを完了する。
7. 次Issueは前の受入後にだけ詳細化する。

詳細なfile/symbol/test実装/command sequenceはIssue着手時の計画に置く。親で将来の全micro-stepを固定しない。

## 5. #392 — ライフサイクルの簡素化

四root・二slot・closed record/wire・exact migration・tooling-only uninstall・保護データ不変を一体で実装する。旧lifecycle writerとその廃止された振る舞いだけを検証するtestsは、代替contract proofの成立と同じIssueで除く。

`system`交換とruntime lockの競合はE384-RQ-019 / Wire §16を実現して閉じる。初回移行の停止運用はユーザー承認済みである。共有root lease、module import前admission、busyのmutation-zero、update/uninstall双方のrelease→exec、親異常終了時もhelper書込み完了まで保つlease、incomplete後の外部復旧を#392自身で検証する。#395/#396の実装を先取りせず、current baseline/PR/full verifierを整合させる。

## 6. #395 — 既知失敗が表す契約の回復

register §6.1が原因と修復責務の正本である。「全部Product bug」「全部testを直せばよい」のどちらにも決め打ちしない。廃止CLIを復活させず、現行portへtest doubleを追随させ、Product責務混線は本番側で修正する。

14件のnode/signature履歴とaccepted behaviorを保持し、元の振る舞いがnormal passになった証拠でresolvedへ移す。Skip/xfail/approved failure/assertion弱化を認めない。修復途中の部分集合でmerge/完了しない。

## 7. #396 — 最終検証基盤への切替

通常のPR gateは一回のrole graphとper-attempt判定で閉じる。五回測定と二十件履歴の関係、cancel/missing evidence、retry/rerun、環境能力境界は親E384-QUAL-001をそのまま実装する。初期qualificationを五回×二十件の入れ子ループへしない。

Required-contextのintentional REDは五回campaign freeze前に実施し、二十件履歴へは失敗として残す。RED後に必要な二十成功attemptは初期導入証拠の実コストとして扱い、削除・取り直しで隠さない。同一candidateのbuildは一回だけで、後続attemptは同じ保存artifactを使う。

Replacement consumers/providersを先に成立させ、old consumer 0を確認してからledger/timing/sharder/skip/hook/old workflowを削除する。Compatibility-only surface除去後の最終sourceで証拠を取得する。

## 8. レビューと証拠を増殖させない

- 現在の独立review経路はRolling-Wave Contract §5のChatGPT Strict browser flow。User-approved `chatgpt-use-strict`はBlue Team分析用、`chatgpt-code-review-strict`は実装後のRed Team review、`chatgpt-final-quality-gate-strict-v2`はProによる最終gateに使う。local subagentやnon-Strict fallbackへ切り替えない。
- Authorとreviewerを分離する。同一周期は初回fresh・以後same reviewerを使う。
- 変更対象と候補identityを固定し、指摘の原因を直す。未実装のIssue micro-step不足だけでEpicを再設計しない。
- 親の横断契約を変えない実装詳細はIssue側に閉じ、影響のない受入済み親部分を最初から書き直さない。
- 同じraw observationを複数の必要な集計から参照してよい。見せる資料のためだけに製品テストを重複実行しない。
- Review pass、formal start、implementation-ready、実装検証、merge、closureは別々に報告する。

## 9. Merge・回復・停止

Issue PR baseは常にEpic branch。人間だけがmerge/revert/required-context設定を行う。Integration rollbackはwhole Issue merge単位で、後続作業があれば停止して依存suffixの逆順revertまたはowned境界のforward-fixを選ぶ。Agentは未merge作業を勝手に削除しない。

Dependency/identity不一致、未決判断、非GREEN、保護データ変化、未説明のfailure、他Issueの責務、evidence不足、context gap、回復不能の曖昧さでは停止して親へ戻す。実装者にProduct/Policy判断を推測させない。

### 9.1 直列実装中の親修正

[準備失敗ADR](artifacts/20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md)に従い、選択済み#392 branchで親修正を行った。CP1–CP4のProduct candidateは存在するが未受入であり、安全停止後の新しいProduct変更は改訂仕様G0が閉じるまで行わない。親とIssueの内容reviewはworking-tree manifestで固定できるが、公開freezeの完了は別証拠とする。後続Issueの責務は参照確認だけ行い、#395/#396は開始しない。

## 10. 完了

親計画は、未決判断を閉じ、同一候補の独立reviewと公開済みtipの受入記録を揃えた時点で具体化完了とする。Epic製品完了は、G1–G3の受入とG4の人間merge後だけである。

Current parent decision: `owner_decisions_required=[]`。両decisionはユーザー採用済み。
