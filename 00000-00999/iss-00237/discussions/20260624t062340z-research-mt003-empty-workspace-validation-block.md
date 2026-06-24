---
種別: research
ID: "20260624t062340z-research"
タイトル: "MT003 Empty Workspace Validation Block"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
親: ["iss-00237"]
関連: ["MT-003", "validate"]
authority: "synthesized"
derived_from:
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md"
  - "manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md"
reflected_to: []
---

# 20260624t062340z-research MT003 Empty Workspace Validation Block

## 調査目的
- MT-003 の `No nodes found.` が product defect、test precondition error、documentation note のどれに該当するかを判断する。

## sources / 調査方法
- 参照先:
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/execution-log.md`
  - `manual-tests/epic-00224-dynamic-workflow-resource-allocation/summary-report.md`
- 検証手順:
  - `spec-dock init` 直後の `validate` 結果と、node 作成後の `validate` 結果を比較した。

## facts / 観測できた事実
- `spec-dock init` / `update` は成功した。
- empty initialized workspace で `./spec-dock/scripts/spec-dock validate` を実行すると `error: No nodes found.` で exit 1。
- MT-004 で initiative / epic / issues を作成した後、`validate` は `spec-dock: ok (validate) nodes=5` で成功した。

## inference / 推測
- `validate` は「SpecDock tree が存在し、node consistency を検証する」command であり、empty workspace を valid とみなさない設計の可能性が高い。
- MT-003 の期待値「fresh init 直後に validate exits 0」はテスト計画側の前提が早すぎた。
- product code fix より、manual test plan / operator docs に「empty workspace validate は baseline ではない」と明記するのが妥当。

## unverified / 未検証事項
- `validate` が empty workspace を invalid と扱うことが canonical docs に明記済みか。
- `doctor` など別 command で init/update scaffold validity を確認する導線があるか。

## options
- Option A: 受け入れ済み挙動として扱い、manual test plan を node 作成後 validation に修正する。
  - 長所: 実装変更不要。今回の主問題から scope を広げない。
  - 短所: fresh init の scaffold health を単独で検証する command は別途必要かもしれない。
- Option B: `validate --allow-empty` のような option を追加する。
  - 長所: init/update smoke と tree validation を分けられる。
  - 短所: Epic 00224 の routing defect scope から外れる。
- Option C: empty workspace を validate success に変える。
  - 長所: fresh init の手動テストは簡単になる。
  - 短所: `validate` の意味が弱まり、node missing を見逃しやすくなる。

## recommendation
- iss-00237 の修正 scope には含めない。
- manual test plan / summary では MT-003 を `BLOCKED: test precondition too early` と扱う。
- 必要なら follow-up として `validate` と `doctor` の責務整理 issue を作る。

## implications / 判断への含意
- routing 修正の release blocker ではない。
- Epic 00224 merge 判定では「node 作成後 validate 成功」を baseline evidence とする。
