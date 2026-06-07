---
created_by_role: main-orchestrator
scope_id: iss-00170
artifact_type: research
source_paths:
  - src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml
  - src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
  - .agents/skills/github-pr-creator/SKILL.md
  - spec-dock/active/issue/discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md
  - spec-dock/active/issue/discussions/20260607t083017z-research-v2-progress-delta-for-script-driven-polling.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# リサーチ: PR monitor agent と PR workflow skill の責務境界

この文書は、`iss-00170` の設計を見直すにあたり、`pr-monitor` agent、`github-pr-merge-preparer` skill、`github-pr-creator` skill の役割分担を分析した research artifact である。
ユーザーは別作業で、system-architect / implementation-planner のように agent と skill が同じ authoring 責務を二重に持つ構造を agent 側へ統一する方向を検討している。
本リサーチでは、その方針を PR workflow 周辺にも適用すべきかを検討する。

## 1. 結論

この issue では、PR 周辺の workflow を agent に統一しない方がよい。

推奨:

- `pr-monitor` は read-only な bounded executor / monitor agent として残す。
- `github-pr-merge-preparer` は workflow coordinator skill として維持する。
- `github-pr-creator` も PR 作成 workflow skill として維持する。
- `pr-monitor` の polling loop は script 側へ移す。
- `pr-monitor` は `wait_pr_stable_observation.sh` を1回実行し、final JSON を要約・分類・handoff する。
- 初回 review request comment posting は `pr-monitor` / wait script に入れない。
- 必要なら、`github-pr-merge-preparer` 側から明示 opt-in の separate write-capable requester script / role を呼ぶ設計を、別 issue または future scope で扱う。

system-architect / implementation-planner の統一方針は、同じ成果物を同じ責務で作る authoring role の二重化を解消する話である。
一方、PR workflow は複数の権限境界、GitHub write、local git 状態、CI/review の非同期監視、人間ゲートを束ねる coordinator workflow であり、同列に扱うべきではない。

## 2. 現在の役割

| 役割 | 現在の責務 | 性質 |
|---|---|---|
| `pr-monitor` agent | checks / statuses / review outcomes を read-only に監視し、結果を main orchestrator へ返す | bounded executor / monitor |
| `github-pr-merge-preparer` skill | PR 作成/発見、monitor invocation、bounded fix delegation、push 確認、再 monitor、merge-prepared / human gate 判定を調整する | workflow coordinator |
| `github-pr-creator` skill | branch push、base branch selection、PR title/body、issue linkage、PR create、PR URL 返却を行う | write-capable workflow helper |

現状の `pr-monitor` agent は polling loop、sleep、deadline、再確認を agent 自身が管理する設計になっている。
`iss-00170` の新しい設計方針では、この loop は `wait_pr_stable_observation.sh` に移し、`pr-monitor` は final JSON の要約・分類に寄せる。

## 3. 推奨する責務分担

| 役割 | 推奨責務 | この issue での扱い |
|---|---|---|
| `pr-monitor` agent | `wait_pr_stable_observation.sh` を1回実行し、final JSON を読んで checks/statuses/reviews/mergeability を要約・分類・handoff する read-only monitor | 変更推奨 |
| `wait_pr_stable_observation.sh` | deadline、sleep、polling、stable observation 判定、progress delta、final JSON 出力を持つ機械的 loop | 変更推奨 |
| `github-pr-merge-preparer` skill | PR 作成/発見後の全体 workflow coordination、人間ゲート、bounded fix delegation、再 push 確認、再 monitor、merge-prepared 判定 | 変更不要 |
| `github-pr-creator` skill | branch push、PR 作成、base selection、title/body、issue linkage、PR URL 返却、monitor への handoff 指示 | 変更不要 |
| review request comment requester | 必要な場合だけ、明示 opt-in された write-capable separate script / role として実行。idempotency 必須 | future または別 issue |

## 4. 変更不要と判断するもの

今回の issue では次を変更しない。

- `github-pr-merge-preparer` を agent 化しない。
- `github-pr-creator` を agent 化しない。
- `pr-monitor` に write 権限を持たせない。
- `pr-monitor` に review request comment posting を持たせない。
- `pr-monitor` に fix delegation、push 判断、merge-prepared predicate 全体の coordinator 責務を持たせない。
- PR merge、auto-merge、branch delete、issue close、review reply、thread resolve、review dismiss は引き続き forbidden のままにする。

理由:

- PR workflow は write 操作と read-only 監視が混在する。
- local git state、branch push、PR creation、CI/review 監視、人間 gate は、それぞれ失敗時の対応が異なる。
- これを一つの agent に急に閉じ込めると、権限境界と stop condition が曖昧になる。
- `github-pr-merge-preparer` skill は、複数 agent / command / human gate を束ねる workflow contract としてまだ価値がある。

## 5. 変更推奨と判断するもの

今回の issue で変更するべきもの:

- `pr-monitor` の polling loop 責務を script に移す。
- `pr-monitor` agent prompt を、loop 手順から次の責務へ寄せる。
  - wait wrapper を1回呼ぶ。
  - progress は状況説明として扱う。
  - final JSON を parse する。
  - `normalized_status`、`observation_complete`、artifact paths、limitations を要約する。
  - main orchestrator / `github-pr-merge-preparer` へ handoff する。
- `pr-monitor` から direct GitHub API fallback、write operation、comment posting を明確に排除する。
- review request comment posting は `pr-monitor` / wait script から分離する。

## 6. 将来の構造改革候補

将来的に PR workflow を agent へ寄せるなら、別 issue として扱うべきである。

候補:

```text
pr-merge-preparer agent
  - PR discovery
  - monitor invocation
  - failure classification
  - bounded fix delegation
  - re-push confirmation
  - re-monitor
  - human gate report
```

この場合、`github-pr-merge-preparer` skill は次のような薄い routing / instruction layer へ縮退できる。

- いつ `pr-merge-preparer` agent を使うか。
- 禁止事項。
- merge-prepared predicate。
- human gate output。
- reviewer / repair worker の使い分け。

ただしこれは multi-agent orchestration と write-adjacent workflow を agent 内に閉じる設計変更であり、`iss-00170` の stable observation hardening からは外すべきである。

`pr-creator` agent 化も将来候補にはなる。
ただし PR 作成は write 操作であり、branch push、base branch、PR body、issue linkage の判断が main orchestrator の現在文脈に強く依存する。
そのため、現時点では skill として手順・安全制約・戻り値 contract を持つ価値が高い。

## 7. 初回 review request comment posting の責務

初回 Codex review request comment posting は、`pr-monitor` には置かない。

却下する配置:

- `pr-monitor`:
  - read-only invariant を壊すため不適。
- `wait_pr_stable_observation.sh`:
  - observation loop に write intent が混ざるため不適。
- `github-pr-creator`:
  - PR 作成と review request comment が結合しすぎる。
  - 既存 PR / repush 後 / re-monitor の場合に扱いづらい。

推奨配置:

- `github-pr-merge-preparer` 側から、必要な場合だけ separate write-capable requester script / role を明示 opt-in で呼ぶ。

推奨 safety boundary:

- default dry-run。
- 実投稿には `--execute` が必須。
- idempotency key が必須。
- same `repo/pr/head_sha/request-key` では二重投稿しない。
- output は `posted` / `already_exists` / `skipped` / `failed` を返す。
- 失敗時は human gate。
- `pr-monitor` は fallback 投稿しない。

## 8. system-architect / implementation-planner 統一方針との違い

system-architect / implementation-planner は authoring role である。
これらは次の理由で agent 化しやすい。

- 生成する成果物が scope-local discussion draft や design/plan draft として明確。
- write scope が docs に限定される。
- 権限境界が比較的単純。
- skill と agent が同じ成果物 authoring を二重に担っている場合、統合の利益が大きい。

PR workflow は性質が違う。

- PR 作成は write operation。
- PR monitoring は read-only operation。
- repair は dev-coder への bounded delegation。
- push は git/GitHub write。
- merge-prepared は human decision 前の evidence reporting。
- merge は forbidden / human action。

このように複数の権限・責務・停止条件をまたぐため、workflow skill と bounded agents の組み合わせとして扱う方が安全である。

## 9. `iss-00170` への反映方針

`iss-00170` の requirement / design / plan には、次を反映する。

- この issue の scope は `pr-monitor` の stable observation hardening に限定する。
- `github-pr-merge-preparer` / `github-pr-creator` の agent 統合は行わない。
- `github-pr-merge-preparer` は `pr-monitor` を呼び、latest head SHA に対する final JSON を消費する workflow coordinator として維持する。
- `github-pr-creator` は PR 作成 workflow skill として維持し、PR 作成後の monitoring handoff を明示する。
- `pr-monitor` は read-only summarizer / classifier として残し、polling loop は wait wrapper script に移す。
- review request comment posting は monitor から分離し、必要なら別 issue / future scope の explicit opt-in write requester として扱う。

## 10. 最終判断

今回の issue では、PR workflow 全体を agent へ統一しない。
統一対象は `pr-monitor` の中に残っていた不安定な polling responsibility であり、これは agent ではなく deterministic script に移す。

`github-pr-merge-preparer` と `github-pr-creator` は、当面 workflow skill として維持する。
これは二重化の放置ではなく、coordinator skill と bounded executor agent の責務分担である。
