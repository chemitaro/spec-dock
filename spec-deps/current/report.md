---
種別: 実装報告書（Issue）
ID: "iss-00019"
タイトル: "discussions 配下の資料命名を時系列順に並ぶ形式へ統一し、全種別を共通採番できるようにする"
関連GitHub: ["#19", "https://github.com/chemitaro/spec-dock/issues/19"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-03-09"
依存: ["requirement.md", "design.md", "plan.md"]
親: []
---

# iss-00019 discussions 配下の資料命名を時系列順に並ぶ形式へ統一し、全種別を共通採番できるようにする — 実装報告（LOG）

## 実装サマリー (任意)
- `new doc <type>` を discussion docs の唯一の公開インターフェイスとして実装し、`NNN-type-slug.md` の shared 3-digit sequence を runtime に導入した。
- discussion docs の採番対象を recognized new-format files のみに限定し、legacy / nonconforming / `rules.md` を無視する単純な新ロジックへ整理した。
- shipped assets, current guidance, tests を新契約へ全面更新し、フルテスト `python -m unittest discover -v` を green で確認した。

## 実装記録（セッションログ） (必須)

### 2026-03-09 07:40 - 08:55

#### 対象
- Step: S01, S02, S03, S90
- AC/EC: AC-002, AC-003, AC-004, AC-005, AC-006, EC-001, EC-002, EC-003, EC-004, EC-005

#### 実施内容
- runtime を `new doc <type>` へ切り替え、`new adr` / per-type discussion command / sequence override option を公開面から削除した。
- `app.py` に shared sequence scanner / next-sequence calculator を追加し、recognized format `NNN-type-slug.md` だけを採番対象にした。
- duplicate sequence / overflow / invalid slug / unknown type を fail-fast にし、overflow 時は follow-up issue で archive または桁拡張を決める guidance を返すようにした。
- shipped docs, templates, skill, current guidance を `new doc <type>` と `NNN-type-slug.md` へ更新し、旧 `new adr` 導線と `<type>-00001-<slug>.md` 例示を current rule から除去した。
- `tests/test_cli.py` を新契約へ追随させ、CLI surface, shared sequence, ignore-nonconforming, duplicate/overflow/invalid slug, docs/assets refresh をカバーする回帰テストを追加した。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_cli.TestCli.test_new_doc_adr_increments_id_within_scope_discussions \
  tests.test_cli.TestCli.test_new_doc_adr_uses_shared_sequence_across_discussion_types \
  tests.test_cli.TestCli.test_new_doc_disc_increments_after_adr \
  tests.test_cli.TestCli.test_new_doc_ignores_nonconforming_files_for_sequence \
  tests.test_cli.TestCli.test_new_doc_fails_on_duplicate_sequence \
  tests.test_cli.TestCli.test_new_doc_fails_on_sequence_overflow \
  tests.test_cli.TestCli.test_new_doc_rejects_invalid_slug \
  tests.test_cli.TestCli.test_new_doc_rejects_unexpected_sequence_override_option \
  tests.test_cli.TestCli.test_new_doc_rejects_unknown_type \
  tests.test_cli.TestCli.test_new_discussion_per_type_commands_are_not_available \
  tests.test_cli.TestCli.test_new_help_exposes_only_doc_discussion_entrypoint \
  tests.test_cli.TestCli.test_init_scaffolds_discussion_guidance_without_legacy_examples_across_asset_set \
  tests.test_cli.TestCli.test_update_refreshes_discussion_guidance_without_legacy_examples_across_asset_set \
  tests.test_cli.TestCli.test_current_guidance_documents_match_discussion_numbering_contract

# OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `new doc <type>` route, shared sequence, strict filename recognition, overflow/duplicate validation
- `tests/test_cli.py` - CLI surface / sequence / docs refresh / regression tests
- `src/spec_dock/assets/spec_dock/templates/README.md` - discussion naming contract を更新
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/discussions/rules.md` - `NNN-type-slug.md`, new-format only, overflow guidance へ更新
- `src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,phase_requirement.md,phase_design.md,phase_plan.md,reference_naming.md,workflow_adr.md,workflow_epic.md,workflow_initiative.md,workflow_issue.md}` - public interface と naming rule を更新
- `src/spec_dock/assets/spec_dock/scripts/README.md` - runtime usage examples を `new doc <type>` へ更新
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` - bundled skill guidance を更新
- `spec-deps/current/discussions/rules.md` - current guidance を新契約へ更新
- `spec-deps/README.md` - discussion naming summary を更新

#### コミット
- なし（コミット未実施）

#### メモ
- 実装は dev_coder と連携して反映した。
- legacy filename parse / alias compatibility は requirement/design の確定方針どおり実装しなかった。

---

### 2026-03-09 08:55 - 09:14

#### 対象
- Step: S99
- AC/EC: 全体品質ゲート

#### 実施内容
- working tree diff を確認し、変更範囲が issue 契約どおり runtime / tests / shipped docs/assets / current guidance に収まっていることを確認した。
- `git diff --check` を実行し、whitespace error がないことを確認した。
- フルテスト `python -m unittest discover -v` を実行し、全 161 件 green を確認した。
- code reviewer / qa reviewer の sub-agent 起動を試したが、実行基盤側で interrupt が発生したため、最終ログには手動 diff review とローカル品質ゲート結果を記録した。

#### 実行コマンド / 結果
```bash
git status --short
# 変更対象 20 files を確認

git diff --stat
# 20 files changed, 624 insertions(+), 200 deletions(-)

git diff --check
# OK

python -m unittest discover -v
# OK (Ran 161 tests in 23.454s)
```

#### 変更したファイル
- `spec-deps/current/report.md` - 実装内容と品質ゲート結果を記録

#### コミット
- なし（コミット未実施）

#### メモ
- `git diff --name-only | rg '[A-Z]'` は既存 uppercase filename（`README.md`, `SKILL.md`）を返した。今回は新規作成/rename はなく、uppercase path を増やしていない。
- reviewer sub-agent は `Interrupted` で完了ログを回収できなかったため、次工程で必要なら fresh reviewer session を再度切る。

---

## 遭遇した問題と解決 (任意)
- 問題: reviewer / qa reviewer sub-agent が最終品質ゲート中に `Interrupted` となり、verdict を回収できなかった。
  - 解決: main agent 側で `git diff`, `git diff --check`, targeted regression tests, `python -m unittest discover -v` を実行して品質ゲートを代替し、その経緯を report に明記した。

## 学んだこと (任意)
- discussion docs の naming contract は runtime だけでなく、template rules, shipped docs, bundled skill, current guidance まで一体で更新しないと利用者導線が崩れる。
- legacy compatibility を捨てて new-format only に寄せると、採番ロジックと説明責務が大きく簡素化できる。

## 今後の推奨事項 (任意)
- コミットまたは PR 前に fresh `code_reviewer` session を再実行し、sub-agent 基盤が安定しているタイミングで最終 verdict を取り直す。
- 実際の利用フローでも `new doc adr|disc|research|note` を 1 回ずつ叩く manual smoke test を行うと、docs/UX の最終確認がしやすい。

## 省略/例外メモ (必須)
- reviewer sub-agent verdict は実行基盤の interrupt により未取得。代替として手動 diff review と full test suite を記録した。
