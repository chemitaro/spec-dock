---
種別: 要件定義書（Issue）
ID: "iss-00070"
タイトル: "Installer source discovery and managed ownership"
関連GitHub: ["#70"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-12"
親: ["epic-00067", "init-local-00003"]
---

# iss-00070 Installer source discovery and managed ownership — 要件定義（WHAT / WHY）

## 目的
- installer が agent-tooling assets の canonical source を `install_root/` として解決し、current managed file set と explicit obsolete managed path set の境界を一意に扱える状態を作る。
- package-installed surface で確認済みの `install_root` assets を、consumer repo への actual init/update reflection に接続する。

## 背景・現状
- 現状の挙動:
  - `_build_managed_skill_install_plan()` と `_apply_managed_skill_install_plan()` は `assets_dir / "codex_skills"` 配下を正本として読んでいる。
  - host adapter metadata の `source_of_truth_asset` も `codex_skills/native-shims/...` を指している。
  - cleanup は managed skills と native shim obsolete paths だけを対象にし、workflow は current managed set に含めていない。
- 現状の課題:
  - `iss-00068` で authority を `install_root` へ移しても、installer が legacy root を読んでいる限り actual install/update の source of truth が一致しない。
  - workflow files が current managed set に含まれないため、`.github/workflows/ci.yml` の sync / refresh / ownership が contract 化されていない。
  - current managed file set と explicit obsolete managed path set の境界が複数箇所に分散しており、cleanup safety が読みづらい。
- 再現手順:
  1. `src/spec_dock/cli.py` の managed skill install plan を確認する。
  2. `host-adapters/meta.json` の `source_of_truth_asset` と current installed target を見比べる。
- 観測点:
  - Filesystem:
    - `src/spec_dock/assets/install_root/`
    - `src/spec_dock/assets/codex_skills/`
    - target repo の `.agents/`, `.codex/`, `.github/`, `.github/workflows/`
  - Tests:
    - `tests/test_init_update.py`
- 情報源:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/codex_skills/host-adapters/meta.json`
  - `iss-00068` docs
  - `iss-00069` docs
  - `epic-00067` requirement / design / plan

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock init/update` を実行する maintainer / contributor
  - managed ownership / cleanup の安全性を監査する reviewer
- 代表シナリオ:
  - maintainer が `install_root` 配下 assets を更新し、`spec-dock update` で同じ relative path のまま consumer repo へ反映する。
  - updater が obsolete managed native shim path や workflow を整理しても、managed 外 user-authored file は削除されない。

## スコープ
- MUST:
  - installer の source discovery を `install_root/` authoritative surface に切り替える。
  - host adapter metadata の `source_of_truth_asset` を `install_root` 基準へ更新する。
  - current managed file set を `install_root` 実在 tree から導出する。
  - explicit obsolete managed file path set を `.agents/host-adapters/meta.json` の top-level `managed_assets.obsolete_exact_file_paths` field で保持し、cleanup はその集合に限定する。
  - `.github/workflows/` を current managed file set に含め、init/update で sync される対象にする。
  - current managed path に対する exact-path ownership conflict の扱いを固定する。
  - source-side move / deletion によって current managed target path が消える change を、同じ change で obsolete managed file path への昇格または ownership 引継ぎまで含めて完結させる。
  - managed 外 user-authored file を delete/prune しないことを acceptance で固定する。
- MUST NOT:
  - package inclusion / artifact parity 自体をここで再設計しない。
  - consumer repo install target path を rename しない。
- OUT OF SCOPE:
  - wheel / sdist / installed package parity regression の主契約
  - dogfooding checked-in state の最終同期
  - init/update parity の exhaustive matrix 検証
  - final authority retirement review

## 境界
- Always:
  - `iss-00070` は installer cutover と managed ownership boundary だけを閉じる。
  - current managed set は `install_root` tree、obsolete managed set は `.agents/host-adapters/meta.json` に明示された exact file path から決まる。
  - current managed set と obsolete managed set は disjoint でなければならず、同一 target path を同時に共有しない。
  - path が current managed set に含まれる限り、その exact target path は spec-dock managed path とみなし、update は canonical source asset で上書きする。
  - current managed path を source tree から外す change は、同じ change でその target path を explicit obsolete managed file path set へ追加するか、別の current managed asset で同じ target path を引き続き所有する形にしなければならない。
  - obsolete managed exact file path は、一括切替と同時に有効になる cleanup contract であり、旧 managed filename を update 時に掃除するための spec-dock-owned prune 対象とする。
  - same change とは provider-side source tree と manifest を同時に更新する同一 source revision / 同一 PR を指し、その完全性は provider-side validation / CI regression で判定する。
- Ask:
  - managed path に含めるか user-authored path に残すか判断できない新 path がある場合だけ確認する。
- Never:
  - `install_root` tree に存在しない current path を current managed set に含めない。
  - directory path や glob のような広い指定を obsolete managed cleanup の対象にしない。
  - manifest 未定義 path を obsolete managed cleanup の対象にしない。
  - current managed set へ昇格した exact target path を user-authored preserve 対象として扱わない。
  - explicit obsolete managed file path set に含まれる exact target path を user-authored preserve 対象として扱わない。
  - current managed set と obsolete managed set の overlap を許したまま sync/cleanup を進めない。
  - user-authored custom agent file / workflow を spec-dock managed と誤認して削除しない。
  - epic の「user-authored files は prune しない」という保証を、current managed set または explicit obsolete managed file path set に含まれる exact target path へ拡張解釈しない。

## 非交渉制約
- `epic-00067` の E-RQ-003、E-RQ-004、E-RQ-005、E-RQ-007 をこの issue の primary closure target とする。
- `iss-00070` は E-AC-002 / E-AC-003 を閉じる issue ではなく、その中核になる installer ownership contract と fail-closed boundary を固定して、後続の final verification tranche が consume できる handoff evidence を残す tranche とする。
- `iss-00069` が閉じた配布面の package parity / installed discovery contract は維持し、この issue はその isolated installed surface を消費して cutover 後の authoritative reflection が checkout fallback なしで成立することだけを追加で証明する。これは `E-RQ-009` / `E-AC-006` の owner 再割当ではなく、issue-69 handoff を使った issue-local acceptance とする。
- current managed file set の canonical source は `src/spec_dock/assets/install_root/` 実在 tree である。
- legacy `codex_skills` はこの issue の runtime cutover で installer/build/runtime authority を失い、installer は `install_root` だけを canonical source として扱う。
- legacy duplicate files 自体は issue-70 完了時点で installer source discovery と managed-ownership runtime から参照されない inert non-authoritative copy でなければならない。physical deletion、docs/test cleanup、source tree final cleanup だけを issue-72 の cleanup tranche に残す。
- `iss-00068` の temporary coexistence contract に含まれる legacy parity mirror 必須条件は、この issue の cutover 完了時点で installer/runtime contract に対しては superseded とする。issue-70 完了後は byte-equivalent mirror 維持を要求しない。
- obsolete managed file path は `.agents/host-adapters/meta.json` の top-level `managed_assets.obsolete_exact_file_paths` に定義された normalized posix exact target file だけを cleanup 対象にする。
- `.agents/host-adapters/meta.json` は native shim だけでなく obsolete workflow path を含む shared cleanup manifest の正本である。
- `.agents/host-adapters/meta.json` の top-level `managed_assets.obsolete_exact_file_paths` は shared skills、shared metadata、native shim、workflow の obsolete exact path を単一配列で保持する。
- required host とは source-of-truth `.agents/host-adapters/meta.json` の `targets` 配下で `enabled: true` を持つ host entry を指す。issue-70 の in-scope required host は `codex` と `copilot` である。
- `managed_assets.obsolete_exact_file_paths` は string array とし、各 entry は normalized posix exact path、重複禁止、current managed set との overlap 禁止、許可 namespace を `.agents/skills/`、`.agents/host-adapters/`、`.codex/agents/`、`.github/agents/`、`.github/workflows/` の 5 つに限定して validation される。
- `source_of_truth_asset` は cutover 後も native shim source resolution の authoritative field として runtime が参照し、required host では `install_root` relative path でなければ fail-closed とする。
- workflow current managed path は `install_root/.github/workflows/...` 実在 file に対応するものだけを含める。
- exact target path が current managed set に含まれる場合、その path の ownership は spec-dock が持ち、pre-existing file の由来にかかわらず update で canonical asset に置換される。
- source-side move / deletion によって current managed target path が消える change は、同じ change set で explicit obsolete managed file path set への昇格、または別 current managed asset への ownership 引継ぎを伴わなければならない。
- current managed set と obsolete managed set が overlap した場合、installer は sync/cleanup 前に fail しなければならない。
- consumer repo runtime が fail-closed で拒否すべき invalid manifest 条件は、source-of-truth `.agents/host-adapters/meta.json` file missing、`managed_assets` container missing / null / wrong-type、`obsolete_exact_file_paths` missing / null / wrong-type、blank / non-string path、absolute path、`..` を含む path、directory path、glob pattern、managed namespace 外 path、duplicate obsolete path、current managed set との overlap、required host の `source_of_truth_asset` missing / wrong-type / non-install_root path / provider-side non-file target とする。
- obsolete-path cleanup は source-of-truth manifest validation が通り、current managed file set の sync が全件成功した後にだけ実行してよい。
- consumer repo runtime は target repo 既存の pre-cutover `meta.json` を validation 入力にせず、provider-side source-of-truth から同期する `.agents/host-adapters/meta.json` だけを validation 入力にする。
- consumer repo runtime は provider-side source-of-truth manifest file を target repo へ書き込む前に、その内容を in-memory で validation し、invalid な場合は target repo への write を一切行わない。
- issue-70 の handoff evidence は issue report の `handoff-validation-evidence` section に残し、最低でも source inventory / manifest assertions、invalid manifest negative test coverage、current managed / obsolete managed boundary assertions を machine-readable なコマンド出力要約付きで記録できなければならない。
- target repo 側で current managed file path または obsolete exact file path と directory/container が衝突する場合、runtime は fail-closed で停止し、sync/cleanup を一切進めない。

## 前提
- `iss-00068` で `install_root` authority と asset classification が確定している。
- `iss-00069` で package inclusion / installed discovery parity が通っている。
- legacy `codex_skills` 実体が source tree に残っていても installer authority は持たず、この issue の cutover で参照対象から外れる。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - `install_root` に canonical assets があり、empty repo へ `spec-dock init` する場合と既存 repo へ `spec-dock update` する場合がある
  - When:
    - installer が managed skill / native shim / workflow sync plan を構築する
  - Then:
    - current managed file set は `install_root` 実在 tree から導出される
    - `.agents`, `.codex`, `.github`, `.github/workflows` の current files は source tree と同じ relative path で init/update の両方に反映される
  - 観測点:
    - init contract test
    - update contract test
    - target filesystem assertions
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - target repo に obsolete managed path、current managed path と衝突する pre-existing file、user-authored custom path が混在している
  - When:
    - `spec-dock update` を実行する
  - Then:
    - current managed path に一致する pre-existing file は canonical source asset で置換される
    - manifest に明示された obsolete managed exact file paths だけが prune される
    - obsolete managed exact file path に存在する file は user edit の有無にかかわらず prune 対象のままである
    - current managed set / explicit obsolete managed file path set のどちらにも含まれない user-authored custom agent / workflow / skill だけが保持される
    - current managed file set の sync が一部でも失敗した場合は obsolete-path cleanup が実行されない
  - 観測点:
    - cleanup safety regression
    - before/after filesystem assertions

- AC-003:
  - Actor:
    - reviewer
  - Given:
    - host adapter metadata と installer source discovery 実装を確認する
  - When:
    - canonical source root と managed boundary を review する
  - Then:
    - `source_of_truth_asset` は `install_root` 基準である
    - installer は `install_root` を current authority として読む
    - `.agents/host-adapters/meta.json` の top-level `managed_assets.obsolete_exact_file_paths` が obsolete native shim path と obsolete workflow path を含む shared cleanup manifest の正本であり、tree の第二正本にはならない
    - source-side move / deletion によって current managed target path を source tree から外すときは、同じ change で obsolete file path への昇格または ownership 引継ぎが必要だと確認できる
    - current managed set と obsolete managed set が overlap した場合、および invalid manifest 条件に該当した場合は fail-closed になると確認できる
    - runtime manifest validation は target repo 既存 file ではなく、source-of-truth manifest content を in-memory で行った後にだけ sync が始まると確認できる
  - 観測点:
    - `src/spec_dock/cli.py`
    - `.agents/host-adapters/meta.json`
    - runtime invalid manifest negative tests
    - machine-readable validation evidence

- AC-004:
  - Actor:
    - maintainer
  - Given:
    - source-side move / deletion によって current managed target path が source tree から消える change を用意する
  - When:
    - provider-side validation / CI regression を `tests/test_init_update.py` ベースで実行する
  - Then:
    - 旧 target path が同じ change で explicit obsolete managed file path set に昇格しているか、別 current managed asset に ownership が引き継がれていない限り、その change は契約違反として失敗する
    - current managed set と obsolete managed set が overlap する change も契約違反として失敗する
    - remove / rename が正しく昇格または引継ぎされている場合だけ update 後に旧 target path cleanup が成立する
  - 観測点:
    - `python -m unittest tests.test_init_update`
    - transition regression
    - source inventory / manifest comparison

- AC-005:
  - Actor:
    - maintainer
  - Given:
    - source-of-truth `.agents/host-adapters/meta.json` file missing、`managed_assets` container missing / null / wrong-type、`obsolete_exact_file_paths` missing / null / wrong-type、blank / non-string path、absolute path、`..` を含む path、directory path、glob pattern、managed namespace 外 path、duplicate obsolete path、current managed set と overlap する path、required host の `source_of_truth_asset` missing / wrong-type / non-install_root path / provider-side non-file target、target repo 側 directory/container conflict をそれぞれ注入した malformed fixture を用意する
  - When:
    - `spec-dock init` / `spec-dock update` の runtime contract test を実行する
  - Then:
    - 各 invalid manifest 条件は fail-closed で拒否され、sync/cleanup は一切進まない
    - 許可 namespace 以外の obsolete exact path は fail-closed で拒否される
    - target repo への `meta.json` write を含む managed file mutation は一切発生しない
    - target repo 側 directory/container conflict も preflight で検出され、write/cleanup は一切行われない
  - 観測点:
    - malformed manifest negative tests
    - no-mutation filesystem assertion

- AC-006:
  - Actor:
    - maintainer
  - Given:
    - `install_root` authoritative asset と legacy `codex_skills` duplicate の内容が意図的に食い違う fixture を duplicate class ごとに用意する
  - When:
    - `spec-dock init` / `spec-dock update` を実行する
  - Then:
    - shared skill duplicate、shared metadata duplicate、native shim duplicate の各 class について、target repo には `install_root` authoritative asset の内容だけが反映される
    - stale legacy duplicate content は runtime source discovery で一切参照されない
  - 観測点:
    - class-complete stale legacy divergence regression
    - target filesystem assertion

- AC-007:
  - Actor:
    - maintainer
  - Given:
    - `iss-00069` で確立した isolated non-editable installed package 環境があり、source-of-truth manifest と `install_root` assets は issue-70 cutover 後の contract に更新されている
  - When:
    - package-installed `spec-dock init` / `spec-dock update` を実行する
  - Then:
    - package-installed runtime でも current managed file set は `install_root` authoritative surface から導出される
    - consumer repo には `.agents`、`.codex`、`.github`、`.github/workflows` の current managed files が canonical relative path のまま反映される
    - obsolete managed exact file paths だけが cleanup 対象になり、managed 外 user-authored path は保持される
    - checkout fallback や legacy `codex_skills` source discovery に依存せず、installed package だけで cutover 後の authoritative reflection が成立する
  - 観測点:
    - isolated package-installed init/update cutover regression
    - target filesystem assertion

## 例外・エッジケース
- EC-001:
  - 条件:
    - `install_root` に workflow file が追加されるか、source-side move / deletion によって workflow target path が消える
  - 期待:
    - current managed file set は tree 差分に追従する
    - workflow target path が消える change では、旧 target path が同じ change で explicit obsolete managed file path set に追加されるか、別 current managed asset へ ownership が引き継がれる
    - obsolete cleanup は上記昇格後の manifest 定義 path だけを削除対象にする
  - 観測点:
    - workflow sync regression
- EC-002:
  - 条件:
    - custom user file が managed namespace 配下に存在し、その path が current managed set と衝突する場合としない場合がある
  - 期待:
    - current managed path と一致する file は canonical source asset で置換される
    - current managed set / explicit obsolete managed file path set のどちらにも含まれない file は削除されない
  - 観測点:
    - custom file preservation test

- EC-003:
  - 条件:
    - legacy `codex_skills` copy が残っている
  - 期待:
    - installer authority は `install_root` を読む
    - legacy copy の存在や内容差分だけでは current managed set を決めない
    - legacy copy が stale content を持っていても target repo へ反映されない
  - 観測点:
    - source discovery assertion
    - patched asset root regression
    - stale legacy divergence regression

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `src/spec_dock/assets/install_root/.github/workflows/ci.yml` が存在する状態で `spec-dock update` を実行する
  - Output:
    - target repo の `.github/workflows/ci.yml` が managed file として更新される

- EX-002:
  - Input:
    - target repo に `.codex/agents/spec-dock-codex-adapter.toml` と `.codex/agents/custom-reviewer.toml` が共存している
  - Output:
    - obsolete managed file path の前者だけが削除され、custom file の後者は保持される

- EX-003:
  - Input:
    - source-of-truth manifest の `managed_assets.obsolete_exact_file_paths` に `.agents/skills/spec-dock-codex-adapter/SKILL.md` が含まれている
  - Output:
    - shared skill obsolete path も同じ shared cleanup manifest 契約で prune 対象として扱われる

## 用語（ドメイン語彙）
- TERM-001:
  - current managed file set:
    - `install_root` 実在 tree から導出される、update ごとに同期される managed files
- TERM-002:
  - explicit obsolete managed file path set:
    - `.agents/host-adapters/meta.json` に明示され、cleanup でのみ削除対象になる exact target file path 集合
- TERM-003:
  - cleanup safety:
    - obsolete managed file paths は削除するが、current managed set と explicit obsolete managed file path set のどちらにも含まれない user-authored path だけを保持する性質
- TERM-006:
  - disjoint ownership invariant:
    - current managed set と explicit obsolete managed file path set が同一 target path を共有してはいけないという不変条件
- TERM-004:
  - exact-path ownership conflict:
    - pre-existing file がある target path を current managed set が所有するとき、その path は spec-dock managed として canonical asset に置換される状態
- TERM-005:
  - current-to-obsolete transition:
    - source-side move / deletion によって current managed target path が消えるとき、同じ exact target path を別 current managed asset が引き続き所有するか、explicit obsolete managed file path set へ昇格する契約
- TERM-007:
  - one-shot cutover:
    - backward compatibility や多段 migration を前提にせず、asset authority と managed ownership を一括で切り替える前提

## 未確定事項
- なし:
  - current managed set / obsolete managed set / workflow ownership / source discovery authority の分担はこの issue で固定する。
