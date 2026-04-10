---
種別: 実装報告書（Issue）
ID: "iss-00060"
タイトル: "Meta json dependency schema and reader alignment"
関連GitHub: ["#60"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00060 Meta json dependency schema and reader alignment — 実装報告（LOG）

## 実装サマリー (任意)
- S01 では `.meta.json` top-level `depends_on` schema と T1/T3 owner boundary を文書上で固定し、provider-side dependency reference docs を正本として更新した。
- 初回 spec review で epic 文書との raw grammar / docs ownership の不整合が検出されたため、epic design/plan と reference docs を補正し、再レビューで S01 gate を pass した。
- S02 では `infra/deps_reader.py` を `.meta.json` only に切り替え、`deps` / `sync` / `active` の downstream smoke を含む 117 tests を green にして close-ready の review evidence を揃えた。

## 実装記録（セッションログ） (必須)

### 2026-04-10 03:xx - 05:03

#### 対象
- Step: S01
- AC/EC: AC-001, AC-003, EC-004

#### 実施内容
- active initiative / epic / issue の requirement / design / plan を読んで issue execution contract を確認した。
- S01 spec review を実施し、epic design の raw grammar 記述不足と epic plan の provider-side docs owner timing 不整合を検出した。
- epic design / epic plan / provider-side `reference_deps.md` / dogfooding copy を補正し、`.meta.json` top-level `depends_on`、field absence=`[]`、no dual-read / no auto-migration / rollback-by-revert、T1/T3 owner split を固定した。
- 補正後に S01 spec review を再実施し、pass を確認した。

#### 実行コマンド / 結果
```bash
sed -n '1,260p' spec-dock/active/{initiative,epic,issue}/{requirement,design,plan}.md
git diff -- spec-dock/active/epic/design.md spec-dock/active/epic/plan.md src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md

- active docs の読込完了
- 初回 spec review: fail（P1 2件）
- 補正後 spec review: pass
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/design.md` - epic-level raw grammar / docs owner boundary を issue spec と整列
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/plan.md` - T1/T3 deliverable と owner timing を整列
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md` - provider-side dependency reference の正本を `.meta.json` contract へ更新
- `spec-dock/docs/reference_deps.md` - dogfooding copy を secondary verification として同期
- `spec-dock/active/issue/report.md` - S01 review / fix / pass を記録

#### コミット
- `cc52538` `docs(epic-00059): .meta.json依存契約を整列`

#### メモ
- S01 gate verdict: spec review pass
- 初回 fail findings は epic 文書側の不整合であり、人手判断は不要だったため self-heal で解消した。

---

### 2026-04-10 05:03 - 05:52

#### 対象
- Step: S02
- AC/EC: AC-002, EC-001, EC-002, EC-003

#### 実施内容
- `infra/deps_reader.py` を `.meta.json` only reader に切り替え、`schema_version` を型込みで厳密検証するよう補強した。
- `tests/cli_runtime/test_deps.py` と `tests/cli_runtime/test_sync.py` の dependency fixture を `.meta.json` ベースへ移行し、missing-field default / no-fallback / schema error / schema_version missing/bool / unresolved / shorthand compile / empty expansion warning / downstream smoke を固定した。
- implementation review で `.meta.json` cutover後に `deps.json` fixture が残っていた回帰を検出し、追加で test module 全体を `.meta.json` 契約へ追従させた。
- main workspace で `python -m unittest -v tests.cli_runtime.test_deps tests.cli_runtime.test_sync` を実行し、80 tests / OK を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_deps tests.cli_runtime.test_sync

- implementation review: pass
- QA review: pass（P2 の追加否定ケース提案のみ）
- 80 tests / OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py` - `.meta.json` only read path と strict schema guard へ更新
- `tests/cli_runtime/test_deps.py` - dependency-focused fixture と fail-closed regression を `.meta.json` 契約へ移行
- `tests/cli_runtime/test_sync.py` - downstream smoke を `.meta.json` 契約へ移行

#### コミット
- `793fb72` `test(iss-00060): .meta.json依存readerを整列`

#### メモ
- RG1 verdict: pass
- QG1 verdict: pass
- reviewer から P2 として、top-level 非 object / `depends_on: [{}]` の否定ケースを追加すると将来の fail-closed 回帰保護がさらに強くなる提案があった

---

### 2026-04-10 05:52 - 06:12

#### 対象
- Step: S90, S99
- AC/EC: AC-001, AC-002, AC-003, final exit contract

#### 実施内容
- `test_active.py` の dependency fixture を `.meta.json` 契約へ移行し、`active set` の deps guard 系 downstream smoke を reader cutover に追従させた。
- `tests/cli_runtime/test_deps.py` に no-fallback regression と fail-closed 追加否定ケース（missing `schema_version` / root non-object / `depends_on: [{}]`）を補強した。
- provider-side `reference_deps.md` と dogfooding copy の整合を再確認し、差分が無いことを確認した。
- `python -m unittest -v tests.cli_runtime.test_deps tests.cli_runtime.test_sync tests.cli_runtime.test_active` を main workspace で実行し、117 tests / OK を確認した。
- final diff review を実施し、code reviewer / QA reviewer ともに pass を確認した。

#### 実行コマンド / 結果
```bash
diff -u src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md
python -m unittest -v tests.cli_runtime.test_deps tests.cli_runtime.test_sync tests.cli_runtime.test_active

- provider/dogfooding docs diff: なし
- 117 tests / OK
- final code review: pass
- final QA review: pass
```

#### 変更したファイル
- `tests/cli_runtime/test_active.py` - active deps guard の dependency fixture を `.meta.json` 契約へ移行
- `tests/cli_runtime/test_deps.py` - no-fallback と fail-closed 追加否定ケースを補強
- `spec-dock/active/issue/report.md` - S90/S99 の evidence と close-ready verdict を記録

#### コミット
- `2b4acc6` `test(iss-00060): active依存ガード回帰を補強`

#### メモ
- S90 verdict: provider-side docs update 済み、dogfooding copy と整合
- S99 verdict: final diff review pass
- reviewer から P2 として、schema fail-closed 分岐の追加否定ケース強化は今後も継続推奨

---

## 遭遇した問題と解決 (任意)
- 問題: 初回 S01 spec review で issue spec と epic design/plan の間に raw grammar と provider-side docs ownership timing の不整合があった
  - 解決: epic design/plan を issue spec と整列させ、reference docs へ `.meta.json` contract と owner boundary note を反映したうえで再レビューを実施し pass を確認した

## 学んだこと (任意)
- issue-level spec が十分でも、epic-level owner timing が揃っていないと review gate は fail する
- provider-side docs を T1 deliverable として明示しておくと T3 cutover evidence の owner split が明瞭になる

## 今後の推奨事項 (任意)
- `infra/deps_reader.py` の fail-closed 分岐は、将来の refactor でもテストから外れないよう継続して否定ケースを維持する
- T3 (`iss-00062`) では dogfooding checked-in data manual fix と `validate` / `sync` evidence を issue-level `report.md` に集約する

## 省略/例外メモ (必須)
- 全体回帰（`python -m unittest discover -v`）は未実施。issue plan の S02/S90/S99 に必要な focused suites と review gate は完了した
