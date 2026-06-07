---
種別: ADR（Architecture Decision Record）
ID: "20260607t085456z-adr"
タイトル: "Script Driven Pr Observation Boundary"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
親: ["iss-00170"]
authority: "accepted"
derived_from:
  - "spec-dock/active/issue/discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md"
  - "spec-dock/active/issue/discussions/20260607t083017z-research-v2-progress-delta-for-script-driven-polling.md"
  - "spec-dock/active/issue/discussions/20260607t110532z-research-pr-observation-skill-retirement-and-naming.md"
  - "spec-dock/active/issue/discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md"
  - "spec-dock/active/issue/discussions/20260607t132357z-interview-summary-artifact-contract.md"
  - "user decision 2026-06-07/08: pr-monitorを完全廃止し、stdout final JSONとstderr progressを正規I/Oにする"
reflected_to:
  - "iss-00170 requirement.md"
  - "iss-00170 design.md"
---

# 20260607t085456z-adr Script Driven Pr Observation Boundary

## 位置づけ

この ADR は、PR observation における polling loop、progress reporting、旧 `pr-monitor` sub-agent、旧 Codex-only review skill、PR workflow skills の責務境界を固定する。

`iss-00170` の要件定義書、設計書、実装計画書は、この ADR を source decision として反映する。

## 結論（Decision）

Accepted.

PR monitoring は `pr-monitor` sub-agent ではなく、deterministic read-only `github-pr-observation` skill / scripts を正規入口として実装する。

互換性維持のための deprecated shim は残さない。
この issue の完了時点で、`pr-monitor` sub-agent は provider-side asset と dogfooding mirror の両方から削除される。

また、旧 `github-codex-pr-review-comments` skill は残さず、新しい `github-pr-observation` の review collector に統合する。

### 正規 I/O 契約

- `wait_pr_observation.sh`:
  - deterministic bounded polling loop を持つ public wait entrypoint。
  - stdout には final JSON text を1回だけ出す。
  - stderr には default `--progress stderr-summary` として bounded progress を出す。
  - progress は non-authoritative であり、success / failure / timeout / merge-ready の最終判定には使わない。
  - `--progress none` は progress 抑止用 opt-out とする。ただし fatal diagnostics まで黙らせる契約ではない。
  - `--out <dir>` は optional debug/audit mode であり、通常 path の必須ではない。
  - `--out` 指定時だけ `result.json`、`events.ndjson`、`latest.json`、`latest_delta.json`、`snapshots/`、必要に応じて `raw/` を書く。
  - `result.json` は stdout final JSON の同一内容の写しであり、別 authority ではない。
  - `summary.md` は生成しない。human-facing summary は final JSON fields として返す。
- `fetch_pr_observation_snapshot.sh`:
  - 1回分の normalized PR snapshot / fingerprint を stdout JSON text として返す。
  - wait loop は持たない。
  - `--out` 指定時だけ debug/audit artifacts を書く。
- `github-pr-observation` skill:
  - read-only PR observation capability として新設する。
  - wait / snapshot scripts、schema、progress contract、prerequisites、no-write rules を保持する。
- `github-pr-merge-preparer` skill:
  - PR 作成/発見、`wait_pr_observation.sh` invocation、bounded repair delegation、push 確認、再 observation、merge-prepared / human gate 報告を担う。
  - `pr-monitor` へ handoff しない。
- `github-pr-creator` skill:
  - PR 作成 workflow skill として維持する。
  - 単なる PR 作成が目的なら PR URL / number / head SHA を返す。
  - 軽い確認が必要な場合は `fetch_pr_observation_snapshot.sh` を使う。
  - merge-prepared まで求める場合は `github-pr-merge-preparer` または `wait_pr_observation.sh` contract へ進む。
  - `pr-monitor` へ handoff しない。
- main orchestrator:
  - 明示的に待つ必要がある場合だけ `wait_pr_observation.sh` を使う。
  - 単なる現状確認では `fetch_pr_observation_snapshot.sh` を使う。
  - モデル自身が polling loop / sleep / timeout / quiet window / same fingerprint count を判断しない。

### stderr progress 契約

progress は、event-diff log ではなく adaptive current-state summary とする。

- 常に stdout と分離し、stderr のみに出す。
- 1 poll 最大1行。
- no-change poll でも liveness を示すため1行出す。
- 進行中の領域だけ counters を出し、完了済み領域は compact status に畳む。
- 個別 check 名、job 名、reviewer 名、comment body、URL、event diff は default progress に出さない。
- default progress line は ASCII key/value の single line とする。
- hard max は 200-240 chars 程度を目標にし、超過時は optional fields を落として `limit=truncated` を出す。

推奨 line:

```text
pr_obs poll=4 elapsed=06m00s remain=24m00s phase=waiting_checks ci=running checks=7/9 ok=6 fail=0 pend=2 other=1 review=requested quiet=00m30s limit=none
```

CI 完了後:

```text
pr_obs poll=9 elapsed=13m30s remain=16m30s phase=observing ci=passed review=none quiet=04m00s limit=none
```

review 指摘あり:

```text
pr_obs poll=10 elapsed=14m00s remain=16m00s phase=attention ci=passed review=changes_requested quiet=00m20s limit=none
```

### progress status taxonomy

CI status は GitHub から機械的に取れる checks / commit statuses の観測結果だけで表す。

- `ci=unknown`:
  - API取得失敗、権限不足、schema不明、head不一致などで判定不能。
- `ci=none`:
  - current head に checks/statuses が観測されない。
- `ci=running`:
  - failed がなく、in_progress が1件以上ある。
- `ci=pending`:
  - failed / running がなく、queued / requested / waiting / pending など、まだ開始前または待機中の状態がある。
- `ci=failed`:
  - failure / error / cancelled / timed_out / action_required / startup_failure / stale など否定的 terminal state が1件以上ある。
- `ci=passed`:
  - 失敗・pending・running がなく、観測対象が merge-blocking ではない終端状態。
  - `success` だけでなく、GitHub上で終端済みとして扱われる `skipped` / `neutral` もここに含める。
  - workflow 自体が path filtering 等で skip され、required check が Pending のまま残る場合は `passed` ではなく `pending` とする。

`mixed` と `inconclusive` は default progress status として採用しない。
1件でも失敗系があれば `ci=failed`、実行中があれば `ci=running`、開始前または待機中だけなら `ci=pending` とする方が agent / human に分かりやすい。

Review status は GitHub から機械的に取れる reviewDecision、review states、review requests、review threads、comments の存在だけで表す。
P1/P2 などの本文上の優先度は text interpretation なので progress status には含めない。

- `review=unknown`:
  - reviewDecision / reviews / comments / threads の取得が不完全。
- `review=none`:
  - review、review comment、issue comment、review request が観測されない。
- `review=requested`:
  - review request が残っている、または `reviewDecision=REVIEW_REQUIRED`。
- `review=commented`:
  - COMMENTED review や comment があるが、changes requested / unresolved とは断定しない。
- `review=approved`:
  - `reviewDecision=APPROVED` または有効 review state に APPROVED がある。
- `review=changes_requested`:
  - `reviewDecision=CHANGES_REQUESTED` または有効 review state に CHANGES_REQUESTED がある。
- `review=unresolved`:
  - review thread に unresolved かつ non-outdated の thread があると取得できた場合。

`review=blocked` は採用しない。
何が block かは branch protection、required review、draft、merge conflict、thread resolution などの合成であり、review単体の GitHub field から安全に言い切れないため。

## 棄却する方針

- `pr-monitor` sub-agent を read-only summarizer / classifier として残す。
- `pr-monitor` 名の deprecated shim を残す。
- 旧 `github-codex-pr-review-comments` skill を互換 wrapper として残す。
- `wait_pr_stable_observation.sh` / `github-pr-stable-observation` のように `stable` を public asset 名へ露出する。
- agent / model が複数 poll / sleep / quiet window / timeout を推論で判断する。
- observation scripts に GitHub write operation を持たせる。
- progress から final decision を確定する。
- progress に text interpretation 由来の P1/P2 などを status として出す。
- `summary.md` を生成する。
- default path で永続 artifacts を必須にする。

## 背景（Context）

`iss-00170` の初期設計では、`pr-monitor` sub-agent が PR 作成後または push 後の checks / statuses / Codex review を監視していた。
その instruction には deadline、sleep policy、polling loop、completion rules が含まれており、推論モデルが loop の継続判断を持っていた。

その後の分析で、polling loop、sleep、timeout、quiet window、same fingerprint count、progress、final JSON を deterministic script に移す方針が採用された。
この時点で、`pr-monitor` が担う実質価値は「script を起動して final JSON を要約する」だけになった。
これは独立 sub-agent として責務が薄く、skill/script と sub-agent guidance の二重メンテ、final JSON authority の情報落ち、prompt behavior の再混入につながる。

また、旧 `github-codex-pr-review-comments` は Codex-only review comments 取得に特化した wrapper であり、PR 全体の observation、all/Codex signal separation、head SHA binding、thread state、review requests、progress を扱う新設計と責務が重複・衝突する。

長時間 wait は10〜30分に及ぶ可能性がある。
silent wait は agent / human が停止と誤認しやすいため、stdout final JSON の契約を壊さない stderr progress を default とする。

## 判断理由（Rationale）

PR observation の安定判定は、推論モデルの逐次判断ではなく、入力・時間・snapshot から機械的に再現できる必要がある。
そのため loop / timeout / quiet window / same fingerprint count は script へ移す。

script が stdout final JSON を authority として返せるなら、`pr-monitor` sub-agent は独立した責務を持たない。
human-facing summary は final JSON の `summary` / `recommended_next_action` / `limitations` / `artifacts` fields と、caller 側の短い要約で代替できる。

progress は、長時間 wait の liveness と current state を示すために必要である。
ただし、progress を event log にすると1行制約を壊しやすく、途中行を取りこぼすと状態復元も難しい。
そのため default progress は、各行が自己完結する current-state summary とする。

CI/CD は GitHub checks/statuses から機械的に集約できる。
`skipped` / `neutral` は、文脈によって正常な「実行不要」または非必須 terminal state になりうる。
そのため、default progress では失敗・未完了がない終端状態を `ci=passed` として畳む。
逆に required workflow が path filtering 等で skip され Pending のまま残る場合は、GitHub上も pending なので `ci=pending` とする。

Review は CI と違い binary pass/fail ではない。
GitHub から機械的に取れる reviewDecision、review state、review request、review thread state、comment presence に限定して status を作る。
P1/P2 など本文の意味解釈や「blocker」判定は progress には入れず、final JSON の actionable summary や caller / human gate 側で扱う。

read-only 境界は sub-agent role ではなく、fixed read-only scripts、caller-provided arbitrary endpoint 禁止、write command 不在、tests、command rules によって守る。

## 影響（Consequences）

Positive:

- PR observation の正規入口が `github-pr-observation` に一本化される。
- model / agent の polling 判断が observation 判定から消える。
- stdout final JSON text が唯一の primary result になる。
- stderr progress により long-running wait の liveness が見える。
- progress line が GitHub から機械的に取得できる current state に限定される。
- `pr-monitor` prompt と script contract の二重メンテを避けられる。
- old Codex-only wrapper と new full PR observation の重複を避けられる。
- init / update の managed asset cleanup まで含めて shipped layout を整理できる。

Negative / debt:

- `github-pr-merge-preparer` / `github-pr-creator` / role guidance / tests の更新範囲が広がる。
- caller は stdout final JSON を読む規約を持つ必要がある。
- stderr progress を stdout と混ぜて JSON parse しないよう、caller guidance と tests が必要になる。
- host が stderr を live 表示しない場合、progress の UX 効果は弱くなる。
- shell / `gh` / auth / long-running command が使えない host では observation unavailable を明示する必要がある。
- final JSON summary fields の品質を script contract 側で設計する必要がある。

Impact scope:

- Add:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`
- Remove:
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/`
  - dogfooding mirror equivalents under `.codex/`, `.github/`, `.agents/`
- Update:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
  - host / role guidance that mentions `pr-monitor`
  - installer / update cleanup behavior if stale managed assets are otherwise left behind
  - asset inventory / parity tests

Migration / rollback:

- No deprecated `pr-monitor` shim.
- No compatibility `github-codex-pr-review-comments` skill.
- Consumer update must remove stale managed assets or test-visible stale assets must fail the implementation gate.
- Rollback means restoring deleted assets and reverting workflow docs/tests; no write-side GitHub behavior is introduced by this ADR.

Follow-ups:

- 必要なら、`github-pr-merge-preparer` owned の explicit opt-in / idempotent review request commenter を別 issue で設計する。
- 必要なら、future issue で cross-repo policy judgement / human triage agent を新しい役割として設計する。
- 必要なら、debug-only checks/review snapshot helpers を internal から public に昇格するかを別 issue で検討する。

## 参考（References）

- 関連仕様:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/report.md`
- 元になった discussion docs:
  - `spec-dock/active/issue/discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md`
  - `spec-dock/active/issue/discussions/20260607t083017z-research-v2-progress-delta-for-script-driven-polling.md`
  - `spec-dock/active/issue/discussions/20260607t110532z-research-pr-observation-skill-retirement-and-naming.md`
  - `spec-dock/active/issue/discussions/20260607t124933z-research-pr-monitor-retirement-analysis.md`
  - `spec-dock/active/issue/discussions/20260607t132357z-interview-summary-artifact-contract.md`
- ユーザー決定:
  - 2026-06-07: `pr-monitor` を完全廃止し、互換 shim を残さず `github-pr-observation` skill / scripts へ置き換える。
  - 2026-06-08: stdout final JSON text を primary result とし、stderr progress は current-state summary として default 表示する。
