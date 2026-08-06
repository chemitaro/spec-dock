# iss-00354 S10 Blue Gate 再評価ブリーフ v5

## 固定 identity と判定

| 項目 | 確認値 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Named branch | `codex/iss-00354-chatgpt-context-contract` |
| Exact pushed HEAD | `6abc002d867b6dcde1ac801622f18f0f8017d82d` |
| Branch parity | identical（ahead 0 / behind 0） |
| Default branch fallback | 使用していない |
| Oracle version | `0.17.0` |
| Oracle source HEAD | `9fb87d9326ab1c07216f1eb904917013df6d9270` |
| 判定 | **S10 production/test gate は引き続き blocked** |
| closure claim | `none` |

GitHub connectorでnamed branchと指定HEADの完全一致を確認した。artifact-pendingのpersisted producerとtransfer-failedのclosed discriminatorがない限り、五分類の部分実装は禁止する。

## 今回解消した証跡 gap

Oracleが生成したterminal `meta.json`に、送信前モデル選択失敗の `promptSubmitted=false` が保存されることを実測した。これはpre-submitのpositive fixtureとして採用できる。

```json
{
  "status": "error",
  "mode": "browser",
  "browser": {"runtime": {"promptSubmitted": false}},
  "error": {
    "category": "browser-automation",
    "details": {"stage": "execute-browser"}
  }
}
```

観測された条件は、accepted model alias `gpt-5.4`、UI target `Thinking 5.4`、Oracleのmodel-selection failure、artifact inventory absent、warning inventory absent、ChatGPT submission 0 である。

したがって、次のdecision-engine fixtureは安全に実装できる。

```text
prompt_submitted=False
terminal_stage=pre-submit
successful_submission_count=0
harvest_builder/process=0
capture_builder/process=0
same-session poll=0
failure_class=MODEL_SELECTION_UNAVAILABLE
recovery_action=NEW_EXECUTION_SAME_MODEL
```

ただし、任意の `error.details.stage="execute-browser"` を model-selection failure に変換してはならない。このstageは一般のbrowser execution errorにも使われるため、version-bound fixtureまたはclosed discriminatorとのexact match以外は `undecidable` としてfail closedにする。`promptSubmitted` が欠落またはnon-booleanの場合は `None` のまま扱い、`false` へ補完しない。

## 未解消 blocker

### Artifact pending

Oracle typeには `ready` / `streaming` が存在するが、remote serverの `artifact-ready` / `artifact-progress` はremote transport上の一時状態であり、SpecDockが読むlocal session `meta.json` の `artifacts[].transfer.status` へ永続化された証拠ではない。artifact absence、response complete、artifact-ready event、process timeout/nonzero、session nonterminalからpendingを推測しない。

### Transfer failed

Remote clientは `remote-artifact-transfer-failed` warningを生成するが、local browser session `meta.json` への永続化、および `artifacts[].transfer.status="failed"` のproducerは確認できていない。よって `OUTPUT_DOWNLOAD_FAILED` → `blocked / oracle_output_download_failed` のclosed mappingはまだ実装しない。

## 実装着手可否

```text
pre-submit false reader/test fixture = unblocked
model-selection pre-submit decision fixture = unblocked
artifact-pending production classifier = blocked
transfer-failed production classifier = blocked
complete S10 bounded change-set = blocked
```

今回のreceiptだけを根拠にpre-submit branchを部分的にproduction投入しない。現行のstop gateを維持する。

### 現時点で許可される変更

```text
report.md
本briefのimmutable artifact
新receiptのimmutable characterization artifact
```

### 現時点で禁止される変更

```text
src/spec_dock/
tests/
requirement.md
design.md
plan.md
EAL-083〜EAL-086
S09 source/tests/evidence
```

## 次の exact verification command

Oracle source rootでlocal session metadataまで通すproducer-integrated testを実行する。

```bash
cd workspace/tools/oracle && \
pnpm exec vitest run \
  tests/cli/sessionRunner.test.ts \
  tests/remote/server.test.ts \
  --reporter=dot
```

このcommandのPASSだけでは不十分であり、`tests/cli/sessionRunner.test.ts`に、同一のsession `meta.json`を通して次をassertするfixtureが必要である。

```text
artifact pending:
  performSessionRunを通る
  promptSubmitted=true
  response.status=completed
  artifacts[].transfer.status=ready|streaming

transfer failed:
  performSessionRunを通る
  artifacts[].transfer.status=failed
    または browser.warnings[].code=remote-artifact-transfer-failed
```

Remote descriptor、remote event、client-local warningだけをassertするtestではstop gateを解除しない。

## Handoff状態

```text
decision=remains_blocked
production_candidate=none
test_candidate=none
pre_submit_false_fixture=adoptable
artifact_pending_persistence=unresolved
transfer_failed_persistence=unresolved
fresh_red_review=not_started
closure_claim=none
S11_start=prohibited
next_action=producer-integrated local meta.json persistence verification
```
