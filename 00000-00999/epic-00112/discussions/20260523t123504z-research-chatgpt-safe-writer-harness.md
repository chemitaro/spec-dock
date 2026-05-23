---
type: research
source: chatgpt-pro
created_at: 2026-05-23T12:35:04+09:00
epic: epic-00112
topic: safe writer harness
status: current
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a119d17-e92c-83ab-beb8-4ea2f41e9754
---

# ChatGPT Pro Research: Safe Writer Harness

## source_note

This report summarizes a ChatGPT Pro thread created through Chrome in the Codex-only ChatGPT Project. It is external analytical input and should not be treated as independently verified repo truth.

## write_capable_authoring_verdict

ChatGPT Pro の結論は、ゼロベースでは `system-architect` / `implementation-planner` を write-capable writer に進める価値がある、というものだった。

ただし writer の意味は、canonical `design.md` / `plan.md` を直接所有・昇格する agent ではなく、`design.md` / `plan.md` の内容を一次作成する bounded draft writer に限定すべきである。

| 役割 | 所有するもの | 書けるもの | 書けないもの |
| --- | --- | --- | --- |
| main orchestrator | canonical artifact、user dialogue、integration、phase promotion、report evidence | canonical `requirement.md` / `design.md` / `plan.md`、ledger、promotion record | なし。ただし review gate なしに通さない |
| system-architect | design content authorship | role-scoped draft design candidate | canonical `design.md`、implementation code、GitHub mutation |
| implementation-planner | plan content authorship | role-scoped draft plan candidate | canonical `plan.md`、implementation code、GitHub mutation |
| spec-reviewer | independent review evidence | review report / preflight finding | candidate / canonical artifact の本文 |
| human | high-level product / quality judgment | approval / comment | agent execution の細部を常時追う義務は負わない |

核心は authorship と authority の分離である。

Go:

- `system-architect` / `implementation-planner` を draft evidence writer にする。
- role-specific writable path に draft を永続化し、diff gate、preflight review、final main-owned promotion を通して canonical に反映する。

No-Go:

- `system-architect` / `implementation-planner` に canonical `design.md` / `plan.md` を直接編集させ、同じ subagent flow 内で review と promotion まで完結させる。

## minimum_safe_harness

最小安全ハーネスは次の pipeline として設計する。

```text
approved requirement.md
  -> main orchestrator creates task manifest
  -> active path resolver locks canonical paths and hashes
  -> writer subagent runs with role-scoped Permission Profile
  -> writer writes draft candidate only
  -> deterministic diff gate validates scope/path/hash/schema
  -> read-only spec-reviewer performs preflight review
  -> writer may revise draft candidate within same scope
  -> main orchestrator performs final review and integration
  -> canonical artifact updated atomically
  -> discussion ledger records evidence, hashes, decisions
  -> rollback point retained
```

### task_manifest

delegation は自然文依頼だけで渡さない。main orchestrator が immutable task manifest を生成し、それを delegation authority にする。

必須 fields:

- task_id
- role
- phase
- mode
- canonical_owner
- writer_may_promote
- writer_may_edit_canonical
- writer_may_edit_code
- writer_may_mutate_github
- input paths and hashes
- repo head
- resolved active path
- canonical target
- candidate output path
- write allow / deny list
- output contract
- review owner
- fallback behavior

### resolved_active_path

writer に「この epic の `design.md` を作って」と渡すだけでは危険。

必須:

- canonical target は main orchestrator が解決する。
- writer は canonical target を参照対象として扱うが、書かない。
- writer の唯一の書き込み先は candidate output と author notes。
- path は symlink 解決後の realpath で workspace root 配下にあることを gate が検証する。
- `requirement.md` / `design.md` / repo HEAD の hash が delegation 時と promotion 時で変わっていたら promotion は fail closed。

### file_permission_model

Permission Profile は次のように扱う。

- local command filesystem/network の guard として使う。
- old sandbox settings との混在は避ける。
- parent runtime override を probe する。
- role-specific draft zone だけ write にする。
- canonical docs / code / `.git` / secrets / config / workflow files は deny にする。

推奨 write target:

- `.spec-dock/drafts/<node-id>/<task-id>/system-architect/design.candidate.md`
- `.spec-dock/drafts/<node-id>/<task-id>/implementation-planner/plan.candidate.md`
- related `notes.md`

禁止:

- canonical `requirement.md`
- canonical `design.md`
- canonical `plan.md`
- implementation code
- tests
- `.git/**`
- secrets / `.env*`
- `.codex/**`
- workflow / config files unless explicit maintenance task

## review_model

Review は 3 層に分ける。

1. Writer self-check
   - traceability、assumptions、open questions、scope、template completeness。

2. Preflight review
   - `spec-reviewer` は read-only。
   - candidate を review し、canonical には触れない。
   - pass は advisory。final pass ではない。

3. Final review / promotion
   - main orchestrator owned。
   - canonical integration 後に actual canonical docs と diff を review する。
   - final pass なしに phase promotion しない。

## failure_modes_and_controls

| Failure mode | Control |
| --- | --- |
| writer が canonical doc を編集する | Permission Profile + diff gate + No-Go |
| active symlink の target drift | resolved realpath + input hash lock |
| source artifact が stale | promotion 時 hash check |
| author が assumption を silent に入れる | required assumptions section + reviewer check |
| reviewer pass と final pass の混同 | preflight / final review type を分離 |
| depth=2 write-capable delegation | write-capable child delegation 禁止 |
| Permission Profile 不発 | probe failure -> read-only fallback |
| evidence が canonical と誤認される | ledger status / non-canonical label |
| rollback 不可 | promotion 前 rollback point |

## staged_migration_plan

### Stage 0: Read-only candidate author

- runtime は read-only のまま。
- output を `design.candidate.md` / `plan.candidate.md` 形式に寄せる。
- essay / advice ではなく promotion-ready candidate を返す。

### Stage 1: Manifest and ledger

- task manifest、resolved active path、input hashes、ledger を導入。
- writer はまだ write 不可でもよい。

### Stage 2: Draft-path writer

- 初めて write-capable にする。
- 書けるのは task-specific draft zone のみ。
- canonical docs / code / GitHub mutation は禁止。
- permission probe 必須。

### Stage 3: Preflight review loop

- `spec-reviewer` を read-only preflight reviewer として追加。
- author -> reviewer -> author revision を最大 1-2 loop 許可。
- final promotion は main only。

### Stage 4: Main-owned canonical promotion automation

- diff gate が normalized patch を生成。
- main orchestrator が final review 後に canonical `design.md` / `plan.md` を atomic write。
- report evidence と phase status を更新。
- rollback id を発行。

### Stage 5: Optional isolated worktree canonical editing

- 標準 route ではない。
- writer は dedicated worktree / branch 内で canonical path を編集してよいが、main branch / canonical source of truth には直接反映しない。
- promotion / merge は main orchestrator only。

## go_no_go_criteria

Go 条件:

- task manifest が role / phase / target / input hashes / write scope を固定している。
- resolved active path が main orchestrator により決定されている。
- writer の write path は task-specific draft zone のみに限定されている。
- canonical docs は writer から write 不可。
- implementation code は writer から write 不可。
- GitHub mutation / destructive command は禁止。
- network は default disabled。
- secrets / `.env` / `.git` は deny または gate で遮断される。
- Permission Profile の effective behavior を probe 済み。
- parent runtime override が broad access になっていない。
- diff gate が path / hash / scope / schema を deterministic に検証する。
- preflight reviewer は independent かつ read-only。
- final review / promotion は main orchestrator owned。
- ledger は evidence であり canonical source ではない。
- rollback point が promotion 前に作られる。
- probe / gate / review failure 時に read-only fallback できる。

No-Go 条件:

- Permission Profile の有効性を task ごとに確認できない。
- active config に old sandbox settings が混在している。
- parent runtime が workspace-wide write または danger-full-access 相当。
- writer が canonical `design.md` / `plan.md` を直接編集する設計。
- author と reviewer が同じ責務境界にいる。
- preflight approval が final approval と混同される。
- discussion ledger が canonical source of truth として使われる。
- resolved active path がなく、cwd や会話文脈で target を推測している。
- diff gate がない、または LLM 判断だけに依存している。
- rollback がない。
- depth=2 の write-capable delegation を許す。
- GitHub mutation / code edit / destructive command が同じ初期 writer profile に含まれる。

## final_judgment

最小安全ハーネスがあるなら、`system-architect = design draft writer`、`implementation-planner = plan draft writer` に進めるのが望ましい。

最小安全ハーネスがないなら、read-only adviser 継続が正しい。ただし、この場合でも出力契約を `design.candidate.md` / `plan.candidate.md` 形式に寄せれば、consultant との差は維持できる。

権限を広げるのは、manifest、path、diff、review、rollback が揃ってからで十分である。

