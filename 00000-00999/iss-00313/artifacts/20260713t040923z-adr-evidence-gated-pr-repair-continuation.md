---
種別: ADR（Architecture Decision Record）
ID: "20260713t040923z-adr"
タイトル: "PR修復継続を固定回数から証拠駆動判定へ変更する"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-13"
accepted_by: "product owner execution request + fresh spec-reviewer"
mirror_eligible: true
derived_from:
  - "artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md"
  - "requirement.md"
  - "design.md"
  - "plan.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260713t040923z-adr PR修復継続を固定回数から証拠駆動判定へ変更する

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由: PR修復の停止権限、外部相談の必須境界、例外時の人間承認を長期運用契約として固定する判断であり、誤ると無限反復または早すぎる停止を招くため。

## 結論（Decision）

`github-pr-merge-preparer` の blocking repair は、固定試行回数ではなく証拠駆動で継続を判定する。

- P0 1回、同一 failure family 2回、合計4回という固定上限と、同一 family 再発だけを理由とする自動停止を廃止する。
- 現在の blocking findings を単一の integrated repair batch に統合し、分析、戦略、実行結果、検証、再観測を追記可能な形で保持する。
- branch を変更する blocking repair の委任前に、fresh な ChatGPT consultation evidence を必須とする。ChatGPT の出力は advisory evidence であり、採否と最終判断は orchestrator が所有する。
- semantic continuation は、fresh evidence、未解消 hard stop がないこと、前回から material strategy delta があること、対象テスト・検証・再観測を実施できることをすべて満たす場合だけ許可する。
- 同一 failure family の再発は自動停止ではなく再分析の契機とする。試行回数と iteration は telemetry として記録するが、継続または停止の authority にしない。
- stale consultation は先に refresh を試みる。consultation と定義済み recovery が hard-unrecoverable の場合だけ、ユーザーが明示承認した one-invocation、local-only fallback を許可し、承認範囲、理由、失効条件を記録する。これは consultation 成功として扱わず、承認がなければ停止する。
- P2/P3 no-mutation、security/privacy、GitHub mutation、reviewer、CI、mergeability の既存 hard gate は維持する。
- legacy repair-batch は移行せず append-compatible とし、新しい欄がないことだけで invalid にしない。

## 背景（Context）

現行契約は回数上限に達すると、fresh evidence や新しい修復戦略が残っていても停止する。一方、単純に上限を外すだけでは、同じ失敗への無限反復や相談結果の無批判な採用を招く。

本 Issue は PR 修復の継続権限を、回数から観測可能な進捗と安全ゲートへ移す。同時に、外部相談を一次判断にせず advisory evidence として扱い、例外経路を明示的な人間承認に限定する必要がある。

## 選択肢（Options considered）

### 選択肢 A: 固定上限を維持または増加する

- Pros: 停止条件が単純で、無限反復を機械的に防げる。
- Cons: 有効な新戦略があっても任意の回数で停止し、failure complexity と停止判断が一致しない。
- 棄却理由: Issue の主要目的である、進捗に基づく継続判定を満たさない。

### 選択肢 B: 固定上限だけを撤廃する

- Pros: 回数による早すぎる停止はなくなる。
- Cons: material strategy delta、fresh evidence、consultation、human gate がなく、無限反復と権限の曖昧化を防げない。
- 棄却理由: 安全性と監査可能性が不足する。

### 選択肢 C: 証拠駆動の semantic continuation を採用する

- Pros: failure complexity に応じて継続でき、反復ごとの根拠、戦略差分、検証結果を監査できる。既存 hard gate を維持できる。
- Cons: integrated batch と consultation evidence の記録負担が増え、相談経路障害時は人間判断が必要になる。
- 採用理由: 早すぎる停止と無限反復の両方を、回数ではなく明示的な証拠契約で制御できる。

## 判断理由（Rationale）

回数は進捗の代理指標にすぎず、修復継続の十分条件にも停止の十分条件にもならない。fresh evidence、material strategy delta、validation、再観測を結び付けることで、各反復が前回と異なる妥当な試行であることを確認できる。ChatGPT consultation を advisory evidence と位置付け、orchestrator disposition と人間承認 fallback を分離することで、外部モデルへ authority を移さない。

## 影響（Consequences）

- 良い影響:
  - 固定上限による早すぎる停止を防ぎ、修復継続の理由を監査できる。
  - 同一 failure family 再発時も、戦略差分があれば安全に続行できる。
  - consultation 障害時の例外が一回限りかつ明示承認となる。
- 悪い影響 / 将来負債:
  - batch 記録と consultation freshness の管理が増える。
  - semantic delta の判定には orchestrator の判断が残る。
- 影響範囲:
  - provider-side skill、agent metadata、repair-batch templates、生成 mirror、契約テスト。
  - runtime CLI、schema、GitHub mutation、既存 batch の migration は変更しない。
- 移行 / ロールバック:
  - provider-first で更新し `spec-dock update .` により mirror を同期する。
  - rollback は provider と生成 mirror の変更を一括で戻す。既存 batch の移行やデータ変換は不要。
- 追加対応:
  - 3つ以上の無関係な skill へ同じポリシーを展開する場合は、cross-skill ADR または Epic を別途起票する。

## 参考（References）

- `requirement.md`
- `design.md`
- `plan.md`
- `report.md`
- `artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md`
