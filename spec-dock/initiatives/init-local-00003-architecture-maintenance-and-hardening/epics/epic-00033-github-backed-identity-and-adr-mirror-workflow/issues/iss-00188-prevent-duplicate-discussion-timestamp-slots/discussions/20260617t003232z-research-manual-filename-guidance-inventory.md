---
種別: research
ID: "20260617t003232z-research"
タイトル: "Manual Filename Guidance Inventory"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["iss-00188"]
関連:
  - "20260617t003044z-adr"
  - "20260617t003048z-adr"
authority: "synthesized"
derived_from:
  - "20260617t000227z-research"
  - "20260617t000333z-interview"
  - "20260617t002152z-disc"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260617t003232z-research Manual Filename Guidance Inventory

## 調査目的
- #188 の requirement / design / plan を固めるため、repo 内で shipped skill / workflow / docs が manual timestamp filename generation を促している箇所を分類する。
- 単なる naming grammar reference と、実際に agent に filename を手作業で作らせる危険な target guidance を分ける。

## sources / 調査方法
- 参照先:
  - `.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/AGENTS.md`
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/spec_dock/templates/**`
  - `.codex/AGENTS.md`
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
  - `spec-dock/docs/**`
  - `spec-dock/system/**`
- 検証手順:
  - `rg -n "<ts>|timestamped|timestamp|disc-pr-repair|target filename|filename|path=" ...`
  - `./spec-dock/scripts/spec-dock validate`
- 実験条件:
  - Active issue: `iss-00188`
  - Branch: `iss-00188-prevent-duplicate-discussion-timestamp-slots`

## facts / 観測できた事実
- `github-pr-merge-preparer` の provider asset と dogfooding copy は、PR repair batch / unit について timestamped target の例を示している。
  - Batch: create/update a timestamped target such as `<ts>-disc-pr-repair-batch.md`
  - Unit: create the repair unit as a timestamped issue-local `disc` such as `<ts>-disc-pr-repair-unit-<unit-slug>.md`
- `spec-dock-hub` は delegated architecture / planning evidence を `discussions/<ts>-<kind>-<slug>.md` と説明している。
  - これは exact PR repair target ほど危険ではないが、agent role が filename を直接作るよう読める余地がある。
- `.codex/AGENTS.md` と provider asset の `.codex/AGENTS.md` は delegated authoring output の allowed filenames として `<ts>-<kind>-<slug>.md` / `<ts>-<nn>-<kind>-<slug>.md` を列挙している。
- `.codex/agents/system-architect.toml` / `.codex/agents/implementation-planner.toml` と provider asset copy は、delegated role に "Create exactly one new flat Markdown file" と "Use filenames `<timestamp>-...`" を指示している。
  - これは manual filename construction を明示的に促しているため、#188 scope に含めるべきである。
- `workflow_spec_authoring.md` / `workflow_issue.md` / phase docs は allowed filename rule として `<ts>-<kind>-<slug>.md` を説明している。
  - これは validation / allowed path contract の説明として必要だが、new artifact creation では generator command を使うべきことを併記する余地がある。
- `reference_naming.md` / `workflow_adr.md` / `rules/*/discussions.md` は naming grammar の正本説明であり、grammar 自体の記述は必要。
- `new doc` command surface は `doc_type`, scope, `--title`, optional `--slug` を受け取る。外部 template/body を直接受け取る option は現時点では確認できなかった。
- `./spec-dock/scripts/spec-dock validate` は `spec-dock: ok (validate) nodes=97` で成功した。

## inference / 推測
- もっとも優先度が高い修正対象は `github-pr-merge-preparer` の PR repair batch / unit guidance である。
- 次に、`.codex/agents/system-architect.toml` / `.codex/agents/implementation-planner.toml` と `.codex/AGENTS.md` は manual filename instruction を generator command instruction に変える必要がある。
- `spec-dock-hub` / delegated authoring docs は "filename rule" を説明するだけでなく "runtime command creates the file and the returned path is authoritative" と明示した方がよい。
- `reference_naming.md` の grammar reference は削除すべきではない。削除すると validation / contract の理解が難しくなる。

## unverified / 未検証事項
- `new doc` に `--template-file` / `--body-file` / stdin body のような option を追加するべきか、#188 では generated path 作成だけを command 化し、本文更新は generated path に対する guarded edit として扱うべきか。
  - これは design で決める必要がある。

## question candidates / 質問候補
- source-grounded に解けず、人間判断が必要な候補:
  - なし。現時点の requirement は、既存回答と ADR で十分に固められる。
- pressure-test question として切り出すべき候補:
  - Template/body 反映まで #188 で command option 化するか、まずは generated path を作ってから skill が本文を更新する guidance に留めるか。
- 質問せずに解決できた候補:
  - Timestamp grammar は #188 では変えない。
  - Suffix fallback は残す。
  - Manual filename construction は shipped skill/workflow guidance から外す。

## terminology conflicts / 用語衝突
- `filename rule`:
  - Existing docs では validation / allowed path contract を意味している箇所がある。
  - Agent-facing guidance では "agent が filename を組み立てる手順" と誤読され得る。
- `<timestamp>`:
  - `reference_naming.md` では grammar variable として必要。
  - `.codex/agents/*.toml` では delegated agent が実ファイル名を自作する instruction として読める。
- `timestamped target`:
  - PR repair guidance では target filename の手作業作成を促す表現になっている。
  - #188 では generated artifact path に置き換える必要がある。

## edge cases / 具体シナリオ
- Edge case:
  - 1回の PR repair workflow で batch と複数 unit を短時間に連続生成する。
- Requirement / design / plan への影響:
  - Runtime generator は同一 scope 内の同秒 collision を wait/retry して、通常は suffix なし path を返す必要がある。
  - Suffix fallback は frozen clock / bounded wait exhaustion / race の safety fallback として残す。

## implications / 判断への含意
- Requirement:
  - Shipped skills / workflows MUST NOT instruct agents to manually assemble timestamped discussion artifact filenames for new generated artifacts.
  - Runtime/script generator MUST allocate and create discussion artifact files and return authoritative path/doc_id.
- Design:
  - `new doc` or adjacent runtime surface must support PR repair batch/unit artifact creation without caller-provided filename.
  - Design must choose between:
    - generating the artifact file from existing discussion templates, then letting skill/workflow update the returned path safely;
    - adding a runtime-supported external template/body input.
  - Agent-facing docs should distinguish grammar reference from generation procedure.
- Plan:
  - Add regression search/test for PR repair manual target guidance.
  - Add regression search/test for delegated authoring role configs that currently say "Use filenames `<timestamp>-...`".
  - Add allocator tests for wait-first, suffix fallback, and existing validation behavior.

## リスク/制約
- If template/body support is not implemented in runtime, skill guidance may still need a safe two-step flow: generate artifact first, then update generated file content without changing filename/front matter.
- Updating only dogfooding `.agents` copy would be insufficient; provider asset under `src/spec_dock/assets/install_root/` must be updated first.

## 反映先
- reflected_to:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`

## 参考（References）
- `20260617t003044z-adr-runtime-owned-discussion-artifact-creation.md`
- `20260617t003048z-adr-wait-on-discussion-timestamp-collision.md`
