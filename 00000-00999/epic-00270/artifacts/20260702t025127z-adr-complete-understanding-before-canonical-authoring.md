---
種別: ADR（Architecture Decision Record）
ID: "20260702t025127z-adr"
タイトル: "Complete Understanding Before Canonical Authoring"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-02"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from:
  - "artifacts/20260702t024032z-interview-phase3-artifact-adoption-requiredness.md"
reflected_to:
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260702t025127z-adr Complete Understanding Before Canonical Authoring

## ADR 化基準
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `interview` / `design.md` / `plan.md` / `report.md`
- ADR として残す理由:
  - この判断は単一 template の文言ではなく、SpecDock の clarification / authoring / review / handoff 全体に効く作業原則である。
  - 「ユーザーに大量質問して確認する」方向にも「エージェントが曖昧なまま勝手に決める」方向にも倒れやすいため、後続エージェントが参照できる accepted ADR として固定する。

## 結論（Decision）
- Requirement / design / plan の canonical authoring に入る前に、エージェントは source-grounded な完全理解を構築しなければならない。
- 完全理解はチャットコンテキスト内の記憶だけに置かず、scope-local `artifacts/`、accepted ADR、canonical docs、`report.md` Evidence Adoption Ledger / Spec Authoring Gate に外部化する。
- エージェントは、コードベース、既存 docs、tests、templates、workflow、git history、提供済み planning pack、既存 artifacts / ADR から分かることを自分で調査する。
- ユーザーへ質問するのは、完全理解を達成するために必要で、かつ local / source-grounded investigation では判断できない user intent / product decision / tradeoff だけに限る。
- 重要な質問は `interview` artifact として作成し、回答後は同じ artifact に採用判断を記録し、必要に応じて ADR へ格上げする。
- Raw artifact は canonical authority ではない。採用された知識は canonical docs、accepted ADR、または `report.md` EAL / Spec Authoring Gate へ反映して初めて authoring / implementation の根拠になる。

## 背景（Context）
- V3 planning pack は discovery artifacts、reference flow、scope layering、Issue slicing、authoring gates を重視している。
- 一方で、artifact が増えすぎると適切な情報にたどり着けず、逆に artifact を作らないと判断根拠がチャットコンテキストに埋もれる。
- ユーザーは、曖昧な情報で requirement / design / plan を作ることを避けたい一方、すべてを人間に質問する運用も避けたいと明示した。
- この Epic では SpecDock 自身を dogfooding しており、clarification workflow の良し悪しがそのまま将来の SpecDock 利用体験に反映される。

## 選択肢（Options considered）
- 選択肢 A: 軽量採用
  - 概要:
    - 重要な decisions だけ EAL / ADR 化し、通常の調査や疑問はチャット上で処理する。
  - 良い点:
    - 運用が軽い。
    - ファイル数を抑えられる。
  - 悪い点 / 制約:
    - 後続エージェントが判断根拠を復元しにくい。
    - context loss に弱い。
  - 棄却理由:
    - この Epic では「判断の余地やブレを残さない」ことが求められており、軽すぎる。
- 選択肢 B: ユーザー質問中心
  - 概要:
    - 不明点を広くユーザーに聞き、回答をもとに docs を作る。
  - 良い点:
    - user intent の取り違えは減る。
  - 悪い点 / 制約:
    - ユーザーの認知負荷と時間消費が大きい。
    - コードや既存 docs から分かる事実まで人間に聞いてしまう。
  - 棄却理由:
    - ユーザーは「自分で調査できることは自分でやる」ことを明示した。
- 選択肢 C: 完全理解 + 自力調査 + 必要最小限のインタビュー + 知識外部化
  - 概要:
    - エージェントがまず source-grounded investigation を行い、理解を artifacts に残し、残った user-intent gap だけを一問ずつ質問する。
  - 良い点:
    - 完全理解とユーザー負荷軽減を両立できる。
    - context loss や後続エージェントへの handoff に強い。
    - Raw evidence と canonical authority の境界を保ちやすい。
  - 悪い点 / 制約:
    - 調査・記録の初期コストは増える。
    - 何でも artifact 化すると発見性が落ちるため、artifact type と adoption target の整理が必要。
  - 採用理由:
    - ユーザーの明示決定と V3 planning pack の authority model に最も合う。

## 判断理由（Rationale）
- Requirement / design / plan は、曖昧さを残したまま作ると downstream Issue planning / implementation で再解釈が発生する。
- AI agent は context window や会話履歴に依存しがちだが、SpecDock の目的はその判断根拠を durable artifact として残すことである。
- 人間への質問は価値が高い一方、乱発すると product owner の認知負荷が高まり、機械的に調査できる事実確認に人間の時間を使ってしまう。
- そのため、clarification は「質問すること」ではなく「完全理解に足りないピースを、最も低負荷で揃えること」と定義する。

## 影響（Consequences）
- 良い影響:
  - 後続エージェントが artifacts / ADR / report ledger を読めば、なぜその requirement / design / plan になったかを復元できる。
  - ユーザーインタビューは、source-grounded に解けない product decision に集中できる。
  - Spec Authoring Gate が、調査済み事実、未確定事項、回答、採用判断を確認する場として機能する。
- 悪い影響 / 将来負債:
  - 調査 artifact や ADR が増えすぎると、参照先の探索コストが増える。
  - 完全理解という言葉を過剰に解釈すると、軽微な変更まで過剰な調査になる。
- 影響範囲:
  - `spec-dock-clarification` workflow
  - Initiative / Epic authoring templates
  - Evidence Adoption Ledger / Spec Authoring Gate
  - planning skills and reviewer gates
- 移行/ロールバック:
  - この ADR は planning / authoring policy であり、runtime migration は不要。
  - 将来、運用が重すぎると判明した場合は、artifact 必須範囲を `report.md` / workflow docs で再調整し、必要なら新ADRで上書きする。
- 追加対応:
  - Matt Pocock 氏の "Grill With Docs" 調査を research artifact に保存し、この ADR の実践例として必要な範囲を今後の `design.md` / `plan.md` へ反映する。

## 参考（References）
- 関連仕様:
  - `epic-00270/design.md`
  - `epic-00270/plan.md`
  - `epic-00270/report.md`
- 元になった artifacts:
  - `artifacts/20260702t024032z-interview-phase3-artifact-adoption-requiredness.md`
- 関連 ADR:
  - `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`
