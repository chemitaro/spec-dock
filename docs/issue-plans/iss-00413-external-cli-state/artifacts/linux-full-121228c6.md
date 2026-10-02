# Linux 通常全件 — 121228c6

対象full SHA: `121228c6fca1fd016e7bccef009902396112ba43`。2026-10-02 JST。P-18前のbaseline証拠であり、撤去後候補の合格ではありません。

Linux x86_64 / Python 3.11.16。macOS arm64ホストのamd64 Dockerで検証。固定image `sha256:c514701300438939d8f2f3fd75cc57ea2eff502c1920e5cc98c713cf17452e3d`、networkなし、read-only root、capabilities 0、fixture local/tmpfs。実Gitと通常pytestを使用。root UIDの限定container検証であり、全filesystemや全ユーザー条件を保証しません。

最初の通常全件は4 failed / 1884 passed / 20 skipped / 12 errors、947.99秒、exit1。[元log](linux-full-121228c6-original.txt)を保全しました。失敗・errorはchild processがPATHからuvを発見できない環境設定でした。

検証containerのPATHへ `/fixture/tools/bin` を追加し、製品source/testsを変更せず通常 `/fixture/tools/bin/uv run pytest -q --tb=short -ra` を再実行しました。1900 passed / 20 skipped、977.90秒、original session 86011のactual exit0。[補正後log](linux-full-121228c6-path-fixed.txt)を保全しています。

[前観測](linux-full-121228c6-before.txt)と[後観測](linux-full-121228c6-after.txt)でfull SHA/clean、actual Python、provider importを確認。source/tests等324 tracked input filesのSHA-256は両方 `2bcbce60d8b318761f81529c4b998fae4d43027b52470fba317143400547494e` で一致しました。元の失敗結果を書き換えず、件数を合算しません。

20 skipの内訳はzsh不在12、Windows native3、macOS専用1、Linux匿名stageのpathname cleanup非該当4です。Windows成功の証拠には使いません。Windows対応義務は[最新OS決定](os-support-decision.md)で失効します。P-18とFinish P1修正後には新candidate SHAの通常全件・配布・manual・Strict/FQを別途確認します。

元logの完全bytesは[raw JSON](linux-full-121228c6-original-raw.json)のUTF-8 text/bytes/SHA-256で保持します。閲覧用txtだけ行末空白を整形し、Gitの空白検査を通します。source log、件数、exit、内容は変更していません。
