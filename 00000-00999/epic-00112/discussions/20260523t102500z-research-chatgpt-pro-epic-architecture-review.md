---
type: review
source: chatgpt-pro
created_at: 2026-05-23T10:25:00+09:00
epic: epic-00112
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1100e7-f8a0-83a8-8187-4c2d5248ad14
verdict: conditional_pass
---

# ChatGPT Pro Review: Epic Architecture and Agentic Workflow

## verdict: conditional_pass

**結論:** Epic の方向性と 6 issue decomposition は、初期リサーチレポートの意図を概ね正しく実現しています。特に「design / plan は専門 role が draft するが、canonical artifact、統合、phase promotion、report evidence は main orchestrator が所有する」という中核不変条件は、Epic requirement/design/plan に十分反映されています。初期レポート自体も、設計書は `system-architect`、実装計画書は `implementation-planner` が一次作成し、最終責任は main orchestrator が持つべきだと整理しています。

ただし、**実装開始前に P1 レベルで直すべき点が 2 つあります。** いずれもアーキテクチャ方針そのものの欠陥ではなく、実装時に contract が曖昧化するリスクです。修正後は、再設計ではなく軽量な spec-reviewer 再確認で実装に入ってよい判断です。

根拠は、添付 Markdown 全体と、その中の research / Epic / issue docs のみです。外部 Web 参照や通常記憶は使っていません。

## must_fix_before_implementation

### P1-1: spec-reviewer criteria を「実際の reviewer 実行面」に接続する必要がある

現在の Epic は、`spec-reviewer` が delegated draft を pass 代替として扱わず、canonical artifact と delegated evidence の統合安全性を review する、という方針を正しく定義しています。外部分析でも、reviewer は draft 自体ではなく「canonical artifact が delegated draft を安全に統合したか」を見るべきだと指摘されています。

しかし、Issue 004 の対象成果物は主に `phase_design.md` / `phase_plan.md` / `phase_plan_epic.md` / `phase_plan_issue.md` であり、**実際の `spec-reviewer` skill / reviewer entrypoint がその criteria を読むのか、または reviewer skill 側も更新するのかが明示されていません。** Issue 004 は reviewer criteria と phase gate を扱うとしていますが、対象 surface は phase docs に寄っています。

これは delegated author と reviewer の独立性に関わる中核リスクです。phase docs に criteria を書いただけで reviewer が必ず適用するなら問題ありませんが、その前提は提示資料だけでは確認不能です。

**修正案:**

- `issues/iss-00116-delegated-authoring-phase-gates/{requirement,design,plan}.md`
  - 対象成果物に以下のどちらかを追加する。
    - `spec-reviewer` skill / reviewer prompt / reviewer authority doc の具体 path
    - または「`spec-reviewer` は phase docs を authority として必ず読むため、reviewer skill 更新は不要」という明示的な根拠と evidence requirement
  - AC に次を追加する。
    - `spec-reviewer` が delegated draft provenance / stale / superseded / traceability / scope creep / phase gate bypass を fail または incomplete にできることを、reviewer 実行面で確認する。
  - S99 final gate に「delegated-specific reviewer criteria が実際の reviewer invocation に反映されていること」を追加する。

### P1-2: child issue の S01/S02 で provider source と dogfooding mirror の境界が混ざっている

Epic design は provider-first を明確に採用しており、shipped docs/skills/adapters は `src/spec_dock/assets/...` を source of truth とし、`spec-dock/` dogfooding workspace は validation surface とする方針です。

しかし複数の child issue plan では、S01 “Provider source update” の対象ファイルに dogfooding mirrors が含まれています。たとえば evidence schema issue は provider docs/templates/active-none に加えて dogfooding mirrors を S01 の対象に含めています。Role skill issue も provider skill と `.agents/skills mirrors` を同じ S01 target に含めています。

これは実装上、**provider-first の検証順序を曖昧にします。** S01 は provider source だけを閉じ、S02 で dogfooding mirror / parity / validate / sync を閉じるべきです。現在のままだと、consumer 側を同時編集しても “provider source update complete” に見えてしまい、drift 検出が弱くなります。

**修正案:**

- `issues/iss-00113`〜`issues/iss-00117` の `plan.md`
  - S01 allowed paths / target files は provider-side source of truth のみに限定する。
  - dogfooding mirror、`.agents/skills mirrors`、`.codex/agents mirrors`、`spec-dock/templates/**`、`spec-dock/system/active-none/**` は S02 に移す。
  - `tc-001` は provider contract の存在だけを検証する。
  - `tc-002` は provider/consumer parity、validate/sync、意図した差分の記録を検証する。
- Issue 006 は例外として、先行 provider outputs を消費して dogfooding evidence を残す issue なので、provider update no-op / prerequisite ledger を維持してよい。

## should_improve

### P2-1: Issue 006 dogfooding pilot に negative / blocked case を 1 件入れる

Issue 006 は design draft と plan draft、integration evidence、fresh reviewer、metrics、write-capable defer decision を要求しており、dogfooding evidence としてはかなり強いです。

ただし、failure modes の実効性を確認するには、成功系だけでは不十分です。自然発生しなければ tabletop でもよいので、以下のいずれか 1 件を pilot に入れると、workflow の安全性がかなり上がります。

- `Requirement Clarification Request`
- `Plan Blocked`
- stale draft reconciliation
- rejected / partially integrated draft
- host adapter unavailable fallback

### P2-2: `.codex/agents` adapter の fallback が Epic closure に与える影響を明記する

Issue 005 は `.codex/agents` の path / TOML schema が未確認なら、verified host integration と偽らず documented uncertainty / approved no-op として閉じる方針を持っています。これは安全側の良い設計です。

一方で、Issue 006 は “shipped workflow / skills / adapters” を使う pilot です。Issue 005 が adapter contract only で閉じた場合、Issue 006 は host-callable adapter を使った pilot ではなく、role skill / documented workflow を使った pilot になります。

**修正案:** Issue 006 に次を追加する。

```md
If Issue 005 closes as documented uncertainty rather than verified adapter implementation:
- The pilot may proceed using shipped role skills and documented invocation contracts.
- The pilot must not claim verified Codex host callability.
- E-RQ-010 host adapter boundary is closed as contract-only, not runtime-verified integration.
```

### P2-3: child issue AC が generic なので、Parent Epic Contract Details を AC 本体へ昇格する

各 child issue の AC はおおむね `AC-001 provider source update / AC-002 validate-sync / AC-003 final spec review` の汎用形です。Parent Epic Contract Details が後段に付いているため情報はありますが、実装者が AC だけを見た場合に、role-specific obligations を見落とす可能性があります。

特に Issue 003 は、RCR / Plan Blocked / forbidden actions / traceability maps を AC 本体に入れる方が安全です。Issue 004 も reviewer criteria を AC 本体へ昇格すべきです。

### P2-4: `source_snapshot` の最低フィールドを明示する

Epic design の Draft Artifact Contract には `source_snapshot` が入っていますが、最低限何を記録するかが少し曖昧です。runtime validation は defer でよいですが、Markdown schema として次を明記すると stale 判定が安定します。

```md
- source_snapshot:
  - source_revision: commit hash | doc timestamp | unknown
  - requirement_reviewer_pass_reference:
  - design_reviewer_pass_reference:
  - generated_at:
```

`unknown` を許す場合も、unknown のまま promotion evidence に使ってよい条件を明記した方がよいです。

### P3-1: Epic report の placeholder を整理する

`report.md` の `状態: "draft | approved"`、ADR placeholder、completed issue placeholder は、実装開始前に大きな問題ではありません。ただし report evidence を重視する Epic なので、着手時には placeholder を減らし、現在地と未実装範囲をより明確にした方がよいです。

## architecture_assessment

全体アーキテクチャは妥当です。初期リサーチの本質は、「専門サブエージェントを使うか」ではなく、「専門サブエージェントの出力を canonical authority にしないこと」です。現在の Epic はこの点を正しく捉えています。

境界設計も自然です。policy、evidence schema、role skills、phase gates、host adapters、dogfooding pilot という 6 分割は、contract boundary ごとに切られています。

最大のアーキテクチャリスクは、**docs contract が実際の agent execution contract に届かないこと**です。特に reviewer criteria と host adapter は、Markdown に書くだけでは実効性が保証されません。

## agentic_workflow_assessment

Delegation 設計は強いです。`system-architect` は design draft、`implementation-planner` は plan draft に限定され、requirement gap は RCR、design gap は Plan Blocked として返す設計になっています。

Reviewer independence も方針としては明確です。ただし reviewer criteria が実際の `spec-reviewer` execution surface に反映されることを明示する必要があります。

Evidence lifecycle はかなり良いです。`requested` / `produced` / `integrated` / `partially_integrated` / `rejected` / `superseded` / `blocked` / `stale` を明示し、stale / rejected / superseded / blocked draft を promotion evidence にしない設計は、古い draft が authority 化するリスクを抑えます。

Dogfooding pilot は、draft count、integration cost、rejected reasons、traceability defects、gate violations、forbidden action attempts、reviewer findings、stale events、provider/consumer drift まで見る設計になっています。

## issue_decomposition_assessment

- Issue 001: delegated authoring policy foundation: 妥当。
- Issue 002: delegated draft artifact and report evidence schema: 妥当。
- Issue 003: role skill assets: 妥当。ただし AC 本体に forbidden actions、RCR / Plan Blocked、traceability map を明示する余地あり。
- Issue 004: phase gate and spec-reviewer integration: 必要かつ正しいが、最も P1 リスクを持つ。phase docs update だけでなく reviewer execution contract update まで含めるべき。
- Issue 005: Codex host callable role adapter: 妥当。ただし documented uncertainty で閉じた場合に Epic closure / dogfooding pilot が何を claim できるかを明示すべき。
- Issue 006: dogfooding parity and validation pilot: 妥当。negative case と host adapter 未検証時の pilot claim 制限を追加するとよい。

## final_recommendation

**実装開始可。ただし P1-1 と P1-2 を先に直す条件付きです。**

この Epic は、初期リサーチの要求を十分に実現しています。draft-only delegation、main orchestrator ownership、independent spec-reviewer、draft lifecycle、report evidence、provider-first、host adapter thin boundary、dogfooding pilot という中核要素はすべて揃っています。

修正後の進め方は次が妥当です。

1. P1-1 / P1-2 の doc edit を反映する。
2. Epic plan と影響 child issue plan に fresh `spec-reviewer` を再実行する。
3. Issue 001 から順に実装へ進む。
4. Issue 004 では reviewer criteria が実際の reviewer 実行面に届くことを必ず確認する。
5. Issue 006 では成功系だけでなく、少なくとも 1 件の negative / blocked case evidence を残す。

再アーキテクチャは不要です。条件修正後は **conditional_pass -> pass 相当** と見てよいです。
