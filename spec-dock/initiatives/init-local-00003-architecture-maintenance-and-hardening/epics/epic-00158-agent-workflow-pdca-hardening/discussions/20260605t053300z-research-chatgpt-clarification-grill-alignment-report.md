---
種別: research
ID: "20260605t053300z-research"
タイトル: "ChatGPT Report For Clarification Grill Alignment"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "20260605t052200z-research"
  - "20260605t050100z-disc"
authority: "external-analysis"
derived_from:
  - "ChatGPT じっくり思考 Pro thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a226f41-80b0-83a3-b764-208ab9681f48"
reflected_to: []
---

# 20260605t053300z-research ChatGPT Report For Clarification Grill Alignment

## 実行記録

- 対象:
  - `spec-dock-clarification` を Matt Pocock 氏の `Grill with me` / `Grill with dog` 的な対話ワークフローの SpecDock 統合 skill として分析した。
- 入力:
  - `spec-dock/active/epic/discussions/20260605t052200z-research-chatgpt-clarification-grill-alignment-task-package.md`
- 使用スレッド:
  - 採用対象:
    - ChatGPT `じっくり思考 Pro`
    - https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a226f41-80b0-83a3-b764-208ab9681f48
  - 破棄対象:
    - 先に `Thinking` で送信された同内容の thread は、ユーザー指示により使用しない。
    - その thread の回答本文は採用、要約、反映していない。

## ChatGPT 結論の要約

`spec-dock-clarification` は、単なる `docs-aware clarification` ではなく、SpecDock 版の `source-grounded grill loop` として書き直す価値がある。

ただし、Matt Pocock 氏の原文は入力 context に含まれていないため、原文への exact fidelity は主張しない。ここでいう `Grill` は、supplied context に基づく限定的な意味、すなわち「focused, iterative, pressure-tested questions によってユーザーの考えを深め、要求の曖昧さを潰す対話パターン」として扱う。

結論として、この変更は `Align Skill Docs Template Context Surfaces` の broader cleanup に属するが、`spec-dock-clarification` 固有の concrete issue として切り出すべきである。

## 推奨 workflow spine

ChatGPT は、`SKILL.md` に次の実行順序を first-read surface として置くことを推奨した。

1. `Establish mode and scope`
   - `analysis-only` / `draft-only` / `canonical authoring` を判断する。
   - ユーザーに毎回モード確認を投げず、依頼文と local context から判断できる場合は判断して進める。
2. `Read before asking`
   - active docs、parent docs、`discussions/`、関連 code/tests/templates、ADR を読む。
   - local context で答えられる事実や制約を human に聞かない。
3. `Build a provisional model`
   - current understanding。
   - source-grounded facts。
   - inferred assumptions。
   - ambiguity / contradiction / missing decision。
   - affected artifact。
   - implementation / test / review / migration impact。
   - evidence が支える場合の candidate answer / recommended default。
4. `Select one essential pressure-test question`
   - source-grounded。
   - one question only。
   - consequential。
   - answerable。
   - affected artifact と結びつく。
   - scenario / edge case / tradeoff / scope boundary / adoption consequence のいずれかを圧力テストする。
   - local context で答えられない。
5. `Route through artifacts`
   - `scratch`: raw / transient capture。
   - `research`: facts、uncertainty、terms、question candidates。
   - `interview`: important human decision。
   - `disc`: synthesis / ADR triage。
   - `adr`: durable tradeoff decision。
   - `report.md`: canonical authoring adoption evidence。
6. `Create unanswered interview before asking`
   - 重要判断では、質問前に unanswered `interview` を作る。
   - 回答後、同じ artifact を complete し、impact / reflection / adoption needs を残す。
7. `Iterate or stop`
   - 回答ごとに provisional model と assumptions を更新する。
   - 次の single essential question を選ぶか、`unresolved questions: none` として handoff する。

## Skill / Docs / Templates boundary

| Surface | 役割 | 入れるべき内容 | 入れない内容 |
| --- | --- | --- | --- |
| `SKILL.md` | operational workflow spine | source-grounded grill loop、one essential question、artifact routing、orchestrator discipline、handoff | 長い formal trigger list、ledger 詳細、artifact 定義全文、長い例 |
| `workflow_clarification.md` | source of truth | definitions、decision tree、formal triggers、artifact semantics、mode semantics、ledger semantics、issue handoff boundary | skill と同じ短い reminder の重複だけ |
| `interview.md` | formal one-question artifact | unanswered before asking、source grounding、pressure-test question、candidate answers、answer capture、reflection/adoption | 複数質問 questionnaire |
| `research.md` | facts / uncertainty / question candidates | source facts、terms、ambiguity map、question candidates for orchestrator | human decision の正式回答保存先としての濫用 |
| `disc.md` | synthesis / ADR triage | resolved understanding、tradeoff、ADR threshold、reflection plan | raw fact dump や unanswered interview の代替 |

## Template 反映案

### `templates/discussions/interview.md`

`interview.md` は Grill workflow の中心 artifact になる。特に次の slots が重要。

- `Status`
  - `state: unanswered / answered`
  - `question owner: orchestrator`
  - `mode`
- `Source grounding`
  - `sources read`
  - `relevant facts`
  - `local context could not answer because`
- `Provisional understanding`
  - `current interpretation`
  - `assumptions`
  - `affected artifacts`
- `Essential question`
  - `question`
  - `why this is the next essential question`
  - `pressure-tested boundary / scenario / edge case`
  - `downstream impact if unanswered`
- `Candidate answers`
  - `option A`
  - `option B`
  - `recommended default, if any`
  - `rationale for recommendation`
- `Answer capture`
  - `human answer`
  - `interpretation`
  - `assumptions accepted`
  - `assumptions rejected`
- `Reflection / adoption`
  - `affected docs`
  - `affected templates`
  - `affected issues/plans`
  - `report.md ledger evidence needed`
  - `next question, or none`

### `templates/discussions/research.md`

`research.md` は、human answer の保存先ではなく、質問前の仮説構築と question candidates 作成に寄せる。

- `Sources read`
- `Source-grounded facts`
- `Terms and domain language`
- `Uncertainties`
  - answerable from local sources
  - not answerable from local sources
  - requires human decision
- `Ambiguity map`
  - ambiguity
  - affected artifact
  - downstream impact
  - candidate interpretation
  - confidence
- `Question candidates for orchestrator`
  - candidate question
  - rationale
  - affected artifact
  - recommended answer, if any
  - should become interview?: yes/no

### `templates/discussions/disc.md`

`disc.md` は、research / interview を束ね、ADR triage と reflection plan に接続する surface として整理する。

- `Inputs`
  - research
  - interviews
  - related docs / ADRs
- `Synthesis`
  - resolved understanding
  - remaining ambiguity
  - accepted assumptions
  - rejected assumptions
- `Decision pressure`
  - tradeoff
  - scope boundary
  - implementation / test / review / migration impact
- `ADR triage`
  - durable decision?: yes/no
  - ADR needed because
  - ADR not needed because
- `Reflection plan`
  - canonical docs to update
  - templates to update
  - report.md ledger entries
  - unresolved questions

## Issue decomposition recommendation

ChatGPT は、次の concrete issue を `Align Skill Docs Template Context Surfaces` の子 issue / explicit sub-issue として切ることを推奨した。

Title:

- `Revise spec-dock-clarification as source-grounded grill workflow`

Scope:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
- `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
- dogfooding mirror は verification target であり authority ではない。

Non-scope:

- Matt Pocock 氏の original text のコピーまたは exact reproduction。
- `spec-dock-clarification` を generic coaching skill にすること。
- runtime gates。
- automated regression checks first。
- templates の compliance authority 化。
- `workflow_clarification.md` の全文を skill にコピーすること。
- issue planning / execution workflow の再設計。
- ADR 作成条件そのものの大幅変更。
- specialist agents が human に直接質問する flow への変更。

## Acceptance criteria 案

- `SKILL.md` を最初に読んだモデルが、次の loop を理解できる。
  - read sources。
  - build provisional understanding。
  - identify ambiguity / assumption / impact。
  - ask one pressure-test question。
  - capture answer in artifact。
  - iterate or handoff。
- `SKILL.md` に、human に聞く前の source reading と、local context で答えられることを聞かない制約が明示されている。
- `SKILL.md` に、良い question の quality bar がある。
- 重要判断では、質問前に unanswered `interview` artifact を作り、回答後に同じ artifact を complete する流れが明示されている。
- `workflow_clarification.md` は artifact semantics、formal question triggers、mode definitions、ledger semantics、orchestrator / specialist protocol の詳細を保持している。
- `interview.md` は、一問だけの formal question artifact として機能する。
- `research.md` は facts の羅列だけでなく、ambiguity map と orchestrator 向け question candidates を作れる。
- `disc.md` は research / interview の結果を synthesis し、ADR triage と reflection / adoption plan に接続できる。
- skill / docs / templates の境界が保たれている。
- clarification は issue execution redesign に拡張されていない。

## Verification 案

- provider-side files の diff を読んで、skill に workflow spine が見えることを確認する。
- `workflow_clarification.md` に詳細定義が残っており、skill への過剰コピーがないことを確認する。
- `interview.md` が複数質問 questionnaire になっていないことを確認する。
- `research.md` が facts、uncertainty、question candidates を分けていることを確認する。
- `disc.md` が ADR triage と reflection plan を扱えることを確認する。
- sample scenario で dry-run する。
  - local docs で答えられる ambiguity では human に聞かない。
  - local docs で答えられない重要 decision では unanswered `interview` を作ってから一問だけ聞く。
  - 回答後に同じ `interview` を complete する。
- `analysis-only mode` の dry-run で canonical docs adoption を強制しないことを確認する。
- `canonical authoring mode` の dry-run で `report.md` evidence adoption / objective alignment / spec authoring gate に接続できることを確認する。
- dogfooding mirror は provider-side と矛盾していないか確認する。ただし authority として扱わない。

## Risks and mitigations

### Overfit risk

- `Grill` を「とにかく人間に鋭い質問をすること」と解釈し、source-grounded read が弱まる。
  - Mitigation:
    - `Read before asking` を skill spine の先頭に置く。
    - `interview.md` に `local context could not answer because` を置く。
- generic coaching skill になり、SpecDock artifact へ反映されない。
  - Mitigation:
    - artifact routing を skill spine に含める。
    - `interview.md` に answer capture / reflection / adoption slots を置く。
    - `disc.md` に ADR triage / report ledger linkage を置く。
- adversarial / performative な grilling になる。
  - Mitigation:
    - `one essential question` を維持する。
    - `whose answer most reduces downstream risk` を quality bar にする。
    - affected artifact と downstream impact を必須化する。
- original skill への fidelity 問題。
  - Mitigation:
    - 原文一致は主張しない。
    - SpecDock constraints に基づく interaction pattern adaptation として扱う。

### Underfit risk

- 現行 skill が reminder list のままで、実行順序が伝わらない。
  - Mitigation:
    - skill に workflow spine を明示する。
    - provisional understanding と pressure-test question を入れる。
- 質問が generic になる。
  - Mitigation:
    - source-grounded question format を template に置く。
    - scenario / edge case / tradeoff / scope boundary / adoption consequence を明示させる。
- formal interview trigger が使われない。
  - Mitigation:
    - `create unanswered interview before asking` を skill に入れる。
    - `interview.md` に unanswered / answered state を持たせる。
- specialist / orchestrator 分離が崩れる。
  - Mitigation:
    - skill に `specialists return question candidates; orchestrator asks` を残す。
    - `research.md` に `Question candidates for orchestrator` slot を置く。
- authoring handoff が弱くなる。
  - Mitigation:
    - skill の最初に mode 判定を置く。
    - handoff に authoring mode と `report.md` adoption evidence を残す。
    - `disc.md` に reflection / adoption plan を入れる。

## Codex synthesis

この分析は、前回の ChatGPT issue decomposition report が `spec-dock-clarification` を「現状良く、return wording 程度でよい」と軽く扱った点を上書きする重要な補正である。

今回のユーザー観点では、`spec-dock-clarification` は単なる clarification helper ではなく、SpecDock における `Grill with me / Grill with dog` の統合 surface である。そのため、`return-to-authoring wording` だけでは不足する。

採用候補:

- `Align Skill Docs Template Context Surfaces` の中核 sub-issue として、`Revise spec-dock-clarification as source-grounded grill workflow` を追加する。
- `spec-dock-clarification` は、issue planning / execution と同様に、skill 側へ first-read workflow spine を置く対象に昇格する。
- docs と templates も同時に整える必要があるため、skill-only fix ではなく、skill / docs / templates 横断の修正 issue として扱う。
