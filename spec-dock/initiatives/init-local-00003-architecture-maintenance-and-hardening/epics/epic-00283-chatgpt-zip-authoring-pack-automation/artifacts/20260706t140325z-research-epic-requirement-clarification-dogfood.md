---
種別: research
ID: "20260706t140325z-research"
タイトル: "Epic Requirement Clarification Dogfood"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t090820z-research"
  - "20260706t103820z-disc"
  - "20260706t111806z-research"
  - "20260706t114128z-research"
  - "20260706t131838z-research"
authority: "synthesized"
adoption_status: "partially_adopted"
oracle_provider: "chatgpt-use"
oracle_model: "gpt-5.5-pro"
oracle_thinking: "Pro Extended"
oracle_session_slug: "specdock-epic-00283-requiremen-clarificat"
local_head_sha: "918e624b8a97a4c67bd5ac1ac4ff552999b64bbb"
local_branch_state: "detached-head"
derived_from:
  - "/private/tmp/codex-agent-work/501/session-20260706t135003z-specdock-epic-00283-requirement-clarification-f03a8e52/epic-00283-requirement-clarification-brief.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t135003z-specdock-epic-00283-requirement-clarification-f03a8e52/epic-00283-requirement-clarification-output.md"
reflected_to:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/requirement.md"
---

# 20260706t140325z-research Epic Requirement Clarification Dogfood

## 調査目的

`epic-00283 ChatGPT Zip Authoring Pack Automation` の要件定義書を書く前に、ここまでの research / discussion artifact と workflow docs を source として、追加インタビューが必要な user-intent blocker が残っているかを確認する。

同時に、将来作る `ChatGPT ZIP Authoring Pack Automation` の機能を、まだ script がない状態で manual prompt により dogfood する。

## sources / 調査方法

### 参照先

- `epic-00283` scaffold:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- `epic-00283/artifacts/` に移動した既存 research / disc:
  - `20260706t090820z-research-chatgpt-oracle-advanced-analysis.md`
  - `20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md`
  - `20260706t111806z-research-chatgpt-reviewer-gate-script-analysis.md`
  - `20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices.md`
  - `20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control.md`
  - `20260706t133043z-chatgpt-zip-authoring-onboarding-brief.md`
- Parent / sibling context:
  - `init-local-00003` requirement / design / plan
  - `epic-00158` requirement
  - `epic-00224` requirement
  - `epic-00270` requirement
- Workflow docs:
  - `workflow_spec_authoring.md`
  - `workflow_epic.md`
  - `workflow_clarification.md`
  - `workflow_issue.md`
  - `phase_requirement.md`
  - `phase_design.md`
  - `phase_plan.md`
  - `phase_plan_epic.md`
  - `authoring/scope-layering.md`
  - `authoring/decision-routing.md`
  - `reference_naming.md`
- Skills:
  - `spec-dock-hub`
  - `spec-dock-clarification`
  - `spec-dock-epic-planning`

### 検証手順

- `chatgpt-use` skill の `/Users/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt` を直接実行した。
- dry-run で 32 files / 約 146,207 tokens の bundle になることを確認した。
- live run で GPT-5.5 Pro Extended に、source-grounded provisional understanding、gap classification、pressure-test question、requirement draft、candidate Issue seeds、dogfood observations を依頼した。
- ChatGPT output は advisory evidence として扱い、local workflow docs と既存 research に照合してから `requirement.md` へ部分採用した。

### 実験条件

- 実行日: 2026-07-06
- Oracle session: `specdock-epic-00283-requiremen-clarificat`
- ChatGPT: GPT-5.5 Pro Extended
- GitHub connector:
  - `chemitaro/spec-dock` と GitHub Issue `#283` は確認された。
  - `Current branch: unavailable` は branch ref として開けず、ChatGPT 側は default branch `main` を検査した。
- local checkout:
  - detached HEAD
  - local HEAD: `918e624b8a97a4c67bd5ac1ac4ff552999b64bbb`

## facts / 観測できた事実

- ChatGPT は、`epic-00283` を ChatGPT Use / GPT-5.5 Pro Extended を SpecDock の structured authoring backend として使うための dogfood-first automation Epic と整理した。
- ChatGPT は、この Epic の対象を「ChatGPT に正本を書かせる runtime」ではなく、「ChatGPT が返す ZIP / structured pack を untrusted evidence delivery format として受け取り、quarantine、validation、diff、staging、Evidence Adoption Ledger、fresh `spec-reviewer` gate を通じて採否判断できる workflow と script / skill / prompt surface」と定義した。
- ChatGPT は user-intent blocker について `unresolved_user_questions: none` と回答した。
- ChatGPT は source-grounded decisions として、ZIP は delivery format であり authority format ではないこと、SpecDock local workflow が control plane を持つこと、Issue grade/profile は local assurance authority に残すこと、初期実装は `manual-tests/oracle-zip-authoring/` の dogfood-only script 群に置くことを挙げた。
- ChatGPT は candidate Issue seed として、preflight/prompt pack、safe ZIP intake/schema validation、diff/staged artifact rendering、profile-controlled selected skeleton validation、candidate-only Epic to Issue ZIP、existing Issue selected-profile ZIP、mismatch/stale probe、workflow docs、dogfood metrics を提案した。

## inference / 推測

### 事実から推測したこと

- ここまでの議論と既存 research だけで、`epic-00283` の requirement draft を作成できる。
- 現時点で人間へ確認すべき blocking question はない。
- ただし、raw ZIP / extracted tree の repo durable storage、runtime promotion threshold、profile recommendation と local classify mismatch の salvage policy、Strict / Critical で ChatGPT Use を named specialist evidence として扱う将来 path は design / plan / ADR で扱う non-blocking design questions として残る。
- 今回の manual ChatGPT Use run は、将来の script が必要とする preflight fields を明確にした。特に `requested_ref`、`inspected_ref`、`branch_sensitive`、`source_paths`、`stale_if` は machine-readable に残すべきである。

### 推測の根拠

- `workflow_spec_authoring.md` は canonical adoption と reviewer gate を local workflow に残している。
- `workflow_epic.md` は Epic が cross-Issue design backbone / Issue slicing / handoff boundary を所有すると定義している。
- 既存 ZIP / grade research は、ZIP delivery と local authority boundary を分ける必要性を具体化している。
- ChatGPT output は同じ方向の source-grounded decisions を返し、blocking question を提示しなかった。

## unverified / 未検証事項

- 実際の ZIP capture / intake / validation scripts はまだ存在しない。
- ChatGPT が毎回安定して ZIP を生成できるかは未検証である。
- `manual-tests/oracle-zip-authoring/` の script surface は proposal であり、runtime contract ではない。
- `epic-00283/requirement.md` はまだ fresh `spec-reviewer` を通していない。
- 今回の ChatGPT 側は default branch `main` を見ており、local detached HEAD の全状態を GitHub connector だけで保証しているわけではない。

## question candidates / 質問候補

### source-grounded に解けず、人間判断が必要な候補

- なし。

### pressure-test question として切り出すべき候補

- なし。ChatGPT output も `Recommended Pressure-Test Question: none` を返した。

### 質問せずに解決できた候補

- 追加インタビューなしで requirement draft を作成できる。
- v1 は shipped runtime ではなく dogfood-only script とする。
- ChatGPT は evidence producer であり、reviewer gate / profile authority / canonical writer ではない。
- `--profile auto` は local assurance による resolution を意味し、ChatGPT recommendation を意味しない。

## terminology conflicts / 用語衝突

- `ZIP authoring pack`
  - 意味: ChatGPT が生成する複数ファイル delivery。
  - canonical authority ではない。
- `authority`
  - SpecDock では canonical docs / accepted ADR / `report.md` ledger が authority を持つ。
  - ChatGPT output / research / ZIP は adoption 前 evidence。
- `profile recommendation`
  - ChatGPT や candidate pack が返す提案。
  - `.assurance.json` の `authorized_profile` とは別物。
- `bundle generation`
  - ChatGPT が requirement / design / plan をまとめて出すこと。
  - phase promotion をまとめることではない。

## edge cases / 具体シナリオ

- current branch が GitHub connector から見えない:
  - branch-sensitive run では hard fail。
  - requirement clarification では default-ref + attached local sources の advisory evidence として扱い、stale_if を残す。
- ZIP に unsafe path / hidden file / binary / symlink が含まれる:
  - safe extraction 前に reject する。
- ChatGPT が `adoption_status: adopted` や reviewer pass を自己主張する:
  - unsafe authority claim として adoption-ineligible。
- Strict / Critical Issue に対して bundle ZIP が返る:
  - generation は evidence として許可できるが、canonical adoption は force staged。

## implications / 判断への含意

- `epic-00283/requirement.md` には、dogfood-only script surface、ZIP schema、safe validation、profile authority、staged adoption、fresh reviewer gate、manual fallback を explicit requirements として入れる。
- `design.md` では、control plane / data plane、ZIP lifecycle、schema、profile resolution、template rendering vs section fill、quarantine storage、validation failures を固定する。
- `plan.md` では、preflight / prompt pack、ZIP intake / validation、diff / stage、profile validation、dogfood A/B/C、docs / metrics の Issue slicing を行う。
- `report.md` には、本 artifact と先行 research artifacts の採用を Evidence Adoption Ledger に残し、requirement phase は reviewer 未実施の draft として記録する。

## リスク/制約

- ChatGPT output は高品質でも、local validation / reviewer gate の代替にはならない。
- 手動 prompt dogfood は、script が担うべき preflight / provenance / schema validation を人間が補っている状態である。
- 出力が自然文としてよく見えるほど authority confusion が起きやすい。

## 反映先

reflected_to:

- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/requirement.md`

## 参考（References）

- Prompt:
  - `/private/tmp/codex-agent-work/501/session-20260706t135003z-specdock-epic-00283-requirement-clarification-f03a8e52/epic-00283-requirement-clarification-brief.md`
- ChatGPT output:
  - `/private/tmp/codex-agent-work/501/session-20260706t135003z-specdock-epic-00283-requirement-clarification-f03a8e52/epic-00283-requirement-clarification-output.md`
