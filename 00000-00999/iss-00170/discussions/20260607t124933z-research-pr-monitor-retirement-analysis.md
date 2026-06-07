---
種別: リサーチ
ID: "20260607t124933z-research"
タイトル: "PR monitor sub-agent retirement analysis"
関連Issue: "iss-00170"
作成者: "orchestrator"
作成日: "2026-06-07"
情報源:
  - "user追加仮説: pr-monitor sub-agent は github-pr-observation skill/script に置き換えられるのではないか"
  - "deep-consultant Lagrange: 2026-06-07"
  - "src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml"
  - "src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/report.md"
状態: "draft"
---

# PR monitor sub-agent retirement analysis

## 1. 目的

`iss-00170` では、PR 作成後または push 後の checks / statuses / reviews の観測を、推論モデルの polling loop ではなく deterministic script に移す方針へ転換した。

さらに、旧 `github-codex-pr-review-comments/` skill は新 `github-pr-observation/` skill へ統合して削除する方針が推奨された。

この追加リサーチでは、さらに一段進めて、`pr-monitor` sub-agent 自体が必要かを分析する。

ユーザー仮説は次である。

- `pr-monitor` が実施していたことのほぼすべては、新しい script / skill で実施できる。
- 最新設計では `pr-monitor` は script を実行して結果を返すだけになる。
- それなら `pr-monitor` sub-agent を廃止し、`github-pr-observation` skill / scripts を正規入口にした方がシンプルではないか。

## 2. 現行参照状況

現行の provider-side sub-agent asset は次に存在する。

```text
src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml
src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md
```

dogfooding mirror にも次が存在する。

```text
.codex/agents/pr-monitor.toml
.github/agents/pr-monitor.agent.md
```

現行 `github-pr-merge-preparer` は、workflow step 5 で `pr-monitor` を呼ぶ契約を持つ。

```text
Invoke `pr-monitor` with `repo`, `pr`, `head_sha`, and `reason: created | pushed | repushed`.
```

現行 `github-pr-creator` も、PR 作成後に `pr-monitor` へ handoff する契約を持つ。

```text
After PR creation, the main orchestrator should hand off PR monitoring to `pr-monitor`.
```

`iss-00170` の現行 requirement / design / report も、直前の設計では `pr-monitor` を read-only summarizer / classifier として残す前提を持つ。

このため、`pr-monitor` を廃止する場合は、単に agent asset を消すだけではなく、少なくとも次を更新する必要がある。

- `github-pr-merge-preparer` の monitoring step。
- `github-pr-creator` の post-create handoff。
- main orchestrator / collaboration guidance の role routing。
- `iss-00170` requirement / design / ADR / plan。
- provider-side `.codex/agents` / `.github/agents` asset inventory。
- dogfooding mirror parity。
- tests / update cleanup。

## 3. Deep Consultant の結論

Deep Consultant の結論は次である。

```text
`pr-monitor` sub-agent は廃止し、`github-pr-observation` skill/script を正規入口にするのが最適である。
```

代替入口は明確に2つへ分ける。

```text
即時観測:
  .agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh

待機込み観測:
  .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
```

移行期間だけ既存参照を壊さないための deprecated shim として `pr-monitor` 名を残す余地はある。

ただし target architecture では、`pr-monitor` は独立した sub-agent ではなく削除対象である。

## 4. `pr-monitor` を残す場合の実質価値

`pr-monitor` を残す場合に考えられる価値は次である。

- 長時間観測を main orchestrator の文脈から隔離する。
- human-friendly summary を返す。
- host 差を吸収する。
- sub-agent sandbox / read-only posture を見た目上の境界として使う。
- caller が JSON parsing / artifact reading を直接行わずに済む。

しかし、今回の中核方針では、次をすべて deterministic script に移す。

- polling loop
- sleep
- timeout
- quiet window
- same fingerprint count
- progress delta
- final JSON
- checks/statuses collection
- reviews/comments/thread/request collection

この前提が成立すると、`pr-monitor` の仕事は「script を起動して final JSON を要約する」だけになる。

これは独立 sub-agent としては責務が薄い。

また、human-friendly summary は `summary.md` artifact、final JSON の `summary` field、または caller 側の要約規約で代替できる。

長時間観測の context 汚染も、stdout final JSON only、stderr bounded progress、`events.ndjson` / `latest_delta.json` / `result.json` によって抑制できる。

host 差についても、sub-agent が同じ script executor を呼ぶだけなら根本解決にはならない。必要なのは skill 側の prerequisites / fallback policy である。

## 5. `pr-monitor` を残す場合の問題

`pr-monitor` を残すと、次の問題が残る。

### 5.1 責務境界が曖昧になる

polling 判断をモデルから剥がしたにもかかわらず、入口だけ agent に残る。

その結果、`pr-monitor` がどこまで final JSON を解釈してよいか、progress をどう扱うか、timeout をどう説明するかが再び prompt behavior に寄る。

### 5.2 二重メンテになる

同じ観測 contract を次の複数箇所に持つことになる。

- `github-pr-observation` skill docs
- `wait_pr_observation.sh` usage
- `fetch_pr_observation_snapshot.sh` schema
- Codex host の `pr-monitor.toml`
- GitHub host の `pr-monitor.agent.md`
- workflow skills の `pr-monitor` handoff 文言

script が正になった後も agent guidance を保守し続けるのは、単純性に反する。

### 5.3 final JSON の情報落ちリスクが増える

script の stdout final JSON / artifacts が authority である。

`pr-monitor` がその上に要約層として入ると、caller が見る情報は agent の自然言語要約になりやすい。

これにより、machine-readable な limitation、stale head、thread-state unknown、zero-check grace、artifact path などが落ちる可能性がある。

### 5.4 テスト対象が広がる

本来は script contract を fixture / fake clock / fake snapshot でテストすればよい。

`pr-monitor` を残すと、agent prompt の behavior も受け入れ対象になり、テスト容易性が下がる。

### 5.5 security boundary と誤解される

sub-agent は便利な実行主体ではあるが、厳密な security boundary ではない。

read-only 境界は、agent role ではなく、fixed read-only script / command rule / mutation command 不在で守るべきである。

## 6. 推奨アーキテクチャ

推奨アーキテクチャは次である。

```text
main orchestrator / github-pr-merge-preparer / github-pr-creator
  -> github-pr-observation skill
      -> scripts/wait_pr_observation.sh
      -> scripts/fetch_pr_observation_snapshot.sh
      -> scripts/lib/fetch_pr_checks_snapshot.sh
      -> scripts/lib/fetch_pr_review_snapshot.sh
```

### 6.1 `github-pr-observation`

`github-pr-observation` は read-only PR observation capability とする。

この skill は次を保持する。

- usage guide
- prerequisites
- fixed command contract
- snapshot schema
- wait final JSON schema
- progress artifact contract
- limitations / status taxonomy
- read-only / no mutation rules

### 6.2 `fetch_pr_observation_snapshot.sh`

一回限りの現在値取得に限定する。

用途:

- PR 作成直後の軽い確認。
- ユーザーからの「今どうなっているか」確認。
- timeout 後の再確認。
- debug / audit。

責務:

- PR current head SHA の取得。
- checks/statuses の正規化。
- review-related signals の正規化。
- all / Codex / human / bot subset の分類。
- fingerprint 出力。

待機はしない。

### 6.3 `wait_pr_observation.sh`

bounded polling の唯一の実装とする。

責務:

- sleep
- timeout
- quiet window
- same fingerprint count
- zero-check grace
- head change detection
- progress delta
- final status classification
- final JSON output
- durable artifacts

stdout は final JSON 専用にする。

progress は stderr または progress JSONL artifact に出す。

### 6.4 `github-pr-merge-preparer`

PR 作成後または push 後に `wait_pr_observation.sh` を直接呼ぶ。

結果に応じて次へ進む。

- `ready` / equivalent:
  - human merge decision へ渡す。
- `checks_failed`:
  - failure class を作って bounded fix lane へ進む。
- `changes_requested` / review blocker:
  - actionable review feedback と source signal を repair worker へ渡す。
- `timeout`:
  - merge-prepared ではないと報告し、human gate へ進む。
- `stale_head`:
  - latest head SHA を取り直して再観測するか、human gate へ進む。

### 6.5 `github-pr-creator`

単なる PR 作成が目的なら、PR URL / number / head SHA を返して終了してよい。

PR 作成直後の軽い確認が必要なら `fetch_pr_observation_snapshot.sh` を使う。

「レビューを通過する」「merge-prepared まで進める」ことが要求される場合は、`github-pr-merge-preparer` または `wait_pr_observation.sh` の contract へ進む。

`pr-monitor` への handoff は廃止する。

### 6.6 main orchestrator

明示的に待つ必要がある場合だけ `wait_pr_observation.sh` を使う。

単なる現状確認では `fetch_pr_observation_snapshot.sh` を使う。

モデル自身が polling loop / sleep / timeout 判断を行わないことを guidance に明記する。

## 7. 廃止リスクと対処

### 7.1 host capability 差

リスク:

- shell / `gh` / 長時間 command が使えない host では、script を直接実行できない。

対処:

- `github-pr-observation` skill に prerequisites を明記する。
- `gh` 不在、auth 不備、shell 実行不可は observation unavailable として machine-readable に返す。
- sub-agent を残しても同じ script executor を使うだけなら根本解決にならないため、sub-agent 維持理由にはしない。

### 7.2 長時間コマンド実行

リスク:

- foreground wait が長く、host timeout / user不安 / log肥大につながる。

対処:

- `wait_pr_observation.sh` は timeout 必須。
- default timeout を conservative にする。
- progress は bounded stderr summary / `events.ndjson` / `latest_delta.json` に出す。
- stdout は final JSON only。
- 無期限監視を禁止する。

### 7.3 結果要約

リスク:

- agent が要約しないと、人間向け報告が薄くなる。

対処:

- final JSON に `summary`, `recommended_next_action`, `limitations`, `artifacts` を持たせる。
- 必要なら `summary.md` artifact を生成する。
- caller は final JSON を根拠に短い日本語要約を返す。

### 7.4 権限境界

リスク:

- sub-agent read-only sandbox がなくなるように見える。

対処:

- observation skill / scripts は read-only command だけを持つ。
- arbitrary endpoint / method / GraphQL query / body / header / jq expression / write command passthrough を禁止する。
- mutation command は `github-pr-observation` に置かない。
- command rule / tests で write operation 不在を確認する。

### 7.5 sub-agent isolation

リスク:

- main context に長い logs が流れる。

対処:

- progress は bounded にする。
- raw data は artifacts に逃がす。
- final response は final JSON の要点だけを返す。

### 7.6 future extensibility

リスク:

- 将来、policy arbitration や複雑な判断が必要になったときに agent がない。

対処:

- collector 追加、schema versioning、artifact contract で拡張する。
- 将来、非決定的な cross-repo policy judgement が必要になった場合だけ、別 agent を再導入する。
- 現時点では script executor 化した `pr-monitor` を残すより、必要になった時に新しい役割として設計し直す方がよい。

## 8. 要件・設計・ADR への反映事項

### 8.1 ADR

既存 ADR は次を前提にしていた。

```text
`pr-monitor` は read-only summarizer / classifier として残す。
```

新しい判断では、これを取り消す。

置き換える判断:

```text
PR monitoring を `pr-monitor` sub-agent から deterministic `github-pr-observation` skill / scripts へ移管する。
```

ADR に追加すべき却下案:

- `pr-monitor` を script executor として残す案。

却下理由:

- 責務が薄い。
- skill/script と sub-agent guidance の二重メンテになる。
- final JSON authority の情報落ちリスクがある。
- prompt behavior が受け入れ対象に残る。
- 非決定性の再混入につながる。

### 8.2 要件定義

要件定義では次を修正する。

- 目的を「`pr-monitor` を強化する」から「PR observation を deterministic read-only skill/script に移管する」へ変える。
- `pr-monitor` を read-only summarizer として残す記述を削除する。
- `github-pr-observation` を正規入口とする。
- `fetch_pr_observation_snapshot.sh` と `wait_pr_observation.sh` を明確に分ける。
- model / agent は polling loop / sleep / timeout 判定を行わない、と明記する。
- `pr-monitor` asset retirement を scope / acceptance criteria に追加する。
- `github-pr-merge-preparer` / `github-pr-creator` の handoff 先を `pr-monitor` から `github-pr-observation` へ変更する。

### 8.3 設計

設計では次を修正する。

- module diagram から `pr-monitor agent` を削除する。
- `github-pr-merge-preparer` / main orchestrator / PR creator が `github-pr-observation` scripts を直接呼ぶ図へ変更する。
- provider file plan から次を削除対象にする。

```text
src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml
src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md
.codex/agents/pr-monitor.toml
.github/agents/pr-monitor.agent.md
```

- 新設対象を次にする。

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/
```

- `github-pr-merge-preparer` と `github-pr-creator` の skill docs 更新を設計に含める。
- schema prefix を `github-pr-observation.wait.v1` / `github-pr-observation.snapshot.v1` にする。

### 8.4 実装計画

実装計画は、ADR / requirement / design 更新後に再生成する。

計画には次を含める。

- `pr-monitor` 参照箇所の完全 inventory。
- `pr-monitor` provider / mirror assets 削除。
- `github-codex-pr-review-comments/` 機能を `github-pr-observation` collector に統合して旧 skill 削除。
- `github-pr-merge-preparer` の monitoring step を `wait_pr_observation.sh` 呼び出しへ更新。
- `github-pr-creator` の post-create behavior を snapshot default / wait optional に整理。
- command rule / exec policy / tests の更新。
- init / update で旧 managed assets が残らないことの検証。
- dogfooding repo で agent なしの PR observation path を確認。

## 9. 推奨判断

本リサーチとしての推奨判断は次である。

```text
`pr-monitor` sub-agent は廃止する。
PR monitoring / observation の正規入口は `github-pr-observation` skill / scripts とする。
待機込み観測は `wait_pr_observation.sh`、即時観測は `fetch_pr_observation_snapshot.sh` が担う。
`github-pr-merge-preparer` / `github-pr-creator` / main orchestrator は `pr-monitor` へ handoff せず、必要に応じて `github-pr-observation` を直接使う。
```

この判断により、今回の改善目的である「モデルが loop 判断をしない」「観測を deterministic / testable / read-only にする」「古い重複 asset を残さない」を最もシンプルに満たせる。

`pr-monitor` は、今回の新設計では独立した責務を持たない。

将来、PR observation とは別に、cross-repo policy judgement や複雑な human-facing triage が必要になった場合は、その時点で新しい role として設計し直す方がよい。
