---
種別: 要件定義書（Issue）
ID: "iss-00103"
タイトル: "Agentic TDD report decision ledger"
関連GitHub: ["#103"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
親: ["epic-00067", "init-local-00003"]
---

# iss-00103 Agentic TDD report decision ledger — 要件定義（WHAT / WHY）

## 目的
- `report.md` を、Agentic TDD の実行結果を記録する observed evidence ledger に加えて、実装中の仕様解釈・判断・逸脱・tradeoff・open question・promotion を追跡する decision ledger として拡張する。
- `plan.md` で agent に自律的な具体化を許す一方、その判断理由を後から検証できるようにする。
- worker / main orchestrator / reviewer の責任分界を明確にし、worker の一次情報を canonical `report.md` へ安全に統合できる workflow contract を定義する。
- 将来も効く判断を `report.md` に閉じ込めず、`design.md` / ADR / plan amendment / follow-up issue へ昇格する運用を定義する。

## 背景・現状
- 現状の挙動:
  - `iss-00102` で、Issue `plan.md` は executable Agentic TDD workflow contract として整理された。
  - `plan.md` は実装前の planned contract、`report.md` は observed evidence ledger という境界が明確になった。
  - 実装 agent は `plan.md` の guardrails、test obligation、evidence destination、amendment trigger に従い、詳細をある程度自律的に具体化する。
- 現状の課題:
  - agent の自律性を高めるほど、実装中に「仕様をどう解釈したか」「なぜその実装を選んだか」「なぜ plan から逸脱したか」を後から追えないと監査性が落ちる。
  - `report.md` は Red / Green / Refactor / verification evidence を記録する土台を持つが、仕様解釈、実装判断、tradeoff、open question、promotion を扱う canonical section がまだない。
  - worker が実装中に得た一次情報をどう `report.md` に反映するか、main orchestrator がどこまで統合責任を持つか、reviewer が何を blocker とするかが未定義である。
  - 実装中判断が `report.md` だけに残り、将来の実装者が守るべき設計判断が `design.md` / ADR / follow-up に昇格されないリスクがある。
- 再現手順:
  1. `iss-00102` の `plan.md` / `report.md` と、今回移管した discussion を読む。
  2. agent が plan の抽象的な guardrails の範囲で実装判断を行った場合、その判断をどこへ、誰が、どの形式で記録するかを確認する。
  3. worker / orchestrator / reviewer の責任分界と completion gate を確認する。
- 観測点:
  - shipped report template: `src/spec_dock/assets/spec_dock/templates/issue/report.md`
  - workflow docs: `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - plan/report authoring docs: `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - installed agent assets: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`, `.codex/prompts/execute-issue.md`, `.codex/agents/*.toml`
  - dogfooding workspace: `spec-dock/` 側の mirror と active issue docs
  - structural tests: scaffold / installed asset の content assertions
- 情報源:
  - `iss-00102` は plan contract 側の前提として扱う。
  - `discussions/20260520t142357z-disc-report-decision-ledger-policy.md`
  - `discussions/20260520t143000z-disc-report-decision-ledger-residual-issues-analysis.md`
  - `discussions/20260520t144200z-disc-report-decision-ledger-requirement-delta.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - Issue を実行する main orchestrator。
  - 実装・文書更新を担当する dev-coder / doc-writer / utility-worker。
  - code-reviewer / qa-reviewer / spec-reviewer。
  - spec-dock を導入した consumer repo の利用者。
- 代表シナリオ:
  - dev-coder が実装中に plan の曖昧さや既存実装制約を発見し、structured `Ledger Note` として orchestrator に返す。
  - main orchestrator が worker note を検証し、`report.md` の `Spec Interpretation / Decision Ledger` に統合する。
  - reviewer が diff / plan / report / tests を照合し、重要判断が追跡可能か、open decision が残っていないか、report-only にしてはいけない判断が昇格されているかを確認する。
  - 小規模 issue では material な判断がなかったことを明示し、過剰な記録負担を避ける。

## スコープ
- 必須:
  - `report.md` template に `Spec Interpretation / Decision Ledger` の canonical section を定義する。
  - decision ledger は作業ログではなく、material な仕様解釈・判断・逸脱・tradeoff・open question・promotion / follow-up の台帳として定義する。
  - 小規模 issue でも section は省略せず、material な判断がない場合は `No material interpretation changes.` / `No decision entries.` を明示できるようにする。
  - worker が返す structured `Ledger Note` の最小 schema を定義する。
  - main orchestrator が worker note を canonical `report.md` に統合する責任を定義する。
  - reviewer が decision traceability、promotion 漏れ、open decision、report-only design decision を監査できるようにする。
  - `report.md` に残る durable decision を `design.md` / ADR / plan amendment / follow-up issue へ昇格する基準を定義する。
  - provider-side source と dogfooding mirror の影響を確認する。
  - scaffold / installed asset の重要文言や構造が維持されるよう、必要な structural tests を追加・更新する。
- 禁止:
  - `report.md` を shell command transcript や逐次作業ログにしない。
  - agent の private reasoning / chain-of-thought を保存しない。
  - worker が authoritative decision status を勝手に close / promote / reject しない。
  - 将来も効く設計判断を `report.md` だけに閉じ込めない。
  - legacy issue report に ledger がないことを遡及的 blocker にしない。
- 対象外:
  - `iss-00102` の plan contract 再実装。
  - runtime `validate --strict-report-ledger` の本格実装。
  - 既存 Issue docs 全件の migration / backfill。
  - GitHub issue / PR workflow 全体の再設計。
  - agent runtime や model selection policy の変更。

## 境界
- 常に行う:
  - provider-side source を正として変更し、必要に応じて dogfooding mirror の整合を確認する。
  - `plan.md` は実装前の contract、`report.md` は observed evidence + decision ledger として責務境界を保つ。
  - worker は firsthand rationale を structured note として提出し、orchestrator が canonical report ledger を統合する。
  - reviewer は read-only で、ledger の存在ではなく decision traceability と promotion completeness を監査する。
- 判断が必要:
  - `Spec Interpretation / Decision Ledger` を単一 section として実装するか、`Spec Interpretation` と `Decision Ledger` を分けるか。
  - `Proposed Report Entries` を report template に常設するか、worker output schema に留めるか。
  - `Retrospective` を template 常設にするか、必要時 section にするか。
- 行わない:
  - `implementation-notes.md` を標準 issue artifact として新設しない。
  - `plan.md` を実装中の判断メモ置き場にしない。
  - 低リスク issue に長大な decision entry を義務化しない。

## 非交渉制約
- `iss-00102` は plan contract 側の前提として維持し、この issue では report ledger contract に集中する。
- `src/spec_dock/assets/spec_dock/...` は shipped scaffold docs/templates/system の provider-side source of truth として扱う。
- `src/spec_dock/assets/install_root/...` は installed agent-tooling assets の provider-side source of truth として扱う。
- `spec-dock/` は dogfooding workspace であり、必要な確認対象ではあるが primary implementation source ではない。
- 新規・変更する path は repository instruction に従い lowercase を基本にする。
- `report.md` は将来の唯一正本ではなく audit trail である。durable decision は適切な canonical artifact へ昇格する。

## 前提
- 高度な coding agent は `plan.md` の guardrails の範囲内で実装詳細を自律的に具体化できる。
- 自律性を許すほど、後から「なぜそうしたか」を復元できる記録が必要である。
- 完全な実装中 transcript は不要であり、必要なのは判断の再検証に足る最小十分な rationale、evidence、disposition である。
- `report.md` の ledger は、worker の raw note をそのまま貼る場所ではなく、orchestrator が統合した canonical issue-level record である。

## 受け入れ条件
- AC-001:
  - アクター: main orchestrator / delegated worker
  - 前提: Issue 実装中に仕様解釈、実装判断、plan 逸脱、tradeoff、test strategy 変更、reviewer finding 対応、follow-up 化が発生する。
  - 操作: worker は structured `Ledger Note` を返し、orchestrator は `report.md` の `Spec Interpretation / Decision Ledger` に必要な entry を統合する。
  - 期待結果: 実装後に、どの判断がなぜ行われ、どの evidence に基づき、どこへ着地したかを `report.md` から追跡できる。
  - 観測点: `templates/issue/report.md`、`workflow_issue.md`、`spec-dock-issue-execution/SKILL.md`、agent configs、structural tests。
- AC-002:
  - アクター: main orchestrator / reviewer
  - 前提: 小規模 issue で material な仕様解釈や判断が発生していない。
  - 操作: `report.md` の decision ledger section を確認する。
  - 期待結果: section は省略されず、`No material interpretation changes.` と `No decision entries.` により、判断がなかったことが明示されている。
  - 観測点: `templates/issue/report.md`、reviewer instruction、structural tests。
- AC-003:
  - アクター: main orchestrator / spec-reviewer / qa-reviewer / code-reviewer
  - 前提: `report.md` に decision ledger entry が存在する。
  - 操作: issue completion 前に ledger entry の status / disposition / evidence / follow-up を確認する。
  - 期待結果: `open` entry は残らず、将来も効く判断は `design.md` / ADR / plan amendment / follow-up issue へ昇格または変換され、issue-local な判断は理由付きで閉じられている。
  - 観測点: `templates/issue/report.md`、reviewer instruction、completion checklist。
- AC-004:
  - アクター: dev-coder / doc-writer / main orchestrator
  - 前提: 複数 agent に実装または文書更新を委任する。
  - 操作: worker が material decision を発見し、作業完了時に `Ledger Note` を返す。
  - 期待結果: worker は提案・観測事実・根拠・リスクを返し、orchestrator が canonical `report.md` に採用 / 却下 / 保留 / 昇格を統合する。worker の提案が、未統合のまま accepted decision として扱われない。
  - 観測点: `spec-dock-issue-execution/SKILL.md`、worker agent instruction、report template。
- AC-005:
  - アクター: spec-reviewer / qa-reviewer / code-reviewer
  - 前提: issue final review または step review を行う。
  - 操作: diff、plan obligations、report evidence、decision ledger を照合する。
  - 期待結果: reviewer は、重要判断が ledger なしで実装されていないか、accepted design decision が report-only になっていないか、open question が未解決のまま finish されていないかを指摘できる。
  - 観測点: reviewer agent config、workflow docs、report template。

## 例外・エッジケース
- EC-001:
  - 条件: typo / formatting / mechanical sync など、material decision がない小規模 issue。
  - 期待: ledger section は残し、`No material interpretation changes.` / `No decision entries.` で軽量に閉じられる。
  - 観測点: report template、reviewer instruction。
- EC-002:
  - 条件: worker が implementation detail を一時的に決めて先へ進む必要がある。
  - 期待: worker は provisional な `Ledger Note` を返し、orchestrator が採用 / 修正 / 差し戻し / 昇格を判断する。
  - 観測点: worker output schema、report ledger。
- EC-003:
  - 条件: reviewer finding が false positive、scope 外、または follow-up 対象である。
  - 期待: 必要に応じて decision ledger に理由と disposition を記録し、単に comment thread 側だけで閉じない。
  - 観測点: reviewer gate、report ledger。
- EC-004:
  - 条件: legacy issue report に decision ledger がない。
  - 期待: 遡及 blocker にはしない。必要な場合だけ source と confidence を明示して backfill する。
  - 観測点: workflow docs、reviewer instruction。

## 入力→出力例
- EX-001:
  - 入力: worker が「plan では artifact 境界が曖昧だったため、`implementation-notes.md` ではなく `report.md` に decision ledger を置く案を選んだ」と報告する。
  - 出力: orchestrator が `report.md` に、trigger、options considered、decision、rationale、evidence、disposition を持つ `D-001` entry として統合する。
- EX-002:
  - 入力: 小規模 docs typo 修正で material decision がない。
  - 出力: `Spec Interpretation / Decision Ledger` に `No material interpretation changes.` / `No decision entries.` を記録する。

## 用語（ドメイン語彙）
- TERM-001:
  - Spec Interpretation / Decision Ledger:
    - `report.md` に置かれる、実装中・文書更新中の material な仕様解釈、判断、逸脱、tradeoff、open question、promotion / follow-up を追跡する台帳。
- TERM-002:
  - Ledger Note:
    - worker が orchestrator に返す structured note。authoritative decision ではなく、orchestrator が `report.md` に統合するための一次情報。
- TERM-003:
  - Disposition:
    - decision ledger entry がどこへ着地したかを表す分類。例: `applied`, `rejected`, `promoted_to_design`, `promoted_to_adr`, `promoted_to_plan`, `converted_to_followup`, `deferred`, `no_action`, `superseded`。
- TERM-004:
  - Promotion:
    - `report.md` に記録された判断を、将来の実装者が守るべき正本へ昇格すること。昇格先は `design.md`、ADR、plan amendment、follow-up issue など。

## 未確定事項
- Q-001:
  - 質問: `Spec Interpretation / Decision Ledger` を単一 section とするか、`Spec Interpretation` と `Decision Ledger` を分けるか。
  - 推奨案: 単一 section。
  - 影響範囲: report template、reviewer instruction、structural tests。
- Q-002:
  - 質問: `Proposed Report Entries` を template 常設にするか。
  - 推奨案: 常設せず、worker output schema に留める。
  - 影響範囲: report template の軽さ、worker handoff。
- Q-003:
  - 質問: `Retrospective` を template 常設にするか。
  - 推奨案: 任意 section。
  - 影響範囲: small issue の負担、audit fidelity。
