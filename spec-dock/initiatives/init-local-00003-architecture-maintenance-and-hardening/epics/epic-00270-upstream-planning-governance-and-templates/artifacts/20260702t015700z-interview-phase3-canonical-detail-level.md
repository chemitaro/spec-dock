---
種別: interview
ID: "20260702t015700z-interview"
タイトル: "Phase 3 Canonical Detail Level"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-01"
  - "20260702t014409z-research"
  - "20260702t014409z-02-interview"
  - "20260702t015012z-interview"
  - "20260702t015343z-interview"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T01:57:00Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t015700z-interview Phase 3 Canonical Detail Level

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - V3 の目的・背景・scope・acceptance criteria をどの粒度で本文化するかに影響する。
  - `design.md`:
    - upstream abstraction model、discovery-to-canonical model、Initiative/Epic responsibility model、Issue handoff model をどこまで展開するかに影響する。
  - `plan.md`:
    - Issue slicing policy、Issue list、delivery gate、追加/再分割 gate の書き込み量に影響する。
  - `ADR`:
    - Canonical docs に収めきれない長期判断を ADR へ逃がす必要があるかに影響する。
- chat 上の軽微な一問では足りない理由:
  - V3 reference は全文 artifact に保存済みだが、canonical docs へどの程度取り込むかで reviewer gate の読みやすさと将来の実行可能性が変わる。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - Canonical Epic docs を詳細な設計文書に寄せるか、要点を絞った実行可能な handoff に寄せるか。
- 回答が後続判断へ与える影響:
  - `requirement.md` / `design.md` / `plan.md` の章立て、artifact参照の使い方、reviewerへ渡す情報量が変わる。

## 質問

- pressure-test question:
  - V3 reference はかなり情報量があります。canonical docs はそれをどこまで本文化し、どこから artifact 参照に逃がすのがよいですか。
- 質問:
  - `epic-00270` の canonical `requirement.md` / `design.md` / `plan.md` は、V3 reference の内容をどの粒度で取り込みますか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 ZIP full intake artifact に Markdown 24ファイル全文を保存済み。
  - Repo survey artifact に、現行 templates / skills / workflow docs との差分を整理済み。
  - First interview: 6 Issueは暫定baseline、必要なら追加/再分割可。
  - Second interview: 追加/再分割は中程度gate、推奨ではない。
  - Third interview: 原則1PR、IssueごとのPR分割はしない。破綻時のみ再検討。
- local context で解決できたこと:
  - V3全文は artifact に残っているため、canonical docs に全文を貼る必要はない。
  - ただし reviewer gate と downstream Issue handoff のため、canonical docs には少なくとも採用した判断・境界・Issue slicing policy は必要。
- まだ人間判断が必要な理由:
  - canonical docs を厚くしすぎると読みにくくなり、薄くしすぎると downstream Issue が raw artifact を読まないと進めなくなる。

## 回答案

- Option A:
  - 厚めに取り込む。V3 reference の主要モデルを canonical `design.md` / `plan.md` にかなり展開し、artifact は補足証跡にする。
- Option B:
  - 中程度に取り込む。Canonical docs には採用判断、境界、Issue slicing policy、handoff package、acceptance / gate を明記し、詳細な分析・長い例・playbook は artifact 参照にする。
- Option C:
  - 薄めに取り込む。Canonical docs は短い要約とIssue list中心にして、詳細はほぼ artifact 参照にする。

## Codex の分析

- 判断軸:
  - reviewer が canonical docs だけで pass/fail 判断できるか。
  - downstream Issue planning が raw V3 artifact を読まずに親制約を理解できるか。
  - canonical docs が長すぎて保守しにくくならないか。
  - artifact adoption boundary が守られるか。
- tradeoff:
  - Option A は自己完結性が高いが、V3全文に近くなり canonical docs が重くなる。
  - Option B は実行に必要な判断だけ canonical に置き、長い分析を artifact に残せる。
  - Option C は軽いが、Epic design/plan が薄くなり、V3が解消しようとしている upstream handoff insufficiency が残りやすい。
- リスク:
  - 厚すぎると Initiative/Epic templates の設計をする前に Epic docs 自体が巨大化する。
  - 薄すぎると Issue 03/04/05 が親設計を再発見することになる。
- 具体シナリオ / edge case:
  - `upstream-abstraction-model` は canonical design に要約採用が必要。
  - `initiative-design-playbook` / `epic-design-playbook` の長い例は artifact 参照で足りる。
  - `epic-to-issue-slicing-and-handoff` の handoff package fields は canonical plan に採用する必要がある。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - Raw V3 artifact を保存済みなので、canonical docs は「採用された判断」と「downstream handoff」に集中できる。
  - reviewer と後続 Issue が必要な制約を canonical docs だけで確認できる。
  - 長い分析や参考playbookは artifact を source evidence として参照できる。
- 未回答時の影響:
  - Canonical docs の章立てと情報量を固定できず、authoring に進む前に再確認が必要になる。

## ユーザー回答

- answer capture:
  - Option B を採用する。
  - Canonical `requirement.md` / `design.md` / `plan.md` へ V3 reference を全文書き写す必要はない。
  - V3 reference は無視せず、既存資産として活かし、設計・計画はそれらの情報に従って進める。
  - ZIP全文を1つのMarkdownにまとめただけでは参照しにくいため、重要部分は分割 artifact として整理し、意思決定は必要に応じて ADR に切り出して参照する。
  - Canonical docs は採用判断、境界、Issue slicing policy、handoff package、acceptance / gate を明記し、長い分析・例・playbook は artifact / ADR 参照にする。
  - コーディングエージェントが見やすいように、適切な流路で管理する。
- 回答:
  - `epic-00270` の canonical docs は中程度の詳細にする。V3 reference の判断・制約・handoff に必要な要素を canonical docs に採用し、詳細分析やplaybookは分割artifactやADR候補として管理する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Canonical docs 作成後に Issue scaffold をすぐ作るか、まず reviewer pass を優先するか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md` / `design.md` / `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - V3 reference を無視せず、かつ canonical docs へ全文貼りしない運用方針が明示されたため採用する。詳細分析は分割 artifact、長期/細部の意思決定は ADR 候補へ流す。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - V3 purpose / scope / acceptance を採用するが、詳細分析は artifact 参照へ分離する。
- `design.md`:
  - Scope layering / abstraction model / discovery adoption / handoff model の採用判断と境界を記述し、詳細playbookは artifact / ADR 参照にする。
- `plan.md`:
  - Issue slicing policy / final gate / handoff fields を明記し、詳細な例や補足は分割artifact参照にする。
- `ADR`:
  - 細かい意思決定や将来も参照される境界判断は、必要に応じて ADR 候補へ切り出す。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - canonical docs へ反映するまでは、この interview artifact が user-approved evidence。`report.md` Evidence Adoption Ledger へ採用記録を残す必要がある。
