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

（本番の切り替えの後に書く。2026-11-01 時点で、準備の手順1〜4が済んだ。）

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
- SpecDock：`installation update` は `.claude/skills/spec-dock*` の写しを外すが、`.agents/skills` への相対リンクを作らない。ルートの `.gitignore` の `.workbench/` で、雛形の `templates/cue/*/.workbench/README.md` がコミットから漏れる。
