---
種別: ADR（Architecture Decision Record）
ID: "20260728t025412z-adr"
タイトル: "Separate Fast Merge Gate And Full Regression Execution"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["iss-00342"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-28"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from:
  - "artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md"
  - "artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md"
  - "user clarification on 2026-07-28"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260728t025412z-adr 高速マージゲートと完全回帰実行を分離する

## ADR 化基準

- hard to reverse:
  - yes。PR の merge protection、通常開発時の既定テスト、`main` merge 後の障害検知時点を変更するため、暗黙に戻すと検証契約が不明確になる。
- surprising without context:
  - yes。完全回帰を全 PR で実行しないことは、`iss-00167` が採用した full `uv run pytest` 契約だけを読む利用者には意外である。
- real tradeoff:
  - yes。PR feedback を短縮する代わりに、完全回帰でしか検出できない不具合は merge 後に判明し得る。
- ADR として残す理由:
  - この判断は単一テストの最適化方法ではなく、今後の CI とローカル開発に共通する長期的な検証レーン契約だからである。

## 結論（Decision）

次の検証レーンを分離する。

1. **高速既定レーン（fast default lane）**
   - PR の merge blocker と通常開発時の既定テストに使用する。
   - lint、短時間の unit tests、provider / dogfooding parity、代表的な CLI contract smoke を含める。
   - 長時間の完全回帰テストを含めない。
2. **完全回帰レーン（full regression lane）**
   - 高速既定レーンから除外した長時間テストを含め、論理的な全テスト集合を実行する。
   - 明示的な手動実行で利用できる。
   - `main` への merge 後の `push` を契機にバックグラウンド実行する。
   - PR の merge blocker にはしない。失敗は merge 後の事後検知として可視化し、修復対象にする。

追加の schedule / cron 実行は導入しない。実行経路と運用を増やす複雑性に対して、明示手動実行と `main` merge 後実行で必要な検知機会を確保できるためである。

先行 interview で例示した「20 PR の shadow period」は必須の運用契約としては採用しない。切替前には、高速既定レーンと完全回帰レーンの test collection、代表的 contract、GitHub Actions の event / job 条件を実装テストで固定する。

## 背景（Context）

- Provider CI は `push` と `pull_request` の双方で full `uv run pytest` を実行し、直近の pytest step は約 37〜38 分を要している。
- ローカルでも `tests/cli_runtime` は約 20 分、`tests/unit` は約 6 分20秒を要する。通常開発と PR feedback の双方で待ち時間がボトルネックになっている。
- `iss-00160` の accepted ADR は、遅いローカルテストを integration へ移すだけの見かけ上の短縮を禁止し、CLI contract と provider / dogfooding parity の維持を要求する。
- `iss-00167` は Provider CI で full suite を実行する契約を意図的に採用したが、performance と実行レーン分離は後続課題として残した。
- ユーザーは、長時間テストを PR merge blocker と通常開発の既定経路から外し、手動実行と `main` merge 後の事後実行へ分離する Option A を明示的に採用した。

## 選択肢（Options considered）

### 選択肢 A: 高速既定レーンと完全回帰レーンを分離する（採用）

- 良い点:
  - PR と通常開発の feedback を、完全回帰の wall time から切り離せる。
  - 完全回帰自体は削除せず、手動と `main` merge 後に維持できる。
  - 既存の required check 名を高速 job に維持できれば、branch protection migration のリスクを抑えられる。
- 悪い点 / 制約:
  - 完全回帰でしか検出できない不具合は merge 後に判明し得る。
  - 高速レーンが代表的 CLI contract と parity obligation を十分に保持していることを機械的に検証する必要がある。

### 選択肢 B: 全 PR で完全回帰を必須のまま維持する（棄却）

- 良い点:
  - 完全回帰の失敗を merge 前に検出できる。
- 悪い点 / 制約:
  - 30〜40 分の PR feedback と、通常開発時の長い待ち時間が継続する。
  - テスト内部の大幅な最適化または sharding が完了するまで問題を解消できない。
- 棄却理由:
  - ユーザーが「長時間テストを merge blocker にしない」ことを優先すると決定したため。

### 選択肢 C: 方針を保留して計測だけ続ける（棄却）

- 良い点:
  - merge-gate policy を変更せず追加データを集められる。
- 悪い点 / 制約:
  - 既に確認済みの重大な feedback latency が継続する。
- 棄却理由:
  - owner intent が明確になり、方針決定を保留する必要がなくなったため。

### 選択肢 D: schedule / cron でも完全回帰を実行する（非採用）

- 良い点:
  - 変更がない期間にも定期的な回帰検知ができる。
- 悪い点 / 制約:
  - workflow、失敗通知、重複実行、運用責任を追加する。
- 非採用理由:
  - ユーザーが追加実装の複雑性を避けると決定したため。手動実行と `main` merge 後実行で代替する。

## 判断理由（Rationale）

- ボトルネックの中心は pytest workload であり、dependency install や lint ではない。既定経路から長時間レーンを分離することが、PR と通常開発の feedback を直接短縮する。
- 完全回帰を削除せず、明示手動実行と `main` merge 後実行に残すことで、coverage intent を保持しながら merge blocker だけを変更できる。
- schedule を追加しないことで、今回の目的に不要な運用面を増やさない。
- これは「遅いテストを別名に移すだけ」の処置ではない。高速既定レーンには代表的 CLI contract と parity obligation を残し、完全回帰レーンとの test collection 契約を検証可能にする。

## 影響（Consequences）

### 良い影響

- PR の required test path と通常開発の既定 test path が短くなる。
- 同じ長時間 suite を PR の `push` と `pull_request` で重複実行する必要がなくなる。
- 開発者は必要なときに明示的な完全回帰コマンドを実行できる。

### 悪い影響 / 将来負債

- `main` merge 後の完全回帰失敗は、既に merge 済みの変更に対する修復作業を必要とする。
- 高速レーンの選定が不十分だと、merge 前に検出できたはずの回帰を見逃す。
- 長時間テストそのものの実行時間は、このレーン分離だけでは短縮されない。

### 影響範囲

- `.github/workflows/provider-ci.yml` の event / job / command 契約。
- `pyproject.toml`、test marker / collection configuration、または同等の test lane selector。
- `Makefile` と README 等の通常・手動・完全回帰コマンド。
- `tests/unit/infra/test_init_update.py`、`tests/cli_runtime/`、代表的 fast CLI / parity tests の分類。
- CI workflow contract と test lane contract を固定する regression tests。

### 移行 / ロールバック

- 切替前に、fast / full の collection、代表的 contract、PR / `main` / manual event routing を自動テストで確認する。
- 既存 branch protection が `provider-tests` を required check としている場合は、その check identity を高速 job に維持することを優先する。
- merge 後の回帰見逃しが許容できない頻度で発生する、collection 漏れが見つかる、または required check が欠落する場合は、完全回帰を PR gate に戻せる構成を維持する。

### 追加対応

- `iss-00342` の `requirement.md` / `design.md` / `plan.md` / `report.md` に本判断を反映する。
- 実装後の長時間テスト内部の最適化は、本 Issue の受け入れ条件を満たすために必要な場合だけ扱い、単なる追加最適化は follow-up 候補とする。

## 参考（References）

- `artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md`
- `artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md`
- `iss-00160-reduce-test-runtime-followup/discussions/20260605t075347z-01-adr-test-suite-boundary-and-fixture-strategy.md`
- `iss-00167-migrate-tests-to-pytest/requirement.md`
- `.github/workflows/provider-ci.yml`
