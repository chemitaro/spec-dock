---
種別: ディスカッション
ID: "033-disc-pr29-r16-checked-in-json-state-helper-parity-analysis"
タイトル: "PR #29 R16 checked-in json_state helper parity を分析する"
状態: "done"
作成者: "Codex CLI"
作成日: "2026-03-20"
更新日: "2026-03-20"
関連: ["issue-28-runtime-regression-bugs"]
---

# 結論

- 指摘は妥当
- checked-in `presentation/json_state.py` に provider-side の `_normalize_repo_slug(...)` parity が欠けており、linked import 後の post-sync artifact rendering で `NameError` を起こしうる
- `S90G` で checked-in parity refresh と no-crash regression を追加して閉じる

```plantuml
@startuml
title checked-in json_state parity gap

rectangle "provider json_state.py" as provider {
  [_normalize_repo_slug]
  [repo-aware github fallback]
}

rectangle "checked-in json_state.py" as checkedin {
  [repo-aware github fallback call]
  [missing helper]
}

provider --> checkedin : helper parity missing
@enduml
```
