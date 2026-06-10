---
種別: disc
ID: "20260610t031332z-disc"
タイトル: "PR Repair Batch Dedicated Sheet Analysis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["iss-00178"]
関連:
  - "20260610t022800z-interview-pr-repair-template-scope.md"
  - "20260609t154515z-disc-pr-repair-triage-workflow-proposal.md"
  - "github-pr-merge-preparer"
  - "github-pr-observation"
authority: "proposed"
derived_from:
  - "Deep Consultant: 019eaf82-3fe3-7a82-a610-7084e43ddcf9"
  - "spec-dock/templates/discussions/disc.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py"
reflected_to: []
---

# 20260610t031332z-disc PR Repair Batch Dedicated Sheet Analysis

## 対象論点

`iss-00178 Review Feedback Triage` の要件定義に入る前に、ユーザー回答で示された第三案を評価する。

第三案:

- PR repair batch は、複数の review finding / CI failure / log / observation limitation を 1 枚にまとめ、妥当性、修正必要性、関心ごとの分類、repair unit 作成判断まで扱うため、既存の通常 `disc` template では足りない。専用 structured sheet が必要。
- repair unit は、個別の修正単位について分析・設計・計画を行うため、既存の `disc` template / discussion sheet で対応できる可能性がある。

## 確認した実装事実

- 現行 `new doc` runtime は `--template` option を持たない。
- `new doc disc` は `spec-dock/templates/discussions/disc.md` を読む。
- provider-side source of truth も `src/spec_dock/assets/spec_dock/templates/discussions/disc.md` であり、`disc` template は synthesis / tradeoff / adoption target / ADR triage の汎用構造である。
- `CreateDiscussionDocRequest` と `commands/new.py` の discussion doc catalog は、`adr` / `disc` / `research` / `interview` / `scratch` / `draft-requirement` / `draft-design` / `draft-plan` を扱う。
- `--template pr-repair-batch` を CLI として実装する場合、runtime parser、application template resolution、provider-side templates、docs、tests まで変更範囲が広がる。

## Deep Consultant の結論

Deep Consultant は第三案を妥当と評価した。

要点:

- batch と unit は責務が異なる。
- batch は control sheet であり、複数 input を inventory 化し、classification、repair unit grouping、stop condition、merge-prepared gate を管理する。通常 `disc` template だけでは構造が安定しない。
- unit は detail artifact であり、ひとつの修正単位について synthesis / proposal / options / implementation plan を深掘りする。これは既存 `disc` の意味論に自然に収まる。
- 初期実装では first-class doc type や runtime `--template` ではなく、既存 `disc` に専用 skeleton を流し込む運用が適切。
- runtime `--template` 昇格は、複数 agent が skeleton 転記を頻繁に誤る、機械検証したい、CLI 生成が workflow 成功条件になる、pilot で構造が安定した、などの条件が揃ってからでよい。

## Codex の分析

### batch は専用 structured sheet が必要

ユーザー案のうち、batch 専用シートは採用するべきである。

理由:

- batch は「議論」だけではなく、PR 修正ループの制御面である。
- 複数の review finding / CI failure / log / observation limitation を欠落なく inventory 化する必要がある。
- 各 item に対して、妥当性と修正必要性を分けて判断する必要がある。
- 関心ごとの grouping、repair unit 作成要否、`no-action` / `follow-up` / `covered-by` の rationale を同じシートで追跡する必要がある。
- merge-prepared 判定時に、untriaged item、未解決 `needs-human`、未完了 blocking unit が残っていないことを確認する必要がある。

既存 `disc` template は synthesis / tradeoff には向いているが、batch control sheet の inventory / status / gate には不足する。

### unit は既存 disc でよい

repair unit は、少なくとも初期実装では既存 `disc` として扱ってよい。

理由:

- repair unit は「同じ root cause / 同じ修正単位について、妥当性、root cause、選択肢、推奨案、実装計画、検証計画を整理する」artifact である。
- これは `disc` の synthesis / option framing / recommendation という意味論に合う。
- unit ごとに first-class doc type や runtime template を作ると、軽量に閉じたい修正まで形式化が重くなる。

ただし、通常 `disc` をそのまま自由記述で使うだけでは弱い。`github-pr-merge-preparer` skill に、repair unit `disc` の必須チェックリストを明記する必要がある。

## 推奨する方針

### 今回の issue で採用する

- PR repair batch は、既存 `disc` として作成するが、通常 `disc` ではなく **PR repair batch dedicated skeleton** を使う。
- repair unit は、既存 `disc` として作成し、skill guidance の必須チェックリストで補強する。
- `github-pr-merge-preparer` skill は observation 後、fix delegation 前に PR Repair Triage Gate を通す。
- `github-pr-observation` は evidence collection 境界を維持し、risk / disposition / grouping を持たない。

### 今回の issue では対象外にする

- 新しい first-class doc type の追加。
- `new doc disc --template pr-repair-batch` / `--template pr-repair-unit` の runtime 実装。
- 自動分類 runtime。
- CI log parser。
- GitHub API judgment の追加。

### 将来 follow-up として検討する

runtime `--template` は有望だが、今回の初期実装では急がない。

昇格判断基準:

- agent が skeleton 転記を頻繁に誤る。
- batch 構造を `spec-dock validate` などで機械検証したい。
- CLI だけで deterministic に dedicated sheet を生成することが workflow の成功条件になる。
- batch skeleton の語彙と構造が pilot 運用で安定する。

## batch dedicated skeleton に必要な section

batch artifact は最低限、次を持つ。

- `PR / Observation Metadata`
- `Batch Purpose`
- `Concern Catalog`
- `Inventory`
- `Classification Values`
- `Per-Concern Analysis`
- `Repair Queue`
- `Unit Discussion Plan`
- `Stop Conditions`
- `Merge-Prepared Gate`

Inventory の item は最低限、次を持つ。

- `ID`
- `source_type`
- `concern`
- `evidence`
- `summary`
- `validity`
- `risk_class`
- `need_to_fix`
- `disposition`
- `repair_unit`
- `status`

分類値:

- `validity`: `valid` / `partially-valid` / `false-positive` / `duplicate` / `unknown`
- `risk_class`: `blocking` / `material-follow-up` / `minor` / `false-positive` / `duplicate`
- `need_to_fix`: `yes` / `no` / `follow-up` / `human-decision`
- `disposition`: `fix-now` / `follow-up` / `no-action` / `covered-by` / `needs-human`
- `status`: `untriaged` / `triaged` / `unit-needed` / `unit-created` / `implemented` / `reobserved-pass` / `blocked`

## repair unit disc に必要な補強

repair unit `disc` は、通常 `disc` template をベースにしてよいが、以下を必須チェックリストとして扱う。

- `source_batch`
- `unit_id`
- `covered_ids`
- `source_links`
- `failure_class`
- `risk_class`
- `disposition`
- `Validity Analysis`
- `Need-To-Fix Decision`
- `Root Cause`
- `Options Considered`
- `Recommended Design`
- `Implementation Plan`
- `Validation Plan`
- `Implementation Result`
- `Commit Evidence`
- `Re-observation Result`
- `Residual Risk / Follow-up`

運用ルール:

- batch inventory の `repair_unit` と unit disc の `unit_id` は一致する。
- `fix-now` / `needs-human` で実装修正・設計判断が必要なものは repair unit `disc` を作る。
- `covered-by` / `duplicate` / `no-action` / `follow-up` は、batch 内 rationale だけで閉じてよい。
- repair worker は raw finding ではなく repair unit `disc` の implementation plan を source of truth とする。
- 計画逸脱が必要な場合は unit disc へ追記するか human gate に戻す。

## 要件への反映案

`requirement.md` には以下を採用する。

- 必須:
  - `github-pr-merge-preparer` は observation 後、fix delegation 前に PR Repair Triage Gate を実行する。
  - すべての review finding / CI failure / merge blocker / observation limitation を batch inventory に載せる。
  - batch artifact は existing `disc` として作成するが、PR repair batch dedicated skeleton を使う。
  - batch artifact は複数関心ごとの妥当性、修正必要性、repair unit 作成判断を 1 枚で管理する。
  - 実装修正または human decision が必要なものは repair unit `disc` に紐づける。
  - merge-prepared 判定では、untriaged item、未解決 `needs-human`、blocking かつ未完了の repair unit が残っていないことを要求する。
- 対象外:
  - first-class doc type 追加。
  - runtime `--template` 実装。
  - 自動分類 runtime / CI log parser。
- 受け入れ条件:
  - skill / docs から batch dedicated skeleton と classification vocabulary が確認できる。
  - repair unit `disc` の必須チェックリストが確認できる。
  - `github-pr-observation` の collection-only boundary が保たれている。

## 残る論点

専用 batch skeleton の正本の置き場所を決める必要がある。

推奨:

- full skeleton と実行手順は `github-pr-merge-preparer` skill に置く。
- `discussions.md` には catalog 上の短い契約だけを置く。

理由:

- 実際に batch を作成する主体は `github-pr-merge-preparer` workflow である。
- `discussions.md` に長大 skeleton を置くと、discussion catalog の参照文書として重くなる。
- 将来 runtime `--template` に昇格する場合、skill 内 skeleton を pilot source として provider-side template へ切り出せる。

## 推奨結論

要件定義では、ユーザー案を採用し、以下の形で確定するのがよい。

- PR repair batch: 既存 `disc` だが専用 structured skeleton 必須。
- PR repair unit: 既存 `disc` を利用し、skill 上の必須チェックリストで補強。
- runtime `--template`: 今回は対象外、pilot 後の follow-up。
- first-class doc type: 今回は対象外。
