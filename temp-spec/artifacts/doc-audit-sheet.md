# ドキュメント監査シート（README撤廃 / wrapper導線 / artifacts統一）

- 作成日: 2026-02-16
- 監査対象:
  - このツールのドキュメント（repo docs / packaged docs）
  - このツールが生成・提供するドキュメント（templates / skill）
- 監査観点:
  - C1: Node作成用 wrapper (`new-epic` / `new-issue` / `new-adr`) の導線説明が現仕様と一致しているか
  - C2: `artifacts/` が全レイヤー共通の補足資料置き場として説明されているか
  - C3: 新規ノードで `README.md` を生成しない仕様と矛盾していないか
  - C4: `discussions/` が必要以上に現行導線として案内されていないか（レガシー扱いに留まっているか）

| No | File | Category | 判定 | 指摘/確認結果 | 対応 |
|---:|---|---|---|---|---|
| 1 | `src/spec_dock/assets/spec_dock/docs/guide.md` | 配布ドキュメント | 要修正 | C1/C2/C3不整合。構造図に `artifacts/` と wrapper (`epics/new-epic`,`issues/new-issue`,`adrs/new-adr`) が未記載。README撤廃後のノード構造説明になっていない。 | 構造図と「作る（new/import）」節に wrapper導線・`artifacts/_template.md`・README非生成を追記。 |
| 2 | `src/spec_dock/assets/spec_dock/docs/README.md` | 配布ドキュメント | 軽微修正推奨 | 事実誤りはないが C1/C2 の新導線（各スコープ配下 wrapper 実行、`artifacts/_template.md`）が未記載。入口としては追記した方が一貫性が高い。 | 「コマンド早見」下に“生成後ノードでは `epics/new-epic` 等を使える”補足を追加。 |
| 3 | `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | 配布ドキュメント | 要修正 | C1/C2/C3不整合。`epics/new-epic` 導線、`artifacts/` の使い分け、README非生成の説明がない。 | 「作成後の運用」節に `epics/new-epic "<title>"` と `artifacts/_template.md` 利用方針を追記。 |
| 4 | `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | 配布ドキュメント | 要修正 | C1/C2/C3不整合。`issues/new-issue` 導線がなく、`artifacts/` の利用規約が未記載。README非生成後のノード運用説明が不足。 | Epic作成後の「配下 Issue 追加は `issues/new-issue`」と `artifacts/_template.md` 利用を追記。 |
| 5 | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | 配布ドキュメント | 軽微修正推奨 | 主要フローは整合。C2観点で `spec-dock/active/issue/artifacts/`（補足資料）運用が未言及。README依存はなし。 | 「計画/記録」付近に `artifacts/` への補足資料記録ルールを1段追加。 |
| 6 | `src/spec_dock/assets/spec_dock/docs/workflow_adr.md` | 配布ドキュメント | 要修正 | C1不整合。`./spec new adr --{issue|epic|initiative}` のみ記載で、新仕様の `adrs/new-adr "<title>"` 導線が未反映。 | 推奨導線を wrapper 実行に変更し、既存 `./spec new adr ...` は代替手段として併記。 |
| 7 | `src/spec_dock/assets/spec_dock/docs/reference_github.md` | 配布ドキュメント | 軽微修正推奨 | 大枠は整合。C1観点で wrapper (`new-epic`/`new-issue`) 実行時の `gh` 不在ハンドリング（自動フォールバックしない・直接コマンド案内）への言及がない。 | 「よくある失敗」に wrapper実行時の挙動を1項追加。 |
| 8 | `src/spec_dock/assets/spec_dock/docs/reference_naming.md` | 配布ドキュメント | 修正不要 | C1-C4の直接矛盾なし。タイトル/slug制約の説明は wrapper 経由でも有効（runtime委譲）で整合。 | 変更不要。 |
| 9 | `src/spec_dock/assets/spec_dock/docs/reference_sync.md` | 配布ドキュメント | 修正不要 | C1-C4の直接矛盾なし。`sync` の責務説明は今回変更範囲（wrapper/artifacts/README撤廃）と独立。 | 変更不要。 |
| 10 | `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` | 提供ドキュメント（Skill） | 要修正 | C1不整合。ADR作成が旧導線（`spec-dock new adr --issue ...`）のみ。新仕様の `adrs/new-adr "<title>"` を優先導線として示せていない。 | wrapper優先導線を追記し、既存コマンドは代替として併記。 |
| 11 | `src/spec_dock/assets/spec_dock/templates/README.md` | 提供ドキュメント（Template案内） | 軽微修正推奨 | 主要説明は有効。C1/C2の観点で、配下テンプレに `new-*` wrapper と `artifacts/_template.md` が含まれる点を追記すると利用者理解が向上。 | テンプレ項目に wrapper/artifacts テンプレの説明を追加。 |
| 12 | `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。README前提や`discussions/`前提を持たない汎用テンプレ。 | 変更不要。 |
| 13 | `src/spec_dock/assets/spec_dock/templates/initiative/design.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。READMEや`discussions/`依存がなく、`ADR index` 前提も維持可能。 | 変更不要。 |
| 14 | `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。README依存や旧導線依存なし。 | 変更不要。 |
| 15 | `src/spec_dock/assets/spec_dock/templates/initiative/report.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 16 | `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 17 | `src/spec_dock/assets/spec_dock/templates/epic/design.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 18 | `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 19 | `src/spec_dock/assets/spec_dock/templates/epic/report.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 20 | `src/spec_dock/assets/spec_dock/templates/issue/requirement.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 21 | `src/spec_dock/assets/spec_dock/templates/issue/design.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 22 | `src/spec_dock/assets/spec_dock/templates/issue/plan.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 23 | `src/spec_dock/assets/spec_dock/templates/issue/report.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。 | 変更不要。 |
| 24 | `src/spec_dock/assets/spec_dock/templates/initiative/artifacts/_template.md` | 提供ドキュメント（Template） | 修正不要 | C2/C3整合。補足資料の用途と運用が明確で、README代替として成立。 | 変更不要。 |
| 25 | `src/spec_dock/assets/spec_dock/templates/epic/artifacts/_template.md` | 提供ドキュメント（Template） | 修正不要 | C2/C3整合。補足資料の用途と運用が明確で、README代替として成立。 | 変更不要。 |
| 26 | `src/spec_dock/assets/spec_dock/templates/issue/artifacts/_template.md` | 提供ドキュメント（Template） | 修正不要 | C2/C3整合。補足資料の用途と運用が明確で、README代替として成立。 | 変更不要。 |
| 27 | `src/spec_dock/assets/spec_dock/templates/adr.md` | 提供ドキュメント（Template） | 修正不要 | C1-C4の矛盾なし。ADR本文テンプレは導線変更と独立。 | 変更不要。 |
| 28 | `README.md` | ツール本体ドキュメント | 軽微修正推奨 | 現仕様と矛盾はないが、C1/C2/C3の更新（生成ノード内 wrapper と `artifacts/_template.md`、README非生成）を明示していない。 | 「What it creates」または「Usage(local scripts)」に新導線を補足。 |
| 29 | `docs/github-issue-integration.md` | ツール本体ドキュメント | 軽微修正推奨 | 記述自体は正しいが C1観点で「wrapperはruntimeを呼ぶ薄い導線」である点が未記載。 | 冒頭の対象に `templates/*/new-*` の位置づけを1段補足。 |
| 30 | `docs/sync-aggregation.md` | ツール本体ドキュメント | 修正不要 | `sync` 内部仕様の説明であり、C1-C4の変更範囲と独立。README非生成との矛盾なし。 | 変更不要。 |
| 31 | `docs/discussion-sheets/README.md` | ツール本体ドキュメント（設計メモ） | 修正不要 | 過去設計判断のアーカイブであり、現行運用導線を規定する文書ではない。C1-C4と矛盾する記述なし。 | 変更不要。 |
| 32 | `docs/discussion-sheets/01_tree_root_location.md` | ツール本体ドキュメント（設計メモ） | 修正不要 | 過去の設計意思決定記録。現行仕様との差分管理対象ではなく、C1-C4矛盾なし。 | 変更不要。 |
| 33 | `docs/discussion-sheets/02_current_pointer_design.md` | ツール本体ドキュメント（設計メモ） | 修正不要 | アーカイブ文書。文中に README 例示があるが「設計検討時点の記述」であり現行導線文書ではない。 | 変更不要（必要なら将来 `historical` 注記だけ追加）。 |
| 34 | `docs/discussion-sheets/03_source_of_truth_and_sync.md` | ツール本体ドキュメント（設計メモ） | 修正不要 | アーカイブ文書であり、C1-C4変更との直接矛盾なし。 | 変更不要。 |
| 35 | `src/spec_dock/assets/spec_dock/system/active-none/README.md` | 提供ドキュメント（placeholder） | 修正不要 | README撤廃の対象外（active未設定時のplaceholder表示）。現仕様と整合。 | 変更不要。 |
| 36 | `src/spec_dock/assets/spec_dock/system/active-none/initiative/README.md` | 提供ドキュメント（placeholder） | 修正不要 | README撤廃の対象外。active未設定時の案内として必要。 | 変更不要。 |
| 37 | `src/spec_dock/assets/spec_dock/system/active-none/epic/README.md` | 提供ドキュメント（placeholder） | 修正不要 | README撤廃の対象外。active未設定時の案内として必要。 | 変更不要。 |
| 38 | `src/spec_dock/assets/spec_dock/system/active-none/issue/README.md` | 提供ドキュメント（placeholder） | 修正不要 | README撤廃の対象外。active未設定時の案内として必要。 | 変更不要。 |

## 集計サマリー

- 総確認ファイル数: 38
- 要修正: 5
- 軽微修正推奨: 6
- 修正不要: 27

## 優先修正対象（実施順）

1. `src/spec_dock/assets/spec_dock/docs/guide.md`
2. `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
3. `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
4. `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
5. `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
6. `src/spec_dock/assets/spec_dock/docs/README.md`（軽微）
7. `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`（軽微）
8. `src/spec_dock/assets/spec_dock/docs/reference_github.md`（軽微）
9. `src/spec_dock/assets/spec_dock/templates/README.md`（軽微）
10. `README.md`（軽微）
11. `docs/github-issue-integration.md`（軽微）

## 修正実施ログ（今回）

- 実施日時: 2026-02-16
- 実施方針: 監査で `要修正` / `軽微修正推奨` と判定した11ファイルをすべて更新

### 修正済み

1. `src/spec_dock/assets/spec_dock/docs/guide.md`
2. `src/spec_dock/assets/spec_dock/docs/README.md`
3. `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
4. `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
5. `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
6. `src/spec_dock/assets/spec_dock/docs/workflow_adr.md`
7. `src/spec_dock/assets/spec_dock/docs/reference_github.md`
8. `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
9. `src/spec_dock/assets/spec_dock/templates/README.md`
10. `README.md`
11. `docs/github-issue-integration.md`

### 未対応（次回）

- なし
