---
種別: research
ID: "20260627t031714z-research"
タイトル: "Clarification Before Requirement Authoring"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連: []
authority: "synthesized"
derived_from:
  - "../../../discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md"
  - "../../../discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md"
  - "../../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md"
  - "../../../discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md"
  - "../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md"
reflected_to: []
---

# 20260627t031714z-research Clarification Before Requirement Authoring

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的
- `iss-00241` の要件定義に入る前に、Epic 00224 の spec-reviewer 追加レビューで確認された P0 / P1 gap を source-grounded に整理する。
- 新 Issue が解くべき課題、既存 Issue / Epic artifact との境界、要件化前に人間判断が必要な論点を切り分ける。
- 既存 review artifact は Epic に残し、この Issue はそれらを参照して corrective work を行う前提を確認する。

## sources / 調査方法
- 参照先:
  - Epic 00224 `requirement.md` / `design.md` / `plan.md` / `report.md`
  - Epic discussion `20260627t025746z-research-epic-quality-gate-traceability-audit.md`
  - Epic discussion `20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md`
  - ADR `20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
  - ADR `20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
  - Issue `iss-00238` research / report
  - Issue `iss-00239` scaffold
  - provider / dogfooding `github-pr-observation` skill and trigger script
  - `tests/unit/infra/test_init_update.py`
- 検証手順:
  - `spec-reviewer` review result を Epic artifact 化した。
  - `spec-dock new issue` で `iss-00241 / #241` を作成した。
  - `spec-dock sync` を実行し、post-mutation sync failure を回復した。
  - `issue start iss-00241 --force` を試行したが、dirty worktree guard により安全停止した。
- 実験条件:
  - Worktree: `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock`
  - Branch: `iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files`
  - Active issue at sync time: `iss-00238`
  - New issue: `iss-00241 Resolve Epic Traceability And Review Policy Gate Gaps`, GitHub `#241`

## facts / 観測できた事実
- `iss-00241` は作成済みで、GitHub issue `#241` に紐づいている。
- `issue start iss-00241 --force` は dirty worktree のため失敗した。失敗理由は checkout safety guard であり、dependency readiness failure ではない。
- dirty worktree には、既存の手動テスト文書削除、runtime / tests の変更、Epic discussion review artifacts、`iss-00241` scaffold が混在している。
- `spec-reviewer` は review_status `fail` を返し、以下を P0 / P1 とした:
  - P0: trusted base policy failure が human gate にならず bare `@codex review` に fallback している。
  - P1: `github-pr-observation` skill write contract が stale。
  - P1: `guidance <target>` stdout handoff が Epic 正本へ昇格されていない。
  - P1: corrective Issue `iss-00239` が scaffold のまま。
  - P1: Epic report completion evidence が内部矛盾している。
- `iss-00239` は既に corrective Issue として存在するが、要件・設計・計画・report が scaffold 状態である。
- Epic artifact 側に追加した監査 / spec-reviewer report は、Epic discussions に残したままでよいというユーザー判断がある。

## inference / 推測
- 事実から推測したこと:
  - `iss-00241` は単なる PR review trigger bug fix ではなく、Epic 00224 の closure gate / traceability gate を補修する corrective integration Issue として扱うのが妥当である。
  - P0 trusted policy failure と P1 skill contract stale は同一 implementation slice で直すと整合しやすい。
  - `guidance` handoff の Epic canonical reflection と Epic report reconciliation は docs/spec slice だが、runtime implementation と tests の current truth に依存するため同じ corrective Issue で扱う方が取りこぼしを防ぎやすい。
  - `iss-00239` の扱いは scope 判断が必要である。`iss-00241` に吸収すると traceability closure は単純になるが、既存 issue を空のまま残すとまた closure gap になる。
- 推測の根拠:
  - Spec reviewer finding はすべて Epic close readiness / PR merge-prepared readiness を block すると判定している。
  - Decision routing guide では、cross-issue design backbone と quality gate gap は Epic / Epic配下 corrective Issue に置くべきであり、単一実装 bug に閉じない。
  - User request は「これらの課題を解決する、取りこぼした要件を達成する Issue」を求めている。

## unverified / 未検証事項
- まだ確認していないこと:
  - `iss-00241` start 後の branch / active manifest / context pack の状態。
  - `iss-00239` をこの Issue に吸収するか、別 Issue として planning / execution するかの最終判断。
  - trusted policy human gate の JSON contract の詳細名称:
    - `overall_status=human_gate`
    - `trigger.action=skipped` / `blocked` / `none`
    - limitation code naming
  - Epic canonical docs の更新範囲:
    - requirement / design / plan / report すべてをこの Issue で更新するか
    - accepted ADR 本文へ追記するか、追記 discussion で扱うか
  - Issue start を可能にするための dirty worktree 整理方法。
- 確認できない理由:
  - dirty worktree を勝手に stash / commit / revert することは安全でない。
  - `iss-00239` の扱いは scope / ownership / issue lifecycle に影響し、人間の意図確認で変わり得る。

## question candidates / 質問候補
- source-grounded に解けず、人間判断が必要な候補:
  - `iss-00241` は `iss-00239` の未解決 corrective scope を吸収して閉じるべきか、それとも `iss-00239` は独立した Issue として残し、`iss-00241` では Epic traceability / review policy / report reconciliation だけを扱うべきか。
  - dirty worktree をどう整理して issue start を完了するか。
  - Epic ADR 本文そのものを更新するか、ADR は historical accepted decision として残し、新しい `disc` / Epic docs で reflection するか。
- pressure-test question として切り出すべき候補:
  - `iss-00239` の扱い。これは requirement / design / plan の scope と issue dependency を大きく変える。
- 質問せずに解決できた候補:
  - review artifact は Epic に残す。ユーザーが「EPICに置いといたままでいい」と明示した。
  - 新 Issue は作成する。ユーザーが明示した。
  - 要件定義書はまだ作成しない。ユーザーが明示した。

## terminology conflicts / 用語衝突
- 衝突している用語:
  - `workflow next` vs `guidance <target>`
  - `Runbook projection` vs `agent handoff authority`
  - `fixed @codex review body` vs `deterministic runtime-composed review body`
  - `Issue complete` vs `Epic close readiness`
- 既存 docs / code / tests / discussions での使われ方:
  - Epic requirement / old ADR wording は `workflow next` を primary handoff として残している。
  - `iss-00238` discussion / report / shipped skills / tests は `guidance <target>` を primary handoff とし、`workflow next` 互換 alias 不要としている。
  - `github-pr-observation` skill は fixed body と説明するが、trigger happy path は multiline deterministic body を生成する。
  - accepted ADR は missing base policy を human gate とするが、tests は fallback success を期待している。
- 判断が必要な理由:
  - 後続要件で用語を誤ると、実装対象が過去仕様へ戻る。
  - Skill / runtime / tests / Epic docs が同じ public contract を共有しない限り、同じ取りこぼしが再発する。

## edge cases / 具体シナリオ
- edge case:
  - PR head に `.github/codex/review-policy.md` を追加しているが、base branch にはまだない。
  - base SHA は取れるが policy file fetch が 404 / permission failure / non-UTF-8 / oversized。
  - `guidance` stdout は成功するが projection write は symlink / permission / stale path で失敗する。
  - `iss-00239` が未完了のまま `iss-00241` だけが完了扱いになる。
  - Epic report が pass と blocked を同時に示す。
  - issue start したいが worktree に前 Issue の未コミット差分が残っている。
- その edge case が requirement / design / plan に与える影響:
  - trusted policy failure path は acceptance criteria と negative tests が必要。
  - projection failure と context packet failure は同じ扱いにしない設計が必要。
  - issue scope に `iss-00239` closure を含めるかどうかで plan steps と dependencies が変わる。
  - Epic report reconciliation を final step / S90/S99 相当に置く必要がある。

## implications / 判断への含意
- `iss-00241` requirement では、少なくとも次を扱う必要がある:
  - trusted base policy failure の fail-closed human gate
  - `github-pr-observation` skill / provider / dogfooding / tests の contract parity
  - Epic canonical docs の `guidance <target>` reflection
  - Epic report closure ledger reconciliation
  - corrective issues `iss-00237` / `iss-00238` / `iss-00239` の Epic final gate inclusion
- `iss-00241` design では、script JSON contract、skill wording contract、Epic doc update policy、report reconciliation policy を分ける必要がある。
- `iss-00241` plan では、implementation fix と docs/spec reconciliation を分けつつ、最後に spec-reviewer gate を必須にする必要がある。
- `iss-00239` の扱いが未確定のため、要件定義へ進む前に formal interview で scope を確認するのが妥当である。

## リスク/制約
- Dirty worktree のため `issue start` は未完了。勝手に stash / commit / revert しない。
- `iss-00241` 作成時、post-mutation sync は一度失敗したが、filename 修正後の `spec-dock sync` は成功した。
- `spec-dock new issue` は GitHub issue `#241` を作成済みのため、重複 Issue を作らない。

## 反映先
- reflected_to:
  - 未反映。次はユーザー回答後、`iss-00241` requirement / design / plan authoring に進む。

## 参考（References）
- `../../../discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md`
- `../../../discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md`
- `../../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
- `../../../discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
- `../iss-00238-stdout-runbook-handoff-instead-of-generated-workflow-files/discussions/20260624t083737z-research-stdout-runbook-handoff-current-state.md`
