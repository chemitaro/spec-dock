---
種別: research
ID: "20260706t111806z-research"
タイトル: "ChatGPT Reviewer Gate Script Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t090820z-research"
  - "20260706t103820z-disc"
authority: "synthesized"
created_by_role: "main-orchestrator"
oracle_provider: "chatgpt-use"
oracle_model: "gpt-5.5-pro"
oracle_thinking: "Pro Extended"
oracle_session_slug: "specdock-chatgpt-review-gate-scripts"
inspected_repo: "chemitaro/spec-dock"
inspected_default_branch: "main"
local_head_sha: "918e624b8a97a4c67bd5ac1ac4ff552999b64bbb"
local_branch_state: "detached-head"
adoption_status: "unreviewed"
derived_from:
  - "/private/tmp/codex-agent-work/501/session-20260706t110553z-specdock-chatgpt-review-gate-scripts-fd030dc7/chatgpt-review-gate-scripts-brief.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t110553z-specdock-chatgpt-review-gate-scripts-fd030dc7/chatgpt-review-gate-scripts-output.md"
reflected_to: []
---

# 20260706t111806z-research ChatGPT Reviewer Gate Script Analysis

## 調査目的

ユーザーの追加仮説を検証する。仮説は、`chatgpt-use` による GPT-5.5 Pro Extended を、現在の `spec-reviewer` / `code-reviewer` / `qa-reviewer`、および `system-architect` / `implementation-planner` の一部または全部の代替 backend として使い、GitHub に push 済み・clean な branch/ref を前提に scripted review / scripted authoring を行うことで、レビュー精度、認知負荷、sub-agent 数、token 効率を改善できるのではないか、というもの。

この research は canonical workflow 変更の決定ではない。`chatgpt-use` による外部高深度分析を evidence として保存し、採用する場合は後続の requirement / design / plan / ADR / reviewer gate で別途固定する。

## sources / 調査方法

実行:

- `chatgpt-use` skill の local wrapper `/Users/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt` を直接実行した。
- dry-run: browser mode, `gpt-5.5-pro`, prompt only 約 `175,210` tokens, 46 files bundled。
- live run: `7m45s`, `gpt-5.5-pro[browser]`, input 約 `175.21k`, output 約 `6.85k`, total 約 `182.06k` tokens。
- 出力保存先: `/private/tmp/codex-agent-work/501/session-20260706t110553z-specdock-chatgpt-review-gate-scripts-fd030dc7/chatgpt-review-gate-scripts-output.md`

主な添付:

- `AGENTS.md`, `README.md`, `pyproject.toml`
- `chatgpt-use/SKILL.md`
- 先行 artifact:
  - `20260706t090820z-research-chatgpt-oracle-advanced-analysis.md`
  - `20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md`
- `init-local-00003-architecture-maintenance-and-hardening` の initiative docs
- `epic-00158-agent-workflow-pdca-hardening` の requirement / design / plan / report
- `iss-00186-harden-issue-execution-step-gates`
- `iss-00210-epic-planning-system-architect-draft-cycles`
- `.codex/agents/{code-reviewer,spec-reviewer,qa-reviewer,system-architect,implementation-planner,consultant,deep-consultant}.toml`
- `spec-dock-hub`, `spec-dock-issue-planning`, `spec-dock-issue-execution`, `github-pr-observation`
- workflow / phase / authoring docs

## facts / 観測できた事実

- 現在の local checkout は detached HEAD であり、branch-sensitive な reviewer script の実例としては不適格。
- `gh repo view` で `chemitaro/spec-dock` と default branch `main` を確認した。
- 既存 reviewer agents は fixed output contract と authoritative `review_status` を持つ gate として設計されている。
- `chatgpt-use` wrapper は high-depth analysis / critique / drafting には適するが、GitHub connector の branch correctness、local test execution、local dirty state の authority ではない。
- 先行分析も、ChatGPT output は canonical docs ではなく evidence artifact として扱い、採用は main orchestrator と reviewer gate を通すべきだと整理している。

## inference / 推測

- GPT-5.5 Pro Extended は reviewer の品質を上げる可能性が高いが、remote GitHub connector 前提では local dirty state、untracked file、test 実行、schema validity、fresh reviewer independence をそのまま保証できない。
- そのため、reviewer gate の即時置換より、`oracle-review-preflight` と shadow review で測定し、最初の実用化は `oracle-spec-authoring-batch` の draft evidence 化に寄せるのが安全。
- 最終 gate にするには、branch/ref/source hash、schema validation、independence、stale evidence prevention、artifact adoption rule を script と ADR で固定する必要がある。

## ChatGPT GPT-5.5 Pro Extended analysis

### 結論

推奨は **「GPT-5.5 Pro Extended を reviewer gate の即時置換にしない。まずは remote-provenance 付きの advisory / shadow gate と、reviewed requirement から design+plan draft package を作る `ChatGPT Spec Authoring Batch` の dogfood 実験を行う」** です。

理由は単純です。現在の `spec-reviewer` / `code-reviewer` / `qa-reviewer` は、固定 JSON schema と authoritative `review_status` を返す workflow gate として設計されています。`review_status` は単なる感想ではなく downstream orchestration の gate です。GitHub connector 経由の ChatGPT review は高品質な second opinion になり得ますが、現時点では local git state、uncommitted diff、test execution、fresh reviewer independence、schema validity、source grounding、stale evidence prevention を同じ強度で保証できません。

一方で、**reviewed requirement → design draft + implementation plan draft + self-review + reviewer focus + adoption map** を一括生成する用途は有望です。ただし output は canonical `design.md` / `plan.md` ではなく、scope-local `artifacts/` の draft evidence として受け取り、main orchestrator が Evidence Adoption Ledger 経由で採否を決め、canonical docs を再記述し、その後 fresh `spec-reviewer` gate を必須にするべきです。

### 根拠

GitHub connector で `chemitaro/spec-dock` にアクセスでき、default branch は `main` と確認できました。current branch は提示条件どおり unavailable なので、default branch `main` を検査対象にしました。repository 側では、`src/spec_dock/` が provider source of truth、`spec-dock/` が dogfooding / validation surface、`src/spec_dock/assets/install_root/` が installed agent-tooling assets の authority とされています。

現行 workflow は、`requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` を基本契約とし、fresh `spec-reviewer` の `review_status: pass` だけが phase promotion を許可します。missing / stale / failed / unavailable / denied / waived / provisional は pass ではありません。

`spec-reviewer` は固定 output contract を持ち、`findings` と authoritative `review_status` を返します。`review_status` は workflow gate であり、user / orchestrator が schema や gate semantics を置換してはいけないと定義されています。さらに `spec-reviewer` は canonical artifact と upstream context を evidence-grounded に読む前提で、delegated draft の provenance / stale / rejected / blocked / phase gate bypass も review 対象にします。

`code-reviewer` と `qa-reviewer` も同様に fixed contract と authoritative `review_status` を持ちます。`code-reviewer` は Git を使って review scope を発見し、diff / line number / tests / local state を読む前提です。`qa-reviewer` は test adequacy の gate で、closure ids、changed contracts、negative / error paths、manual-required exceptions などを `plan.md` / `report.md` に照らして判断します。

`chatgpt-use` wrapper は GPT-5.5 Pro Extended、browser mode、fixed Codex-only ChatGPT Project、manual-login profile を固定します。これは高深度 analysis / critique / drafting / plan review には適しますが、wrapper 自体は GitHub connector 可用性や branch correctness を証明する authority ではありません。

### Replacement matrix

| Role / gate | 推奨 | 置換可否 | 理由 |
| --- | --- | --- | --- |
| `code-reviewer` | local final + oracle shadow/preflight | 即時置換不可 | 現行 role は Git diff、uncommitted / staged / untracked、line number、必要に応じた tests を local に確認する gate。GitHub connector は pushed remote しか見えず、local state や test execution を同等に扱えない。 |
| `spec-reviewer` | local final + oracle shadow/spec-risk preflight | 即時置換不可。ただし将来の最有力 candidate | Docs/spec review は ChatGPT と相性が良いが、phase promotion は fresh `spec-reviewer` pass に結びついているため、schema・independence・source hash・Promotion Record を固める ADR なしに置換不可。 |
| `qa-reviewer` | local final + oracle missing-test scout | 即時置換不可 | Test adequacy は local test files、changed behavior、実行済み evidence、manual-required exception の妥当性を見る。ChatGPT は high-level gap discovery には強いが、実行 evidence の authority にはならない。 |
| `system-architect` | draft backend / hybrid | draft production は部分置換可 | 現行 role 自体が canonical writer ではなく、scope-local `artifacts/` draft evidence を作る役割。ChatGPT batch は design draft 作成を強化できるが、canonical `design.md` への採用は main orchestrator + fresh `spec-reviewer` のまま。 |
| `implementation-planner` | draft backend / hybrid | draft production は部分置換可 | 計画 draft、test strategy、review gates、rollback の作成は ChatGPT と相性が良い。ただし implementation readiness や reviewer pass を自己主張してはならない。 |
| `deep-consultant` | oracle backend 最有力 | 置換 / backend 化しやすい | 高難度・高コスト・不可逆判断の read-only decision support で、ChatGPT Pro Extended の強みと一致する。 |
| `consultant` | oracle backend 候補 | 条件付き置換可 | option framing、tradeoff analysis、experiment proposal の read-only role であり、oracle backend 化しやすい。ただし実装・review gate ではない。 |

### Reviewer gate scripts の architecture

`oracle-*reviewer` は最初から authoritative gate にしない。最初は次の 3 層に分けます。

1. **preflight / shadow**: ChatGPT が likely findings、risk focus、missing evidence を返す。`review_status` は advisory とし、phase promotion や issue completion に使わない。
2. **candidate gate**: schema validation、remote provenance、fresh independent session、source hash、review target hash、branch cleanliness が全て通った場合だけ、local reviewer と同じ形式の JSON を生成する。ただし dogfood 実験中は local reviewer が final authority。
3. **future remote final gate**: 実測で local reviewer と同等以上、かつ failure mode が制御できると分かった role だけ ADR で gate semantics を変更する。最初の candidate は `spec-reviewer` の docs/spec-only scope。`code-reviewer` / `qa-reviewer` は後回し。

### Repository cleanliness / GitHub provenance checks

GPT-5.5 Pro Extended reviewer script を branch-sensitive に使う場合、preflight は fail-closed にするべきです。

必須 checks:

```bash
# repository identity
git config --get remote.origin.url
gh repo view --json nameWithOwner,defaultBranchRef,url

# branch state
git symbolic-ref --short HEAD
git rev-parse HEAD
git rev-parse --abbrev-ref --symbolic-full-name @{u}

# local cleanliness
git status --porcelain=v1
git diff --exit-code
git diff --cached --exit-code

# remote freshness
git fetch origin --prune
git rev-parse HEAD
git rev-parse @{u}
test "$(git rev-parse HEAD)" = "$(git rev-parse @{u})"

# review target
git merge-base HEAD origin/main
git diff --stat <base>..HEAD
git diff --name-status <base>..HEAD
```

PR mode では追加で:

```bash
gh pr view <n> --json headRefName,headRepositoryOwner,headRepository,headRefOid,baseRefName,baseRefOid,url
test "$(git rev-parse HEAD)" = "<headRefOid>"
```

Hard fail 条件:

- detached HEAD
- no upstream
- local staged / unstaged / untracked diff
- local HEAD != upstream HEAD
- PR head SHA != local HEAD
- target repo mismatch
- default branch / base branch not resolvable
- GitHub connector context missing
- ChatGPT response says repository access failed
- schema invalid
- source paths / diff hash / target hash missing
- response cites files outside declared scope
- raw transcript includes secrets or private data

### Review target model

| Target | 推奨度 | 用途 | 注意 |
| --- | --- | --- | --- |
| PR number | 最高 | delivery / review gate | base/head SHA が GitHub 上で固定でき、review provenance が最も明確 |
| remote branch vs base | 高 | PR 前の branch review | local HEAD == upstream HEAD 必須 |
| commit range | 中 | release note / narrow review / bisect | base/head SHA を明記し、scope を狭める |
| last commit | 低〜中 | small commit review | branch全体の plan/report consistency は見落としやすい |
| direct diff | 補助 | ChatGPT connector が見られない local diff の advisory review | canonical gate には不向き。diff hash と source file snapshot が必要 |
| file set | 補助 | spec-only / docs-only targeted review | changed behavior を隠せるので explicit scope reason が必要 |
| explicit prompt scope | 必須の補助 | review focus / non-goals / known risks | machine provenance を上書きしてはならない |

結論として、**authoritative candidate gate は PR mode か pushed remote branch mode に限定**します。direct diff / file set / manual scope は advisory mode に留めるのが安全です。

### Proposed scripts

最初は shipped runtime に入れず、dogfood-only の host-local script または `manual-tests/` 相当から始めます。provider product に入れるのは Phase 2 以降です。理由は、`chatgpt-use` wrapper が host-local path、browser session、manual-login、GitHub connector 可用性に依存するためです。

#### `oracle-review-preflight`

目的: reviewer script が実行可能な provenance を持つかだけ検査する。

```bash
oracle-review-preflight \
  --repo chemitaro/spec-dock \
  --role spec-reviewer|code-reviewer|qa-reviewer \
  --target pr|branch|range|last-commit|diff|files \
  --pr 123 \
  --base main \
  --head feature-branch \
  --range BASE..HEAD \
  --scope-file path/to/scope.md \
  --source-paths-file path/to/source-paths.txt \
  --json-out /tmp/oracle-preflight.json
```

Output:

```json
{
  "schema_version": "oracle_preflight_v1",
  "ok": true,
  "repo": "chemitaro/spec-dock",
  "default_branch": "main",
  "target": {
    "type": "pr",
    "pr_number": 123,
    "base_ref": "main",
    "head_ref": "feature",
    "base_sha": "...",
    "head_sha": "..."
  },
  "local_state": {
    "branch": "feature",
    "head_sha": "...",
    "upstream": "origin/feature",
    "clean": true,
    "local_equals_remote": true
  },
  "source_paths": ["..."],
  "stale_if": [
    "local HEAD changes",
    "remote head SHA changes",
    "source_paths content changes",
    "review scope changes"
  ]
}
```

#### `oracle-review`

目的: GPT-5.5 Pro Extended に role-specific review を依頼し、schema-valid JSON を返す。

```bash
oracle-review \
  --role spec-reviewer|code-reviewer|qa-reviewer \
  --target pr|branch|range|last-commit|diff|files \
  --pr 123 \
  --base main \
  --head feature-branch \
  --scope-file review-scope.md \
  --source-paths-file source-paths.txt \
  --mode advisory|shadow|candidate-gate \
  --json-out artifacts/oracle-review.json \
  --artifact-out spec-dock/.../artifacts/<ts>-research-oracle-review.md
```

Preflight:

- `oracle-review-preflight` success 必須
- `chatgpt-use` wrapper path exists
- prompt file generated outside repo or under approved temporary path
- no `.env*`, token, cookie, production dump, private customer data in attachments
- output schema validation
- response must explicitly state inspected repo/ref and target SHA
- response must not continue if repository access failed

#### `oracle-spec-authoring-batch`

目的: reviewed requirement から design+plan draft package を作る。

```bash
oracle-spec-authoring-batch \
  --scope issue|epic|initiative \
  --scope-id iss-XXXXX \
  --requirement spec-dock/active/issue/requirement.md \
  --requirement-review-report spec-dock/active/issue/report.md \
  --base main \
  --head feature-branch \
  --source-paths-file source-paths.txt \
  --grade standard|strict|critical \
  --output-artifact spec-dock/.../artifacts/<ts>-disc-chatgpt-spec-authoring-batch.md \
  --json-out /tmp/oracle-authoring-batch.json
```

Hard preconditions:

- requirement has fresh `spec-reviewer` pass
- requirement hash / reviewer target hash recorded
- no unresolved blocking question
- no stale / blocked EAL entry
- GitHub target pushed and clean if branch-sensitive
- source paths explicit
- output goes to artifact evidence only, not canonical docs

### Proposed review output schema

既存 reviewer schemas を壊さないため、oracle output は envelope + role-compatible body にします。

```json
{
  "schema_version": "oracle_review_v1",
  "oracle": {
    "provider": "chatgpt-use",
    "model": "gpt-5.5-pro",
    "thinking": "extended",
    "session_slug": "oracle-review-...",
    "mode": "advisory|shadow|candidate-gate",
    "repository_access": "confirmed|failed|unknown"
  },
  "target": {
    "repo": "chemitaro/spec-dock",
    "target_type": "pr|branch|range|commit|diff|files",
    "pr_number": 123,
    "base_ref": "main",
    "head_ref": "feature",
    "base_sha": "...",
    "head_sha": "...",
    "diff_hash": "...",
    "source_paths": ["..."],
    "scope_text_hash": "...",
    "stale_if": ["..."]
  },
  "role": "spec-reviewer|code-reviewer|qa-reviewer",
  "review_scope_summary": "...",
  "findings": [
    {
      "title": "[P1] ...",
      "body": "...",
      "confidence_score": 0.87,
      "priority": 1,
      "location": {
        "path": "spec-dock/...",
        "line_range": {"start": 10, "end": 14},
        "section_or_line": "..."
      },
      "evidence": {
        "source_paths": ["..."],
        "source_quote": "...",
        "reasoning_summary": "..."
      },
      "blocks_gate": true
    }
  ],
  "oracle_review_status": "pass|conditional_pass|fail|incomplete",
  "review_status": "pass|fail",
  "review_status_reason": "...",
  "overall_confidence_score": 0.82,
  "schema_valid": true,
  "authority": "advisory_evidence"
}
```

重要点:

- `oracle_review_status` は tri-state / incomplete を持てる。
- `review_status` は既存 gate compatibility のため `pass|fail` に限定する。
- dogfood phase では `authority` は常に `advisory_evidence`。
- `conditional_pass` は final phase promotion に使わない。現行 workflow で promotion できるのは fresh local reviewer の `review_status: pass` だけ。
- schema invalid / connector missing / target mismatch は `review_status: fail` または `incomplete` とし、pass 相当にしない。

### Proposed design/plan generation output schema

`oracle-spec-authoring-batch` の出力は canonical doc ではなく composite artifact です。

```json
{
  "schema_version": "oracle_spec_authoring_batch_v1",
  "kind": "oracle_spec_authoring_batch",
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "oracle": {
    "provider": "chatgpt-use",
    "model": "gpt-5.5-pro",
    "thinking": "extended",
    "session_slug": "specdock-oracle-authoring-..."
  },
  "target": {
    "repo": "chemitaro/spec-dock",
    "scope_type": "issue|epic|initiative",
    "scope_id": "iss-XXXXX",
    "inspected_ref": "main|branch",
    "head_sha": "...",
    "requirement_path": "...",
    "requirement_hash": "...",
    "requirement_review": {
      "reviewer": "spec-reviewer",
      "review_status": "pass",
      "reviewer_target_hash": "..."
    },
    "source_paths": ["..."],
    "stale_if": ["..."]
  },
  "requirement_critique": {
    "blocking_gaps": [],
    "non_blocking_gaps": [],
    "assumptions": []
  },
  "design_draft": {
    "summary": "...",
    "decisions": [],
    "interfaces": [],
    "data_flow": [],
    "failure_modes": [],
    "risks": [],
    "adr_candidates": []
  },
  "plan_draft": {
    "milestones": [],
    "implementation_steps": [],
    "test_strategy": [],
    "review_gates": [],
    "rollback": [],
    "docs_impact": [],
    "completion_criteria": []
  },
  "self_review": {
    "findings": [],
    "limitations": [],
    "known_weak_evidence": []
  },
  "reviewer_focus": {
    "spec_reviewer": [],
    "code_reviewer": [],
    "qa_reviewer": []
  },
  "adoption_map": [
    {
      "claim_id": "C-001",
      "claim": "...",
      "recommended_target": "design.md#...",
      "evidence_strength": "high|medium|low",
      "adoption_recommendation": "adopt|partial|reject|defer",
      "risk_if_adopted": "..."
    }
  ],
  "privacy_review": {
    "secret_paths_included": false,
    "raw_transcript_excluded": true
  }
}
```

Markdown artifact frontmatter:

```yaml
種別: disc
created_by_role: main-orchestrator
oracle_provider: chatgpt-use
model: gpt-5.5-pro
inspected_repo: chemitaro/spec-dock
requested_branch: <branch-or-unavailable>
inspected_ref: <branch-or-main>
head_sha: <sha>
adoption_status: unreviewed
reflected_to: []
source_paths:
  - ...
stale_if:
  - remote head SHA changes
  - requirement hash changes
  - requirement reviewer target hash changes
  - source_paths change
```

### SpecDock artifact integration

統合ルールは次です。

1. Oracle output は `artifacts/` の `research` / `disc` として保存する。
2. `adoption_status: unreviewed`, `reflected_to: []` を初期値にする。
3. raw transcript を canonical docs に貼らない。
4. main orchestrator が `report.md` の Evidence Adoption Ledger に claim 単位で採否を記録する。
5. 採用部分だけを canonical `design.md` / `plan.md` に再記述する。
6. `design.md` 更新後に fresh `spec-reviewer`。
7. `plan.md` 更新後に fresh `spec-reviewer`。
8. self-review / reviewer focus は reviewer input であって reviewer pass ではない。
9. `code-reviewer` / `qa-reviewer` は execution / diff / test evidence phase で別途 fresh gate として実行する。

### Orchestrator への影響

下がる部分:

- design / plan の初期構造化
- alternatives / risk / reviewer focus の抽出
- cross-document traceability の候補作成
- `system-architect` と `implementation-planner` の重複 context 読み込み

上がる部分:

- GitHub provenance / local cleanliness preflight
- source_paths / stale_if / hash 管理
- schema validation
- EAL claim-level adoption
- advisory output と authoritative gate の区別
- connector unavailable / stale branch / raw transcript / secret leak 対策

結論として、**authoring synthesis load は下がるが、evidence governance load は上がる**。この governance load を script が吸収できるまでは reviewer gate replacement ではなく authoring batch evidence に限定するべきです。

### Risks and mitigations

| Risk | 影響 | Mitigation |
| --- | --- | --- |
| Reviewer laundering | ChatGPT self-review が `spec-reviewer` pass と誤認される | `self_review` / `reviewer_focus` と `review_status` を schema 上分離。self-review は gate に使わない |
| Stale branch | ChatGPT が古い main / branch を読む | local HEAD == upstream HEAD、PR head SHA == local HEAD、stale_if、head_sha 必須 |
| Local diff invisibility | GitHub connector が unpushed diff を見ない | clean worktree / no unpushed diff を hard fail |
| Schema drift | ChatGPT が自然文や余分な keys を返す | JSON schema validation。invalid は fail / incomplete |
| Connector unavailable | attached files だけで branch-sensitive claim を続ける | branch-sensitive review は hard fail。advisory-only なら provenance に明記 |
| Authority confusion | artifact が canonical docs と誤認される | `adoption_status: unreviewed`, `reflected_to: []`, EAL 必須 |
| Privacy leak | secret / `.env*` / raw transcript 混入 | denylist、pre-attach manifest、artifact は summary のみ |
| Availability dependency | Browser / manual-login / ChatGPT UI が flaky | local workflow fallback を維持。unavailable は degraded success にしない |
| Reviewer independence loss | Authoring run と reviewer run が同じ context | fresh independent session、different slug、authoring output を作った run は final review 不可 |
| Over-reliance | high-quality prose が verification を置換 | local tests / local reviewer / report evidence を final gate とする |

### Phased rollout plan

#### Phase 0: dogfood-only runbook

- `oracle-review-preflight` と `oracle-spec-authoring-batch` を手動 script / runbook として実施。
- provider runtime にはまだ入れない。
- output は `artifacts/` の `disc` / `research`。
- final reviewer gates は local のまま。

#### Phase 1: Spec Authoring Batch experiment

実験対象:

> reviewed requirement から combined design+plan draft package を作り、canonical adoption と reviewer gates を保つ workflow。

比較 arm:

- Baseline: existing `system-architect` draft + adoption + `implementation-planner` draft + adoption
- Oracle batch: ChatGPT one-shot requirement critique + design draft + plan draft + self-review + reviewer focus
- Hybrid: ChatGPT batch first, then existing specialists use it as evidence

#### Phase 2: Shadow reviewer scripts

- `oracle-review --role spec-reviewer --mode shadow`
- `oracle-review --role code-reviewer --mode shadow`
- `oracle-review --role qa-reviewer --mode shadow`
- local reviewer と finding overlap / false positive / false negative / schema validity / elapsed time / provenance failure を比較。
- gate authority はまだ local。

#### Phase 3: Candidate gate for narrow docs/spec scope

- docs-only / spec-only / no implementation diff の `spec-reviewer` に限定して candidate gate を試す。
- local `spec-reviewer` と disagreement が一定閾値以下、かつ schema / provenance failure が低いことを条件にする。
- ADR なしに final gate へ昇格しない。

#### Phase 4: Provider docs / optional adapter

- `src/spec_dock/assets/spec_dock/docs/integrations/chatgpt-oracle.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/oracle-evidence.md`
- no hardcoded local path
- capability discovery
- denylist
- unavailable / stale / failed output handling
- EAL examples

#### Phase 5: Gate semantics ADR

- Reviewer backend abstraction
- remote gate eligibility
- schema contracts
- independence conditions
- branch/ref/source hash requirements
- fallback behavior
- security / privacy / availability
- migration / rollback

### Clear do-this-first recommendation

**最初にやるべきことは、`Dogfood ChatGPT Spec Authoring Batch for Design+Plan Drafts` を 1 issue 分だけ実験することです。**

実装ではなく、dogfood feature issue として次を固定します。

1. reviewed requirement を 1 つ選ぶ。
2. `oracle-spec-authoring-batch` の manual runbook を作る。
3. source_paths / inspected_ref / head_sha / stale_if / privacy review を必須にする。
4. output を `artifacts/<ts>-disc-chatgpt-spec-authoring-batch-experiment.md` に保存する。
5. EAL で claim 単位に採用 / 部分採用 / 棄却を記録する。
6. canonical `design.md` / `plan.md` は main orchestrator が再記述する。
7. design と plan に fresh local `spec-reviewer` を通す。
8. baseline / oracle batch / hybrid を比較する。
9. reviewer gate replacement はこの結果を見るまで延期する。

### 仮定

- GPT-5.5 Pro Extended / `chatgpt-use` wrapper は、添付 skill に記載された固定 wrapper contract に従って使える前提です。
- GitHub connector はこの応答時点で `chemitaro/spec-dock` default branch `main` にアクセスできました。
- current branch は unavailable / detached 相当として扱い、branch-sensitive な current-branch claim は避けています。

### 不確実性

- ChatGPT Project 内 GitHub connector が常に同じ権限・同じ branch visibility を持つかは、Codex 側から完全には保証できません。
- `oracle-chatgpt` の browser session capture / timeout / incomplete response の扱いは、script contract と artifact provenance で fail-closed にする必要があります。
- 現行 workflow に `conditional_pass` を正式 gate value として入れるには、既存 reviewer schema が `pass|fail` である点との整合を ADR で決める必要があります。短期的には `conditional_pass` は `oracle_review_status` の advisory value に留め、既存 `review_status` は `pass|fail` に維持するのが安全です。

### 未検証主張

- 「ChatGPT reviewer が local reviewer と同等以上の finding quality を出す」は未検証です。Phase 2 の shadow comparison で測るべきです。
- 「design+plan batch が `system-architect` + `implementation-planner` より token / time / quality で有利」は未検証です。Phase 1 の baseline / oracle / hybrid 比較で測るべきです。
- 「future remote `spec-reviewer` final gate が安全に成立する」は未検証です。現時点では architecture initiative + ADR + measured dogfood evidence が必要です。

## question candidates / 質問候補

- 人間判断が必要な候補:
  - `oracle-spec-authoring-batch` を dogfood-only script として先に作るか、最初から provider docs / shipped optional adapter まで含めるか。
  - shadow reviewer の最初の対象を docs/spec-only `spec-reviewer` に限定するか、PR code review も同時に観測するか。
- 質問せずに解決できた候補:
  - reviewer gate の即時置換は避ける。
  - design/plan 作成支援は evidence-only batch として開始する。
  - pushed/clean branch/ref preflight は必須。

## terminology conflicts / 用語衝突

- `review_status`:
  - 既存 reviewer agents では authoritative gate value。
  - ChatGPT reviewer script では advisory/candidate value として扱う必要がある。
  - 解決案: `oracle_review_status` と既存互換 `review_status` を分け、dogfood phase では `authority: advisory_evidence` を必須にする。
- `self-review`:
  - ChatGPT からの self-review は reviewer input であって reviewer pass ではない。
  - 解決案: `self_review` / `reviewer_focus` と final `review_status` を schema 上分離する。
- `ChatGPT reviewer`:
  - final reviewer gate と誤解されやすい。
  - 解決案: 初期名称は `oracle-review --mode shadow` / `oracle-spec-authoring-batch` とし、final gate 化までは `reviewer` 単独名称を避ける。

## edge cases / 具体シナリオ

- Detached HEAD で script を実行する:
  - branch-sensitive review は fail。今回の checkout はこの状態なので、実装 dogfood では branch を作り push してから実行する必要がある。
- Local untracked artifact がある:
  - GitHub connector から見えないため、authoritative branch review には使えない。添付ファイルによる advisory analysis として扱う。
- GitHub PR head と local HEAD がずれる:
  - `oracle-review-preflight` は hard fail。stale ChatGPT output は EAL adoption 対象にしない。
- ChatGPT が schema 以外の自然文を返す:
  - schema validation failure とし、gate pass にしない。
- Authoring batch が優れた design/plan を返す:
  - それでも canonical `design.md` / `plan.md` に直接配置しない。main orchestrator が claim 単位に採用し、fresh `spec-reviewer` を通す。

## implications / 判断への含意

- 次の実装 initiative / issue は、reviewer gate replacement ではなく `ChatGPT Spec Authoring Batch` の dogfood experiment として切るのが安全。
- reviewer gate script は `oracle-review-preflight` を先に作り、実際の ChatGPT review は `shadow` mode から始める。
- `code-reviewer` / `qa-reviewer` の final gate 置換は、local diff/test evidence authority が弱いため後回し。
- `spec-reviewer` は将来の remote final gate 候補だが、最初は docs/spec-only かつ local reviewer との比較測定が必要。
- `consultant` / `deep-consultant` は ChatGPT Pro Extended backend 化に最も向いている。

## リスク/制約

- Browser / manual-login / ChatGPT UI 依存があるため、SpecDock provider runtime に直ちに入れると portability が落ちる。
- GitHub connector の可視性は Codex 側から完全には証明できないため、script output に `repository_access`, `inspected_ref`, `head_sha`, `source_paths`, `stale_if` を持たせる必要がある。
- 既存 reviewer schema と `conditional_pass` の扱いが衝突するため、short-term では advisory-only に閉じる。

## 反映先

- まだ canonical docs へ反映していない。
- 反映する場合の候補:
  - `epic-00158` 配下に `oracle-spec-authoring-batch` dogfood issue を追加。
  - `oracle-review-preflight` / `oracle-review --mode shadow` の issue を追加。
  - gate semantics を変更する場合は ADR を追加。
