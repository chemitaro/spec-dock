---
種別: research
ID: "20260522t120437z-research"
タイトル: "Delegated authoring source architecture report"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-22"
親: ["epic-00112"]
関連: ["GitHub #112"]
authority: "synthesized"
derived_from:
  - "user-provided report in Codex conversation on 2026-05-22"
reflected_to: []
---

# spec-dock delegated authoring architecture report

## 結論

**設計書と実装計画書は、専任サブエージェントを一次作成者にした方がよいです。**
ただし、完全に任せ切るのではなく、**メインオーケストレーターは「仕様の所有者・対話責任者・統合責任者・フェーズ昇格責任者」として残すべき**です。

最適解は次です。

| フェーズ  | 一次作成者                             | 最終責任 | 理由                                               |
| ----- | --------------------------------- | ---: | ------------------------------------------------ |
| 要件定義書 | メインオーケストレーター + 人間                 |  メイン | ユーザー意図、非スコープ、優先順位、受け入れ基準は対話でしか確定しにくい             |
| 設計書   | `system-architect` サブエージェント       |  メイン | 要件確定後は、既存コード・ADR・依存関係・境界・トレードオフを体系的に設計する専門タスクになる |
| 実装計画書 | `implementation-planner` サブエージェント |  メイン | 設計確定後は、依存順序・TDDスライス・レビューゲート・検証計画に分解する専門タスクになる    |
| レビュー  | 独立した `spec-reviewer`              |  メイン | 作成者とレビュアーを分離し、仕様ドリフトを検出する                        |

つまり、**「サブエージェントが設計・計画を作る」こと自体は正しい方向**です。ただし、spec-dock の思想に合わせるなら、正確には **“サブエージェントが canonical artifact の一次ドラフトを作成し、オーケストレーターが統合・昇格・対話・証跡管理を行う”** という形がベストです。

---

## 現在の spec-dock の構造理解

spec-dock は、既存リポジトリに軽量な仕様駆動ドキュメントワークスペースを生成するツールで、日常運用は生成された Markdown テンプレート、スクリプト、エージェントスキルを使う構造になっています。GitHub issue との import/new/start/finish、validate/sync、Initiative/Epic/Issue のツリー、`active/` の作業入口、`.agent/index.json` / `.agent/tree.json` の同期などを備えています。([GitHub][1])

設計上の中核は、**Initiative → Epic → Issue** の階層と、各ノードに `requirement.md` / `design.md` / `plan.md` / `report.md` を持たせることです。公式ガイド上も、Initiative は投資単位、Epic は設計の背骨、Issue は最小実装単位として整理されています。([GitHub][2])

また、spec-dock 自体も dogfooding されており、`src/spec_dock/` が provider code の source of truth、`spec-dock/` が生成された consumer-side workspace / active docs として扱われる構成です。active docs の canonical path は `spec-dock/active/{initiative,epic,issue}/{requirement,design,plan}.md` です。([GitHub][3])

重要なのは、現行ドキュメントがすでに **「requirement → spec-reviewer pass → design → spec-reviewer pass → plan → spec-reviewer pass → downstream handoff」** というフェーズ昇格ゲートを定義している点です。fresh な spec-reviewer pass がない限り次フェーズへ進めず、degraded / unavailable / denied などは pass ではありません。([GitHub][4])

この前提に立つと、設計書・実装計画書をサブエージェントに委譲しても、**フェーズゲートと canonical ownership を維持すれば、spec-dock の一貫性は壊れません。**

---

## なぜ要件定義はメインが持つべきか

要件定義は「正しい答えを導く作業」ではなく、**ユーザーの意思決定を仕様に固定する作業**です。

spec-dock の requirement phase も、WHAT / WHY / scope / success を固定し、HOW は design に送るものとして定義されています。Initiative は why/outcome/success/scope/constraints、Epic は capability/change area/AC、Issue は最小 behavior / AC / EC / concrete delta を扱うという責務分離も明確です。([GitHub][5])

ここをサブエージェントに主導させると、次のリスクが出ます。

1. **ユーザー意図の取り違え**
   サブエージェントは対話の全体文脈や暗黙の優先順位を過小評価しやすい。

2. **非スコープの弱体化**
   優秀な設計エージェントほど「ついでに良い設計」を広げやすい。これは spec-dock 的には scope creep です。

3. **トレードオフの責任所在が曖昧になる**
   「速く作る」「堅牢に作る」「将来拡張を優先する」「既存設計を守る」などは、最終的には人間とメインオーケストレーターが確定すべき判断です。

したがって、要件定義ではサブエージェントを使うとしても、**read-only research specialist** や **existing-code investigator** 程度に留めるのがよいです。一次作成とユーザー確認はメインが持つべきです。

---

## なぜ設計書は system-architect に委譲すべきか

設計フェーズは、要件定義とは性質が異なります。spec-dock の design phase は、WHAT/WHY を HOW/guardrails に変換し、既存実装、ADR、責務境界、契約、依存関係、移行、観測性、テスト戦略まで固定するものとして定義されています。([GitHub][6])

さらに issue design では、dependency analysis、module dependency diagram、Linux tree 形式の file change plan、interface contract、test strategy、verification mapping まで求められます。([GitHub][6])

これはかなり専門的な作業です。特に GPT-5.5 のような高推論モデルでは、次のような仕事をメインエージェントが毎回抱え込むより、専用ロールに切り出した方が品質が上がります。

* 既存コード・既存ドキュメント・ADR の照合
* bounded context / aggregate / value object / domain event など DDD 上の判断
* module / class / function / file レベルの依存分析
* API / DB / repository / service / UI boundary の契約整理
* migration / rollback / compatibility / observability の設計
* 代替案とトレードオフの比較
* PlantUML / C4 / sequence / module dependency diagram の適切な選択

OpenAI の reasoning model ドキュメントでも、GPT-5.5 のような reasoning model は、複雑な問題解決、コーディング、科学的推論、multi-step agentic workflow に向いており、`reasoning.effort` は `low` / `medium` / `high` / `xhigh` などで調整できます。([OpenAI デベロッパーズ][7]) また、reasoning model は複雑で曖昧なタスクの計画・意思決定に向き、単純実行系モデルと組み合わせて使うのが一般的なワークフローとして説明されています。([OpenAI デベロッパーズ][8])

したがって、**設計書は `system-architect` サブエージェントに一次ドラフトさせるのが自然**です。

ただし制約が必要です。

`system-architect` は requirement を変更してはいけません。
要件の不足を見つけた場合は、勝手に補完するのではなく、次のような **Requirement Clarification Request** を返すべきです。

```md
## Requirement Clarification Request

- Missing decision:
- Why this blocks design:
- Candidate options:
  - Option A:
  - Option B:
- Recommended default:
- Risk if assumed without user confirmation:
```

これにより、設計能力を活用しつつ、要件の所有権はメインに残せます。

---

## なぜ実装計画書も implementation-planner に委譲すべきか

実装計画書は、設計書の単なる箇条書きではありません。

spec-dock の plan phase は、承認済み requirement/design を、実行可能な分解、順序、停止点、品質ゲート、依存関係、exit criteria に変換するものとして定義されています。各 plan item は requirement item または design decision に traceable でなければならず、trace できない step は scope creep または前フェーズの不足です。([GitHub][9])

特に issue plan では、1 step = 1 observable behavior、Spec-Locked Closure Index、risk-calibrated test obligation、per-step delegation contract、S90 docs impact、S99 final gate などが要求されています。([GitHub][10])

これは **実装経験のある planner** の仕事です。system architect がそのまま plan まで書くより、別ロールにした方がよいです。理由は、設計者は自分の設計を過信しやすく、計画時に「実装順序」「テスト容易性」「レビュー単位」「rollback」「commit boundary」の粗さを見落とすことがあるからです。

最適な分離は次です。

```text
requirement.md
  ↓
system-architect
  → design.md draft
  → spec-reviewer
  ↓
implementation-planner
  → plan.md draft
  → spec-reviewer
  ↓
dev-coder / doc-writer
```

planner は design を変更してはいけません。
design に不足がある場合は、`Plan Blocked` を返すべきです。

```md
## Plan Blocked

- Blocking design gap:
- Affected requirement/design decision:
- Why implementation order cannot be safely derived:
- Required design amendment:
- Suggested amendment:
```

これを入れると、plan が design の隠れた矛盾を検出する第二のレビューにもなります。

---

## 推奨ワークフロー

### 1. Requirement Phase: メインが対話で固定する

入力:

* ユーザーとの対話
* 既存 docs/code/ADR
* GitHub issue
* Initiative/Epic/Issue の親子関係
* 現行制約、非スコープ、AC/EC

出力:

* `requirement.md`
* unresolved decision がない状態
* fresh `spec-reviewer` pass
* `report.md` への gate evidence

この段階では、メインは必要に応じて read-only investigator を呼んでもよいですが、requirement の canonical author はメインです。

---

### 2. Design Phase: system-architect が一次作成する

呼び出し条件:

* requirement が fresh spec-reviewer pass 済み
* scope が Initiative / Epic / Issue のどれか明確
* 親ノードの docs が読まれている
* 既存コード・ADR・関連 docs を調査できる

`system-architect` の出力契約:

```md
# Design Draft Result

## Summary

## Requirement Coverage
- Requirement ID:
- Design decision:

## Existing Implementation Findings

## Architecture Decisions

## Alternatives Considered

## Dependency Analysis

## Interface / Data / Domain Contracts

## Diagrams
- Diagram:
- Question answered:
- Update trigger:

## File / Module Change Plan

## Test Strategy

## Risks / Migration / Rollback

## ADR Candidates

## Requirement Clarification Requests
```

重要なのは、**design.md の template を埋めることではなく、設計判断を固定すること**です。spec-dock の design docs も、テンプレートは completion/compliance standard ではなく、必要に応じて section を追加・削除・並べ替えてよい minimal scaffold としています。([GitHub][6])

---

### 3. Design Integration Gate: メインが統合する

メインオーケストレーターは、architect の出力をそのまま通すのではなく、次を確認します。

* requirement の scope / non-scope を侵食していないか
* parent Initiative/Epic の設計方針と矛盾していないか
* design decision が requirement に traceable か
* unresolved user decision を勝手に仮定していないか
* diagram が「見た目」ではなく設計上の問いに答えているか
* file change plan が plan phase の入力として十分か
* ADR に昇格すべき判断が埋もれていないか

その後、`spec-reviewer` を fresh に走らせます。

---

### 4. Plan Phase: implementation-planner が一次作成する

呼び出し条件:

* requirement/design が fresh spec-reviewer pass 済み
* design に dependency analysis / module diagram / file change plan / test strategy がある
* scope が issue/epic/initiative のどれか明確

`implementation-planner` の出力契約:

```md
# Implementation Plan Draft Result

## Plan Summary

## Requirement IDs

## Milestones

## Dependency-Derived Order

## Step List
- Step ID:
- Observable behavior:
- Depends on:
- Target files/modules:
- Tests:
- Review gate:
- Commit boundary:

## Requirement-Step Mapping

## Spec-Locked Closure Index

## Delegation Contracts

## Test Cards

## Docs Impact

## Rollback / Recovery

## S90 Docs Impact Gate

## S99 Final Quality Gate

## Plan Blockers
```

plan は「作業手順」ではなく、**実行可能な command queue** として扱うべきです。spec-dock の issue execution skill も、plan は executable contract、report は observed evidence ledger として定義しています。([GitHub][11])

---

### 5. Plan Integration Gate: メインが統合する

確認観点:

* すべての step が requirement/design に traceable か
* 1 step = 1 observable behavior になっているか
* 実装順序が design の依存分析から導かれているか
* TDD/QA/code review/spec review の gate が入っているか
* delegation contract が実装 worker に渡せる粒度か
* docs impact と final gate が plan に含まれているか
* plan が design decision を勝手に追加していないか

その後、fresh `spec-reviewer` pass を必須にします。

---

## サブエージェントの権限設計

ここは重要です。最初から write-capable agent にする必要はありません。

### 推奨初期形: Draft-only delegation

サブエージェントは canonical file を直接編集せず、次のどちらかを返します。

* `design.md` / `plan.md` の全文ドラフト
* unified diff
* structured draft result

メインが差分を確認して適用します。

利点:

* 安全
* 仕様ドリフトを検出しやすい
* 既存の consent model を大きく変えずに導入できる
* reviewer / planner / architect の責務分離を試しやすい

欠点:

* メインの統合作業が残る
* コストと手順は少し増える

### 発展形: Scoped write-capable delegation

成熟後は、次の範囲に限定して write を許可してよいです。

```text
Allowed:
- spec-dock/active/{scope}/design.md
- spec-dock/active/{scope}/plan.md
- spec-dock/active/{scope}/discussions/*.md
- spec-dock/active/{scope}/report.md の delegation evidence section

Forbidden:
- requirement.md の変更
- 実装コードの変更
- テストコードの変更
- 親 Initiative/Epic docs の変更
- GitHub issue close/update
- destructive command
- credentials / external side effect
```

現行の issue workflow は、実装フェーズでは parent agent が inspect/plan/delegate/verify/integrate/report を担い、直接実装者ではないという不変条件を持っています。また、実装 step ごとに delegation gate を置き、dev-coder / doc-writer などへ role/scope/SSOT/allowed/forbidden/verification/stop/output を渡す構造を持っています。([GitHub][12])

この思想を spec authoring にも拡張するとよいです。

---

## reasoning effort の割り当て

GPT-5.5 の API ドキュメントでは、`reasoning.effort` によって推論量を調整でき、`high` や `xhigh` は高品質だがコスト・レイテンシが増える設定として扱われます。([OpenAI デベロッパーズ][13]) したがって、常に xhigh を使うのは非効率です。

推奨は次です。

| タスク                                                      |     推奨 effort | 理由                         |
| -------------------------------------------------------- | ------------: | -------------------------- |
| 要件対話の通常応答                                                | medium / high | ユーザー意図の確認と scope 整理が中心     |
| requirement.md 初稿                                        |          high | AC/EC/non-scope の漏れが後工程に効く |
| requirement reviewer                                     |          high | 仕様抜け検出が重要                  |
| issue-level design                                       |          high | 既存実装・依存関係・テスト戦略が必要         |
| epic/initiative-level design                             |  high / xhigh | 境界、責務、将来互換性、ADR 判断が必要      |
| migration / DB / auth / concurrency / external API を含む設計 |         xhigh | 失敗コストが高い                   |
| normal issue plan                                        |          high | 実装順序とテスト設計が品質に直結           |
| cross-epic roadmap / dependency plan                     |         xhigh | 分解ミスが全体計画を壊す               |
| template 整形、metadata sync、軽微な文言修正                        |  low / medium | 推論より正確な編集が中心               |
| reviewer 再実行                                             |          high | 作成者と独立した検出能力が必要            |

コスト最適化の観点では、**作成系よりレビュー系に high/xhigh を厚めに割り当てる**のが有効です。作成者が high、reviewer が medium だと、レビューが形式確認に寄りやすい。逆に、作成者 high、reviewer high/xhigh の方が、設計漏れや trace 不整合を検出しやすいです。

---

## spec-dock に入れるべき具体的変更

### 1. 新しい role skill を追加する

現在の skill 構成は、hub と Initiative/Epic/Issue/ADR の leaf skill を持つ形です。hub skill は workflow_spec_authoring を source of truth とし、各 artifact が fresh spec-reviewer pass を得てから次へ進むことを要求しています。([GitHub][14])

ここに、scope 別ではなく **role 別 skill** を追加するのがよいです。

```text
.agents/skills/spec-dock-system-architect/SKILL.md
.agents/skills/spec-dock-implementation-planner/SKILL.md
```

scope skill と role skill は分離すべきです。

* `spec-dock-issue-execution` は issue workflow の owner
* `spec-dock-system-architect` は design artifact の専門 author
* `spec-dock-implementation-planner` は plan artifact の専門 author

こうすると、Initiative/Epic/Issue すべてに対して同じ architect/planner ロールを再利用できます。

---

### 2. `workflow_spec_authoring.md` に artifact ownership を追加する

追加すべき概念はこれです。

```md
## Artifact Ownership vs Authoring Delegation

- The orchestrator owns canonical artifacts, phase promotion, user dialogue, and gate evidence.
- A delegated author may draft or patch design.md / plan.md within the active node.
- Delegated authors must not mutate previous-phase artifacts.
- If a previous phase is insufficient, the delegated author must return a blocker request.
```

これを入れないと、サブエージェント化したときに「誰が仕様を所有しているのか」が曖昧になります。

---

### 3. Delegated Design Gate を追加する

`phase_design.md` に次の gate を追加するのがよいです。

```md
## Delegated Design Authoring Gate

Required before invoking system-architect:

- requirement.md has fresh spec-reviewer pass
- active scope is confirmed
- parent docs are identified
- existing implementation/docs/ADR search scope is defined
- allowed write paths are declared
- forbidden actions are declared
- output format is declared
```

---

### 4. Delegated Plan Gate を追加する

`phase_plan.md` または `phase_plan_issue.md` に次を追加します。

```md
## Delegated Plan Authoring Gate

Required before invoking implementation-planner:

- requirement.md and design.md have fresh spec-reviewer pass
- design dependency analysis exists
- design file/module change plan exists
- verification strategy exists
- planner must not introduce new design decisions
- planner must return Plan Blocked if design is insufficient
```

---

### 5. report.md に delegation evidence を記録する

現行 workflow_issue には Decision Ledger や worker summary の思想があります。material decision を report に残し、open decisions を残したまま completion しないという構造です。([GitHub][12])

設計・計画のサブエージェント化でも、report に次を残すべきです。

```md
## Design Authoring Delegation

- Role:
- Model / reasoning effort:
- Scope:
- Inputs:
- Allowed paths:
- Output:
- Integrated by:
- Reviewer result:
- Open blockers:

## Plan Authoring Delegation

- Role:
- Model / reasoning effort:
- Scope:
- Inputs:
- Allowed paths:
- Output:
- Integrated by:
- Reviewer result:
- Open blockers:
```

これにより、「誰が何を判断したか」が後から追えます。

---

## 最終的な推奨アーキテクチャ

私なら spec-dock の authoring workflow を次のように再設計します。

```text
Main Orchestrator
  ├─ owns user dialogue
  ├─ owns requirement.md
  ├─ owns canonical integration
  ├─ owns phase promotion
  ├─ owns report evidence
  │
  ├─ read-only investigator
  │    └─ existing code/docs/ADR research
  │
  ├─ spec-reviewer
  │    └─ independent gate review for requirement/design/plan
  │
  ├─ system-architect
  │    └─ primary author for design.md
  │
  ├─ implementation-planner
  │    └─ primary author for plan.md
  │
  ├─ dev-coder
  │    └─ implementation step execution
  │
  └─ doc-writer
       └─ docs/templates/skills/workflow changes
```

この構成では、メインエージェントの責務は **「全部を書くこと」ではなく、「正しい専門家を呼び、出力を統合し、仕様の整合性を守ること」** になります。

これはエージェンティックコーディングのハーネスとして自然です。ハーネスが提供すべき価値は、単一エージェントに巨大な文脈を抱えさせることではなく、**仕様・設計・計画・実装・レビューを明確な契約で接続すること**だからです。

---

## 判断基準

この変更を入れるべきかどうかは、次の基準で判断できます。

**入れるべきケース**

* design.md が毎回かなり具体的になっている
* 人間が design.md / plan.md をほぼ修正していない
* 実装失敗の原因が「計画の粗さ」や「依存順序の見落とし」に寄っている
* DDD、レイヤード、CQRS、migration、API boundary など設計判断が多い
* spec-reviewer で後から design/plan の欠陥が見つかることがある

**入れない方がよいケース**

* docs-only の小さな issue
* 単一ファイルの trivial fix
* requirement 自体がまだ曖昧
* ユーザー意思決定が設計判断より支配的
* サブエージェントの write scope を安全に制限できない

したがって、全面的な義務化ではなく、最初は **risk-based delegation** がよいです。

```text
small issue:
  main writes design/plan directly

normal issue:
  system-architect drafts design
  implementation-planner drafts plan

high-risk issue/epic:
  system-architect high/xhigh
  implementation-planner high/xhigh
  independent spec-reviewer high/xhigh
  optional architecture-reviewer / qa-strategist
```

---

## 最終提案

spec-dock の次の進化としては、次の方針が最も筋が良いです。

1. **要件定義はメインオーケストレーターが人間と対話して作る**
2. **設計書は `system-architect` サブエージェントを一次作成者にする**
3. **実装計画書は `implementation-planner` サブエージェントを一次作成者にする**
4. **サブエージェントは前フェーズ artifact を変更できない**
5. **不足があれば勝手に補完せず、Clarification / Blocked として返す**
6. **メインは canonical artifact owner として統合・昇格・証跡管理を行う**
7. **fresh `spec-reviewer` pass は現行通り必須**
8. **最初は draft-only、成熟後に scoped write-capable delegation へ移行する**

この形なら、GPT-5.5 high/xhigh の設計・計画能力を最大限使いつつ、spec-dock の強みである **spec-driven、phase gate、traceability、report evidence、agent-native TDD** を壊さずに拡張できます。

[1]: https://github.com/chemitaro/spec-dock/blob/main/README.md "spec-dock/README.md at main · chemitaro/spec-dock · GitHub"
[2]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/guide.md "spec-dock/spec-dock/docs/guide.md at main · chemitaro/spec-dock · GitHub"
[3]: https://github.com/chemitaro/spec-dock/blob/main/AGENTS.md "spec-dock/AGENTS.md at main · chemitaro/spec-dock · GitHub"
[4]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/workflow_spec_authoring.md "spec-dock/spec-dock/docs/workflow_spec_authoring.md at main · chemitaro/spec-dock · GitHub"
[5]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/phase_requirement.md "spec-dock/spec-dock/docs/phase_requirement.md at main · chemitaro/spec-dock · GitHub"
[6]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/phase_design.md "spec-dock/spec-dock/docs/phase_design.md at main · chemitaro/spec-dock · GitHub"
[7]: https://developers.openai.com/api/docs/guides/reasoning "Reasoning models | OpenAI API"
[8]: https://developers.openai.com/api/docs/guides/reasoning-best-practices "Reasoning best practices | OpenAI API"
[9]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/phase_plan.md "spec-dock/spec-dock/docs/phase_plan.md at main · chemitaro/spec-dock · GitHub"
[10]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/phase_plan_issue.md "spec-dock/spec-dock/docs/phase_plan_issue.md at main · chemitaro/spec-dock · GitHub"
[11]: https://github.com/chemitaro/spec-dock/blob/main/.agents/skills/spec-dock-issue-execution/SKILL.md "spec-dock/.agents/skills/spec-dock-issue-execution/SKILL.md at main · chemitaro/spec-dock · GitHub"
[12]: https://github.com/chemitaro/spec-dock/blob/main/spec-dock/docs/workflow_issue.md "spec-dock/spec-dock/docs/workflow_issue.md at main · chemitaro/spec-dock · GitHub"
[13]: https://developers.openai.com/api/docs/guides/latest-model "Using GPT-5.5 | OpenAI API"
[14]: https://github.com/chemitaro/spec-dock/blob/main/.agents/skills/spec-driven-tdd-workflow/SKILL.md "spec-dock/.agents/skills/spec-driven-tdd-workflow/SKILL.md at main · chemitaro/spec-dock · GitHub"
