---
種別: ADR（Architecture Decision Record）
ID: "016-adr-issue-plan-tdd-structure"
タイトル: "issue plan における TDD 構造契約"
状態: "accepted"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00021"]
---

# 016-adr issue plan における TDD 構造契約

## 結論（Decision） (必須)
- issue plan では `step = 1 observable behavior` を invariant とする。
- `block` は optional concern group とする。
- `iteration` は 1 回の完全な TDD cycle とする。
- `Red / Green / Refactor` は iteration の内部 phase とする。
- failing test は iteration ごとに 1 本を基本とする。
- review / QA / docs impact / final diff review は iteration の外に置き、step / milestone / `S90` / `S99` で扱う。
- cadence policy の正本は `workflow_issue.md` に置き、`phase_plan_issue.md` はその policy を `plan.md` にどう埋め込むかの正本とする。

## 背景（Context） (必須)
- issue plan は execution contract であり、単なる作業リストではなく、どの粒度で Red / Green / Refactor と review gate を切るかまで扱う必要がある。
- 一方で、TDD の思想そのものと実行 cadence まで template に書き込むと、template と workflow の責務が重なる。
- nested structure を使って TDD を plan に埋め込みつつ、policy の正本は workflow に残す分離が必要だった。
- 本 ADR は一時検討資料 `011 / 012 / 013 / 014` の結論を統合した恒久判断である。

## 選択肢（Options considered） (必須)
- Option A:
  - 概要:
    - `block = 1 tdd slice`、`iteration = Red / Green / Refactor` として、TDD の各 phase を iteration に割り当てる。
  - Pros:
    - 直感的に見える。
    - phase ごとの進行を強調しやすい。
  - Cons:
    - iteration が細かくなりすぎる。
    - review / docs / QA との境界が曖昧になりやすい。
    - `block` に必須意味を持たせると柔軟性が落ちる。
  - 棄却理由（棄却する場合）:
    - 実運用では粒度が細かすぎ、plan と execution policy の境界も崩れやすい。
- Option B:
  - 概要:
    - `block = optional concern group`、`iteration = 1 TDD cycle` とし、Red / Green / Refactor は内部 phase にとどめる。
  - Pros:
    - `step` と `iteration` の責務が自然に分かれる。
    - review / QA / docs / final diff を iteration 外へ分離しやすい。
    - 実案件ごとの plan で柔軟に block を省略できる。
  - Cons:
    - TDD の phase が plan 上では一段抽象化される。
    - 慣れない読者には block の optional 性を補足したくなる。
  - 棄却理由（棄却する場合）:
    - 採用。

## 判断理由（Rationale） (必須)
- issue plan で固定したいのは「TDD をどう構造化して plan に落とすか」であり、Red / Green / Refactor の教義説明ではない。
- `iteration = 1 TDD cycle` にすると、観測可能な振る舞いを表す `step` と、最小の検証ループである `iteration` の役割がきれいに分かれる。
- review / QA / docs / final diff を iteration の外へ出すことで、micro TDD cycle と quality gate を混線させずに運用できる。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - issue plan が TDD を構造として表現できる。
  - `workflow_issue.md` と `phase_plan_issue.md` の ownership が明確になる。
  - review / QA / docs / final diff の配置が一貫する。
- Negative / Debt（悪い点 / 将来負債）:
  - 実案件で iteration 粒度を守らないと形骸化しやすい。
  - block の optional 運用は reviewer 側の理解が必要。
- 影響範囲（コード/テスト/運用/データ）:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- 移行/ロールバック:
  - nested semantics を再変更する場合は、この ADR を supersede する新 ADR で扱う。
- Follow-ups（追加の Epic/Issue/ADR）:
  - issue plan 運用で nested semantics に混乱が出た場合は follow-up issue で補助例を追加検討する。

## 参考（References） (任意)
- 関連仕様（requirement/design/plan/report）:
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
- PR/実装:
  - `#22`
- 外部資料:
  - `013-disc-issue-plan-tdd-embedding-best-practice.md`
  - `014-disc-issue-plan-tdd-production-change-proposal.md`
  - `011-disc-scope-specific-plan-playbook-drafts.md`
  - `012-disc-plan-playbook-responsibility-redistribution.md`
