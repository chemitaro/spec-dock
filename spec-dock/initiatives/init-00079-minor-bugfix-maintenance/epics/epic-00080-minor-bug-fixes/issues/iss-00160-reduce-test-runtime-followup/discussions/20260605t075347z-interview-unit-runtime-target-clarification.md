---
種別: interview
ID: "20260605t075347z-interview"
タイトル: "Unit Runtime Target Clarification"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00160"]
関連:
  - "20260605t075347z-01-adr"
scope: "issue"
scope_id: "iss-00160"
created_at: "2026-06-05T07:53:47Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260605t045222z-research-test-runtime-measurement-analysis.md"
  - "20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md"
  - "20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260605t075347z-interview Unit Runtime Target Clarification

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Unit test の受け入れ条件として「どの程度速ければ成功か」を固定する。
  - `design.md`:
    - fixture 軽量化、CLI subprocess 縮小、runner 分離の優先度と depth を左右する。
  - `plan.md`:
    - step の完了条件、測定コマンド、final QA gate の success threshold を左右する。
  - `ADR`:
    - ADR の分類方針自体は確定済みだが、runtime target は ADR ではなく issue-local AC に反映する。
- chat 上の軽微な一問では足りない理由:
  - 目標時間は acceptance criteria / verification gate / implementation scope に直接影響するため、回答前の正式質問シートとして残す。

## 質問の目的

- 対象者:
  - `spec-dock` maintainer / user
- 何を明確にする質問か:
  - 日常実行する `tests/unit/` の目標実行時間を、どの程度に設定するか。
- 回答が後続判断へ与える影響:
  - 目標が短いほど、CLI subprocess 削減や fixture direct materialization の範囲が広がる。
  - 目標が緩やかなら、まず分類と default fixture 縮小を優先し、深い branch coverage 移行は段階化できる。

## 質問

- 質問:
  - `tests/unit/` の日常実行時間について、今回の issue の成功条件としてどの目標を固定しますか？
- 回答してほしいこと:
  - 次の Option A/B/C のいずれか、または別の具体秒数を指定してください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/active/initiative/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
  - `20260605t045222z-research-test-runtime-measurement-analysis.md`
  - `20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md`
  - `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`
- local context で解決できたこと:
  - 現状 full run は `10:00.07 total`。
  - 遅い test は外部実通信ではなく local heavy fixture に集中している。
  - `unit` / `integration` の分類方針と fixture 軽量化方針はユーザー共有の決定として ADR に記録済み。
- まだ人間判断が必要な理由:
  - 「日常的に高速」の許容値は product / maintainer experience の判断であり、local code から一意に決められない。

## 回答案

- Option A:
  - `tests/unit/` は 60 秒以内を目標にする。
  - aggressive target。CLI subprocess の代表 smoke 化、branch coverage の application/domain 直移行、fixture direct materialization を強く要求する。
- Option B:
  - `tests/unit/` は 120 秒以内を目標にする。
  - balanced target。現状 10 分からの改善を明確にしつつ、移行を段階化しやすい。
- Option C:
  - 今回の issue では秒数 target を固定せず、境界整理と top bottleneck 削減を成功条件にする。
  - safe target。過剰な test rewrite を避けやすいが、成功判定がやや曖昧になる。

## Codex の分析

- 判断軸:
  - 日常 feedback loop として何分なら許容できるか。
  - test migration の scope をこの issue でどこまで広げるか。
  - 速度 target を満たすために、既存 CLI black-box coverage をどれだけ lower-layer tests へ移すか。
- tradeoff:
  - 60 秒以内は開発体験として強いが、1 issue の差分が大きくなる可能性がある。
  - 120 秒以内は十分に速い一方、最終的な理想値へは follow-up が必要になる可能性がある。
  - 秒数 target なしは柔軟だが、実装後の「改善した」の客観判定が弱くなる。
- リスク:
  - 秒数 target が強すぎると、分類整理と速度改善を同時に深くやりすぎて diff が大きくなる。
  - 秒数 target が弱すぎると、重い CLI subprocess 反復が残る。
- 具体シナリオ / edge case:
  - CI や別 machine では wall clock が違うため、target は local measurement reference として扱い、CI では trend / relative improvement を見る必要がある可能性がある。

## Codex の推奨案

- 推奨:
  - Option B: `tests/unit/` は 120 秒以内を目標にする。
- 理由:
  - 現状 full run `10:00.07 total` から明確に改善できる。
  - `test_deps.py` / `test_validate.py` / `test_delegated_authoring.py` の top bottleneck を優先しても到達可能性があり、差分を過度に巨大化しにくい。
  - 将来 60 秒以内を目指す follow-up を切る余地を残せる。
- 未回答時の影響:
  - requirement の acceptance criteria を確定できない。
  - design / plan で軽量化の深さを安全に固定できない。

## ユーザー回答 (回答後に必須)

- 回答:
  - Option B を採用する。
  - `tests/unit/` の日常実行時間は、今回の issue の成功条件として 120 秒以内を目標に固定する。
- 回答日時:
  - 2026-06-05

## 追加確認の要否 (回答後に必須)

- 追加確認が必要か:
  - 不要
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 該当なし

## 採用判断 (回答後に必須)

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option B を明示採用したため、requirement / design / plan の runtime target と verification threshold に反映する。

## requirement / design / plan / ADR への含意 (回答後に必須)

- `requirement.md`:
  - Unit test runtime の AC に反映する。
- `design.md`:
  - runner / fixture / coverage migration の深さに反映する。
- `plan.md`:
  - final verification command と threshold に反映する。
- `ADR`:
  - ADR への反映は不要。ADR は分類と fixture strategy を固定済み。
- reflected_to 更新方針:
  - 回答後、canonical docs へ反映した時点で更新する。
