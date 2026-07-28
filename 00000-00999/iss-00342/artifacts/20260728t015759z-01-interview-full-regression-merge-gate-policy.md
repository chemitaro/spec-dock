---
種別: interview
ID: "20260728t015759z-01-interview"
タイトル: "Full Regression Merge Gate Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["iss-00342"]
関連: []
scope: "issue"
scope_id: "iss-00342"
created_at: "2026-07-28T01:57:59Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260728t015759z-research: artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md"
  - "20260605t075347z-01-adr: iss-00160/discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md"
  - "iss-00167 requirement.md and report.md: pytest full-suite provider CI adoption"
reflected_to:
  - "artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md"
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260728t015759z-01-interview Full Regression Merge Gate Policy

## 位置づけ
- 用途: Provider CI の PR merge protection を、完全回帰unionのまま維持するか、証跡と rollback を伴う高速laneへ段階移行するかについて記録した source-grounded 正式質問・回答シートである。
- authority: ユーザー回答により `user-approved`。この interview 自体は canonical authority ではなく、採用済みの ADR が durable policy の authority である。
- 一つの `interview` artifact には一つの本質的な質問だけを記録する。回答後に別の高影響な判断が残る場合は、新しい unanswered `interview` に分ける。

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`: PR で必須にする検証範囲、shadow period の受入条件、完全回帰unionの実行契約を定義する。
  - `design.md`: fast lane と完全回帰unionの CI topology、collection union の同一性確認、required check name migration、alert と rollback を定義する。
  - `plan.md`: 最適化、shadow period、branch protection の運用確認、段階切替と rollback の順序を定義する。
  - `ADR`: A または B を将来の Issue にも及ぶ durable な merge-gate policy として採用する場合に候補となる。
  - `report.md` Evidence Adoption Ledger: 回答と採用可否、根拠、反映先を記録する。
- chat 上の軽微な一問では足りない理由:
  - full-suite を PR 必須に戻した `iss-00167` の意図的な契約を変更し得るため、技術的な実測だけからは決められない owner policy である。

## 質問の目的
- 対象者:
  - Provider CI の merge protection 方針を決める owner。
- 何を明確にする質問か:
  - 30〜40分の PR feedback を、実テストコストの削減だけで解くか、検証リスクを明示管理する gate policy の段階変更も解決手段に含めるかを明確にする。
- 回答が後続判断へ与える影響:
  - accepted policy に応じて、Issue の acceptance criteria、CI topology、rollout/rollback plan、必要時の durable ADR を authoring する。

## 質問
- pressure-test question:
  - 30〜40分問題を実テストコスト削減だけで解く必要があるのか、検証リスクを明示管理したgate policy変更も解決手段に含められるか。
- 質問:
  - 20 PR程度の shadow period で回帰見逃しが0件であることを確認した後、PRのmerge protectionは lint・unit・parity・代表的CLI smokeから成る高速lane（目標p95 10分以内）のみを必須にし、完全回帰unionは `main`・schedule・manualで実行する運用へ移行してよいですか。それとも、全PRを完全回帰unionで引き続きblockすることを必須条件にしますか。
- 回答してほしいこと:
  - Option A、B、C のいずれを採用するか、または採用に必要な条件を回答する。

## source-grounded context
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `.github/workflows/provider-ci.yml` は現在、`push` と `pull_request` で `uv run pytest` の完全suiteを実行し、concurrency / cancellation は設定していない。
  - Issue-local research artifact `20260728t015759z-research` を本質問の調査根拠として参照する。
  - 直近観測は 2696 collected、成功した `pytest` は 2249.64 秒、Provider CI の中央値は 38.1 分、最大は 40.9 分、local `cli_runtime` は 20:28、`unit` は 6:20 である。
  - `iss-00167` の requirement/report は、unit・integration・runtime/CLI regression を含む full `uv run pytest` を Provider CI の意図的な契約として復元し、並列化などの最適化は後続へ defer した。
  - accepted `iss-00160` ADR は、遅いローカルテストを単に別カテゴリへ再分類して残すことを許容せず、parity と代表的 CLI contract の義務を維持する。
- local context で解決できたこと:
  - 現在の遅延、full-suite の実行契約、既存の parity/CLI contract 境界は確認できた。
  - branch protection の required check name は token の 403 により読めないため、workflow job 名を変更する前に operational migration を検証する必要がある。
- まだ人間判断が必要な理由:
  - full regression を PR merge protection から外すかは、coverage と feedback speed の許容リスクを伴う owner policy であり、実測だけでは採否を決定できない。

## 回答案
- Option A（推奨）: Staged fast gate
  - 長時間完全回帰テストを PR merge blocker と通常開発の既定テストから外し、lint・短時間 unit・parity・代表的 CLI smoke から成る fast lane を merge-required とする。完全回帰unionは明示手動実行と `main` への merge 後 push でバックグラウンド実行し、失敗は merge 後の事後検知として修復対象にする。schedule / cron は導入しない。20 PR shadow period は必須にせず、切替前に collection と event routing を検証する。p95 10分以内は提案上の目標であり未検証である。
- Option B: Full union always required on every PR
  - 全 PR で完全回帰unionを必須のまま維持し、テストコスト削減と計測済み parallel shards により p50 15分以内、p95 20分以内を達成する。compute と feedback は増えるが、pre-merge coverage は最も強い。
- Option C: Defer policy decision
  - 最初の最適化 Issue の間は現在の完全回帰union必須を維持し、escape・latency・compute のデータを収集する。gate policy を変える前に、後続の decision artifact / ADR を作成する。直近の policy risk は小さいが、短期の latency 改善は制限され得る。

## Codex の分析
- 判断軸:
  - PR feedback latency、pre-merge regression coverage、collection union の同一性、回帰見逃しの検知と rollback、branch protection の実運用可能性。
- tradeoff:
  - A は feedback を大きく改善し得るが、完全回帰の検知を post-merge に移す。B は coverage を最大化するが、30〜40分の feedback をテストコスト削減だけで解消する必要がある。C は証跡を増やせるが、現状の開発者待ち時間を維持する。
- リスク:
  - required check name migration の誤り、merge 後の完全回帰失敗、fork PR の挙動差、無関係 branch の cancellation、docs-only 変更での parity、collection omission。
- 具体シナリオ / edge case:
  - 切替前に fast lane と完全回帰unionの collection を比較し、union の欠落を fail とする。PR / `main` push / manual の event routing を実装テストで固定する。切替後に `main` の完全回帰が失敗した場合は、既に行った merge は block せず、原因が collection omission か test flake かを切り分け、必要なら完全回帰を PR gate に戻す。fork PR と branch protection は実際の required check 名で事前に確認する。

## Codex の推奨案
- 推奨:
  - Option A をユーザー refinement とともに採用する。採用済み ADR は `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md` である。
- 理由:
  - collection と event routing を切替前に検証し、完全回帰を明示手動実行と `main` merge 後に維持すれば、`iss-00160` の parity/CLI contract を保持しつつ、通常開発と PR feedback から長時間テストを外せる。schedule / cron を導入しないため、不要な運用複雑性も増やさない。
- 未回答時の影響:
  - 該当しない。ユーザー回答により Option A を採用した。

## ユーザー回答
- answer capture:
  - Option A を採用する。
- 回答:
  - 長時間完全回帰テストは PR merge blocker と通常開発の既定テストから外す。完全回帰unionは明示手動実行時のみ実行可能とし、加えて `main` への merge 後 push でバックグラウンド実行する。schedule / cron は追加複雑性のため採用しない。完全回帰の失敗は merge 後の事後検知であり、既に行った merge は block しない。先に例示した 20 PR shadow period は必須運用にはせず、cutover 前の collection / event-routing 検証へ置き換える。
- 回答日時:
  - 2026-07-28T02:55:03Z

## 追加確認の要否
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断
- adoption_status:
  - adopted
- adoption target:
  - `ADR`: `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md`。`requirement.md`、`design.md`、`plan.md`、`report.md` Evidence Adoption Ledger は後続反映予定であり、まだ反映しない。
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option A を採用し、長時間完全回帰を PR merge blocker と通常開発の既定経路から外す refinement、`main` merge 後実行、手動実行、schedule / cron 非採用、20 PR shadow period 非必須を明示した。判断は accepted ADR に記録済みである。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes。canonical authoring の後続作業として反映する。

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - 後続反映で、PR 必須の fast lane、通常開発の既定経路、手動完全回帰、`main` merge 後の完全回帰、merge 後事後検知を明記する。
- `design.md`:
  - 後続反映で、fast lane / full union の CI topology、collection parity、PR / `main` push / manual event routing、required check migration、alert と rollback を設計する。schedule / cron は設計しない。
- `plan.md`:
  - 後続反映で、collection / event-routing 検証、operational verification、cutover、rollback rehearsal の順に実行する。20 PR shadow period は必須 step にしない。
- `ADR`:
  - `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md` に accepted decision として記録済みである。
- reflected_to 更新方針:
  - 現時点では accepted ADR のみを記録する。canonical adoption 後に main orchestrator が対象文書と section を追加する。
- adoption reflection:
  - interview の回答は adopted であり、durable policy は accepted ADR に反映済み。canonical requirement / design / plan / report への反映は後続作業である。
