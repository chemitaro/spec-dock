---
種別: レポート（Issue）
ID: "iss-00439"
タイトル: "Migrate Remaining Repositories To Canonical Storage"
関連GitHub: ["#439"]
最終更新: "2026-11-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

2026-11-01、4つのリポジトリを canonical モード（宣言の版4）に切り替えた。どれも、main（taikyohiyou は develop）のチェックアウトで `canonical status` のすべての項目が ok、`verify` が一致（`.meta.json` がなく、すべて `<区切り>/<ID>/`）、`workspace validate` が成功。`canonical link` が示すツールの1行は、どのリポジトリでも要らなかった。

| リポジトリ | 切り替えの PR（マージ） | `spec-dock/canonical` | 切り替えの PR で足したこと |
|---|---|---|---|
| input-devices | #19（`1daf2e3`） | `7d4999b`（15コミット） | `ci.yml` を消す、`AGENTS.md` |
| company-os | #2（`ac64d77`） | `8778f2a`（`canonical link` が最初の canonical を作成） | `ci.yml` を消す、`integrations/spec-dock/contract.md` |
| housing-lifecycle | #239（`887315a`） | `9ed86d4`（411コミット） | 判断 S72 に合わせ、`spec-dock-check.yml` を手動の起動だけに、`ci.yml` を消す、`.githooks/pre-push` を `canonical check` に、`AGENTS.md`・`README.md` |
| taikyohiyou | #2228（`7f579cf`） | `4504a42`（2896コミット） | `spec-dock-check.yml`（ホストの runner）を消し、`ci.yml`（VM の runner、費用の見張りが `validate` を名前で参照）の検査を `canonical check` に、`AGENTS.md` ほか、ツリーの外のリンク4件 |

- 仕様のツリーの外から古い入れ子のパスを指すリンクは、`migrate.py` が書き換えないので、切り替えで切れた（input-devices 17、housing-lifecycle 316、taikyohiyou 4）。切り替え前のコミットの `.meta.json` から新旧の対応を作って書き換え、input-devices#20（`6100bb7`）、housing-lifecycle#240（`3fd5e98`）、taikyohiyou は #2228 の中で直した。書き換えた先は、すべて main のチェックアウトからカタログを通して開けることを確かめた。
- `move-local`：taikyohiyou だけ、追跡外のファイル19件（`.workbench/` 18件と `.DS_Store`）をカタログへ移した。`.DS_Store` が canonical に保存されたので、消して保存し直した（`4b15af0`）。ほかの3つは移すものがなかった。
- 作業用の worktree：利用者の決定で、3つのリポジトリの23個（すべてマージ済み、清潔、仕様の変更なし）を `orca worktree rm` で片付けた。`adopt-worktree` は使わなかった。
- taikyohiyou の staging の検査（run 41296565967）：1回目は `release_command`（alembic）でデータベースへの接続が切れて失敗（`asyncpg ConnectionDoesNotExistError`、接続の段階）。2回目（失敗したジョブだけの再実行）は、許可の記録が1回目のままで `deployment_binding_mismatch`（仕組みの上で必ず止まる）。3回目（すべてのジョブ）で成功。

## Verification

記録は `../epic-00424/.workbench/i12/`（`plan-*`、`register-*`、`verify-*`、`rehearsal-<リポジトリ>/`）。

### 準備1：配布資産 0.4.1 と CI の固定（2026-11-01）

PR をすべて人がマージした：input-devices#18（`773f81e48`）、company-os#1（`1c2acaa39`）、housing-lifecycle#238（`d059b225e`）、taikyohiyou_project#2227（`4218d1a82`、develop）。taikyohiyou の staging の検査（run 41279066856）は成功（e2e の一連は skipped）。

### 準備2：`plan`（読むだけ）

止める異常は0件。taikyohiyou の `TITLE_MISMATCH` 62件は、GitHub の題名を残す。

### 準備3：`register --apply` と `verify`

| リポジトリ | 書き込み | Scope | verify |
|---|---|---|---|
| input-devices | 49 | 17 | 一致 |
| company-os | 3（ラベル） | 0 | 比べるものなし（`no commit with schema-3 metadata was found`、exit 2） |
| housing-lifecycle | 517 | 237（依存56） | 一致 |
| taikyohiyou | 791 | 254（依存284） | 一致（題名の違い62件は警告） |

`migrate.py` は書き込みを1時間に500件までに抑える（`WRITES_PER_HOUR`）。500件に達すると、表示なしで最大1時間待つ。housing-lifecycle の1回目は、この待ちを停止と見誤って止め、同じコマンドで続きから終えた（中断の直前の sub-issue は GitHub に書けていて、再実行で重ねて書かれなかった）。

### 準備4：予行演習（README の「予行演習」の1〜5）

使い捨てのクローンと bare の origin、`XDG_STATE_HOME` は一時のディレクトリ。4つとも、`plan`・`verify`、`build-canonical`・`cut`、取り込み、`move-local`・`canonical link --no-schedule`・`sync`・`check`、仕様の書き込みが保存されて push されること（30秒の静けさの規則の後）、`export-legacy`、従来モードの `workspace validate` が通った。

| リポジトリ | 作り直した履歴（落とした） | リンク（書き換え／書き換えられない／前から切れている） | `canonical check` の項目 | `.meta.json` の往復 |
|---|---|---|---|---|
| input-devices | 15（0） | 116／0／6 | 207 | 17件、違い0 |
| company-os | なし（追跡された仕様がない） | 0／0／0 | 406（最初の canonical を `link` が作成） | 0件。往復の木は移行前と同じ |
| housing-lifecycle | 411（0） | 2599／0／2 | 2564 | 237件、違い0 |
| taikyohiyou | 2896（0） | 717／0／46 | 5400 | 254件、違いは題名62件（と `revision`）だけ |

往復の後の、移行前のコミットとの違い（試しに書いたファイルを除く）：

- housing-lifecycle：3ファイル、リンク4つ。リポジトリの根まで上ってから降りるリンクが、同じ先への短い形に変わった（開く先は同じ）。
- taikyohiyou：`.meta.json` 62件の題名（GitHub の題名を残す決定どおり）と、1つのリンク。`iss-02128/artifacts/…-self-review-after-e2e-gate-deferral.md` の `../../../../artifacts/…` は移行の前から切れていて、往復で別の切れた先を指す形に変わった（どちらも存在しない）。
- input-devices、company-os：違いなし。

`cut` が示した、切り替えの PR で手で外す今の CI の SpecDock の手順：input-devices `ci.yml` 17〜20行、company-os `ci.yml` 16〜19行、housing-lifecycle `ci.yml` 16〜21行、taikyohiyou `ci.yml` 13〜21行。taikyohiyou の `.github/scripts/`（`check_commit_identities.py`、`resolve_staging_route.py` とそのテスト）にも `spec-dock` の語の一致があるが、中身を見ると、`spec-dock/` の下の変更の振り分けと、bot の名前の一覧で、SpecDock を呼ばない。外さない。

## Residual Risks / Follow-ups

- `migrate.py`：Scope が0件のリポジトリで `verify` が失敗で終わる。500件の待ちに表示がない。往復で、前から切れたリンクの書き方が変わる。いずれも移行を止めない。
- `migrate.py`：仕様のツリーの外から仕様を指すリンクを書き換えない（今回は手で直した）。`cut` が足す `spec-dock-check.yml` は、PR と push で、ホストの runner（`ubuntu-latest`）で動くので、費用の決まりのあるリポジトリでは手で合わせる必要があった。
- SpecDock：カタログが `.DS_Store` を保存する（利用者の全体の除外が効いていない）。
- SpecDock：`installation update` は `.claude/skills/spec-dock*` の写しを外すが、`.agents/skills` への相対リンクを作らない。ルートの `.gitignore` の `.workbench/` で、雛形の `templates/cue/*/.workbench/README.md` がコミットから漏れる。

対応の状況（2026-11-02）：`migrate.py` の穴は #495（README に記載）、`spec-dock-check.yml` の費用は #494、`.DS_Store` は #493 で直し、0.4.2 で5つのリポジトリに配った（input-devices#21、company-os#3、housing-lifecycle#241、taikyohiyou_project#2229）。skill のリンクの警告は #496、雛形の README は #497 で、0.5.0（I-13）に入れる。

## 運用の点検（2026-11-02）

切り替えの後の同期の記録と、5つのリポジトリの今の状態を見た。読むだけで、何も変えていない。

- 同期の記録（`~/.local/state/spec-dock/canonical-sync.log` と `.log.1`、2026-10-30T04:23Z〜2026-11-02T00:15Z）：周期の記録 6436件は、すべて `result=ok`、`holds=0`、エラーのコードなし。

  | リポジトリ | 周期 | 保存と push | 最初の周期 |
  |---|---|---|---|
  | spec-dock | 3750 | 117 | 2026-10-30T04:23Z |
  | input-devices | 709 | 0 | 2026-11-01T09:36Z |
  | company-os | 705 | 0 | 2026-11-01T09:40Z |
  | housing-lifecycle | 690 | 0 | 2026-11-01T09:57Z |
  | taikyohiyou | 582 | 2 | 2026-11-01T12:09Z |

  spec-dock では、2026-10-30T04:25Z に1回、遠くの変更の取り込み（`merged=True`）があり、成功した。
- 各カタログの `state.json`：5つとも `last_error` なし、`holds`・`blocking`・`conflicts` が空、`adopt_remote_pending` は false。
- `spec-dock canonical status`（0.4.2）：5つとも、リンクが正しく、予定の仕事（launchd、60秒ごと）が入っていて動いている。push の認証は ok。未保存0、未 push 0、`conflict_files` と `junk_files` は空。
- カタログの `HEAD` は、5つとも GitHub の `spec-dock/canonical` と同じ。
- 予定の仕事は uv の tool の `spec-dock` を呼ぶので、0.4.2 を入れた後（2026-11-02T00:15Z〜）の周期も 0.4.2 で動き、ok だった。

見えている限界：input-devices、company-os、housing-lifecycle では、切り替えの後に仕様の編集がなく、保存と push の実地の記録はまだない（spec-dock と taikyohiyou で確かめた形と同じ道を通る）。
