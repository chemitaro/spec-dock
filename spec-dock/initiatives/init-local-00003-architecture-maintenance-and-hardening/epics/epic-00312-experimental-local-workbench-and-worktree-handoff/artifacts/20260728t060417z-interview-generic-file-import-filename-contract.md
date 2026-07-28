---
種別: interview
ID: "20260728t060417z-interview"
タイトル: "任意ファイルArtifact importの自動filename規則"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00312"]
関連:
  - "20260728t054338z-research"
  - "20260728t054625z-interview"
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-28T06:04:17Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "2026-07-28 user clarification"
reflected_to:
  - "20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md"
---

# 任意ファイルArtifact importの自動filename規則

## 正式質問として扱う理由

任意file importのfilenameはArtifact validation、collision allocation、original extension、利用時の見つけやすさ、backward compatibilityを決める。

この回答は次へ影響する。

- `requirement.md`: import後filenameの受け入れ条件
- `design.md`: allocator、normalizer、validator
- `plan.md`: generic Markdown/non-Markdown test matrix
- ADR: non-Markdown Artifact filename familyを長期固定する場合だけ候補

## 質問

任意fileをArtifactへimportするとき、destination filenameはどの形が意図に近いでしょうか。

### Option A — timestamp prefix + original filename（Codex推奨）

```text
report.pdf
  -> 20260728t060000z-report.pdf

system-log.txt
  -> 20260728t060001z-system-log.txt
```

- timestamp/collision prefixだけをruntimeが追加する。
- original basenameとextensionを可能な限り保持する。
- filesystem上危険な文字だけnormalizeする。
- `--title` / `--slug`は不要。

### Option B — timestamp prefix + normalized slug

```text
顧客向け 最終報告.PDF
  -> 20260728t060000z-customer-final-report.pdf
```

- basenameをArtifact向けkebab-case slugへ正規化する。
- extensionは保持する。
- 安全で規則的だが、original filenameとの対応が弱くなる。

### Option C — typed `file` token + slug

```text
report.pdf
  -> 20260728t060000z-file-report.pdf
```

- imported file専用の`file` type tokenを導入する。
- formal Artifact familyとして識別しやすい。
- 新しい永続filename contractとvalidator拡張が必要。

回答では、A / B / C、または修正版を指定してほしい。

## source-grounded context

確認済み:

- current blank Artifact:
  - `<ts>-<slug>.md`
- current typed Artifact:
  - `<ts>-<type>-<slug>.md`
- collision:
  - `<ts>-<nn>-...`
- current `artifact import chatgpt-output`:
  - blank grammarを使う
  - `chatgpt-output-<slug>`を生成する
  - `.md`のみ
  - title必須
- user clarification:
  - 任意fileを指定scopeへimportする
  - runtimeが規約準拠prefixを自動付与する

local contextで解決できたこと:

- timestamp/collision allocatorは再利用できる
- source bytesとextensionは分けて扱える
- callerにfull destination filenameを指定させる必要はない

人間判断が必要な理由:

- 「prefixを付ける」は明示されたが、prefix後にoriginal filenameを保持するかslugへ変換するかは明示されていない
- `file` token導入の有無は長期互換性へ影響する

## Codexの分析

判断軸:

- original fileとの対応の分かりやすさ
- commandの簡単さ
- security/path safety
- Artifact namingの規則性
- non-Markdown recognition

tradeoff:

- Option Aは最も単純で、利用者の「fileへprefixを付ける」という表現に近い
- Option Bは規則的だが、filenameの意味をruntimeが書き換える
- Option Cはformal identityが明確だが、今回必要な小さな機能より契約が重い

## Codexの推奨案

Option Aを推奨する。

追加規則:

- path componentはbasenameだけを使う
- `/`、NUL、platform予約名など安全上必要な箇所だけnormalizeする
- extensionを保持する
- source filenameが既にtimestamp prefixを持っていても、新しいimport prefixを付ける
- collisionはexisting `<nn>` allocatorを使う
- sourceはcopy-not-moveで残す

## ユーザー回答

- answer capture:
  - 2026-07-28 chat回答
- 回答:
  - Option Aを採用する。
  - runtimeはtimestamp/collision prefixを自動付与する。
  - prefix後はoriginal basenameとextensionを可能な限り保持する。
  - filesystem/path safety上必要な箇所だけnormalizeする。
  - importに`--title` / `--slug`を必須としない。
- 回答日時:
  - 2026-07-28

## 追加確認の要否

- 追加確認が必要か: yes
- 次のquestion candidate:
  - `20260728t060706z-interview-external-file-import-policy.md`

## 採用判断

- adoption_status: adopted
- adoption target:
  - target-state research
  - future `requirement.md`
  - future `design.md`
  - future `plan.md`
  - future `report.md` Evidence Adoption Ledger
- 理由:
  - product ownerがOption Aを明示採用した
- `report.md`反映要否:
  - yes when canonical authoring begins

## requirement / design / plan / ADRへの含意

- `requirement.md`:
  - destinationは`<ts>-<original-basename>`を基本形とする
  - collisionは`<ts>-<nn>-<original-basename>`
  - extensionを維持する
  - title/slugを必須としない
- `design.md`:
  - basename抽出、minimum safety normalization、collision allocatorを定義する
- `plan.md`:
  - Unicode、space、reserved character、extension、same-second collision testを追加する
- `ADR`:
  - typed `file` tokenは採用しない
- reflected_to:
  - target-state researchへ反映済み
