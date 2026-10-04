# Code Review Strict r12 完全batchの分析
状態: 完全batchをローカル照合して計画へ採用。2026-10-02 JST。P-07の追加修正として登録。実装修正は未実施。
対象: chemitaro/spec-dock、codex/iss-00413-external-cli-state、121228c6fca1fd016e7bccef009902396112ba43。比較基準6fec3099d8759b4e5b3b393b2987534b46dfa383。
最新user authority: 対応OSはLinux/macOSのみ。Windows義務は廃止。先にStrict第三者の要件/設計/追加計画、次にStrict実装brief、その後に必要な削除を行う。
## Batchの完了と証拠
r12 native JSONはfindings一件、priority1、review_status=fail、wrapper actual exit10。原文はcode-review-r12-121228c6.jsonへ保全。
同じsource/tests/CIのclean2b2be5e2のmacOS普通全件は1916 passed/4 skipped、exit0、手動installed console14操作（stateful fake gh26 requests）も別の証拠としてある。
現在121228c6のLinux ordinary fullは最初4 failed/1884 passed/20 skipped/12 errors、exit1。全failure/errorはuvのsubprocess PATH不足。container PATHだけを修正した普通fullは1900 passed/20 skipped（977.90秒）、actual exit0。before/after候補SHA/clean/input324filesのhash2bcbce60d8b318761f81529c4b998fae4d43027b52470fba317143400547494eが一致。source/tests修正なし。skipをnative Windows成功にしない。
## Finding R12-F1
原分類: [P1] 選択観測不能でもFinishがIssueをCloseする。分類は変更しない。
妥当性: source traceで成立。application/direct_finish.py:50のread_selectionがinvalid/unavailableを返しても、明示TARGETはresolve_scopeから解決できる。61-67のclear_handleはNoneになり、gateway.get/set_state又はlocal metadata replaceへ進む。選択保存を観測不能のまま、該当選択の解除を省略して成功へ到達できる。
到達条件: Linux/macOSでbroken JSON、複数record、identity不一致、読取不能storeなどがあり、明示Scope IDによるwork finish。@currentはresolve_scopeの既存guardで停止するので同一ではない。emptyは妥当な無選択であり、invalid/unavailableと区別して維持する。
authority: RQ-413-08/AC-413-16/D-08の完了確認と該当record解除、RQ-413-14/AC-413-31とD-03/D-04のinvalid/unavailableをemptyにしない契約。Windows非対応の最新決定でもPOSIXへの到達条件は消えない。
最初の誤り: implementation（direct_finishの選択観測結果のadmission）。全writer lockの欠如ではない。
primary route: implementation-remediation。対象に選択があるかを確定できないFinishだけを、remote GET/PATCH・local lifecycle write前にinvalid/unavailableで停止する。empty/selected、既存のexplicit chain外Finishとcaptured-tokenの遅い解除、子孫条件、Git原文、branch保持を保全。
認可: 既存全指摘の分析/修正/再レビュー指示とIssue413実装認可の範囲。さらに今回はWindows撤去の計画確定・brief後の実装順序を守る。新たな人間のOS判断・通常ファイル権限/lockは不要。
ブロッキング: CodeReviewのP1によりcandidate合格は阻害される。ローカル修正だけではclosureにせず、変更後のclean/push済みSHAからfresh CodeReviewStrictを行う。
検証予定: 明示TARGET+実corrupt JSONの公開mainがgh呼出し0/effects[]/保存bytes不変で拒否するRed→Greenを一件ずつ進める。次に実unavailable store、legacy local lifecycle保全、dry-runを検証。既存empty Finish、selected chain外Finish、A/B遅い解除、unknown Closeと子孫guardを回帰する。Windows-onlyテストは要求しない。
## その他のroot group
Linux initial runner failure: external environment。PATH補正だけで同SHAのfullが通過。元失敗・input hash・exitを保存し、製品を歪めて通さない。
Windows coverage obligations in old review explanation: 最新の人間のOS決定でscopeから廃止。requirement/design/planとWindows専用code/CIを第三者分析後に改訂・撤去する。raw review本文を改ざんしない。
過去SHAのfull/manualと未実施P-16/P-17、Strict/FQは別に保全。今回のレビュー又はLinux passを全Issue完成にしない。

原文: [r12 native JSON](code-review-p06-12.json)。実測: [Linux通常全件](linux-full-121228c6.md)。Windows撤去: [P-18](../plan.md#p-18)。
