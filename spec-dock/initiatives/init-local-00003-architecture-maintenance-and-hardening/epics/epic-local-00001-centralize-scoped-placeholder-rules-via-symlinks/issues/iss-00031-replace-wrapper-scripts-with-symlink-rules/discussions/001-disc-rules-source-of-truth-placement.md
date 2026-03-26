# 001-disc-rules-source-of-truth-placement

## 目的
- `rules.md` の原本を `docs/` と `system/` のどちらに置くべきかを比較し、今回の設計判断を固定する。

## 比較対象
- A:
  - `spec-dock/docs/rules/<scope-kind>/<child-kind>.md` を原本にする。
- B:
  - `spec-dock/system/...` を原本にする。
- C:
  - `templates/` を原本にする。

## 確認した事実
- `docs/` は workflow / phase playbook の正本として使われている。
- `system/` は `active-none` など runtime fallback / managed state 寄りの責務を持つ。
- 現行 `discussions/rules.md` は状態ファイルではなく、運用ルール文書である。
- このツールは dogfooding 専用で、後方互換性より単純さが重要である。

## 評価
- A:
  - 文書の意味と置き場所が一致する。
  - workflow / phase docs から自然に参照できる。
  - 「読むべき正本は docs」という理解に揃えやすい。
- B:
  - runtime 管理物と人間向けルール文書の責務が混ざる。
  - `system/active-none` との意味論がぶつかりやすい。
- C:
  - 生成素材を正本にしてしまい、利用者が読む場所として不自然。

## 決定
- `docs/rules/` を原本にする。
- 粒度は次の 5 ファイルに分ける。
  - `initiative/discussions.md`
  - `initiative/epics.md`
  - `epic/discussions.md`
  - `epic/issues.md`
  - `issue/discussions.md`
- 各 node directory には `rules.md` という名前で symlink を置く。

## 採用理由
- rules は state ではなく documentation であり、SoR は `docs/` が自然である。
- dogfooding 専用で単純化優先なので、読む場所と正本を一致させるのが最も分かりやすい。
- `system/` は runtime 管理用途として意味を保ったほうが repo 全体の構造が明快である。

## 文書粒度の方針
- `docs/rules/` 本文は最小の役割説明と runtime command 導線に留める。
- 命名規約や discussion 採番などの詳細規約は既存の workflow / naming docs を参照する。

## 影響
- epic / issue requirement/design/plan は `docs/rules/` 正本前提へ更新する。
- 実装時は generic な symlink framework を広げるより、新規 node 作成時に `rules.md` symlink を明示配置する最小案を優先する。
