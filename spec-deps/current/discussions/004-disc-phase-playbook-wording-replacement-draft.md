---
種別: disc
ID: "004-disc-phase-playbook-wording-replacement-draft"
タイトル: "phase playbook の実文言差し替え案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00019"]
関連: ["002-disc-phase-playbook-authoring-workflow-revision", "003-disc-phase-playbook-concrete-edit-blueprint"]
---

# 004-disc phase playbook の実文言差し替え案

## 議題 (必須)
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` の冒頭追加と見出し整理について、実際に差し替えに使える文言案を固定する。
- あわせて、`guide.md`, `docs/README.md`, `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md` に入れる最小限の導線文言案も用意する。

## 背景 (必須)
- ここまでの分析で、既存の phase playbook には個別要素は十分にある一方、全体 workflow の入口が弱いことが分かった。
- そこで、各 phase 文書の最初の方に「この phase は全体 workflow のどこか」「この phase の中でどう進めるか」を先に示し、その後で既存の詳細説明へ降りる構成に改める。
- このシートは、実編集時にそのまま貼り込める文言のたたき台である。

## 推奨する差し替え方針 (必須)
- 各 `phase_*.md` の導入文と `関連:` の直後に、新しい `## 1. ... の全体 workflow` セクションを追加する。
- 既存の `この phase の目的 / 出力 / 非ゴール` は残しつつ、`## 2.` 以降へ後ろ倒しする。
- 既存の詳細節は活かし、必要最小限の見出し改名だけを行う。
- `guide.md` と `docs/README.md` には入口導線だけを足し、詳細は phase playbook へ寄せる。
- `workflow_*.md` には scope 固有と共通作法の責務分離を短く明記する。

## 差し替え案: `phase_requirement.md` (必須)

### 追加する冒頭セクション案
```md
## 1. requirement phase の全体 workflow

requirement phase は、全体 workflow の中で「何を解くか」「なぜ今やるか」「どこまでを対象にするか」を固定する工程です。  
この phase の前には、対象スコープの確認と初期的な調査分析があり、この phase の後に design、plan、実装/品質ゲート確認が続きます。  
Initiative / Epic / Issue のどれでも、まず対象 scope の `workflow_*.md` で前後の流れと品質ゲートを確認し、そのうえでこの playbook に沿って requirement を詰めます。

- この phase の位置づけ:
  - 調査分析の結果をもとに、WHAT / WHY / scope / success を固定する
- 前段で揃っている前提:
  - 対象 scope が明確になっている
  - 既存 docs / 実装 / 周辺情報を調べ始められる状態になっている
- この phase で固定すること:
  - 目的
  - 背景・現状
  - 成功条件
  - スコープと非スコープ
- この phase の完了条件:
  - reviewer が「design へ進めてよい」と判断できること

標準順:
1. 目的と意図を理解する
2. 関連 docs / 実装 / 制約を徹底調査する
3. 調査結果を `research` / `disc` / `note` / `adr` に残す
4. 必要なら discussion / ADR を材料にヒアリングする
5. 情報が揃ってから requirement 本文を書く
6. reviewer コメントを反映し、re-review を回す
7. `requirement.md` と関連 docs を束で提出し、design へ渡す

注意:
- 情報が揃う前に requirement 本文を書き始めません。
- source のない断定や、HOW に踏み込みすぎた内容は requirement 本文へ入れません。
- scope 固有の操作、entry 条件、品質ゲートは `workflow_*.md` を正本とします。
```

### 推奨する見出し名
```md
## 1. requirement phase の全体 workflow
## 2. この phase の目的 / 出力 / 非ゴール
## 3. workflow 開始前に確認すること
## 4. requirement workflow の進め方
## 5. ユーザーヒアリングを挟む条件
## 6. discussion sheet を作る条件
## 7. ADR を切る条件
## 8. template で先に埋める節
## 9. reviewer に渡す前の exit criteria
## 10. 次の phase へ進める条件
## 11. subagent 活用ガイダンス
## 12. 迷ったときの判断順
```

## 差し替え案: `phase_design.md` (必須)

### 追加する冒頭セクション案
```md
## 1. design phase の全体 workflow

design phase は、全体 workflow の中で requirement で固めた WHAT / WHY を、実装可能な HOW と guardrails に落とす工程です。  
この phase の前には requirement の承認があり、この phase の後に plan、実装/品質ゲート確認が続きます。  
Initiative / Epic / Issue のどれでも、まず対象 scope の `workflow_*.md` で前後の流れと品質ゲートを確認し、そのうえでこの playbook に沿って設計を進めます。

- この phase の位置づけ:
  - requirement を、境界・契約・移行・観測性・テスト戦略を備えた HOW に変換する
- 前段で揃っている前提:
  - requirement が reviewer 承認レベルに達している
  - design で閉じる論点と、追加ヒアリングが必要な論点が切り分けられている
- この phase で固定すること:
  - 設計方針
  - 境界 / 契約
  - 依存 / リスク
  - テスト戦略
- この phase の完了条件:
  - reviewer が「plan へ進めてよい」と判断できること

標準順:
1. requirement の意図と未確定論点を確認する
2. 既存実装 / docs / ADR を徹底調査する
3. 調査結果や比較結果を `research` / `disc` / `adr` に残す
4. 必要なら discussion / ADR を材料にヒアリングする
5. 情報が揃ってから design 本文を書く
6. reviewer コメントを反映し、re-review を回す
7. `design.md` と関連 docs を束で提出し、plan へ渡す

注意:
- requirement の不足を design 本文でごまかしません。
- 長い比較表や非採用案の詳細は discussion / ADR へ出し、本文は HOW / Guardrails に集中します。
- scope 固有の操作、entry 条件、品質ゲートは `workflow_*.md` を正本とします。
```

### 推奨する見出し名
```md
## 1. design phase の全体 workflow
## 2. この phase の目的 / 出力 / 非ゴール
## 3. workflow 開始前に確認すること
## 4. design workflow の進め方
## 5. ユーザーヒアリングを挟む条件
## 6. discussion sheet を作る条件
## 7. ADR を切る条件
## 8. template で先に埋める節
## 9. reviewer に渡す前の exit criteria
## 10. 次の phase へ進める条件
## 11. subagent 活用ガイダンス
## 12. 迷ったときの判断順
```

## 差し替え案: `phase_plan.md` (必須)

### 追加する冒頭セクション案
```md
## 1. plan phase の全体 workflow

plan phase は、全体 workflow の中で requirement / design で確定した内容を、実行可能な順序と粒度に分解する工程です。  
この phase の前には requirement と design の承認があり、この phase の後に実装と品質ゲート確認が続きます。  
Initiative / Epic / Issue のどれでも、まず対象 scope の `workflow_*.md` で前後の流れと品質ゲートを確認し、そのうえでこの playbook に沿って計画を組み立てます。

- この phase の位置づけ:
  - 確定した要求と設計を、実行順・分解単位・停止点・品質ゲートへ落とす
- 前段で揃っている前提:
  - requirement と design が reviewer 承認レベルに達している
  - 依存とブロッカーを見積もれるだけの情報がある
- この phase で固定すること:
  - 分解単位
  - 順序
  - 完了判定
  - review / docs / quality gate の置き方
- この phase の完了条件:
  - reviewer が「この計画で実行してよい」と判断できること

標準順:
1. requirement / design の確定事項と未確定事項を確認する
2. 依存順・並行可能性・停止点・品質ゲートを調査する
3. 分割案や順序案を必要に応じて `disc` / `note` / `adr` に残す
4. 必要なら discussion を材料にヒアリングする
5. 情報が揃ってから plan 本文を書く
6. reviewer コメントを反映し、re-review を回す
7. `plan.md` と関連 docs を束で提出し、実行へ渡す

注意:
- requirement / design の再議論を plan 本文へ持ち込みません。
- 分割案や順序案の比較が長くなる場合は `disc` に分離します。
- scope 固有の操作、entry 条件、品質ゲートは `workflow_*.md` を正本とします。
```

### 推奨する見出し名
```md
## 1. plan phase の全体 workflow
## 2. この phase の目的 / 出力 / 非ゴール
## 3. workflow 開始前に確認すること
## 4. plan workflow の進め方
## 5. ユーザーヒアリングを挟む条件
## 6. discussion sheet を作る条件
## 7. ADR を切る条件
## 8. template で先に埋める節
## 9. reviewer に渡す前の exit criteria
## 10. 実行へ進める条件
## 11. subagent 活用ガイダンス
## 12. 迷ったときの判断順
```

## 周辺 docs の短い追記案 (必須)

### `guide.md`
```md
requirement / design / plan の進め方は、scope 共通の phase playbook を参照してください。  
このガイドは全体像と生成物の理解を目的とし、phase ごとの実務手順は `workflow_*.md` と `phase_*.md` に分離しています。
```

### `docs/README.md`
```md
実務の入口は `workflow_*.md`、phase ごとの共通作法は `phase_*.md` を参照してください。  
この README は docs 全体の導線だけをまとめ、詳細ルールの正本は各 workflow / playbook に置きます。
```

### `workflow_initiative.md`
```md
Initiative の requirement / design / plan の書き方は `phase_*.md` を正本とします。  
この workflow では、Initiative 固有の再利用判定、作成手順、品質ゲートだけを扱います。
```

### `workflow_epic.md`
```md
Epic の requirement / design / plan の書き方は `phase_*.md` を正本とします。  
この workflow では、Epic 固有の再利用判定、作成手順、Issue 分割の判断だけを扱います。
```

### `workflow_issue.md`
```md
Issue の requirement / design / plan の書き方は `phase_*.md` を正本とします。  
この workflow では、active issue 起点の実行、TDD、review loop、docs impact、final quality gate を扱います。
```

## 補足メモ (任意)
- 実編集では、まず 3 本の `phase_*.md` に共通の冒頭セクションを揃え、そのあとで見出し番号と文言を調整するのが安全である。
- 既存本文の詳細な条件分岐、template 優先節、subagent 活用ガイダンス、判断順は基本的に残し、不要な全面書き換えは避ける。

## 次アクション (必須)
- この文言案をベースに、次は `phase_requirement.md`, `phase_design.md`, `phase_plan.md` 本体の実更新に進む。
- その後で `guide.md`, `docs/README.md`, `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md` へ最小限の導線追記を行う。
