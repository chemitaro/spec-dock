---
種別: interview
ID: "20260707t143000z-interview"
タイトル: "Workflow first ChatGPT authoring redesign interview 1"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00295"
created_at: "2026-07-07THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260707t140041z-01-research-chatgpt-workflow-integration-analysis.md"
  - "artifacts/20260707t140041z-research-authoring-pack-install-architecture-analysis.md"
reflected_to:
  - "report.md#Evidence Adoption Ledger"
---

# 20260707t143000z-interview Workflow first ChatGPT authoring redesign interview 1

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Epic が最初に最適化するユーザー体験、主要ユースケース、scope / non-scope。
  - `design.md`:
    - Planning / Execution skill の再編境界、ChatGPT と Codex の責務分担、runtime command の導出順序。
  - `plan.md`:
    - Issue 分割順、最初に実装する skill / docs / runtime surface。
  - `ADR`:
    - 必要なら、Issue Planning skill split / mode split の長期判断。
- chat 上の軽微な一問では足りない理由:
  - 回答によって、Epic 全体の主目的、skill の分割粒度、ChatGPT batch workflow の入口が変わる。

## 質問の目的 (必須)
- 対象者:
  - SpecDock の主利用者 / product owner。
- 何を明確にする質問か:
  - ChatGPT-assisted workflow redesign で最初に最適化する体験。
- 回答が後続判断へ与える影響:
  - Initiative / Epic / Issue planning skill をどう分けるか、Issue Planning を mode split するか、Execution skill が planning をどう呼ぶかが変わる。

## 質問 (必須)
- pressure-test question:
  - もし最初の release で一つの体験だけを圧倒的に良くするとしたら、どの体験を最優先にしますか。
- 質問:
  - SpecDock の新しい ChatGPT-assisted workflow で、最も大きく変えたい体験はどれですか。
- 回答してほしいこと:
  - A / B / C のどれを最優先にするか。必要なら「A を主、B を次」など優先順位で回答してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - active Epic: `epic-00295`
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
  - `spec-dock-issue-planning`
  - `spec-dock-epic-execution`
  - `spec-dock-issue-execution`
  - `workflow_spec_authoring.md`
  - `workflow_epic.md`
  - `workflow_issue.md`
  - `artifacts/20260707t140041z-01-research-chatgpt-workflow-integration-analysis.md`
  - `artifacts/20260707t140041z-research-authoring-pack-install-architecture-analysis.md`
- local context で解決できたこと:
  - 前回の root `scripts/authoring-pack/` 起点の進め方は、consumer repo へ提供されないため不十分。
  - 新 Epic では workflow / skill / runtime command の順に再設計する必要がある。
  - 現行 Issue Planning は、ゼロベース対話型と Epic draft 採用型を同じ spine に含んでいる疑いがある。
- まだ人間判断が必要な理由:
  - どの体験を第一最適化するかは product strategy / usage priority の判断であり、repo だけでは決められない。

## 回答案 (必須)
- Option A:
  - 大きな仕事を一括で計画する体験。
  - Initiative / Epic から複数 Epic / Issue へ分解し、要件・設計・計画ドラフトをまとめて作ることを最優先する。
  - ChatGPT は batch planner / decomposer、Codex は採用・配置・実行を担う。
- Option B:
  - 各 Issue を実行直前に高速で正本化する体験。
  - Epic から渡された draft requirement/design/plan を、Issue start 後に formal canonical docs へ整えることを最優先する。
  - ChatGPT は draft adoption / refinement / self-review、Codex は canonical adoption と reviewer gate を担う。
- Option C:
  - 単体 Issue をゼロから一緒に作る体験。
  - ユーザーとの quick dialogue で Issue requirement を固め、その後 ChatGPT で design/plan を深く作ることを最優先する。
  - Codex の対話性を前面に残し、ChatGPT は深い設計・計画に使う。

## Codex の分析 (必須)
- 判断軸:
  - 最初に product value を出す workflow の入口。
  - skill split / mode split の必要性。
  - ChatGPT の長時間推論と Codex の即時対話の最適な分担。
- tradeoff:
  - A は巨大タスクの分解に効くが、Issue 実行時の draft adoption が弱いと実装前に詰まる。
  - B は Epic execution の流れを大きく改善するが、上流の decomposition quality は別途必要になる。
  - C は単体 Issue の体験が良いが、今回の authoring-pack / batch workflow の価値を小さく使う可能性がある。
- リスク:
  - 優先体験を決めずに全部を一度に良くしようとすると、skill が肥大化し、前回と同じく script / workflow / skill の責務が逆転する。
- 具体シナリオ / edge case:
  - Epic Planning が 10 Issue の draft pack を生成した後、Epic Execution が Issue を一つずつ start し、Issue Planning が draft を正式版に整えるケース。
  - ユーザーが単体 Issue だけを持ち込み、Codex と対話しながら requirement を作るケース。

## Codex の推奨案 (必須)
- 推奨:
  - B を第一優先、A を第二優先にする案。
- 理由:
  - 前回の失敗は scripts を先に作ったことに加え、Epic Execution 中に Issue draft を formal docs に変換する workflow が未定義だったことが大きい。
  - B を固めると、Epic Planning の batch output が実装可能な Issue execution に接続される。
  - A はその次に、上流 batch planning の入口として自然に積み上げられる。
- 未回答時の影響:
  - Issue Planning を split するか mode 化するか、ChatGPT authoring-pack skill の最初の入口をどこに置くかが確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A の優先度が最も高い。
  - 小さい仕事だけでなく、大きな仕事をスライスし、モデル化・実装できる小さな Issue 単位へ分ける体験を最優先する。
  - 要件具体化、要件・設計・計画の具体化を SpecDock に記載し、その過程で ChatGPT の長時間・高度な推論を使うことに特に期待している。
  - 規模の小さな update / 利用では Option B が有力。
  - 実質的に多いのは A と B の組み合わせ。
  - Initiative を Epic に分解し、Epic を複数 Issue に分解・スライスした上で、各 Issue の実装前に正式な仕様・設計・計画を固めて実装する。
  - A と B はセットであり、A の先に B がある。
- 回答:
  - Option A を第一優先とする。Option B は A の下流としてセットで扱う。
- 回答日時:
  - 2026-07-07

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - A -> B の一連 workflow において、人間が必ず承認する checkpoint をどこに置くか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - この回答は、Epic の主要目的を「大きな仕事を ChatGPT で一括計画・分解し、下流で Issue 実装前に正本化する workflow」に固定する product priority であるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Epic の第一目的は Option A: 大きな仕事を Initiative / Epic / Issue へスライスし、実装可能な単位まで具体化する体験。
  - Option B は A の下流として、Issue 実装直前の canonical docs 正本化 workflow に位置づける。
- `design.md`:
  - workflow model は `large-work batch planning -> Epic/Issue slicing -> Issue draft handoff -> draft-adoption Issue Planning -> Issue Execution` を主軸にする。
  - Issue Planning は `zero-base` と `draft-adoption` の mode 差を明示する。
- `plan.md`:
  - 実装順は workflow / skill redesign を先に行い、その後 runtime command / scripts を導出する。
  - A と B をつなぐ dogfood scenario を plan に含める。
- `ADR`:
  - Issue Planning skill の split / mode 化が長期契約になる場合は ADR 候補。
- reflected_to 更新方針:
  - まず `report.md` EAL に反映し、requirement / design / plan 具体化時に採用する。
- adoption reflection:
  - `report.md` EAL にユーザー回答の採用を記録する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る artifacts:
  - ...
