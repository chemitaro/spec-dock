---
種別: research
ID: "20260706t131838z-research"
タイトル: "ChatGPT ZIP Authoring Pack And Issue Grade Control"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t111806z-research-chatgpt-reviewer-gate-script-analysis"
  - "20260706t114128z-research-chatgpt-spec-authoring-automation-best-practices"
authority: "synthesized"
adoption_status: "unreviewed"
oracle_provider: "chatgpt-use"
oracle_model: "gpt-5.5-pro"
oracle_thinking: "Pro Extended"
oracle_session_slug: "specdock-zip-authoring-pack"
oracle_followup_session_slug: "required-repository-connector-context-github"
local_head_sha: "918e624b8a97a4c67bd5ac1ac4ff552999b64bbb"
local_branch_state: "detached-head"
derived_from:
  - "/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/zip-authoring-pack-brief.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/zip-authoring-pack-output.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/issue-grade-followup-brief.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/issue-grade-followup-output.md"
reflected_to: []
---

# 20260706t131838z-research ChatGPT ZIP Authoring Pack And Issue Grade Control

## 調査目的

ChatGPT Use / GPT-5.5 Pro Extended が downloadable ZIP file を返せる実験結果を前提に、SpecDock の仕様 authoring workflow へどう組み込むべきかを整理する。

特に、次を明らかにする。

- ZIP 出力を、Epic design / plan と複数 Issue draft をまとめて返す first-class delivery format として扱えるか。
- ZIP を直接配置してよい範囲と、quarantine / validation / staged adoption が必要な範囲を切り分ける。
- Issue の `lite / standard / strict / critical` grade がある前提で、ChatGPT に grade/profile 選択を任せるべきか、ローカル `assurance classify` / `.assurance.json` を authority に残すべきかを決める。
- Issue authoring の二つの流れ、すなわち Epic decomposition からの Issue draft 生成と、human discussion 済み requirement からの design / plan 生成を、同じ制御面で扱えるかを検討する。

## sources / 調査方法

### 参照先

- ChatGPT Use / GPT-5.5 Pro Extended 初回分析:
  - `/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/zip-authoring-pack-output.md`
- ChatGPT Use / GPT-5.5 Pro Extended follow-up 分析:
  - `/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/issue-grade-followup-output.md`
- SpecDock workflow authority:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/requirement.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`

### 検証手順

- `chatgpt-use` skill の `oracle-chatgpt` wrapper で GPT-5.5 Pro Extended を起動した。
- 初回分析では ZIP authoring pack lifecycle、pack schema、prompt template、intake scripts、adoption policy、dogfood plan を依頼した。
- follow-up 分析では Issue grade/profile 制御、`--profile` / `--profile-source` / `--profile-override-policy` / `--bundle-policy` の CLI/API semantics、Issue authoring の二つの流れ、ChatGPT の template selection authority の有無を追加で依頼した。
- ローカル repo の workflow docs / templates を `rg` / `nl` で確認し、ChatGPT の提案が現行 SpecDock contract と矛盾しないかを照合した。

### 実験条件

- 実行日: 2026-07-06
- repo: `chemitaro/spec-dock`
- local HEAD: `918e624b8a97a4c67bd5ac1ac4ff552999b64bbb`
- local branch: detached HEAD
- active SpecDock scope: unset。作成時は `epic-00158` の scope-local research artifact として記録したが、後続の配置整理により `epic-00283` へ移動した。
- ChatGPT 側の GitHub connector は current branch を `unavailable` と扱い、default branch `main` を検査対象にした。よって ChatGPT output は advisory evidence であり、local checkout の authority ではない。

## facts / 観測できた事実

### ユーザー実験で観測された ZIP 能力

- ChatGPT Use に対して、出力フォーマットとして「実際に配置するファイルを想定したディレクトリ構成を保った ZIP file」を指示したところ、downloadable ZIP file を取得できた。
- 取得した ZIP file は展開でき、複数ファイル・長文ファイルを通常テキスト応答より扱いやすい形で返せる見込みがある。
- この性質を使うと、Epic design / plan と複数 Issue draft requirement / design / plan を一括生成し、Codex 側は ZIP を検証・展開・配置するだけに近づけられる可能性がある。

### 現行 SpecDock の authority boundary

- `workflow_spec_authoring.md` は、仕様書作成を `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` と定義している。
- 各 phase promotion には fresh `spec-reviewer` の `review_status: pass` が必要であり、missing / stale / failed / unavailable / denied / waived / provisional は promotion authority ではない。
- Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator の single-writer authority である。
- Sub-agent / external / delegated output は、対象 scope の `artifacts/` direct child に置く evidence であり、canonical docs へ採用するには main orchestrator の integration と `report.md` Evidence Adoption Ledger が必要である。
- Artifact path が存在するだけでは authority にならない。採用判断と canonical artifact / report ledger への反映が必要である。

### Issue grade/profile の現行契約

- Issue の `authorized_profile` は runtime template、guidance、authoring obligation の authority である。
- manual escalation は reviewer / specialist / evidence gate を強める補助判断であり、`authorized_profile` を上書きする authority ではない。
- Lite は automatic default ではない。小さく低リスクで、既存 contract / scaffold / runtime / user-facing behavior への影響が限定されることを明示できる場合だけ Lite として扱える。
- grade が unknown / ambiguous、または影響範囲や reviewer obligation を判断できない場合は Standard 以上に倒す。
- Strict / Critical では specialist evidence または明示的な unavailable / manual fallback evidence が必要であり、Critical fallback は明示承認と強い evidence を要する。
- `templates/issue/design.md` と `templates/issue/plan.md` は compose 前 placeholder であり、手動 authoring の開始点ではない。
- 実体の Issue design / plan は `.assurance.json` の `authorized_profile` に従い、`templates/issue-profiles/<profile>/design.md` / `plan.md` から `assurance compose` が合成する。
- Issue-local `draft-design` / `draft-plan` も、verified `.assurance.json` の `authorized_profile` に対応する profile template を source とする。missing / invalid / stale contract では no-write fail-closed する。

### ChatGPT 初回分析の要点

ChatGPT は、既存の Oracle Spec Authoring Batch Engine を Oracle ZIP Authoring Pack Engine に拡張することを提案した。ただし、ZIP は authority ではなく untrusted evidence として扱うべきだとした。

推奨 lifecycle は次である。

```text
ChatGPT ZIP
  -> download/capture
  -> quarantine
  -> safe ZIP central-directory inspection
  -> schema + checksum + path + content validation
  -> dry-run diff
  -> staged evidence artifact / draft artifact materialization
  -> main orchestrator adoption
  -> fresh spec-reviewer gate
  -> canonical docs update
```

ZIP pack は単一 root `specdock-authoring-pack/` を持つ。absolute path、`..`、backslash separator、hidden path segments、symlink、hardlink、device file、executable bit、nested archive、binary、`.env*`、token、cookie、secret、`.git`、`.ssh`、`.codex`、`.agents`、`.github` は拒否する。

ZIP の主要構成は次である。

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  schema/
  sources/
  stale-if.json
  drafts/
  candidates/
  adoption/
    adoption-map.json
    eal-proposal.json
  reviewer-focus/
  validation/
```

用途は三つに分かれる。

- Initiative -> Epic decomposition pack
- Epic -> Issue decomposition pack
- Issue requirement/design/plan bundle pack

ただし bundle generation は bundle promotion ではない。requirement / design / plan の canonical adoption は段階的に行い、各段階で fresh `spec-reviewer` が必要である。

### ChatGPT follow-up 分析の要点

ChatGPT は、Issue grade/profile 制御について次の結論を出した。

```text
ZIP は多ファイル authoring delivery format として強化するが、
Issue profile は local assurance-owned control plane とし、
ChatGPT は selected-template content filler と recommendation evidence に限定する。
```

`--profile auto` は許可してよいが、意味は「ChatGPT に grade/profile を選ばせる」ではなく、local `assurance classify` / existing `.assurance.json` を deterministic authority として profile を解決することに限定する。

推奨 flow は次である。

```text
Issue requirement / draft / Epic handoff
  -> local profile resolution
     1. existing .assurance.json / authorized_profile があればそれを読む
     2. なければ assurance classify --stage requirement
     3. authorized_profile に従い assurance compose --artifact design|plan|all
  -> ChatGPT ZIP は selected profile の skeleton / section contract を埋める
  -> ZIP は evidence-only
  -> main orchestrator が採否を決める
  -> canonical requirement/design/plan は staged adoption
  -> fresh spec-reviewer
```

ChatGPT は `profile recommendation` を出してよいが、`profile decision`、template selection authority、`.assurance.json` update authority、canonical compose authority は持たせない。

## inference / 推測

### 推奨結論

SpecDock における ChatGPT ZIP authoring は有効である。ただし、強化すべき領域は「ChatGPT に判断 authority を渡すこと」ではなく、「ChatGPT の大きな出力を machine-sortable evidence pack として受け取り、ローカルの deterministic gate で安全に扱うこと」である。

したがって、最適方針は次である。

- ZIP は first-class delivery format として採用候補にする。
- ZIP は first-class authority format にしない。
- canonical docs への直接展開は禁止する。
- quarantine / static ZIP inspection / schema validation / source hash validation / dry-run diff / staged artifact materialization を必須にする。
- Issue grade/profile は local assurance control plane に残す。
- ChatGPT は profile recommendation、risk trigger、Lite disqualifier、Strict/Critical trigger、selected skeleton section fill、adoption-map claim を返す。
- `authorized_profile`、`.assurance.json`、`assurance compose`、fresh `spec-reviewer` gate はローカル / SpecDock runtime の authority として保持する。

### なぜ ChatGPT に grade 決定を任せないか

Issue grade は単なる文体やテンプレート選択ではなく、reviewer obligation、specialist evidence、fallback evidence、execution readiness、commit candidate gate に影響する。

ChatGPT に grade 決定を任せると、次のリスクがある。

- Lite が「小さいから軽くする」方向へ誤って選ばれる。
- template selection と reviewer obligation が分離され、`authorized_profile` と実際の design / plan がずれる。
- Strict / Critical の specialist / fallback evidence gate を ZIP の self-review で代替したように見える。
- all-profile variant を ZIP に入れることで profile shopping を誘発する。
- stale template hash や stale `.assurance.json` を検知できないまま、もっとも自然に見える Markdown を採用してしまう。

このため、ChatGPT は recommendation evidence に閉じ、authority はローカル resolver に残すのがよい。

### ローカル側で単純化できる箇所

ローカル側の複雑さを減らす対象は、profile 判断そのものではなく、次の機械処理である。

- source manifest / source hash 生成
- profile resolution snapshot 生成
- `.assurance.json` hash capture
- selected profile template hash capture
- composed skeleton generation
- section inventory generation
- ZIP schema validation
- path traversal / symlink / binary / oversize rejection
- adoption-map normalization
- candidate comparison table generation
- dry-run diff generation
- staged artifact path creation

これにより、main orchestrator は巨大な自然言語出力を読むのではなく、構造化された adoption map と dry-run diff を見るだけで判断できる。

## recommended design / 推奨設計

### Control plane と data plane を分ける

```text
control plane:
  - authorized_profile
  - assurance classify
  - assurance compose
  - template hash validation
  - bundle/staged policy resolution
  - canonical adoption decision
  - fresh reviewer gate

data plane:
  - ChatGPT ZIP draft files
  - profile recommendation
  - adoption-map claims
  - reviewer-focus notes
  - candidate issue drafts
  - validation self-report
```

ChatGPT ZIP は data plane に限定する。control plane の authority を持たせない。

### CLI/API semantics

初期 dogfood command は shipped runtime ではなく `manual-tests/oracle-zip-authoring/` 配下の実験 script として始める。

```bash
manual-tests/oracle-zip-authoring/oracle-issue-authoring-zip \
  --scope-id iss-00234 \
  --parent-epic epic-00158 \
  --profile auto \
  --profile-source assurance-classify \
  --profile-override-policy forbid \
  --bundle-policy auto \
  --mode evidence-only
```

#### `--profile`

```text
auto
  - default
  - existing .assurance.json があれば authorized_profile を読む
  - なければ assurance classify --stage requirement を実行する
  - unknown / ambiguous は minimum standard

lite|standard|strict|critical
  - caller requested profile
  - それ自体は authority ではない
  - profile-source と override-policy で検査する
```

`--profile auto = ChatGPT が profile を選ぶ` ではない。`--profile auto = local assurance が profile を解決する` と定義する。

#### `--profile-source`

```text
existing-authorized-profile
  - 既存 .assurance.json の authorized_profile を使う
  - 既存 Issue の design / plan refinement では最優先

assurance-classify
  - canonical / adopted requirement から local classify を実行する
  - standalone Issue の requirement -> design/plan では標準経路

human
  - human-specified desired profile
  - downgrade には使えない
  - stricter obligation への manual escalation には使える

chatgpt-recommendation
  - advisory only
  - template selection / .assurance.json update / canonical placement には使えない
```

#### `--profile-override-policy`

```text
forbid
  - default
  - requested_profile と authorized_profile の mismatch は block

escalate-obligations-only
  - requested profile が authorized_profile より厳しい場合だけ許可
  - template は authorized_profile のまま
  - effective_obligation_profile を report evidence gate に残す

reclassify-required
  - mismatch 時に停止し、requirement または classify input を直して再実行する

advisory-only
  - Epic -> Issue candidate で使う
  - final profile は決めない
```

downgrade を許す policy は作らない。

#### `--bundle-policy`

```text
auto
  - default
  - local resolver が bundle generation / staged adoption を決める

force-bundle
  - request にすぎない
  - Strict / Critical、stale .assurance.json、template mismatch、unknown risk では staged へ downgrade または block

force-staged
  - 常に有効
  - 初期 dogfood と Strict / Critical では推奨
```

重要な区別は次である。

```text
bundle generation != bundle promotion
```

ChatGPT が requirement / design / plan を一つの ZIP に入れても、canonical adoption は phase ごとに staged に行う。

### Workflow 別の扱い

| Workflow | Profile authority | ChatGPT role | Template rendering | Bundle policy |
|---|---|---|---|---|
| Epic -> multiple Issue candidates | final profile なし。candidate recommendation のみ | `minimum_safe_profile`、Lite disqualifier、Strict/Critical trigger を返す | profile-specific template は出さない | candidate-level staged |
| Standalone Issue requirement -> design/plan | local `assurance classify` | selected skeleton を埋め、mismatch risk を報告 | local compose first | generation は bundle 可、adoption は staged |
| Existing Issue refinement | existing `.assurance.json` | selected profile 内の refinement | existing / composed docs と hash 一致必須 | existing profile が制御 |
| ZIP draft bundle with no profile | profile unresolved | requirement-only or profile-neutral evidence | design/plan は出さないか brief に留める | force staged |

### Epic decomposition から Issue draft を作る場合

Epic-level ZIP が複数 Issue draft を返す場合、それらは Issue canonical docs ではなく Epic handoff evidence として扱う。

各 candidate は次を持つ。

```text
candidates/issues/cand-issue-001/
  candidate.json
  profile.json
  requirement-draft.md
  design-brief.md
  plan-brief.md
  classification-inputs.json
  bundle-recommendation.json
  creation-command.txt
  draft-artifact-commands.txt
  adoption-notes.md
```

`profile.json` は recommendation only である。

```json
{
  "candidate_id": "cand-issue-001",
  "profile_recommendation": {
    "recommended_profile": "standard",
    "minimum_safe_profile": "standard",
    "lite_allowed": false,
    "lite_disqualifiers": [
      "runtime/scaffold/workflow contract impact is possible"
    ],
    "strict_critical_triggers": []
  },
  "profile_decision": {
    "status": "not_authoritative",
    "must_run_local_assurance_classify": true
  }
}
```

Issue creation 後は、requirement を採用 / 具体化し、fresh `spec-reviewer` pass 後に `assurance classify` と `assurance compose` を実行する。Epic-level design/plan draft は claim-level evidence に格下げし、selected profile template へ再マッピングする。

### Human discussion 済み Issue requirement から design / plan を作る場合

この場合は、requirement が canonical / reviewed になってから profile を解決する。

```text
human discussion
  -> canonical requirement authored
  -> fresh spec-reviewer requirement pass
  -> assurance classify --stage requirement
  -> assurance compose --artifact design|plan|all
  -> ChatGPT ZIP fills selected design/plan skeleton
  -> local validation
  -> staged adoption
  -> fresh spec-reviewer
```

人間が `--profile strict` を指定することはできるが、それは manual escalation であり、`authorized_profile` を上書きしない。`authorized_profile=standard` で `requested_profile=strict` の場合、template は Standard のまま、effective obligation を Strict 相当に上げる運用にするか、`reclassify-required` で requirement / classification を見直す。

### ChatGPT に template を描かせるか

default は「ChatGPT 単独では描かせない」である。

正しい順序は次である。

```text
local:
  assurance classify --stage requirement
  assurance compose --artifact design|plan|all
  template hash / composed skeleton hash / section inventory を固定

ChatGPT:
  selected composed skeleton の section を埋める
  section-map.json と missing-section-report.json を返す

local:
  template hash / section coverage / profile mismatch を検証
  dry-run diff
  staged evidence に配置
```

ChatGPT に全 profile variant を出させない。理由は、stale template risk が増え、profile shopping を誘発し、reviewer が構造的に 75% の生成物を捨てる作業を背負うためである。

## ZIP schema additions / grade対応 schema

Issue-aware ZIP pack には次を追加する。

```text
specdock-authoring-pack/
  manifest.json
  provenance.json
  stale-if.json

  profile/
    profile-request.json
    profile-resolution.json
    profile-recommendations.json
    profile-evidence.json
    assurance-snapshot.json
    template-sources.json
    bundle-policy.json

  drafts/
    issue/
      requirement.md
      design.md
      plan.md
      section-map.json
      missing-section-report.json

  candidates/
    issues/
      cand-issue-001/
        candidate.json
        profile.json
        requirement-draft.md
        design-brief.md
        plan-brief.md
        classification-inputs.json
        bundle-recommendation.json
        creation-command.txt
        draft-artifact-commands.txt
        adoption-notes.md

  adoption/
    adoption-map.json
    eal-proposal.json

  validation/
    model-validation-report.json
    profile-validation-report.json
```

`manifest.json` は profile control を明示する。

```json
{
  "schema_version": "specdock.oracle_authoring_pack.v2",
  "kind": "epic_issue_decomposition | issue_requirement_design_plan_bundle",
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "profile_control": {
    "requested_profile": "auto",
    "requested_profile_source": "assurance-classify",
    "profile_override_policy": "forbid",
    "requested_bundle_policy": "auto",
    "resolved_bundle_policy": "staged",
    "profile_authority": "local-assurance",
    "chatgpt_profile_authority": "recommendation_only"
  },
  "template_control": {
    "template_rendering_authority": "local-assurance-compose",
    "chatgpt_template_selection_allowed": false,
    "all_profile_variants_allowed": false,
    "selected_profile_only": true,
    "template_hash_validation_required": true
  }
}
```

Validation rule:

- `chatgpt_profile_authority` は `recommendation_only` でなければならない。
- `template_rendering_authority` は `local-assurance-compose` でなければならない。
- `selected_profile_only=false` は candidate-only pack 以外では invalid。
- `profile_resolution.status=stale|blocked` の場合、design / plan draft は adoption-ineligible。
- ZIP 内の script-like files は plain text suggestion だけにし、実行権限を持たせない。

## Prompt best practices

ChatGPT ZIP 生成 prompt には、次の profile block を入れる。

```text
Issue profile control:
- You may recommend a profile, but you must not decide authorized_profile.
- authorized_profile is owned by local .assurance.json / assurance classify.
- If profile_resolution.json says status=resolved, use only that selected profile.
- If profile_resolution.json is missing/stale/blocked, do not render profile-specific design.md or plan.md.
- Do not output all profile variants.
- Do not create or modify .assurance.json.
- Do not claim Lite is valid unless local input already authorizes Lite; otherwise provide Lite evidence candidate only.
- For Strict/Critical, include specialist/fallback evidence requirements, but do not claim they are satisfied.
- Preserve composed template headings and section IDs.
- Output section-map.json mapping every generated section to the composed skeleton section.
- Any profile mismatch must be listed in validation/profile-validation-report.json.
```

candidate pack では次を指示する。

```text
For each Issue candidate:
- emit profile.json with recommendation only
- emit classification-inputs.json
- emit requirement-draft.md
- emit design-brief.md and plan-brief.md, not profile-specific templates
- mark profile_decision.status = not_authoritative
```

existing Issue pack では次を指示する。

```text
Use the attached composed design/plan skeletons.
Fill only the selected profile.
Do not add profile sections that are not in the skeleton unless listed as proposal in adoption-map.
```

## edge cases / 具体シナリオ

### `authorized_profile=standard` だが ZIP が `lite` design を返す

- 判定: invalid / reject selected template content。
- 対応: natural-language claim は advisory evidence として salvage 可能だが、template section fill としては使わない。
- canonical impact: Standard template で local compose し直し、必要なら ChatGPT に selected skeleton fill を再依頼する。

### `authorized_profile=lite` だが人間が `standard` を指定する

- 判定: manual escalation として許容可能。
- 対応: template は Lite のまま、effective obligation profile を Standard 相当に上げるか、`reclassify-required` で requirement / classifier input を見直す。
- report impact: manual escalation reason、追加 gate、戻し条件を `report.md` に残す。

### `.assurance.json` が stale

- 判定: design / plan draft は adoption-ineligible。
- stale 条件:
  - requirement hash が classifier input hash と異なる。
  - requirement reviewer target hash が変わった。
  - authorized_profile が欠落している。
  - template hash が変わった。
  - compose command version が変わった。
  - `.assurance.json` が別 Issue id の path を指している。
- 対応: `assurance classify` と `assurance compose` を再実行する。

### Strict / Critical の bundle ZIP

- 判定: generation は evidence として許可してもよいが、canonical adoption は force staged。
- 対応: specialist evidence または manual fallback evidence がない場合、readiness は block / incomplete。
- Critical では explicit approval / risk acceptance なしの fallback を許可しない。

### ChatGPT が `.assurance.json` を作る、または更新案を出す

- 判定: invalid。
- 対応: ZIP validation で block。`.assurance.json` は local assurance command だけが authority を持つ。

### ZIP に all profile variants が含まれる

- 判定: candidate-only brief 以外では invalid。
- 対応: selected profile 以外の design / plan は adoption-ineligible。再生成を推奨。

## unverified / 未検証事項

- ChatGPT Use が ZIP file を安定して毎回生成できるかは未検証である。
- ZIP 内 manifest / provenance / source-hashes が、ローカル validator に通る精度で安定生成されるかは未検証である。
- ZIP による authoring が orchestrator 認知負荷、human edit burden、reviewer repair loop 数を実際に下げるかは未検証である。
- `manual-tests/oracle-zip-authoring/` の preflight / capture / intake / validate / diff / stage scripts は未実装である。
- `--profile auto` / `--profile-source` / `--profile-override-policy` / `--bundle-policy` の command surface は提案段階であり、runtime contract ではない。
- ChatGPT 側は default branch `main` を検査しており、local detached HEAD の全差分と完全一致しているとは限らない。

## question candidates / 質問候補

### source-grounded に解けず、人間判断が必要な候補

- ZIP authoring pack の dogfood を `epic-00158` の manual-tests として先に行うか、先に新規 Issue を起こして runtime command design を formalize するか。
- ZIP file を repo に保存せず、summary artifact のみを保存する v1 で十分か。将来的に artifact-pack contract として ZIP / extracted tree の保存 surface を作るか。
- Strict / Critical で ChatGPT Use を named specialist evidence として扱う path を将来定義するか。v1 では oracle evidence に限定するのが安全。

### pressure-test question として切り出すべき候補

- `force-bundle` が request でしかないことを CLI help / schema / validation error で十分に表現できるか。
- candidate Issue の `profile_recommendation` が、将来の local `assurance classify` と食い違ったときに、どこまで自動 salvage するか。
- Lite の low-risk evidence を local validator でどこまで機械判定し、どこから reviewer / orchestrator 判断に残すか。

### 質問せずに解決できた候補

- ChatGPT に `authorized_profile` を最終決定させるか: させない。
- ChatGPT に `.assurance.json` を作らせるか: 作らせない。
- ChatGPT に all profile variants をまとめて返させるか: 原則させない。
- ZIP を canonical docs に直接展開するか: しない。

## terminology conflicts / 用語衝突

### `profile recommendation` vs `authorized_profile`

- `profile recommendation`: ChatGPT / Epic handoff / candidate analysis が返す advisory evidence。
- `authorized_profile`: `.assurance.json` / local `assurance classify` が解決する runtime template / guidance / obligation authority。
- 判断: 同じ "profile" でも authority が違うため、ZIP schema では `profile_recommendation` と `profile_resolution.authorized_profile` を分ける。

### `bundle generation` vs `bundle promotion`

- `bundle generation`: ChatGPT が requirement / design / plan を一つの ZIP に入れること。
- `bundle promotion`: canonical phase をまとめて進めること。
- 判断: 前者は許可候補、後者は不許可。canonical adoption は staged。

### `template rendering` vs `section fill`

- `template rendering`: selected profile template を materialize する authority。local `assurance compose` が持つ。
- `section fill`: composed skeleton の各 section を埋める作業。ChatGPT が担当できる。
- 判断: ChatGPT を template selector ではなく section filler として扱う。

### `manual escalation` vs `profile override`

- `manual escalation`: reviewer / specialist / evidence gate を強める補助判断。
- `profile override`: `authorized_profile` 自体を書き換える authority。
- 判断: human は stricter obligation へ manual escalation できるが、downgrade や `.assurance.json` override はできない。

## implications / 判断への含意

### 仕様 authoring workflow への含意

- ChatGPT Use を大きなまとまりの authoring backend として使う方向は有効である。
- ただし、system-architect / implementation-planner の役割を単純に ChatGPT ZIP で置き換えるのではなく、control plane を SpecDock runtime に残したうえで、ChatGPT を structured evidence producer として扱うのがよい。
- Epic -> Issue decomposition では、複数 Issue candidate の requirement draft / profile recommendation / classification inputs / dependency notes をまとめて ZIP で受ける価値が高い。
- Issue単体では、reviewer-pass 済み requirement から selected profile skeleton を local compose し、それを ChatGPT が埋める形がもっとも安全である。

### 実装方針への含意

v1 は shipped runtime ではなく、dogfood-only scripts と artifact practice から始める。

```text
manual-tests/oracle-zip-authoring/
  oracle-authoring-preflight
  oracle-authoring-prompt-pack
  oracle-zip-capture
  oracle-zip-intake
  oracle-zip-validate
  oracle-zip-diff
  oracle-zip-stage
  oracle-issue-authoring-zip
```

初期 pass criteria:

- ZIP capture が成功する。
- static ZIP validation が path traversal / hidden / symlink / binary / executable / oversize を拒否する。
- `manifest.json` / `provenance.json` / `source-hashes.json` / `stale-if.json` / `adoption-map.json` が必須になる。
- profile recommendation は advisory であり、`.assurance.json` を作らない。
- selected profile は existing `.assurance.json` または local `assurance classify` だけで決まる。
- `assurance compose` の selected skeleton hash と ChatGPT output の section map が一致する。
- Strict / Critical は force staged になり、specialist / fallback evidence gate が残る。
- canonical docs は ZIP から直接上書きされない。

### 最初の dogfood 案

`epic-00158 Agent Workflow PDCA Hardening` の配下で、次の三つの実験を行う。

```text
A. Candidate-only Epic -> Issue ZIP
  - ChatGPT emits multiple Issue candidates
  - profile recommendation only
  - no profile-specific template rendering

B. Existing Issue selected-profile ZIP
  - local requirement exists
  - local assurance classify resolves profile
  - local assurance compose renders design/plan skeleton
  - ChatGPT fills selected-profile sections

C. Mismatch probe
  - intentionally feed stale/mismatched profile_resolution
  - validator must block placement
```

## リスク/制約

| リスク | 影響 | 緩和 |
|---|---|---|
| ZIP を repo に直接展開する | path traversal / hidden file / canonical overwrite | quarantine + central-directory inspection + safe extraction |
| ChatGPT self-validation を信頼する | unsafe pack を安全と誤認 | local validation を authority にする |
| Grade を ChatGPT に決めさせる | Lite 誤選択 / Strict gate bypass | recommendation-only + local assurance authority |
| all profile variants を返させる | profile shopping / stale template risk | selected profile only |
| bundle を promotion と誤解する | phase gate bypass | bundle generation と staged adoption を分離 |
| Strict/Critical を ZIP で済ませる | specialist / fallback evidence 欠落 | force staged + gate evidence required |
| source hash mismatch | stale source に基づく adoption | preflight hashes と local observed hashes を照合 |
| artifact-pack と flat artifact contract の衝突 | workflow contract mismatch | v1 は extracted tree を repo 外 quarantine に置き、repo には flat summary artifact だけ保存 |

## 反映先

reflected_to: []

この research artifact は未採用 evidence である。採用する場合は、次のいずれかへ反映する。

- `epic-00158` の design / plan に dogfood scope と acceptance criteria を追加する。
- 新規 Issue として `manual-tests/oracle-zip-authoring/` の dogfood-only scripts を作る。
- `workflow_spec_authoring.md` に ChatGPT ZIP authoring pack の authority boundary を追加する。
- Issue authoring CLI / assurance docs に `--profile auto` semantics を追加する。
- 将来的に artifact-pack contract を設計する ADR または Epic を作る。

## 参考（References）

- ChatGPT 初回 output:
  - `/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/zip-authoring-pack-output.md`
- ChatGPT follow-up output:
  - `/private/tmp/codex-agent-work/501/session-20260706t125420z-specdock-chatgpt-zip-authoring-pack-fafe3add/issue-grade-followup-output.md`
- Local docs:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
