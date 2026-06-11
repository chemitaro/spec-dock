---
種別: disc
ID: "20260609t154515z-disc"
タイトル: "PR Repair Triage Workflow Proposal"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["iss-00178"]
関連:
  - "20260609t151424z-research-review-feedback-triage-policy.md"
  - "20260609t152616z-research-historical-p2-p3-review-analysis.md"
  - "github-pr-merge-preparer"
  - "github-pr-observation"
authority: "proposed"
derived_from:
  - "Deep Consultant: PR repair triage workflow analysis"
  - ".agents/skills/github-pr-merge-preparer/SKILL.md"
  - ".agents/skills/github-pr-observation/SKILL.md"
reflected_to: []
---

# 20260609t154515z-disc PR Repair Triage Workflow Proposal

## 対象論点

PR observation が CI/CD、review、review threads、Codex review body を安定して収集できるようになった後、複数の review finding や CI failure をどのように扱うべきかを整理する。

現在の `github-pr-merge-preparer` は、coarse failure classification、bounded fix delegation、再 monitor、merge-prepared 判定を持っている。一方で、複数の finding / failure を一度に受け取った後、修正前に妥当性・優先度・修正単位・設計・計画を整理する workflow が薄い。そのため、場当たり的に修正し、再 push し、また review / CI を待つ運用になりやすい。

この提案では、PR 修正ループに **PR Repair Triage Gate** を追加し、修正前に analysis / design / plan を軽量だが明示的に通す仕組みを定義する。

## 参照した根拠

- `github-pr-merge-preparer/SKILL.md`
  - 現在は observation 後に coarse labels で分類し、明確に actionable な implementation failure / review feedback だけ bounded fixes へ委任する。
  - ただし、finding ごとの妥当性分析、risk class、disposition、repair unit grouping、設計・計画 artifact の作成は明示されていない。
- `github-pr-observation/SKILL.md`
  - observation は証拠収集の責務を持つ。
  - stdout JSON が authoritative evidence であり、review body / selected review comment body を含む。
- `20260609t151424z-research-review-feedback-triage-policy.md`
  - P2 / P3 は severity だけではなく risk class / disposition で扱うべきと整理。
- `20260609t152616z-research-historical-p2-p3-review-analysis.md`
  - 過去 142 件の P2 / P3 finding のうち 128 件が `対処すべき`、13 件が `follow-up 可`、1 件が `軽微`。
  - P2 は軽視すべきではないが、全件を同じ重さで current PR 修正対象にするのも過剰。
- Deep Consultant
  - `1 observation batch = 1 control artifact` と `1 repair unit = 1 detail artifact` のハイブリッドを推奨。

## synthesis

### 合意できること

- Review / CI failure は全件収集し、全件 inventory に載せるべきである。
- ただし、全 raw finding に full analysis / full design / full plan を要求すると過剰である。
- 修正実行の単位は raw finding ではなく、同じ根本原因または同じ修正単位に束ねた **repair unit** にするべきである。
- CI failure と review finding は intake では分けるべきだが、同じ root cause に収束する場合は同じ repair unit に統合すべきである。
- `github-pr-observation` は証拠収集に留め、disposition や修正方針の判断は `github-pr-merge-preparer` に置くべきである。
- SpecDock runtime は GitHub API 判断を持つのではなく、discussion artifact template / 作成支援だけを持つのが安全である。

### 重要な設計判断

`1 raw finding = 1 Markdown file` は採用しない。

理由:

- 同一 root cause が複数 CI job に出ることがある。
- 同じ review loop で同種の review finding が複数出ることがある。
- finding ごとに full sheet を作ると、軽微・重複・誤検知まで設計/計画を強制し、運用コストが高くなる。

採用する粒度:

- **PR repair batch artifact**: 1 observation result / 1 repair loop batch ごとに 1 つ作る control artifact。
- **PR repair unit artifact**: `fix-now` または `needs-human` のうち、分析・設計・計画が必要な修正単位ごとに 1 つ作る detail artifact。

## 推奨 workflow

### Phase 1: Observation Intake

1. `github-pr-observation` で PR snapshot / wait result を取得する。
2. stdout JSON、CI failure、review finding、review thread、merge state、head SHA、base SHA、trigger boundary を evidence として扱う。
3. `github-pr-merge-preparer` が observation result を読み、修正前に PR repair batch artifact を作成する。

### Phase 2: Batch Triage

PR repair batch artifact に、すべての input item を載せる。

- Review finding: `R001`, `R002`, ...
- CI/check failure: `C001`, `C002`, ...
- Merge/status blocker: `M001`, `S001`, ...

各 item に最低限、以下を付ける。

- `source_type`: `review_feedback` / `check_failure` / `merge_conflict` / `status_failure`
- `evidence`: URL、job name、comment ID、review ID、log excerpt、JSON path
- `summary`: 短い要約
- `failure_class`: `check_failure:<job>` / `review_feedback:<topic>` / `merge_conflict` / `unknown` など
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `repair_unit`: `U001` など。修正不要なら空でもよい。
- `status`: `triaged` / `planned` / `implemented` / `reobserved-pass` / `blocked`

### Phase 3: Repair Unit Design

`fix-now` または `needs-human` で、実装修正・設計判断・複数案比較が必要なものは repair unit に束ねる。

repair unit artifact には以下を記録する。

- covered finding IDs
- 問題の概要
- 妥当性分析
- 修正必要性
- root cause
- options considered
- 推奨案
- 設計具体化
- 実装計画
- validation plan
- implementation result
- commit evidence
- re-observation result
- residual risk / follow-up

軽微な `follow-up` / `no-action` / `false-positive` は、batch artifact の rationale だけで閉じてよい。すべてに repair unit artifact を作らない。

### Phase 4: Bounded Repair Execution

1. `github-pr-merge-preparer` は repair unit artifact を根拠に、bounded repair worker を起動する。
2. repair worker は artifact の implementation plan から逸脱しない。
3. 実装、検証、commit、push evidence を repair unit artifact または `report.md` に残す。
4. 1 repair unit = 1 logical commit を基本とする。ただし小さな同根修正は同一 unit に束ねてよい。

### Phase 5: Re-observation and Batch Update

1. push 後、latest head SHA を取得する。
2. `github-pr-observation` を再実行する。
3. PR repair batch artifact を更新し、各 item / repair unit の状態を `reobserved-pass` / `reobserved-fail` / `superseded` / `blocked` へ更新する。
4. 新しい finding が出た場合は、新しい batch artifact を作るか、同じ batch の follow-up section に追記する。

## artifact design

### PR Repair Batch Artifact

推奨 doc type:

- 初期実装では既存の `disc` を使うが、通常の自由記述 `disc` ではなく **PR repair batch 専用テンプレート** として扱う。
- 新しい first-class doc type はまだ作らない。
- 理由: batch は複数 finding / failure の control sheet であり、classification、関心ごとの分析、repair unit 作成判断、merge-prepared gate を束ねる必要がある。通常の `disc` より構造化が必要だが、discussion catalog を増やすほどの runtime 変更は初期スコープでは重い。
- 将来、専用 validation や UI / CLI support が必要になった場合は `pr-repair-batch` doc type への昇格を検討する。

推奨ファイル名:

```text
<ts>-disc-pr-<number>-repair-batch-<head-short-sha>.md
```

推奨作成コマンド:

```bash
./spec-dock/scripts/spec-dock new doc disc \
  --issue <issue-id> \
  --title "PR <number> Repair Batch <head-short-sha>" \
  --slug "pr-<number>-repair-batch-<head-short-sha>"
```

将来、template variant を追加する場合の理想:

```bash
./spec-dock/scripts/spec-dock new doc disc \
  --issue <issue-id> \
  --title "PR <number> Repair Batch <head-short-sha>" \
  --slug "pr-<number>-repair-batch-<head-short-sha>" \
  --template pr-repair-batch
```

template skeleton:

```md
# <DOC_ID> PR <number> Repair Batch <head-short-sha>

## PR / Observation Metadata

- PR:
- observation source:
- captured_at:
- base_ref:
- base_sha:
- head_ref:
- head_sha:
- trigger_comment_id:
- observation_status:
- observation_result_path:
- previous_batch:

## Batch Purpose

- この batch で判断すること:
- この batch の完了条件:
- この batch で実装しないこと:

## Concern Catalog

| concern | 説明 | 関連する finding / check | 修正単位候補 | 備考 |
|---|---|---|---|---|
| review-boundary | Codex review / human review / stale review の境界 | R001, R002 | U001 | ... |
| ci-typecheck | typecheck / lint / test failure | C001, C002 | U002 | ... |

## Inventory

| ID | source_type | concern | evidence | summary | validity | risk_class | need_to_fix | disposition | repair_unit | status |
|---|---|---|---|---|---|---|---|---|---|---|
| R001 | review_feedback | review-boundary | ... | ... | valid | blocking | yes | fix-now | U001 | triaged |
| C001 | check_failure | ci-typecheck | ... | ... | valid | blocking | yes | fix-now | U002 | triaged |

### Classification Values

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## Per-Concern Analysis

### <concern>

- 対象 finding / failure:
- 妥当性:
- 修正必要性:
- root cause 仮説:
- 同じ repair unit に束ねられるもの:
- 分けるべきもの:
- 推奨 disposition:

## Repair Queue

| unit | concern | covered_ids | unit_discussion | recommended_action | owner | status | commit | re_observation |
|---|---|---|---|---|---|---|---|---|
| U001 | review-boundary | R001, R002 | `discussions/...pr-123-repair-u001-review-boundary.md` | ... | dev-coder | planned | ... | ... |

## Unit Discussion Plan

この batch の末尾で、後続に作るべき repair unit discussion を明示する。

| unit | 作成要否 | covered_ids | reason | required analysis depth | proposed slug | next action |
|---|---|---|---|---|---|---|
| U001 | yes | R001, R002 | blocking かつ設計判断が必要 | full | pr-123-repair-u001-review-boundary | create unit discussion |
| U002 | no | R003 | duplicate / covered-by U001 | batch-only | - | mark covered-by |
| U003 | later | R004 | follow-up 可 | lightweight | pr-123-repair-u003-docs-clarity | create follow-up issue |

## Stop Conditions

- untriaged finding remains:
- needs-human remains:
- same failure_class repeated:
- loop budget:
- scope expansion:
- unit discussion required but missing:
- follow-up / no-action without rationale:

## Merge-Prepared Gate

- blocking findings:
- unresolved review feedback:
- required checks:
- residual risks:
- final decision:
```

### PR Repair Unit Artifact

推奨 doc type:

- 既存の `disc` を使う。
- 理由: options considered、recommended design、implementation plan を含む synthesis であるため。

推奨ファイル名:

```text
<ts>-disc-pr-<number>-repair-u<nnn>-<topic>.md
```

推奨作成コマンド:

```bash
./spec-dock/scripts/spec-dock new doc disc \
  --issue <issue-id> \
  --title "PR <number> Repair U001 <topic>" \
  --slug "pr-<number>-repair-u001-<topic>"
```

将来、template variant を追加する場合の理想:

```bash
./spec-dock/scripts/spec-dock new doc disc \
  --issue <issue-id> \
  --title "PR <number> Repair U001 <topic>" \
  --slug "pr-<number>-repair-u001-<topic>" \
  --template pr-repair-unit
```

template skeleton:

```md
# <DOC_ID> PR <number> Repair U001 <topic>

## Unit Metadata

- unit_id:
- source_batch:
- covered_ids:
- source_links:
- failure_class:
- risk_class:
- disposition:
- owner:
- status:

## Summary

## Validity Analysis

- finding は妥当か:
- 根拠:
- 誤検知 / 重複 / covered-by の可能性:

## Need-To-Fix Decision

- decision: fix-now | follow-up | no-action | needs-human
- rationale:
- risk if not fixed:
- follow-up target:

## Root Cause

## Options Considered

| option | summary | pros | cons | decision |
|---|---|---|---|---|

## Recommended Design

## Implementation Plan

1. ...

## Validation Plan

- local command:
- CI/check expectation:
- review expectation:

## Implementation Result

- changed files:
- summary:
- deviations from plan:

## Commit Evidence

- commit:
- push:

## Re-observation Result

- observation command:
- head_sha:
- result:

## Residual Risk / Follow-up
```

## classification vocabulary

### source_type

- `review_feedback`
- `check_failure`
- `merge_conflict`
- `status_failure`
- `observation_limit`
- `unknown`

### risk_class

- `blocking`: 修正しないと merge-prepared にできない。
- `material-follow-up`: 正しいが current PR ではなく follow-up にできる。
- `minor`: 軽微。no-action / follow-up 可。
- `false-positive`: 指摘の前提が誤り。
- `duplicate`: 他 finding / repair unit に含まれる。

### disposition

- `fix-now`: この PR で修正する。
- `follow-up`: follow-up issue / discussion に送る。
- `no-action`: 修正しない。理由必須。
- `covered-by`: 他 repair unit に含める。
- `needs-human`: 人間判断が必要。

### repair_status

- `untriaged`
- `triaged`
- `planned`
- `implementing`
- `committed`
- `pushed`
- `reobserved-pass`
- `reobserved-fail`
- `blocked`
- `superseded`

## stop conditions

PR repair loop は、以下のいずれかで止める。

- untriaged finding が残っている。
- `needs-human` が未解決。
- `blocking` + `fix-now` の repair unit が未完了。
- same `failure_class` が 2 回再発した。
- total repair loop が 4 回に達した。
- 修正が current issue / current PR scope を超える。
- migration、secret、外部サービス設定、破壊的操作、権限変更が必要。
- CI log / review context が不足し、妥当性を判断できない。
- `follow-up` disposition に rationale / owner / revisit condition がない。
- `no-action` disposition に risk acceptance rationale がない。

## この issue で実装するべき内容

### 採用する最小スコープ

この issue では、巨大な自動分類 runtime を作らない。まずは workflow / template / skill guidance の pilot として実装する。

推奨スコープ:

1. `github-pr-merge-preparer` skill に **PR Repair Triage Gate** を追加する。
2. `github-pr-merge-preparer` skill に、observation 後・fix delegation 前に batch artifact を作る手順を追加する。
3. `github-pr-merge-preparer` skill に、repair unit artifact を根拠に bounded repair worker へ委任する手順を追加する。
4. `github-pr-merge-preparer` skill に、merge-prepared 判定時に untriaged / unresolved / needs-human / blocking repair unit がゼロであることを要求する。
5. `github-pr-observation` skill は責務を変えず、判断を持たせないことを明記する。
6. `spec-dock` の discussion docs guidance に、PR repair batch / repair unit は `disc` として作成する運用を追記する。
7. batch artifact は、複数の関心ごとの分析、妥当性、修正必要性、classification、repair unit discussion 作成計画を入力できる専用シートとして定義する。
8. テンプレートそのものは、まず docs / skill 内の skeleton として提供する。

### template variant を入れるか

初期実装では `new doc` の新 doc_type 追加は避ける。ただし、PR repair batch は通常の `disc` ではなく専用テンプレートとして扱う。

理由:

- discussion catalog を増やすと runtime / validation / docs / tests の影響が広い。
- `disc` が用途として近い。
- まず workflow と skeleton で運用できるか試す方が安全。

ただし、将来の follow-up として `new doc disc --template pr-repair-batch` / `--template pr-repair-unit` の template variant は有望である。

テンプレート化の優先度:

1. `pr-repair-batch` 専用テンプレートを優先する。
   - 複数 finding / CI failure の classification と repair unit 作成判断を支えるため、構造化の効果が最も大きい。
   - batch 末尾に `Unit Discussion Plan` を置き、どの repair unit discussion を作るか、作らない場合はなぜ作らないかを明示する。
2. `pr-repair-unit` 専用テンプレートを次に追加する。
   - unit discussion は通常の `disc` でも運用できるが、妥当性分析、options considered、implementation plan、validation、commit evidence を安定して残すには専用 skeleton がある方がよい。

この issue で template variant まで入れる場合は、以下を追加 scope とする。

- `new doc` に `--template` optional argument を追加。
- `disc` doc type のみ `default`, `pr-repair-batch`, `pr-repair-unit` を許可。
- template file を `templates/discussions/disc/pr-repair-batch.md` のような下位 path に置くか、template registry を導入する。

ただしこれは runtime scope が広がるため、初期 issue では非推奨。

## 推奨する acceptance criteria

- `github-pr-merge-preparer` は observation 後、fix delegation 前に PR Repair Triage Gate を通すよう記述されている。
- 全 review finding / CI failure / merge blocker は batch inventory に載せる必要がある。
- 各 item は `risk_class` と `disposition` を持つ。
- 各 item は `validity` と `need_to_fix` を持ち、妥当性と修正必要性を分けて判断できる。
- batch artifact は `Concern Catalog` と `Per-Concern Analysis` を持ち、複数 finding / failure を関心ごとに束ねて分析できる。
- batch artifact は末尾に `Unit Discussion Plan` を持ち、作成すべき repair unit discussion、作成しない理由、follow-up 化する理由を明示できる。
- `fix-now` / `needs-human` は repair unit に紐づく。
- repair worker は repair unit artifact を根拠に実装する。
- repair unit は妥当性分析、root cause、options considered、recommended design、implementation plan、validation plan を持つ。
- commit hash、検証コマンド、push evidence、re-observation result が repair unit または report に残る。
- `merge-prepared` 判定時、untriaged / unresolved `needs-human` / blocking unfixed repair unit がゼロである。
- `follow-up` / `no-action` は rationale と residual risk を持つ。
- `github-pr-observation` は observation-only boundary を維持する。

## リスク / tradeoff

### 形式化しすぎるリスク

全 finding に full sheet を要求すると、レビュー修正が重くなりすぎる。特に P3、重複、明白な false positive、docs typo、低影響 test coverage finding まで詳細設計を要求すると、開発速度を落とす。

対策:

- full detail artifact は repair unit だけに要求する。
- batch inventory だけで閉じてよい finding を許可する。
- `covered-by` / `duplicate` / `no-action` / `follow-up` を正式な disposition として扱う。

### 場当たり修正が残るリスク

batch artifact だけだと、修正の設計・計画が薄くなり、worker が場当たり的に実装し続ける可能性がある。

対策:

- `fix-now` は repair unit artifact 必須にする。
- repair worker は repair unit artifact の plan を source of truth とする。
- 計画逸脱は artifact に追記し、必要なら human gate に戻す。

### observation と judgment が混ざるリスク

`github-pr-observation` に risk class / disposition を持たせると、収集 script が判断責務を持ち始める。

対策:

- observation は JSON evidence の収集まで。
- risk / disposition / repair unit grouping は `github-pr-merge-preparer` の責務。

## 結論

この issue では、PR review / CI failure の収集後に **PR Repair Triage Gate** を追加する方針が妥当である。

ベストプラクティスは、`1 observation batch = 1 control artifact` と `1 repair unit = 1 detail artifact` のハイブリッドである。

これにより、すべての finding / failure を収集・分析しつつ、全 raw finding に過剰な設計書を作らず、同じ根本原因を一つの修正単位へ束ねられる。結果として、場当たり的な修正を減らし、修正前の妥当性分析、設計、計画、実装、検証、再 observation の一連の evidence を残せる。
