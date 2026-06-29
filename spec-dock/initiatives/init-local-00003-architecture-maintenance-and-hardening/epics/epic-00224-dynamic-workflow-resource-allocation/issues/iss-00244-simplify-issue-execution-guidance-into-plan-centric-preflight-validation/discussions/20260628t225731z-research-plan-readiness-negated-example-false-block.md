---
種別: research
ID: "20260628t225731z-research"
タイトル: "Plan Readiness Negated Example False Block"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: []
authority: "synthesized"
derived_from:
  - "../../plan.md"
  - "../../report.md"
  - "../../../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md"
reflected_to:
  - "../../report.md"
---

# 20260628t225731z-research Plan Readiness Negated Example False Block

## 調査目的

PR #245 の手動テストを兼ねて `./spec-dock/scripts/spec-dock guidance issue-execution` を実行したところ、active issue `iss-00244` の `plan.md` が実装ステップを持っているにもかかわらず `plan-not-executable` になった。原因、影響、修正方針を整理する。

## sources / 調査方法

- 参照先:
  - `spec-dock/active/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `spec-dock/scripts/spec_dock_runtime/application/workflow.py`
  - `tests/cli_runtime/test_workflow.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock guidance issue-execution`
  - plan readiness classifier の marker 判定を確認。
  - active plan 内の negated marker 出現箇所を確認。
- 実験条件:
  - branch: `iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation`
  - head before fix: `357797ee71978668d83e27eb92c4d798b02b59a2`

## facts / 観測できた事実

- `guidance issue-execution` は `state=blocked`、`reason_code=plan-not-executable`、`may_execute_approved_plan=false` を返した。
- active `plan.md` は `状態: "approved"` で、`## 実装ステップ`、`#### 具体テストケース一覧`、S01-S399 の step contract を持っている。
- active `plan.md` の `tc-044` 行は、バグクラス説明として `approved plan says there are no implementation steps yet` を含む。
- plan readiness classifier は `no implementation steps` / `no executable steps` を本文全体から検出し、executable marker の存在確認より先に scaffold と判定していた。
- 既存テストは「実装ステップがない plan が `no implementation steps` と書いた場合に block する」ケースを固定していたが、「executable plan 内のテスト説明に negated marker が出る」ケースを固定していなかった。

## inference / 推測

- 原因は、scaffold marker を artifact 全文に対して先勝ち評価したことによる false positive である。
- `TODO` / `TBD` については本文中の user data として許容するテストが既にあり、negated marker も同じく「実装可能性を示す強い marker がある場合は説明文として扱う」方針が妥当である。
- 一方で、実装ステップを持たず `There are no implementation steps yet` とだけ書く plan は引き続き block すべきである。

## unverified / 未検証事項

- PR #245 の最新 head に対する GitHub Actions と Codex review completion は、この artifact 作成時点では再監視前である。
- 修正後の live PR observation が `review_completion_unknown` に戻らないことは、後続の `wait_pr_observation.sh` 手動テストで確認する。

## question candidates / 質問候補

- 人間判断が必要な候補:
  - なし。既存 AC-004 / AC-010 / tc-044 の範囲内で修正可能。
- 質問せずに解決できた候補:
  - executable marker が存在する plan 内の negated marker は、fixture / bug-class / test explanation として扱う。

## terminology conflicts / 用語衝突

- 衝突している用語:
  - `no implementation steps`
- 既存 docs / code / tests / discussions での使われ方:
  - genuine non-executable plan の説明として使われる。
  - `Spec-Locked Closure Index` では、失敗検出・bug class の説明としても使われる。
- 判断が必要な理由:
  - 同じ文字列が「plan 自体が未計画」を意味する場合と「未計画 plan を検出するテスト説明」を意味する場合がある。

## edge cases / 具体シナリオ

- edge case:
  - approved executable plan が `Spec-Locked Closure Index` や具体テストケースで `no implementation steps` を negative fixture として説明する。
- その edge case が requirement / design / plan に与える影響:
  - AC-004 は「非実行 plan を block する」要件であり、「実行 plan 内の説明文を block する」要件ではない。
  - tc-044 はこの edge case を実運用で踏んだため、テストとして固定する必要がある。

## implications / 判断への含意

- `_classify_plan_text` は frontmatter scaffold marker を引き続き fail-closed に扱う。
- 本文中の negated marker は、executable marker が存在しない場合だけ scaffold として扱う。
- provider runtime と dogfooding runtime の両方を同期する。
- `tests/cli_runtime/test_workflow.py` に executable plan 内の negated fixture prose を許容する regression test を追加する。

## リスク/制約

- この修正で、`## 実装ステップ` だけを含む空に近い approved plan が通りやすくなる可能性はある。
- ただし現行 classifier は元々 heuristic preflight であり、詳細な step schema enforcement は plan authoring/review 側の責務である。
- frontmatter draft や template managed marker は引き続き block する。

## 反映先

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
- `spec-dock/scripts/spec_dock_runtime/application/workflow.py`
- `tests/cli_runtime/test_workflow.py`
- `report.md`
