package spec

// 設計（Issue）。型 specdock/v1。

goals: ["リンクの許可を `spec-dock/initiatives` の1か所に限り、ほかの経路の検査は変えない。"]
current: "`_open_parent` が、すべての要素を `O_NOFOLLOW` で開くので、版4のリンクを通れず「unsafe directory component 'initiatives'」で止まる。"
target:  "`spec-dock/initiatives` が、そのクローンの実ディレクトリ `spec-dock/.canonical` を指すリンクのときだけ、そのリンク先を開いて進む。"

design: {
	"D-01": {
		title:     "カタログへのリンクだけを許す経路の検査"
		text:      "`finalize-artifact.py` の `_open_parent` で、先頭が `spec-dock`、2番目が `initiatives` の要素だけを特別に扱う。「そのクローンのカタログ」は、`--repo-root` の `.git` から求めた main チェックアウトの `spec-dock/.canonical` とする（`.git` がディレクトリなら root 自身、`gitdir: <main>/.git/worktrees/<名前>` のファイルならその main。どちらでもなければ、リンクは拒む）。要素がリンクのとき、`readlink` した行き先（相対なら `spec-dock` の下からの相対）の `realpath` が、そのカタログの `realpath` と等しく、カタログ自体が `lstat` でリンクでない実ディレクトリのときだけ、その `realpath` を `O_NOFOLLOW` で開いて進む。別のクローンのカタログ、名前だけが `.canonical` のディレクトリ、行き先の途中にリンクを含み実体がずれるものは、今までの誤りで止める。ほかの要素は今までどおりすべて `O_NOFOLLOW`。`_require_parent_still_bound` は同じ `_open_parent` を通るので、device と inode の再確認は変わらない。コマンド、引数、出力、終了コードは変えない。"
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title:     "配布資産の更新"
		text:      "提供側 `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` を直し、`static-inventory.json` の今のハッシュを更新して、0.5.0 のバイトを既知の古い版に足す。dogfood の写し `.agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` は、提供側のバイトを写す。"
		satisfies: ["R-02"]
	}
}

compatibility: "引数と出力は変わらない。以前は拒んでいた版4のリンク経路が通るだけで、ほかは同じ。版は上げない（0.5.1 は #513）。"
risks: ["リンクの行き先の検査が甘いと、カタログの外へ書ける。行き先を、そのクローンの main チェックアウトの `spec-dock/.canonical`（リンクでない実ディレクトリ）に限る。"]
