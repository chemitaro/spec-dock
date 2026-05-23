---
type: research
source: chatgpt-pro
created_at: 2026-05-23T12:35:03+09:00
epic: epic-00112
topic: initial research reinterpretation
status: current
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a119d0a-f084-83a6-b33c-a06825f3c54c
---

# ChatGPT Pro Research: Initial Research Reinterpretation

## source_note

This report summarizes a ChatGPT Pro thread created through Chrome in the Codex-only ChatGPT Project. It is external analytical input and should not be treated as independently verified repo truth.

## interpretation_of_initial_research

ChatGPT Pro は、初期リサーチの「設計書と実装計画書は、専任サブエージェントを一次作成者にした方がよい」と、「Modify `design.md` / `plan.md` directly 禁止」は矛盾ではない、と判断した。

これは draft candidate author と canonical artifact writer / owner を分離する設計だと読むのが最も整合的である。

| 対象 | 一次的な知的著者 | canonical 所有者 | 最終責任 |
| --- | --- | --- | --- |
| `requirement.md` | main orchestrator + human | main orchestrator | main orchestrator |
| `design.md` | system-architect | main orchestrator | main orchestrator |
| `plan.md` | implementation-planner | main orchestrator | main orchestrator |
| review evidence | spec-reviewer | main orchestrator が統合 | review independence を維持 |

ここでいう「一次作成者」は、必ずしも `design.md` や `plan.md` のファイルを直接編集する主体ではない。approved `requirement.md` などを入力として、canonical artifact に昇格可能な品質・粒度の draft candidate を最初に構成する主体である。

## does_readonly_satisfy_original_intent

read-only であること自体は、初期意図と矛盾しない。

ただし、現在の read-only 実装が「adviser」に留まっているなら初期意図を満たしていない。read-only でも、subagent が complete draft candidate を出力しているなら、初期意図の重要部分は満たしている。

### read-only adviser なら初期意図を満たさない

次のような出力しか返さない場合:

- 設計観点のコメント
- リスク指摘
- 構成案
- `design.md` には X を含めるべき、という助言
- `plan.md` 作成前の注意点

この場合、実際の `design.md` / `plan.md` の一次著者は main orchestrator のままであり、`system-architect` / `implementation-planner` は consultant とほぼ同じになる。

### read-only draft-candidate author なら初期意図を概ね満たす

read-only でも次を返すなら、初期意図と整合する。

- `design.md` としてそのまま昇格可能な全文候補
- 既存 `design.md` に対する unified diff 候補
- section-by-section replacement candidate
- requirement traceability 付きの design candidate
- unresolved questions / assumptions / risks / rejected alternatives を含む candidate

`implementation-planner` も同様に、`plan.md` の完全候補や差分候補を返すなら、read-only であっても「一次作成者」と言える。

## draft_candidate_vs_file_writer

問題の本質は、writer を一語で扱っていること。少なくとも次の 4 種類を分けるべき。

| 種別 | 役割 | system-architect / implementation-planner に許可すべきか |
| --- | --- | --- |
| Adviser | 助言・論点・リスクを返す | 可。ただしこれだけでは弱い |
| Draft candidate author | 完成度の高い候補文書を作る | 是 |
| Scratch artifact writer | 非 canonical な draft path に候補を書き出す | 条件付きで是 |
| Canonical artifact writer | `design.md` / `plan.md` を直接編集する | 初期導入では否 |

初期リサーチの正しい読みは次である。

> subagent は `design.md` / `plan.md` の一次 draft candidate author である。main orchestrator は canonical artifact writer / owner / integrator / promoter である。

## where_current_design_is_too_conservative

現在の設計が保守的すぎる可能性があるのは、canonical direct edit を禁止している点ではない。そこは妥当である。

保守的すぎるのは、read-only を理由に subagent の出力を advisory evidence 程度に弱めてしまう点。

ズレ:

- `draft evidence` が曖昧すぎる。
- read-only adviser と read-only author が区別されていない。
- main orchestrator の責務が「統合」ではなく「再著述」になっている可能性がある。
- consultant と authoring specialist の差分が出力契約に現れていない。
- future write-capable readiness が「canonical write」か「draft path write」か曖昧。

## corrected_intent_statement

修正後の intent statement は次。

> `system-architect` は、approved `requirement.md` を入力として、canonical `design.md` を直接編集せずに、promotion-ready `design.md` draft candidate を一次作成する。
> `implementation-planner` は、approved `requirement.md` と approved / candidate `design.md` を入力として、canonical `plan.md` を直接編集せずに、promotion-ready `plan.md` draft candidate を一次作成する。
> delegated draft candidate は authority ではなく auditable evidence であり、main orchestrator が検証・統合・必要なユーザー確認・canonical 反映を行うまで source of truth ではない。

短く言うなら:

> Subagents should be primary authors of draft candidates, not direct writers of canonical artifacts.

日本語では:

> サブエージェントは `design.md` / `plan.md` の一次候補著者であるべきだが、canonical artifact の直接編集者であるべきではない。

## recommendation

`system-architect` / `implementation-planner` を単なる read-only adviser に留めるべきではない。ただし、初期導入で `design.md` / `plan.md` の canonical file を直接編集する writer にするべきでもない。

最適解は、read-only draft-candidate author、または将来的には non-canonical scratch writer である。

推奨:

1. 初期 Epic では canonical direct write を禁止したままでよい。
2. ただし role contract を adviser から candidate author に強化する。
3. subagent output format を厳格化する。
4. 将来的には non-canonical writable draft path を検討してよい。
