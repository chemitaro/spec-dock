# 第11回コードレビューの完全batch分析

## 証拠と判定

対象は `chemitaro/spec-dock`、`codex/iss-00413-external-cli-state` の `8c59994c8dad473697dcd8314721aeeef3f52d79`。利用者指定の固定点は `6fec3099d8759b4e5b3b393b2987534b46dfa383` で、merge-baseも同じ。cleanなattached branchと設定済みGitHub upstreamのfull SHA一致、二回のread-only remote照合を行ってから、通常のChatGPT Code Review StrictをGPT-5.6 Sol / Proで直接実行した。40分03秒、wrapper exit 0、`review_status=pass`、P0/P1なし、P2五件。回答の生成終了と直前のローカル検証終了を確認してから、このbatch全体を分析した。

[原文](code-review-p06-11.json)はwrapper stdoutのbytesを再serializeせず保全した（SHA-256 `2f144e8328f27004e757c6da7d77ec1cde2465de7ed7b217b10e309be434c024`）。P2、non-blocking、passを変更しない。利用者の「指摘事項を分析・修正・再レビューする」という別途の明示認可に従い、五件とも修正対象にする。レビュー単独を編集認可として扱わない。

レビュー範囲はP-02〜P-09とP-10のScope/Artifact/Workbenchまで。第10回のbranch/直接record照合とScope query helpの修正を含む。新しいnative Worktreeの未コミット変更は今回の判定外であり、52関連tests、旧createの六tests、変更四source限定mypy、398 filesのRuff check/formatはその別のローカル証拠である。full-suite/type gate、native Windows、worktree remove/bootstrap、P-11以後、consumer切替、Final Quality Gate、手動製品確認は引き続き未完了で、P severityを捏造せず残務として保持する。レビュー自身はtestsを実行していない。

## 五件の主張と対応

| 原分類 / group | 主張・到達性・根本原因 | authority / 初めに誤る層 | primary response route / 最小対応・検証 |
|---|---|---|---|
| F1 / P2 / root Artifact create | `mutate_artifact`がimport以外の`@root`を先に拒否する。拒否を外すだけでは後続の`assert target is not None`とScope専用置換も破綻するため、root ownerから六typeのcreate/dry-runへ実際に到達できない。公開CLIで到達可能。 | C-01の`artifact create --scope TARGET\|@root`、C-05の既存owner/catalogと六type保全。implementation層。 | `implementation-remediation`。root ownerのID/catalogを既存方式で使い、root-safeなtemplate置換とScopeの置換を明示分岐する。六typeのcreate/dry-run、legacy placeholder、list/show、無関係なScope metadata非依存を公開CLIで検証する。 |
| F2 / P2 / Workbench mode差 | regular fileの差分判定がmode差をoverwrite時だけ認識する。同一bytes・異なるmodeのerror policyでunchangedになる。sourceのregular-file modeを保持する契約と競合停止に反する。 | P-10/C-05のsource entry保全・error/overwrite。implementation層。 | `implementation-remediation`。bytes/modeの差分認識をpolicyに依存させず、errorは副作用前拒否、overwriteはsource modeで原子的公開。両policy、dry-runとdestination-only/部分失敗の既存回帰で検証する。 |
| F3 / P2 / 読取expect guard | `branch show`がguardを明示的に除外し、scope show、dependency list/check、artifact list/showも受理したoptionを検査しない。不一致の指定から成功応答に到達する。 | C-02の共通`--expect-current`と`--expect-backend`。implementation層。 | `implementation-remediation`。捕捉した同じ自WTの直接選択と解決済みScopeに対し、statelessな共通検査を読取経路にも適用する。対象のないleafでbackend guardを黙って無効化しない。同一原因に属するScope list/active/Syncの読取も照合する。明示/dynamic selector、canonical GH ref、empty/stale、backend不一致、GET前拒否、無変更を公開CLIで検証する。これはremote/global CASや新しいlockの追加ではない。 |
| F4 / P2 / import sourceの終了値 | `source_snapshot`がFileNotFoundErrorを含むOSErrorを一律ValueErrorへ変換するため、効果前の不存在/環境IOがexit 3になる。sourceのpathを隠す目的と終了値分類は別の要件である。 | C-04の明示local不存在exit 4、環境IO exit 5、unsafe/precondition exit 3とArtifact本文/source path非開示。implementation層。 | `implementation-remediation`。pathを含まない診断のまま、不存在・unsafe input・環境IOを区別する。missing、native permission/IO fault、unsafe file、公開前のsource変化、結果/effects/副作用0を検証する。 |
| F5 / P2 / 補完のpath解釈 | bash/zshは先行する非option tokenをすべてkeyへ結合し、fishはcommandlineの全tokenを比較する。`--project /repo scope`のoption値やleaf後のoperandがcommand keyに混入し、既存catalog候補が消える。 | C-02の共通optionのleaf前後対応、C-01の静的completion、同catalog生成。implementation層。 | `implementation-remediation`。catalogのcommand depth/option arityから、command componentだけを抽出して補完keyを作る。新しい業務状態やproject読取を追加しない。可能な実shellでprefix/suffix common option、leaf operand、inline値、必須option値、静的utilityを検証し、未検証shellは明記する。 |

五件は別のroot-cause groupとして扱う。F3だけは各read leafに散った同じ検査漏れなので共通のstateless検査へまとめ、症状ごとの例外や新しい状態管理を追加しない。

## 認可・保証・次の工程

全groupの主張は現行source経路とaccepted contractから妥当であり、利用者の既存認可内で実装修正できる。public syntax、GitHub番号SSOT、既存metadata、Start-only排他、直接record、no registry/journal/cache、raw Git error、partial/unknown、Artifactのsource privacyを維持する。意味変更、新leaf、UUID、global CAS、権限制御、復旧台帳を追加しないため、今回の対応に新しい人間判断は不要。

native Worktree create/list/showの検証済みunitを先にcheckpointし、この五件をTDDで順に修正する。関連検証と完全なstaged diff確認を経てtask-scoped commit/pushを行い、現在候補を固定したfresh Strictを一回実行する。今回の原文や以前のレビュー回答を次のreviewerへ添付せず、current GitHub sourceとcanonical contractから独立に判定させる。P2修正はpassの書換えでも最終certificationの代用でもなく、既存goalをactiveに保つ。
