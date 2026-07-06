# ChatGPT Use planning summary for iss-00286

## 実行情報

- 実行: ChatGPT Use / GPT-5.5 Pro Extended
- session slug: `specdock-iss-00286-planning`
- 対象 branch: `iss-00286-implement-authoring-pack-diff-and-staged-artifact-rendering`
- 目的: Issue `iss-00286` の要件定義書、設計書、実装計画書を実装可能な粒度へ具体化する。

## 採用した主要提案

- 新しい dogfood-only staging helper を `scripts/authoring-pack/` に追加する。
- 入力は `review_chatgpt_authoring_pack.py` の `validation-report.json` と、その review と同じ pack から隔離展開された `specdock-authoring-pack/` tree に限定する。
- `validation-report.json.status == "pass"` の場合だけ staging を許可する。
- 正本 `requirement.md` / `design.md` / `plan.md` は read-only で扱い、直接 write しない。
- dry-run diff、staged artifacts、EAL candidate rows は output directory 配下にのみ生成する。
- EAL candidate rows の `adoption_status` は常に `unreviewed` とし、`adopted` / `rejected` / `stale` / `blocked` を採用済み状態として出力しない。
- v1 の target は Issue-local `requirement.md` / `design.md` / `plan.md` に限定する。
- unsafe path、direct-write claim、canonical authority claim、reviewer pass claim、`.assurance.json` mutation claim、PR / implementation complete claim は staging 前に拒否する。
- staged artifact の output path は untrusted source path / target path から作らず、`item-0001.md` のような固定名にする。
- diagnostics / CLI summary / Markdown summary に host absolute path、secret、raw transcript、unsafe raw value を出さない。
- helper は dogfood-only であり、配布 runtime command として扱わない。

## 正本 docs への反映

- `requirement.md`:
  - AC-005 を pass review result 限定の staging / no canonical overwrite 条件へ締め直した。
  - AC-006 を `unreviewed` EAL candidate row への変換へ締め直した。
  - AC-007 として診断漏えい防止を追加した。
- `design.md`:
  - `authoring-pack-stage` component の入力、処理、出力、禁止事項を追加した。
- `plan.md`:
  - S03 / tc-003 の対象を AC-005〜AC-007 に拡張した。
  - non-pass review no-stage、diagnostic redaction、output ownership の negative test を追加した。

## 保留した提案

- 任意 repo file への staging diff は採用しない。v1 は Issue-local `requirement.md` / `design.md` / `plan.md` に限定する。
- `target` を `target_path` alias として扱う互換は実装時に必要最小限で判断する。
- stage output を repo 外に固定するか Issue-local `artifacts/` へ配置可能にするかは、実装で安全な output ownership に従う。
