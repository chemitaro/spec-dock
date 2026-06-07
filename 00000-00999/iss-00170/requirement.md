---
種別: 要件定義書（Issue）
ID: "iss-00170"
タイトル: "Harden Pr Monitor Stable Observation"
関連GitHub: ["#170"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-07"
親: ["epic-00067", "init-local-00003"]
---

# iss-00170 Harden Pr Monitor Stable Observation — 要件定義（何を、なぜ行うか）

## 目的
- `pr-monitor` が PR 作成後または push 後の checks / statuses / reviews を、最新 head SHA に束縛した安定観測として扱えるようにする。
- 「情報が出揃った」という自然言語の完了判定を、bounded timeout、stable snapshot、review-thread limitation disclosure を持つ観測可能な契約へ置き換える。
- `github-pr-merge-preparer` が要求する merge-prepared evidence に対して、古い SHA の green / review なし、遅延 review comment、unresolved thread state 不明を success と誤判定しない read-only monitoring 基盤を作る。

## 背景・現状
- 現状の挙動:
  - `pr-monitor` は read-only agent として、PR に紐づく checks / statuses と Codex review を監視し、`success` / `failed` / `review_changes_requested` / `timeout` を返す。
  - `pr-monitor` は GitHub Actions のみではなく PR-linked checks / statuses を対象にし、Codex review は PR conversation comments、inline review comments、review bodies を fixed REST wrapper で取得する。
  - `github-pr-merge-preparer` は `pr-monitor` に `repo`、`pr`、`head_sha`、`reason` を渡し、monitor output が latest head SHA でなければ stale と扱う。
  - 既存 `github-codex-pr-review-comments` wrapper は fixed REST GET endpoints で comments / reviews を取得し、raw arrays と Codex-authored subset を出力する。
- 現状の課題:
  - `pr-monitor` の「checks / statuses と review の両方が出揃った」状態が、fingerprint、quiet window、連続 poll 回数として定義されていない。
  - expected head SHA と current head SHA の照合、監視中の head SHA 変更時の snapshot reset、final output の SHA binding が完了条件として弱い。
  - checks が terminal になった直後に 1〜2 回だけ review grace wait して終了すると、遅れて付く review comment / review body / review thread を見逃す余地がある。
  - `gh pr checks` の表示だけでは check runs、commit statuses、statusCheckRollup、review/comment/thread の同期状態を十分に表せない。
  - 現行 wrapper は Codex subset を中心にした report を生成するが、all issue comments、all inline review comments、all reviews、reviewDecision、reviewRequests、reviewThreads、human/bot/Codex subset を分けた観測契約にはなっていない。
  - unresolved / resolved / outdated review thread state を取得できない場合、merge-prepared 判定で必要な limitation disclosure と human gate が `pr-monitor` output から安定して得られない。
- 観測点:
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - `iss-00105` の PR merge-ready monitoring requirement / design / review-thread state discussion。
- 情報源:
  - `discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md`
  - `iss-00105-pr-creation-and-merge-ready-monitoring-skill/discussions/20260521t000352z-01-interview-review-thread-state-policy.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - PR 作成後または push 後に、CI / checks / statuses / review feedback が本当に揃ったかを確認してから次の判断へ進みたい maintainer。
  - `github-pr-merge-preparer` や issue execution workflow から `pr-monitor` を呼ぶ main orchestrator。
- 代表シナリオ:
  - PR 作成直後、orchestrator が `pr-monitor` に PR number と expected head SHA を渡す。
  - `pr-monitor` は current head SHA を確認し、expected head SHA と一致する観測だけを最終結果の対象にする。
  - checks/statuses と reviews/comments/threads を一定間隔で取得し、正規化 fingerprint が quiet window と連続 poll 条件を満たすまで bounded に待つ。
  - head SHA が変わった場合は古い snapshot を stale として破棄し、latest head SHA に対する観測へ切り替えるか、呼び出し元へ stale / blocked として返す。
  - unresolved actionable review thread、`CHANGES_REQUESTED`、failed check/status、thread state unknown などを区別して返し、修正・再 push・human gate は `github-pr-merge-preparer` 側が判断する。

## スコープ
- 必須:
  - `pr-monitor` の provider-side Codex / GitHub agent instructions を、head-SHA-bound stable observation contract に更新する。
  - dogfooding mirror の `.codex/agents/pr-monitor.toml` と `.github/agents/pr-monitor.agent.md` を provider-side asset と同等に更新する。
  - checks / statuses と review/comment/thread signals を正規化して返す fixed read-only wrapper または既存 wrapper 拡張を追加する。
  - wrapper は arbitrary endpoint / method / GraphQL query / write operation を caller から受け取らず、入力を `--repo` / `--pr` / `--out` などの限定された read-only parameters に固定する。
  - all review signals と Codex-authored subset を分けて出力する。
  - review thread state が取得できる場合は unresolved / resolved / outdated を区別し、取得できない場合は limitation として machine-readable に出力する。
  - `pr-monitor` output は既存 `overall_status` との互換性を維持しつつ、`normalized_status` または同等の詳細分類を追加する。
  - installer / dogfooding parity / wrapper output schema / agent instruction contract に対する regression coverage を追加または更新する。
- 禁止:
  - `pr-monitor` に PR merge、auto-merge、branch delete、issue close、review reply、review thread resolve、review dismiss、label/status mutation、push、commit、修正実装を持たせない。
  - arbitrary `gh api`、arbitrary GraphQL、direct GitHub API `curl`、POST / PATCH / PUT / DELETE 系操作へ fallback しない。
  - 古い head SHA の checks green / review なしを latest head SHA の success として返さない。
  - thread state unknown、wrapper failure、auth failure、rate limit、schema mismatch を success として隠さない。
  - prompt-only の曖昧な指示強化だけで deterministic observation contract を満たしたことにしない。
- 対象外:
  - `github-pr-merge-preparer` の fix-loop 責務、repair delegation、push、merge-prepared 判定全体の再設計。
  - GitHub issue lifecycle close、`spec-dock issue finish`、PR merge 実行。
  - GitHub plugin skills の再実装。
  - repository-specific required checks policy の全面設定機構。
  - PR comment への返信や review thread resolve の自動化。

## 境界
- 常に行う:
  - PR current head SHA を取得し、expected head SHA が与えられている場合は照合する。
  - final result は最新または明示対象の head SHA に対する観測であることを明示する。
  - 監視中に head SHA が変わった場合は、checks/statuses/reviews/comments/threads の snapshot をリセットするか、stale result として返す。
  - checks/statuses と reviews/comments/threads は、取得成功、terminal/complete、normalized fingerprint stability を分けて扱う。
  - stable 判定は、同一 fingerprint の連続観測と minimum quiet window を組み合わせる。
  - `reviewDecision=CHANGES_REQUESTED`、unresolved actionable thread、actionable review feedback は success ではなく review blocker とする。
  - review thread state が取得できない状態で actionable か不明な review comment が存在する場合は `review_state_unknown` / human gate 相当で返す。
  - wrapper output と `pr-monitor` output は、caller が latest head SHA、check failure、review blocker、unknown limitation、timeout を区別できる形にする。
- 判断が必要:
  - expected check names が caller から与えられた場合の deadline / grace handling。
  - requested reviewer が残っている場合に、bot review / human review request をどこまで待つか。
  - neutral / skipped / cancelled / action_required / stale などの check conclusion を blocking とするか unknown とするか。
  - review body / comment body を fingerprint に含める場合、body hash と raw body のどちらを output に残すか。
  - fixed read-only GraphQL wrapper の exact query、pagination、schema drift handling。
- 行わない:
  - write operation を行わない。
  - 修正・push・再監視 loop の owner にならない。
  - all reviewers の feedback を Codex-only feedback と混同しない。
  - review thread state が不明な状態を「レビューなし」と表現しない。

## 非交渉制約
- `pr-monitor` は read-only monitor のままである。
- latest head SHA に束縛されていない observation は merge-prepared evidence に使えない。
- 「完全に待つ」は無限待機ではなく、deadline 付きの stable snapshot observation として定義する。
- Thread state 不明、wrapper failure、stale head、zero-check grace 未満は success ではない。
- Provider-side source of truth は `src/spec_dock/assets/install_root/` であり、dogfooding mirror は検証対象として parity を保つ。

## 前提
- `github-pr-merge-preparer` は PR delivery loop の coordinator として維持する。
- `pr-monitor` は read-only observation と summarization を担当し、修正・push・merge 判断は caller 側へ返す。
- `github-codex-pr-review-comments` の fixed REST wrapper は既存安全境界として尊重する。必要な場合は後方互換を保って拡張するか、同じ安全境界の fixed read-only wrapper を追加する。
- `iss-00105` では review thread state 取得が follow-up candidate だった。本 issue は、その follow-up を stable observation hardening として具体化する。

## 受け入れ条件
- AC-001:
  - アクター:
    - `github-pr-merge-preparer` から呼ばれる `pr-monitor`。
  - 前提:
    - expected head SHA が指定されている。
  - 操作:
    - `pr-monitor` が PR current head SHA を取得する。
  - 期待結果:
    - current head SHA が expected head SHA と一致する場合だけ、その SHA に対する observation を final result として扱う。
    - 一致しない場合は stale / blocked / human gate 相当の詳細 status を返し、古い SHA の green を success としない。
  - 観測点:
    - agent instructions、wrapper output、tests。
- AC-002:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - 監視中に PR head SHA が変わる。
  - 操作:
    - 次回 poll で head SHA 変更を検出する。
  - 期待結果:
    - 変更前の checks/statuses/reviews/comments/threads snapshot を破棄または stale として分離する。
    - final output は、どの head SHA に対する結果かを明示する。
  - 観測点:
    - normalized snapshot state、output schema、tests。
- AC-003:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - latest head SHA に紐づく checks/statuses が存在する。
  - 操作:
    - checks/statuses を複数 poll で取得する。
  - 期待結果:
    - 全 check/status が terminal であり、失敗・pending・unknown が残らず、正規化 fingerprint が minimum quiet window と連続 poll 条件を満たすまで success としない。
    - failed / error / cancelled / timed_out / action_required / stale などは success ではない詳細分類になる。
  - 観測点:
    - wrapper output、completion rules、tests。
- AC-004:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - check/status が 0 件に見える PR。
  - 操作:
    - monitoring 開始直後に checks/statuses を取得する。
  - 期待結果:
    - 即 success とせず、initial grace window 中は pending / unknown として扱う。
    - deadline まで出現しない場合は、0 件であることと limitation を明示して返す。
  - 観測点:
    - completion rules、tests。
- AC-005:
  - アクター:
    - fixed read-only wrapper。
  - 前提:
    - PR に issue comments、inline review comments、review bodies、reviewDecision、reviewRequests、reviewThreads がある。
  - 操作:
    - wrapper が PR review-related signals を取得する。
  - 期待結果:
    - all signals と Codex-authored subset が分離される。
    - review thread state が利用可能な場合は unresolved / resolved / outdated が machine-readable に出力される。
    - pagination / fetched_at / thread_state_available など collection metadata が出力される。
  - 観測点:
    - wrapper output schema、tests。
- AC-006:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - review/comment/thread signals が複数 poll で取得できる。
  - 操作:
    - review snapshot を正規化して fingerprint 化する。
  - 期待結果:
    - same fingerprint が連続して観測され、minimum quiet window が経過するまで review monitoring complete としない。
    - checks green 直後に遅れて付く review comment を見逃しにくい。
  - 観測点:
    - completion rules、fingerprint field definition、tests。
- AC-007:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - `reviewDecision=CHANGES_REQUESTED` または unresolved actionable review thread が存在する。
  - 操作:
    - review signals を分類する。
  - 期待結果:
    - `overall_status` は後方互換を保ちながら review blocker を表し、詳細分類は `review_changes_requested` 相当になる。
    - actionable summary と source signal が caller に返る。
  - 観測点:
    - output schema、tests。
- AC-008:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - review thread state を取得できず、actionable か不明な review comment が存在する。
  - 操作:
    - wrapper limitation を受け取る。
  - 期待結果:
    - success ではなく `review_state_unknown` / human gate 相当の詳細分類を返す。
    - limitation、取得できた comments/reviews、推奨 next action が明示される。
  - 観測点:
    - output schema、tests。
- AC-009:
  - アクター:
    - `pr-monitor`。
  - 前提:
    - review thread state を取得できない。
    - visible comments / reviews だけでは unresolved thread が存在しないことを確認できない。
  - 操作:
    - wrapper limitation を受け取る。
  - 期待結果:
    - visible comments / reviews が 0 件でも、thread state absence を隠して unconditional success としない。
    - thread state が unavailable であること、success に必要な waiver / human gate 条件、推奨 next action を machine-readable に返す。
  - 観測点:
    - output schema、tests。
- AC-010:
  - アクター:
    - installer / dogfooding verifier。
  - 前提:
    - provider-side agent assets または wrapper scripts が更新される。
  - 操作:
    - scaffold / install_root parity を確認する。
  - 期待結果:
    - provider-side source と dogfooding mirror の `pr-monitor` / wrapper files が意図した同等性を保つ。
    - init/update regression が managed asset inventory の drift を検出できる。
  - 観測点:
    - tests、diff inspection、`spec-dock sync` / validation。

## 例外・エッジケース
- EC-001:
  - 条件:
    - checks が green になった直後に review comment が追加される。
  - 期待:
    - review snapshot が stable になるまで success を返さない。
  - 観測点:
    - quiet window / fingerprint tests。
- EC-002:
  - 条件:
    - GitHub Actions check run は success だが commit status が pending。
  - 期待:
    - checks/statuses 全体として pending / unknown が残る。
  - 観測点:
    - normalized checks/statuses output。
- EC-003:
  - 条件:
    - review thread が outdated または resolved。
  - 期待:
    - 単なる comment 存在だけで blocking review feedback と誤分類しない。
  - 観測点:
    - reviewThreads state output。
- EC-004:
  - 条件:
    - review thread state wrapper が missing / auth failure / rate limit / schema mismatch で失敗する。
  - 期待:
    - limitation を明示し、必要なら `review_state_unknown` / human gate で停止する。
  - 観測点:
    - wrapper failure tests、agent output。
- EC-005:
  - 条件:
    - non-required check が fail しているが GitHub UI の merge button は押せる。
  - 期待:
    - `pr-monitor` は failure を隠さず返す。waiver や optional 判定は caller / human gate 側に委ねる。
  - 観測点:
    - output schema、`github-pr-merge-preparer` compatibility。

## 入力→出力例
- EX-001:
  - 入力:
    - `repo=OWNER/REPO`
    - `pr=123`
    - `head_sha=abc123`
    - checks terminal success
    - review snapshot stable
    - thread state available and no unresolved actionable threads
  - 出力:
    - `overall_status=success`
    - `normalized_status=success`
    - `head_sha=abc123`
    - `snapshot_stable=true`
    - no blocking checks
    - no blocking review feedback
- EX-002:
  - 入力:
    - expected `head_sha=abc123`
    - current PR head SHA is `def456`
  - 出力:
    - `overall_status=timeout` または後方互換上の non-success status
    - `normalized_status=stale_head`
    - expected / current head SHA を明示
    - recommended next action: latest head SHA で re-monitor
- EX-003:
  - 入力:
    - checks success
    - review comments exist
    - thread state unavailable
  - 出力:
    - `overall_status=review_changes_requested` または後方互換上の non-success status
    - `normalized_status=review_state_unknown`
    - limitation と human gate 推奨を明示

## 用語（ドメイン語彙）
- TERM-001:
  - stable snapshot:
    - head SHA、checks/statuses、reviews/comments/threads を正規化した fingerprint が、minimum quiet window と連続 poll 条件を満たして変化していない状態。
- TERM-002:
  - head-SHA-bound observation:
    - PR current head SHA または expected head SHA に紐づく signals だけを final result の根拠にする観測。
- TERM-003:
  - review_state_unknown:
    - review comments / reviews は存在するが、thread state や actionability が判定できず success と扱えない状態。
- TERM-004:
  - fixed read-only wrapper:
    - caller から arbitrary endpoint / method / query を受け取らず、固定された read-only GitHub data collection だけを行う script。

## 未確定事項
- Blocking question:
  - なし。
  - ユーザー提供レポートと既存 `iss-00105` の follow-up candidate を踏まえ、本 issue は fixed read-only wrapper を含む stable observation hardening として要件化する。
- Non-blocking design questions:
  - reviewThreads 取得を既存 wrapper 拡張に入れるか、別 wrapper に分けるか。
  - GraphQL query と pagination をどの schema / helper で固定するか。
  - `overall_status` 後方互換のため、`review_state_unknown` / `stale_head` をどの existing status に map するか。
  - zero-check grace window と minimum quiet window の default 秒数。
  - expected check names / requested reviewer wait を optional input とするか、初期 scope では explicit policy がある時だけ扱うか。
