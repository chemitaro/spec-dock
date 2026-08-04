# 補助アーティファクト: 決定履歴・矛盾・移行台帳

> **補助資料 / non-canonical**  
> 本台帳は `CAND-ISS-00354-20260803T172642Z` の source-grounded synthesis であり、canonical report または Evidence Adoption Ledger
> そのものではない。

## 1. GitHub 確認結果

| 項目 | 結果 |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Requested branch | `codex/iss-00354-chatgpt-context-contract` |
| Requested source HEAD | `88a9fdb567f17f50bee421862d3b7859a5eb6384` |
| Branch existence | confirmed |
| Branch vs requested HEAD | identical / ahead 0 / behind 0 |
| Default branch fallback | not used |
| Branch vs `main` | inspected snapshotでは branch が4 commits ahead |
| Issue hierarchy | `init-00322` → `epic-00331` → `iss-00354`; parent GitHub Issue `#334` |
| Issue assurance | `standard` provisional |

## 2. 全 artifact 確認一覧

指定 directory 内の次の17ファイルをファイル名で全件確認した。

| # | Filename | 主な役割 / 採用判断 |
|---:|---|---|
| 1 | `20260803t005640z-research-current-chatgpt-context-attachment-research.md` | 現行 prompt / attachment / Oracle adapter 調査 |
| 2 | `20260803t005840z-interview-chatgpt-thread-continuity-scope-interview.md` | Blue継続 / fresh Red の Option A 採用 |
| 3 | `20260803t010552z-chatgpt-output-chatgpt-clarification-analysis.md` | continuity advisory。user decision に従属 |
| 4 | `20260803t011239z-interview-chatgpt-thread-failure-recovery-interview.md` | continuity failure時の fail-closed / new Blue 採用 |
| 5 | `20260803t011552z-chatgpt-output-chatgpt-continuity-recovery-analysis.md` | recovery advisory。manifest SHA提案は後続決定で失効 |
| 6 | `20260803t023549z-interview-chatgpt-context-attachment-matrix-interview.md` | body / attachment matrix の Option A 採用 |
| 7 | `20260803t023819z-chatgpt-output-chatgpt-context-attachment-matrix-analysis.md` | matrix advisory。strict envelopeの一部は歴史的 |
| 8 | `20260803t024349z-interview-chatgpt-output-template-contract-interview.md` | operation別 output instruction 採用 |
| 9 | `20260803t024658z-chatgpt-output-chatgpt-output-template-contract-analysis.md` | ZIP / JSON guidance。入力manifest案は失効 |
| 10 | `20260803t025103z-interview-chatgpt-context-contract-scope-interview.md` | product/personal分離、operation directory方式へ修正採用 |
| 11 | `20260803t025321z-chatgpt-output-chatgpt-context-contract-scope-analysis.md` | common strict profile案は部分失効 |
| 12 | `20260803t030211z-disc-chatgpt-operation-pack-flexible-input-discussion.md` | Option Cを統合した最終synthesis |
| 13 | `20260803t030323z-interview-chatgpt-attachment-directory-safety-interview.md` | 初期safe collection質問。推奨安全策は最終決定で不採用 |
| 14 | `20260803t030543z-chatgpt-output-chatgpt-attachment-directory-safety-analysis.md` | fail-closed / scanner提案は歴史的記録 |
| 15 | `20260803t034911z-interview-chatgpt-attachment-transport-entry-boundary-interview.md` | 無検査・全件・direct transport Option C 最終採用 |
| 16 | `20260803t035221z-chatgpt-output-chatgpt-attachment-transport-entry-boundary-analysis.md` | transport advisory。user Option C が優先 |
| 17 | `rules.md` | artifact directory local rule |

## 3. 最終採用事項

### D-001 Minimal body

目的、operation、repository、branch、HEAD、scope identity、authority、output だけを本文に置く。

### D-002 Detailed attachment instructions

詳細手順、review criteria、revision rules、output schema / examples は Markdown attachments に置く。
attachments は instruction を含み得る。

### D-003 Operation directory

各 product-owned operation は prompt template と attachment directory を別管理する。file 増減で code を変えない。

### D-004 Option C direct transport

directory path を direct Oracle へ渡す。SpecDock は tree を walk / inspect / transform / hash / filter しない。

### D-005 Normal error

unsupported entry / transport failure は Oracle / ChatGPT の通常 error。自動除外、変換、retry、fallbackをしない。

### D-006 Output remains typed

Planning / Revision は ZIP、Review は closed JSON。output validator と Human binding は維持する。

### D-007 Blue / Red

Clarification / Planning / Semantic Revision は verified Blue。Candidateごとの Review は fresh Red。

### D-008 Continuity recovery

Blue validation失敗時は complete current inputs で new Blue。lineage曖昧時は Human block。

### D-009 Product boundary

direct Oracle only。personal `chatgpt-use` wrapper は runtime dependency / formal evidence source にしない。

### D-010 Non-authority

ChatGPT output は evidence-only。canonical mutation / adoption はしない。

## 4. 置換済み提案

| Historical proposal | Status | 理由 |
|---|---|---|
| attachment manifest + per-file SHA | superseded | Option C が入力 manifest / checksum を拒否 |
| filename / extension allowlist | superseded | contents / names を分類しない |
| regular-file only / symlink reject | superseded | symlink / special entry を判断しない |
| secret / private path scanner | superseded for input attachment collection | operator responsibility。content-free public diagnosticsは維持 |
| size / count hard limits | superseded for input attachment collection | transport通常結果へ委ねる |
| transport capability precheck per entry | superseded | entry除外 /変換を誘発する |
| automatic ZIP conversion | rejected | inputを変更する |
| strict all-operation profile/schema | rejected | operation-specific flexibilityに反する |
| attachment reference-only | rejected | detailed instructions を attachmentsへ移す |
| Blue / Red same thread | rejected | fresh review independenceを壊す |
| every failure requires Human confirmation | rejected | exact lineageならnew Blueを開始できる |
| personal wrapper continuation | rejected | product dependency boundaryに反する |

## 5. Current implementation conflict table

| Current implementation | Conflict | Target |
|---|---|---|
| `MAX_RELEVANT_FILES` / byte limits | Option C | remove from input path |
| `_safe_source_file` / descriptor reads | Option C | no source file materialization |
| `_reject_sensitive` on attachment content | Option C | remove from input collection |
| `PlanningPromptAttachment` classification / SHA | Option C | direct Path references |
| exact attachment index in body | Option A/C | remove |
| role + transport resources concatenated into body | Option A | minimal `prompt.md`; detailed attachments |
| `_write_transport_pack` | Option C | direct Oracle path argv |
| generated `context-NNN.md` | Option C | remove |
| generated input manifest / source-manifest | Option C | remove |
| `_attachments_match_source_manifest` | Option C | remove from input path |
| `--context-manifest` | operation directory | hard cutover |
| per-role random new session | Blue continuity | provider-owned thread policy |
| onboarding 13 H2 / 4 PlantUML prompt hardcode | flexible content | semantic minimum |
| exact ZIP / Review JSON parser | no conflict | retain |
| Candidate / Review / Human binding | no conflict | retain |
| exact GitHub preflight / postflight | no conflict | retain |
| managed Chrome / direct Oracle | no conflict | retain |

## 6. Parent scope contradictions

`epic-00331` canonical docs currently state that detailed role / task / authority / output contract is in the prompt body and
attachments are reference-only data. Issue #354 final decision changes this responsibility split。

Migration rule:

- update only the conflicting input contract wording;
- keep exact GitHub identity;
- keep Candidate / Review / Human / apply lifecycle;
- keep fresh Review;
- keep direct Oracle;
- keep output ZIP / closed JSON;
- do not change Issue ordering or Epic completion criteria beyond necessary consistency。

## 7. Output Candidate と runtime output の区別

この手動 Candidate ZIP は user brief に従い、三文書、exactly-one onboarding、補助 artifacts を含む。
source HEAD 時点の formal Issue Planning runtime は canonical three documents + exactly-one onboarding companion の
exact authoring ZIPを期待する。

したがって、この Candidate の補助 artifact inventory を runtime authoring ZIP schema の変更として暗黙採用しない。
runtime output inventory を変える場合は別の明示要件・validator変更・reviewが必要である。

## 8. Technical capability gates

ユーザー判断は完了しているが、implementation 前に primary contract を確認する必要がある。

1. direct Oracle directory attachment。
2. multiple direct attachment paths。
3. direct Oracle same-conversation continuation。
4. normal failure mapping。

unsupported 時の選択肢は「停止して再設計」のみであり、wrapper / API fallback はない。

## 9. Follow-up ownership

| Topic | Ownership |
|---|---|
| Issue Planning input implementation | iss-00354 |
| Parent Epic contradiction update | iss-00354 closure |
| Clarification public direct-Oracle command | clarification owning follow-up |
| Other ChatGPT roles | operation-specific follow-up |
| Cross-scope thread retention ADR | only if policy expands beyond Issue-local |
| Generic attachment preparation tooling | optional operator tooling; runtime scannerにはしない |

## 10. Candidate authority

本台帳は Blue Team evidence である。正式な EAL reflection は main orchestrator が canonical docs へ採用する時に行う。
本 Candidate は Red Team review、PASS / FAIL、patch、PR、commit、push、merge、Issue close を含まない。
