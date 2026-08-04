# 補助アーティファクト: Context / Attachment / Oracle 0.17 Contract 実例集

> **implementation aid / non-canonical / Red Team レビュー対象外**  
> `CAND-ISS-00354-ORACLE017-V2-20260804T043533Z` の補助資料。review対象四文書を置き換えない。

## 1. Preserved contract summary

| Concern | Chat body | Attachments | Runtime / Oracle |
|---|---|---|---|
| Goal / operation | required | supplemental | typed operation selection |
| Repository / branch / HEAD | required | substitute forbidden | exact pre/postflight |
| Authority / no mutation | required | detailed explanation allowed | Human/apply gate |
| Detailed steps | minimal | primary location | provider operation directory |
| Candidate / Review identity | compact identity | original evidence path | strict output binding |
| Attachment inventory/SHA | not embedded | no generated input manifest | no entry inspection |
| Thread handle / transcript | forbidden | forbidden | adapter-private |
| Oracle version/model/stage | content-free summary only | none | compatibility profile / private receipt |

## 2. Planning minimal body example

```md
Operation: Issue planning
Objective: Create an evidence-only Candidate for existing Issue iss-00354.

Repository: chemitaro/spec-dock
Branch: codex/iss-00354-chatgpt-context-contract
Source HEAD: d0659cfa83bf97a05ceab01f4d9ce76162a2baa1
Initiative: init-00322
Epic: epic-00331
Issue: iss-00354

Verify the exact connected GitHub repository, named branch, and source HEAD.
Do not use the default branch or attachments as a repository substitute.
Do not mutate repository, canonical documents, GitHub, Issue state, or Human authority.

Expected output: one authoring ZIP.
Read the attached operation instructions.
```

Oracle version、model label、retry policyの詳細を本文へ毎回連結しない。Runtime profileとattached operation instructionが所有する。

## 3. Path assembly

```text
static provider operation attachment directory
+ required dynamic original evidence paths
+ optional operator-supplied directory paths
= top-level attachment_paths tuple
```

Runtimeが行わないこと:

```text
walk / glob / stat each entry / open / decode / hash each entry
classify / filter / copy / rename / archive / generate input manifest
exclude failing entries / drop required evidence
```

## 4. Oracle 0.17 invocation intent

Conceptual direct attempt:

```text
oracle <profile browser args>
  --model <logical profile mapping>
  --browser-model-strategy <profile strategy>
  --remote-chrome <managed loopback endpoint>
  --slug <private session slug>
  --prompt <exact synthesized string>
  --file <static directory original path>
  --file <dynamic evidence original path> ...
```

actual repeatable attachment syntaxと0.17 flagsはS09 characterizationで確定する。未確認flagを実装計画から発明しない。

## 5. One-shot inline recovery example

```text
initial direct attempt
  -> failure_class=attachment_submission_failed
  -> prompt_submitted=false
  -> profile.inline_mode_characterized=true
  -> automatic_new_execution_budget=1
  -> new execution with same prompt digest + same original paths + inline mode
  -> no third execution
```

not eligible:

- prompt reconstruction mismatch。
- model selection failure。
- response generation timeout。
- output download failure。
- artifact validation failure。
- required attachmentを落とす必要があるcase。

## 6. Prompt case identifiers

| Case | Purpose | Raw content persistence |
|---|---|---|
| `P-SHORT-ASCII` | browser readiness control | no |
| `P-UNICODE-JA` | UTF-8/quotes/newlines | no; fixture source only |
| `P-ISS354-REPRESENTATIVE` | realistic long Markdown | no; source fixture only |
| `P-TRAILING-NL` | exact end-of-input behavior | no |

execution receiptはcase ID、SHA-256、byte lengthだけを持てる。

## 7. Model evidence example

```json
{
  "logical_model": "pro",
  "observed_model_label": "<observed non-empty label>",
  "model_verified": true,
  "profile_version": "0.17.0"
}
```

`GPT-5.6 Sol`はexternal observation ledgerに記録できるが、direct characterization前は上記placeholderを置換しない。

## 8. Output / thread matrix

| Operation | Successful submission lane | Output | Recovery after submit |
|---|---|---|---|
| Planning | Blue start/reuse | authoring ZIP | same-session only |
| Formal Review | fresh Red | closed JSON | same-session only |
| Semantic Revision | verified/new Blue | authoring ZIP | same-session only |
| Mechanical Revision | no ChatGPT | deterministic local result | none |

pre-submit failed Oracle executionはlaneをadvanceしない。successful Red submission後にnew executionでreviewを再生成しない。

## 9. Evidence handling

Durable formal evidence:

- exact source identity。
- Candidate ZIP + SHA / logical filename。
- Review JSON + reviewed identity。
- Human decision / apply record。

Operational content-free evidence:

- Oracle exact version/profile ID。
- prompt case ID / digest。
- target kind category。
- logical / observed model label / verified flag。
- attachment mode。
- terminal stage / submission / response / artifact booleans。
- failure class / retry count。

Do not persist:

- raw prompt or attachment contents copied for diagnostics。
- private absolute path / target URL。
- session/thread handle。
- raw browser transcript / UI dump。
- credentials or config payload。
