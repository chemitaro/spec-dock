---
種別: 要件定義書（Issue）
ID: "iss-00160"
タイトル: "Reduce Test Runtime Followup"
関連GitHub: ["#160"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00080", "init-00079"]
---

# iss-00160 Reduce Test Runtime Followup — 要件定義（何を、なぜ行うか）

## 目的
- `spec-dock` の日常的なテスト feedback loop を短縮する。
- ローカル完結テストと外部サービス実通信テストの境界を明確にし、普段実行する `tests/unit/` を 120 秒以内で完了できる状態にする。
- 重い local fixture と CLI subprocess 反復に依存した coverage を、意図が明確で軽量な test structure へ移す。

## 背景・現状
- 現状の挙動:
  - `python -m unittest discover` は `Ran 1035 tests in 599.706s`、shell time `10:00.07 total` だった。
  - 同一実行で `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` が 1 failure になったが、失敗内容は dogfooding `.meta.json` snapshot divergence であり、速度問題とは別論点である。
- 現状の課題:
  - 遅い test は外部サービス実通信ではなく、local fixture / temp repo / subprocess を多用する Unit 相当 test に集中している。
  - top slow files は `tests/cli_runtime/test_deps.py` 113.02s、`tests/cli_runtime/test_validate.py` 101.91s、`tests/cli_runtime/test_delegated_authoring.py` 85.50s、`tests/test_init_update.py` 60.03s、`tests/cli_runtime/test_active.py` 56.76s だった。
  - `tests/cli_runtime/harness.py` の default fake `gh issue list` は 1..10000 の issue JSON を返すため、多くの local tests が大きな index を繰り返し生成している。
  - `_create_same_repo_linked_hierarchy()` は複数 test file で合計 100 回以上使われ、`main(["init"])`、node 作成、post mutation sync を繰り返している。
  - `test_delegated_authoring.py` では `_make_target_repo_with_scope()` の call site が 49 あり、temp workspace 初期化と CLI contract 確認の反復が重い。
- 再現手順:
  1. repository root で `python -m unittest discover` を実行する。
  2. shell time と unittest の reported runtime を記録する。
  3. file-level timing で slow files と fixture 利用箇所を確認する。
- 観測点:
  - CLI:
    - unittest output、shell `time`、file-level timing。
  - code:
    - `tests/cli_runtime/harness.py` の fake `gh` default behavior。
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` の runtime layer 構造。
  - docs:
    - `20260605t045222z-research-test-runtime-measurement-analysis.md`
    - `20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md`
    - `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`
    - `20260605t075347z-interview-unit-runtime-target-clarification.md`
- 情報源:
  - Local measurement research。
  - Deep consultant analysis。
  - User-shared external-agent discussion。
  - ADR: Test Suite Boundary And Fixture Strategy。
  - User answer: Option B。

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `spec-dock` maintainer。
  - `spec-dock` runtime / shipped scaffold を変更する実装者。
- 代表シナリオ:
  - 実装者がローカルで `tests/unit/` を日常的に実行し、外部認証やネットワークなしに短時間で feedback を得る。
  - 外部 GitHub / remote git を使う検証は `tests/integration/` として明示的に実行する。
  - 第三者が test path を見て、どの production layer / external boundary を検証しているか追える。

## スコープ
- 必須:
  - Test suite を `tests/unit/` と `tests/integration/` の 2 分類に整理する。
  - `unit` はこの PC 上で完結し、外部サービス通信を行わない test と定義する。
  - `unit` には CLI subprocess、local filesystem、tempdir、local git、stub 化した `gh` を含める。
  - `integration` は GitHub など外部サービスと実通信する test と定義する。
  - `integration` には real `gh issue list/view/create`、`git fetch/pull/push/ls-remote`、認証やネットワークが必要な test を置く。
  - `tests/unit/` 配下は production runtime layer に対応する `cli/`、`commands/`、`application/`、`domain/`、`infra/`、`presentation/` に整理する。
  - `tests/integration/` 配下は対象 external boundary に対応する `github/` と `git_remote/` に整理する。
  - default fake `gh` stub は 1 万件を返さず、test intent に必要な数件だけを返す。
  - `--gh-limit=10000` の検証は 1 万件 data generation ではなく、`gh` に渡された argv の `--limit` 値確認で行う。
  - 大きな issue 番号の検証は 1 万件生成ではなく `number: 10000` の最小 fixture で行う。
  - missing / unknown / open / closed などの状態検証は 2〜3件の最小 fixture で再現する。
  - CLI subprocess を大量起動する test は CLI contract smoke に絞り、business logic / application logic は fake port / fake gateway を使って直接検証する。
  - local git 操作は Unit 側に置けるが、git を本当に検証したい adapter / CLI smoke に限定する。
  - 日常実行 command として `tests/unit/` を実行でき、その local measurement が 120 秒以内で完了する。
  - full regression fallback command を残し、遅いまたは integration を含む検証を明示実行できる。
- 禁止:
  - Production behavior を test 高速化だけのために変えること。
  - `tests/unit/` に外部 credential、network availability、real GitHub state、remote git state を要求すること。
  - 大規模 index / large issue number の regression coverage を完全に消すこと。
  - parser、stdout/stderr、exit code、module import path など CLI contract smoke を削除すること。
  - unrelated refactor、format churn、runtime architecture 変更を混ぜること。
- 対象外:
  - CI workflow 全体の再設計。
  - performance benchmark framework の新設。
  - 速度問題と無関係な dogfooding `.meta.json` snapshot divergence の修正。
  - 実 GitHub / remote git に対する新規 E2E シナリオの網羅追加。

## 境界
- 常に行う:
  - Test path と production layer / external boundary の対応を明確にする。
  - Unit command は外部通信なしで実行できることを確認する。
  - 速度改善は測定値で記録する。
  - 既存 coverage の意図を保ったまま fixture / execution path を軽量化する。
- 判断が必要:
  - 既存 CLI black-box test をどこまで lower-layer direct test へ移すか。
  - Local git を adapter smoke として残す範囲。
  - Full regression fallback の failure が既知 snapshot divergence のみか、今回の変更由来かの切り分け。
- 行わない:
  - Unit / integration 以外の third category を追加する。
  - Real external service test を default unit run に含める。
  - Test speed のために runtime command contract を狭める。

## 非交渉制約
- `tests/unit/` は外部サービス実通信を行わない。
- `tests/unit/` の local measurement target は 120 秒以内とする。
- `tests/integration/` は明示実行される opt-in suite とする。
- 1 万件 issue fixture は routine unit path の default にしない。
- Test reorganization は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の layered architecture と対応させる。

## 前提
- 現 repository の test framework は `unittest` である。
- Unit の定義はこの repository の開発運用上の定義であり、local subprocess / local git / tempdir を含む。
- Runtime source of truth は provider-side `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` である。
- `spec-dock/` は dogfooding workspace であり、実装 source of truth ではない。
- 速度目標は今回測定した local environment を基準にした acceptance threshold である。CI や別 machine では絶対秒数が変動しうる。

## 受け入れ条件
- AC-001:
  - アクター:
    - `spec-dock` maintainer。
  - 前提:
    - Repository checkout があり、外部 credential / network を使わない。
  - 操作:
    - `tests/unit/` と `tests/integration/` の分類、directory、実行 command を確認する。
  - 期待結果:
    - Unit / integration の境界が ADR と一致し、`tests/unit/{cli,commands,application,domain,infra,presentation}` と `tests/integration/{github,git_remote}` に整理されている。
  - 観測点:
    - Directory layout、test discovery command、関連 docs / report evidence。
- AC-002:
  - アクター:
    - `spec-dock` maintainer。
  - 前提:
    - Unit suite が外部通信なしで実行できる。
  - 操作:
    - Unit suite command を local で実行し、shell time と unittest output を記録する。
  - 期待結果:
    - Unit suite が 120 秒以内に完了する。
  - 観測点:
    - `time` output、unittest result、report evidence。
- AC-003:
  - アクター:
    - 実装者。
  - 前提:
    - fake `gh` harness を使う tests が存在する。
  - 操作:
    - default fake `gh issue list`、`--gh-limit=10000` contract、large issue number、state variations の tests を確認する。
  - 期待結果:
    - Default fixture は必要最小件数で、`--limit 10000` は argv assertion、large number は `number: 10000` の最小 fixture、状態 variation は 2〜3件 fixture で検証されている。
  - 観測点:
    - Harness implementation、test assertions、targeted test results。
- AC-004:
  - アクター:
    - 実装者。
  - 前提:
    - 既存の slow CLI runtime tests がある。
  - 操作:
    - deps / validate / delegated authoring / active / sync / new などの重い branch coverage の配置を確認する。
  - 期待結果:
    - CLI subprocess tests は command contract smoke を中心に残り、business / application / domain logic は fake port / fake gateway で直接検証されている。
  - 観測点:
    - Test file placement、direct tests、CLI smoke tests、runtime measurement。
- AC-005:
  - アクター:
    - `spec-dock` maintainer。
  - 前提:
    - Unit suite と integration suite が分離されている。
  - 操作:
    - Full regression fallback command を確認する。
  - 期待結果:
    - Full regression を実行できる command が残り、unit より遅い検証や opt-in integration 検証の位置づけが明確である。
  - 観測点:
    - Existing or updated test commands、report evidence。

## 例外・エッジケース
- EC-001:
  - 条件:
    - Test が real GitHub API、real `gh issue list/view/create`、remote git、認証、network を要求する。
  - 期待:
    - `tests/unit/` から除外され、`tests/integration/` の明示実行対象になる。
  - 観測点:
    - Directory placement、skip / opt-in behavior、test command。
- EC-002:
  - 条件:
    - Large index behavior または large issue number behavior の regression coverage が必要。
  - 期待:
    - Routine unit path で 1 万件 JSON を生成せず、argv contract または `number: 10000` の最小 fixture で検証する。
  - 観測点:
    - Test fixture、fake `gh` invocation capture、targeted test output。
- EC-003:
  - 条件:
    - Local git を使う adapter / CLI smoke がある。
  - 期待:
    - 外部 remote 通信をしない deterministic local git test は Unit 側に残せる。
  - 観測点:
    - Test path、command under test、network-free evidence。
- EC-004:
  - 条件:
    - Final full regression fallback が既知の dogfooding snapshot divergence で失敗する。
  - 期待:
    - 速度改善 issue の達成とは分けて report に記録し、今回の変更由来 failure と混同しない。
  - 観測点:
    - Failure message、changed files、targeted unit result。

## 入力→出力例
- EX-001:
  - 入力:
    - `python -m unittest discover -s tests/unit`
  - 出力:
    - External credential / network なしで 120 秒以内に完了する unittest result。
- EX-002:
  - 入力:
    - fake `gh` harness 経由で `--gh-limit=10000` を指定する command。
  - 出力:
    - 1 万件 issue JSON ではなく、captured argv に `--limit 10000` が含まれることを assertion する。

## 用語（ドメイン語彙）
- TERM-001:
  - `unit`: この PC 上で完結し、外部サービス通信を行わない test。CLI subprocess、local filesystem、tempdir、local git、stub 化した `gh` を含む。
- TERM-002:
  - `integration`: GitHub など外部サービスと実通信する test。real `gh issue list/view/create`、`git fetch/pull/push/ls-remote`、認証、network を必要とするものを含む。
- TERM-003:
  - `CLI contract smoke`: Parser、argument wiring、exit code、stdout/stderr、module import path など、CLI surface の代表的 contract を確認する軽量 test。
- TERM-004:
  - `fake gh`: Unit tests で外部 GitHub 通信の代わりに使う deterministic stub / fixture。
- TERM-005:
  - `full regression fallback`: Unit suite より広い範囲を実行する既存または更新後の full test command。

## 未確定事項
- なし。
