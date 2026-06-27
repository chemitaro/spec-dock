---
種別: discussion
ID: "20260627t114637z-disc"
タイトル: "guidance issue-execution execution model stability analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連:
  - "20260627t112517z-research"
authority: "synthesized"
derived_from:
  - "oracle: gpt-5.5-pro extended via chatgpt-use"
  - "local research: 20260627t112517z-research-guidance-step-selection-regression-analysis.md"
reflected_to: []
---

# guidance issue-execution execution model stability analysis

## 位置づけ
- この artifact は、`guidance issue-execution` が `selected_step: S01` に戻り続けた個別バグを超えて、そもそも「作業中に `report.md` を更新し、その Markdown から次の step を動的推定するモデル」が安定して有用かを検討した設計ディスカッションである。
- `chatgpt-use` skill により Oracle CLI browser mode で GPT-5.5 Pro Extended に分析を依頼し、その回答をローカル調査結果と統合した。
- この artifact は canonical requirement / design そのものではない。採用する場合は `requirement.md` / `design.md` / `plan.md` / `report.md` に反映する。

## 問題定義
- 現行の `guidance issue-execution` は、`plan.md` と `report.md` を読み、完了済み step を推定して次の operational guidance を stdout に返す。
- 今回、`report.md` 上では S01-S99 の完了証跡があるにもかかわらず、`./spec-dock/scripts/spec-dock guidance issue-execution` が `selected_step: S01` を返し続けた。
- この直接原因は parser が current report ledger 形式を読めないことだが、より大きな懸念は、作業中に人間向けの報告書を更新し続け、その可変 Markdown を機械制御の状態正本として扱う設計そのものが不安定ではないか、という点である。

## Oracle 分析の要旨
- GPT-5.5 Pro Extended の結論は、短期的には parser patch が必要だが、長期的な最善案は Hybrid である。
- Hybrid とは、機械制御用の明示的な step state / progress metadata を導入し、`report.md` は audit ledger / human-readable evidence として維持し、`guidance issue-execution` は両者の整合性を検証した上で operational guidance を返す設計である。
- `plan.md` / `report.md` の可変 Markdown だけを都度パースして「次 step」を自動選択する現在のモデルは、個別 parser bug を直しても、長期的な operational authority としては安定しない。
- ただし `iss-00241` の近傍では大規模 rewrite は不要であり、現行 parser を current report ledger に合わせて直し、全 step 完了時に S01 へ戻らない明示状態を返すのが妥当である。

## 選択肢比較

| 選択肢 | 評価 | 採否 |
| --- | --- | --- |
| Markdown parser を current report ledger に合わせて修正する | 即効性があり、今回の `selected_step: S01` 症状は止められる。ただし Markdown から workflow state を復元する根本的な脆さは残る。 | 短期採用 |
| 明示的な machine-readable step progress metadata を導入する | 機械判断が安定する。schema、validation、既存 report との整合性検査が必要。 | 中期採用 |
| auto-select をやめ、issue-wide checklist だけ返す | 堅牢性は高いが、dynamic resource allocation や step-specific context routing の価値を大きく削る。 | fallback として採用 |
| Hybrid: metadata + report audit + consistency validation | operational value と信頼性のバランスが最も良い。stdout guidance の目的も維持できる。 | 推奨 |

## 推奨する責務分担
- `plan.md`: planned executable contract。step order、step scope、required gates の正本。
- `report.md`: observed evidence / audit ledger。実施結果、reviewer gate、commit gate、例外判断の人間向け証跡。
- progress metadata: machine workflow state。step ごとの state、closed evidence ref、plan hash / report hash などを保持する機械制御用の状態。
- `guidance` stdout: current operational projection。agent がその場で読むべき次アクションと stop condition。
- generated runbook projection: human-readable projection。agent handoff authority ではなく、人間が状況を俯瞰するための副産物。

## `iss-00241` で行うべき短期修正
- provider source と dogfooding mirror の `context_packets.py` drift を解消する。
- `_completed_step_ids()` を global ledger aware にし、`### セッションログ` block だけでなく、`Step Contract Closure` / `Reviewer Gate Status` / `Step Commit Gate` を report 全体から読めるようにする。
- step 完了判定は少なくとも Step Contract Closure、Reviewer Gate Status、Step Commit Gate の conjunction とする。
- 全 selectable step が完了している場合は `S01` に戻さず、`all_steps_completed` や `issue_completion_gates_required` に相当する明示状態を返す。
- parser confidence / state sources / warnings を返し、confidence が低い場合は step を推測せず、issue-wide obligations と checklist guidance に落とす。
- stdout guidance は agent handoff authority として必要情報を持たせ、generated runbook projection を読み直す運用へ戻さない。

## 中期的に導入するべき metadata のイメージ

```json
{
  "schema_version": "issue-execution-progress-v1",
  "issue_id": "iss-00241",
  "plan_sha256": "...",
  "report_sha256": "...",
  "steps": {
    "S01": {
      "state": "closed",
      "closure": "passed",
      "reviewer_gate": "passed",
      "commit_gate": "committed",
      "commit": "<sha-or-approved-no-op-ref>",
      "report_refs": [
        "Step Contract Closure:S01",
        "Reviewer Gate Status:S01",
        "Step Commit Gate:S01"
      ]
    }
  },
  "current_step": null,
  "next_action": "issue-completion-gates"
}
```

## failure modes
- Markdown 節名の揺れで completed step を取りこぼし、S01 に戻る。
- 古い session log の failed と新しい global ledger の passed の precedence を誤る。
- Reviewer Gate が unavailable / provisional / failed なのに passed と誤判定する。
- Step Contract Closure だけで次 step に進み、commit gate 未完了を見逃す。
- `approved-no-op` を軽く扱いすぎて、必要な review / no-diff evidence なしに step を閉じる。
- `plan.md` が amendment された後、古い report evidence で新 plan step を閉じたと誤判定する。
- provider source と dogfooding mirror の drift により、install 後と dogfooding workspace で guidance が違う。
- all completed と no structured plan を同じ `issue_wide_default` に潰し、完了後状態と plan 不備を区別できない。

## 追加すべき検証
- global `Step Contract Closure` / `Reviewer Gate Status` / `Step Commit Gate` に S01 完了がある場合、S02 を選ぶ。
- S01-S99 すべてが完了 / committed の場合、S01 に戻らず all steps completed state を返す。
- Step Contract Closure は pass だが Reviewer Gate が failed / unavailable / provisional の場合、その step は未完了または blocked として扱う。
- Reviewer Gate は passed だが Commit Gate が missing / blocked / provisional の場合、その step は未完了または blocked として扱う。
- session log と global ledger が矛盾する場合、無理に auto-select せず ambiguous / blocked guidance を返す。
- provider source と dogfooding mirror の behavior が一致する。

## 判断
- `iss-00241` では Option 1 を短期修正として実施しつつ、設計判断としては Option 4 Hybrid を採用するのが最も安全である。
- ただし Hybrid の metadata 導入は `iss-00241` で全量実装する必要はない。`iss-00241` の目的は、現 PR を merge 可能にするための取りこぼし修正と、現行 guidance の誤誘導を止めることである。
- 中期 metadata 導入は別 Issue として扱うのが妥当である。理由は、schema、migration、既存 report との reconciliation、command update path の設計が必要であり、現在の corrective issue に含めると blast radius が大きくなるためである。

## 反映候補
- `spec-dock/active/issue/requirement.md`
  - all steps completed state と parser confidence / ambiguous guidance の要件追加。
- `spec-dock/active/issue/design.md`
  - Markdown parser は best-effort projection であり、将来の machine-readable progress metadata を前提にした責務分担の記録。
- `spec-dock/active/issue/plan.md`
  - short-term parser repair と all completed regression tests の step 追加または既存 step への補強。
- `spec-dock/active/issue/report.md`
  - Decision / Evidence Adoption Ledger への採用判断記録。

## Oracle session
- tool: `npx -y @steipete/oracle --engine browser`
- project: Codex-only ChatGPT Project
- model: `gpt-5.5-pro`
- thinking time: `extended`
- session: `spec-dock-guidance-execution-model`
- dry run token estimate: about 51.4k prompt tokens, 10 bundled files
- result: completed successfully
