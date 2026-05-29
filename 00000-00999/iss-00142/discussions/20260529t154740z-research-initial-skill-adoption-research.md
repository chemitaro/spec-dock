---
種別: research
ID: "20260529t154740z-research"
タイトル: "Initial Skill Adoption Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["iss-00142"]
関連: ["#142", "iss-00134"]
authority: "synthesized"
derived_from:
  - "iss-00134 discussions/mattpocock-skills-source/source-metadata.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/diagnose/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/tdd/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/to-issues/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/to-prd/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/triage/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/improve-codebase-architecture/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/engineering/prototype/SKILL.md"
  - "iss-00134 discussions/mattpocock-skills-source/skills/productivity/handoff/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md"
reflected_to: []
---

# 20260529t154740z-research Initial Skill Adoption Research

## 位置づけ
- この文書は、`iss-00142 Matt Pocock Skill Adoption Analysis` の初期作業環境メモ兼 research report である。
- 目的は、`grill-me` / `grill-with-docs` 以外の Matt Pocock skills を、spec-dock にどのように適用できるかを徹底調査するための出発点を残すことである。
- まだ `requirement.md` / `design.md` / `plan.md` を作り込まない。まずは `discussions/` に source-grounded な調査、分析、採用候補、見送り理由、衝突リスクを積み上げる。
- この文書の内容は採用済み canonical decision ではない。後続作業で追加調査、consultant / deep-consultant レビュー、必要なら interview artifact を経て canonical docs へ反映する。

## 調査目的 (必須)
- Matt Pocock skills source snapshot のうち、既に `docs-aware clarification workflow` として取り込み中の `grill-me` / `grill-with-docs` 以外を対象に、spec-dock へ取り込む価値がある概念、workflow、skill 候補を洗い出す。
- 候補を「そのまま skill 追加」「既存 workflow / docs / template / agent guidance へ概念吸収」「別 issue で検討」「見送り」に分類する。
- 既存 spec-dock の authority model、provider-side asset source of truth、dogfooding workspace、canonical docs single-writer、fresh reviewer gate、issue execution readiness と衝突しない取り込み方を明らかにする。
- 次の担当者がこの issue で何を調査すべきか、どの source を読めばよいか、どこから始めればよいかを共有する。

## sources / 調査方法 (必須)
- 参照先:
  - `iss-00134` の既存 requirement / design / discussions。
  - `iss-00134/discussions/mattpocock-skills-source/` に取り込まれた Matt Pocock skills local snapshot。
  - `src/spec_dock/assets/install_root/.agents/skills/` 配下の現行 spec-dock skill。
  - `spec-dock/docs/workflow_clarification.md`、`workflow_issue.md`、`workflow_spec_authoring.md`、`phase_plan_issue.md`、`authoring/issue-plan.md`。
  - consultant / deep-consultant による役割分担分析。
- 検証手順:
  - local snapshot の `SKILL.md` 一覧を取得し、`grill-me` / `grill-with-docs` を除く engineering / productivity / misc / deprecated / in-progress skills を確認した。
  - `diagnose`、`tdd`、`to-issues`、`to-prd`、`triage`、`improve-codebase-architecture`、`prototype`、`handoff`、`write-a-skill`、`setup-matt-pocock-skills` などを重点的に読んだ。
  - 現行 spec-dock skill との重複と衝突を確認した。
  - consultant には優先度付き適用候補分析、deep-consultant には長期設計上の採用・見送り判断を依頼した。
- 実験条件:
  - source snapshot は `source_commit: 0288510dd61ff6ef7c2003834082ab8f2387e80e`、`captured_at: 2026-05-28` の local capture。
  - GitHub upstream の最新状態はこの調査では再取得していない。現時点では local capture を安定証拠として扱う。
  - executable helper scripts は snapshot 対象外であり、scripts の挙動には依存していない。

## facts / 観測できた事実 (必須)
- `iss-00134` は Matt Pocock の `grill-me` / `grill-with-docs` 由来の考え方を、無加工移植ではなく `docs-aware clarification workflow` として spec-dock-native に翻訳する方針を持っている。
- `spec-dock-clarification` は既に source-grounded read、一問一答、unanswered `interview` artifact、domain language sharpening、ADR sparingly、analysis-only / draft-only mode を扱う entrypoint として存在する。
- `spec-driven-tdd-workflow` は `workflow_clarification.md`、issue planning、issue execution、system architect、implementation planner への routing hub として存在する。
- `spec-dock-issue-execution` は、approved / reviewer-pass 済みの `requirement.md` / `design.md` / `plan.md` と executable `plan.md` を implementation handoff 前提としている。
- `spec-dock-system-architect` / `spec-dock-implementation-planner` は、canonical docs を直接編集せず、scope-local `discussions/` に flat Markdown evidence を作る delegated authoring model を持つ。
- Matt Pocock `diagnose` は、hard bug / performance regression に対して feedback loop、reproduce、ranked hypotheses、instrument、fix + regression test、cleanup + post-mortem を明確に要求している。
- Matt Pocock `tdd` は、public interface / observable behavior、one test at a time、vertical slice、horizontal test batching 禁止、refactor は GREEN 後、mock は system boundary に限定、を明示している。
- Matt Pocock `to-issues` は、plan / spec / PRD を tracer bullet vertical slices に分割し、HITL / AFK、dependency order、issue body を扱う。
- Matt Pocock `improve-codebase-architecture` は、deep module、interface、seam、adapter、deletion test、interface as test surface、locality / leverage という強い architecture vocabulary を持つ。
- Matt Pocock `triage` は issue tracker label state machine と `ready-for-agent` / `ready-for-human` / `needs-info` などの状態を扱う。
- Matt Pocock `prototype` は throwaway prototype を使って design question を検証し、終了時に delete or absorb を求める。
- Matt Pocock `handoff` は temp directory に handoff document を作成し、既存 artifact は重複せず参照する方針を持つ。
- `setup-matt-pocock-skills` は `AGENTS.md` / `CLAUDE.md` と `docs/agents/` に repo-specific setup を書く前提である。
- local snapshot は MIT License である。ただし license 上可能でも、spec-dock へは設計上「直接移植」ではなく「spec-dock-native translation」が必要である。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 新規 skill を大量に追加するより、既存 spec-dock workflow / skill / template へ思想を吸収する方が安全である。
  - そのまま first-class skill として検討する価値が最も高いのは `spec-dock-diagnosis` である。
  - `diagnose`、`tdd`、`to-issues` は P0 として concept adoption 価値が高い。
  - `improve-codebase-architecture` は独立 skill ではなく `spec-dock-system-architect` や design / ADR guidance に短く吸収するのがよい。
  - `handoff` は context-pack / report と競合しない session handoff utility としてなら低リスクで導入できる。
  - `triage` と `prototype` は魅力はあるが、spec-dock の status / readiness / artifact lifecycle と衝突しやすいため別 issue で扱うべきである。
- 推測の根拠:
  - spec-dock は既に single-writer canonical docs、discussion evidence、fresh reviewer pass、issue execution readiness を持っており、Matt skills の直接 workflow を追加すると入口と authority が増えすぎる。
  - consultant と deep-consultant の分析はどちらも、skill proliferation を避けて既存 governance に接続する方針を推奨した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - GitHub upstream の Matt Pocock skills が local snapshot 以後に変更されているか。
  - excluded helper scripts の中に、spec-dock へ参考になる deterministic helper が含まれるか。
  - `workflow_issue.md` / `authoring/issue-plan.md` / `phase_plan_issue.md` のどこに TDD / diagnose / vertical slice 概念を置くのが最小で読みやすいか。
  - `spec-dock-diagnosis` を独立 skill として追加するか、`spec-dock-issue-execution` に収めるか。
  - `triage` を GitHub intake adapter として設計する場合、spec-dock node creation / GitHub issue sync / label state とどう整合させるか。
  - `prototype` を採用する場合の保存先、削除/吸収 gate、report evidence、cleanup guarantee。
- 確認できない理由:
  - 今回のユーザー依頼は作業環境整備と初期調査レポート作成であり、要件定義書や設計書の作り込みはまだ行わないため。
  - scripts capture は `iss-00134` の snapshot scope から外れているため。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `ready-for-agent`
  - `PRD`
  - `CONTEXT.md`
  - `issue`
  - `handoff`
  - `review`
- 既存 docs / code / tests / discussions での使われ方:
  - Matt Pocock `ready-for-agent` は issue tracker label state の一つであり、AFK agent が着手可能という意味を持つ。
  - spec-dock の implementation readiness は、approved / reviewer-pass `requirement.md` / `design.md` / `plan.md`、executable `plan.md`、report evidence、issue execution handoff によって決まる。
  - Matt Pocock `PRD` は product requirements document として issue tracker に publish される想定だが、spec-dock では `requirement.md` / `design.md` / `plan.md` が canonical authoring artifacts である。
  - Matt Pocock `CONTEXT.md` は domain language の正本として扱われるが、spec-dock では active docs、parent docs、`discussions/`、source/tests/templates が context source であり、`CONTEXT.md` を新しい正本にしない方針が既にある。
  - Matt Pocock `issue` は主に external issue tracker item を指すが、spec-dock issue は initiative / epic 配下の local node と GitHub issue mirror を含む。
  - `handoff` は Matt Pocock skill では temp handoff document、spec-dock では context-pack / active docs / report / issue start handoff と意味が重なる。
  - `review` は Matt Pocock in-progress skill では standards/spec review の並列分析に近いが、spec-dock では fresh `spec-reviewer` pass が phase gate として独立している。
- 判断が必要な理由:
  - これらの語をそのまま導入すると、spec-dock の readiness / authority / source-of-truth model を壊す可能性がある。
  - 後続の requirement / design では、外部 skill の語を採用する場合に spec-dock-native な別名または明確な変換ルールが必要である。

## edge cases / 具体シナリオ (必須)
- edge case:
  - `triage` が GitHub issue に `ready-for-agent` label を付けたが、spec-dock 側の `requirement.md` / `design.md` / `plan.md` が reviewer-pass していない。
  - `diagnose` が bug fix を進めたいが、再現 loop が作れない。
  - `tdd` がすべてのテストを先に書こうとし、spec-dock の executable plan と乖離した horizontal slicing になる。
  - `improve-codebase-architecture` が `CONTEXT.md` や ADR を直接更新しようとする。
  - `prototype` が throwaway code を repo 内に残したまま issue completion へ進もうとする。
  - `handoff` が既存 `context-pack.md` や `report.md` と同じ情報を重複要約し、どれが最新かわからなくなる。
- その edge case が requirement / design / plan に与える影響:
  - `ready-for-agent` は spec-dock の implementation readiness と同義にしない。
  - bug / performance issue では、再現 loop failure 自体を planning / report evidence として扱う必要がある。
  - TDD guidance は behavior slice / public interface / one test at a time を `plan.md` field semantics と接続する必要がある。
  - architecture guidance は canonical docs direct write ではなく `discussions/` evidence -> orchestrator adoption -> canonical reflection に接続する必要がある。
  - prototype guidance を入れるなら cleanup gate を受け入れ条件に含める必要がある。
  - handoff guidance は existing artifact references first、duplication last のルールが必要である。

## implications / 判断への含意 (必須)
- P0 candidate:
  - `diagnose`: `spec-dock-issue-execution` または新規 `spec-dock-diagnosis` として、bug / performance issue 用の feedback-loop-first discipline を導入する。
  - `tdd`: `workflow_issue.md` / `phase_plan_issue.md` / `authoring/issue-plan.md` に public-interface behavior test、vertical tracer bullet、horizontal batching 禁止を追加する。
  - `to-issues`: epic -> issue / plan -> issue decomposition に vertical slice、HITL/AFK、dependency order の考え方を吸収する。
- P1 candidate:
  - `improve-codebase-architecture`: `spec-dock-system-architect` と design/ADR docs に deep module、deletion test、interface as test surface、locality/leverage を短く吸収する。
  - `zoom-out`: 独立 skill より repo map / caller map を求める prompt pattern として扱う。
- P2 candidate:
  - `handoff`: temp handoff utility として検討。ただし `context-pack.md` / `report.md` と競合させない。
  - `write-a-skill`: skill description trigger、progressive disclosure、script 化基準を provider-side skill authoring guidance に吸収する。
- P3 / follow-up:
  - `triage`: GitHub intake adapter として別 issue で検討する。
  - `prototype`: experimental workflow として別 issue で検討する。削除/吸収 gate なしでは採用しない。
- 見送り:
  - `setup-matt-pocock-skills`、`to-prd` artifact、`setup-pre-commit`、`git-guardrails-claude-code`、personal / writing / teach / exercises / migration-specific skills。

## リスク/制約 (任意)
- Matt Pocock skills を増やしすぎると、spec-dock の entrypoint が分散し、agent がどの workflow を使うべきか迷う。
- `CONTEXT.md` / `docs/agents` / PRD / GitHub label state を別正本として導入すると、spec-dock の canonical docs と provider-side assets の authority が割れる。
- `diagnose` や `tdd` を直接 skill 化すると、approved specs / reviewer pass / executable plan を飛ばして実装に入る誤用が起きうる。
- 取り込みは、まず docs / template / existing skill guidance への最小概念追加で検証し、必要が明確になったものだけ first-class skill にするべきである。

## 反映先 (任意)
- reflected_to:
  - `requirement.md`: この issue が扱う調査範囲、非目的、分類方針。
  - `design.md`: 既存 workflow / skill / template への取り込み設計。
  - `plan.md`: P0/P1/P2 の段階的調査・実装順序。
  - `workflow_issue.md` / `phase_plan_issue.md` / `authoring/issue-plan.md`: TDD / diagnose / vertical slice guidance。
  - `spec-dock-system-architect` skill: architecture deepening heuristics。
  - `spec-dock-issue-execution` skill: bug diagnosis feedback-loop guidance。

## 参考（References） (任意)
- 作業環境:
  - issue: `iss-00142 Matt Pocock Skill Adoption Analysis`
  - GitHub issue: `#142`
  - worktree: `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-matt-pocock-skill-adoption-analysis`
  - branch: `iss-00142-matt-pocock-skill-adoption-analysis`
  - active issue start: 完了
- この issue で取り組むべきこと:
  - `grill-me` / `grill-with-docs` 以外の Matt Pocock skills をさらに読み込み、spec-dock-native な採用候補を確定する。
  - P0/P1/P2/P3 分類を source-grounded に精査する。
  - `diagnose` を独立 skill にするか既存 issue execution に吸収するかを比較する。
  - `tdd` / `to-issues` の思想を spec-dock plan / execution docs へ入れる最小場所を決める。
  - `improve-codebase-architecture` の architecture vocabulary を `spec-dock-system-architect` にどこまで入れるかを決める。
  - `triage` / `prototype` を別 issue に切る必要があるかを判断する。
- 今回の初期分析の要点:
  - そのまま skill 追加する候補は少ない。
  - `diagnose`、`tdd`、`to-issues` は最優先で思想を吸収する価値が高い。
  - `improve-codebase-architecture` は強いが、直接移植ではなく system architect / design docs に概念吸収する。
  - `handoff` は限定的な session handoff utility としてなら導入余地がある。
  - `triage` と `prototype` は別 issue の方が安全。
  - `setup-matt-pocock-skills`、`to-prd`、Claude-specific guardrails、personal/writing/teach 系は core には入れない。
