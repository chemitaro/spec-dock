---
種別: discussion
ID: "056"
タイトル: "manual test findings root-cause analysis after enriched exploratory round"
状態: "open"
作成者: "Codex CLI"
作成日: "2026-03-24"
関連: ["report.md", "design.md", "plan.md", "discussions/055-disc-manual-test-round-20260324-s04k-repo-scope-plan.md"]
---

# manual test findings root-cause analysis after enriched exploratory round

## 対象証跡
- `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/summary.md`
- `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/execution-log.md`
- `manual-tests/reports/2026-03-24-issue-28-manual-repo-scope-active/evidence/`
- consultant / repo_analyst analysis

## 結論サマリー
- 今回の main blocker は 1 つで、`no-origin` copied workspace に mixed scoped/unscoped GitHub linkage を持ち込むと `sync --github` / `validate` / `doctor` が恒久的に fail-closed する点である
- これは fail-closed policy 自体が誤っているのではなく、`origin` がある時点で current-repo linked node の repo scope を persisted metadata へ正規化/backfill していないことが根本原因である
- `--github-issue` ambiguity は現行契約どおりの convenience selector の fail-closed であり、今回の primary defect ではない
- `owner/repo#n` の command target 非対応は surface 差の問題で、即時の correctness bug ではなく UX/doc policy の follow-up でよい
- `spec-dock update` が plain file / invalid dir conflict を自動修復しないのは非破壊ポリシーとして妥当で、default auto-heal は推奨しない

## F1 no-origin + mixed scoped/unscoped linkage ambiguity

### 観測
- `origin` を remove した copied workspace では canonical URL と `--id` は継続利用できた
- 一方で `sync --github` / `validate` / `doctor` は `github.issue_number=2` の mixed scoped/unscoped linkage ambiguity で fail-closed した

### 根本原因
- current repo slug を解決できる間は、unscoped current-repo linked node を current repo とみなして repo-aware uniqueness / fallback fetch / target resolution を行える
- しかし persisted metadata 自体には current repo linked node の `github.repo_owner/name` が必ずしも backfill されておらず、`origin` を失うと effective repo scope を再構成できない
- その結果、validation / deps resolution は「scoped と unscoped が同じ issue number に混在した危険状態」として fail-closed し続ける

### 修正要否
- `required`
- 理由:
  - no-origin continuation は manual test plan で意図的に扱っただけでなく、copied workspace / temp checkout / exported environment で自然に起こる
  - canonical URL target だけ通っても、`sync --github` / `validate` / `doctor` が止まると実運用の継続性を欠く

### 修正案
- option A:
  - fail-closed を緩めて、`current_repo_slug is None` でも unscoped を current repo 扱いで推測する
  - 欠点:
    - genuinely ambiguous graph を silent mis-resolution しやすい
- option B:
  - `origin` がある時点で current-repo linked node に repo scope を persisted metadata へ backfill / normalize し、copy/update/sync 前後で mixed state を減らす
  - 利点:
    - fail-closed を維持したまま no-origin operability を回復できる
    - validation / deps / target resolution の safety model を崩さない
- option C:
  - no-origin 用の explicit normalization command を導入し、operator が copy 前または copy 後に normalize してから続行する
  - 利点:
    - migration risk を切り離しやすい
  - 欠点:
    - operator burden が残る

### 推奨
- best practice は `option B` を主、必要なら `option C` を補助にすること
- つまり:
  - current repo slug が解決できる workspace では current-repo linked node の repo scope を metadata へ正規化する
  - no-origin では真に不明な mixed state だけ fail-closed に残す
  - error / doctor guidance には「origin 付き workspace で normalize してから copy」を明示する

## F2 `--github-issue` ambiguity under overlap

### 観測
- overlap-rich graph で `--github-issue 6` は ambiguity fail-closed した
- canonical URL と `--id` は同条件で成功した

### 根本原因
- `--github-issue` は unscoped `TargetRef(github_issue)` を作り、repo scope を持たない convenience selector である
- same-number coexistence 下では current repo 優先推測をせず、複数 match なら fail-closed する

### 修正要否
- `not required` for correctness
- これは manual test でも docs/auto-tests と整合した現行契約である

### 修正案
- option A:
  - current repo 優先 heuristic を導入する
- option B:
  - 現行 fail-closed を維持し、error message を強化する

### 推奨
- best practice は `option B`
- overlap 環境では canonical URL または `--id` を標準 guidance にし、numeric convenience selector を authoritative selector にしない

## F3 `owner/repo#n` command target 非対応

### 観測
- dependency ref では `owner/repo#n` が通る
- しかし `active set` / `deps check` の positional target では invalid target になった

### 根本原因
- dependency resolver と command target parser の surface contract が分かれており、command target は canonical URL / numeric / node id に限定されている

### 修正要否
- `optional`
- correctness より UX / contract consistency の問題

### 修正案
- option A:
  - command target parser でも `owner/repo#n` を受理する
- option B:
  - 非対応のまま維持し、docs / error message に「scoped shorthand は depends_on 用、command target は canonical URL 推奨」と明記する

### 推奨
- best practice は当面 `option B`
- command target の exact selector は canonical URL に寄せ、surface 差は docs / error で明示する

## F4 active entrypoint plain-file / invalid-dir conflict

### 観測
- stale symlink / stale `.path` / healthy real entrypoint / placeholder rebuild は self-heal した
- しかし plain file conflict / invalid dir conflict は update 後も残った

### 根本原因
- installer `update` は `spec-dock/active/*` を non-destructive に扱い、managed pointer と確信できる artifact 以外は壊さない
- explicit file/dir conflict は user-authored か accidental overwrite か判別できず、自動削除より preserve を優先している

### 修正要否
- `not required` for default auto-heal
- ただし guidance / diagnostics は改善余地が大きい

### 修正案
- option A:
  - default で auto-heal する
  - 欠点:
    - user data を誤削除する危険がある
- option B:
  - non-destructive を維持し、doctor/update の warning と手動修復 guidance を強化する
- option C:
  - opt-in `--force-repair-active-entrypoints` のような専用 repair surface を追加する

### 推奨
- best practice は `option B`
- 将来必要なら `option C` を separate issue で検討する

## 優先順位
1. F1 no-origin mixed scoped/unscoped normalization
2. F1 向け doctor / error guidance 強化
3. F2 ambiguity message 改善
4. F3 command target shorthand policy の docs/error 明確化
5. F4 active conflict manual-repair guidance 強化

## 推奨アクション
- 次の corrective scope は `no-origin continuity` を中心に切る
- requirement / design / plan では次を固定する
  - current-repo linked node の repo scope normalization/backfill contract
  - no-origin copy 後も repo-aware read path が継続する acceptance
  - truly ambiguous mixed scope だけ fail-closed を維持する境界
- active conflict は non-destructive default を崩さず、doctor/update guidance を別 corrective scope に分ける
