---
種別: 要件定義書（Issue）
ID: "iss-00285"
タイトル: "安全な仕様作成パック検査とスキーマ検証を実装する"
関連GitHub: ["#285"]
状態: "review-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00283", "init-local-00003"]
---

# iss-00285 安全な仕様作成パック検査とスキーマ検証を実装する — 要件定義

## 位置づけ

この Issue は `epic-00283` の T1 安全検査 / スキーマ検証 slice です。`iss-00284` が作成した dogfood-only prompt pack / preflight output を入力契約として参照し、ChatGPT ZIP 仕様作成パックを未信頼の evidence-only candidate として検査します。

この Issue の成果物は `scripts/authoring-pack/` 配下の dogfood-only helper です。配布 runtime command ではありません。ChatGPT ZIP output、展開済み tree、validation report、Markdown summary は正本ではなく、canonical SpecDock docs を直接上書きしません。

## 目的

ChatGPT ZIP 仕様作成パックについて、展開前の ZIP central directory、パス、ファイル種別、必須 metadata、source hash、stale 条件、危険な権威主張を fail-closed に検査できるようにします。

## 親 Epic への対応

- 対応要件: E-RQ-004, E-RQ-005
- 関連要件: E-RQ-002, E-RQ-006, E-RQ-007, E-RQ-008, E-RQ-010
- 対応受け入れ条件: E-AC-002, E-AC-003, E-AC-004
- 関連受け入れ条件: E-AC-005, E-AC-008, E-AC-009, E-AC-010
- 推奨グレード: `strict`
- 実施単位: T1 安全検査 / スキーマ検証

## 範囲

- `scripts/authoring-pack/` 配下に dogfood-only validator script / library を追加する。
- actual `.zip` input を主経路として扱い、central directory を展開前に検査する。
- 隔離済み extracted directory tree input を補助経路として扱い、schema / claim / source hash を検査できるようにする。ただし tree input は ZIP central directory safety evidence の代替にはしない。
- valid pack の root は単一 `specdock-authoring-pack/` とする。
- 必須 metadata として `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`adoption/adoption-map.json` を検査する。
- 任意 evidence として `README.md`、`drafts/`、`candidates/issues/`、`reviewer-focus/` を検査対象に含める。
- Markdown / JSON / plain text 中の reviewer pass、adopted claim、canonical overwrite、`.assurance.json` mutation claim、PR 作成 claim、implementation complete claim を検出する。
- ZIP 内 `source-manifest.json` と `iss-00284` preflight / source snapshot を照合し、source hash mismatch を `stale` として扱う。
- 結果は JSON validation report と Markdown summary に出す。
- diagnostics は host-local absolute path、secret、private key、token、raw transcript を出さない。

## 対象外

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` 配下の runtime command 追加。
- canonical `requirement.md` / `design.md` / `plan.md` の自動上書き。
- `.assurance.json` の作成・更新。
- reviewer gate の置換、または `spec-reviewer` / `code-reviewer` / `qa-reviewer` pass の自己主張。
- Pull Request 作成。この Epic の Pull Request は `iss-00293` に集約する。
- raw ZIP または未検査の展開済み tree を durable canonical artifact として保存する契約。
- staged diff rendering、profile-controlled skeleton fill、dogfood scenario、metrics、runtime promotion 判断。

## 入力

- `--input <path>`: `.zip` file または extracted directory tree。
- `--preflight <path>`: `iss-00284` 由来の `preflight.json` または equivalent source snapshot。
- `--output-dir <path>`: validation report / summary の出力先。repo 外を基本とし、repo 内の場合は明示された Issue-local artifacts path に限定する。
- 任意 `--input-kind zip|tree|auto`: input 種別。未指定時は拡張子と filesystem state から判定する。
- 任意 `--extract-dir <path>`: ZIP の central directory safety が通った場合だけ safe extraction する隔離先。

## 出力

- `validation-report.json`
- `validation-summary.md`
- 任意 `extracted/` または `safe-tree/`: safe central directory 検査を通過した ZIP に限り作成する。

すべての出力は次の authority boundary を持ちます。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

## status taxonomy

- `pass`: ZIP / tree がこの Issue の必須安全検査と schema 検査を満たす。canonical adoption は未実施。
- `fail`: 入力引数、JSON schema、必須 file / field、expected root が不正。
- `blocked`: local observation、preflight、filesystem permission などが不足し、判定できない。
- `stale`: source hash、repo/ref、preflight snapshot、stale_if 条件が一致しない。
- `rejected`: safety boundary violation。例: path traversal、absolute path、hidden path、symlink、nested archive、binary、secret-looking path、unsafe authority claim。
- `deferred`: 後続 Issue の責務。例: staged diff rendering、profile-controlled skeleton fill、EAL final adoption。
- `unreviewed`: artifact adoption state。validator 実行 status ではない。

## 受け入れ条件

### AC-001: 親 Epic trace が保持される

- 前提: validator の report を読む。
- 操作: report の `trace` と `inputs` を確認する。
- 期待結果: E-RQ-004, E-RQ-005 / E-AC-002, E-AC-003, E-AC-004 に trace でき、`iss-00284` preflight source snapshot への依存が記録される。
- 観測点: `validation-report.json`、Issue `report.md`。

### AC-002: actual ZIP は展開前に安全検査される

- 前提: `.zip` fixture がある。
- 操作: validator を実行する。
- 期待結果: central directory の root / path / size / mode / type を展開前に検査し、危険な entry があれば `rejected` で停止する。
- 観測点: `validation-report.json`、extract dir 不作成、repo 内副作用なし。

### AC-003: expected root と mandatory files が検査される

- 前提: valid / invalid pack fixture がある。
- 操作: validator を実行する。
- 期待結果: 単一 root `specdock-authoring-pack/`、`manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`adoption/adoption-map.json` が必須として検査される。欠落は `fail` になる。
- 観測点: focused pytest、`validation-report.json`。

### AC-004: unsafe path / file type は fail-closed に拒否される

- 前提: path traversal、absolute path、hidden path、symlink、hardlink/device-like mode、binary、nested archive を含む fixture がある。
- 操作: validator を実行する。
- 期待結果: ZIP input では展開前に `rejected` となり、tree input でも safety boundary violation として `rejected` になる。
- 観測点: focused pytest、extract dir 不作成、post-run diff。

### AC-005: source hash / stale 条件が検査される

- 前提: `iss-00284` preflight または source snapshot と ZIP 内 source-manifest がある。
- 操作: validator を実行する。
- 期待結果: source path / sha256 mismatch、missing expected source snapshot、stale_if hit を `stale` または `blocked` として report し、`pass` にしない。
- 観測点: focused pytest、`validation-report.json`。

### AC-006: unsafe authority claim が検出される

- 前提: reviewer pass、`adoption_status: adopted`、canonical overwrite、`.assurance.json updated`、PR 作成、implementation complete を含む fixture がある。
- 操作: validator を実行する。
- 期待結果: 危険 claim は `rejected` または claim-level adoption-ineligible として report され、fresh reviewer gate と混同されない。
- 観測点: focused pytest、`validation-report.json`。

### AC-007: diagnostics が安全である

- 前提: host path、secret-looking path、private key header、token-like value を含む fixture がある。
- 操作: validator を実行する。
- 期待結果: stdout、stderr、JSON report、Markdown summary に host-local absolute path、secret、private key、token、raw transcript が出ない。
- 観測点: focused pytest、redaction check。

### AC-008: canonical docs と assurance は変更されない

- 前提: validator 実行前の workspace がある。
- 操作: valid / invalid fixture を実行する。
- 期待結果: canonical `requirement.md` / `design.md` / `plan.md`、`.assurance.json` は validator により変更されない。必要な証跡だけが指定 output に作られる。
- 観測点: focused pytest、`git status --short`、Issue `report.md`。

## 例外ケース

- GitHub connector / preflight snapshot がない場合は `blocked` とし、手動 authoring path に戻す。
- `.zip` ではない input が directory の場合は tree mode として検査できるが、ZIP central directory AC の証跡としては扱わない。
- source hash mismatch は regeneration / reconciliation 対象として `stale` にする。
- profile mismatch や skeleton section validation は後続 Issue へ `deferred` とし、危険 claim や unsafe path は `deferred` にしない。
