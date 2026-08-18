---
種別: ADR（Architecture Decision Record）
ID: "20260818t031610z-adr"
タイトル: "Unified Distribution Reconciliation And Forward Recovery"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-08-18"
親: ["epic-00365"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-08-18"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: ["20260818t030454z-disc-epic-365-distribution-reconciliation-authoring-brief.md"]
reflected_to: ["epic-00365", "iss-00368", "iss-00369", "iss-00370", "iss-00371", "iss-00372"]
---

# 20260818t031610z-adr Unified Distribution Reconciliation And Forward Recovery

architecture / contract / migration の判断を記録する。これは `accepted` ADR であり、Epic 365 の cross-Issue decision authority とする。個別 behavior の正本は各 canonical Requirement、構造の詳細は Design、実装順は Plan に置く。

## Context

exact commit `51a0586f8eb02f622f386a1fe32f15d90fcac4bc` では、managed distribution の read-only classification と identity-checked apply が `managed_distribution.py` に存在する一方、fresh scaffold と uninstall lifecycle には `cli.py` 所有の別 mutation path、別 action type、別 retry marker が残る。現行 behavior は unknown/modified content preservation、symlink/hardlink/root-rebind rejection、uninstall dry-run、explicit `--remove-specs` など重要な安全契約を持つため、単純な rewrite や一括置換は受け入れられない。

判断が必要な論点は次のとおりである。

- all public intent を一つの operation model に統合するか。
- blocker のない path だけを部分適用するか、operation 全体を pre-write block するか。
- partial failure を whole-operation rollback で扱うか、journaled forward recovery で扱うか。
- managed deprovision と spec history purge を同じ authority とみなすか。
- legacy path を長期 dual mode で残すか、vertical flow ごとに hard cutover するか。

## Decision

### 1. Unified operation model

`init`、`init --force`、`update`、managed distribution deprovision、explicit spec history purge は、一つの Distribution Operation Service、Distribution Contract、Workspace Assessment、action grammar、Descriptor-bound Filesystem Kernel、Operation Journal、typed ProcessResult を共有する。

CLI は adapter とし、ownership policy、recursive mutation、journal transition、staging cleanup、operation 固有 action model を持たない。distribution invariants の owner は `managed_distribution.py` または同じ domain boundary の明示的な module 群とする。

### 2. Pre-write fail-closed

eligibility、observation、ownership assessment、plan construction は side-effect free とする。blocker が一件でもあれば executable plan を発行せず、operation 全体を最初の write より前に停止する。safe subset の部分適用は行わない。

unknown、modified、user-owned content は、explicit spec history purge authority の境界内を除いて保持する。pathname や managed root の membership だけで ownership を推測しない。

### 3. Journaled forward recovery

partial failure の正規 recovery は Operation Journal による forward recovery とし、whole-operation atomic rollback は保証しない。

journal は root binding、intent、authority、package/contract/protocol identity、plan digest、ordered action、checkpoint、staging lease を持つ。mutation resume は same root、same intent、exact same authority、same reconstructable plan、compatible protocol に限定する。lower-authority invocation は journal の read-only inspection と diagnostic だけを許可し、action 実行や checkpoint 更新を行わない。

regular-file recovery は exact pre-action SHA-256 と expected post-action SHA-256 を使う。historical catalog の index、配列位置、pathname 推測を pre-state identity として使わない。未完了 action が exact pre-state、完了 action が exact post-state に一致しない場合は ambiguous として write 前に停止する。

postcondition 成功後だけ journal と staging lease を完了・除去する。new journal 作成後の code rollback は、その code が protocol を理解できると証明されない限り正規経路にしない。同一または compatible newer package で forward recovery する。

### 4. Deprovision と purge の authority separation

managed distribution deprovision と spec history purge は同じ engine を使うが、別 intent、別 authority、別 postcondition とする。

- deprovision は current `uninstall --apply --keep-specs` 相当であり、spec history と authority 外 unknown content を保持する。
- purge は current `uninstall --apply --remove-specs` 相当であり、explicit `--apply` と `--remove-specs` の組合せだけが authority を与える。
- `update`、fresh/force init、deprovision、retry/resume は purge authority を暗黙取得できない。
- journaled retry で deprovision から purge へ昇格できない。

新 command/flag は追加しない。現行 dry-run、human text、JSON schema version 1、exit semantics を compatibility adapter で維持する。

### 5. Vertical hard cutover

D1〜D4 は public flow ごとの vertical slice とし、新 engine への切替と対象 legacy path の削除を同じ Issue で完了する。長期 dual mode、runtime toggle、二重 writer は採用しない。

- D1: recognized target の `update` / `init --force`
- D2: fresh target の `init` / `init --force` / `update`
- D3: default/`--keep-specs` dry-run と managed deprovision apply
- D4: `--remove-specs` dry-run/apply による explicit history purge
- D5: remaining legacy seam absence と distribution/platform parity の確定

## Options

### 棄却: operation ごとの既存 engine を維持し、共通 helper だけ増やす

短期差分は小さいが、action grammar、marker、postcondition、recovery authority の二重化が残り、failure behavior の drift を防げない。

### 棄却: blocker のない path を先に適用する

一部進行後の workspace state と retry reasoning が複雑になり、unknown content を巻き込む data-loss risk と診断負荷が増える。安全性より可用性を優先する根拠がない。

### 棄却: whole-operation rollback

filesystem tree 全体の rollback を正しく保証するには user-owned content、external mutation、crash timing、platform behavior を包含する汎用 transaction framework が必要になる。Epic scope を超え、誤った原子性保証になる。

### 棄却: exact same package だけ resume

開始 package の bug で永久に recovery 不能になる。protocol compatibility と same-plan reconstruction を証明できる compatible newer package を許可する方が、安全性と forward fix を両立する。

### 棄却: latest package なら無条件 resume

plan/authority/protocol drift を許し、元の mutation authority を超える可能性がある。same root/intent/authority/plan と明示的 protocol compatibility を必須にする。

### 棄却: deprovision と purge を一つの uninstall authority とする

spec history deletion が通常の lifecycle cleanup へ混入する。明示的な data-destruction authority と dry-run/confirmation boundary を失う。

### 棄却: 長期 dual mode または一括 big-bang cutover

長期 dual mode は drift を固定化し、big-bang は rollback blast radius を増やす。vertical slice ごとの hard cutover が、observable value と code rollback boundary を両立する。

## Consequences

### Positive

- public flow 間で ownership、failure、recovery、diagnostic の意味が揃う。
- pre-write blocker と authority separation により user-owned data の誤変更 risk が下がる。
- per-action exact identity と journal checkpoint により、partial failure を推測なしで再照合できる。
- filesystem safety mechanism の唯一の owner を形成できる。
- Issue ごとに end-to-end behavior と legacy removal を検証できる。

### Cost

- D1 は recognized flow を完了するため、contract/assessment/kernel/journal/result の最小 vertical foundation を同時に導入する必要がある。
- legacy marker の情報不足により、自動変換できない recovery case が残る。特に current `.uninstall-retry.json` は root/intent/plan/checkpoint を証明できず、fail-closed manual recovery が必要になり得る。
- Linux/macOS の syscall/capability evidence と package surface parity の維持コストが増える。
- internal journal schema と plan digest の versioning discipline が必要になる。

### Non-consequences

- Windows support は追加しない。
- Full Regression の既存 failure は修復しない。
- AI review orchestration を product に戻さない。
- generic transaction framework を作らない。
- whole-operation rollback を約束しない。
- existing node metadata title/path を手編集しない。

### Revisit conditions

次のいずれかが判明した場合は、この ADR を supersede する新しい明示判断が必要である。

- per-action forward recovery では public data-preservation contract を満たせない実証例
- Linux/macOS の required filesystem capability が production environment で安定提供されない証拠
- public JSON contract を維持したまま typed result に統合できない外部 consumer evidence
- exact pre/post identity だけでは crash state を一意判定できず、追加 durable evidence が必須となる failure mode

## References

- `20260818t030454z-disc-epic-365-distribution-reconciliation-authoring-brief.md`
- `epic-00365` Requirement / Design / Plan
- `iss-00368` Recognized Workspace Reconciliation
- `iss-00369` Fresh Distribution Provisioning
- `iss-00370` Managed Distribution Deprovision
- `iss-00371` Explicit Spec History Purge
- `iss-00372` Distribution Hard Cutover And Parity
- exact implementation authority: `51a0586f8eb02f622f386a1fe32f15d90fcac4bc`
