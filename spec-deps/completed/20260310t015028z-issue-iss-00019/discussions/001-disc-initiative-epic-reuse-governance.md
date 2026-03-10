---
種別: disc
ID: "001-disc-initiative-epic-reuse-governance"
タイトル: "initiative/epic の既存再利用優先ルールを docs/skills へ反映する修正案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-09"
親: ["iss-00019"]
関連: []
---

# 001-disc initiative/epic の既存再利用優先ルールを docs/skills へ反映する修正案

## 議題 (必須)
- `spec-dock` の docs / skills に、`initiative` / `epic` は既存ノードの再利用を優先し、適合しない場合のみ新規作成する運用ルールを明示する。
- その理由は issue discussion に残し、後続の docs 更新判断と reviewer 合意の根拠にする。

## 背景 (必須)
- 現状の入口 docs と workflow docs は `new initiative` / `new epic` を直接案内しており、作成前に既存ノードへ収まるかを確認する手順がない。
- skill も `create/import` を典型ユースケースとして案内しているため、エージェントが新規作成を先に選びやすい。
- 一方で、`phase_design.md` には「既存パターンがあるなら、まずそれに乗れるかを検討する」という一般原則があり、思想自体は repo と矛盾しない。
- ユーザー意図は、ノード増殖の抑制と、判断理由を requirement に混ぜず discussion に切り出すことにある。

## 観測した不足 (必須)
- 入口レイヤ:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - 不足: `new/import` の前に「既存 initiative/epic を確認する」原則がない。
- workflow レイヤ:
  - `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - 不足: `新規作成前の再利用判定` 節がなく、品質ゲートにも再利用判断が入っていない。
- playbook レイヤ:
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - 不足: decomposition の際に「既存 epic / issue へ収まるかを先に見る」ガードがない。
- skill レイヤ:
  - `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md`
  - 不足: 「create/import をデフォルトにしない」「まず既存ノードを確認する」がない。

## consultant 観点の推奨（客観レビュー要約） (必須)

### 1. 文書レイヤごとの責務
- 入口 docs (`README.md`, `guide.md`):
  - ここには運用原則を短く置く。
  - 推奨: `initiative/epic は増やす前に既存ノードへの収まり先を確認する` を 2〜4 行で明示する。
  - 理由: 最初に読む層で方向を固定しないと、後段 workflow の細則が読まれない。
- workflow docs (`workflow_initiative.md`, `workflow_epic.md`):
  - ここには判断手順と新規作成条件を書く。
  - 推奨: `0. 新規作成前の再利用判定` を新設し、チェックリストと許容条件を置く。
  - 理由: 実務で参照されるのはここであり、具体的な分岐が必要。
- playbook (`phase_plan.md`):
  - ここには分解時のガードを書く。
  - 推奨: `大きすぎるから新規 epic を増やす` の前に `既存 epic の plan / DoD / 依存に収まるか確認する` を足す。
  - 理由: ノード増殖は plan phase で起きやすい。
- skills:
  - ここには短い reminder だけ置く。
  - 推奨: `Do not default to create/import; inspect existing initiative/epic first.` 相当の短文を追加する。
  - 理由: 詳細は docs 正本、skills は行動の初速だけ矯正すればよい。

### 2. 再利用判定の最小チェックリスト
- initiative 再利用判定:
  - 目的が既存 initiative と同じ投資単位か。
  - 成功条件が既存 initiative の success metrics に自然に入るか。
  - スコープが既存 initiative の境界を壊さず追加できるか。
  - 依存関係や意思決定者が既存 initiative と大きく衝突しないか。
- epic 再利用判定:
  - 変更の背骨が既存 epic の契約 / 移行 / 観測性に収まるか。
  - Done 定義を壊さず、issue 分解で表現できるか。
  - rollout 順や依存順が既存 epic の plan と矛盾しないか。
  - 単に issue を増やせば足りる話を、新しい epic に逃がしていないか。

### 3. 新規作成を許容する条件
- 新規 initiative を許容:
  - 投資判断の単位が別である。
  - success metrics が別である。
  - スコープ境界や責任主体が別で、同じ initiative に入れると判断軸が崩れる。
- 新規 epic を許容:
  - 契約 / 移行 / 観測性の背骨が別である。
  - 同じ epic に入れると Done 定義が曖昧になる。
  - rollout 順序や依存関係が別管理でないと plan が破綻する。

### 4. 最初の disc に残す妥当性
- 推奨: 「なぜ既存を再利用しなかったか」「どこで境界を切ったか」は、作成後の対象ノード配下 `discussions/` の最初の `disc` に残す。
- 理由:
  - requirement は WHAT / WHY を固定する文書であり、比較検討の途中経緯を混ぜると冗長になる。
  - 再利用可否の比較、既存ノードとの境界判断、選択肢比較は discussion の責務に合う。
  - docs 更新時の rationale と reviewer 合意を参照しやすい。

## 具体的な修正案 (必須)

### A. `src/spec_dock/assets/spec_dock/docs/README.md`
- 追加位置:
  - `コマンド早見` の前、または `重要な注意` に 1 ブロック追加
- 追加内容案:
  - `initiative / epic を作る前に、既存ツリーと active node を確認し、既存ノードへ収まるなら更新・再利用を優先する。`
  - `新規作成は、目的・成功条件・スコープ・契約境界が既存ノードに収まらない場合だけ行う。`

### B. `src/spec_dock/assets/spec_dock/docs/guide.md`
- 追加位置:
  - `4.1 作る（new / import）` の冒頭
- 追加内容案:
  - `new/import は新規作成コマンドであり、作成判断そのものを正当化するものではない。`
  - `initiative / epic は、まず既存ノードの requirement / design / plan を確認し、適合するなら既存を使う。`

### C. `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`
- 追加内容案:
  - `## 0. 新規作成前の再利用判定`
  - `既存 initiative の requirement / design / plan / discussions を確認する`
  - `目的・成功条件・スコープ・責任主体が一致するなら既存 initiative を更新する`
  - `一致しない場合だけ new/import を使う`
- 品質ゲート追加案:
  - `この initiative を新規作成する理由が 1〜3 行で説明できる`

### D. `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
- 追加内容案:
  - `## 0. 新規作成前の再利用判定`
  - `親 initiative 配下の既存 epic の requirement / design / plan を確認する`
  - `契約・移行・観測性・Done 定義が既存 epic に収まるなら既存 epic を更新する`
  - `収まらない場合だけ new/import を使う`
- 品質ゲート追加案:
  - `この epic を分ける理由と、既存 epic に収めない理由が説明できる`

### E. `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
- 追加内容案:
  - `分解時は、新しい epic / issue を増やす前に既存 plan の粒度・DoD・依存順へ収まるかを確認する`
  - `新規ノードを増やす場合は、作成後の対象ノード配下の最初の disc に既存へ収めない理由を残す`

### F. skill files
- 対象:
  - `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/codex_skills/spec-dock-epic-planning/SKILL.md`
- 追加内容案:
  - `Do not default to create/import; inspect existing initiative/epic first.`
  - `If an existing node fits, update/reuse it and record the boundary rationale in discussions.`

## 推奨文言の最小形 (任意)
```md
- 原則: initiative / epic は新規作成より既存再利用を優先する。
- 新規作成前に、目的・成功条件・スコープ・契約境界・依存関係・既存 plan への収まりを確認する。
- 既存ノードに収めると判断軸や Done 定義が壊れる場合に限り、新規作成してよい。
- 新規作成した理由は、作成後の対象ノード配下 `discussions/` の最初の `disc` に残す。
```

## 推奨する記録運用 (必須)
- requirement:
  - 新しいノードの WHAT / WHY / scope のみを書く。
- discussion:
  - 既存ノード候補
  - 再利用可否の比較
  - 新規作成を選んだ理由
  - docs / skills に反映すべき運用ルール
- 理由:
  - requirement を比較検討ログで肥大化させず、判断根拠を別紙で追える。

## 結論 (必須)
- ベストプラクティスは、`入口 docs で原則を短く宣言し、workflow で再利用判定を具体化し、skills で短く強制する` 構成である。
- 既存ノードを使わない理由は、作成後の対象ノード配下 `discussions/` の最初の `disc` に残す運用が適切である。
- 実際の修正は、`README.md` / `guide.md` / `workflow_initiative.md` / `workflow_epic.md` / `phase_plan.md` / 3つの skill を最小セットとして進めるのがよい。

## 次アクション (必須)
- この discussion を根拠に、docs / skills の実ファイル修正へ進む。
- 修正時は、discussion の結論を各文書レイヤの責務に応じて短く分配し、同じルールを重複・競合させない。
