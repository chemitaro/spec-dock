# P-07 選択観測不能時のFinishを変更前に拒否する

2026-10-02 JST。基準aa91b756f886ac3e42085b665e1e9ca93c20f9f5。独立r12の[完全batch分析](code-review-p06-12-analysis.md)と[P-07追加契約](../plan.md#p-07)に沿う独立した修正です。Windows撤去とは別のcheckpointとし、raw reviewのP1分類とfail判定を変更しません。

## Authorityと対応方針

RQ-413-08/14、AC-413-16/31、D-03/04/08はinvalid/unavailableを妥当なemptyとして扱わず、捕捉した選択だけを完了確認後に解除する契約です。明示TARGETから読めない選択を無視してremote/local lifecycleへ進むimplementation admissionが最初の誤りです。新state、公共API、同期、lock、権限、journal、旧記録の自動修復は不要です。利用者の全指摘分析・修正・再レビューと本Issueの実装許可により対応します。要件・設計の意味は変更しません。

`direct_finish.py` の一回の観測直後にinvalid/unavailableを拒否します。target解決、remote GET/PATCH、真正local metadata変更、dry-runの成功計画より先です。妥当なempty/selected、既存chain外Finish、staleの既存意味、遅いcaptured-token解除、子孫条件、Git原文とbranch保持は維持します。

## 公開境界でのTDDと回帰

[元ログ](p07-finish-observation-repair.json)にactual exitとhashを保存しています。実corrupt JSONを持つ明示TARGETの公開mainは、修正前にGitHub completedを返しexit0になり、意図したassertion Red（1 failed、0.69秒、exit1）。同じtestはguardの二行追加後、1 passed（0.18秒）、exit0です。

実symlinkで観測不能なstoreはGitHub側apply/dry-runともexit3/PRECONDITION_FAILED、gh呼出し0/effects[]、選択・metadata・HEAD・foreign bytes不変を確認しました。妥当なemptyは従来通り明示IssueをCloseします。既存true-localのredirected .agentもapply/dry-runでmetadata/外部pathを保全して変更前に拒否します。この事前拒否の終了値は旧の後段IO失敗exit5からexit3となり、旧testを新admission契約へ合わせました。

Finish、active、public contract、native concurrent Startの回帰は99 passed（23.93秒）、actual exit0。通常make lintもRuff check/format、mypy全てpass、exit0。空からのFinish、選択された親/子、A/Bの遅い解除、unknown Close、native Git部分失敗を含みます。

## 残る認定

これはローカル修正とfocused evidenceです。P1のreviewer closure、撤去後のLinux/macOS full、必要なPython3.10範囲、installed product手動、fresh Code Review Strict、Final Quality Gateはまだ認定していません。clean/push済み新候補で実施します。P-16実dogfood切替とP-17正式#413 import/Startはhuman merge後のままです。
