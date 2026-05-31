---
種別: interview
ID: "20260531t135206z-interview"
タイトル: "Uninstall empty directory cleanup"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-31"
親: ["iss-00147"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00147"
created_at: "2026-05-31THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260531t135206z-interview Uninstall empty directory cleanup

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - uninstall 後に repo に残る empty directory の扱いと受け入れ条件が変わる。
  - `design.md`:
    - cleanup traversal、scope boundary、preserved file を含む directory の扱いが変わる。
  - `plan.md`:
    - filesystem tests と manual verification が変わる。
  - `ADR`:
    - 不要。
- chat 上の軽微な一問では足りない理由:
  - uninstall の目的は agent / skill noise removal だが、空の `.agents/skills`, `.codex/agents`, `.github/agents` などが残ると、実行結果が中途半端に見える。一方で親 directory を強く消しすぎると unrelated user files を巻き込む可能性があるため。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner
- 何を明確にする質問か:
  - uninstall が削除対象 files の親 directory をどこまで自動 cleanup するかを確定する。
- 回答が後続判断へ与える影響:
  - filesystem mutation boundary、tests、dry-run output、risk wording が変わる。

## 質問 (必須)
- 質問:
  - uninstall 後、削除対象 file に由来する空 directory は自動削除しますか？
- 回答してほしいこと:
  - Option A / B / C から選ぶか、別案があれば cleanup の上限 directory を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260531t133315z-interview-uninstall-command-scope.md`: repo-local uninstall が user-approved。
  - `20260531t133616z-interview-uninstall-removal-boundary.md`: specs handling は explicit mode selection が user-approved。
  - `20260531t134650z-interview-uninstall-managed-asset-mismatch.md`: agent / skill assets は content mismatch でも削除する方針が user-approved。
  - `src/spec_dock/assets/install_root/`: managed assets は `.agents/skills/**`, `.codex/agents/**`, `.github/agents/**`, `.codex/prompts/**`, `.codex/rules/**`, `.github/workflows/ci.yml` など複数 directory に配置される。
- local context で解決できたこと:
  - file 削除だけでは empty directory が残り得る。
  - preserved mismatch files や user-authored files が残る directory は削除してはいけない。
- まだ人間判断が必要な理由:
  - きれいな uninstall 結果を優先するか、directory cleanup の副作用最小化を優先するかは product policy で決める必要がある。

## 回答案 (必須)
- Option A:
  - file-only: files だけ削除し、空 directory cleanup はしない。
- Option B:
  - bounded empty-dir cleanup: 削除対象 file の親から上に向かって、空になった directory だけ削除する。ただし `.agents`, `.codex`, `.github`, `spec-dock` など既定の上限 root を越えない。
- Option C:
  - remove known empty roots: `.agents/skills`, `.codex/agents`, `.github/agents` など既知の managed directory が空なら root ごと削除するが、それ以外は残す。

## Codex の分析 (必須)
- 判断軸:
  - cleanup の見た目、副作用の小ささ、実装単純性、user-authored file 保護、dry-run の説明しやすさ。
- tradeoff:
  - Option A は最も安全だが、empty directory が残りやすい。
  - Option B はきれいに片付くが、上限 root と traversal 条件を正しく設計する必要がある。
  - Option C は分かりやすいが、新しい managed directory が増えたとき追従が必要になる。
- リスク:
  - cleanup traversal が強すぎると unrelated empty directory を消す。
  - cleanup しないと uninstall 後に agent / skill directory が残り、ノイズ除去の完了感が弱い。
- 具体シナリオ / edge case:
  - `.github/agents/` が空になったが `.github/workflows/ci.yml` は残る。
  - `.codex/agents/` は空になったが `.codex/config.toml` は content mismatch で残る。
  - `.agents/skills/` は空になったが `.agents/host-adapters/meta.json` が残る / 消える。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - preserved files がある directory は残しつつ、uninstall で空になった managed directory だけを片付けられる。
  - dry-run で removed-directories として表示すれば副作用も追いやすい。
- 未回答時の影響:
  - requirement の filesystem cleanup acceptance と design の cleanup traversal を固定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
  - 削除対象 file の親 directory から上に向かって、空になった directory だけを自動削除する。
  - ただし `.agents`, `.codex`, `.github`, `spec-dock` など既定の上限 root を越えて cleanup しない。
  - preserved file、user-authored file、content mismatch で残した file がある directory は削除しない。
- 回答日時:
  - 2026-05-31

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により、uninstall 後の empty directory cleanup は bounded cleanup として確定した。
  - uninstall で空になった managed directory を片付け、agent / skill noise removal の完了感を高める。
  - 上限 root を設けることで、unrelated directory cleanup や user-authored file の巻き込みを避ける。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - uninstall は削除対象 files の removal 後、既定上限 root 内で空になった directory を自動 cleanup する。
  - preserved files がある directory は削除しない。
- `design.md`:
  - cleanup traversal は削除対象 file の親から開始し、configured boundary root を越えない。
  - removed directories を dry-run / execution result に表示する。
- `plan.md`:
  - empty directory cleanup、boundary root preservation、preserved file がある directory の非削除を test obligation に含める。
- `ADR`:
  - 不要。
- reflected_to 更新方針:
  - requirement authoring 時に `requirement.md` と `report.md` の Evidence Adoption Ledger / Spec Authoring Gate へ反映する。

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
- 追加で作る discussion docs:
    - ...
