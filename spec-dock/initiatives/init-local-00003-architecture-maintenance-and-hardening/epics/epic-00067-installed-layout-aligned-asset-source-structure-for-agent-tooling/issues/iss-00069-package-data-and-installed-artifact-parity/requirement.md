---
種別: 要件定義書（Issue）
ID: "iss-00069"
タイトル: "Package data and installed artifact parity"
関連GitHub: ["#69"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
親: ["epic-00067", "init-local-00003"]
---

# iss-00069 Package data and installed artifact parity — 要件定義（WHAT / WHY）

## 目的
- `install_root/` 配下の hidden directories、dotfiles、workflow files、native shims を build artifact に欠落なく含め、local checkout と package-installed `spec-dock` の asset discovery が同じ結果を返す状態を作る。
- `iss-00068` で導入した install-shaped source tree を、「repo に存在するだけ」ではなく「配布物として成立している」状態へ引き上げる。

## 背景・現状
- 現状の挙動:
  - `pyproject.toml` の package-data は `assets/**/*` と `.gitignore` の例外だけを明示している。
  - `setup.py` は stale build output の除去は行うが、`install_root` 用の hidden path inclusion を明示していない。
  - 既存テストは `codex_skills` 配下の bundled assets を前提にしており、`install_root/.agents`、`.codex`、`.github`、`.github/workflows` の package artifact inclusion を検証していない。
- 現状の課題:
  - Python の glob / packaging semantics では dot-directory / dotfile が想定どおりに拾われないことがあり、`install_root/.agents/...` や `install_root/.github/...` が wheel / sdist から欠落するリスクがある。
  - source tree に `install_root` があっても、配布物に入らなければ `uvx --from . spec-dock ...` や package-installed 実行では再現できない。
  - local checkout と installed package で見える asset set がずれると、後続 issue の installer cutover 検証が不安定になる。
- 再現手順:
  1. 現行の package-data / build 設定を確認する。
  2. bundled asset tests が `codex_skills` 前提であることを確認する。
- 観測点:
  - Build artifact:
    - wheel
    - sdist
  - Filesystem:
    - `src/spec_dock/assets/install_root/`
  - Tests:
    - `tests/test_init_update.py`
- 情報源:
  - `pyproject.toml`
  - `setup.py`
  - `tests/test_init_update.py`
  - `epic-00067` の requirement / design / plan
  - `iss-00068` の requirement / design

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `uvx --from . spec-dock ...` や package-installed `spec-dock` を使う maintainer / contributor
  - build artifact を通じて `spec-dock` を検証する CI / release フロー
- 代表シナリオ:
  - maintainer が wheel / sdist を作り、その配布物から `spec-dock` を実行しても `install_root` assets が欠落しない。
  - local checkout で見える `install_root` assets と、installed package の `importlib.resources` で見える assets が一致する。

## スコープ
- MUST:
  - `src/spec_dock/assets/install_root/` 配下の in-scope assets が wheel / sdist / local package install に含まれるよう packaging contract を定義する。
  - dot-directory、dotfile、workflow file、native shim を含む representative asset set を built artifact content check の対象にする。
  - package-installed `spec-dock` から `install_root` assets が resource discovery できることを smoke / regression として観測可能にする。
  - local checkout と package-installed artifact の asset inventory parity を検証する。
- MUST NOT:
  - managed ownership / obsolete path cleanup 契約を変更しない。
  - install target path や tree classification を再定義しない。
  - Claude Code 用 asset を追加しない。
  - package-installed `init/update` の consumer repo 反映結果をこの issue の acceptance に含めない。
- OUT OF SCOPE:
  - installer の canonical source discovery を `install_root` へ切り替える本実装
  - `.agents` / `.codex` / `.github` への managed sync ルール変更
  - legacy `codex_skills` authority の最終 retire
  - workflow sync semantics の変更

## 境界
- Always:
  - `iss-00069` は distribution / package artifact parity だけを閉じる。
  - source tree foundation は `iss-00068` の contract を前提にする。
- Ask:
  - どの asset を representative artifact check に含めるべきか判断が割れる場合だけ、coverage 範囲を調整する。
- Never:
  - packaging inclusion の不足を「local checkout では動くから」で許容しない。
  - `iss-00069` の中で managed ownership や installer cleanup を先回りで変更しない。

## 非交渉制約
- この issue は `epic-00067` の E-RQ-009 に対する package inclusion / installed discovery prerequisite を担当する。
- `E-RQ-009` のうち package-installed `init/update` が `install_root` を canonical source root として解決する最終 closure は `iss-00070` の cutover で閉じる前提とする。
- `E-AC-006` については、この issue は package inclusion / installed discovery parity を担当し、consumer repo への authoritative reflection は `iss-00070` の cutover で閉じる前提とする。
- build artifact parity は wheel / sdist / local package install の 3 系統で考える。
- `local package install` は、locally built wheel から isolated temporary environment へ行う non-editable install を指す。editable install や source-linked install は禁止する。
- installed smoke / parity 実行時は repo checkout を `PYTHONPATH` や current working directory から参照できない isolated execution にする。
- artifact 観測の canonical path basis は `spec_dock/assets/...` とする。
- wrapper-era legacy paths も archive member / installed resource 上の実在 namespace に合わせて `spec_dock/assets/...` basis へ正規化する。旧 workflow path は歴史的に `spec_dock/assets/github/...` を使うものとしてそのまま扱う。
- source tree path は `src/` prefix を除き、`spec_dock/assets/...` へ写像して artifact-relative string に正規化する。wheel / sdist archive members と installed resource listings も同じ artifact-relative string に正規化して比較する。
- normalization rule:
  - source tree file: `src/spec_dock/...` から先頭の `src/` を除いた path を canonical artifact-relative string とする。
  - wheel member: archive member 中の先頭 `spec_dock/` から始まる部分を canonical artifact-relative string とする。
  - sdist member: top-level distribution directory を除去した後、先頭 `src/` を除いた `spec_dock/...` を canonical artifact-relative string とする。
  - installed resource: installed package root `.../site-packages/spec_dock/` からの相対 path に `spec_dock/` を前置したものを canonical artifact-relative string とする。
  - installed inventory: installed package 内の `spec_dock/assets/install_root/` 配下を再帰走査した file-only 集合を artifact-relative string へ正規化して比較する。
  - separator normalization: canonical artifact-relative string 比較は常に `/` 区切りで行う。
  - pattern normalization: stale exclusion set と seeded stale-output fixture set の pattern match も、正規化済み `/` artifact-relative strings に対して行う。
  - matcher semantics: pattern match は `pathlib.PurePosixPath.match` 相当の `*` / `**` semantics を前提にする。
- `install_root` の representative artifact set は次の exact artifact-relative paths とする。
  - `spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `spec_dock/assets/install_root/.agents/skills/spec-dock-codex-adapter/SKILL.md`
  - `spec_dock/assets/install_root/.agents/skills/spec-dock-copilot-adapter/SKILL.md`
  - `spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `spec_dock/assets/install_root/.codex/agents/spec-dock.toml`
  - `spec_dock/assets/install_root/.github/agents/spec-dock.agent.md`
  - `spec_dock/assets/install_root/.github/workflows/ci.yml`
- issue-70 handoff の重点 installed-discovery surface は次の 3 件とする。
  - `spec_dock/assets/install_root/.agents/host-adapters/meta.json`
  - `spec_dock/assets/install_root/.codex/agents/spec-dock.toml`
  - `spec_dock/assets/install_root/.github/agents/spec-dock.agent.md`
- handoff representative coverage は issue-70 handoff に必要な canonical install_root surface を検証対象とする。`codex_skills/native-shims/*` の legacy packaged source はこの issue の representative coverage 対象ではなく、issue-70 cutover 前の transitional compatibility surface として別扱いにする。
- local checkout と installed package で asset discovery の結果がずれたら fail とする。
- full install_root inventory は `src/spec_dock/assets/install_root/` 配下の全 file を `spec_dock/assets/install_root/...` へ正規化した artifact-relative inventory とする。
- wrapper-era stale exclusion set は次の exact artifact-relative patterns とする。
  - `spec_dock/assets/spec_dock/scripts/spec-dock-close*.sh`
  - `spec_dock/assets/github/workflows/spec-dock-close.yml`
  - `spec_dock/assets/spec_dock/templates/**/current/**`
  - `spec_dock/assets/spec_dock/templates/**/completed/**`
  - `spec_dock/assets/spec_dock/templates/adr.md`
  - `spec_dock/assets/spec_dock/templates/**/discussions/rules.md`
  - `spec_dock/assets/spec_dock/templates/issue/discussions/_template.md`
  - `spec_dock/assets/spec_dock/templates/initiative/epics/new-epic`
  - `spec_dock/assets/spec_dock/templates/epic/issues/new-issue`
  - `spec_dock/assets/spec_dock/templates/*/**/README.md`
  - `spec_dock/assets/spec_dock/templates/design.md`
  - `spec_dock/assets/spec_dock/templates/plan.md`
  - `spec_dock/assets/spec_dock/templates/report.md`
  - `spec_dock/assets/spec_dock/templates/requirement.md`
- seeded stale-output fixture set は build staging area の artifact-relative namespace に次の exact stale paths を作ることで観測する。
  - `spec_dock/assets/spec_dock/scripts/spec-dock-close-smoke.sh`
  - `spec_dock/assets/github/workflows/spec-dock-close.yml`
  - `spec_dock/assets/spec_dock/templates/initiative/current/stale.md`
  - `spec_dock/assets/spec_dock/templates/initiative/completed/stale.md`
  - `spec_dock/assets/spec_dock/templates/adr.md`
  - `spec_dock/assets/spec_dock/templates/issue/discussions/rules.md`
  - `spec_dock/assets/spec_dock/templates/issue/discussions/_template.md`
  - `spec_dock/assets/spec_dock/templates/initiative/epics/new-epic`
  - `spec_dock/assets/spec_dock/templates/epic/issues/new-issue`
  - `spec_dock/assets/spec_dock/templates/issue/legacy/README.md`
  - `spec_dock/assets/spec_dock/templates/design.md`
  - `spec_dock/assets/spec_dock/templates/plan.md`
  - `spec_dock/assets/spec_dock/templates/report.md`
  - `spec_dock/assets/spec_dock/templates/requirement.md`
- wheel stale-fixture precondition は `build_py.run` 後かつ `_prune_stale_build_outputs()` 実行前の `build_lib/spec_dock/assets/...` staging area に、seeded stale-output fixture set の exact paths が存在することとする。
- sdist stale-fixture precondition は temporary source build context の `src/spec_dock/assets/...` namespace に、seeded stale-output fixture set と同じ relative stale paths を source-tree relative path で注入し、sdist build 開始前にその全件が存在することとする。

## 前提
- `iss-00068` により `install_root/` と in-scope asset inventory が定義済みである。
- 現行 installer / tests は `codex_skills` 依存をまだ持ちうるため、本 issue では distribution parity を先に固める。
- `_assets_dir()` は installed package の resource root を返す入口として使える。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - wheel / sdist / local package install 用の build artifact を作成する
  - When:
    - packaged contents を inspection する
  - Then:
    - full install_root inventory の全 file が wheel と sdist に欠落なく含まれている
    - local package install でも site-packages 配下の installed resources から full install_root inventory と同じ paths が確認できる
    - representative artifact set は full install_root inventory check の明示サンプルとしても成立する
  - 観測点:
    - full inventory artifact content check
    - wheel / sdist file listing
    - installed site-packages resource listing
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - local checkout と package-installed `spec-dock` の両方を使える
  - When:
    - asset discovery を比較する
  - Then:
    - `install_root` 配下の representative artifact set について、local checkout と installed package が同じ asset inventory を返す
    - isolated non-editable wheel install から `spec-dock init <tmp-repo>` と `spec-dock update <tmp-repo>` を実行しても missing asset error が発生しない
    - installed smoke / parity 実行時に checkout fallback を使わず、site-packages 由来の installed resources だけで観測できる
    - 上記 isolated env では package-installed command が参照できる provider-side assets は site-packages 内 package data だけであり、`init/update` の asset resolution は installed package 由来である
    - package-installed `init/update` smoke の成功だけでは AC-002 を満たしたことにしない。pass には、同じ isolated env で `install_root` representative/handoff surface の installed discovery assertion が併せて成功することが必要である
    - issue-70 handoff の重点 installed-discovery surface として `spec_dock/assets/install_root/.agents/host-adapters/meta.json`、`spec_dock/assets/install_root/.codex/agents/spec-dock.toml`、`spec_dock/assets/install_root/.github/agents/spec-dock.agent.md` の installed discovery が確認できる
    - legacy `codex_skills` package data だけで `init/update` が起動できても、上記 `install_root` installed discovery assertion が欠ける場合は fail とする
    - consumer repo への authoritative reflection 成否はこの issue の acceptance 対象外である
  - 観測点:
    - local vs installed discovery parity check
    - package-installed `init/update` smoke
    - installed handoff-surface assertion

- AC-003:
  - Actor:
    - CI
  - Given:
    - local checkout に full install_root inventory が存在する
    - wheel / sdist / local package install を利用できる
  - When:
    - local checkout と installed package の asset inventory を比較する
  - Then:
    - artifact-relative full install_root inventory の全 file が wheel / sdist / installed package の 3 系統すべてで発見できる
    - local checkout から正規化した full install_root inventory と installed package から取得した full inventory は完全一致する
    - full inventory parity check も checkout fallback を使わず、site-packages 由来の installed resources だけで観測される
    - `iss-00070` へ渡す前提として、artifact inclusion と installed discovery parity は full inventory で満たされている
  - 観測点:
    - artifact-relative full inventory parity check
    - installed package resource listing

- AC-004:
  - Actor:
    - CI
  - Given:
    - package data inclusion と stale build output guard を検証する
  - When:
    - stale build output fixture を含む build artifact regression を実行する
  - Then:
    - representative artifact set は built artifacts に含まれる
    - wrapper-era stale exclusion set の paths は built artifacts に含まれない
    - seeded stale-output fixture set の各 path は build staging area では存在し、wheel / sdist listing では 0 件である
    - wheel は `build_lib/spec_dock/assets/...` staging area、sdist は temporary source build context の `src/spec_dock/assets/...` namespace で seeded stale-output fixture set の事前存在が確認できる
    - stale build output fixture によって exclusion guard が実際に効いていることを pass/fail 判定できる
    - inclusion と exclusion の両方が同じ regression suite で pass/fail 判定できる
  - 観測点:
    - artifact inclusion regression tests
    - stale build output exclusion regression tests

## 例外・エッジケース
- EC-001:
  - 条件:
    - dot-directory や dotfile を含む path を package data に含める
  - 期待:
    - `assets/**/*` のような単純 glob に依存せず、hidden path も built artifact に入る
  - 観測点:
    - built artifact listing
- EC-002:
  - 条件:
    - stale build output exclusion が有効なまま `install_root` assets を追加する
  - 期待:
    - 削除済み wrapper-era assets は引き続き除外される一方、`install_root` current assets は誤除外されない
  - 観測点:
    - package-data / exclude-package-data regression tests

- EC-003:
  - 条件:
    - package-installed 実行では current installer がまだ legacy root 参照を持つ
  - 期待:
    - 本 issue では distribution parity と installed discovery parity を保証し、consumer repo への authoritative reflection は `iss-00070` に委ねる
    - ただし installed package 内で `install_root` assets 自体は discovery 可能でなければならない
  - 観測点:
    - installed package resource discovery check

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - built wheel を展開する
  - Output:
    - `spec_dock/assets/install_root/.github/workflows/ci.yml` が wheel 内に存在する

- EX-002:
  - Input:
    - installed package の `_assets_dir()` から asset root を得る
  - Output:
    - `assets_dir / "install_root" / ".codex" / "agents" / "spec-dock.toml"` が解決できる

## 用語（ドメイン語彙）
- TERM-001:
  - package artifact parity:
    - local checkout と installed package で見える asset set が一致している状態
- TERM-002:
  - representative artifact set:
    - package inclusion を監査するための最小代表 asset 集合
- TERM-003:
  - package-installed smoke:
    - installed package 経由で `spec-dock` を実行し、asset 欠落が起きないことを確認する軽量検証
- TERM-004:
  - full install_root inventory:
    - `src/spec_dock/assets/install_root/` 配下の全 file 集合

## 未確定事項
- downstream handoff:
  - `iss-00070` が `install_root` を installer の canonical source discovery へ切り替え、package-installed `init/update` が consumer repo へ authoritative reflection する責務を持つ。
  - `iss-00069` の acceptance は artifact inclusion と installed discovery parity までとし、consumer repo reflection は handoff の外に置く。
