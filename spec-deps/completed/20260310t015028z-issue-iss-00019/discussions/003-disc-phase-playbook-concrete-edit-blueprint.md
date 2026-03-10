---
種別: disc
ID: "003-disc-phase-playbook-concrete-edit-blueprint"
タイトル: "phase playbook 修正の具体設計と見出し変更案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00019"]
関連: ["002-disc-phase-playbook-authoring-workflow-revision"]
---

# 003-disc phase playbook 修正の具体設計と見出し変更案

## 議題 (必須)
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` の冒頭へ、全体 workflow を俯瞰できる新セクションを追加する際の具体的な設計を決める。
- 各文書で、どの見出しを改名し、どこへ何を書くかを実編集可能な粒度で固定する。
- `guide.md`, `docs/README.md`, `workflow_*.md` へどこまで最小波及させるかを決める。

## 背景 (必須)
- 前シート `002-disc-phase-playbook-authoring-workflow-revision` で、必要なのは個別要素の追加ではなく、一本の共通 workflow の明示だと整理した。
- 今回さらに必要なのは、理念ではなく編集設計である。
- ユーザー意図は次の構成にある。
  - 各 phase 文書の最初の方で全体像を俯瞰する
  - その後で詳細な要素の説明へ降りる
  - ヒアリングや調査結果は揮発コンテキストに閉じず、必ず docs に残す
  - その docs を使ってヒアリング・意思決定・本文作成・review loop を進める

## 設計原則 (必須)
- 原則 1:
  - 新しい workflow ファイルは増やさない。
  - `phase_requirement.md`, `phase_design.md`, `phase_plan.md` を共通 authoring 正本として強化する。
- 原則 2:
  - 冒頭で「この phase は全体のどこか」「前段で何が揃っているべきか」「この phase で何を固定するか」「次へどう渡すか」を短く見せる。
- 原則 3:
  - その後で既存の詳細節へ入る。
  - 既存の詳細情報や判断基準はできるだけ残し、配置と見出しだけを整理する。
- 原則 4:
  - `research / disc / note / adr` の既存 doc type を再利用し、新しい doc type は作らない。
- 原則 5:
  - `workflow_*` は scope 固有、`phase_*` は共通作法、`guide.md` と `docs/README.md` は入口、という layering を崩さない。

## 選択肢 (必須)

### Option A: 各 phase 文書の冒頭に `全体 workflow` セクションを新設し、既存節を後ろへずらす
- Pros:
  - 読み始めてすぐ全体像が分かる。
  - ユーザー要望と最も一致する。
  - 既存の詳細節を大きく壊さずに済む。
- Cons:
  - 章番号がずれる。
  - 冒頭が少し長くなる。

### Option B: 冒頭には `この phase の位置づけ` だけ短く置き、全体 workflow は後段へ置く
- Pros:
  - 冒頭を短く保てる。
  - 既存節の移動量が少ない。
- Cons:
  - ユーザーが求める「最初の方で全体像を俯瞰」がやや弱い。
  - workflow の見通しが十分に強くならない。

### Option C: `guide.md` に全体 workflow を集約し、phase 文書は最小限のリンクだけにする
- Pros:
  - phase 文書を短く保てる。
  - 共通説明を 1 箇所へ集約できる。
- Cons:
  - phase 文書単体で読んだときに flow が見えない。
  - 今回の要望である「各ドキュメントの最初の方で全体像を示す」に合わない。

## 推奨案 (必須)
- 推奨は Option A。
- 具体策:
  - 各 `phase_*.md` の導入文と `関連:` の直後に `## 1. <phase> phase の全体 workflow` を新設する。
  - 現行の `目的 / 出力 / 非ゴール` を `## 2.` へ後ろ倒しする。
  - その後ろに、既存の詳細節を改名しつつ再配置する。
- 理由:
  - 「最初に流れを掴む → その後で詳細を読む」という読書順が自然になる。
  - 冒頭で workflow が見えれば、エージェントが individual tips をつなぎ合わせずに動ける。

## 共通の冒頭セクション設計 (必須)

### 新設する冒頭セクション
- 見出し名:
  - `## 1. <phase> phase の全体 workflow`
- この節に共通で入れる内容:
  - この phase が全体のどこにあるか
  - 前段で揃っている前提
  - この phase で固定すること
  - 標準順:
    1. 目的理解
    2. 徹底調査
    3. 調査結果の docs 化
    4. discussion / ADR 準備
    5. ヒアリング
    6. 本文作成
    7. reviewer loop
    8. 次 phase へ handoff
  - stop rule:
    - 情報が揃う前に本文を書かない
    - source のない断定を本文へ入れない
    - 比較表や長い分析は discussion docs へ逃がす
  - scope 固有の entry 条件や品質ゲートは `workflow_*.md` を参照すること

### 冒頭セクションのテンプレ案
```md
## 1. <phase> phase の全体 workflow

この phase は、`requirement -> design -> plan -> execution/review` の流れのうち **<phase>** を扱います。

- 前段で揃っている前提:
  - <承認済み成果物 / active scope / 必要な判断材料>
- この phase で固定すること:
  - <この phase が決める対象>
- この phase の完了条件:
  - reviewer が「<次 phase>へ進めてよい」と判断できること

標準順:
1. 目的理解
2. 徹底調査
3. 調査結果を `research` / `disc` / `note` / `adr` に残す
4. 必要なら discussion/ADR を材料にヒアリングする
5. 情報が揃ってから本文を作成する
6. reviewer コメントを反映し、re-review を回す
7. 本文 + 関連 docs を束で提出し、次 phase へ渡す

注意:
- scope 固有の操作、entry 条件、品質ゲートは `workflow_*.md` を正本とします。
```

## 文書ごとの具体修正案 (必須)

### A. `phase_requirement.md`

#### 推奨する見出し構成
1. `## 1. requirement phase の全体 workflow`
2. `## 2. requirement phase の役割と成果物`
3. `## 3. workflow 開始前の確認`
4. `## 4. 要件を固める調査・分析`
5. `## 5. 調査結果を docs に残すときの使い分け`
6. `## 6. 調査資料ベースのユーザーヒアリング`
7. `## 7. ADR を切る条件`
8. `## 8. template で先に埋める節`
9. `## 9. reviewer に渡す前の exit criteria`
10. `## 10. 提出 / 承認 / 次 phase へ進める条件`
11. `## 11. subagent 活用ガイダンス`
12. `## 12. 迷ったときの判断順`

#### 改名・移動の意図
- 現行 `目的 / 出力 / 非ゴール` は良いので残す。ただし位置を後ろへずらし、役割・成果物として読みやすくする。
- 現行 `調査・分析の進め方` は、本文に入れる前に docs に残す手順まで含めて強化する。
- 現行 `discussion sheet を作る条件` は、単なる条件列挙ではなく `docs に残すときの使い分け` に昇格させる。
- 現行 `ユーザーヒアリングの進め方` は、discussion 資料を前提に行うことを見出し名で明示する。

#### この文書で特に強調すべきこと
- WHAT / WHY を決める文書であること
- 主要事実は `research` や `disc` に根拠付きで残してから requirement 本文へ昇格させること
- 解法比較は本文へ押し込まず `disc` に置くこと
- reviewer へは `requirement.md + 関連 discussions + unresolved list` を束で渡すこと

### B. `phase_design.md`

#### 推奨する見出し構成
1. `## 1. design phase の全体 workflow`
2. `## 2. design phase の役割と成果物`
3. `## 3. workflow 開始前の確認`
4. `## 4. 既存理解と差分設計の進め方`
5. `## 5. 調査結果・比較結果を docs に残すときの使い分け`
6. `## 6. 調査資料ベースのユーザーヒアリング`
7. `## 7. ADR を切る条件`
8. `## 8. template で先に固める節`
9. `## 9. reviewer に渡す前の exit criteria`
10. `## 10. 提出 / 承認 / 次 phase へ進める条件`
11. `## 11. subagent 活用ガイダンス`
12. `## 12. 迷ったときの判断順`

#### 改名・移動の意図
- 現行の `既存を 99.9% 理解してから差分を設計する` という強い原則は残す。
- そのうえで、既存実装調査・比較表・非採用案を本文へ押し込まず discussion / ADR へ分離する流れを強める。
- `template のどこを埋めるか` は、どの順で差分を固めるかが分かる名前に近づける。

#### この文書で特に強調すべきこと
- HOW / Guardrails を決める文書であること
- requirement の不足を design 本文でごまかさないこと
- 境界・契約・データ・移行・観測性・テスト戦略の順で理解を深めること
- reviewer へは `design.md + 関連 research/disc/adr` を束で渡すこと

### C. `phase_plan.md`

#### 推奨する見出し構成
1. `## 1. plan phase の全体 workflow`
2. `## 2. plan phase の役割と成果物`
3. `## 3. workflow 開始前の確認`
4. `## 4. 分解・順序付けの進め方`
5. `## 5. 分割案・順序案を docs に残すときの使い分け`
6. `## 6. 調査資料ベースのユーザーヒアリング`
7. `## 7. ADR を切る条件`
8. `## 8. template で先に固める節`
9. `## 9. reviewer に渡す前の exit criteria`
10. `## 10. 実行へ進める条件`
11. `## 11. subagent 活用ガイダンス`
12. `## 12. 迷ったときの判断順`

#### 改名・移動の意図
- plan では、調査そのものより分解・順序・停止点・品質ゲートの整理が主になる。
- そのため、`調査・分析の進め方` は `分解・順序付けの進め方` へ改名するのが自然である。
- `次 phase へ進める条件` は、plan では次が execution なので `実行へ進める条件` と明示する。

#### この文書で特に強調すべきこと
- requirement / design 承認済みが前提であること
- 分割案や順序案の比較は必要なら `disc` に逃がすこと
- Issue plan では `review / docs impact / final quality gate` を必ず可視化すること
- reviewer へは `plan.md + 関連 discussions + 実行前の blocking 論点一覧` を束で渡すこと

## 周辺 docs への最小導線案 (必須)

### `guide.md`
- 追加する内容:
  - `phase_*.md は requirement/design/plan の共通作法であり、各文書の冒頭に phase 全体 workflow がある`
- 追加位置:
  - `## 0. phase playbook` の末尾が自然

### `docs/README.md`
- 追加する内容:
  - `phase を書くときは、まず対象 scope の workflow を確認し、その後に phase playbook 冒頭の workflow に沿って進める`
- 追加位置:
  - `## phase 別の共通作法` の補足ブロック

### `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md`
- 追加する内容:
  - `この workflow では scope 固有の判断と操作を扱います。requirement/design/plan の作り方自体は phase playbook を参照してください。`
- 追加位置:
  - `## 2. 記述` の補足 bullet が自然

## 書かない方がよいこと (必須)
- `phase_*.md` に `new/import/active set` のコマンド手順を再掲しない
- `phase_*.md` に scope 固有品質ゲートを長文で複製しない
- `workflow_*.md` にヒアリング手順や discussion sheet 条件を全文転記しない
- `guide.md` / `docs/README.md` に phase の詳細を要約しすぎない
- 新しい `interview` doc type や `workflow_authoring.md` のような新規正本を増やさない

## 客観レビューと壁打ちの要約 (必須)
- 客観レビューでは、共通して次が支持された。
  - 冒頭に `この phase は全体のどこか` を置くと迷いにくい
  - 全体 workflow は、各 phase 文書の最初の方で見せるのが最も自然
  - 既存 3 文書の詳細情報はかなり揃っているため、全交換ではなく冒頭追加と見出し整理で十分
  - 周辺 docs は導線だけ持てばよく、詳細の複製は不要

## 次アクション (必須)
- この設計をベースに、次は `phase_requirement.md`, `phase_design.md`, `phase_plan.md` の実際の文言差し替え案を作る。
- 実編集では、まず 3 文書の冒頭 workflow を揃え、その後に周辺 docs の導線を最小修正する。
