# iss-00354 S08 Fresh Red Team Review v3

## 結論

# **PASS**

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  0 |
| P2       |  0 |
| P3       |  0 |

S08 authoritative quality receipt の PASS と S08 Red review gate は別に判定した。authoritative quality verification HEAD は引き続き `c9c59bd507daf9f7909e5c6a216d856aab472a49` であり、今回の fresh v3 は exact reviewed source HEAD `8c807bb4a799f8c489ca1131588e22763ff3c7db` に対する Red gate 判定である。

Red v2 の唯一の P1 `RT-354-S08-V2-001` は解消されている。Final Commit row は、その行を含む commit SHA を literal として自己参照せず、`current_pushed_head` を named branch tip の ref identity として扱い、その時点の exact SHA を fresh review identity で固定する契約へ変更された。今回の review identity が current tip `8c807bb4…` を外部から exact に固定するため、旧 SHA を current tip と誤認させる状態はない。

---

## 1. Repository identity

| 項目                              | 確認結果                                       |
| ------------------------------- | ------------------------------------------ |
| Repository                      | `chemitaro/spec-dock`                      |
| Named branch                    | `codex/iss-00354-chatgpt-context-contract` |
| Exact reviewed source HEAD      | `8c807bb4a799f8c489ca1131588e22763ff3c7db` |
| GitHub branch / HEAD comparison | `identical`                                |
| Ahead / behind                  | `0 / 0`                                    |
| Default branch fallback         | **未使用**                                    |
| Review mode                     | fresh v3 / read-only / defect-only         |
| GitHub確認日                       | 2026-08-06                                 |

GitHub Connector で named branch と指定 source HEAD を直接比較した。named branch tip、base commit、merge-base はすべて `8c807bb4a799f8c489ca1131588e22763ff3c7db` で一致した。指定 commit 自体も GitHub 上で取得できた。

`main` は repository の default branch であるが、ファイル取得、commit比較、判定のいずれにも使用していない。

---

## 2. 添付 MANIFEST 相当一覧

指示上は「7ファイル」だが、canonical/raw を個別物理ファイルとして数えると **7論理項目・9物理ファイル**である。9物理ファイル、合計 **4,079行 / 475,766 bytes** を全文確認した。

添付 bytes から Git blob SHA-1を算出し、GitHub exact HEAD `8c807bb4…` の対応 blobと比較した。全件一致した。

| 論理項目 / 物理ファイル                                                                         |    行数 / bytes | 添付 SHA-256                                                           | GitHub blob                                  | 結果                  |
| ------------------------------------------------------------------------------------- | ------------: | -------------------------------------------------------------------- | -------------------------------------------- | ------------------- |
| `requirement.md`                                                                      |  491 / 35,868 | `f87e59aaa54dcf1cdf6637bb9ead34647d5fc33091f3e1abc94c8d883d0aca71`   | `76ebf016b12abb06f2b5daa544ea7a1421c7471e`   | 一致                  |
| `design.md`                                                                           |  661 / 33,365 | `ffd88599b265509711c122cd682c00e02c3159435010420e4887f568b4ec727b`   | `118e46f905b86883aac9df0f34ebca9e7be2fe91`   | 一致                  |
| `plan.md`                                                                             |  795 / 70,129 | `6e5b8418b7ef98c15a895de90d2b4d49a209fc1e52b9b61cba010b769fec3b0e`   | `c553db3d222f5c346c1d15c21f0242cebdee0de4`   | 一致                  |
| `report.md`                                                                           | 998 / 255,252 | `4d0a0992c1b46e43fa463bf5a3232b3f6dc4a7b368ef736dc2333cf1823cdef4`   | `1b552544aa7f986acfeb70da21c85f9fc5026969`   | 一致                  |
| `s08-regression-quality-closure.md`                                                   |  506 / 23,214 | `7a79a63fe2111f61764e915fc7c4d89e6a1a2a94af78aa5feaa7f0d04dd6100b`   | `caffae6167b09b7639fb0aaa8c1a468507db3864`   | 一致                  |
| Red v1 canonical/raw: `red-team-review-s08-v1.md`  / `red-team-review-s08-v1-raw.md`  | 各109 / 15,853 | 各 `c5549248aeba54fec25e51f02afcbf45e25ffb95e51b3f12e73043be9815babb` | 各 `2371e468400d4dcb865c64553db27b6275f0c018` | byte-identical / 一致 |
| Red v2 canonical/raw: `red-team-review-s08-v2.md`  / `red-team-review-s08-v2-raw.md`  | 各205 / 13,116 | 各 `4c8539cb6ad3d344367cb4e4dfa3fb3d6898610fec4e572d006a20e264b7a7dd` | 各 `2e925f68ebe0b05c9fc74fe6a6d7b22877723a60` | byte-identical / 一致 |

canonical requirement/design/plan、current report、S08 brief、Red v1/v2 canonical/raw の全内容を確認した。

---

## 3. 差分境界

GitHub Connector の commit比較結果は次のとおり。

### Authoritative verification HEAD → current reviewed HEAD

`c9c59bd507daf9f7909e5c6a216d856aab472a49`
→ `8c807bb4a799f8c489ca1131588e22763ff3c7db`

変更は3 commits、次の5ファイルだけだった。

1. `report.md`
2. `reviews/red-team-review-s08-v1.md`
3. `reviews/red-team-review-s08-v1-raw.md`
4. `reviews/red-team-review-s08-v2.md`
5. `reviews/red-team-review-s08-v2-raw.md`

### Red v2 target → current reviewed HEAD

`fa9637fa098c1b96b6ea1f990ecde1cea1f16c43`
→ `8c807bb4a799f8c489ca1131588e22763ff3c7db`

変更は1 commit、次の3ファイルだけだった。

1. `report.md`
2. `reviews/red-team-review-s08-v2.md`
3. `reviews/red-team-review-s08-v2-raw.md`

したがって、次には差分がない。

* production source
* tests
* provider / installed / dogfood projection
* canonical `requirement.md` / `design.md` / `plan.md`
* S07 evidence
* S07 v8 canonical/raw review artifacts
* S08 implementation brief

S08 quality receiptの前提である「production/test/projection/S07 evidence driftなし」は、current sourceまでのGitHub file boundaryとも整合している。

---

## 4. Findings

**新規 finding なし。**

| Severity | 件数 | Finding |
| -------- | -: | ------- |
| P0       |  0 | なし      |
| P1       |  0 | なし      |
| P2       |  0 | なし      |
| P3       |  0 | なし      |

---

## 5. Red v1 findings の解消確認

### `RT-354-S08-001` — 解消

EAL-059のrehearsal、EAL-060のauthoritative quality receipt、EAL-061のRed v1 FAIL、EAL-062のRed v2 FAILは、履歴を削除せず別identityとして保持されている。EAL-060は `c9c59bd…` をauthoritative verification HEADとし、EAL-061/EAL-062はそれぞれ `0be0d2e6…` / `fa9637fa…` をreviewed HEADとして記録している。

Final QA GateはEAL-060と `c9c59bd…` のみをquality receiptとして参照し、S08 quality closureをpassとしている。一方、Final Spec Review GateはRed v1/v2を別のreport-only gateとしてFAILのまま保持し、fresh v3までS09以降をblockしている。quality PASSとRed gateは混同されていない。

### `RT-354-S08-002` — 解消

Final Commit tableはheaderを含めて4列で一致している。

Red v2 target `fa9637fa…` の旧rowは、`current branch HEAD` と `current_pushed_head` に旧Red v1 HEAD `0be0d2e6…`をliteralで固定していた。

current rowは次の契約へ変更されている。

* `verification_head` は quality receipt `c9c59bd…` に固定。
* `current_pushed_head` は Final Commit row自身へcommit SHAを埋め込まない。
* current identity は named branch tip を指す ref identity。
* 完了済みreviewのexact SHAはEAL/review identity entryへ記録。
* EAL-062の `fa9637fa…` はRed v2のhistorical targetとして明示。
* v2 repair後のtipは次のfresh review identityへ引き継ぐ。

今回のGitHub comparisonにより named branch tipはexactに `8c807bb4…` と確認され、このfresh v3 reviewがそのexact SHAをreview identityとして固定する。したがって、reportが自己参照によって一世代staleになる問題は再発しない。

### `RT-354-S08-003` — 解消

current `report.md` では次が維持されている。

* Implementation Delegation Gate のS08 rowは12列。
* `必須出力` と `観測結果` は独立セル。
* Delegated Worker Evidence のS08 rowは8列。
* Red v2未解消状態、S09–S13 pending、fresh v3 requirement、parent integration decisionが独立して記録されている。

Red v2で解消済みとされたtable-shape/field-bindingは、current reportでもregressionしていない。

---

## 6. Red v2 finding の解消確認

### `RT-354-S08-V2-001` — 解消

Red v2は、Final Commit rowが `current branch HEAD` / `current_pushed_head` として旧SHAをliteral固定していた点をP1とした。

current rowはliteral SHA更新方式を廃止し、named branch refとfresh review identityを分離した。これはS08 briefの「report自身のcommit SHAを先取りして自己参照しない」という不変条件とも一致する。

EAL-062が `fa9637fa…` のままなのは、Red v2のimmutable historical review identityだからであり、current tipの主張ではない。current tip `8c807bb4…` は今回のGitHub preflightとfresh v3 identityで確定している。この分離により、historical rowを改変せず、current identityも誤らせない。

---

## 7. Final Gate Decision

# **PASS**

* P0 = `0`
* P1 = `0`
* P2 = `0`
* P3 = `0`

S08 authoritative quality receiptは `c9c59bd507daf9f7909e5c6a216d856aab472a49` のまま維持する。

今回のfresh v3 Red review targetは `8c807bb4a799f8c489ca1131588e22763ff3c7db` であり、named branch tipとexactに一致する。

この結果により、**S08 Red review gateはPASS** と判定する。ただし、これはS09–S13、whole-Issue QA、PR、merge、Issue close、Issue finish、Human adoption、Oracle 0.17 formal compatibilityの完了を意味しない。

## 仮定

verdictに必要なmaterial assumptionはない。

## 不確実性・未検証主張

pytest、Ruff、Mypy、SpecDock validate、`git diff --check` は今回再実行していない。quality結果は、committed report receipt、authoritative verification HEAD、GitHub commit lineage、変更ファイル境界を監査した。

repository外の `/private/tmp/iss-00354-s08-quality-20260805-authoritative` raw logsは直接再生していない。この制約は、current reportのidentity契約とRed v2 findingの解消判定には影響しない。

## Read-only確認

repository、branch、report、canonical三文書、S08 brief、review artifacts、添付ファイルを変更していない。

**修正版、パッチ、ZIP、新Candidateは生成していない。**
