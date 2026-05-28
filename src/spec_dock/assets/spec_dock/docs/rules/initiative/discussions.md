# 議論ルール（discussions/rules.md）

このディレクトリには initiative に紐づく議論資料を置きます。

- Discussion workflow: `spec-dock/docs/workflow_adr.md`
- Naming rules: `spec-dock/docs/reference_naming.md`
- 作成される docs はこの directory に timestamp-prefixed original として保存されます（標準: `<ts>-<kind>-<slug>.md` / same-second collision: `<ts>-<nn>-<kind>-<slug>.md`）。legacy sequential files は grandfathered で、自動 rename しません。
- Delegated authoring の draft / analysis / discussion-local report も、この directory の直下に同じ命名規則で flat Markdown として保存します。per-agent directory、run/task directory、global draft store、`discussions/delegated-authoring/` は新規出力先にしません。
- Sub-agent-created draft は canonical docs への直接書き込みではなく、scope-local `discussions/` 直下の flat Markdown として保存します。`draft-requirement` / `draft-design` / `draft-plan` は draft 専用 template を持たず、scope kind に応じた canonical template を直接 source として render します。canonical docs remain main-orchestrator-only. `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` は自己主張しません。
- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator single-writer authority です。discussion draft は evidence であり、採用は canonical `report.md` の Evidence Adoption Ledger と canonical docs への再記述で成立します。
- `report.md` は canonical observed evidence ledger であり、`new doc report` の discussion doc type ではありません。
- Historical delegated-authoring manifest/Profile/probe/session artifacts は grandfathered evidence です。current delegated drafts が flat model を使うことだけを理由に削除、rename、validation failure 化しません。
- 実行場所: コマンドはリポジトリ root から実行してください。`./spec-dock/scripts/spec-dock ...` はその位置で保証される実行経路で、nested directory では相対 path が変わります。
- Current catalog:
  - `scratch`: raw capture。非 authoritative。未整理の発話、観察、思考、会話ログを置く。
  - `interview`: 一問一答の正式質問シート。未回答で作成し、回答後に同じ file へ回答、採用判断、反映先への含意を追記する。既存の複数質問 artifact は grandfathered として壊さない。
  - `research`: 事実調査。sources、facts、inference、unverified、terms、edge cases、implications を分ける。
  - `disc`: synthesis / reflection proposal / ADR candidate triage。採否確定 ledger ではなく、採用は canonical docs / ADR / `report.md` の Evidence Adoption Ledger で決める。
  - `adr`: 意思決定記録。hard to reverse、surprising without context、real tradeoff を満たす長期判断に絞る。
  - `draft-requirement`: scope kind に応じた canonical requirement template を直接 source として render する discussion-local draft。
  - `draft-design`: scope kind に応じた canonical design template を直接 source として render する discussion-local draft。
  - `draft-plan`: scope kind に応じた canonical plan template を直接 source として render する discussion-local draft。
- `note` は retired。既存 artifact は grandfathered だが、新規 raw capture は `scratch` を使う。
- `disc` が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、生ログは `scratch`、長期判断は `adr` へ分割してください。採否確定や reflected evidence は `report.md` に昇格して記録してください。
- Create commands:
  - `./spec-dock/scripts/spec-dock new doc scratch --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc interview --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc research --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc disc --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc adr --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc draft-requirement --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc draft-design --initiative <id> --title "<title>"`
  - `./spec-dock/scripts/spec-dock new doc draft-plan --initiative <id> --title "<title>"`
