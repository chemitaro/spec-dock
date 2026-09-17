---
種別: artifact
ID: "20260917t162312z"
タイトル: "Issue #396 strict review remediation analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-09-18"
親: ["iss-00396"]
template: "blank"
authority: "evidence"
derived_from:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "artifacts/20260917t124918z--luna-max-implementation-handoff.md"
  - "artifacts/20260917t124918z-01--b1-b2-gate-receipt.md"
  - "artifacts/provider-gate-contracts-v1.schema.json"
  - "artifacts/role-ownership-v1.json"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "artifacts/20260917t124918z--luna-max-implementation-handoff.md"
---

# Issue #396 Strict review remediation analysis

## 1. 対象と判断

初回Strict reviewはRed reviewer session `iss396-spec-review-red`で実行された。Blue分析は独立session `iss396-blue-analysis`で行われ、両方とも`gpt-5.6-sol`のPro推論を指定したStrict browser routeを使用した。レビュー候補SHAは`3ded647d247b9399a4b79ad6f854d6a87fbf4313`、treeは`614778cc7e6e64609a7de80bf2428b3e7f5ec4b7`。初回結果はP0=0、P1=8、P2=2、P3=1、`review_status=fail`だった。

対象はIssue #396のRequirement、Design、Plan、Luna Max handoff、およびそれらを機械的に閉じる必要があるIssue-level schemaとtest ownership artifactである。親`E384-QUAL-001`、accepted ADR、#392/#395の実装範囲、Issue #396 Product source/workflow/test、GitHub settingsは変更対象ではない。

Epic #384の現在のPlanとentry receiptを照合した結果、前回の報告時点では不足していたB1/B2は、#395のpost-merge exact SHA `fd5df1d64b5d7ebf7bd4b41bb35fd8760d17e65d` / tree `37eabc1aa250838dcd9f61d627309b0ff27e0db7`で後日実施され、現在はentry evidenceとして記録済みである。B1はcurrent gates GREEN、B2は`2188 passed, 26 skipped`、15/0/15、violations 0だった。これは#396の開始入力だけを満たす。Issue #396のreplacement gate、required-context切替、B3、Epic main受入を満たす証拠ではない。

判断は`documentation-correction`である。全P1はR/D/P/handoff/schema間の契約補完で解消でき、親Qualification policyの変更やProduct実装を必要としない。仕様修正・artifact同期・検証の後に、同じRed reviewer sessionで再レビューする。

## 2. P1別の検証と修正結果

| # | 初回指摘 | ローカル証拠と判定 | 正本へ反映した修正 |
|---:|---|---|---|
| 1 | `bundle_sha256`がmanifest self-referenceを起こし、final manifest digestも存在しない | 初回Design §5.3ではbundleの入力に完成manifest全体を含めていた。完成manifest自身へbundle digestを書き戻す循環が成立するため有効なP1。 | Acyclic core/bundle/final-manifest digest DAGをRequirement/Design/Schemaに定義。coreはfields 1–12、bundleはraw core digestとfilename byte順のmetadata/実bytes、final manifest digestは完成bytesから計算しmanifest外のEvidenceIndex/producer receipt/CandidateIdentityだけに置く。Goldenで各中間digestを固定する。 |
| 2 | 集約結果とEvidenceIndexのclosed schemaがない | 初回Designはfield名のみの結果と未定義のEvidenceIndexを示し、実装者が型/null/completenessを推測する状態だった。 | `provider-gate-contracts-v1.schema.json`へCandidate/Source/Environment/Attempt/Role/Process/Campaign/Fault/Window/Qualification/EvidenceIndex/ProtectedSnapshot/Packet/StopReturn/RoleOwnershipとnested typeを集約。objectはunknown keyを拒否し、required・nullability・enum・配列順序・key順を定義する唯一のwire authorityとした。Runtime copyはbyte-identicalを要求する。 |
| 3 | test ownershipが実装時まで未確定 | source SHA `3ded647...` / tree `614778...`で採取したLinux/macOS collect-only出力を実byte照合。双方2,214 unique node、normalized set hash一致、集合差0。ownerはLinux 2,191、sdist 1、macOS 22でunion complete・intersection empty。 | `role-ownership-v1.json`へ全2,214 node assignment、baseline identity、normalized set hash、raw evidence refsを保存。raw Linux/macOS outputを同artifact directoryに追加。新しい/移動したnodeはbody実行前のcollection-only差分と明示owner登録を必須にし、旧markerから推定しない。 |
| 4 | legacy policy skipがreplacement GREENを循環的に阻害 | 現行`tests/conftest.py`のcollection hookはold marker/policy skip/ledger classificationを行う。role外integration nodeが旧hookでskipされ、replacementがpolicy skipを拒否する経路では旧hook削除までGREENにならない。 | Design/Requirement/Plan/Handoffへ一時transition seamを統一。通常/旧pytestは現行挙動を保ち、role modeは明示`--provider-gate-role`と`-p scripts.quality.provider_gate.pytest_plugin`を要求。root hook先頭からschema・全node assignmentを検証し一度だけ選択を委譲、legacy skipを付けずに戻る。plugin不在/unknown node/schema不正/legacy flag併用はbody開始前に失敗。consumer-zero後P15でseamとold hookを削除する。 |
| 5 | producer command、run-attempt、PR source SHAが不一致 | 初回Planは必須run metadataを渡さず`GITHUB_SHA`を使い、Handoffはrun ID/attempt必須であり、PR head SHA mappingも未定義だった。 | `SourceIdentityV1`と`resolve_source_identity`をevent別に定義。PRはhead SHA/repository、dispatchはrequired `inputs.source_sha`、merge_groupはmerge-group SHA。Producer commandはSourceIdentity fileとrun ID/attemptを渡し、同一attempt内の各roleは同一identity bytes、後続runは別run identityでsource SHA/treeだけCandidateManifestと一致させる。GitHub公式event仕様へのリンクをDesignに明記。 |
| 6 | old required contextを残したままemitter削除 | 初回P15で旧check emitterを削除し、P20でold required contextを初めて外す順だった。Required old checkが出ないIssue PRをmergeできない循環になるため有効なP1。 | P13はold/new共存とintentional RED/GREENまで。P14でconsumer-zeroを証明し、old emitterを残した状態でHumanがold contextだけを削除し、`U + new`とmerge_group coverageをreadback。P15はreadback後に限りemitterを削除。P17は`U + new`と旧emitter absenceを検証し、P20は設定変更せずreadbackのみ。 |
| 7 | execution packetが複数checkpoint rangeを許し、B2 pathsとP03 scriptを閉じない | 初回Handoffは`P01-P22`を一つの`authorized_checkpoint`に渡し、P01のB2 artifact変数とP03 snapshot helperをpacketで特定できなかった。 | `ExecutionPacketV1`のenumは一つのP00–P22のみ。`authorized_checkpoint == checkpoint_inputs.checkpoint_id`、Plan section SHA、EvidenceIndex ref、write boundaryとallowlistを必須化。B2のexact Issue artifact paths/hashをschemaで固定し、P03はreview済み`capture_protected_snapshot.py`とSHA-256を指定する。Implementationは`implementation_authorized=false`のまま。 |
| 8 | PlanとHandoffのStopReturn JSONが競合 | Planは`owner/scope_impact`、Handoffは`verified_facts/hypotheses/operations`を要求し、単一payloadで両立しない。 | `StopReturnV1`をschema一つへ統合。Plan §28とHandoff §17は同じschema `$ref`だけを示し、独立JSON field listを削除。 |

## 3. 共通原因と修正の境界

1. **Wire contractが文章で二重化されていた。** Schemaを唯一のfield authorityにし、要件・設計・handoffはsemantic ruleとschema referenceを担当する。
2. **候補識別子、実行attempt識別子、集約識別子の境界が混ざっていた。** Hash DAGとevent-resolved SourceIdentityを分け、producer provenanceと後続run provenanceを同一視しない。
3. **実装中に受入母集団を決める余地があった。** Exact ownership baselineとcollection evidenceをレビュー前に固定し、差分時の更新順序を明記する。
4. **置換・削除の時系列に循環があった。** Transition seamとHuman settings gateを旧hook/emitterが存在する期間に置き、consumer-zero/readbackを削除の前提にする。

修正範囲はIssue #396の仕様文書とplanning/support artifactsに限定した。Product source、test source、workflow YAML、required-context/ruleset settings、Epic parent qualification valuesは変更していない。Strict pass後もProduct implementation permissionは自動ではtrueにならず、GitHub Issue projection readback、explicit user dispatch、concurrent-writer absenceを別途必要とする。

## 4. P2/P3の扱い

初回reviewのP2二件とP3一件は、review methodの境界どおり記録のみとする。これらを直す変更、タスク化、再レビュー条件化は行わない。最新版のRequirementにあるentry-state表の正確性に関するP2も、記録された指摘の範囲を越えて修正しない。

## 5. 残る外部gate

- Independent Strict reviewが`review_status=pass`かつP0/P1=0であること。
- GitHub Issue #396 body projectionの更新とreadback。
- Product implementation dispatchと実行packet。
- P02でeffective required-context/ruleset/merge queue、runner class/limits/image、artifact retentionをread-only captureできること。
- P14でHumanのold context removalと`U + new` readbackが成功すること。
- B3は#396のfinal sourceがEpic branchへ人間mergeされた後に別identityとして実行すること。

この分析はこれら外部事実が既に成立したとは主張しない。
