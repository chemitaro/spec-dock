---
種別: 要件定義書（Issue）
ID: "iss-00096"
タイトル: "Add self update command"
関連GitHub: ["#96"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-15"
親: ["epic-00054", "init-local-00002"]
---

# iss-00096 Add self update command — 要件定義（WHAT / WHY）

## 目的
- repo-local runtime command `./spec-dock/scripts/spec-dock update` を追加し、managed repo 内の spec-dock workspace を upstream GitHub package から更新できるようにする。
- 利用者が `uvx` の長い upstream 指定を毎回手入力せず、spec-dock 自身の command surface から self-update を実行できる状態にする。
- uvx cache による stale package / stale scaffold の混入を避けるため、runtime から実行する update は no-cache 契約を必須にする。

## 背景・現状
- 現状の挙動:
  - installer CLI は `uvx --from git+https://github.com/chemitaro/spec-dock spec-dock update [path]` で managed files / docs / templates / scripts / skills を更新できる。
  - repo-local runtime script `./spec-dock/scripts/spec-dock` は daily workflow command（`new` / `issue start` / `sync` / `validate` など）を提供するが、top-level `update` command は持っていない。
  - README は uvx cache が stale package を使う場合の workaround として `uvx --no-cache --from ... spec-dock init` を案内している。
- 現状の課題:
  - managed repo 利用者は update のたびに upstream repository URL と `uvx` invocation を覚える必要がある。
  - runtime command surface から見ると、spec-dock 自身を更新する導線だけが外部手順になっている。
  - uvx cache が使われると、更新したつもりでも古い package / scaffold が使われ、dogfooding や配布確認で混乱しやすい。
- 再現手順（現状確認）:
  1. managed repo で `./spec-dock/scripts/spec-dock update --help` を実行する。
  2. runtime parser に `update` subcommand がなく、installer update を呼ぶ repo-local 導線がないことを確認する。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock update --help`
    - `./spec-dock/scripts/spec-dock update [path]`
  - subprocess:
    - `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` が実行されること。
  - docs:
    - README / shipped docs が repo-local update command と no-cache 前提を説明していること。
  - tests:
    - runtime CLI tests が parser help、default path、explicit path、subprocess args、failure propagation を確認すること。
- 情報源:
  - `src/spec_dock/cli.py`: installer `update` は optional `path` を持ち、target の `spec-dock/` 存在を要求してから managed assets を force refresh する。
  - `README.md`: upstream uvx invocation と uvx cache workaround を説明している。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`: runtime top-level command に `update` が未登録。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`: runtime command registry に update command が未登録。
  - `spec-dock/active/epic/requirement.md` / `design.md`: command lifecycle expansion の一部として repo-local self-update command を含むように upstream scope を明示。
  - `spec-dock/active/issue/discussions/20260514t154002z-disc-workflow-scoped-delegation-consent.md`: reviewer gate と delegation consent の再発防止方針。

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - spec-dock を dogfooding する maintainer。
  - spec-dock を managed repo に導入済みで、repo-local command から scaffold / docs / scripts / skills を更新したい利用者。
- 代表シナリオ:
  - maintainer が managed repo の root で `./spec-dock/scripts/spec-dock update` を実行し、current directory の `spec-dock/` managed assets を upstream から更新する。
  - maintainer が別 workspace を明示して `./spec-dock/scripts/spec-dock update /path/to/project` を実行し、その target project の managed assets を更新する。
  - uvx cache が stale な可能性がある環境でも、runtime update は常に `--no-cache` を付けるため、upstream GitHub repository から最新 package resolution を試みる。

## スコープ
- 必須:
  - repo-local runtime command `./spec-dock/scripts/spec-dock update` を top-level command として追加する。
  - runtime update は内部で `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update <target>` を実行する。
  - target path は省略時 `.` とし、明示 path を指定できる。
  - runtime update は installer 側の existing `spec-dock update [path]` interface に合わせ、`init --force` とは混同しない。
  - uvx subprocess の stdout / stderr / exit code を operator が追える形で CLI output と exit status に反映する。
  - docs / shipped docs / tests を更新し、provider-side assets と dogfooding mirror の両方で command surface を確認できるようにする。
- 禁止:
  - `init --force` の destructive overwrite semantics を runtime update の user-facing option として追加しない。
  - uvx cache を使う self-update path を標準経路にしない。
  - subprocess failure、permission failure、network failure、uvx missing を成功扱いにしない。
  - arbitrary package source や arbitrary executable を runtime command の通常 option として許可しない。
  - local `spec-dock/initiatives/**` の user-authored specs を update 対象として削除・移行しない。
- 対象外:
  - installer `spec-dock update` 自体の managed asset sync semantics 変更。
  - legacy `.spec-dock` workspace の自動 migration。
  - GitHub issue lifecycle / close / delete command の追加変更。
  - uv / uvx のインストール支援。
  - package version comparison や update availability check。
  - repo-wide runtime state schema 追加。

## 境界
- 常に行う:
  - upstream source は `git+https://github.com/chemitaro/spec-dock` に固定する。
  - `uvx --no-cache` を使用して cache を避ける。
  - target path は runtime invocation の current working directory を基準に解決される。
  - update subprocess の結果を隠さず、失敗時に operator が原因を追える情報を残す。
- 判断が必要:
  - docs で `uvx --no-cache` の理由をどこまで詳述するか。
  - runtime command の implementation layer を `commands` / `application` / `infra` のどこまで分けるか。
- 行わない:
  - target repo 以外への update scope expansion。
  - cache directory の削除や global uv cache clean。
  - external publishing、GitHub comment、PR 作成、push。
  - user-authored issue / epic / initiative docs の自動 rewrite。

## 非交渉制約
- Self-update は cache 回避のため `uvx --no-cache` を必ず使う。
- Runtime command は upstream GitHub package を source of truth とし、ローカル checkout や editable install を暗黙利用しない。
- Runtime update は installer update の wrapper であり、installer update の WHAT を拡張しない。
- Failure は fail-closed に扱い、subprocess exit code を runtime exit code へ反映する。
- Secret / credential / private browser session を要求しない。

## 前提
- `uvx` が実行環境に存在する場合に self-update は実行可能である。
- target project は current `spec-dock/` workspace を持つ managed repo である。
- installer `spec-dock update [path]` は managed files / docs / templates / scripts / skills を更新する既存能力として維持される。
- GitHub repository `chemitaro/spec-dock` が upstream package source である。

## 受け入れ条件
- AC-001:
  - アクター: maintainer
  - 前提: managed repo に `./spec-dock/scripts/spec-dock` が存在する
  - 操作: `./spec-dock/scripts/spec-dock update --help` を実行する
  - 期待結果: runtime top-level `update` command の help が表示され、upstream GitHub repo と no-cache update path が分かる
  - 観測点: CLI stdout / stderr、runtime CLI test
- AC-002:
  - アクター: maintainer
  - 前提: managed repo root で runtime update を実行する
  - 操作: `./spec-dock/scripts/spec-dock update` を実行する
  - 期待結果: subprocess args が `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update .` と同等の target を含む
  - 観測点: subprocess stub を使った runtime CLI test、exit code
- AC-003:
  - アクター: maintainer
  - 前提: 別 target path を更新したい
  - 操作: `./spec-dock/scripts/spec-dock update /path/to/project` を実行する
  - 期待結果: explicit target path が installer `spec-dock update <target>` に渡される
  - 観測点: subprocess stub を使った runtime CLI test、captured args
- AC-004:
  - アクター: maintainer
  - 前提: uvx / network / permission / installer update のいずれかが失敗する
  - 操作: `./spec-dock/scripts/spec-dock update` を実行する
  - 期待結果: runtime command は失敗を成功扱いせず、subprocess exit code と stdout / stderr を operator が追える形で返す
  - 観測点: failure propagation test、CLI output、exit code
- AC-005:
  - アクター: maintainer / reviewer
  - 前提: README / shipped docs / runtime help を確認する
  - 操作: self-update command の説明を読む
  - 期待結果: repo-local update command、uvx no-cache、upstream GitHub source、target path default が一貫して説明されている
  - 観測点: docs diff、docs parity / mirror check、spec-reviewer

## 例外・エッジケース
- EC-001:
  - 条件: `uvx` executable が PATH に存在しない
  - 期待: runtime update は失敗し、`uvx` を実行できないことが分かる error / stderr を返す
  - 観測点: subprocess failure test
- EC-002:
  - 条件: target path に `spec-dock/` が存在しない
  - 期待: installer update の failure を隠さず伝播し、runtime 側で成功扱いしない
  - 観測点: failure propagation test
- EC-003:
  - 条件: uvx cache に stale package が存在しうる
  - 期待: runtime update subprocess args に `--no-cache` が含まれ、shared cache を標準経路で使わない
  - 観測点: subprocess args assertion
- EC-004:
  - 条件: user が `./spec-dock/scripts/spec-dock update --force` を指定する
  - 期待: installer update interface に存在しない option は runtime 側でも成功扱いしない。`init --force` と update を混同しない
  - 観測点: CLI parser / help test
- EC-005:
  - 条件: subprocess が stdout と stderr の両方へ出力して non-zero exit する
  - 期待: runtime command は両方の出力を operator が確認できる形で保持し、exit code を non-zero にする
  - 観測点: failure propagation test

## 入力→出力例（必要時）
- EX-001:
  - 入力: `./spec-dock/scripts/spec-dock update`
  - 出力: `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update .` が実行され、成功時は installer update の成功結果が確認できる
- EX-002:
  - 入力: `./spec-dock/scripts/spec-dock update ../target-project`
  - 出力: `uvx --no-cache --from git+https://github.com/chemitaro/spec-dock spec-dock update ../target-project` が実行される

## 用語（ドメイン語彙）
- TERM-001:
  - runtime command:
    - managed repo に shipped される `./spec-dock/scripts/spec-dock` の command surface。
- TERM-002:
  - installer update:
    - Python package entrypoint `spec-dock update [path]` が managed assets を更新する既存能力。
- TERM-003:
  - self-update:
    - runtime command が upstream package を `uvx` で起動し、自分が属する managed workspace を更新する導線。
- TERM-004:
  - no-cache:
    - `uvx --no-cache` により shared uv cache を使わず、stale package 混入を避ける実行契約。

## 未確定事項 / 設計へ送る論点
- Requirement gate を block する未確定事項:
  - なし。
- DQ-001:
  - 論点: runtime update は installer update 以外の additional option を持つべきか。
  - 選択肢:
    - A:
      - installer update の current interface に合わせ、optional `path` のみにする。
    - B:
      - runtime 固有の `--from` / `--cache-dir` / `--force` などを追加する。
  - 推奨案:
    - A。self-update は upstream / no-cache を標準契約に固定する方が安全で、arbitrary source や init force semantics の混入を避けられる。
  - design への影響範囲:
    - CLI UX、help、tests、security boundary
- DQ-002:
  - 論点: target path を runtime 側で absolute に正規化して渡すか、user input 表現のまま installer に渡すか。
  - 選択肢:
    - A:
      - Runtime 側で current working directory 基準に absolute path へ正規化して渡す。
    - B:
      - User input 表現を保ったまま installer に渡し、installer 側の既存解決に委ねる。
  - 推奨案:
    - A。subprocess evidence と failure diagnosis が安定し、runtime invocation cwd に依存する曖昧さを減らせる。
  - design への影響範囲:
    - subprocess args test、CLI output、path display
