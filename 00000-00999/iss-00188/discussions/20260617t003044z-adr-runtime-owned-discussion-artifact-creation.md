---
種別: ADR（Architecture Decision Record）
ID: "20260617t003044z-adr"
タイトル: "Runtime Owned Discussion Artifact Creation"
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

# 20260617t003044z-adr Runtime Owned Discussion Artifact Creation

## ADR 化基準
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR として残す理由:
  - Shipped skills / workflows の artifact 作成境界を変える判断であり、将来の skill authoring と runtime command design の前提になるため。

## 結論（Decision）
- Shipped SpecDock skills / workflows は、new discussion artifact の filename を手作業で組み立ててはならない。
- `discussions/` 配下の artifact filename allocation と file creation は、SpecDock runtime/script-owned generator が担う。
- Skill / workflow は `doc type`、scope、title/slug、template/body、metadata などの semantic input を渡し、生成された path / doc_id を runtime の戻り値から受け取る。
- PR branch、PR number、unit id、covered ids、source batch path などの workflow metadata は、filename ではなく generated artifact の front matter または本文 metadata に記録する。
- Existing files は自動 rename しない。新規 artifact generation の contract として適用する。

## 背景（Context）
- GitHub issue #188 の直接の症状は、同一 `discussions/` 配下に同じ timestamp slot の discussion docs が複数作られ、validation が `Duplicate discussion timestamp slot detected` で fail することだった。
- Runtime `new doc` path には create lock、suffix allocator、duplicate guard が存在する一方、`github-pr-merge-preparer` などの skill guidance は `<ts>-disc-pr-repair-batch.md` / `<ts>-disc-pr-repair-unit-...md` のような target filename を agent が手で組み立てるよう読める。
- ユーザー判断として、root problem は timestamp の桁数ではなく「skill が filename を手作業で作る経路があること」と確定した。

## 選択肢（Options considered）
- Option A:
  - 概要:
    - Shipped skills / workflows が filename を手作業で組み立て続け、衝突時だけ suffix / retry を運用で回避する。
  - Pros:
    - Runtime command surface の変更が少ない。
    - 既存 skill 記述との差分が小さい。
  - Cons:
    - 同じ失敗を別 skill / 別 workflow で再発させやすい。
    - Agent が timestamp / suffix / sorting の仕様を再実装することになる。
    - `new doc` runtime 側の lock / guard を迂回してしまう。
  - 棄却理由:
    - 根本原因を残すため棄却。
- Option B:
  - 概要:
    - Runtime/script が discussion artifact の filename allocation と file creation を担い、skills / workflows は semantic input と returned path だけを扱う。
  - Pros:
    - Timestamp allocation policy を一箇所に閉じ込められる。
    - `new doc` の lock / validation / guard を活かせる。
    - Skill guidance が単純になり、agent ごとの手作業 timestamp 実装を避けられる。
  - Cons:
    - Runtime command/API shape と shipped skill guidance の更新が必要。
    - Template/body 反映時に front matter / doc_id を壊さない contract が必要。
  - 棄却理由:
    - 採用。

## 判断理由（Rationale）
- Artifact filename は identity / ordering / validation に関わる contract であり、skill ごとの手作業生成に分散させるべきではない。
- Runtime/script に generator を集約すると、timestamp collision、suffix fallback、future timestamp policy change を一箇所で扱える。
- Workflow metadata を filename に埋め込むと naming contract が膨らむため、PR branch などは artifact content 側へ移す方が保守しやすい。

## 影響（Consequences）
- Positive（良い点）:
  - Shipped skills が duplicate timestamp slot を作る経路を減らせる。
  - Agent-facing guidance が command-first / returned-path-first になる。
  - Future generator improvements を runtime 側だけで進めやすくなる。
- Negative / Debt（悪い点 / 将来負債）:
  - Skill-local template/body を generated artifact に反映する最小 contract が必要。
  - Existing manual filename examples を repo 全体から洗い出す必要がある。
- 影響範囲（コード/テスト/運用/データ）:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/install_root/.agents/skills/**`
  - `spec-dock/docs/reference_naming.md`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - asset regression tests for shipped guidance
- 移行/ロールバック:
  - Existing artifact files は rename しない。
  - Rollback は shipped skills を manual filename guidance に戻すことになるため、#188 の目的に反する。
- Follow-ups（追加の Epic/Issue/ADR）:
  - Large batch artifact creation が必要になった場合だけ、batch allocator API を別 issue で検討する。

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
