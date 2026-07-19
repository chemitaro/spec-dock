---
種別: research
ID: "20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact"
タイトル: "現行SpecDock Workflow Gap／Migration Impact調査"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-16"
親: ["init-00322"]
関連:
  - "artifacts/20260716t235120z-06-interview-skill-agent-oracle-and-model-policy.md"
  - "artifacts/20260716t235120z-10-disc-skill-topology-and-global-cutover-rationale.md"
  - "artifacts/20260716t131924z-01-research-initiative-bootstrap-repository-baseline.md"
authority: "synthesized"
derived_from:
  - "source inspection performed during the ChatGPT interview"
  - "artifacts/20260716t054458z-disc-gpt56-chatgpt-delegation-vnext-decision-registry.md"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md"
---

# 20260716t235120z-13-research-current-repository-workflow-gap-and-migration-impact 現行SpecDock Workflow Gap／Migration Impact調査

## 位置づけ

- このArtifactは、外部仕様・公開実装・現行repositoryの観測事実を、判断根拠として再利用できるよう整理する。
- 事実、推測、未検証事項、用語衝突、edge case、canonical文書への含意を分離する。
- 本文はsource-grounded evidenceであり、accepted ADRまたはcanonical三文書を上書きしない。

## 調査目的

- `chemitaro/spec-dock@3ee6d9047506a40b938407ecfffbb341a3ca76af`の現行Skill、Agent、Workflow、template、WorkbenchとvNext target architectureの差分を責務単位で整理し、Epic分割とglobal cutoverの根拠を提供する。

## sources／調査方法

- 参照先:
  - `chemitaro/spec-dock@3ee6d9047506a40b938407ecfffbb341a3ca76af`
  - `.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `.codex/agents/*.toml`と`src/spec_dock/assets/install_root/` mirror
  - `spec-dock/docs/workflow_*`、template、PR #323
- 検証手順:
  - 現行SkillのResponsibility、Read First、Operating Spine、Stop Conditionsを比較した
  - Agent設定のprovider／installed mirrorを検索した
  - Planning／Execution／Review／PR Deliveryで旧Evidence Ledger、manual fallback、Reviewer dependencyを抽出した
  - 既存Initiative `init-00322`とGitHub Issue #322の存在を確認した
  - Workbenchが既にmainへmerge済みであることを確認した
- 実験条件:
  - 調査基準commitはPR #323 merge後の`3ee6d904...`
  - historical discussion／closed scopeはmigration対象としない
  - exact全file inventoryはEpic 1で再生成する

## facts／観測できた事実

- 現行Initiative／Epic／Issue Planning SkillはChatGPT-firstだが、ChatGPT outputをevidenceとしてCodexがcanonical三文書を再執筆する
- 現行Planning Skillはmanual Planning Skillをemergency fallbackとして参照する
- `spec-dock-chatgpt-authoring`はgithub-synced／local-context、prompt pack、preservation receipt、artifact import、Evidence Adoption Ledgerを所有する
- 現行Issue Executionは`spec-reviewer`、`code-reviewer`、`qa-reviewer`、dev-coder、doc-writer、Evidence Ledgerへ強く依存する
- 現行Epic Executionはper-Issue PRとfinal quality Issueによるdeferred PRの両方を扱う
- custom Explorer、Repository Analyst、Docs Writer、default／utility／worker系Agentがprovider／installed surfaceに存在する
- Workbenchはroot／scope-localのGit非管理一時領域としてPR #323で導入済み
- 既存canonical fileは`requirement.md`、`design.md`、`plan.md`、`report.md`、`artifacts/`であり、vNextも同じ基本構造を使う
- `init-00322`とGitHub Issue #322は既に存在し、当初三文書はtemplate-onlyだった

## inference／推測

- 事実から推測したこと:
  - vNextはdocument schema migrationではなくWorkflow／Actor cutoverとして実装できる
  - 既存open Scopeを一括変換せず、次の操作に必要なcontractが不足する場合だけPlanning gapとしてrefreshすべき
  - Skill名を維持して内部responsibilityを全面改訂する方がNode／user interface互換性を保ちやすい
  - provider／installed／dogfood mirrorを同一Epicで更新しないとcutover後に旧Skillが再配布される
  - 旧Reviewer Agent削除とIssue Execution改訂は同じmigration unitで行う必要がある
- 推測の根拠:
  - 上記factsと、Current Effective Decision Snapshotで承認済みのauthority／YAGNI原則を組み合わせた。
  - 推測はexact implementationを固定せず、Epic Planningで再検証する前提である。

## unverified／未検証事項

- まだ確認していないこと:
  - すべてのlegacy Skill／Agent／doc／test参照の完全inventory
  - package installer／uninstaller／self-updateが新CLIと削除assetをどう扱うか
  - dogfood rootとinstalled rootでの全parity
  - GitHub PR watcher scriptの再利用可能範囲
- 確認できない理由:
  - browser／hosted service／operator environmentに依存する挙動、または実装Epicで初めて作られるsurfaceであるため。
  - 未検証事項を事実としてcanonical文書へ昇格させない。

## question candidates／質問候補

- source-groundedに解けず、人間判断が必要な候補:
  - なし。global workflow cutoverとdocument migrationなしは承認済み
- pressure-test questionとして切り出すべき候補:
  - 旧surface削除をどのEpicで行うと途中branchが壊れないかはEpic 1のdependency inventoryで決める
- 質問せずに解決できた候補:
  - 新規ScopeだけvNextを使う案は不採用
  - 全open Scopeの事前文書refreshは不要
  - closed historical artifactは変更しない
  - 必要なcontract不足だけ通常Planning gapとして局所修復

## terminology conflicts／用語衝突

- `migration`:
  - 文書変換ではなくWorkflow／Actor cutover
  - 旧asset削除とmirror parityを含む
- `compatibility`:
  - 既存Scopeのfile layout互換
  - 旧Workflowの並行運用を意味しない
- `refresh`:
  - Scopeが古いから機械実行するのではなく、次操作に必要なcontractが不足した場合の通常Planning

## edge cases／具体シナリオ

- active IssueのPlanにExit Contractがない:
  - 実装を推測せずIssue Planning gapとしてrefreshする
- installed mirrorだけ旧Reviewerが残る:
  - parity testをFAILさせcutoverを完了扱いにしない
- 旧historical reportにEvidence Ledgerがある:
  - historical artifactとして残し、現行Workflow authorityにしない
- 途中Epicで旧Skill削除により後続作業が困る:
  - Epic dependencyとDelivery Boundaryを設計し、replacementを先に提供してから削除する

## implications／判断への含意

- `requirement.md`:
  - REQ-023〜REQ-026、NFR-006、AC-015〜AC-018
- `design.md`:
  - Skill／Agent topology、Cutover、Parity、Legacy removal
- `plan.md`:
  - 7 Epicの順序、Epic 6 global cutover、Epic 7 dogfood
- `ADR`:
  - Global Workflow Cutover Without Document Migration

## リスク／制約

- current commit以降のrepository変更をEpic Planningで再調査する
- 検索結果だけで削除し、runtime／installer dependencyを見落とさない
- 一部surfaceだけ更新してprovider／installed parityを壊さない

## 反映先

- reflected_to:
  - initiative/requirement.md
  - initiative/design.md
  - initiative/plan.md
  - artifacts/20260716t123423z-09-adr-global-workflow-cutover-without-document-migration.md

## 参考

- `chemitaro/spec-dock@3ee6d9047506a40b938407ecfffbb341a3ca76af`
- `.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `.agents/skills/spec-dock-epic-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `.agents/skills/spec-dock-epic-execution/SKILL.md`
- `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
- `.codex/agents/*.toml`と`src/spec_dock/assets/install_root/` mirror
- `spec-dock/docs/workflow_*`、template、PR #323
