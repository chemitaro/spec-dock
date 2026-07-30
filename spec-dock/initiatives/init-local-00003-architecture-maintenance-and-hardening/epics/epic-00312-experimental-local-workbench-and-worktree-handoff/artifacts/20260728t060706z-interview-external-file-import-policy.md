---
種別: interview
ID: "20260728t060706z-interview"
タイトル: "repository外ファイルのArtifact import許可方式"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00312"]
関連:
  - "20260728t054338z-research"
  - "20260728t060417z-interview"
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-28T06:07:06Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "2026-07-28 user clarification"
reflected_to:
  - "20260728t054338z-research-workbench-artifact-import-target-state-gap-reassessment.md"
---

# repository外ファイルのArtifact import許可方式

## 正式質問として扱う理由

「Workbenchでなくてもよい任意file」が、repository内だけを指すのか、repository外の明示pathも含むのかでCLI、path guard、privacy表示、security testが変わる。

影響先:

- `requirement.md`: source eligibility
- `design.md`: source guardとprovenance
- `plan.md`: repository内外path matrix
- ADR: 通常は不要

## 質問

repository外にあるfileをimportするとき、どの許可方式が理想でしょうか。

### Option A — 明示指定された任意regular fileを通常許可（Codex推奨）

```bash
spec-dock artifact import file \
  --file /outside/repository/report.pdf \
  --epic epic-00312
```

- `artifact import file`を実行してpathを指定したこと自体を明示的な許可とみなす。
- repository内外で追加flagを分けない。
- regular non-symlink fileだけを許可する。
- command outputへexternal absolute pathを露出しない。

### Option B — repository外だけ追加flagを要求

```bash
spec-dock artifact import file \
  --file /outside/repository/report.pdf \
  --epic epic-00312 \
  --allow-external
```

- accidental external readへの追加確認になる。
- commandが複雑になり、agent/operatorがflagを付け忘れる可能性がある。

### Option C — repository内fileだけ許可

- root/scoped Workbenchまたはrepository内の任意fileを許可する。
- repository外fileは先にWorkbenchへcopyする必要がある。
- current restrictionより広いが、「任意file」には届かない。

回答では、A / B / C、または修正版を指定してほしい。

## source-grounded context

確認済み:

- current importはapproved Workbench配下だけを許可する
- current source guardはrepository containmentとWorkbench rootsをsecurity boundaryにしている
- current binary publisherにはregular-file、symlink、source stability、no-overwrite guardがある
- product ownerはWorkbench内外の任意file importを要求している

local contextで解決できたこと:

- destinationは常にselected scopeの`artifacts/`内へ固定できる
- outside sourceを許可してもoutside destination writeは不要
- sourceはread-only、copy-not-moveにできる
- resultはbasename/hash/byte count中心のcontent-free表示にできる

人間判断が必要な理由:

- repository外sourceを追加flagなしで許可するかはUXとsecurity postureの選択であり、local codeからproduct intentを確定できない

## Codexの分析

判断軸:

- 「任意file」という期待への一致
- CLIの単純さ
- accidental path指定
- external path privacy
- agent利用時のpredictability

tradeoff:

- Option Aは最も単純で、明示command実行そのものをauthorization boundaryにする
- Option Bはdefense-in-depthだが、path指定とflagの二重確認になる
- Option Cは安全範囲が明確だが、不要なpre-copyを再導入する

## Codexの推奨案

Option Aを推奨する。

安全条件:

- exactly one explicit source path
- regular non-symlink file
- source ancestryのsymlink policyを明示
- source bytesを変更しない
- sourceを削除しない
- destinationはscope `artifacts/`から出さない
- absolute external pathをnormal outputやtracked provenanceへ保存しない
- basename、SHA-256、byte count、source zone程度のcontent-free provenanceだけを返す

## ユーザー回答

- answer capture:
  - 2026-07-28 chat回答
- 回答:
  - Option Aを採用する。
  - `artifact import file`でpathを明示指定したこと自体を許可とみなす。
  - repository内外で追加flagを分けない。
  - repository外のreadable regular non-symlink fileも通常importできる。
  - external absolute pathを通常出力やtracked provenanceへ保存しない。
- 回答日時:
  - 2026-07-28

## 追加確認の要否

- 追加確認が必要か: yes
- 次のquestion candidate:
  - `20260728t060909z-interview-workbench-copy-disposition.md`

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
  - exactly one explicit readable regular file pathをrepository内外から許可する
  - repository外sourceに追加flagを要求しない
- `design.md`:
  - explicit path指定をauthorization boundaryとする
  - external absolute pathを通常出力・tracked provenanceへ残さない
  - destination containmentはscope `artifacts/`で固定する
- `plan.md`:
  - repo-local / external / symlink / special-file / privacy testを追加する
- `ADR`:
  - 現時点では不要
- reflected_to:
  - target-state researchへ反映済み
