---
種別: interview
ID: "20260708t151122z-interview"
タイトル: "Primary And Fallback Skill Naming Interview"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00309"
created_at: "2026-07-08THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "unanswered"
authority: "proposed"
adoption_status: "unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked"
derived_from: []
reflected_to: []
---

# 20260708t151122z-interview Primary And Fallback Skill Naming Interview

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
    - ChatGPT-first primary route と manual fallback route の skill discoverability。
  - `design.md`:
    - Installed skill taxonomy、skill name、routing order、fallback handoff。
  - `plan.md`:
    - 既存 skill rename / copy、managed skill list、docs update、compatibility note。
  - `ADR`:
    - 必要なら skill naming policy の ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - skill 名はユーザーが毎回呼び出す入口であり、ChatGPT-first が正規 route として使われるか、従来 route がノイズとして残るかに直結するため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock を利用する人間ユーザー / product owner。
- 何を明確にする質問か:
  - 既存の `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` 名を primary ChatGPT-first route に残すか、ChatGPT-first 専用名を新設するか。
- 回答が後続判断へ与える影響:
  - primary skill と fallback skill の命名、Skill list の並び、既存ユーザー互換、fallback 誘導文、実装範囲が決まる。

## 質問 (必須)
- pressure-test question:
  - 正規 route を ChatGPT-first にしたいなら、ユーザーが自然に呼ぶ skill 名は primary route を指すべき。一方で既存 skill 名を大きく変えると、現在の利用者・既存 docs・既存 invocation が迷子になる。
- 質問:
  - skill naming はどの方針にしますか。
- 回答してほしいこと:
  - A/B/C のどれに近いか、または別案を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `artifacts/20260708t150402z-interview-chatgpt-first-planning-route-fallback-boundary-interview.md`
- local context で解決できたこと:
  - 既存 planning skill 名はすでに installed skill として使われており、ユーザーが自然に呼びやすい。
  - 現在の中身は ChatGPT を補助 evidence lane として扱っているだけで、ChatGPT-first route ではない。
  - ユーザー回答により、ChatGPT-first が正規 route、従来 route は人間承認つき backup route と確定した。
- まだ人間判断が必要な理由:
  - skill name は product UX であり、互換性・分かりやすさ・正規 route の強制力のどれを優先するかは repo から一意に決まらない。

## 回答案 (必須)
- Option A:
  - 既存名を primary ChatGPT-first route にする。従来 route は `spec-dock-initiative-planning-manual` / `spec-dock-epic-planning-manual` / `spec-dock-issue-planning-manual` に退避する。
- Option B:
  - ChatGPT-first 専用名を新設する。例: `spec-dock-chatgpt-initiative-planning` / `spec-dock-chatgpt-epic-planning` / `spec-dock-chatgpt-issue-planning`。既存名は従来 route のまま残す。
- Option C:
  - 既存名は routing hub にして、内部で ChatGPT-first primary route と manual fallback route を選ぶ。fallback の実体 skill は hidden / internal に近い扱いにする。

## Codex の分析 (必須)
- 判断軸:
  - 正規 route の強制力、既存利用者の互換性、skill list の読みやすさ、fallback の誤用防止、将来の host / backend 差し替え余地。
- tradeoff:
  - Option A は「普通に planning skill を呼べば ChatGPT-first」になるため、正規 route 化が最も強い。ただし従来 route の名前変更が必要。
  - Option B は互換性が高いが、ユーザーが従来名を呼び続けると ChatGPT-first が使われない。
  - Option C は互換性と正規 route 化の両立に見えるが、hub 内の条件分岐が増え、今回の懸念である「従来 workflow のノイズ」が残りやすい。
- リスク:
  - fallback skill 名に `fallback` を入れると平時にも安易に使われる可能性がある。
  - `legacy` は古くて非推奨という印象が強すぎ、まだ有効な backup route としての性格とずれる。
  - `manual` は「人間承認つき」「ChatGPT automation を使わない」という意味が比較的伝わる。
- 具体シナリオ / edge case:
  - ユーザーが `$spec-dock-epic-planning` を呼んだときに ChatGPT-first route が走るべきか。
  - ChatGPT が一時障害のときに `$spec-dock-epic-planning-manual` を明示的に呼ぶべきか。
  - Skill list 上で `manual` route が primary route より上に出てしまい、誤って選ばれないか。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。既存名を primary ChatGPT-first route に残し、従来 route は `-manual` suffix に退避する。
- 理由:
  - 正規 route を本当に ChatGPT-first にするには、ユーザーが自然に呼ぶ既存 planning skill 名が ChatGPT-first を実行する必要がある。
  - `manual` は backup route の性格を比較的正確に表し、`legacy` より否定的すぎず、`fallback` より常用されにくい。
- 未回答時の影響:
  - skill taxonomy が決まらず、要件・設計・計画で primary / fallback route を具体化できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ...
- 回答:
  - ...
- 回答日時:
  - ...

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes | no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - ...

## 採用判断 (回答後に必須)
- adoption_status:
  - unreviewed | adopted | partially_adopted | rejected | deferred | stale | blocked
- adoption target:
  - `requirement.md` | `design.md` | `plan.md` | `ADR` | `report.md` Evidence Adoption Ledger | none
- 採用 / 棄却 / deferred の理由:
  - ...
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes | no

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- reflected_to 更新方針:
  - ...
- adoption reflection:
  - ...

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
