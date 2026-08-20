---
種別: 設計書（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00368 Recognized Workspace Reconciliation — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

`update` / `init --force` を最初の complete vertical slice として、以下を実際の public flow まで接続する。

```text
CLI Adapter
  -> recognize/update intent
  -> Distribution Operation Service
      -> Contract + read-only Assessment
      -> ExecutableMutationPlan
      -> OperationJournal
      -> Descriptor-bound Kernel
      -> postcondition + ProcessResult
```

D1 で導入する abstraction は後続 Issue が拡張できるが、未使用の generic framework にしない。recognized flow で必要な action、identity、journal transition だけを実装し、同じ Issue 内で旧 recognized-flow seam を削除する。

## Current / Target

### Current

- `admit_distribution_operation()` が package version、workspace version/anchors、retry marker を read-only に検証する。
- `build_distribution_plan()` が current/historical/unknown provenance と create/adopt/upgrade/prune/preserve/block を作る。
- `apply_distribution_plan()` が no-follow target/parent/root checks、staging、atomic publish、cleanup、progress callback を持つ。
- `cli.py` が root lock、marker phases、scaffold callback、post-plan、version write、marker finalization を orchestration する。
- `allow_blocked_scaffold_paths` と `scaffold_applier` により、plan action とは別の mutation authority が存在する。

### Target

- recognized flow の orchestration を `DistributionOperationService.execute()` 相当へ移す。
- `WorkspaceAssessment` と `ExecutableMutationPlan` を別 type にし、blocker 有り assessment から plan を構築できない API にする。
- plan の全 mutation を common action grammar と kernel operation に展開する。scaffold refresh を callback で外注しない。
- journal が operation phase と action checkpoint を所有し、CLI は marker phase を書かない。
- `ProcessResult` から current text/exit semantics を生成する。

## 責務・Interface

### Recognized intent

```text
RecognizedIntent = update | init-force
```

`init-force` は overwrite authority ではなく、recognized workspace で installer init semantics を選ぶ intent とする。unknown/modified asset の ownership blocker を解除しない。

### Assessment input

- target root descriptor binding
- recognized workspace version/anchor evidence
- package Distribution Contract
- current/historical ownership evidence
- current journal または convertible legacy marker
- explicit intent

### Assessment output

各 target disposition は次を持つ。

```text
relative_path
observed_identity
ownership_provenance: missing | current | historical | unknown
action: create | adopt | replace | remove | preserve | block
reason_code
blocking
```

obsolete target は historical evidence と exact current observation が一致する場合だけ remove authority を得る。mode drift は content が current desired bytes と一致し、target が safe regular single-link identity と証明できる場合だけ desired mode への repair action とする。content ownership、type、link count、parent safetyを証明できない mode drift は blocker とし、mode repair authorityを発行しない。

### Plan construction

`ExecutableMutationPlan.from_assessment()` 相当は次を検証する。

- blockers が空
- root/intent/authority/contract identity が固定済み
- action path が contract boundary 内
- precondition/postcondition identity が complete
- deterministic order と canonical `plan_digest`

plan digest は absolute path、timestamp、process-specific inode 値だけに依存させず、resume に必要な root binding と relative contract/action identity を明示的に含める。

### Journal lifecycle

```text
absent
  -> prepared       # plan digest と actions を durable publish、target mutation 0
  -> executing      # action checkpoint が単調進行
  -> verifying      # all actions checkpointed、postcondition assessment
  -> completed      # postcondition success
  -> removed        # staging cleanup と finalization success
```

crash/exception では `prepared` 以降の journal を保持する。`completed` 前に削除しない。

schema-2 forward guard は journal より先に `operation_id`、`contract_identity`、canonical `plan_digest` を durable publish する。legacy conversion が exact stage lease を伴う場合は、その lease も同じ guard publish に含め、marker 置換から初回 journal 作成までの crash window で cleanup authority を失わない。journal はこの独立アンカーと一致する場合だけ作成・再開でき、journal 内部の action 順序や immutable metadata と digest をまとめて差し替えても authority を再構成できない。

journal不在のschema-2 forward guardはschema-1 conversionと区別し、既存bytes/identityを保持したままoperation/contract/planがexact一致するpre-journal状態だけを再開する。recovery metadata自身の作成で変わるdirectory ctimeはplan digestから除外するが、journal actionのexact preconditionとdevice/inode/type/linkは維持する。terminal cleanupはguardを削除するまでcompleted journalを残し、guard削除後のcompleted journal-onlyは対象mutationを再実行せずcleanupだけを許可する。旧実装が残した曖昧なguard-onlyは保持し `forward-guard-plan-mismatch` で停止する。

stage作成、atomic exchange、prune quarantine、missing parent作成は、可視namespace mutationより先に予約名またはmissing intentをjournalへ記録する。regular stageは可変write中は予約leaseを維持し、bytes/mode確定後にだけexact successor inodeへ昇格する。exchange後は、公開前から保持した stage descriptor が指す exact inode と canonical pathname が一致することを証明し、その successor leaseをdisplaced predecessor cleanupより先にdurable化する。cleanup直前にもcanonicalを同じleaseへ再照合し、same-content replacementからauthorityを再取得しない。強制終了後は予約名、exact canonical successor、displaced predecessor、空のcreated parentが単一の既知遷移に一致する場合だけforward recoveryする。same-contentでもcanonical inodeがleaseと異なる場合、またはexchange後にcanonicalが未知entryへ置換された場合はrollback/cleanupせず両entryを保持してblockする。

Action checkpoint:

- `pending`: current state は exact pre-action identity であること
- `published`: expected post-action identity を確認済み
- `verified`: operation-level postcondition に含めて再評価済み

checkpoint write failure 時は current target を再観測し、pre/post のどちらか一方に exact match する場合だけ state を再構成する。両方/どちらにも一致しない場合は block する。

### Legacy `.distribution-retry.json`

one-way conversion または compatibility resume の必須条件:

- regular file、expected schema/purpose
- marker root identity と current root binding が一致
- marker operation が current invocation と一致
- executing package version が marker/package/workspace compatibility policy を満たす
- `.uninstall-retry.json` と同時存在しない
- recorded stage ownership が exact no-follow identity に一致
- current Contract と observation から same remaining plan を一意に再構成できる

exact legacy stage lease がある場合は、対応action、private stage name family、parent chain、device/inode/ctime/type/link count を照合し、schema-2 guardと初回journalへleaseを引き継いでからcleanup/resumeする。旧実装がswap後にdesired canonicalとdisplaced predecessor stageを残した状態は、再構成actionが`adopt`でcanonical postconditionがexact一致する場合に限り、stage leaseをcleanup authorityとして変換する。guard conversion中のlegacy predecessorはschema-2 successorのcanonical identity/bytes受理が終わるまでprivate recovery nameに保持する。

一つでも証明できなければ marker を書き換えず `legacy-marker-unconvertible` とする。

### Filesystem Kernel subset

D1 で使用する operation:

- validate/open root and parent chain
- create managed directories
- stage/write/fsync/publish regular file
- create/replace exact symlink
- exact unlink proven-owned obsolete file
- apply mode
- cleanup journal-owned staging
- atomic journal publish/remove

recursive removal は D3/D4 で必要になるまで public kernel contract に入れない。ただし obsolete empty directory cleanup は owned children と emptiness を descriptor-relative に証明した範囲で許可する。

## data / failure

### Exact precondition

regular target:

```text
file_type + device + inode + link_count + size + mode + sha256
```

provider source:

```text
source device/inode/ctime/mtime/size/mode + bytes sha256
```

recovery では action record の exact SHA を参照する。historical list の index から bytes/identity を選ばない。

### Retry mismatch reason

stable internal reason を少なくとも次に分ける。

- `journal-root-mismatch`
- `journal-intent-mismatch`
- `journal-authority-mismatch`
- `journal-plan-mismatch`
- `journal-protocol-incompatible`
- `journal-precondition-mismatch`
- `legacy-marker-unconvertible`
- `dual-recovery-state`

public text は sanitization してよいが、tests と result は reason distinction を失わない。

## 変更対象

- `src/spec_dock/managed_distribution.py` の type/service/journal/kernel boundary
- recognized flow に必要なら package 内の focused module 抽出
- `src/spec_dock/cli.py` の recognized-target update/init-force dispatch と output mapping
- current distribution manifest の protocol compatibility metadata
- `tests/unit/infra/test_managed_distribution.py`
- `tests/unit/infra/test_init_update.py`
- README recovery guidance

fresh-only flow、uninstall/purge behavior、package/platform final parity は変更しない。

## 移行・互換性・rollback

- existing recognized workspace version/anchor/historical evidence contract を入力 adapter から再利用する。
- new journal 作成前の failure は mutation 0 で current command retry 可能とする。
- new journal 作成後は new/compatible package の forward recovery を使う。old package への code rollback が safe と証明されない場合は実行しない。
- cutover commit では recognized-target update/init-force の old orchestration route を削除する。fresh target の `init` / `init --force` / `update` compatibility path は D2 の ownerとして残し、recognized service から到達不能にする。
- legacy marker conversion fixture は exact current marker bytes を使い、field を推測追加した fixtureだけで成功を証明しない。

## testability

- pure assessment tests: current/historical/missing/obsolete/unknown/current-content mode-only repair/unproven mode drift block/symlink/hardlink
- plan-construction negative test: blocker 有り、unsafe path、incomplete identity、nondeterministic digest
- journal lifecycle tests: prepared/executing/verifying/completed、checkpoint failure、atomic publish failure
- resume tests: same-plan convergence、root/intent/plan/protocol/SHA mismatch
- kernel negative tests: parent/root rebind、target appearance、provider mutation、staging collision、unknown stage sibling
- CLI tests: recognized update/init-force success/error、unmanaged preservation、no prompt/backup on no-write path、current output/exit、および fresh entrypoint matrix が D1 で変化しないこと
- absence tests: recognized flow から `scaffold_applier`、legacy phase writer、plan outside mutation への dependency がない

## risk

- D1 が horizontal rewrite に膨張する risk: recognized flow の acceptance に必要な interface だけを作り、fresh/deprovision/purge action は後続 Issue に残す。
- digest canonicalization の誤り: stable serialization fixture と order permutation negative test を作る。
- marker conversion が authority を推測する risk: exact required fields と failure reason を code/test/docs で同時固定する。
- current behavior drift: existing tests を先に characterization し、新実装の都合で unknown preservation expectation を弱めない。
