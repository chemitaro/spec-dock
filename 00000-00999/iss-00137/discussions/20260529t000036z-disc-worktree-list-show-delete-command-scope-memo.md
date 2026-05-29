---
種別: disc
ID: "20260529t000036z-disc"
タイトル: "Worktree list show delete command scope memo"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
authority: "proposed"
derived_from: []
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t000036z-disc Worktree list show delete command scope memo

## ユーザー入力
- SpecDock 自身を dogfooding する SpecDock に追加したい機能として、現在 `worktree create` だけがある `worktree` command group に、一覧表示、詳細表示、削除を追加したい。
- 要件定義書はまだ作成しない。
- この issue でやりたいことを `discussions/` directory のメモ書きとしてまとめる。

## 対象 scope
- 親 epic:
  - `epic-00107 Worktree Provisioning`
- 新規 issue:
  - `iss-00137 Worktree list show delete commands`
- 対象 command group:
  - `spec-dock worktree`
- 追加したい command:
  - `spec-dock worktree list`
  - `spec-dock worktree show <target>`
  - `spec-dock worktree delete <target>`

## やりたいこと
- `worktree list`:
  - SpecDock が管理対象として扱う worktree を一覧表示できるようにする。
  - `worktree create` で使っている central root / namespace の考え方と整合させる。
  - 一覧では、少なくとも worktree path、branch、識別しやすい名前または id、現在の存在状態を確認できるようにしたい。
- `worktree show`:
  - 一覧から一つを指定して、詳細を確認できるようにする。
  - 詳細では、path、branch、Git worktree record、main checkout との関係、削除可能かどうかを判断できる情報を表示したい。
- `worktree delete`:
  - 指定した worktree を削除できるようにする。
  - 誤削除を避けるため、main checkout や現在実行中の checkout を削除しない safety guard が必要。
  - dirty worktree、未 push branch、branch 削除の扱いは実装前に方針を決める。

## 実装前に確認したい論点
- `target` の指定方法:
  - path、directory basename、branch name、`worktree create` 由来の id のどれを受け付けるか。
  - 複数一致した場合の error message と disambiguation の方針。
- 管理対象の範囲:
  - `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` 配下だけを SpecDock-managed とみなすか。
  - `git worktree list --porcelain` に存在するが central root 外にある worktree を一覧や詳細でどう扱うか。
- delete の意味:
  - `git worktree remove` だけを行うのか。
  - 関連 branch の削除も command scope に含めるのか。
  - dirty worktree / locked worktree / missing path / stale record をどう扱うか。
- output contract:
  - text output のほか、将来的に JSON output が必要か。
  - `list` は人間向け表形式でよいか、machine readable な列安定性を意識するか。
- naming:
  - `delete` と `remove` のどちらを user-facing command 名にするか。
  - 今回のユーザー入力は `delete` だが、Git terminology は `worktree remove` に近い。

## 最初の成功条件案
- `spec-dock worktree list` で central root namespace 内の worktree を一覧できる。
- `spec-dock worktree show <target>` で指定 worktree の詳細を表示できる。
- `spec-dock worktree delete <target>` で safety guard を通過した worktree を削除できる。
- main checkout、現在の checkout、dirty worktree はデフォルトで削除しない。
- provider-side runtime source を変更し、dogfooding workspace 側でも command help / behavior を確認する。
- runtime tests は temp Git repo と temp worktree root を使い、実 checkout の worktree を破壊しない。

## この issue ではまだ決めないこと
- canonical `requirement.md` / `design.md` / `plan.md` への正式反映。
- branch 削除を default behavior に含めるかどうか。
- stale worktree record の prune を同じ issue に入れるかどうか。
- JSON output や interactive confirmation の有無。

## 次アクション
- 既存 `worktree create` の implementation / tests / output contract を調べる。
- `list` / `show` / `delete` の target resolution と safety guard を小さく設計する。
- 必要なら、このメモをもとに `requirement.md` / `design.md` / `plan.md` へ正式化する。
