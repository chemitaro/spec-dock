---
種別: 要件定義書（Issue）
ID: "iss-00061"
タイトル: "Dependency mutation command contract"
関連GitHub: ["#61"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
親: ["epic-00059", "init-local-00003"]
---

# iss-00061 Dependency mutation command contract — 要件定義（WHAT / WHY）

## 目的
- `deps add` / `deps remove` を runtime の正式 command contract として導入し、依存変更を手編集ではなく fail-closed な mutation path に収束させる。
- `duplicate add` と `remove not-found` の扱いを曖昧にせず、current graph validation を先行させたうえで CLI と storage の振る舞いを固定する。

## 背景・現状
- 現状の挙動:
  - runtime には `deps check` は存在するが、依存関係を更新する `deps add/remove` は未提供である。
  - `iss-00060` により read path は `.meta.json` SoT へ整列済みで、dependency 整合性の検査は read path 側に寄っている一方、mutation 実行前に current graph 自体を fail-closed に止める command contract は未定義である。
  - 現行 test には `deps check` 実行で `.meta.json` が変化しない baseline（`test_deps_commands_do_not_mutate_meta_json`）があり、mutation command 導入後も fail-closed / no-write 境界を明示的に更新する必要がある。
- 現状の課題:
  - command 不在のままでは、依存変更が JSON 直編集や ad-hoc 修正に寄りやすく、duplicate edge や not-found remove の扱いが実装者依存になる。
  - current graph が既に壊れている場合でも、duplicate add を no-op 扱いしてしまうと corruption を見逃す。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock deps check <target>` は実行できるが、依存追加・削除用 subcommand は存在しない。
  2. 依存変更を行うには保存ファイルを直接触るしかなく、validation order / response contract / atomic write が統一されない。
- 観測点:
  - CLI:
    - `deps` subtree は `check` のみ。
  - Storage:
    - dependency SoT は epic/T1 で `.meta.json` に寄せる前提。
  - Validation:
    - downstream command は dependency graph を前提に動くため、mutation path でも同じ validation を再利用する必要がある。
- 情報源:
  - epic-00059 `requirement.md`
  - epic-00059 `design.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - spec-dock runtime 利用者
  - repo maintainer / operator
- 代表シナリオ:
  - issue 間の依存 edge を追加し、同じ command で削除できることを期待する。
  - graph が壊れている repo では mutation を進めず、先に validation error を受け取りたい。

## スコープ
- MUST:
  - `deps add --from <node-id> --to <node-id>` と `deps remove --from <node-id> --to <node-id>` を追加する。
  - mutation 対象は existing issue node から existing issue node への direct edge に限定し、`from` / `to` に non-issue node を受けた場合は error に固定する。
  - duplicate add / remove existence 判定は compiled/inherited dependency ではなく、`from` node 直下 `.meta.json.depends_on` に保持された raw direct ref 基準で行う。
  - parser / handler / application / domain / infra write path / presentation に mutation contract を通す。
  - mutation 前に current graph validation を実行し、不整合時は fail-closed error で終了する。
  - mutation preflight の current graph validation は local dogfooding / import/sync と同じく dependency graph 整合性を対象とし、GitHub mandatory linkage は強制しない。
  - current graph が正常な場合だけ duplicate add を success/no-op（`result=unchanged`）とし、dependency 配列の non-dup invariant を維持する。
  - remove not-found を success/no-op に丸めず error に固定する。
  - integration test で CLI response/error contract と no-write guarantee を固定する。
  - command surface が変わるため、provider-side の dependency/operator docs 更新要否を本 issue で解決し、`src/spec_dock/assets/spec_dock/docs/reference_deps.md` を正本、`spec-dock/docs/reference_deps.md` を secondary verification として扱う。
- MUST NOT:
  - `deps.json` fallback read/write や temporary compatibility path を追加しない。
  - delete/sync/active/validate の全面的な parity work をこの issue に混ぜ込まない。
- OUT OF SCOPE:
  - hard cutover judgment、dogfooding checked-in data manual fix、T3/T4 evidence packaging。
  - dependency の新しい意味論（priority、weight、conditional edge など）。

## 境界
- Always:
  - mutation target node kind 判定、remove existence 判定、mutation/no-op 判定より先に current graph validation を行う。
  - 保存前 validation と atomic write により、失敗時は partial write を残さない。
  - 成功時の response には `from` / `to` / `result` を含め、error 時は failure reason を CLI で観測可能にする。
- Ask:
  - なし。
- Never:
  - current graph が壊れているのに duplicate add を `unchanged` success にしない。
  - remove not-found を warning や silent no-op にしない。
  - dependency 配列へ同一 edge を 2 回以上保存しない。

## 非交渉制約
- current graph validation failure を duplicate-edge 判定より優先する。
- current graph validation failure を remove existence 判定と non-issue node 判定より優先する。
- `deps add` の duplicate edge は healthy graph のときだけ `result=unchanged` の success/no-op にする。
- `deps remove` の対象 edge 不在は error に固定する。
- non-issue node を `from` / `to` に指定した場合は `unsupported_node_kind` error に固定する。
- exit status は success/no-op を `0`、mutation error を non-zero に固定し、parse error は argparse 標準に従う。

## 前提
- `iss-00060-meta-json-dependency-schema-and-reader-alignment` により `.meta.json` dependency schema と reader contract が先に固まっている。
- `iss-00060` で provider-side `reference_deps.md` 正本、dogfooding copy、`deps` / `sync` / `active` の read-side regression が `.meta.json` 契約へ追従済みである。
- upstream prerequisite の authoritative source は `iss-00060/report.md` とし、`S99 verdict: final diff review pass` と close-ready evidence をもって T1 foundation 完了とみなす。
- この issue の実装正本は provider-side shipped runtime（`src/spec_dock/assets/spec_dock/...`）であり、dogfooding runtime copy は update/sync 前に一時的に遅れていても本 issue の前提不成立とはみなさない。
- issue 対象は mutation contract に集中し、downstream parity / validate evidence / hard cutover judgment は `iss-00062` へ渡す。

## 受け入れ条件
- AC-001 add updated:
  - Actor:
    - runtime 利用者
  - Given:
    - current graph が valid で、`from` / `to` が既存 issue node を指している。
  - When:
    - `./spec-dock/scripts/spec-dock deps add --from <from-id> --to <to-id>` を実行する。
  - Then:
    - edge が追加され、`.meta.json` に 1 回だけ保存される。
    - CLI は success を返し、`result=updated` を含む。
  - 観測点:
    - command exit code、stdout、保存後 `.meta.json`、`deps check` / targeted integration test。
- AC-002 duplicate add no-op after validation:
  - Actor:
    - runtime 利用者
  - Given:
    - current graph が valid で、`from` / `to` が既存 issue node を指し、指定 direct edge が `from` node 直下 `.meta.json.depends_on` に既に存在する。
  - When:
    - 同一 `deps add` を再実行する。
  - Then:
    - current graph validation 通過後に限り success/no-op となり、CLI は `result=unchanged` を返す。
    - 保存内容は変化せず、dependency 配列の non-dup invariant を維持する。
  - 観測点:
    - command exit code、stdout、保存前後 diff、integration test。
- AC-003 remove updated:
  - Actor:
    - runtime 利用者
  - Given:
    - current graph が valid で、`from` / `to` が既存 issue node を指し、指定 direct edge が `from` node 直下 `.meta.json.depends_on` に存在する。
  - When:
    - `./spec-dock/scripts/spec-dock deps remove --from <from-id> --to <to-id>` を実行する。
  - Then:
    - edge が削除され、CLI は success を返し、`result=updated` を含む。
  - 観測点:
    - command exit code、stdout、保存後 `.meta.json`、integration test。
- AC-004 error contract:
  - Actor:
    - runtime 利用者
  - Given:
    - invalid input、unsupported node kind、または invalid graph condition がある。
  - When:
    - `deps add/remove` を実行する。
  - Then:
    - CLI は非 0 で終了し、`preflight_*` / `unsupported_node_kind` / `edge_not_found` など error kind を識別できるメッセージを stderr に返す。
    - 失敗時は保存内容が変化しない。
  - 観測点:
    - command exit code、stderr、保存前後 diff、integration test。

## 例外・エッジケース
- EC-001 current graph invalid first:
  - 条件:
    - mutation 実行前の current graph が unresolved/self/cycle/legacy mismatch などで invalid。
  - 期待:
    - duplicate add 判定、remove existence 判定、non-issue node 判定より前に fail-closed error で終了する。
    - 保存は発生しない。
  - 観測点:
    - stderr に preflight/current graph validation failure、保存前後 diff。
- EC-002 remove not-found:
  - 条件:
    - `deps remove` 対象 direct edge が `from` node 直下 `.meta.json.depends_on` に存在しない。
  - 期待:
    - inherited/compiled dependency によって target issue へ到達できる場合でも、direct ref が無ければ error で終了し、success/no-op にしない。
  - 観測点:
    - exit code 非 0、stderr の error code/message、保存前後 diff。
- EC-003 non-issue node input:
  - 条件:
    - current graph は valid だが、`from` または `to` が existing epic/initiative など non-issue node を指す。
  - 期待:
    - `unsupported_node_kind` error で終了し、edge existence 判定や mutation 判定へ進まない。
    - 保存しない。
  - 観測点:
    - exit code 非 0、stderr の error code/message、保存前後 diff。
- EC-004 invalid add request:
  - 条件:
    - `to` が未解決、`from == to`、または追加後に cycle を作る。
  - 期待:
    - error で終了し、保存しない。
  - 観測点:
    - exit code 非 0、stderr、保存前後 diff。
- EC-005 parser error:
  - 条件:
    - 必須 flag 欠落または不正 selector。
  - 期待:
    - argparse error と usage を返し、application まで進まない。
  - 観測点:
    - exit code `2`、stderr、no-write。
- EC-006 write failure atomicity:
  - 条件:
    - current graph は valid だが、`.meta.json` 更新の最終書き込みまたは置換で I/O failure が発生する。
  - 期待:
    - CLI は write failure を識別できる non-zero error で終了し、partial write や壊れた `.meta.json` を残さない。
  - 観測点:
    - 失敗注入 test、stderr の error code/message、保存前後 diff。

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - `./spec-dock/scripts/spec-dock deps add --from iss-00061 --to iss-00060`
  - Output:
    - stdout: `spec-dock: ok (deps add) from=iss-00061 to=iss-00060 result=updated`
- EX-002:
  - Input:
    - `./spec-dock/scripts/spec-dock deps add --from iss-00061 --to iss-00060`
  - Output:
    - stdout: `spec-dock: ok (deps add) from=iss-00061 to=iss-00060 result=unchanged`
- EX-003:
  - Input:
    - `./spec-dock/scripts/spec-dock deps remove --from iss-00061 --to iss-99999`
  - Output:
    - stderr: `spec-dock: error (deps remove) from=iss-00061 to=iss-99999 code=edge_not_found`

## 用語（ドメイン語彙）
- TERM-001 current graph validation:
  - mutation 対象 edge の判定前に、現在保存済み graph 全体の dependency 整合性を検証する preflight。
  - 本 issue の mutation preflight では `enforce_github_mandatory_linkage=False` を取り、GitHub linkage mandatory check はスコープ外とする。
- TERM-002 duplicate-edge non-dup invariant:
  - 同一 `from -> to` edge は current graph が正常な場合に限り `unchanged` success に収束し、storage 上で重複保存されない制約。
- TERM-003 issue-node-only mutation target:
  - `deps add/remove` の `from` / `to` は issue node id のみ受け付け、existing non-issue node は `unsupported_node_kind` error で拒否する契約。

## 未確定事項
- 現時点ではなし。
