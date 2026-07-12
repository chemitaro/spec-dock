---
種別: 要件定義書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
関連GitHub: ["#297"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00297 Authoring Command Skeleton — 要件定義

## 目的

この Issue は、Epic `epic-00295` の runtime surface の入口として、installed runtime に `authoring` command group の骨格を追加する。利用者と後続 Issue は、`./spec-dock/scripts/spec-dock authoring --help` から supported / deferred boundary を確認できる。

この Issue では command group、help、machine-readable status を持つ unsupported/deferred 応答だけを実装する。GitHub sync preflight、prompt pack、backend invocation、ZIP review/stage、candidate validation、approval check の実質ロジックは後続 Issue の責務とする。

## 背景

`iss-00296` で authoring-pack helper inventory は provider-side installed asset として配布されるようになった。一方、consumer repository で使う primary entrypoint はまだ `spec-dock authoring ...` として存在しない。後続 Issue が機能を増やす前に、runtime parser / registry / command outcome の形に沿った command group skeleton を用意する必要がある。

## スコープ

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` を追加する。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` に `authoring` command group を追加する。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` に command specs を登録する。
- provider-side 変更に合わせて dogfooding runtime mirror を更新する。
- `authoring --help` で command group と deferred subcommands の境界を表示する。
- 初期 subcommand は unsupported/deferred として fail-closed し、`CommandOutcome` 互換の text diagnostics を返す。
- tests で help、dispatch、unsupported/deferred exit code、installed init reachability を確認する。

## 対象外

- `authoring preflight github-sync` の実質ロジック。
- `authoring pack prepare`、`authoring backend invoke`、`authoring pack review`、`authoring pack stage` の実質ロジック。
- `authoring validate ...`、`authoring approval check` の実質ロジック。
- `authoring adopt`、`create-issues-from-zip`、`mark-reviewer-pass`、`set-authorized-profile`、`issue-execution-ready`、`pr-ready` の実装。
- canonical docs、`.assurance.json`、authorized profile、reviewer pass、execution-ready、PR-ready を command が主張すること。
- この Issue での PR delivery。PR は final quality gate Issue `iss-00307` に defer する。

## 要件

- `authoring` command group は installed runtime parser から認識される。
- `authoring --help` は、supported surface が skeleton であることと、後続 Issue に defer される subcommands を明確に表示する。
- deferred subcommand を実行した場合、exit code は non-zero で、success / adoption / reviewer pass / PR-ready を示す文言を返さない。
- machine-readable automation が扱えるよう、deferred 応答には `status=deferred`、`authority=evidence_only`、`next_issue=<issue-id>` 相当の安定した診断を含める。
- root `scripts/authoring-pack/` ではなく provider-side runtime source of truth を変更する。
- dogfooding mirror は validation artifact として provider-side runtime 変更に追従する。

## 受け入れ条件

- `./spec-dock/scripts/spec-dock authoring --help` が表示できる。
- `./spec-dock/scripts/spec-dock authoring preflight github-sync` は deferred / unsupported として non-zero で終了する。
- `./spec-dock/scripts/spec-dock authoring pack prepare` は deferred / unsupported として non-zero で終了する。
- `./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption` は deferred / unsupported として non-zero で終了する。
- `uv run pytest tests/cli_runtime` または focused CLI runtime tests が成功する。
- `./spec-dock/scripts/spec-dock validate` が成功する。
- `report.md` に no-per-Issue-PR defer evidence が残る。

## Draft adoption

- 採用元:
  - `artifacts/20260707t171238z-draft-requirement-add-authoring-command-skeleton-draft-requirement.md`
  - `artifacts/20260707t171239z-draft-design-add-authoring-command-skeleton-draft-design.md`
  - `artifacts/20260707t171239z-01-draft-plan-add-authoring-command-skeleton-draft-plan.md`
- 採用判断:
  - command group skeleton、parser / registry registration、deferred command boundary、CommandOutcome compatibility、status taxonomy、PR defer 方針を採用する。
  - draft の branch wording、authority self-claim、後続 Issue の実質ロジックは正本 authority として採用しない。
