# S07 Fresh Red Team Review v6

* candidate_id: `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z`
* logical_filename: `iss-00354-oracle-017-compatibility-candidate-v2-20260804t043533z.zip`
* sha256: `a870bb35971d86a5a0c5311f404ab717669d6bbaf6798a03a0ad3061537202f8`
* repository: `chemitaro/spec-dock`
* branch: `codex/iss-00354-chatgpt-context-contract`
* source_head: `d96ce0807340631bbf214ed24cdfe9bd91165780`
* model_requested: `GPT-5.6 Pro`
* model_resolved: `GPT-5.6 Pro`
* model_verified: `no`
* verdict: `FAIL`
* p0_count: `0`
* p1_count: `1`
* p2_count: `0`
* p3_count: `0`

## Findings

### `RT-354-S07-V6-001` — Current-state ledger に完了済み v5 mutation と完了済み v5 review を再要求する記述が残っている

* **severity:** P1
* **対象ファイル / 箇所:**

  * `report.md` — `Evidence Adoption Ledger` の `EAL-053`、`next_action` セル
  * `report.md` — `クロージャ網羅（Closure Coverage）` の `cl-s07-projection / tc-s07-001` 行
* **観測事実:**

  * `EAL-053` は、v5 Red evidence import と disposition 修正を今後 `commit/push` してから fresh Red v6 を行うと記載している。
  * `Closure Coverage` は、依然として v4 finding の report-only correction が Blue action であり、fresh Red v5 が pending、v5 PASS で close すると記載している。
  * 一方、同じ現行 `report.md` の S07 v4/v5 narrative、S90、Final Code Review、Final Spec Review、Final Commit は、v5 evidence・Blue brief・一文修正がすでに commit/push 済みで、v5 Red review は `FAIL / P1=1` として完了し、次の gate は fresh Red v6 だけであると記録している。
  * source HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780` の commit 自体も、v5 evidence の追加と S07 v4 disposition の修正を完了済み変更としている。
* **なぜ現行 Candidate の整合性を損なうか:**
  同じ current-state ledger 内に、「v5 repair と v5 review は完了し、次は v6」と「v5 repair の commit/push と v5 review が未実施」という二つの状態遷移が併存している。このため、現行 Candidate は v6 gate へ一意に handoff できず、完了済み mutation の重複実行または完了済み v5 review の再要求を誘発する。S07 の実施状況、EAL、closure coverage、final gate の相互整合という本レビューの必須条件を満たさない。
* **最小限の修正方向:**
  `EAL-053` の `next_action` と `Closure Coverage` の S07 行だけを、v5 evidence／brief／disposition correction は commit/push 済み、v5 Red review は `FAIL / P1=1` で完了、次の唯一の gate は fresh Red v6、という現行状態へ同期する。`S07 pending`、`S08–S13未開始`、PR／merge／Issue close／Issue finish の保留は維持する。Red v1〜v5、Blue brief、Skill、Epic、cleanup receipt、runtime、tests、Issue 三文書は変更対象にしない。

## Verified checks

* GitHub 上で指定 branch が存在し、その tip は source HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780` と `identical`、ahead `0`、behind `0` であることを確認した。default branch fallback は使用していない。
* Candidate の historical immutable identity は、`candidate_id`、logical filename、ZIP SHA-256、repository、branch、historical source HEAD の各値で `MANIFEST.json` と `report.md` が一致している。MANIFEST は `authority=evidence_only`、`adoption_status=unreviewed` であり、現行 S07 HEAD の checksum authority と混同されていない。
* 添付正式 bundle は元のファイル名で確認し、Issue 三文書、`report.md`、親 Epic design、provider Skill、MANIFEST、CHECKSUMS、cleanup receipt、v5 Blue brief、v5 Red canonical/raw を GitHub exact HEAD の対応 blob と照合した。
* `report.md` の S07 v4 narrative は historical state として閉じている。`7538f749…`、`76ab5b3…`、`03ce7f0c…` の完了済み状態、Red v5 `FAIL / P1=1`、fresh Red v6 next gate が記録され、v4 correction の再実行を要求していない。
* v5 Red review の正式結果は、reviewed HEAD `03ce7f0cbf487c2dbf7c20fc41fcf7b13765dc9a`、`FAIL`、P0=`0`、P1=`1`、finding `RT-354-S07-V5-001`、output SHA-256 `1e67e8d951f3be03b9885d584888f21a2997187de283670f2c2866bfcb53c5fc` とともに記録されている。canonical と raw の Git blob SHA は同一である。
* v5 Blue brief は GitHub exact HEAD に存在し、修正範囲を S07 v4 narrative の disposition 一文に限定している。source HEAD の commit は、その一文修正、v5 Red canonical/raw、v5 Blue briefを含む。
* `Test Contract Closure`、Implementation Delegation Gate、Delegated Worker Evidence、Milestone / Commit Candidate Gate、S90、Final Code Review、Final Spec Review、Final Commit は、finding で特定した二つの stale cell を除き、S07 を pending／blocked、fresh Red v6 を次の gate とし、S08、PR、merge、Issue close、Issue finishを完了扱いしていない。
* provider Skill と `.agents/skills/spec-dock-issue-planning/SKILL.md` は同一 Git blob SHA `69b0a87c5fa23e78bbe776f75d61f154b222bf87` であり、byte-identical である。
* 親 Epic §6.3、provider Skill、cleanup receipt、MANIFEST／CHECKSUMSについて、今回の v5 report-only correction に伴う新規の P0/P1 identity・契約・投影不整合は確認しなかった。CHECKSUMS は historical Candidate v2 の完全性証跡として保持されている。
* Final QA は S01–S13 全体の implementation／test evidence 未完了として `pending` のままであり、S07 v6 PASS 前の whole-Issue completion、final PR、merge、close、finish は主張されていない。

## Review boundary

本レビューは source HEAD `d96ce0807340631bbf214ed24cdfe9bd91165780` に対する read-only、defect-only formal review に限定した。実装コード、Oracle compatibility architecture、provider Skill、Epic §6.3、テスト契約の再設計、改善提案、修正版ファイル、パッチ、Candidate ZIP、commit、push は生成していない。

fresh-installed 一時ツリーおよび過去のローカル parity／validate セッションは再実行せず、commit 済み receipt、永続 GitHub blob、exact identity、commit scopeを照合した。今回の P1 は現行 GitHub `report.md` 内で直接観測できるため、この未再実行事項は判定を左右しない。
