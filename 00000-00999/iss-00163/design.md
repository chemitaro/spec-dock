---
種別: 設計書（Issue）
ID: "iss-00163"
タイトル: "Revise Spec Dock Clarification As Skill Owned Grill Workflow"
関連GitHub: ["#163"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00163 Revise Spec Dock Clarification As Skill Owned Grill Workflow — 設計

## 目的・制約

- 目的:
  - `spec-dock-clarification` を first-read skill-owned workflow にし、agent が docs を読まなくても source-grounded grill loop の最初の行動を理解できるようにする。
  - `workflow_clarification.md` は workflow の実行 authority ではなく、artifact semantics / lifecycle / link navigation を支える bridge/reference doc に寄せる。
  - `interview` / `research` / `disc` templates は clarification-specific support slots を持つ scaffold として整える。
- 必須:
  - Provider source を正本として更新し、dogfooding mirror を parity verification target とする。
  - User-intent clarification が blocking になった場合は、deep-consultant や specialist proxy ではなくユーザーへ直接一問で聞く境界を skill に置く。
- 禁止:
  - Hub route table / broader leaf routing を変更しない。
  - Runtime command / validation harness を追加しない。
  - `workflow_clarification.md` を削除しない。
  - Templates 全体の global consistency rewrite をしない。

## 既存実装 / 規約の理解

- 現行 `spec-dock-clarification/SKILL.md`:
  - `workflow_clarification.md` を source of truth とする薄い reminder。
  - Source read、一問一答、artifact selection、adoption reporting はあるが、loop の手順と stop condition が spine として弱い。
- 現行 `workflow_clarification.md`:
  - first-class workflow doc として mandatory operational steps を持っている。
  - `iss-00163` 後は、skill-owned workflow を隠さず、artifact semantics / lifecycle / bridge detail を説明する doc にする。
- 現行 templates:
  - `interview.md` は unanswered / answered lifecycle を持つが、pressure-test question / blocking condition / direct-user-only boundary を明示すると skill と接続しやすい。
  - `research.md` は facts / inference / unverified を分けているが、question candidates への接続が弱い。
  - `disc.md` は synthesis / ADR triage を持つが、clarification loop からの adoption reflection を少し強める余地がある。
- 採用するパターン:
  - `iss-00159` の first-read skill spine 語彙。
  - `iss-00162` の ownership model: skill-owned spine / docs-owned detail / template-owned scaffold / bridge-reference。

## 採用方針 / トレードオフ

- Skill:
  - Read-first -> provisional understanding -> gap classification -> one pressure-test question -> artifact capture -> answer adoption / handoff の loop を `SKILL.md` に置く。
  - Detailed schema や template field semantics は docs/templates に送る。
- Workflow doc:
  - 削除せず、bridge/reference として残す。
  - "workflow is source of truth" / "mandatory runbook authority" と読める wording を避ける。
  - Skill-owned workflow の補足 detail、artifact lifecycle、formal question trigger、adoption evidence semantics を説明する。
- Templates:
  - Clarification-specific minimum slots に限定する。
  - `iss-00166` の global template consistency を先取りしない。

## ディレクトリ / ファイル変更計画

```text
.
|-- src/spec_dock/assets/install_root/.agents/skills/
|   `-- spec-dock-clarification/SKILL.md
|       # 変更: first-read source-grounded grill loop、mode判断、direct-user question boundary、handoff output
|-- .agents/skills/
|   `-- spec-dock-clarification/SKILL.md
|       # 変更: provider mirror parity
|-- src/spec_dock/assets/spec_dock/docs/
|   `-- workflow_clarification.md
|       # 変更: bridge/reference doc化、artifact semanticsとadoption detailに寄せる
|-- spec-dock/docs/
|   `-- workflow_clarification.md
|       # 変更: dogfooding mirror
|-- src/spec_dock/assets/spec_dock/templates/discussions/
|   |-- interview.md
|   |-- research.md
|   `-- disc.md
|       # 変更: clarification-specific minimum slots
|-- spec-dock/templates/discussions/
|   |-- interview.md
|   |-- research.md
|   `-- disc.md
|       # 変更: dogfooding mirror
`-- spec-dock/active/issue/report.md
    # 変更: Evidence Adoption, authoring gates, implementation evidence, reviewer gates
```

## 要件 → 設計マッピング

- AC-001 -> Skill first-read grill loop。
- AC-002 -> `workflow_clarification.md` bridge/reference wording。
- AC-003 -> `interview.md` clarification decision lifecycle slots。
- AC-004 -> `research.md` / `disc.md` clarification support slots。
- AC-005 -> Provider/mirror parity, `sync`, `validate`, targeted inspection evidence。
- EC-001 -> Workflow doc retained as bridge/reference; no delete.
- EC-002 -> Skill mode contract for analysis-only / draft-only / canonical authoring.
- EC-003 -> Skill stop condition: user-intent blocker asks user directly; no proxy.

## 実装順序

1. Skill spine first:
   - Fix the operational loop where the risk is highest.
   - Provider and mirror must stay byte-equivalent.
2. Workflow doc bridge:
   - Reword doc after skill spine exists so the doc can point back to skill-owned workflow.
   - Keep links intact.
3. Templates:
   - Add only clarification-specific support slots.
   - Avoid global formatting/style normalization.
4. Verification and docs impact:
   - `cmp` provider/mirror pairs.
   - Targeted parity unittest for checked-in dogfooding assets.
   - `sync`, `validate`, `git diff --check`.

## テスト戦略

- Inspect-only:
  - Skill contains the loop keywords and no stale "workflow doc is source of truth" authority claim.
  - Workflow doc states bridge/reference and points to the skill-owned workflow.
  - Templates include clarification-specific slots for pressure-test question, source-grounding, answer/adoption reflection, question candidates, and synthesis/adoption target.
- Covered-existing:
  - Provider/mirror asset parity via:
    - `cmp -s <provider> <mirror>`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`
- Manual-required:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`

## リスク / ロールバック

- リスク:
  - Skill に詳細を書き込みすぎると docs-owned semantics を吸収する。
  - Template slot 追加が `iss-00166` の global template consistency を先取りする。
  - Workflow doc bridge 化により既存リンク利用者が迷う可能性がある。
- 緩和:
  - Skill は operational spine に限定し、詳細 semantics は workflow doc / templates へ明示 route する。
  - Templates は clarification-specific slots に限定する。
  - Workflow doc は削除せず、既存 link compatibility を維持する。
- ロールバック:
  - Changed files are text-only shipped assets. Revert provider/mirror pairs together if reviewer finds boundary drift.

## 未確定事項

- Blocking question:
  - なし。
- Deferred:
  - `workflow_clarification.md` の full retirement は first wave 後の link inventory 次第。
  - Global template examples / wording normalization は `iss-00166`。
