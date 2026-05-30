---
種別: research
ID: "20260530t081132z-research"
タイトル: "Local Only Node Creation Option Surface Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["iss-00141"]
関連: []
authority: "synthesized"
derived_from:
  - spec-dock/active/issue/discussions/20260529t153534z-disc-handoff-scratch.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/discussions/20260327t093000z-adr-github-mandatory-node-linkage.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
  - tests/cli_runtime/test_new.py
  - tests/cli_runtime/test_wrappers.py
  - src/spec_dock/assets/spec_dock/docs/reference_github.md
  - src/spec_dock/assets/spec_dock/docs/github.md
  - src/spec_dock/assets/spec_dock/docs/workflow-tree.md
  - src/spec_dock/assets/spec_dock/scripts/README.md
  - README.md
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260530t081132z-research Local Only Node Creation Option Surface Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00141` の requirement authoring 前に、local-only node creation option surface がどこに残っているか、どこまでを requirement scope に含めるべきか、ユーザー確認が必要な判断が何かを整理する。

## sources / 調査方法 (必須)
- 参照先:
  - active issue docs:
    - `spec-dock/active/issue/requirement.md`
    - `spec-dock/active/issue/design.md`
    - `spec-dock/active/issue/plan.md`
    - `spec-dock/active/issue/report.md`
  - issue discussion:
    - `spec-dock/active/issue/discussions/20260529t153534z-disc-handoff-scratch.md`
  - parent docs / ADR:
    - `spec-dock/active/initiative/requirement.md`
    - `spec-dock/active/epic/requirement.md`
    - `spec-dock/active/epic/design.md`
    - `spec-dock/active/epic/plan.md`
    - `spec-dock/active/epic/discussions/20260327t093000z-adr-github-mandatory-node-linkage.md`
  - runtime / tests / docs:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
    - `tests/cli_runtime/test_new.py`
    - `tests/cli_runtime/test_wrappers.py`
    - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
    - `src/spec_dock/assets/spec_dock/docs/github.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
    - `src/spec_dock/assets/spec_dock/scripts/README.md`
    - `README.md`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show`
  - `gh issue view 141 --json number,title,state,body,comments,url`
  - `rg -n -- "--no-github|local-only|Local Only|no github" ...`
  - targeted `nl -ba` / `sed` inspection for runtime parser, tests, and docs.
- 実験条件:
  - コード変更前の read-only 調査。

## facts / 観測できた事実 (必須)
- `iss-00141` の canonical `requirement.md` / `design.md` / `plan.md` は scaffold-heavy で、実質的な AC / scope / non-scope はまだ書かれていない。
- `gh issue view 141` の body は spec-dock generated placeholder のみで、詳細要件は含まれていない。
- issue-local scratch には、`new issue --help` が `--no-github` を rejected contract option として露出しており、follow-up は local-only option surface 自体を除去する可能性が高い、と記録されている。
- parent epic は `new initiative` / `new epic` / `new issue` を GitHub issue mandatory とし、local-only path を持たないことを requirement にしている。
- accepted ADR `20260327t093000z-adr-github-mandatory-node-linkage.md` は、GitHub issue に紐づかない node は作成せず、`local-only` / local fallback を廃止する、と決定している。
- runtime parser は `new initiative` / `new epic` / `new issue` の mutually exclusive GitHub group に `--no-github` を追加している。
- runtime handler は `typed.no_github` の場合に `"'--no-github' is not supported for <kind>; GitHub linkage is mandatory."` を返す。
- `tests/cli_runtime/test_new.py` は `--no-github` が contract error として reject されること、および GitHub flag group の相互排他に `--no-github` が含まれることを期待している。
- `tests/cli_runtime/test_wrappers.py` は `reference_github.md` に `--no-github` compatibility option の説明があること、issue skill text に `--no-github` があることを期待している。
- provider docs は node creation context で `--no-github` を compatibility option / reject path として説明している。
- `sync` / `deps check` / `active set` の `--no-github` は cache/local state opt-out として別用途に存在し、今回の node creation surface と同名だが意味が異なる。

## inference / 推測 (必須)
- 事実から推測したこと:
  - requirement の中心は、GitHub mandatory contract の再実装ではなく、既存 mandatory contract に反する UX / docs / tests の compatibility surface を削ること。
  - `new initiative|epic|issue --no-github` は「認識されるが contract error」から「そもそも node creation の option ではない」へ変えるのが自然な close condition になる。
  - parser-level unknown option 化を要求する場合、GitHub CLI を呼ばないことは argparse の前段失敗で満たせるため、既存 fake `gh` test は別の期待値に置き換える必要がある。
  - `sync` / `deps` / `active` の cache/local `--no-github` は残すべきであり、単純な全文削除を requirement にすると scope が広がりすぎる。
- 推測の根拠:
  - parent epic / ADR が GitHub mandatory を既に決定済みであり、issue title が `Option Surface` に限定されているため。
  - scratch が「remove the local-only option surface itself, not merely keep it as a rejected path」と明記しているため。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - ユーザーが求める「surface removal」が parser option の完全削除までを含むのか、help/docs からの削除に留めて explicit use は従来の contract error として残すのか。
  - 互換性のために `--no-github` explicit invocation に専用エラーを残す価値を完全に棄却してよいか。
  - import の `--allow-foreign-url` のような他の compatibility flag まで同時に触るか。
- 確認できない理由:
  - これは UX / backward compatibility / error-message policy の判断であり、コードから一意には決まらない。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `--no-github`
  - `local-only`
  - `compatibility option`
  - `cache/local state`
- 既存 docs / code / tests / discussions での使われ方:
  - node creation では `--no-github` が local-only creation rejected path を意味している。
  - `sync` / `deps check` / `active set` では `--no-github` が GitHub live fetch を行わない cache/local state mode を意味している。
  - docs は両者を同じ flag name で説明しているため、requirement で「node creation surface」に限定しないと誤って state command の flag を消す risk がある。
- 判断が必要な理由:
  - requirement の MUST / MUST NOT で、削除対象の command surface と維持対象の command surface を明確に分ける必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - `new issue --help` に `--no-github` が表示され続ける。
  - `new issue --no-github --epic <id> --title "..."` が dedicated contract error を返す。
  - `new issue --create-github-issue --no-github ...` が mutually exclusive group error を返す。
  - docs / skills が `--no-github` を node creation compatibility option として残す。
  - `sync --no-github` や `deps check --no-github` まで誤って削除される。
- その edge case が requirement / design / plan に与える影響:
  - help / parser / error behavior / docs / tests のいずれを AC に入れるかを requirement で固定する必要がある。
  - 同名 flag の別用途を protected non-scope として明記する必要がある。

## implications / 判断への含意 (必須)
- Requirement では、対象を `new initiative` / `new epic` / `new issue` の node creation surface に限定する。
- Requirement では、`--create-github-issue` default / explicit alias と `--github-issue <n>` link-existing path は維持する、と明記する。
- Requirement では、`sync` / `deps check` / `active set` の cache/local `--no-github` は対象外または維持対象とする。
- Requirement では、node creation `--no-github` の explicit invocation を parser-level unknown option にするか、専用エラーを残すかをユーザー確認したうえで AC に固定する。
- Design では provider asset と checked-in dogfooding mirror の parity、tests の期待値更新、docs / skill text の drift removal を扱う。

## リスク/制約 (任意)
- 同名 `--no-github` が state command に残るため、`rg -- "--no-github"` は false positive が多い。requirement / plan では対象 command を限定して検証する必要がある。
- `app.py` の legacy monolithic runtime comments に古い local-only default 記述が残っている。current parser source of truth との関係を design 時に確認する必要がある。

## 反映先 (任意)
- reflected_to:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- `spec-dock/docs/workflow_clarification.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_requirement.md`
