# Workbench の Git 追跡状態に関する調査記録

調査日: 2026-09-24。対象: このリポジトリの `83cb5f56be52fe45c52ad4b6aa0b0144a409d06b` から作成した調査ブランチ。ここには現物確認の事実を記し、期待する仕様の変更は決定しない。

## 現物確認

- `git status --short --branch` は調査開始時 `HEAD (no branch)` のみを示し、変更はなかった。
- `git ls-files 'spec-dock/**/.workbench/**'` は 25 件を返した。すべて各 Workbench 直下の `README.md` であり、一時 payload の追跡例は確認されなかった。
- `spec-dock/.gitignore` と provider 側 `src/spec_dock/assets/spec_dock/.gitignore` は一致し、`**/.workbench/*` で entry を除外したうえで `!**/.workbench/README.md` により直下の README だけを再包含する。
- 実際の Issue scope で `git check-ignore -v --no-index` を使うと、仮想の `example.txt` には除外規則、`README.md` には再包含規則が適用された。
- 配布 docs の `src/spec_dock/assets/spec_dock/docs/README.md` は、README を唯一の tracking 対象、ほかの entry を ignored payload と説明している。

## 変更の由来

- Issue #315 の `design.md` は Workbench 全体を Git ignore する構想を記載している。
- 後続の Issue #344 の `requirement.md` は、Workbench 直下の README を Git tracking 対象とし、その他の entry は ignore する契約へ明示的に変えている。理由として、各 Workbench 内に使用方法を説明する tracked file を置くことと、空 directory を Git checkout で維持することを挙げる。
- `99569fb94c37b049d192f6b348887f55177e170b` は 2026-07-29 に provider の `.gitignore` と README template を dogfooding 側へ反映した。

## 独立分析で確認する論点

1. Issue #315 から #344 への仕様変更は、Worktree-local・disposable という目的と矛盾しないか。
2. 現在の ignore pattern は各スコープ、入れ子のファイル、名前違い、既存の tracked entry に対して意図どおり働くか。
3. `README.md` を例外として追跡することによる利用者の誤認や、将来の安全な設計選択肢は何か。
4. この checkout で確認できない利用先 repository の ignore drift や、明示 `git add -f` による追跡は、どの証拠を得れば判別できるか。

この記録は原因分析の入力であり、Workbench 内のファイルや ignore 規則は変更していない。
