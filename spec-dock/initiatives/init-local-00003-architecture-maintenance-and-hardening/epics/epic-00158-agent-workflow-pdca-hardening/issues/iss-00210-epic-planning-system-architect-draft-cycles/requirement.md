---
種別: 要件定義書（Issue）
ID: "iss-00210"
タイトル: "Epic Planning System Architect Draft Cycles"
関連GitHub: ["#210"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["epic-00158", "init-local-00003"]
---

# iss-00210 Epic Planning System Architect Draft Cycles — 要件定義（何を、なぜ行うか）

## 目的
- Epic planning で、非自明な Epic の設計・計画を main orchestrator の単独判断だけで進めず、`system-architect` の scope-local discussion draft を先に作成し、採用判断と fresh reviewer gate を通して canonical Epic docs へ統合する workflow を明確にする。
- Epic planning 完了時に、後続の独立 Issue である `iss-00211` が参照できる planning completion / handoff contract を定義する。
- `epic-00158` の context-surface 方針に従い、first-read workflow spine は skill に置き、詳細 semantics は docs へ分離し、canonical docs は main orchestrator single-writer authority に保つ。

## 背景・現状
- 現状の挙動:
  - `spec-dock-epic-planning/SKILL.md` は Epic planning の入口、fresh `spec-reviewer` gate、bounded delegation の基本境界を持つ。
  - しかし、Epic design / plan の前に `system-architect` discussion draft を作る条件、draft 採用の証跡、Issue 作成後の cross-issue draft package、issue-local draft requirement/design の扱いは first-read surface としてまだ明確ではない。
  - `iss-00211` は Epic planning 後の Epic execution coordinator を扱う予定だが、Issue 210 とは独立 Issue として実行する。
- 現状の課題:
  - 非自明な Epic で main orchestrator が直接 design / plan を作り始めると、Epic-level の設計判断が単独判断になりやすい。
  - Epic requirement / design / plan が十分に具体化する前に Issue 候補を固定すると、Issue 粒度や依存関係が後から歪みやすい。
  - 複数 Issue にまたがる vocabulary、責務境界、dependency order、handoff artifact が issue ごとに独立して作られると、重複・抜け漏れ・矛盾が起きやすい。
  - 後続の Epic execution coordinator が「Epic planning 完了時に何を入力として期待してよいか」を再定義してしまうリスクがある。
- 情報源:
  - GitHub issue `#210`
  - GitHub issue `#211`
  - 親 Epic `epic-00158` の `requirement.md` / `plan.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/authoring/decision-routing.md`
  - `discussions/20260619t023116z-research-issue-210-clarification-research.md`
  - `discussions/20260619t023120z-interview-issue-210-essential-scope-question.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock を使って Epic planning を行う main orchestrator。
  - Epic planning で draft evidence を作成する `system-architect`。
  - Epic planning 完了後に独立 Issue として Epic execution coordination を行う agent。
- 代表シナリオ:
  - 非自明な Epic を planning するとき、main orchestrator は requirement を固めた後、Epic-level design / plan の discussion draft を `system-architect` に作成させる。
  - main orchestrator は draft の採用 / 部分採用 / 棄却を Evidence Adoption Ledger に記録し、採用部分だけを canonical Epic docs へ統合する。
  - Epic design / plan から Issue list と dependency order を作成し、Issue 作成後には cross-issue draft requirement/design package を evidence として作る。
  - 各 issue の `discussions/` に draft requirement / draft design を置き、canonical issue docs は個別 Issue planning workflow で正式化する。
  - 後続の `iss-00211` は、この planning completion / handoff contract を参照できるが、Issue 210 の実行範囲には含まれない。

## スコープ
- 必須:
  - `spec-dock-epic-planning` skill に、非自明な Epic の Epic design / plan 前に `system-architect` discussion draft を使う workflow spine を追加する。
  - `system-architect` draft は scope-local `discussions/` artifact であり、canonical docs を直接編集しないことを明示する。
  - main orchestrator が draft の採用判断を Evidence Adoption Ledger に記録し、canonical Epic docs へ統合した後に fresh `spec-reviewer` gate を通すことを明示する。
  - Issue 作成は Epic requirement / design / plan の具体化と issue slicing / dependency analysis の結果として行うべきことを明示する。
  - Issue 作成後、全 issue を横断した draft requirement / draft design package を `system-architect` evidence として作る workflow を明示する。
  - 各 issue には `new doc draft-requirement` / `new doc draft-design` で issue-local discussion draft を作り、canonical issue docs と区別することを明示する。
  - `iss-00211` が参照できる Epic planning completion / handoff contract を定義する。ただし `iss-00211` は独立 Issue として扱う。
  - provider-side source を正本として更新し、dogfooding mirror の update / targeted inspection / validate / sync のうち design で選んだ検証経路で mirror validation evidence を残す。
- 禁止:
  - `system-architect` が canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を直接編集できるようにすること。
  - Issue 作成前に issue canonical `requirement.md` / `design.md` / `plan.md` を完成させる workflow にすること。
  - Issue 210 の中で Epic execution coordinator、`issue start` / `issue finish` cycle、PR merge-ready preparation を定義・実装すること。
  - Issue 211 を Issue 210 の subtask や completion condition にすること。
  - すべての Epic に heavyweight delegation を無条件強制すること。
  - metadata や dependency を直編集する運用を許可すること。
- 対象外:
  - 新しい `spec-dock-epic-execution` skill の追加。
  - Issue execution workflow、PR delivery / merge preparation workflow の置き換え。
  - runtime enforcement、automated regression harness、CLI gate の実装。
  - discussion draft / delegated authoring template 全体の大規模再設計。

## 境界
- 常に行う:
  - Epic planning の canonical docs は main orchestrator が所有する。
  - Delegated draft は evidence として扱い、採用判断なしに canonical authority としない。
  - Fresh `spec-reviewer` pass なしに requirement -> design、design -> plan、plan -> Issue decomposition / downstream handoff へ進めない。
  - Issue 作成後の draft requirement / draft design は issue-local `discussions/` artifact として置き、canonical issue docs への昇格は個別 Issue planning で行う。
  - Issue dependencies は `.meta.json` 直編集ではなく `spec-dock deps add` を使う。
- 判断が必要:
  - 「非自明な Epic」の詳細な判定例は、skill に最小限の spine として置くか、docs 側に詳細を置くかを design で決める。
  - `workflow_epic.md` / `workflow_spec_authoring.md` / delegated authoring docs のどこまでを今回更新するかは、現行記述との重複と hidden mandatory workflow の有無を見て design で決める。
  - 軽微な Epic で `system-architect` draft cycle を skip する場合の skip reason 記録場所を design で決める。
- 行わない:
  - Issue 211 の execution coordinator の手順を Issue 210 の acceptance に含めない。
  - 既存 docs の全文を skill へコピーして skill を肥大化させない。
  - Templates を compliance authority にしない。
  - Discussion draft を reviewer pass の代替にしない。

## 非交渉制約
- Provider-side installed skill source は `src/spec_dock/assets/install_root/.agents/skills/` を正本とする。
- Dogfooding mirror `.agents/` は検証対象であり、正本ではない。
- Scope-local discussion draft は evidence であり、canonical docs への反映は main orchestrator が行う。
- `review_status: pass` 以外の reviewer state は phase promotion に使えない。
- Issue 210 と Issue 211 は独立 Issue として扱い、Issue 210 は Issue 211 が参照できる contract を定義するだけに留める。

## 前提
- Issue 210 の要件 clarification では Option B を採用済み。
- 採用内容:
  - Epic planning completion / handoff contract を Issue 210 で定義する。
  - Issue 210 と Issue 211 は独立 Issue とする。
  - Issue 211 は Issue 210 の成果を参照してよいが、Issue 210 の実行範囲には含めない。
- 現時点で追加の blocking user interview はない。

## 受け入れ条件
- AC-001: Epic planning draft cycle が first-read surface で読める。
  - アクター: Epic planning を行う main orchestrator。
  - 前提: agent が `spec-dock-epic-planning/SKILL.md` を読む。
  - 操作: 非自明な Epic の design / plan authoring に進もうとする。
  - 期待結果: `system-architect` discussion draft を先に作り、main orchestrator が採用判断を行い、canonical docs 統合後に fresh `spec-reviewer` を通す流れを判断できる。
  - 観測点: provider-side skill diff、必要な docs diff、manual first-read inspection。
- AC-002: delegated draft の authority boundary が明示されている。
  - アクター: main orchestrator / `system-architect`。
  - 前提: Epic-level draft design / draft plan を作成する。
  - 操作: draft を canonical docs へ反映する。
  - 期待結果: draft は scope-local `discussions/` artifact であり、canonical docs を直接編集せず、Evidence Adoption Ledger / diff guard / fresh reviewer gate を通して採用されることが明記されている。
  - 観測点: skill/docs wording、Issue 210 report EAL。
- AC-003: Issue 作成前の Epic planning completion が定義されている。
  - アクター: main orchestrator。
  - 前提: Epic requirement / design / plan を具体化している。
  - 操作: Issue list を作ろうとする。
  - 期待結果: Issue 作成は Epic design / plan の issue slicing policy / dependency analysis の結果として行うべきであり、Epic docs の reviewer gate が未完了なら進めないことが読める。
  - 観測点: skill/docs wording、acceptance inspection。
- AC-004: Issue 作成後の cross-issue draft package が定義されている。
  - アクター: main orchestrator / `system-architect`。
  - 前提: Epic plan から複数 Issue が作成されている。
  - 操作: 個別 Issue planning へ移る前に shared vocabulary / dependency / handoff を整理する。
  - 期待結果: 全 issue を横断した draft requirement / draft design package を discussion evidence として作り、各 issue の `discussions/` に draft requirement / draft design を作る flow が明記されている。
  - 観測点: skill/docs wording、manual inspection。
- AC-005: Issue canonical docs と discussion draft の境界が保たれている。
  - アクター: future issue planner。
  - 前提: issue-local draft requirement / draft design が存在する。
  - 操作: 個別 Issue planning を開始する。
  - 期待結果: issue-local draft は planning input / evidence であり、canonical issue `requirement.md` / `design.md` / `plan.md` は個別 Issue planning workflow で正式化することが明記されている。
  - 観測点: skill/docs wording、Issue 210 requirement/design trace。
- AC-006: Issue 211 との独立境界が明示されている。
  - アクター: Issue 210 / Issue 211 を連続実行する agent。
  - 前提: Issue 210 が完了し、Issue 211 を開始する。
  - 操作: Issue 211 が Epic planning completion / handoff contract を参照する。
  - 期待結果: Issue 211 は Issue 210 の成果を参照できるが、Issue 210 の subtask でも completion condition でもないことが読める。Epic execution coordinator、issue start/finish、PR merge-ready preparation は Issue 211 側の責務として残る。
  - 観測点: Issue 210 docs、Issue 211 reference boundary。
- AC-007: metadata / dependency mutation は command-first である。
  - アクター: main orchestrator。
  - 前提: Issue dependencies を登録する。
  - 操作: dependency edge を追加する。
  - 期待結果: `.meta.json` 直編集ではなく `spec-dock deps add --from <dependent> --to <prerequisite>` を使うことが明記されている。
  - 観測点: skill/docs wording。
- AC-008: Provider source と dogfooding mirror の検証が記録されている。
  - アクター: main orchestrator。
  - 前提: provider-side installed skill / docs に影響する変更を行う。
  - 操作: design で選んだ dogfooding mirror validation route を実行する。
  - 期待結果: provider-side source が正本であること、dogfooding mirror が update / targeted inspection / validate / sync のうち選択した経路で検証されたこと、検証結果が `report.md` に残っていることが確認できる。
  - 観測点: provider-side diff、dogfooding mirror diff or inspection result、`./spec-dock/scripts/spec-dock validate` / `sync` の実行結果または実行しない理由、Issue 210 report evidence。

## 例外・エッジケース
- EC-001: 軽微な Epic。
  - 条件: Epic の design / plan が明らかに単純で、system-architect draft が workflow 負荷に見合わない。
  - 期待: Skip reason を記録して manual authoring へ進める。ただし fresh reviewer gate と canonical single-writer authority は維持する。
  - 観測点: skip reason wording、report evidence guidance。
- EC-002: `system-architect` が利用不可。
  - 条件: delegated role が unavailable / denied / unsupported。
  - 期待: unavailable / denied を記録し、妥当なら manual authoring fallback を使える。ただし delegated draft evidence としては扱わず、reviewer gate は弱めない。
  - 観測点: workflow wording、report evidence guidance。
- EC-003: draft package が requirement gap を発見する。
  - 条件: cross-issue draft package 作成中に Epic requirement / design / plan の不足や矛盾が見つかる。
  - 期待: その不足を個別 Issue execution assumption にせず、Epic planning の該当 phase または clarification へ戻す。
  - 観測点: skill/docs wording。
- EC-004: Issue 211 が handoff contract の不足を発見する。
  - 条件: Issue 211 planning / execution 中に Issue 210 の contract では足りない前提が見つかる。
  - 期待: Issue 211 は独立 Issue として不足を自身の clarification / follow-up / Epic decision routing に載せる。Issue 210 の完了済み範囲へ暗黙に混入しない。
  - 観測点: Issue 210 / Issue 211 boundary wording。

## 入力→出力例
- EX-001: 非自明な Epic planning。
  - 入力: Epic requirement が固まり、design / plan に複数 Issue の責務境界や dependency order が関わる。
  - 出力: `system-architect` draft design / draft plan、main orchestrator の Evidence Adoption Ledger、reviewer-pass 済み canonical Epic design / plan、Issue list / dependencies、cross-issue draft package、issue-local draft requirement/design。
- EX-002: 軽微な Epic planning。
  - 入力: Epic の scope が小さく、delegated design draft の追加価値が低い。
  - 出力: skip reason、manual authoring evidence、fresh reviewer-pass 済み canonical Epic docs。

## 用語
- Epic planning completion:
  - Epic requirement / design / plan が required reviewer gate を通過し、Issue list / dependency order / handoff evidence が downstream から参照できる状態。
- Handoff contract:
  - 後続 Issue や Epic execution coordinator が参照できる planning output の境界。Issue 210 では planning output を定義し、execution coordinator の手順は定義しない。
- Cross-issue draft package:
  - Issue 作成後、全 issue に共通する vocabulary、責務境界、dependency order、handoff outputs / inputs、test / validation strategy、各 issue の draft requirement / draft design を整理する discussion evidence。
- Issue-local draft requirement / draft design:
  - 各 issue の `discussions/` に置く planning input。canonical issue docs ではない。

## 未確定事項
- Blocking question:
  - なし。
- Non-blocking design questions:
  - `system-architect` draft cycle を skill 本文でどこまで詳述し、詳細をどの docs に委譲するか。
  - Skip reason の記録場所を skill 本文、workflow docs、report evidence guidance のどこに置くか。
  - Dogfooding mirror validation の具体経路を update / targeted inspection / validate / sync のどの組み合わせにするか。
