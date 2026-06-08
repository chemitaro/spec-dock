---
種別: リサーチ
ID: "20260607t110532z-research"
タイトル: "PR observation skill retirement and naming"
関連Issue: "iss-00170"
作成者: "orchestrator"
作成日: "2026-06-07"
情報源:
  - "user追加懸念: github-codex-pr-review-comments削除 / github-pr-stable-observation名称再考 / pr-monitor専用化 vs skill公開"
  - "deep-consultant Bacon: 2026-06-07"
  - "src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh"
  - "src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml"
  - "src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md"
状態: "draft"
---

# PR observation skill retirement and naming

## 1. 目的

`iss-00170` の設計では、PR monitor の観測を deterministic script に移し、`pr-monitor` agent は wait script を1回実行して final JSON を要約する方針に転換した。

その後、ユーザーから次の懸念が提示された。

- 既存 `github-codex-pr-review-comments/` は役目を終えるのではないか。
- 互換性維持のために古い skill を残すより、重複や衝突を回収して新機能に統合した方がよいのではないか。
- `github-pr-stable-observation/` という名称の `stable` は、利用側 agent には内部事情であり、skill 名としては再考すべきではないか。
- 実際の利用者が `pr-monitor` sub-agent なら、script 仕様を独立 skill として公開するべきか、`pr-monitor` の developer instructions / 内部知識に閉じるべきか。

本リサーチは、この追加論点について Deep Consultant に分析を依頼し、要件・設計・ADR に反映すべき方向を整理する。

## 2. 現行実装の確認

### 2.1 既存 `github-codex-pr-review-comments/`

Provider-side の既存 skill は次に存在する。

- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`

この skill は、PR の Codex review feedback を fixed read-only REST GET wrapper で取得する。

主な出力は次の通り。

- `issue_comments.json`
- `review_comments.json`
- `reviews.json`
- `review_data.json`
- `codex_report.md`

取得対象は次の3種類である。

- PR conversation comments
- inline review comments
- review bodies

一方で、今回の `iss-00170` が必要とする full PR observation には、少なくとも次が含まれる。

- latest head SHA への束縛
- checks / statuses
- all review signals
- Codex-authored subset
- human / bot subset
- review requests
- review thread state
- quiet window / same fingerprint count
- progress delta
- final JSON authority

したがって、既存 skill は read-only 境界としては有用だったが、今回の統合観測設計とは責務が狭く、重複する。

### 2.2 現行 `pr-monitor` instructions

Provider-side の `pr-monitor` は次に存在する。

- `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
- `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`

現行 instruction は、`pr-monitor` 自身が deadline / sleep / polling loop を管理する前提を持つ。

また、Codex review / PR review comment data については、既存 wrapper を使うよう指示している。

```text
./.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh --repo <repo> --pr <pr> --out <tmp-dir>
```

今回の設計変更では、この agent-side polling と旧 wrapper 参照を、新しい deterministic PR observation command に置き換える必要がある。

## 3. Deep Consultant の結論

Deep Consultant の推奨は次である。

- 既存 `github-codex-pr-review-comments/` を削除する。
- 新しい単一 asset を `github-pr-observation/` として設ける。
- `stable` は skill 名から外す。
- 安定化判定は skill 名ではなく、`wait_pr_observation.sh` の挙動、JSON field、exit reason に閉じ込める。
- script 群は `pr-monitor` 専用の隠れ実装ではなく、独立 skill として `install_root` に置く。
- ただし通常 workflow の入口は `pr-monitor` に限定する。

推奨される役割分担は次の通り。

```text
github-pr-merge-preparer skill
  -> pr-monitor agent
      -> .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
          -> fetch_pr_observation_snapshot.sh
              -> lib/fetch_pr_checks_snapshot.sh
              -> lib/fetch_pr_review_snapshot.sh
```

## 4. 削除する既存 skill

削除対象:

```text
.agents/skills/github-codex-pr-review-comments/
```

Provider-side source:

```text
src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/
```

削除してよい理由:

- 新しい review collector が、旧 wrapper の実質機能を包含する。
- `pr-monitor` が参照する read-only PR observation surface は1つでよい。
- Codex-only review comment collection と full PR observation を並存させると、agent がどちらを参照すべきかが曖昧になる。
- `github-codex-pr-review-comments` という名前は、all review signals / Codex subset / checks / statuses / head SHA binding を扱う新設計と責務が合わない。
- 互換維持のために残すと、旧 path を使う運用が温存され、今回の deterministic observation contract の一本化を弱める。

削除してよい条件:

- 新 `fetch_pr_review_snapshot.sh` が旧 wrapper の実質機能を内包する。
  - PR conversation comments
  - inline review comments
  - review bodies
  - Codex-authored subset
  - body hash
  - thread state available / unknown
- 旧 `codex_report.md` 相当が必要な場合、新 artifact として unified output 配下に出す。
  - 例: `codex_review_report.md`
- `pr-monitor` instructions、provider / mirror asset inventory、tests から旧 path を完全に消す。
- `spec-dock update` 後の consumer repo に旧 managed asset が残らないことを検証する。
- direct `gh api` / arbitrary endpoint / write operation を許さない command boundary を、新 wait entrypoint / snapshot helper 側へ移す。
- init / update regression で、旧 skill 不在と新 skill 存在を両方確認する。

## 5. 新 skill 名

推奨名:

```text
github-pr-observation
```

推奨 public entrypoint:

```text
scripts/wait_pr_observation.sh
```

推奨 snapshot helper:

```text
scripts/fetch_pr_observation_snapshot.sh
```

推奨 internal collectors:

```text
scripts/lib/fetch_pr_checks_snapshot.sh
scripts/lib/fetch_pr_review_snapshot.sh
```

### 5.1 `stable` を名前に含めない理由

`stable` は実装・運用側には重要である。

しかし、利用側 agent が欲しいのは「PR が stable かどうかを判定する技術」ではなく、「PR の観測結果」である。

`github-pr-stable-observation` という名前は正確ではあるが、内部アルゴリズム名を外部 contract に露出する。

これに対して `github-pr-observation` は、wait / snapshot / checks / reviews / progress / final JSON を束ねる中立的な名前である。

### 5.2 他候補との比較

`github-pr-monitoring`:

- `pr-monitor` agent と名前が近く、agent と skill の責務境界が曖昧になりやすい。
- 「monitoring」は継続実行や agent role を連想し、script asset としてはやや広い。

`github-pr-readiness`:

- merge-ready 判定や workflow coordinator の責務まで担うように見える。
- `github-pr-merge-preparer` と責務が衝突しやすい。

`github-pr-observation`:

- checks/statuses/reviews/head SHA/progress artifact をまとめる名前として自然。
- read-only data collection / wait result に閉じやすい。
- `pr-monitor` agent の通常利用にも、将来の debug / human inspection にも耐える。

## 6. 独立 skill として公開するか、pr-monitor 内部に閉じるか

Deep Consultant の推奨は、独立 skill として公開する案である。

ただし、ここでの「公開」は通常入口を増やすという意味ではない。

通常 workflow は次に固定する。

```text
github-pr-merge-preparer
  -> pr-monitor
      -> github-pr-observation/scripts/wait_pr_observation.sh
```

`github-pr-observation` は、再利用可能な read-only utility asset として公開される。

### 6.1 独立 skill として置く利点

- `install_root` の source of truth に置ける。
- Codex / GitHub 両 host の `pr-monitor` instruction から同じ repo-relative script を参照できる。
- `pr-monitor` の host-specific developer instructions に shell script の契約を埋め込まずに済む。
- tests / parity / managed asset retirement を skill 単位で検証しやすい。
- `github-pr-merge-preparer` などの workflow skill が必要に応じて artifact contract を参照できる。
- fixed read-only wrapper boundary を script 側に閉じ込められる。

### 6.2 pr-monitor 内部に閉じる案の弱点

- Codex host と GitHub host の agent instruction に実行契約が分散する。
- script path / schema / progress / final JSON contract が agent prompt に埋まり、テスト対象として弱くなる。
- workflow skill から script contract を参照しにくくなる。
- 将来 `pr-monitor` instruction を変更したときに、実装 contract と説明が乖離しやすい。

### 6.3 採用する境界

採用すべき境界は次である。

- `github-pr-observation`:
  - read-only PR observation utility skill。
  - wait / snapshot / internal collectors / schema docs / usage docs を保持する。
  - write operation は持たない。
- `pr-monitor`:
  - 通常 workflow の唯一の agent entrypoint。
  - `wait_pr_observation.sh` を1回だけ実行する。
  - stdout final JSON / `result.json` を authoritative result として要約する。
  - progress は状況説明にのみ使う。
  - repair / merge / comment posting / thread resolve は行わない。
- `github-pr-merge-preparer`:
  - workflow coordinator。
  - monitor invocation、fix delegation、再 push、再 monitor、human gate を担う。
- `github-pr-creator`:
  - PR creation workflow helper。
  - 作成後に `pr-monitor` へ handoff する。

## 7. 要件・設計・ADR への反映事項

### 7.1 ADR

既存 ADR の次の判断は取り消す必要がある。

```text
既存 Codex review wrapper は互換境界として残す。
```

置き換える判断:

```text
旧 Codex-only skill `github-codex-pr-review-comments` は、新しい unified PR observation skill に統合して削除する。
```

ADR に追加すべき決定:

- skill 名は `github-pr-observation` とする。
- `stable` は asset 名に含めず、wait script の内部判定・JSON schema・exit reason で表現する。
- `wait_pr_stable_observation.sh` ではなく `wait_pr_observation.sh` とする。
- 旧 Codex-only wrapper の互換維持は行わない。
- stale managed asset が consumer repo に残らないことを実装の受け入れ条件に含める。

### 7.2 要件定義

要件定義では次を修正する。

- `github-codex-pr-review-comments` 維持方針を削除する。
- `github-pr-stable-observation` / `stable observation public wait entrypoint` という表現を、`github-pr-observation` / `PR observation wait entrypoint` に寄せる。
- Codex subset は unified review collector の一部として扱う。
- 旧 managed skill retirement を scope / acceptance criteria に追加する。
- `pr-monitor` が使う script path を `github-pr-observation/scripts/wait_pr_observation.sh` に固定する。
- `stable` は目的・内部判定としては残してよいが、skill 名や利用者向け entrypoint 名には出さない。

### 7.3 設計

設計では次を修正する。

- 新 skill directory:

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/
```

- Public wait entrypoint:

```text
scripts/wait_pr_observation.sh
```

- Snapshot helper:

```text
scripts/fetch_pr_observation_snapshot.sh
```

- Internal collectors:

```text
scripts/lib/fetch_pr_checks_snapshot.sh
scripts/lib/fetch_pr_review_snapshot.sh
```

- Schema prefix:

```text
github-pr-observation.wait.v1
github-pr-observation.snapshot.v1
```

- 旧 skill deletion:

```text
src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/
```

- Provider / dogfooding mirror の parity に、旧 skill 不在と新 skill 存在の両方を含める。
- update path に stale managed asset cleanup の検証を含める。

### 7.4 実装計画

実装計画は ADR / requirement / design の改訂後に再生成する。

計画には少なくとも次を含める。

- 旧 skill 削除。
- 新 skill 追加。
- command rule / exec policy 更新。
- `pr-monitor` instructions の旧 wrapper path 削除と新 wait command への置換。
- Codex subset tests を新 review collector tests に移行。
- init / update / dogfooding parity tests。
- `spec-dock update` 後、旧 managed skill が残らないことの検証。

## 8. 推奨判断

本リサーチとしての推奨判断は次である。

```text
`github-codex-pr-review-comments/` は削除する。
新設 skill は `github-pr-observation/` とする。
`stable` は skill 名・entrypoint 名から外し、内部判定・JSON schema・exit reason に閉じる。
script 群は `pr-monitor` 内部に埋め込まず、独立 read-only utility skill として install_root に置く。
通常 workflow の入口は `pr-monitor` に固定する。
```

これにより、古い Codex-only 経路と新しい full PR observation 経路の二重化を避けられる。

また、`pr-monitor` agent は「見る役」に集中し、`github-pr-observation` は「機械的に観測する道具」、`github-pr-merge-preparer` は「PR を merge 可能状態へ運ぶ coordinator」という分担を維持できる。
