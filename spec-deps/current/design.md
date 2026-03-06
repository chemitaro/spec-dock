---
種別: 設計書（Issue）
ID: "iss-00014"
タイトル: "ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合）"
関連GitHub: ["#14", "https://github.com/chemitaro/spec-dock/issues/14"]
状態: "approved"
作成者: "chemitaro"
最終更新: "2026-03-06"
依存: ["requirement.md"]
親: []
---

# iss-00014 ディスカッション資料の格納先を discussions/ に統一（adrs/artifacts の統合） — 設計（HOW）

## 目的・制約（要件から転記・圧縮） (必須)
- 目的: `adrs/` + `artifacts/` を `discussions/` に統合し、運用と導線を単純化する
- MUST:
  - 新規生成テンプレートは `discussions/` のみを作る
  - `discussions/` は `rules.md` を必ず含む（空ディレクトリにしない）
  - 配布パッケージ（`pip install .` / wheel / sdist）にも `discussions/rules.md` と `templates/discussions/*.md` が含まれる
  - `spec-dock new adr` は `discussions/` に出力する
  - `discussions/` 配下のファイルは「種類（prefix）+ 連番」で運用する（`adr-00001-...`, `disc-00001-...`, `research-00001-...`, `note-00001-...`）
  - テンプレは 1つのテンプレディレクトリ（複数ファイル）に集約し、type ごとのテンプレをコピー運用する旨を `rules.md` に明記する
  - `discussions/` 配下にスクリプト（`new-adr` 等）を置かない（ラッパ廃止）
- MUST NOT:
  - トップレベルの用途別ディレクトリを増やさない（`discussions/` で固定）
  - 後方互換性のための併走サポート・自動移行・レガシー走査を入れない
  - 旧 `adrs/` を採番・重複判定・集計対象として読み戻さない
- 非交渉制約:
  - ADR の採番（`adr-00001-...`）は維持
- 前提:
  - `discussions/` 内の分類は「ファイル名規約」と「frontmatter」のどちらか/併用で成立させる

---

## 既存実装/規約の調査結果（As-Is / 99.9%理解） (必須)
- 参照した規約/実装（根拠）:
  - `src/spec_dock/assets/spec_dock/templates/README.md`: テンプレの出力先マッピング（`adr.md` → `<scope>/adrs/...`）
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/`: 各スコープ配下に `adrs/`, `artifacts/` が存在
  - `src/spec_dock/assets/spec_dock/templates/adr.md`: ADR テンプレ（frontmatter と構成）
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`:
    - `_new_adr`: `scope.path / "adrs"` に出力（採番: `adrs/adr-*.md` を走査して max+1）
    - `_next_id`: `initiatives_root.rglob("adrs/adr-*.md")` で ADR の最大値を走査（prefix=="adr" の fallback）
  - `pyproject.toml`:
    - `tool.setuptools.exclude-package-data` が `assets/spec_dock/templates/**/discussions/**` を除外しており、配布物から `rules.md` が落ちる
- 観測した現状（事実）:
  - `artifacts/` はユーザー運用（テンプレ `_template.md` のコピー）で、ランタイムに強い依存はない
  - ADR は `spec-dock new adr` によって生成され、ランタイムの走査対象になっている
- 採用するパターン（命名/責務/例外/DI/テストなど）:
  - 生成物は小文字ディレクトリ/ファイル名（既存テンプレの規約に合わせる）
  - 後方互換は維持しない（`adrs/` / `artifacts/` のレガシーはサポートしない）
- 採用しない/変更しない（理由）:
  - `discussions/` を type ごとのサブディレクトリに分割（「1ディレクトリ」要望に反する）
- 影響範囲（呼び出し元/関連コンポーネント）:
  - テンプレ: `src/spec_dock/assets/spec_dock/templates/**`
  - ランタイム: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - Packaging: `pyproject.toml`
  - ドキュメント/サンプルツリー: `docs/discussion-sheets/**`, `spec-deps/**`（記述更新が必要になる可能性）

## 主要フロー（テキスト：AC単位で短く） (任意)
- Flow for AC-001（新規スコープ作成）:
  1) `new {initiative,epic,issue}` がテンプレをコピー
  2) `discussions/` が生成される（`adrs/`, `artifacts/` は生成しない）
- Flow for AC-002（ADR 作成）:
  1) `new adr` がスコープの `discussions/` を解決
  2) `adr-xxxxx-<slug>.md` を作成（採番は既存走査ロジックを流用）

### UML（任意） (任意)
```plantuml
@startuml
skinparam monochrome true
title File creation flow (new adr)

actor User
participant "spec-dock runtime" as RT
database "scope/discussions/" as D

User -> RT: new adr --scope <id> --title ...
RT -> RT: resolve scope path
RT -> D: scan adr-*.md (max id)
RT -> D: write adr-<next>-<slug>.md\n(from templates/discussions/adr.md)
RT --> User: ok (path=...)
@enduml
```

## データ・バリデーション（必要最小限） (任意)
- 追加データは無し（既存のファイル走査/採番のみ変更）
- バリデーション:
  - `discussions/` のディレクトリ名は固定
  - ADR のファイル名は `adr-*.md` を維持
  - 非ADRのファイル名は `<type>-00001-<slug>.md`（typeごとの連番）を推奨

### UML（任意） (任意)
```plantuml
@startuml
skinparam monochrome true
title Discussions directory (per scope)

folder "<scope>/" as Scope
folder "discussions/" as Discussions
file "adr-00001-..." as ADR
file "note-00001-..." as Note
file "disc-00001-..." as Disc
file "research-00001-..." as Research
file "rules.md" as Rules

Scope -down- Discussions
Discussions -down- ADR
Discussions -down- Note
Discussions -down- Disc
Discussions -down- Research
Discussions -down- Rules
@enduml
```

## 判断材料/トレードオフ（Decision / Trade-offs） (任意)
- 論点: `discussions/` 内の分類をどう担保するか
  - 選択肢A: ファイル名 prefix（`adr-`, `disc-`, `research-`, `note-`）で識別（主ルール）
    - Pros: 検索性が高い、ツール側で扱いやすい、混在でも破綻しにくい
    - Cons: 命名規約の教育が必要
  - 選択肢B: frontmatter `種別:` を必須化（主ルールにする）
    - Pros: ドキュメント単体で完結
    - Cons: 記入漏れが起きると分類不能、強制するほど運用負荷が上がる
  - 選択肢C: サブディレクトリで分類（`discussions/adr/`, `discussions/research/`）
    - Pros: 直感的
    - Cons: 「トップレベル1ディレクトリ」要望に反する
  - 決定（推奨）: A（prefix を主）+ frontmatter は “任意〜推奨” として補助的に使う
  - 理由: 1ディレクトリ制約と探索性の両立。将来の機械集計余地も残せる。

## インターフェース契約（ここで固定） (任意)
### API（ある場合）
- N/A（HTTP API は無し。CLI を契約として扱う）

### CLI（ユーザー導線）
- CLI-001: `spec-dock new adr --{initiative|epic|issue} <id> --title "<title>" [--slug <slug>] [--id <adr-id>]`
  - Output: `<scope>/discussions/adr-xxxxx-<slug>.md`
  - Notes:
    - 採番/重複チェックは `<scope>/discussions/adr-*.md` を走査（後方互換なし）
- CLI-002（将来検討）: `spec-dock new doc --{initiative|epic|issue} <id> --type {note|disc|research} --title "<title>" [--slug <slug>]`
  - Output: `<scope>/discussions/<type>-00001-<slug>.md`
  - Notes:
    - 本Issueでは実装しない（非ADRはテンプレの手動コピー運用を正とする）
    - 非ADRも連番に統一する（typeごとに `00001` から採番）
    - テンプレは `spec-dock/templates/discussions/<type>.md` を用意し、type で選択して生成する（無ければ `note.md` にフォールバック）

### 関数・クラス境界（重要なものだけ）
- IF-001: `spec_dock_runtime.app::_new_adr(...)`
  - Input: scope_id, title, slug, (optional) node_id
  - Output: `<scope>/discussions/adr-...md`
  - Errors/Exceptions: スコープ不存在、重複 id、slug 不正
- IF-002（internal / 保険）: `spec_dock_runtime.app::_next_id(specdock_dir, "adr", ...)`
  - Input: specdock_dir, local, (optional) nodes
  - Output: 次の ADR id（走査パスは `**/discussions/adr-*.md`）
- IF-003（任意）: `spec_dock_runtime.app::_new_doc(...)`（新設する場合）
  - Input: scope_id, type(note/disc/research), title, slug
  - Output: `<scope>/discussions/<type>-00001-<slug>.md`

### UML（任意） (任意)
```plantuml
@startuml
skinparam monochrome true
title Template copy flow (non-ADR)

actor User
file "spec-dock/templates/discussions/<type>.md" as T
folder "<scope>/discussions/" as D

User -> T: copy
User -> D: paste as\n<type>-00001-<slug>.md
User -> D: edit content
@enduml
```

### 実装詳細（重要部分だけ固定） (任意)
- 追加のクラス/モジュールは不要（既存 runtime 関数の改修で対応する）
- `_new_adr`（`spec_dock_runtime.app`）:
  - Template: `spec-dock/templates/discussions/adr.md`
  - Output: `<scope>/discussions/adr-xxxxx-<slug>.md`
  - 採番/衝突: `requirement.md` の EC-001 を満たす（`--id` 省略時は max+1、明示時の重複は非0で失敗）
  - 旧 `<scope>/adrs/adr-*.md` は読まない（後方互換なしを維持）
- `_next_id`（prefix=="adr" の保険）:
  - `initiatives_root.rglob("discussions/adr-*.md")` に更新する（現状未使用だが将来の安全のため）
- Packaging:
  - `pyproject.toml` の `exclude-package-data` から `assets/spec_dock/templates/**/discussions/**` を除去する
  - `assets/**/*` の package-data と整合させ、scope 配下の `discussions/rules.md` を wheel / sdist に含める
- （任意）`_new_doc`（追加する場合）:
  - Template: `spec-dock/templates/discussions/<type>.md`（無ければ `note.md`）
  - Output: `<scope>/discussions/<type>-xxxxx-<slug>.md`
  - 採番: type ごとに `discussions/<type>-*.md` を走査して max+1

### 例外/エラー契約（主要なものだけ） (任意)
- ERR-ADR-001: scope 不存在
  - 条件: 指定した scope_id が解決できない
  - 振る舞い: 非0で失敗、ファイルは作成しない
- ERR-ADR-002: テンプレ不足
  - 条件: `spec-dock/templates/discussions/adr.md` が存在しない
  - 振る舞い: 非0で失敗、ファイルは作成しない
- ERR-ADR-003: ID 重複
  - 条件: `--id` を明示し、同一IDの ADR が既に存在する
  - 振る舞い: 非0で失敗、ファイルは作成しない（EC-001）
- ERR-SLUG-001: slug 不正
  - 条件: `--slug` が kebab-case に合致しない、または空になる
  - 振る舞い: 非0で失敗、ファイルは作成しない

## 変更計画（ファイルパス単位） (必須)
- 追加（Add）:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/discussions/rules.md`:
    - 最小ルール（分類/命名/ADR昇格基準/テンプレの場所）
  - `src/spec_dock/assets/spec_dock/templates/discussions/{note,disc,research}.md`:
    - `discussions/` 用テンプレ（type ごと / 最小セット）
- 変更（Modify）:
  - `pyproject.toml`:
    - `exclude-package-data` から `assets/spec_dock/templates/**/discussions/**` を除去
  - `src/spec_dock/assets/spec_dock/templates/README.md`: 出力先マッピング（`adrs/`/`artifacts/` → `discussions/`）
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/`:
    - `adrs/`, `artifacts/` を `discussions/` に置換
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`:
    - `_new_adr`: `scope.path / "adrs"` → `scope.path / "discussions"`
    - `_next_id`: `rglob("adrs/adr-*.md")` → `rglob("discussions/adr-*.md")`
    - （将来）`new doc` の追加（type テンプレ + typeごとの連番採番）は別Issueで検討
- 削除（Delete）:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/{adrs,artifacts}/`（新規テンプレからは削除）
- 移動/リネーム（Move/Rename）:
  - `src/spec_dock/assets/spec_dock/templates/adr.md` → `src/spec_dock/assets/spec_dock/templates/discussions/adr.md`
- 参照（Read only / context）:
  - `docs/discussion-sheets/01_tree_root_location.md`: v2 ツリー例に `adrs/` が含まれるため追随が必要
  - `spec-deps/README.md`: v1 の運用説明（`adrs/`, `artifacts/` 記述）

## マッピング（要件 → 設計） (必須)
- AC-001 → テンプレ差し替え（`src/spec_dock/assets/spec_dock/templates/**`）
- AC-002 → `_new_adr`（`app.py`）と `templates/discussions/adr.md`
- AC-003 → `discussions/rules.md` の同梱（テンプレ）+ `rules.md` に導線を固定
- AC-004 → type テンプレ（`templates/discussions/<type>.md`）+ 命名規約（prefix+連番）
- AC-005 → `discussions/` 配下にラッパスクリプトを含めない（テンプレから `adrs/new-adr` を削除し、`discussions/` は markdown のみ）
- AC-006 → `spec-dock/templates/discussions/{adr,note,disc,research}.md` を同梱し、コピー導線を成立させる
- AC-007 → `pyproject.toml` の packaging 設定を修正し、`pip install .` 後も `rules.md` / templates が欠落しないことを保証
- EC-001/EC-002/EC-003 → 連番衝突時の挙動（採番・エラー）+ rules での手動運用ルール + legacy `adrs/` 非走査
- 非交渉制約（採番維持） → `_new_adr` の既存ロジック流用（走査パスのみ変更）

## テスト戦略（最低限ここまで具体化） (任意)
- 追加/更新するテスト:
  - Unit: `tests/test_cli.py`（init/update の生成物差分、runtime の新規作成コマンド）
  - Integration: なし（ネットワークなし、`gh` は stub で代替）
- どのAC/ECをどのテストで保証するか:
  - AC-001 → init/update の scaffold 検証（`discussions/` があり `adrs/`/`artifacts/` が無い）
  - AC-002 → `new adr` の生成先・採番（`discussions/adr-*.md`）
  - AC-003 → `discussions/rules.md` が生成される
  - AC-005 → `discussions/` 配下にラッパスクリプトが存在しない（`new-*` 不在、markdown のみ）
  - AC-006 → `spec-dock/templates/discussions/` と type テンプレが同梱されている
  - AC-007 → `pip install .` 相当の配布経路でも `discussions/rules.md` が利用可能
  - EC-001 → `--id` 省略時は max+1 採番、`--id` 明示時の重複は非0で失敗（挙動をテストで固定）
  - EC-003 → 旧 `adrs/` を読まない方針を runtime 実装のまま維持し、回帰を入れない

- 実行コマンド: `python -m unittest discover -v`

## リスク/懸念（Risks） (任意)
- R-001: 破壊的変更で旧ツリーが動かなくなる（影響: 既存利用者 / 対応: 後方互換は提供しない。`rules.md` に最小の手動移行手順を記載）
- R-002: `discussions/` が “何でも置き場” 化する（影響: 探索性低下 / 対応: `rules.md` に命名規約と type 定義、テンプレ導線を固定）
- R-003: 手動運用で連番衝突が起きる（影響: 作成時の手戻り / 対応: `rules.md` に衝突時の手順を明記。必要性が顕在化したら `new doc` を別Issueで追加）
- R-004: packaging の除外設定が新 assets と衝突すると、ローカル開発では再現せず CI / 配布後にだけ欠落が起こる（影響: 発見遅延 / 対応: `pip install .` 経路の検証を追加）

## 未確定事項（TBD） (必須)
- Q-001:
  - 質問: 後方互換性を維持するか
  - 回答: No（決定。破壊的変更を許容）
  - 影響範囲: ランタイム走査/テンプレ/ドキュメント
- Q-002:
  - 質問: ADR 以外の作成導線をどこまで標準搭載するか（CLI vs 手動コピー）
  - 選択肢:
    - A: `spec-dock/templates/discussions/<type>.md` を手動コピーして作成（最小）
    - B: `spec-dock new doc --type {note|disc|research} ...` で生成（採番・衝突回避をツールで担保）
  - 回答: A（決定。今Issueでは手動コピー運用）
  - 影響範囲: ランタイム実装/テスト/運用負荷
- Q-003:
  - 質問: 非ADRドキュメントの連番は「typeごと」か「discussions全体で共通」か
  - 回答: A（決定）
  - 選択肢（記録）:
    - A: typeごと（`note-00001`, `disc-00001`, `research-00001`）: 直感的、衝突が減る
    - B: 共通（`doc-00001` + frontmatter で type）: 作成順で並ぶが識別が弱い
  - 影響範囲: 命名規約/採番ロジック/探索性

---

## ディレクトリ/ファイル構成図（変更点の見取り図） (任意)
```text
<scope>/
├── discussions/                 # Add (new)
│   ├── rules.md                 # Add
│   ├── adr-00001-....md         # New
│   ├── note-00001-....md        # Add (optional)
│   ├── disc-00001-....md        # Add (optional)
│   └── research-00001-....md    # Add (optional)
```

## 省略/例外メモ (必須)
- 該当なし
