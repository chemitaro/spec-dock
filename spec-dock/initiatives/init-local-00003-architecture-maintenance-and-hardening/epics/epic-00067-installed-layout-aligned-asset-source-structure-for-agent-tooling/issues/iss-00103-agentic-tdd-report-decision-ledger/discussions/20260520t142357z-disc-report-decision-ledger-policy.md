# SpecDock report.md Decision Ledger 運用方針ドラフト

作成日: 2026-05-20

## 目的

Agentic TDD では、`plan.md` がすべての実装詳細を事前に固定するのではなく、実装 agent が `plan.md` の guardrails の範囲内で具体化しながら進める。

この自律性を許す以上、後から次を検証できる必要がある。

- なぜその実装判断をしたのか
- spec / plan の曖昧さをどう解釈したのか
- どの tradeoff を受け入れたのか
- plan から逸脱した場合、なぜ許容したのか
- 未解決事項や follow-up は何か
- その判断は report-only でよいのか、design / ADR / plan amendment へ昇格すべきか

このため、X の投稿にある `implementation-notes` 的な運用を SpecDock に取り込む。ただし、issue ごとに新しい `implementation-notes.md` を増やすのではなく、既存の `report.md` を拡張する。

## 基本方針

`plan.md` は実装前の契約である。

- scope
- guardrails
- acceptance criteria
- implementation order
- validation obligations
- escalation / amendment trigger

`report.md` は実行中・実行後の監査台帳である。

- 実際の Red / Green / Refactor evidence
- verification result
- discovered tests
- closure delta
- reviewer gate status
- commit / no-op evidence
- agent の自律判断、仕様解釈、逸脱、tradeoff、open question

`design.md` / ADR は将来も守るべき設計判断の正本である。

`report.md` は audit trail であり、永続的な仕様・設計の唯一正本にしてはならない。将来の実装者が守るべき判断は `design.md`、`plan.md` amendment、ADR、または follow-up issue へ昇格する。

## 推奨する report.md 追加セクション

名称は `Spec Interpretation / Decision Ledger` を推奨する。

`Implementation Notes` は広すぎて作業ログ化しやすい。`Spec Interpretation / Decision Ledger` は、記録対象が「仕様解釈と判断」であることを明確にする。

```markdown
## Spec Interpretation / Decision Ledger

Record only material decisions where implementation interpreted an ambiguity,
chose between viable options, changed the planned route, constrained scope,
accepted a trade-off, or found an unresolved question.

| ID | Status | Type | Trigger / Gap | Decision / Interpretation | Rationale | Impact | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|
| D-001 | applied | interpretation | ... | ... | ... | ... | ... | none |
```

## Status 値

| Status | 意味 | 完了判定への影響 |
|---|---|---|
| `applied` | 実装で採用済み。成果物に反映されている | 通常は完了可能 |
| `open` | 未解決の問い、判断保留、reviewer / user 判断待ち | blocking か follow-up かを明記する |
| `superseded` | 別判断で置き換えられた | 置換先 ID を書けば完了可能 |
| `reverted` | 一度採用したが取り消した | 理由と evidence があれば完了可能 |
| `deferred` | 今回は扱わず後続 issue / spec へ送る | scope 外である根拠と follow-up が必要 |
| `amended` | plan / design / requirement / ADR に反映済み | 反映先と re-review evidence が必要 |
| `escalated` | user / reviewer / ADR 判断へ上げた | 判断結果または blocker 状態が必要 |

`accepted` は避ける。reviewer / maintainer が承認したように見えるため、agent が自己判断で使う status としては強すぎる。

## Type 値

| Type | 記録対象 |
|---|---|
| `interpretation` | spec / plan の曖昧さを具体実装へ落とした |
| `decision` | 複数の妥当案から選んだ |
| `deviation` | plan / spec から意味のある逸脱をした |
| `constraint` | 既存 architecture、互換性、API、環境制約による判断 |
| `test-strategy` | Red / covered-existing / inspect-only / manual-required などの検証方針判断 |
| `refactor` | refactor 境界や責務配置を判断した |
| `question` | 未解決確認事項 |
| `follow-up` | 今回範囲外へ送る作業 |

## 記録必須の trigger

次に該当する場合は `Spec Interpretation / Decision Ledger` に記録する。

- plan / spec に明記されていない挙動を agent が決めた
- plan の implementation order、scope、allowed files、validation path が意味を持って変わった
- `red-required` を `covered-existing` / `inspect-only` / `manual-required` に変えた
- 2つ以上の妥当な実装案から選んだ
- reviewer が見れば「なぜこうした？」と聞きそうな判断をした
- 互換性、migration、runtime contract、scaffold contract、workflow/template/skill contract に影響しうる判断をした
- reviewer fail への対応方針を選んだ
- scope 外の問題を発見し、今回は扱わない判断をした
- 未解決の質問を持ったまま先へ進んだ
- risk acceptance、waiver、approved-no-op、rollback 不能な変更に関わる判断をした

## 記録しないもの

次は記録しない。

- formatting / import 整理
- typo 修正
- plan に完全に従った routine step
- diff を読めば分かるだけの変更説明
- テスト実行の逐次ログ
- 試行錯誤の全文
- agent の private reasoning / chain-of-thought
- 自明な既存 pattern 追従

## 著者責任モデル

`report.md` の authoritative ledger は main orchestrator が所有する。

ただし、一次情報は実装・文書作業を行った worker が structured note として提出する。

基本原則:

> Workers record firsthand rationale.  
> Orchestrator owns the canonical report.  
> Reviewers audit the ledger.

### main orchestrator の責任

- `report.md` の最終統合責任者になる
- worker の structured notes を検証し、採用 / 却下 / 保留 / 昇格を判断する
- overlapping notes を統合する
- status、scope、evidence、follow-up を正本として整える
- issue completion 前に ledger が閉じていることを確認する

### dev-coder の責任

- 実装中に発見した仕様解釈、実装判断、tradeoff、逸脱候補、テスト方針を structured note として提出する
- `report.md` の authoritative ledger を直接編集しないのが原則
- temporary / provisional に進めた判断は、その理由と rollback / revisit 条件を明記する

### doc-writer の責任

- docs / templates / workflow text の意味変更、文言判断、未解決の前提を structured note として提出する
- 不確実性を丸めず、orchestrator 判断が必要かを明記する

### reviewer の責任

- read-only
- ledger と diff / tests / spec の整合を監査する
- 「この判断は report にない」「rationale が不足」「report-only にしてはいけない設計判断」と指摘する

## Worker Structured Note

dev-coder / doc-writer は、作業完了時に次の形で一次情報を返す。

```markdown
### Ledger Note

- source-agent: dev-coder | doc-writer
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

判断がない場合も明示する。

```markdown
### Ledger Note

- No material implementation decisions beyond the approved plan.
```

## Orchestrator 統合ルール

orchestrator は worker note をそのまま貼らず、以下を確認して `report.md` に統合する。

1. note を `applied` / `rejected` / `deferred` / `open` / `amended` / `escalated` に分類する
2. source docs、diff、tests、reviewer output と照合する
3. 重複 note を統合する
4. provenance を残す
   - proposed by
   - accepted / integrated by
   - reviewed by
5. provisional decision には rollback / revisit 条件を付ける
6. 将来も効く判断は `design.md` / ADR / follow-up issue へ昇格する
7. raw worker note は unresolved の場合を除き、そのまま残さない

## Orchestrator 統合 entry 例

```markdown
### D-001: Keep report.md as canonical decision ledger

- status: applied
- type: decision
- proposed by: consultant / doc-writer
- integrated by: main orchestrator
- reviewed by: spec-reviewer
- trigger: implementation-notes pattern would otherwise add another issue artifact.
- decision: Expand `report.md` with `Spec Interpretation / Decision Ledger` instead of adding `implementation-notes.md`.
- alternatives considered:
  - Add per-issue `implementation-notes.md`
  - Backfill decisions into `plan.md`
  - Rely on PR body
- rationale: `report.md` is already the issue-local observed evidence ledger, while `plan.md` must remain the pre-implementation contract.
- impact: report template and reviewer checklist must change.
- evidence: updated workflow docs, report template, and structural tests.
- follow-up: none
```

## 昇格ルール

`report.md` に留めてよいもの:

- issue-local な実装判断
- 軽微な順序変更
- reviewer に見せたい補足
- scope 外 follow-up 候補

`plan.md` amendment が必要なもの:

- closure 条件が変わる
- verification path を弱める
- scope / allowed files / step 順が意味を持って変わる
- required closure row、locked expectation、required flag、spec link の意味が変わる

`design.md` 更新が必要なもの:

- 責務境界が変わる
- データモデル、runtime contract、scaffold contract が変わる
- 今後の実装者が守るべき構造判断

ADR が必要なもの:

- 複数 issue / epic / initiative に波及する
- 後戻りコストが高い
- workflow 標準や reviewer policy を変える
- 将来の運用負担や migration risk を伴う

## Reviewer Gate 追加観点

### spec-reviewer

- decision ledger が requirement / design / plan と矛盾していない
- `deviation` が必要な plan amendment を通している
- 将来効く判断が `report.md` に閉じ込められていない
- `open` な decision が blocking のまま complete になっていない
- report が transcript dump になっていない

### code-reviewer

- ledger の判断と実 diff が一致している
- unrecorded material decision が diff から見えない
- rejected alternatives が後付け正当化ではなく、既存構造や実装リスクに基づいている
- allowed scope / forbidden scope から逸脱していない

### qa-reviewer

- test strategy の判断が closure id と対応している
- `red-required` から `covered-existing` / `inspect-only` / `manual-required` に変えた場合、検出力の根拠がある
- integration test 不要判断に risk-based rationale がある
- manual-required の場合、stateful scenario / failure-recovery evidence が必要な範囲で残っている

## 完了条件への追加

Issue を complete と報告してよいのは、既存の completion 条件に加えて次を満たす場合だけにする。

- material autonomous decision がすべて ledger に記録されている
- ledger の各 row が `applied` / `amended` / `escalated` / `reverted` / `deferred` / `superseded` のいずれかで閉じている
- `open` row が残る場合は blocking でない根拠、owner、follow-up が明記されている
- `deviation` row は妥当化され、必要なら plan amendment / re-review を通している
- 将来効く判断が report-only になっていない
- reviewer が ledger を監査している

## Anti-patterns

避けるべきもの:

- `plan.md` を実行中に上書きして当初計画と実績差分を消す
- `report.md` を shell transcript にする
- worker の提案をそのまま承認済み decision として貼る
- report-only に将来の workflow / architecture contract を残す
- 小さい issue に長大な decision template を義務化する
- `implementation-notes.md` など別ファイルへ重要判断を逃がす
- 「詳細はコード参照」で rationale を省略する
- 「たぶん問題ない」で open question を閉じる

## 良い entry / 悪い entry

良い:

```markdown
| D-002 | applied | deviation | plan expected command-layer change, but root cause was presentation rendering | Implemented fix in presentation renderer instead of command handler | Command handler already passed correct domain state; changing it would duplicate logic | Lower blast radius; added presentation regression test | `tests/presentation_runtime/...` | none |
```

悪い:

```markdown
- Refactored validation.
```

理由、影響、evidence、代替案がなく、後から監査できない。

## 残課題 / 追加で詰めるべき論点

1. セクション名の最終決定
   - `Spec Interpretation / Decision Ledger`
   - `Agent Autonomy Decision Trace`
   - `Execution Ledger`
   - 現時点の推奨は `Spec Interpretation / Decision Ledger`。

2. table 形式か bullet 形式か
   - table は構造検証しやすいが横長になりやすい。
   - bullet は読みやすいが機械検証が難しい。
   - 推奨は summary table + 必要時のみ detail bullet。

3. worker が `report.md` を直接編集してよい例外条件
   - 原則禁止。
   - orchestrator が明示委任した場合のみ許可。
   - それでも owner は orchestrator。

4. `open` decision の completion 条件
   - blocking / non-blocking / follow-up の分類をどこまで必須にするか。
   - 最低限、owner と next action は必須にするべき。

5. reviewer failure severity
   - ledger 欠落を常に P1 にするか、重要度で P2 にするか。
   - 推奨: material decision 欠落、durable decision の report-only は P1。

6. 小規模 issue の負担軽減
   - `No material autonomous decisions beyond the approved plan.` を許す。
   - ただし reviewer が diff から material decision を見つけたら fail できるようにする。

7. 既存テンプレートとの統合位置
   - `Delegated Worker Evidence` の後、`Reviewer Gate Status` の前が自然。
   - 実装サマリー直後に summary を置く案もある。

8. structural tests の粒度
   - heading と status/type vocabulary だけ固定するか、table columns まで固定するか。
   - 初期は heading + key vocabulary + completion rules を固定し、過剰 lint は避ける。

9. skills / prompts への反映範囲
   - `spec-dock-issue-execution` skill
   - dev-coder / doc-writer / reviewer agent prompts
   - `.codex/prompts/execute-issue.md`
   - report template / workflow docs / authoring docs / tests

10. 既存 report との互換性
   - 過去 issue へ backfill するか。
   - 推奨: backfill しない。新規 issue から適用。

11. completion state の分離
   - `report.md` が埋まったことと issue 完了を混同しない。
   - `implementation_done`、`verification_done`、`review_done`、`followups_triaged`、`report_finalized` を分けて扱う余地がある。
   - 推奨: 初期実装では final gate に `Completion Decision` を追加するか、既存 `Final Quality Gate` の中でこれらを明示する。

12. reviewer finding closure の扱い
   - reviewer 指摘が ledger に載っていても、対応済みか、risk accepted か、deferred かが曖昧になる可能性がある。
   - 推奨: reviewer finding 由来の ledger row には `open / addressed / accepted_risk / deferred / rejected` 相当の解決状態を持たせる。

13. audit fidelity と retrospective 記録
   - 後からきれいに要約しすぎると、判断を変えた失敗や重要な rollback 根拠が消える。
   - 一方で逐語ログを貼ると ledger が読まれなくなる。
   - 推奨: 逐語ログは禁止しつつ、判断を変えた失敗、rollback に必要な失敗、reviewer finding による方針変更は ledger に残す。

14. direct edit 例外の明文化
   - worker が `report.md` を直接編集する例外を許す場合、`author_role` / `source` / `integrated_by` を entry に残す必要がある。
   - 推奨: 原則は orchestrator single-writer。例外は明示委任された小規模 issue に限定する。

## 実装に向けた提案

次の issue では、まずこの方針を要件化する。

- requirement:
  - `report.md` が decision ledger を持つ
  - orchestrator-owned / worker-note-supplied モデルを定義する
  - reviewer gate が ledger を監査する

- design:
  - artifact responsibility
  - ledger schema
  - worker note schema
  - promotion rules
  - reviewer checks

- plan:
  - workflow docs 更新
  - report template 更新
  - issue execution skill / prompts 更新
  - tests 更新
  - dogfooding mirror 更新
  - final review
