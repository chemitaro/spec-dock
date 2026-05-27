---
種別: 要件定義書（Issue）
ID: "iss-00130"
タイトル: "Central Worktree Root Placement"
関連GitHub: ["#130"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-27"
親: ["epic-00107", "init-local-00002"]
---

# iss-00130 Central Worktree Root Placement — 要件定義（何を、なぜ行うか）

## 目的
- `spec-dock worktree create` が作成する linked worktree の配置先を、repo sibling container から環境変数で指定する central root へ変更する。
- Codex sandbox の writable root を product ごとに手動追加する運用を避け、全 product の spec-dock managed worktree を 1 つの許可済み root 配下に集約できるようにする。
- 既存の id / directory basename / branch naming / bootstrap behavior は維持し、placement contract だけを安全に置き換える。

## 背景・現状
- 現状の挙動:
  - `epic-00107` の既存契約では、worktree は Git main worktree の親 directory に `<repo-basename>-worktrees/` container を作り、その配下に `<repo-basename>-<id>` として作成される。
  - この repository では `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/...` のような sibling container が既に使われている。
  - `reference_worktree.md` と runtime tests も sibling placement を現行仕様として扱っている。
- 現状の課題:
  - Codex sandbox を有効にした環境では、sibling container が現在の project writable root の外になりやすい。
  - product ごとに Codex writable root を手動追加する運用は、設定漏れと human error の原因になる。
  - 通常の product checkout と linked worktree は lifecycle が異なる。linked worktree は短命の開発 surface であり、通常 checkout と同列の場所へ増え続けると管理しづらい。
- 代表的な問題の流れ:
  1. maintainer が `spec-dock worktree create` を実行する。
  2. command が repo sibling の `<repo-basename>-worktrees/` に linked worktree を作成する。
  3. Codex sandbox から見ると、その sibling path は project writable root 外になり、追加の手動許可が必要になる。
- 情報源:
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/issue/discussions/20260526t081258z-scratch-user-input-capture.md`
  - `spec-dock/active/issue/discussions/20260526t081259z-01-interview-requirement-interview.md`
  - `spec-dock/active/issue/discussions/20260526t081259z-research-existing-worktree-contract-research.md`
  - `spec-dock/active/issue/discussions/20260526t081356z-disc-central-root-placement-options.md`
  - `spec-dock/active/issue/discussions/20260526t082342z-research-shell-environment-setup-research.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `tests/cli_runtime/test_worktree.py`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock maintainer。
  - Codex sandbox を使いながら、複数 issue / branch を linked worktree で並行開発する operator。
- 代表シナリオ:
  - maintainer が `SPEC_DOCK_WORKTREE_ROOT=$HOME/workspace/worktrees` を設定した環境で `spec-dock worktree create` を実行し、central root 配下に dedicated worktree を作る。
  - maintainer が `spec-dock` 以外の product checkout でも同じ `SPEC_DOCK_WORKTREE_ROOT` を使い、product ごとの namespace 配下に worktree を集約する。
  - Codex sandbox 側では central root だけを writable root として許可し、project ごとの sibling worktree path を個別追加しない。

## スコープ
- 必須:
  - `spec-dock worktree create` の future placement を `SPEC_DOCK_WORKTREE_ROOT` based central root に変更する。
  - この issue は `epic-00107` の既存 sibling placement 契約を、future `worktree create` について明示的に supersede する。対象は Epic requirement の sibling container placement clauses と `reference_worktree.md` の user-facing placement contract である。
  - `SPEC_DOCK_WORKTREE_ROOT` は `worktree create` に必須とし、未設定・空文字・空白のみの場合は fatal error にする。
  - central root 配下の namespace は Git main worktree basename とする。この repository では `spec-dock` である。
  - worktree path は `$SPEC_DOCK_WORKTREE_ROOT/<namespace>/<repo-basename>-<id>` とする。
  - env var が設定済みで root / namespace directory が存在しない場合、command が必要な directory を作成できる。
  - `~` 展開後に絶対パスになる env var 値は許可する。
  - 相対パスは fatal error にする。
  - 通常 directory と directory を指す symlink は root として許可する。
  - file、directory 以外、壊れた symlink、作成不能な path は fatal error にする。
  - missing / invalid env var の error は、変数名、原因、絶対パスを使う設定例を含める。
  - 既存の id 生成、label validation、branch naming、collision retry、`make init` bootstrap semantics を維持する。
  - shipped docs と tests を新しい placement contract に合わせる。
  - この開発機では local setup evidence として、`.zshenv` に `SPEC_DOCK_WORKTREE_ROOT` export があり、`/Users/iwasawayuuta/workspace/worktrees` が root として利用可能であることを確認する。
- 禁止:
  - `SPEC_DOCK_WORKTREE_ROOT` が missing / blank の場合に旧 sibling placement へ fallback すること。
  - 既存 sibling worktree を自動移動・削除・migration すること。
  - この issue で namespace override 用の flag / config / env var を追加すること。
  - Codex app が `$CODEX_HOME/worktrees` 配下に作る short-lived worktree を spec-dock managed worktree と混在させること。
  - worktree list / remove / prune / cleanup command をこの issue の scope に含めること。
- 対象外:
  - 既存 sibling worktree の migration guide 実装。
  - central root 配下 namespace の owner metadata 管理。
  - 同 basename repository の collision を完全に防ぐ namespace 設計。
  - shell profile を自動編集する setup command。
  - Codex sandbox 設定そのものの自動変更。
  - local setup evidence を repo-managed product artifact として扱うこと。

## 境界
- 常に行う:
  - `worktree create` 実行時に `SPEC_DOCK_WORKTREE_ROOT` を確認する。
  - env var 値を `~` 展開し、absolute path contract を検証する。
  - Git main worktree basename から namespace と repo basename を導出する。
  - 作成予定 path / branch / Git worktree record の collision を既存方針どおり検出する。
  - 成功時は absolute worktree path、id、branch、bootstrap status を観測可能にする。
- 判断が必要:
  - 将来、同 basename repository が central root で衝突した場合に namespace override を追加するか。
  - 将来、central root 配下の worktree list / remove / prune を spec-dock command として追加するか。
- 行わない:
  - 旧 sibling placement を backward-compatible fallback として残す。
  - namespace directory に repository owner metadata を置く。
  - `.zshenv` / `.zprofile` / `.zshrc` を runtime command が変更する。

## 非交渉制約
- `SPEC_DOCK_WORKTREE_ROOT` missing / blank は worktree 作成成功として扱わない。
- Missing / blank env var 時は Git mutation、branch 作成、directory 作成、bootstrap を行わない。
- Central root は `$CODEX_HOME/worktrees` ではなく、operator が指定する spec-dock managed worktree root とする。
- Existing linked worktree の lifecycle を尊重し、自動移動・自動削除しない。
- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` とし、dogfooding workspace は検証・反映対象として扱う。
- Parent Epic の sibling placement 記述は、この issue の完了時に future behavior として残してはならない。親 Epic / shipped docs / dogfooding docs のどこに sibling placement が残る場合も、legacy boundary または historical context として明示する。

## 前提
- `epic-00107` で定義済みの `worktree create [LABEL]` command surface は維持する。
- `LABEL` の許可文字は lowercase letters、digits、hyphen のみであり、uppercase、underscore、dot、space、slash、shell metacharacters は拒否する。
- id 生成は label なしなら `wt1`, `wt2`, ...、label ありなら `<label>`, `<label>2`, ... を維持する。
- branch naming は `<current-branch>-<id>` を維持する。
- linked worktree から実行した場合も、namespace / repo basename は Git main worktree basenameを使い、branch prefix は実行元 checkout の current branch を使う。
- `make init` bootstrap は optional / non-fatal のまま維持する。
- この開発機では `SPEC_DOCK_WORKTREE_ROOT` の想定値は `/Users/iwasawayuuta/workspace/worktrees` である。
- `.zshenv` export は `export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"` のように既存値を尊重する形式を推奨する。

## 受け入れ条件
- AC-001: env var missing / blank の fatal failure
  - アクター:
    - maintainer
  - 前提:
    - Git repo 内の named branch checkout である。
    - `SPEC_DOCK_WORKTREE_ROOT` が未設定、空文字、または空白のみである。
  - 操作:
    - maintainer が `spec-dock worktree create` を実行する。
  - 期待結果:
    - command は fatal error で終了する。
    - error message は `SPEC_DOCK_WORKTREE_ROOT` が必須であることと設定例を示す。
    - 旧 sibling container、central root directory、worktree path、branch、bootstrap side effect は作成されない。
  - 観測点:
    - CLI runtime test。
    - filesystem / Git branch / Git worktree record assertion。

- AC-002: central root placement
  - アクター:
    - maintainer
  - 前提:
    - Git main worktree basename が `sample-repo` である。
    - current branch が `main` である。
    - `SPEC_DOCK_WORKTREE_ROOT` が `/tmp/worktrees` のような absolute path に設定されている。
  - 操作:
    - maintainer が label なしで `spec-dock worktree create` を実行する。
  - 期待結果:
    - command は `/tmp/worktrees/sample-repo/sample-repo-wt1` に linked worktree を作成する。
    - branch は `main-wt1` になる。
    - 旧 sibling container `/tmp/.../sample-repo-worktrees` は新規作成先として使われない。
  - 観測点:
    - CLI runtime test。
    - `git worktree list --porcelain` assertion。

- AC-003: env root / namespace directory auto creation
  - アクター:
    - maintainer
  - 前提:
    - `SPEC_DOCK_WORKTREE_ROOT` は absolute path に設定されている。
    - その root directory または namespace directory はまだ存在しない。
  - 操作:
    - maintainer が `spec-dock worktree create` を実行する。
  - 期待結果:
    - command は root / namespace directory を必要に応じて作成する。
    - 作成済み worktree は central root 配下に配置される。
  - 観測点:
    - filesystem assertion。
    - CLI runtime test。

- AC-004: path validation
  - アクター:
    - maintainer
  - 前提:
    - `SPEC_DOCK_WORKTREE_ROOT` に `~/workspace/worktrees`、absolute path、relative path、file path、壊れた symlink、directory symlink のいずれかが設定される。
  - 操作:
    - maintainer が `spec-dock worktree create` を実行する。
  - 期待結果:
    - `~` 展開後に absolute path になる値と directory symlink は許可される。
    - relative path、file path、壊れた symlink、directory として使えない path は fatal error になる。
    - invalid root の場合、Git mutation、branch 作成、directory 作成、bootstrap は行われない。
  - 観測点:
    - path validation tests。
    - filesystem / Git assertion。

- AC-005: existing naming and collision behavior is preserved
  - アクター:
    - maintainer
  - 前提:
    - `SPEC_DOCK_WORKTREE_ROOT` は valid absolute path に設定されている。
    - label なし、valid label あり、directory / branch / Git worktree record collision が発生する case がある。
  - 操作:
    - maintainer が `spec-dock worktree create [LABEL]` を実行する。
  - 期待結果:
    - id 生成は既存どおり `wt1`, `wt2`, ... または `<label>`, `<label>2`, ... になる。
    - branch は `<current-branch>-<id>` になる。
    - retryable collision は次候補へ進む。
    - non-retryable failure は作成成功として扱わない。
  - 観測点:
    - existing worktree tests の central root 対応後の regression。

- AC-006: linked worktree invocation normalization
  - アクター:
    - maintainer
  - 前提:
    - command が既存 linked worktree から実行される。
    - Git main worktree basename は `sample-repo` である。
    - 実行元 current branch は `main-outer` である。
    - `SPEC_DOCK_WORKTREE_ROOT` は valid absolute path に設定されている。
  - 操作:
    - maintainer が linked worktree から `spec-dock worktree create inner` を実行する。
  - 期待結果:
    - namespace / repo basename は Git main worktree basename `sample-repo` から導出される。
    - path は `$SPEC_DOCK_WORKTREE_ROOT/sample-repo/sample-repo-inner` になる。
    - branch は実行元 current branch を基点に `main-outer-inner` になる。
    - linked worktree basename 由来の nested namespace は作られない。
  - 観測点:
    - linked worktree CLI runtime test。

- AC-007: bootstrap behavior preservation
  - アクター:
    - maintainer
  - 前提:
    - `SPEC_DOCK_WORKTREE_ROOT` は valid absolute path に設定されている。
    - 作成先 worktree には `make init` success / failure / missing / detection failure の各 case がある。
  - 操作:
    - maintainer が `spec-dock worktree create` を実行する。
  - 期待結果:
    - `make init` success は `succeeded` として表示される。
    - `make init` missing は `skipped` として表示される。
    - `make init` failure / detection failure は warning として観測可能だが、worktree 作成成功を取り消さない。
    - placement はすべて central root 配下になる。
  - 観測点:
    - bootstrap CLI runtime tests。

- AC-008: docs and dogfooding parity
  - アクター:
    - maintainer
  - 前提:
    - provider-side docs / runtime / tests を更新する。
  - 操作:
    - maintainer が shipped docs、dogfooding docs、runtime tests、validation を確認する。
  - 期待結果:
    - `reference_worktree.md` は `SPEC_DOCK_WORKTREE_ROOT`、fatal missing env、central root layout、namespace rule、legacy sibling boundary、Codex app worktree boundary を説明する。
    - `epic-00107` の sibling placement 記述は、future `worktree create` の正本として残らず、central root contract または legacy context へ更新される。
    - provider-side source of truth と dogfooding workspace の relevant docs / runtime contract が一致する。
  - 観測点:
    - docs inspection。
    - parity test または update / validation evidence。

- AC-009: local setup evidence
  - アクター:
    - maintainer
  - 前提:
    - この開発機で `spec-dock worktree create` を実用する。
  - 操作:
    - maintainer が shell environment と central root directory を確認する。
  - 期待結果:
    - `SPEC_DOCK_WORKTREE_ROOT` が `/Users/iwasawayuuta/workspace/worktrees` または user-approved equivalent を指している。
    - `.zshenv` には既存 override を尊重する export がある。
    - root directory は存在するか、valid env var を使った `worktree create` により作成可能である。
    - `.zshenv` や user-local directory の状態は repo-managed product artifact として commit 対象にしない。
  - 観測点:
    - shell env inspection。
    - filesystem inspection。
    - report evidence。

## 例外・エッジケース
- EC-001: invalid label
  - 条件:
    - label に uppercase、underscore、dot、space、slash、shell metacharacter が含まれる。
  - 期待:
    - command は invalid label として fatal error になる。
    - env root / namespace / worktree / branch / bootstrap side effect は作成されない。
  - 観測点:
    - existing invalid label tests。

- EC-002: valid env var but root path creation fails
  - 条件:
    - `SPEC_DOCK_WORKTREE_ROOT` は absolute path だが、permission error、file conflict、broken symlink などで root / namespace を directory として使えない。
  - 期待:
    - command は fatal error になる。
    - 作成成功として扱わない。
    - error は対象 path と原因を追える情報を含む。
  - 観測点:
    - path failure tests。

- EC-003: namespace directory already exists
  - 条件:
    - `$SPEC_DOCK_WORKTREE_ROOT/<repo-basename>` が既に存在する。
  - 期待:
    - directory として使える場合、それ自体では fatal にしない。
    - 作成予定 worktree path / branch / Git worktree record が衝突する場合のみ既存 collision rule で扱う。
  - 観測点:
    - collision tests。

- EC-004: same basename repository collision
  - 条件:
    - 別 repository が同じ Git main worktree basename を持ち、同じ central namespace を使う。
  - 期待:
    - この issue では namespace owner metadata や override は導入しない。
    - 通常の path / branch / Git worktree record collision で検出できる範囲だけ扱う。
    - 追加の namespace 設計は future extension とする。
  - 観測点:
    - scope inspection。

- EC-005: existing sibling worktrees
  - 条件:
    - `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/...` のような既存 sibling worktree が残っている。
  - 期待:
    - command は既存 sibling worktree を移動・削除しない。
    - future `worktree create` は central root を使う。
  - 観測点:
    - docs inspection。
    - runtime does not migrate existing path。

## 入力→出力例
- EX-001: label なし
  - 入力:
    - `SPEC_DOCK_WORKTREE_ROOT=/Users/iwasawayuuta/workspace/worktrees`
    - main worktree: `/Users/iwasawayuuta/workspace/tools/spec-dock`
    - current branch: `main`
    - command: `./spec-dock/scripts/spec-dock worktree create`
  - 出力:
    - id: `wt1`
    - path: `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-wt1`
    - branch: `main-wt1`

- EX-002: label あり
  - 入力:
    - `SPEC_DOCK_WORKTREE_ROOT=/Users/iwasawayuuta/workspace/worktrees`
    - main worktree: `/Users/iwasawayuuta/workspace/tools/spec-dock`
    - current branch: `iss-00130-central-worktree-root-placement`
    - command: `./spec-dock/scripts/spec-dock worktree create central-root`
  - 出力:
    - id: `central-root`
    - path: `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-central-root`
    - branch: `iss-00130-central-worktree-root-placement-central-root`

- EX-003: missing env var
  - 入力:
    - `SPEC_DOCK_WORKTREE_ROOT` unset
    - command: `./spec-dock/scripts/spec-dock worktree create`
  - 出力:
    - fatal error:
      - `SPEC_DOCK_WORKTREE_ROOT` is required for `worktree create`
      - setup example uses an absolute path such as `export SPEC_DOCK_WORKTREE_ROOT="$HOME/workspace/worktrees"`
    - no worktree / branch / directory side effect

## 用語（ドメイン語彙）
- TERM-001: central root
  - `SPEC_DOCK_WORKTREE_ROOT` が指す、spec-dock managed linked worktree を集約する root directory。
- TERM-002: namespace
  - central root 直下の product / repository scope directory。この issue では Git main worktree basename を使う。
- TERM-003: repo basename
  - Git main worktree path の basename。worktree directory basename と namespace の導出元になる。
- TERM-004: spec-dock managed worktree
  - `spec-dock worktree create` が作成する、operator が手動管理する長命寄りの linked worktree。
- TERM-005: Codex app managed worktree
  - Codex app が `$CODEX_HOME/worktrees` 配下に作成する短命 worktree。この issue の管理対象ではない。
- TERM-006: sibling placement
  - 旧仕様の `<main-worktree-parent>/<repo-basename>-worktrees/<repo-basename>-<id>` 形式の配置。

## 未確定事項
- なし。
