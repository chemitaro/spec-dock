---
種別: discussion
ID: "062"
タイトル: "issue-28 manual rerun current state analysis after contract rerun"
状態: "open"
作成者: "Codex CLI"
作成日: "2026-03-24"
関連: ["report.md", "061-disc-manual-rerun-contract-plan.md", "056-disc-manual-test-findings-root-cause-analysis.md", "manual-tests/reports/2026-03-24-issue-28-contract-rerun/checklist.md", "manual-tests/reports/2026-03-24-issue-28-contract-rerun/execution-log.md", "manual-tests/reports/2026-03-24-issue-28-contract-rerun/summary.md"]
---

# issue-28 manual rerun current state analysis after contract rerun

## 要旨
- 2026-03-24 の contract rerun により、issue-28 で直近に問題化していた runtime contract は、主要経路で再度確認できた
- 全体判定は `conditional-pass` であり、主因は product bug の再発ではなく、long-run stress 中に人為的に投入した invalid dependency により validator / sync が設計どおり停止したためである
- 現在の実装は「曖昧さを解消して自動修復する」方向ではなく、「repo overlap / no-origin / legacy unscoped metadata が混在しても fail-closed で安全に止まる」方向に整理されている
- そのため、現状の最大論点は「まだ壊れているバグがあるか」ではなく、「fail-closed 契約と運用 guidance を利用者が理解して使えるか」に移っている

## このレポートの目的
- manual test artifacts の内容を、issue 正本の discussion として読みやすく要約する
- 「何が直ったのか」「どこまで確認できたのか」「何が未解決なのか」を current issue の外側から見ても追えるようにする
- 今後の判断を、追加実装ではなく運用 guidance / manual remediation / follow-up scope の観点で支援する

## 対象 evidence
- test plan:
  - [061-disc-manual-rerun-contract-plan.md](/srv/mount/spec-dock/spec-deps/current/discussions/061-disc-manual-rerun-contract-plan.md)
- checklist:
  - [checklist.md](/srv/mount/spec-dock/manual-tests/reports/2026-03-24-issue-28-contract-rerun/checklist.md)
- execution log:
  - [execution-log.md](/srv/mount/spec-dock/manual-tests/reports/2026-03-24-issue-28-contract-rerun/execution-log.md)
- summary:
  - [summary.md](/srv/mount/spec-dock/manual-tests/reports/2026-03-24-issue-28-contract-rerun/summary.md)

## 背景整理
- issue-28 の後半では、GitHub issue linkage の repo scope、legacy unscoped metadata、no-origin workspace、stale active recovery、checked-in runtime parity が複合的に絡む review loop が続いていた
- とくに `S03L` 以降では、従来の「現在 repo らしいものを sync 時に補完していく」発想から離れ、write-time normalization と already-normalized metadata continuity を基準契約に置き直した
- その結果、legacy unscoped current-repo link を bulk `sync --github` で自動 backfill する path は最終的に撤去され、manual remediation 別 scope に分離された
- 今回の manual rerun は、この最終契約が実動作と一致しているかを確かめるための round である

## 今回確認したかった問い
- overlap 環境で same-number issue があっても exact selector は安定して使えるか
- no-origin になっても、already-normalized metadata は継続利用できるか
- legacy unscoped metadata は危険な自動補完をせず、fail-closed を維持するか
- stale active manifest/path recovery は non-destructive に動くか
- checked-in runtime は provider-side の契約に追随しているか
- long-run session で GitHub close / reopen / edit / new、initiative / epic / issue / deps churn を重ねても、期待された壊れ方と期待された継続性が保たれるか

## 結論

### 1. 主要 contract は再確認できた
- overlap 下でも canonical URL と `--id` は安定して current/foreign を区別できた
- bare numeric と `--github-issue` は、same-number overlap 下で一貫して fail-closed した
- already-normalized current-repo metadata は、origin を失っても `sync --github`、`deps check <canonical url>`、`active set <canonical url>`、`active set --id` で continuity を保った
- checked-in runtime でも `validate` / `doctor` / `sync --github` / `deps check` / `active set` の core contract が崩れていなかった

### 2. legacy unscoped current-repo link は「直らない」のではなく「勝手に直さない」が正しい挙動になっている
- manual で unscoped 化した current-linked node は、no-origin 状態で `sync --github` をかけても `.meta.json` が scoped metadata へ変化しなかった
- canonical current URL targeting は `No node found` 系の fail-closed に戻り、`--id` は node 自体の参照だけ維持した
- これは regression ではなく、`S03N` / `S03O` / `060` で確定した最終契約どおりの結果である
- したがって、現在残っている gap は runtime bug というより、manual remediation command がまだ別 scope のままであることによる運用上の不便さである

### 3. readonly `.meta.json` と stale active recovery は安全側の契約を維持できている
- readonly legacy `.meta.json` は sync/validate/doctor 後も byte-identical で、不要な mutation は観測されなかった
- stale active recovery では placeholder fallback、healthy entrypoint priority、plain-file conflict non-destruction が期待どおりに動いた
- これにより、「直そうとして余計に壊す」種類の regressions は今回の round では観測されていない

### 4. long-run stress でも product bug の再燃は確認されなかった
- RR-07 では 2 initiatives、4 epics、10 以上の issues、複数 dependencies、current/foreign overlap、GitHub close/reopen/edit/new を混在させた
- initial run で validation/sync が止まったのは、stress 用に投入した dependency 変更が invalid descendant dependency を作ったためであり、これは validator の guard が効いた結果だった
- remediation continuation 後は corpus を `nodes=20` まで拡張し、no-origin continuation、legacy unscoped fail-closed、checked-in parity 再サンプルまで完了した
- したがって、今回の `conditional-pass` は「現行実装が不安定」という意味ではなく、「stress round に block event はあったが、その block は仕様どおりだった」という意味で読むのが妥当である

## 現在の問題をどう理解すべきか

### 解消済みと見てよい問題
- overlap repo で exact selector が不安定になる問題
- normalized metadata が no-origin で使えなくなる問題
- checked-in runtime が provider-side 契約から drift する問題
- stale active recovery が destructive になったり、placeholder へ戻せなくなる問題
- readonly `.meta.json` を不用意に mutate する問題

### 未解決だが、今は bug と呼ばない問題
- legacy unscoped current-repo link を permanent に scoped metadata へ戻す自動救済経路
- overlap-heavy workspace で bare numeric selector を便利に使う運用
- 人手で dependency / metadata を崩したときに、どこまで self-heal させるべきかという UX

### 依然として注意が必要な実運用上のリスク
- `origin` を失った overlap workspace では、legacy unscoped metadata が残っていると exact repo-scoped lookup に乗らない
- bare numeric / `--github-issue` は overlap 下で convenience path ではなく hazard path と考えるべき
- 長時間セッションで metadata や dependency を手で崩すと、runtime は安全側に止まるが、operator は「急に使えなくなった」と感じやすい

## 利用者への実用的な guidance
- overlap がありうる repo では canonical GitHub URL または `--id` を主 selector にする
- no-origin copy を使う前に、対象 node が already-normalized metadata を持っているかを確認する
- legacy unscoped node を見つけても、現時点では `sync --github` に自動修復を期待しない
- validator / sync が dependency invalid を返した場合は、runtime failure と決めつけず graph の整合性を先に確認する
- checked-in runtime を使う場面でも provider-side と同等の contract を前提にしてよいが、曖昧 selector の fail-closed は回避しない

## 今の判断
- issue-28 の current runtime は、少なくとも今回の手動 rerun で再発 blocker を示していない
- 現在の open point は implementation correctness ではなく、manual remediation と operator guidance の不足である
- したがって、次の投資先としては「さらに自動 backfill を増やす corrective patch」よりも、「explicit remediation flow を設計する」「guidance を CLI/doctor/docs に落とす」ほうが妥当である

## 推奨 next action
- option 1:
  - この round をもって issue-28 の現行 contract 検証は十分と判断し、merge / close 判断へ進む
- option 2:
  - strictness を上げるため、RR-07 だけ clean-slate で再実施し、`overall pass` を取りに行く
- option 3:
  - follow-up issue として、legacy unscoped current-repo link 向け manual remediation command または doctor guidance 強化を切り出す

## 推奨
- 現時点の最良案は option 3 である
- 理由:
  - 現行 runtime の fail-closed contract は manual rerun で再確認できている
  - unresolved point は product correctness の不足より UX / operability の不足に寄っている
  - 自動 backfill を再度広げるより、明示的 remediation のほうが安全で review loop を再燃させにくい
