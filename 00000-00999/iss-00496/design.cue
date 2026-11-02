package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"`installation update` が `.claude/skills/spec-dock*` の古い写しを外して、Claude Code からその skill が見えなくなるときだけ、結果で知らせて次の1手を示す。",
	"SpecDock はリンクを作らない（リンクは Claude Code の側の `sync-project-skills` が作る決まり）。警告は置き方を示すだけにする。",
]
current: "`update_static_assets()` は、`RETIRED_SKILL_SLOTS` の中の既知の写しを外す（`--dry-run` では `planned_retired_paths` に出す）。枠そのものがリンクなら `_linked_host_slot()` が飛ばす。写しを外した後に枠の空の（または利用者のファイルが残る）ディレクトリが残り、リンクがないことは結果に出ない。"
target:  "外す写し（`--dry-run` では外す予定の写し）が1つ以上ある枠ごとに、結果の外枠の `warnings` に `CLAUDE_SKILL_LINK_MISSING` が1件出る。リンクがある枠は飛ばされたままで、何も言わない。"

design: {
	"D-01": {
		title: "枠ごとの警告 CLAUDE_SKILL_LINK_MISSING"
		text: """
			`direct_static_update.py` に、外した（外す予定の）道筋の一覧から、警告を作る小さな関数を足す。

			- 道筋が `RETIRED_SKILL_SLOTS` のどれかの枠の下にあれば、その枠ごとに1件（`RETIRED_SKILL_SLOTS` の並び順）。ほかの古い道筋（`spec-dock/spec-dock.version` など）は数えない。
			- 置き場は、外枠の `warnings`（`OperationResult.warnings`、`Diagnostic`）。JSON の `warnings[]` と、テキストの標準エラーの `warning [CODE] 文` に、今の決まりのまま出る。`data.result` の形は変えない（`ACTIVE_LINK_NOT_UPDATED` と同じく、結果の成否を変えない派生の知らせとして扱う）。
			- コードは `CLAUDE_SKILL_LINK_MISSING`。`details` は `slot`（例 `.claude/skills/spec-dock`）、`link_target`（`../../.agents/skills/<name>`）、`command`（置き方の1行のシェルのコマンド）。
			- 文（`message`）は、テキストの出力だけでも次の1手が分かるように、枠、リンクの行き先、`sync-project-skills`、コマンドを1行に含める。
			- コマンドは、どこで実行しても対象の作業ツリーに作用し、途中で失敗すれば後を実行しないように、`&&` でつないだ1行にする：`cd <作業ツリーの根の絶対パス> && find <slot> -mindepth 1 -depth -type d -empty -delete && rmdir <slot> && ln -s ../../.agents/skills/<name> <slot>`。根の道筋はシェルの引用符で囲む。空のディレクトリだけを消し、利用者のファイルが残れば `rmdir` が失敗して止まる（`ln -s` が既存のディレクトリの中にリンクを作る事故を防ぐ）。SpecDock はこれを実行しない。
			"""
		satisfies: ["R-01"]
	}
	"D-02": {
		title: "出す場合と出さない場合"
		text: """
			- `installation update --dry-run`：`planned` の結果に、外す予定の写しの枠ごとに出す。
			- `installation update`（適用）：`succeeded` の結果に、実際に外した写しの枠ごとに出す。途中で止まった `partial` の結果でも、実際に外せた写しがあれば出す（その枠はもう見えないため）。
			- 外す写しがない（`unchanged`、または写しのない枠）なら出さない。前の更新で写しを外した後の空の枠にも、もう一度は出さない（R-01 の「外す写しの名前ごとに」は、その回に外す写しを数える）。
			- 枠、`.claude/skills`、`.claude` がリンクなら、今までどおり枠ごと飛ばすので出さない。リンクが壊れている（行き先がない）場合も、リンクは Claude Code の側のもので、SpecDock は写しを外さないので出さない（壊れたリンクの診断は、この Issue の範囲外）。
			- `installation uninstall` には出さない。`.agents/skills` の skill も外すので、リンクを置く理由がない。
			"""
		satisfies: ["R-01"]
	}
	"D-03": {
		title: "葉の help の案内"
		text:  "`cli/catalog.py` の `installation update` の Writes に、写しを外してリンクがない枠に `CLAUDE_SKILL_LINK_MISSING` を出し、リンクは作らないことを1文で足す。配る文書（`src/spec_dock/assets/`）は変えない（警告の文そのものが置き方を示すため。`static-inventory.json` で #497 とぶつからない）。"
		satisfies: ["R-01"]
	}
}

compatibility: "成功の終了コード、`status`、`effects`、`data.result` は変えない。足すのは `warnings[]` の要素と、テキストの標準エラーの `warning` の行だけ。`warnings` を空と決めつけて読む利用者には、新しい要素が見える（0.5.0 の「更新」の節に書く契約の変更）。"
risks: ["コマンドの例は POSIX の `find`、`rmdir`、`ln` を前提にする（SpecDock の業務のコマンドは Linux と macOS だけを支える）。"]
