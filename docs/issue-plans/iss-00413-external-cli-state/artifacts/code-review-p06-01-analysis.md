# P-03〜P-06 checkpointレビュー第1回の全件分析

候補は `ad73a06a5838aded54dc36cf1704aecdd1aca3f8`、固定baseは `6fec3099d8759b4e5b3b393b2987534b46dfa383`。通常Strict wrapper、GPT-5.6 Sol / Proの新規回答を原文のまま保全した。wrapper exit10、review_status=fail、P1四件。レビュー自身は試験を実行していない。ローカル後続の未commit変更はこの候補のレビュー対象ではない。

判定・認可・対応を分ける。四件とも既存D-03/D-06/D-09、AC-413-04とC-04に対する実装の不足であり、要求や設計の変更は必要ない。分類P1を維持し、全てblocking、主経路をimplementation-remediationとする。利用者の全実装・レビュー指摘修正・再レビューの認可内で対応する。新しいregistry/lock/permission/UUID/rollbackを導入しない。

| ID | 主張と到達経路・根因 | 対応と検証 | 親workflowへの結果 |
|---|---|---|---|
| F1 | 固定zero probeだけのignore規則を現行gateが受理する。公開実名が別ならGit差分を作る。D-03/AC-413-04を破る。最初の誤りは実装の実名未固定。 | 効果前に一つのランダムtokenをmemoryで固定し、stage/final実名をcurrent/candidate双方で読取専用検査し、storeへ同じtokenを渡す。probe専用ignore規則の公開CLI試験をRed→Green。 | 修正後、新規Strict再レビューが必要 |
| F2 | workspaceのfalsy required_features/禁止type/control_epoch、Scopeの未知featureをwriter admissionが検査しない。candidateから通常Startへ到達する。D-09/data-schemaに違反。最初の誤りは実装のwriter schema admission不足。 | workspaceと全current/candidate Scopeの構造/feature検査を再利用可能なdomain境界へ置く。unknown任意fieldは保持し、未知必須feature・不正型・禁止workspace fieldは副作用前拒否。公開CLIのcurrent/candidate両側ケースをRed→Green。 | 同上 |
| F3 | 同じbranch/HEADのearly unchangedはcandidate exact bytes検査を飛ばす。assume-unchangedの事前変更はlocal captureにもstatusにも矛盾しない。commit側だけのreadinessで成功できる。D-06の照合/readinessに違反。 | unchangedの成功前にもcandidateの全path/bytesを照合する。既存recordを保持したassume-unchanged metadata差の公開CLI試験をRed→Green。 | 同上 |
| F4 | held root検証後、storeがpathnameを独立openする。replacement cloneへの公開をheld identityでは防げない。D-03/D-05物理handle継続に違反。最初の誤りは公開adapterのroot binding不足。 | storeをheld root descriptorへ相対bindし、公開/readbackでidentity検査を維持する。外部OS boundaryでroot pathnameを交換する試験をRed→Green。途中で公開済みならunknown、成功とは返さない。 | 同上 |

後続作業で加えたinventory前後比較、same-Scope別branch/switch、Git失敗後現物観測、rename/unlink後unknownは独立の既存P-06義務であり、四件を閉じた証拠とは扱わない。関連試験469 passed/1 skippedおよび別process同一Scope競合1 passedはこの未commit作業の証拠で、全Issue受入・Windows native認定・FQG合格ではない。

全体型gateの既知未合格、Windows native/store未接続、P-07以降未完了、実dogfood適用前提、人間merge gateを維持する。四件の修正結果と後続checkpointを保存し、clean/pushed full SHA一致を確認して新規一回のStrictレビューへ渡す。先の回答を捨てたり、JSONだけを理由に再生成したりしない。
