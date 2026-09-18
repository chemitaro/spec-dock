---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-17"
依存:
  - "requirement.md"
  - "design.md"
  - "artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md"
  - "artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md"
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
  sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
  tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

**現行状態（2026-09-17、GitHub readback）:** [E384-DEC-004](artifacts/20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md)と[P392 sequence ADR](artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md)は引き続き有効である。PR #399は人間によりEpic branchへmergeされ、PR head `75f0ec5a23eee40c528f049029b8561dcb7880dd`とmerge commit `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`は同じtree `190bc566a18cd84813c4b7c043f8724e275cb55d`である。このmergeはP392であり、B1や#392の完了・closureではなかった。#395の人間merge後のexact SHA `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`に対しB1/B2を同一tipで実施し、B1 current gatesはGREEN、B2は`2188 passed, 26 skipped`、15/0/15、violations 0で成立した。証拠は#396の[B1/B2 entry receipt](issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/artifacts/20260917t124918z-01--b1-b2-gate-receipt.md)に保存した。GitHub #392/#395はCLOSED、#396はOPENでformal start済みかつactiveである。現在は#396のR/D/Pを独立Strict reviewへ通す段階で、Product実装許可はfalse、B3は未開始である。

**2026-09-15時点の履歴:** 当時のreadbackでは#392/#395がOPENで、#392の`active`は未設定、#396は未開始だった。下記の過去手順・receiptはその時点の状態を記録する。

## 1. 今回の位置づけ

親計画のfreezeとIssue #392の正式startは完了し、PR #399もP392として人間merge済みである。#395のB1/B2をexact post-merge SHA/treeで実施し、#392/#395は所定順でCLOSEDとなった。2026-09-17現在、Issue #396がformal start済み・activeであり、このR/D/P候補の独立Strict reviewを準備している。Product実装許可はfalseで、B3は未開始である。安全停止前のCP1–CP4 candidateと過去Reportのfull-verifier結果は履歴であり、現在のmerged-tip証拠には流用しない。具体的な状態・SHA gate・formal startは§3.1に従う。

目的はprovider状態数・重複検証・実行コストの削減であり、文書数やIssue数を増やすことではない。実装・検証単位は#392 → #395 → #396の三件を維持する。各Issue PRをEpic branchへ人間が順次mergeし、最後にmainへ一度mergeする。

## 2. 作業場所と開始の区別

- Integration branchは `codex/epic-00384-provider-test-strategy-planning` のまま残す。
- 各Issueは最新の受理済みintegration tipから分岐した専用branchで作業する。
- 専用branchは新worktreeでも、ユーザーが明示した本worktreeの再利用でもよい。作業場所の選択はIssueの受入単位やPR baseを変えない。
- SpecDock `issue start` はbranch/activeの正式選択であり、Product実装開始許可ではない。
- Issue詳細R/D/P、Luna Max handoff、独立reviewが揃うまでProduct実装を行わない。formal startだけ、Epic passだけ、dependency readyだけを実装許可にしない。

以前のstart/checkout保留は2026-09-08の明示的な開始依頼で解除され、#392はformal start済み、#395と#396も後続の明示依頼と依存gateを経てformal startされた。2026-09-17現在#392/#395はCLOSED、#396がactiveである。formal startは選択状態でありProduct実装許可ではない。#396のR/D/Pをclean pushed exact SHAで独立Strict reviewし、GitHub Issue projectionをreadbackし、ユーザーが実装をdispatchするまでProduct変更を開始しない。

## 3. 依存順と受入条件

| Gate | 必要な入力 | 受入条件 | 次の段階 |
|---|---|---|---|
| G0 Parent freeze | 現行親R/D/P、三Issue draft、契約、原因別register、E384-DEC-004 | 同一候補の独立review pass、P0/P1=0、親の未決判断0。clean pushed tipのfreeze receiptと4 Issue body projection readback | #392は正式start済み。改訂候補の受理後、Issue Plan §2.1から既存candidateを再開 |
| G1 #392 | G0受入済み、#387完了、Option 1とP392 ADR、改訂Issue R/D/P | Issue Plan §2.1から限定再開し、不要なtestだけを削除して影響gateを再検証する。#395所有baselineは変更・抑止しない。merge前の#392所有gate／required checksとStrict review／Final Quality Gateを満たして人間mergeした後、§3.1に従ってmerge SHA上のfresh P392 receiptを記録する。P392はB1・#392 closureではない。 | P392 receipt後に、#392をOPENのまま#395をexact tipから詳細化・正式startする。 |
| G2 #395 | §3.1のexact P392 witness、15/14/1・243・policy不変、#392所有gate pass、明示的なユーザーstart依頼 | 14 active rowsをcause-appropriate repairでterminalizeする。skip/xfailやpolicy変更は禁止。人間merge後に一つのexact SHAを固定し、同じSHAでB1（全current gates GREEN）、続けてB2（15/0/15）を検証する。closureと#396へのhandoffは§3.1に従う。`ready=true`だけでは開始しない。 | B1/B2の同一tip証拠後に#392/#395をclosureし、#396へ進む。 |
| G3 #396 | #395 post-merge exact tipでB1/B2成立、#392/#395 CLOSED、#396 formal start済み | R/D/PとLuna Max handoffを独立Strict reviewでpassにし、GitHub Issue projectionをreadbackする。明示的な実装dispatchまではProduct実装を行わない | 実装許可後に#396のreplacement gateとB3計画を実行 |
| G4 Epic main | B3が未達 | Epic merge/closureを行わない | 停止 |

`E384-DEC-001` / `E384-DEC-002` / `E384-DEC-004` はユーザー採用済みで、親の未決判断は0件である。G0は改訂候補の独立review・clean pushed freeze receipt・projection readbackで受理する。Option 1の採用だけでG0や実装開始を完了扱いにしない。

### 3.1 P392から#395へのhandoff

この節は受理済み[P392 sequence ADR](artifacts/20260913t144152z-adr-issue-392-provisional-merge-and-deferred-b1.md)を運用手順にするもので、新しいnon-GREEN例外や#395の依存edgeは追加しない。2026-09-15のreadbackではPR #399がmerge SHA `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`でEpic branchへ統合済みであり、#392と#395はともにOPEN、`active`は未設定である。#392 Report §33に、このexact merge SHAのP392 receiptと検証結果を記録済みである。

1. **#392のtracker状態を整合させる。** P392で#392を完了・closeしない。#392はreopen済みでGitHub OPENを確認済みであり、P392中に`issue finish`を使わない。これは受理済みclosure順を保つ状態補正であり、#395のcontent gateやP392 evidenceの代替ではない。
2. **merged-tip P392 witnessを確定する。** `codex/epic-00384-provider-test-strategy-planning`のHEADとupstreamがともに`921bf7512c72bfa2887673cb7ec9bc512cec6ff3`であることを確認し、そのSHAでP392 ADRの条件をfreshに検証した。current full verifierは同じSHAで実行し、全10 violationをregister §6.1の#395-owned active rows（4–12、15）へ対応付け、#392-owned failureとunexpected failureが0であることを記録した。併せて#392-owned/required checks、15/14/1、timing 243、required-fast 4、policy不変、lifecycle/protected-data/dogfood evidenceを確認した。Code Review Strict／Final Quality Gate receiptはmerge tree `190bc566a18cd84813c4b7c043f8724e275cb55d`に対して取得し、Code Reviewはpass、Final Quality GateはProでpassとなった。full verifierはGREENではなく、P392限定の受入証拠として扱う。過去candidateの結果はmerged-tip証拠として流用していない。
3. **P392のbaseを保つ。** #395用branch/worktreeは、Epic Planのdoc-only補正PRより先に、このexact P392 SHAから作成・readback済みである。branch `codex/epic-00384-provider-test-strategy-planning-iss-00395-p392-921bf751`、HEAD `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`、clean、`active`未設定、dependency `ready=true`、SpecDock validate `nodes=236`を確認した。この計画補正は開始点を移動させず、#395のformal startを代替しない。不一致・来歴不明なら停止し、reset/deleteで直さない。
4. **明示依頼の後に#395を正式startする。** `active show`でIssue selectionを確認する。active Issueが#392なら`./spec-dock/scripts/spec-dock issue start iss-00395 -f`を使う。`-f`が迂回するのはunfinished-active-Issue guardだけで、dependency readiness・checkout・active writeの検査は維持される。active Issueがない場合は`./spec-dock/scripts/spec-dock issue start iss-00395`を使い、#392以外のIssueがactiveなら停止して解消する。`active set`はformal startではなく、`ready=true`もP392 witnessやユーザーの開始依頼を代替しない。start直後にbranch、HEAD/base SHA、active Issue #395、Issue状態、未変更Product treeをreadbackする。
5. **実装開始を別gateに保つ。** #395のformal start後も、implementation-ready R/D/Pとhandoffを具体化し、clean pushed exact SHAへの独立Strict reviewがpassするまでProduct実装を開始しない。formal start、implementation readiness、Product実装許可は別々に判定する。
6. **B1/B2とIssue closureを同一tipで行う。** #395を人間mergeした後にexact SHAを固定し、B1を確認してから同じSHAでB2を確認する。両方の証拠を揃えた後、非activeの#392は`./spec-dock/scripts/spec-dock close iss-00392`でcloseし、active #395は`./spec-dock/scripts/spec-dock issue finish`でcloseする。両GitHub IssueがCLOSEDでactive pointerが解除されたことを確認し、その後にだけ#396をstartする。#392はB1後、#395はB2後が最早のclosure時点であり、この順序はADRを遅らせるだけで変更しない。

### 3.2 2026-09-17 B1/B2 and Issue #396 handoff

上記gateを実行した結果、#395 exact post-merge tip `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`でB1とB2は成立し、#392/#395はCLOSED、#396はOPEN・activeとなった。実測とraw evidence hashは[#396 B1/B2 receipt](issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover/artifacts/20260917t124918z-01--b1-b2-gate-receipt.md)および同IssueのJSON evidence artifactsを参照する。これは#396 entry gateだけを満たし、Issue #396の独立仕様review、Product実装、required-context cutover、B3を完了扱いにしない。

## 4. 各Issueで繰り返す進め方

1. 受理済みEpic tip、前Issueのmerge/state（#395は§3.1のP392 witness、#396はB2）、dependency、main driftを確認する。
2. ユーザーが開始を依頼したら、現行CLIの正式`issue start`で専用branch/activeを選択する。#395のactive guardとexact baseは§3.1を守り、worktreeはユーザーの指定を守る。
3. 選択したIssueの契約をcurrent treeへ具体化し、R/D/PとIssue専用handoffを作る。調査Issueは作らない。
4. Blue Teamの必要な分析とRed Teamの独立仕様reviewを分離する。Red Teamは`chatgpt-spec-review-strict`をclean pushed exact SHAに対して実行し、初回fresh、同一目的の修正reviewは同じreviewer sessionを使う。P0/P1=0かつ`review_status=pass`になるまでProduct実装を開始しない。
5. 実装・そのIssue自身のテスト/保護/回復確認を行い、Epic baseのPRをmerge-readyにする。
6. 人間merge後のexact integrated tipで、その段階の受入を確認する。P392では#392を完了扱いにせず、#392/#395はB1/B2が同じtipで成立した後、§3.1の順でclosureする。
7. 次Issueは前段階の受入後に詳細化する。#395に限り、受理済みP392 witnessは#392の最終acceptanceではなく、#395の限定handoff入力である。

詳細なfile/symbol/test実装/command sequenceはIssue着手時の計画に置く。親で将来の全micro-stepを固定しない。

## 5. #392 — ライフサイクルの簡素化

四root・二slot・closed record/wire・exact migration・tooling-only uninstall・保護データ不変を一体で実装する。旧lifecycle writerとその廃止された振る舞いだけを検証するtestsは、代替contract proofの成立と同じIssueで除く。

`system`交換とruntime lockの競合はE384-RQ-019 / Wire §16を実現して閉じる。初回移行の停止運用はユーザー承認済みである。共有root lease、module import前admission、busyのmutation-zero、update/uninstall双方のrelease→exec、親異常終了時もhelper書込み完了まで保つlease、incomplete後の外部復旧を#392自身で検証する。#395/#396の実装を先取りせず、current baseline/PR/full verifierを整合させる。

## 6. #395 — 既知失敗が表す契約の回復

register §6.1が原因と修復責務の正本である。「全部Product bug」「全部testを直せばよい」のどちらにも決め打ちしない。廃止CLIを復活させず、現行portへtest doubleを追随させ、Product責務混線は本番側で修正する。

P392でhuman-mergedされた#392 exact tipをread-only lifecycle inputにする。14件のnode/signature履歴とaccepted behaviorを保持し、元の振る舞いがnormal passになった証拠でresolvedへ移す。Skip/xfail/approved failure/assertion弱化を認めない。修復途中の部分集合でmerge/完了しない。B1/B2およびclosure手順は§3.1に従う。

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

Dependency/identity不一致、未決判断、P392許容集合外のfailure、B1/B2非GREEN、保護データ変化、他Issueの責務、evidence不足、context gap、回復不能の曖昧さでは停止して親へ戻す。P392に限る許容はnew ADRのexact measurement ruleだけで、一般のnon-GREEN waiverではない。

### 9.1 直列実装中の親修正

[準備失敗ADR](artifacts/20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md)に従った親修正、#392のreopen、P392 human merge、merged-tip receiptの記録は完了した。後続の#395 B1/B2とIssue closureを経て、#396は2026-09-17にformal startされactiveとなった。次の作業は#396 R/D/Pの独立Strict reviewとIssue projection readbackであり、明示的な実装dispatchの前にProduct変更を行わない。Initiative-level portfolio priorityは別のgovernance follow-upで扱い、このEpic/Issue更新では変更しない。

## 10. 完了

親計画は、未決判断を閉じ、同一候補の独立reviewと公開済みtipの受入記録を揃えた時点で具体化完了とする。Epic製品完了は、G1–G3の受入とG4の人間merge後だけである。

Current parent decision: `owner_decisions_required=[]`。両decisionはユーザー採用済み。
