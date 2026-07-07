---
種別: research
ID: "20260706t090820z-research"
タイトル: "ChatGPT Oracle Advanced Analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連: []
authority: "synthesized"
created_by_role: "main-orchestrator"
oracle_provider: "chatgpt-use"
oracle_session: "specdock-chatgpt-role-analysis"
model: "gpt-5.5-pro"
wrapper: "oracle-chatgpt"
wrapper_mode: "browser"
requested_branch: "unavailable-detached-head"
local_head: "918e624b8a97a4c67bd5ac1ac4ff552999b64bbb"
inspected_repo: "chemitaro/spec-dock"
inspected_ref: "main"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "not_applicable"
derived_from:
  - "chatgpt-use live run: specdock-chatgpt-role-analysis"
  - "deep-research-use dry-run: specdock-chatgpt-deep-research-check"
intended_targets:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md"
  - "future issue for optional oracle evidence provider"
source_paths:
  - "AGENTS.md"
  - "pyproject.toml"
  - "README.md"
  - "src/spec_dock/assets/install_root/.codex/config.toml"
  - "src/spec_dock/assets/install_root/.codex/AGENTS.md"
  - "src/spec_dock/assets/install_root/.codex/agents/*.toml"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-*.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow*.md"
  - "src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md"
  - "src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md"
  - "src/spec_dock/assets/spec_dock/templates/artifacts/research.md"
  - "src/spec_dock/assets/spec_dock/templates/artifacts/disc.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/requirement.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/design.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/plan.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/report.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/plan.md"
---

# 20260706t090820z-research ChatGPT Oracle Advanced Analysis

## 位置づけ

- この artifact は、`chatgpt-use` / GPT-5.5 Pro Extended を SpecDock の高度分析能力としてどう使うべきかを調査した source-grounded research evidence である。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への採用前の evidence であり、単独では workflow authority、reviewer pass、phase promotion、implementation readiness を主張しない。
- 主結論は、`chatgpt-use` を reviewer gate や canonical authority の置換にせず、optional oracle evidence provider として導入すること。

## 調査目的

- SpecDock の既存 role / reviewer / delegated authoring / evidence model を保ったまま、ChatGPT GPT-5.5 Pro Extended を高度分析に利用する安全な導入方式を明らかにする。
- `consultant`、`deep-consultant`、`repo-analyst`、`researcher`、`spec-reviewer`、`qa-reviewer`、`code-reviewer`、`system-architect`、`implementation-planner` のうち、置換可能なもの、補強に留めるべきもの、置換してはいけないものを分ける。
- dogfood-only の first artifact から provider asset / docs / optional adapter へ進める段階的 roadmap を整理する。

## sources / 調査方法

- 参照先:
  - local `chatgpt-use` skill と wrapper script。
  - local `deep-research-use` skill と wrapper script。
  - provider-side SpecDock agent / skill / workflow docs under `src/spec_dock/assets/...`。
  - dogfooding initiative docs under `spec-dock/initiatives/init-local-00002...` and `init-local-00003...`。
  - GitHub repository context: `chemitaro/spec-dock`, default branch `main`。
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で active context が未設定であることを確認した。
  - `git rev-parse HEAD`、`git branch --contains HEAD`、`gh repo view` で detached HEAD / default branch / repo context を確認した。
  - `oracle-chatgpt --dry-run summary --files-report` で約 101k token / 44 files の bundle を確認した。
  - `oracle-deep-research --dry-run summary --files-report` で Deep Research wrapper の dry-run を確認した。
  - `oracle-chatgpt` live run `specdock-chatgpt-role-analysis` を実行し、Pro Extended が選択済みであること、browser slot を取得したこと、約 9 分 11 秒で回答が返ったことを確認した。
- 実験条件:
  - local worktree は detached `HEAD` at `918e624b8a97a4c67bd5ac1ac4ff552999b64bbb`。
  - `git branch --contains HEAD` は `(no branch)`, `main`, `main-fable` を示した。
  - GitHub default branch は `main`。
  - active SpecDock context は未設定。

## facts / 観測できた事実

- `chatgpt-use` wrapper は browser mode、fixed Codex-only ChatGPT Project URL、`gpt-5.5-pro`、Pro Extended thinking、manual-login profile、archive disabled、API provider credentials unset を固定する。
- `deep-research-use` wrapper は browser mode、fixed Codex-only ChatGPT Project URL、`gpt-5.5-pro`、ChatGPT Deep Research、manual-login profile、archive disabled、API provider credentials unset を固定する。
- `chatgpt-use` は repo-local architecture / code / workflow analysis 向きで、`deep-research-use` は public-web research / citation / standards / vendor info 向きである。
- 両 wrapper は GitHub repo と default branch を `gh repo view` / `git symbolic-ref` から検出して prompt に repository connector context を注入しようとする。今回の worktree は detached HEAD のため current branch は unavailable になる。
- `init-local-00002 Prototype Feature Expansion` は feature/operator value 拡張の approved initiative であり、今回の dogfood research の置き場所として自然である。
- `init-local-00003 Architecture Maintenance and Hardening` は source-of-truth、workflow authority、provider registry、reviewer semantics などを変更する場合の受け皿である。
- `spec-reviewer` / `code-reviewer` / `qa-reviewer` は fixed JSON schema と authoritative `review_status` を返す workflow gate である。
- `consultant` / `deep-consultant` は read-only decision support であり、`chatgpt-use` の高度分析能力と責務が近い。
- `system-architect` / `implementation-planner` は scope-local `artifacts/` に exactly one flat Markdown draft / analysis を作る delegated authoring contract を持つ。canonical docs は main orchestrator の single-writer authority のままである。

## ChatGPT の分析結果要約

### Executive recommendation

- `chatgpt-use` は SpecDock の既存 gate / canonical authority の代替にせず、optional oracle evidence provider として導入する。
- 直接置換を検討できるのは `consultant` / `deep-consultant` の read-only decision support 部分に限定する。
- reviewer 系 role は gate semantics を持つため置換しない。ChatGPT は preflight / risk scouting / critique input に留める。

### Role-by-role matrix

| Role | 推奨 | 理由 |
|---|---|---|
| `consultant` | 条件付きで oracle backend 化可 | read-only decision support であり、option framing / tradeoff analysis が `chatgpt-use` と近い |
| `deep-consultant` | 最有力の oracle backend 候補 | 高影響・長期・tooling/model/vendor 判断の高コスト分析に合う |
| `researcher` | 補強 | public-web/citation が中心なら `deep-research-use`、repo reasoning 中心なら `chatgpt-use` |
| `repo-analyst` | 補強 | local repo traversal / symbol / command evidence を持つ role なので完全置換しない |
| `system-architect` | 補強 | scope-local artifact write / diff guard / adoption ledger contract を持つため、ChatGPT は draft input |
| `implementation-planner` | 補強 | plan artifact contract を持つため、ChatGPT は critique / risk / test strategy input |
| `spec-reviewer` | 置換禁止 | fixed JSON schema と authoritative `review_status` gate を持つ |
| `code-reviewer` | 置換禁止 | code review gate と strict output contract を持つ |
| `qa-reviewer` | 置換禁止 | test adequacy gate と strict output contract を持つ |
| `dev-coder` / `doc-writer` / `spec-manager` | 置換禁止 | 実装、恒久 docs 編集、SpecDock command operation は local workflow authority を伴う |

### Proposed architecture

```text
main orchestrator / operator
  -> select task scope and source files
  -> run chatgpt-use manually or through a host-local optional adapter
  -> capture answer as research/disc artifact under scope artifacts/
  -> record provenance, source_paths, stale_if, privacy review
  -> main orchestrator adopts/rejects in Evidence Adoption Ledger
  -> canonical docs updated only after adoption
  -> required fresh reviewers still run
```

- 最初は wrapper-only external oracle evidence provider として dogfood する。
- 後段で `oracle-consultant` / `external-oracle` のような read-only specialist role を追加できるが、reviewer gate backend にはしない。
- shipped product から `/Users/...` や `/Volumes/...` の個人 local wrapper path を直接 shell out しない。
- product 側は abstract `OracleEvidenceProvider` contract と host-local opt-in config に寄せる。

## inference / 推測

- 最小で安全な導入は、`init-local-00002` の feature artifact として `chatgpt-use` output を evidence 化し、canonical docs や reviewer gate へは昇格させない形で dogfood すること。
- `consultant` / `deep-consultant` を完全に削除して置き換えるより、role contract は SpecDock 側に残し、backend / evidence provider として ChatGPT を選べるようにする方が壊れにくい。
- `spec-reviewer` / `code-reviewer` / `qa-reviewer` の replacement は、strict JSON schema と gate status の downstream contract を壊すため現時点では不適切。
- `system-architect` / `implementation-planner` への接続は、draft 作成者の代替ではなく、設計案・計画案・リスク表の input として扱うのがよい。
- provider registry、host-local capability discovery、runtime shell-out、workflow authority model 変更に進む場合は `init-local-00003` 側の architecture concern になる。

## 推奨 roadmap

### Phase 0: dogfood-only research artifact

- `init-local-00002` の `artifacts/` に ChatGPT oracle research / discussion を残す。
- provenance、source paths、privacy review、stale conditions、unverified items を記録する。
- product runtime は変更しない。
- reviewer gate replacement はしない。

### Phase 1: provider docs / host guidance

- shipped docs に optional oracle evidence provider の使い方を追加する。
- 候補 path:
  - `src/spec_dock/assets/spec_dock/docs/integrations/chatgpt-oracle.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/oracle-evidence.md`
- docs では evidence-only、no gate replacement、no hardcoded local path、secret/file denylist を明記する。

### Phase 2: optional role-backed adapter

- `oracle-consultant` / `external-oracle` などの read-only role を検討する。
- `consultant` / `deep-consultant` の backend として扱い、既存 role を削除しない。
- unavailable / failed / stale output は reviewer pass や degraded success にしない。

### Phase 3: optional CLI or runtime adapter

- 抽象 adapter contract、stub command、hermetic tests、opt-in config、file allowlist / denylist が固まってから検討する。
- live ChatGPT / browser / GitHub connector は integration smoke に限定する。

### Phase 4: reviewer preflight only

- `oracle preflight spec-review`、`oracle preflight code-review`、`oracle preflight qa-risk` のような risk discovery は可能。
- ただし final `spec-reviewer` / `code-reviewer` / `qa-reviewer` は必ず別に fresh gate として実行する。

## unverified / 未検証事項

- ChatGPT Project 内で GitHub connector が常に利用可能かは、今回の ChatGPT 回答では「確認できた」とされたが、local Codex 側から直接検証できるものではない。
- Deep Research の live 起動は今回実施していない。dry-run は成功したが、過去メモリには Deep Research UI activation failure の記録があるため、live reliability は未確認である。
- ChatGPT output を保存・再取得するための durable session export contract は未設計である。
- Shipped product として optional adapter を持つ場合の config path、capability discovery、stub testing contract は未設計である。
- `new artifact` stdout が `spec-dock/spec-dock/...` と表示されたが、実ファイルは期待どおり `spec-dock/initiatives/.../artifacts/` に生成された。stdout 表示の二重 path が runtime bug か表示上の問題かは未調査である。

## question candidates / 質問候補

- 人間判断が必要な候補:
  - ChatGPT oracle を正式な feature epic として起票するか、まずは dogfood-only artifact として継続調査に留めるか。
  - `oracle-consultant` のような新 role 名を追加するか、既存 `deep-consultant` の backend option とするか。
  - Deep Research の live reliability をこの feature scope で検証するか、public-web research が必要になるまで defer するか。
- pressure-test question:
  - `chatgpt-use` output が reviewer finding と矛盾した場合、どちらを gate authority とするか。推奨は reviewer gate を authority とし、ChatGPT output は evidence / follow-up candidate として扱う。
  - GitHub connector が unavailable のとき、attached files だけで analysis を採用してよいか。推奨は branch/repo-sensitive analysis では採用しない。
- 質問せずに解決できた候補:
  - first artifact の置き場所は `init-local-00002` が適切。feature/operator value expansion の範囲であり、architecture model の変更ではないため。

## terminology conflicts / 用語衝突

- `replacement`:
  - ユーザーの文脈では「sub-agent の責務を ChatGPT Use に切り替える」意味を含む。
  - SpecDock の workflow 文脈では、role contract / reviewer gate / canonical authority を置換するかどうかが別問題になる。
  - この artifact では、backend / evidence provider の切替と workflow authority の置換を分けて扱う。
- `review`:
  - ChatGPT の自然文 review / critique と、`spec-reviewer` / `code-reviewer` / `qa-reviewer` の authoritative `review_status` gate は同じではない。
- `research`:
  - `chatgpt-use` は repo-local high-depth analysis。
  - `deep-research-use` は public-web / citation-heavy research。
  - 両者を同じ `researcher` replacement として扱うと用途が混ざる。

## edge cases / 具体シナリオ

- GitHub connector unavailable:
  - `chatgpt-use` wrapper prompt の hard failure condition に従い、artifact evidence として採用しない。
  - `repository access failed` 相当の failure artifact / report evidence として扱う。
- Detached HEAD:
  - current branch は unavailable とし、default branch `main` と attached local filesの組み合わせで分析したことを provenance に残す。
  - branch-sensitive claim は stale / low confidence にする。
- Reviewer preflight confusion:
  - ChatGPT が reviewer-like finding を出しても、`review_status` は持たない。
  - final reviewer gate を省略しない。
- Secrets exposure:
  - wrapper が API env vars を unset しても、添付ファイルに secret が含まれる risk は別に残る。
  - `.env*`、tokens、cookies、production dumps、private customer data は attach しない。
- Runtime shell-out:
  - host-local wrapper path を shipped runtime に hardcode すると multi-host failure になる。
  - opt-in config / capability discovery / stub testing が必要。

## implications / 判断への含意

- 今回の research は `init-local-00002` の feature evidence として保持し、canonical initiative docs へは未採用のままにする。
- 次に進めるなら、まず dogfood-only feature issue を起こし、manual `chatgpt-use` runbook、artifact provenance、adoption ledger sample、stale handling を定義する。
- provider docs / adapter / CLI integration は後続段階に分ける。
- reviewer gate semantics、promotion record、source-of-truth model を変更する場合は architecture initiative 側で扱う。

## リスク/制約

- Advisory output を workflow authority と誤認すると、SpecDock の reviewer gate と evidence model を破壊する。
- ChatGPT / Oracle / browser / manual-login / GitHub connector は host-local external dependency なので、required workflow gate にすると可用性が落ちる。
- Public-web research が中心でない task に `deep-research-use` を使うと、速度と focus が悪化する。
- Raw transcript や prompt 全文を canonical docs に保存すると、ノイズ、private reasoning、secret 混入 risk が増える。

## 反映先

- reflected_to:
  - なし。この artifact は `adoption_status: unreviewed` の research evidence であり、canonical docs へは未反映。
- candidate targets:
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/report.md`
  - future feature epic / issue for dogfood-only oracle evidence workflow
  - possible provider docs under `src/spec_dock/assets/spec_dock/docs/`

## 推奨 follow-up

- Feature initiative:
  - Dogfood-only oracle evidence workflow issue:
    - manual `chatgpt-use` runbook
    - artifact provenance / stale condition schema
    - Evidence Adoption Ledger sample
    - no reviewer gate replacement
  - Provider docs issue:
    - optional oracle evidence provider docs
    - no hardcoded local path
    - secret/file denylist
  - Optional role-backed adapter issue:
    - `oracle-consultant` or `deep-consultant` backend option
    - unavailable / stale / failure handling
    - final reviewer gates remain required
- Architecture initiative only if needed:
  - Generic provider registry
  - Runtime shell-out contract
  - Capability discovery as source-of-truth
  - Reviewer gate semantics change

## 参考（References）

- Local ChatGPT Use skill:
  - `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/chatgpt-use/SKILL.md`
  - `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt`
- Local Deep Research Use skill:
  - `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/deep-research-use/SKILL.md`
  - `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/skills/deep-research-use/scripts/oracle-deep-research`
- ChatGPT live run:
  - session slug: `specdock-chatgpt-role-analysis`
  - result: completed, Pro Extended, approximately 9m11s
- Deep Research dry-run:
  - session slug: `specdock-chatgpt-deep-research-check`
  - result: dry-run completed
