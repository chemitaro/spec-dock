---
種別: 要件定義書（Issue）
ID: "iss-00180"
タイトル: "Github Token Capability Preflight"
関連GitHub: ["#180"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-11"
親: ["epic-00067", "init-local-00003"]
---

# iss-00180 Github Token Capability Preflight — 要件定義（何を、なぜ行うか）

## 目的
- GitHub token の権限不足により PR / CI 観測が `unknown` になる前に、実際に使われる token の capability 不足として診断できるようにする。
- `spec-dock doctor` では手動診断として GitHub token capability findings を返し、`github-pr-observation` では PR observation の final JSON に machine-readable limitation と semantic non-success を返す。
- `GH_TOKEN` が `gh` 保存済み token より優先される実行環境でも、利用者とエージェントが原因、失敗 API、次アクションを切り分けられる状態にする。

## 背景・現状
- 現状の挙動:
  - PR observation / merge-preparer 系 workflow は `check-runs`、commit statuses、`statusCheckRollup`、PR review / comment signals を GitHub CLI / API で収集する。
  - GitHub API 権限不足、schema failure、取得不能は observation の `unknown` や limitation として現れる。
  - `spec-dock doctor` は spec tree / active pointer / create lock などの構造診断を持つが、GitHub token capability の診断 contract はない。
- 現状の課題:
  - `GH_TOKEN` に設定された fine-grained PAT の権限が不足していると、`gh` 保存済み token では読める API でも `Resource not accessible by personal access token` になる。
  - 現在の利用者体験では、PR / CI が本当に不明なのか、実行 token の権限不足なのか、どの API / permission が不足しているのかを切り分けにくい。
  - PR observation の final JSON を merge-prepared evidence として使う workflow では、権限不足を `passed` 相当として扱ってはならない。
- 再現手順:
  1. `GH_TOKEN` に checks / actions / statuses 系 read 権限が不足した token を設定する。
  2. PR observation または GitHub checks 取得を実行する。
  3. `gh api repos/<owner>/<repo>/commits/<sha>/check-runs --paginate`、`gh pr view <pr> --json statusCheckRollup`、`gh pr checks <pr>` が `Resource not accessible by personal access token` を返す。
  4. `GH_TOKEN` を外して `gh` 保存済み token を使うと同じ repo / PR / commit で取得できる。
- 観測点:
  - CLI:
    - `spec-dock doctor`
    - `github-pr-observation` scripts の stdout final JSON
  - GitHub API:
    - `check-runs`
    - commit `status`
    - `statusCheckRollup`
    - PR metadata
    - trigger comment write failure when `@codex review` posting is attempted
  - ログ / 出力:
    - stderr progress は authority ではない。PR observation の primary authority は stdout final JSON である。
- 情報源:
  - GitHub issue `#180`
  - `discussions/20260611t135317z-interview-github-token-capability-scope.md`
  - `discussions/20260611t135608z-interview-github-capability-probe-profile.md`
  - `discussions/20260611t135901z-interview-github-capability-failure-semantics.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00170-harden-pr-monitor-stable-observation/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00176-github-pr-observation-codex-review-trigger-and-completion/requirement.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - PR 作成後または push 後に GitHub checks / reviews を待つ main orchestrator。
  - `github-pr-merge-preparer` / `github-pr-observation` を使い、merge-prepared evidence を作る agent。
  - GitHub token / PAT 設定を調整する maintainer。
- 代表シナリオ:
  - maintainer が `spec-dock doctor` を実行し、現在の実行環境で `GH_TOKEN` が優先されていることと、core GitHub capability の不足を確認する。
  - PR observation が `check-runs` または `statusCheckRollup` を読めない場合、stdout final JSON に permission limitation と recommended next action を含め、merge-prepared と誤判定しない。
  - `@codex review` trigger comment の投稿権限が不足した場合、trigger write failure を PR observation の limitation として返し、blind retry や arbitrary write に広げない。

## スコープ
- 必須:
  - `doctor` と PR observation workflow の両方を scope に含める。
  - 共通 core capability probe を fixed API set として定義する。
  - core capability probe は repository metadata / PR read / commit check-runs read / commit statuses read / `statusCheckRollup` read を対象にする。
  - `doctor` では core capability と optional extended checks を分けて表示する。
  - `doctor` の PR / commit 固有 core probe は、対象 repo / PR / head SHA が明示された場合だけ実行する。
  - `doctor` に PR / commit probe target が無い場合は、通常の structural diagnosis を維持し、GitHub PR core probe を `skipped` / `target_unavailable` diagnostic として表示できる。これは capability failure ではない。
  - optional extended checks は `doctor` の診断表示用に限定し、次の fixed capability set だけを扱う。
    - `actions_read`: repository Actions runs metadata read。
    - `issue_comments_read`: PR conversation issue comments read。
  - `doctor` standalone probe は write operation を実行しない。PR observation の固定 `@codex review` trigger write failure / success は `doctor` 表示対象ではなく、PR observation final JSON の limitation / trigger result surface で扱う。
  - Optional extended checks は core result と分けて扱う。上記以外の GitHub capability / endpoint はこの issue の optional extended scope に含めない。
  - `GH_TOKEN` が設定されている場合、実行時に優先される token source として明示する。ただし token value は表示しない。
  - `Resource not accessible by personal access token` を GitHub token permission issue として分類できる。
  - permission denied / auth missing / rate limited / transient unknown / malformed response を区別できる machine-readable result を持つ。
  - `doctor` は capability findings を診断結果として返し、capability finding だけで structural doctor failure と混同しない。
  - PR observation は core capability failure と trigger write failure を stdout final JSON の limitation / recommended next action / semantic non-success として返す。
  - PR observation の permission limitation は merge-prepared evidence に使えない。
  - malformed input、script misuse、final JSON construction failure などは command/runtime error として扱い、capability limitation と混同しない。
  - provider-side source と dogfooding mirror の parity を維持する。
  - token permission guidance は必要 permission の目安を示し、fine-grained PAT / classic PAT / GitHub App token の違いを断定しすぎない。
- 禁止:
  - arbitrary GitHub API checker を作らない。
  - caller-provided endpoint / method / raw `gh` args / GraphQL / jq / headers を capability probe に受け入れない。
  - token value、hosts.yml の secret、private payload を出力しない。
  - capability probe のために不要な GitHub write operation を実行しない。
  - Issue comment write capability を検査するために任意 body を投稿しない。
  - PR observation が permission limitation を `passed` / merge-ready / merge-prepared 相当として返さない。
  - stderr progress を final decision authority にしない。
  - `pr-monitor` や retired wrapper を復活させない。
- 対象外:
  - GitHub token の自動発行、保存、更新。
  - GitHub fine-grained PAT permission UI の自動操作。
  - GitHub App / organization policy の管理。
  - repository-specific required checks policy の全面設定機構。
  - PR merge、auto-merge、branch cleanup、issue finish。
  - `gh` の認証状態そのものを修復する command。

## 境界
- 常に行う:
  - fixed core probe と optional extended checks を分ける。
  - `GH_TOKEN` 優先状態は source label として表示し、secret は表示しない。
  - permission denied は API / capability / token source / remediation hint を machine-readable に残す。
  - PR observation final JSON の semantic status / limitation / recommended next action を caller が読める形にする。
- 判断が必要:
  - Design phase で `permission_denied` を新しい normalized status として導入するか、既存 `unknown` / `human_gate` + limitation に留めるかを決める。
  - Design phase で `doctor` の明示 target surface を CLI option にするか、既存 observation artifact / environment 由来にするかを決める。ただし no-target path は skipped diagnostic とする。
  - なし。PR observation の fixed trigger write failure / success は `doctor` 表示対象から外し、PR observation final JSON のみで扱う。
  - `doctor` の structural findings と capability findings を同じ `DoctorFinding` に入れるか、別の diagnostic channel に分けるかを決める。
- 行わない:
  - GitHub API 全般の permission scanner にしない。
  - GitHub CLI の credential store を読み取って secret を表示しない。
  - PR observation の read-only / fixed trigger write 境界を広げない。

## 非交渉制約
- Capability probe は fixed endpoint set に閉じる。
- Core probe は PR checks / statuses 観測に必要な最小 capability に固定する。
- PR / commit 固有 probe は target context なしに推測実行しない。
- Target context がない `doctor` 実行は capability failure ではなく target unavailable / skipped diagnostic とする。
- Optional extended checks は `doctor` 表示用であり、PR observation の必須 success 条件に混ぜない。
- Optional extended checks は `actions_read`、`issue_comments_read` に限定し、不要な write operation を発生させない。
- `doctor` は capability findings を返せるが、capability finding だけを spec tree structural failure として扱わない。
- PR observation は permission limitation を semantic non-success として扱い、merge-prepared evidence に使わない。
- stdout final JSON が PR observation の primary authority である。
- Token value / secret / private payload は絶対に出力しない。

## 前提
- 実行環境には GitHub CLI `gh` がある。
- 対象 repo / PR / commit が probe の入力として解決できる。
- `doctor` の PR / commit 固有 probe は対象 repo / PR / head SHA の target context を必要とし、target context が無い通常 `doctor` 実行では probe skipped とする。
- `GH_TOKEN` が設定されている場合、GitHub CLI はそれを保存済み token より優先する。
- `github-pr-observation` の provider-side source of truth は `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` である。
- Dogfooding mirror `.agents/skills/github-pr-observation/` は provider-side source と parity を保つ。
- `doctor` runtime の provider-side source of truth は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` である。

## 受け入れ条件
- AC-001: `doctor` が明示 target 付きで core capability findings を表示する
  - アクター:
    - maintainer
  - 前提:
    - `GH_TOKEN` が優先されている。
    - maintainer が対象 repo / PR / head SHA を明示して GitHub PR core probe を有効にしている。
    - core capability のうち `check-runs` または `statusCheckRollup` read が permission denied になる。
  - 操作:
    - maintainer が `spec-dock doctor` の GitHub PR core probe path を実行する。
  - 期待結果:
    - `doctor` は token source と failing capability を secret なしで表示する。
    - `Resource not accessible by personal access token` は token permission issue として説明される。
    - structural spec tree failure と capability finding は混同されない。
  - 観測点:
    - CLI runtime test
    - doctor rendering assertion

- AC-001b: `doctor` が target なしでは PR core probe を失敗扱いしない
  - アクター:
    - maintainer
  - 前提:
    - repo 内で通常の `spec-dock doctor` を実行する。
    - PR number / head SHA などの PR core probe target は明示されていない。
  - 操作:
    - maintainer が `spec-dock doctor` を実行する。
  - 期待結果:
    - structural diagnosis は従来どおり実行される。
    - GitHub PR core probe は `skipped` / `target_unavailable` diagnostic として表現され、permission denied や structural failure として扱われない。
    - token value は表示されない。
  - 観測点:
    - CLI runtime test
    - doctor rendering assertion

- AC-002: PR observation が permission limitation を final JSON に返す
  - アクター:
    - main orchestrator / `github-pr-merge-preparer`
  - 前提:
    - `check-runs`、commit statuses、または `statusCheckRollup` が token permission で取得できない。
  - 操作:
    - `github-pr-observation` の snapshot または wait script を実行する。
  - 期待結果:
    - stdout final JSON に permission limitation、failing capability、recommended next action が含まれる。
    - normalized status は merge-prepared に使えない non-success になる。
    - process exit code は final JSON が構築できる限り原則 0 を維持する。
  - 観測点:
    - script stub test
    - final JSON assertion

- AC-003: trigger write failure が core read failure と分離される
  - アクター:
    - main orchestrator
  - 前提:
    - core read capability は足りているが、`@codex review` trigger comment の投稿が permission denied になる。
  - 操作:
    - `wait_pr_observation.sh` を trigger posting path で実行する。
  - 期待結果:
    - trigger write failure は core read failure とは別の limitation として返る。
    - blind retry や arbitrary write に広がらない。
    - final JSON は human gate / permission remediation を促す。
  - 観測点:
    - trigger script / wait script stub test
    - limitation code assertion

- AC-004: capability probe が secret を出力しない
  - アクター:
    - maintainer / reviewer
  - 前提:
    - `GH_TOKEN` または `gh` credential store が存在する。
  - 操作:
    - `doctor` と PR observation failure path を実行する。
  - 期待結果:
    - 出力には token source label と capability result だけが含まれ、token value、hosts.yml secret、private payload は含まれない。
  - 観測点:
    - output assertion
    - forbidden token assertion

- AC-005: capability probe が fixed endpoint set に閉じる
  - アクター:
    - implementer / reviewer
  - 前提:
    - capability probe を実装する。
  - 操作:
    - API invocation surface と script arguments を確認する。
  - 期待結果:
    - caller-provided endpoint / method / raw `gh` args / GraphQL / jq / headers は受け付けない。
    - probe は requirement で固定した core / extended capability に限定される。
  - 観測点:
    - unit test
    - script usage validation
    - code review

- AC-006: malformed input と capability limitation が分離される
  - アクター:
    - implementer / maintainer
  - 前提:
    - repo slug missing、PR number missing、invalid JSON など command/runtime error が起きる。
  - 操作:
    - `doctor` または PR observation を不正入力 / malformed response path で実行する。
  - 期待結果:
    - script misuse / malformed input / JSON construction failure は command/runtime error として扱われる。
    - GitHub token permission limitation と誤分類されない。
  - 観測点:
    - negative test

- AC-007: `doctor` が optional extended checks を core と分離して表示する
  - アクター:
    - maintainer / reviewer
  - 前提:
    - `doctor` の GitHub capability diagnosis が有効である。
    - core probe target は明示されている、または core probe は target unavailable として skipped されている。
  - 操作:
    - maintainer が `spec-dock doctor` を実行する。
  - 期待結果:
    - optional extended checks は core capability result と別の group / field / label で表示される。
    - `actions_read`、`issue_comments_read` は optional extended check として扱われ、core pass / fail を汚さない。
    - 上記以外の GitHub capability は skipped / out-of-scope として扱われる。
    - optional extended checks のために不要な GitHub write operation は実行されない。
  - 観測点:
    - CLI runtime test
    - no-write assertion
    - doctor rendering assertion

## 例外・エッジケース
- EC-001: `GH_TOKEN` missing
  - 条件:
    - `GH_TOKEN` が未設定で、`gh` 保存済み token が使われる。
  - 期待:
    - token source は saved `gh` auth 相当として表示される。secret は表示しない。
  - 観測点:
    - doctor rendering assertion

- EC-002: auth missing
  - 条件:
    - GitHub CLI が認証されていない。
  - 期待:
    - auth missing と permission denied を区別し、`gh auth login` または token 設定確認を促す。
  - 観測点:
    - CLI / script stub test

- EC-003: rate limit / transient failure
  - 条件:
    - GitHub API が rate limit、network、temporary unavailable、schema mismatch を返す。
  - 期待:
    - permission denied と区別し、transient / unknown limitation として扱う。
  - 観測点:
    - script stub test

- EC-004: partial capability
  - 条件:
    - PR metadata は読めるが check-runs が読めない、または check-runs は読めるが `statusCheckRollup` が読めない。
  - 期待:
    - capability ごとの result を返し、失敗した API だけを remediation 対象として示す。
  - 観測点:
    - unit / script test

- EC-005: optional extended check unavailable
  - 条件:
    - `doctor` の optional extended checks が一部確認できない。
  - 期待:
    - core capability result と分けて表示し、PR observation の core success / failure 判定を汚さない。
  - 観測点:
    - doctor rendering assertion

## 入力→出力例
- EX-001: `doctor` の capability finding
  - 入力:
    - `GH_TOKEN` が優先され、`check-runs` read が `Resource not accessible by personal access token` を返す。
  - 出力:
    - `github_token_capability` finding / diagnostic に `token_source=GH_TOKEN`, `capability=check_runs_read`, `status=permission_denied`, `api=check-runs`, `secret_redacted=true` が含まれる。

- EX-002: PR observation final JSON
  - 入力:
    - `fetch_pr_observation_snapshot.sh` が checks collector で permission denied を受け取る。
  - 出力:
    - `normalized_status` は merge-prepared に使えない non-success。
    - `limitations[]` に permission limitation object が含まれる。
    - `recommended_next_action` は token permission remediation / human gate を示す。

## 用語（ドメイン語彙）
- TERM-001: core capability probe
  - PR checks / statuses 観測に必要な fixed endpoint set の read-only probe。repository metadata、PR read、check-runs、commit statuses、`statusCheckRollup` を対象にする。
- TERM-002: optional extended checks
  - `doctor` 表示用の追加診断。`actions_read`、`issue_comments_read` だけを扱う。上記以外の GitHub capability / endpoint はこの issue の optional extended checks に含めない。
- TERM-003: token source
  - 実行時に GitHub CLI が使う token の由来を示す label。`GH_TOKEN`、saved gh auth、unknown など。secret value ではない。
- TERM-004: semantic non-success
  - process が final JSON を返せても、workflow evidence として成功ではない状態。PR observation では merge-prepared evidence に使えない。

## 未確定事項
- なし:
  - Scope、probe profile、failure semantics は adopted interview 3件で確定済み。
