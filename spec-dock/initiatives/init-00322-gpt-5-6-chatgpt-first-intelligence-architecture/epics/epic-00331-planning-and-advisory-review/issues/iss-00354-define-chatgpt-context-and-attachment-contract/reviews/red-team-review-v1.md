# Red Team Review

- verdict: **FAIL**
- repository: `chemitaro/spec-dock`
- branch: `codex/iss-00354-chatgpt-context-contract`
- source HEAD: `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1`
- Candidate logical filename: `iss-00354-oracle-017-compatibility-candidate-20260804t033922z.zip`
- Candidate ID: `CAND-ISS-00354-ORACLE017-20260804T033922Z`
- Candidate timestamp: `2026-08-04T03:39:22Z`
- Candidate ZIP SHA-256: `8f979a5609b5d4dfa899871d50d51a659e273a7191b97e36c4d8de253348d13c`
- reviewed scope: `requirement.md`, `design.md`, `plan.md`, `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`
- excluded from verdict: `onboarding.md`, `candidate-note.md`, and all other artifacts

## Findings

### [P1] 現行の stage-blind harvest から profile-owned な Oracle 0.17.0 recovery への移行契約が閉じていない

- document/section: `requirement.md` §3.1、ISS354-REQ-021、ISS354-REQ-027–029、`design.md` §6・§10.2・§11、`plan.md` §3・S09–S10・S12
- evidence: exact source HEAD の `infra/issue_planning_chatgpt.py` は Oracle 終了コード nonzero または session state nonterminal で prompt submission 成否を判定せず `_recover_same_session` を呼び、`oracle session <session-id> --harvest --no-recover` を直接組み立てる。一方、文書は recovery を prompt submit 後と記述し、profile に version-specific harvest/capture argv contract がない。`design.md` §10.2 の `profile.inline_mode_characterized` も提示された profile contract に定義されていない。
- impact: Oracle 0.16.1 固有の recovery command を 0.17.0 に流用する余地、pre-submit failure への harvest、inline recovery eligibility の実装場所の曖昧さが残る。
- required correction: baseline を「submission evidence なしで harvest する stage-blind behavior」と訂正し、compatibility profile に version-specific same-session harvest/capture command builder と宣言済み inline capability を定義する。S09–S12 に現行 hardcoded argv の除去と profile 経由への移行を明記し、`prompt_submitted=false`/unknown の全 failure class は harvest/capture 0 回、post-submit は characterized profile command のみという invocation-level test を追加する。

### [P1] Stage-specific public reason の要件と設計が矛盾し、受け入れ判定が一意でない

- document/section: `requirement.md` ISS354-REQ-030・§12.2、`design.md` §15、`plan.md` S10・§18
- evidence: ISS354-REQ-030 は `oracle_prompt_reconstruction_mismatch`、`oracle_model_selection_unavailable`、`oracle_attachment_submission_failed`、`oracle_generation_incomplete`、`oracle_output_download_failed` 等を列挙し、異なる stage を generic retryable error に潰してはならないとする。しかし exact source HEAD の `PlanningInvocationResult` は主に `oracle_unavailable`、`oracle_capability_unsupported`、`oracle_session_recovery_required`、`oracle_artifact_*` を許可し、`design.md` は public reason の追加を調査事項に先送りし、既存 reason への many-to-one mapping も許容している。S10/§18 に authoritative mapping と exact test expectation がない。
- impact: 新しい public reason の追加と既存 reason への mapping の双方が適合と主張でき、CLI/API consumer、domain validation、受け入れテストの範囲が一意に決まらない。
- required correction: internal failure class から public `status`/`reason` への authoritative mapping を四文書で統一し、既存 reason 維持・新規 reason 追加・many-to-one mapping の許否を明記する。REQ-030 が public contract なら exact values/status pairing を AC と tests に追加し、private evidence のみなら見出し・列挙値をその意味に訂正する。

## Review notes

- GitHub connector で指定 repository/branch を確認し、branch HEAD と `d0659cfa83bf97a05ceab01f4d9ce76162a2baa1` は identical。default branch fallback は未使用。
- 添付 ZIP の SHA-256 は提示値と一致。ZIP integrity/CRC は成功。
- logical root は一つ。path traversal、absolute entry、symlink entry はなし。
- 10 regular files をすべて展開・確認。MANIFEST/CHECKSUMS 相当ファイルは存在しない。
- Candidate logical filename、Candidate ID、timestamp、repository、branch、source HEAD に不一致なし。
- repository、Candidate、canonical documents、Git、GitHub state は変更していない。修正版・patch・別 ZIP は生成していない。
