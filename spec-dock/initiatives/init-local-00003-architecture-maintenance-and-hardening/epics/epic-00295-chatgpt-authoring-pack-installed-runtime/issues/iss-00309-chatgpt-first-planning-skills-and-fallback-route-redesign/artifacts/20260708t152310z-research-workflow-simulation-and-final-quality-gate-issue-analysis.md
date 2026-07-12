---
種別: research
ID: "20260708t152310z-research"
タイトル: "Workflow Simulation And Final Quality Gate Issue Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260708t152310z-research Workflow Simulation And Final Quality Gate Issue Analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- ChatGPT-first planning skills を実際に Codex が使う前提で、Initiative Planning、Epic Planning、Issue Planning、Epic Execution、Issue Execution、final quality gate / PR delivery までの情報動線をシミュレートする。
- 現行 skill / docs / template が、ChatGPT-first primary route と `-manual` backup route の分離を自然に支えられるかを確認する。
- Epic Planning で最終 Issue として Epic quality gate / mergeable PR delivery Issue を必ず計画へ含めるべきか、どこへ契約を置くべきかを整理する。

## sources / 調査方法 (必須)
- 参照先:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - `spec-dock/active/issue/report.md`
  - `artifacts/20260708t150402z-interview-chatgpt-first-planning-route-fallback-boundary-interview.md`
  - `artifacts/20260708t151122z-interview-primary-and-fallback-skill-naming-interview.md`
- 検証手順:
  - active scope を確認し、`iss-00309` の現在状態を前提に読んだ。
  - planning / execution / ChatGPT authoring の installed skill を読み、実際に Codex がどの順で skill を踏むかを手順化した。
  - Epic plan template と Epic workflow docs を読み、final quality gate / PR delivery Issue の契約がどこに存在し、どこが弱いかを確認した。
- 実験条件:
  - 実際の ChatGPT invocation / ZIP 生成は未実施。この research は workflow simulation と source-grounded design analysis である。

## facts / 観測できた事実 (必須)
- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` は、現時点では ChatGPT を evidence-only producer として参照しているが、ChatGPT-first primary route としては構成されていない。
- `spec-dock-chatgpt-authoring` は shared evidence lane であり、canonical docs、reviewer gates、assurance state、execution readiness、PR delivery を所有しない。
- `spec-dock-epic-execution` は、中間 Issue の PR delivery を final quality Issue に defer する policy を扱える。中間 Issue では final quality Issue id、dependency edge、no-per-Issue-PR rationale、merge-prepared を主張しないこと、local completion / issue finish 条件を `report.md` に残す必要がある。
- `workflow_chatgpt_authoring_pack.md` は、reviewed Epic plan が final delivery Issue を定義している場合に中間 Issue は個別 PR を作らず、最後の delivery Issue で Epic 全体の品質ゲート、レビュー指摘修正、手動確認、push、mergeable PR 作成をまとめると書いている。
- `workflow_epic.md` には final quality Issue 集約の実行ライフサイクル記述があるが、Epic planning 時に必ず Issue list 末尾へ final quality gate / PR delivery Issue を作る、という plan authoring checklist と template の圧はまだ弱い。
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md` には `最終品質ゲート（final quality gate）` section があるが、これは plan の section であり、Issue list の末尾に具体的な final quality Issue candidate を含める契約としては明示されていない。
- `phase_plan_epic.md` の作成 checklist は `final exit contract` を要求しているが、final quality gate Issue の必須化、Issue grade に応じた gate 内容、PR delivery 集約、review repair loop までは明文化していない。

## inference / 推測 (必須)
- 事実から推測したこと:
  - ChatGPT-first primary route を本当に使わせるには、既存 planning skills の Operating Spine 自体を「まず ChatGPT authoring runtime を使う」構造へ書き換える必要がある。
  - `spec-dock-chatgpt-authoring` は shared lane として残し、primary planning skills はそれを呼び出す coordinator / adoption owner になるのが自然である。
  - `-manual` skills は既存 planning kernel をほぼ保持し、primary skills からは human-approved emergency fallback としてだけ案内するのがよい。
  - Epic Planning は、Issue slicing output に `final-quality-gate-and-pr-delivery` 系の最終 Issue を含めることを標準契約にするべきである。
  - final quality Issue は単なる docs section ではなく、Epic Execution が最後に start する実行単位である必要がある。そこで Epic-wide verification、manual test、Codex PR review / CI repair loop、mergeable PR creation を閉じる。
  - final quality Issue の中身は Issue grade / Epic risk / changed surface に応じて変わるため、Epic plan template は「必須 Issue の存在」と「grade-sensitive gate 内容」を分けて表現するべきである。
- 推測の根拠:
  - 現行 execution skill は final quality Issue defer path を読めるが、planning template が final Issue を必ず生成しないと execution 側で参照できない。
  - 現行 ChatGPT authoring docs は evidence lane に留まっており、primary skill が ChatGPT-first を明示しなければ、従来 flow が通常経路として残り続ける。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実装後の skill discovery order が実際の Codex skill list で primary skills を manual skills より上に見せるか。
  - `-manual` suffix の skill が installed assets と runtime / managed skill list の両方で正しく配布されるか。
  - Epic plan template 変更後に existing Epic docs へどこまで retroactive update を要求するか。
  - final quality Issue を単一 Issue / no-op Epic / docs-only Epic にも必須にするか、multi-Issue implementation Epic に限定するか。
- 確認できない理由:
  - これは product workflow policy の判断を含み、repo の現物だけでは一意に決まらない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - final quality gate / PR delivery Issue を、全 Epic に必須とするか、複数 Issue を持つ implementation Epic に必須とするか。
  - existing Epic plan へ retroactive migration を求めるか、今後の template / planning skill からのみ適用するか。
  - `-manual` skills を通常の skill list に表示するか、説明上は backup として明記しつつ discovery order では primary より下げるだけにするか。
- pressure-test question として切り出すべき候補:
  - final quality Issue の必須範囲。これが決まると template / skill / docs の書き方が決まる。
- 質問せずに解決できた候補:
  - 中間 Issue で PR を作らない場合は、final quality Issue id と dependency edge と no-per-Issue-PR rationale を evidence として残す必要がある。
  - ChatGPT-first route 失敗時は automatic fallback ではなく、wait / retry / recover を先に行い、manual fallback は人間承認を必要とする。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `quality gate`
  - `final quality gate`
  - `PR delivery`
  - `mergeable PR`
  - `merge-prepared`
  - `manual`
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - `workflow_epic.md` は Epic-level final quality gate と PR delivery 集約を扱う。
  - `github-pr-merge-preparer` は merge-prepared evidence を作るが、merge はしない。
  - `manual` は今回の user-approved decision では従来 planning route の backup skill suffix を指す。
- 判断が必要な理由:
  - final quality Issue が「PR を作る Issue」だけに見えると、Epic-wide verification / review repair / manual test / issue finish evidence が抜ける。
  - `manual` route が平時にも使える名前として見えすぎると、ChatGPT-first primary route が形骸化する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Initiative Planning から始まる巨大タスク:
    1. `spec-dock-initiative-planning` を呼ぶ。
    2. 既存 Initiative fit を確認する。
    3. GitHub sync / local-context mode を決める。
    4. ChatGPT-first route で Initiative requirement / design / plan と Epic candidates を ZIP/tree evidence として生成する。
    5. review / stage / validate を行い、EAL に採否を残す。
    6. 人間が Epic candidates を承認する。
    7. Epic node を作成し、各 Epic へ handoff evidence を渡す。
- その edge case が requirement / design / plan に与える影響:
  - Initiative Planning skill は ChatGPT-first invocation を primary spine に含める必要がある。Epic candidate node creation 前の human approval gate は維持する。

- edge case:
  - Epic Planning から始まるタスク:
    1. `spec-dock-epic-planning` を呼ぶ。
    2. Epic fit / parent Initiative / requirement を確認する。
    3. ChatGPT-first route で Epic design / plan、Issue candidate list、各 Issue draft requirement/design/plan、dependency order、final quality Issue candidate を ZIP/tree evidence として生成する。
    4. `authoring pack review` / `stage` / `validate epic-issue-candidates` を通す。
    5. EAL へ採否を記録する。
    6. 人間が Issue slicing を承認する。
    7. Issue nodes と draft artifacts を作成する。
    8. Issue dependencies を設定し、末尾に final quality gate / PR delivery Issue を置く。
- その edge case が requirement / design / plan に与える影響:
  - Epic plan template と Epic planning skill は、Issue list に final quality Issue candidate を含めること、また中間 Issue は PR delivery を defer することを明記する必要がある。

- edge case:
  - Issue Planning で Epic draft を正式化する:
    1. `spec-dock-issue-planning` を呼ぶ。
    2. active Issue と guidance を確認する。
    3. ChatGPT-first route で draft adoption / missing design / implementation plan refinement を生成する。
    4. Draft evidence を EAL に採否記録し、canonical docs へ再記述する。
    5. `spec-reviewer` pass を通す。
    6. execution-ready handoff を作る。
- その edge case が requirement / design / plan に与える影響:
  - Issue Planning skill は `zero-base` / `requirement-first` / `draft-adoption` の各 mode で ChatGPT-first を primary とする必要がある。

- edge case:
  - Epic Execution:
    1. `spec-dock-epic-execution` を呼ぶ。
    2. reviewed Epic handoff と dependency order を読む。
    3. `deps check` で次の Issue を一つ選ぶ。
    4. `issue start` する。
    5. Issue docs が未正式なら `spec-dock-issue-planning` へ渡す。
    6. execution-ready なら `spec-dock-issue-execution` へ渡す。
    7. 中間 Issue では PR を作らず、deferred PR delivery evidence を `report.md` に残して `issue finish` する。
    8. 次 Issue へ進む。
    9. 最後の final quality Issue で Epic-wide gate と PR delivery を実行する。
- その edge case が requirement / design / plan に与える影響:
  - Epic Execution skill は既存方針を維持しつつ、final quality Issue が plan に存在しない multi-Issue Epic を structural blocker として扱うべき可能性がある。

- edge case:
  - Issue Execution:
    1. `spec-dock-issue-execution` を呼ぶ。
    2. execution-ready canonical docs と plan を確認する。
    3. approved step を一つずつ実行する。
    4. report に evidence を残し、必要 reviewer gate を通す。
    5. 中間 Issue では PR delivery を defer し、final quality Issue dependency と rationale を残す。
    6. final quality Issue の場合だけ PR delivery / merge-preparer を起動する。
- その edge case が requirement / design / plan に与える影響:
  - final quality Issue は通常の Issue Execution と同じ issue grade / reviewer obligation を持ちつつ、Epic-wide verification と PR delivery を追加責務として持つ。

- edge case:
  - ChatGPT browser の 4 tab 上限:
    - 正規 route は待機 / timeout 後の再整列 / recovery を行う。
    - automatic manual fallback はしない。
- その edge case が requirement / design / plan に与える影響:
  - primary skills は fallback ではなく wait / retry / recover を先に案内し、manual fallback には human approval evidence を要求する。

## implications / 判断への含意 (必須)
- `requirement.md` には、既存 planning skills が ChatGPT-first primary route であること、`-manual` skills が human-approved emergency backup であること、final quality Issue が Epic-level PR delivery gate を担うことを入れる。
- `design.md` には、primary skills、manual backup skills、shared `spec-dock-chatgpt-authoring` lane、authoring runtime commands、EAL/canonical adoption/fresh reviewer gates、Epic final quality Issue の責務境界を入れる。
- `plan.md` には、skill asset 分離、docs/template 更新、Epic plan template への final quality Issue contract 追加、tests / validation / dogfood checks を入れる。
- `src/spec_dock/assets/spec_dock/templates/epic/plan.md` は、Issue list の末尾に final quality gate / PR delivery Issue を入れる section を強める必要がある。
- `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md` は、作成 checklist と review gate に final quality Issue の存在、grade-sensitive gate 内容、no-per-Issue-PR relay policy を追加する必要がある。
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` は、現行 final delivery 例外を維持しつつ、Epic planning 側の required handoff package として final quality Issue の存在を明文化する余地がある。

## リスク/制約 (任意)
- final quality Issue を常に必須にすると、小さな single-Issue Epic や docs-only/no-op Epic で過剰になる可能性がある。
- ただし multi-Issue implementation Epic で final quality Issue がないと、Epic-wide verification、review repair、manual test、mergeable PR delivery が中間 Issue のどこかへ曖昧に漏れる。
- `-manual` backup skills を作ると skill 数が増える。description と discovery order で primary route を明確に上位に置く必要がある。

## 反映先 (任意)
- reflected_to:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`

## 参考（References） (任意)
- `artifacts/20260708t150402z-interview-chatgpt-first-planning-route-fallback-boundary-interview.md`
- `artifacts/20260708t151122z-interview-primary-and-fallback-skill-naming-interview.md`
