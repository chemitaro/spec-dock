---
種別: 要件定義書（Epic）
ID: "epic-00283"
タイトル: "ChatGPT Zip Authoring Pack Automation"
関連GitHub: ["#283"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["init-local-00003"]
---

# epic-00283 ChatGPT Zip Authoring Pack Automation — 要件定義（何を、なぜ行うか）

## 目的（Initiative との紐づき）

`epic-00283` は、`init-local-00003 Architecture Maintenance and Hardening` の一部として、ChatGPT Use / GPT-5.5 Pro Extended を SpecDock の仕様 authoring backend として dogfood できるようにする。

この Epic の目的は、ChatGPT が返す ZIP authoring pack や structured output を、canonical authority ではなく untrusted evidence として安全に受け取り、検証し、staged evidence へ変換し、main orchestrator が canonical docs へ採否判断できる workflow / script / prompt / skill surface を整えることである。

この Epic は、ChatGPT に正本を書かせる機能、reviewer gate を置き換える機能、Issue grade/profile を決定させる機能を作るものではない。SpecDock の source-of-truth、artifact authority、profile authority、fresh reviewer gate を維持したまま、ChatGPT の長文・複数ファイル生成能力を安全に使う。

## 背景と Why now

これまでの調査では、ChatGPT Use / GPT-5.5 Pro Extended が、SpecDock の高度分析、設計・計画 draft、Issue slicing、reviewer focus、ZIP による複数ファイル出力に有効であることが確認された。

一方で、ChatGPT output は local git state、untracked files、fresh reviewer independence、`.assurance.json`、template hashes、runtime validation、test execution を authority として保証できない。よって、ChatGPT output をそのまま canonical docs や reviewer pass として扱うと、SpecDock の authority boundary が崩れる。

特に今回のユーザー実験では、ChatGPT にディレクトリ構造を保った downloadable ZIP file を出力させ、展開できることが分かった。これは Epic design / plan と複数 Issue draft を一括生成する delivery mechanism として有望である。ただし、ZIP は path traversal、hidden file、symlink、binary、secret、stale source、unsafe authority claim などの検査を通す必要がある。

したがって、まずは shipped runtime ではなく `manual-tests/oracle-zip-authoring/` の dogfood-only script 群として、ChatGPT ZIP authoring pack の preflight、prompt pack、capture、intake、validation、diff、stage、adoption handoff を検証する。

## 能力 / モデル envelope（capability / model envelope）

### 対象 capability

- ChatGPT Use / GPT-5.5 Pro Extended に、複数ファイル・長文の authoring output を ZIP pack または structured pack として生成させる。
- ZIP pack を repo 外 quarantine に取り込み、安全検査、schema validation、source hash / stale condition validation、dry-run diff、staged artifact rendering に通す。
- Epic -> Issue candidate generation、Issue selected-profile design / plan fill、mismatch / stale probe を dogfood scenario として扱う。
- `adoption-map`、`eal-proposal`、`reviewer-focus`、`profile recommendation`、`section-map`、`missing-section-report` を machine-readable evidence として扱う。
- ChatGPT manual prompt run 自体を dogfood として使い、将来の script / skill に必要な preflight、prompt shape、output shape、failure mode を抽出する。

### model / lifecycle boundary

- ChatGPT ZIP は evidence-only である。
- ChatGPT は profile recommendation を出せるが、`authorized_profile` を決定しない。
- ChatGPT は selected composed skeleton の section を埋められるが、template selection、`.assurance.json` update、canonical compose を行わない。
- ChatGPT self-review / reviewer-focus は reviewer input であり、`spec-reviewer` pass ではない。
- Canonical adoption は main orchestrator が `requirement.md` / `design.md` / `plan.md` / `report.md` へ再記述し、fresh `spec-reviewer` を通す。
- ZIP generation と canonical phase promotion は別物である。`bundle generation != bundle promotion` を不変条件にする。

### cross-Issue invariant の seed

- ZIP validation は fail-closed。
- Canonical docs への direct overwrite は禁止。
- `profile recommendation != authorized_profile`。
- `template rendering != section fill`。
- raw transcript、secret、credential、token、cookie、private data は pack / artifact に含めない。
- proposed commands は dogfood-only until promoted。
- ChatGPT / browser / GitHub connector unavailable は degraded success ではなく、blocked / skipped evidence として扱う。

### 対象外の capability

- reviewer gate replacement。
- shipped runtime command の即時導入。
- provider registry / generic external oracle adapter。
- ChatGPT による `.assurance.json` 作成・更新。
- ChatGPT による all-profile template variant generation。
- raw ZIP / extracted tree の repo canonical artifact 化。
- GitHub PR review / merge preparation の置換。
- Deep Research live reliability の改善。

## ユースケース

### 正常系

- Maintainer が Epic / Issue の requirement、source paths、scope、non-scope、stale conditions を preflight に渡す。
- `oracle-authoring-preflight` が repo/ref/source_paths/source_hashes/denylist/profile state/stale_if を固定する。
- `oracle-authoring-prompt-pack` が ChatGPT に渡す prompt、source manifest、selected skeleton、ZIP schema、authority boundary を生成する。
- ChatGPT が `specdock-authoring-pack/` root を持つ ZIP を返す。
- `oracle-zip-capture` / `oracle-zip-intake` が ZIP を repo 外 quarantine に保存し、central directory を検査する。
- `oracle-zip-validate` が path、schema、manifest、provenance、source hash、unsafe authority claim、profile mismatch を検査する。
- `oracle-zip-diff` が canonical overwrite なしの dry-run diff を作る。
- `oracle-zip-stage` が scope-local `artifacts/` に sanitized Markdown evidence を作る。
- Main orchestrator が adoption-map を確認し、採否を `report.md` Evidence Adoption Ledger へ記録する。
- 採用内容だけを canonical docs へ再記述し、fresh `spec-reviewer` gate を通す。

### 例外 / 運用シナリオ

- GitHub connector / repo / target ref が利用できない場合、branch-sensitive pack generation は hard fail する。
- current branch が unavailable の場合、default-ref mode へ fallback できるが、branch-sensitive claim は adoption-ineligible または stale 条件付きにする。
- ZIP に absolute path、`..`、hidden path、symlink、hardlink、device file、binary、nested archive、executable bit、`.env*`、token、cookie、secret、`.git`、`.ssh`、`.codex`、`.agents`、`.github` が含まれる場合は reject する。
- `manifest.json` が `authority: evidence_only`、`adoption_status: unreviewed` を示さない場合は reject する。
- `profile_resolution.status` が stale / blocked の場合、design / plan draft は adoption-ineligible にする。
- `authorized_profile` と ZIP の selected profile が一致しない場合、section fill としては reject し、自然言語 claim だけ salvage 候補にできる。
- Strict / Critical は ZIP bundle generation を許可しても canonical adoption は force staged とし、specialist / fallback evidence gate を残す。
- ChatGPT unavailable / ZIP generation failed の場合、manual authoring path を継続する。

## エピック要件（Epic requirements）

- E-RQ-001: Dogfood-only script surface
  - 初期 script 群は `manual-tests/oracle-zip-authoring/` 配下に置く。
  - Proposed commands は runtime contract として扱わない。
  - Scripts は canonical docs を書き換えない。

- E-RQ-002: Preflight / source manifest contract
  - repo、requested ref、fallback ref、scope id、source paths、source hashes、attached file hashes、denylist result、stale_if、profile state を記録する。
  - branch-sensitive mode では clean worktree、pushed head、PR head SHA 一致を要求する。
  - default-ref mode では `branch_sensitive=false` を明示する。

- E-RQ-003: Prompt pack generation
  - ChatGPT に渡す source pack は allowlist-based にする。
  - Prompt は ZIP schema、authority boundary、profile control、template fill constraints、forbidden claims、output root を明記する。
  - Prompt は repo artifacts に含まれる instruction-like text を data として扱わせる。

- E-RQ-004: ZIP pack schema
  - ZIP は単一 root `specdock-authoring-pack/` を持つ。
  - 必須 file は `manifest.json`、`provenance.json`、`stale-if.json`、source hash / source manifest、`adoption/adoption-map.json`、validation report とする。
  - Issue-aware pack は profile request / resolution / recommendation / assurance snapshot / template source / bundle policy / section-map / missing-section-report を持つ。
  - Candidate-only pack は Issue candidate ごとに `candidate.json`、`profile.json`、`requirement-draft.md`、`design-brief.md`、`plan-brief.md`、classification inputs、creation command suggestion を持てる。

- E-RQ-005: Safe ZIP intake / validation
  - Direct extraction into repo を禁止する。
  - central directory inspection 後に safe extraction する。
  - path traversal、hidden paths、symlink、hardlink、device file、executable bit、binary、nested archive、oversize、denylisted path/content を reject する。
  - Schema invalid、source hash mismatch、stale_if missing、unsafe authority claim、unlisted source reliance は adoption-ineligible とする。

- E-RQ-006: Dry-run diff / staging
  - ZIP content は canonical docs へ直接配置しない。
  - Dry-run diff は intended canonical target と staged artifact target を分ける。
  - `artifacts/` へ置くのは sanitized flat Markdown summary / disc / research / decision-candidate evidence とする。
  - Raw ZIP / extracted tree の durable repo 保存は v1 scope 外とし、必要なら後続 artifact-pack ADR へ送る。

- E-RQ-007: Artifact authority boundary
  - ZIP、ChatGPT transcript、research、disc、onboarding brief、validation report は adoption 前 evidence とする。
  - Canonical authority は adopted canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger / Spec Authoring Gate に限る。
  - Evidence Adoption Ledger なしに delegated / ChatGPT evidence の採用を主張しない。

- E-RQ-008: Issue profile control
  - `authorized_profile` は `.assurance.json` / `assurance classify` が決定する。
  - `--profile auto` は local profile resolution を意味し、ChatGPT recommendation を意味しない。
  - ChatGPT は `minimum_safe_profile`、Lite disqualifier、Strict/Critical trigger を recommendation evidence として返せる。
  - ChatGPT は `.assurance.json` を作成・更新しない。

- E-RQ-009: Template rendering と section fill の分離
  - `assurance compose` が selected profile skeleton を生成し、template hash / skeleton hash / section inventory を固定する。
  - ChatGPT は selected skeleton の section を埋め、section-map と missing-section-report を返す。
  - All-profile variants は candidate-only brief 以外では invalid とする。

- E-RQ-010: Bundle generation と staged adoption の分離
  - ZIP に requirement / design / plan が同梱されても、canonical adoption は requirement -> design -> plan の順に staged に行う。
  - 各 phase で fresh `spec-reviewer` pass が必要である。
  - Self-review / reviewer-focus は reviewer input であり、reviewer pass ではない。

- E-RQ-011: Dogfood scenarios と metrics
  - v1 は少なくとも A: Candidate-only Epic -> Issue ZIP、B: Existing Issue selected-profile ZIP、C: Mismatch probe を実行する。
  - Metrics は validation failure rate、adoption ratio、human edit burden、fresh reviewer repair loop、profile mismatch block、canonical overwrite prevention、manual fallback success を含む。

- E-RQ-012: Manual fallback
  - ChatGPT / browser / GitHub connector / ZIP generation unavailable は degraded success ではない。
  - Manual authoring path と existing SpecDock workflow は継続可能でなければならない。

- E-RQ-013: Future promotion criteria
  - Shipped runtime command、provider docs、optional adapter、artifact-pack contract、reviewer gate backend は v1 acceptance ではない。
  - Dogfood evidence が安全性・有用性を示した場合だけ、後続 Issue / ADR で runtime promotion を検討する。

## エピック受け入れ条件（Epic acceptance criteria）

- E-AC-001: Preflight が branch / repo / source manifest を固定する。
  - 前提: current branch unavailable または default-ref mode。
  - 操作: proposed `oracle-authoring-preflight` を実行する。
  - 期待結果: inspected repo/ref、branch_sensitive、source_paths、stale_if、denylist result が記録される。
  - 観測点: preflight JSON / summary artifact。

- E-AC-002: ZIP intake が dangerous archive を拒否する。
  - 前提: path traversal、hidden path、symlink、binary、executable、nested archive を含む fixtures。
  - 操作: proposed `oracle-zip-intake` / `oracle-zip-validate` を実行する。
  - 期待結果: safe extraction 前に reject され、repo には canonical / artifact side effect が出ない。
  - 観測点: validation report、git status / filesystem inspection。

- E-AC-003: 必須 manifest / provenance / adoption map が検証される。
  - 前提: valid / invalid ZIP fixtures。
  - 操作: schema validation を実行する。
  - 期待結果: missing `manifest.json`、missing `provenance.json`、missing source hashes、missing stale_if、missing adoption-map は adoption-ineligible。
  - 観測点: schema validation report。

- E-AC-004: Unsafe authority claim が block される。
  - 前提: ZIP manifest または Markdown が `authority: accepted`、`adoption_status: adopted`、reviewer pass、phase completion、implementation readiness を claim する。
  - 操作: validation を実行する。
  - 期待結果: pack は reject または adoption-ineligible になり、canonical docs は更新されない。
  - 観測点: validation report、staged artifact absence。

- E-AC-005: Profile control が local assurance-owned として守られる。
  - 前提: `.assurance.json` / `assurance classify` で selected profile が解決済み。
  - 操作: selected-profile ZIP を validate する。
  - 期待結果: ZIP の profile recommendation は advisory として残り、authorized_profile / template selection は変更されない。
  - 観測点: profile-resolution report、`.assurance.json` unchanged evidence。

- E-AC-006: Selected skeleton fill が section-map と一致する。
  - 前提: local `assurance compose` で skeleton hash / section inventory が固定済み。
  - 操作: ChatGPT ZIP の `drafts/issue/design.md` / `plan.md` と `section-map.json` を validate する。
  - 期待結果: skeleton hash / section coverage / missing-section-report が一致しない pack は adoption-ineligible。
  - 観測点: profile-validation-report。

- E-AC-007: Candidate-only Epic -> Issue ZIP は profile-specific templates を出さない。
  - 前提: Epic-level decomposition pack。
  - 操作: candidate validation を実行する。
  - 期待結果: Issue candidate は requirement draft / design brief / plan brief / profile recommendation only を持ち、profile-specific canonical design / plan template body を出さない。
  - 観測点: candidate validation report。

- E-AC-008: Dry-run diff と staged artifact が canonical overwrite を防ぐ。
  - 前提: valid ZIP pack。
  - 操作: proposed `oracle-zip-diff` / `oracle-zip-stage` を実行する。
  - 期待結果: canonical files は直接変更されず、scope-local `artifacts/` に sanitized evidence が作成される。
  - 観測点: git diff、artifact frontmatter、diff report。

- E-AC-009: Evidence Adoption Ledger handoff が可能である。
  - 前提: staged artifact と adoption-map が存在する。
  - 操作: main orchestrator が adoption decision を記録する。
  - 期待結果: adopted / partially_adopted / rejected / deferred / stale / blocked の claim-level ledger が `report.md` に書ける情報を持つ。
  - 観測点: EAL proposal、report update candidate。

- E-AC-010: Fresh `spec-reviewer` gate は維持される。
  - 前提: ChatGPT ZIP 由来の content を canonical docs に採用した。
  - 操作: design / plan それぞれで fresh `spec-reviewer` を実行する。
  - 期待結果: ChatGPT self-review や reviewer-focus は pass として扱われず、fresh reviewer result だけが phase gate evidence になる。
  - 観測点: Spec Authoring Gate / reviewer evidence。

- E-AC-011: Dogfood A/B/C が完了する。
  - 前提: dogfood fixtures または real low-risk scope がある。
  - 操作: Candidate-only Epic -> Issue ZIP、Existing Issue selected-profile ZIP、Mismatch probe を実行する。
  - 期待結果: A/B は evidence-only artifact を生成し、C は validator が stale / mismatch placement を block する。
  - 観測点: dogfood report、validation reports、manual summary。

- E-AC-012: Manual fallback remains viable。
  - 前提: ChatGPT / ZIP capture / GitHub connector が unavailable。
  - 操作: workflow を続行する。
  - 期待結果: unavailable は degraded success ではなく blocked / skipped evidence として残り、manual authoring path に戻れる。
  - 観測点: report evidence、fallback summary。

## 証跡の権限境界（artifact authority）

- raw evidence として扱うもの:
  - `epic-00283/artifacts/` 配下の research / disc / onboarding / decision-candidate。
  - ChatGPT ZIP pack。
  - quarantine された extracted tree。
  - validation report。
  - dry-run diff。
  - adoption-map / eal-proposal。
  - reviewer-focus / self-review。
  - dogfood run summary。

- canonical authority として扱うもの:
  - `requirement.md`:
    - この Epic の目的、scope、non-scope、acceptance criteria、Issue seed。
  - `design.md`:
    - ZIP lifecycle、schema boundary、profile control、validation architecture。
  - `plan.md`:
    - Issue slicing、dogfood order、dependency graph、promotion criteria。
  - accepted ADR:
    - artifact-pack durable storage、remote reviewer gate backend など、長期判断が必要な場合。
  - `report.md` Evidence Adoption Ledger:
    - ChatGPT / ZIP / artifact evidence の採否と stale / blocked 状態。

- 禁止:
  - raw ZIP を canonical docs とみなすこと。
  - artifact path の存在だけを adoption とみなすこと。
  - ChatGPT output の self-claim を accepted authority とみなすこと。
  - raw transcript を canonical docs へ貼ること。

## スコープ

- 必須:
  - `manual-tests/oracle-zip-authoring/` dogfood scripts。
  - ZIP schema / JSON schema fixtures。
  - ZIP safe intake / validation / diff / stage scripts。
  - Prompt pack generation runbook。
  - Source manifest / stale_if / denylist handling。
  - Profile resolution snapshot / selected skeleton fill validation。
  - Dogfood A/B/C scenarios。
  - Sanitized artifact rendering。
  - `report.md` EAL proposal structure。
  - Japanese-first docs / README / prompt guidance。

- 禁止:
  - shipped runtime command として最初から公開すること。
  - canonical docs への direct write。
  - reviewer gate replacement。
  - `.assurance.json` の ChatGPT 作成・更新。
  - all-profile variants generation。
  - Strict / Critical specialist / fallback gate の省略。
  - ZIP self-validation を local validation の代替にすること。
  - secrets / tokens / cookies / production dumps / private customer data の添付。
  - host-local wrapper path の shipped runtime hardcode。

- 対象外:
  - provider registry。
  - generic oracle adapter。
  - remote final reviewer gate。
  - Deep Research live reliability。
  - artifact-pack durable ZIP storage contract。
  - GitHub PR repair loop。
  - automatic Lite default rollout。
  - existing Issue 全量 migration。

## 境界

- 常に行う:
  - repo/ref/source_paths/stale_if を記録する。
  - ZIP は quarantine してから検証する。
  - local assurance が profile / template を決める。
  - ChatGPT は evidence producer として扱う。
  - Adoption は main orchestrator が `report.md` に記録する。
  - Fresh reviewer gate を維持する。

- 判断が必要:
  - raw ZIP / extracted tree を repo に保存する将来 contract。
  - dogfood metrics が runtime promotion に十分か。
  - candidate issue の profile recommendation と local classify が食い違った場合の salvage policy。
  - Strict / Critical で ChatGPT Use を named specialist evidence として扱う将来 path。

- 行わない:
  - ZIP を repo root や canonical path に直接展開しない。
  - ChatGPT に profile decision を委ねない。
  - ChatGPT に template selection を委ねない。
  - self-review を `spec-reviewer` pass と表現しない。
  - unavailable / stale / schema invalid を degraded success にしない。

## 非機能要件

- 信頼性 / 一貫性:
  - 同じ preflight input、source hashes、schema version から deterministic validation result を返す。
  - Validation は fail-closed。
  - Source hash mismatch / stale condition / schema drift / unsafe authority claim は adoption-ineligible。

- セキュリティ:
  - ZIP inspection は safe extraction 前に行う。
  - Denylist paths and content を検査する。
  - Raw transcript、secret、credential、token、cookie、private data を artifact に残さない。
  - Script-like files は plain text suggestion とし、実行権限を持たせない。

- 運用:
  - Dogfood script は repo-local manual test として使える。
  - ChatGPT unavailable 時も manual workflow が成立する。
  - Proposed command は help / README で proposed / dogfood-only と明記する。

- 可読性:
  - Maintainer-facing docs / artifacts は日本語ファースト。
  - Path、command、schema key、fixed SpecDock terms は原文を保持する。

- 性能:
  - ZIP validation は local deterministic process とし、validation 自体に network access を要求しない。
  - Oversize ZIP / file count / file size limit を持つ。

## 依存 / 影響範囲

- 影響する component:
  - `manual-tests/oracle-zip-authoring/`
  - `manual-tests/oracle-zip-authoring/schemas/`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/artifacts/`
  - `epic-00283/report.md`
  - 将来必要なら `src/spec_dock/assets/spec_dock/docs/authoring/` の oracle evidence docs。
  - 将来必要なら `src/spec_dock/assets/install_root/.agents/skills/` の planning skill prompt guidance。

- 外部依存:
  - ChatGPT Use / GPT-5.5 Pro Extended / browser / GitHub connector は dogfood-only external dependency。
  - v1 validation / staging は local deterministic scripts を authority とする。

- 互換性:
  - Existing SpecDock workflow は維持する。
  - Existing manual / delegated authoring path を削除しない。
  - Shipped runtime support は dogfood evidence 後の後続判断にする。

## 後続 Issue seed

- parent requirement trace:
  - E-RQ-001〜E-RQ-013
- acceptance seed:
  - E-AC-001〜E-AC-012
- allowed local delta:
  - dogfood script name / schema detail / fixture shape / report format の具体化。
- forbidden parent boundary changes:
  - ChatGPT authority 化、reviewer gate replacement、profile authority 移譲、canonical direct write。
- expected evidence:
  - preflight JSON、validation report、dry-run diff、staged artifact、dogfood report、EAL proposal、manual fallback summary。
- suggested grade:
  - ZIP intake / validation / profile-control slices は `strict`。
  - docs / prompt / dogfood reporting slices は `standard`。

### Candidate Issue Seeds

- Dogfood Oracle ZIP Authoring Preflight And Prompt Pack
  - 目的: repo/ref/source_paths/stale_if/denylist/profile snapshot を固定し、ChatGPT ZIP generation 用 prompt pack を作る。
  - closes: E-RQ-001, E-RQ-002, E-RQ-003 / E-AC-001
  - suggested grade: `strict`

- Implement Safe ZIP Intake And Schema Validation
  - 目的: ZIP central-directory inspection、safe extraction、path / content rejection、manifest/provenance/schema validation を dogfood scripts として作る。
  - closes: E-RQ-004, E-RQ-005 / E-AC-002, E-AC-003, E-AC-004
  - suggested grade: `strict`

- Implement Oracle ZIP Diff And Staged Artifact Rendering
  - 目的: valid ZIP を canonical overwrite なしで dry-run diff し、scope-local sanitized Markdown evidence へ stage する。
  - closes: E-RQ-006, E-RQ-007 / E-AC-008, E-AC-009
  - suggested grade: `strict`

- Implement Profile Controlled Selected Skeleton Fill Validation
  - 目的: local assurance profile resolution、template hash、section inventory、section-map、missing-section-report を照合する。
  - closes: E-RQ-008, E-RQ-009 / E-AC-005, E-AC-006
  - suggested grade: `strict`

- Dogfood Candidate Only Epic To Issue ZIP Pack
  - 目的: Epic-level ZIP で複数 Issue candidate を出し、profile recommendation only / no profile-specific template rendering を検証する。
  - closes: E-RQ-011 / E-AC-007, E-AC-011
  - suggested grade: `standard`

- Dogfood Existing Issue Selected Profile ZIP Pack
  - 目的: reviewed Issue requirement から local assurance compose 済み skeleton を ChatGPT に埋めさせ、staged adoption flow を検証する。
  - closes: E-RQ-008, E-RQ-009, E-RQ-010 / E-AC-005, E-AC-006, E-AC-010, E-AC-011
  - suggested grade: `strict`

- Dogfood ZIP Mismatch And Stale Probe
  - 目的: stale profile_resolution、profile mismatch、source hash mismatch、unsafe authority claim を validator が block できることを検証する。
  - closes: E-RQ-005, E-RQ-008, E-RQ-010 / E-AC-002, E-AC-004, E-AC-005, E-AC-011
  - suggested grade: `strict`

- Document ZIP Authoring Pack Workflow And Adoption Ledger Examples
  - 目的: dogfood-only README、prompt rules、authority boundary、EAL examples、manual fallback rules を日本語ファーストで整備する。
  - closes: E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012
  - suggested grade: `standard`

- Evaluate Dogfood Metrics And Runtime Promotion Criteria
  - 目的: adoption ratio、validation failure rate、reviewer repair loops、human edit burden、fallback success を集計し、runtime promotion / defer / reject を判断する材料を作る。
  - closes: E-RQ-011, E-RQ-013 / E-AC-011, E-AC-012
  - suggested grade: `standard`

## 未確定事項

- Blocking question:
  - なし。

- Non-blocking design questions:
  - raw ZIP / extracted tree を repo 外 quarantine のみに残すか、将来 artifact-pack として repo に保存するか。
  - Runtime promotion の測定閾値。
  - Candidate profile recommendation と local classify mismatch の salvage policy。
  - ChatGPT Use を Strict / Critical の named specialist evidence として扱う将来 path。
