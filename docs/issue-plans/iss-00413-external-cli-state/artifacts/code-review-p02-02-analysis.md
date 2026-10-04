# P-02 再レビューの分析

## 対象と形式

対象は`6fec3099d8759b4e5b3b393b2987534b46dfa383..c16015db8751318c64bd670d78d624b2e38f0c96`。GPT-5.6 Sol / Proの新規Strict回答はGitHub connectorのrepository/branch/full SHA確認を明記した。wrapperは`OUS-O001-OUTPUT-CONTRACT-INVALID`/exit20だった。説明文字列に未escapeの引用記法が入り、機械JSON判定を満たさない。[原回答のbytes](code-review-p02-02-response.txt)を保全した。利用者の「JSONの正確さではなくレビュー内容を汲み取る」指示に従い、意味を分析する。形式が直った結果を捏造せず、合格とも扱わない。同時必須laneなし。新しいP-06作業はこの固定候補のレビュー証拠ではない。

## P1の対応

原分類P1はtextのparse failureの既知tokenと、JSONのURL userinfoが未秘匿になる到達経路。同じcredential invariantが別出口で再発しているため、局所JSON修正だけを繰り返さず、C-04と全公開parse出力経路を再照合した。`_parse_failure`のtext分岐はraw messageを返し、既存`_redact`はURL userinfoを扱わない。いずれもpresentation/parsing実装が最初の誤りで、accepted requirement/designは明確。妥当かつblocking。

primary routeは`implementation-remediation`。既存の共通秘匿処理にURL userinfoの最小置換を追加し、JSON/textのparse診断とexplicit helpの診断へ同じ処理を使う。通常エラー文言、host/path、改行と公開schema/exit/effectsは維持する。新しい責任・state・policyは追加せず、利用者の修正指示内で認可済み。公開mainのJSON/text×既知token/URL userinfoをRed→Greenで確認し、現在候補を新規Strict再レビューする。

## P2/P3とcoverage

原分類P2はleaf helpのv1案内とv2出力の不一致、原分類P3はAGENTSのruntime旧path案内。どちらも現物で確認できるが、Strictのblocking policyはP0/P1であり、この2件だけを理由に新しい自律修正や再レビューは起こさない。P-12の既存help/skills更新とP-14の文書確認がそれぞれ同じ問題を解消する予定なので、その実装時に検査する未完了の既存plan obligationとして保持する。

全体mypy、Windows、business/installationは引き続き後続必須gate。現在のレビュー合格を全体完成に読み替えない。
