# 補助アーティファクト: 既存実装対応表・テスト観点・停止条件

> **補助資料 / non-canonical**  
> `CAND-ISS-00354-20260803T172642Z` の実装者向け cross-reference であり、三文書が優先する。

## 1. Module-by-module delta

| Module | Keep | Remove / replace | Add |
|---|---|---|---|
| `application/issue_planning_prompt.py` | typed identity、output expectation、GitHub hard failure | source safe-read、limits、scanner、attachment bytes/index/SHA、resource concatenation | operation registry、minimal body、attachment path tuple |
| `application/issue_planning.py` | create/review/revise/apply orchestration、pre/postflight、Candidate lifecycle | context manifest load、input sensitivity check、source-manifest attachment match、exact attachment materialization | static/dynamic/operator path assembly、thread policy |
| `domain/issue_planning_contracts.py` | Candidate / Review / Human / source evidence | prompt-materialization-only fields as needed | operation input、thread request/binding types |
| `infra/issue_planning_chatgpt.py` | direct Oracle、managed Chrome、sanitized env、recovery、typed output snapshot | `_write_transport_pack`、input temp pack、manifest/provenance/context copies | direct attachment argv、thread start/continue adapter |
| `commands/issue_planning.py` | existing command family / output format | `--context-manifest` | directory-oriented option |
| `application/ports.py` | existing gateway boundaries | none unless old attachment bytes port exists | private thread store / adapter port if needed |
| operation resources | role intent / authority / output meaning | old flat resource layout、fixed onboarding headings | per-operation `prompt.md` + opaque `attachments/` |
| skills/docs | direct Oracle、exact branch、Human gate | reference-only attachments、input manifest safety、old CLI | Option A/C、Blue/Red、operator responsibility |
| parent Epic docs | lifecycle / identity / authority | conflicting body/attachment wording | scoped consistency amendment |

## 2. Test replacement map

### 2.1 `tests/unit/application/test_issue_planning_prompt.py`

Replace:

- descriptor-relative source read race tests。
- UTF-8 source requirement。
- relevant source count / byte budget。
- operator context byte budget。
- secret / private path attachment rejection。
- attachment index / SHA。
- fixed prompt character budget。
- exact 13 heading / 4 diagram text。

Add:

- deterministic minimal body。
- no detailed instruction in body。
- operation definition path resolution。
- attachment directory path only。
- no tree walk / stat / read。
- file add/remove independent from code。
- planning / review / revision body field matrix。
- no thread handle leak。

Retain:

- canonical Issue ID / output expectation validation。
- reviewer read-only / defect-only meaning。
- formal output / authority wording semantics。
- installed resource resolution, adapted to new tree。

### 2.2 `tests/unit/application/test_issue_planning.py`

Add:

- planning static + optional directory path assembly。
- Review Candidate original path。
- Revision Candidate / Review / request original paths。
- no duplicated prior docs。
- Blue continuation request。
- fresh Red request。
- continuity ambiguous blocked before backend。
- source preflight / postflight unchanged。

Retain:

- existing Issue target resolution。
- Candidate publication。
- Review identity。
- P0 / P1 revision trigger。
- mechanical revision。
- apply / transaction / stale behavior。

### 2.3 `tests/unit/infra/test_issue_planning_chatgpt.py`

Replace:

- `_write_transport_pack` manifest assertions。
- exact binary copy into pack。
- source hash manifest assertions。

Add:

- pure argv builder uses original paths。
- directory fixture with hidden / symlink / FIFO does not trigger tree operation。
- no input temporary pack。
- normal attachment failure no retry / exclusion。
- direct continuation capability。
- Blue private handle absent from public result。
- fresh Red new session。
- output snapshot unchanged。

Retain:

- Oracle executable / version / help。
- managed Chrome。
- sanitized environment。
- shell false。
- same invocation recovery。
- invalid session metadata。
- typed ZIP / JSON。
- output archive safety。
- transcript / private diagnostic containment。

### 2.4 CLI / integration

Update:

- `--context-manifest` help / parsing removal。
- new directory option。
- fake Oracle prompt parsing for minimal body。
- fake Oracle attachment operand capture。
- no generated prompt-pack inventory assertion。
- end-to-end create → review → revise → apply。
- installed skill guidance。

## 3. No-prewalk proof

Option C は「scanner testを削除した」だけでは証明できない。次を直接 test する。

```python
def fail_tree_access(*args, **kwargs):
    raise AssertionError("attachment directory must not be inspected")

monkeypatch.setattr(Path, "rglob", fail_tree_access)
monkeypatch.setattr(Path, "iterdir", fail_tree_access)
monkeypatch.setattr(Path, "resolve", fail_tree_access)
monkeypatch.setattr(Path, "read_bytes", fail_tree_access)
```

path object 自体の string conversion に必要な method まで過剰 monkeypatch しない。adapter の pure argv assembly が
directory pathを保持し、filesystem syscall 0であることを spy する。

FIFO fixture は test teardown が hang しないよう、作成だけ行い、openしないことを assertion とする。

## 4. Input / output boundary regression

| Boundary | Must be removed | Must remain |
|---|---|---|
| Input directory | per-entry safe read、hash、manifest、secret scan、quota | top-level path selection |
| GitHub source | attachment-based source substitute | exact named branch / HEAD pre/postflight |
| Oracle process | generated input pack | direct argv、managed Chrome、env sanitization |
| ChatGPT output | none | typed ZIP / JSON snapshot |
| Candidate | none | identity、SHA、source baseline、evidence-only |
| Review | none | closed JSON、fresh Red、identity |
| Apply | none | exact Human decision、transaction safety |

A regression test が「manifest」という文字列を検出する場合、input manifest と output Candidate manifest を
区別する。全 manifest を一括削除しない。

## 5. Body content assertions

Planning minimal body の expected assertions:

- operation / objective。
- repository / branch / source HEAD。
- Initiative / Epic / Issue。
- GitHub exact access failure。
- no mutation。
- authoring ZIP。
- attached instructions。

Not present:

- attachment filename inventory。
- attachment SHA。
- source file content。
- detailed 13-heading onboarding contract。
- full JSON schema。
- personal wrapper。
- default branch fallback。

Review / Revision は target identity が必要なため Candidate / Review SHA を含められる。これは input directory
checksumではない。

## 6. Thread tests

### 6.1 Blue reuse

Given:

- binding repo / branch / HEAD / Issue match。
- Candidate lineage match。
- provider reports handle resumable。

Then:

- `continue_verified` once。
- `start` zero。
- complete current static / dynamic attachment paths supplied。
- no handle in public result。

### 6.2 New Blue

Given:

- handle missing / expired。
- lineage exact。

Then:

- old binding invalidated。
- `start` once。
- current body / static dir / prior Candidate / Review / request supplied。
- new binding privately stored。
- public output says only content-free restart status if needed。

### 6.3 Human block

Given:

- two plausible prior Candidates or identity mismatch。

Then:

- backend invocation zero。
- status blocked。
- no automatic selection。
- no default branch / wrapper fallback。

### 6.4 Fresh Red

For Candidate v1 and v2:

- two distinct start operations。
- no Blue binding use。
- no Red handle reuse。
- v1 PASS cannot validate v2。

## 7. Resource parity tests

Target behavior:

```text
provider operation tree
  == recursive relative path + bytes ==
installed operation tree
  == recursive relative path + bytes ==
dogfood operation tree
```

test は file name allowlist を持たず、tree 増減を expected parity 差分として扱う。hidden file も parity comparison の
対象になり得るが、runtime attachment collector が検査するという意味ではない。

## 8. Documentation checks

Search and remove / revise stale guidance:

```text
--context-manifest
relevant_source_paths
operator_context
attachments are untrusted reference data  # instruction禁止の意味で使っている箇所
context-NNN.md
source-manifest.json                       # input transportとして
13 nonempty distinct H2s
4+ valid `plantuml` fences
```

Retain references where they describe historical evidence or output Candidate safety。blind global replace はしない。

## 9. Focused commands

```bash
uv run pytest tests/unit/application/test_issue_planning_prompt.py -q
uv run pytest tests/unit/application/test_issue_planning.py -q
uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q
uv run pytest tests/unit/commands/test_issue_planning.py -q
uv run pytest tests/cli_runtime/test_chatgpt_cli.py -q
uv run pytest tests/integration/test_issue_planning_e2e.py -q
```

Combined:

```bash
uv run pytest \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_e2e.py -q
```

Static / repo:

```bash
uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime tests
uv run mypy src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime
./spec-dock/scripts/spec-dock validate
git diff --check
```

repository が既存 `make lint` / ordinary pytest / installer smoke を標準 gate とする場合は追加実行する。

## 10. Stop conditions

| Condition | Required action |
|---|---|
| exact branch / HEAD mismatch | stop; do not use default branch |
| Oracle directory attachment unsupported | stop / replan |
| multiple path unsupported | stop; do not build temporary pack |
| continuation unsupported | stop; do not call personal wrapper |
| no-prewalk test requires production tree scan | design defect; return to S03/S04 |
| output ZIP / JSON test regresses | stop; input simplificationで緩和しない |
| Candidate / Human binding regresses | stop |
| provider / dogfood parity fails | stop before review |
| stale parent docs remain | closure incomplete |
| clarification wiring needs new public command | follow-up owner required |
| P0 / P1 review finding | repair and fresh review |
| unscoped worktree changes | isolate before implementation |

## 11. Completion evidence checklist

- [ ] exact implementation HEAD。
- [ ] Oracle capability evidence。
- [ ] no generated input pack。
- [ ] no attachment tree inspection。
- [ ] direct static / dynamic path。
- [ ] old CLI cutover。
- [ ] Blue continuity。
- [ ] fresh Red。
- [ ] output regressions pass。
- [ ] provider / installed / dogfood parity。
- [ ] docs / skills / parent Epic consistency。
- [ ] focused tests。
- [ ] static gates。
- [ ] SpecDock validation。
- [ ] fresh review。
- [ ] Human gate status accurately reported。
