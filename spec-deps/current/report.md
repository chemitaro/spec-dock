---
種別: 実装報告書（Issue）
ID: "iss-00019"
タイトル: "discussions 配下の資料命名を時系列順に並ぶ形式へ統一し、全種別を共通採番できるようにする"
関連GitHub: ["#19", "https://github.com/chemitaro/spec-dock/issues/19"]
状態: "approved"
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
- code reviewer / qa reviewer の sub-agent 起動を試したが、実行基盤側で interrupt が発生したため、当初は手動 diff review とローカル品質ゲート結果を記録した。

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
- reviewer sub-agent は `Interrupted` で完了ログを回収できなかったが、その後 Codex CLI 組み込み review で「blocking correctness issues なし」の verdict を確認した。

---

### 2026-03-09 12:18 - 12:19

#### 対象
- Step: S99
- AC/EC: 全体品質ゲート

#### 実施内容
- ユーザー提供の Codex CLI 組み込み review 結果を確認した。
- review verdict は「blocking correctness issues なし」「new `new doc <type>` flow / shared numbering / asset updates / regression tests は internally consistent」「full test suite passes」であった。
- これにより S99 の `reviewer 承認レベル` を満たしたため、`plan.md` と `report.md` の状態を完了に更新した。

#### 実行コマンド / 結果
```text
review result:
I did not find any blocking correctness issues in the changes relative to the merge base.
The new `new doc <type>` flow, shared discussion numbering, asset updates,
and regression tests appear internally consistent, and the full test suite passes.
```

#### 変更したファイル
- `spec-deps/current/plan.md` - S99 を完了へ更新
- `spec-deps/current/report.md` - review verdict と完了状態を記録

#### コミット
- `50443b9` `feat(discussion-doc): 議論資料の共通採番とnew doc導線を実装`

#### メモ
- reviewer verdict は external review source として扱い、sub-agent interrupt による欠損を補完した。

---

### 2026-03-09 12:19 - 12:23

#### 対象
- Step: 追加 manual test
- AC/EC: AC-002, AC-003, AC-004, EC-003, EC-005

#### 実施内容
- `manual-tests/spec-dock-deps/trial-2026-03-09-discussion-doc-sequence` に手動検証環境を作成した。
- `PYTHONPATH=src python -m spec_dock.cli init ...` で trial repo を初期化し、`new initiative` → `new epic` → `new issue` をローカル作成した。
- `new doc disc` → `new doc adr` → `new doc research` → `new doc note` を順に実行し、`001` から `004` まで shared sequence で並ぶことを確認した。
- `discussions/` に `adr-00001-legacy.md` と `050-bogus-ignored.md` を手動配置した後でも、次番号が `003`, `004` と継続し、legacy/nonconforming files を採番対象に含めないことを確認した。
- `new adr` が invalid choice で拒否されること、`new doc adr --slug Bad!Slug` が validation error で拒否されることを確認した。

#### 実行コマンド / 結果
```bash
PYTHONPATH=src python -m spec_dock.cli init manual-tests/spec-dock-deps/trial-2026-03-09-discussion-doc-sequence
# spec-dock: ok (init)

./spec-dock/scripts/spec-dock new initiative --no-github --title 'Discussion sequencing manual test'
# ok

./spec-dock/scripts/spec-dock new epic --no-github --initiative init-local-00001 --title 'Manual epic for sequencing'
# ok

./spec-dock/scripts/spec-dock new issue --no-github --epic epic-local-00001 --title 'Manual issue for doc sequencing'
# ok

./spec-dock/scripts/spec-dock new doc disc --issue iss-local-00001 --title 'Open implementation questions'
./spec-dock/scripts/spec-dock new doc adr --issue iss-local-00001 --title 'Adopt shared numbering'
./spec-dock/scripts/spec-dock new doc research --issue iss-local-00001 --title 'Check legacy handling'
./spec-dock/scripts/spec-dock new doc note --issue iss-local-00001 --title 'Manual smoke notes'
# 001-disc / 002-adr / 003-research / 004-note を確認

./spec-dock/scripts/spec-dock new adr --issue iss-local-00001 --title 'Should fail'
# invalid choice: 'adr'

./spec-dock/scripts/spec-dock new doc adr --issue iss-local-00001 --title 'Bad slug doc' --slug 'Bad!Slug'
# --slug is invalid
```

#### 変更したファイル
- `spec-deps/current/report.md` - manual test 結果を追記

#### コミット
- `50443b9` `feat(discussion-doc): 議論資料の共通採番とnew doc導線を実装`

#### メモ
- trial repo の場所: `manual-tests/spec-dock-deps/trial-2026-03-09-discussion-doc-sequence`
- `new doc --help` も `{adr,disc,research,note}` の位置引数だけを公開し、override option は露出していなかった。

---

## 遭遇した問題と解決 (任意)
- 問題: reviewer / qa reviewer sub-agent が最終品質ゲート中に `Interrupted` となり、verdict を回収できなかった。
  - 解決: main agent 側で `git diff`, `git diff --check`, targeted regression tests, `python -m unittest discover -v` を実行して品質ゲートを代替し、その後ユーザー提供の Codex CLI 組み込み review verdict で最終承認を補完した。

## 学んだこと (任意)
- discussion docs の naming contract は runtime だけでなく、template rules, shipped docs, bundled skill, current guidance まで一体で更新しないと利用者導線が崩れる。
- legacy compatibility を捨てて new-format only に寄せると、採番ロジックと説明責務が大きく簡素化できる。

## 今後の推奨事項 (任意)
- 実際の利用フローでも `new doc adr|disc|research|note` を 1 回ずつ叩く manual smoke test を行うと、docs/UX の最終確認がしやすい。

## 省略/例外メモ (必須)
- reviewer sub-agent verdict は実行基盤の interrupt により未取得だったが、最終的にはユーザー提供の Codex CLI review verdict で補完した。
