---
種別: 設計書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

D1/D2のunified engineへ`deprovision` intentを追加し、dry-run、owned removal、preservation、journaled apply、postcondition、public JSON mappingをend-to-end接続する。current CLI-owned `_UninstallAction` grammarとrecursive mutationをcommon domain/kernelへ移す。

## Current / Target

### Current

- `_build_uninstall_plan()`がcategory/status/reasonを持つ`_UninstallAction`を構築する。
- `_apply_uninstall_plan()`と複数の`_remove_uninstall_*` helperがdescriptor-relative removalを行う。
- `_uninstall_payload()`がschema version 1のtext/JSON dataを作る。
- `.uninstall-retry.json`はminimal purpose markerで、root/intent/plan/checkpointを持たない。
- testsはdry-run、keep/remove、preserved content、symlink/hardlink、partial failure、retry guidanceを広く固定する。

### Target

- `deprovision`をcommon `OperationIntent`とauthority policyへ追加する。
- current uninstall classificationをcommon disposition/actionへmappingする。
- recursive removeをDescriptor-bound Filesystem Kernelのbounded operationにする。
- dry-runはassessment/planから`ProcessResult(planned)`を返す。
- applyはcommon Operation Journalを使い、spec history rootをpreserve postconditionに含める。
- current JSONはCLI compatibility mapperで維持する。

## 責務・Interface

### Deprovision authority

```text
intent = deprovision
authority = remove-owned-distribution; preserve-spec-history
```

authorityは次を許可する。

- current/historical evidenceでproven-ownedなtooling/managed assetのremove
- generated state policyでownedと定義されたpathのremove
- owned children除去後のempty managed directory cleanup

次を許可しない。

- `spec-dock/initiatives` spec historyのremove
- unknown/modified/user-owned contentのremove
- repository boundary外のremove
- retry時のpurge authority取得

### Dry-run

`assess()`と`build_plan()`までを実行し、journalを作らない。blockerを含む場合もdiagnostic plan/resultを返せるが、apply可能な`ExecutableMutationPlan`とは型を分ける。public action status/category/reasonはcurrent JSON semanticsへmappingする。

### Removal action

common grammarへ次を追加する。

- remove exact regular file/symlink
- remove bounded tree whose root and every child are authority-covered
- remove owned empty directory
- preserve path/root
- block operation

bounded tree removeはdirectory descriptorからchildrenをno-follow列挙し、各entryのidentity/authorityを検証する。unexpected symlink、hardlink、unsafe type、unknown childはfollowせずblockする。preserved descendantがあるdirectoryはremoveしない。

### Postcondition

- owned tooling/generated/managed targetsがabsentまたはexplicit preserved disposition
- spec history rootsとcontentsがpre-operation identityに一致
- authority外unknown contentがpre-operation identityに一致
- journal-owned staging以外のunknown stage-like entryがunchanged
- no outside sentinel change

### JSON compatibility mapper

current schema version 1の少なくとも次のsemantic fieldを維持する。

```text
schema_version, target, mode, apply, specs_mode, status,
phase, last_completed_phase, retry_command,
failed_paths, pending_paths, summary, actions, guidance, errors
```

action fields `path`, `category`, `status`, `reason`, `error`を維持し、failure時のabsolute target/error sanitizationとexactly one stdout JSON objectを保つ。internal action/result名をpublic schemaへ露出しない。

### Legacy uninstall marker

current `.uninstall-retry.json` はoriginal specs mode、root identity、plan digest、checkpointを証明しない。原則:

- marker存在をrecognized recovery stateとして検出する。
- new deprovision journalへのautomatic conversionは行わない。
- current-compatible packageでlegacy operationを完了するか、operatorがevidenceを確認するmanual recovery guidanceを返す。
- markerを削除・上書きしてfresh operationとして進めない。

exact conversionに必要な追加evidenceがcurrent treeから一意に得られることを実装で証明できたcaseだけ、narrow adapterを許可する。less-authority intentであってもroot/plan ambiguityを無視しない。

## data / failure

- deprovision journalは`intent=deprovision`とauthorityをdigestに含める。
- remove actionはexact pre-action identityを持つ。regular fileはSHA-256、symlinkはlink target、directory treeはroot bindingとchild authority digestを持つ。
- checkpoint済みremoveはexpected absentをre-observeする。pending removeが既にabsentなら、journal/postconditionから一意にoperation-owned deletionと証明できる場合だけcompleted扱いにする。
- partial recursive removalでunknown divergenceを見つけた場合、remaining actionを停止しjournalを保持する。whole tree rollbackは行わない。

## 変更対象

- common contract/assessment/action/journal/kernelへのdeprovision extension
- `cli.py` uninstall dry-run/apply dispatchとJSON/text mapper
- current uninstall legacy helperのdeprovision route
- `test_init_update.py` uninstall scenarios
- `test_managed_distribution.py` common remove/journal/kernel tests
- README uninstall/recovery guidance

`--remove-specs` executionはD4まで切り替えない。

## 移行・互換性・rollback

- dry-run firstでnew assessmentとcurrent classificationのsemantic parityを確認する。
- apply cutoverとlegacy deprovision plan/apply/postverify removalを同じchange setで行う。
- new journal作成後はforward recovery。legacy markerは推測変換しない。
- code rollbackはnew journal開始前まで。進行中new journalはcompatible packageで完了する。
- spec history preservation mismatchが一件でもあればjournal finalizationを拒否する。

## testability

- dry-run no-write snapshot
- keep-specs successful removal
- modified/unknown file preserve/block
- initiatives/spec history byte identity
- bounded cleanup with preserved descendant
- symlinked boundary/root/child、hardlink、parent/root rebind
- partial remove/journal/checkpoint/postcondition failure
- deprovision-to-purge resume rejection
- legacy marker unconvertible behavior
- JSON golden fields/one-object/sanitized errors/retry guidance
- absence of `_UninstallAction` grammar and CLI recursive mutation for deprovision

## risk

- current JSON consumer breakage:golden schema/semantic testsをcutover gateにする。
- recursive removeのblast radius:authority-covered child setとdescriptor-relative identityを必須にする。
- legacy markerをless-authorityとして安易にconvertするrisk:root/plan ambiguityもblock conditionにする。
- spec history preservationをpostconditionで見落とすrisk:pre/post tree identity fixtureを必須にする。
