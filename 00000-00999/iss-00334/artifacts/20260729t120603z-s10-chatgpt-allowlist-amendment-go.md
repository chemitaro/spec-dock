# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a69e0e4-bf74-83e8-bb93-0ba1a931ac51

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use @GitHub to inspect chemitaro/spec-dock branch iss-00334-implement-chatgpt-issue-planning-workflow at exact HEAD 211c73e9fca6292d120686504a3d33f3f10ba387. Never use another branch; return exactly repository access failed if exact access fails. Read active S10 work packet 20260729t104419z-s10-chatgpt-implementation-work-packet.md, current S10 implementation, and tests/unit/application/test_issue_planning_apply.py. Focused S10 is Green: 316 passed,35 skipped; apply regression 71 passed. Full unit has 30 new failures only in that omitted test file, plus 2 known S11 failures. Its old fixtures lack the now-required companion and GitBoundOperationBindingV1. Production compatibility would violate S10-CT-NF03, while S10 requires PA-NF-01 through 10B Green. Decide only: minimally add this one test file to S10 allowlist for fixture migration, or STOP S10. No spec change, production weakening, S11 work, redesign, or other path. Return concise Markdown: exact source evidence; GO/STOP; exact one-file allowlist delta and permitted fixture-only edits; prohibited changes; required tests; rationale; copy-ready dev-coder instruction. No patch or repository mutation. Decision artifact review is waived.

## Answer

# S10 Allowlist Decision

## Exact source evidence

* GitHub connector で `chemitaro/spec-dock` の branch `iss-00334-implement-chatgpt-issue-planning-workflow` を直接解決し、HEAD が要求値 `211c73e9fca6292d120686504a3d33f3f10ba387` であることを確認した。
* S10 work packet の writable test allowlist は9ファイルであり、`tests/unit/application/test_issue_planning_apply.py` を含んでいない。
* 同packetは `S10-CT-NF03` として、archive identityへのbinding混入と、bindingを欠くgit-bound identityの双方を拒否するよう要求している。
* 同packetは `PA-NF-01`〜`PA-NF-10B` のGreen維持を必須回帰としている。
* 現行production contractは、git-bound identityにcanonical target三パスと`GitBoundOperationBindingV1`の両方を必須とし、archive identityではbindingを禁止している。
* 現行apply実装も、git-boundでCandidateを読み、companionを含むbindingを再構築してReview bindingとの完全一致を要求している。
* 一方、対象テストの旧fixtureは、git-bound identityにbindingを与えず、`VerifiedIssueCandidate`にcompanionを与えず、git-bound requestの`candidate_path`を`None`にしている。
* このファイル自身が `PA-NF-01`〜`PA-NF-10B` の回帰を所有している。

## Decision — **GO**

**`tests/unit/application/test_issue_planning_apply.py` だけをS10の有効allowlistへ追加し、fixture migrationを実施する。**

これはproduction compatibilityではなく、現行S10 contractへ旧テストfixtureを追従させるための最小修正である。work packet、canonical spec、Report、productionコードは変更しない。

## Exact one-file allowlist delta

```text
+ tests/unit/application/test_issue_planning_apply.py
```

この追加作業の基準はpacket作成時の旧HEADではなく、現在のexact HEADである。

```text
BASE=211c73e9fca6292d120686504a3d33f3f10ba387
```

このmicro-batchで許されるrepository差分は、上記1ファイルだけとする。ローカル検証スクリプト上では、このファイルをS10 test set、test static-check set、exact diff allowlistへ追加してよいが、work packet artifact自体は編集しない。

## Permitted fixture-only edits

対象ファイル内でのみ、次を許可する。

1. `GitBoundOperationBindingV1` と `OnboardingCompanionBindingV1` のimport。
2. 決定的なtest companion path、bytes、SHA-256 fixtureの追加。
3. `_verified_candidate()` に以下を追加する。

   * companion pathとbytesを`files`へ含める。
   * 同じbytesのSHAを持つ`onboarding_companion`を設定する。
4. `_identity()` のgit-bound branchで、同じCandidate identityとcompanionから`GitBoundOperationBindingV1.create(...)`を生成し、`git_bound_operation_binding`へ渡す。
5. `_request()` で、`candidate_path`をarchive/git-boundの双方へ設定する。以下のmode分離は維持する。

   * archiveのみ: `logical_filename`、`zip_sha256`
   * git-boundのみ: `reviewed_head`
6. `_run()` のdefault Candidate、reviewed binding、candidate loaderが同じfixture identityを参照するよう整合させる。
7. wrong-path等のnegative fixtureにも**有効なoperation binding**を追加し、意図した不正条件だけを残す。
8. 明示的なCandidate drift testでは、candidate-loader側の不正Candidateにreviewed identityを自動追従させない。Review時とapply時の不一致という既存negative semanticsを維持する。

既存test名、parameter set、期待する`status`、`reason`、mutation-zero判定、PA-NFの意味は変更しない。

## Prohibited changes

* productionコードの変更またはcompatibility fallbackの追加
* git-boundでCandidate、companion、operation bindingの欠落を許容する変更
* `S10-CT-NF03`の弱化
* canonical Requirement／Design／Plan／Report／artifact／work packetの変更
* S11のprovider projection、dogfood、distribution、旧integration import修復
* 他のtestファイルの変更
* `skip`、`xfail`、test削除、parameter削減
* 期待するstatus/reasonを現行production結果に合わせて弱化する変更
* fixture migrationを越えるリファクタリングまたは再設計

## Required tests

```bash
set -euo pipefail

BASE='211c73e9fca6292d120686504a3d33f3f10ba387'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'

test "$(git rev-parse HEAD)" = "$BASE"
test "$(git branch --show-current)" = "$BRANCH"
test -z "$(git status --porcelain=v1)"

uv run pytest -q tests/unit/application/test_issue_planning_apply.py

uv run pytest -q \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/authoring_pack/test_zip_contract_profiles.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/integration/test_issue_planning_apply.py

uv run ruff check tests/unit/application/test_issue_planning_apply.py
./spec-dock/scripts/spec-dock validate
git diff --check

test "$(git diff --name-only "$BASE" --)" = \
  "tests/unit/application/test_issue_planning_apply.py"
```

さらに、以前 `71 passed` を記録したapply regression commandを**同一引数のまま**再実行し、`71 passed`を維持する。

最後にfull unitを再実行する。

```bash
uv run pytest -q tests/unit
```

受入条件は次のとおり。

* 対象ファイル由来の30件の新規failureが0件になる。
* 新規failure、collection error、skip追加がない。
* full unitに残るfailureは、開始時点と同一test IDの既知S11-owned 2件だけである。
* その2件を本作業で修正しない。

## Rationale

対象ファイルはPA-NF回帰のownerであるにもかかわらず、S10 allowlistから漏れ、S10で必須化されたCandidate companionと`GitBoundOperationBindingV1`へfixtureが移行されていない。productionを旧fixtureへ合わせると、明示的なfail-closed要件である`S10-CT-NF03`を破る。

したがって、一ファイルのfixture migrationが、PA-NF Green義務とS10のproduction contractを同時に維持する唯一の最小経路である。fixture-only変更でGreen化できない、または別ファイルが必要になった場合に限り、S10を**STOP**する。

## Copy-ready dev-coder instruction

```text
Repository: chemitaro/spec-dock
Branch: iss-00334-implement-chatgpt-issue-planning-workflow
Required starting HEAD: 211c73e9fca6292d120686504a3d33f3f10ba387

Perform one S10 fixture-migration micro-batch only.

The sole permitted repository change is:
- tests/unit/application/test_issue_planning_apply.py

Migrate that file’s shared fixtures to the already-required S10 contracts:

1. Import GitBoundOperationBindingV1 and OnboardingCompanionBindingV1.
2. Add deterministic companion path/bytes/SHA fixtures.
3. Make _verified_candidate() include the companion bytes and onboarding_companion binding.
4. Make git-bound _identity() construct and include GitBoundOperationBindingV1 from the exact Candidate identity and companion binding.
5. Make _request() supply candidate_path in both archive and git-bound modes while preserving archive-only logical_filename/zip_sha256 and git-bound-only reviewed_head.
6. Keep _run() defaults coherent, but do not make deliberately drifted candidate-loader fixtures automatically match the reviewed identity.
7. Give direct wrong-path git-bound fixtures a valid operation binding while retaining the intended wrong-path defect.
8. Preserve every existing test name, parameter set, status/reason expectation, mutation-zero assertion, and PA-NF semantic.

Do not modify production, specs, Report, artifacts, the S10 work packet, S11-owned paths, or any other test file. Do not add compatibility behavior, skip/xfail tests, delete cases, or weaken S10-CT-NF03.

Run:
- the target test file;
- the effective ten-file S10 suite;
- the unchanged command that previously produced 71 apply-regression passes;
- ruff check on the changed file;
- SpecDock validate;
- git diff --check;
- full tests/unit.

The final diff from 211c73e9fca6292d120686504a3d33f3f10ba387 must contain exactly tests/unit/application/test_issue_planning_apply.py. Full unit may retain only the exact two pre-existing S11 failures.

If fixture-only edits cannot make the target Green, any production/spec/S11 change is needed, or any second path must change: STOP S10 and report the blocker without broadening the diff.
```

Repository mutation was not performed. The reported `316 passed, 35 skipped`, `71 passed`, and full-unit failure counts are prompt-supplied execution evidence and were not rerun through the read-only GitHub connector.
