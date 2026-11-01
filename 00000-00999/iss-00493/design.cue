package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"OS が作る不要なファイルを、カタログの同期が新しく保存しない",
	"既存のカタログでも、パッケージの更新だけで効く",
	"すでに保存された不要なファイルは、利用者が見つけて消せる",
]

current: """
	同期（`canonical_sync._save`）は、`canonical_git.list_changes`（`git status --untracked-files=all`）が返す変更のうち、30秒たったものをすべて保存する。
	無視の規則はカタログ自身の `.gitignore`（形式1のルートのファイル。`.runtime/` と `.workbench/`）だけで、`.DS_Store` は保存され push される。
	未保存の数（`catalog_change_summary`）と `work finish` の確かめ（`canonical_work._unsaved_places`）も、`.DS_Store` を未保存と見る。
	"""

target: """
	新しい純粋な規則 `is_os_junk(path)` が、OS の不要なファイルを名前で見分ける。
	同期は、まだツリーにない不要なファイル（`added`）を保存の候補から外す。ツリーにすでにある不要なファイルの変更と削除は、今までどおり保存する。
	未保存の数と `work finish` の確かめは、まだツリーにない不要なファイルを数えない。`canonical status` は、ツリーにある不要なファイルを `changes.junk_files` に示し、消し方を案内する。
	"""

design: {
	"D-01": {
		title: "OS の不要なファイルの規則（純粋な関数）"
		text: """
			`spec_dock.runtime.domain.canonical_sync_rules` に `is_os_junk(path: str) -> bool` を足す。パスの最後の部分（ファイル名）だけを、大文字と小文字を区別せず（`casefold`）に比べる。ディレクトリの位置は問わない。

			一覧（`OS_JUNK_NAMES` と接頭辞 `._`）：
			- macOS：`.DS_Store`（Finder の表示の設定）、`._*`（AppleDouble。FAT や SMB の上の拡張属性）、`Icon\\r`（フォルダーのアイコン）
			- Windows：`Thumbs.db`、`ehthumbs.db`、`ehthumbs_vista.db`、`desktop.ini`
			- Linux：`.directory`（KDE の Dolphin の表示の設定）

			どれも OS かファイルの管理の道具が自動で作り、仕様の中身にならない名前に限る。エディターの一時ファイル（`*~`、`*.swp`）や、ボリュームのルートだけにできるもの（`.Spotlight-V100`、`.Trashes`）は対象外。
			"""
		satisfies: ["R-01", "R-02", "R-03", "R-04"]
	}
	"D-02": {
		title: "同期は、まだツリーにない不要なファイルを保存しない"
		text: """
			`canonical_sync._save` は、`list_changes` の結果から「`kind` が `added` で `is_os_junk` が真」の変更を最初に外してから、変更の束（changeset）への割り当て、30秒の規則、保留の規則に渡す。外した変更は `pending_since` にも残らない。

			`list_changes` 自体は変えない。統合（`_merge`）が手元の編集との重なりを見るときと、衝突の別名を選ぶときは、今までどおり不要なファイルも手元のファイルとして数え、取り込みで手元のファイルを黙って上書きしない。

			ツリーにすでにある不要なファイル（`modified`、`deleted`）は外さない。外すと、R-02 の案内で消した削除が保存されず、また、ほかの PC が変えた版との統合が手元の変更に阻まれ続けるため。
			"""
		satisfies: ["R-01"]
	}
	"D-03": {
		title: "まだツリーにない不要なファイルは未保存と数えない"
		text: """
			`canonical_git.catalog_change_summary` は、`git status --porcelain=v2` の未追跡（`?`）の記録のうち `is_os_junk` が真のものを `unsaved` に数えず、`local_junk`（パスの組）に分ける。`canonical status` の `changes.unsaved` は保存されるものだけの数になる。

			`canonical_work._unsaved_places` は、`--porcelain=v1` の `??` の記録のうち `is_os_junk` が真のものを未保存の場所に数えない。`work finish` は、その場所の変更の束を作らず、保存の確かめも止まらない。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "`canonical status` が、ツリーにある不要なファイルを示す"
		text: """
			`catalog_change_summary` は、`git ls-files -z --cached` の結果のうち `is_os_junk` が真のパスを `junk_files` として返す（読むだけで、何も書かない）。

			`canonical status` の `changes` に `junk_files`（パスの並び。既定は空）を足す。空でなければ `changes.status` を `problem` にし、`next_step` を「示したファイルをカタログから消すと、次の同期が削除を保存し、以後は保存しない」という1手にする。衝突の別名（`conflict_files`）があるときは、そちらの1手を先に示す（統合を先に済ませるため）。警告のコードは足さない（`conflict_files` と同じ扱い）。
			"""
		satisfies: ["R-02"]
	}
	"D-05": {
		title: "不要なファイルの削除は大量の削除に数えない"
		text: """
			`classify_holds` は、`deletions` のうち `is_os_junk` が真のパスを、大量の削除の数（`MASS_DELETE_COUNT`、`MASS_DELETE_MIN`、`MASS_DELETE_RATIO`）に数えない。数の分母（`tracked_count`）は変えない。不要なファイルを消しても仕様の中身は失われないため。

			同じ関数は、重ね直し（`_adopt_holds`）でも使われるので、同じ規則が及ぶ。
			"""
		satisfies: ["R-04"]
	}
	"D-06": {
		title: "`canonical remove` は、残った不要なファイルを名指して止まる"
		text: """
			`canonical_remove._refuse_unsaved` は、`summary.local_junk` を、消してしまう無視されたファイル（`ignored_files`）と合わせて `CANONICAL_IGNORED_FILES_PRESENT` の対象にする（今の次の1手「示したファイルをカタログの外へ移してから、同じコマンドを実行する」をそのまま使う）。この確かめは、リンク、登録、worktree を消す前に行う。
			"""
		satisfies: ["F-01"]
	}
	"D-07": {
		title: "配布の文書"
		text: """
			提供側の `src/spec_dock/assets/spec_dock/docs/canonical.md` の「保存と同期」に、保存しない OS の不要なファイルの一覧と、`changes.junk_files` の扱いを1項目足す。`static-inventory.json` の sha256 を直し、前の値を `known_old_sha256` に足す。dogfood の `spec-dock/docs/canonical.md` を同じ PR で同じ内容にする。
			"""
		satisfies: ["R-01", "R-02"]
	}
}

compatibility: """
	**カタログの `.gitignore` に行を足す案を採らない理由**

	1. 既存の5つのカタログに効かせるには、同期か `canonical link` が、利用者のカタログの追跡されたファイル（`.gitignore`）を書き換えて保存する必要がある。利用者がそのファイルを直していれば手での統合が要り、すべてのカタログに SpecDock の都合のコミットが入る。
	2. `.gitignore` は形式1のルートのファイル（`CANONICAL_ROOT_FILES`）で、`is_initial_commit` は最初のコミットのツリーがこれとちょうど同じかで、push できなかった最初のコミットを見分ける。中身を変えると、前の版が作った最初のコミットを見分けられなくなる。
	3. 同期の規則なら、パッケージを更新した時点で、すべての既存のカタログに同じように効き、カタログには何も書かない。

	**互換性**：`canonical status --json` の `changes` に `junk_files` を足す（足すだけ）。`changes.unsaved` は、保存しない不要なファイルを数えなくなる。`canonical remove` が不要なファイルで止まるときの誤りのコードは、`CANONICAL_UNSAVED_CHANGES` から `CANONICAL_IGNORED_FILES_PRESENT` に変わる（どちらも何も消さずに止まる）。
	"""

risks: [
	"古い版の PC が不要なファイルを保存して push し、手元の同じパスに未追跡の不要なファイルがあると、取り込みは手元の編集として待つ（`blocking` の `local_edit`）。手元のファイルを消せば進む。すべての PC を更新すれば起きない",
	"利用者が消したツリーの `.DS_Store` を、30秒のうちに Finder が作り直すと、削除ではなく変更として保存される。`canonical status` が示し続けるので、もう一度消す",
	"名前だけで見分けるので、仕様として `desktop.ini` などの名前のファイルを置いても保存されない（この一覧の名前を仕様に使う場面は想定しない）",
]
