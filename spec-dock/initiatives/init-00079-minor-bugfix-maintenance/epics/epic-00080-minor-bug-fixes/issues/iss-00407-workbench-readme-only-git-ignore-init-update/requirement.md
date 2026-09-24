---
種別: 要件定義書（Issue）
ID: "iss-00407"
タイトル: "Fix Workbench Readme Only Git Ignore Contract"
関連GitHub: ["#407"]
状態: "draft"
最終更新: "2026-09-24"
親: ["epic-00080", "init-00079"]
---

# iss-00407 Fix Workbench Readme Only Git Ignore Contract — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的
SpecDock が新規・既存 workspace に README-only の Workbench Git ignore 契約を配布し、通常の Git 操作で一時 payload が追跡候補にならない状態を保つ。各 `.workbench/` 直下の `README.md` は例外として Git 追跡可能にする。

## 背景
- provider とこの dogfooding workspace の `spec-dock/.gitignore` には、README だけを再包含する規則が現存する。削除されたとの事実は確認されていない。
- 現行 installer の既存 workspace 更新は固定6ディレクトリだけを置換し、`spec-dock/.gitignore` の欠落・旧版を修復しない。部分的な fresh init 後に欠落したまま更新できることも現行テストが固定している。
- fresh init では root の `.workbench/README.md` がテンプレート内に留まり、要求された `spec-dock/.workbench/README.md` が生成されないことを実行確認した。
- 既存利用先で既に Git 追跡された Workbench payload の追跡解除は利用者が各 project で手動実施する。本 Issue は Epic #80 の repo-local な配布契約の修正に閉じる。

## 観測可能な要件
- RQ-407-01: 新規 workspace の `spec-dock/.gitignore` は、root / Initiative / Epic / Issue の各 `.workbench/` において、直下の正確な `README.md` のみを通常の Git 追跡候補とし、それ以外の entry を ignore する。
- RQ-407-02: fresh init は root の `spec-dock/.workbench/README.md` を生成する。新規 node にも同じ README を生成し、既存 root / node には通常 update で backfill しない。
- RQ-407-03: 既存 workspace の update と `init --force` は、欠落または確認済みの旧版の `spec-dock/.gitignore` を現行契約へ到達させる。独自編集されたファイルは変更しない。
- RQ-407-04: ignore 規則の実効結果を実 Git repository で検証できる。Workbench payload の内容は診断のために読み取らない。

## スコープ
- 対象: provider 側の配布 asset、installer の fresh/update 経路、必要な shipped docs、dogfooding projection、対応する回帰テスト。
- 維持: Workbench は optional・temporary・worktree-local・non-canonical。README 以外の payload を自動 copy / sync しない既存境界、および既存 scope への no-backfill。
- 対象外: 各利用先 project の既追跡 payload の `git rm --cached`、履歴改変、既存 Workbench payload の削除・移動、`workbench copy` の source-wins 仕様変更、強制的な `git add -f` の全面禁止。

## 失敗・境界条件
- `.gitignore` が欠落、確認済みの旧版、利用先で独自編集された状態を区別する。独自編集は無断で上書きせず、通常 update による修復対象外とする。
- 親階層の ignore 規則も効くため、配布 asset の byte 一致だけで実効結果を保証したと扱わない。
- `.gitignore` は既に index に入った payload と明示的な強制 add を追跡対象から外せない。この限界を docs と検証結果で明示する。

## 受け入れ条件
- AC-407-01: fresh init 後に `spec-dock/.gitignore` と root README が存在し、root / 新規 node の README だけが通常の Git add 候補となり、一時 payload と nested README は ignored になる。
- AC-407-02: `.gitignore` が欠落または既知の旧版である既存 workspace は、通常 update 後に README-only の実効規則を持つ。未知の独自編集は無断で変更されない。
- AC-407-03: update は既存 Workbench の名前・内容・mtime を変更せず、既存 root / node の README を backfill しない。
- AC-407-04: provider asset から dogfooding 側への正規更新経路と、fresh / update / force-init の実 Git テストで契約を確認する。

## 制約・前提
- 既存利用先の追跡済み payload への Git 操作は利用者が手動で行い、provider は自動移行しない。
- `spec-dock/.gitignore` の独自編集を更新せず保持する。利用先の既追跡 payload は利用者が手動で確認する。
