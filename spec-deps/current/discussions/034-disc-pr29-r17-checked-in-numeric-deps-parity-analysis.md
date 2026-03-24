---
種別: ディスカッション
ID: "034-disc-pr29-r17-checked-in-numeric-deps-parity-analysis"
タイトル: "PR #29 R17 checked-in numeric deps parity を分析する"
状態: "done"
作成者: "Codex CLI"
作成日: "2026-03-20"
更新日: "2026-03-20"
関連: ["issue-28-runtime-regression-bugs"]
---

# 結論

- 指摘は妥当
- provider-side `infra/deps_reader.py` は current repo slug aware な numeric dep 解決へ更新済みだが、checked-in runtime は stale reader のままで same-number overlap 時に `Ambiguous github.issue_number=123` を再発しうる
- `S90G` で checked-in `infra/deps_reader.py` を refresh し、numeric deps overlap parity regression を追加して閉じる

```plantuml
@startuml
title checked-in numeric deps parity gap

rectangle "provider deps_reader.py" as provider {
  [resolve current repo slug]
  [repo-aware numeric refs]
}

rectangle "checked-in deps_reader.py" as checkedin {
  [bare github.issue_number refs]
}

provider --> checkedin : parity drift
@enduml
```
