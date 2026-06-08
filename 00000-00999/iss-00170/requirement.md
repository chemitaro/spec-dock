---
種別: 要件定義書（Issue）
ID: "iss-00170"
タイトル: "Harden Pr Monitor Stable Observation"
関連GitHub: ["#170"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
親: ["epic-00067", "init-local-00003"]
---

# iss-00170 Harden Pr Monitor Stable Observation — 要件定義（何を、なぜ行うか）

## 目的

- PR 作成後または push 後の checks / statuses / reviews 観測を、`pr-monitor` sub-agent ではなく deterministic read-only `github-pr-observation` skill / scripts に移管する。
- 推論モデルが poll ごとに sleep / timeout / quiet window / same fingerprint count を判断する構造をやめ、`wait_pr_observation.sh` が bounded polling loop を機械的に実行する契約へ置き換える。
- `github-pr-merge-preparer` が要求する merge-prepared evidence に対して、古い SHA の green、遅延 review comment、unresolved thread state 不明、wrapper failure、zero-check grace 未満を success と誤判定しない observation 基盤を作る。
- 長時間 foreground wait 中も、agent / 人間が「まだ動いている」「どの領域が進行中か」を把握できる stderr progress を出しつつ、最終判定の authority は stdout final JSON text に限定する。
- 旧 `github-codex-pr-review-comments` skill を残さず、新 `github-pr-observation` の review collector へ統合する。
- `@codex review` trigger 後に付いた review / comment 本文と CI failure detail を stdout final JSON に含め、caller agent が追加の direct GitHub API 取得へ逃げなくてよい契約にする。

## 採用済み ADR

- `20260607t085456z-adr Script Driven Pr Observation Boundary`
  - `pr-monitor` sub-agent を完全廃止する。
  - deprecated shim は残さない。
  - `github-codex-pr-review-comments` skill は削除する。
  - PR observation の正規入口は `github-pr-observation` skill / scripts とする。
  - `wait_pr_observation.sh` は stdout に final JSON text を1回だけ出す。
  - stderr progress は default `stderr-summary` として出すが、non-authoritative とする。
  - `--out` は optional debug/audit mode であり、通常 path の必須ではない。
  - `summary.md` は生成しない。

## 背景・現状

- 既存 `pr-monitor` agent は read-only monitor として定義されているが、agent instructions 内に deadline、sleep policy、polling loop、completion rules が書かれており、推論モデルが loop の継続判断を持つ。
- script-driven polling を採用すると、`pr-monitor` の実質責務は script executor / summarizer になり、独立 sub-agent としての責務が薄い。
- 既存 `fetch_codex_pr_review_comments.sh` は Codex-focused wrapper であり、PR 全体の observation、all/Codex signal separation、head SHA binding、thread state、review requests、progress を扱う新設計と重複する。
- CI/check/status と review/comment/thread/request は収集対象としては性質が異なるため内部 collector は分けるべきだが、merge-prepared evidence としては同じ head SHA / observation window に基づく combined wait result が必要である。
- `wait_pr_observation.sh` は10〜30分程度の foreground wait になりうるため、silent wait ではなく stderr progress による liveness が必要である。
- review 本文は PR 全件を常に出すと古い指摘がノイズになるため、`@codex review` trigger comment を基準にした trigger window 内の本文を final JSON に含める必要がある。
- `@codex review` という文字列を含む通常 feedback を trigger command と誤分類すると、最新の人間/レビュー指摘が current review signal から消えるため、trigger 判定は actual command comment に限定する必要がある。
- CI は件数だけでは修正判断に不足するため、失敗時は workflow / run / job / failed step を machine-readable に返す必要がある。
- `.codex/config.toml` は bootstrap-only file であり通常 update では上書きされないため、既存 repo に残る stale `pr-monitor` / `github-codex-pr-review-comments` guidance は、旧 agent を復活させずに fixed migration で解消する必要がある。

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - PR 作成後または push 後に、CI / checks / statuses / review feedback が本当に揃ったかを確認してから次の判断へ進みたい maintainer。
  - `github-pr-merge-preparer` や issue execution workflow から PR observation を行う main orchestrator。
- 代表シナリオ:
  - `github-pr-merge-preparer` が PR number と expected head SHA を持って `wait_pr_observation.sh` を実行する。
  - wait script は snapshot helper を繰り返し呼び、checks/statuses と review signals の normalized fingerprint が quiet window / same fingerprint 条件を満たすまで bounded に待つ。
  - wait script は実行中、stderr に adaptive current-state progress summary を poll ごと最大1行出す。
  - wait script は stdout に final JSON text を1回だけ出す。
  - caller は stdout final JSON の `normalized_status`、`ci` / `review` summary、trigger-window review body、CI failure detail、`limitations`、`recommended_next_action` を読み、merge-prepared evidence または human gate を報告する。
  - debug / audit が必要な場合だけ `--out <dir>` を指定し、stdout final JSON と同一内容の `result.json` および補助 artifacts を保存する。

## スコープ

- 必須:
  - `github-pr-observation` skill を provider-side `src/spec_dock/assets/install_root/.agents/skills/` に新設する。
  - `wait_pr_observation.sh` を、待機込み observation の public entrypoint として導入する。
  - `fetch_pr_observation_snapshot.sh` を、1回分の normalized PR snapshot / fingerprint を返す public snapshot entrypoint として導入する。
  - snapshot helper の内部 collector として、CI/check/status collection と review/comment/thread/review_request collection を責務分離する。
  - `github-pr-merge-preparer` / `github-pr-creator` の `pr-monitor` handoff を `github-pr-observation` invocation に置き換える。
  - wait wrapper は arbitrary endpoint / method / GraphQL query / body / header / write operation を caller から受け取らない。
  - stdout は final JSON text only とし、途中経過を混ぜない。
  - stderr progress は default `--progress stderr-summary` とし、`--progress none` で抑止できる。
  - progress line は adaptive current-state summary とし、event-diff log ではない。
  - `--out` は optional debug/audit mode とし、通常 path の必須 artifact を増やさない。
  - all review signals と Codex-authored subset を分けて出力する。
  - `@codex review` trigger comment を explicit input または fixed inference で特定し、trigger window 後の review/comment body を final JSON に含める。
  - trigger command 判定は、explicit trigger comment id または本文の first nonblank line が `@codex review` command である comment に限定する。
  - review body inclusion は `--body-mode` で制御し、default は bounded な `trigger-window-truncated` とする。
  - CI failure detail として workflow / run / job / failed step を取得できる範囲で final JSON に含める。
  - review thread state が取得できる場合は unresolved / resolved / outdated を区別し、取得できない場合は limitation として machine-readable に出力する。
  - `overall_status` 互換を維持しつつ、`normalized_status`、`observation_complete`、`limitations`、`summary`、`recommended_next_action` を final JSON に出力する。
  - provider-side source と dogfooding mirror の parity、old asset retirement、wrapper schema、progress contract に対する regression coverage を追加または更新する。
  - bootstrap-only `.codex/config.toml` に stale `pr-monitor` / old review wrapper guidance が残る既存 repo は、update 時に `github-pr-observation` direct invocation guidance へ移行する。
- 禁止:
  - `pr-monitor` provider / mirror asset を残さない。
  - deprecated shim を残さない。
  - `github-codex-pr-review-comments` を互換 skill として残さない。
  - wait script / snapshot helper / collector に GitHub write operation を持たせない。
  - progress から success / failure / timeout / merge-ready を確定しない。
  - stdout と stderr を merge した stream を JSON として parse する運用を正規契約にしない。
  - progress に個別 check 名、job 名、reviewer 名、comment body、URL、P1/P2 など text interpretation 由来の priority を出さない。
  - trigger window 外の古い review/comment body を current review payload として final JSON に混ぜない。
  - caller-provided arbitrary endpoint / method / GraphQL query / body / header / jq / raw gh args で本文取得や CI 詳細取得を拡張しない。
  - `summary.md` を生成しない。
  - `github-pr-merge-preparer` / `github-pr-creator` を本 issue で agent 化しない。
- 対象外:
  - review request comment requester の実装。
  - PR merge 実行、auto-merge enablement、branch cleanup、issue lifecycle close。
  - GitHub plugin skills の再実装。
  - repository-specific required checks policy の全面設定機構。

## 境界

- `github-pr-observation`:
  - read-only PR observation capability。
  - usage guide、schema、progress contract、prerequisites、no-write rules を保持する。
- `wait_pr_observation.sh`:
  - loop / sleep / timeout / quiet window / same fingerprint count / zero-check grace / head-change detection / final status classification を担う。
  - stdout に final JSON text を1回だけ出す。
  - stderr progress は non-authoritative として出す。
  - `--out` 指定時だけ durable artifacts を書く。
- `fetch_pr_observation_snapshot.sh`:
  - 1回分の normalized snapshot と fingerprint を stdout JSON text として出す。
  - wait loop は持たない。
- `github-pr-merge-preparer`:
  - workflow coordinator として維持する。
  - PR 作成/発見、observation invocation、bounded fix delegation、push 確認、再 observation、merge-prepared / human gate 報告を担う。
- `github-pr-creator`:
  - PR 作成 workflow skill として維持する。
  - PR 作成後の軽い確認が必要な場合だけ snapshot path を使う。

## 非交渉制約

- `pr-monitor` は完全廃止する。
- wait wrapper / snapshot helper / collector は read-only である。
- latest head SHA に束縛されていない observation は merge-prepared evidence に使えない。
- observation は無限待機ではなく、deadline 付きの deterministic bounded wait とする。
- stdout final JSON text が唯一の primary result である。
- stderr progress は final decision authority ではない。
- `--out` artifacts は optional debug/audit output であり、通常 path の正規受け渡しではない。
- review/comment body を final JSON に含める場合も、trigger window、body mode、size cap、truncation metadata に従う。
- `@codex review` trigger command は explicit trigger id または first nonblank line command としてだけ扱い、本文中の単なる言及は通常 feedback signal として保持する。
- body hash / fingerprint には raw body ではなく body hash を使う。
- wait wrapper の semantic stability 判定は、wrapper 実行ごとに変わり得る raw snapshot fingerprint ではなく、head / CI / review / limitations / normalized status 等の意味的 field に基づく。
- CI failure detail は取得可能な workflow / run / job / failed step metadata に限定し、log body 全文取得は本 issue の通常 path に含めない。
- Thread state 不明、wrapper failure、stale head、zero-check grace 未満は success ではない。
- Provider-side source of truth は `src/spec_dock/assets/install_root/` であり、dogfooding mirror は検証対象として parity を保つ。

## Progress 表示要件

- default:
  - `--progress stderr-summary`
- opt-out:
  - `--progress none`
- stdout:
  - final JSON text only。
- stderr:
  - start line を1行出してよい。
  - poll ごとに最大1行。
  - no-change poll でも liveness のため current-state summary を出す。
  - terminal line を出す場合も final decision word ではなく `final=stdout_json` 程度にする。
- line shape:
  - ASCII key/value。
  - 200-240 chars 程度を目標に bounded。
  - truncation は free text を切るのではなく optional fields を落とし、`limit=truncated` を出す。
- 常に出す fields:
  - `poll`, `elapsed`, `remain`, `phase`, `ci`, `review`, `quiet`, `limit`
- CI が進行中の場合だけ出す fields:
  - `checks`, `ok`, `fail`, `pend`, `other`
- review が意味を持つ場合だけ出す fields:
  - 必要に応じて `reviewers`, `changes`
- CI status:
  - `unknown`, `none`, `pending`, `running`, `passed`, `failed`
  - `passed` は observed checks/statuses だけでなく、GitHub の merge-state / required-check view が未充足を示していないことを前提にする。
  - `gh pr view --json mergeStateStatus,statusCheckRollup` で `mergeStateStatus=BLOCKED` かつ required check rollup に `EXPECTED` / `IN_PROGRESS` / `PENDING` / `QUEUED` / `REQUESTED` / `WAITING` が見える場合、observed checks が success/skipped/neutral だけでも required checks 未充足として `pending` 相当として扱う。
  - `mergeStateStatus=UNKNOWN` は GitHub 側の一時的な mergeability 未計算状態として扱い、blocking human gate ではなく `pending` / wait 相当として扱う。
  - commit statuses API の top-level aggregate `state` が `pending` / `failure` / `error` を示す場合、individual `statuses[]` が1件以上返っているときだけ aggregate を backstop として `ci=pending` / `ci=failed` に反映する。
  - `DIRTY` / `BEHIND` など、check の完了待ちではなく人間または branch action が必要な merge state は `pending` へ畳まず、`ci=unknown` と blocking limitation / human gate 相当で返す。
  - required-check metadata の取得に失敗した場合は `pr_required_check_state_unavailable` limitation を final JSON に含め、checks/statuses が観測されている場合でも observed checks だけで `passed` / merge-prepared と誤判定しない。
- Review status:
  - `unknown`, `none`, `pending`, `requested`, `commented`, `approved`, `changes_requested`, `unresolved`
  - `dismissed` は個別 review signal state として保持するが、aggregate review status としては単独で block しない。
  - `reviewDecision=REVIEW_REQUIRED` は、明示的な review request signal がなくても `requested` 相当として扱う。
  - `reviewDecision=CHANGES_REQUESTED` は、REST review list が stale / trigger-window 外に見える場合でも aggregate review blocker として `changes_requested` に反映する。

## Final JSON 詳細要件

- Trigger window:
  - explicit input:
    - `--trigger-comment-id`
    - `--trigger-created-at`
  - fallback:
    - explicit trigger がない場合は、fixed logic で PR conversation comments から最新の `@codex review` comment を推定してよい。
    - 推定した場合は `trigger.source=inferred` と `limitations` に `trigger_inferred` を出す。
  - window boundary:
    - review / comment / workflow signal の body / current signal inclusion は `trigger_created_at` 以後を current trigger window とする。
    - unresolved かつ non-outdated の visible review thread は、trigger window より前に開始していても active blocker として扱う。
    - PR conversation comments で同一 timestamp の場合は `id > trigger_comment_id` のものだけを trigger 後として扱う。
    - PR conversation comments は `created_at` だけでなく `updated_at` も signal metadata として保持し、`updated_at >= trigger_created_at` の edit は current trigger window signal として扱う。
    - expected head SHA と一致しない review / check detail は stale として分離する。
    - `--trigger-comment-id` だけが渡され `--trigger-created-at` が省略された場合、固定 issue comments 取得結果から該当 comment id の `created_at` を解決する。解決できない場合は trigger unknown / informational limitation とし、body payload を全件化しない。
  - Body mode:
    - `none`:
      - metadata と `body_sha256` のみ。
  - `trigger-window-truncated`:
    - default。
    - trigger window 内の review/comment body を stdout final JSON に含める。
    - item cap、per-item body char cap、total body char cap を適用する。
  - `trigger-window-full`:
    - 明示 opt-in。
    - stdout 肥大化 risk / limitation を final JSON に出す。
  - `out-only`:
    - stdout は metadata + `body_sha256`。
    - `--out` 指定時だけ raw body artifact を保存する。
- Body cap:
  - cap 超過時も JSON validity を保つ。
  - 各 item は `body_truncated`, `body_original_length`, `body_sha256`, `omitted_reason` を出す。
  - 全体 overflow は `item_count_omitted`, `body_chars_omitted` を出す。
- CI failure detail:
  - failed / error / cancelled / timed_out / action_required / startup_failure / stale などの failure 系がある場合、取得できる範囲で `ci.failures[]` に workflow name、workflow run id、job name、job id、failed steps、URL を出す。
  - GitHub Actions job / step が取得できない check は check run name、status、conclusion、details_url / html_url を出す。
  - CI logs の全文取得は対象外。

## 受け入れ条件

- AC-001:
  - アクター:
    - `github-pr-merge-preparer` または main orchestrator。
  - 操作:
    - `wait_pr_observation.sh` を repo / pr / expected head SHA 付きで実行する。
  - 期待結果:
    - caller は自前で polling loop / sleep / quiet window / timeout を判断しない。
    - final decision は stdout final JSON text に基づく。
    - stderr progress から final decision しない。
- AC-002:
  - アクター:
    - `wait_pr_observation.sh`。
  - 前提:
    - expected head SHA が指定されている。
  - 操作:
    - PR current head SHA を取得する。
  - 期待結果:
    - current head SHA が expected head SHA と一致する場合だけ、その SHA に対する observation を final result として扱う。
    - checks / review collection の後にも PR current head SHA を再取得し、collection 中に head が変わった場合は collected green result を採用しない。
    - 一致しない場合は `stale_head` / non-success / `observation_complete=false` 相当を stdout final JSON に返す。
- AC-003:
  - アクター:
    - wait wrapper。
  - 前提:
    - monitoring 中に PR head SHA が変わる。
  - 操作:
    - 次回 snapshot で head SHA 変更を検出する。
  - 期待結果:
    - 変更前 snapshot を stable result に混ぜず、head change / stale を machine-readable に返す。
    - final output は、どの head SHA に対する結果かを明示する。
- AC-004:
  - アクター:
    - snapshot helper / checks collector。
  - 操作:
    - latest head SHA に紐づく checks/statuses を取得し正規化する。
  - 期待結果:
    - `ci=unknown|none|pending|running|passed|failed` の progress status と、final JSON の詳細 counts を生成できる。
    - failure / error / cancelled / timed_out / action_required / startup_failure / stale が1件でもあれば `ci=failed` 相当になる。
    - failure 系がなく in_progress があれば `ci=running` 相当になる。
    - failure 系も in_progress もなく queued / requested / waiting / pending があれば `ci=pending` 相当になる。
    - 失敗・pending・running がなく、観測対象が terminal non-blocking なら `ci=passed` 相当になる。
    - skipped / neutral は、それだけを理由に unknown にしない。
    - failure 系がある場合は、取得可能な workflow / run / job / failed step detail を final JSON に出す。
    - `mergeStateStatus=BLOCKED` かつ required check rollup に pending / expected 系 state がある場合は、observed check run がすべて terminal non-blocking でも `ci=pending` 相当になり、`required_checks_missing_or_pending` limitation と required check state metadata を返す。
    - `mergeStateStatus=UNKNOWN` は `ci=pending` 相当として扱い、`pr_merge_state_blocking` には分類しない。
    - commit status aggregate `state=pending|failure|error` は individual `statuses[]` が1件以上ある場合に限り `ci=pending` / `ci=failed` の backstop として扱い、empty `statuses[]` の aggregate だけで false wait / false failed にしない。
    - `DIRTY` / `BEHIND` など polling では解消しない merge state は `required_checks_missing_or_pending` に混ぜず、`pr_merge_state_blocking` limitation と `ci=unknown` / human gate 相当を返す。
    - required-check metadata が取得できない場合は `pr_required_check_state_unavailable` limitation を返し、checks/statuses が存在する限り observed green だけで `passed` 相当にしない。
- AC-005:
  - アクター:
    - wait wrapper。
  - 操作:
    - snapshot fingerprint を比較し、quiet window と same fingerprint count を評価する。
  - 期待結果:
    - terminal / complete / stable の条件を満たすまで success としない。
    - checks green 直後に遅れて付く review signal を見逃しにくい。
    - wrapper 側の semantic fingerprint は、raw snapshot fingerprint のみの churn で same-fingerprint count を無限に reset しない。
- AC-006:
  - アクター:
    - snapshot helper / review collector。
  - 操作:
    - issue comments、inline review comments、review bodies、reviewDecision、reviewRequests、reviewThreads を取得する。
  - 期待結果:
    - all signals と Codex-authored subset が分離される。
    - review-related progress status は GitHub から機械的に取れる `unknown|none|pending|requested|commented|approved|changes_requested|unresolved` だけを使う。
    - P1/P2 など本文解釈由来の priority は progress status にしない。
    - `reviewDecision=REVIEW_REQUIRED` は `requested` に反映され、`reviewDecision=APPROVED` は current issue comments / unresolved threads / changes requested より優先されない。
    - current trigger window 内の issue comment は、approval より後段の軽微情報ではなく、approval を上書きし得る current review signal として扱う。
    - review thread state が利用可能な場合は unresolved / resolved / outdated が machine-readable に出力される。
    - trigger window 内の review/comment body は body mode に従って final JSON に出力される。
    - trigger window 外の古い review/comment body は current-window payload に含まれない。
    - issue comment の `updated_at` が trigger window 内に入る場合は current-window comment signal として本文 / metadata / fingerprint に反映される。
- AC-007:
  - アクター:
    - wait wrapper。
  - 前提:
    - check/status が0件に見える PR。
  - 操作:
    - monitoring 開始直後に checks/statuses を取得する。
  - 期待結果:
    - 即 success とせず、zero-check grace 中は `ci=none` / pending-equivalent として扱う。
    - deadline まで出現しない場合は、0件であることと limitation / recommended next action を stdout final JSON に明示する。
- AC-008:
  - アクター:
    - wait wrapper / review collector。
  - 前提:
    - `reviewDecision=CHANGES_REQUESTED` または unresolved review thread が存在する。
  - 操作:
    - review signals を分類する。
  - 期待結果:
    - progress は `review=changes_requested` または `review=unresolved` を表示できる。
    - final JSON は actionable summary と source signal を返す。
- AC-009:
  - アクター:
    - wait wrapper / review collector。
  - 前提:
    - review thread state を取得できない。
  - 操作:
    - limitation を受け取る。
  - 期待結果:
    - visible comments / reviews が0件でも、thread state absence を隠して unconditional success としない。
    - `review=unknown` / limitation / recommended next action を machine-readable に返す。
- AC-010:
  - アクター:
    - wait wrapper。
  - 前提:
    - foreground wait が複数 poll 継続する。
  - 操作:
    - stderr progress を出す。
  - 期待結果:
    - stdout は final JSON only。
    - stderr progress は poll ごとに最大1行。
    - default progress は event-diff ではなく adaptive current-state summary。
    - progress line は bounded、single-line、parse-safe key/value。
    - `--progress none` で progress を抑止できる。
    - progress line には review/comment body、URL、reviewer 名、job 名を出さない。
- AC-011:
  - アクター:
    - installer / dogfooding verifier。
  - 操作:
    - scaffold / install_root parity と stale asset cleanup を確認する。
  - 期待結果:
    - provider-side source と dogfooding mirror に `github-pr-observation` が存在する。
    - provider-side source と dogfooding mirror に `pr-monitor` assets と `github-codex-pr-review-comments` skill が残らない。
    - init/update regression が managed asset inventory の drift を検出できる。
    - 既存 bootstrap-only `.codex/config.toml` に stale `pr-monitor` / old review wrapper guidance がある場合、update は旧 agent / shim を復活させず `github-pr-observation` direct invocation guidance へ移行する。
- AC-012:
  - アクター:
    - wait wrapper / review collector。
  - 前提:
    - `@codex review` trigger comment が explicit input として渡されている。
  - 操作:
    - trigger 後に付いた PR conversation comment、inline review comment、review body を取得する。
  - 期待結果:
    - trigger comment 自身、または first nonblank line が `@codex review` command である inferred trigger comment は `trigger_command=true` として識別される。
    - `@codex review` という文字列を本文途中に含む通常 feedback は trigger command ではなく current review/comment signal として残る。
    - trigger 前の old review/comment body は final JSON の current trigger-window payload に含まれない。
    - trigger 後の body は `--body-mode` と cap に従って final JSON に含まれる。
    - cap 超過時は truncation / overflow metadata を出す。
    - explicit trigger comment id だけが渡された場合も、issue comments 内の同 id から trigger timestamp を解決できれば explicit trigger window として扱う。
- AC-013:
  - アクター:
    - wait wrapper / review collector。
  - 前提:
    - explicit trigger が渡されていない。
  - 操作:
    - fixed logic で最新の `@codex review` comment を探す。
  - 期待結果:
    - first nonblank line が `@codex review` command である comment が見つかった場合は `trigger.source=inferred` と `limitations=["trigger_inferred"]` 相当を出す。
    - 本文途中の単なる `@codex review` 言及だけでは inferred trigger としない。
    - 見つからない場合は body payload を全件化せず、trigger unknown limitation と recommended next action を出す。
- AC-014:
  - アクター:
    - checks / actions collector。
  - 前提:
    - GitHub Actions run / job / step detail が取得できる。
  - 操作:
    - failed check / failed workflow run を収集する。
  - 期待結果:
    - final JSON の `ci.failures[]` に workflow name、run id、job name、job id、failed steps、html/details URL が出る。
    - 取得できない場合は check run level detail と limitation を出す。

## 例外・エッジケース

- EC-001:
  - checks が green になった直後に review comment が追加される。
  - 期待:
    - review snapshot が stable になるまで success を返さない。
- EC-002:
  - GitHub Actions workflow が path filtering などで skip され、required check が Pending のまま残る。
  - 期待:
    - `ci=passed` ではなく `ci=pending` 相当として扱う。
- EC-003:
  - GitHub Actions job が条件分岐により skipped だが、GitHub上は terminal non-blocking として観測される。
  - 期待:
    - skipped だけを理由に unknown にせず、失敗・pending・running がなければ `ci=passed` 相当に畳む。
- EC-004:
  - review thread が outdated または resolved。
  - 期待:
    - 単なる comment 存在だけで blocking review feedback と誤分類しない。
- EC-005:
  - review thread state wrapper が missing / auth failure / rate limit / schema mismatch で失敗する。
  - 期待:
    - limitation と `review=unknown` / human gate 相当を返す。
- EC-006:
  - progress output が多くなりすぎる。
  - 期待:
    - stderr は bounded にし、詳細は final JSON または optional `--out` debug/audit artifacts に残す。
- EC-007:
  - PR が draft、closed、または merged 等の non-open 状態である。
  - 期待:
    - CI / review が green に見えても merge-prepared success とせず、`human_gate` と `mark_pr_ready_for_review` / `reopen_or_use_open_pr` 相当の recommended next action を返す。
- EC-008:
  - wait 終盤の snapshot poll、または quiet / same-fingerprint 安定待ちの最中に wait deadline が timeout するが、直前に有効な latest payload がある。
  - 期待:
    - 直前の CI / review summary と artifacts を破棄して synthetic unknown へ落とさず、latest payload に `snapshot_poll_timeout` limitation を付与し、`normalized_status=timeout` として返す。
- EC-009:
  - GitHub PR merge state または required-check metadata が、polling 継続だけでは安全に merge-prepared と判断できない状態を示す。
  - 期待:
    - `mergeStateStatus=BLOCKED` かつ required check rollup が pending / expected の場合は `ci=pending` / wait 相当として扱う。
    - `DIRTY` / `BEHIND` など non-CI merge state は `ci=pending` ではなく `ci=unknown` / `pr_merge_state_blocking` / human gate 相当として扱う。
    - required-check metadata 取得失敗は `pr_required_check_state_unavailable` limitation として保持し、observed checks だけの false pass を防ぐ。
- EC-010:
  - GitHub API の aggregate field または collection timing が、個別 signals だけでは false pass / false gate を生み得る。
  - 期待:
    - `mergeStateStatus=UNKNOWN` は transient として `ci=pending` / wait 相当にし、human gate にしない。
    - commit status aggregate `state=pending|failure|error` は individual `statuses[]` が1件以上ある場合に限り、individual statuses より広い backstop として使う。
    - commit statuses API の `statuses[]` が空の場合、top-level aggregate `state=pending|failure|error` は backstop として採用せず、check runs / required-check rollup が success なら CI を `passed` にできる。
    - issue comment edit は `updated_at` を使って trigger window に入る current feedback として扱う。
    - `reviewDecision=CHANGES_REQUESTED` は REST review freshness に依存せず `review=changes_requested` に反映する。
    - snapshot collection 後に PR head が変わっていた場合は `stale_head` / `observation_complete=false` / `rerun_for_current_head` 相当で返す。
- EC-011:
  - GitHub API の pagination / timestamp granularity が、review thread state または trigger window の false gate を生み得る。
  - 期待:
    - GraphQL `reviewThreads.comments(last: 100)` に対象 REST review comment id が含まれない場合でも、REST review comment の `thread_id` と GraphQL thread node id が一致すれば resolved / outdated / unresolved state を反映する。
    - REST review comment に `thread_id` がない場合は従来通り GraphQL comment id 突合と limitation / unknown fallback に留め、推測で thread state を割り当てない。
    - review / inline review comment が `trigger_created_at` と同秒の場合は、GitHub timestamp の秒精度では trigger 後と断定できないため current trigger-window signal / body として扱わない。
    - trigger issue comment 自体と issue comment edit の既存契約は維持する。
- EC-012:
  - GitHub API の空 aggregate / 同秒 review ordering / bootstrap-only symlink が、false wait、false review collapse、repo 外 config 書き換えを生み得る。
  - 期待:
    - commit statuses API の `statuses[]` が空の場合、top-level aggregate `state=pending|failure|error` は backstop として採用せず、check runs / required-check rollup が success なら CI を `passed` にできる。
    - 同一 reviewer の複数 review が同じ `submitted_at` 秒にある場合、review id を文字列ではなく数値または API order 相当の deterministic tie-breaker で畳み、古い review が新しい review を上書きしない。
    - bootstrap-only `.codex/config.toml` migration は symlink を辿って書き換えず、実体ファイルの場合だけ known stale guidance を移行する。

## 確定済み補足

- 本 issue に、初回 Codex review request comment requester の実装は含めない。
  - 必要なら `github-pr-merge-preparer` owned の explicit opt-in / idempotent requester として別 issue 化する。
- 初期 default は設計で固定する。
  - `timeout=1800s`, `poll_interval=30s`, `quiet=90s`, `same_fingerprint_count=2` を初期値とし、tests では fake clock で検証する。
- 現時点でユーザー確認が必要な未確定事項はない。
