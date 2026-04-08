# delegated workflow manual test 後の skill 修正ベストプラクティス分析

日時: 2026-04-07
対象: `iss-00051`
目的: 手動テストで確認された delegated workflow completion gap を、どの skill / docs にどの強さで反映するべきかを整理し、具体的な修正文言案まで落とし込む。

## 背景
- 2026-04-07 の real manual test では、install/static と fail-closed guard は通った。
- しかし local delegated-runtime は、initiative / epic / issue 作成と active set までは進んだ一方、`spec-dock/active/issue/requirement.md` / `design.md` / `plan.md` / `report.md` がテンプレートのまま残り、completion-quality を満たさなかった。
- current GitHub delegated-runtime でも docs 読み取り後に work item 生成や docs 充填まで進まず、completion gate を越えられなかった。
- したがって問題は shim install や static delegation ではなく、`shim -> adapter -> issue execution` の completion contract が delegated runtime を最後まで拘束できていないことにある。

参照:
- `manual-tests/reports/2026-04-07-iss-00051-completion-guard-real-manual/summary.md`
- `manual-tests/reports/2026-04-07-iss-00051-completion-guard-real-manual/execution-log.md`
- `20260406t190500z-disc-delegated-workflow-gap-analysis-and-best-practice.md`
- `20260406t195500z-disc-concrete-wording-proposals-for-completion-guard.md`

## consultant 論点整理

### consultant A の見解
- 推奨は `二層`。
- adapter には最小限の fail-closed completion guard だけを置く。
- issue-execution には completion loop と blocked ルールを置く。
- adapter を重くして phase 順や closure schema を持たせるのは非推奨。
- `workflow_issue.md` は最も厳密な正本のまま維持し、skills はその要約だけを持つのがよい。

### consultant B の見解
- 現行 adapter には docs 4 点ガードはあるが、`report.md` に `sync` / `validate` / review の証跡または未実施理由が必要だという最小 guard が不足している。
- `issue-00049` のような過去 issue を規範参照に使うのは保守上弱い。規範参照は `workflow_issue.md` に寄せるべき。
- `real issue data` / `templated` / `effectively blank` という wording は direction はよいが主観寄りなので、厳密な意味は workflow quality gate 側に置き、skill 側は短くすべき。
- Codex/Copilot adapter は意味的に同一文言を維持し、差分は host 導入文だけにするべき。

## 比較した修正候補

### 候補 A: adapter 強化のみ
- 内容:
  - `.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  だけを強化する。
- 利点:
  - 変更量が最小。
  - false complete を減らす即効性がある。
- 欠点:
  - leaf workflow 側が曖昧なまま残る。
  - adapter を経由しない経路や route 後の早期停止を根治できない。

### 候補 B: issue-execution 強化のみ
- 内容:
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `spec-dock/docs/workflow_issue.md`
  だけを強化する。
- 利点:
  - 責務分離は最もきれい。
- 欠点:
  - ingress 側で「route したら勝ち」の挙動が残りやすい。
  - host-native delegated flow の guard が弱いまま。

### 候補 C: 二層強化
- 内容:
  - adapter に minimum completion guard
  - issue-execution に completion loop / blocked contract
  - `workflow_issue.md` を厳密正本として維持
- 利点:
  - false complete を入口と実行の両方で防げる。
  - host 間 parity を保ちやすい。
  - manual test でも pass/fail の切り分けがしやすい。
- 欠点:
  - A/B より少し修正箇所が増える。

### 候補 D: adapter を厚くする
- 内容:
  - adapter 側に phase 順、closure schema、詳細 workflow を持たせる。
- 利点:
  - host-native entrypoint 側だけで振る舞いを強く固定できる。
- 欠点:
  - shim / adapter が厚くなりすぎる。
  - Codex/Copilot drift を起こしやすい。
  - `workflow_issue.md` の複製になる。

## 結論
推奨は **候補 C: 二層強化**。

### 理由
- adapter は `route-only / active-set-only では完了不可` を伝える薄い guard を持つべき。
- issue-execution は `docs 4 点 + report evidence` が満たされるまで進み、満たせない場合は `blocked` / `incomplete` として止まり、どちらも `report.md` に reason と next action を残す明示ルールを持つべき。
- `workflow_issue.md` は quality gate の厳密な正本であるべき。
- これにより、shim を厚くせずに delegated workflow の completion contract を閉じられる。

## ベストプラクティス

### 1. adapter は最小 guard のみ
adapter に書くべきことは以下に限定する。
- active issue が set されること
- docs 4 点が issue-specific content で埋まるまで complete と報告しないこと
- route-only / active-set-only progress で止まらないこと
- `sync` / `validate` / review を完了できないなら、`report.md` に reason と next action を残し `blocked` または `incomplete` と報告すること

adapter には phase 順、closure schema、review cadence は持たせない。

### 2. issue-execution は completion loop を持つ
issue-execution には以下を明示する。
- `workflow_issue.md` を detailed source of truth として扱うこと
- issue execution は active issue が set / confirmed され、docs 4 点が issue-specific で、`report.md` に successful/pass な required `sync` / `validate` と required review approval/pass の証跡が残るまで complete ではないこと。required step が未実施または unsuccessful の場合は `complete` 不可とし、`blocked` または `incomplete` として `reason` と `next action` を残すこと
- `blocked` と `incomplete` を分けること
  - `blocked`: environment / dependency constraints
  - `incomplete`: workflow progress 未充足
- `blocked` / `incomplete` のどちらでも reason と next action を `report.md` に残すこと
- `blocked` では blocker type / impact も該当する範囲で `report.md` に残すこと

### 3. workflow docs が最も厳密な正本
`spec-dock/docs/workflow_issue.md` には skill より厳密な quality gate を維持する。
詳細な定義はここに置き、skill は要約だけにする。

### 4. host parity を維持する
Codex/Copilot adapter の completion clause は意味的に同一に保つ。差分は host の導入文だけにする。

### 5. wording は観測可能な動詞で書く
推奨動詞:
- `set`
- `populate`
- `record`
- `classify`

避ける表現:
- `properly`
- `sufficiently`
- `real`（厳密な定義なしに使う）

## 具体的な修正文言案

> 注記: この節の初期候補には、required step の未実施理由だけで `complete` を許す旧案が含まれていた。以下は 2026-04-07 latest review follow-up を反映した**最終候補のみ**であり、旧 wording 候補は再利用しない。

### 1. `src/spec_dock/assets/codex_skills/spec-dock-codex-adapter/SKILL.md`

```md
- For issue work, do not report completion until the active issue is set and confirmed, `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md` contain issue-specific content, and `spec-dock/active/issue/report.md` records successful required `sync` / `validate` outcomes and required review approval or pass outcomes.
- Do not stop at route-only or active-set-only progress. If any required step is skipped, or executed without a successful, pass, or approved outcome, report the status as `blocked` or `incomplete`, record the reason and next action in `spec-dock/active/issue/report.md`, and do not report `complete`.
```

### 2. `src/spec_dock/assets/codex_skills/spec-dock-copilot-adapter/SKILL.md`
Codex adapter と同一の completion clause を採用する。

```md
- For issue work, do not report completion until the active issue is set and confirmed, `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md` contain issue-specific content, and `spec-dock/active/issue/report.md` records successful required `sync` / `validate` outcomes and required review approval or pass outcomes.
- Do not stop at route-only or active-set-only progress. If any required step is skipped, or executed without a successful, pass, or approved outcome, report the status as `blocked` or `incomplete`, record the reason and next action in `spec-dock/active/issue/report.md`, and do not report `complete`.
```

### 3. `src/spec_dock/assets/codex_skills/spec-dock-issue-execution/SKILL.md`

```md
- Treat `spec-dock/docs/workflow_issue.md` as the source of truth for detailed step order and quality gates.
- An issue execution run is not complete unless the active issue is set and confirmed, `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md` are issue-specific, and `spec-dock/active/issue/report.md` records successful required `sync` / `validate` outcomes and required review approval or pass outcomes.
- If any required step is skipped, or executed without a successful, pass, or approved outcome, classify the result as `blocked` or `incomplete`, record the reason and next action in `spec-dock/active/issue/report.md`, and do not report `complete`.
- Use `blocked` for environment or dependency constraints and `incomplete` for unfinished workflow progress or product gaps.
```

### 4. `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`

```md
- `complete` と報告してよいのは、active issue が set / confirmed され、`spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, `report.md` が issue-specific content を持ち、`report.md` に successful/pass な required `sync` / `validate` と required review approval/pass の証跡が残っている場合のみとする。
- required step が未実施、または実施済みでも successful / pass / approved outcome に到達していない場合は `complete` 不可とし、`blocked` または `incomplete` に分類して `report.md` に reason と next action を残す。
- `blocked` は environment / dependency / external constraint に使い、`incomplete` は workflow progress 未完了または product gap に使う。
```

## 今回は直さない方がよいもの
- `.codex/agents/spec-dock.toml`
- `.github/agents/spec-dock.agent.md`
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md`

これらは薄い route/discovery のまま維持する。必要があっても hub には 1 行だけにとどめる。

## 最小検証方針
manual test を再実施する際の pass 条件は次の二択で十分。

- `PASS`
  - docs 4 点が populated され、`report.md` に evidence がある
- `PASS (blocked/incomplete but correctly classified)`
  - docs 4 点未充足でも、`blocked` または `incomplete` と返し、reason と next action が `report.md` に残る
- `FAIL`
  - docs 4 点未充足なのに `complete` と報告する
  - または `blocked` / `incomplete` なのに reason と next action を残さず終了する

## 補足
この修正は shim を太らせるものではなく、delegated workflow の完了条件を skills / workflow docs に正しく再配置するためのもの。

## 2026-04-07 latest review follow-up
- superseded wording candidates:
  - any wording that allows `complete` when a required step is skipped as long as the reason is recorded
  - any wording that treats raw `sync` / `validate` / review command evidence as sufficient without showing a successful, pass, or approved outcome
  - the earlier wording blocks in `具体的な修正文言案` should not be reused as-is where they rely on command evidence alone
- final rule:
  - `complete` requires the active issue to be set and confirmed, issue-specific content in `spec-dock/active/issue/requirement.md`, `design.md`, `plan.md`, and `report.md`, and command evidence in `spec-dock/active/issue/report.md` showing successful required `sync` / `validate` outcomes and required review approval or pass outcomes.
  - if any required step is skipped, or executed without a successful, pass, or approved outcome, recording the reason does not permit `complete`; classify the status as `blocked` or `incomplete` and record the reason plus next action in `spec-dock/active/issue/report.md`.
  - adapter wording should summarize the same rule without adding workflow detail, and should refer to successful required `sync` / `validate` outcomes plus required review approval or pass outcomes so the host adapter summary stays aligned with `workflow_issue.md`.
  - Codex/Copilot adapter completion bullets should remain byte-for-byte identical except for the host intro line.
