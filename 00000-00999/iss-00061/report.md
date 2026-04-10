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
- spec review では upstream prerequisite の権威付けと write-failure atomicity の検証契約が不足していたため、issue docs と `iss-00060` status fields を補正し、再レビューで pass を取得した。
- 実装コード変更はまだ着手しておらず、本 report は implementation readiness と review evidence の記録に限定する。

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
- 未作成（この後 S01 commit を実施）

#### メモ
- S01 は happy path のみで、duplicate/no-op、remove、詳細な error family、write-failure atomicity は未実装のまま維持している。
- 現在の add write は `depends_on` への最小追記実装で、重複排除は S02 で扱う前提である。

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
- 実装コード、テスト追加、`sync` / `validate` 実行、dogfooding manual verification は未着手
- この段階では implementation readiness と spec review pass の取得のみを実施した
