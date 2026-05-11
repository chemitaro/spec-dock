---
種別: 要件定義書（Issue）
ID: "iss-00091"
タイトル: "Default Github State Commands"
関連GitHub: ["#91"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-11"
親: ["epic-00090", "init-local-00003"]
---

# iss-00091 Default Github State Commands — 要件定義（WHAT / WHY）

## 目的
- `sync` / `deps check` / `active set` が、flag なしで GitHub issue state を取得する状態を標準動作にする。
- stale cache に依存した通常運用をやめ、GitHub-backed workflow の実態に合わせる。
- GitHub 連携を行わない明示 opt-out は、既存インターフェース語彙に合わせて `--no-github` とする。

## 背景・現状
- 現状の挙動:
  - `sync` は `--github` を付けた場合だけ `gh issue list` / `gh issue view` で GitHub state を取得する。
  - `deps check` と `active set` も `--github` を付けた場合だけ GitHub state を使う。
  - flag なしでは `.agent/index-all.json` / `.agent/index.json` の cached status を使う。
  - `new initiative` / `new epic` / `new issue` はすでに GitHub linkage mandatory であり、`--no-github` は rejected contract として残っている。
- 現状の課題:
  - 通常運用の issue lifecycle は GitHub-backed なのに、状態確認系コマンドだけが cache-first に見える。
  - `issue start` や readiness 判断の前に `sync --github` / `deps check --github` を明示する必要があり、利用者が stale cache を読んで判断しやすい。
  - docs / skill / tests に `--github` 必須前提の表現が残っており、今後の標準 workflow とずれる。
- 情報源:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/sync.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `spec-dock/docs/reference_github.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - GitHub-backed な spec-dock workspace を使う coding agent / maintainer。
- 代表シナリオ:
  - maintainer が `./spec-dock/scripts/spec-dock sync` を実行すると、GitHub の open / closed state が標準で反映される。
  - agent が `deps check <target>` を実行すると、追加 flag なしで最新の GitHub state に基づく readiness を確認できる。
  - maintainer が意図的に GitHub へ接続したくない場合だけ `--no-github` を指定し、既存 cache に基づく状態確認を行う。

## スコープ
- MUST:
  - `sync` は flag なしで `github_enabled=True` として動作する。
  - `deps check` は flag なしで `use_github=True` として動作する。
  - `active set` は flag なしで `use_github=True` の deps guard を使う。
  - `sync` / `deps check` / `active set` に `--no-github` を追加し、指定時だけ GitHub 連携を行わない。
  - 既存 `--github` は後方互換 flag として残す。
  - `--github` と `--no-github` の同時指定は argparse error とする。
  - `new initiative` / `new epic` / `new issue` の `--no-github` rejected contract を維持する。
  - provider 側 docs / checked-in dogfooding docs / installed skill mirror / checked-in skill mirror の該当説明を更新する。
- MUST NOT:
  - `--offline` を導入しない。
  - local-only node creation を復活させない。
  - GitHub issue list の全件 cache file を新設しない。
  - `sync_state.py` / `check_deps.py` / `set_active.py` の GitHub fetch と cache resolution の基本構造を再設計しない。
- OUT OF SCOPE:
  - GitHub fetch failure を fatal error に変えること。
  - `close` / `delete` / `issue finish` の remote mutation contract 変更。
  - GitHub auth repair や network retry policy の新設。

## 境界
- Always:
  - GitHub-backed workspace の通常状態確認は GitHub live state を優先する。
  - GitHub を使わない読み取りは明示 opt-out でだけ行う。
  - `new` 系の GitHub mandatory identity contract は崩さない。
- Ask:
  - 将来、local-only workspace を正式サポートする必要が出た場合。
  - GitHub fetch failure を warning ではなく fatal にしたい場合。
- Never:
  - `--no-github` を local-only node creation の成功経路として扱わない。
  - `--github` なしの通常状態確認を stale cache 優先へ戻さない。

## 非交渉制約
- single GitHub repo 前提を維持する。
- GitHub issue state の bulk-first 取得方針を維持する。
- provider asset と dogfooding mirror の docs / skill drift を残さない。
- 新規パスは lowercase にする。

## 前提
- `gh` が利用可能で認証済みなら GitHub live state 取得が成功する。
- `--no-github` は cache/local state を明示的に選ぶための互換・退避手段であり、通常 workflow の推奨経路ではない。
- GitHub fetch 失敗時の現行 behavior は warning と unknown/stale 解決であり、この issue では fatal 化しない。

## 受け入れ条件
- AC-001:
  - Actor: maintainer / agent
  - Given: linked GitHub issues を持つ spec-dock workspace
  - When: `./spec-dock/scripts/spec-dock sync` を実行する
  - Then: `gh issue list` ベースの GitHub bulk fetch が標準で実行され、生成 artifact の issue status source は取得できた node で `github` になる
  - 観測点: CLI runtime test / `.agent/index-all.json`
- AC-002:
  - Actor: maintainer / agent
  - Given: `.agent/index-all.json` または `.agent/index.json` に cached issue status がある
  - When: `./spec-dock/scripts/spec-dock sync --no-github` を実行する
  - Then: `gh` は呼ばれず、既存 cache path で status が解決される
  - 観測点: gh guard log が作成されないこと / generated artifact
- AC-003:
  - Actor: maintainer / agent
  - Given: dependency blockers を持つ target issue
  - When: `./spec-dock/scripts/spec-dock deps check <target>` を実行する
  - Then: GitHub live state に基づいて readiness が判定される
  - 観測点: JSON / text output、stub issue gateway call count
- AC-004:
  - Actor: maintainer / agent
  - Given: active set 対象 issue と dependency graph がある
  - When: `./spec-dock/scripts/spec-dock active set <target>` を実行する
  - Then: GitHub live state に基づく deps guard が標準で実行される
  - 観測点: active set result / blocked message / stub issue gateway call count
- AC-005:
  - Actor: maintainer / agent
  - Given: `sync` / `deps check` / `active set`
  - When: `--github` を指定する
  - Then: 後方互換 flag として GitHub enabled のまま動作する
  - 観測点: CLI runtime test
- AC-006:
  - Actor: maintainer / agent
  - Given: `sync` / `deps check` / `active set`
  - When: `--github --no-github` を同時指定する
  - Then: argparse error で失敗する
  - 観測点: exit code / stderr
- AC-007:
  - Actor: maintainer / agent
  - Given: `new initiative` / `new epic` / `new issue`
  - When: `--no-github` を指定する
  - Then: 現行通り GitHub linkage mandatory の contract error で拒否される
  - 観測点: existing test preservation

## 例外・エッジケース
- EC-001:
  - 条件: default GitHub mode で `gh issue list` または repo-scoped `gh issue view` が失敗する
  - 期待: 現行通り `gh_fetch_failed` warning を出し、取得不能な GitHub-linked node は `unknown` / stale 相当になる
  - 観測点: sync / deps / active tests
- EC-002:
  - 条件: `--no-github` を指定し、usable cache が存在しない
  - 期待: `gh` を呼ばず、GitHub-linked node は `unknown` / stale 相当になる
  - 観測点: generated artifact / deps check output
- EC-003:
  - 条件: `--no-github` 指定時に cache が古い
  - 期待: 古い cache を明示的に選んだ結果として扱い、GitHub へ fallback fetch しない
  - 観測点: gh guard log が作成されないこと

## 入力→出力例
- EX-001:
  - Input: `./spec-dock/scripts/spec-dock sync`
  - Output: GitHub state fetch enabled; artifacts written
- EX-002:
  - Input: `./spec-dock/scripts/spec-dock sync --no-github`
  - Output: GitHub fetch disabled; cached status used
- EX-003:
  - Input: `./spec-dock/scripts/spec-dock deps check iss-00091 --github --no-github`
  - Output: argparse error

## 用語
- GitHub default:
  - flag なしで GitHub issue state を取得する CLI behavior。
- `--no-github`:
  - 状態取得系コマンドで GitHub 連携を明示的に無効化する opt-out flag。
- cache path:
  - `.agent/index-all.json`、次に `.agent/index.json` から issue status を読む既存 path。

## 未確定事項
- なし。
