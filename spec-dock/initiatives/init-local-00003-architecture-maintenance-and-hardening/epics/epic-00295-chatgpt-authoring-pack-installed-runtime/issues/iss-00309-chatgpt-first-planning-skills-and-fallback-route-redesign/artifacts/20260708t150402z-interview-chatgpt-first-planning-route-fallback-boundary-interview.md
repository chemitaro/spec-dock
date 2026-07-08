---
種別: interview
ID: "20260708t150402z-interview"
タイトル: "ChatGPT First Planning Route Fallback Boundary Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00309"
created_at: "2026-07-08THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260708t150402z-interview ChatGPT First Planning Route Fallback Boundary Interview

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
    - ChatGPT-first planning route を正規 workflow とする範囲。
    - 従来 planning route を backup / fallback として残す要件。
  - `design.md`:
    - primary skill と fallback skill の分離、命名、routing、stop gate。
    - ChatGPT browser / Oracle backend の fragility と concurrency limit を扱う運用設計。
  - `plan.md`:
    - 既存 skill の rename / copy / deprecation、new primary skill 追加、docs / installed asset 同期、検証順序。
  - `ADR`:
    - 必要なら、ChatGPT-first route を正規 route とする operating model の ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 回答により、正規 skill の責務、fallback skill の名称、fallback へ移る条件、自動/手動の境界、EAL 証跡の必須度が変わるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock を実際に使う人間ユーザー / product owner。
- 何を明確にする質問か:
  - ChatGPT-first planning route が失敗・渋滞・未設定・低信頼になったとき、従来 planning route へどの条件で切り替えてよいか。
- 回答が後続判断へ与える影響:
  - primary skill と fallback skill を完全分離するか、primary skill から fallback skill へ明示 handoff するか、また fallback が自動で走れるか human approval を必須にするかを決める。

## 質問 (必須)
- pressure-test question:
  - ChatGPT-first を正規 route にすると、browser 操作 failure / 4 tab 上限 / backend 未設定 / GitHub sync 不成立 / output validation failure のような「技術的に失敗しやすい状態」が通常運用で必ず発生する。このとき fallback が強すぎると結局 ChatGPT-first が使われず、弱すぎると作業が止まる。
- 質問:
  - ChatGPT-first planning route から従来 planning route への fallback は、どの程度まで自動化してよいですか。
- 回答してほしいこと:
  - A/B/C のどれに近いか、または別案を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - PR #308 observation result: CI passed, latest Codex review still has P1 findings, merge-preparer stopped at human gate by repeated blocker fingerprints.
- local context で解決できたこと:
  - 現在の planning skills は ChatGPT を補助 evidence lane として参照しているだけで、ChatGPT-first を正規 route として強制する構造ではない。
  - 親 Epic は既存 skill names 維持、`spec-dock-chatgpt-authoring` 追加、evidence-only、human approval gate、local-context mode を既に前提にしている。
  - ただし「正規 route / fallback route の分離」「fallback skill の命名」「fallback 移行条件」は未確定。
- まだ人間判断が必要な理由:
  - fallback 条件は UX / 運用思想の選択であり、repo から一意に決まらない。強制しすぎると運用不能になり、緩めすぎると ChatGPT-first が形骸化する。

## 回答案 (必須)
- Option A:
  - 手動承認 fallback: primary ChatGPT-first skill は失敗時に止まり、fallback skill を使うにはユーザーの明示承認を必須にする。
- Option B:
  - 条件付き自動 fallback: backend 未設定、browser concurrency saturated、timeout、GitHub sync 不成立、ZIP validation failure など deterministic な failure reason を記録できる場合だけ、primary skill が fallback skill へ自動 handoff する。
- Option C:
  - 常時 fallback 併走: ChatGPT-first route と従来 route を最初から並列に走らせ、ChatGPT output が使えない場合は従来 route の結果を採用候補にする。

## Codex の分析 (必須)
- 判断軸:
  - ChatGPT-first の実効性、fragility 対応、ユーザー待ち時間、token / browser queue コスト、誤って従来 route に逃げるリスク、証跡の明確さ。
- tradeoff:
  - A は最も安全だが、ChatGPT 側の一時 failure が多いと人間の割り込みが増える。
  - B は現実的だが、failure reason taxonomy と handoff report が必要になる。
  - C は止まりにくいが、正規 route が形骸化しやすく、二重作業でコストが増える。
- リスク:
  - fallback を曖昧にすると、スキル名を分けても実運用では従来 workflow がノイズとして残り続ける。
  - fallback を禁止しすぎると、ChatGPT browser / Oracle の脆さがそのまま planning workflow の停止要因になる。
- 具体シナリオ / edge case:
  - 4 tab 上限で ChatGPT invocation が queueing / timeout した場合。
  - `SPECDOCK_CHATGPT_COMMAND` 未設定の導入先 repo。
  - GitHub sync preflight が dirty / unpushed / branch missing で fail したが、local-context pack なら十分な evidence を渡せる場合。
  - ChatGPT ZIP が validation rejected になり、すぐに人間/Codex の従来 planning で進めたい場合。

## Codex の推奨案 (必須)
- 推奨:
  - Option B を基本にしつつ、fallback が canonical docs を直接 authoring する前に report / handoff record を必須にする。
- 理由:
  - ChatGPT-first を正規 route にするなら、primary skill はまず ChatGPT authoring runtime を試すべき。一方で実運用の fragility と 4 tab 上限を考えると、deterministic failure reason がある場合は作業を止めずに fallback へ移れるべき。
- 未回答時の影響:
  - fallback 条件が決まらず、skill 分離後も「どちらをいつ使うか」が曖昧なままになる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option A を採用する。
  - ただし、ChatGPT-first route は単に一度試して失敗したら止める route ではない。
  - 4 tab 上限に達している場合は順番待ちをし、timeout したら再度並び直す。
  - Browser / ChatGPT automation が起動しない、壊れている、応答しない場合は、ブラウザ再起動、原因特定、復旧を試み、再度 ChatGPT の利用を行う。
  - ChatGPT 利用が正規 route であり、基本的には待つ・直す・再試行する。
  - 従来 planning skill route は、OpenAI 側または tool / browser 側の修正困難な不具合があり、人間ユーザーもそれを認識し、一時的に対処できないと判断した場合だけ、明示的な手動承認により使う backup route とする。
- 回答:
  - ChatGPT-first を正規 route とし、fallback は人間承認がある場合だけ許可する。
  - Tab concurrency saturation は fallback 理由ではなく wait / retry 理由とする。
  - Browser / automation failure は fallback 理由ではなく recovery / restart / retry 理由とする。
  - fallback は system / provider / tool 側の一時的かつ修正困難な障害に対する emergency backup とする。
- 回答日時:
  - 2026-07-09

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 正規 route と fallback route の skill naming / discovery order をどうするか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ChatGPT-first 正規 route と従来 route の fallback 境界を決める product / workflow decision であり、Issue 要件・設計・計画へ直接反映する。
  - fallback の自動化は採用しない。Tab 上限・timeout・browser 起動不良は、まず待機・再試行・復旧対象であり、fallback へ自動移行する理由にはしない。
  - fallback は人間承認つきの emergency backup とし、通常の planning workflow では ChatGPT-first route を維持する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - ChatGPT-first route を正規 planning workflow として定義する。
  - 従来 route は fallback / backup route として残すが、自動 fallback は禁止し、人間承認を必須にする。
  - Tab 上限・timeout・browser failure は wait / retry / recovery の対象として定義する。
- `design.md`:
  - Primary skill は ChatGPT-first orchestration を明示的に実行する。
  - Fallback skill は別名・別 route として discoverable にするが、primary skill の通常 spine に混ぜない。
  - Failure taxonomy は `wait`, `retry`, `recover`, `human-approved-fallback` を分ける。
- `plan.md`:
  - Skill naming / routing / docs / tests の変更を、primary route と fallback route の分離として実装する。
  - Backup route は human approval evidence と fallback reason を report / artifact に残す。
- `ADR`:
  - 必須ではないが、ChatGPT-first 正規 route と manual fallback policy が他 Epic / future workflow に波及する場合は ADR 候補にする。
- reflected_to 更新方針:
  - 要件・設計・計画の具体化時に反映し、`report.md` EAL に採用行を追加する。
- adoption reflection:
  - ChatGPT-first を補助線ではなく正規 route とし、従来 route は人間承認つき backup とする。

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
