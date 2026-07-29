---
種別: research
ID: "20260728t015759z-research"
タイトル: "Unit Test And Provider CI Runtime Investigation"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["iss-00342"]
関連:
  - "iss-00160"
  - "iss-00167"
  - "20260605t075347z-01-adr"
  - "https://github.com/chemitaro/spec-dock/actions/runs/29708758044"
  - "https://github.com/chemitaro/spec-dock/actions/runs/30278654717"
  - "oracle:specdock-test-ci-performanc-review"
authority: "synthesized"
derived_from:
  - "iss-00160-reduce-test-runtime-followup/requirement.md"
  - "iss-00160-reduce-test-runtime-followup/design.md"
  - "iss-00160-reduce-test-runtime-followup/plan.md"
  - "iss-00160-reduce-test-runtime-followup/report.md"
  - "iss-00160-reduce-test-runtime-followup/discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md"
  - "iss-00167-migrate-tests-to-pytest/requirement.md"
  - "iss-00167-migrate-tests-to-pytest/design.md"
  - "iss-00167-migrate-tests-to-pytest/report.md"
  - "github-actions:29708758044"
  - "github-actions:30278654717"
  - "oracle:specdock-test-ci-performanc-review (advisory; not adopted)"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260728t015759z-research Unit Test And Provider CI Runtime Investigation

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00342` の対象を、現在の Provider CI latency と、ローカル完結の `tests/unit` / `tests/cli_runtime` の runtime 増大に限定して、再現可能な観測値と既存の境界決定を整理する。
- 実装・workflow の変更前に、どの反復操作と CI topology が主要な待ち時間を作っているか、また性能改善が既存の test boundary / coverage intent を損なわないための制約を明らかにする。
- 本 artifact は判断候補の根拠であり、性能目標、CI merge gate、実装方式を採用または達成したことを宣言しない。

## sources / 調査方法 (必須)
- 参照先:
  - 現在の checkout: `3ee6d9047506a40b938407ecfffbb341a3ca76af`（`origin/main` と一致）。active node は未設定。
  - 現行 workflow: `.github/workflows/provider-ci.yml`、`.github/workflows/ci.yml`。
  - 現行 test source: `tests/cli_runtime/harness.py`、`tests/unit/infra/test_init_update.py`。
  - 先例: `iss-00160` の requirement / design / plan / report、および accepted ADR `20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`。
  - pytest 移行時の Provider CI full-suite 選択: `iss-00167` の requirement / design / report。
  - GitHub Actions: [run 29708758044](https://github.com/chemitaro/spec-dock/actions/runs/29708758044)、[run 30278654717](https://github.com/chemitaro/spec-dock/actions/runs/30278654717)。
  - Oracle ChatGPT Use: `specdock-test-ci-performanc-review`（browser Pro selection を確認、回答は advisory / not adopted、transcript SHA-256 prefix `ab592a24bd21`）。
- 検証手順:
  - `uv run pytest --collect-only` で full collection を確認し、`uv run pytest tests/unit --durations=100 -q`、`uv run pytest tests/unit --ignore=tests/unit/infra/test_init_update.py -q`、`uv run pytest tests/cli_runtime --durations=100 -q` を実行した。
  - `--durations=100` の上位事例と source を照合し、遅延が test 名だけでは説明できない場合は fixture、subprocess、sleep の実装を読んだ。
  - workflow YAML と GitHub run の step / elapsed を照合した。直近 100 件の Provider CI run は duration と同一 SHA の push + pull_request 重複を集計した。
- 実験条件:
  - Python / dependency / host は当該 checkout の `uv run pytest` 実行環境であり、単発計測値は warmup を伴う分布測定ではない。
  - 実行中に変更は加えていない。network / GitHub branch-protection contract はこの調査では完全には取得できていない。

## facts / 観測できた事実 (必須)
- collection と局所実行:
  - full collection は 2,696 tests、`tests/unit` は 1,209 tests、`tests/cli_runtime` は 1,269 tests、test source は約 118,565 行だった。
  - `uv run pytest tests/unit --durations=100 -q` は 1 failed、1,207 passed、1 skipped、380.19s だった。失敗した `test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state` は expected polls `2` に対して observed `1` であり、実時間依存の flaky evidence である。
  - 同コマンドから `tests/unit/infra/test_init_update.py` を除外すると 655 passed、1 skipped、5.45s だった。全 unit elapsed の約 98% は同ファイルに集中している。
  - `test_init_update.py` は 39,918 行、534 test methods。上位 duration には dogfooding deps mutation 14.19s、PR observation timeout 13.24s、slow snapshot quiet wait 11.48s、wheel preflight 6.95s が含まれる。
  - `uv run pytest tests/cli_runtime --durations=100 -q` は 1,194 passed、75 skipped、2 warnings、1,228.31s（20:28）だった。最長は malformed discussion validate 57.67s、次点は required meta identity 10.55s で、その後にも 2〜5.5s 級の事例が多数ある。
- source:
  - `CliRuntimeHarness._create_same_repo_linked_hierarchy()` は real local git 初期化 / 設定の後、initiative、epic、issue の 3 runtime subprocess を実行する。
  - `_run_runtime()` と `_run_runtime_capture()` は、それぞれ runtime script を `sys.executable` の subprocess として起動する。
  - source-level の静的出現数は `init` call 425、hierarchy helper call 166、runtime / capture call 1,118 だった。これは動的な実行回数ではない。
  - `test_init_update.py` の fake snapshot / observation script には `time.sleep(...)` があり、poll delay、hang、quiet wait などを実時間で待つテストが存在する。
- Provider CI:
  - `.github/workflows/provider-ci.yml` は `push` と `pull_request` の双方で単一 `provider-tests` job を起動し、checkout、Python setup、pip による uv install、`make lint`、`uv run pytest` を順に実行する。concurrency / cancellation 設定はない。
  - `.github/workflows/ci.yml` は runtime script exists、local sync、validate を行う CI で、observed duration は 17〜33s 程度であり long pole ではない。Provider CI の uv install は 2〜5s、static analysis は 11〜12s 程度だった。
  - run 29708758044 は success、pytest 37m31s、`2620 passed, 76 skipped`、2,249.64s。run 30278654717 は 37m29s 後に failed、dogfooding snapshot failures 2 件、`2 failed, 2618 passed, 76 skipped`、2,247.80s だった。
  - 直近 100 件の Provider CI では 61 run が 10 分超で、最小 26.0m、中央値 38.1m、最大 40.9m。push + pull_request が同一 SHA で完走した group は 9 件あり、sample 内の余分な compute は約 318 分だった。
- 既存決定:
  - `iss-00160` の初期 full unittest は 1,035 tests / 599.706s、accepted unit target は `<=120s` で、当時の完了時は unit 約 60s / 421 tests、full 402〜426s だった。
  - accepted ADR は local subprocess、filesystem、tempdir、local git、stub `gh` を unit に含める。一方で、遅い local test を integration へ移すだけの対処は禁止し、CLI subprocess は contract smoke に限定し、business logic は lower layer を直接テストし、大きな fixture は縮小する方針を定めている。
  - `iss-00167` は Provider CI を full `uv run pytest` に意図的に移行した。移行完了時は 1,082 collected、full 1,006 passed / 76 skipped / 421.21s であり、performance / pytest-xdist は対象外だった。
  - 現在の 2,696 collected / 約2,249s は、当該 migration 時点に対して collection が約 2.49 倍、runtime が約 5.34 倍である。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 現在の主要因は、単一の遅い assertion ではなく、real local git、temporary target、runtime subprocess、state polling / real sleep、重い asset / wheel preflight が多数回重なる test-work amplification である可能性が高い。
  - Provider CI の full-suite 実行を push と pull_request の双方で無条件に起動する topology は、同一 SHA 重複時に test-work amplification を CI latency / compute amplification に増幅している可能性が高い。
  - fake clock / sleeper、immutable-only な wheel / asset reuse、繰返し CLI behavior matrix の一部を lower layer 直接テストへ移すことは、有力な改善仮説である。CLI public contract の smoke は残す必要がある。
  - static shard と lane 化は、collection-set の union が full suite と等しいことを機械的に守れる場合にのみ、Provider CI latency を下げる候補になる。xdist は fixture isolation audit の後段候補である。
- 推測の根拠:
  - `test_init_update.py` 除外後の unit 実行が 380.19s から 5.45s へ低下し、同ファイルに sleep と packaging / dogfooding / observation の重いシナリオがある。
  - harness source は local hierarchy ごとに複数 subprocess を起動し、static call-site 数も大きい。
  - GitHub run の pytest step は約 37.5 分で、install / static analysis / validation の時間は相対的に小さい。
  - Oracle advisory は上記二つの amplification と、immutable reuse、direct lower-layer tests、dedupe/cancel、collection-set equality guard を推奨した。ただしこれは独立に採用された決定ではない。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - shadow period 後、branch protection が fast lane のみを merge gate にできるか、または全 PR で full union を必須とし続けるか。
  - branch protection の required check 名と、workflow / job 名を変更した場合の migration 契約。
  - warmup + 5 回以上の p50 / max、CI runner variance を含む改善前後の分布。
  - 各 CLI matrix を lower layer direct test に変換しても、parser、stdout、exit code、import path の CLI contract が十分に残る最小 smoke set。
  - immutable wheel / asset reuse の cache key、失効条件、stale package を検出する guard。
  - xdist を導入した場合の shared mutable repository、filesystem、environment、network port の race 有無。
- 確認できない理由:
  - branch protection query は 403 であり required check contract を取得できなかった。
  - 本調査は source / single-run duration / GitHub history の観測までで、変更を加えた benchmark、shadow workflow、parallel safety audit をまだ実施していない。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - shadow period の後、merge protection は fast lane のみを必須にし、full union は main / schedule / manual の検証へ移せるか。それとも全 PR で full union を必須とするか。
  - Provider CI latency の target を、required PR path と full regression のどちらに適用するか。
- pressure-test question として切り出すべき候補:
  - 「高速 lane が green でも、static shard の union が full collection と等しくない、または flaky snapshot test が未実行なら merge を許可するか」。
  - 「同一 SHA の push + pull_request 重複を cancel / dedupe して、required check の観測や監査性を損なわないか」。
- 質問せずに解決できた候補:
  - 「CI/CD を対象にするか」は source で deployment / CD workflow が見当たらないため、confirmed scope を Provider CI latency とした。
  - 「遅い local test を integration へ移すだけでよいか」は accepted ADR が明示的に否定している。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - ユーザー表現の「CI/CD」と、repository に存在する「Provider CI」および `CI` workflow。
  - 一般的な狭義の unit test と、accepted ADR が定義する「外部実通信をしない local-complete test」を含む repository 固有の unit lane。
- 既存 docs / code / tests / artifacts / primary sources での使われ方:
  - `.github/workflows/provider-ci.yml` は provider package の full pytest、`.github/workflows/ci.yml` は spec-dock sync / validate を行う。deployment / CD workflow は確認できなかった。
  - accepted ADR は local subprocess、filesystem、tempdir、local git、stub `gh` を `tests/unit` に含め、実 GitHub / remote git / network / auth を `tests/integration` に置く。
- 判断が必要な理由:
  - CD の不存在を前提にしない施策や、一般論で local-heavy tests を integration へ移す施策は、実際の performance scope と既存 ADR の境界を誤るため。

## edge cases / 具体シナリオ (必須)
- edge case:
  - shared mutable repo / cache を複数 test または worker が再利用し、順序依存や race により本来の bug を隠す。
  - wheel / asset reuse が stale package を使用し、checkout source と shipped artifact の差を見逃す。
  - fake sleeper 化で timeout / poll contract の assertion が弱まり、実際の timeout propagation の regression を見逃す。
  - shard selector の誤りで test が full union から漏れる、または skip / xfail が説明なく増える。
  - workflow / job 名の変更が branch protection required checks と一致せず、PR gate を意図せず弱める。
  - docs-only workflow change でも fast parity / validate が不足し、shipped runtime guidance と CI contract が乖離する。
- その edge case が requirement / design / plan に与える影響:
  - reuse は immutable input のみに限定し、mutable target は test ごとに一意にする契約、staleness guard、失敗時の再現手順を設計へ明記する必要がある。
  - fake time は timeout semantics を別テストで保持し、単なる実待ち除去にしない必要がある。
  - shard / lane には collection-set equality（full collection との union equality）と、skip / xfail の増加を fail とする guard を計画する必要がある。
  - workflow migration は required check の実測と shadow period を終えるまで、既存 full suite の保護を下げない必要がある。

## implications / 判断への含意 (必須)
- 以下は proposed / not adopted の実装順候補である。
  1. operation counts と warmup + 5 回の p50 / max を計測し、fixture、subprocess、sleep、asset / wheel 操作を分離して baseline を固定する。
  2. fake clock / sleeper を timeout semantics の専用証跡と組み合わせ、実時間待ちを除去する。
  3. immutable wheel / asset のみ再利用し、mutable repository / target は一意にする。繰返し CLI behavior matrix は lower layer direct test を選択的に使い、CLI smoke を残す。
  4. Provider CI に同一 SHA の dedupe / cancel を検討し、required check の contract を先に確認する。
  5. static shard / fast lane は collection union guard を持つ shadow period で測定し、xdist は isolation audit 後にのみ評価する。
- 候補となる受け入れ指標は、local unit p50 `<=120s`、max `<=150s`、completed duplicate same-SHA run `0`、説明のない skip / xfail 増加 `0`、shared mutable repo `0` である。required PR path と full regression の latency target は、上記の人間判断なしには固定しない。
- 期待される短縮効果は仮説であり、現時点で実現済みではない。変更の採否は canonical requirement / design / plan、必要なら accepted ADR、および `report.md` Evidence Adoption Ledger の判断後に成立する。

## リスク/制約 (任意)
- `iss-00160` の accepted test boundary を維持し、遅い local test を integration へ移すだけで日常 lane の runtime を見かけ上短縮しない。
- `iss-00167` が選択した Provider CI full pytest の coverage intent を、branch-protection owner の決定なく弱めない。
- Oracle output は advisory であり、source / tests / GitHub evidence による検証なしに canonical decision にしない。

## 反映先 (任意)
- reflected_to:
  - `[]`（未反映。main orchestrator が canonical docs / accepted ADR / report ledger への採用を判断する）。

## 参考（References） (任意)
- `.github/workflows/provider-ci.yml`
- `.github/workflows/ci.yml`
- `tests/cli_runtime/harness.py`
- `tests/unit/infra/test_init_update.py`
- `iss-00160-reduce-test-runtime-followup/discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`
- `iss-00167-migrate-tests-to-pytest/report.md`
- [Provider CI run 29708758044](https://github.com/chemitaro/spec-dock/actions/runs/29708758044)
- [Provider CI run 30278654717](https://github.com/chemitaro/spec-dock/actions/runs/30278654717)
