# S019 Blue Team recovery record

## Identity

- Repository: `chemitaro/spec-dock`
- Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- Source HEAD at submission: `e1ae20d96400520d5c80168d0d799b9109853dd9`
- Scope: the single formal Red Team finding `FINAL-P1-001` from S018.
- Status: `advisory / not-adopted` for the ChatGPT response; the response was not captured and no model-generated patch was used.

## ChatGPT Use evidence

The fresh Blue Team session `iss00334-s019-blue-pro-aug2e` used the managed Chrome browser through the repository wrapper. Oracle recorded `requested=Pro`, `resolved=Pro`, and `verified=yes`, and the prompt was submitted to conversation `6a6e108d-a044-83ee-88c0-716fa3a1fefe`. ChatGPT generated for approximately seven minutes, then the remote Chrome connection was lost before a final answer was captured. Reopening the same conversation produced only a stalled status snippet; it did not produce a bounded implementation packet.

The same Blue Team conversation was not replaced. A recovery follow-up session `iss00334-s019-blue-pro-followup` was attempted in that conversation. Oracle recorded a `prompt-commit-timeout` (`userMatched=false`, `hasNewTurn=false`) and `resolved=(unavailable)`, so its output is not treated as submitted design evidence. No fresh Blue Team thread was used after this uncertain follow-up.

This records a wrapper/browser recovery problem, not a repository design decision. The failed/stalled ChatGPT output must not be used as a patch or authority.

## Bounded implementation packet adopted from local evidence

The implementation was derived from the formal S018 Red finding and the current source, not from the unavailable ChatGPT response:

1. Acquire the Git-owned `.git/HEAD.lock` with `O_EXCL`, `O_NOFOLLOW`, and ownership/type checks. Fail closed if another lock exists or the lock identity changes.
2. Hold that lock across the symbolic HEAD, operation branch ref, and resolved HEAD proof, the CAS push, remote parity observation, publication evidence write, and terminal result.
3. Pass the already-held lock through `_push_operation_commit_cas` and all final branch proofs so no independent proof reopens a race window.
4. Keep the provider source and dogfooding projection byte-identical.
5. Add deterministic initial, resume, and already-remote-parity tests that attempt `git checkout` immediately after the symbolic HEAD observation and verify that the checkout is rejected while publication remains safe.

## Verification performed

- Focused explicit Apply unit/application/integration suite: `259 passed`.
- Ordinary fast lane: `1362 passed, 2223 skipped`.
- `make lint`: Ruff check/format and mypy passed.
- `spec-dock validate`: `nodes=227`.
- `git diff --check`: passed.
- Provider and dogfooding `issue_planning_apply.py` copies: byte-identical.
