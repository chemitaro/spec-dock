---
種別: interview
ID: "20260612t070646z-interview"
タイトル: "Hub Skill Naming Compatibility Direction"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["iss-00184"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00184"
created_at: "2026-06-12T07:06:46Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: ["requirement.md", "report.md"]
---

# 20260612t070646z-interview Hub Skill Naming Compatibility Direction

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - canonical skill name / compatibility policy / non-scope の表現が変わる。
  - `design.md`:
    - rename / alias / staged migration の設計方針と変更対象ファイルが変わる。
  - `plan.md`:
    - test obligation、parity check、reference cleanup、migration note の step 分割が変わる。
  - `ADR`:
    - 長期的に skill naming policy を固定する場合は ADR candidate になり得る。
- chat 上の軽微な一問では足りない理由:
  - 旧名 `spec-driven-tdd-workflow` は implementation / tests / docs / historical specs に広く参照されており、選ぶ互換方針によって issue の scope とリスクが大きく変わるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / user.
- 何を明確にする質問か:
  - この issue の成功条件を「canonical skill path/name の rename」まで求めるのか、「discoverability を改善しつつ旧 path を残す」ことを許容するのかを明確にする。
- 回答が後続判断へ与える影響:
  - canonical name、compatibility alias、reference update 範囲、tests の期待値、migration note の要否を決める。

## 質問 (必須)
- pressure-test question:
  - 旧名を破壊的に置き換える価値があるか、それとも互換性を優先して新名を案内名 / alias として導入するべきか。
- 質問:
  - この issue では、hub skill の canonical な directory / skill name を新名へ移行するところまで目指しますか。それとも旧 `spec-driven-tdd-workflow` path は互換入口として残し、表示名・description・docs で「SpecDock hub」と明示する段階的移行を目指しますか。
- 回答してほしいこと:
  - どちらを優先するか。
  - もし新名を強く希望する場合、現時点の第一候補名。
  - 旧名を残す場合、残し方は compatibility alias / forwarding note / docs-only migration note のどれが好みか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `README.md`
  - `spec-dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/cli.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/**`
- local context で解決できたこと:
  - 現行 hub skill は本文上では entry / routing skill, route selector, global invariant surface と説明済み。
  - `iss-00164` は `done` で、hub/leaf responsibility boundary は既に整理済み。
  - 旧名 `spec-driven-tdd-workflow` は tests、README、CLI bundled asset list、historical spec/discussion に広く現れる。
  - 単純な directory rename は、少なくとも tests / CLI asset list / docs / dogfooding mirror / generated docs に影響する。
- まだ人間判断が必要な理由:
  - `spec-dock-hub` のように明快な新名へ切り替える価値と、旧名互換を残して利用者・既存参照を守る価値は product judgement であり、local source だけでは優先順位を決められない。

## 回答案 (必須)
- Option A:
  - Canonical rename: 新しい canonical skill directory / metadata name を採用し、旧 `spec-driven-tdd-workflow` は必要最小限の compatibility alias または migration note にする。
- Option B:
  - Staged compatibility: 旧 `spec-driven-tdd-workflow` path は残し、title / description / README / docs で `SpecDock Hub` と明示する。新 canonical name は alias / future migration candidate として扱う。
- Option C:
  - Metadata-only clarification: directory / skill name は変えず、`SKILL.md` の `name` / description / heading と docs 表現だけを改善する。

## Codex の分析 (必須)
- 判断軸:
  - discoverability, compatibility risk, reference churn, future migration cost, user-facing clarity.
- tradeoff:
  - Option A は名前の問題を最も直接解決するが、asset install / update tests / docs / historical references の churn が大きい。
  - Option B は互換性を保ちつつ意図を伝えやすく、後段で rename を進める余地を残す。
  - Option C は最小差分だが、available skills の key / directory name が分かりにくい問題は残る。
- リスク:
  - 旧 path 依存の tests / docs / scripts を壊す。
  - 新旧名が併存して、かえって hub が二つあるように見える。
  - historical specs まで機械的に rewrite して、過去の証跡を不必要に汚す。
- 具体シナリオ / edge case:
  - New install では新名だけを出したいが、既存 consumer repo の update では旧名が残る可能性がある。
  - Generated / historical spec 内の旧名は、実行時参照ではなく過去証跡として残す方がよい場合がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option B: staged compatibility を第一候補にする。
- 理由:
  - 現時点の参照数と bundled asset / tests への影響を見ると、いきなり canonical path を完全 rename するより、旧 path を互換入口として残しながら `SpecDock Hub` を表示名・description・docs で前面に出す方が、今回の「分かりにくい」を小さな差分で改善しやすい。
- 未回答時の影響:
  - canonical rename まで踏み込む plan にするか、compatibility-first plan にするかを確定できず、requirement / design / plan authoring が止まる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ユーザーは、互換性を中途半端に残すのではなく、統合的に新しい名前へ完全移行する方針を明示した。
- 回答:
  - 互換性は不要。旧 `spec-driven-tdd-workflow` を互換入口として残さず、この tool を使う人が矛盾や破綻に惑わされないように、完全に新しい名前へ刷新する。
- 回答日時:
  - 2026-06-12

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - canonical な新 skill name を何にするか。Codex の現時点の推奨は `spec-dock-hub`。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - これは互換性方針を決める user-intent blocker であり、ユーザー回答が issue scope と acceptance criteria を直接変更するため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 旧名互換を残す前提を削除し、新 canonical name への完全移行を必須 scope にする。
- `design.md`:
  - rename / reference cleanup / tests update / dogfooding mirror refresh を一体で設計する。compatibility alias は採用しない。
- `plan.md`:
  - 旧名が実行時 surface に残らないことを negative inspection として固定する。
- `ADR`:
  - 今回の issue 内判断で足りる見込み。ただし skill naming policy として長期固定する場合は ADR candidate にできる。
- reflected_to 更新方針:
  - `requirement.md` と `report.md` にまず反映し、design / plan authoring 時に詳細化する。
- adoption reflection:
  - `report.md` の Decision Ledger / Evidence Adoption Ledger に、互換性なしの full migration 方針として採用する。

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
