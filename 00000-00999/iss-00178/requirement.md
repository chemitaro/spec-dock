---
種別: 要件定義書（Issue）
ID: "iss-00178"
タイトル: "Review Feedback Triage"
関連GitHub: ["#178"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["epic-00067", "init-local-00003"]
---

# iss-00178 Review Feedback Triage — 要件定義（何を、なぜ行うか）

## 目的

PR observation が収集した複数の Codex review finding、CI failure、merge blocker、observation limitation を、場当たり的に修正せず、修正前に妥当性・修正必要性・関心ごとの grouping・repair unit 化を判断できる PR Repair Triage Gate として定義する。

これにより、P2 / P3 を一律に無視せず、一律に全修正もせず、人間が最終 merge 判断できる `merge-prepared` 状態へ効率よく到達できるようにする。

## 背景・現状

- 現状の挙動:
  - `github-pr-observation` は `@codex review` の deterministic trigger、CI / review / thread / comment body collection、final stdout JSON を提供する。
  - `github-pr-merge-preparer` は PR 作成または発見、observation、coarse failure classification、bounded repair delegation、再 observation、`merge-prepared` 判定を担う。
  - ただし、observation が複数の review finding / CI failure を返した後、修正前に全体を inventory 化し、妥当性・修正必要性・関心ごとの grouping・repair unit 化を明示する gate が不足している。
- 現状の課題:
  - 複数 finding / failure を受け取った後、個別に場当たり修正し、再 push / CI / review ループを繰り返しやすい。
  - P2 / P3 の多くは実害ある指摘になり得るが、severity だけでは current PR で修正すべきか、follow-up でよいか、no-action でよいかを判断できない。
  - 全 finding に full design / plan を要求すると運用が重すぎる一方、batch 全体の分析なしに repair worker へ渡すと修正単位と判断根拠が不安定になる。
  - `review-clean` と `merge-prepared` が混ざると、Codex review が完全に無指摘になるまでループし続ける圧力が生じる。
- 観測点:
  - GitHub PR review / review comments:
    - PR #177 では P2 / P3 の多くが PR observation の correctness、timeout、trigger boundary、resume safety、external side effect safety に関わっていた。
  - historical review analysis:
    - 過去 PR #2 から #177 の Codex P2 / P3 inline review 142 件のうち、128 件が `対処すべき`、13 件が `follow-up 可`、1 件が `必須ではない軽微` と分類された。
  - runtime / docs:
    - 現行 `new doc` runtime は `--template` option を持たず、`disc` は汎用 synthesis template である。
- 情報源:
  - `discussions/20260609t151424z-research-review-feedback-triage-policy.md`
  - `discussions/20260609t152616z-research-historical-p2-p3-review-analysis.md`
  - `discussions/20260609t154515z-disc-pr-repair-triage-workflow-proposal.md`
  - `discussions/20260610t022800z-interview-pr-repair-template-scope.md`
  - `discussions/20260610t031332z-disc-pr-repair-batch-dedicated-sheet-analysis.md`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `spec-dock/templates/discussions/disc.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - PR を作成し、人間の merge 判断前に CI と Codex review を確認するメイン orchestrator。
  - `github-pr-merge-preparer` skill を使って PR を merge-prepared に近づける agent。
  - review finding / CI failure の修正を委任される repair worker。
- 代表シナリオ:
  1. PR 作成後、`github-pr-observation` が複数の review finding と CI failure を返す。
  2. `github-pr-merge-preparer` が fix delegation 前に PR repair batch artifact を作り、すべての finding / failure を inventory に載せる。
  3. orchestrator が各 item の妥当性、修正必要性、risk class、disposition、repair unit grouping を判断する。
  4. `fix-now` / `needs-human` かつ実装修正・設計判断が必要なものだけ repair unit `disc` に分ける。
  5. repair worker は raw finding ではなく repair unit `disc` の implementation plan を根拠に修正する。
  6. 再 push 後、latest head SHA で re-observation し、batch / unit / report evidence を更新する。
  7. untriaged item、未解決 `needs-human`、blocking かつ未完了の repair unit が残っていなければ `merge-prepared` と報告できる。

## スコープ

- 必須:
  - `github-pr-merge-preparer` に、observation 後かつ fix delegation 前の **PR Repair Triage Gate** を追加する。
  - PR repair batch は既存 `disc` として作成するが、通常 `disc` template ではなく PR repair batch 専用 template を使うことを必須にする。
  - PR repair batch 専用 template は、`github-pr-merge-preparer` skill の provider-side asset として作成し、skill から参照できる正本にする。
  - batch template は、複数 finding / failure / limitation を 1 枚で扱う control sheet として、PR metadata、observation evidence、Concern Catalog、Inventory、Per-Concern Analysis、Repair Queue、Unit Discussion Plan、Stop Conditions、Merge-Prepared Gate を持つ。
  - batch inventory の item は、`validity`、`risk_class`、`need_to_fix`、`disposition`、`repair_unit`、`status` を持つ。
  - batch inventory の分類語彙は次を標準値として採用する。
    - `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
    - `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
    - `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
    - `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
    - `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`
  - repair unit は既存 `disc` として作成し、`source_batch`、`unit_id`、`covered_ids`、Validity Analysis、Need-To-Fix Decision、Root Cause、Options Considered、Recommended Design、Implementation Plan、Validation Plan、Implementation Result、Commit Evidence、Re-observation Result、Residual Risk / Follow-up の必須チェックリストで補強する。
  - `github-pr-observation` は evidence collection 境界を維持し、risk classification、disposition、repair unit grouping を持たないことを明記する。
  - `merge-prepared` 判定は、CI / review / merge blocker だけでなく、batch の triage 完了状態を確認する。
  - `review-clean` と `merge-prepared` の区別を明記する。
- 禁止:
  - PR merge、auto-merge enablement、branch deletion、GitHub issue close、`spec-dock issue finish` をこの workflow で自動実行すること。
  - review comment reply、review thread resolve、review dismiss、admin override をこの workflow で自動実行すること。
  - `github-pr-observation` に判断責務を持たせること。
  - raw finding から直接 repair worker に場当たり修正を委任すること。
- 対象外:
  - 新しい first-class discussion doc type の追加。
  - `new doc disc --template pr-repair-batch` / `--template pr-repair-unit` の runtime 実装。
  - `src/spec_dock/assets/spec_dock/templates/**` の runtime template catalog への追加。
  - 自動分類 runtime、AI classifier、CI log parser、GitHub API judgment の追加。
  - `spec-dock validate` による batch structure の機械検証。
  - PR body 自動更新。

## 境界

- 常に行う:
  - observation result の latest head SHA 一致を確認する。
  - observation result に含まれる review finding、CI failure、merge blocker、observation limitation を batch inventory に載せる。
  - 各 item を `validity` と `need_to_fix` に分けて判断する。
  - `fix-now` / `needs-human` で、実装修正・設計判断・複数案比較が必要な item は repair unit `disc` に紐づける。
  - `follow-up` / `no-action` / `covered-by` には rationale と residual risk を残す。
- 判断が必要:
  - P2 / P3 finding を current PR で修正するか、follow-up に送るか、no-action にするか。
  - 同じ root cause の review finding / CI failure を同一 repair unit に束ねるか。
  - 同種 finding の再発、budget 超過、scope expansion を human gate にするか。
- 行わない:
  - severity label だけで修正要否を決めない。
  - Codex Review が no major issues になるまで無制限にループしない。
  - batch artifact を省略して repair worker に直接委任しない。

## 非交渉制約

- `github-pr-observation` の stdout JSON は authoritative evidence であり、進捗ログや `--out` artifact は補助証跡に留める。
- `github-pr-observation` は deterministic trigger / evidence collection の責務に留める。
- `github-pr-merge-preparer` は merge preparation coordinator であり、merge 自体は人間 action として残す。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator が所有し、delegated draft は evidence として採用判断を経て反映する。
- 今回の実装は agent-tooling asset / docs / skill guidance の変更に閉じ、runtime `new doc` contract は変更しない。

## 前提

- `github-pr-observation` は current trigger boundary の review body / selected review comment body を final stdout JSON に含める。
- `github-pr-merge-preparer` は `github-pr-observation` を直接呼び、結果 JSON を読んで判断できる。
- PR repair batch / repair unit は issue scope の `discussions/` 直下に flat Markdown として作成する。
- batch / unit は既存 `disc` の filename / front matter / authority semantics に従う。
- PR repair batch 専用 template は、runtime `new doc` ではなく `github-pr-merge-preparer` workflow が参照・転記する agent-tooling asset として扱う。

## 受け入れ条件

- AC-001: PR Repair Triage Gate
  - アクター: `github-pr-merge-preparer` を使う orchestrator
  - 前提: PR observation result が review finding、CI failure、merge blocker、または observation limitation を返している。
  - 操作: fix delegation 前に `github-pr-merge-preparer` workflow を確認する。
  - 期待結果: observation 後かつ fix delegation 前に PR repair batch artifact を作成し、triage を完了する手順が明記されている。
  - 観測点: `.agents/skills/github-pr-merge-preparer/SKILL.md`

- AC-002: batch dedicated template
  - アクター: orchestrator
  - 前提: 複数の finding / failure / limitation がある。
  - 操作: PR repair batch artifact を作成する。
  - 期待結果: batch は既存 `disc` として作成されるが、`github-pr-merge-preparer` skill-local の PR repair batch 専用 template を source とし、`PR / Observation Metadata`、`Batch Purpose`、`Concern Catalog`、`Inventory`、`Classification Values`、`Per-Concern Analysis`、`Repair Queue`、`Unit Discussion Plan`、`Stop Conditions`、`Merge-Prepared Gate` を持つ。
  - 観測点: skill-local template / skill guidance / docs guidance

- AC-003: inventory classification
  - アクター: orchestrator
  - 前提: batch inventory に review finding または CI failure がある。
  - 操作: item を triage する。
  - 期待結果: 各 item は標準分類語彙に基づく `validity`、`risk_class`、`need_to_fix`、`disposition`、`repair_unit`、`status` を持ち、妥当性と修正必要性が分離して判断される。
  - 観測点: skill guidance / batch template

- AC-004: repair unit handoff
  - アクター: orchestrator / repair worker
  - 前提: batch item が `fix-now` または `needs-human` で、実装修正・設計判断・複数案比較が必要である。
  - 操作: repair unit `disc` を作成し、repair worker に委任する。
  - 期待結果: repair worker は raw finding ではなく repair unit `disc` の implementation plan を source of truth として修正する。
  - 観測点: `github-pr-merge-preparer` skill guidance

- AC-005: non-fix disposition
  - アクター: orchestrator
  - 前提: finding の `disposition` が `follow-up` / `no-action` / `covered-by` のいずれか、または `validity` / `risk_class` が `duplicate` / `false-positive` のいずれかである。
  - 操作: batch item を閉じる。
  - 期待結果: `disposition` が `follow-up` / `no-action` / `covered-by` の item には rationale、evidence、residual risk、必要なら follow-up target が batch 内に残る。`duplicate` / `false-positive` の item には該当する `validity` / `risk_class` と、対応する `disposition`（通常は `covered-by` または `no-action`）および rationale が残る。これらの item では repair unit `disc` は必須にならない。
  - 観測点: batch template / merge-prepared gate

- AC-006: merge-prepared gate
  - アクター: orchestrator
  - 前提: repair loop 後に latest head SHA で re-observation が完了している。
  - 操作: `merge-prepared` と報告する。
  - 期待結果: required check failure が残っておらず、non-required check failure は known optional または user explicit waiver がある場合だけ残せる。untriaged item、未解決 `needs-human`、blocking かつ未完了の repair unit が残っていないことを確認してから `merge-prepared` と報告する。`review-clean` ではない場合も、残存 finding が分類済みかつ non-blocking なら `merge-prepared` と報告できる。
  - 観測点: `github-pr-merge-preparer` merge-prepared predicate / response checklist

- AC-007: observation boundary preservation
  - アクター: `github-pr-observation`
  - 前提: PR observation script / skill が PR checks and review を収集する。
  - 操作: skill guidance を確認する。
  - 期待結果: `github-pr-observation` は evidence collection のみを担い、risk classification / disposition / repair unit grouping を行わないことが保たれている。
  - 観測点: `.agents/skills/github-pr-observation/SKILL.md`

- AC-008: scope containment
  - アクター: implementer
  - 前提: この issue の実装に着手する。
  - 操作: 変更対象を確認する。
  - 期待結果: skill-local PR repair batch template は追加されるが、first-class doc type、runtime `--template`、`src/spec_dock/assets/spec_dock/templates/**` の runtime template、自動分類 runtime、CI log parser は追加しない。
  - 観測点: git diff / tests / docs inspection

## 例外・エッジケース

- EC-001: timeout / observation limit
  - 条件: observation が timeout または limit に達し、CI / review が完了していない。
  - 期待: batch inventory に observation limitation と resume metadata を載せ、必要なら `human-decision` または resume path として扱う。新しい trigger を勝手に投稿しない。
  - 観測点: batch template / `github-pr-observation` resume guidance

- EC-002: same root cause
  - 条件: 複数の review finding と CI failure が同じ root cause に収束する。
  - 期待: batch の `Concern Catalog` / `Per-Concern Analysis` で同じ repair unit に束ねる。
  - 観測点: batch template

- EC-003: false positive / stale review
  - 条件: review finding の前提が誤り、または古い head / 古い trigger boundary に基づく。
  - 期待: `validity=false-positive` または `risk_class=false-positive` と、`disposition=no-action` または `disposition=covered-by` を明記し、false-positive / stale / already-addressed と判断した rationale を残す。必要なら human gate にする。
  - 観測点: batch inventory

- EC-004: scope expansion
  - 条件: finding は妥当だが、修正が current issue / current PR scope を超える。
  - 期待: `follow-up` または `needs-human` として扱い、current PR で場当たり修正しない。
  - 観測点: batch inventory / stop conditions

- EC-005: repeated failure class
  - 条件: 同じ failure class が repair 後に再発する。
  - 期待: loop limit に従い、追加自動修正ではなく human gate に切り替えられる。
  - 観測点: `github-pr-merge-preparer` fix loop limits / batch status

## 入力→出力例

- EX-001: 複数 finding の batch triage
  - 入力:
    - `R001`: P2 review finding
    - `R002`: P3 review finding
    - `C001`: failed check
  - 出力:
    - `R001`: `valid`, `blocking`, `yes`, `fix-now`, `U001`, `unit-created`
    - `C001`: `valid`, `blocking`, `yes`, `fix-now`, `U001`, `unit-created`
    - `R002`: `valid`, `minor`, `follow-up`, `follow-up`, empty unit, `triaged`
    - `U001`: repair unit `disc` が作成され、repair worker がその plan から実装する。

- EX-002: review-clean ではないが merge-prepared
  - 入力:
    - Codex review が P3 の operator clarity finding を残している。
    - CI は成功し、P0 / P1 / blocking P2 はない。
  - 出力:
    - finding は `valid`, `minor`, `follow-up`, `follow-up` として rationale と revisit condition を batch に残す。
    - `review-clean: no` だが `merge-prepared: yes` と報告できる。

## 用語（ドメイン語彙）

- TERM-001: PR Repair Triage Gate
  - `github-pr-observation` 後、fix delegation 前に、すべての finding / failure / limitation を batch inventory に載せ、妥当性、修正必要性、disposition、repair unit grouping を決める gate。
- TERM-002: PR repair batch
  - 1 observation result / 1 repair loop batch ごとに作る control artifact。既存 `disc` として作成するが、PR repair batch 専用 template を使う。
- TERM-003: repair unit
  - 同じ root cause または同じ修正単位に束ねた detail artifact。既存 `disc` として作成する。
- TERM-004: review-clean
  - Codex review が no major issues / no actionable review を返している状態。
- TERM-005: merge-prepared
  - CI / review / merge blocker と residual risks が整理され、人間が merge 判断できる状態。必ずしも review-clean ではない。

## 未確定事項

- なし。
