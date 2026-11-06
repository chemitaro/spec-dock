---
種別: レポート（Epic）
ID: "epic-00573"
関連GitHub: ["#573"]
最終更新: "2026-11-06"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 状態の色と形を改め、作業中を「区切りの輪」（plan.cue の手順の進みと、30分以内の稼働の点滅）で示した（iss-00574、PR #577）。
- 構造の図の最上位の Initiative を、全体表示の倍率が最大になる行の幅で並べた（iss-00575、PR #576）。最初の版（100%表示の幅の残りに入れば並べる）は実データで一度も並ばなかったため、統括の判断で同じ PR で方式を改めた。
- 構造の図の左右・上下の極端に広い隙間と、枠の外への遠回りを直した（iss-00578、PR #579）。taikyohiyou_project の epic-02233 で、列の間 1188→62、行の帯 388→106（1440）、frameExits 56→0。
- SpecDock 0.9.0 をリリースし（iss-00580、PR #582、v0.9.0 = 982932e47）、この PC に導入して常駐のダッシュボードを起動し直し、6つのリポジトリの配布資産を更新した（company-os#9、input-devices#27、housing-lifecycle#253、taikyohiyou_project#2294、generic-mona#25、tenting-cradle#17。すべて利用者がマージ）。
- 同じ版に、epic-00080 の iss-00572（時間のテストの測り方、favicon、Scope 0件の札、390px の帯の線。PR #581）も入った。

## Verification

- 各 Issue：仕様のレビュー、コードのレビュー、最終品質ゲートが P0・P1 なしで合格。`make lint` と `uv run pytest`（全体）が最終のコミットで合格。CI 合格。写しは各 Issue の artifacts と report.md。
- 統括の確かめ：headless Chrome で、#574 の写し（明るい・暗い）、#575 の実データの写し（1440、1920、390）、#578 の直す前後と遠回りの直し、#572 の favicon・札・390px を見た。
- リリース後：`spec-dock --version` が 0.9.0、http://100.85.74.8:47800/ と `/favicon.ico` が 200、7つのリポジトリの main（taikyohiyou_project は develop）で版 0.9.0 と `canonical check` の合格。

## Residual Risks / Follow-ups

- 構造の図で、線の通らない行の帯が一部残る（同じ行の高い Epic の枠に行の高さをそろえる決まりによる。#578 の対象外）。
- 「終わったものも」を出す木の表し方の最も重い配置は、もとから遅く 4.2→4.8 秒（#578 の report）。
- 1440×900 では、Initiative の横並びの倍率の上がり方が小さい（高さで決まるため。27%→30%）。
- 統括が 2026-11-05 に挙げた「文書の画面の目次の背景が切れる」は、ページ全体を1枚に撮る写し方による見かけで、不具合ではなかった（#572）。
