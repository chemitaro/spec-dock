# 2026-10-03 ドッグフーディング後のレビュー分析・設計判断資料

## 実施結果と、この資料の位置付け

現在の作業環境 `0805/spec-dock` には外部CLI、薄いshim、writer宣言、静的資産を実際に適用した。`./spec -h`、通常reader、240 Scopeのvalidate、Artifactの実書込みは成功している。メインを含む他4 worktreeは変更していない。したがって、メインで旧shimを使った場合まで解決済みとは扱わない。

製品候補は `aa44ea1d37220f8d9f013df3ac44f22632099ee7`、レビュー固定baseは `6fec3099d8759b4e5b3b393b2987534b46dfa383`。新しいFinal Quality Gate v2はGPT-5.6 Sol・ProのUI確認付きで完了した。全13 perspectiveのcoverageはcomplete、結果は **fail / P1 1件、P2 2件**。前の候補でのpassを今回のpassへ転用しない。この資料は分析と判断用であり、仕様変更の承認や修正完了の証拠ではない。

必要test lane 8本は同候補SHAで全て終了・exit0。macOS通常全件1902 passed / 1 skipped、Linux Docker通常全件1886 passed / 17 skipped、Python 3.10関連境界170 passed。LinuxはDocker上の実Linux実行であり、物理Linuxホストの実施とは区別する。fresh wheelの197 provider payloadは現在installed packageと一致した。生ログ、候補identity、wheel、before/after入力hashは既存Epicのignored Workbenchに保持している。

## FQG-413-001 — P1 / performance-capacity

### 妥当性と到達条件

主張は妥当。直接記録のIssueと祖先が正常でも、同じissue containerに別IDの通常file／symlinkを置く、または別Initiative名の通常file／symlinkを置くだけで、他worktreeの観測がunavailableになる。隔離fixtureの4条件で再現した。Syncはexit7、complete=false、effects=[]。観測した直接記録のbytesは変わらない。

Startも `_check_selection → observe_worktrees → check_inventory` で同じunavailable行を開始前に拒否する。実GitHubへのStart／Closeは再現に使っていない。実際の5 worktreeの状態も変更していない。

最初の不正な実装処理は `scope_tree.py::_selected_paths` の無関係なentryに対する `lstat` と、未知の親の全階層探索である。後段の `walk` は選択chainだけのmetadataを読むが、その前の探索が無関係な異常を持ち込んでいる。

### Authorityと設計上の不足

- AC-413-24：他worktreeの全Scopeを横断ロードしない。
- D-10：他worktreeの直接対象と必要な祖先だけを読み、全Scope treeを走査しない。
- D-13：最小IO境界を試験する。
- D-03／data-schema.json：直接記録は固定7項目で、ID/refは保存するがScopeの保存場所・親IDは保存しない。
- D-04：branchを変えても対象と祖先が現在treeに存在すれば選択を保持し、現在metadataから祖先を求める。

IDだけから、任意のInitiative/Epic配下にある現在のScopeの保存場所を得るには、外部の名前索引かディレクトリ名の探索が必要になる。「対象以外のdirectory名も一切探索しない」という厳密な条件は、固定7項目かつ任意の現在配置という条件だけでは満たせない。この情報不足を局所的な例外や中央registryで隠してはならない。

Gitの `ls-files` を対象pathspecに限定した診断では、tracked／untrackedを含む実際の対象metadataのpathを取得でき、上記4条件に影響されなかった。ただし、Git内部での未追跡pathの名前探索まで不要になると主張しない。これはまだ製品修正ではなく、方式候補の実現性確認である。

### Primary response route

`design-decision-required`。P1はblockingのまま維持する。次のどちらを採るかで、D-10のIO保証またはD-03/D-04の永続契約・寿命の意味が変わるため、人間判断を経る。P2をこの判断の理由には使わない。

### 選択肢1：Gitの対象path検索を許容する（推奨）

Gitが持つ現在のファイル一覧からIDに一致する対象pathを絞り、対象と祖先のmetadataだけを安全に読む。未追跡の現在Scopeも読み取るため、必要ならGitの未追跡path検索を行う。無関係なScopeのmetadataや実体を製品側で検査しない。

維持するもの：ID/refが正本、固定7項目の直接記録、現在metadata由来の祖先、branch変更後の選択保持、ignoredな一件記録、readonly Sync、Startだけの短い排他、未知状態のfail-closed、中央engine／registry／cacheなし。Git管理領域へのツール独自の書込みを追加しない。

変更する保証：D-10の「全treeを走査しない」を、無関係なScope本文・実体の検証は禁止、対象pathを見つけるためのGitの名前検索は許容、と具体化する。未追跡探索の計算量が必要対象3件だけの定数時間とは限らない。有限timeoutを維持し、一覧取得失敗や対象/祖先の安全性不明は不完全とする。Gitのpath検索へ委ねただけで全ての性能問題が消えるとは説明しない。

影響：永続schema/API/既存記録のmigrationは不要。要件・設計・計画のIO定義、infraの対象path取得、applicationの観測入力、必要chainのみのloader、回帰試験を更新する。名前queryがignored/untracked/削除/移動/重複pathをどう扱うかを実装前に固定する。

### 選択肢2：直接記録に相対Scope pathを追加する

Start時に選択Scopeの相対pathを一項目保存し、以後はそのpathと最大2段の祖先だけを開く。保存pathはlocatorであり、Scope IDやGitHub番号の代替identityではない。

維持するもの：無関係な階層探索なし、ID/refが正本、現在metadataを照合、中央engine／registryなし。path escape／symlinkを拒否し、現在のID/refが記録と違えば採用しない。

変更する保証：固定7項目の永続契約を変える。保存pathが現在branchで消えた場合は、同じIDが別pathに存在しても探索せずstaleとし、明示clear／新Startが必要になる。D-04の任意の現在配置を保持する意味が狭くなる。既存formatの記録をどう保全・明示変換するかも設計する必要がある。pathをhintとして全tree fallbackすると、禁止している探索が復活するため採用しない。

影響：data-schema、WorkTarget／Store、Start出版、reader／Finish/activeの互換境界、D-03/D-04、手動移行説明、試験が対象。現在の0805には新直接記録は0件で、他4 worktreeは旧writerだが、一般consumerの互換性を無視して無断採用しない。

### 選択しない案

無関係なentryをcatchして無条件にempty扱いする、Git indexだけで未追跡Scopeを無視する、別の中央索引を作る、過去の祖先を保存して現在情報として返す、といった案は、観測・不完全性・簡素化の保証を失うため推奨しない。

### 判断後の検証とreview

対象/祖先だけのmetadata読取り、無関係なsymlink/file/壊れmetadataに影響されない観測、対象自身のredirect/消失/不一致でstaleまたはunavailableとなること、branch変更、未追跡/移動、重複、Git path取得失敗、全readonly不変、Start/Syncの公開経路をTDDで検証する。

設計の意味を変更する判断なら、その判断を正本R/D/Pへ反映し、既存fail campaignを保存した上で、更新した固定IO境界を持つ新campaignを準備する。新しい同SHAの必要test laneと独立reviewでpassを得るまで認定済みとしない。公開／merge／他の実worktree適用はこの判断の許可に含めない。

## FQG-413-002 — P2 / api-contract

妥当な情報指摘。`direct_artifact.py` と `direct_workbench.py` はmkdir呼出前にattemptedを立てるため、EACCESで作成前に失敗した経路にもpartial/unknownを返し得る。C-04の効果なし確定IO失敗exit5との不一致で、最初のfault layerは実装の効果分類である。

Primary routeの分析は `implementation-remediation` 相当だが、今回のFQ v2 policyではP2は情報記録のみであり、自律修正もこの項目のための再reviewも行わない。データ破壊の到達証拠ではない。P1を閉じる変更に便乗して修正しない。

## FQG-413-003 — P2 / requirements-closure

妥当な情報指摘。P-16本文は現在WT適用済み、P-17は前提不成立としているが、plan末尾の生成時summaryにはP-16/P-17未着手が残る。意味を変えず最新記録に合わせる場合のprimary routeは `documentation-correction` である。

今回のFQ v2 policyでは情報記録のみ。元のplan summaryをこのreview応答で修正しない。最新実施証拠は `dogfooding-20261003.md` と本資料を参照し、正式#413 Start成功と混同しない。

## 実環境の未完了・別の前提

同cloneの他4 worktreeが旧writer／schema1であるため、実Syncは不完全となる。#413 import dry-runはGitHub祖先#31がCLOSEDのため副作用前に拒否された。これらはFQG-413-001の隔離再現とは別の既存前提であり、P1を修正しても自動で解消しない。4 worktreeの移行・削除、#31のreopen/付替え、#413のcloseは無断で行わない。

## 生証拠の所在

- Epic Workbench `chatgpt-final-quality-gate-strict-v2/iss-00413-dogfood-20261003/`：request、preparation、review-result-1.json、wrapper-owned reviewer state、8 laneのmanifest/raw logs。
- Epic Workbench `dogfood-iss00413-20261003/logs/review-target-resolution.{json,stdout,stderr}`：隔離4条件の再現実測。
- Review conversation： https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6ac04bb8-9714-83ec-b080-bba08bb86c00
- この資料はagent-owned。wrapper-owned state／reviewerのraw resultは書き換えていない。
