---
種別: 要件定義書（Issue）
ID: "iss-00038"
タイトル: "Docs Dogfooding Parity and Final Regression Gate"
関連GitHub: ["#38"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["epic-00033", "init-local-00003"]
---

# iss-00038 Docs Dogfooding Parity and Final Regression Gate — 要件定義（WHAT / WHY）

## 目的
- epic `epic-00033` の最後の open slice として、provider docs / dogfooding docs の close-out と final spec review record を完成させる。
- `iss-00040` が完了させた wrappers / domain / dogfooding parity / final regression evidence を参照可能な形で束ね、`E-AC-005` の docs/spec-review slice を客観的に閉じる。
- この issue は epic の `E-RQ-005` を close し、`E-AC-005` の docs/spec-review slice を完了させる owner である。

## 背景・現状
- 現状の挙動:
  - `spec-dock/dashboard.md` と `spec-dock/.agent/index*.json` では、todo は `iss-00038` のみで `deps.ready=true` になっている。
  - `epic-00033/report.md` では `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` が完了済み、残件は `iss-00038` の docs close-out と final spec review record のみと整理されている。
  - targeted docs list である `reference_github.md` / `reference_naming.md` / `reference_sync.md` は provider-side と dogfooding 側で現時点ですでに一致している。
  - `iss-00040` が owner だった regression/parity 系 evidence は現スナップショットでも pass しており、full suite / parity / `validate` / `sync` は current contract に整合している。
- 現状の課題:
  - `iss-00038` 自身の issue spec は split 前の責務を引きずっており、`iss-00040` へ移管済みの final regression ownership が requirement/design/plan に残っている。
  - docs parity が現時点で no-op に見えても、close evidence と final spec review record が整理されない限り epic close-out を客観的に判定できない。
- 再現手順:
  1. `spec-dock/active/epic/plan.md` と `spec-dock/active/epic/report.md` を確認する。
  2. `iss-00038` の現 spec が split 前の責務を含んでいることを確認する。
  3. provider/dogfooding の targeted docs list を比較すると、現時点では内容差分がないことを確認できる。
- 観測点:
  - Docs:
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
    - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
    - `spec-dock/docs/reference_github.md`
    - `spec-dock/docs/reference_naming.md`
    - `spec-dock/docs/reference_sync.md`
  - State:
    - `spec-dock/dashboard.md`
    - `spec-dock/.agent/index-all.json`
    - `spec-dock/.agent/index.json`
  - Upstream evidence:
    - `epic-00033/report.md`
    - `iss-00040/report.md`
- 情報源:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `spec-dock/active/epic/report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/plan.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - epic close を判断する maintainer / spec reviewer
- 代表シナリオ:
  - maintainer が `epic-00033` を close する前に、targeted docs list、`validate` / `sync` の実行結果、upstream issue evidence、final spec review verdict を 1 つの issue close-out evidence として確認する。
  - reviewer が `iss-00038` と `iss-00040` の責務非重複を確認しつつ、`E-AC-005` の残 slice が docs/spec-review だけであることを判定する。

## スコープ
- MUST:
  - `iss-00038` の scope を `docs parity + final spec review record` に再固定し、`iss-00040` へ移管済みの責務を除外する。
  - targeted docs list 6 ファイルについて、old local-only / sequential / index assumption が残っていないことを確認し、必要なら provider-side と dogfooding 側の両方を更新する。
  - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` の close-out evidence を取得する。
  - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence を参照する final spec review record を作成し、verdict を `pass` に到達させる。
- MUST NOT:
  - `iss-00040` が owner である wrappers / domain / dogfooding parity / final regression を再実行前提で抱え込まない。
  - runtime contract や test expectation の realignment を、この issue の close-out のために再度変更しない。
  - docs parity を provider-side だけで閉じない。
- OUT OF SCOPE:
  - create / naming / sync / migration contract の中核実装変更
  - stale-contract cluster の再調査や full regression の再所有
  - `iss-00040` 完了済み evidence の差し替え

## 境界
- Always:
  - `iss-00038` は docs close-out owner であり、`iss-00040` の final regression evidence を参照して閉じる。
  - targeted docs list の評価は provider-side source of truth と checked-in dogfooding docs の両方で行う。
  - close evidence は docs review結果、`validate` / `sync` の実行結果、final spec review record の 3 本柱で残す。
  - upstream issue report の記述と generated state / epic report が衝突する場合は、`spec-dock/.agent/index-all.json` と `spec-dock/active/epic/report.md` を close status の優先正本とする。
- Ask:
  - targeted docs list 以外に old contract assumption が見つかった場合、それが `iss-00038` の docs close-out に含めるべき drift か、別 issue に分けるべき drift かを design/plan で判断する。
- Never:
  - `iss-00040` が閉じた scope を再び `iss-00038` に混ぜて完了条件を曖昧にする。
  - upstream evidence が欠けたまま narrative だけで epic close を宣言する。

## 非交渉制約
- final spec review verdict は `pass` を要求する。
- final spec review record には `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence 参照を含める。
- `validate` / `sync` は current repo state に対して exit=0 を示す。
- 新たに uppercase path を増やさない。

## 前提
- `iss-00040` は完了済みで、stale-contract / final regression / dogfooding parity evidence はその report に集約されている。
- `epic-00033/report.md` は「残りは `iss-00038` のみ」という進捗認識を正本としている。
- 現時点の targeted docs list は provider/dogfooding 間で一致しているため、docs 作業は no-op diff で閉じる可能性がある。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer / reviewer
  - Given:
    - targeted docs list を確認する
  - When:
    - provider-side と dogfooding 側の 6 ファイルを current contract 観点でレビューする
  - Then:
    - old local-only / sequential / index assumption が残っていないことを示せる
    - 差分が必要なら provider-side と dogfooding 側の両方で更新される
    - 差分が不要なら no-op であることが close evidence として説明される
  - 観測点:
    - targeted docs diff または no-op parity evidence
- AC-002:
  - Actor:
    - maintainer / reviewer
  - Given:
    - docs close-out 候補が揃っている
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する
  - Then:
    - 両コマンドが exit=0 で成功し、current repo state と generated state が close-out 可能であることを示せる
  - 観測点:
    - command outputs
    - `spec-dock/dashboard.md` / `.agent/index*.json` の整合
- AC-003:
  - Actor:
    - spec reviewer
  - Given:
    - docs evidence、command evidence、upstream issue evidence が揃っている
  - When:
    - final spec review record を確認する
  - Then:
    - verdict が `pass` である
    - `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の close evidence 参照が追える
    - `iss-00038` と `iss-00040` の non-overlap が明記されている
  - 観測点:
    - final spec review record

## 例外・エッジケース
- EC-001:
  - 条件:
    - targeted docs list がすでに完全一致で、内容変更が不要
  - 期待:
    - docs close-out は no-op でよいが、parity evidence と current contract review 結果を記録しなければ close にしない
  - 観測点:
    - `diff -q` 相当の parity evidence
- EC-002:
  - 条件:
    - `validate` / `sync` は成功するが、dashboard や index snapshot の open/ready 認識が epic report と整合しない
  - 期待:
    - close-out を停止し、generated state drift として原因を切り分ける
  - 観測点:
    - command outputs
    - generated state review
- EC-003:
  - 条件:
    - upstream issue evidence の参照先が不足している、または final spec review で ownership conflict が再発する
  - 期待:
    - `iss-00038` 単独で強行 close せず、欠落 evidence または ownership 競合を docs に明記して reviewer 判断を待つ
  - 観測点:
    - review feedback
    - evidence index

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - targeted docs parity evidence
    - `validate` / `sync` の成功結果
    - `iss-00040/report.md` を含む upstream close evidence
  - Output:
    - `E-AC-005` docs/spec-review slice を閉じる final spec review record

## 用語（ドメイン語彙）
- TERM-001:
  - targeted docs list:
    - provider-side と dogfooding 側の `reference_github.md` / `reference_naming.md` / `reference_sync.md`
- TERM-002:
  - final spec review record:
    - final verdict、参照 evidence、non-overlap check を束ねた close-out 記録
- TERM-003:
  - docs close-out owner:
    - `iss-00040` の regression ownership を再実行せず、docs parity と spec review の最後の slice だけを閉じる責務

## 未確定事項
- なし:
  - split 後の ownership boundary は epic plan / epic report / `iss-00040` report で確定している
