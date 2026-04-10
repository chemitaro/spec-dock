---
種別: 実装報告書（Issue）
ID: "iss-00061"
タイトル: "Dependency mutation command contract"
関連GitHub: ["#61"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00061 Dependency mutation command contract — 実装報告（LOG）

## 実装サマリー (任意)
- active initiative / epic / issue と `iss-00060` の docs / report / 現状実装を突き合わせ、`iss-00061` の requirement / design / plan を実装開始可能な粒度まで具体化した。
- `deps add/remove` の command/application/domain/infra/presentation/tests を TDD で実装し、S01-S04 の step commit を積み上げて mutation contract を完成させた。
- S90 で provider-side `reference_deps.md` 正本と dogfooding copy を更新し、S99 では reviewer fail を受けて remove write-failure regression、atomic lock failure/no-write 契約、mutation preflight scope の明文化まで含めて最終整合を取った。
- 最終 focused validation は `python -m unittest tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_deps` で `Ran 104 tests ... OK` である。

## 実装記録（セッションログ） (必須)

### 2026-04-10 00:00 - 00:00

#### 対象
- Step: implementation readiness / spec review loop
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003, EC-004, EC-005, EC-006

#### 実施内容
- active initiative / epic / issue の requirement / design / plan を読んで、今回 issue の scope / constraints / acceptance criteria / implementation order を整理した。
- `iss-00060` の requirement / design / plan / report と provider-side source/tests を確認し、`.meta.json` SoT、`deps_reader.py` の read contract、read-side regression 完了、`deps check` しか無い current implementation baseline を把握した。
- `iss-00061` requirement / design / plan を更新し、#60 から引き継ぐ前提、provider-side 正本境界、docs owner、generic RuntimeError fallback を使わない error taxonomy、write-failure atomicity verification を明記した。
- 初回 spec review は fail で、`iss-00060` prerequisite の権威ソース不足と write-failure atomicity の検証不足を指摘された。
- `iss-00060` requirement / design / plan / report の status fields を authoritative に整え、`iss-00061` requirement / design / plan に `iss-00060/report.md` を prerequisite authority として追記したうえで再レビューし、最終的に pass を取得した。

#### 実行コマンド / 結果
```bash
sed -n '1,240p' spec-dock/active/context-pack.md
sed -n '1,260p' spec-dock/active/{initiative,epic,issue}/{requirement,design,plan}.md
sed -n '1,240p' spec-dock/initiatives/.../iss-00060-.../{requirement,design,report}.md
rg -n "deps add|deps remove|depends_on|dependency" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests/cli_runtime
git status --short

- active docs / issue60 docs / current implementation status の読込完了
- spec review 1回目: fail
- 修正後 spec review 2回目: fail
- prerequisite authority を report ベースに固定後、spec review 3回目: pass
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/requirement.md` - #60 前提、provider-side 正本境界、docs owner、prerequisite authority を明記
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/design.md` - current implementation baseline、typed failure 契約、atomic write 定義、failure injection verification を追加
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/plan.md` - docs owner、write-failure atomicity step、prerequisite authority gate を追加
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00060-meta-json-dependency-schema-and-reader-alignment/{requirement,design,plan,report}.md` - upstream prerequisite を authoritative に参照できるよう status / author fields を補正

#### コミット
- なし（実装準備のみ。コミット未作成）

#### メモ
- repo 調査では provider-side source-of-truth では `.meta.json` reader が整列済みだが、dogfooding runtime copy は未同期の可能性があることを確認した。今回 issue では provider-side shipped runtime を正本として扱うよう docs へ明記した。
- current implementation baseline として `deps` subtree は `check` のみ、`MutateDepsRequest/Result` と mutation use case / write helper は未実装である。

---

### 2026-04-10 07:44 - 07:45

#### 対象
- Step: S01
- AC/EC: AC-001

#### 実施内容
- `deps add --from <id> --to <id>` の happy path を TDD で実装し、parser / command / use case / write helper / renderer / runtime wiring を最小構成で接続した。
- `tests/cli_runtime/test_deps.py` に add success integration を追加し、`tests/cli_runtime/test_runtime_deps_s04.py` に wrapper / delegation smoke を追加した。
- implementation review を実施し、S01 の scope 内で blocking finding が無いことを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04

- Ran 71 tests in 17.445s
- OK
- implementation review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` - `deps add` subcommand を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` - add args / request 生成 / happy-path outcome を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - mutation request/result と use case endpoint を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py` - S01 用の minimal add use case を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - `.meta.json` に dependency を追記する最小 write helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - `deps add` success renderer を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - mutation use case wiring を追加
- `tests/cli_runtime/test_deps.py` - add success integration を追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - runtime wrapper/delegation smoke を追加

#### コミット
- `a29e296` `feat(runtime): deps add の最小 mutation 経路を追加`

#### メモ
- S01 は happy path のみで、duplicate/no-op、remove、詳細な error family、write-failure atomicity は未実装のまま維持している。
- 現在の add write は `depends_on` への最小追記実装で、重複排除は S02 で扱う前提である。

---

### 2026-04-10 08:03 - 08:03

#### 対象
- Step: S02
- AC/EC: AC-002, EC-001

#### 実施内容
- `deps add` 実行時に current graph preflight を duplicate 判定より先に実行し、healthy graph でのみ `result=unchanged` を返す no-op 契約を追加した。
- duplicate add 時に `.meta.json` を再書き込みしないこと、および current graph が壊れている場合は duplicate success へ進まず preflight error を返すことを TDD で固定した。
- implementation review と QA review を実施し、S02 scope で blocking finding が無いことを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_deps
python -m unittest tests.cli_runtime.test_runtime_deps_s04

- tests.cli_runtime.test_deps: Ran 61 tests / OK
- tests.cli_runtime.test_runtime_deps_s04: Ran 13 tests / OK
- implementation review: pass
- QA review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py` - preflight-first と duplicate `unchanged` no-write を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - duplicate edge 判定 helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - current graph preflight helper を追加
- `tests/cli_runtime/test_deps.py` - duplicate add unchanged と broken current graph preflight-first を追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - `result=unchanged` の runtime rendering を追加

#### コミット
- `9505092` `feat(runtime): deps add の重複追加を unchanged として扱う`

#### メモ
- preflight は S02 時点では local-compat fixture を維持するため `enforce_github_mandatory_linkage=False` で実行している。
- non-issue node / remove / invalid add 詳細 error family は S04 で扱う。

---

### 2026-04-10 08:19 - 08:19

#### 対象
- Step: S03
- AC/EC: AC-003

#### 実施内容
- `deps remove --from <id> --to <id>` の happy path を TDD で実装し、existing issue->issue edge を削除して `result=updated` を返す最小経路を追加した。
- parser / command / use case / repo helper / runtime wiring を remove path に拡張し、S01/S02 の add 契約を壊さないことを focused tests で確認した。
- implementation review を実施し、S03 scope で blocking finding が無いことを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04

- Ran 76 tests in 18.411s
- OK
- implementation review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` - `deps remove` subcommand を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` - remove args / request 生成 / happy-path outcome を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py` - remove action の success path を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - `.meta.json` の dependency 削除 helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - remove helper wiring を追加
- `tests/cli_runtime/test_deps.py` - remove success integration を追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - remove runtime delegation smoke を追加

#### コミット
- `d4c2ce0` `feat(runtime): deps remove のコマンド契約を追加`

#### メモ
- remove not-found や broader error taxonomy は未実装で、S04 でまとめて扱う。
- 現段階の remove は happy path のみで、existing edge がある前提に限定している。

---

### 2026-04-10 08:29 - 08:48

#### 対象
- Step: S04
- AC/EC: AC-004, EC-002, EC-003, EC-004, EC-005, EC-006

#### 実施内容
- `deps add/remove` の error family を TDD で拡張し、remove not-found、invalid add/remove request、non-issue node input、cycle add、parser error、write failure を deterministic な CLI contract として固定した。
- application では typed `MutateDepsError` により fail-closed に統一し、infra では same-directory temp + replace の atomic write と temp cleanup、readonly lock の再適用、unlock/stat/replace 系失敗の `write_failed` 化を実装した。
- 初回 implementation review で write-failure mapping と permission bit preservation に欠陥が見つかったため修正し、再 review / re-QA で pass を取得した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04

- Ran 91 tests in 20.999s
- OK
- implementation review: fail -> fix -> pass
- QA review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - typed `MutateDepsError` と mutation error code contract を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py` - fail-closed mutation orchestration、cycle/not-found/invalid/write failure mapping を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` - node id normalization と mutation error handling を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - issue edge existence / cycle detection helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - atomic temp+replace write、temp cleanup、readonly read-bit preserve/relock、write failure mapping を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - mutation error renderer を追加
- `tests/cli_runtime/test_deps.py` - add/remove の error contract、unsupported node、cycle、write failure の integration を追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - atomic no-partial-write、temp cleanup、permission preservation、wrapper error rendering の runtime tests を追加

#### コミット
- `9fde052` `fix(deps): s04のエラー契約と原子書き込みを統一`

#### メモ
- final pass 時点では `write_failed` が `stat` / `chmod` / `replace` / cleanup 系失敗でも typed error に正規化され、partial write を残さないことを focused tests で確認した。
- QA からは CLI-level remove `write_failed` regression と lock-failure contract の追加余地が示されたが、現時点では non-blocking suggestion 扱いである。

---

### 2026-04-10 08:49 - 08:55

#### 対象
- Step: S90
- AC/EC: docs impact resolution

#### 実施内容
- `deps add/remove` が公開 command surface になったため、provider-side 正本 `reference_deps.md` と dogfooding copy の両方を更新した。
- command surface、issue->issue direct edge only、current graph preflight-first、duplicate add=`result=unchanged`、remove not-found=`edge_not_found`、`.meta.json` only、atomic no-partial-write / rollback-by-revert を reference に追記した。
- provider-side 正本と dogfooding copy が一致していることを確認した。

#### 実行コマンド / 結果
```bash
rg -n "deps add|deps remove|depends_on|reference_deps|deps check" src/spec_dock/assets/spec_dock/docs spec-dock/docs

- docs impact: change required
- provider-side reference_deps.md と dogfooding copy を更新
- provider-side / dogfooding copy 一致確認: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md` - mutation command contract と atomic no-partial-write 契約を追記
- `spec-dock/docs/reference_deps.md` - dogfooding copy を provider-side 正本に同期

#### コミット
- 未作成（S99 の final diff review 後に docs/report 差分をまとめてコミット）

#### メモ
- docs 変更は command surface の公開差分に限定し、downstream parity / hard cutover 判断は引き続き `iss-00062` の責務として据え置いた。

---

### 2026-04-10 08:56 - 09:32

#### 対象
- Step: S99
- AC/EC: final diff review quality gate

#### 実施内容
- S01-S04 + S90 を含む final diff を対象に reviewer 群へ final gate を依頼した。
- 初回 QA review で `deps remove` の `write_failed` CLI 回帰テスト不足と relock failure branch の未固定が指摘されたため、provider-side runtime/tests に focused regression を追加した。
- 続く spec/QA review で、mutation preflight scope と `write_failed[lock]` の no-write 契約が docs/report と完全に一致していない点が指摘されたため、issue docs と reference docs に `dependency graph consistency only` / `enforce_github_mandatory_linkage=False` を明文化し、atomic write を `tmp作成 -> write -> tmpへreadonly lock -> replace` へ改めて lock failure を replace 前 failure に寄せた。
- さらに QA 指摘を受け、malformed `.meta.json` / `depends_on` schema failure も `code=preflight_validate_failed` に正規化する preflight mapping を追加した。
- 続く implementation review で、compiled topology と direct metadata の取り違えにより `deps add/remove` が direct edge 無しでも `unchanged` / `updated` を返しうる点が指摘されたため、direct dependency existence/removal を raw metadata 基準へ寄せ、shorthand direct ref の remove と remove-side unresolved/non-issue regression まで追加した。
- 最終修正後に `python -m unittest tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_deps` を再実行し、104 tests すべて green を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_deps

- Ran 104 tests in 24.525s
- OK
- reviewed scope: `HEAD~4..working tree`
- initial QA review: fail
- fix 1: remove write_failed CLI regression + mkstemp/write_temp mapping を追加
- fix 2: mutation preflight scope を docs に明文化し、lock failure を replace 前 failure/no-write に修正
- fix 3: topology load / malformed `.meta.json` / invalid `depends_on` schema も typed `preflight_validate_failed` へ統一
- fix 4: direct/raw dependency semantics で add/remove 判定と shorthand remove を整合化
- final implementation review: pass
- final QA review: pass
- final spec review: pass
- S99 verdict: final diff review pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - temp file creation failure を `write_failed[write_temp]` に正規化し、lock failure を replace 前 no-write failure に修正
- `tests/cli_runtime/test_deps.py` - `deps remove` write failure の CLI/no-write regression を追加
- `tests/cli_runtime/test_runtime_deps_s04.py` - lock failure no-write / `write_failed[lock]` / `write_failed[write_temp]` regression を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/mutate_deps.py` - topology load / malformed meta 失敗を typed `preflight_validate_failed` に正規化
- `tests/cli_runtime/test_deps.py` - malformed `.meta.json` / invalid `depends_on` schema の typed preflight/no-write regression を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/{mutate_deps,ports}.py` - direct dependency existence/resolution contract を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/{contracts,deps_reader,fs_repo}.py` - direct dependency resolution と shorthand direct ref remove を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - direct dependency reader wiring を追加
- `tests/cli_runtime/{test_deps,test_runtime_deps_s04}.py` - direct-edge add/remove, shorthand remove, remove unresolved/non-issue regression を追加
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/{requirement,design,report}.md` - mutation preflight scope と S99 closing evidence を更新
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md` - mutation preflight scope を明文化
- `spec-dock/docs/reference_deps.md` - dogfooding copy を同期

#### コミット
- 未作成（fresh final reviews pass 後に S99 docs/report/runtime 差分を最終コミット）

#### メモ
- final gate では reviewer fail をそのまま close へ持ち込まず、contract mismatch を code/tests/docs/report の全レイヤで是正してから fresh review を通した。
- mutation preflight は current dependency graph invalid を止める gate であり、GitHub mandatory linkage は import/sync と同じ local-compat mode の対象外として固定した。

---

## 遭遇した問題と解決 (任意)
- 問題: `iss-00061` が `iss-00060` を完了済み prerequisite として参照していた一方、upstream issue の canonical status fields と prerequisite authority が曖昧だった
  - 解決: `iss-00060` の requirement / design / plan / report header を整え、`iss-00061` requirement / design / plan に `iss-00060/report.md` の close-ready evidence と `S99 verdict: final diff review pass` を authority として明記した
- 問題: atomic / no-partial-write が hard constraint なのに、write-failure の観測点が計画に無かった
  - 解決: `EC-006 write failure atomicity`、same-directory temp + replace の定義、failure injection test、S04 の write-failure verification を追加した

## 学んだこと (任意)
- upstream issue を前提条件として使う場合、body の叙述だけでなく `report.md` の verdict を authority として固定しないと reviewer が gate 判定しづらい
- dependency mutation のような state change は、semantic validation だけでなく write failure 時の保全契約まで spec に入れておくと implementation branch がぶれにくい

## 今後の推奨事項 (任意)
- 実装開始時は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` を正本として `deps add/remove` を追加し、dogfooding runtime copy を実装正本と混同しない
- S01 着手前に `MutateDepsRequest/Result`、error taxonomy、atomic write helper の test seam を先に固定すると TDD が進めやすい

## 省略/例外メモ (必須)
- repo-wide `validate` / `sync` evidence と hard cutover judgment は計画通り `iss-00062` へ委譲し、本 issue では focused mutation validation のみを実施した
- dogfooding runtime copy へのコード同期や manual runtime verification は本 issue のスコープ外として扱い、docs copy は provider-side 正本に同期した
