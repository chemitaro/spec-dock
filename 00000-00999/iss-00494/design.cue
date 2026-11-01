package spec

// 設計（Issue）。型 specdock/v1。

goals: ["動きを変えずに、見本と案内だけで費用と合わせ方を伝える"]
current: "見本は PR と main への push で ubuntu-latest に動く。案内は検査の動きだけを述べ、費用や合わせ方を述べない。"
target:  "見本の先頭のコメントと canonical.md の「既定のブランチの検査」が、費用、起動の条件と runner の変更、push の前の hook の形を述べる。"

design: {
	"D-01": {
		title:     "見本のコメントで合わせ方を示す"
		text:      "spec-dock-check.yml の先頭に注記のコメントだけを足す。`branches: [main]` の行（WORKFLOW_BRANCH_LINE）と他の行は変えず、`canonical_check.py` とテストの参照を壊さない。注記は、ホストの runner の時間に費用がかかること、起動の条件（on）と runs-on はリポジトリの決まりに合わせて変えてよいこと、手動の起動だけ（workflow_dispatch）にもできることを述べる。"
		satisfies: ["R-01"]
	}
	"D-02": {
		title:     "canonical.md に費用と pre-push の形を足す"
		text:      "「既定のブランチの検査」に節を足し、見本の動きが既定であること、費用と合わせ方、push の前の hook（例 `.githooks/pre-push`）で同じ `spec-dock canonical check --json` を回す形を述べる。配布資産と dogfood の写しを同じ内容にし、scripts/migrate-to-canonical/migrate.py の WORKFLOW_SAMPLE_BYTES（見本のバイトの写し。テストが一致を縛る）にも同じ注記を足し、static-inventory.json のハッシュを更新して前の版を known_old_sha256 に足す。"
		satisfies: ["R-01"]
	}
}

compatibility: "CLI の動きは変えない。配布資産のバイトが変わるので、前の版を known_old_sha256 に足し、既存の利用者が installation update できるようにする。"
