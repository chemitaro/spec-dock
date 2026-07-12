---
種別: 要件定義書（Issue）
ID: "iss-00301"
タイトル: "Zip Review Staging"
関連GitHub: ["#301"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00301 Zip Review Staging — Issue 要件定義

## 1. 目的

この Issue は、ChatGPT / Oracle が返す `specdock-authoring-pack/` ZIP または tree 出力を、canonical docs に触れる前に安全検査し、採用前の staged evidence として配置する runtime command を実装する。

`authoring pack review` は safe extraction 前に ZIP central directory と metadata / authority boundary を検査し、`authoring pack stage` は review 済み evidence を staging area に展開して dry-run diff、EAL candidate、ownership marker を生成する。どちらの command も canonical adoption、`.assurance.json` mutation、reviewer pass、execution-ready、PR-ready を自己主張してはならない。

## 2. 背景

`epic-00295` では、ChatGPT 5.5 Pro Extended による長時間・高品質な仕様作成を SpecDock installed workflow に組み込むため、prompt pack 生成、backend invocation、ZIP output の review / stage、候補検証、承認 gate、workflow docs / skill を段階的に整備している。

前段の `iss-00299` では prompt pack と safe output constraints を生成し、`iss-00300` では backend command を設定可能な adapter 経由で呼び出す runtime surface を追加した。次に必要なのは、backend から返された ZIP / tree をそのまま展開・採用せず、SpecDock の authority boundary に沿って安全に検査し、採用判断に使える evidence として staging することである。

## 3. 親 Epic から継承する条件

- Provider-side source of truth は `src/spec_dock/assets/spec_dock/...` に置く。
- Dogfooding workspace の `spec-dock/...` は consumer-side mirror として検証に使う。
- ChatGPT-derived output は `authority: evidence_only` であり、明示的な EAL disposition と reviewer gate までは canonical authority を持たない。
- ZIP output root は `specdock-authoring-pack/` とする。
- required metadata は `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md`、`adoption/adoption-map.json`、`adoption/eal-candidates.json` を含む。
- ZIP は review pass 前に repository workspace へ展開しない。
- 中間 Issue では PR を作成せず、final quality gate / PR delivery は `iss-00307` に defer する。

## 4. Scope

この Issue で実現すること:

- `./spec-dock/scripts/spec-dock authoring pack review` を deferred command から implemented command へ昇格する。
- `./spec-dock/scripts/spec-dock authoring pack stage` を deferred command から implemented command へ昇格する。
- ZIP input では extraction 前に central directory を検査し、root、entry path、metadata、size、suffix、binary / symlink / encrypted entry、nested archive、secret-looking content、raw transcript、forbidden authority claim を検査する。
- tree fallback input では ZIP central directory evidence がないことを明示し、fallback / lower authority evidence として分類する。
- valid pack の review 結果には `status=pass` を返すが、`authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を保持する。
- review pass した pack を stage すると、staging directory に safe extracted / copied files、review report、dry-run diff、EAL candidate、ownership marker を生成する。
- stage output は canonical docs、`.assurance.json`、active issue / epic / initiative docs を直接変更しない。
- provider-side runtime と dogfood installed runtime mirror の両方で CLI smoke / focused tests が通る。

この Issue で実現しないこと:

- ChatGPT backend invocation。
- ZIP / tree output の canonical adoption。
- Initiative / Epic / Issue node creation。
- Issue draft adoption validation。
- approval check / human gate。
- `.assurance.json` mutation。
- `authorized_profile` 決定。
- reviewer pass / execution-ready / PR-ready / mergeable PR の自己主張。
- final quality gate / PR delivery。

## 5. Actor / Trigger

| Actor | 役割 | この Issue との関係 |
| --- | --- | --- |
| Codex orchestrator | ChatGPT output を review / stage する | 主利用者 |
| SpecDock runtime user | consumer repo で installed command を実行する | ZIP / tree evidence を安全に扱う |
| ChatGPT / Oracle backend | authoring pack ZIP / tree を生成する外部 automation | 入力 artifact の生成元 |
| spec-reviewer / code-reviewer / qa-reviewer | planning / implementation / quality gate を評価する | gate 役 |

Trigger:

- `./spec-dock/scripts/spec-dock authoring pack review --input <path> ...`
- `./spec-dock/scripts/spec-dock authoring pack stage --input <path> --stage-dir <path> ...`
- provider-side compatibility script の直接実行。

## 6. Functional Requirements

| ID | 要件 |
| --- | --- |
| RQ-001 | `authoring pack review --help` は implemented command として、ZIP / tree input、format、evidence-mode、output/report path を案内する。 |
| RQ-002 | `authoring pack stage --help` は implemented command として、review 済み input、stage directory、dry-run、format を案内する。 |
| RQ-003 | ZIP input は extraction 前に central directory を検査する。 |
| RQ-004 | ZIP root が `specdock-authoring-pack/` 以外の場合は `rejected` とする。 |
| RQ-005 | required metadata が欠落する場合は `fail` とする。 |
| RQ-006 | metadata の authority boundary が `authority=evidence_only`、`adoption_status=unreviewed`、`bundle_generation_not_promotion=true` を満たさない場合は `rejected` とする。 |
| RQ-007 | path traversal、absolute path、host-local path、hidden path、unsupported suffix、oversized entry、encrypted entry、symlink、binary file、nested archive は `rejected` とする。 |
| RQ-008 | secret-looking content、credential / token / private key、raw transcript は `rejected` とする。 |
| RQ-009 | forbidden authority claim（canonical adoption、reviewer pass、`.assurance.json` mutation、execution-ready、PR-ready など）は warning ではなく `rejected` とする。 |
| RQ-010 | source-manifest hash mismatch または required source evidence mismatch は `stale` とする。 |
| RQ-011 | tree input は検査可能な範囲を review するが、ZIP central directory evidence 不在を `fallback=true` / lower authority として明示する。 |
| RQ-012 | review output は text / json の deterministic diagnostics を返し、validation pass と adoption / reviewer pass を区別する。 |
| RQ-013 | stage は review failure input を展開・配置しない。 |
| RQ-014 | stage は canonical docs と `.assurance.json` を変更しない。 |
| RQ-015 | stage output は review report、safe extracted tree、dry-run diff、EAL candidate、ownership marker を含む。 |
| RQ-016 | compatibility scripts `review_chatgpt_authoring_pack.py` と `stage_chatgpt_authoring_pack.py` は runtime command と同じ contract へ委譲するか、contract parity を維持する。 |
| RQ-017 | この Issue の finish evidence は PR delivery を行わず、`iss-00307` への defer rationale を記録する。 |

## 7. Acceptance Criteria

| ID | 受け入れ条件 | 証跡 |
| --- | --- | --- |
| AC-001 | `authoring pack review --help` が deferred ではなく implemented command として必要 option を表示する。 | CLI stdout / test |
| AC-002 | `authoring pack stage --help` が deferred ではなく implemented command として必要 option を表示する。 | CLI stdout / test |
| AC-003 | valid ZIP fixture は review pass になり、authority / adoption fields は evidence-only のまま保持される。 | CLI JSON / test |
| AC-004 | valid ZIP fixture は stage output、review report、dry-run diff、EAL candidate、ownership marker を生成する。 | filesystem / test |
| AC-005 | review pass 前に unsafe ZIP が workspace へ展開されない。 | filesystem sentinel / test |
| AC-006 | path traversal、absolute path、hidden path、unsupported suffix、oversized entry、encrypted entry、symlink、binary、nested archive の fixtures が rejected になる。 | negative fixture tests |
| AC-007 | secret-looking content、raw transcript、credential / token / private key が rejected になる。 | scanner tests |
| AC-008 | forbidden authority claim が rejected になり、warning 扱いされない。 | scanner tests |
| AC-009 | wrong root は `rejected`、metadata missing は `fail`、source hash mismatch は `stale` になる。 | negative fixture tests |
| AC-010 | tree fallback は pass 相当でも ZIP review pass と同格に扱われず、fallback / lower authority diagnostics を返す。 | CLI JSON / test |
| AC-011 | stage は canonical docs、active docs、`.assurance.json` を変更しない。 | git diff / test |
| AC-012 | text / json output は validation pass、adoption、reviewer pass、execution-ready、PR-ready を明確に区別する。 | CLI output / test |
| AC-013 | provider-side runtime path と dogfood installed runtime path の両方で smoke test が通る。 | pytest / CLI |
| AC-014 | compatibility scripts は hardcoded personal path を持たず、runtime contract と同等の結果を返す。 | inspection / test |
| AC-015 | この Issue は PR delivery を行わず、finish evidence で `iss-00307` への defer rationale を記録する。 | `report.md` |

## 8. Failure Modes

| Failure mode | 期待される扱い |
| --- | --- |
| ZIP wrong root | `rejected`; extraction なし |
| ZIP path traversal / absolute path | `rejected`; extraction なし |
| symlink / encrypted / nested archive | `rejected`; extraction なし |
| binary / unsupported suffix / oversized entry | `rejected`; extraction なし |
| metadata missing / invalid JSON | `fail` |
| source hash mismatch | `stale` |
| secret-looking content / raw transcript | `rejected` |
| forbidden authority claim | `rejected`; warning downgrade 禁止 |
| tree fallback | lower authority evidence; ZIP review pass と同格にしない |
| stage target が canonical docs / active docs | `rejected` |
| stage input が review failure | stage しない |

## 9. Grade

Issue Grade は `standard` とする。

根拠:

- installed runtime command の追加であり、consumer-visible CLI behavior を変更する。
- ZIP safety、path safety、secret / raw transcript scanning、authority boundary を扱う。
- Provider-side runtime と dogfood mirror の両方に影響する。
- Strict/Critical 相当の production data migration、irreversible external mutation、credentialed GitHub mutation は含まない。

## 10. Evidence Sources

- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/plan.md`
- `spec-dock/active/issue/artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md`
- `spec-dock/active/issue/artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md`
- `spec-dock/active/issue/artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md`
- Existing `authoring` command surface under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py`
- Existing prompt pack contract under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/prompt_pack_contract.py`
- Existing authoring tests under `tests/cli_runtime/test_authoring.py`
