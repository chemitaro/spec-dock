---
種別: ADR（Architecture Decision Record）
ID: "20260617t003048z-adr"
タイトル: "Wait On Discussion Timestamp Collision"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
authority: "accepted"
derived_from:
  - "20260617t000227z-research"
  - "20260617t000333z-interview"
  - "20260617t002152z-disc"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260617t003048z-adr Wait On Discussion Timestamp Collision

## ADR 化基準
- hard to reverse:
  - medium
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR として残す理由:
  - Timestamp collision の通常時挙動を suffix-first から wait-first へ変える判断であり、artifact ordering / latency / fallback policy の tradeoff があるため。

## 結論（Decision）
- Discussion artifact generator は、同じ `discussions/` directory 内で生成予定 timestamp slot が既に使われている場合、suffix を即時付与する前に runtime 側で短く待機して timestamp を再取得する。
- 待機と retry は create lock の内側で行い、通常の連続生成では suffix なしの `<ts>-<kind>-<slug>.md` を優先する。
- Clock が進まない、bounded wait budget を超える、または retry 後も slot が衝突する場合は、既存の same-second suffix fallback (`<ts>-<nn>-<kind>-<slug>.md`) を使う。
- #188 では timestamp grammar を変更しない。`yyyymmddthhmmssz` と `01..99` suffix contract を維持する。

## 背景（Context）
- 現行 contract では `ts = yyyymmddthhmmssz` であり、同一秒に複数 artifact を作ると suffix が付く。
- Suffix fallback は衝突回避として正しいが、通常の連続生成で suffix が出ると、unsuffixed file と suffixed file の lexical ordering が実際の生成順とずれることがある。
- ユーザー判断として、suffix mechanism は安全装置として残しつつ、通常経路ではなるべく suffix を出さない runtime-owned sleep/retry を追加する方針が支持された。

## 選択肢（Options considered）
- Option A:
  - 概要:
    - 同秒衝突時に即時 suffix を割り当てる現行挙動を維持する。
  - Pros:
    - 追加 latency がない。
    - 実装変更が最小。
  - Cons:
    - 通常の連続生成でも suffix が出やすい。
    - Suffix 付き/なしの lexical ordering 問題が残る。
  - 棄却理由:
    - 通常経路で suffix を避けたいという要件を満たせないため棄却。
- Option B:
  - 概要:
    - Timestamp grammar に 10ms / 100ms などの sub-second digits を追加する。
  - Pros:
    - 待機時間を短くできる。
    - 連続生成でも suffix が出にくい。
  - Cons:
    - Parser / validator / docs / tests / existing naming contract に広く波及する。
    - 手作業 filename 経路をなくすことが先であり、#188 の最小解としては大きい。
  - 棄却理由:
    - #188 では採用しない。実測で wait latency が問題化した場合に別 issue / ADR で再検討する。
- Option C:
  - 概要:
    - Current grammar を維持し、同秒衝突時だけ runtime が次の timestamp slot まで待って retry し、最後に suffix fallback する。
  - Pros:
    - Naming grammar を安定させたまま通常経路の suffix を減らせる。
    - Existing parser / validator / docs との互換性を保てる。
    - Suffix fallback を安全装置として維持できる。
  - Cons:
    - 同一 scope に多数 artifact を連続生成すると、最大で artifact ごとに約 1 秒の待機が発生し得る。
    - Fake/frozen clock tests では bounded fallback を明確に扱う必要がある。
  - 棄却理由:
    - 採用。

## 判断理由（Rationale）
- #188 の root cause は manual filename generation だが、runtime generator 側も通常経路で suffix を避ける方が artifact ordering の直感に合う。
- Timestamp grammar を変えずに wait-first を導入することで、durable naming contract の変更を避けつつ、今回のユーザー要件に最小差分で応えられる。
- Suffix fallback を残すことで、non-advancing clock、parallel race、wait budget exhaustion でも fail-open ではなく既存 contract 内で安全に作成できる。

## 影響（Consequences）
- Positive（良い点）:
  - 通常の連続生成で suffix が出にくくなる。
  - Discussion artifact の lexical ordering と生成順が一致しやすくなる。
  - Existing second-precision filename contract を維持できる。
- Negative / Debt（悪い点 / 将来負債）:
  - Artifact を大量生成する workflow では待機時間が目立つ可能性がある。
  - Clock abstraction / test clock で retry と fallback を検証する必要がある。
- 影響範囲（コード/テスト/運用/データ）:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `spec-dock/docs/reference_naming.md`
  - `spec-dock/docs/workflow_adr.md`
- 移行/ロールバック:
  - Existing artifact files は rename しない。
  - Rollback は wait/retry を外して suffix-first に戻すだけで可能だが、ordering 改善要件は失われる。
- Follow-ups（追加の Epic/Issue/ADR）:
  - Wait latency が common workflow で問題化した場合は、centisecond timestamp grammar または batch allocator API を別 issue / ADR で検討する。

## 参考（References）
- 関連仕様（requirement/design/plan/report）:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- 元になった discussion docs:
  - `20260617t000227z-research-timestamp-collision-source-grounding.md`
  - `20260617t000333z-interview-scope-boundary-for-timestamp-collision-prevention.md`
  - `20260617t002152z-disc-artifact-filename-generation-strategy.md`
- PR/実装:
  - 未実装
