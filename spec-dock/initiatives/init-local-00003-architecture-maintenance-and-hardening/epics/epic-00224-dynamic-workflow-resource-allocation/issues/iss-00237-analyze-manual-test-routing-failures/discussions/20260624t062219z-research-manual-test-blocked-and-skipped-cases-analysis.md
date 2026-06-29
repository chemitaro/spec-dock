---
種別: research
ID: "20260624t062219z-research"
タイトル: "Manual Test Blocked And Skipped Cases Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-003", "MT-004", "MT-015"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md"
  - "deep-consultant:019ef84b-8b67-7290-9305-5c012566c4d2"
reflected_to: []
---

# 20260624t062219z-research Manual Test Blocked And Skipped Cases Analysis

## 調査目的
- FAIL 以外の MT-003 BLOCKED、MT-015 SKIPPED、および MT-004 で見えた GitHub scope / post-mutation sync の運用課題を、iss-00237 の routing 修正本体に含めるべきか判断する。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
  - deep-consultant analysis `019ef84b-8b67-7290-9305-5c012566c4d2`
- 検証手順:
  - 手動テストログと consultant の分類を照合した。
  - product fix / docs note / follow-up test / accepted behavior に分類した。

## facts / 観測できた事実
- MT-003:
  - fresh initialized empty workspace の `validate` は `No nodes found.` で exit 1。
  - non-empty tree 作成後は `validate` が `nodes=5` で成功。
- MT-004:
  - `--github-issue` は GitHub issue を作らないが、canonical GitHub repo scope と post-mutation GitHub read が必要だった。
  - no-origin では canonical GitHub repo scope を解決できず停止した。
  - fake origin + fake `gh` では linked node creation と auto-sync が成功した。
- MT-015:
  - symlink abuse は未実施。
  - skipped 理由は、routing defect 発見後に同じ trial repo へ破壊的ノイズを増やさないため。

## consultant synthesis
- deep-consultant の結論:
  - MT-003 は accepted behavior + docs/test-plan note。product fix 不要。
  - MT-015 は follow-up test。現時点で product bug とは断定しない。
  - MT-004 は runtime behavior としては accepted。ただし docs/operator note は修正対象。
- 採用判断:
  - 3件とも iss-00237 の routing修正本体には混ぜない。
  - ただし MT-004 の docs 矛盾は別 docs cleanup issue、MT-015 は別 retest issue として候補化する。

## classification

| 対象 | 判断 | 推奨対応 | iss-00237 に含めるか |
|---|---|---|---|
| MT-003 empty workspace validate | accepted behavior + test-plan note | `validate` baseline は node 作成後に置く | 含めない |
| MT-004 `--github-issue` repo scope / post-sync read | accepted runtime behavior + docs gap | docs/operator note を更新する follow-up | 含めない |
| MT-015 symlink abuse skipped | follow-up test | fresh trial repo で symlink abuse retest | 含めない |

## risks
- MT-003 を product fix として空 tree success に変えると、wrong cwd や node 未作成を見逃すリスクが上がる。
- MT-004 の docs が「gh を呼ばない」と説明している場合、operator が local node 作成済み + auto-sync failed state を誤解しやすい。
- MT-015 は security boundary なので未実施のまま confidence を高く見積もるべきではない。

## implications / 判断への含意
- iss-00237 の修正設計は runtime routing failure に集中する。
- follow-up candidate:
  - docs cleanup: `--github-issue` は remote create しないが repo scope と post-mutation GitHub read は必要、と明記する。
  - symlink retest: fresh trial repo で planning artifact / runbook / context packet / assurance contract symlink を確認する。
