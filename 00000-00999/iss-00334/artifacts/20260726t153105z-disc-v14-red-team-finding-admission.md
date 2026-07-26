---
種別: disc
ID: "20260726t153105z-disc-v14-red-team-finding-admission"
タイトル: "iss-00334 Candidate v14 Fresh Red Team Finding Admission"
状態: "resolved"
作成者: "Codex Main"
最終更新: "2026-07-27"
親: ["iss-00334", "epic-00331", "init-00322"]
authority: "main-finding-admission"
adoption_status: "decided"
candidate_id: "iss-00334-v14-20260726t142121z"
candidate_sha256: "cb7a0a9755d7d172c0bf469d47086f4f090f3bcd117ebd9341cd0a96073c17c8"
candidate_source_head: "feefb9e8e96015e48cdb1f837e8f775da8b3d8aa"
review_thread_id: "6a6621ad-d8fc-83ee-a2c1-f44aafe55b81"
review_artifact: "20260726t152913z-chatgpt-output-v14-fresh-red-team-review.md"
review_artifact_sha256: "30a6eaa65a92bd9fc20b2dc0f974a9e0227a2d9bb7ae16a23eadcd8a720a1ec1"
---

# iss-00334 Candidate v14 Fresh Red Team Finding Admission

## 1. 対象

Main Finding Admission Gateは、次のimmutable Candidateとfresh read-only Red Team reviewだけを対象にした。

- logical filename: `20260726t142121z-iss-00334-issue-planning-candidate-v14.zip`
- Candidate ID: `iss-00334-v14-20260726t142121z`
- external SHA-256: `cb7a0a9755d7d172c0bf469d47086f4f090f3bcd117ebd9341cd0a96073c17c8`
- source HEAD: `feefb9e8e96015e48cdb1f837e8f775da8b3d8aa`
- Red Team thread: `6a6621ad-d8fc-83ee-a2c1-f44aafe55b81`
- preserved review: `20260726t152913z-chatgpt-output-v14-fresh-red-team-review.md`
- preserved review SHA-256: `30a6eaa65a92bd9fc20b2dc0f974a9e0227a2d9bb7ae16a23eadcd8a720a1ec1`
- Red Team verdict: `FAIL`
- proposed counts: P0 `0`、P1 `3`、nonblocking `0`

Candidateのdeterministic preflightは`121/121 PASS`であり、archive identity、inventory、checksums、source blob、planned-absent path、禁止済みscope-ratchet patternにfailureはなかった。

## 2. Admission結果

| Finding | Main disposition | Candidate revision | 判断 |
|---|---|---|---|
| RT-001 | `accepted_blocker` | required | 親EpicのE1-I1 end-to-end責務、Initiative DesignのIssue Candidate構成、ADR 20のIssue package義務に対し、v14はChatGPTの三文書responseからmandatory control filesを含むimmutable ZIPへ変換するownerとintegration testを閉じていない。 |
| RT-002 | `rejected_overreach` | prohibited | 同一Blue thread継続はinit-00322限定の暫定運用契約であり、Charter自身がnon-authoritative evidenceかつ将来標準への自動適用禁止を宣言している。D-001〜D-024、親canonical docs、accepted ADRはSemantic Revisionのcomplete replacementとnew identity/fresh reviewを要求するが、恒久product contractとしてsame-thread locatorを要求していない。現在の修正運用では引き続き同一Blue threadを使う。 |
| RT-003 | `accepted_blocker` | required | v14自身のREQ-019とDesign 8.2はexisting safe ZIP primitiveのextension/reuseを要求する一方、S05のexact target/allowed pathsはhard-coded generic root/metadataを持つ既存`authoring_pack` primitiveのbounded extensionを禁止しており、実装可能性に内部矛盾がある。 |

## 3. Blue Teamへ渡す修正契約

Blue Teamへ渡すのはRT-001とRT-003だけとする。RT-002をCandidate変更へ反映してはならない。

### 3.1 RT-001 — Candidate packaging責務を閉じる

必要最小限の修正は次のとおり。

1. ChatGPT Planner responseとRuntime final artifactを分離して明記する。
   - ChatGPT Planner response: complete `requirement.md`、`design.md`、`plan.md`。
   - Runtime final artifact: mandatory control filesを付与したimmutable Issue Candidate ZIP。
2. Issue Candidate ZIPには少なくとも三文書、`SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`を含める。
3. logical filename、version、Candidate ID、internal root、source binding、external ZIP SHAをdeterministically確定するowner stepをS03またはS05の一方へ置く。
4. `planning create`の結果を、そのまま`archive-candidate` Review inputへ渡せることを一本のfocused integration testで閉じる。
5. 新しいpackaging subsystem、state store、proof matrix、追加Review authorityを作らない。

### 3.2 RT-003 — shared archive primitiveのbounded extensionを許可する

必要最小限の修正は次のとおり。

1. S05のexact target/allowed pathsへ、既存`authoring_pack` archive safety primitiveを後方互換に拡張するために本当に必要な既存pathを追加する。
2. hard-coded generic authoring-pack root/metadata contractを壊さず、Issue Candidate向けroot、required metadata、limits、identity validationをbounded parameterまたはshared primitiveとして再利用できる設計を明記する。
3. existing generic authoring-pack behaviorが不変であるfocused regressionと、Issue Candidate固有契約のfocused positive/negative testをS05で閉じる。
4. parallel validator、allocator、general archive framework、全resource matrixを新設しない。

## 4. RT-002の運用上の扱い

RT-002をproduct requirementへ昇格しない一方、現在のinit-00322 Candidate修正サイクルでは暫定Charterをそのまま適用する。

- v15修正はv14を生成した専用Blue Team thread `6a65399a-4940-83e8-a955-8c3a731b68a8`で継続する。
- Blue Teamにはこのadmission結果と保存済み正式Reviewだけを追加で渡す。
- v15は新version、timestamp、Candidate ID、internal root、MANIFEST、CHECKSUMS、external ZIP SHAを持つcomplete replacementとする。
- v14を上書きしない。
- v15は別のfresh Red Team threadでreviewする。

## 5. 禁止するscope拡張

- RT-002のsame-thread locator、session registry、new persistent stateの恒久product contract化。
- 固定件数source ledger、sole-owner proof matrix、全ID対応表、全resource matrix。
- allocator subsystem、S00/G0、self-review、review transcript packaging。
- assurance、severity、blocking、reviewer semanticsの変更。
- current Portfolio、downstream Issue、shared delivery／merge／finish policyの変更。

## 6. 次アクション

1. 本Admissionと保存済みReviewをcommit/pushし、GitHub上のsource HEADを更新する。
2. 同一Blue Team threadへRT-001、RT-003だけを渡し、complete Candidate v15を生成する。
3. v15へdeterministic preflightを行う。
4. v15を新規fresh Red Team threadでreviewする。
5. PASSまたは新しいMain Finding Admissionまで、旧Candidateと旧Reviewをimmutableに保持する。
