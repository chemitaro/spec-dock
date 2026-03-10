---
種別: disc
ID: "002-disc-phase-playbook-authoring-workflow-revision"
タイトル: "phase playbook に共通の authoring workflow を明示する修正案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00019"]
関連: []
---

# 002-disc phase playbook に共通の authoring workflow を明示する修正案

## 議題 (必須)
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` に、本文執筆の前後を含む共通 workflow を明示する。
- 特に、`目的理解 → 徹底調査 → 調査記録化 → discussion/ADR 準備 → ヒアリング → 本文作成 → reviewer loop → 提出` を、迷わず辿れる標準順として固定する。
- 既存 docs 構造を大きく壊さず、最小の波及でこの workflow を導入する。

## 背景 (必須)
- 現行の 3 文書には、調査、ヒアリング、discussion/ADR、reviewer、exit criteria といった要素はすでに入っている。
- ただし、各要素が「作法」として点在しており、phase 文書作成の全体像として一本の工程線になっていない。
- その結果、エージェントが「いつ本文を書き始めるべきか」「調査結果をどこに残すべきか」「ヒアリング前に何を用意すべきか」「reviewer 指摘後にどう戻るか」を迷いやすい。
- ユーザー意図は、要件定義書・設計書・実装計画書のいずれでも、曖昧な推測ではなく完全な理解に基づいて本文を書く流れを明文化することにある。

## 現状の不足 (必須)

### 1. 共通の canonical sequence がない
- 現行 3 文書とも phase 単体の注意点はあるが、入口から提出までの標準順が明示されていない。
- 特に次の順が弱い。
  - 目的理解
  - 徹底調査
  - 調査結果の docs への退避
  - discussion/ADR の準備
  - その資料を使ったヒアリング
  - 本文作成
  - reviewer コメント反映と再レビュー
  - 提出

### 2. 「本文を書く前に調査を docs に残す」が gate になっていない
- 現行文書では `research` / `disc` / `note` / `adr` は optional output として見えやすい。
- しかし今回必要なのは optional ではなく、主要事実・比較・未確定論点を本文に入れる前に discussion 系 docs に残すという標準手順である。

### 3. ヒアリング前の資料準備が弱い
- 現行文書にもヒアリング条件はあるが、ヒアリング前に必ず discussion sheet または結論未記入 ADR を用意する、という運用ルールが明示されていない。
- そのため、何を確認したいのか、どの選択肢があり、何を推奨するのかを整理しないまま質問へ進みやすい。

### 4. reviewer loop が phase playbook に弱い
- `reviewer 承認前に次 phase へ進めない` という gate はある。
- ただし、`submit → feedback → fix → re-review → pass → 提出` の反復自体は Issue workflow 側の色が強く、phase 文書作成フローとしては見えにくい。

### 5. 提出単位が曖昧
- 本文単体を出すのか、関連 `research` / `disc` / `adr` / unresolved list まで含めて出すのかが、明文化されていない。
- 次 phase へ渡す入力束が曖昧なため、handoff 品質がぶれやすい。

### 6. 過剰化を防ぐ圧縮ルールが弱い
- 本文と discussion docs の責務分離は思想としてあるが、「どの時点で本文から別紙へ逃がすか」の基準が弱い。
- これにより、本文へ比較表や調査ログを押し込みやすい。

## 選択肢 (必須)

### Option A: 現行 3 文書に小さな注意書きだけを追加する
- Pros:
  - 差分が最小。
  - 既存構成をほぼ変えない。
- Cons:
  - ユーザーが求める「はっきり分かる workflow」になりにくい。
  - 工程全体の順序が依然として弱い。
  - 目的理解、調査記録化、ヒアリング資料準備、reviewer loop がばらけたまま残る。

### Option B: 既存 3 文書に共通 authoring workflow を明示し、各 phase の違いだけを書き分ける
- Pros:
  - 既存 layering を壊さず、ユーザー要求の workflow をそのまま載せられる。
  - 各 phase の共通部分と差分が分かりやすい。
  - `research / disc / note / adr` の既存 doc type をそのまま再利用できる。
  - reviewer loop と提出単位を 3 文書すべてで揃えられる。
- Cons:
  - 3 文書が少し長くなる。
  - guide / README / workflow_* に最小限の追記が必要になる。

### Option C: phase とは別に新しい workflow 専用文書を追加し、3 文書から参照する
- Pros:
  - 共通手順を 1 箇所に集約できる。
  - 3 文書自体は短く保てる。
- Cons:
  - 新しい正本が増え、導線が 1 つ増える。
  - 既存 `guide` / `workflow_*` / `phase_*` の layering が少し複雑になる。
  - 今回は「既存文書を修正して明示する」が主眼なので、導入コストの割に過剰。

## 推奨案 (必須)
- 推奨は Option B。
- 理由:
  - 既存の `phase_requirement.md`, `phase_design.md`, `phase_plan.md` を共通 authoring 正本として強化するのが最も自然である。
  - 新しい doc type や新しい workflow ファイルを増やさずに済む。
  - `research = 徹底調査`, `disc = 論点整理/ヒアリング前整理`, `note = 軽量メモ`, `adr = 長く効く意思決定` という既存の役割分担をそのまま活用できる。
  - guide / workflow_* には詳細を複製せず、「この共通ループに従う」と短く案内するだけで済む。

## こう直すべき workflow 骨子 (必須)
- 共通 workflow は、3 文書すべてで次の順序を明記する。
  1. 目的理解
  2. 調査計画
  3. 徹底調査
  4. 調査結果の docs 化
  5. discussion/ADR 準備
  6. ヒアリング
  7. 本文作成
  8. reviewer loop
  9. 提出 / 次 phase への handoff
- stop rule も併記する。
  - 情報が揃う前に本文を書き始めない。
  - source を示せない断定は本文に入れない。
  - 2 案以上の比較は本文ではなく `disc` に逃がす。
  - 長く効く決定だけを `adr` に昇格させる。

## discussion sheet の必須要素 (必須)
- ヒアリングや意思決定依頼に使う sheet には、最低限次を入れる。
  - 今回決めたいこと / 聞きたいこと
  - 対象 phase / 対象本文節
  - 確定した事実
  - 未確定事項 / 仮説
  - 選択肢と比較
  - 推奨案
  - ヒアリング質問
  - 決定者 / 期待する返答
  - 決定後の反映先
- つまり、ユーザーへ判断を求めるときは「背景」「分析」「選択肢」「推奨案」まで先に用意する。

## 具体的な修正方針 (必須)

### A. `phase_requirement.md`
- 追加/改名の方向:
  - `着手前に確認すること` に `目的理解で最初に固定すること` を追加する。
  - `調査・分析の進め方` を、調査結果を docs に残す手順まで含む名称に改める。
  - `research / disc / note に先に残し、requirement 本文へ昇格させる条件` を明記する。
  - `ユーザーヒアリングの進め方` を、調査資料ベースで行うことが分かる見出しに改める。
  - `template のどこを埋めるか` を `どの順で埋めるか` まで明記する。
  - exit criteria に `reviewer コメント反映 → re-review → 提出可` を足す。
- phase 固有の強調点:
  - WHAT / WHY に留まる。
  - 解法比較は本文へ押し込まず `disc` へ逃がす。

### B. `phase_design.md`
- 追加/改名の方向:
  - requirement と同じ共通 workflow 骨格を採る。
  - 既存実装調査・比較結果を本文に昇格させる条件を明記する。
  - reviewer へ渡す単位を `design.md + 関連 research/disc/adr` として明記する。
- phase 固有の強調点:
  - HOW / Guardrails に集中する。
  - 採用案と非採用案の比較は必要な分だけ本文へ要約し、長い比較は discussion へ出す。

### C. `phase_plan.md`
- 追加/改名の方向:
  - `計画化前に固定する判断材料` を明記する。
  - 分解案や順序案は、必要なら先に `disc` で比較してから plan に落とすと書く。
  - reviewer review loop と提出単位を明記する。
  - `承認後は実行へ進む` をより強く出す。
- phase 固有の強調点:
  - 実行順と停止点を書く。
  - requirement/design の再議論を持ち込まない。

## 周辺 docs への最小波及 (必須)
- `guide.md`:
  - `phase playbook の共通ループ` を 1 節だけ短く追加する。
- `docs/README.md`:
  - 入口で「phase はこの順で進める」と 1 行補足する。
- `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md`:
  - 詳細の複製は避け、`phase playbook の共通ループに従う` と 1〜2 bullet 足す程度に留める。
- `workflow_adr.md`:
  - 原則そのままでよい。必要なら `disc` から `adr` に昇格する条件を 1 行補足する程度。

## 圧縮ルール (必須)
- 本文には `結論・制約・未決` を残し、調査ログや比較表は discussion 系 docs へ出す。
- 2 案以上の比較になった時点で `disc` に分離する。
- source を示せない内容は本文で断定しない。
- requirement は HOW を書かない。
- design は実行順の細部を書かない。
- plan は判断理由の再論を長く書かない。
- reviewer が `進めてよい / 止めるべき` を判断できる最小情報量で止める。

## 客観レビューの要約 (必須)
- 客観レビューでも、共通して次の結論になった。
  - 不足しているのは個別要素ではなく、一本の標準順である。
  - 新しい doc type は増やさなくてよい。
  - 新しい workflow ファイルを増やすより、既存 3 文書を共通 authoring 正本として厚くするほうが自然である。
  - `guide.md` と `workflow_*` は導線だけを持てばよい。

## 未決事項 (任意)
- 3 文書すべてで同じ章番号構成へ揃えるか、既存見出しを活かしたまま最小差分で追記するかは、実編集時に読みやすさ優先で最終判断する。
- `disc` template 自体に `ヒアリング質問` や `決定者` の欄を足すかは follow-up に分けてもよい。

## 次アクション (必須)
- この提案をベースに、まず `phase_requirement.md`, `phase_design.md`, `phase_plan.md` の修正文案を作る。
- その際、3 文書に共通 workflow を明示しつつ、phase ごとの差分だけを書き分ける。
- つづいて `guide.md`, `docs/README.md`, `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md` に最小限の導線追記を行う。
