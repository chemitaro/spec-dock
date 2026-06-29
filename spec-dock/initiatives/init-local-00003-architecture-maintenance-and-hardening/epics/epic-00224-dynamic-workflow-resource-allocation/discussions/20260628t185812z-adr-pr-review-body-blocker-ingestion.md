---
種別: ADR（Architecture Decision Record）
ID: "20260628t185812z-adr"
タイトル: "PR Review Body Blocker Ingestion"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
amends:
  - "20260623t074447z-adr"
  - "20260628t154553z-adr"
derived_from:
  - "PR #245 Codex review finding: Include pull review bodies in blocker policy"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
reflected_to:
  - "../design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
---

# 20260628t185812z-adr PR Review Body Blocker Ingestion

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - PR observation の blocker 判定がどの GitHub surface を authority として読むかは、merge-prepared 判定の安全性を直接左右する。
  - PR #245 の dogfooding review で、Codex の submitted pull request review body に P1 が含まれる場合、inline comment / review thread がなくても blocker として扱う必要があることが確認された。
  - これは単なる parser detail ではなく、`comment zero` ではなく `verified blocker zero` で閉じるという Epic の PR closure contract の入力境界である。

## 結論（Decision）

- Codex-authored submitted pull request review body は、PR observation の blocker policy input として扱う。
- Current trigger boundary と expected head SHA に bind された selected pull request review body に P0 / P1 finding が含まれる場合、inline review comment / review thread が 0 件でも merge-prepared にはしない。
- Blocker scan の対象は、current Codex issue comments だけではなく、selected pull request review signals を含む。
- selected pull request review body は、completion artifact であると同時に blocker evidence source である。ただし completion proof と blocker disposition は別責務として扱う。
- Pull request review body に含まれる P0 / P1 は、inline thread が存在しない場合でも `human_gate` / `address_review_feedback` へ進める。
- Review body の P2 / P3 は、既存の blocker-centric policy と同じく default non-blocking とし、protected-domain + machine evidence がある場合のみ blocker promotion 対象にする。
- Wrong head、old trigger、current boundary 外の review body は current blocker input として扱わない。

## 背景（Context）

- `20260628t154553z-adr PR Observation Explicit Review Completion` は、review completion を explicit Codex artifact で判断する方針を固定した。
- `20260623t074447z-adr Blocker Centric PR Risk Closure And Re Review` は、merge preparedness を comment zero ではなく verified blocker zero で判断する方針を固定した。
- しかし実装上、blocker policy は current Codex issue comments を中心に scan しており、selected pull request review body の P0 / P1 を blocker evidence として十分に扱えていなかった。
- PR #245 の Codex review は、この gap を P1 として指摘した。特に、review body だけに `[P1]` があり、inline thread/comment がない場合、旧実装は pass 方向に倒れる可能性があった。

## 選択肢（Options considered）

- Option A: inline review comments / review threads だけを blocker input とする。
  - Pros:
    - 実装が単純。
    - line-level repair と対応づけやすい。
  - Cons:
    - Review body だけに P0 / P1 が書かれる GitHub/Codex surface を見逃す。
    - submitted review を completion artifact として認識しながら、その body の blocker finding を無視する矛盾が生じる。
  - 判断: 棄却する。
- Option B: selected pull request review body を issue comment と同等の blocker input に含める。
  - Pros:
    - Codex review の observable surface を漏れなく blocker policy に取り込める。
    - inline thread がない P1 でも merge-prepared を止められる。
    - 既存の severity / protected-domain / machine-evidence policy を再利用できる。
  - Cons:
    - review body parsing の false positive / wording drift に注意が必要。
  - 判断: 採用する。
- Option C: Review body に P0 / P1 がある場合は常に human-only gate とし、machine policy へ入れない。
  - Pros:
    - 誤検出時の自動判断を避けられる。
  - Cons:
    - blocker-centric repair loop の自動化価値が下がる。
    - issue comments と review body で severity policy が分岐し、運用が複雑になる。
  - 判断: 採用しない。

## 判断理由（Rationale）

- Submitted pull request review は、Codex review worker が完了したことを示す主要 artifact の一つである。その body を blocker policy から外すと、completion は認識するが finding は捨てるという不整合が起きる。
- GitHub review surface は、inline comments / threads だけでなく review body に summary finding を含み得る。PR observation は GitHub上で可視な Codex-authored finding を surface 種別で取りこぼしてはならない。
- Epic の目的は P2/P3 noise を避けることであり、P0/P1 blocker を見逃すことではない。Review body P0/P1 の取り込みは、低価値 review loop 削減と矛盾しない。
- Review body を入力に含めても、current trigger boundary / expected head SHA binding を維持すれば stale review の混入を抑えられる。

## 影響（Consequences）

- Positive:
  - Pull request review body だけに P0 / P1 が存在する場合も merge-prepared を止められる。
  - submitted PR review artifact と blocker-centric closure の責務境界が明確になる。
  - PR #245 型の reviewer finding を regression test として固定できる。
- Negative / Debt:
  - Review body parser の wording 変化に追随する必要がある。
  - Body-level finding は file/line location を持たない場合があり、repair guidance では review id / body excerpt / severity を evidence として扱う必要がある。
- 影響範囲:
  - `pr_review_snapshot.py` の blocker policy input。
  - `tests/unit/infra/test_init_update.py` の PR review body blocker regression。
  - `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh` の stdout JSON evidence。
  - Epic / Issue docs の review completion / blocker closure 説明。
- 移行/ロールバック:
  - 旧 artifact を読む場合でも、current selected review body があるなら blocker input として扱う。
  - この decision を戻す場合は、review body P0/P1 を別 gate で確実に止める新 ADR が必要である。

## 旧決定との関係（Supersession / Amendment）

- `20260623t074447z-adr Blocker Centric PR Risk Closure And Re Review`:
  - 補完: verified blocker zero の入力には、current Codex issue comments、selected review comments、selected review threads に加え、selected pull request review body を含める。
  - 変更済み: inline comment / thread が 0 件であれば blocker zero とみなせるという旧実装上の暗黙前提は廃止済み。
- `20260628t154553z-adr PR Observation Explicit Review Completion`:
  - 補完: submitted pull request review は completion artifact であると同時に、その body が blocker evidence source になり得る。
  - 変更済み: selected review comments / threads 0 は no-finding proof ではない。selected review body の blocker scan を通した後でなければ blocker zero と扱わない。

## 非目標（Non-goals）

- Codex review body の自然言語を完全構造化 output として扱うことはしない。
- P2/P3 をすべて blocker に昇格しない。
- GitHub Checks API / statusCheckRollup を新たな authority にしない。
- Review body parsing の全面 rewrite はこの ADR の直接 scope ではない。

## 参考（References）

- `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`
- `20260628t154553z-adr-pr-observation-explicit-review-completion.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md`
