# report.md Decision Ledger 要求差分メモ

作成日: 2026-05-20

## 位置づけ

このメモは、`report.md` を Agentic TDD の実行監査台帳として拡張するために、既存の `iss-00102` 要件へ追加すべき要求差分を整理する。

実装計画ではない。

先行 discussion:

- `20260520t142357z-disc-report-decision-ledger-policy.md`
- `20260520t143000z-disc-report-decision-ledger-residual-issues-analysis.md`

## 背景

`iss-00102` では、`plan.md` を executable Agentic TDD workflow contract として整理した。

その結果、`plan.md` は細かい実装詳細をすべて事前固定するより、scope、guardrails、test obligation、evidence destination、amendment trigger を定義し、実装 agent に一定の自律性を渡す方向へ進んだ。

この方向性は妥当である。

ただし、agent の自律性を高めるほど、後から次を追跡できなければならない。

- 仕様や plan の曖昧さをどう解釈したか
- 複数の実装案から何を選んだか
- plan から意味のある逸脱をしたか
- test strategy をどう判断したか
- reviewer finding へどう対応したか
- 将来も効く判断を `design.md` / ADR / follow-up へ昇格したか

したがって、`report.md` は単なる完了後の報告書ではなく、observed evidence ledger に加えて decision / interpretation ledger を持つ必要がある。

## 追加すべき目的

既存の目的に、次を追加する。

- `report.md` を、Red / Green / Refactor / verification evidence だけでなく、実装中の仕様解釈、判断、逸脱、tradeoff、open question、follow-up、promotion を追跡する監査台帳として拡張する。
- `plan.md` に agent の自律性を許す guardrails を置き、`report.md` に自律判断の traceability を残すことで、agentic execution と後追いレビューを両立する。
- `report.md` に残った判断のうち、将来も守るべきものを `design.md` / ADR / plan amendment / follow-up issue へ昇格する route を明確にする。

## 追加すべきスコープ

必須スコープに、次を追加する。

- `templates/issue/report.md` に `Spec Interpretation / Decision Ledger` を追加する。
- `report.md` の decision ledger は、作業ログではなく、material な仕様解釈・判断・逸脱・tradeoff・open question の台帳として定義する。
- 小規模 issue でも section は省略せず、material な判断がない場合は `No material interpretation changes.` / `No decision entries.` を明示できるようにする。
- `workflow_issue.md` と `spec-dock-issue-execution/SKILL.md` に、orchestrator-owned report ledger と worker structured note の責任分界を追加する。
- dev-coder / doc-writer は、実装または文書更新中に material decision を発見した場合、authoritative `report.md` を直接閉じるのではなく、structured `Ledger Note` を返す。
- main orchestrator は、worker note を `report.md` の canonical ledger へ統合し、status、disposition、evidence、follow-up、promotion を確定する。
- reviewer は、decision が追跡可能か、report-only にしてはいけない判断が `design.md` / ADR / follow-up に昇格しているかを監査する。
- structural tests は、template / skill / reviewer instruction に decision ledger contract が存在することを検査する。

禁止スコープに、次を追加する。

- `report.md` を shell command transcript や逐次作業ログにしない。
- agent の private reasoning / chain-of-thought を保存しない。
- worker が `report.md` の authoritative decision status を勝手に閉じない。
- 将来も効く設計判断を `report.md` だけに閉じ込めない。
- legacy issue report に ledger がないことを遡及的 blocker にしない。

## 追加すべき受け入れ条件

### AC-008: report decision ledger

- アクター: main orchestrator / delegated worker
- 前提: Issue 実装中に仕様解釈、実装判断、plan 逸脱、tradeoff、test strategy 変更、reviewer finding 対応、follow-up 化が発生する。
- 操作: worker は structured `Ledger Note` を返し、orchestrator は `report.md` の `Spec Interpretation / Decision Ledger` に必要な entry を統合する。
- 期待結果: 実装後に、どの判断がなぜ行われ、どの evidence に基づき、どこへ着地したかを `report.md` から追跡できる。
- 観測点: `templates/issue/report.md`、`workflow_issue.md`、`spec-dock-issue-execution/SKILL.md`、agent configs、structural tests。

### AC-009: lightweight no-decision mode

- アクター: main orchestrator / reviewer
- 前提: 小規模 issue で material な仕様解釈や判断が発生していない。
- 操作: `report.md` の decision ledger section を確認する。
- 期待結果: section は省略されず、`No material interpretation changes.` と `No decision entries.` により、判断がなかったことが明示されている。
- 観測点: `templates/issue/report.md`、reviewer instruction、structural tests。

### AC-010: promotion and completion gate

- アクター: main orchestrator / spec-reviewer / qa-reviewer / code-reviewer
- 前提: `report.md` に decision ledger entry が存在する。
- 操作: issue completion 前に ledger entry の status / disposition / evidence / follow-up を確認する。
- 期待結果: `open` entry は残らず、将来も効く判断は `design.md` / ADR / plan amendment / follow-up issue へ昇格または変換され、issue-local な判断は `no_action` または `applied` として理由付きで閉じられている。
- 観測点: `templates/issue/report.md`、reviewer instruction、completion checklist。

### AC-011: worker/orchestrator authorship boundary

- アクター: dev-coder / doc-writer / main orchestrator
- 前提: 複数 agent に実装または文書更新を委任する。
- 操作: worker が material decision を発見し、作業完了時に `Ledger Note` を返す。
- 期待結果: worker は提案・観測事実・根拠・リスクを返し、orchestrator が canonical `report.md` に採用 / 却下 / 保留 / 昇格を統合する。worker の提案が、未統合のまま accepted decision として扱われない。
- 観測点: `spec-dock-issue-execution/SKILL.md`、worker agent instruction、report template。

### AC-012: reviewer ledger audit

- アクター: spec-reviewer / qa-reviewer / code-reviewer
- 前提: issue final review または step review を行う。
- 操作: diff、plan obligations、report evidence、decision ledger を照合する。
- 期待結果: reviewer は、重要判断が ledger なしで実装されていないか、accepted design decision が report-only になっていないか、open question が未解決のまま finish されていないかを指摘できる。
- 観測点: reviewer agent config、workflow docs、report template。

## 追加すべき用語

### TERM-011: Spec Interpretation / Decision Ledger

`report.md` に置かれる、実装中・文書更新中の material な仕様解釈、判断、逸脱、tradeoff、open question、promotion / follow-up を追跡する台帳。

進捗ログや shell transcript ではない。

### TERM-012: Ledger Note

worker が orchestrator に返す structured note。

authoritative decision ではなく、orchestrator が `report.md` に統合するための一次情報である。

### TERM-013: Disposition

decision ledger entry がどこへ着地したかを表す分類。

例:

- `applied`
- `rejected`
- `promoted_to_design`
- `promoted_to_adr`
- `promoted_to_plan`
- `converted_to_followup`
- `deferred`
- `no_action`
- `superseded`

### TERM-014: Promotion

`report.md` に記録された判断を、将来の実装者が守るべき正本へ昇格すること。

昇格先は `design.md`、ADR、plan amendment、follow-up issue などである。

## 追加すべきテンプレート契約

`report.md` の最小構造は次を推奨する。

```markdown
## Spec Interpretation / Decision Ledger

No material interpretation changes.

No decision entries.

<!-- Or, when decisions exist: -->

| ID | Status | Type | Raised By | Trigger / Gap | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | interpretation | orchestrator | ... | ... | ... | applied | ... | none |

### Decision Details

#### D-001: short title

- options considered:
- risk if wrong:
- rollback / revisit:
```

推奨 status:

- `open`
- `resolved`
- `superseded`

推奨 disposition:

- `applied`
- `rejected`
- `promoted_to_design`
- `promoted_to_adr`
- `promoted_to_plan`
- `converted_to_followup`
- `deferred`
- `no_action`
- `superseded`

推奨 type:

- `interpretation`
- `scope`
- `implementation`
- `compatibility`
- `test-strategy`
- `operation`
- `deviation`
- `follow-up`

## 追加すべき worker note schema

```markdown
### Ledger Note

- source-agent: dev-coder | doc-writer | utility-worker
- topic:
- trigger:
- ambiguity / constraint:
- observed facts:
- options considered:
- proposed decision:
- rationale:
- affected files:
- affected tests:
- risk if wrong:
- rollback or revisit:
- confidence: high | medium | low
- needs orchestrator decision: yes | no
```

判断がない場合:

```markdown
### Ledger Note

- No material implementation decisions beyond the approved plan.
```

## 追加すべき reviewer severity

| Severity | 意味 | Completion gate |
|---|---|---|
| `blocker` | 要件違反、安全性、データ破壊、重大な契約違反、decision traceability 欠落 | 完了不可 |
| `major` | acceptance / design contract に影響する実質問題 | 原則完了不可。follow-up / promotion には明示判断必須 |
| `minor` | 局所改善、保守性、軽微な仕様曖昧さ | ledger に記録して disposition があれば完了可 |
| `nit` | 表記、整形、任意改善 | 非ブロック。通常 ledger 不要 |

## 追加すべき structural test

最低限、次を検査する。

- `templates/issue/report.md` に `Spec Interpretation / Decision Ledger` が存在する。
- 軽量 phrase `No material interpretation changes.` / `No decision entries.` が存在する。
- ledger table の必須列が template に存在する。
- allowed status / disposition / type が docs または template に明示されている。
- `spec-dock-issue-execution/SKILL.md` に `Ledger Note` schema または同等の worker note obligation が存在する。
- reviewer agent config に、missing traceability、report-only design decision、open question completion、promotion漏れの監査観点が存在する。

## 残る設計判断

実装前に設計書へ反映する際、次を決める。

1. `Spec Interpretation / Decision Ledger` を単一 section として実装する。
   - 推奨: 単一 section。
   - 理由: section 増加を抑えつつ、仕様解釈と判断のつながりを保てる。
2. `Proposed Report Entries` を template 常設にするか。
   - 推奨: 常設しない。
   - 理由: worker output schema として持てば十分。report template を重くしない。
3. `Retrospective` を template 常設にするか。
   - 推奨: 任意 section。
   - 理由: acceptance evidence と混ぜない説明は必要だが、小規模 issue で常設すると負担が増える。
4. completion validation を runtime `validate` に入れるか。
   - 推奨: 今回は structural tests / reviewer instruction まで。runtime strict validation は対象外。

## まとめ

`iss-00102` の既存要件は、`plan.md` を executable Agentic TDD workflow contract にする点ではおおむね十分である。

今回追加すべきなのは、agentic execution によって生じる実装中判断を、`report.md` で追跡可能にする要求である。

最終方針は次である。

- `plan.md`: 実行前の契約
- `report.md`: observed evidence + decision ledger
- worker: firsthand rationale を `Ledger Note` として提出
- orchestrator: canonical report ledger を統合
- reviewer: traceability / promotion / unresolved decisions を監査
- durable decision: `design.md` / ADR / plan amendment / follow-up へ昇格
