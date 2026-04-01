---
種別: 要件定義書（Issue）
ID: "iss-00034"
タイトル: "GitHub Mandatory Node Creation Contract"
関連GitHub: ["#34"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-28"
親: ["epic-00033", "init-local-00003"]
---

# iss-00034 GitHub Mandatory Node Creation Contract — 要件定義（WHAT / WHY）

## 目的
- `initiative / epic / issue` の create contract を GitHub mandatory に切り替え、local-only path を廃止する。
- single GitHub repo 前提の canonical repo scope を create entrypoint で固定し、node identity collision の温床を残さない。

## 背景・現状
- 現状の挙動:
  - create contract 自体は GitHub mandatory へ寄ってきているが、repo scope 解決と import boundary の strictness がまだ揺れている。
  - create 時の repo scope 解決と `.meta.json` persistence の contract は固定が進んでいる一方、foreign issue URL import の reject 境界が十分に閉じ切れていない。
  - review fix の過程で `import ... --allow-foreign-url` から `iss-local-*` fallback が一時的に復元され、accepted policy と実装が不整合になった。
- 現状の課題:
  - 分散環境では local-only create path が sequential id collision の原因になる。
  - canonical repo scope が曖昧だと、same repo / cross-repo reject の境界が実装依存になる。
- 再現手順:
  1. local-only 前提の create flow を許すと、別 worktree / 別 clone で node id が衝突しうる。
  2. repo scope 解決が曖昧なままだと、create / validate の reject 条件が揺れる。
- 観測点:
  - CLI:
    - `./spec-dock/scripts/spec-dock new initiative`
    - `./spec-dock/scripts/spec-dock new epic`
    - `./spec-dock/scripts/spec-dock new issue`
  - Artifact:
    - `.meta.json`
  - Validation:
    - `./spec-dock/scripts/spec-dock validate`
- 情報源:
  - `epic-00033` requirement / design / plan
  - `epic-00033/discussions/20260327t093000z-adr-github-mandatory-node-linkage.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` maintainer
  - dogfooding repo maintainer
- 代表シナリオ:
  - 新しい initiative / epic / issue を current repo の GitHub issue と結びつけて正規作成する。
  - current repo と異なる GitHub issue や ambiguous repo scope を reject する。

## スコープ
- MUST:
  - `new initiative` / `new epic` / `new issue` を GitHub issue mandatory に揃える。
  - canonical repo scope を `origin` remote から一意に解決する contract を固定する。
  - `.meta.json.github.issue_number` / `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` を lowercase canonical repo scope で保持する。
  - empty workspace / first node を含む create contract の acceptance を固定する。
  - `initiative / epic / issue` node に対する foreign issue URL import を strict reject に揃え、`iss-local-*` fallback を再導入しない。
- MUST NOT:
  - local-only fallback を残さない。
  - cross-repo linkage を許可しない。
- OUT OF SCOPE:
  - discussion / ADR の filename naming 変更
  - `sync` による ADR mirror / sync-generated artifact の再生成
  - foreign issue import reject 以外の import main processing 本体変更
  - docs parity の全面クローズ

## 境界
- Always:
  - canonical repo scope の正本は `origin` remote が指す GitHub repository とする。
  - `origin` missing / non-GitHub remote / fetch-push mismatch / configured scope mismatch は fail-fast にする。
  - first node から same repo scope に束縛する。
  - sync の main processing と sync-generated artifact regeneration は read-only のままにし、本 issue で対象化しない。
  - import については foreign issue URL を node identity に変換しない strict reject への是正だけを対象内とし、external reference model や multi-repo identity は扱わない。
  - validation/preflight は malformed scope を fail-closed にし、single-repo contract と矛盾する exemption を残さない。
- Ask:
  - GitHub issue body / labels / project metadata の扱いは後続 issue で必要なら拡張する。
- Never:
  - create 成功後に local-only node を残す。
  - repo scope が未確定のまま node を作成する。

## 非交渉制約
- single GitHub repo 前提を崩さない。
- `owner/repo` 比較は canonical lowercase basis で行う。
- old workspace に対する in-place 自動移行はこの issue で約束しない。

## 前提
- GitHub auth / CLI が利用可能である。
- consumer repo には GitHub を向く `origin` remote がある、または無い場合は create を失敗させる。
- `epic-00033` で固定した GitHub mandatory 方針を採用済みである。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `origin` が current consumer repo の GitHub repository を指している
  - When:
    - `new initiative` / `new epic` / `new issue` を実行する
  - Then:
    - create は GitHub issue linkage 必須で進み、`.meta.json.github.issue_number` / `.meta.json.github.repo_owner` / `.meta.json.github.repo_name` が lowercase canonical repo scope で保存される
  - 観測点:
    - targeted create tests
    - created `.meta.json`
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - empty workspace / first node create、または configured scope ありの workspace
  - When:
    - create flow を実行する
  - Then:
    - first node から `origin` 解決結果に束縛され、configured scope 不一致や cross-repo target は reject される
  - 観測点:
    - canonical resolver tests
    - create reject tests
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - legacy workspace mismatch や old contract expectation が残っている
  - When:
    - create / validate contract を確認する
  - Then:
    - in-place 自動移行は保証されず、legacy mismatch は `new` では contract error、`validate` では validation error として non-zero で fail-fast に扱われ、checked-in data の無断書き換えを目的としない境界が先行固定される
    - この issue の `validate` / preflight pre-guard は `new` contract 由来の node linkage mismatch と malformed scope の fail-closed に整合し、sync-generated artifact regeneration や external reference model の新設は対象外とする
  - 観測点:
    - boundary docs diff
    - validate / migration contract tests

- AC-004:
  - Actor:
    - maintainer
  - Given:
    - current repo と異なる GitHub issue URL を `initiative / epic / issue` node として import しようとしている
  - When:
    - `import ... --allow-foreign-url` を含む import flow を実行する
  - Then:
    - foreign issue URL は node identity として reject され、`iss-local-*` fallback や cross-repo node 作成は行われない
    - エラーメッセージは single-repo / GitHub-backed identity に基づく reject 理由を示す
  - 観測点:
    - import reject tests
    - no-write / no-side-effect verification

## 例外・エッジケース
- EC-001:
  - 条件:
    - `origin` remote が存在しない
  - 期待:
    - create は fail-fast で止まり、repo scope 未確定の node を作らない
  - 観測点:
    - create error tests
- EC-002:
  - 条件:
    - `origin` fetch/push URL が別 `owner/repo` を指す、または non-GitHub remote である
  - 期待:
    - canonical repo scope resolver は reject し、same repo scope を曖昧にしない
  - 観測点:
    - canonical resolver reject tests
- EC-003:
  - 条件:
    - 既存 issue target が current repo と別 repo を指す
  - 期待:
    - cross-repo linkage として reject される
  - 観測点:
    - create reject tests
- EC-004:
  - 条件:
    - foreign issue URL import に `--allow-foreign-url` が付与されている
  - 期待:
    - compatibility escape hatch ではなく explicit reject として扱われ、local fallback を作らない
  - 観測点:
    - import reject tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock new issue --epic epic-00033 --title "Example"`
  - Output:
    - `iss-xxxxx` node と GitHub issue linkage が current repo scope で生成される

## 用語（ドメイン語彙）
- TERM-001:
  - canonical repo scope:
    - consumer repo の Git remote `origin` から正規化して得る current GitHub `owner/repo`
- TERM-002:
  - local-only path:
    - GitHub issue linkage を持たずに node を作る旧 contract
- TERM-003:
  - first node binding:
    - empty workspace で最初の node が canonical repo scope に束縛されること

## 未確定事項
- なし:
  - create contract の方針は epic spec で固定済み
