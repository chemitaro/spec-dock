# ChatGPT prompt pack / ZIP / staged evidence reference

この文書は ChatGPT authoring pack の生成物を、SpecDock の evidence として安全に扱うための reference です。

## 生成物の関係

```text
preflight evidence
  -> prompt pack
  -> backend invocation
  -> ZIP / tree output
  -> pack review report
  -> staged evidence
  -> candidate / draft adoption validation
  -> EAL adoption decision
  -> canonical rewrite
  -> fresh reviewer gate
```

どの段階でも、ChatGPT output は正本ではありません。
review / stage / validate の `pass` は、その command が担当する構造や安全性の確認結果です。

## Prompt pack

prompt pack は、ChatGPT に渡すタスク、期待出力、source manifest、branch / commit 情報、evidence mode、出力 ZIP のディレクトリ構成をまとめたものです。

prompt pack には次を含めます。

- scope: initiative / epic / issue / selected-skeleton
- target node id
- upstream requirement / design / plan
- relevant ADR / artifact summary
- supported output tree
- explicit forbidden authority claims
- expected ZIP manifest
- evidence mode

## ZIP / tree output

ZIP / tree output は長文の複数ファイルをまとめて受け取るための transport です。
そのまま canonical docs にコピーするものではありません。

安全な取り扱い:

- path traversal を拒否する。
- unsafe symlink を拒否する。
- manifest にない unexpected file を警告または拒否する。
- canonical docs、`.assurance.json`、runtime state、GitHub state を直接変更しない。
- output metadata に `authority: evidence_only` を持たせる。

## Staged evidence

`authoring pack stage` は、review 済み output を evidence として配置する工程です。
staged evidence は採用候補であり、canonical artifact ではありません。

staged evidence から canonical docs へ反映する場合:

1. main orchestrator が採用する claim と捨てる claim を決める。
2. `report.md` の Evidence Adoption Ledger に記録する。
3. canonical docs に main orchestrator が再記述する。
4. fresh reviewer gate を通す。

## Candidate validation

`authoring validate initiative-epic-candidates` と `authoring validate epic-issue-candidates` は、候補 list の構造、source hash、approval 前提を確認します。
candidate validation pass は、人間の node creation approval ではありません。

Epic / Issue node creation の前には、人間が候補を確認して承認します。

## Draft adoption validation

`authoring validate issue-draft-adoption` と `authoring validate selected-skeleton-fill` は、既に作成された Issue node の draft adoption input を検査します。

これらの validation pass は、次のどれでもありません。

- canonical adoption completed
- reviewer pass
- execution-ready
- Issue finish

Issue planning skill は validation 結果を evidence として読み、正式 requirement / design / plan を作り、fresh `spec-reviewer` pass を通します。

## Local-context evidence

`local-context` で作った pack は lower-authority evidence です。
GitHub sync が未確認であること、どの local context を渡したか、採用判断の制約を `report.md` に残します。

