---
種別: 要件定義書（Issue）
ID: "iss-00064"
タイトル: "Update User Facing Docs Help"
関連GitHub: ["#64"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-11"
親: ["epic-00059", "init-local-00003"]
---

# iss-00064 Update User Facing Docs Help — 要件定義（WHAT / WHY）

## 目的
- dependency metadata が `.meta.json` に統合され、依存変更が `deps add/remove/check` の command-first contract に切り替わった現行アーキテクチャを、利用者向け docs / help 補助 docs / skill 導線まで一貫して反映する。
- 初見利用者が古い `./spec ...` や legacy `meta.json` / `deps.json` 前提に誘導されず、現行の supported execution path と mutation contract に最短で到達できる状態を作る。

## 背景・現状
- 現状の挙動:
  - deep reference である `reference_deps.md` と `reference_sync.md` は、`.meta.json` only、no dual-read、command-first mutation を概ね説明できている。
  - CLI help では `deps {check,add,remove}` が表示され、実装 surface 自体は露出している。
- 現状の課題:
  - 入口 docs に `./spec ...` のような旧コマンド例が残っており、現在の `./spec-dock/scripts/spec-dock ...` contract と食い違う。
  - 一部補助 docs に legacy `meta.json` 表記や古い導線が残っている。
  - 利用者や agent が「依存変更は command で行う」という運用原則を入口で把握しにくい。
- 再現手順:
  1. `spec-dock/docs/README.md` や provider-side docs README を読む。
  2. `reference_deps.md` / `reference_sync.md` / `sync.md` / old guide / skill を横断する。
  3. コマンド例、storage 名、mutation 方法の説明が文書ごとに揺れることを確認する。
- 観測点:
  - CLI / docs の最初のコマンド例
  - `.meta.json` / `depends_on` / `deps add/remove/check` に関する説明
  - old doc が現行入口と誤認されないこと
- 情報源:
  - `iss-00063` discussion: `20260411t000000z-disc-user-facing-doc-gap-analysis.md`
  - `spec-dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `spec-dock/docs/**`
  - `src/spec_dock/assets/codex_skills/**`
  - `.agents/skills/**`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `spec-dock` を使って issue execution や docs/graph maintenance を行う maintainer
  - `spec-dock` skills を経由してコマンドを実行する coding agent
- 代表シナリオ:
  - README/guide から最初のコマンドを探す
  - 依存関係を追加・削除する方法を調べる
  - `sync` / `validate` / `deps check` の関係を理解して運用する

## スコープ
- MUST:
  - provider-side docs 正本と dogfooding mirror において、現行 supported command path を一貫して示す。
  - `.meta.json` only / `depends_on` canonical / command-first mutation / no dual-read の利用者向け説明を揃える。
  - `deps add/remove/check` を入口 docs または導線 docs から発見できる状態にする。
  - old / secondary docs が残る場合は、現行入口ではないことを明示する。
  - skills / adapters のうち利用者や agent の実行導線に関わるものは、現行 contract と整合させる。
- MUST NOT:
  - runtime behavior や dependency semantics を新たに変更しない。
  - `.meta.json` only / no dual-read / fail-closed の epic contract を弱めない。
  - `./spec ...` 互換導線を docs 上で現行サポートとして再導入しない。
- OUT OF SCOPE:
  - 新しい CLI サブコマンド追加
  - dependency graph semantics の拡張
  - `iss-00063` の close evidence 自体の再定義

## 境界
- Always:
  - provider-side source of truth を先に更新し、その反映結果として dogfooding mirror も整合させる。
  - 入口 docs、reference docs、skills の 3 面で同じ contract を説明する。
  - 実装済み CLI help と矛盾しない記述にする。
- Ask:
  - old doc を削除するか、deprecated 扱いで残すかは影響と導線の強さを見て判断する。
- Never:
  - legacy `deps.json` fallback や metadata 直編集を推奨しない。

## 非交渉制約
- source of truth は `src/spec_dock/assets/spec_dock/**` であり、`spec-dock/**` は dogfooding mirror として確認する。
- path に新たな大文字を導入しない。
- issue workflow の required review / report / validate / sync evidence を満たす。

## 前提
- `epic-00059` では `iss-00060` が provider-side dependency docs 正本を導入済みである。
- `iss-00061` と `iss-00062` により `deps add/remove/check`、`.meta.json` SoT、downstream parity は実装済みである。
- 今回の issue は新しい architecture contract を利用者向け導線へ揃える docs/help/skill 修正 issue である。

## 受け入れ条件
- AC-001:
  - Actor:
    - 初見の maintainer / agent
  - Given:
    - README / guide / workflow / skill など入口に近い文書から利用を開始する
  - When:
    - 実行コマンドや依存変更方法を探す
  - Then:
    - `./spec-dock/scripts/spec-dock ...` が現行の実行経路として一貫して示され、`./spec ...` は現行導線として残らない
  - 観測点:
    - provider-side README / dogfooding README / 関連 guide / skill の記述
- AC-002:
  - Actor:
    - dependency metadata の保存先や変更方法を確認する利用者
  - Given:
    - docs / help 補助 docs / skills を横断して読む
  - When:
    - canonical storage と mutation contract を確認する
  - Then:
    - `.meta.json` top-level `depends_on`、command-first mutation、no dual-read / no auto-migration が矛盾なく説明される
  - 観測点:
    - `reference_deps.md` / `reference_sync.md` / 補助 docs / skill の記述整合
- AC-003:
  - Actor:
    - 依存関係を追加・削除したい利用者
  - Given:
    - README や guide から運用を始める
  - When:
    - 依存変更の方法を探す
  - Then:
    - `deps add/remove/check` の存在と、`sync` / `validate` との関連が入口導線から把握できる
  - 観測点:
    - docs examples、guide のコマンド列、skill guidance
- AC-004:
  - Actor:
    - old / secondary docs に到達した利用者
  - Given:
    - 旧 guide や補助 docs が repo に残っている
  - When:
    - その文書を読む
  - Then:
    - 現行入口ではないこと、または現行 contract へ誘導することが明示され、誤誘導しない
  - 観測点:
    - old doc の冒頭注意書き、cross-link、deprecated 表現

## 例外・エッジケース
- EC-001:
  - 条件:
    - old doc を削除せず残す必要がある
  - 期待:
    - deprecated / historical であることと、現行正本へのリンクが明示される
  - 観測点:
    - old doc の先頭告知文
- EC-002:
  - 条件:
    - provider-side docs と dogfooding mirror に同名または類似文書が存在する
  - 期待:
    - provider-side source of truth を先に更新し、mirror にも同じ契約が反映される
  - 観測点:
    - 対応ファイルの内容一致、最終 `sync` / `validate` 結果
- EC-003:
  - 条件:
    - CLI help の surface は正しいが docs に説明密度の不足がある
  - 期待:
    - help の再実装ではなく docs / skill 導線の説明を補い、help と矛盾しない
  - 観測点:
    - docs diff と help 出力の照合

## 入力→出力例
- EX-001:
  - Input:
    - 利用者が README から依存追加方法を探す
  - Output:
    - `./spec-dock/scripts/spec-dock deps add --from <issue-a> --to <issue-b>` と `deps check` / `sync` / `validate` の導線が提示される

## 用語
- TERM-001:
  - `.meta.json`
    - node metadata の canonical storage。dependency metadata もここに統合されている。
- TERM-002:
  - `depends_on`
    - `.meta.json` top-level に保持される dependency edge 配列。
- TERM-003:
  - command-first mutation
    - dependency の追加・削除を metadata 直編集ではなく `spec-dock deps add/remove` 経由で行う運用契約。

## 未確定事項
- なし。
