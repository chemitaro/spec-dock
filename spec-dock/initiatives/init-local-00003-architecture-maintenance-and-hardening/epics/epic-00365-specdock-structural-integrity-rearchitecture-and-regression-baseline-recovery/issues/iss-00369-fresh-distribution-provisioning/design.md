---
種別: 設計書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

D1 の unified engine に `fresh` intent policy と creation postcondition を追加し、fresh `init` を end-to-end cutover する。fresh 専用差分は Distribution Contract と intent policy に限定し、別 planner、別 action、別 kernel、別 journal を作らない。

## Current / Target

### Current

- CLI admission が target を fresh/recognized/retry に分類する。
- fresh path は managed distribution plan に加えて scaffold copy/apply と fresh-only workbench README seed を扱う。
- `apply_distribution_plan()` の callback seam により、action list外のmutationを実行できる。
- current testsはfresh install root bytes、managed skills/scripts/templates、second init、workbench seed/ignore behaviorを確認する。

### Target

- `fresh` をD1の`OperationIntent`に追加する。
- Distribution Contractがfresh-only desired assetsとrequired directoriesを明示する。
- Assessmentはtarget rootのunrelated contentを無視せず安全に観測するが、managed pathsとのcollisionだけをblockerにする。
- planは全create/ensure-directory/mode/symlink actionを明示し、callbackなしでkernelへ渡す。
- journalとpostconditionはfresh intent/planに束縛する。

## 責務・Interface

### Fresh contract overlay

D1 contractに次を追加する。

- fresh desired asset set
- fresh-only seed asset set
- required managed directory set
- allowed absent-parent creation policy
- collision policy
- prompt/backup policy
- fresh completion postcondition

fresh-only seedはcurrent package resourceとmanifestでidentityを固定し、hard-coded CLI copy stepにしない。update/init-force contractから参照しない。

### Assessment

fresh assessmentは次を分類する。

- managed path absent → create candidate
- exact desired target present → existing collisionとしてpublic second-init policyへ渡す。silent adoptでinit成功にしない場合は現行contractを維持する。
- parent absent → ensure-directory candidate
- parent real directory and safe → continue
- parent/target symlink、unsafe type、non-writable、unproven existing target → blocker
- unrelated root content → preserve、non-blocking

prompt/backup decisionはassessment resultの`mutation_required`とpublic init policyから導出する。assessment自体はIO read-onlyであり、promptを呼ばない。

### Plan ordering

1. journal prepared
2. managed parent directoriesをtop-downにensure
3. regular/symlink assetsをdeterministic orderでstage/publish
4. mode/post-publish identityをverify
5. fresh-only seed assets
6. version/state artifact
7. full postcondition assessment
8. journal completion/staging cleanup

各createはexpected absent identityをpreconditionとする。destinationが出現した場合はno-replace failureとし、上書きへfallbackしない。

### Directory recovery

created directoryはjournal actionとしてcheckpointする。resume時:

- directory bindingがexpected identityと一致し、authority外childがない/またはpreserve policyで安全なら継続する。
- external childが出現してplanと衝突する場合はblockする。
- rollback目的でnon-empty directoryをrecursive removeしない。

### Prompt/backup adapter

CLI adapterはserviceの`mutation_required` result後、apply開始前だけcurrent prompt/backup contractを実行する。prompt acceptance後は同じassessment/plan digestを再検証し、TOCTOUがあれば再assessmentまたはblockする。no-op/block/dry assessmentではprompt/backupなし。

## data / failure

- fresh journalは`intent=fresh`を固定し、update/init-force journalとしてresumeしない。
- expected-absent preconditionはparent/root bindingとともに記録する。
- created directories、files、symlinks、mode、versionのpostconditionをaction recordに持つ。
- backupを作るcurrent contractが適用されるcaseでは、backup path/identityもjournal authority内に明示する。current behaviorにbackupがないcaseへ新規作成しない。
- partial create後のretryはcompleted post-stateをadoptし、pending expected-absent actionだけを実行する。unknown divergenceはblockする。

## 変更対象

- D1 service/contract/assessment/plan/kernel/journalへのfresh overlay
- `src/spec_dock/cli.py` fresh dispatch/prompt/backup adapter
- packaged fresh desired/seed metadata
- fresh tests in `test_managed_distribution.py` / `test_init_update.py`
- README init/retry guidance

recognized flow、uninstall/purge、JSON schemaは変更しない。

## 移行・互換性・rollback

- existing fresh package assetsとbyte/mode/symlink contractをsource of truthにする。
- cutoverでfresh pathのcallback/scaffold copierを削除し、new serviceだけをwriterにする。
- old fresh retry markerがD1 conversion conditionを満たす場合だけfresh journalへ移す。intent mismatchはblockする。
- new journal作成後はforward recovery。old codeがnew protocolを理解しない場合はcode rollbackだけでconsumer operationを再開しない。
- provider package rollbackは未開始consumerには可能。進行中journal consumerにはcompatible recovery pathを先に提供する。

## testability

- empty fresh root、unrelated existing root content、managed path collision
- missing nested parents、non-directory parent、symlink parent/final、non-writable path
- destination appearance between assessment/apply
- directory created then later failure
- provider source mutation
- prompt/backup called only onmutation-required path
- second init without force
- fresh journal resumed asupdate/init-force rejection
- fresh-only seed exists after fresh init、not backfilled by update/force
- provider catalog vs fresh consumer byte/mode/link parity
- absence of scaffold callback/alternate copier from fresh call graph

## risk

- fresh asset inventoryをcurrent catalogと重複管理するrisk: Contract builderでsingle physical sourceから派生させる。
- directory cleanupがuser contentを巻き込むrisk: forward recoveryを優先し、unknown childを含むrecursive rollbackを禁止する。
- prompt後TOCTOU: plan digest/root identityを再検証する。
- D1 journal schemaをfresh都合で破壊するrisk: protocol versioningとbackward compatibility testを使う。
