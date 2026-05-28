---
種別: scratch
ID: "scratch-20260528t004700z"
タイトル: "ChatGPT initial analysis prompt for Matt Pocock skills integration"
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t004419z"]
authority: "raw"
derived_from:
  - "discussions/20260528t004419z-research-mattpocock-skills-source-capture.md"
  - "discussions/mattpocock-skills-source/"
reflected_to: []
---

# scratch-20260528t004700z ChatGPT initial analysis prompt for Matt Pocock skills integration

## メモ

# 目的
spec-dock に Matt Pocock さんの skills repository のエッセンスを取り入れるため、初回の設計分析をしてください。これは ChatGPT 5.5 Pro / じっくり思考 Pro による深い外部分析として使います。

# 重要な前提
- 通常の個人メモリや過去チャット履歴ではなく、このプロンプトと公開 repo / 取り込み済み source capture の情報に基づいてください。
- 今回は「何度も Web を見に行く」のではなく、spec-dock の issue-local discussions に Matt Pocock skills の Markdown/manifest 原文 snapshot を取り込んだ前提で分析します。
- あなたはその source capture の要点と file inventory を一次 evidence として扱ってください。足りない場合だけ、公開 repo URL を確認し、確認したかどうかを明示してください。
- 未確認の推測は必ず「未検証」とラベルしてください。

# 対象 public repos
- Matt Pocock skills: https://github.com/mattpocock/skills
- spec-dock: https://github.com/chemitaro/spec-dock

# spec-dock 側の現在の active issue
- GitHub issue: https://github.com/chemitaro/spec-dock/issues/134
- Issue ID: iss-00134
- Title: Adopt Matt Pocock grill skill review patterns
- Active local path:
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/
- 現在の issue requirement/design/plan はまだ scaffold に近く、今回の調査・壁打ちで内容を具体化する段階です。

# spec-dock の概要
spec-dock は、既存 repo に spec-driven documentation workspace を scaffolding する CLI です。導入後は generated files を repo-local に使います。
主要構造:
- spec-dock/initiatives/: Initiative -> Epic -> Issue の仕様ツリー
- spec-dock/active/: 現在の active initiative/epic/issue への symlink entrance
- spec-dock/.agent/: sync で生成される index/tree/dependency state
- spec-dock/templates/discussions/: research/disc/interview/scratch/adr templates
- .agents/skills/: shared skill assets
- .codex/agents, .codex/prompts, .github/agents: host-specific agent/tooling assets

README 上の runtime command 例:
- ./spec-dock/scripts/spec-dock new initiative/epic/issue
- ./spec-dock/scripts/spec-dock issue start <target>
- ./spec-dock/scripts/spec-dock issue finish
- ./spec-dock/scripts/spec-dock sync
- ./spec-dock/scripts/spec-dock validate

# active epic の境界
active epic は agent-tooling assets の source-of-truth と installed layout を揃えるものです。
重要な前提:
- provider-side authority: src/spec_dock/assets/install_root/
- install_root は consumer repo の installed layout と同型
- .agents は shared layer、.codex は Codex-specific、.github は GitHub-specific
- installer は structure-preserving sync を行う
- spec-dock/ は dogfooding workspace であり、provider authority は src/spec_dock/assets/ 側

# 現在の spec-dock skill / agent-tooling surface
provider-side skills:
- spec-driven-tdd-workflow
- spec-dock-initiative-planning
- spec-dock-epic-planning
- spec-dock-issue-execution
- spec-dock-adr-facilitation
- spec-dock-system-architect
- spec-dock-implementation-planner
- spec-dock-codex-adapter
- spec-dock-copilot-adapter
- git-commit-conventional-ja
- github-pr-creator
- github-pr-merge-preparer
- github-codex-pr-review-comments

provider-side Codex agents include:
- spec-manager, spec-reviewer, system-architect, implementation-planner, repo-analyst, researcher, dev-coder, doc-writer, code-reviewer, qa-reviewer, consultant, deep-consultant, pr-monitor, worker, utility-worker

# Matt Pocock skills source capture
Local issue discussion path:
- discussions/mattpocock-skills-source/
Source repo HEAD snapshot:
- commit: 0288510dd61ff6ef7c2003834082ab8f2387e80e
- date: 2026-05-27T12:36:22Z
Captured files:
- root docs: README.md, CONTEXT.md, CLAUDE.md, LICENSE
- plugin manifest: .claude-plugin/plugin.json
- docs/adr/0001-explicit-setup-pointer-only-for-hard-dependencies.md
- all skill Markdown docs and SKILL.md files under skills/**
- excluded for now: executable scripts

# Matt Pocock skills inventory and observed essence
README says the repository is "Skills For Real Engineers": small, adaptable, composable agent skills for real engineering, positioned against heavy process-owning systems. It identifies common failure modes: agent/user misalignment, verbose or inconsistent domain language, weak feedback loops, and codebase entropy.

Key skills captured:
- productivity/grill-me: interview the user relentlessly about a plan/design until shared understanding is reached; walk each branch of decision tree; ask questions one at a time; if codebase can answer, explore instead.
- engineering/grill-with-docs: same grilling loop, but docs-aware. It checks domain language against CONTEXT.md, sharpens fuzzy terms, discusses concrete scenarios, cross-references with code, updates CONTEXT.md inline when terms are resolved, and offers ADRs sparingly only for hard-to-reverse, surprising, real-tradeoff decisions.
- engineering/to-prd: synthesize current conversation/codebase understanding into a PRD. It explores repo, uses domain glossary vocabulary, identifies modules/deep modules, asks user to confirm modules/tests, then writes problem, solution, user stories, implementation decisions, testing decisions, out of scope, notes.
- engineering/to-issues: break plan/PRD into independently grabbable vertical-slice issues; distinguish HITL vs AFK slices; publish dependency-ordered issues.
- engineering/tdd: behavior-first red-green-refactor; one vertical tracer bullet at a time; public interfaces, not implementation details; avoid horizontal "all tests then all code".
- engineering/improve-codebase-architecture: find deepening opportunities using domain language and ADRs; focus on interface/implementation/depth/seam/adapter/leverage/locality; produce visual HTML report, then grill selected candidate.
- engineering/setup-matt-pocock-skills: repo-local setup for issue tracker, triage label vocabulary, and domain docs layout.

# spec-dock discussion artifact model relevant to this issue
- research: external facts / implementation facts / evidence. Facts, inference, unverified items, and implications must be separated.
- disc: options, tradeoffs, recommendation, open questions.
- interview: human questions and answers with rationale and reflection targets.
- scratch: raw low-friction notes.
- adr: long-term architecture decisions only, not generic notes.

# 今回の分析で答えてほしいこと
1. Matt Pocock skills の思想・パターンを、spec-dock の現行 workflow / skill / agent architecture にどう対応づけるべきか。
2. `grill-me` と `grill-with-docs` のどちらを、spec-dock の要件定義壁打ちに採用・変形すべきか。単純移植ではなく、spec-dock の active docs / discussions / ADR / lifecycle と整合する形を考えてください。
3. spec-dock に追加するとよさそうな skill / phase / discussion workflow / agent role を、具体名・責務・入力・出力・artifact path・禁止事項まで提案してください。
4. Matt Pocock skills の何を「そのまま採用」、何を「spec-dock 風に変形」、何を「採用しない」べきか分類してください。
5. 最高に良い統合ビジョンを作るために、次の ChatGPT follow-up loop で深掘りすべき質問を 5〜10 個、優先順位つきで出してください。
6. この回答をそのまま spec-dock の discussions/research または discussions/disc に転記しやすい Markdown 構造にしてください。

# 望ましい出力形式
- TL;DR
- Evidence map: Matt Pocock pattern -> spec-dock surface
- Recommended integration vision
- Grill-me vs grill-with-docs decision analysis
- Candidate new skills / workflows table
- Adopt / adapt / reject classification
- Risks and unresolved questions
- Next follow-up prompts for deeper ChatGPT loop
- Discussion artifact draft outline
