# P-02 Strictコードレビュー指摘の分析

## 証拠と対象

GPT-5.6 Sol / Proによる新規Strictレビューは、`6fec3099d8759b4e5b3b393b2987534b46dfa383..f168dc4735aa26188ab0d945d94ef0095a09a9e1`のP-02 package/utility checkpointを対象とした。GitHub固定SHA検証後、JSON契約を満たす結果が返り、wrapperはexit 10、`review_status=fail`だった。全結果は[原文](code-review-p02-01.json)。同時に走っていた必須laneはない。P-03以降と未合格の全体mypyは、このcheckpointの合格と区別している。

## 原因・対応判断

唯一の指摘は原分類P1「v2 parse診断がcredentialを無加工で出力する」。不正なsubcommand値に既知GitHub tokenまたはBearer値を渡すと、argparseのmessageに値が入り、`render_diagnostic_json`が旧rendererの`_redact`を迂回していた。CLI公開入口から到達可能で、C-04の既知token最小秘匿契約を破る。最初の誤りはpresentation実装層であり、要件・設計の変更は不要。妥当かつP-02をblockする。

primary routeは`implementation-remediation`。利用者の修正・再レビュー指示により自律対応が認可されている。JSON schema、exit 2、effects空、引数エラーの内容は維持し、直列化前に既存秘匿処理を適用する。新しい秘匿ポリシーやstateは追加しない。

## 検証・次のゲート

`test_cli_v2_redaction.py`で`github_pat_`、`ghp_`、`Bearer`の3到達例を公開`main`から確認した。最初の試験は先行する別の不正commandで止まり、指摘の再現ではなかったため入力を修正した。修正入力でmessageに未秘匿値が入るassertion失敗を確認し、その後rendererの修正で3例が成功した。既存envelope試験と合わせて15 passed。

ローカルGreenはレビュアーによる閉鎖ではない。必要なcheckpointを保存・push後、現候補を独立した新規Strictレビューへ提出する。合格を得るまではP-02レビュー未合格を維持する。
