---
種別: 要件定義書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
関連GitHub: ["#299"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00299 Prompt Pack Constraints — 要件定義

## 0. 結論

この Issue は、`authoring pack prepare` を installed runtime surface として実装し、`authoring preflight github-sync` で得た preflight/source evidence から、ChatGPT に渡す deterministic prompt pack input を生成する。

生成物は evidence-only の prompt pack であり、ChatGPT output の ZIP/tree format、metadata、provenance、safe output constraints、禁止 authority claim を明示する。生成物は canonical adoption、`.assurance.json` mutation、`authorized_profile` 決定、reviewer pass、execution-ready、PR-ready、PR delivery を主張してはならない。

## 1. 目的

`authoring preflight github-sync` の結果と source manifest を入力に、同じ input から同じ prompt pack tree を生成し、ChatGPT に対して安全な ZIP/tree output contract を明示する。

この Issue は iss-00298 の後続であり、iss-00298 で deferred/fail-closed のまま残された `authoring pack prepare` を実装対象にする。backend invocation、ZIP review/stage、candidate/adoption validators は後続 Issue の責務として残す。

## 2. 観測可能な成果

完了後に観測できること:

- `./spec-dock/scripts/spec-dock authoring pack prepare ...` が deferred ではなく command-local status を返す。
- preflight/source evidence から prompt pack tree が deterministic に生成される。
- prompt pack tree には少なくとも次が含まれる。
  - `manifest.json`
  - `provenance.json`
  - `source-manifest.json`
  - `stale-if.json`
  - `safe-output-constraints.md`
  - `chatgpt-use-prompt.md`
  - `expected-output-contract.md` または同等の prompt guidance
- generated metadata は以下を固定する。
  - `authority: evidence_only`
  - `adoption_status: unreviewed`
  - `bundle_generation_not_promotion: true`
- `github-synced` と `local-context` は provenance 上で区別される。
- `local-context` pack は `sync_state: local_context`、`github_sync: not_verified`、`provided_context_paths`、`diff_summary`、`unsynced_reason`、`adoption_requires: explicit_eal_disposition` を保持する。
- source manifest は `__pycache__`、`.pyc`、`.pyo` など生成 cache を含めない。
- prompt guidance は expected ZIP root `specdock-authoring-pack/` と required metadata を明示する。
- prompt guidance は forbidden authority claims を明示し、ChatGPT output がそれらを主張しないよう制約する。
- provider-side source of truth と dogfood mirror の両方で同等の behavior を検証できる。

完了後に観測できてはいけないこと:

- backend process の実行。
- ChatGPT output ZIP の review、safe extraction、stage。
- candidate/adoption validator の実装。
- canonical docs の自動上書き。
- `.assurance.json` の作成または更新。
- `authorized_profile` の決定。
- reviewer pass、execution-ready、PR-ready、PR delivery の自己主張。
- broad `--force` bypass。
- raw transcript、secret、credential、private key、host-local absolute path の durable 保存契約。

## 3. 親スコープと継承条件

### 3.1 親 Epic

- Epic ID: `epic-00295`
- Epic title: `ChatGPT Authoring Pack Installed Runtime`
- 継承する要件群:
  - Runtime command group。
  - GitHub sync / evidence mode。
  - Prompt pack contract。
  - ZIP/tree artifact contract。
  - Evidence-only authority boundary。
  - Provider-side source-of-truth / dogfood mirror distinction。
  - relay execution / final PR delivery defer policy。

### 3.2 この Issue で再定義しない境界

- `authoring preflight github-sync` の preflight 判定そのものは iss-00298 の成果を前提にし、この Issue では prompt pack input として読む。
- backend invocation は iss-00300。
- ZIP review / stage は iss-00301。
- candidate/adoption validators は後続 Issue。
- approval check と node creation boundary は後続 Issue。
- PR delivery は final quality Issue `iss-00307`。

## 4. Actor / Trigger

| Actor | 役割 | この Issue との関係 |
|---|---|---|
| Maintainer / main orchestrator | Issue planning / execution owner | prompt pack prepare を実行し、evidence-only output を確認する |
| ChatGPT evidence lane | draft / candidate evidence producer | prompt pack guidance に従って ZIP/tree output を作るが、正本権限を持たない |
| dev-coder | 実装担当 | provider-side runtime と mirror 更新を行う |
| code-reviewer | 実装レビュー | command dispatch、determinism、boundary leakage を確認する |
| qa-reviewer | テストレビュー | positive / negative fixture と CLI verification を確認する |
| spec-reviewer | 仕様レビュー | scope、non-scope、authority boundary、relay policy を確認する |

Trigger:

- CLI command:
  - `./spec-dock/scripts/spec-dock authoring pack prepare`
- 前提:
  - preflight evidence が存在する、または `local-context` 用 provenance が明示されている。
  - output directory は明示指定され、canonical docs ではない場所に限定される。

## 5. Scope

### 5.1 対象範囲

- `authoring pack prepare` の runtime command implementation。
- `application/authoring_pack/pack_prepare.py` の use case orchestration。
- `domain/authoring_pack/*` に prompt pack / safe output constraints の契約を定義。
- `presentation/authoring_pack/*` に JSON/text diagnostics と renderer を定義。
- preflight result / source manifest から deterministic prompt pack tree を生成。
- `github-synced` / `local-context` provenance の分岐。
- source manifest の cache exclusion。
- safe output constraints の生成。
- forbidden authority claim list の生成。
- expected ZIP root / required metadata / allowed output paths の prompt guidance。
- provider-side asset と dogfood mirror の同時更新。
- CLI / unit / fixture tests。
- issue-local report evidence proposal。

### 5.2 対象外

- backend invocation command の実装。
- ChatGPT backend command resolution。
- ZIP central directory review。
- ZIP extraction。
- tree fallback review。
- stage / dry-run diff / EAL candidate generation。
- candidate validators。
- issue draft adoption validators。
- approval check。
- automatic canonical adoption。
- automatic GitHub Issue creation。
- `.assurance.json` mutation。
- `authorized_profile` assignment。
- reviewer pass / execution-ready / PR-ready marking。
- broad `--force` bypass。
- PR 作成または PR delivery。

### 5.3 変更しないもの

- `authoring preflight github-sync` の既存 status taxonomy と evidence mode contract。
- `local-context` が lower authority であること。
- `pass` が command-local validation pass であり reviewer pass ではないこと。
- provider-side assets が source of truth であり `spec-dock/...` dogfood mirror は validation target であること。
- 中間 Issue で PR delivery しない relay policy。

## 6. 要求される振る舞い

### BH-001: preflight pass から deterministic prompt pack を生成する

- Given:
  - `authoring preflight github-sync` が `status=pass` の JSON evidence を出力済み。
  - source manifest が存在する。
  - output directory が指定されている。
- When:
  - `authoring pack prepare --preflight <path> --output-dir <path>` を実行する。
- Then:
  - status は `pass`。
  - prompt pack tree が生成される。
  - 同一 input から同一 logical payload が生成される。
  - generated metadata は evidence-only boundary を含む。
- And:
  - canonical docs と `.assurance.json` は変更されない。

### BH-002: stale / blocked preflight では prompt pack を pass にしない

- Given:
  - preflight evidence が `blocked` または `stale`。
- When:
  - `authoring pack prepare` を実行する。
- Then:
  - status は `blocked` または `stale`。
  - prompt pack は ChatGPT invocation-ready として扱われない。
  - diagnostics は regeneration / reconciliation の必要性を示す。
- And:
  - output が存在する場合も diagnostics-only に限定する。

### BH-003: local-context は明示 provenance と lower authority を保持する

- Given:
  - preflight evidence mode が `local-context`。
  - `provided_context_paths`、`diff_summary`、`unsynced_reason` の少なくとも必要項目が記録されている。
- When:
  - prompt pack を生成する。
- Then:
  - `provenance.json` と prompt guidance は `github_sync: not_verified` を明示する。
  - `adoption_requires: explicit_eal_disposition` を明示する。
  - `github-synced` と同等の authority を主張しない。

### BH-004: forbidden authority claims を prompt guidance に固定する

- Given:
  - prompt pack generation input が valid。
- When:
  - `safe-output-constraints.md` と `chatgpt-use-prompt.md` を生成する。
- Then:
  - ChatGPT output が以下を主張してはならないことを明示する。
    - canonical adoption。
    - `.assurance.json` 作成・更新。
    - `authorized_profile` 決定。
    - reviewer pass。
    - execution-ready。
    - PR-ready。
    - PR delivery。
  - `pass` は command-local validation pass であり reviewer pass ではない、と明示する。

### BH-005: ZIP/tree output contract を明示する

- Given:
  - valid prompt pack input。
- When:
  - prompt pack guidance を生成する。
- Then:
  - expected root `specdock-authoring-pack/` を明示する。
  - required metadata entries を明示する。
  - unsafe path、secret、raw transcript、nested archive、binary、executable、symlink、wrong root、forbidden authority claim が後続 review で拒否対象になることを明示する。
- And:
  - この Issue では review 実装は行わない。

### BH-006: source manifest は generated cache を含めない

- Given:
  - source path 配下に `__pycache__`、`.pyc`、`.pyo` が存在する。
- When:
  - source manifest を生成または転記する。
- Then:
  - manifest hash と source file list に cache files は含まれない。

## 7. 受け入れ条件

### AC-001: `authoring pack prepare` が deferred を脱する

- 操作:
  - `./spec-dock/scripts/spec-dock authoring pack prepare --help`
  - valid fixture で `./spec-dock/scripts/spec-dock authoring pack prepare ...`
- 期待結果:
  - command は iss-00299 deferred diagnostics を返さない。
  - supported options と status output が確認できる。
- 観測点:
  - CLI output、pytest。

### AC-002: valid github-synced input から prompt pack tree を生成する

- 操作:
  - valid `github-synced` preflight fixture を入力する。
- 期待結果:
  - `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md`、`chatgpt-use-prompt.md` が生成される。
  - status は `pass`。
- 観測点:
  - generated tree、JSON snapshot test。

### AC-003: output は deterministic である

- 操作:
  - 同じ fixture と同じ option で 2 回生成する。
- 期待結果:
  - timestamp 等の非決定要素を除いた logical payload digest が一致する。
  - deterministic field ordering が維持される。
- 観測点:
  - pytest digest comparison。

### AC-004: evidence-only metadata が固定される

- 操作:
  - generated metadata を確認する。
- 期待結果:
  - `authority: evidence_only`
  - `adoption_status: unreviewed`
  - `bundle_generation_not_promotion: true`
- 観測点:
  - `manifest.json`、`provenance.json`、`safe-output-constraints.md`。

### AC-005: forbidden authority claim guidance が含まれる

- 操作:
  - `safe-output-constraints.md` と `chatgpt-use-prompt.md` を確認する。
- 期待結果:
  - canonical adoption、`.assurance.json` mutation、authorized profile、reviewer pass、execution-ready、PR-ready、PR delivery を禁止する guidance がある。
- 観測点:
  - fixture assertion。

### AC-006: expected ZIP/tree contract が明示される

- 操作:
  - generated guidance を確認する。
- 期待結果:
  - root `specdock-authoring-pack/`。
  - required metadata entries。
  - unsafe entry categories。
  - review/stage は後続 Issue であること。
- 観測点:
  - fixture assertion。

### AC-007: local-context provenance が lower authority を保持する

- 操作:
  - `local-context` fixture で pack を生成する。
- 期待結果:
  - `sync_state: local_context`
  - `github_sync: not_verified`
  - `provided_context_paths`
  - `diff_summary`
  - `unsynced_reason`
  - `adoption_requires: explicit_eal_disposition`
- 観測点:
  - `provenance.json`、prompt guidance。

### AC-008: stale / blocked input は fail-closed になる

- 操作:
  - stale source hash、blocked preflight、missing preflight metadata の fixture で実行する。
- 期待結果:
  - non-zero exit。
  - status は `stale` / `blocked` / `fail` のいずれか適切な分類。
  - ChatGPT invocation-ready と誤読できる output を生成しない。
- 観測点:
  - CLI output、diagnostics JSON。

### AC-009: source manifest は cache files を除外する

- 操作:
  - `__pycache__` / `.pyc` / `.pyo` を含む fixture を使う。
- 期待結果:
  - generated source manifest に cache files が含まれない。
- 観測点:
  - source manifest JSON assertion。

### AC-010: broad `--force` bypass が存在しない

- 操作:
  - help output と parser を確認する。
- 期待結果:
  - `--force` または同等の broad bypass がない。
  - `local-context` は explicit evidence mode と provenance requirement で表現される。
- 観測点:
  - CLI help assertion、parser test。

### AC-011: provider-side source と dogfood mirror が一致する

- 操作:
  - provider-side asset と `spec-dock/...` mirror を比較または installed runtime smoke test を実行する。
- 期待結果:
  - behavior と help が一致する。
- 観測点:
  - pytest、dogfood runtime command。

### AC-012: canonical docs / `.assurance.json` / PR delivery を変更しない

- 操作:
  - 実装後に `git status --short`、`git diff --check` を確認する。
- 期待結果:
  - canonical docs の自動上書きなし。
  - `.assurance.json` mutation なし。
  - PR delivery claim なし。
- 観測点:
  - command output、Issue report。

## 8. 例外・エッジケース

### EC-001: preflight evidence が存在しない

- 期待される扱い:
  - `fail` または `blocked`。
  - required input missing を diagnostics に出す。
  - prompt pack pass にしない。

### EC-002: preflight status が `pass` ではない

- 期待される扱い:
  - preflight status を継承または pack prepare status へ明確に mapping。
  - ChatGPT invocation-ready と誤読させない。

### EC-003: local-context の provenance が不足する

- 期待される扱い:
  - `blocked`。
  - `unsynced_reason` または context evidence が必要だと示す。

### EC-004: source hash mismatch

- 期待される扱い:
  - `stale`。
  - regenerate / reconcile を促す。
  - adoption-sensitive evidence として分類する。

### EC-005: output-dir が repo 内 canonical path を指す

- 期待される扱い:
  - `rejected` または `blocked`。
  - canonical docs 直接書き込みを防ぐ。

### EC-006: secret-looking path / host-local absolute path が input に含まれる

- 期待される扱い:
  - `rejected`。
  - durable output に含めない。

### EC-007: prompt guidance 内の禁止語の扱い

- 期待される扱い:
  - 禁止 claim は「禁止対象として列挙する」ことは許可。
  - 生成物自身が達成済み claim として主張する文脈は不可。

## 9. 非機能要求

- Deterministic:
  - 同じ input から同じ logical output。
- Fail-closed:
  - provenance 不足、stale、unsafe、missing metadata は pass にしない。
- Privacy:
  - raw transcript、secret、credential、private key、host-local absolute path を durable output に含めない。
- Portability:
  - installed runtime asset と dogfood mirror の両方で動作する。
- Minimal dependency:
  - 既存 runtime architecture に合わせ、不要な外部依存を追加しない。
- Observability:
  - JSON と human-readable diagnostics を持つ。
- Authority clarity:
  - validation pass と adoption / reviewer pass を混同しない。

## 10. Issue Grade 判定材料

Workflow authority としての Issue Grade: `standard`

`assurance classify --stage requirement` は `authorized_profile=standard` を返したため、この Issue の obligation authority は `standard` とする。

ただし、ChatGPT Use は次の理由で `strict` 相当のリスク信号を提示した。

- installed runtime CLI behavior を変更する。
- prompt pack metadata / generated contract に影響する。
- safe output constraints は authority / security / privacy 境界に関係する。
- provider-side asset と dogfood mirror の両方を更新する。
- 後続 iss-00300 / iss-00301 / validators の入力契約になる。
- broad bypass、secret leakage、forbidden authority claim の混入が高リスクである。

そのため、実行義務は `standard` としつつ、上記は reviewer focus として扱う。実装範囲は backend invocation や ZIP extraction を含まないため、`critical` 相当の扱いにはしない。

## 11. 依存関係

前提:

- iss-00298:
  - `authoring preflight github-sync`
  - `github-synced` / `local-context` evidence mode
  - source manifest cache exclusion
  - deferred/fail-closed authoring commands

後続:

- iss-00300:
  - backend invocation
- iss-00301:
  - ZIP review / stage
- 後続 validators:
  - candidate/adoption validation
- iss-00307:
  - final quality gate / PR delivery

## 12. 設計への引き渡し

design.md では以下を必ず扱う。

- `commands/authoring.py` の CLI dispatch。
- `application/authoring_pack/pack_prepare.py` の use case orchestration。
- `domain/authoring_pack/prompt_pack_contract.py` または同等 contract。
- `domain/authoring_pack/zip_contract.py` の expected output guidance。
- `domain/authoring_pack/source_manifest.py` の cache exclusion reuse。
- `presentation/authoring_pack/pack_prepare_renderer.py` または同等 renderer。
- `github-synced` / `local-context` provenance model。
- deterministic output strategy。
- diagnostics / status taxonomy。
- provider-side source / dogfood mirror sync。
- no backend / no ZIP review / no adoption boundary。

## 13. 実装計画への引き渡し

plan.md では以下を必ず分解する。

- CLI args / parser update。
- domain contract / schema implementation。
- use case orchestration。
- renderer / file writing。
- fixture generation。
- deterministic tests。
- local-context tests。
- forbidden claim tests。
- source cache exclusion tests。
- mirror smoke tests。
- report evidence / PR defer evidence。
