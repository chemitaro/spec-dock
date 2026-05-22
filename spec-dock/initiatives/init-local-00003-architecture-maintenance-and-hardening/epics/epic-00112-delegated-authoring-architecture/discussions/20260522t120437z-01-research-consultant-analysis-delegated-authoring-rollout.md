---
種別: research
ID: "20260522t120437z-01-research"
タイトル: "Consultant analysis for delegated authoring rollout"
状態: "completed"
作成者: "Codex"
最終更新: "2026-05-22"
親: ["epic-00112"]
関連: ["GitHub #112"]
authority: "synthesized"
derived_from:
  - "consultant sub-agent analysis on 2026-05-22"
  - "deep-consultant sub-agent analysis on 2026-05-22"
reflected_to:
  - "20260522t120437z-02-disc-epic-slicing-recommendation-delegated-authoring.md"
---

# Consultant analysis for delegated authoring rollout

## 調査目的

system-architect / implementation-planner を spec authoring workflow に導入する変更について、単独 issue で実施すべきか、Epic として複数 issue に分割すべきかを評価する。

## 調査方法

- ユーザー提供の source architecture report を consultant / deep-consultant に共有した。
- ローカル repo の authoring workflow、phase docs、issue execution workflow、provider asset 配置を参照対象として指定した。
- consultant と deep-consultant に独立した分析レポートを依頼した。

## Consultant report

### 結論

これは Epic + 複数 issue に分けるべきである。単独 issue では、role skill 追加、authoring workflow 契約変更、phase gate 変更、report evidence 変更、provider / consumer mirror、install / update asset parity、host adapter 側の callable role 整備までが混ざり、レビュー単位が大きすぎる。

初期導入は draft-only delegation を推奨する。現行 workflow_spec_authoring.md は reviewer / read-only specialist の consent までしか許可しておらず、write-capable delegation は明示的に除外している。いきなり canonical design.md / plan.md をサブエージェントに直接書かせると、spec-dock の強みである orchestrator ownership、fresh spec-reviewer gate、report evidence が曖昧になる。

### 根拠

- AGENTS.md は、provider source of truth を src/spec_dock/、dogfooding consumer workspace を spec-dock/ と分けている。特に shipped agent tooling は src/spec_dock/assets/install_root/、shipped docs は src/spec_dock/assets/spec_dock/docs/ が authority である。
- workflow_spec_authoring.md は requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass を正本契約にしており、promotion は fresh passed のみ許可している。
- 同文書の delegation consent は現状 reviewer / read-only specialist 向けで、write-capable delegation は許可外である。
- workflow_issue.md には実装時 delegation の厳密な gate が既にあるが、これは implementation step 用である。spec authoring へ流用するには、artifact ownership と authoring delegation の新契約が必要である。
- 現在、consumer .agents/skills と provider src/spec_dock/assets/install_root/.agents/skills に system-architect / implementation-planner 相当はない。
- tests/test_init_update.py には dogfooding mirror / managed asset list / installed artifact parity の明示リストがあり、新しい shipped skill や host agent を追加するならここも更新対象になる。

### 推奨分割

| Issue | 目的 | 主な成果物 | 依存 |
| --- | --- | --- | --- |
| 1. Delegated authoring policy foundation | ownership / consent / draft-only の正本を固める | workflow_spec_authoring.md、必要なら phase_design.md / phase_plan.md の方針追加、report evidence 契約 | なし |
| 2. Role skill assets | system-architect / implementation-planner の role skill を追加する | spec-dock-system-architect/SKILL.md、spec-dock-implementation-planner/SKILL.md、必要な mirror / test list | Issue 1 |
| 3. Host callable role integration | Codex / GitHub Copilot で named role として呼べる形を整える | .codex/agents/system-architect.toml、.codex/agents/implementation-planner.toml、必要なら .github/agents/*.agent.md | Issue 2 |
| 4. Phase gate and report evidence integration | design / plan authoring に delegated draft gate を組み込む | phase_design.md、phase_plan.md、phase_plan_issue.md、report template / authoring docs | Issue 1-3 |
| 5. Dogfooding parity and validation | provider / consumer 二重管理と install / update 回帰を閉じる | dogfooding workspace refresh、tests/test_init_update.py asset parity、init / update / validate evidence | Issue 2-4 |

### Draft-only を選ぶ理由

Draft-only は現行契約に最も自然に乗る。現状の consent は write-capable delegation を許可しておらず、spec authoring の canonical ownership は main orchestrator にある。

初期形は以下とする。

- system-architect: design.md の draft result を返す。requirement 不足は Requirement Clarification Request として返す。
- implementation-planner: plan.md の draft result を返す。design 不足は Plan Blocked として返す。
- orchestrator: draft を canonical artifact に統合し、report evidence を残し、fresh spec-reviewer を通す。

Scoped write-capable は後続でよい。移行条件は、少なくとも数件の dogfooding issue で、delegated draft が scope creep せず、reviewer fail の主要原因にならず、report evidence が追跡可能だったことである。

### 主なリスク

- requirement 所有権の侵食: architect が不足要件を設計で補うリスク。
- plan に未承認 design decision が混入するリスク。
- role skill、native host agent、workflow docs の三重定義で drift するリスク。
- provider asset と dogfooding consumer の mirror 不一致。
- write-capable delegation を急ぐことで consent model と report evidence が破綻するリスク。
- docs-only 変更に見えて、実際には shipped asset API change になる点の過小評価。

## Deep-consultant report

### 結論

この変更は Epic として複数 issue に分けるべきである。理由は規模ではなく、spec authoring、spec-reviewer、issue execution、provider / consumer dogfooding の責務境界にまたがり、単一 issue で入れると「誰が正本を書いたのか」「reviewer freshness が何を保証したのか」が曖昧になるためである。

最小安全導入は draft-only delegation である。delegated agent は canonical docs を直接更新せず、調査・草案・差分案・未決事項・根拠を report として返すだけにする。canonical な requirement.md / design.md / plan.md への反映、phase gate 判定、spec-reviewer 実行は親 authoring workflow 側が持つべきである。scoped write-capable は初期導入に含めない判断を推奨する。

### 設計原則

- canonical docs の所有者は親 workflow。delegated agent は証拠と草案の提供者であって、phase state の所有者ではない。
- spec-reviewer は独立した gate。delegated author と同一責務にしない。
- freshness は明示する。report には対象 phase、読んだファイル、base commit または doc revision、未確認事項、生成日時を含める。
- provider-first。skills は src/spec_dock/assets/install_root/.agents/skills/、docs は src/spec_dock/assets/spec_dock/docs/ を正本として変更し、consumer 側 spec-dock/ は dogfooding 検証対象にする。
- issue execution とは分離する。issue execution は active issue docs を実装する役割であり、spec authoring の正本作成者にしない。
- delegation report は evidence であり authority ではない。矛盾時は canonical docs と reviewer 結果を優先する。

### 推奨 Epic 分割

1. Delegated authoring contract / ADR
   - draft-only を v0 の明示方針にする。責務境界、禁止事項、freshness、失敗モード、rollback を文書化する。
2. Report template / schema v0
   - report に scope、source docs、assumptions、proposed canonical changes、open decisions、risk、freshness metadata を持たせる。
3. Authoring skills への draft-only delegation 組み込み
   - spec-driven-tdd-workflow と authoring 系 skill が、delegate を使う条件、受け取る report、canonical docs への反映責任を明示する。
4. Phase gate / reviewer freshness 連携
   - workflow_spec_authoring.md と phase docs が、delegated report 使用時の reviewer freshness 条件を明示する。
5. Dogfooding pilot
   - 小さな spec-dock authoring task で draft-only delegation を使い、report、canonical 反映、reviewer pass、issue evidence を一連で残す。

### 初期 Epic に入れない方がよいもの

Agent role registry、runtime validation、canonical write-capable delegation は後続 Epic が妥当である。初期 Epic に入れてよいのは report template / schema v0 までである。registry や runtime validation は、少なくとも dogfooding pilot で 2-3 件の report 例ができてからでないと、早すぎる抽象化になりやすい。

### 事前確認すべき意思決定

- delegated agent にファイル書き込みを許すか。許す場合、discussions/ だけか、canonical docs も含むのか。
- v0 は optional workflow か、authoring 時の既定手順にするのか。
- report の保存場所をどこにするか。
- spec-reviewer が delegated report をどう扱うか。
- freshness metadata に commit hash を必須にするか、doc path + timestamp で始めるか。
- 初回 dogfooding pilot の対象 phase を requirement / design / plan のどれにするか。
- scoped write-capable をこの Epic の明示的非対象にすることを合意するか。
- 将来の role registry / runtime validation を後続 Epic に切り出す方針でよいか。

## 推測 / 未検証事項

- 推測:
  - 初期導入では draft-only delegation を採用する方が、既存 consent model と reviewer freshness contract を壊しにくい。
- 未検証:
  - この Epic の requirement / design / plan はまだ未作成であり、最終的な issue 分割は今後の spec authoring gate で確定する必要がある。
  - .codex/agents と .github/agents を初期 Epic に含めるかは、ユーザー判断が必要である。

## 判断への含意

- この Epic は単独 issue ではなく、複数 issue の設計対象として扱う。
- 初期スコープは draft-only delegated authoring に限定する。
- scoped write-capable delegation、role registry、runtime validation は後続 Epic または後続 issue として扱う。
- provider-first / consumer dogfooding parity を acceptance criteria に含める。
