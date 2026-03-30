---
種別: 実装報告書（Issue）
ID: "iss-00037"
タイトル: "Migration Guardrails and Validation Hardening"
関連GitHub: ["#37"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00037 Migration Guardrails and Validation Hardening — 実装報告（LOG）

## 実装サマリー (任意)
- S01 として、migration boundary の clause-1/2/3 について current evidence・missing evidence・owner boundary を `iss-00037` の report に固定した。
- `iss-00037` は migration-boundary evidence の final closure owner であり、S02 では clause-2 truthfulness に必要な最小 README correction（`README.md` と `spec-dock/docs/README.md`）も吸収する一方、full docs parity は `iss-00038`、stale-contract/test realignment は `iss-00040` に残す前提を明記した。
- S02 として、clause-1/2 wording gap を最小 docs correction で閉じ、provider/dogfooding mirror を current runtime contract に整列させた。reject / fail-fast / no-auto-rename の根拠は既存テストを再利用して evidence として束ね、追加テストは行っていない。

## 実装記録（セッションログ） (必須)

### 2026-03-30

#### 対象
- Step: S01
- AC/EC: AC-004, EC-001
- 備考: AC-001〜AC-003 を閉じるための inventory / ownership baseline

#### 実施内容
- active issue docs を再読し、S01 で固定すべき clause inventory と owner boundary を確認した。
- predecessor reports・current docs・current tests から clause-1/2/3 の current evidence と missing evidence を抽出し、`iss-00037` が閉じる gap だけを report に整理した。
- `iss-00038` の full docs parity と `iss-00040` の stale-contract/test realignment を本 issue に吸収しない ownership lock を記録しつつ、README contradiction の最小 correction は S02 で本 issue が持つと明文化した。

#### evidence inventory
- clause-1（no forced backward compatibility / legacy sequential grandfathering）
  - current evidence:
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md` §4.4 に、legacy sequential docs は grandfathered・自動 rename しない・新 contract で sequence basename を再利用しない旨がある。
    - dogfooding mirror `spec-dock/docs/reference_naming.md` も同 wording を保持している。
    - tests:
      - `tests/cli_runtime/test_new.py::test_new_doc_preserves_legacy_files_without_reusing_sequence_names`
      - `tests/cli_runtime/test_validate.py::test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files`
      - `tests/cli_runtime/test_validate.py::test_validate_rejects_malformed_discussion_doc_candidates`
  - missing evidence:
    - backward compatibility は grandfathering に限るのであって、forced compatibility や auto-rename ではないと reviewer が一読で分かる wording がまだ薄い。
  - owner boundary:
    - `iss-00037` は clause-1 evidence mapping と final closure bundle を持つ。
    - clause-1 の minimal wording hardening は後続 step で扱うが、README を含む broad docs parity refresh は `iss-00038` に残す。
- clause-2（no in-place auto-migration guarantee for `spec-dock update` / reject-fail-fast boundary）
  - current evidence:
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md` に、import preflight validate は副作用なしで失敗すること、legacy `meta.json` tree は unsupported で `.meta.json` への手動移行が必要なことが明記されている。
    - dogfooding mirror `spec-dock/docs/reference_github.md` も同 wording を保持している。
    - current create / import / validate reject evidence により、legacy mismatch が auto-migrate ではなく fail-fast する境界は既に観測可能である。
    - tests:
      - `tests/cli_runtime/test_new.py::test_new_fails_preflight_on_legacy_meta_without_creating_nodes`
      - `tests/cli_runtime/test_validate.py::test_validate_rejects_legacy_unscoped_issue_linkage`
      - `tests/cli_runtime/test_validate.py::test_sync_fails_preflight_on_partially_scoped_issue_linkage`
  - missing evidence:
    - parent epic の clause-2 acceptance を issue docs だけで判定できる形として、`README.md` / `spec-dock/docs/README.md` / `reference_github.md` の named docs diff と current create / import / validate reject evidence を 1 セットで束ねる説明がまだ不足している。
  - owner boundary:
    - `iss-00037` は migration-boundary wording と reject/fail-fast evidence の close owner であり、S02 で `README.md` と `spec-dock/docs/README.md` の最小 contradiction correction も吸収する。
    - `iss-00037` は migration tooling の追加 owner ではなく、parent epic clause-2 は新しい update runtime path なしで閉じる。
    - docs parity の全面同期は `iss-00038` に残す。
- clause-3（non-destructive / no silent auto-repair）
  - current evidence:
    - 上記 clause-2 系 tests により、legacy/malformed linkage は `new` で write 前に reject され、`sync` でも preflight fail-fast することが観測できる。
    - `tests/cli_runtime/test_validate.py::test_sync_fails_preflight_on_partially_scoped_issue_linkage` は `--force` でも partial-scope linkage を通さない境界の current evidence になっている。
  - missing evidence:
    - fail-fast / warning / no-auto-repair / no-write の reviewer-facing mapping がまだ散在しており、targeted validation evidence と command results での束ね直しが必要である。
  - owner boundary:
    - `iss-00037` は non-destructive boundary の最終 evidence packaging owner を持つ。
    - stale-contract/test realignment 自体は `iss-00040` の ownership のままであり、本 issue では再実装しない。

#### 実行コマンド / 結果
```bash
view spec-dock/active/issue/report.md
view spec-dock/active/issue/requirement.md
view spec-dock/active/issue/design.md
view spec-dock/active/issue/plan.md
view spec-dock/initiatives/.../iss-00034.../report.md
view spec-dock/initiatives/.../iss-00035.../report.md
view spec-dock/initiatives/.../iss-00036.../report.md
view spec-dock/initiatives/.../iss-00040.../report.md
cd /srv/mount/spec-dock && find spec-dock/initiatives -path '*iss-00034*report.md' -o -path '*iss-00035*report.md' -o -path '*iss-00036*report.md' -o -path '*iss-00040*report.md' | sort
cd /srv/mount/spec-dock && git --no-pager grep -n "legacy sequential" -- src/spec_dock/assets/spec_dock/docs/reference_naming.md spec-dock/docs/reference_naming.md tests/cli_runtime/test_new.py tests/cli_runtime/test_validate.py
cd /srv/mount/spec-dock && git --no-pager grep -n "meta.json\|preflight\|unsupported\|manual move to \.meta\.json\|partial" -- src/spec_dock/assets/spec_dock/docs/reference_github.md spec-dock/docs/reference_github.md tests/cli_runtime/test_new.py tests/cli_runtime/test_validate.py tests/cli_runtime/test_sync.py

- active issue docs、predecessor reports、current reference docs、current cli_runtime tests の所在と clause evidence anchors を確認した。
- S01 は inventory / ownership lock のみのため、テスト実行はしていない。
```

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - clause-2 acceptance wording と README ownership を S02 scope に反映
- `spec-dock/active/issue/design.md` - named docs diff / reject evidence / README boundary correction owner を設計契約へ反映
- `spec-dock/active/issue/plan.md` - S02 target/files/review gate に README correction と clause-2 discharge note を反映
- `spec-dock/active/issue/report.md` - S01 summary / session log / clause evidence inventory / ownership boundary を記録

#### コミット
- 未コミット

#### メモ
- SG1/spec review（reviewer: `spec_reviewer`、scope: S01 readiness / issue docs after blocker fix）は pass。clause-2 discharge が named docs evidence と parent epic 向け current reject evidence に明示的に結び直され、`README.md` と `spec-dock/docs/README.md` の最小 correction も `iss-00037` S02 owner として明記されつつ、full docs parity は `iss-00038` に維持されることが確認された。
- README contradiction の最小 correction は S02 で `iss-00037` が吸収する。
- full docs parity は `iss-00038`、stale-contract realignment は `iss-00040` の ownership のまま維持する。

### 2026-03-30

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, EC-002
- 備考: clause-1/2 wording gap を最小 docs correction で閉じ、既存 reject / fail-fast / no-auto-rename tests を evidence として再利用

#### 実施内容
- `README.md`、provider asset docs、dogfooding mirror docs の wording を current runtime contract に合わせて見直し、clause-1/2 の reviewer-facing gap のみを最小差分で修正した。
- clause-1 について、legacy sequential naming は grandfathered だが新 contract へ自動 rename しないことを明確化し、no forced backward compatibility / no auto-rename の境界を docs で揃えた。
- clause-2 について、legacy / malformed state は update/import/validate 系で in-place auto-migration せず reject/fail-fast する契約に wording を寄せ、README と reference docs の説明差を解消した。
- provider surface（`src/spec_dock/assets/spec_dock/docs/...`）と dogfooding mirror（`spec-dock/docs/...`）を同内容で更新し、clause-1/2 wording gap を閉じた。
- 追加テストは行わず、既存の `tests.cli_runtime.test_new` / `tests.cli_runtime.test_runtime_new_s08` / `tests.cli_runtime.test_validate` を current evidence として再利用した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_s08 -v
# Ran 82 tests ... OK

python -m unittest tests.cli_runtime.test_validate -v
# Ran 33 tests ... OK
```

- 既存テスト群で reject / fail-fast / no-auto-rename evidence が維持されていることを確認した。
- S02 は docs-only diff として完了し、README・reference docs の wording が current runtime contract と整合した。

#### 変更したファイル
- `README.md` - clause-1/2 wording gap を閉じる最小 README correction
- `src/spec_dock/assets/spec_dock/docs/README.md` - provider asset README mirror を current contract に同期
- `spec-dock/docs/README.md` - dogfooding README mirror を current contract に同期
- `src/spec_dock/assets/spec_dock/docs/reference_github.md` - reject / fail-fast / no in-place auto-migration wording を調整
- `spec-dock/docs/reference_github.md` - dogfooding GitHub reference mirror を同期
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md` - legacy sequential grandfathering / no auto-rename wording を調整
- `spec-dock/docs/reference_naming.md` - dogfooding naming reference mirror を同期
- `spec-dock/active/issue/report.md` - S02 completion log / test evidence / review結果を記録

#### コミット
- 未コミット

#### メモ
- RG1/code review（reviewer: `code_reviewer`、scope: `S02 docs-only diff`）は pass。README / provider docs / dogfooding mirror の wording が current runtime contract と一致し、material defect は確認されなかった。
- review rationale: wording matches the current runtime contract; touched provider/dogfooding mirror surfaces are aligned; no material defects found.
- S02 は clause-1/2 wording gap を最小 docs correction で閉じた step であり、reject / fail-fast / no-auto-rename の追加実装や追加テストは不要と判断した。

---

## 遭遇した問題と解決 (任意)
- 問題: clause-1/2/3 の current evidence は repo 内に存在するが、reviewer が close 判定に使う owner boundary が report に固定されていなかった。
  - 解決: S01 で evidence inventory と ownership lock を clause 単位で整理し、後続 step が閉じる gap のみを明文化した。

## 学んだこと (任意)
- current contract 自体は先行 issue 群でかなり揃っており、`iss-00037` の中心責務は new behavior 追加より evidence packaging にある。
- S01 では gap を増やさず、`iss-00038` / `iss-00040` との ownership boundary を先に固定することが重要。

## 今後の推奨事項 (任意)
- S03 で clause-3 の fail-fast / warning / no-write mapping を targeted evidence と command results で補強する。

## 省略/例外メモ (必須)
- 該当なし
