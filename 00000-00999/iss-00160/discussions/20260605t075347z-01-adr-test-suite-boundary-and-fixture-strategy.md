---
種別: ADR（Architecture Decision Record）
ID: "20260605t075347z-01-adr"
タイトル: "Test Suite Boundary And Fixture Strategy"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["iss-00160"]
authority: "accepted"
derived_from:
  - "20260605t045222z-research-test-runtime-measurement-analysis.md"
  - "20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md"
reflected_to: []
---

# 20260605t075347z-01-adr Test Suite Boundary And Fixture Strategy

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md`, `design.md`, `plan.md`
- ADR として残す理由:
  - `unit` と `integration` の境界を一般的な「local subprocess / filesystem / git を unit から除外する」分類ではなく、この repository の日常実行境界に合わせて定義する。
  - テスト directory layout と fixture 戦略は、多数の既存 test 移動・軽量化・runner contract に波及し、後から意味を取り違えると大きな churn になる。
  - large GitHub index fixture を routine default から外す一方で、外部実通信とは別の regression として残す tradeoff がある。

## 結論（Decision）

- `spec-dock` のテスト分類は、大きく次の 2 つに限定する。
  - `tests/unit/`
  - `tests/integration/`
- `tests/unit/` は、この PC 上で完結し、外部サービス実通信を行わないテストを置く。
  - CLI subprocess
  - local filesystem
  - tempdir
  - local git
  - stub 化した `gh`
  - fake port / fake gateway
  - これらは `unit` 側に含める。
- `tests/integration/` は、GitHub など外部サービスと実通信するテストを置く。
  - real `gh issue list/view/create`
  - `git fetch/pull/push/ls-remote`
  - 認証やネットワークを必要とするもの
  - これらは `integration` 側に置く。
- `tests/unit/` の内側は、production runtime の層と対応するように整理する。
  - `src/.../cli/` -> `tests/unit/cli/`
  - `src/.../commands/` -> `tests/unit/commands/`
  - `src/.../application/` -> `tests/unit/application/`
  - `src/.../domain/` -> `tests/unit/domain/`
  - `src/.../infra/` -> `tests/unit/infra/`
  - `src/.../presentation/` -> `tests/unit/presentation/`
- `tests/integration/` の内側は、実外部境界ごとに分ける。
  - `tests/integration/github/`
  - `tests/integration/git_remote/`
- 現在遅い test の多くは外部実通信ではなく、ローカル完結の重い unit fixture として扱う。
- fake `gh issue list` の default stub は 10,000 件を返さず、関連する数件だけ返す。
- `--gh-limit=10000` の検証は、10,000 件データ生成ではなく、`gh` に渡された argv の `--limit` 値を確認する。
- 大きな issue number の検証は、10,000 件生成ではなく、`number: 10000` の 1 件 fixture で確認する。
- missing / unknown / open / closed などの状態検証は、2〜3 件の最小 fixture で再現する。
- CLI subprocess を大量に起動するテストは、CLI contract 確認に絞る。
- business logic / application logic は、fake port / fake gateway を使って直接テストする。
- local git 操作は unit 側に置いてよいが、git を本当に検証したい adapter / CLI test だけに限定する。

## 背景（Context）

- `iss-00160` の測定では、`time python -m unittest discover` が `10:00.07 total` で完走し、`Ran 1035 tests in 599.706s` だった。
- file-level timing では、遅い test が古い CLI black-box 系に集中していた。
  - `tests/cli_runtime/test_deps.py`: `113.02s`
  - `tests/cli_runtime/test_validate.py`: `101.91s`
  - `tests/cli_runtime/test_delegated_authoring.py`: `85.50s`
  - `tests/test_init_update.py`: `60.03s`
  - `tests/cli_runtime/test_active.py`: `56.76s`
- 一方で、`tests/cli_runtime/test_runtime_*`、`tests/domain_runtime`、`tests/presentation_runtime` はほぼ sub-second だった。
- `main(["init"])` 単体は平均 `0.041s` であり、`init` 単体の処理時間は主因ではない。
- `init + _create_same_repo_linked_hierarchy()` は平均 `0.850s` であり、fixture と subprocess runtime command の反復が累積コストになっている。
- default 10,000 件 GitHub stub と 3 件 GitHub stub の A/B では、`hierarchy + sync` が平均 `1.018s` から `0.836s` へ短縮した。
- deep-consultant は、`post-mutation sync`、10,000 件 GitHub index stub、temp repo / subprocess runtime fixture の大量反復を主因候補として挙げた。

## 選択肢（Options considered）

- 選択肢 A: `unit` / `integration` を外部実通信の有無で切る。
  - 概要:
    - local subprocess / filesystem / tempdir / local git / stub `gh` は `unit` に含め、実 GitHub / real remote git / network / auth を `integration` に分ける。
  - 良い点:
    - 日常実行対象と外部依存 test の境界が明確になる。
    - 今回の遅さが外部通信ではなく local heavy fixture にあることと整合する。
    - fake `gh` や local git の重さを「integration だから仕方ない」と扱わず、unit fixture として軽量化できる。
  - 悪い点 / 制約:
    - 一般的な狭義の unit test より広い定義になる。
    - docs と runner contract でこの repository 固有の定義を明文化しないと誤解される。
  - 採用理由:
    - 実測上の主因と、ユーザーが求める日常実行境界に最も合う。
- 選択肢 B: CLI subprocess / filesystem / local git を `integration` に分類する。
  - 概要:
    - unit は pure domain / application tests のみに絞り、local IO を含むものを integration に送る。
  - 良い点:
    - 一般的な unit / integration terminology に近い。
  - 悪い点 / 制約:
    - 今回の遅い test の多くが integration 扱いになり、日常高速化の本題が曖昧になる。
    - fake `gh` 10,000 件 fixture を「integration 側の重さ」として温存しやすい。
  - 棄却理由:
    - `iss-00160` の目的は外部通信の分離だけでなく、ローカル完結 heavy fixture の軽量化であるため。
- 選択肢 C: 既存 layout のまま、遅い test だけ局所最適化する。
  - 概要:
    - `tests/cli_runtime` などの配置は変えず、fixture だけを小さくする。
  - 良い点:
    - diff が小さい。
    - import path 変更の churn が少ない。
  - 悪い点 / 制約:
    - production code との対応関係が見えにくいまま残る。
    - 将来また CLI black-box test に branch coverage が集まりやすい。
  - 棄却理由:
    - ユーザーが明示した目的は速度だけでなく、第三者が追いやすい test / production 対応関係を作ることでもある。

## 判断理由（Rationale）

- 測定では、遅い test は外部サービス通信ではなく、local temp repo、subprocess runtime、fake `gh`、sync、artifact write の反復に集中していた。
- `integration = 外部実通信あり` と定義すれば、network/auth が必要な test だけを明示的に分離できる。
- `unit = local 完結` と定義すれば、fake `gh` や local git を含む重い local fixture を routine suite の改善対象として扱える。
- `tests/unit/<layer>/` と production runtime layer を対応させることで、branch coverage を CLI black-box に集めず、domain/application/presentation/infra の適切な層で直接検証しやすくなる。
- large GitHub index の regression は必要な場合でも、全 test default ではなく専用 test に閉じ込める方が、意図とコストの対応が明確になる。

## 影響（Consequences）

- 良い影響（Positive）:
  - Unit と Integration の実行境界が明確になる。
  - 外部通信が必要な test だけを integration として明示実行できる。
  - Unit test を日常的に高速実行できる見込みが高くなる。
  - production code と test file の対応関係が見やすくなる。
  - 1 万件 fixture や重い CLI subprocess 繰り返しに依存しない test へ置き換えやすくなる。
- 悪い影響 / 将来負債（Negative / Debt）:
  - 大規模な test file move が発生する可能性がある。
  - `unit` の定義が repository 固有であるため、README / test docs / runner で説明しないと誤解される。
  - CLI subprocess smoke を削りすぎると parser / stdout / exit code / import path regression を見逃す。
  - 10,000 件 fixture を縮小すると large index regression を見逃す可能性がある。
- 影響範囲（コード/テスト/運用/データ）:
  - `tests/`
  - `tests/cli_runtime/harness.py`
  - test runner / README / contributor docs
  - runtime application / domain / infra / presentation tests
  - CI がある場合は unit / integration 実行 command
- 移行/ロールバック:
  - 移行は段階的に行う。
  - まず runner 境界と最小 docs を作り、次に最遅 file から移設 / 軽量化する。
  - full regression command は残し、移行中の rollback path として使う。
- 追加対応（Follow-ups / Epic / Issue / ADR）:
  - 日常 unit runtime target は `20260605t075347z-interview-unit-runtime-target-clarification.md` で確認する。
  - 実装計画では `test_deps.py`、`test_validate.py`、`test_delegated_authoring.py` を優先する。

## 参考（References）

- 関連仕様（requirement/design/plan/report）:
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/requirement.md`
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/design.md`
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/plan.md`
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/report.md`
- 元になった discussion docs（derived_from）:
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/discussions/20260605t045222z-research-test-runtime-measurement-analysis.md`
  - `spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00160-reduce-test-runtime-followup/discussions/20260605t045222z-01-research-deep-consultant-test-runtime-analysis.md`
- ユーザー決定:
  - 2026-06-05 の chat で、外部エージェントとの議論結果として test boundary / fixture strategy が共有された。
