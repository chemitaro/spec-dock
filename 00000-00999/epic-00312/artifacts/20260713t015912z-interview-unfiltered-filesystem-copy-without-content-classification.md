---
種別: interview
ID: "20260713t015912z-interview"
タイトル: "Unfiltered Filesystem Copy Without Content Classification"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: []
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T01:59:12Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260712t235757z-interview-initial-workbench-copy-file-policy.md"
  - "artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md"
reflected_to:
  - "requirement.md#E-RQ-009-Complete-content-without-semantic-filtering"
  - "report.md#証跡採用台帳Evidence-Adoption-Ledger--必須"
---

# Unfiltered Filesystem Copy Without Content Classification

## 正式質問として扱う理由
- Fresh `spec-reviewer` は、ChatGPT提案のspecial-entry preflightが、既に採用された「すべて持っていく」と衝突すると判定した。
- Copy対象を選別するproduct logicを追加するかどうかは、実装複雑性と利用者期待を変えるため明示回答が必要だった。

## 質問
- 「すべてコピーする」の対象を通常file/directory/symlinkに限定し、FIFO/socket/device node等を独自preflightで拒否するか。それとも独自分類を持たず通常のfilesystem copyへ委ねるか。

## ユーザー回答
- 回答:
  - Workbenchはただの作業場であり、ただfileをcopyするだけにする。
  - Python等のprogram、設定file、特殊な拡張子、すべての言語と関連fileについて、copy対象か判定するlogicは書かない。
  - 対象制限、除外、分類、判定をせず、そのままcopyする。
- 回答日時: `2026-07-13`

## 採用判断
- adoption_status: `adopted`
- adoption target:
  - `requirement.md`
  - `design.md`
  - `report.md` Evidence Adoption Ledger
- 採用内容:
  - extension、language、purpose、content、filename、nested `.git` 等に基づく独自判定を禁止する。
  - special filesystem entry を事前分類する独自preflightも設けない。
  - 通常のrecursive filesystem copyを試み、OS/標準copy primitiveが処理できないentryやI/O failureは通常errorとして扱う。これは対象選別ではなくcopy実行結果である。

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - copy対象のsemantic filteringを禁止し、unsupported-entry専用要件を削除する。
- `design.md`:
  - allowlist/denylist、extension table、language registry、file classifier、special-entry inventoryを実装しない。
  - 標準filesystem copyのfailureをそのままstructured errorへ変換する。
- `plan.md`:
  - 多様な通常file/binary/archive/config/nested `.git`の無選別copyをtestするが、全file type列挙を作らない。
- `ADR`:
  - 不要。

## 追加確認の要否
- 追加確認: no
- 理由:
  - copy対象のproduct policyとfailure boundaryが確定した。
