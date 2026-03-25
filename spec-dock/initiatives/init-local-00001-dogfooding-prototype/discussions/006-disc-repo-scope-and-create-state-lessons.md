---
種別: disc
ID: "006-disc"
タイトル: "Repo Scope And Create State Lessons"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "004-adr-runtime-cli-layered-architecture.md",
  "005-disc-review-loop-and-outcome-matrix-lessons.md"
]
---

# 006-disc Repo Scope And Create State Lessons

## 目的
- issue-28 を通じて明確になった 2 つの durable problem domain を残す。
- 1 つは repo-scoped reference model、もう 1 つは create/read 側で共有される state model である。

## 結論
- GitHub-linked node を扱う surface では、repo scope を end-to-end で保持する前提が必要である。
- create の中間状態は boolean flag の寄せ集めではなく、reader / doctor / validate と共有する state model として扱うべきである。
- legacy unscoped current-repo linkage は、bulk heuristic backfill で救済するより、fail-closed と explicit remediation の組み合わせで扱う方が安全である。

## lesson 1: repo scope は write/read/selector を通して保持する
- create/import/meta だけが repo scope を知っていても不十分である。
- active/deps/target resolution/dependency ref でも scope を失わないようにしないと、foreign support を入れても別 surface で current-repo-only へ暗黙還元される。
- user-facing selector でも、canonical URL、`owner/repo#123`、bare number(current-repo-only) の意味を切り分ける必要がある。

## lesson 2: create state は shared model で扱う
- `local_write_committed: bool` のような単一 flag では、`none / partial / committed / verified / stale` を表現しきれない。
- writer だけでなく reader / doctor / validate が同じ phase model を使うことで、classification と recovery guidance が安定する。

## lesson 3: unsafe self-heal は入れない
- legacy unscoped current-repo link は一見すると sync-time backfill で直したくなる。
- しかし lone unscoped node の current repo 所属を positive に証明できないまま bulk mutate を許すと、silent mis-normalization を起こす。
- したがって current runtime では、bulk `sync --github` の heuristic repair より fail-closed を優先し、救済が必要なら explicit remediation を別 surface に切る。

## 現在の運用含意
- overlap-heavy repo では canonical URL と `--id` を primary selector とする。
- bare numeric は convenience path であり、安全な primary path ではない。
- no-origin 継続を期待するなら、already-normalized metadata を前提にする。
- legacy unscoped metadata の永続 upgrade は、今後も opt-in remediation として設計するのが妥当である。

## 移設メモ
- 本 discussion は `spec-deps/current/discussions/053-disc-pr29-root-cause-repo-scope-and-create-state-analysis.md` と `060-disc-pr29-r39-legacy-unscoped-persistence-gap-analysis.md` の durable な判断を統合した。
- 途中の corrective scope 単位の手直しは落とし、将来も使える判断基準に絞っている。
