---
種別: research
ID: "20260619t164615z-research"
タイトル: "Carryover observation source analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00219"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to:
  - "requirement.md"
  - "design.md"
---

# 20260619t164615z-research Carryover observation source analysis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- GitHub issue `#219` が扱う carryover-only unresolved thread の premature stop を、既存の PR observation contract、コード、テスト、隣接 Issue の決定に照らして整理する。
- Requirement / design / plan authoring 前に、ローカル source で解ける事実と、人間判断が必要な policy gap を分離する。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub issue `#219`
  - `spec-dock/active/issue/{requirement,design,plan,report}.md`
  - `spec-dock/active/epic/{requirement,design,plan}.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `tests/unit/infra/test_init_update.py`
  - `iss-00187`, `iss-00197`, `iss-00214`, `iss-00215` の requirement docs
- 検証手順:
  - `issue start iss-00219` で active context を設定した。
  - GitHub issue body を `gh issue view 219 --json number,title,state,body,url` で確認した。
  - `rg` で `carryover_non_outdated_unresolved_thread`, `review_completion_unknown`, `completion_signal`, `terminal_now`, `recommended_next_action` を横断検索した。
  - 該当 Python entrypoint と既存 regression test を line-level に確認した。
- 実験条件:
  - まだコード実行による再現テストは作っていない。現段階は source-grounded clarification。

## facts / 観測できた事実 (必須)
- Issue `#219` の対象は `#218` とは別である。`#218` は `fallback_issue_comment` を trusted completion signal へ昇格できるかの問題で、`#219` は `completion_signal="none"` かつ carryover-only unresolved threads があるときに wait loop が current review completion を観測し切らず停止する問題である。
- GitHub issue `#219` の観測例では、CI は passed、head は matched、`current_selected_unresolved_count=0`、`completion_signal="none"`、`carryover_unresolved_count=8`、`review_completion_unknown_latency_satisfied=false` なのに、`status_reason="carryover_non_outdated_unresolved_thread"` で `human_gate` へ停止している。
- `.agents/skills/github-pr-observation/SKILL.md` は、final readiness が current trigger/resume boundary に scoped されること、`decision` が authoritative であること、carryover unresolved review threads は actionable inventory に含まれることを明記している。
- 同 skill は `review_completion_unknown` を「CI passed、head matched、actionable review inventory empty、trusted completion signal missing、latency guards satisfied」の non-pass human gate として説明している。
- `pr_review_snapshot.py` は `selected_unresolved_thread_ids` と別に、GitHub thread data 上で `state=="unresolved"` かつ selected されていない thread を `carryover_non_outdated_unresolved_threads` とし、`actionable_unresolved_thread_ids` に追加する。
- `pr_observation_snapshot.py` の `actionable_unresolved_reason(...)` は `carryover_unresolved_count > 0` または `actionable_unresolved_count > 0` を `carryover_non_outdated_unresolved_thread` として返す。
- `pr_observation_snapshot.py` の `classify_snapshot(...)` は `ci_status == "passed" and actionable_reason` の場合、current selected と carryover の区別なく `human_gate`, `address_review_feedback`, `observation_complete=True` を返す。
- `pr_observation_wait.py` の `classify(...)` も `ci_status == "passed" and actionable_reason` の場合、`human_gate`, `address_review_feedback`, `terminal=True` を返す。
- `pr_observation_wait.py` の `is_review_completion_unknown_candidate(...)` は `actionable_unresolved_reason(payload)` があると `False` を返すため、carryover-only actionable inventory がある限り `review_completion_unknown` 候補にならない。
- 既存テストは `iss-00182` 周辺で historical audit unresolved thread が final action を支配しないことを固定している。一方、current selected unresolved thread は即 `address_review_feedback` になることを固定している。
- `iss-00187` の requirement は、selected unresolved count が 0 でも non-outdated unresolved carryover thread は actionable review work として可視化し、`review_completion_unknown` / merge-prepared の前に扱う方針を含む。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 現在の premature stop は、collector が carryover を actionable inventory に入れる判断自体ではなく、wait/snapshot classification が carryover-only actionable inventory を current-boundary completion observation の完了条件と同じ扱いにしていることから起きている。
  - 既存仕様は「carryover は無視しない」と「current review completion を観測し切る」を両方要求しており、Issue219 はその調停 policy を固める必要がある。
  - 実装候補は、current selected blocker と carryover-only blocker を分類上分け、carryover-only + missing current completion signal + latency guard 未満では terminal にしないこと。
- 推測の根拠:
  - `classify_snapshot(...)` と `classify(...)` が current selected と carryover を `actionable_reason` でまとめて即 human gate にしている。
  - `review_completion_unknown` の候補判定が actionable inventory の存在で一律除外される。
  - GitHub issue `#219` の期待挙動は、carryover-only では current review completion / current-boundary feedback / latency guard のいずれかまで観測を続けることを求めている。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実際に現行コードで Issue `#219` の JSON fixture を red test として再現すること。
  - Provider-side source `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/...` と dogfooding mirror `.agents/...` の差分方針。
  - `recommended_next_action` を latency guard 未満の carryover-only incomplete state で `wait_or_resume` にするか、resume guidance を持つ新しい/既存 action にするか。
- 確認できない理由:
  - これは requirement/design の境界に関わる policy 判断であり、実装前にユーザーの運用意図を確認したい。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - carryover-only unresolved threads があるが current-boundary completion signal がまだない場合、latency guard 未満で wait loop を止めてもよいか。
  - latency guard 後の final state を `review_completion_unknown` にするか、carryover-specific human gate にするか。
- pressure-test question として切り出すべき候補:
  - 「carryover-only + completion_signal none + latency guard 未満」の final/wait policy。
- 質問せずに解決できた候補:
  - `#218` は本 Issue の範囲外。
  - current selected unresolved feedback は従来通り即 `address_review_feedback` でよい。
  - carryover unresolved thread 自体は audit-only ではなく actionable inventory として可視化する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `actionable_unresolved`
  - `observation_complete`
  - `review_completion_unknown`
  - `human_gate`
- 既存 docs / code / tests / discussions での使われ方:
  - `actionable_unresolved` は current selected と carryover の両方を含む。
  - `observation_complete` は current trigger boundary の review completion 観測が終わったかの意味で使われるが、現コードでは carryover actionable があると early terminal になり得る。
  - `review_completion_unknown` は actionable inventory empty が前提のため、carryover actionable があるケースの終端名としては現状使いにくい。
  - `human_gate` は final state としても partial/incomplete stop としても使われ得るため、`status_reason` / `recommended_next_action` / `observation_complete` の組み合わせで区別が必要。
- 判断が必要な理由:
  - 用語を曖昧にしたまま実装すると、carryoverを無視する false pass か、current review 未観測の premature stop のどちらかに寄りやすい。

## edge cases / 具体シナリオ (必須)
- edge case:
  - EC-001: CI passed、head matched、current selected unresolved 0、completion signal none、carryover unresolved > 0、latency guard 未満。
  - EC-002: EC-001 と同じだが latency guard 満了。
  - EC-003: current selected unresolved > 0。
  - EC-004: fallback issue comment present。
  - EC-005: carryover unresolved > 0 だが thread outdated state unavailable/null。
- その edge case が requirement / design / plan に与える影響:
  - EC-001 は本 Issue の主要 pressure-test。wait継続か partial stop かで design と tests が変わる。
  - EC-002 は `review_completion_unknown` と carryover human gate の関係を決める。
  - EC-003 は既存 behavior を維持する regression test が必要。
  - EC-004 は `#218` との境界として scope-out / no behavior change を固定する。
  - EC-005 は既存 skill に従い actionable inventory へ昇格しない前提でよい。

## implications / 判断への含意 (必須)
- Requirement では、carryover-only unresolved thread を actionableとして可視化しつつ、current review completion observation を早期完了扱いしないことを明記する必要がある。
- Design では、current selected blockers と carryover-only blockers の分類を分け、wait loop の `terminal` 判定と snapshot `observation_complete` を分離する必要がある。
- Plan では、少なくとも red test として「latency guard 未満の carryover-only は terminal complete にならない」「current selected unresolved は即 terminal human gate」「latency guard 後の policy」を固定する必要がある。
- Provider-side source が authority なので、実装時は `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/...` を先に変更し、dogfooding mirror `.agents/...` を同期/同等確認する。

## リスク/制約 (任意)
- Carryoverを単純に non-actionable に落とすと、既存 `iss-00187` の「selected_unresolved_count == 0 は no review work の証明ではない」という安全性を壊す。
- Carryoverを単純に terminal actionable に残すと、Issue `#219` の premature stop が解消されない。
- `review_completion_unknown` は現定義だと actionable inventory empty 前提なので、carryoverありケースでそのまま使うには定義変更または carryover-specific status reason が必要になる。

## 反映先 (任意)
- reflected_to:
  - done: `requirement.md`
  - done: `design.md`
  - pending: `plan.md`
  - pending: `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- GitHub issue `#219`
- `.agents/skills/github-pr-observation/SKILL.md`
- `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `tests/unit/infra/test_init_update.py`
