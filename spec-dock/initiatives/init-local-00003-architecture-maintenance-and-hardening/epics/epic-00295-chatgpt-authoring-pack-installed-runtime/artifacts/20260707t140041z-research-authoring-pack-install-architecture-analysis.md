# SpecDock authoring-pack install architecture analysis

作成日: 2026-07-07

対象: `chemitaro/spec-dock`

入力:

- ChatGPT-Use / GPT-5.5 Pro Extended による分析
- `src/spec_dock/cli.py`
- `pyproject.toml`
- `src/spec_dock/assets/spec_dock/scripts/spec-dock`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- `src/spec_dock/assets/install_root/.agents/skills/**`
- `scripts/authoring-pack/**`
- 直前の workflow integration analysis

## 1. 結論

ユーザー指摘の通り、現在の `scripts/authoring-pack/` 配置には大きな欠陥がある。

`scripts/authoring-pack/` は SpecDock 開発 repo 直下の dogfood helper であり、`spec-dock init/update` によって利用プロダクトへ配布されない。したがって、この場所に置いたままでは「SpecDock が提供する workflow/tooling」ではなく、「SpecDock repo 自身でだけ使える開発補助」に留まる。

推奨アーキテクチャは次の通り。

- 正本実装は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` に移す。
- primary UX は `./spec-dock/scripts/spec-dock authoring ...` とする。
- 必要なら互換・手動実行用に `src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py` を thin wrapper として配る。
- workflow docs は `src/spec_dock/assets/spec_dock/docs/` に置く。
- agent skill は `src/spec_dock/assets/install_root/.agents/skills/spec-dock-authoring-pack/` として配る。
- repo root `scripts/authoring-pack/` は一時的な dogfood compatibility surface に縮小し、長期的には削除または thin shim のみにする。

## 2. 現在の配置の欠陥

SpecDock の provider / consumer 境界は明確である。

- provider-side source of truth: `src/spec_dock/`
- consumer dogfood workspace: `spec-dock/`
- installer が導入先へ配る scaffold: `src/spec_dock/assets/spec_dock/`
- installed agent tooling: `src/spec_dock/assets/install_root/`
- 導入先で日常利用する runtime: `./spec-dock/scripts/spec-dock`

`src/spec_dock/cli.py` では `_MANAGED_DIRS = ("docs", "templates", "scripts", "system")` が定義され、`spec-dock init/update` は `src/spec_dock/assets/spec_dock/{docs,templates,scripts,system}` を target repo の `spec-dock/` へ同期する。

一方、現在の helper は repo root の `scripts/authoring-pack/` にある。これは package assets でも managed scaffold でもない。したがって利用プロダクトには入らない。

現状:

```text
SpecDock 開発 repo:
  scripts/authoring-pack/*.py がある
  -> dogfood では使える

SpecDock 導入先 product repo:
  spec-dock/scripts/spec-dock はある
  spec-dock/scripts/spec_dock_runtime/ はある
  scripts/authoring-pack/*.py はない
  -> ChatGPT authoring-pack workflow を使えない
```

この状態で workflow docs や skill だけ更新しても、利用者の環境では実行コマンドが存在しない。

## 3. 推奨 target layout

### 3.1 正本 runtime 実装

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/
  commands/authoring.py
  application/authoring_pack/
    prepare.py
    backend.py
    review.py
    stage.py
    selected_skeleton_fill.py
    issue_candidates.py
  domain/authoring_pack/
    status.py
    authority_boundary.py
    pack_paths.py
    pack_review.py
    pack_stage.py
    selected_skeleton_fill.py
    issue_candidates.py
  presentation/authoring_pack/
    json_reports.py
    markdown_reports.py
    cli_text.py
```

既存 runtime architecture は `cli/`, `commands/`, `application/`, `domain/`, `infra/`, `presentation/` に分かれている。authoring-pack もこの layered runtime に載せるのが自然である。

### 3.2 installed wrapper

```text
src/spec_dock/assets/spec_dock/scripts/authoring-pack/
  prepare_chatgpt_authoring_pack.py
  invoke_chatgpt_backend.py
  review_chatgpt_authoring_pack.py
  stage_chatgpt_authoring_pack.py
  validate_selected_skeleton_fill.py
  validate_issue_candidates.py
  README.md
```

これは primary surface ではなく、手動実行・移行・後方互換のための thin wrapper とする。中身は runtime module を呼び出すだけにする。

### 3.3 shipped docs

```text
src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
src/spec_dock/assets/spec_dock/docs/authoring_pack.md
src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md
```

`workflow_spec_authoring.md`、`workflow_initiative.md`、`workflow_epic.md`、`workflow_issue.md` から必要に応じてリンクする。

### 3.4 shipped skill

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-authoring-pack/SKILL.md
```

`src/spec_dock/cli.py` の `_MANAGED_SKILL_NAMES` に追加し、`spec-dock init/update` で導入先の `.agents/skills/` に入るようにする。

## 4. Runtime command と standalone helper の判断

primary は runtime command にするべきである。

理由:

- SpecDock の日常操作は `./spec-dock/scripts/spec-dock` に集約されている。
- runtime help / registry / command dispatch / tests に載せられる。
- 導入先 product repo で自然に使える。
- `spec-dock update` で更新される managed surface になる。
- 将来的な workflow integration と skill guidance が command 名を安定して参照できる。

推奨 command group:

```text
./spec-dock/scripts/spec-dock authoring pack prepare
./spec-dock/scripts/spec-dock authoring backend invoke
./spec-dock/scripts/spec-dock authoring pack review
./spec-dock/scripts/spec-dock authoring pack stage
./spec-dock/scripts/spec-dock authoring selected-skeleton validate
./spec-dock/scripts/spec-dock authoring issue-candidates validate
```

standalone helper は残してよいが、長期的な正本にしない。

standalone helper を本体にすると、runtime command と helper script の二重 surface になり、help / registry / tests / workflow docs が drift する。したがって `spec-dock/scripts/authoring-pack/*.py` は runtime command の thin wrapper として扱う。

## 5. backend command 設定

個人環境の `/Users/.../.codex/skills/chatgpt-use/scripts/oracle-chatgpt` を workflow に直書きしてはいけない。

推奨 contract:

1. CLI option:
   - `--backend-command '<argv prefix>'`
2. environment variable:
   - `SPECDOCK_CHATGPT_COMMAND='<argv prefix>'`
3. optional local ignored config:
   - `spec-dock/.agent/authoring-pack/backend.json`
   - または `spec-dock/.agent/authoring-pack/backend.toml`
4. 未設定:
   - `status=blocked` または明確な error で fail-closed

重要な制約:

- shell string として実行しない。
- `shlex.split` 後の argv list を `subprocess.run(..., shell=False)` に渡す。
- `ORACLE_CHATGPT_COMMAND` は互換 fallback 程度に留める。
- shared docs / templates / managed config に個人 path を書かない。
- machine-specific config は gitignored な `spec-dock/.agent/` 配下に置く。

## 6. workflow / skill shipping plan

### docs

`workflow_chatgpt_authoring_pack.md` には、以下を明記する。

- ChatGPT output は `authority: evidence_only`
- `adoption_status: unreviewed`
- `bundle_generation_not_promotion: true`
- ChatGPT は `authorized_profile` を決定しない
- ChatGPT は `.assurance.json` を作成・更新しない
- ChatGPT self-review は `spec-reviewer` pass ではない
- staged artifact は canonical docs ではない
- EAL candidate は final EAL row ではない

### skill

`spec-dock-authoring-pack/SKILL.md` は、次を持つ。

- first-read docs
- required command sequence
- forbidden claims
- backend configuration contract
- adoption boundary
- failure / stale / rejected / blocked の扱い

既存 planning skills には、詳細手順を貼り込まず、必要時に `spec-dock-authoring-pack` へ route する hook だけ追加する。

## 7. migration plan

### Phase 0: 欠陥を明文化

- root `scripts/authoring-pack/README.md` に「temporary dogfood compatibility surface」と明記する。
- consumer source of truth は runtime assets へ移す方針を書く。

### Phase 1: runtime module へ移植

現在の root scripts のロジックを runtime modules に分解する。

```text
scripts/authoring-pack/authoring_pack_review.py
  -> src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/review.py

scripts/authoring-pack/authoring_pack_stage.py
  -> src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/stage.py

scripts/authoring-pack/authoring_pack_selected_skeleton_fill.py
  -> src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/selected_skeleton_fill.py

scripts/authoring-pack/authoring_pack_issue_candidates.py
  -> src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/issue_candidates.py

scripts/authoring-pack/invoke_chatgpt_backend.py
  -> src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend.py
```

### Phase 2: runtime command group 追加

- `cli/parser.py`
- `cli/registry.py`
- `commands/authoring.py`
- `application/authoring_pack/**`
- `domain/authoring_pack/**`
- `presentation/authoring_pack/**`

を追加・更新する。

### Phase 3: installed wrapper 追加

- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py`
- wrapper は runtime module を呼ぶだけにする。
- primary は `./spec-dock/scripts/spec-dock authoring ...` と明記する。

### Phase 4: docs / skills shipping

- shipped docs を追加する。
- `spec-dock-authoring-pack` skill を追加する。
- `_MANAGED_SKILL_NAMES` に追加する。
- README の installed assets 説明を更新する。

### Phase 5: tests

最低限必要な test:

- `spec-dock init` 後に runtime command が存在する。
- `spec-dock update` 後に `spec-dock/scripts/authoring-pack/*.py` が導入先へ入る。
- `.agents/skills/spec-dock-authoring-pack/SKILL.md` が導入先へ入る。
- `./spec-dock/scripts/spec-dock authoring --help` が通る。
- `authoring pack prepare --help` が通る。
- `authoring backend invoke --dry-run` が通る。
- backend 未設定は fail-closed する。
- `SPECDOCK_CHATGPT_COMMAND` は shell injection されない。
- review safety の既存 manual tests を runtime command 経由へ移植する。
- wrapper と runtime command の JSON status / exit code が一致する。

## 8. 退ける案

### root `scripts/authoring-pack/` のままにする

今回の欠陥を解決しない。導入先に配布されない。

### `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` に丸ごとコピーして終わり

短期移行としては許容できるが、正本にすると runtime command と分断される。help / registry / tests / workflow docs が drift しやすい。

### installer CLI `src/spec_dock/cli.py` に authoring-pack command を入れる

installer CLI は `init/update/uninstall` の責務であり、day-to-day workflow は repo-local runtime が担当する設計である。authoring-pack は target repo state / artifacts / assurance / source hash を扱うので runtime 側に置くべき。

### docs / skill だけ shipped する

実行可能な tool が導入先に存在しないため不十分。

### backend を Oracle 固定にする

個人環境依存になる。SpecDock は backend command contract だけを定義し、実体は利用者が設定する。

## 9. 実装判断

次の Epic / Issue では、単に workflow docs を更新するだけでなく、今回の scripts を installed runtime surface へ移すことを最優先にするべきである。

最小実装の推奨順:

1. `authoring-pack` runtime command group の設計
2. existing scripts のロジックを runtime modules へ移植
3. installed thin wrappers を追加
4. shipped docs / skill を追加
5. init/update packaging tests
6. runtime CLI tests
7. existing manual tests の runtime command parity

この順なら、SpecDock の architecture と provider/consumer 境界を守りながら、ChatGPT authoring workflow を実際に導入先 product repo で使える形にできる。

## 10. ChatGPT-Use 実行メモ

- 実行 slug: `specdock-authoring-pack-install-architectu`
- Model evidence: `gpt-5.5-pro`, Pro Extended
- Prompt estimate: 約 253,598 tokens
- 添付: 37 files
- 実行時間: 約 11 分
- 未検証: patch 適用、test suite、runtime command 実行、installer packaging は未実施
