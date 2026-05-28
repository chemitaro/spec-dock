---
kind: interview
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T02:01:35Z
created_by: codex
status: answered
authority: user-approved
derived_from:
  - 20260528t005900z-research-chatgpt-mattpocock-integration-patterns.md
  - 20260528t010000z-disc-adopt-mattpocock-grill-patterns.md
  - 20260528t011700z-research-spec-dock-requirement-grill-skill-design.md
reflected_to:
  - requirement.md
---

# インタビュー記録: grill workflow のスコープと成果物

## 位置づけ

この文書は `iss-00134` の要件定義前インタビューを記録する。
この文書自体は canonical ではなく、`requirement.md`、`design.md`、`plan.md` に明示的に反映されるまでは evidence / proposed record として扱う。

このインタビューは、Matt Pocock `grill-with-docs` の考え方を spec-dock 向けに変形して進める。

- 質問する前に、既存の local docs / research / source snapshot を読む。
- 一度に一つだけ質問する。
- 質問、ユーザー回答、Codex 分析を issue-local evidence として記録する。
- discussion record を、そのまま accepted requirement として扱わない。
- 作成する discussion / research / interview 文書の本文は日本語で書く。

## 事前に確認した文脈

これまでの分析では、次の方向性が示されている。

- `grill-me` / `grill-with-docs` をそのまま直接 import するのは、最初の要件としては適切ではない。
- 有用な本質は、docs-aware で、一問ずつ確認する clarification workflow である。
- spec-dock では root `CONTEXT.md` を新しい正本にしない方がよい。
- spec-dock で優先する context source は、active scope docs、parent docs、`discussions/`、generated state、関連 source/tests/templates になりそうである。
- workflow は skill、template、CLI などに発展しうるが、まずは振る舞いと evidence contract を定義する必要がある。

## Q-001: 導入したい surface

### 質問

この Matt Pocock-style capability は、次のどの surface として導入したいか。

- A. requirement / design / plan docs を作るために、ユーザーへ一問ずつ質問する壁打ちワークフロー。
- B. 再利用可能な skill / agent surface。
- C. 質問回答記録、template、場合によっては `issue clarify` のような CLI を含む正式な product feature。

まずどの surface を意図しているか。

### ユーザー回答

三つすべてを意図している。

中核は A である。要件定義書、設計書、実装計画書を作成するために、ユーザーへ一つずつ質問しながら壁打ちする workflow として定義したい。

workflow は issue-level の要件定義だけに限定しない。より狭いスコープ、より広いスコープでも使いたい。issue、epic、initiative の単位でも使える必要がある。一周だけではなく、必要に応じて複数回実行できるものにしたい。

B も必要である。skill としても利用したい。

C も必要である。ユーザーにヒアリング / インタビューした際に、質問事項と回答を discussion record としてファイルに記録したい。議論した内容、質問内容、ユーザー回答を記録する template も必要になるはずである。

### Codex 分析

ユーザーの回答から、この機能は単一の実装 artifact ではなく、階層化された capability として扱うべきである。

1. 中核の振る舞い:
   - source-grounded interview workflow。
   - 一度に一つの質問。
   - requirement / design / plan の作成に使える。
   - issue / epic / initiative の各スコープで使える。
2. 再利用可能な呼び出し surface:
   - skill または agent-facing workflow として利用できる。
3. 永続的な evidence surface:
   - discussion record が第一級 artifact になる。
   - 各質問と回答を記録する。
   - 記録 template も要件に含まれる可能性が高い。

したがって、最終的な requirement は「issue-level skill を一つ追加する」だけでは狭すぎる。

まず scope-neutral な clarification workflow を定義し、その上で delivery surface を分けて定義するのがよい。

- 適用スコープ: issue / epic / initiative。
- 適用フェーズ: requirement / design / plan。
- 記録 artifact: interview discussion record。
- 呼び出し surface: skill を中心にしつつ、CLI / template integration は productization surface として扱う。

### 要件への含意

- AC には final canonical docs だけではなく、質問回答 evidence の記録も含める必要がある。
- AC には one-question-at-a-time behavior を含める必要がある。
- AC には issue / epic / initiative をまたぐ scope-awareness を含める必要がある。
- design では workflow contract と delivery surface を分離する必要がある。
- plan では workflow contract / artifact contract が合意されるまで実装に進まない。

## Q-002: interview record と canonical docs の関係

### 質問

ユーザーの回答を記録した interview discussion は、最初は evidence として残し、あとで採用判断して `requirement.md` / `design.md` / `plan.md` に反映する、という扱いでよいか。

### ユーザー回答

正規の要件定義書、設計書、計画書の作成も workflow に含める。

要件定義書は orchestrator が、ユーザーと discussion しながら作成する。

一方で、設計書や計画書については専門の agent がいる。専門 agent がより高度な分析をして作成する。

まずユーザーとの壁打ちを行い、その内容を record としてファイルに残す。その記録が十分に積み上がり、憶測や曖昧な理解ではなく、要件定義書を作成するにあたって完全に詳細な理解が得られた状態にする。そのための document / discussion を積み上げることが目的である。

main workflow としては、最終的に要件定義書、設計書、計画書を作成するところまで含む。

ただし skill として使う場合は、必ず要件定義書 / 設計書 / 計画書を作成するとは限らない。特定の分析レポート、設計書ドラフト案など、目的に応じて、インタビュー内容を積み上げ、小さな決定事項を積み上げ、憶測や曖昧な理解ではない完全な理解を構築することが目的になる。

また、作成するファイルの本文は日本語で作成してほしい。

### Codex 分析

ユーザーの回答により、interview record と canonical docs の関係は次のように整理できる。

1. discussion record は単なる任意メモではない。
   - 正規ドキュメントを作成する前提となる理解の積み上げである。
   - 質問、回答、分析、小さな決定事項を保存する evidence layer である。
2. main workflow の最終成果物は canonical docs である。
   - `requirement.md`
   - `design.md`
   - `plan.md`
3. canonical docs の作成責務はフェーズごとに異なる。
   - 要件定義書: orchestrator がユーザーと discussion しながら作成する。
   - 設計書 / 計画書: 専門 agent が高度な分析を行って作成する。
4. skill としての利用は main workflow より汎用的である。
   - 必ず canonical docs 作成まで行くとは限らない。
   - 特定の分析レポート、設計ドラフト、意思決定整理などにも使える。
   - その場合でも、目的は「曖昧さを減らし、完全な理解に近づけること」である。

このため、requirement には少なくとも二つの mode を区別して書く必要がある。

- Canonical authoring mode:
  - interview record を積み上げ、最終的に requirement / design / plan を作成する。
  - phase owner / agent role が明確である。
- Clarification / analysis mode:
  - canonical docs 作成が必須ではない。
  - ただし質問回答記録と理解の積み上げは行う。
  - output は analysis report、draft、decision record などになりうる。

また、日本語話者のユーザーが使う workflow なので、user-facing / discussion-facing docs は日本語を default とする必要がある。

### 要件への含意

- AC に「interview record が日本語で残る」を含める必要がある。
- AC に「main workflow は canonical docs 作成まで含む」を含める必要がある。
- AC に「skill usage では canonical docs 作成が必須ではない」を含める必要がある。
- design で phase owner を整理する必要がある。
  - requirement: orchestrator + user discussion。
  - design / plan: specialized agent analysis。
- plan では、いきなり implementation skill を作る前に、record template と canonical reflection rule を定義する必要がある。

### 未確定事項

- 専門 agent が design / plan を作成する際、ユーザーへの追加質問は orchestrator 経由に限定するのか、専門 agent が直接 interview workflow を使ってよいのか。
- interview record から canonical docs への反映は、どのタイミングで、誰が採用判断するのか。
- 日本語 default としつつ、code identifiers、file paths、command names、frontmatter keys は英語のまま維持するか。

## Q-003: 専門 agent の質問経路

### 質問

設計書や計画書を作る専門 agent が、分析中に「ユーザー確認が必要な曖昧さ」を見つけた場合、その質問は誰がユーザーに聞くべきか。

Codex の推奨案は、専門 agent は直接ユーザーに質問せず、質問候補と理由を discussion record に残し、orchestrator がユーザーへ一問ずつ聞く方式である。

### ユーザー回答

Codex の推奨案を採用する。

Sub-agent がユーザーに直接問い合わせるのではなく、質問事項を取りまとめた上で、orchestrator が人間のユーザーに質問する。

### Codex 分析

この回答により、ユーザー対話の責務境界が明確になった。

- 人間ユーザーとの対話:
  - orchestrator が担当する。
- 専門 agent:
  - 高度な分析、設計案、計画案、質問候補の抽出を担当する。
  - ユーザーへ直接質問しない。
- 質問候補:
  - 専門 agent から orchestrator へ返す。
  - orchestrator が優先順位を判断し、一度に一つだけユーザーへ質問する。

この方針により、対話の一貫性、採用判断、canonical docs への反映責任を orchestrator に集約できる。

### 要件への含意

- AC に「ユーザーへの質問は orchestrator 経由に限定する」を含める必要がある。
- design で agent responsibility boundary を定義する必要がある。
- 専門 agent の出力には、必要に応じて「質問候補」「質問理由」「影響する artifact」「推奨回答」を含める必要がある。
- `grill` workflow は、専門 agent の分析結果を直接ユーザーへ投げるのではなく、orchestrator が質問シートとして整形して提示する workflow になる。

## Q-004 以降に適用する追加ルール: 質問前シート方式

### ユーザー指示

今後は、質問に対する回答を受けてから資料を作るのではなく、質問する前に質問シートを作成する。

質問シートには、次を含める。

- 質問の目的
- 質問内容
- 詳細
- 回答候補
- Codex の分析
- Codex の推奨案
- 視覚的に理解しやすい PlantUML 図

ユーザーが回答する前の未入力状態で質問シートを作成し、その後ユーザーの回答を受けて、同じ質問シートに回答を入力して完成させる。

PlantUML 図の中は、ユーザーが理解しやすいように日本語を基本とする。class 名など英語を使う必要がある technical token は英語のままでよい。

### Codex 分析

このルールは、interview workflow の artifact contract に関わる重要な要件である。

従来の「質問 -> 回答 -> 記録」だけでは、ユーザーが質問の背景、選択肢、影響範囲を把握しにくい。先に質問シートを作ることで、ユーザーは次を見てから回答できる。

- なぜその質問が必要なのか
- どの artifact に影響するのか
- どの選択肢があり、何が tradeoff なのか
- Codex はどの選択肢を推奨しているのか
- 回答後に何が確定するのか

これは `grill-with-docs` の「質問を一つずつ行う」考え方を、spec-dock の evidence-first workflow に適合させる拡張である。

### 要件への含意

- interview artifact には「未回答の質問シート」と「回答済みの質問記録」の両方の状態が必要である。
- 質問シート template が必要になる。
- 質問シートには PlantUML を埋め込める必要がある。
- 本文および図の説明は日本語 default とする必要がある。
- 回答前のシート作成と、回答後のシート completion が workflow の必須手順になる。
