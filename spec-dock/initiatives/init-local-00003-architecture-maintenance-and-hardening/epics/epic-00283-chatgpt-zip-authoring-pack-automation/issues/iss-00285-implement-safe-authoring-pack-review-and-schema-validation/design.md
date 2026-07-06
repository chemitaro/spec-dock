---
種別: 設計書（Issue）
ID: "iss-00285"
タイトル: "安全な仕様作成パック検査とスキーマ検証を実装する"
関連GitHub: ["#285"]
状態: "review-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00285 安全な仕様作成パック検査とスキーマ検証を実装する — 設計

## 結論

`iss-00285` では、`scripts/authoring-pack/` に dogfood-only validator を追加します。実装は次の 2 層に分けます。

- library: `authoring_pack_review.py`
- CLI: `review_chatgpt_authoring_pack.py`

主入力は `.zip` です。ZIP input では central directory を先に検査し、安全境界違反があれば展開しません。補助入力として extracted directory tree も受け付けますが、tree input は ZIP central directory safety evidence にはなりません。

## 責務境界

この Issue が持つ責務:

- ZIP central directory inspection
- safe path normalization
- expected root / mandatory file validation
- unsafe file type detection
- bounded safe extraction prototype
- metadata schema validation
- source hash / stale snapshot comparison
- unsafe authority claim scanning
- sanitized JSON / Markdown report generation

この Issue が持たない責務:

- canonical docs adoption
- staged diff rendering
- profile-controlled skeleton fill
- reviewer gate result
- `.assurance.json` mutation
- runtime command publication
- PR creation

## 入力 contract

### ZIP mode

```bash
python scripts/authoring-pack/review_chatgpt_authoring_pack.py \
  --input /tmp/specdock-authoring-pack/result.zip \
  --preflight /tmp/specdock-authoring-pack/iss-00284-prompt-pack/preflight.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00285-review
```

ZIP mode は主要経路です。`zipfile.ZipFile.infolist()` で central directory を読み、entry name、Unix mode、size、compression、directory flag を展開前に検査します。

### Tree mode

```bash
python scripts/authoring-pack/review_chatgpt_authoring_pack.py \
  --input /tmp/specdock-authoring-pack/extracted/specdock-authoring-pack \
  --input-kind tree \
  --preflight /tmp/specdock-authoring-pack/iss-00284-prompt-pack/preflight.json \
  --output-dir /tmp/specdock-authoring-pack/iss-00285-review
```

Tree mode は、すでに隔離済みの directory tree に対する schema / claim / source hash inspection です。symlink、hidden path、binary、nested archive は拒否します。ZIP central directory safety は `deferred` note として report に残し、AC-002 の代替証跡にしません。

## expected root structure

valid pack は単一 root `specdock-authoring-pack/` を持ちます。

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  source-manifest.json
  stale-if.json
  adoption/
    adoption-map.json
  drafts/
    *.md
  candidates/
    issues/
      <issue-id>/
        candidate.json
        draft-requirement.md
        draft-design.md
        draft-plan.md
        profile.json
  reviewer-focus/
    *.md
  README.md
```

mandatory:

- `manifest.json`
- `provenance.json`
- `source-manifest.json`
- `stale-if.json`
- `adoption/adoption-map.json`

optional:

- `README.md`
- `drafts/**/*.md`
- `candidates/issues/*/candidate.json`
- `candidates/issues/*/draft-requirement.md`
- `candidates/issues/*/draft-design.md`
- `candidates/issues/*/draft-plan.md`
- `candidates/issues/*/profile.json`
- `reviewer-focus/**/*.md`

unknown files は `.md` / `.json` / `.txt`、safe path、UTF-8 text、size limit 内のときだけ warning として許可します。hidden、binary、nested archive、executable、link-like mode、secret-looking、host-path-like、root 外は拒否します。

## safety validation

### path rules

次を拒否します。

- NUL / control character
- backslash path
- Windows drive path
- absolute path
- `..`
- empty segment
- hidden segment starting with `.`
- expected root mismatch
- duplicate normalized path
- secret-looking segment: `.env`、`secret`、`token`、`credential`、`private-key`、`private_key`
- host path marker: `/Users/`、`/home/`、`/Volumes/`、`/private/`、`.oracle`

### ZIP entry rules

展開前に次を拒否します。

- symlink / hardlink / device / FIFO-like Unix mode
- executable bit
- nested archive extension: `.zip`、`.tar`、`.tgz`、`.tar.gz`、`.gz`、`.bz2`、`.xz`、`.7z`、`.rar`
- allowed text file に対する binary-looking content
- per-file size limit 超過
- total uncompressed size limit 超過
- entry count limit 超過
- compression ratio limit 超過
- normalized path 重複

### content rules

JSON files:

- JSON object として parse できる。
- required fields が expected type を持つ。
- authority boundary が固定されている。

Markdown / text files:

- UTF-8 decodable。
- private key header を含まない。
- raw transcript marker を含まない。
- unsafe authority claim を含まない。

## schema model

`manifest.json` required fields:

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true,
  "pack_id": "non-empty string",
  "expected_zip_root": "specdock-authoring-pack/",
  "schema_version": "1"
}
```

`provenance.json` required fields:

```json
{
  "authority": "evidence_only",
  "repository": {
    "full_name": "chemitaro/spec-dock",
    "requested_ref": "string"
  },
  "source": "chatgpt_zip_authoring_pack"
}
```

`source-manifest.json` required fields:

```json
{
  "sources": [
    {
      "path": "repo-relative path",
      "sha256": "64 hex chars",
      "role": "string"
    }
  ]
}
```

`stale-if.json` required fields:

```json
{
  "stale_if": [
    {
      "kind": "source_hash_changed",
      "source_paths": ["repo-relative path"]
    }
  ]
}
```

`adoption/adoption-map.json` required fields:

```json
{
  "items": [
    {
      "source_path": "pack-relative path",
      "target": "repo-relative target or evidence-only",
      "adoption_status": "unreviewed",
      "required_local_validation": ["string"]
    }
  ]
}
```

## preflight / stale validation

`--preflight` は `iss-00284` helper が作成した `preflight.json` を信頼ベースラインとして扱う。ただし validator は次の条件を満たす preflight だけを baseline にできる。

- `preflight.status` は `pass` でなければならない。
- `authority: evidence_only`、`adoption_status: unreviewed`、`bundle_generation_not_promotion: true` を持つ。
- `sources` は 1 件以上で、各 source は safe repo-relative `path`、64 hex `sha256`、non-empty `role` を持つ。
- `stale_if` は配列で、`source_hash_changed` 条件の `source_paths` が safe repo-relative path である。
- `repository.full_name`、`repository.requested_ref`、`repository.observed_ref` または `repository.observed_head` が report 可能な sanitized 値である。
- `safe_output_constraints.forbidden_claims` が配列で、dangerous authority claim の検出に使える。

preflight が unreadable または local observation 不足の場合は `blocked`。preflight JSON shape が壊れている場合は `fail`。`preflight.status` が `fail` / `blocked` / `stale` / `rejected` の場合、validator はその status を安全側に伝播し、ZIP / tree 自体を `pass` にしない。

source / stale checking は次の順で行う。

1. `--preflight` の `sources[*].path` / `sources[*].sha256` を expected snapshot とする。
2. ZIP 内 `source-manifest.json` の `sources[*]` と path / sha256 を照合する。
3. expected source が ZIP 内 source-manifest にない場合は `stale`。
4. ZIP source-manifest と preflight source の sha256 mismatch は `stale`。
5. `stale-if.json` の `source_hash_changed` が参照する source path を current repo root で読み、current sha256 が preflight と異なる場合は `stale`。
6. current repo root を観測できない、または required source を読めない場合は `blocked`。
7. unsafe source path は `rejected`。

local repo file の current hash を読む場合は repo-relative safe path に限定し、host absolute path を report に出さない。

## unsafe authority claim detection

default denylist:

- `spec-reviewer passed`
- `reviewer pass`
- `adoption_status: adopted`
- `adopted as canonical`
- `accepted as canonical`
- `marked as adopted`
- `approved by spec-reviewer`
- `.assurance.json updated`
- `.assurance.json modified`
- `canonical overwrite`
- `authority: canonical`
- `pull request created`
- `implementation complete`
- `qa-reviewer passed`
- `code-reviewer passed`

検出は case-insensitive かつ separator-insensitive にする。`spec-reviewer-passed`、`spec reviewer passed`、`spec_reviewer_passed` は同一扱いです。JSON key / value と Markdown text の両方を対象にします。裸の `accepted` や `adopted` は、decision ledger や EAL の通常語として現れるため単独では拒否しない。authority / canonical / reviewer / assurance / PR / implementation complete と結び付く claim だけを拒否する。

## validation report

`validation-report.json` は次の shape を持ちます。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true,
  "status": "pass|fail|blocked|stale|rejected|deferred",
  "input_kind": "zip|tree",
  "trace": {
    "issue_id": "iss-00285",
    "parent_epic": "epic-00283",
    "requirements": ["E-RQ-004", "E-RQ-005"],
    "acceptance": ["E-AC-002", "E-AC-003", "E-AC-004"]
  },
  "checks": [],
  "errors": [],
  "warnings": [],
  "deferred": [],
  "sources": []
}
```

`validation-summary.md` は同じ status / errors / warnings / deferred / boundary を人間向けに短く出します。report / summary / CLI stdout / stderr は redaction 後の値だけを出します。

CLI exit code は次に固定する。

| status | exit code | meaning |
|---|---:|---|
| `pass` | 0 | validation passed; adoption remains unreviewed |
| `fail` | 1 | invalid input shape, schema, root, or required metadata |
| `blocked` | 2 | required local observation or filesystem operation unavailable |
| `stale` | 3 | preflight / source / stale_if snapshot mismatch |
| `rejected` | 4 | safety boundary violation |
| `deferred` | 5 | recognized later-stage responsibility; never treated as pass |

`unreviewed` は execution status ではなく artifact adoption state であるため、CLI exit code を持たない。

## module design

`authoring_pack_review.py`:

- `review_input(input_path, preflight_path, output_dir, input_kind, extract_dir=None) -> dict`
- `review_zip(...) -> dict`
- `review_tree(...) -> dict`
- `inspect_zip_entries(...) -> list[EntryObservation]`
- `normalize_pack_path(...) -> str`
- `validate_root_structure(...) -> list[CheckResult]`
- `validate_required_metadata(...) -> list[CheckResult]`
- `validate_source_manifest(...) -> list[CheckResult]`
- `scan_unsafe_claims(...) -> list[CheckResult]`
- `sanitize_diagnostic_value(...) -> Any`
- `aggregate_status(...) -> str`

`review_chatgpt_authoring_pack.py`:

- argparse と exit code mapping を担当する。
- output dir ownership marker を使い、unowned output dir を削除しない。
- `validation-report.json` と `validation-summary.md` を書く。

## 失敗時の設計

- unsafe ZIP entry は safe extraction 前に `rejected`。
- multiple root は `fail`。
- mandatory metadata 欠落は `fail`。
- preflight missing / unreadable は `blocked`。
- source hash mismatch は `stale`。
- unsafe authority claim は `rejected`。
- output dir に user-owned files がある場合は `blocked`。
- safe extraction write failure は `blocked`。
- tree input の ZIP central directory safety は `deferred` note。

## 観測性

- 実行ごとに JSON report と Markdown summary を出す。
- diagnostics に host-local absolute paths、secret、private key、token、raw transcript を含めない。
- validation execution status は `pass`、`fail`、`blocked`、`stale`、`rejected`、`deferred` を分ける。`unreviewed` は adoption state として authority boundary にだけ残す。

## テスト戦略

- valid ZIP / tree で pass report を確認する。
- unsafe ZIP path / hidden path / symlink / nested archive / binary を rejected にする。
- mandatory metadata 欠落を fail にする。
- source hash mismatch を stale にする。
- unsafe authority claim を rejected にする。
- redaction と canonical docs / `.assurance.json` no-mutation を確認する。

## レビュアー注目点

- ZIP central directory 検査が展開前に実行されるか。
- tree input を ZIP safety evidence と誤認しないか。
- status taxonomy と親 Epic trace が崩れていないか。
- dogfood-only helper が runtime command として見えないか。
- ChatGPT output が reviewer pass / canonical adoption を claim できないか。
