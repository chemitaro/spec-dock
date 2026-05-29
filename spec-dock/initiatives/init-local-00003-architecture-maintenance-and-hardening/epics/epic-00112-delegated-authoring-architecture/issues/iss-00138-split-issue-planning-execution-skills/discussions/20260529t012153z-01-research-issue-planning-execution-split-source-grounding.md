---
種別: research
ID: "20260529t012153z-01-research"
タイトル: "Issue planning execution split source grounding"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00138"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260529t012153z-01-research Issue planning execution split source grounding

## 調査目的 (必須)
- `iss-00138` の `requirement.md` 作成前に、Issue planning / Issue execution skill split の根拠、既存 asset との整合、変更候補、未確定な人間判断を整理する。
- local context で解ける範囲を先に確認し、ユーザーへ聞くべき質問を最小化する。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md}`
  - `spec-dock/active/issue/discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/active/epic/{requirement.md,design.md,plan.md}`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_wrappers.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で active issue を確認した。
  - active issue / parent epic docs と issue discussion memo を読んだ。
  - provider-side skill assets と shipped docs の参照を `rg` で確認した。
  - skill asset list / install-update parity tests / wrapper tests の期待値を読んだ。
- 実験条件:
  - 実装変更は未実施。
  - GitHub live state は未確認。今回の調査は local repo / active docs / tests に基づく。

## facts / 観測できた事実 (必須)
- Active issue は `iss-00138 Split Issue Planning and Execution Skills` で、branch は `iss-00138-split-issue-planning-execution-skills`。
- `requirement.md` / `design.md` / `plan.md` は template scaffold のままで、canonical requirement は未作成。
- issue discussion memo は、Issue planning skill の新設、Issue execution skill の実装専用整理、hub skill の導線整理、provider/dogfooding parity、init/update tests の必要性を候補として挙げている。
- `workflow_spec_authoring.md` は Initiative / Epic / Issue 共通で `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` を正本にしている。
- `workflow_clarification.md` は、重要判断について回答前に unanswered `interview` artifact を作り、回答後に同じ artifact へ回答と採用判断を追記するよう定めている。
- 現行 `spec-dock-initiative-planning` と `spec-dock-epic-planning` は requirement / design / plan planning 用の leaf skill である。
- 現行 `spec-dock-issue-execution` は、active issue execution、`plan.md` を command queue とする TDD execution、`report.md` evidence ledger、gap 発見時の clarification / authoring phase return、PR delivery / issue finish などを扱う skill である。
- 現行 `spec-driven-tdd-workflow` は leaf routing で `spec-dock-issue-execution` を `issue-level TDD execution and report updates` と説明しており、Issue planning leaf skill は存在しない。
- `src/spec_dock/assets/spec_dock/docs/README.md` は agent entrypoint として Issue を `.agents/skills/spec-dock-issue-execution/SKILL.md` のみで案内している。
- provider-side install asset の正本は `src/spec_dock/assets/install_root/.agents/skills/` であり、dogfooding `.agents/skills/` 側は parity 確認対象。
- `tests/test_init_update.py` は managed asset mapping、authoritative install-root relative paths、docs README skill list、bundled skill routing contract で skill 名を固定している。
- `tests/cli_runtime/harness.py` と `tests/cli_runtime/test_wrappers.py` は bundled skills / wrapper surface で `spec-dock-issue-execution` を確認している。
- `workflow_issue.md` の対応 leaf skill は現状 `.agents/skills/spec-dock-issue-execution/SKILL.md` のみ。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Issue planning skill を追加する場合、単に skill file を追加するだけでは不十分で、hub skill、README/guide/workflow docs、managed asset tests、dogfooding parity の更新が必要になる可能性が高い。
  - `workflow_spec_authoring.md` はすでに Issue の requirement / design / plan authoring を共通 workflow として扱っているため、新規 `spec-dock-issue-planning` は新しい policy 正本ではなく、`workflow_spec_authoring.md` / `workflow_issue.md` / phase playbook への routing reminder として設計するのが小さい。
  - `spec-dock-issue-execution` はすでに execution 中心に整理されているため、この issue の主な変更は「Issue planning leaf skill の追加」と「routing / docs / tests の表示整合」になりそう。
  - planning + execution の同時指定は、automatic execution ではなく、planning gate pass 後に execution へ handoff できる sequencing として表現する方が既存 gate と整合する。
- 推測の根拠:
  - Existing Initiative / Epic planning skills は短い workflow reminder で、policy body は docs 側に置かれている。
  - `workflow_spec_authoring.md` は reviewer pass なしの downstream handoff を block している。
  - `workflow_issue.md` は unresolved spec gap を execution 内で吸収せず clarification / authoring phase へ戻す契約を持つ。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - GitHub Issue #138 の body / comments に、local discussion memo 以外の要求があるか。
  - 新規 `spec-dock-issue-planning` を docs `workflow_issue.md` の対応 leaf skill として併記するか、`workflow_spec_authoring.md` / hub skill のみに置くか。
  - dogfooding `.agents/skills/` 側をこの issue の実装で直接同期するか、provider-side 更新後に update / parity check で反映するか。
  - planning skill が canonical docs 直接編集を「orchestrator が行う」ことを明記するだけか、role skill 自体を canonical writing entrypoint として表現するか。
- 確認できない理由:
  - これらは local source だけでは最終意図が確定しない scope / authority / UX 判断であり、requirement の scope と acceptance criteria に直接影響する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `Issue planning`
  - `Issue execution`
  - `spec authoring`
  - `planning + execution`
- 既存 docs / code / tests / discussions での使われ方:
  - `workflow_spec_authoring.md` は Initiative / Epic / Issue 共通の requirement / design / plan 作成を `spec authoring` と呼ぶ。
  - Initiative / Epic の leaf skill は `*-planning` で requirement / design / plan planning を案内する。
  - Issue の現行 leaf skill は `spec-dock-issue-execution` だけで、`workflow_issue.md` 内に spec authoring 節と execution policy の両方がある。
  - issue discussion memo は、Issue も Initiative / Epic と抽象度を揃え、planning と execution を分けたいとしている。
- 判断が必要な理由:
  - `spec-dock-issue-planning` の責務を「canonical docs を書く orchestrator workflow reminder」と見るか、「委任 role が direct write する skill」と見るかで、必要な permission / authority / report evidence / tests が大きく変わる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - ユーザーが `$spec-dock-issue-planning` だけを指定し、active issue docs が template の場合。
- その edge case が requirement / design / plan に与える影響:
  - planning skill は active issue の requirement / design / plan authoring に入り、source-grounded read と必要な interview を行い、canonical docs 作成へ進む導線を示す必要がある。
- edge case:
  - ユーザーが `$spec-dock-issue-execution` だけを指定し、requirement / design / plan に gap または template placeholder が残っている場合。
- その edge case が requirement / design / plan に与える影響:
  - execution skill は実装を開始せず、planning / clarification へ戻す stop condition を明示する必要がある。
- edge case:
  - ユーザーが `$spec-dock-issue-planning` と `$spec-dock-issue-execution` を同時指定し、簡単な要件だけを渡す場合。
- その edge case が requirement / design / plan に与える影響:
  - planning phase の reviewer gate / handoff readiness が execution の前提であり、同一リクエストでも gate を飛ばして実装へ進まないことを acceptance criteria に含める必要がある。
- edge case:
  - 新規 skill asset を provider-side に追加したが、managed asset test / dogfooding `.agents/skills` に反映されない場合。
- その edge case が requirement / design / plan に与える影響:
  - provider-first と dogfooding parity を requirement / acceptance criteria に含める必要がある。

## implications / 判断への含意 (必須)
- Requirement には、Issue planning skill の新設、Issue execution skill の実装専用境界、hub/docs/test parity、clarification との組み合わせ、gate を飛ばさない sequencing を観測可能な acceptance criteria として置くべき。
- Requirement の対象外には、Permission Profile / sub-agent callability の追加実装、完全自動 planning-to-execution、GitHub/Copilot agent support、workflow_issue の全面再設計を置くのが小さい。
- 最初に人間判断が必要なのは、`spec-dock-issue-planning` を canonical docs direct authoring skill として扱うか、main orchestrator 向けの issue-level planning workflow reminder として扱うかである。

## リスク/制約 (任意)
- Planning skill に direct authoring authority を持たせると、Epic の delegated authoring authority model と衝突しやすく、Permission Profile / promotion record / report ledger まで scope が広がる。
- Hub skill が planning + execution を「半自動」とだけ表現すると、reviewer gate 前に implementation へ進む誤解を生みうる。
- Tests は skill asset の存在だけでなく、hub routing text と docs README の導線も更新しないと regression を見逃す可能性がある。

## 反映先 (任意)
- reflected_to:
  - pending: `spec-dock/active/issue/requirement.md`
  - pending: `spec-dock/active/issue/report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- `spec-dock/active/issue/discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
- `tests/test_init_update.py`
- `tests/cli_runtime/test_wrappers.py`
