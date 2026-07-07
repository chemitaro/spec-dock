---
種別: research
ID: "20260706t145350z-research"
タイトル: "ChatGPT ZIP Authoring Pack Prompt And Output Dogfood"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices"
  - "20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control"
  - "20260706t140325z-research-epic-requirement-clarification-dogfood"
authority: "synthesized"
adoption_status: "unreviewed"
oracle_provider: "chatgpt-use"
oracle_model: "gpt-5.5-pro"
oracle_thinking: "Pro Extended"
oracle_session_slug: "specdock-epic-00283-zip-authoring"
local_repo: "chemitaro/spec-dock"
local_branch: "codex/chatgpt"
local_head_sha: "209811098dc3067a94a3894cb89f9c6f5f6eae31"
zip_sha256: "1a84b8ad9b04663a2118c37c1d2360b229346dd1eb26c78c40a25d9de11786c4"
derived_from:
  - "redacted-managed-temp://epic-00283-zip-authoring-pack-prompt.md"
  - "redacted-managed-temp://chatgpt-output.md"
  - "redacted-chatgpt-generated-zip://specdock-epic-00283-authoring-pack-codex-chatgpt-2098110.zip"
reflected_to: []
---

# 20260706t145350z-research ChatGPT ZIP Authoring Pack Prompt And Output Dogfood

## 調査目的

`epic-00283` で実装予定の ChatGPT ZIP authoring pack workflow を、まだ script / skill が存在しない状態で manual prompt により dogfood する。

具体的には、ChatGPT Use / GPT-5.5 Pro Extended に対し、現在の GitHub repo / branch を参照させた上で、Epic design / plan draft と、Epic 配下に作成予定の 9 Issue candidate の draft requirement / design / plan を、単一 root の downloadable ZIP として生成できるかを確認する。

同時に、ユーザー補足のとおり、将来の script / skill の名前は人間が使いやすく、意味を正確に表す必要があるため、ZIP 内に naming proposal を含めるよう prompt を更新した。

## sources / 調査方法

### 参照先

- Target repo:
  - `chemitaro/spec-dock`
  - branch: `codex/chatgpt`
  - local / origin HEAD: `209811098dc3067a94a3894cb89f9c6f5f6eae31`
- Prompt:
  - `redacted-managed-temp://epic-00283-zip-authoring-pack-prompt.md`
- ChatGPT text output:
  - `redacted-managed-temp://chatgpt-output.md`
- ChatGPT generated ZIP:
  - `redacted-chatgpt-generated-zip://specdock-epic-00283-authoring-pack-codex-chatgpt-2098110.zip`
- Managed temp ZIP copy:
  - not retained as durable evidence; use `zip_sha256` and repo-local adopted artifacts only.
- Attached context:
  - parent Initiative requirement / design / plan
  - `epic-00283` requirement / design / plan / report
  - key prior artifacts:
    - `20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices.md`
    - `20260706t131838z-research-chatgpt-zip-authoring-pack-issue-grade-control.md`
    - `20260706t140325z-research-epic-requirement-clarification-dogfood.md`
    - `20260706t133043z-chatgpt-zip-authoring-onboarding-brief.md`
  - selected workflow docs / templates:
    - `workflow_spec_authoring.md`
    - `workflow_epic.md`
    - `phase_design.md`
    - `phase_plan_epic.md`
    - `authoring/scope-layering.md`
    - `authoring/decision-routing.md`
    - `reference_naming.md`
    - Epic / Issue templates and `profile-sections.json`

### 検証手順

- `git status --short --branch` で current branch が `codex/chatgpt...origin/codex/chatgpt` かつ clean であることを確認した。
- `git rev-list --left-right --count HEAD...origin/codex/chatgpt` が `0 0` で、local head と remote tracking branch が一致していることを確認した。
- `git rev-parse HEAD` と `git rev-parse origin/codex/chatgpt` がどちらも `209811098dc3067a94a3894cb89f9c6f5f6eae31` を返した。
- `gh repo view --json nameWithOwner,defaultBranchRef,url` で repo が `chemitaro/spec-dock`、default branch が `main` であることを確認した。
- `chatgpt-use` wrapper の dry-run で attachment bundle を確認した。
  - 初回: 約 `262,644` tokens / 46 files で大きすぎたため削減。
  - 最終: 約 `101,506` tokens / 25 files。
- Prompt に以下を含めた:
  - GitHub connector hard-failure condition。
  - repo / branch / expected HEAD。
  - required ZIP tree。
  - 9 Issue candidate seed。
  - authority boundary: `authority: evidence_only`, `adoption_status: unreviewed`, `bundle generation != bundle promotion`。
  - profile boundary: ChatGPT は recommendation only、`authorized_profile` / `.assurance.json` は local authority。
  - ZIP safety denylist。
  - naming design requirements。
- Live run:
  - `oracle_session_slug`: `specdock-epic-00283-zip-authoring`
  - runtime: `19m34s`
  - model evidence: `requested=Pro; resolved=Pro Extended; status=already-selected; verified=yes`
  - input: approximately `101.97k` tokens
  - output text: 69 tokens
  - files attached: 25
- Local lightweight validation:
  - `shasum -a 256`
  - `zipinfo -1`
  - `zipinfo -l`
  - `unzip -t`
  - forbidden path scan with `rg`
  - Issue candidate count scan
  - `zipgrep` scan for selected unsafe machine claims

## facts / 観測できた事実

- ChatGPT generated a downloadable ZIP and Oracle captured it locally.
- ChatGPT text output:

```text
ZIP generated. Local validation required.

File: specdock-epic-00283-authoring-pack-codex-chatgpt-2098110.zip
SHA256: 1a84b8ad9b04663a2118c37c1d2360b229346dd1eb26c78c40a25d9de11786c4
Files: 64
```

- Local `shasum -a 256` matched ChatGPT's SHA256:

```text
1a84b8ad9b04663a2118c37c1d2360b229346dd1eb26c78c40a25d9de11786c4
```

- ZIP central directory contains exactly 64 entries under the single root:

```text
specdock-authoring-pack/
```

- Required high-level files are present:
  - `README.md`
  - `manifest.json`
  - `provenance.json`
  - `stale-if.json`
  - `source-manifest.json`
  - `drafts/epic/design.md`
  - `drafts/epic/plan.md`
  - `adoption/adoption-map.json`
  - `adoption/eal-proposal.md`
  - `adoption/issue-creation-commands.md`
  - `naming/script-and-skill-name-proposal.md`
  - `naming/name-decision-matrix.json`
  - `validation/model-validation-report.md`
  - `validation/model-validation-report.json`
  - `validation/unsafe-claim-scan.json`
  - `reviewer-focus/spec-reviewer.md`
  - `reviewer-focus/implementation-reviewer.md`
- ZIP includes 9 Issue candidate directories. Each contains:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `candidate.json`
  - `profile.json`
- `zipinfo -l` showed regular `-rw-r--r--` files and no executable bit.
- `unzip -t` reported no compressed data errors.
- Forbidden path scan returned no hits for:
  - absolute paths
  - `..`
  - backslash separator
  - hidden denylisted roots
  - nested archive suffixes
  - key-like suffixes
- Issue candidate count scan returned `9`.
- `zipgrep` found no `adoption_status": "adopted"` and no `review_status": "pass"` machine claim.
- `manifest.json` states:
  - `authority: "evidence_only"`
  - `adoption_status: "unreviewed"`
  - `bundle_generation_not_promotion: true`
  - `invariant_phrase: "bundle generation != bundle promotion"`
  - `issue_candidates: 9`
- `model-validation-report.json` states required files present, single root OK, forbidden paths absent, JSON parse OK, Issue count 9, profile recommendation only, and local validation still required.
- `provenance.json` includes a limitation:
  - `search_branches_codex_chatgpt: "empty"`
  - `fetch_file_ref_codex_chatgpt_requirement: "succeeded"`
  - `fetch_commit_expected_sha: "succeeded"`
  - `branch_head_sha_verification: "not_observed_with_available_connector_functions"`
- Local git verification filled the branch-sensitive gap: local `HEAD` and `origin/codex/chatgpt` match `209811098dc3067a94a3894cb89f9c6f5f6eae31`.

## prompt analysis / プロンプト設計の分析

### 有効だった prompt 要素

- GitHub connector hard-failure condition:
  - connector が使えない場合は `repository access failed` として止めるようにしたことで、attachments-only の誤継続を防ぐ意図を明確化できた。
- Expected HEAD SHA:
  - ChatGPT 側の branch head observation は限定的だったが、expected SHA を prompt に含めたことで provenance に検証限界を記録させられた。
- Required ZIP tree:
  - 具体的な file tree を明示したことで、64 files の構造化 ZIP が得られた。
- Authority boundary:
  - `authority: evidence_only` / `adoption_status: unreviewed` / `bundle generation != bundle promotion` を明示したことで、manifest / validation / Markdown に authority boundary が反映された。
- Profile boundary:
  - `authorized_profile: null` と `requires_local_assurance: true` の形で candidate profile を advisory に閉じ込められた。
- Naming design requirements:
  - ユーザー補足を本実行前に prompt へ追加したことで、`naming/` 配下に script / skill naming proposal を含められた。

### 改善が必要な prompt 要素

- Branch head verification:
  - ChatGPT GitHub connector は expected SHA の commit fetch と ref file fetch までは成功したが、branch head SHA の直接 observation はできなかった。
  - future script では local preflight が `HEAD == origin/<branch>` を検証し、その結果を prompt pack の `preflight.json` として添付する必要がある。
- Single huge ZIP:
  - 今回の live run は約 19分34秒かかった。
  - Future implementation には timeout / reattach / follow-up generation / smaller pack split の設計が必要。
- Candidate Issue naming:
  - 既存 requirement seed に `Oracle` が含まれるため、ZIP 内の candidate slug / title にも `oracle` が残った。
  - ただし naming proposal は user-facing default に `oracle` を使わず、`authoring-pack-*` 系を推奨している。

## naming findings / 命名の学び

ChatGPT の naming proposal は、provider detail ではなく maintainer task を名前に出す方針を推奨した。

Recommended names:

| Surface | Recommended name | Purpose |
|---|---|---|
| skill | `spec-dock-authoring-pack` | ChatGPT-assisted SpecDock authoring evidence pack generation |
| script | `authoring-pack-preflight` | repo/ref/source/stale/profile snapshot and prompt pack input |
| script | `authoring-pack-review` | intake and validate ZIP authoring pack before extraction/staging |
| script | `authoring-pack-stage` | dry-run diff and sanitized staged evidence |
| command | `draft-issues-from-pack` | candidate Issue suggestions after local review |

Rejected names include:

- `oracle-authoring-pack`
- `approve-authoring-pack`
- `promote-authoring-pack`
- `auto-issue-author`
- `reviewer-replacement-pack`
- `zip-import`

推奨方針:

- Human-facing surface では `oracle` を原則使わない。
- `oracle` は provider / implementation detail として残す。
- `approve` / `promote` / `auto` / `reviewer-replacement` は authority confusion を起こすため避ける。
- `preflight` / `review` / `stage` / `draft` は行為と権限境界が分かりやすい。

## inference / 推測

### 事実から推測したこと

- ChatGPT Use / GPT-5.5 Pro Extended は、Epic design / plan と 9 Issue draft set を一括した downloadable ZIP として生成できる。
- Prompt で authority boundary、required tree、profile boundary、naming requirements を明示すれば、ZIP の構造と自己申告 metadata はかなり安定する。
- ただし ChatGPT 生成 ZIP は、local validation / preflight / fresh reviewer gate / canonical adoption の代替にはならない。
- Branch-sensitive correctness は ChatGPT connector だけでは不足しうる。local preflight が検証結果を machine-readable に添付する必要がある。
- 将来の user-facing script / skill names は `oracle-*` より `authoring-pack-*` 系に寄せた方がよい。

### 推測の根拠

- ZIP は実体として取得でき、local SHA256 と ChatGPT 申告 SHA256 が一致した。
- ZIP tree は prompt で指定した required tree に一致していた。
- `manifest.json` / `provenance.json` / `model-validation-report.json` が authority boundary と local validation required を表現していた。
- `provenance.json` は branch head observation の限界を記録していた。
- `naming/script-and-skill-name-proposal.md` は provider detail を避ける方針を明示した。

## unverified / 未検証事項

- ZIP 内 Markdown の全 claim-level 内容はまだレビューしていない。
- `adoption-map.json` は大きいため、各 claim の採否判断は未実施。
- ZIP 内 JSON の schema は model self-schema であり、local JSON schema validator はまだ存在しない。
- ZIP の extraction / staging script はまだ存在しないため、safe extraction 後の staged artifact rendering は未検証。
- ZIP 内 draft design / plan を canonical `design.md` / `plan.md` へ採用するかは未判断。
- Candidate Issue を実際に作成するか、また作成前に `Oracle` を含む Issue seed title / slug を rename するかは未判断。
- Fresh `spec-reviewer` は未実施。

## question candidates / 質問候補

### source-grounded に解けず、人間判断が必要な候補

- なし。現時点では、次の作業は ZIP内容の採否レビューと canonical design / plan への統合判断であり、追加インタビューなしに進められる。

### pressure-test question として切り出すべき候補

- Candidate Issue seed の title / slug から `Oracle` を外し、`authoring-pack-*` 系に寄せるか。
  - これは blocking question ではないが、Issue 作成前に検討した方がよい。

### 質問せずに解決できた候補

- Script / skill naming は provider detail より human-facing task name を優先する。
- ZIP は raw repo artifact として保存せず、Oracle session / managed temp path を references として残す。
- ZIP generation は phase promotion ではない。

## terminology conflicts / 用語衝突

- `Oracle`
  - 既存 wrapper / implementation detail としては通じる。
  - human-facing command / skill name に使うと、ChatGPT provider detail や特別な authority を想起しやすい。
  - 今回の naming proposal は、default user surface から `oracle` を外す方向を推奨した。
- `authoring pack`
  - ZIP / structured output としての evidence package を表す。
  - Canonical docs への promotion ではない。
- `review`
  - `authoring-pack-review` は ZIP intake / validation review を意味する。
  - `spec-reviewer` pass とは別物であるため、docs / help で区別が必要。
- `stage`
  - `authoring-pack-stage` は sanitized evidence staging を意味する。
  - Git staging や canonical adoption と混同しないよう、help text で明示が必要。

## edge cases / 具体シナリオ

- ChatGPT connector が branch head SHA を直接観測できない:
  - local preflight で `HEAD == origin/<branch>` を検証し、prompt pack に添付する。
  - provenance の limitation を adoption-map に反映する。
- ZIP生成が 15分以上かかる:
  - wrapper session reattach / status inspection を設計に入れる。
  - future script は timeout 後に即再実行せず、既存 session artifact を探す。
- ZIP は取得できたが local artifact capture 先が不明:
  - Oracle session artifacts directory を first-class capture target として扱う。
  - `Downloads` 依存にしない。
- Required tree は満たすが Markdown の claim が危険:
  - machine self-validation は信用せず、local unsafe-claim scanner と spec-reviewer input を使う。
- Candidate Issue names が provider detail を含む:
  - user-facing names は command / skill / script から先に整え、Issue seed name も必要に応じて rename する。

## implications / 判断への含意

- `epic-00283/design.md` へ反映する候補:
  - ChatGPT ZIP generation は実用可能だが、local preflight / validation / staging / adoption が control plane である。
  - Oracle session artifacts directory を capture source として明記する。
  - Branch-sensitive mode は local preflight required とする。
  - ZIP generation long-running behavior に対して session reattach / artifact discovery を設計する。
- `epic-00283/plan.md` へ反映する候補:
  - Issue slicing は 9 candidates を維持できる。
  - ただし script / skill naming は `authoring-pack-*` / `spec-dock-authoring-pack` を優先する。
  - Candidate Issue title / slug の `Oracle` は作成前に rename 検討する。
- Future script / skill:
  - `spec-dock-authoring-pack` skill
  - `authoring-pack-preflight`
  - `authoring-pack-review`
  - `authoring-pack-stage`
  - `draft-issues-from-pack`
- Validation requirement:
  - local validator は ZIP central directory、file mode、path denylist、file count、required tree、JSON parse、unsafe authority claim、source provenance、profile boundary を検査する。

## リスク/制約

- ChatGPT output is not canonical authority。
- ZIP generation success does not imply ZIP adoption readiness。
- ChatGPT GitHub connector observation may be partial; local git preflight is mandatory for branch-sensitive runs。
- ZIP 内の `model-validation-report.json` は model self-report であり、local validation result ではない。
- Long-running browser generation can consume 20 minutes; scripts need session recovery and duplicate-run prevention。
- Raw ZIP / extracted tree should not be committed into repo in v1 unless a future artifact-pack durable storage contract is accepted。

## 反映先

reflected_to:

- 未反映。
- 次に `design.md` / `plan.md` へ採用判断する場合は、claim 単位で `report.md` Evidence Adoption Ledger に記録する。

## 参考（References）

- Prompt:
  - `redacted-managed-temp://epic-00283-zip-authoring-pack-prompt.md`
- ChatGPT output:
  - `redacted-managed-temp://chatgpt-output.md`
- ZIP:
  - `redacted-chatgpt-generated-zip://specdock-epic-00283-authoring-pack-codex-chatgpt-2098110.zip`
- ZIP managed temp copy:
  - not retained as durable evidence.
