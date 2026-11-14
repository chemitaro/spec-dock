---
種別: レポート（Epic）
ID: "epic-00471"
関連GitHub: ["#471"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 2026-11-14：要件・設計・計画を、統括の決定（Orca の依頼 task_87517b448497）どおりに書き、子の Issue に切り分けた。
  - iss-00591「orca-web の場所の設定と、Scope と worktree の対応を決める」（standard）
  - iss-00592「構造の図・ボード・横の欄に稼働の印と「Orca で開く」を出す」（standard、iss-00591 の後）
  - 依存：iss-00592 → iss-00591。epic-00526 の iss-00593 も iss-00591 に依存する。
- 統括の決定に足した設計の判断（requirement.cue の decisions の最後の2つ）：設定は `config.json` の最上位の節 `orca_web`（`enabled`、`port`）に置く。「同じリポジトリ」は、要約の中でこのリポジトリの worktree とパスが一致した worktree の `project.id` で決め、手がかりがなければブランチ名だけでは対応させない。ほかに、画面の CSP に orca-web のオリジンを足すこと（今の CSP では読めないため）、埋め込みの画面では「Orca で開く」を置かないこと（orca-web の frame-ancestors のため）を設計に入れた。

## レビュー記録

- 2026-11-14 仕様レビュー：合格（round-1）。spec-reviewer（Opus 5.5 / high）。P0 0、P1 0、P2 3、P3 2。
  - 対象の sha256：requirement.cue `0e7e70b8aff7703a6a309f406a563a9e755f3a90bcd9a55051710c23d0cc8d28`、design.cue `a145de2ab28564512b4ce1ac8f9e03295a291b46da20998d77d9a9d1ce9a2aa2`、plan.cue `95256b06b09e62ee562035ffd5f1e276b61bed37c1cfeac5038ad499ca882c54`、explanation.html `c34e66377bdbf338cb6c5aaf4db4750bfda30da0680bb7d949e472fb1ea1a5e2`。main の HEAD `89f51588a`（clean）。
  - 結果：main のチェックアウトの `.workbench/spec-review/epic-00471/round-1.json`（検査 `round-1.check.json`、valid、pass）。
  - P2/P3 は直さずに記録する。子の Issue のタスク担当は、Issue の仕様を書くときに次を扱う：
    - P2（iss-00591）：構造の worktree の記録は、画面が構造の revision の変化のときしか読み直さないので、ほかに変化がなければ新しい worktree の印が出るまでの時間が決まらない（`dashboard_site.py` の revision の材料に `git worktree list` が入っていない）。revision に含めるか、別の読み直しの経路を Issue の設計で決める。R-08 の「5秒ごとの描き直し」は「構造の描き直し」と読む。
    - P2（iss-00592）：横の欄の `build()` が走り直したとき（片付けの候補の一覧の後など）、D-07 の「Orca で開く」の比べの鍵も戻す。
    - P2（iss-00591）：受け入れの確かめの例の iss-00589 の worktree は、マージ後に片付けられた。確かめのときにエージェントのいる別の worktree を使う。
    - P3（iss-00592）：D-06 の `max` の値（全体の例の 4 と、箱 3・枠 4）は、置き場ごとに決める。
    - P3（iss-00592）：D-05 の「送る要求の限り」に、D-07 の `open-button.js` の読み込みとその iframe も入る。

## Verification

- `spec-dock scope check epic-00471`：誤りなし、警告なし（2026-11-14）。

## Residual Risks / Follow-ups

- design.cue の risks を参照（部品の契約の変化、module の import の失敗の覚え、localhost と MagicDNS の名前で開いたときに読めない、箱の狭さ）。
