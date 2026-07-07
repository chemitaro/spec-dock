# Evidence Adoption Ledger examples

## Status semantics

Evidence Adoption Ledger は、ChatGPT output や staged artifact の採否判断を claim 単位で記録する台帳です。ChatGPT が採用状態を決めるのではなく、main orchestrator が local validation と reviewer gate を踏まえて記録します。

| status | 意味 | 次アクション |
|---|---|---|
| `unreviewed` | staged candidate または raw evidence。まだ採用判断していない。 | manual review |
| `adopted` | claim を正本へ再記述し、必要な reviewer gate を通した。 | keep evidence |
| `partially_adopted` | 一部 claim は採用し、一部 claim は除外した。 | record excluded claims |
| `rejected` | unsafe claim または境界違反により採用しない。 | do not stage / do not adopt |
| `stale` | source / ref / profile / skeleton / digest が古い。 | regenerate or reconcile |
| `blocked` | 必要な local observation または外部接続が使えず判断できない。 | manual fallback / unblock evidence |
| `deferred` | この Issue では決めず、後続 Issue または final gate に送る。 | record defer target |

## Required row fields

- ID。
- adoption_status。
- source。
- target。
- rationale。
- evidence。
- next_action。

## Example rows

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-EX-000 | `unreviewed` | staged artifact | README draft candidate | `stage_chatgpt_authoring_pack.py` が作った候補。まだ正本反映していない。 | `artifacts/.../staged-artifacts/item-0001.md` | manual review |
| EAL-EX-001 | `adopted` | ChatGPT draft + local rewrite | `scripts/authoring-pack/README.md` | workflow outline を人間が再記述し、reviewer gate 後に採用した。 | `artifacts/.../authoring-pack-workflow.ja.md` | keep evidence |
| EAL-EX-002 | `partially_adopted` | ChatGPT draft | prompt contract artifact | useful prompt boundary は採用し、host-local path と reviewer-pass claim は除外した。 | `artifacts/.../prompt-contract.ja.md` | record excluded claims |
| EAL-EX-003 | `rejected` | unsafe ZIP candidate | canonical docs | `spec-reviewer passed` や `.assurance.json updated` を output が主張した。 | validation report with `status: rejected` | do not stage |
| EAL-EX-004 | `stale` | reviewed pack | staged adoption | source hash または selected skeleton hash が preflight / review report と一致しない。 | validation report with `status: stale` | regenerate or reconcile |
| EAL-EX-005 | `blocked` | external dependency | ChatGPT authoring flow | GitHub connector、ChatGPT、ZIP generation、required local source observation が使えない。 | blocked evidence note | manual fallback |
| EAL-EX-006 | `deferred` | workflow decision | backend command adapter | backend command adapter、runtime promotion、PR delivery、mergeable confirmation は `iss-00293` または後続 Issue で扱う。 | Epic plan / deferred PR gate | record defer target |

## Anti-patterns

- ChatGPT self-review を `reviewer_result: pass` として扱う。
- validator `pass` を canonical adoption として扱う。
- `unreviewed` staged candidate を `adopted` として report に転記する。
- `.assurance.json` や `authorized_profile` を ChatGPT output で変更したと書く。
- raw transcript、host-local absolute path、personal wrapper path を adoption evidence にする。
- `deferred` を「完了済み」と誤読できる書き方にする。

## Reviewer checklist

- status と next_action が矛盾していないか。
- rejected / stale / blocked が adopted と同じ扱いになっていないか。
- evidence path が repo-relative か。
- 採用対象が正本へ再記述された claim だけか。
- fresh reviewer gate の証跡が別途あるか。
