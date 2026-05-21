---
種別: research
ID: "20260520t231224z-research"
タイトル: "PR Lifecycle Skill Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["iss-00105"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260520t231224z-research PR Lifecycle Skill Analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、判断への含意を混ぜない。

## 調査目的 (必須)
- ユーザーが毎回口頭で指示している「PR 作成、PR 監視、CI / review 指摘の分析、修正委譲、push、再監視、merge-ready までの反復」を、spec-dock の agent-tooling skill としてどう定義すべきかを明らかにする。
- 既存の `github-pr-creator`、`pr-monitor`、GitHub plugin skills、Codex agent roles、install_root 配布契約を調べ、新規 skill と既存 skill 更新の境界を決める。
- 要件定義書へ反映する前に、責務、状態遷移、停止条件、人間確認 gate、検証可能な受け入れ条件を整理する。

## 調査方法 (必須)
- Active context:
  - `./spec-dock/scripts/spec-dock active show`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/report.md`
- 既存 skill / agent:
  - `.agents/skills/github-pr-creator/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/SKILL.md`
  - `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
  - `.codex/agents/pr-monitor.toml`
  - `.github/agents/pr-monitor.agent.md`
  - `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
- Provider / packaging / test surface:
  - `src/spec_dock/cli.py`
  - `tests/test_init_update.py`
  - `pyproject.toml`
  - `src/spec_dock/assets/install_root/`
- GitHub plugin reference:
  - `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/gh-fix-ci/SKILL.md`
  - `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/gh-address-comments/SKILL.md`
  - `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/yeet/SKILL.md`
- 過去 memory:
  - `/Users/iwasawayuuta/.codex/memories/MEMORY.md` の PR monitoring / merge-ready 関連項目。
- Delegated analysis:
  - `consultant`: workflow / product design recommendation。
  - `repo-analyst`: repo source-of-truth、実装面、影響範囲分析。
  - `deep-consultant`: durable skill contract と failure mode 分析。
- 外部一次情報:
  - GitHub CLI manual: `gh pr create`, `gh pr view`, `gh pr checks`
  - GitHub Docs: status checks, auto-merge

## 調査結果 (必須)
- Active issue:
  - `iss-00105` は `epic-00067 Installed layout aligned asset source structure for agent tooling` 配下で active 化済み。
  - 現在の `requirement.md` はテンプレート状態であり、要件作成前の調査・方針決定が必要。
- 既存 `github-pr-creator` skill:
  - PR 作成を担当する bounded skill として存在する。
  - base branch 解決、base/head diff inspection、日本語 PR title/body 作成、issue linkage、push、`gh pr create`、既存 PR 検出を扱う。
  - PR 作成後に `pr-monitor` へ渡すべきことは明記されている。
  - ただし、CI / review failure の分類、修正委譲、再 push、再監視、merge-ready までの反復を所有しない。
- 既存 `pr-monitor`:
  - `.codex/agents/pr-monitor.toml` と `.github/agents/pr-monitor.agent.md` に同等の read-only monitoring contract がある。
  - PR の checks / statuses と Codex review を監視し、情報が出揃った時点で `overall_status` を返す。
  - output status は `success` / `failed` / `review_changes_requested` / `timeout`。
  - 監視は read-only で、修正、コメント返信、thread resolve、merge、close、label 変更はしない。
  - default timeout は 30 分で、state-aware backoff を持つ。
- 既存 `github-codex-pr-review-comments` skill:
  - Codex review feedback を fixed REST GET wrapper で取得する。
  - wrapper は `--repo`、`--pr`、`--out` だけを受け取り、direct arbitrary GitHub API を公開しない。
  - `gh pr view --comments` の GraphQL failure を避けるため REST GET endpoints を使う。
- GitHub plugin skills:
  - `gh-fix-ci` は failing GitHub Actions checks の log inspection と root cause summary を扱うが、実装修正前に explicit approval を要求する設計。
  - `gh-address-comments` は unresolved review threads / inline comments の inspection と selected fixes を扱う。コメントが曖昧なら確認する。
  - `yeet` は staging / commit / push / draft PR creation までの publish flow であり、PR 作成後の反復監視・修正までは所有しない。
- Provider source-of-truth:
  - agent-tooling assets の authority は `src/spec_dock/assets/install_root/`。
  - dogfooding root の `.agents/`, `.codex/`, `.github/` は install_root と parity を保つ対象。
  - 新しい shipped skill を追加する場合は、少なくとも provider 側 `src/spec_dock/assets/install_root/.agents/skills/<skill>/SKILL.md` と dogfooding 側 `.agents/skills/<skill>/SKILL.md` の追加、`src/spec_dock/cli.py` の `_MANAGED_SKILL_NAMES`、`tests/test_init_update.py` の asset inventory / parity assertions 更新が必要になる可能性が高い。
- 過去運用記録:
  - PR monitoring の先例では、PR 作成や push だけで完了扱いせず、checks / reviews / `mergeStateStatus=CLEAN` / `mergeable=MERGEABLE` まで追う必要がある。
  - `gh pr view` の情報が不足するときは `gh run list/view` と review REST endpoint に pivot する運用が記録されている。
  - staging / required checks があとから失敗して mergeState が `UNSTABLE` になるケースがあり、local tests green だけでは不十分。
- Consultant recommendation:
  - 新 skill 名は `spec-dock-pr-lifecycle` が推奨。
  - skill は万能実装者ではなく coordinator とし、PR 作成・監視・修正・分析は既存 skill / roles へ委譲する。
  - 推奨 state machine は `prepare -> create-pr -> monitor -> classify-event -> delegate-fix-or-analysis -> verify -> monitor-again -> merge-ready-or-human-gate`。
  - merge 実行は初期 scope から外し、merge-ready 報告までに留めるのが安全。
- Repo-analyst recommendation:
  - 新 skill は `github-pr-creator` と `pr-monitor` を置き換えず、上位 orchestration として作るのがよい。
  - 名前候補は `github-pr-merge-ready`。
  - `pr-monitor` の現行 success は merge-ready と同義ではない。`mergeStateStatus`、`mergeable`、`reviewDecision`、branch freshness、failed check names を output に追加する必要がある可能性が高い。
  - 変更面は新 shared skill、`github-pr-creator` の使い分け追記、`pr-monitor` の output 拡張、dogfooding mirror、`tests/test_init_update.py` asset inventory / parity assertion 更新。
- Deep-consultant recommendation:
  - 新 shared skill の正本名候補は `github-pr-lifecycle`。
  - `github-pr-creator` は互換 entrypoint または leaf skill として残すのが壊れにくい。
  - `PR Lifecycle Consent` を別 contract として導入する。通常の issue delegation consent は external publishing / credentialed access を許可しないため、push / PR create / re-push / mark ready などの外部書き込みを tier 化する必要がある。
  - 自律範囲は PR 作成、監視、失敗分類、bounded fix 委任、再 push、再監視、merge-ready 判定まで。merge / auto-merge / branch delete / issue close / admin override は別 human gate。
  - fix loop は total 3 回、または同一 failure class 2 回程度で止めるのが安全。
  - `merge-ready` は「human が merge 判断に入れる状態」であり、自動 merge 許可ではない。
- GitHub CLI / GitHub Docs facts:
  - `gh pr create` は `--base` 指定を持ち、未指定時は current branch の `gh-merge-base` git config、なければ repository default branch を使う。PR body の `Fixes #123` / `Closes #123` は merge 時に issue を自動 close する。
  - `gh pr create --head` は `<user>:<branch>` をサポートするが、organization を `<user>` として指定することは現在サポートされていない。
  - `gh pr view --json` には `mergeStateStatus`、`mergeable`、`reviewDecision`、`statusCheckRollup`、`headRefOid` など merge-ready 判定に必要な field がある。
  - `gh pr checks --json` は `bucket` field で `pass` / `fail` / `pending` / `skipping` / `cancel` に分類でき、`--required` と `--watch` を持つ。
  - GitHub status checks には checks と commit statuses があり、required status checks は protected branch へ merge する前に pass が必要。
  - Auto-merge の有効化には write permission が必要で、required reviews / required status checks など repo 側条件とも絡むため、今回の自律範囲から外すのが妥当。

## 推測 / 未検証事項 (必須)
- 推測:
  - 新 skill は `.agents/skills/spec-dock-pr-lifecycle/SKILL.md` として追加するのが自然。`github-pr-creator` を肥大化させるより、上位 orchestration skill として切り出す方が責務が明確。
  - `github-pr-creator` は PR creation leaf skill として維持し、新 skill 側から利用する形がよい。
  - `pr-monitor` は read-only status aggregator として維持し、fix / push / retry の判断は新 skill 側が所有するべき。
  - 既存 GitHub plugin skills (`gh-fix-ci`, `gh-address-comments`) はこの repo に shipped される skill ではないが、設計上の参照として「CI failure handling」「review comment handling」の分離に使える。
- 未検証:
  - `pr-monitor` role が現在の host runtime で `spawn_agent(agent_type="pr-monitor")` として常に利用可能か。
  - `pr-monitor` が mergeability (`mergeStateStatus`, `mergeable`, branch up-to-date) を十分に監視しているか。現状 text では checks / statuses / Codex review が中心で、merge-ready 判定に必要な branch freshness / conflict / required review decision まで十分かは追加確認が必要。
  - `github-pr-creator` が PR body で spec-dock issue docs / report をどこまで読むべきか。現状は diff grounded PR title/body が中心で、active issue docs / report 由来の作業経緯を必須読取にするなら更新が必要。
  - 修正後 commit / push の責務を新 skill 自体が持つのか、`dev-coder` / `utility-worker` / main orchestrator へどの粒度で委譲するのか。
  - 自動継続可能な修正とユーザー確認が必要な修正の境界。
  - 反復上限を回数、同一 failure recurrence、経過時間のどれで固定するか。
  - 新 skill 名を `spec-dock-pr-lifecycle`、`github-pr-lifecycle`、`github-pr-merge-ready` のどれにするか。
  - `github-pr-creator` を互換 entrypoint として新 lifecycle skill へ route させるか、creation-only leaf skill として現状維持するか。
  - unresolved review thread state を現行 REST wrapper の範囲で扱うか、固定 read-only GraphQL wrapper / GitHub connector を追加許可するか。

## 判断への含意 (必須)
- Requirement では「作るもの」を `spec-dock-pr-lifecycle` という上位 coordinator skill として定義するのが有力。
- Requirement の MUST は、PR 作成そのものではなく、PR lifecycle の orchestration を中心に置くべき:
  - active issue docs / report / diff / branch state の事前理解。
  - PR 未作成時の `github-pr-creator` または `utility-worker` への PR 作成委譲。
  - PR 作成後 / push 後の `pr-monitor` 委譲。
  - `pr-monitor` output の分類。
  - CI failure / review feedback の分析・修正委譲。
  - 修正後 push と再監視の反復。
  - merge-ready または human gate で停止。
- Requirement の MUST NOT:
  - skill 自体に CI log parsing、review thread handling、implementation fix、merge execution を抱え込ませない。
  - 独断で merge しない。
  - 要件・設計・public contract・migration・secret / deployment settings をユーザー確認なしに変更しない。
  - 無限 retry しない。
- Design では state machine と role routing table が必要。
- Plan では docs-only / skill-text change として、provider install_root、dogfooding parity、installer managed skill list、asset inventory tests、spec-review を step 化する必要がある。
- `pr-monitor` 自体の merge-ready coverage が不足している場合、`pr-monitor` 更新を同じ issue に含めるか、新 skill 側で補うかを design で決める必要がある。
- `PR Lifecycle Consent` を requirement に入れる場合、既存 `workflow_issue.md` の delegation consent との境界を明記する必要がある。PR 作成と push は external publishing / credentialed write なので、通常の reviewer / specialist delegation consent とは別の明示許可を要求するのが安全。
- 名称はユーザー意図と配布対象を両方考慮すると、`github-pr-lifecycle` が最も中立的。`spec-dock-pr-lifecycle` は spec-dock issue/report の読取を強く示すが、GitHub PR lifecycle general skill としては狭い。`github-pr-merge-ready` は outcome が分かりやすいが、PR 作成前から始まる state machine 全体を少し狭く表現する。

## リスク/制約 (任意)
- 既存 `pr-monitor` は read-only agent なので、修正・push・再監視の loop owner にはできない。loop owner を `pr-monitor` に寄せると責務が壊れる。
- `github-pr-creator` を拡張しすぎると、PR creation leaf skill が PR lifecycle coordinator に変質し、再利用性が落ちる。
- merge-ready の定義が曖昧なままだと、checks green だが branch stale / conflict / required review pending の PR を成功扱いする危険がある。
- review comments のうち、Codex review のみを対象にするか、人間 reviewer / GitHub requested changes も対象にするかを明確にしないと、skill の停止条件と自動修正範囲が揺れる。
- CI failure の中には flaky / external / infra / permission failure があり、実装修正へ進むと逆に悪化する場合がある。
- GitHub 操作は credentialed access を伴うため、host policy、`gh` auth、repo permissions、fork PR の扱いを failure mode として明記する必要がある。

## 反映先 (任意)
- reflected_to:
  - 未反映。repo-analyst / deep-consultant の結果とユーザー確認後、`requirement.md` へ反映する。

## 参考（References） (任意)
- `.agents/skills/github-pr-creator/SKILL.md`
- `.codex/agents/pr-monitor.toml`
- `.github/agents/pr-monitor.agent.md`
- `.agents/skills/github-codex-pr-review-comments/SKILL.md`
- `.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh`
- `src/spec_dock/cli.py`
- `tests/test_init_update.py`
- `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/gh-fix-ci/SKILL.md`
- `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/gh-address-comments/SKILL.md`
- `/Users/iwasawayuuta/.codex/plugins/cache/openai-curated/github/ed8ce2ea/skills/yeet/SKILL.md`
- `/Users/iwasawayuuta/.codex/memories/MEMORY.md`
- GitHub CLI manual: `gh pr create` https://cli.github.com/manual/gh_pr_create
- GitHub CLI manual: `gh pr view` https://cli.github.com/manual/gh_pr_view
- GitHub CLI manual: `gh pr checks` https://cli.github.com/manual/gh_pr_checks
- GitHub Docs: About status checks https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks
- GitHub Docs: Automatically merging a pull request https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request
