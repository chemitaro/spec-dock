---
kind: disc
scope: issue
issue_id: iss-00134
created_at: 2026-05-28T03:51:17Z
created_by: deep-consultant
status: answered
authority: synthesized
derived_from:
  - 20260528t020135z-interview-grill-scope-and-surfaces.md
  - 20260528t021116z-interview-question-sheet-artifact-unit.md
  - 20260528t021530z-interview-question-sheet-promotion-lifecycle.md
  - 20260528t023921z-interview-question-sheet-template-artifact-set.md
  - 20260528t024729z-interview-question-sheet-common-template-catalog.md
  - 20260528t032050z-interview-question-sheet-missing-template-criteria.md
  - 20260528t032332z-interview-question-sheet-reflection-record-location.md
  - 20260528t033128z-interview-question-sheet-interview-template-migration.md
  - 20260528t033641z-interview-question-sheet-question-artifact-threshold.md
  - 20260528t034100z-interview-question-sheet-required-fields.md
  - 20260528t034302z-interview-question-sheet-lifecycle-status.md
reflected_to:
  - requirement.md
---

# deep consultant 追加判断: template / workflow follow-up

## 位置づけ

この文書は、ユーザー指示により deep consultant を一次回答役として起用した結果を記録する discussion artifact である。
deep consultant は人間ユーザーへ直接質問せず、既存議論と repository context に基づき、回答可能な判断と人間確認が必要な判断を切り分けた。

## consultant summary

- 現時点で、人間に追加確認しないと `requirement.md` を進められない論点は残っていない。
- Q001-Q016 で、workflow の目的、質問経路、artifact 単位、template 方針、正式質問シート条件、lifecycle / status は十分に決まっている。
- 残っているのは人間の価値判断ではなく、`design.md` で詰める実装・template 設計の詳細である。
- ただし、design 中に既存 `report.md` との責務衝突など、現在の採用方針を覆す証拠が出た場合だけ再確認対象である。

## answerable decisions

- `interview.md` の lifecycle / status は Q016 の B で要件レベルとして十分であり、補足は `design.md` 側で行えばよい。
- `status` は質問状態だけに限定し、`unanswered` / `answered` / `superseded` / `deferred` を持たせるのが妥当である。
- 採用状態は `adoption_status`、反映先は `reflected_to`、根拠性は `authority` に分離する。
- `status` に `adopted` や `reflected` を混ぜない方針を維持すべきである。
- `research.md` / `disc.md` / `adr.md` / `report.md` の再設計について、追加の人間確認は不要である。
- Q009-Q011 で「既存 template を共通 template として再設計し、独立 lifecycle が必要な場合だけ追加」という判断が済んでいる。
- `research.md` は source-grounding / fact / inference / unverified / implication を扱う共通 template として強化する。
- `disc.md` は synthesis、中間レポート、上位レポート、reflection proposal、ADR candidate triage を扱う proposed artifact として強化する。
- `adr.md` は final / durable decision 用の共通 template として維持し、ADR candidate triage は原則 `disc.md` 側で扱う。
- `report.md` は observed evidence ledger / adoption ledger として維持する。
- `reflection.md` は初期追加しない判断でよい。
- Q013 で明示されきらなかった既存複数質問型 artifact の扱いは、grandfathered が妥当である。
- 既存 Q001-Q003 を分割する必要はない。
- `requirement.md` と `design.md` の境界は、requirement が「何を満たすべきか」、design が「どの file path / frontmatter / section / transition / migration / tests で実現するか」である。

## human required questions

なし。

## requirement update candidates

- `derived_from` に Q007-Q016 の採用済み question sheet を追加する。
- Q015 を反映し、PlantUML 図を「すべての正式質問シートで機械的に必須」ではなく「重要判断で理解を助ける場合は原則含める条件付き項目」として整合させる。
- AC-003 / AC-004 を Q016 に合わせ、質問前は `status: unanswered` / `authority: proposed` / `adoption_status: unreviewed`、回答後は `status: answered` / `authority: user-approved` / 採用判断に応じた `adoption_status` とする。
- Q014 を反映し、一問一答は常時標準、正式質問シートは重要判断のみ必須、軽微な確認は chat 上の一問でよい、と明記する。
- Q009-Q011 を反映し、`research` / `interview` / `disc` / `adr` / `report` は grill 専用 variant ではなく共通 template として再設計する方針を明確化する。
- Q016 の deep consultant 方針を、細かい設計判断の一次回答役として requirement に残す。
- 人間確認は判断材料不足、権限不足、価値判断が必要な場合だけに限定する。

## design handoff candidates

- `interview.md` の具体 section、frontmatter key、allowed values、状態遷移、legacy artifact の読み方。
- `scope_id` と既存 `issue_id` / `epic_id` / `initiative_id` 表現の互換方針。
- `research.md` の source-grounding 用 section 設計。fact / inference / unverified / references / evidence strength の分離。
- `disc.md` の synthesis、中間レポート、reflection proposal、ADR candidate triage の section 設計。
- `adr.md` へ昇格する条件。`disc.md` で triage し、ADR は durable decision のみを扱う境界。
- `report.md` の Evidence Adoption Ledger を、要件定義前の discussion adoption にも使えるかの具体設計。
- `reflection.md` / `adoption-ledger.md` を追加しない初期設計と、追加検討が必要になる衝突条件。
- provider-side template path、dogfooding mirror 更新要否、CLI `new doc` catalog への反映範囲。
- 既存複数質問型 interview artifact は自動移行せず grandfathered とする migration note。
- template 変更に対する scaffold / installer / runtime catalog の test 方針。
