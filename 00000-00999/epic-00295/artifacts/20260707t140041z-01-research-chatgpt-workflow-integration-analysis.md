# SpecDock ChatGPT authoring-pack workflow integration analysis

作成日: 2026-07-07

対象: `chemitaro/spec-dock` / PR 294 merge 後の `main` 相当 tree

入力:

- ChatGPT-Use / GPT-5.5 Pro Extended による分析
- `scripts/authoring-pack/` の README / helper scripts
- SpecDock の workflow docs
- Initiative / Epic / Issue planning skills
- `epic-00283-chatgpt-zip-authoring-pack-automation` の要件・設計・計画・過去調査 artifact

## 1. 結論

今回追加された `scripts/authoring-pack/` は、既存 workflow の外に置いたままだと「知っている人だけが使う便利スクリプト」で止まる。正式に活用するには、既存の Initiative / Epic / Issue planning workflow に **ChatGPT Batch Evidence Lane** として組み込むのがよい。

ただし、ChatGPT batch output を canonical workflow の置換として扱うべきではない。推奨は次の分担である。

- ChatGPT / GPT-5.5 Pro Extended: 広い候補生成、複数ファイル draft、Issue/Epic decomposition 案、設計・計画の初期具体化、自己レビュー観点の生成
- Codex / local workflow: scope 判定、採否判断、canonical docs への書き換え、profile authority、`.assurance.json`、artifact ledger、コマンド実行
- reviewer gate: fresh `spec-reviewer` による phase promotion
- human: scope expansion、優先順位、プロダクト判断、外部公開・破壊的操作・権限が必要な判断

したがって、既存の `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` は維持し、その前段または phase 内の draft producer として ChatGPT lane を追加するのが最小で強い。

## 2. 現状診断

現行 workflow は権威境界が明確である。canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator が採用・整形し、sub-agent や外部生成物は scope-local `artifacts/` evidence として扱う。`spec-reviewer` pass は phase promotion の必須条件であり、self-review、provisional、staged artifact、ChatGPT output は代替できない。

一方で、現在の planning skills は `ChatGPT authoring-pack` を first-read workflow spine として見つけられない。`scripts/authoring-pack/README.md` には preflight / ChatGPT Use / review / stage / validate / adoption の流れがあるが、`spec-dock-hub`、`spec-dock-initiative-planning`、`spec-dock-epic-planning`、`spec-dock-issue-planning` から自然に呼ばれる導線が薄い。

つまり現状は「安全な evidence-only helper はあるが、workflow に載っていない」状態である。

## 3. 推奨ターゲット workflow

共通形は次の lane とする。

```text
local source grounding
  -> prepare_chatgpt_authoring_pack.py
  -> ChatGPT Use / backend invocation
  -> review_chatgpt_authoring_pack.py
  -> scope-specific validator
  -> stage_chatgpt_authoring_pack.py
  -> EAL candidate
  -> local adoption decision
  -> canonical rewrite
  -> fresh spec-reviewer
  -> phase promotion / downstream handoff
```

重要なのは、ZIP 出力をそのまま正本化しないことである。採用単位は ZIP ではなく、claim / section / candidate / draft artifact である。ChatGPT output の `pass` は「helper validation が通った」にすぎず、「SpecDock reviewer pass」や「execution-ready」ではない。

## 4. Scope 別 lane

### 4.1 Initiative -> 複数 Epic candidates

ChatGPT に任せる:

- Initiative の outcome map
- architecture / product / operation 上の論点整理
- Epic candidate portfolio
- Epic 切り分け案、依存関係、優先順位案
- リスクと rejected alternatives

local に残す:

- 既存 Initiative / Epic との重複確認
- 新規 Epic 作成判断
- canonical Initiative docs への採用
- Epic ID / path / dependency mutation
- fresh `spec-reviewer`

短期的には manual validation + report ledger でよい。中期的には `validate_epic_candidates.py` 相当を追加するとよい。

### 4.2 Epic -> Epic design/plan + 複数 Issue draft packs

この lane が最も現行 scripts と相性がよい。

ChatGPT に任せる:

- Epic design draft
- Epic plan draft
- Issue candidate 一覧
- 各 Issue の draft requirement/design/plan
- profile recommendation
- Issue 間依存・順序案

local に残す:

- Issue 作成
- `authorized_profile`
- Issue-local artifact placement
- canonical Epic design/plan 採用
- Issue draft を正本化するかどうかの判断
- fresh `spec-reviewer`

推奨 sequence:

```text
reviewer-passed Epic requirement
  -> ChatGPT batch pack
  -> review ZIP/tree
  -> validate issue candidates
  -> local Issue slicing decision
  -> spec-dock new issue / new artifact
  -> Epic report に handoff path index
  -> Epic design/plan の fresh spec-reviewer
```

### 4.3 Issue -> selected-profile requirement/design/plan concretization

Issue 単位では、ChatGPT に profile を決めさせるより、local assurance が選んだ selected skeleton を ChatGPT に埋めさせる方が安全である。

ChatGPT に任せる:

- selected skeleton の許可 section fill
- requirement/design/plan draft
- implementation step の候補
- reviewer focus の候補

local に残す:

- assurance classify / compose
- `authorized_profile`
- template hash / section map authority
- canonical docs への rewrite
- fresh `spec-reviewer`

### 4.4 既存 Issue requirement approved -> design/plan generation

既存 Issue の requirement が既に通っている場合、ChatGPT は design/plan draft producer として有効である。ただし design 中に requirement gap が見つかった場合は、design で隠さず requirement phase に戻す。

推奨:

```text
approved requirement + local profile
  -> design/plan skeleton
  -> ChatGPT draft
  -> review / validate / stage
  -> canonical design rewrite
  -> fresh spec-reviewer
  -> canonical plan rewrite
  -> fresh spec-reviewer
  -> issue execution handoff
```

## 5. Skill / document 変更案

優先順:

1. `scripts/authoring-pack/README.md`
   - Initiative / Epic / Issue / existing Issue / final adoption の lane table を追加する。
   - dogfood-only、evidence-only、not runtime command を維持する。

2. `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
   - 共通の `ChatGPT batch evidence lane` を追加する。
   - preflight / review / stage / validate / EAL / fresh reviewer gate の共通 contract を定義する。

3. `workflow_initiative.md`
   - Initiative planning で Epic candidate portfolio を batch 生成できることを明示する。
   - Epic 作成と canonical adoption は local authority とする。

4. `workflow_epic.md` / `phase_plan_epic.md`
   - Epic -> Issue candidate pack を first-class handoff pattern とする。
   - `validate_issue_candidates.py` と Issue-local draft path index の関係を記述する。

5. `workflow_issue.md` / `phase_plan_issue.md`
   - selected-profile skeleton fill と existing Issue design/plan generation を追記する。
   - `authorized_profile` は local authority と明示する。

6. `spec-dock-hub/SKILL.md`
   - route selector に ChatGPT authoring-pack evidence lane を追加する。
   - 詳細手順は README / workflow docs へ委ねる。

7. planning leaf skills
   - `spec-dock-initiative-planning`
   - `spec-dock-epic-planning`
   - `spec-dock-issue-planning`
   - それぞれ Operating Spine に「non-trivial planning では authoring-pack lane を検討する」短い hook を入れる。

8. 必要なら repository-local dogfood skill
   - 例: `spec-dock-authoring-pack-dogfood`
   - shipped skill にする前の transitional surface として扱う。

## 6. `system-architect` / `implementation-planner` の扱い

完全置換はしない方がよい。

理由:

- 現行 workflow では specialist は canonical docs を直接書く役割ではなく、scope-local evidence producer である。
- Strict / Critical profile では specialist / reviewer evidence の意味が残る。
- ChatGPT output を specialist evidence の代替とすると、profile authority と reviewer gate の境界が曖昧になる。

推奨は次の再定義である。

- ChatGPT: high-depth batch draft producer
- `system-architect`: ChatGPT design draft の local critique / architecture risk reviewer / fallback author
- `implementation-planner`: ChatGPT plan draft の local critique / execution feasibility reviewer / fallback author
- main orchestrator: canonical adoption owner

これにより、ChatGPT の強みである「大きい仕事を一括で考える」能力を使いながら、SpecDock の gate 構造を崩さない。

## 7. Command / script integration model

workflow docs に個人環境の wrapper path は出さない。正式には backend command contract として記述する。

推奨 contract:

- `SPECDOCK_CHATGPT_COMMAND` を primary
- 必要なら `ORACLE_CHATGPT_COMMAND` を fallback
- 未設定なら明確に fail
- scripts は `shell=False` 相当の安全な command invocation を保つ
- local `oracle-chatgpt` wrapper は backend の一例であり、SpecDock の正式依存ではない

標準 command spine:

```bash
python scripts/authoring-pack/prepare_chatgpt_authoring_pack.py ...
python scripts/authoring-pack/invoke_chatgpt_backend.py ...
python scripts/authoring-pack/review_chatgpt_authoring_pack.py ...
python scripts/authoring-pack/validate_issue_candidates.py ...
python scripts/authoring-pack/validate_selected_skeleton_fill.py ...
python scripts/authoring-pack/stage_chatgpt_authoring_pack.py ...
```

ただし、これをすぐ `./spec-dock/scripts/spec-dock` の runtime command に昇格しない。まず dogfood workflow として docs / skills から使えるようにし、採用率・失敗率・review loop 削減効果を見てから runtime promotion を判断する。

## 8. Authority boundaries / safety gates

ChatGPT が主張してはいけないもの:

- `.assurance.json updated`
- `authorized_profile`
- `spec-reviewer passed`
- canonical adoption
- implementation complete
- issue execution-ready
- PR created / PR ready / mergeable

必須 gate:

- prompt 前: source hash / branch / profile / selected skeleton / stale condition の preflight
- invocation 前: preflight pass
- extract 前: ZIP path / size / suffix / nested archive / unsafe file / transcript / host path の review
- stage 前: review pass
- canonical rewrite 前: EAL candidate の claim-level 採否判断
- phase promotion 前: canonical docs + fresh `spec-reviewer`
- execution 前: Issue workflow の execution readiness gate

## 9. Rollout plan

### Phase 0: dogfood lane の明文化

- `scripts/authoring-pack/README.md` を lane table 付きにする。
- backend command examples は env contract だけにする。
- local wrapper path を正式 workflow に書かない。

### Phase 1: workflow bridge

- `workflow_spec_authoring.md` に共通 lane を追加する。
- Initiative / Epic / Issue docs に thin reference を追加する。

### Phase 2: skill exposure

- hub に route を追加する。
- planning leaf skills に短い operational hook を追加する。
- skills には詳細手順を貼らず、README / workflow docs へリンクする。

### Phase 3: validation gap 補強

- Initiative -> Epic 用 `validate_epic_candidates.py` を検討する。
- staged EAL candidate の lint を検討する。
- multi-Issue draft placement の helper を検討する。

### Phase 4: runtime promotion 判断

- dogfood 実績を見て、`scripts/authoring-pack/` を runtime command 化するか判断する。

判断指標:

- reviewer loop 削減
- human rewrite effort 削減
- stale / rejected output rate
- scope drift 発生率
- Issue/Epic slicing の品質
- agent の迷い・手戻り削減

## 10. リスクと退ける案

退ける案:

- ChatGPT ZIP をそのまま canonical docs として採用する。
- ChatGPT に `authorized_profile` を決めさせる。
- ChatGPT output を fresh `spec-reviewer` pass とみなす。
- `system-architect` / `implementation-planner` を完全削除する。
- dogfood-only scripts を即 runtime command 化する。
- 個人環境の `oracle-chatgpt` wrapper path を workflow に直書きする。

主要リスク:

- over-batching により upstream scope が固まる前に downstream detail が正本化される。
- staged artifact の `pass` が reviewer pass と誤解される。
- ChatGPT が profile / assurance / PR readiness を越権主張する。
- README / workflow docs / skills / scripts が drift し、agent が使わなくなる。
- GitHub connector / pushed branch 前提が崩れたときの fallback が曖昧になる。

## 11. 次にやるとよいこと

最初の実装 Epic は、次の順で小さく切るのがよい。

1. README に lane table と usage policy を追加する。
2. `workflow_spec_authoring.md` に共通 `ChatGPT Batch Evidence Lane` を追加する。
3. Initiative / Epic / Issue workflow docs に thin reference を追加する。
4. hub / planning skills に route hook を追加する。
5. dogfood-only skill を作るか判断する。
6. `validate_epic_candidates.py` と EAL lint を follow-up Issue として検討する。

この順にすると、既存 gate を壊さず、今回追加した scripts を実運用の workflow に載せられる。

## 12. ChatGPT-Use 実行メモ

- 実行 slug: `specdock-chatgpt-workflow-integratio-analysis`
- Model evidence: `gpt-5.5-pro`, Pro Extended
- Prompt estimate: 約 141,851 tokens
- 添付: 34 files
- 実行時間: 約 12 分
- ChatGPT 側の未検証事項: scripts / tests / `spec-reviewer` / `./spec-dock/scripts/spec-dock validate` は未実行
