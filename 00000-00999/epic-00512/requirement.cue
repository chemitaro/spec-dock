package spec

// 要件（Epic）。型 specdock/v1。書き方は spec-dock/docs/authoring/ のガイドにある。

// 型の版。消さない。
schema: "specdock/v1"

assurance: {
	level:  "standard"
	reason: "GitHub への書き込みと、利用者のファイルを消すおそれのある処理を直し、5つのリポジトリに配る。誤りは別の Issue やファイルに及ぶが、0.5.0 に戻せば回復できる。"
}

purpose:    "0.5.0（canonical モードだけ）の撤去で見つかった canonical の処理の不足を直し、0.5.1 として5つのリポジトリにそろえ、移行のために残した控えと古い worktree を片付ける。"
background: "epic-00424 の I-13（#440、PR #505）で、従来モードのテストを canonical に書き直したとき、canonical の処理が従来の処理より弱い所が見つかった（`iss-00440/report.md` の「後続の候補」1〜14）。従来の処理を確かめていたテストは撤去で消えたので、今は守られていない。また、I-12（#439）と I-13 の控え（`worktrees/i12-prep/backups/`、`worktrees/i12-prep/migrate-to-canonical-state/`、`worktrees/spec-dock-042/backups/`、`worktrees/spec-dock-050/backups/`）と、版3のまま残した spec-dock の worktree 2つ（`local-macos-vm-ci`、`schema1-preserving-migration-20261004`）が残っている。関係者は利用者（PR のマージ、片付けの許可）と、統括のエージェント（配布と片付けの実行）。"

includes: [
	"`iss-00440/report.md` の後続の候補 1〜13 の直しと、候補 14（入れたコンソールでの `work start`／`work finish` の e2e）を足すかの判断（#506〜#511）",
	"0.5.1 のリリースと、spec-dock、input-devices、company-os、housing-lifecycle、taikyohiyou_project への配布（#513）",
	"配布の PR での、利用者のリポジトリの古い記述の直し（input-devices の `README.md` の `4d25a8b` の固定、company-os の `contract.md` の 0.2.4）",
	"移行の控えと、版3の worktree の片付け（#514）",
]
excludes: [
	"新しい機能（ダッシュボード epic-00427、#471）",
	"Linux の未確認の事項（epic-00424 の締めくくりで、別の Issue にする）",
	"古い Epic の棚卸し（この Epic の後に別に行う）",
]

requirements: {
	"R-01": {
		title: "確認の後に状態が変わったら、何も書かずに止まる"
		text:  "`scope close`／`scope reopen` は、端末での確認の後に直接の選択を読み直す。`scope create` は、確認の後と GitHub に書く前と作成の後に `origin` を読み直す。変わっていれば書かない。"
		acceptance: ["#506 の受け入れの条件がテストで観測できる"]
	}
	"R-02": {
		title: "途中の失敗を、起きたとおりに返す"
		text:  "`scope delete` と `artifact create` は、途中で失敗したとき、実際に消えたもの・作ったものを effects と status に正しく出す。"
		acceptance: ["#507 の受け入れの条件がテストで観測できる"]
	}
	"R-03": {
		title: "許可なしに、無視されたファイルを消さない"
		text:  "`worktree remove --unlock` は、unlock の後にできた無視されたファイルを、`--discard-ignored` なしで消さない。"
		acceptance: ["#508 の受け入れの条件がテストで観測できる"]
	}
	"R-04": {
		title: "grill の Artifact を、カタログへのリンク越しに仕上げられる"
		text:  "`spec-dock-grill-with-docs` の `finalize-artifact.py` が、版4の `spec-dock/initiatives` のリンクを通る Artifact のパスを受け付ける。"
		acceptance: ["リンクの配置で Artifact を仕上げるテストが通る（#509）"]
	}
	"R-05": {
		title: "曖昧な宣言と、観測の間に消えた worktree を、はっきり扱う"
		text:  "重複キーの宣言を版4として受け付けない。観測の間に消えた版3の worktree は unavailable の行にする。"
		acceptance: ["#510 の2つの要件がテストで観測できる"]
	}
	"R-06": {
		title: "文書とテストが、0.5.0 の後の形に合う"
		text:  "README のコマンドの数、`docs/` と `pyproject.toml` の古い記述を直し、撤去した案内の不在と雛形のバイトを確かめるテストを足す。入れたコンソールでの `work start`／`work finish` の e2e を足すかを決め、足さないなら理由を残す。"
		acceptance: ["#511 の要件がテストで観測できる"]
	}
	"R-07": {
		title: "5つのリポジトリが 0.5.1 にそろう"
		text:  "0.5.1 を出し、利用者の環境に入れ、5つのリポジトリの配布資産を `installation update` で 0.5.1 に上げる。配布の PR で、利用者のリポジトリの古い記述も直す。"
		acceptance: ["タグ `v0.5.1` があり、`spec-dock --version` が 0.5.1 を返す", "5つのリポジトリの `spec-dock/system/spec-dock-version` が 0.5.1 で、`canonical check` と、各リポジトリの検査のワークフローが通る", "5つのリポジトリの `canonical status` で、リンク、同期、変更が ok", "input-devices の `README.md` が SpecDock を `4d25a8b` に固定しておらず、company-os の `contract.md` が 0.2.4 と `4d25a8b` を述べていない"]
	}
	"R-08": {
		title: "移行の控えと版3の worktree を、利用者の決めたとおりに片付ける"
		text:  "0.5.1 を配った後、1〜2週間の通常の利用で問題がなければ、控えと版3の worktree の一覧（パス、大きさ、残した理由）を利用者に示し、許可されたものだけを消す。"
		acceptance: ["利用者に示した一覧と、利用者の決定と、消した結果（残したものを含む）が #514 の report.md にある"]
	}
}

failures: {
	"F-01": {
		title:    "直しが、ほかの canonical のコマンドを壊す"
		impact:   "5つのリポジトリの作業の始めと終わり、同期、仕様の作成が止まる"
		recovery: "配る前なら PR を閉じるか `git revert` する。配った後なら、パッケージを 0.5.0 に戻し、配布の PR を `git revert` する（0.5.0 の配布資産は 0.5.1 と同じ形のまま動く）"
	}
	"F-02": {
		title:    "配る途中で、一部のリポジトリだけが 0.5.1 になる"
		impact:   "リポジトリごとに SpecDock の版が違う"
		recovery: "各リポジトリの CI は版のファイルに従って動くので、そのまま残りを配るか、配った分を `git revert` する"
	}
	"F-03": {
		title:    "控えを消した後に、移行の前に戻す必要が出る"
		impact:   "I-12 の前の状態に、控えから戻せない"
		recovery: "戻すときは、版のタグ `v0.4.2` の移行の道具と、GitHub の `spec-dock/canonical` の履歴から作り直す。消す前に、1〜2週間の通常の利用と利用者の確かめを条件にして、起きにくくする"
	}
}

constraints: [
	"PR は人がマージする。エージェントはマージしない",
	"0.5.0 の公開の契約（コマンド、引数、終了コード、JSON の形）は、次の直しのほかは変えない：誤って書き込みや受け付けに進んでいた操作を止める直し（#506 の読み直し、#508 の unlock の後に無視されたファイルがあれば止めること、#510 の重複キー）と、途中の失敗の status・終了コード・effects を起きたことに合わせる直し（#507 の `failed` を `partial` にする）。これらは各 Issue の設計で、変わるコマンド、エラーのコード、終了コード、JSON を書き、#513 が `migration.md` の 0.5.1 の節に載せる。ほかの契約の変更が要るときは、その Issue で利用者に確かめる",
	"各 Issue は、テストを先に書いて直す（`tdd`）",
	"控えと worktree の削除は、利用者が対象と結果を確かめた後だけに行う",
]

decisions: [
	"2026-11-02：利用者が、epic-00424 の後の進め方の案（締めくくり、0.5.1 の直し、片付け、次の開発の4段）を承認した。直しは #508 を最初にし、6件を1つのリリース（0.5.1）にまとめて配る。控えは、配った後の1〜2週間の利用で問題がなければ消す",
	"2026-11-02：利用者が、Epic ごとに計画を具体化して書いてから進めるよう指示した",
]
