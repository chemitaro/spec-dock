---
種別: 要件定義書（Issue）
ID: "iss-00411"
タイトル: "Remove retired SpecDock CLI surfaces after scope active work cutover"
関連GitHub: ["#411"]
状態: "draft"
最終更新: "2026-09-27"
親: ["epic-00080", "init-00079"]
---

# iss-00411 Remove retired SpecDock CLI surfaces after scope active work cutover — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

Issue #409 / PR #410 で公開 CLI を Scope / Active / Work 中心の固定 external engine へ切り替えた後も、provider package、配布 runtime、CI、現行風の文書、test fixture に旧 CLI 実装が残っている。本 Issue は、現在の公開経路を一つに収束させ、旧実装を誤って呼び出す caller と旧契約だけを守る test を除去しながら、現在の CLI、固定 SHA CI、失敗診断、移行履歴、provider / dogfood parity の有意味な回帰を残す。

利用者・保守者が観測できる最終状態は次のとおりである。

- 日常操作、固定 distribution、repository shim、CI が同じ current CLI contract を使う。
- 旧 CLI を実行可能な fallback は配布物と test setup のどちらにも残らない。
- 旧コマンドを入力したときは、互換実行ではなく、到達可能な current parser が安全に拒否する。
- current docs と examples は 44 leaf の現行 CLI、固定 engine、journal / recovery を案内する。
- historical docs、schema migration、旧コマンド拒否診断は、その役割が現在も到達可能または監査上必要な範囲で保持される。

## 背景

### 切替済みの契約

Issue #409 と PR #410 により、公開入口は `spec_dock.cli:main` から固定 external engine へ進み、配布 shim も検証済み engine pin を実行する構造になった。current runtime は `cli/options.py` と `cli/vnext_runtime.py` を入口に、44 個の leaf command を提供する。

### 残っている不整合

verified source snapshot `chemitaro/spec-dock@d7c816d11bee1a73cb87273b15e486c3b669206c` では、次の残件が同時に存在する。

- 旧 runtime stack `spec_dock_runtime/app.py -> cli/{parser,registry,dispatch,bootstrap}.py -> commands/<old>.py` が provider asset に残る。
- package entry `src/spec_dock/cli.py` に test 専用 `legacy_installer_main` が残り、旧 directory installer `src/spec_dock/installer.py` を呼ぶ。
- ただし current `external_cli.py` は `installer.ASSETS` を参照しているため、installer file を丸ごと削除できない。
- `.github/workflows/ci.yml` は repository-local shim に旧 root `sync` と `validate` を渡す一方、`.github/scripts/specdock-ci-validate.sh` には fixed source SHA と distribution digest を検証する read-only CI 経路がある。
- `.github/workflows/provider-ci.yml` の focused parity job は旧 installer test と旧 harness の smoke test を明示実行する。
- `tests/cli_runtime/harness.py` と `tests/fixtures/legacy_spec_dock.script` は旧 launcher を意図的に差し込み、旧 runtime test 群を起動する。
- `tests/cli_runtime/test_cli_vnext_contract.py` は current 44 leaf contract に加えて旧 28 leaf inventory を固定する。
- provider / dogfood の `scripts/README.md`、root `docs/github-issue-integration.md`、`docs/sync-aggregation.md` などに、旧 repo-local command を現行案内として読むことのできる記述が残る。

### 親 scope から継承する境界

親 Epic #80 は、repo 内で tightly coupled な runtime / installer / docs / dogfood contract の保守を扱い、provider source を正本とし、dogfood consumer を確認対象とする。本 Issue は切替後の一つの根本原因「retired CLI surface が複数層に残っている」を end-to-end で閉じる。

## 関係者と期待成果

| 関係者 | 期待成果 |
|---|---|
| 個人利用者 | 古い CLI が暗黙に動作せず、現行 command または明確な拒否へ必ず到達する。 |
| 実装担当 | provider / runtime / CI / docs / tests の整理順と削除判定が固定され、追加の product 判断なしで実装できる。 |
| reviewer | 削除が文字列一致ではなく caller / reachability と回帰移植の証拠に基づくことを確認できる。 |
| CI operator | checkout した完全な commit SHA から固定 engine を構築し、target workspace を変更せず検証できる。 |
| 将来の保守者 | historical evidence、migration contract、current rejection diagnostics と、実行不能な旧 implementation を区別できる。 |

## 観測可能な要件

### RQ-411-01 公開実行経路の単一化

- package command `spec-dock`、fixed engine、repository shim は current external engine と 44 leaf catalog だけを実行する。
- checkout 内の旧 runtime へ fallback しない。
- test fixture も production package に残る旧 launcher を呼び出さない。

### RQ-411-02 retired implementation の除去

- 旧 parser / registry / dispatch / bootstrap / app と、それらだけから到達する old command modules は、current source、package data、fixed distribution から除去される。
- current route または current test が参照する共有定数・application use case・infra / domain / presentation module は、名前に `legacy` や旧語が含まれるだけでは削除しない。
- 削除候補は、static import、dynamic import / resource path、test caller、package-data inclusion、固定 distribution 実行の全てで非到達を確認してから削除する。

### RQ-411-03 旧コマンドの fail-closed 境界

- 後方互換実行、alias、旧 parser への translation fallback は提供しない。
- current parser から到達する tombstone（例: `cli/legacy.py`）は、旧 root に対する replacement guidance と非 zero exit を提供し続ける。
- tombstone が存在しない retired installer root も、書込み前に usage / removed failure となる。
- rejection message の維持対象は、current public entrypoint から到達できるかどうかで決める。

### RQ-411-04 fixed read-only CI

- `.github/workflows/ci.yml` は checked-out full commit SHA を expected source SHA として `.github/scripts/specdock-ci-validate.sh` を呼ぶ。
- CI は `workspace validate --ci --json` を固定 distribution から実行し、`workspace sync`、repository-local `sync`、repository-local `validate` を実行しない。
- source SHA mismatch、dirty source、invalid distribution digest は fail closed する。
- target workspace、active state、installation control、generated state を CI validation が変更しない。
- provider test workflow の focused parity lane も、削除される旧 installer / harness test ではなく current fixed-engine / installation / provider-dogfood parity regression を実行する。

### RQ-411-05 current docs と historical docs の分離

- current guidance は `scope`、`active`、`work`、`dependency`、`workspace`、`installation` など現行 leaf を案内する。
- `src/spec_dock/assets/spec_dock/` を provider authority とし、current dogfood projection `spec-dock/` は provider と byte parity または明示された generated difference を保つ。
- `docs/github-issue-integration.md` と `docs/sync-aggregation.md` は current CLI / data authority / fixed engine に書き換える。
- `docs/scope-lifecycle-start-finish-analysis.md` と provider `docs/historical/**` は historical evidence として保持し、現行契約ではないことを明示する。
- migration 文書が旧形から現行形への説明に必要とする旧 command text は、stale-current-guidance 検査の例外として管理する。

### RQ-411-06 有意味な current regression の維持

- 旧 launcher や旧 28 leaf inventory だけを固定する test は除去する。
- 旧 test が守っていた invariant のうち current route でも有効なものは、current CLI integration test、application / domain / infra unit test、provider distribution parity test の適切な層へ移植してから旧 test を削除する。
- 少なくとも次を regression として残す。
  - 44 leaf catalog と help / JSON / recovery contract
  - fixed distribution が checkout runtime に fallback しないこと
  - 旧 root の fail-closed rejection
  - fixed CI の SHA / digest / read-only contract
  - current installation init / update / uninstall と journal / recovery
  - schema 3 migration と migration failure recovery
  - provider asset と current dogfood projection の整合
  - fixed distribution に retired runtime files が含まれないこと

### RQ-411-07 provider-first と限定 rollout

- 実装は provider source を先に変更し、この repository の dogfood consumer を同期・検証する。
- 稼働中の他 worktree、他 consumer repository、個別に固定された外部 installation を一斉更新しない。
- Issue 完了は「今後配布される provider」と「この repository の dogfood projection」が整合することを意味し、全導入先の rollout 完了を意味しない。

### RQ-411-08 migration / history / safety の保持

- schema 3 の機械的 migration は本 Issue で再実行しない。
- `workspace migrate` implementation、migration test、fixture / helper、journal / rollback contract は保持する。
- historical docs と Git history で参照可能な旧情報を、current executable surface と混同しない。
- user spec data、active selection、Git branch / worktree、GitHub Issue を cleanup 処理で変更しない。

## スコープ

### 対象

- package public entry と legacy installer fixture の分離・除去
- provider asset 内の retired CLI shell と old command modules の除去
- shared constants / use cases の current ownership への移設または保持
- `.github/workflows/ci.yml` の fixed validation 経路への切替
- `.github/workflows/provider-ci.yml` の旧 focused test caller の更新
- current docs、provider scripts README、dogfood mirror、operator guidance の更新
- old harness / fixture / manifest / retired tests の削除と current regression への移植
- lint / mypy / test configuration の削除後整合
- fixed distribution と provider / dogfood parity の確認

### 対象外

- 旧公開 CLI の互換実行を維持すること
- 44 leaf の新 feature、command rename、option redesign
- schema 3 migration の再実行、mapping の再決定、他 worktree の一括 migration
- 他 repository / consumer への installation update rollout
- GitHub Issue / PR の作成・更新・merge
- user spec data、scope metadata、active state、branch、worktree の変更
- historical content を現行文書へ書き換えること
- runtime layering の全面再設計、共有 use case の無関係な rename

## 失敗・境界条件

### 削除判定が不十分な場合

候補 module に current root、dynamic import、resource path、test、package-data のいずれかの caller が残る場合は削除しない。current 責務を中立 module へ移し、caller と regression を移行した後に再判定する。

### test 移植が不十分な場合

旧 test の assertion が current behavior または共有 business rule を守っているか未確認なら、その test file を削除しない。old CLI syntax だけを守る assertion と current invariant を分離し、current invariant の移植先が green になってから削除する。

### CI の source identity が一致しない場合

workflow checkout の `HEAD^{commit}` と expected full SHA が一致しなければ validation を実行せず失敗する。短縮 SHA、branch 名、default branch への fallback は使用しない。

### dirty source の場合

fixed CI validator は dirty source を拒否する。開発中の dirty checkout では integration test が clean temporary source を作成して contract を検証し、workflow 相当の end-to-end 確認は clean commit checkout で行う。

### dogfood projection に差分がある場合

provider と dogfood の差分を手編集で正当化しない。provider を先に直し、current installation / projection 手順または明示された copy によって dogfood を更新し、byte parity test で確認する。

### historical text が stale scan に一致する場合

`historical/**`、migration guidance、tombstone mapping、Issue specification archive は intentional allowlist として扱う。allowlist 外の current guidance に一致があれば受け入れ不可とする。

## 受け入れ条件

### AC-411-01 current entrypoint only

- `spec_dock.cli:main` は current external engine のみを呼ぶ。
- production package に `legacy_installer_main` の callable public / test hook が残らない。
- repository shim と fixed bundle の help / current leaf smoke が成功する。

### AC-411-02 retired runtime absent

- `spec_dock_runtime/app.py` と retired `cli/{bootstrap,parser,registry,dispatch}.py` が provider asset と built fixed distribution に存在しない。
- old command registry が import していた command modules は、current reachability がないことを確認した上で存在しない。
- current root から retired module 名への import / string resource reference がない。

### AC-411-03 safe rejection retained

- representative retired roots（少なくとも `issue start`、`deps check`、`delete`）は current entrypoint で non-zero となり、既存 tombstone contract の error code と replacement guidance を返す。
- retired installer root `init` は target を作成・変更せず non-zero となる。
- old runtime へ fallback して成功する経路はない。

### AC-411-04 CI callers corrected

- `.github/workflows/ci.yml` は `specdock-ci-validate.sh` に checkout root、target root、`${{ github.sha }}` 相当の full SHA を渡す。
- workflow に repository-local `sync` / `validate` invocation がない。
- `test_ci_fixed_validation.py` は success、SHA mismatch、read-only target を検証する。
- `provider-ci.yml` は削除済み old installer / old harness test を参照せず current focused tests を実行する。

### AC-411-05 docs current / historical boundary

- provider `scripts/README.md` と dogfood `spec-dock/scripts/README.md` は current fixed engine と現行 command を案内し、内容が一致する。
- root current docs と current skill / operator guidance に retired invocation の実行案内がない。
- historical docs は保持され、current contract への pointer / historical label が確認できる。

### AC-411-06 tests migrated before deletion

- `tests/cli_runtime/harness.py`、legacy launcher fixture、legacy 28-leaf manifest、および旧 wire だけを検証する test が削除される。
- `test_cli_vnext_contract.py` は old parser / registry を import せず、44 leaf、help、JSON、recovery、tombstone contract を引き続き検証する。
- old test から移植した current invariant の対応表が `artifacts/20260927t131352z--cleanup-inventory.md` に更新される。

### AC-411-07 full verification green

- `make lint`
- `uv run pytest`
- focused CI / entrypoint / distribution / docs / installation / migration tests
- `git diff --check`
- fixed bundle build と `workspace validate --ci --json`

上記が全て成功し、fixed distribution に retired paths が含まれない。

### AC-411-08 bounded side effects

- schema migration、他 worktree update、外部 consumer rollout、GitHub write が実施されていない。
- current repository の provider / dogfood tool assets と test / docs 以外の user data に差分がない。

## 制約・前提

- source baseline は verified branch `iss-00411-retired-cli-surface-cleanup` の full tip SHA `d7c816d11bee1a73cb87273b15e486c3b669206c` である。
- provider authority は `src/spec_dock/`、dogfood consumer は `spec-dock/` である。
- 個人用ツールの coordinated cutover 後であり、retired public CLI の後方互換は不要である。
- fail-closed safety、journal / recovery、migration history は cleanup より優先する。
- 文字列検索だけで source deletion を確定しない。文字列検索は dynamic reference と stale guidance の補助証拠として使う。
- 本文の `状態: "draft"` は repository scaffold と human review gate を維持するためであり、実装順序と判定規則は本 pack で具体化する。
