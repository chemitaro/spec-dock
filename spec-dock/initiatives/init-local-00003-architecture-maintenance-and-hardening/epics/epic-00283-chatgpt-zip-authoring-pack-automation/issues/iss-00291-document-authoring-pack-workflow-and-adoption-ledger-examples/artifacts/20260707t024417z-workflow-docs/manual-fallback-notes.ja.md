# Manual fallback notes

## ChatGPT unavailable

ChatGPT Use が使えない場合は、manual authoring path に戻ります。`report.md` には blocked evidence として、使えなかった backend、必要だった出力、再開条件を記録します。ChatGPT が使えないことを理由に、Issue planning や reviewer gate を省略しません。

## ZIP generation unavailable

ZIP を生成できないが隔離済み tree がある場合、tree review は fallback として扱えます。ただし ZIP central directory safety evidence は提供できないため、その不足を明示します。

推奨記録:

- input kind: `tree`。
- ZIP-specific safety evidence: unavailable。
- fallback reason。
- local path は repo-relative または redacted reference。
- next action: ZIP regeneration または tree-only review の reviewer confirmation。

## GitHub connector unavailable

GitHub connector が使えない場合、pushed branch を前提にした ChatGPT analysis は hard failure として扱います。代替する場合は、local checkout の `git status`、`git rev-parse HEAD`、source hash、branch push evidence を記録し、ChatGPT connector analysis の代替ではなく manual fallback evidence として扱います。

## review helper unavailable

review helper が実行できない場合、ChatGPT output を正本採用しません。blocked evidence を残し、helper 復旧、manual schema inspection、または Issue scope の見直しへ戻します。

## source stale / hash mismatch

source hash、requested ref、selected skeleton hash、profile snapshot、review digest が一致しない場合は `stale` として扱います。regenerate または source reconciliation まで adoption しません。

## backend command adapter unavailable

ChatGPT Use / Oracle backend command adapter の正式実装は `iss-00293` の scope です。`iss-00291` では、個人環境固有 wrapper path を正本 docs や正式 workflow に直書きしません。

将来の adapter では、backend command が未設定の場合は明確なエラーで fail し、設定時だけ指定された command を呼び出す、という契約を `iss-00293` で検証します。

## evidence recording

fallback evidence には次を含めます。

- fallback type。
- unavailable component。
- affected workflow step。
- observed status: `blocked` / `stale` / `deferred`。
- canonical docs を変更していないこと。
- `.assurance.json` を変更していないこと。
- next action。

## restart criteria

- connector / backend / helper が復旧した。
- branch が push され、source hash が再固定された。
- stale source が reconcile された。
- fresh reviewer が fallback evidence を確認した。
- EAL に adoption / rejection / deferred decision が記録された。
