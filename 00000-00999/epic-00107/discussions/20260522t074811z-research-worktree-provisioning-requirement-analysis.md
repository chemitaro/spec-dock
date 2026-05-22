---
種別: research
ID: "20260522t074811z-research"
タイトル: "worktree provisioning requirement analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
親: ["epic-00107"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: ["../requirement.md"]
---

# 20260522t074811z-research worktree provisioning requirement analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、判断への含意を混ぜない。

## 調査目的 (必須)
- `spec-dock` に worktree 作成 command を追加する epic の requirement を固めるため、次を明らかにする。
  - 既存 `spec-dock` runtime command architecture の追加先。
  - 参照プロダクト `taikyohiyou_project-issue-1716` の worktree naming / branch naming / bootstrap の実用実装。
  - Git / Codex app / AGENTS.md / local environment の一次情報から見た、worktree placement と bootstrap の制約。
  - 今回の epic で閉じる scope と、将来 issue / future epic へ送る scope。

## 調査方法 (必須)
- ローカル repo 調査:
  - `git status --short --branch`
  - `find spec-dock/active -maxdepth 3 ...`
  - `rg -n "worktree|MakeInit|make init|git worktree" src spec-dock tests`
  - `sed -n` で runtime parser / registry / command / infra / test harness を確認。
- 参照プロダクト調査:
  - `rg -n "worktree|MakeInit|make init|COMPOSE_PROJECT_NAME|git worktree" /Users/iwasawayuuta/workspace/product/taikyohiyou_project-issue-1716`
  - `scripts/worktree/create_worktree.sh`
  - `Makefile`
  - `docs/dynamic-worktree-support.md`
- 外部一次情報:
  - Git worktree manual: https://git-scm.com/docs/git-worktree
  - Codex app worktrees: https://developers.openai.com/codex/app/worktrees
  - Codex app local environments: https://developers.openai.com/codex/app/local-environments
  - Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md

## 調査結果 (必須)
- 現在の `spec-dock` 状態:
  - active initiative / epic / issue は `spec-dock/system/active-none/...` を指しており、active context は未設定。
  - `epic-00107-worktree-provisioning` は既に `init-local-00002` 配下に作成されているが、`requirement.md` はテンプレート未記入状態だった。
  - `epic-00107` の `.meta.json` は GitHub issue `#107` と紐づいている。
- 既存 epic との関係:
  - `epic-00054` は close / delete / self-update の lifecycle command expansion を扱っており、worktree 作成の能力追加は含まない。
  - `epic-00074` は host agent / config asset expansion を扱っており、worktree 作成 command とは別の feature capability である。
  - 既存 epic へ混ぜるより、並行開発 capability として新規 epic にするのが自然である。
- `spec-dock` runtime architecture:
  - CLI parser は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` で top-level subcommand を定義する。
  - command registry は `cli/registry.py` で `commands/*` の `command_specs()` を集約する。
  - user-facing command args / output は `commands/` と `presentation/`、orchestration は `application/`、Git subprocess は `infra/git_cli.py` が既存の層である。
  - runtime tests は `tests/cli_runtime/`、domain/presentation tests はそれぞれ `tests/domain_runtime/`, `tests/presentation_runtime/` に分かれている。
- 参照プロダクトの worktree 実装:
  - `Makefile` の `worktree` target は `make worktree <optional-label>` 形式で `scripts/worktree/create_worktree.sh "$DIR_ARG"` を呼ぶ。
  - label 省略時は `wt1`, `wt2`, ... を使い、label 指定時は `<label>`, `<label>2`, ... を使う。
  - label は `^[a-z0-9-]+$` のみを許可する。
  - worktree directory は現在 checkout の basename に `-<id>` を足した sibling directory として合成する。
  - branch name は現在 branch に `-<id>` を足して合成する。
  - directory existence、branch existence、`git worktree list --porcelain` の record existence を事前確認し、衝突時は番号を進める。
  - `git worktree add -b <new-branch> <path>` が、retryable な衝突で失敗した場合も番号を進める。
  - 作成後に worktree root で `make init` を実行する。
- 参照プロダクトの bootstrap contract:
  - `docs/dynamic-worktree-support.md` は project-local bootstrap の正本を `make init` とし、worktree 作成後に worktree root で `make init` を呼ぶと明記している。
  - 同 docs は secret-bearing env file copy や `.env.git` generation を通常 worktree setup へ戻さないことを明記している。
- Git worktree 一次情報:
  - Git は main worktree と linked worktree を同じ repository metadata に紐づけ、複数 branch の同時 checkout を可能にする。
  - `git worktree add -b <branch> <path>` は新しい branch を作って worktree に checkout する。
  - `git worktree list --porcelain` は script 用の安定した一覧形式として使える。
  - 不要な linked worktree は `git worktree remove` で消すのが基本であり、手動削除後は `git worktree prune` / `repair` が必要になる場合がある。
- Codex app 一次情報:
  - Codex app は `$CODEX_HOME/worktrees` に worktree を作り、通常 detached HEAD で開始する。
  - Codex app の Handoff は Git 操作で Local と Worktree の間を移すが、同じ branch は複数 worktree で同時 checkout できない。
  - Codex local environments は worktree setup steps と common actions を `.codex` folder に保存できる。
  - Codex は `AGENTS.md` を global / project / nested scope で読み込み、repo guidance を作業前に取り込む。

## 推測 / 未検証事項 (必須)
- 推測:
  - ユーザー発話の「MakeInit」は、参照プロダクトと周辺文脈から `make init` を指すと解釈するのが自然である。
  - worktree container は `../<repo-basename>-worktrees/` が望ましい。ユーザーは `.<suffix>` ではなく、ハイフンまたはアンダースコアを好むと述べており、既存 repo 名 `spec-dock` と lowercase path ルールにも `spec-dock-worktrees` が合う。
  - container 配下の個別 worktree directory 名は、参照プロダクトの naming を維持するため `<repo-basename>-<id>` とするのが最も保守的である。
- 未検証:
  - `spec-dock` 自体の `make init` で実行すべき具体的 bootstrap 内容は、この requirement phase では未設計。
  - worktree cleanup / list / status を同じ command family に入れるべきかは、今回の user request の主眼ではないため future extension として扱う。
  - command family は requirement 反映時に `worktree create` 採用で確定した。`worktree cleanup / list / status` の追加有無は future extension として未検証である。

## 判断への含意 (必須)
- Requirement へ反映すること:
  - この epic は `init-local-00002` の feature expansion として、SpecDock が repo-local runtime command から dedicated linked worktree を作成できる capability を提供する。
  - `../<repo-basename>-worktrees/` container を標準 placement とし、repo 内 nested `.worktrees/` は採らない。
  - linked worktree から実行された場合でも、container placement と repo basename は Git worktree list の main worktree を基準に正規化する。
  - naming は参照プロダクトに合わせ、id は省略時 `wtN`、label 指定時 `<label>N`、branch は current branch + `-<id>`、directory は repo basename + `-<id>` を基本にする。
  - label validation は lowercase alnum + hyphen のみを要求する。
  - 作成後 bootstrap は worktree root の `make init` を optional / non-fatal にする。存在しなければ skip し、存在して失敗しても worktree 作成自体は exit code 0 の成功として扱う。ただし operator が追える warning / output は残す。
  - Codex-managed worktree を置き換えるのではなく、手動管理の長命 worktree 作成を扱う。
  - main checkout での実装作業を禁止する epic ではなく、複数変更の並行開発を支援する epic として扱う。
- Design / plan へ送ること:
  - `worktree create` command の application / infra / presentation 責務境界。
  - Git subprocess adapter の責務境界。
  - `make init` target existence check と non-fatal warning の表現。
  - created path / branch / init status の output contract。
  - provider-side runtime と dogfooding workspace の更新順。

## リスク/制約 (任意)
- `make init` failure を完全に無音化すると、依存関係や env setup の失敗を operator が見落とす。要件では「作成失敗にはしない」が、warning として観測可能にする。
- branch name は current branch へ suffix を足すため、保護 branch 上で実行しても新 branch は別名になる。ただし current branch が detached HEAD の場合は作成を拒否する必要がある。
- worktree container を repo 外へ作るため、permission / parent path の存在 / path collision を明確な failure として扱う必要がある。
- `git worktree add` は branch が他 worktree で checkout 済みの場合に拒否する。command は collision detection と retry で扱える範囲だけ retry し、未知エラーは隠蔽しない。

## 反映先 (任意)
- reflected_to:
  - `../requirement.md`

## 参考（References） (任意)
- Git worktree manual: https://git-scm.com/docs/git-worktree
- Codex app worktrees: https://developers.openai.com/codex/app/worktrees
- Codex app local environments: https://developers.openai.com/codex/app/local-environments
- Codex AGENTS.md guidance: https://developers.openai.com/codex/guides/agents-md
- `/Users/iwasawayuuta/workspace/product/taikyohiyou_project-issue-1716/scripts/worktree/create_worktree.sh`
- `/Users/iwasawayuuta/workspace/product/taikyohiyou_project-issue-1716/Makefile`
- `/Users/iwasawayuuta/workspace/product/taikyohiyou_project-issue-1716/docs/dynamic-worktree-support.md`
