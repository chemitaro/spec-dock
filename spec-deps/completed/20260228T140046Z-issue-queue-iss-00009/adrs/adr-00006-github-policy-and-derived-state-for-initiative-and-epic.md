---
種別: ADR（Architecture Decision Record）
ID: "adr-00006"
タイトル: "initiative/epic の GitHub Issue 作成をデフォルトで無効化し、状態は配下 issue から導出する"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-02-27"
親: ["iss-00009"]
---

# adr-00006 initiative/epic の GitHub Issue 作成をデフォルトで無効化し、状態は配下 issue から導出する

## 結論（Decision） (必須)
- 採用: Option B（initiative/epic はローカルをデフォルト、必要時のみ GitHub 連携。状態は配下 issue から導出）
- 破壊的変更（許容）:
  - `new initiative` / `new epic` のデフォルト挙動を反転し、GitHub Issue を自動作成しない
  - 段階導入は行わず、このタイミングで一括で変更する

### GitHub 連携ポリシー（new）
- initiative:
  - デフォルト: GitHub Issue を作成しない（local-only）
  - 任意: `--create-github-issue`（新規作成してリンク）または `--github-issue <n>`（既存番号へリンク）
- epic:
  - デフォルト: GitHub Issue を作成しない（local-only）
  - 任意: `--create-github-issue`（新規作成してリンク）または `--github-issue <n>`（既存番号へリンク）
- issue:
  - デフォルト: GitHub Issue を作成する（従来どおり）
  - 例外: `--no-github`（local-only）

#### CLI フラグの排他・組み合わせ（案）
- initiative/epic:
  - `--create-github-issue` と `--github-issue` と `--no-github` は相互に排他
  - `--id` は local-only（`--no-github` またはデフォルト local）でのみ許可（GitHub 番号由来 ID と衝突させない）
- issue:
  - 現状どおり（デフォルト GitHub、`--no-github` で local、`--github-issue` で既存リンク）

### GitHub 連携ポリシー（import）
- `import initiative/epic` は当面維持する（既存 GitHub Issue を “参照情報としてリンク” できる導線）。
  - ただし initiative/epic の GitHub OPEN/CLOSED は状態判定に使用しない。

### 状態ポリシー（deps / 可視化）
- initiative/epic の Done 判定は **配下 issue の状態から導出**する（= “親 GitHub Issue を閉じたら Done” を廃止）。
  - Done 条件（変更）:
    - `open == 0` かつ `unknown == 0`
      - `total == 0`（配下 issue が無い）場合も Done とみなす（= “実質的に完了済み”）
      - 表示上は `done(empty)` 相当として区別できるようにする（例: PlantUML ラベルに `Empty` / `No issues` を付与）
- initiative/epic が GitHub Issue にリンクされている場合でも、**その OPEN/CLOSED は状態判定に使わない**（ナビゲーション用の参照情報としてのみ許容）。

#### initiative/epic の state（表示用）導出（案）
- 前提:
  - issue の最小状態は `open|done|unknown`（`--github` 時に GitHub OPEN/CLOSED を反映、未取得は unknown）
  - initiative/epic の `progress={total,done,open,unknown}` は配下 issue 集計で得る
- state:
  - `done`: Done 条件を満たす
  - `doing`: active leaf が配下に存在する（例: initiative 配下の active issue がある）
  - `unknown`: `unknown > 0`（配下に未知がある）
  - `todo`: 上記以外（未完了だが、active はない）
- `blocked` は従来どおり ready=false の導出状態（依存未解決の表示用）として優先する

### wrapper ポリシー（導線）
- `new-epic` wrapper は “親の GitHub 連携有無” に関わらず **epic を local-only で作成**できる導線を提供する（gh 依存を排除）。
- `new-issue` wrapper は “親 epic が local-only” であっても **issue を GitHub デフォルトで作成**する（issue だけは実装単位として GitHub を標準入口にする）。
  - `gh` が未導入/未認証の場合は wrapper 側で失敗し、次の行動を提示する:
    - option 1) `gh` を導入/認証して再実行
    - option 2) direct command で local issue を作成（`new issue --no-github`）

## 背景（Context） (必須)
- initiative/epic は抽象度が高く、実際に作業を進める最小単位は issue である。
- 現状は initiative/epic でも GitHub Issue を作成するため、以下が発生する:
  - initiative/epic の状態を「親 GitHub Issue の OPEN/CLOSED」と「配下 issue の進捗集計」の二重で扱うことになり、運用が複雑化する。
  - 依存関係判定（deps）で “親を閉じれば Done 扱い” が成立し、依存ガードが弱まり得る（実態と乖離する）。
  - `new initiative` / `new epic` のデフォルトが `gh issue create` になり、副作用（GitHub チケット増殖）と摩擦（gh 未導入/未認証）が増える。

## 選択肢（Options considered） (必須)
- Option A: initiative/epic の GitHub Issue は作るが、状態（Done/Todo）は無視して配下 issue だけで導出する
  - Pros:
    - GitHub 上に “器” を残せる（議論/通知/Projects など）。
  - Cons:
    - GitHub 上で CLOSED にしても spec-dock 的には Done にならないケースが増え、混乱を招きやすい。
    - GitHub チケット増殖（副作用）は残る。
- Option B: initiative/epic はデフォルト local-only、必要時のみ GitHub 連携。状態は配下 issue から導出する（本 ADR の提案）
  - Pros:
    - 副作用を減らし、二重管理を撤廃できる。
    - GitHub に “器” が必要な場合のみ opt-in できる。
  - Cons:
    - 既存の “new は GitHub デフォルト” 前提の手順・期待が変わる（破壊的変更）。
    - mixed mode（local 親 + GitHub 子）が標準になるため、導線（wrapper/ドキュメント）の設計が重要。
- Option C: initiative/epic は GitHub と完全に切り離し、リンク自体も許容しない（import も縮退）
  - Pros:
    - 一貫性が最も高く、二重管理が起きない。
  - Cons:
    - 組織運用で GitHub Projects / 検索 / 通知の “上位概念” が必要な場合に適合しない。

## 判断理由（Rationale） (必須)
- initiative/epic を “作業対象” として GitHub に作る必然性が低い一方で、状態二重化と運用コストが顕著である。
- Option B は「GitHub の副作用削減（デフォルト local）」と「必要な場合の逃げ道（任意 link/create）」を両立できる。

## 影響（Consequences） (必須)
### Positive（良い点）
- initiative/epic の状態管理が “配下 issue の事実” に統一され、閉じ忘れ/先に閉じた等の揺れを減らせる。
- `new initiative` / `new epic` が gh 依存しなくなり、初期導入・オフライン・権限制約時の摩擦が下がる。
- GitHub 上のチケット増殖を抑制できる。

### Negative / Debt（悪い点 / 将来負債）
- 破壊的変更:
  - `new initiative` / `new epic` のデフォルト挙動・ID の見え方が変わる（ドキュメント/テスト/運用ルールの更新が必須）。
- 既存運用とのズレ:
  - 既存の initiative/epic が GitHub Issue を持っていても、CLOSED は Done 判定に使わないため「閉じたのに Done ではない」が起き得る（周知が必要）。
- `total == 0` を Done 扱いする副作用:
  - 後から配下 issue を追加すると、initiative/epic が Done→Todo/Doing へ戻り得る
  - 依存関係の ready 判定も動的に変わるため、運用上は「依存先のスコープが後から増えた」ことに注意が必要

### 既存 ADR との関係（重要）
- 本 ADR が採用された場合:
  - `adr-00005`（epic/initiative Done に “親 GH CLOSED” を含める）を **superseded/amended** として扱う（A を撤廃し B のみへ）。
  - `adr-00002`（状態モデル）を **initiative/epic について改訂**し、issue は従来どおり GitHub state + active、initiative/epic は配下 issue 集計 + active から導出とする。

## リスクと対策（Risks & mitigations） (必須)
- ID の曖昧性（数値ショートハンド）:
  - 例: `init-00001` と `init-local-00001` が同居すると、親指定で `--initiative 1` が曖昧になり得る。
  - 対策（案）:
    - local 採番時に “同prefixの全 ID（local/nonlocal）” の最大値を見て衝突を避ける。
    - もしくは `validate` で “曖昧化し得る組” を警告し、運用上はフル ID を推奨する。
- `active set` の入力（数値=GitHub issue 番号）:
  - initiative/epic が local-only になるほど、`active set 123` のような数値入力は initiative/epic に効かなくなる。
  - 対策（案）:
    - ドキュメントで「local ノードは `active set init-local-...` のようにフル ID を使う」を明記する。
- `sync --github` の warning ノイズ:
  - initiative/epic の GitHub state を状態判定に使わない場合、`gh_index_incomplete` の対象は issue 中心に寄せた方が分かりやすい。
  - 対策（案）:
    - “状態判定に使う番号（= issue の github.issue_number）” を missing 判定の対象に限定する。
- wrapper の local 伝播:
  - 誤って `new-issue` wrapper が `--no-github` を付け続けると、issue まで local-only になり progress/依存の unknown が急増する。
  - 対策:
    - “issue は GitHub デフォルト” を wrapper/ドキュメント/テストで固定する（導線でブレさせない）。

## 移行（Migration） (必須)
- 既存ツリーの `meta.json` スキーマ変更は不要（GitHub link を消す強制もしない）。
- 既存の initiative/epic GitHub link は “参照情報としては保持可” とし、状態判定からは除外する。
- ドキュメント上は以下を明記する:
  - “initiative/epic は GitHub CLOSED でも Done とは限らない（Done は配下 issue）”
  - “issue は GitHub を標準入口にする（wrapper も GitHub を前提にする）”

## 実装メモ（Implementation notes） (任意)
- 影響範囲（例）:
  - runtime: `new initiative` / `new epic` のデフォルト分岐・引数（`--create-github-issue` の追加など）
  - templates: `initiative/epics/new-epic` / `epic/issues/new-issue` の local 伝播ルール変更
  - deps: initiative/epic Done 判定の変更（親 GH CLOSED を除外） + base_state の再設計
    - 注意: Done 判定ロジックは `deps check` と `sync`（`.agent/deps.json` 生成）側で重複しているため、同一ルールへ同時改修する
  - docs: README / workflow / reference_github / reference_deps / reference_sync
  - tests: “デフォルトは GitHub” 前提の回帰テスト更新

## 参考（References） (任意)
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/adrs/adr-00002-deps-status-model.md`
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/adrs/adr-00005-done-definition-for-epic-and-initiative.md`
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
