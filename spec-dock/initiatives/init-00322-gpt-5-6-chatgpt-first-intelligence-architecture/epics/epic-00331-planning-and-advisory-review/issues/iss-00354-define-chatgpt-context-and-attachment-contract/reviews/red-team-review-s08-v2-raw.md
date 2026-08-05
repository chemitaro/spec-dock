# iss-00354 S08 Fresh Red Team Review v2

## 1. 対象 identity

| 項目                                          | 確認結果                                                               |
| ------------------------------------------- | ------------------------------------------------------------------ |
| Repository                                  | `chemitaro/spec-dock`                                              |
| Named branch                                | `codex/iss-00354-chatgpt-context-contract`                         |
| Exact reviewed source HEAD                  | `fa9637fa098c1b96b6ea1f990ecde1cea1f16c43`                         |
| GitHub branch / HEAD comparison             | `identical`                                                        |
| Ahead / behind                              | `0 / 0`                                                            |
| Default branch fallback                     | **未使用**                                                            |
| S08 authoritative quality verification HEAD | `c9c59bd507daf9f7909e5c6a216d856aab472a49`                         |
| S08 Red v1 reviewed HEAD                    | `0be0d2e6df4809215edd024afd97ea3978f2a690`                         |
| S08 Red v1 canonical/raw SHA-256            | `c5549248aeba54fec25e51f02afcbf45e25ffb95e51b3f12e73043be9815babb` |
| Review mode                                 | Fresh v2 / read-only / defect-only                                 |

GitHub Connector で named branch と指定 source HEAD を直接比較し、`identical`、ahead `0`、behind `0` を確認した。`fa9637fa…` は S08 Red v1 の三件を report 台帳へ反映した report/evidence-only commit である。

**対象 identity の確認は成功した。default branch へのフォールバックは行っていない。**

---

## 2. 添付資料の読了・GitHub 同一性確認

添付 ZIP アーカイブは存在せず、次の7ファイルが個別ファイルとして直接添付されていた。そのためアーカイブ展開処理は該当しない。7ファイルすべてを全文読了し、ローカル添付の Git blob を GitHub exact source HEAD `fa9637fa…` の対応 blob と照合した。

### MANIFEST 相当一覧

| 添付ファイル                               |    行数 / bytes | 添付 SHA-256                                                         | GitHub blob at `fa9637fa…`                 | 結果 |
| ------------------------------------ | ------------: | ------------------------------------------------------------------ | ------------------------------------------ | -- |
| `requirement.md`                     |  491 / 35,868 | `f87e59aaa54dcf1cdf6637bb9ead34647d5fc33091f3e1abc94c8d883d0aca71` | `76ebf016b12abb06f2b5daa544ea7a1421c7471e` | 一致 |
| `design.md`                          |  661 / 33,365 | `ffd88599b265509711c122cd682c00e02c3159435010420e4887f568b4ec727b` | `118e46f905b86883aac9df0f34ebca9e7be2fe91` | 一致 |
| `plan.md`                            |  795 / 70,129 | `6e5b8418b7ef98c15a895de90d2b4d49a209fc1e52b9b61cba010b769fec3b0e` | `c553db3d222f5c346c1d15c21f0242cebdee0de4` | 一致 |
| `report.md`                          | 997 / 253,151 | `b30654ee5576c80706029481c4d8f3cb25dd2ab05780f1aec6b6fa641f144966` | `3b46089312ae1f358ba8e238de020c4220fd4fd5` | 一致 |
| `s08-regression-quality-closure.md`  |  506 / 23,214 | `7a79a63fe2111f61764e915fc7c4d89e6a1a2a94af78aa5feaa7f0d04dd6100b` | `caffae6167b09b7639fb0aaa8c1a468507db3864` | 一致 |
| `red-team-review-s08-v1.md`          |  109 / 15,853 | `c5549248aeba54fec25e51f02afcbf45e25ffb95e51b3f12e73043be9815babb` | `2371e468400d4dcb865c64553db27b6275f0c018` | 一致 |
| `red-team-review-s08-v1-raw.md`      |  109 / 15,853 | `c5549248aeba54fec25e51f02afcbf45e25ffb95e51b3f12e73043be9815babb` | `2371e468400d4dcb865c64553db27b6275f0c018` | 一致 |

Red v1 canonical と raw は byte-identical であり、指定された SHA-256 と一致した。GitHub 上でも両ファイルは同一 blob である。

確認対象は以下をすべて含む。

* canonical requirement / design / plan の三文書
* current `report.md`
* S08 implementation brief
* S08 Red v1 canonical / raw evidence

---

## 3. 差分境界の確認

### Red v1 reviewed HEAD → current source HEAD

`0be0d2e6df4809215edd024afd97ea3978f2a690` から `fa9637fa098c1b96b6ea1f990ecde1cea1f16c43` までの差分は1 commit、次の3ファイルだけだった。

1. `report.md`
2. `reviews/red-team-review-s08-v1.md`
3. `reviews/red-team-review-s08-v1-raw.md`

### Authoritative verification HEAD → current source HEAD

`c9c59bd507daf9f7909e5c6a216d856aab472a49` から `fa9637fa…` までの差分も、同じ3ファイルだけだった。

したがって、今回の前提どおり次には差分がない。

* production source
* tests
* provider / installed / dogfood projection
* canonical requirement / design / plan
* S07 evidence
* S07 v8 review artifacts

---

## 4. Severity 集計

| Severity |    件数 |
| -------- | ----: |
| P0       |     0 |
| P1       | **1** |
| P2       |     0 |
| P3       |     0 |

---

## 5. Findings

| ID                  | Severity | Exact location                                            | Observed defect                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Minimal correction boundary                                                                                                                                                                                                                                                                                  |
| ------------------- | -------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `RT-354-S08-V2-001` | **P1**   | `report.md` — `### 最終 commit（Final Commit）` の current row | Final Commit table は4列へ修正され、`verification_head=c9c59bd…` と report-finalization/current-pushed identity も意味上分離された。しかし、actual named branch tip / reviewed source HEAD は `fa9637fa098c1b96b6ea1f990ecde1cea1f16c43` であるのに、current row は現在も `current branch HEAD` と `current_pushed_head` の両方を旧 Red v1 reviewed HEAD `0be0d2e6df4809215edd024afd97ea3978f2a690` と記録している。これにより、v1修正を含む現在の report state が exact reviewed source HEAD に結合されず、current closure identity が一世代 stale である。 | Final Commit の current identity だけを current source / pushed HEAD `fa9637fa098c1b96b6ea1f990ecde1cea1f16c43` に結合する。`verification_head=c9c59bd507daf9f7909e5c6a216d856aab472a49`、Red v1 historical identity、EAL-059〜061、canonical/raw evidenceは保持する。production source、tests、projection、三文書、S07 evidenceを変更しない。 |

### 影響

これは単なる表示上の古い短縮 SHA ではない。Final Commit row が明示的に「current branch HEAD」「current_pushed_head」を宣言しているため、現在レビューしている `fa9637fa…` と異なる SHA を記録すると、次を誤らせる。

* Fresh Red v2 の exact review target
* report-only repair の完了 identity
* S08 Red gate と S09 handoff の監査対象
* current pushed state と historical Red v1 state の区別

したがって、現在の S08 Red gate を PASS とする前に解消すべき P1 である。

---

## 6. Red v1 finding の解消確認

### `RT-354-S08-001` — **解消**

確認結果:

* S90 current row は `EAL-059 rehearsal`、`EAL-060 authoritative receipt`、`EAL-061 Red v1 FAIL` を明示的に区別している。
* Final QA の S08 row は EAL-060 と authoritative verification HEAD `c9c59bd…` のみを quality receipt として参照し、S08 quality closure を `pass` としている。
* Parent Implementation Exception は、S08 quality closure/evidence import は完了済みとしつつ、Red v1 FAIL と fresh v2 gateを別に保持している。
* Final Spec Review は、S08 quality receipt と S08 Red review gate を別行・別判断として扱い、Red v2 PASS前の S09開始を禁止している。

EAL-059 の historical row自体は保持されているが、current-state surfaces では rehearsal として位置付けられている。これは immutable historical evidence を維持するという判定規則と整合する。

**Status: resolved**

---

### `RT-354-S08-002` — **部分修正、未解消**

解消済み部分:

* Final Commit header と current row はともに4列で一致している。
* `verification_head=c9c59bd…` と `current_pushed_head` は別の役割として記録されている。
* 完了済み report synchronization を将来 action として再要求していない。
* S09–S13、whole-Issue QA、PR、merge、Issue close、Issue finishは適切に後続 gate として残されている。

未解消部分:

* `current branch HEAD` と `current_pushed_head` が `fa9637fa…` ではなく、旧 `0be0d2e6…` のままである。

**Status: unresolved — residual P1 `RT-354-S08-V2-001`**

---

### `RT-354-S08-003` — **解消**

Implementation Delegation Gate:

* header: 12列
* S08 row: 12列
* `output required`: `authoritative same-HEAD receipt, report-only closure, and S99 input`
* `observed result`: `PASS; cl-s08-regression and tc-s08-001 are closed; S09 is the next gated step`

Delegated Worker Evidence:

* header: 8列
* S08 row: 8列
* `unresolved risks`: `S09〜S13 remain pending; no residual S08 risk`
* `parent integration decision`: `cl-s08-regression and tc-s08-001 are closed; S08 closure is adopted and S09 is the next gated step`

各契約フィールドは独立セルに分離されている。

**Status: resolved**

---

## 7. 根拠

1. GitHub named branch と `fa9637fa…` の exact comparison は `identical`、ahead/behind `0/0`。
2. 添付7ファイルはすべて GitHub exact source HEAD の blob と一致。
3. Red v1 canonical/raw は byte-identical かつ指定 SHA-256 と一致。
4. v1 reviewed HEAD 以降の変更は report と v1 evidenceだけで、production/test/projection/spec/S07 driftはない。
5. current report の table shape は修正されているが、Final Commit の current identityだけが旧 HEAD に残っている。

---

## 8. 仮定

**Verdict に必要な material assumption はない。**

GitHub named branch、exact commits、file blobs、添付 bytes、current report textから直接判定した。

---

## 9. 不確実性・未検証主張

* 本レビューでは pytest、Ruff、Mypy、SpecDock validate、`git diff --check` を再実行していない。
* repository外の authoritative raw command logsを独立再生していない。
* `c9c59bd…` の quality resultについては、committed report receipt、GitHub lineage、変更範囲を監査した。
* 今回の finding は command実行結果ではなく、exact current GitHub `report.md` の identity不一致から直接確認できるため、上記未再実行は verdict に影響しない。
* Oracle `0.17.0` formal compatibility、S09–S13、whole-Issue QAは本レビュー対象外である。

---

# 10. Final Verdict

# **FAIL**

* P0 = `0`
* P1 = `1`
* P2 = `0`
* P3 = `0`

S08 authoritative quality receipt `c9c59bd507daf9f7909e5c6a216d856aab472a49` の pass 自体は否定しない。

ただし、current source HEAD `fa9637fa098c1b96b6ea1f990ecde1cea1f16c43` に対して Final Commit ledger の current branch / pushed identity が `0be0d2e6…` のままであるため、S08 Red v2 gate は PASS 条件を満たさない。

**S08 Red review gate は FAIL のままであり、S09開始、PR、merge、Issue close、Issue finishへ昇格できない。**

本レビューでは repository、branch、report、review artifacts、添付ファイルを変更していない。修正版、パッチ、ZIP、新しい Candidate は生成していない。
