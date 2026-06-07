---
種別: research
ID: "20260607t050635z-research"
タイトル: "ChatGPT Post First Wave PDCA Direction"
状態: "completed"
作成者: "codex"
最終更新: "2026-06-07"
親: ["epic-00158"]
関連:
  - "iss-00159"
  - "iss-00162"
  - "iss-00163"
  - "iss-00164"
  - "iss-00165"
  - "iss-00166"
  - "iss-00167"
authority: "synthesized"
derived_from:
  - "ChatGPT thread A 現状評価とリスク監査: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f30c-0ab0-83ab-9f49-bd9f1666eba3"
  - "ChatGPT thread B 展開可能性と技術方式: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f316-950c-83a3-979f-600c3ab28419"
  - "ChatGPT thread C 具体ロードマップと計画ベストプラクティス: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f350-1700-83a8-b0c4-121bc6a6985f"
reflected_to: []
---

# 20260607t050635z-research ChatGPT Post First Wave PDCA Direction

## 位置づけ

この文書は、`epic-00158 Agent Workflow PDCA Hardening` の first wave 実施後に、ChatGPT じっくり思考 Pro 相当の外部分析を 3 スコープで依頼し、今後の方針検討に使える evidence として統合した research である。

Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の authority ではない。今後の issue 化、ADR 化、または Epic report の Evidence Adoption Ledger へ採用する場合は、main orchestrator が採否を判断して記録する。

## 調査目的 (必須)

- First wave で採用した「skills = first-read workflow spine、docs = detailed semantics、templates = scaffolds/examples、discussions/research/sub-agent/ChatGPT output = evidence」という分離を、実施後の状態として評価する。
- 現在の更新がユーザーの問題仮説にどの程度効いているか、残存 risk は何か、次 wave で何を観測・実装すべきかを整理する。
- Runtime gate / regression checks / manual harness / telemetry / status command などの技術方式を比較し、次の具体 issue 化に使える候補を得る。

## sources / 調査方法 (必須)

- ローカル確認:
  - `./spec-dock/scripts/spec-dock active show`
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/epic/{requirement,design,plan,report}.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-*.md`
  - `spec-dock/active/epic/issues/iss-*/.meta.json`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/templates/`
- ChatGPT 依頼:
  - Scope A: 現状評価とリスク監査。
  - Scope B: 展開可能性と技術方式。
  - Scope C: 次の具体ロードマップと計画ベストプラクティス。
- ChatGPT への提示制約:
  - supplied context と public repo URL を中心に評価する。
  - Project 内の過去会話や通常 memory に依存しない。
  - Matt Pocock 氏の Grill with me / Grill with dog に関する一般知識は未検証なら明記する。
- 実行環境:
  - ChatGPT Codex-only Project 内で 3 スレッドを作成。
  - 生成完了後、DOM から assistant response を抽出。
  - ChatGPT 側は公開 GitHub / public information を一部参照したと自己申告しているが、Codex 側ではその外部参照内容を個別再検証していない。

## facts / 観測できた事実 (必須)

- Active state は `init-local-00003` / `epic-00158`、active issue は none。
- GitHub remote は `https://github.com/chemitaro/spec-dock.git`。
- `epic-00158` は accepted ADR として次を持つ:
  - skills own operational workflow spine。
  - docs own meanings/details/policy/hard cases。
  - templates own scaffolds/evidence slots/examples and are not compliance authorities。
  - `spec-dock-clarification` is skill-owned source-grounded grill workflow。
  - first wave は context-surface cleanup を優先し、regression / harness / runtime gates は deferred。
- Epic 配下には `iss-00159` から `iss-00166` の first wave issue と、後段 testing infrastructure lane として `iss-00167` が存在する。
- 現在の `spec-dock-issue-planning/SKILL.md` は `Mandatory Issue Authoring Workflow` を持ち、requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> execution handoff を first-read surface に出している。
- 現在の `spec-dock-clarification/SKILL.md` は source-grounded grill loop を skill-owned とし、read sources、provisional understanding、gap classification、one pressure-test question、artifact capture、answer adoption、iterate/handoff を明示している。
- 現在の hub skill は skills/docs/templates の責務分離を global invariant として述べ、leaf skills に workflow spine を委ねている。
- ChatGPT A は総合評価を `4 / 5` とし、「context surface architecture が整った」段階であって「agent behavior が安定した」証明ではないと評価した。
- ChatGPT B は、全 workflow を skill-owned にするのではなく、agent が最初の 30 秒で誤ると phase 越境・権限逸脱・証跡欠落を起こす箇所だけ skill spine 化すべきと評価した。
- ChatGPT C は、次 wave は runtime gate 強制からではなく、manual probe baseline、static drift detection、report ledger / reviewer evidence の最小 schema 固定から始めるべきと提案した。

## inference / 推測 (必須)

- 事実から推測したこと:
  - First wave の方向性は妥当で、ユーザーの問題仮説に直接対応している。
  - ただし、first wave は主に文書・skill・template surface の整備であり、agent 行動の一貫性向上はまだ観測によって証明されていない。
  - 次 wave の主目的は「さらに workflow text を増やす」ではなく、「drift を検出する」「agent が実際に止まる/戻る/証跡を残すかを観測する」「将来 runtime gate が参照できる evidence schema を薄く整える」ことである。
- 推測の根拠:
  - ChatGPT A/B/C がいずれも、runtime enforcement より先に manual / synthetic probe、static drift lint、report schema v0 を推奨している。
  - Epic plan でも regression checks / harness / runtime gates は deferred とされており、first wave 後の revisit 条件に合う。
  - `iss-00167` の pytest migration は重要な testing infrastructure だが、skill/docs/templates 分離による agent behavior 改善の直接 evidence ではない。

## unverified / 未検証事項 (必須)

- まだ確認していないこと:
  - First wave 後の agent が、実際に stale reviewer、missing EAL、unresolved gap、template-only evidence、sub-agent draft direct adoption などで停止できるか。
  - `workflow_clarification.md` を含む docs 側の residual wording drift が、実際の agent 読解で誤誘導になるか。
  - report ledger の現在の記録量が、実運用で boilerplate 化していないか。
  - ChatGPT B が参照した公開 GitHub / public information の細部。
  - Matt Pocock 氏の `Grill with dog` という名称・由来・原典。
- 確認できない理由:
  - 今回は ChatGPT discussion とローカル source inspection が主目的であり、別 agent による empirical probe はまだ実行していない。
  - ChatGPT Web の回答中に含まれる外部参照は、Codex 側で個別 source verification していない。
  - `Grill with dog` は ChatGPT B も「公開情報で確認できず、grill-me / grill-with-docs は確認できた」としている。

## question candidates / 質問候補 (必須)

- source-grounded に解けず、人間判断が必要な候補:
  - 次 wave の最初の issue は、manual probe baseline と static drift detection のどちらを先に切るか。
  - Runtime gate を hard blocker として扱う最初の条件をどこに置くか。
  - Report ledger の最小 schema をどの粒度で固定するか。
- pressure-test question として切り出すべき候補:
  - 「次 wave の主目的は、agent behavior の empirical evidence を集めることか、それとも context surface drift の機械的検出を先に固定することか」
- 質問せずに解決できた候補:
  - `iss-00167` は first wave の置換ではなく、deferred testing / regression infrastructure lane として扱う。
  - `workflow_clarification.md` は mandatory runbook authority ではなく bridge/reference として扱う。

## terminology conflicts / 用語衝突 (必須)

- 衝突している用語:
  - `workflow_clarification.md`
- 既存 docs / code / tests / discussions での使われ方:
  - ADR では `workflow_clarification.md` は bridge/reference とされる。
  - 一方で docs 側のリンクや説明では「Clarification workflow」または workflow doc として残る箇所がある。
- 判断が必要な理由:
  - 「workflow」というファイル名・リンク名自体は互換性上残せるが、agent が primary runbook authority と誤読する場合は first wave の目的と衝突する。
  - ただし docs から workflow detail を全面削除すると hard cases / lifecycle semantics の置き場を失うため、削るべきなのは detail ではなく primary authority に見える表現である。

## edge cases / 具体シナリオ (必須)

- stale reviewer:
  - Agent が `review_status: pass` の古い結果を current artifact に流用しようとする。
  - 影響: phase promotion を誤る。manual probe / static report check / future status command の候補。
- template-only evidence:
  - Template slot が埋まっているだけで pass / completion と誤認する。
  - 影響: templates as scaffold の境界を崩す。template authority phrase denylist の候補。
- delegated draft laundering:
  - Sub-agent / ChatGPT output を EAL 採用なしに canonical authority として扱う。
  - 影響: main orchestrator ownership が崩れる。report ledger schema v0 と adoption check の候補。
- over-questioning clarification:
  - Grill pattern を広げすぎて、local source で解けることまで人間に聞く。
  - 影響: clarification skill が source-grounded ではなく generic coaching になる。one-question + source-read-first probe が必要。
- premature runtime gate:
  - Free-text report を status command が解釈し、false positive / false negative を生む。
  - 影響: wrong stop condition の固定化。schema v0 -> advisory status -> hard gate の順が望ましい。
- skill bloat:
  - Details / field semantics / examples / hard cases まで skill にコピーされる。
  - 影響: skill が読まれにくくなり、docs との drift が増える。spine manifest / token budget / section checks が必要。

## implications / 判断への含意 (必須)

- 次 wave の優先 top 3:
  1. `Add Manual Agent Workflow Probe Baseline`
     - 目的: first wave 後の agent が、代表 scenario で止まる/戻る/証跡を残すかを観測する。
     - scope: 10-15 個程度の scenario table、expected behavior、manual dogfooding result、rubric。
     - non-scope: CI blocking、runtime enforcement、large harness。
     - verification: scenario ごとの expected vs observed、failure taxonomy、follow-up mapping。
  2. `Add Context Surface Drift Checks`
     - 目的: skill/docs/templates の責務分離が将来の変更で崩れないようにする。
     - scope: static checks for required sections, semantic tokens, forbidden authority phrases, provider/mirror identity, docs bridge wording。
     - non-scope: behavioral proof、runtime gate、full semantic parser。
     - verification: checks fail on fixture / known bad example and pass current repo。
  3. `Define Report Ledger Schema V0`
     - 目的: future status / runtime gate / evidence audit の前提になる最小 machine-readable evidence contract を作る。
     - scope: EAL, Spec Authoring Gate, Reviewer Gate Status, Delegated Draft Evidence の minimum fields / states / blocking semantics。
     - non-scope: strict legacy validation, database migration, hard runtime gate。
     - verification: current first-wave issue reports can be classified without excessive false failures。
- その後の候補:
  - `Add Synthetic Scenario Harness`
  - `Add Skill Spine Regression Checks To CI`
  - `Add Docs Link Authority Audit`
  - `Add Advisory Spec Dock Status Command`
  - `Add Reviewer Gate Freshness Read Model`
  - `Add Runtime Issue Start Readiness Advisory`
  - `Add Runtime Issue Finish Evidence Guard`
  - `Add Agent Workflow Telemetry Opt In`
  - `Audit Ledger Burden And Boilerplate`
- 推奨順序:
  - manual probes
  - static drift checks
  - report schema v0
  - synthetic scenario harness
  - advisory status command
  - limited runtime hard gates
  - opt-in telemetry
- 重要な制約:
  - Runtime enforcement は後段で有用だが、manual / synthetic evidence と report schema がない段階で hard blocker 化しない。
  - Templates は evidence slot を増やしても pass 条件・compliance authority にしない。
  - `spec-dock status` は new source of truth ではなく、canonical docs / report / runtime state の summary とし、根拠 path/hash/verdict を出す。

## リスク/制約 (任意)

- ChatGPT output は third-party evidence であり、canonical docs への採用には EAL が必要。
- ChatGPT は一部公開 GitHub を参照したと述べているが、Codex 側の現在ターンではその参照先を逐一検証していない。
- Manual probes は非決定的であり、最初から CI blocking に向かない。
- Static checks は文言変更で壊れやすい。Exact string より section + semantic token + forbidden phrase を使い、意図的変更の allowlist / reviewer override を設計する。
- Telemetry は privacy / host dependency / noise が重い。Opt-in、local-only、secret/path allowlist が必要で、self-reported telemetry を compliance evidence にしない。

## 反映先 (任意)

- reflected_to:
  - 未反映。
- 採用候補:
  - Epic `report.md` の Evidence Adoption Ledger。
  - Next-wave issue requirement / design / plan。
  - Deferred work の priority update。
  - Future ADR: report ledger schema v0 / advisory status command / runtime gate hardening order。

## 参考（References） (任意)

- ChatGPT thread A 現状評価とリスク監査:
  - https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f30c-0ab0-83ab-9f49-bd9f1666eba3
- ChatGPT thread B 展開可能性と技術方式:
  - https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f316-950c-83a3-979f-600c3ab28419
- ChatGPT thread C 具体ロードマップと計画ベストプラクティス:
  - https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a24f350-1700-83a8-b0c4-121bc6a6985f
- Local active docs:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
- Accepted ADRs:
  - `spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md`
