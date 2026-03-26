---
種別: 要件定義書（Issue）
ID: "iss-00031"
タイトル: "Replace Wrapper Scripts With Symlink Rules"
関連GitHub: ["#31"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-26"
親: ["epic-local-00001", "init-local-00003"]
---

# iss-00031 Replace Wrapper Scripts With Symlink Rules — 要件定義（WHAT / WHY）

## 目的
 - `new-epic` / `new-issue` wrapper script をやめ、`epics/`, `issues/`, `discussions/` に置く placeholder を `docs/rules/` の中央管理 rule sheet への symlink に統一する。
 - canonical な user-facing rules source-of-truth を `spec-dock/docs/rules/**` に置き、provider-side assets 配下 `src/spec_dock/assets/spec_dock/docs/rules/**` は package に同梱する authoring/source files として installer / runtime / docs / tests がその新規生成 contract を守る状態へ更新する。

## 背景・現状
- 現状の挙動:
  - initiative 作成後は `epics/new-epic`、epic 作成後は `issues/new-issue` という wrapper script が生成される。
  - `discussions/rules.md` は scope ごとに実体ファイルとしてコピーされる。
- 現状の課題:
  - wrapper script は runtime 探索や `.meta.json` 解釈に依存し、壊れやすい。
  - 空ディレクトリ維持と create entrypoint が同じ artifact に混ざっている。
  - rules markdown の実体が scope ごとに複製され、一元管理になっていない。
  - ルール文書の原本が `docs/` ではなく template 実体に埋まっているため、読む場所と生成元がずれている。
- 再現手順:
  1. `spec-dock init` 後に `new initiative` / `new epic` / `new issue` を作成する。
  2. 生成された `epics/` や `issues/` を見ると wrapper script が唯一の placeholder になっている。
- 観測点:
  - UI:
    - なし
  - HTTP:
    - なし
  - DB:
    - なし
  - Log:
    - CLI filesystem output / tests
- 情報源:
  - `src/spec_dock/assets/spec_dock/templates/initiative/epics/new-epic`
  - `src/spec_dock/assets/spec_dock/templates/epic/issues/new-issue`
  - `src/spec_dock/assets/spec_dock/templates/*/discussions/rules.md`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_wrappers.py`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` を運用する maintainer と coding agent
- 代表シナリオ:
  - 新しい scope を作った直後に child directory を見ても、使い方は `rules.md` と runtime command に一本化されている。

## スコープ
- MUST:
  - `initiative/epics/new-epic` と `epic/issues/new-issue` を新規 scaffold から除去する。
  - `initiative/epics/rules.md`, `epic/issues/rules.md`, `initiative|epic|issue/discussions/rules.md` を `docs/rules/` の実体ファイルへの symlink として配置する。
  - 中央管理ファイルは `docs/rules/` 側に置き、node directory 側には実体ファイルを持たせない。
  - `spec-dock init/update` は `docs/rules/` 原本を配布し、runtime `new *` は新規 node に symlink を配置する。
  - 関連 docs と tests を更新する。
  - review で出た回帰リスクについて、今回の contract に直接関係するものは tests で固定する。
- MUST NOT:
  - rules markdown をコピーして複製管理しない。
  - wrapper script と symlink rules を併存させない。
  - main create flow を wrapper 前提の UX に戻さない。
- OUT OF SCOPE:
  - discussion template 本文の大幅改訂
  - GitHub issue 生成仕様の変更
  - active pointer 機構の変更
  - 既存 checked-in node 配下の wrapper / rules 実体の置換
  - symlink 非対応環境への fallback

## 境界
- Always:
  - provider-side `src/spec_dock/assets/spec_dock/...` は package に同梱する authoring/source files として修正し、canonical な user-facing rules source-of-truth は `spec-dock/docs/rules/**` に置く。
  - child directory の placeholder 名は `rules.md` に統一する。
  - symlink target は repo 内の `spec-dock/docs/rules/` に限定する。
- Ask:
  - `docs/rules/` の粒度と参照先 docs が重複過多にならないか。
  - runtime create flow へ足すのが最小の責務か。
- Never:
  - docs 原本を `system/` や `templates/` に寄せない。
  - uppercase path を増やさない。

## 非交渉制約
- パスは lowercase を維持する。
- 既存の `new doc` / validate / sync / active flow を壊さない。
- dogfooding 専用ツールとして、過剰な互換維持や汎用化を入れない。
- docs contract test は command path / `docs/rules/**` 参照 / wrapper absence などの stable な契約を優先し、非本質な prose への結合を増やしすぎない。

## 前提
- Linux/Unix 系の test 環境では symlink が利用できる。
- `docs/` はルール文書の原本置き場として扱える。
- installer は `docs/rules/` 原本を通常の managed docs として配布できる。
- runtime は新規 node 作成時に `rules.md` symlink を明示配置する。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `spec-dock init` または `spec-dock update` を実行する repo
  - When:
    - `spec-dock/docs/` と `spec-dock/templates/` が展開される
  - Then:
    - `docs/rules/` の中央管理 rules 実体が存在し、新規生成フローがその原本を参照できる
  - 観測点:
    - installer tests、`docs/rules/` の存在
- AC-002:
  - Actor:
    - coding agent
  - Given:
    - `new initiative`, `new epic`, `new issue` を実行する
  - When:
    - 生成された `epics/`, `issues/`, `discussions/` を確認する
  - Then:
    - `rules.md` symlink が存在し、`new-epic` / `new-issue` は存在しない
  - 観測点:
    - runtime CLI tests、新規生成 node 実体
- AC-003:
  - Actor:
    - coding agent
  - Given:
    - symlink 化後の scope directory
  - When:
    - `new doc` と関連 validation を実行する
  - Then:
    - discussion 採番と関連フローが従来どおり成功する
  - 観測点:
    - regression tests
- AC-004:
  - Actor:
    - coding agent
  - Given:
    - `new initiative` / `new epic` / `new issue --create-github-issue` の事前条件のうち、GitHub issue 作成前に判定できる local collision がある
  - When:
    - create flow を実行する
  - Then:
    - remote side effect より前に `pre_github_fail` で停止し、GitHub gateway call は発生しない
  - 観測点:
    - create-mode preflight regression tests
- AC-005:
  - Actor:
    - maintainer
  - Given:
    - 既存 node tree 配下に legacy wrapper / rules 実体が残っている repo
  - When:
    - `spec-dock update` を実行する
  - Then:
    - managed docs/templates は更新されるが、既存 node tree 配下の legacy artifact は out-of-scope として preserve される
  - 観測点:
    - installer/update regression tests

## 例外・エッジケース
- EC-001:
  - 条件:
    - runtime が新規 node に `rules.md` を配置する
  - 期待:
    - `docs/rules/` を指す相対 symlink が作られるか、少なくとも tests で退行が検出される
  - 観測点:
    - symlink-aware tests
- EC-002:
  - 条件:
    - `discussions/` に `rules.md` symlink があっても `new doc` が採番対象を走査する
  - 期待:
    - `rules.md` は採番対象外のままである
  - 観測点:
    - existing discussion tests
- EC-003:
  - 条件:
    - 既存 checked-in tree に旧 wrapper が残る
  - 期待:
    - 既存 tree は out of scope として扱い、新規生成 contract だけを保証する
  - 観測点:
    - requirement / design / plan の境界記述
- EC-004:
  - 条件:
    - docs wording を軽微に調整する
  - 期待:
    - docs contract test は stable anchor を維持する限り不要に失敗しない
  - 観測点:
    - docs contract tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock new epic --no-github --initiative init-local-00003 --title "Sample Epic"`
  - Output:
    - `<initiative>/epics/rules.md -> ../../../docs/rules/initiative/epics.md`
    - `<initiative>/epics/epic-local-0000x-sample-epic/...`

## 用語（ドメイン語彙）
- TERM-001:
  - 中央管理 rules 実体:
    - `docs/rules/` 配下に置かれる、scope child directory 用 rule sheet の正本ファイル
- TERM-002:
  - placeholder symlink:
    - 空ディレクトリ維持と利用ガイド提示のために node 配下へ置かれる `rules.md` symbolic link

## 未確定事項
- なし:
  - `docs/rules/` は最小の役割説明と導線だけを持ち、詳細規約は既存 docs 参照へ寄せる。
