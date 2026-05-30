---
種別: 要件定義書（Issue）
ID: "iss-00141"
タイトル: "Remove Local Only Node Creation Option Surface"
関連GitHub: ["#141"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["epic-00033", "init-local-00003"]
---

# iss-00141 Remove Local Only Node Creation Option Surface — 要件定義（何を、なぜ行うか）

## 目的
- `new initiative` / `new epic` / `new issue` の node creation surface から、local-only creation を示す `--no-github` を完全に削除する。
- GitHub mandatory node linkage の方針を、CLI help、parser、内部 request contract、tests、docs で一貫させる。
- `--no-github` を rejected compatibility path として残さず、node creation では unsupported option として扱う。

## 背景・現状
- 現状の挙動:
  - Parent epic `epic-00033` と accepted ADR `20260327t093000z-adr-github-mandatory-node-linkage.md` は、`initiative` / `epic` / `issue` の GitHub issue linkage mandatory と local-only / local fallback 廃止を決定済み。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py` は、`new initiative` / `new epic` / `new issue` に `--no-github` を argparse option として登録している。
  - 同 command handler は `--no-github` を dedicated contract error として reject している。
  - `application/create_node.py` / `application/contracts.py` には `github_mode="local_only"` と local-only planning branch が残っている。
  - docs / tests は `--no-github` を node creation の compatibility option として残す前提を持っている。
- 現状の課題:
  - `--no-github` が help / docs / tests / internal contract に残ることで、local-only creation が option surface としてまだ存在するように見える。
  - rejected path として残すだけでは、GitHub mandatory contract の UX と実装構造が一致しない。
  - future maintainer が `local_only` branch を復活可能な互換経路として誤読する risk がある。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock new issue --help` を実行する。
  2. help 上に `--no-github` が表示されることを確認する。
  3. `./spec-dock/scripts/spec-dock new issue --no-github --epic <epic-id> --title "..."` を実行する。
  4. parser が option を受け付け、handler-level の dedicated contract error を返すことを確認する。
- 観測点:
  - CLI:
    - `new initiative|epic|issue --help`
    - `new initiative|epic|issue --no-github ...`
    - `new ... --create-github-issue --no-github ...`
  - Code:
    - `commands/new.py` の argparse / args dataclass / handler branch
    - `application/contracts.py` の `CreateNodeRequest.github_mode`
    - `application/create_node.py` の GitHub mode resolution と planning branch
  - Docs:
    - provider docs / dogfooding docs / root README / installed skill text where node creation `--no-github` is mentioned
  - Tests:
    - `tests/cli_runtime/test_new.py`
    - `tests/cli_runtime/test_wrappers.py`
- 情報源:
  - `spec-dock/active/issue/discussions/20260529t153534z-disc-handoff-scratch.md`
  - `spec-dock/active/issue/discussions/20260530t081132z-research-local-only-node-creation-option-surface-research.md`
  - `spec-dock/active/issue/discussions/20260530t081243z-interview-node-creation-no-github-surface-policy.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/discussions/20260327t093000z-adr-github-mandatory-node-linkage.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_wrappers.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - spec-dock を使って initiative / epic / issue を作成する coding agent / maintainer。
  - spec-dock の shipped scaffold / docs / skills を読む future maintainer。
- 代表シナリオ:
  - maintainer が `new issue --help` を確認し、GitHub-backed creation と existing GitHub issue linkage だけを選択肢として認識する。
  - coding agent が node creation で `--no-github` を使おうとした場合、local-only creation の compatibility path ではなく unsupported option として扱う。
  - implementation maintainer が内部 contract を読んだとき、`local_only` node creation mode が残っていないことを確認できる。

## スコープ
- 必須:
  - `new initiative` / `new epic` / `new issue` の parser から `--no-github` option を削除する。
  - `new initiative` / `new epic` / `new issue --help` に `--no-github` が表示されないようにする。
  - explicit `new initiative|epic|issue --no-github ...` は parser-level unsupported option として失敗する。
  - `commands/new.py` の `no_github` args field、args factory plumbing、handler-level dedicated rejection branch、専用 helper など、node creation `--no-github` の内部ロジックを削除する。
  - `CreateNodeRequest.github_mode` と `create_node` mode resolution / planning から、node creation の `local_only` mode と local-only branch を整理する。
  - provider-side runtime と checked-in dogfooding runtime mirror の挙動を一致させる。
  - provider docs / dogfooding docs / root README / installed skill text / tests から、node creation `--no-github` compatibility option の説明と期待値を削除または置換する。
  - `--create-github-issue` と `--github-issue <n>` の既存 GitHub-backed creation / link-existing path は維持する。
- 禁止:
  - local-only initiative / epic / issue creation path を残さない。
  - `--no-github` を hidden compatibility option として残さない。
  - dedicated contract error を維持するためだけの `no_github` handler branch を残さない。
  - GitHub mandatory policy、canonical repo scope policy、cross-repo reject policy をこの issue で再設計しない。
- 対象外:
  - `sync --no-github` / `deps check --no-github` / `active set --no-github` など、GitHub live fetch を避ける cache/local state option。
  - `import` の `--allow-foreign-url` compatibility flag。
  - GitHub issue create / close / import / sync の behavior redesign。
  - multi-repo support、offline node creation support、local draft node support。

## 境界
- 常に行う:
  - node creation context と state cache context の `--no-github` を区別する。
  - `initiative` / `epic` / `issue` node creation は GitHub issue linkage mandatory として扱う。
  - docs / tests / runtime / dogfooding mirror を同じ contract に揃える。
- 判断が必要:
  - design phase で、`CreateNodeRequest.github_mode` を `None | "create" | "link_existing"` に狭めるか、nullable default の扱いも整理するかを既存 call site とテストから確定する。
  - legacy monolithic `app.py` に残る stale wording / dead code を今回の shipped runtime surface として扱うかを、design phase の code ownership analysis で確定する。
- 行わない:
  - `sync` / `deps` / `active` の `--no-github` を削除しない。
  - local-only node data の migration / cleanup を行わない。
  - parent epic / ADR の方針を変更しない。

## 非交渉制約
- `initiative` / `epic` / `issue` は GitHub issue mandatory。
- node creation に local-only / local fallback / hidden local-only compatibility option を残さない。
- provider-side source of truth は `src/spec_dock/assets/spec_dock/...`、dogfooding workspace は parity validation 対象として扱う。
- 変更は local-only node creation option surface とその内部 plumbing に限定する。
- `--no-github` という文字列の全削除を目的にしない。state/cache commands の supported option は維持する。

## 前提
- `epic-00033` の GitHub mandatory node linkage contract は既に accepted ADR で固定済み。
- `new initiative` / `new epic` / `new issue` の default は GitHub issue create であり、`--github-issue <n>` は existing current-repo issue への link path である。
- ユーザー回答により、Option A（parser-level removal）が採用済み。
- ユーザー回答により、入力 option だけでなく内部ロジック整理も scope に含める。

## 受け入れ条件
- AC-001:
  - アクター:
    - spec-dock maintainer。
  - 前提:
    - spec-dock runtime がこの issue の変更後状態である。
  - 操作:
    - `new initiative --help` / `new epic --help` / `new issue --help` を確認する。
  - 期待結果:
    - `--no-github` が node creation help に表示されない。
    - `--create-github-issue` と `--github-issue <n>` は引き続き表示される。
  - 観測点:
    - CLI help output。
- AC-002:
  - アクター:
    - coding agent。
  - 前提:
    - spec-dock runtime がこの issue の変更後状態である。
  - 操作:
    - `new initiative --no-github --title "..."` を実行する。
    - `new epic --no-github --initiative <id> --title "..."` を実行する。
    - `new issue --no-github --epic <id> --title "..."` を実行する。
  - 期待結果:
    - いずれも parser-level unsupported / unrecognized option として失敗する。
    - dedicated contract error `"'--no-github' is not supported for <kind>; GitHub linkage is mandatory."` は返らない。
    - GitHub CLI は呼び出されない。
  - 観測点:
    - CLI exit code / stderr。
- AC-003:
  - アクター:
    - implementation maintainer。
  - 前提:
    - implementation source and tests are inspected after change.
  - 操作:
    - node creation command / request / use-case code を確認する。
  - 期待結果:
    - `NewInitiativeArgs` / `NewEpicArgs` / `NewIssueArgs` に `no_github` field がない。
    - `commands/new.py` に node creation `--no-github` argument registration、args factory plumbing、handler branch、dedicated helper が残っていない。
    - `CreateNodeRequest.github_mode` は node creation local-only mode を受け取らない。
    - `create_node` planning に local-only node id allocation branch が残っていない、または node creation から到達しない dead compatibility path として残さない。
  - 観測点:
    - source inspection / targeted tests。
- AC-004:
  - アクター:
    - spec-dock maintainer。
  - 前提:
    - docs / skills / tests are inspected after change.
  - 操作:
    - provider docs、dogfooding docs、root README、installed skill text、tests を確認する。
  - 期待結果:
    - node creation `--no-github` を compatibility option として説明する文が残っていない。
    - node creation `--no-github` dedicated rejection を期待する tests が残っていない。
    - `sync` / `deps check` / `active set` の cache/local `--no-github` 説明と tests は維持されている。
  - 観測点:
    - docs diff / tests diff / targeted search。
- AC-005:
  - アクター:
    - spec-dock maintainer。
  - 前提:
    - provider runtime and checked-in dogfooding runtime mirror are both present.
  - 操作:
    - provider-side runtime と checked-in dogfooding runtime mirror を確認する。
  - 期待結果:
    - node creation `--no-github` removal が provider source and dogfooding mirror の両方に反映されている。
  - 観測点:
    - parity test / diff inspection。

## 例外・エッジケース
- EC-001:
  - 条件:
    - `new issue --create-github-issue --no-github --epic <id> --title "..."` が実行される。
  - 期待:
    - mutually exclusive error ではなく、`--no-github` が unsupported / unrecognized option として失敗する。
  - 観測点:
    - CLI stderr。
- EC-002:
  - 条件:
    - `sync --no-github` / `deps check --no-github` / `active set --no-github` が実行される。
  - 期待:
    - これらの state/cache command では `--no-github` が引き続き valid option として扱われる。
  - 観測点:
    - existing targeted tests / CLI help。
- EC-003:
  - 条件:
    - docs に `--no-github` という文字列が残る。
  - 期待:
    - 残存箇所が state/cache command の説明である場合は許容する。
    - node creation compatibility option / local-only creation path の説明である場合は不合格。
  - 観測点:
    - targeted `rg -- "--no-github|local-only"` inspection。

## 入力→出力例（必要時）
- EX-001:
  - 入力:
    - `./spec-dock/scripts/spec-dock new issue --help`
  - 出力:
    - `--create-github-issue` と `--github-issue` は表示される。
    - `--no-github` は表示されない。
- EX-002:
  - 入力:
    - `./spec-dock/scripts/spec-dock new issue --no-github --epic 123 --title "Example"`
  - 出力:
    - parser-level unsupported / unrecognized option error。

## 用語（ドメイン語彙）
- TERM-001:
  - node creation:
    - `new initiative` / `new epic` / `new issue` による initiative / epic / issue node の作成。
- TERM-002:
  - local-only creation:
    - GitHub issue linkage なしで initiative / epic / issue node を作成する経路。現行 contract では廃止済みであり、この issue では option surface と internal plumbing を削除する。
- TERM-003:
  - option surface:
    - CLI help、parser option、docs、tests、skills、internal request contract など、利用者または maintainer が option の存在を認識できる表面。
- TERM-004:
  - cache/local state `--no-github`:
    - `sync` / `deps check` / `active set` で GitHub live fetch を避けるための supported option。node creation local-only path ではない。

## 未確定事項
- なし:
  - `--no-github` の扱いは `20260530t081243z-interview-node-creation-no-github-surface-policy.md` で Option A 採用として回答済み。
