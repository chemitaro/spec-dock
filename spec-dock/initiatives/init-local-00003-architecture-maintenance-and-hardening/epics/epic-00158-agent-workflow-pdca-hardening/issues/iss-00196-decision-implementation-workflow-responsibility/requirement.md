---
種別: 要件定義書（Issue）
ID: "iss-00196"
タイトル: "Document Decision Implementation Layer Responsibilities"
関連GitHub: ["#196"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["epic-00158", "init-local-00003"]
---

# iss-00196 Document Decision Implementation Layer Responsibilities — 要件定義（何を、なぜ行うか）

## 目的
- SpecDock の workflow において、意思決定をどの階層（Initiative / Epic / Issue）で扱い、どの階層で実装へ進めるべきかを明文化する。
- Issue が実装可能な最小単位であることを保ちつつ、Issue が実装前の意思決定だけを抱えている場合に、上位 scope へ戻す判断基準を提供する。
- agent-facing context surface を、薄い workflow skills、薄い final-artifact templates、詳細な説明と具体例を置く docs に分離する。

## 背景・現状
- 現状の挙動:
  - `workflow_issue.md` は Issue を「implementation minimum unit」と定義し、`workflow_epic.md` は Epic を cross-issue design backbone として扱っている。
  - しかし、Issue planning / clarification の入口では、Issue が「実装単位」なのか「意思決定だけの箱」なのかを早期判定する明示的な contract が不足している。
  - 既存テンプレートは scaffold として機能する一方、どの程度の authoring guidance や例を残すべきかが明文化されていない。
- 現状の課題:
  - architecture boundary、ownership、workflow policy のような判断を、実装 Issue として先に分解すると、Issue が実装可能な作業単位ではなく意思決定の仮置き場になりやすい。
  - テンプレートや skill に詳細説明や具体例を厚く入れると、作成済みの requirement / design / plan を読む後続 implementation agent にとって instructional noise になる。
  - 逆に docs 側に判断基準や例が不足すると、authoring agent が decision-only Issue を見逃し、Issue / Epic / Initiative の責務境界を誤りやすい。
- 観測点:
  - Docs:
    - `workflow_issue.md`, `workflow_epic.md`, `workflow_initiative.md`, `workflow_spec_authoring.md`
  - Skills:
    - `.agents/skills/spec-dock-issue-planning/SKILL.md`
    - `.agents/skills/spec-dock-epic-planning/SKILL.md`
    - `.agents/skills/spec-dock-clarification/SKILL.md`
  - Templates:
    - `src/spec_dock/assets/spec_dock/templates/`
    - generated dogfooding mirror under `spec-dock/templates/`
- 情報源:
  - GitHub issue `#196`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/issue/discussions/20260617t154620z-research-decision-implementation-layer-source-grounding.md`
  - `spec-dock/active/issue/discussions/20260617t154625z-interview-decision-boundary-primary-intent.md`
  - `spec-dock/active/issue/discussions/20260618t000451z-disc-deep-consultant-decision-scope-synthesis.md`
  - `spec-dock/active/issue/discussions/20260618t000833z-interview-decision-boundary-example-policy.md`
  - `spec-dock/active/issue/discussions/20260618t003437z-disc-deep-consultant-clean-template-revision.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - SpecDock maintainer
  - SpecDock の spec authoring / clarification / planning を担当する agent
  - 完成した requirement / design / plan を読んで実装する downstream implementation agent
- 代表シナリオ:
  - Issue start 後、Issue 本文が実装作業ではなく architecture / workflow policy / ownership decision を要求していることを検出し、Epic / Initiative へ戻す。
  - Epic authoring 中、複数 Issue にまたがる設計判断を Epic requirement / design に保持し、Issue には実装可能な slice だけを落とす。
  - Requirement / design / plan templates から作成された完成 artifact が、例や説明文を残さず、後続 agent に必要な実仕様だけを渡す。

## スコープ
- 必須:
  - Workflow docs に、Initiative / Epic / Issue の decision responsibility と implementation responsibility の境界を明記する。
  - Issue planning / clarification skill に、decision-only Issue を早期検出し、適切な上位 scope へ戻す thin gate を追加する。
  - Skill は workflow routing、stop condition、参照先 docs の案内に留め、詳細な概念説明や長い具体例を skill body に抱え込まない。
  - Templates は final artifact scaffold として薄く保ち、完成後に残って意味がある最小フィールド、短い問い、readiness checklist だけを持つ。
  - 具体例、good / bad pattern、decision routing の説明は docs / authoring guidance に置く。
  - Docs の具体例は reusable / generic な例にし、dogfooding 固有の product name や architecture name を shipped reusable templates に入れない。
  - この Issue の `report.md` に、dogfooding で発見された failure mode と意思決定の採用証跡を残す。
- 禁止:
  - Templates に `例:` やサンプル prose を残し、完成した spec artifact に instructional noise が混入する状態にすること。
  - Templates または shipped reusable docs に、今回の dogfooding 固有名を汎用規約として埋め込むこと。
  - Skill body を tutorial 化し、docs と重複する長い説明や多数の例を保持すること。
  - Templates を policy authority として扱うこと。Policy authority は workflow docs、accepted ADR、reviewer gates、runtime contract に置く。
- 対象外:
  - Runtime CLI による decision routing の強制 enforcement。
  - Strict schema enforcement、GitHub bot、ADR registry、automated harness / eval の実装。
  - 既存 spec 全体の広範な migration。
  - dogfooding で発見された個別 architecture decision 自体の解決。
  - すべての template を包括的な tutorial document に作り替えること。

## 境界
- 常に行う:
  - Issue が実装可能な最小単位であるかを確認する。
  - Issue が主に意思決定だけを要求している場合は、Issue-local に閉じてよい軽量判断か、Epic / Initiative へ昇格すべき durable decision かを判定する。
  - Completed spec artifact に残る文言は、後続 agent が実装・検証に使う仕様として意味があるものに限る。
- 判断が必要:
  - Issue-local に閉じる軽量判断:
    - 実装手順に付随する小さな tradeoff、可逆な選択、単一 Issue の内部構造に限られる判断。
  - Epic に置く判断:
    - 複数 Issue の分解、責務境界、依存方向、shared component / workflow policy など、Issue 群の設計 backbone になる判断。
  - Initiative に置く判断:
    - 複数 Epic にまたがる product / architecture / operating model の投資判断。
- 行わない:
  - decision-only Issue を、実装可能な scope に変換しないまま execution phase へ進める。
  - docs で説明すべき概念理解を templates や skills に厚く埋め込む。

## 非交渉制約
- Provider-side source of truth を優先する。Shipped docs / templates / skills の変更は `src/spec_dock/assets/...` 側を authority とし、dogfooding mirror は validation target として扱う。
- Templates は final artifact scaffold であり、作成後の requirement / design / plan に残る文言は downstream agent にとって仕様として有用でなければならない。
- Skills は workflow を開始・停止・分岐させる薄い adapter / gate とし、詳細な概念理解は docs へ委譲する。
- Docs は概念説明、判断基準、具体例を保持する authority surface とする。
- Discussion artifact は evidence surface であり、`requirement.md` / `design.md` / `plan.md` / accepted ADR / workflow docs へ採用されるまでは canonical authority ではない。

## 前提
- Parent epic `epic-00158` は agent-facing context surface の整理と hardening を扱う。
- この Issue は、runtime enforcement より先に、docs / skills / templates の責務境界を明文化する documentation / workflow hardening Issue として扱う。
- User-approved decision と deep consultant analysis により、Option D / B-lite contract-first と clean-template policy が採用済みである。

## 受け入れ条件
- AC-001:
  - アクター: SpecDock maintainer / authoring agent
  - 前提: Issue が implementation task ではなく durable decision を主目的にしている
  - 操作: workflow docs / issue planning skill を参照する
  - 期待結果: Initiative / Epic / Issue のどこへ判断を置くべきかが明確に分かり、decision-only Issue を execution-ready と誤認しない
  - 観測点: workflow docs と planning skill の decision routing 記述
- AC-002:
  - アクター: Issue planning / clarification agent
  - 前提: Issue が architecture boundary、ownership、workflow policy など cross-issue decision を要求している
  - 操作: planning workflow を開始する
  - 期待結果: Issue-local 実装計画へ進む前に、Epic / Initiative へ戻すか、Issue-local lightweight decision として扱うかを判定する gate がある
  - 観測点: `spec-dock-issue-planning` / `spec-dock-clarification` の thin gate
- AC-003:
  - アクター: Spec authoring agent
  - 前提: decision-boundary の概念理解や具体例が必要である
  - 操作: shipped docs / authoring guidance を読む
  - 期待結果: Docs 側に reusable / generic な具体例と good / bad pattern があり、templates や skills に長い例を埋め込まずに authoring できる
  - 観測点: workflow / authoring docs
- AC-004:
  - アクター: Downstream implementation agent
  - 前提: Templates から作成済みの requirement / design / plan を読む
  - 操作: spec artifact をもとに実装作業を行う
  - 期待結果: Template 由来の `例:`、サンプル prose、product-specific dogfooding details、authoring-only instruction が残っていない
  - 観測点: provider templates と生成済み dogfooding mirror の inspection
- AC-005:
  - アクター: SpecDock maintainer
  - 前提: この Issue の背景になった dogfooding failure mode を将来追跡したい
  - 操作: `report.md` と discussion artifacts を確認する
  - 期待結果: どの evidence を採用し、何を templates/docs/skills へ反映したかが Evidence Adoption Ledger で追跡できる
  - 観測点: `report.md` Evidence Adoption Ledger
- AC-006:
  - アクター: Reviewer
  - 前提: docs / skills / templates の変更が入っている
  - 操作: spec review を行う
  - 期待結果: thin skills、thin templates、docs detailed guidance の責務分離が満たされている
  - 観測点: final spec review gate / docs inspection

## 例外・エッジケース
- EC-001:
  - 条件: 単一 Issue 内の実装手順にだけ関わる小さな判断が必要
  - 期待: Issue-local decision として `report.md` に記録でき、Epic へ昇格しなくてよい
  - 観測点: decision ledger の `Disposition=no_action` または `applied`
- EC-002:
  - 条件: 複数 Issue の分解や責務境界を変える判断が見つかった
  - 期待: Epic requirement / design へ戻す、または follow-up を作成し、当該 Issue を execution-ready として進めない
  - 観測点: planning skill の stop condition / `report.md` decision ledger
- EC-003:
  - 条件: 複数 Epic または product operating model に影響する判断が見つかった
  - 期待: Initiative または ADR 候補へ昇格し、Issue-local な判断として閉じない
  - 観測点: workflow docs / follow-up record
- EC-004:
  - 条件: Authoring agent が具体例を必要とする
  - 期待: Docs / authoring guidance を参照し、template body には例を追加しない
  - 観測点: docs reference from skill / absence of examples in templates

## 入力→出力例（必要時）
- この Issue の requirement には入力→出力例を置かない。具体例は templates ではなく docs / authoring guidance に置く方針自体がこの Issue の requirement である。

## 用語（ドメイン語彙）
- TERM-001:
  - Decision-only Issue:
    - 実装可能な成果物よりも、architecture / workflow / ownership / policy 判断を主目的にしている Issue。
- TERM-002:
  - Thin template:
    - 完成後の spec artifact に残っても仕様として意味がある最小限の headings、fields、readiness prompts だけを持つ template。
- TERM-003:
  - Thin skill:
    - workflow routing、stop condition、参照先 docs の案内を担い、詳細な概念説明や大量の例を持たない skill。
- TERM-004:
  - Docs detailed guidance:
    - 判断基準、概念説明、具体例、good / bad pattern を保持する reusable documentation surface。

## 未確定事項
- 現時点で blocking な未確定事項はない。
- 採用済み判断:
  - Option D / B-lite contract-first を採用する。
  - Templates は薄く保ち、具体例は docs に置く。
  - Skills も薄く保ち、workflow routing / stop condition を担う。
  - 詳細な概念理解と具体例は docs / authoring guidance に置く。
