# iss-00354 S10 Blue Gate 再評価ブリーフ v6

## 固定 identity

| 項目 | 確認値 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Named branch | `codex/iss-00354-chatgpt-context-contract` |
| Exact pushed HEAD | `46436678d927a82cbe0206043991ca4b13db4980` |
| Branch parity | identical（ahead 0 / behind 0） |
| Default branch fallback | 使用していない |
| Oracle | `0.17.0` / source HEAD `9fb87d9326ab1c07216f1eb904917013df6d9270` |
| 判定 | **S10 production/test implementation は blocked** |
| Production Candidate | `none` |
| Fresh Red review | 未開始 |
| closure claim | `none` |

## 採用できる証拠

Oracleが生成した送信前モデル選択失敗のterminal metadataで、`browser.runtime.promptSubmitted=false`、`status=error`、`mode=browser`、送信0回、artifact／warningなしを確認した。このfixtureからは、pre-submitのharvest、capture、same-session pollを0回に固定する不変条件を採用できる。missingまたはnon-booleanの`promptSubmitted`は`None`のままfail closedとする。

## 残存 blocker

Oracleのcombined test 42件PASSと、native remote client + browser session runner + file session storeのtransfer-failure harnessを確認した。しかし、強制転送失敗の最終状態は次のとおりだった。

```text
sessionStatus = completed
browserWarnings = []
artifact transfer statuses = [not-needed]
```

remote clientが作る`remote-artifact-transfer-failed` warningはbrowser session runnerで結果へ継承されず、`transfer.status=failed`を持つartifact producerもない。remote descriptor、event、client-local warning、artifact absenceからlocal pending／failedを推測してはならない。

## 完了可否

現時点で、S10の五分類（model selection、attachment submission、prompt reconstruction、generation、output download）をすべて満たすSpecDock-onlyのevidence-backed実装経路はない。pre-submit branchだけをproductionへ部分投入することも禁止する。

## 最小の外部前提

Oracle側で、実際のSpecDock execution pathから到達する同一sessionのlocal `meta.json`へ、次のいずれかを永続化する必要がある。

1. artifact pending: `promptSubmitted=true`、`response.status=completed`、`artifacts[].transfer.status=ready|streaming`
2. transfer failed: `artifacts[].transfer.status=failed` または `browser.warnings[].code=remote-artifact-transfer-failed`
3. capture成功後の同一session transition: `completed`、validation、size、SHA

このOracle upstream変更は本Issueの変更範囲外である。

## 許可／禁止範囲

許可は`report.md`のappend-only evidence更新、本briefのimmutable保存、新しいsanitized receiptの保存のみ。`src_spec_dock/`、`tests/`、`requirement.md`、`design.md`、`plan.md`、Oracle source、S09、S11以降は変更しない。Fresh Red review、PR、merge、Issue close、Issue finishも保留する。

## 次ゲート

```text
Oracle producer-integrated local meta.json fixtures
→ append-only evidence adoption
→ separate S10 unblock brief
→ bounded SpecDock implementation
→ verification
→ fresh Red review
```
