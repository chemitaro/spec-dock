---
type: research
source: deep-consultant
created_at: 2026-05-23T12:35:00+09:00
epic: epic-00112
topic: zero-base writer versus adviser analysis
status: current
---

# Deep Consultant Research: Zero-Base Writer Versus Adviser Analysis

## executive_conclusion

Deep Consultant の結論は、`system-architect` / `implementation-planner` は長期的には writer 能力を持つべきだが、pure writer ではなく staged / mode-based writer として設計すべき、というものだった。

つまり、単なる read-only adviser に留めるのは主たる authoring workflow として弱い。一方で、`design.md` / `plan.md` を無条件に直接編集する pure writer 方式も危険である。

推奨形は次。

- default mode: read-only adviser / reviewer
- authoring mode: 明示的に起動されたときだけ、限定された draft または proposed diff を生成
- promotion: main orchestrator が diff gate / validation / human-visible summary を通して canonical `design.md` / `plan.md` に昇格
- emergency / high-risk mode: adviser-only に戻す

要するに、subagent は専門 artifact の一次著者でよい。ただし canonical source of truth の最終所有者にはしない。

## original_intent_hypothesis

元の構想は次の分業だった可能性が高い。

- main orchestrator: ユーザー対話、要求整理、`requirement.md` の責任者
- system-architect: requirement に基づき `design.md` を作成
- implementation-planner: requirement / design に基づき `plan.md` を作成

この名前付けと役割は、単なる相談役よりも、特定成果物の author を示唆する。

ただし、spec-dock は canonical docs を source of truth とするため、複数 agent が直接編集すると、誰が正本を保証するのかが崩れやすい。特に architecture / plan は後続実装を長期間拘束するため、誤った canonical 化のコストが高い。

したがって、元の intent は writer だった可能性が高いが、現在の read-only は安全側の暫定設計として理解できる。最終形は pure read-only でも pure writer でもなく、authoring transaction を持つ staged writer である。

## adviser_vs_writer_comparison

| 観点 | Read-only adviser | Write-capable writer | Staged / mode-based writer |
| --- | --- | --- | --- |
| 品質 | 専門判断は得られるが、main orchestrator の転記品質に依存 | 専門 agent の文脈を直接 artifact に反映できる | 専門性を artifact 化しつつ、昇格時に検査できる |
| 速度 | 提案から編集まで二段階で遅い | 速い | ほぼ速い。gate 分だけ遅いが実用的 |
| 安全性 | 高い | 低いから中程度 | 中から高い |
| 認知負荷 | 高い。人間 / main が提案を再構成する | 低いが、誤編集の監視負荷が出る | 低い。人間は diff と論点だけ見ればよい |
| review independence | 保ちやすい | author と reviewer が混ざる | mode を分ければ保てる |
| source of truth | 安定 | 混乱しやすい | promotion point を単一化すれば安定 |
| harness 複雑度 | 低い | 中 | 高いが、投資価値がある |
| subagent 導入価値 | 中から低。consultant と重なる | 高い | 高い |

## cognitive_load_analysis

人間ユーザーの認知は有限なので、理想のインターフェースは長い提案文ではなく reviewable diff である。

read-only adviser 方式では、ユーザーまたは main orchestrator が次を担う。

- adviser の長文出力を読む
- 採用部分を選ぶ
- canonical docs の構造に変換する
- requirement / design / plan 間の traceability を確認する
- 書き漏れや矛盾を検出する

これは高コストである。特に architecture decision では、提案の価値が高いほど文脈も濃くなり、転記負荷が増える。

writer 方式では、ユーザーは artifact diff を見られる。これは認知的に優れている。

- 何が正本に入るかが明確
- 差分単位で accept / reject できる
- traceability と validation を機械的に確認しやすい
- 「読んでから再構成」ではなく「差分を審査」になる

ただし pure writer は危険である。したがって context engineering 上の最適解は、subagent に artifact-shaped output を作らせ、main orchestrator が promotion gate を管理すること。

## recommended_workflow

1. Requirement Ownership
   - main orchestrator がユーザー対話を通じて `requirement.md` を作成・更新する。
   - 要求の所有者はユーザーに最も近い agent であるべき。

2. Architecture Draft Transaction
   - `system-architect` を authoring mode で起動する。
   - 入力は active `requirement.md`、関連設計文書、architecture map、constraints / non-goals、known open questions に絞る。
   - 出力は canonical 直編集ではなく、proposed `design.md` または patch。

3. Design Gate
   - main orchestrator が requirement traceability、既存 architecture との整合、security / migration / rollback、unresolved decisions、許可範囲 diff を確認する。

4. Plan Draft Transaction
   - `implementation-planner` を authoring mode で起動する。
   - 入力は approved `requirement.md` と approved / proposed `design.md`。
   - 出力は proposed `plan.md`。

5. Plan Gate
   - main orchestrator が milestone、test / validation gate、rollback / migration / docs update、実装順序、人間判断が必要な irreversible step を確認する。

6. Canonical Promotion
   - main orchestrator が canonical docs に昇格する。
   - 可能なら promotion は spec-dock runtime command 化する。

7. Independent Review
   - 同じ subagent が自分の artifact を最終 review しない。
   - review mode は別 agent、または同 agent でも fresh context / read-only mode で行う。

## risk_controls

- `adviser`, `draft-writer`, `canonical-promoter`, `reviewer` を明示的に分ける。
- canonical `design.md` / `plan.md` へ最終反映できる責任者は main orchestrator に限定する。
- authoring mode の write 対象を proposed artifact または対象 doc に限定する。
- subagent は「何を変えたか」だけでなく「なぜ canonical に入れるべきか」を trace 付きで出す。
- design は requirement item に、plan は design decision に紐づく必要がある。
- author と reviewer を分ける。
- 既存 canonical docs がある場合、subagent は置換ではなく差分提案にする。
- gate failed、trace missing、scope violation、unresolved decision hidden のいずれかで promotion しない。
- 人間には全文ではなく、採用差分、未決事項、リスク、代替案だけを提示する。

## final_recommendation

`system-architect` / `implementation-planner` は、長期的には writer 能力を持つべきである。ただし、canonical docs を自由に編集する writer ではなく、staged / mode-based writer として設計するべき。

結論:

- read-only adviser は review / arbitration / high-risk analysis には残す。
- primary authoring では proposed artifact または patch を生成させる。
- canonical promotion は main orchestrator が担う。
- 人間ユーザーには diff、trace、未決事項、リスクだけを提示する。
- Permission Profile / diff gate は補助輪であり、責任境界と transaction 設計を主防御にする。

この方式が、専門 subagent の価値を最大化しつつ、spec-dock の source of truth と review independence を壊しにくい。
