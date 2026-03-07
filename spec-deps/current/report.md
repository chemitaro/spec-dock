---
種別: 実装報告書（Issue）
ID: "iss-00016"
タイトル: "Codex skills を hub + leaf 構成へ再編する"
関連GitHub: ["#16, https://github.com/chemitaro/spec-dock/issues/16"]
状態: "draft | approved"
作成者: "chemitaro"
最終更新: "2026-03-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00016 Codex skills を hub + leaf 構成へ再編する — 実装報告（LOG）

## 実装サマリー (任意)
- S01 で、installer が hub + 4 leaf の managed full set を導入できる土台を追加した。
- 4 つの leaf skill asset を配布物へ追加し、`init` 後の導入結果と bundled asset の存在をテストで固定した。

## 実装記録（セッションログ） (必須)

### 2026-03-08 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, AC-007

#### 実施内容
- `src/spec_dock/cli.py` に managed skill manifest を追加し、`_install_skill()` を 5 skill 導入へ拡張した。
- 4 つの leaf skill asset を最小骨格で追加した。
- `tests/test_cli.py` を更新し、`init` 後の 5 skill 導入と bundled asset 存在保証を検証した。
- `code_reviewer` に S01 差分要約レビューを依頼し、ブロッカーなしの承認レベル判定を得た。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_init_creates_expected_structure \
  tests.test_cli.TestCli.test_init_no_skill_skips_skill_install \
  tests.test_cli.TestCli.test_bundled_skill_assets_cover_managed_manifest \
  tests.test_cli.TestCli.test_update_keeps_initiatives_by_default

Ran 4 tests in 0.055s
OK
```

#### 変更したファイル
- `src/spec_dock/cli.py` - managed skill manifest と multi-skill install の初期実装
- `tests/test_cli.py` - S01 の導入結果と bundled asset を検証するテスト更新
- `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md` - leaf skill 骨格追加
- `src/spec_dock/assets/codex_skills/spec-dock-adr-facilitation/SKILL.md` - leaf skill 骨格追加

#### コミット
- pending

#### メモ
- reviewer 結果: `overall_correctness = patch is correct`, findings なし（要約ベースの S01 スコープ確認）
- `--no-skill` 廃止、migration / ownership boundary、routing 文面完成、README/docs 更新は S02 以降へ意図的に deferred

---

### 2026-03-06 HH:MM - HH:MM

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- 該当なし
