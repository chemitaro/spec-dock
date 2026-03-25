---
種別: disc
ID: "007-disc"
タイトル: "Manual Rerun Current State"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "005-disc-review-loop-and-outcome-matrix-lessons.md",
  "006-disc-repo-scope-and-create-state-lessons.md",
  "/srv/mount/spec-dock/manual-tests/reports/2026-03-24-issue-28-contract-rerun/summary.md"
]
---

# 007-disc Manual Rerun Current State

## 目的
- dogfooding 再開時点の current runtime を、過去の issue-28 文脈を知らなくても読める形で要約する。
- 「どこまで直っているか」「どの前提で使うべきか」を initiative 側へ残す。

## current state
- current runtime は通常利用可能である。
- 主要 contract は manual rerun で再確認済みである。
- ただし設計は「曖昧さを自動修復する」より「曖昧なときは fail-closed で止まる」を優先している。

## manual rerun で確認できたこと
- overlap 環境でも canonical GitHub URL と `--id` は安定して解決される。
- bare numeric と `--github-issue` は overlap 下で fail-closed を維持する。
- already-normalized metadata は no-origin でも continuity を維持する。
- stale active recovery、readonly `.meta.json` non-mutation、checked-in parity は崩れていない。

## 未解決だが bug と呼ばないもの
- legacy unscoped current-repo link の automatic persistence upgrade
- overlap-heavy workspace で bare numeric selector を便利に使う運用
- 人手で metadata / dependency を崩したときの self-heal UX

## 再開時の運用 guidance
- selector は canonical URL または `--id` を優先する。
- no-origin copy を継続利用する前に、対象 node が already-normalized metadata を持つか確認する。
- legacy unscoped node に `sync --github` の自動修復を期待しない。
- validator / sync が dependency invalid で止まったときは、runtime failure と決めつけず graph 整合性を先に確認する。

## 現時点の判断
- main open point は correctness bug というより、manual remediation と operator guidance の不足である。
- そのため、次の投資先は automatic backfill の拡張ではなく、explicit remediation flow や doctor guidance 強化である。

## 移設メモ
- 本 discussion は `spec-deps/current/discussions/062-disc-manual-rerun-current-state-analysis.md` の要点を initiative 側へ移したものである。
- 実行証跡そのものは `manual-tests/reports/2026-03-24-issue-28-contract-rerun/` を参照する。
